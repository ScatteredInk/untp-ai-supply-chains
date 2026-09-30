"""Validate the credentials and write validation-report.md.

Checks, per credential:
  1. Core UNTP 0.7.0 JSON schema, full credential (core + extension properties).
  2. Core schema, core-only variant (aic: properties and extension context removed).
  3. Extension schema rules for every aic: property (extension/untp-ai-schema.json).
  4. Unit rule: every Measure unit is a Rec 20 code or a declared extension unit IRI.
  5. JSON-LD expansion in safe mode (jsonld.js, as the UNTP Playground runs it), both
     variants, and where extension terms end up after expansion.

Formats (uri, date-time) are checked here; the Playground does not check them
(Ajv validateFormats: false).

Run: .venv/bin/python validate.py
"""

import copy
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from build import AIC, AIC_CONTEXT, CREDENTIALS, ROOT, SCHEMA_FILES

SCHEMAS = ROOT / "schemas" / "v0.7.0"
EXT_SCHEMA = json.loads((ROOT / "extension" / "untp-ai-schema.json").read_text())
REC20 = set(json.loads((ROOT / "sources/snapshots/untp/rec20-codes.json").read_text()))
EXT_UNITS = set(EXT_SCHEMA["$defs"]["Unit"]["anyOf"][1]["enum"])


def strip_extension(node):
    if isinstance(node, dict):
        return {k: strip_extension(v) for k, v in node.items() if not k.startswith("aic:")}
    if isinstance(node, list):
        return [strip_extension(v) for v in node]
    return node


def core_only(cred):
    c = strip_extension(copy.deepcopy(cred))
    c["@context"] = [x for x in c["@context"] if x != AIC_CONTEXT]
    return c


def schema_errors(schema, doc):
    v = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message[:200]}"
                  for e in v.iter_errors(doc))


def ext_errors(doc):
    errs = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if k.startswith("aic:"):
                    if k in EXT_SCHEMA["$defs"]:
                        sub = {"$schema": EXT_SCHEMA["$schema"], "$defs": EXT_SCHEMA["$defs"],
                               "$ref": f"#/$defs/{k}"}
                        errs.extend(f"{path}.{k}: {e}" for e in schema_errors(sub, v))
                    else:
                        errs.append(f"{path}.{k}: no rule in extension schema (allowed, unconstrained)")
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(doc, "$")
    return errs


def unit_errors(doc):
    bad = []

    def walk(node, path):
        if isinstance(node, dict):
            if "unit" in node and "value" in node:
                u = node["unit"]
                if u not in REC20 and u not in EXT_UNITS:
                    bad.append(f"{path}: unit {u!r} is neither Rec 20 nor a declared extension unit")
            for k, v in node.items():
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(doc, "$")
    return bad


def units_used(doc, acc):
    if isinstance(doc, dict):
        if "unit" in doc and "value" in doc:
            acc.add(doc["unit"])
        for v in doc.values():
            units_used(v, acc)
    elif isinstance(doc, list):
        for v in doc:
            units_used(v, acc)
    return acc


def expand(doc, tmp):
    tmp.write_text(json.dumps(doc))
    out = subprocess.run(["node", str(ROOT / "jsonld-expand.js"), str(tmp)],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def predicates(node, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if not k.startswith("@"):
                acc.add(k)
            if k == "@type" and isinstance(v, list):
                acc.update(f"@type {t}" for t in v)
            predicates(v, acc)
    elif isinstance(node, list):
        for v in node:
            predicates(v, acc)
    return acc


def unit_iris(node, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "https://vocabulary.uncefact.org/untp/unit":
                for x in v:
                    acc.add(x.get("@id") or x.get("@value"))
            unit_iris(v, acc)
    elif isinstance(node, list):
        for v in node:
            unit_iris(v, acc)
    return acc


def main():
    tmp = ROOT / ".validate-tmp.json"
    results = []
    for stem, _, family, chain in CREDENTIALS:
        cred = json.loads((ROOT / "credentials" / f"{stem}.json").read_text())
        schema = json.loads((SCHEMAS / SCHEMA_FILES[family]).read_text())
        core = core_only(cred)
        full_exp = expand(cred, tmp)
        core_exp = expand(core, tmp)
        preds = predicates(full_exp.get("expanded", []), set())
        results.append({
            "stem": stem, "family": family, "chain": chain,
            "core_full": schema_errors(schema, cred),
            "core_only": schema_errors(schema, core),
            "ext": [e for e in ext_errors(cred) if "unconstrained" not in e],
            "ext_unconstrained": [e for e in ext_errors(cred) if "unconstrained" in e],
            "units": unit_errors(cred),
            "units_used": sorted(units_used(cred, set())),
            "jsonld_full": full_exp.get("error"),
            "jsonld_core": core_exp.get("error"),
            "aic_predicates": sorted(p for p in preds if p.startswith(AIC)),
            "untp_squatted": sorted(p for p in preds if p.startswith("https://vocabulary.uncefact.org/untp/")
                                    and "#" in p and p.split("#", 1)[1].startswith("aic")),
            "issuer_dependent": sorted(p for p in preds if "issuer-dependent" in p),
            "unit_iris": sorted(u for u in unit_iris(full_exp.get("expanded", []), set()) if u),
        })
    tmp.unlink(missing_ok=True)
    write_report(results)
    ok = all(not r["core_full"] and not r["core_only"] and not r["ext"] and not r["units"]
             and not r["jsonld_full"] and not r["jsonld_core"] for r in results)
    for r in results:
        print(f"{r['stem']:32} core+ext:{len(r['core_full'])} core-only:{len(r['core_only'])} "
              f"ext:{len(r['ext'])} units:{len(r['units'])} jsonld:{'ok' if not r['jsonld_full'] else 'FAIL'}"
              f"/{'ok' if not r['jsonld_core'] else 'FAIL'}")
    print("ALL PASS" if ok else "FAILURES (see validation-report.md)")


def write_report(results):
    L = ["# Validation report", "",
         "Generated by `validate.py`. Schemas: UNTP 0.7.0 (the version untp.unece.org/versions labels "
         "'Pilots'), from `schemas/v0.7.0/`. JSON Schema draft 2020-12 via Python `jsonschema` with format "
         "checking. JSON-LD: jsonld.js 8 in safe mode with local copies of the VC v2, UNTP 0.7.0 and "
         "extension contexts.", "",
         "| Credential | Type | Core schema (core + ext) | Core schema (core only) | Extension rules | "
         "Units | JSON-LD safe expansion (core + ext / core only) |",
         "|---|---|---|---|---|---|---|"]
    for r in results:
        def c(errs):
            return "pass" if not errs else f"**{len(errs)} errors**"
        jl = f"{'pass' if not r['jsonld_full'] else 'FAIL'} / {'pass' if not r['jsonld_core'] else 'FAIL'}"
        L.append(f"| `{r['stem']}` | {r['family']} | {c(r['core_full'])} | {c(r['core_only'])} | "
                 f"{c(r['ext'])} | {c(r['units'])} | {jl} |")
    L += ["", "## Findings", ""]
    L += [
        "- **Extension properties pass core validation.** Every object that carries an `aic:` property "
        "(the credential subject, `characteristics`, a `Claim`) has `additionalProperties: true` in the 0.7.0 "
        "schemas. Objects that are closed (`Measure`, `Classification`, `Link`, `PartyRole`, `Period`, "
        "`EventProduct`, `Performance`) cannot carry extension properties, so extension data sits beside them.",
        "- **Core schema does not enforce Rec 20.** `Measure.unit` is a free string with "
        "`x-external-enumeration`. Extension unit IRIs pass the schema; `validate.py` applies the Rec 20 rule "
        "itself.",
        "- **Extension units must be IRIs.** The UNTP context types `unit` as `@vocab` against "
        "`https://vocabulary.uncefact.org/UnitMeasureCode#`. A bare code such as `FLOP` expands to "
        "`UnitMeasureCode#FLOP`, which does not exist in Rec 20, and nothing flags it.",
        "- **Extension terms need a prefix.** UNTP type-scoped contexts set `@vocab` (for example "
        "`untp/Facility#`). Tested: an unprefixed `installedEquipment` on a Facility expands silently to "
        "`https://vocabulary.uncefact.org/untp/Facility#installedEquipment`, a term UNTP never defined. "
        "Unprefixed keys nested inside it do not expand at all, so safe mode fails (the Playground's context "
        "step would fail). Inside `characteristics`, unprefixed keys expand to `untp/Characteristics#`, which "
        "is UNTP's intended extension point. The `aic:` prefix plus the extension context avoids all of this.",
        "- **The Playground will reject the extension variant until the context resolves.** "
        f"`{AIC_CONTEXT}` is a fictional URL. Locally it is served from `extension/`. The Playground fetches "
        "remote contexts over HTTPS and fails the context step if one cannot be loaded.",
        "",
        "## Units used", "",
    ]
    all_units = sorted({u for r in results for u in r["units_used"]})
    for u in all_units:
        L.append(f"- `{u}` {'(Rec 20)' if u in REC20 else '(extension)' if u in EXT_UNITS else '(UNKNOWN)'}")
    L += ["", "## Detail", ""]
    for r in results:
        L += [f"### {r['stem']} ({r['family']}, chain position {r['chain']})", ""]
        for label, key in [("Core schema, core + extension", "core_full"), ("Core schema, core only", "core_only"),
                           ("Extension rules", "ext"), ("Unit rule", "units")]:
            errs = r[key]
            L.append(f"- {label}: {'pass' if not errs else ''}")
            L += [f"  - `{e}`" for e in errs]
        L.append(f"- JSON-LD (core + extension): {'pass' if not r['jsonld_full'] else r['jsonld_full']}")
        L.append(f"- JSON-LD (core only): {'pass' if not r['jsonld_core'] else r['jsonld_core']}")
        L.append(f"- Extension predicates after expansion: {len(r['aic_predicates'])}")
        if r["untp_squatted"]:
            L.append(f"- Extension terms expanded into UNTP namespace: {r['untp_squatted']}")
        if r["issuer_dependent"]:
            L.append(f"- Terms falling back to VC `issuer-dependent#` vocabulary: {r['issuer_dependent']}")
        if r["ext_unconstrained"]:
            L.append(f"- Extension properties with no rule yet: {len(r['ext_unconstrained'])}")
        L.append("")
    (ROOT / "validation-report.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()

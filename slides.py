"""Slide feed: summarise field-matrix.csv and gap-register.csv for the two slides.

Writes:
  slides/chain-fields.csv  slide 1: top-level fields beneath each credential, with status
  slides/gap-summary.csv   slide 2: gap counts by chain position and gap type
  slides/index.html        draft of both slides (ODS Visual Guidelines 2026 palette)

Run: .venv/bin/python slides.py
"""

import csv
import html
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "slides"

ORDER = ["published", "needs extension vocabulary", "not published"]
SYMBOL = {"published": "●", "needs extension vocabulary": "◐", "not published": "○"}
CHAIN = [("1 chips (stretch)", "Chips"), ("2 sites", "Sites"), ("3 data", "Data"),
         ("4 training runs", "Training runs"), ("5 model", "Model")]
TITLES = {
    "01-h100-sxm5-passport": ("DPP", "NVIDIA H100 SXM5 80GB (model level)"),
    "02-jupiter-facility-record": ("DFR", "Jupiter, Austin TX"),
    "03-augusta-facility-record": ("DFR", "Augusta, Council Bluffs IA"),
    "04-olmo-mix-1124-passport": ("DPP", "olmo-mix-1124"),
    "05-dolmino-mix-1124-passport": ("DPP", "dolmino-mix-1124"),
    "06-training-run-jupiter": ("DTE MakeEvent", "Training at Jupiter"),
    "07-training-run-augusta": ("DTE MakeEvent", "Training at Augusta"),
    "08-olmo-2-7b-passport": ("DPP", "OLMo 2 7B"),
}
SKIP = {"type", "id", "name", "description", "idScheme", "relatedDocument"}
TOP = re.compile(r"^\$\.credentialSubject(\[\])?\.([^.\[]+)(\[\])?$")
CHAR = re.compile(r"^\$\.credentialSubject\.characteristics\.(aic:[^.\[]+)$")


def rollup(statuses):
    """Status of a container from the statuses of the fields beneath it."""
    s = set(statuses)
    if "needs extension vocabulary" in s:
        return "needs extension vocabulary"
    if "published" in s:
        return "published"
    return "not published"


def chain_fields(rows):
    by_cred = defaultdict(list)
    for r in rows:
        if r["credential"] in TITLES and r["applicable"] == "yes":
            by_cred[r["credential"]].append(r)
    out = []
    for cred, rs in by_cred.items():
        for r in rs:
            m = TOP.match(r["path"]) or CHAR.match(r["path"])
            if not m:
                continue
            field = m.group(2) if TOP.match(r["path"]) else m.group(1)
            if field in SKIP or field == "characteristics" or r["status"] == "issuer-controlled":
                continue
            status = r["status"]
            if status == "container" or field.startswith("aic:"):
                kids = [x["status"] for x in rs if x["path"].startswith(r["path"] + ".")
                        or x["path"].startswith(r["path"] + "[]")]
                status = rollup([status] + kids) if status != "container" else rollup(kids)
            out.append({
                "credential": cred, "type": TITLES[cred][0], "title": TITLES[cred][1],
                "chain": r["chain"], "field": field, "required": r["required"],
                "status": status,
                "placeholder": "yes" if any(x["basis"] == "placeholder" for x in rs if x["path"] == r["path"]
                                            or x["path"].startswith(r["path"] + ".")
                                            or x["path"].startswith(r["path"] + "[]")) else "no",
                "extension_property": "yes" if field.startswith("aic:") else "no",
            })
    seen, dedup = set(), []
    for o in out:
        key = (o["credential"], o["field"])
        if key not in seen:
            seen.add(key)
            dedup.append(o)
    return dedup


def main():
    OUT.mkdir(exist_ok=True)
    rows = list(csv.DictReader(open(ROOT / "field-matrix.csv")))
    gaps = list(csv.DictReader(open(ROOT / "gap-register.csv")))
    fields = chain_fields(rows)
    with open(OUT / "chain-fields.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields[0]))
        w.writeheader()
        w.writerows(fields)
    counts = Counter((g["chain"], g["gap_type"]) for g in gaps)
    types = ["standard", "data", "knowledge", "institutional"]
    chains = [c for c in dict.fromkeys(g["chain"] for g in gaps)]
    with open(OUT / "gap-summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["chain"] + types + ["total"])
        for c in chains:
            w.writerow([c] + [counts[(c, t)] for t in types] + [sum(counts[(c, t)] for t in types)])
    write_html(fields, gaps, chains, types, counts)
    print(f"wrote {len(fields)} slide-1 fields, {len(chains)} slide-2 rows")


def write_html(fields, gaps, chains, types, counts):
    e = html.escape
    by_cred = defaultdict(list)
    for f in fields:
        by_cred[f["credential"]].append(f)
    cols = []
    for chain_key, label in CHAIN:
        cards = []
        for cred, (typ, title) in TITLES.items():
            fs = [f for f in by_cred[cred] if f["chain"] == chain_key]
            if not fs:
                continue
            fs.sort(key=lambda f: (f["extension_property"], ORDER.index(f["status"])))
            items = "".join(
                f'<li class="{f["status"].split()[0]}"><span class="sym">{SYMBOL[f["status"]]}</span>'
                f'{e(f["field"])}{"<sup>R</sup>" if f["required"] == "yes" else ""}'
                f'{" <em>placeholder</em>" if f["placeholder"] == "yes" else ""}</li>'
                for f in fs)
            cards.append(f'<div class="card"><div class="ctype">{e(typ)}</div><h3>{e(title)}</h3><ul>{items}</ul></div>')
        cols.append(f'<section class="col"><h2>{e(label)}</h2>{"".join(cards)}</section>')
    maxc = max(counts.values())
    grid = "".join(
        f"<tr><th>{e(c)}</th>" + "".join(
            f'<td style="--a:{counts[(c, t)] / maxc:.2f}">{counts[(c, t)] or ""}</td>' for t in types)
        + "</tr>" for c in chains)
    owners = Counter()
    for g in gaps:
        plain = g["candidate_owner_proposal"].replace(" (proposal; not approached)", "")
        for o in re.split(r";\s*", plain):
            owners[o.strip()] += 1
    owner_list = "".join(f"<li><b>{n}</b> {e(o)}</li>" for o, n in owners.most_common(12))
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>OLMo 2 7B in UNTP: slide drafts</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;600;700&display=swap">
<style>
:root {{ --sunburst:#f46036; --page:#f5f5f5; --cream:#efecca; --sage:#a9cbb7; --sky:#6fafe8;
        --olive:#c2b520; --citron:#e6e014; --g1:#595959; --g2:#cccccc; --g3:#d9d9d9; --g4:#f3f3f3; }}
body {{ margin:0; background:var(--page); font-family:"Instrument Sans", Arial, sans-serif; color:#222; }}
.slide {{ width:1600px; min-height:900px; box-sizing:border-box; padding:40px 48px; margin:24px auto;
          background:#fff; border:1px solid var(--g2); }}
h1 {{ font-size:30px; margin:0 0 6px; }}
.sub {{ color:var(--g1); margin:0 0 20px; font-size:15px; }}
.chain {{ display:grid; grid-template-columns:repeat(5,1fr); gap:14px; }}
.col h2 {{ font-size:18px; margin:0 0 8px; padding:6px 8px; background:var(--cream); }}
.card {{ border:1px solid var(--g2); padding:8px 10px; margin-bottom:10px; background:#fff; }}
.ctype {{ font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--g1); }}
.card h3 {{ font-size:15px; margin:2px 0 6px; }}
.card ul {{ list-style:none; margin:0; padding:0; font-size:12.5px; line-height:1.45; }}
.sym {{ display:inline-block; width:16px; }}
li.published .sym {{ color:#4f8a68; }} li.needs .sym {{ color:var(--sky); }} li.not .sym {{ color:var(--sunburst); }}
li em {{ color:var(--g1); font-size:11px; }}
sup {{ font-size:9px; color:var(--g1); }}
.key {{ display:flex; gap:24px; font-size:13px; margin:16px 0 0; color:var(--g1); }}
.key .published {{ color:#4f8a68; }} .key .needs {{ color:var(--sky); }} .key .not {{ color:var(--sunburst); }}
.arrow {{ font-size:13px; color:var(--g1); margin-bottom:10px; }}
table {{ border-collapse:collapse; font-size:15px; }}
th, td {{ border:1px solid var(--g3); padding:8px 14px; text-align:left; }}
td {{ text-align:center; min-width:90px; background:color-mix(in srgb, var(--sunburst) calc(var(--a) * 70%), #fff); }}
thead th {{ background:var(--g4); }}
.two {{ display:grid; grid-template-columns:1.1fr 1fr; gap:40px; }}
.owners li {{ margin-bottom:4px; font-size:14px; }} .owners b {{ display:inline-block; width:26px; }}
.defs {{ font-size:13px; color:var(--g1); }} .defs b {{ color:#222; }}
</style></head><body>
<div class="slide">
<h1>OLMo 2 7B supply chain in UNTP 0.7.0: what each credential can hold</h1>
<p class="sub">Reconstructed by ODS from public sources (30 Sep 2026). Top-level fields beneath each credential.
R = required by the schema. Every credential validates against the core schema, with and without the extension.</p>
<div class="arrow">chips → sites → data → training runs → model</div>
<div class="chain">{"".join(cols)}</div>
<div class="key"><span class="published">● published</span><span class="needs">◐ needs extension vocabulary</span>
<span class="not">○ not published</span><span><em>placeholder</em> = required field filled because nothing is published</span></div>
</div>
<div class="slide">
<h1>Gap register: {len(gaps)} gaps</h1>
<p class="sub">Counts by position in the chain and gap type. Candidate owners are proposals; none has been approached.</p>
<div class="two">
<div><table><thead><tr><th></th>{"".join(f"<th>{t}</th>" for t in types)}</tr></thead><tbody>{grid}</tbody></table>
<p class="defs"><b>standard</b>: UNTP or its vocabularies have no place or code for it. <b>data</b>: UNTP could hold it,
but nobody publishes it. <b>knowledge</b>: sources conflict or it cannot be known from outside. <b>institutional</b>:
no body or process exists to issue, host or assess it.</p></div>
<div><h2 style="font-size:18px;margin-top:0">Candidate owners (proposals), by number of gaps</h2><ol class="owners" style="list-style:none;padding:0">{owner_list}</ol></div>
</div></div>
</body></html>
"""
    (OUT / "index.html").write_text(doc)


if __name__ == "__main__":
    main()

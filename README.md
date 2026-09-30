# OLMo 2 7B supply chain in UNTP

ODS Field Work, AI Supply Chains (September 2026). This is a prototype of how far the UN Transparency Protocol (UNTP) can describe an AI supply chain, using Ai2's OLMo 2 7B (`allenai/OLMo-2-1124-7B`) as the worked example.

**All credentials here are reconstructions by ODS from public sources.** None of the parties named issued, reviewed or endorsed them. The issuer (`did:web:example.org`) is fictional and nothing is signed.

## Contents

| Path | What it is |
|---|---|
| `credentials/` | 8 UNTP 0.7.0 credentials, ordered along the chain: chips → sites → data → training runs → model |
| `field-matrix.csv` | Every field of every schema, per credential. Each row has a status (published / not published / needs extension vocabulary, plus issuer-controlled and container), value, basis, source key, locator and note. |
| `gap-register.csv` | 54 gaps: item, field, gap type, proposed extension or profile, and candidate owner (all proposals) |
| `extension/` | Proposed AI compute and models extension: JSON-LD context, JSON Schema rules, vocabulary (`extension/README.md`) |
| `schemas/v0.7.0/` | Downloaded UNTP schemas, context and samples, with URLs and hashes (`MANIFEST.md`) |
| `sources.md` | Every source, with URL and access date. Keys are cited in the matrix and register. |
| `sources/snapshots/` | Raw copies of the Hugging Face API responses and cards, the UNTP taxonomies and the Rec 20 code list |
| `validation-report.md` | Validation results (generated) |
| `slides/` | Slide diagrams: `diagram-1-chain` (the chain, core vs extension links) and `diagram-2-model-passport` (inside the OLMo 2 7B passport) and `diagram-3-untp-data` (the four UNTP credential types), as SVG and 2× PNG with transparent backgrounds. Also `chain-fields.csv`, `gap-summary.csv` and an earlier `index.html` draft. |

## Run

```sh
python3 -m venv .venv && .venv/bin/pip install jsonschema pyld && npm install
.venv/bin/python build.py      # credentials, field matrix, extension context, sources.md
.venv/bin/python gaps.py       # gap register
.venv/bin/python validate.py   # validation-report.md
.venv/bin/python slides.py     # slides/ summaries
.venv/bin/python diagrams.py   # slides/diagram-*.svg and .png (needs Google Chrome for the PNGs)
```

`build.py` holds every value with its source. Edit values there, not in `credentials/`.

## Credentials

| # | Chain | Credential | UNTP type | Main source |
|---|---|---|---|---|
| 01 | chips (stretch) | NVIDIA H100 SXM5 80GB, model level | DPP | Nvidia whitepaper and blog, SK hynix, ETO Chip Explorer |
| 02 | sites | Jupiter cluster, Austin TX | DFR | OLMo 2 report §6.1.1, §6.5, Table 19 |
| 03 | sites | Augusta cluster, Council Bluffs IA | DFR | OLMo 2 report §6.1.2, §6.5; Google Cloud docs |
| 04 | data | olmo-mix-1124 | DPP | Hugging Face dataset card and API |
| 05 | data | dolmino-mix-1124 | DPP | Hugging Face dataset card and API |
| 06 | training runs | Training at Jupiter | DTE (MakeEvent) | OLMo 2 report §6.1 |
| 07 | training runs | Training at Augusta | DTE (MakeEvent) | OLMo 2 report §6.1 |
| 08 | model | OLMo 2 7B | DPP | Hugging Face model API; report Tables 6 and 19 |

No Digital Conformity Credential was produced: no third-party assessment exists for any claim. DCC fields still appear in the field matrix, all marked not published.

## Validation (all pass)

Each credential passes the core UNTP 0.7.0 schema twice: with the extension properties, and with them stripped. It also passes the extension rules and the Rec 20 unit rule, and it expands in JSON-LD safe mode with jsonld.js, as the Playground does. Negative tests (a missing required field, a bad role, an extension key inside `Measure`, a bare `FLOP` unit, a missing context) are all caught. Details are in `validation-report.md`.

## Open checks: resolution

| Check | Result | Evidence |
|---|---|---|
| UNTP version for pilots | **0.7.0.** The versions page labels 0.7.0 "Pilots", Work in Progress "Testing" and 0.6.0 "Unmaintained". The spec repo moved to opensource.unicc.org; the GitHub copy stops at 0.6.1. | `UNTP-VERSIONS` |
| Can a DPP describe a digital product? | **Schema: yes; design: poorly.** Nothing forbids it, but `producedAtFacility` and `countryOfProduction` are required, and dimensions, packaging, materials and granularity assume physical goods. Recorded as a "digital product profile" gap. | `UNTP-SCHEMA`; G21 |
| Must units come from Rec 20? | **The spec says yes; the schema does not enforce it** (free string with `x-external-enumeration`). Rec 20 has no FLOP, token, GPU-hour or parameter unit. The context types `unit` as `@vocab` against Rec 20, so extension units must be full IRIs. | `REC20`; G30, G38 |
| Can the MakeEvent business step be extended? | **Yes.** `activityType` is a Classification with an open `schemeId`, and DTE requirement TEV-09 explicitly allows industry-specific schemes. GS1 CBV has no training step. | `UNTP-SCHEMA`; G31 |
| Does the DFR have a field for installed equipment? Does UNTP distinguish equipment used from inputs? | **No and no.** The Facility has `materialUsage` (consumed) only; the MakeEvent has input and output products only. | G09, G32 |
| Carbon emissions unit in Table 19 | **Not printed.** tCO2eq is inferred from §6.5 ("about 154 tCO2 eq" = 52 + 101). Intensity is kg CO2/kWh and WUE is L/kWh, also from §6.5. | `OLMO2`; G43 |
| Iowa 0.351 vs 0.352 | **Unresolved.** The text says 0.352 and Table 19 says 0.351, identically in v1, v2 and v3. The text value is used and flagged. | `OLMO2`; G18 |
| Jupiter hardware ownership | **Not stated.** "Ai2 cluster … operated by Cirrascale Cloud Services". "Owned" appears nowhere in the report. Recorded as a knowledge gap pointing to BODS. | `OLMO2`; G11 |
| Ai2's EIN | **82-4083177** (ProPublica/IRS; Seattle, 3800 Latona Ave NE). Wikidata's 91-2155317 is the Allen Institute (bioscience). | `PROPUBLICA-AI2` |
| Ai2's UEI | **H2VSQE9MCUU5, confirmed via USAspending**, not directly in SAM.gov (the API needs a key). | `USASPENDING-AI2` |
| H100 form factor | **SXM5.** Only the SXM variant is 80 GB HBM3 at 700 W; PCIe is HBM2e at 350 W and NVL is 94 GB. Google documents A3 Mega as H100 SXM. The report itself never says SXM. | `NV-WP`, `NV-PB-PCIE`, `GCP-GPUS` |
| Stretch facts: designer, fab, HBM | **Sourced.** Nvidia designs it; TSMC fabricates the die on 4N (Nvidia blog). SK hynix supplies HBM3 (SK hynix, 2022); Samsung's share is minor and unconfirmed. CoWoS-S packaging comes from secondary sources only. | `NV-BLOG`, `SKH-2022`, `TRENDFORCE-2024`, `SEMIANALYSIS-2023` |
| Candidate owners | **All are proposals; none approached.** | `gap-register.csv` |

New issues found along the way:

- The report is inconsistent on stage 1 tokens: 3.90T in §2.3, 4T in §3 and Table 3.
- The dataset repos were modified after OLMo 2's release, so the recorded commits may not be the training revisions.
- The UNTP 0.7.0 samples use singular metric and topic IRIs where the taxonomy uses plural ones.

## UNTP Playground (task 5)

This was established by reading the Playground source (`PLAYGROUND-SRC`). **No credential was uploaded**, because uploading sends the files to an external service.

- **Unsigned credentials are accepted.** They are schema-checked against the version detected from `@context` (0.6.0, 0.6.1 and 0.7.0 are bundled), and only the "Credential Verification" step fails. Extra properties are tolerated.
- **The context step fails for an unresolvable context.** The Playground expands JSON-LD in safe mode and fetches every context over HTTPS, and `https://example.org/untp-ai/0.1/context.jsonld` does not resolve. The core-only variant should pass. To test the extension variant, the context must be hosted at a real HTTPS URL.
- **Signing is not needed for schema checks.** If a clean verification step is wanted, VCkit (uncefact/project-vckit) can issue an enveloped JWT from a did:web that must resolve publicly. These steps were not run.

## Visualiser

No UNTP tool draws the chain (DPP → DTE → DFR → DCC).

- **Reference Implementation `/verify` page** (`untp.showthething.com/verify`, `RI-VERIFY`). It renders one credential at a time through `renderMethod`. It only accepts a signed `EnvelopedVerifiableCredential` fetched from a public URL: an unsigned sample was rejected with `UNSUPPORTED_CREDENTIAL_TYPE`.
- **UNTP Playground.** A validator. Its Link Sets tab lists resolver links, but it does not draw them.
- **RI templates.** The RI ships 0.7.0 Handlebars render templates for DPP, DTE, DFR and DCC (GPL-3.0). These could render our unsigned credentials locally.
- **Graph views.** None exist yet. `absoludity/untp-graph-validation-cli` builds an RDF graph but draws nothing and targets 0.6.0-beta. The tests-untp "transparency graphs" suite is still a placeholder.

For the slides, `slides/index.html` is a static draft built from the matrix and register.

## Not done

- No credential has been uploaded to the Playground or signed.
- The Olmo 3 contrast row relies on the handoff and was not re-checked.
- CoWoS-S for H100 rests on secondary sources.
- SWHID as ISO/IEC 18670 is unchecked.
- The ISO/IEC 30134 references are an ODS assumption; the report does not cite them.

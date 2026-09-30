"""Gap register for the OLMo 2 7B UNTP reconstruction. Writes gap-register.csv.

Gap types:
  standard       UNTP (or a vocabulary it relies on) has no place or code for the information
  data           UNTP could hold it, but no public source publishes it
  knowledge      Public sources conflict, or nobody outside the parties could know it
  institutional  No body or process exists to issue, host, assess or maintain it

Every candidate owner is a PROPOSAL. None has been approached, and fit has not been checked with them.

Run: .venv/bin/python gaps.py
"""

import csv
from pathlib import Path

from sources import SOURCES

P = " (proposal; not approached)"
UNTP_TEAM = "UN/CEFACT UNTP project team" + P
AI_EXT = "AI-sector UNTP extension maintainer, e.g. a UNTP Community Activation Program for AI" + P

GAPS = [
    # chain, item, field, gap type, description, evidence, proposal, owner
    ("1 chips", "H100 lot", "batchNumber / itemNumber", "data",
     "No lot, batch or serial numbers are published for the GPUs installed at Jupiter or Augusta, so the "
     "passport can only be model-level.", "OLMO2", "Asset register of installed GPUs (model, lot, count) "
     "published by the operator, linked from the facility record.", "Ai2, Cirrascale, Google (data holders)" + P),
    ("1 chips", "H100 lot", "modelNumber / id", "data",
     "Nvidia's part number for the SXM5 module appears only on reseller listings; no GTIN found.",
     "NV-PB-PCIE", "Manufacturer-issued product identifier (GTIN or part number) resolvable via an identity resolver.",
     "NVIDIA; GS1" + P),
    ("1 chips", "H100 lot", "productCategory", "standard",
     "No CPC or HS class names AI accelerators. HS 8473.30 (CPC 45290) applies only by analogy with a V100 ruling.",
     "CPC21; CPC-HS; CBP-N304787", "AI extension product class 'gpu-accelerator' alongside CPC 45290.",
     "UNSD (CPC); WCO (HS)" + P),
    ("1 chips", "H100 lot", "materialProvenance", "standard",
     "The composition model is mass fraction plus origin country. A chip's value chain is components (die, HBM, "
     "package) from named suppliers, with no published masses.", "NV-BLOG; SKH-2022; SEMIANALYSIS-2023",
     "aic:components bill of materials (component, supplier, process, evidence, status).", AI_EXT),
    ("1 chips", "H100 lot", "relatedParty.role", "standard",
     "PartyRole has no 'designer' or 'component supplier' role. Nvidia is recorded as brandOwner and TSMC as "
     "manufacturer, though TSMC makes the die, not the module.", "UNTP-SCHEMA",
     "Add designer and componentSupplier roles to PartyRole.", UNTP_TEAM),
    ("1 chips", "H100 lot", "aic:components (HBM3 supplier)", "knowledge",
     "SK hynix supplied HBM3 for H100. Samsung entered in late 2023. Which supplier's stacks are in these GPUs "
     "cannot be known from public sources.", "SKH-2022; TRENDFORCE-2024",
     "Supplier per lot carried in the manufacturer's passport.", "NVIDIA (data holder)" + P),
    ("1 chips", "H100 lot", "producedAtFacility / countryOfProduction", "data",
     "Module assembly site and country not published. The 10-K names contract manufacturers without mapping "
     "them to products.", "NV-10K", "None; required field filled with an explicit placeholder.",
     "NVIDIA (data holder)" + P),
    ("1 chips", "H100 upstream trace", "(whole trace)", "knowledge",
     "ETO Chip Explorer is type-level (inputs, providers, country shares). It has no facilities, lots or "
     "identifiers, no firm-level foundry row for TSMC, and no HBM or memory inputs.", "ETO",
     "Use ETO input IDs as a process and input vocabulary. Add LEIs to providers and memory inputs.",
     "Georgetown CSET / ETO" + P),

    ("2 sites", "Jupiter, Augusta", "installed equipment (no core field)", "standard",
     "The DFR has no property for installed equipment. materialUsage covers materials consumed. UNTP does not "
     "distinguish equipment used by a process from inputs consumed by it.", "UNTP-SCHEMA",
     "aic:installedEquipment on Facility (type, model, count, specs, passport link); aic:equipmentUsed on MakeEvent.",
     UNTP_TEAM + "; " + AI_EXT),
    ("2 sites", "Jupiter, Augusta", "id / idScheme / registeredId", "institutional",
     "There is no public facility register identifier for either cluster. The IDs are ODS-minted. UNTP says to "
     "use the owner's party ID when self-issuing, but the owner is not published.", "OLMO2",
     "Data-centre identifiers from a public register.",
     "European Commission (EU data-centre reporting database) or national registers; applicability to US sites unchecked" + P),
    ("2 sites", "Jupiter", "relatedParty (owner)", "knowledge",
     "The report calls Jupiter an 'Ai2 cluster operated by Cirrascale'. Who owns the hardware is not stated.",
     "OLMO2", "Out of UNTP scope: record ownership and control via a BODS statement linked from the party.",
     "Open Ownership (BODS)" + P),
    ("2 sites", "All parties", "ownership and control", "institutional",
     "UNTP identifies parties but does not model beneficial ownership or control between them (Ai2, Cirrascale, "
     "Google, NVIDIA).", "UNTP-SCHEMA",
     "Out of UNTP scope. Link Party records to BODS ownership-or-control statements.", "Open Ownership (BODS)" + P),
    ("2 sites", "Jupiter, Augusta", "relatedParty.role (tenant)", "standard",
     "PartyRole has no tenant or compute-customer role for Ai2, whose workloads run on capacity operated or "
     "provided by others.", "UNTP-SCHEMA", "Add a tenant/customer role; meanwhile aic:computeTenant.", UNTP_TEAM),
    ("2 sites", "Augusta", "installed equipment", "knowledge",
     "A cloud tenant sees VMs, not physical hosts. Host servers, CPUs, GPU TDP and the GPU total (1,280 is "
     "calculated) are not published.", "OLMO2; GCP-GPUS",
     "Provider-issued facility record for the capacity allocated to a tenant.", "Google Cloud (data holder)" + P),
    ("2 sites", "Jupiter, Augusta", "performanceClaim (PUE, WUE)", "standard",
     "The UNTP performance-metrics taxonomy has no PUE or WUE metric.", "UNTP-METRICS; OLMO2",
     "Add PUE and WUE metrics referencing ISO/IEC 30134-2 and -9 (the report does not cite them).",
     "UNTP taxonomy maintainers (UN/CEFACT); ISO/IEC JTC 1/SC 39" + P),
    ("2 sites", "Jupiter, Augusta", "performanceClaim.applicablePeriod", "data",
     "PUE periods are not stated. Augusta's 1.12 is a campus trailing-twelve-month figure, not the cluster's.",
     "OLMO2", "None.", "Ai2, Google (data holders)" + P),
    ("2 sites", "Jupiter, Augusta", "grid carbon intensity", "standard",
     "The value is the electricity supplier's or state's emission factor, not a facility performance. UNTP "
     "claims are about the subject facility, and there is no slot for an energy-supply emission factor or for "
     "location- versus market-based accounting.", "OLMO2",
     "Energy-supply object on Facility (supplier, factor, basis, year).", UNTP_TEAM),
    ("2 sites", "Augusta", "grid carbon intensity value", "knowledge",
     "The text gives 0.352 kg CO2/kWh, Table 19 gives 0.351; the mismatch is identical in all three arXiv versions "
     ".", "OLMO2", "None; flag for erratum.", "Ai2 (report authors)" + P),
    ("2 sites", "Jupiter, Augusta", "address / locationInformation", "data",
     "Only the city is published. Street, postcode and coordinates are placeholders in required fields.", "OLMO2",
     "None.", "Cirrascale, Google (data holders)" + P),
    ("2 sites", "Jupiter, Augusta", "materialUsage (electricity, water)", "data",
     "Facility-period electricity and water consumption are not published; only model-level estimates exist.",
     "OLMO2", "None.", "Operators (data holders)" + P),

    ("3 data", "olmo-mix-1124, dolmino-mix-1124", "DPP for a digital product", "standard",
     "The DPP is written for shipped physical goods. The schema does not forbid digital products, but "
     "producedAtFacility and countryOfProduction are required and have no meaning for a dataset; dimensions, "
     "packaging and labels do not apply.", "UNTP-SCHEMA",
     "A 'digital product' profile of the DPP: optional production facility, data-size dimension, licence, "
     "and a repo + commit + hash identifier rule.", UNTP_TEAM + "; " + AI_EXT),
    ("3 data", "olmo-mix-1124, dolmino-mix-1124", "productCategory", "standard",
     "CPC v2.1 has no class for training datasets. 84399 'Other on-line content n.e.c.' is the nearest.",
     "CPC21", "AI extension product class 'training-dataset'.", "UNSD (CPC)" + P + "; " + AI_EXT),
    ("3 data", "datasets and model", "id / idScheme", "standard",
     "There is no registered identifier scheme for datasets or models. A Hub URL at a commit is used.",
     "HF-MODEL; HF-OLMOMIX", "Identifier rule: repository + commit + SHA-256 per file (aic:artefactFiles). "
     "Candidate persistent scheme: SWHID (believed standardised as ISO/IEC 18670; unchecked).",
     "Hugging Face; Software Heritage" + P),
    ("3 data", "datasets and model", "idGranularity", "standard",
     "The model/batch/item distinction assumes physical copies. A commit fixes identical bytes; 'batch' is used.",
     "UNTP-SCHEMA", "Define commit-level granularity in the digital product profile.", UNTP_TEAM),
    ("3 data", "olmo-mix-1124, dolmino-mix-1124", "materialProvenance", "standard",
     "Dataset composition is by source and tokens, with component licences. materialProvenance needs mass "
     "fraction and origin country.", "HF-OLMOMIX; HF-DOLMINO", "aic:composition (source, tokens, bytes, documents, licence).",
     AI_EXT),
    ("3 data", "olmo-mix-1124, dolmino-mix-1124", "batchNumber (training revision)", "data",
     "The commits recorded are those at access. Both repos were modified after OLMo 2's release (2025-08-19, "
     "2025-10-29). The revision used for training is not published.", "HF-OLMOMIX; HF-DOLMINO",
     "Model passport cites dataset commit used.", "Ai2 (data holder)" + P),
    ("3 data", "olmo-mix-1124, dolmino-mix-1124", "producedAtFacility / countryOfProduction", "data",
     "Where the datasets were assembled is not published; required fields hold placeholders (ZZ).",
     "HF-OLMOMIX", "Make optional in the digital product profile.", UNTP_TEAM),
    ("3 data", "olmo-mix-1124, dolmino-mix-1124", "upstream sources (DCLM, Common Crawl, arXiv, ...)", "institutional",
     "No upstream source issues any credential, so the trace stops at the composition table.", "HF-OLMOMIX",
     "Dataset passports issued by upstream data publishers.", "DataComp-LM (DCLM) maintainers; Common Crawl Foundation" + P),
    ("3 data", "datasets and model", "licence (no core field)", "standard",
     "The DPP has no licence property. Licences differ by component (CC-BY-4.0, ODC-By, CC-BY-SA, MIT, Apache-2.0).",
     "HF-OLMOMIX; HF-DOLMINO; HF-MODEL", "aic:licence using SPDX identifiers.", AI_EXT + "; SPDX (Linux Foundation)" + P),
    ("3 data", "datasets", "units (tokens)", "standard",
     "Rec 20 has no token unit. Bytes (AD, E35) and counts (C62) exist.", "REC20",
     "Extension unit IRI aic unit#TOKEN; request a Rec 20 code.", "UNECE Rec 20 maintenance" + P),

    ("4 training runs", "Training at Jupiter, Augusta", "activityType", "standard",
     "GS1 CBV has no training business step. UNTP allows industry-specific schemes for activityType.",
     "UNTP-SCHEMA", "AI extension activity-type scheme: training, with stages pretraining, mid-training "
     "and model averaging.", AI_EXT + "; GS1 (CBV)" + P),
    ("4 training runs", "Training at Jupiter, Augusta", "equipment used (no core field)", "standard",
     "A MakeEvent has inputs and outputs only. GPUs are used, not consumed, and have no slot.", "UNTP-SCHEMA",
     "aic:equipmentUsed referencing the facility's installed equipment, with GPU-hours.", UNTP_TEAM + "; " + AI_EXT),
    ("4 training runs", "Training at Jupiter, Augusta", "inputProduct.disposition", "standard",
     "The disposition vocabulary assumes inputs are consumed or transformed. Datasets are non-rival, so 'active' "
     "is used.", "UNTP-SCHEMA", "Add a 'used' (not consumed) disposition or an input role.", UNTP_TEAM),
    ("4 training runs", "Training at Jupiter, Augusta", "eventDate", "data",
     "Training dates are not published. The required field holds the Hugging Face repo creation time as a "
     "placeholder.", "OLMO2; HF-MODEL", "None.", "Ai2 (data holder)" + P),
    ("4 training runs", "Training at Jupiter, Augusta", "per-site split (tokens, stages, energy)", "data",
     "The report says only 'bulk of the 7B training on Jupiter'. No fraction, stage attribution or per-site "
     "energy is published, so input quantities are empty.", "OLMO2", "aic:trainingShare.", "Ai2 (data holder)" + P),
    ("4 training runs", "Training at Jupiter, Augusta", "GPU-hours", "data",
     "GPU-hours are not published (Rec 20 also has no unit).", "OLMO2; REC20",
     "Extension unit GPU-HOUR; publish per run.", "Ai2 (data holder)" + P),
    ("4 training runs", "Training at Jupiter, Augusta", "outputProduct (distributed training)", "standard",
     "One model is produced by work at two facilities. UNTP expects one make event per output at one facility, "
     "and has no way to say two events jointly made one output.", "OLMO2; UNTP-SCHEMA",
     "Allow a MakeEvent to reference a parent process, or allow multiple madeAtFacility.", UNTP_TEAM),
    ("4 training runs", "Training runs", "units (FLOP)", "standard",
     "Rec 20 has no FLOP unit. The report gives 1.8e23 FLOP (an approximation).", "REC20; OLMO2",
     "Extension unit IRI aic unit#FLOP; request a Rec 20 code.", "UNECE Rec 20 maintenance" + P),

    ("5 model", "OLMo 2 7B", "producedAtFacility", "standard",
     "This field holds a single facility. The model was trained at two.", "OLMO2",
     "aic:producedAtFacilities, or make the field an array in the digital product profile.", UNTP_TEAM),
    ("5 model", "OLMo 2 7B", "productCategory", "standard",
     "CPC has no class for trained models.", "CPC21", "AI extension product class 'foundation-model'.",
     "UNSD (CPC)" + P + "; " + AI_EXT),
    ("5 model", "OLMo 2 7B", "relatedParty.role (developer)", "standard",
     "PartyRole has no developer role; 'producer' is used.", "UNTP-SCHEMA", "Add a developer role.", UNTP_TEAM),
    ("5 model", "OLMo 2 7B", "characteristics (architecture, parameters, files)", "standard",
     "Model attributes fit the open characteristics object but need a shared vocabulary and a parameter unit.",
     "HF-MODEL; HF-MODEL-CONFIG", "aic model characteristics vocabulary.", AI_EXT),
    ("5 model", "OLMo 2 7B", "performanceClaim (carbon emissions unit)", "knowledge",
     "Table 19 prints no unit for carbon emissions (52). tCO2eq is inferred from §6.5 ('about 154 tCO2 eq' = 52 + 101).",
     "OLMO2", "None; flag for erratum.", "Ai2 (report authors)" + P),
    ("5 model", "OLMo 2 7B", "aic:trainingTokens", "knowledge",
     "§2.3 gives 3.90T pretraining tokens; §3 and Table 3 say stage 1 stopped at 4T.", "OLMO2",
     "None; flag for erratum.", "Ai2 (report authors)" + P),
    ("5 model", "OLMo 2 7B", "performanceClaim.referenceCriteria", "institutional",
     "Claims need a reference criterion. No standard for AI training energy or emissions accounting is cited, "
     "so the report's own §6.5 method is referenced.", "OLMO2",
     "A recognised criterion for training-run energy, emissions and water.",
     "Standards body to be identified; e.g. Green Software Foundation or ISO/IEC JTC 1/SC 42 (fit unchecked)" + P),
    ("5 model", "OLMo 2 7B", "performanceClaim (scope)", "data",
     "131 MWh is GPU/node power before PUE, for pretraining only, computed with Jupiter's metrics for the whole "
     "7B. Embodied emissions, inference and the Augusta share are excluded.", "OLMO2", "None.",
     "Ai2 (data holder)" + P),
    ("5 model", "OLMo 2 7B and all claims", "conformity (DCC)", "institutional",
     "No third-party assessment exists for any claim in the chain, so no Digital Conformity Credential can be "
     "produced.", "UNTP-SCHEMA", "Assurance scheme for AI compute and training claims.",
     "Conformity assessment bodies; scheme owner to be identified" + P),
    ("5 model", "OLMo 2 7B", "redistribution and hosting after release", "institutional",
     "Out of scope. After release the model is copied, hosted, fine-tuned and served by others. Each copy is "
     "byte-identical at a commit, so UNTP's shipment-by-shipment passport model does not apply; downstream use "
     "would need MoveEvent or ModifyEvent chains that nobody issues.", "HF-MODEL",
     "Out of scope for this prototype.", "Not assigned"),

    ("all", "All credentials", "issuer / proof", "institutional",
     "None of the parties issues UNTP credentials. These are unsigned reconstructions under a fictional DID.",
     "UNTP-VERSIONS", "Issuer DIDs (did:web) for Ai2 and operators, plus signed issuance.",
     "Ai2, Cirrascale, Google, NVIDIA" + P),
    ("all", "AI extension", "@context hosting", "institutional",
     "The extension context has no resolvable home. The Playground fetches every @context and fails the context "
     "step if one cannot be loaded.", "UNTP-SCHEMA",
     "Register and host the extension via the UNTP extensions register.", "UNTP extensions register (UN/CEFACT)" + P),
    ("all", "UNTP 0.7.0", "performance metric and topic IDs", "standard",
     "The 0.7.0 samples use /performance-metric/ and /conformity-topic/ (singular); the taxonomy files use plural "
     "paths. The plural IDs are used here.", "UNTP-METRICS", "Fix the samples or the taxonomy IRIs.", UNTP_TEAM),
    ("all", "Ai2", "party identifiers", "data",
     "Ai2 has no LEI. Wikidata Q16002567 gives the wrong EIN (91-2155317, the Allen Institute). The UEI is "
     "confirmed via USAspending, not SAM.gov.", "PROPUBLICA-AI2; USASPENDING-AI2; GLEIF-NONE",
     "Obtain an LEI; correct Wikidata.", "Ai2; Wikidata editors" + P),
    ("all", "Cirrascale", "party identifiers", "data",
     "No LEI or confirmed registered identifier.", "CIRRASCALE-WEB; GLEIF-NONE", "Obtain an LEI.",
     "Cirrascale (data holder)" + P),
    ("contrast", "Olmo 3", "facility, location, energy", "data",
     "The Olmo 3 report and blog publish no facility, location or energy data (from the handoff; not re-checked "
     "in this pass).", "ODS", "Contrast only.", "Ai2 (data holder)" + P),
]


def main():
    known = set(SOURCES)
    rows = []
    for i, (chain, item, field, gtype, desc, ev, prop, owner) in enumerate(GAPS, 1):
        assert gtype in {"standard", "data", "knowledge", "institutional"}, gtype
        bad = {k.strip() for k in ev.split(";")} - known
        assert not bad, f"unknown source {bad} in gap {i}"
        rows.append({"id": f"G{i:02d}", "chain": chain, "item": item, "field": field, "gap_type": gtype,
                     "description": desc, "evidence": ev, "proposed_extension_or_profile": prop,
                     "candidate_owner_proposal": owner})
    with open(Path(__file__).parent / "gap-register.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} gaps")


if __name__ == "__main__":
    main()

"""Source register for the OLMo 2 7B UNTP reconstruction.

Every value placed in a credential or table cites one of these keys.
All sources were accessed on 2026-09-30 unless stated otherwise.
"""

ACCESSED = "2026-09-30"

SOURCES = {
    # --- OLMo 2 ---
    "OLMO2": {
        "title": "Team OLMo et al., '2 OLMo 2 Furious', arXiv:2501.00656v3 (8 October 2025)",
        "url": "https://arxiv.org/abs/2501.00656v3",
        "note": "PDF SHA-256 8614beaaf35ce5d20fde755d350bd02637bdbe5a390de237ce942c8ac4ee2dd8. "
                "v1 (31 Dec 2024) and v2 (15 Jan 2025) give identical §6.1 and Table 19 values.",
    },
    "HF-MODEL": {
        "title": "Hugging Face API: allenai/OLMo-2-1124-7B (commit 7df9a82518afdecae4e8c026b27adccc8c1f0032)",
        "url": "https://huggingface.co/api/models/allenai/OLMo-2-1124-7B?blobs=true",
        "note": "Snapshot: sources/snapshots/huggingface/model.json, model_tree.json",
    },
    "HF-MODEL-CONFIG": {
        "title": "Hugging Face: allenai/OLMo-2-1124-7B config.json at main",
        "url": "https://huggingface.co/allenai/OLMo-2-1124-7B/raw/main/config.json",
        "note": "Snapshot: sources/snapshots/huggingface/config.json",
    },
    "HF-OLMOMIX": {
        "title": "Hugging Face: allenai/olmo-mix-1124 API record and dataset card (commit 99ee6aaace88779d1ef099d36251b91101c1679b)",
        "url": "https://huggingface.co/datasets/allenai/olmo-mix-1124",
        "note": "Snapshot: sources/snapshots/huggingface/olmo-mix-1124.json, olmo-mix-1124_README.md",
    },
    "HF-DOLMINO": {
        "title": "Hugging Face: allenai/dolmino-mix-1124 API record and dataset card (commit a319f19eef1e257417b11ea8c30da266ae175557)",
        "url": "https://huggingface.co/datasets/allenai/dolmino-mix-1124",
        "note": "Snapshot: sources/snapshots/huggingface/dolmino-mix-1124.json, dolmino-mix-1124_README.md",
    },
    # --- Party identifiers ---
    "PROPUBLICA-AI2": {
        "title": "ProPublica Nonprofit Explorer API (IRS data): The Allen Institute For Artificial Intelligence, EIN 82-4083177",
        "url": "https://projects.propublica.org/nonprofits/api/v2/organizations/824083177.json",
        "note": "Address 3800 Latona Ave NE Ste 300, Seattle WA 98105-6405. Wikidata Q16002567 lists EIN 91-2155317, "
                "which ProPublica shows is the Allen Institute (bioscience, 615 Westlake Ave N): the Wikidata value is wrong for Ai2.",
    },
    "USASPENDING-AI2": {
        "title": "USAspending.gov recipient record: THE ALLEN INSTITUTE FOR ARTIFICIAL INTELLIGENCE, UEI H2VSQE9MCUU5",
        "url": "https://api.usaspending.gov/api/v2/recipient/6c5c3e27-835f-4647-8c4b-ee7239b4e69f-R/",
        "note": "UEI confirmed via USAspending, not directly in SAM.gov (SAM.gov API needs a key).",
    },
    "GLEIF-NONE": {
        "title": "GLEIF API searches: no LEI for 'Allen Institute for Artificial Intelligence' or 'Cirrascale'",
        "url": "https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]=Allen%20Institute%20for%20Artificial%20Intelligence",
        "note": "Also fuzzycompletions and fulltext; all returned zero records.",
    },
    "GLEIF-GOOGLE": {
        "title": "GLEIF LEI record: Google LLC, LEI 7ZW8QJWVPR4P1J1KQY45 (US-DE, registeredAs 3582691)",
        "url": "https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]=Google%20LLC",
        "note": "Links 'Google Cloud' (named in the report) to the legal entity Google LLC: ODS inference.",
    },
    "CIRRASCALE-WEB": {
        "title": "Cirrascale Cloud Services website (cited as report footnote 23)",
        "url": "https://www.cirrascale.com",
        "note": "No registered identifier found; USAspending has a 'CIRRASCALE CORPORATION' (UEI C31LNJJ5LN86) but "
                "whether it is the same legal entity is unconfirmed.",
    },
    # --- UNTP and code lists ---
    "UNTP-VERSIONS": {
        "title": "UNTP versions page: 0.7.0 labelled 'Pilots'; Work in Progress labelled 'Testing'; 0.6.0 'Unmaintained'",
        "url": "https://untp.unece.org/versions",
        "note": "Snapshot: sources/snapshots/untp/versions-page.html",
    },
    "UNTP-SCHEMA": {
        "title": "UNTP 0.7.0 JSON schemas (DPP, DFR, DTE, DCC) and JSON-LD context",
        "url": "https://untp.unece.org/artefacts/schema/v0.7.0/",
        "note": "Copies in schemas/v0.7.0/ (see schemas/v0.7.0/MANIFEST.md)",
    },
    "UNTP-METRICS": {
        "title": "UNTP Core Taxonomies: Performance Metrics and Conformity Topics (SKOS)",
        "url": "https://untp.unece.org/docs/0.7.0/specification/CoreTaxonomies",
        "note": "Machine-readable files from the spec-untp main branch: sources/snapshots/untp/untp-metrics.jsonld, untp-topics.jsonld. "
                "IDs use /performance-metrics/ and /conformity-topics/ (plural); 0.7.0 samples use singular paths.",
    },
    "REC20": {
        "title": "UN/CEFACT Recommendation 20 unit codes (UnitMeasureCode)",
        "url": "https://vocabulary.uncefact.org/UnitMeasureCode",
        "note": "1,828 codes parsed. Present: MWH, KWH, K6 (kilolitre), MTQ, TNE, KGM, WTT, C62, E34 (GB), E35 (TB), E36 (PB), "
                "MMK (mm2). Absent: FLOP, token, GPU-hour, parameter.",
    },
    "CPC21": {
        "title": "UN Central Product Classification (CPC) v2.1 structure",
        "url": "https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/CPC_Ver_2_1_english_structure.txt",
        "note": "",
    },
    "CPC-HS": {
        "title": "UNSD correspondence HS 2017 to CPC 2.1 (HS 8473.30 maps to CPC 45290)",
        "url": "https://unstats.un.org/unsd/classifications/Econ/tables/CPC/CPCv21_HS2017/CPC21-HS2017.csv",
        "note": "",
    },
    "ISIC4": {
        "title": "UN ISIC Rev.4 structure (6311 Data processing, hosting and related activities)",
        "url": "https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/ISIC_Rev_4_english_structure.txt",
        "note": "",
    },
    "ISO3166-ZZ": {
        "title": "ISO 3166-1 user-assigned code ZZ (used here for 'not published')",
        "url": "https://www.iso.org/iso-3166-country-codes.html",
        "note": "ZZ is user-assignable; it is not an official country. Used as an explicit placeholder.",
    },
    # --- H100 (stretch) ---
    "NV-WP": {
        "title": "NVIDIA H100 Tensor Core GPU Architecture whitepaper V1.01 (mirrored copy)",
        "url": "https://www.advancedclustering.com/wp-content/uploads/2022/03/gtc22-whitepaper-hopper.pdf",
        "note": "Spec table marked 'Preliminary specifications'. Nvidia-hosted copy only rendered as an HTML viewer.",
    },
    "NV-BLOG": {
        "title": "NVIDIA Technical Blog, 'NVIDIA Hopper Architecture In-Depth'",
        "url": "https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/",
        "note": "'fabricated using the TSMC 4N process customized for NVIDIA'; '80 billion transistors, a die size of 814 mm2'",
    },
    "NV-PRODUCT": {
        "title": "NVIDIA H100 product page",
        "url": "https://www.nvidia.com/en-us/data-center/h100/",
        "note": "H100 SXM: 80 GB, up to 700 W. H100 NVL: 94 GB, 350-400 W.",
    },
    "NV-PB-PCIE": {
        "title": "NVIDIA H100 PCIe product brief PB-11133-001_v02",
        "url": "https://www.nvidia.com/content/dam/en-zz/Solutions/gtcs22/data-center/h100/PB-11133-001_v01.pdf",
        "note": "PCIe: 80 GB HBM2e, 350 W. So '80 GB HBM3, 700 W' identifies SXM.",
    },
    "NV-10K": {
        "title": "NVIDIA Form 10-K for fiscal year ended 28 January 2024",
        "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581024000029/nvda-20240128.htm",
        "note": "'We utilize CoWoS technology'; 'We purchase memory from Micron Technology, Inc., SK Hynix Inc., and Samsung.' Not H100-specific.",
    },
    "SKH-2022": {
        "title": "SK hynix press release, 'SK hynix to Supply Industry's First HBM3 DRAM to NVIDIA' (8 June 2022)",
        "url": "https://news.skhynix.com/sk-hynix-to-supply-industrys-first-hbm3-dram-to-nvidia/",
        "note": "",
    },
    "TRENDFORCE-2024": {
        "title": "TrendForce press release (13 March 2024) on HBM3 supply for H100",
        "url": "https://www.trendforce.com/presscenter/news/20240313-12075.html",
        "note": "'primarily met by SK hynix'; Samsung entry 'late 2023, though initially minor'. Secondary source.",
    },
    "SEMIANALYSIS-2023": {
        "title": "SemiAnalysis, 'AI Capacity Constraints - CoWoS and HBM Supply Chain' (5 July 2023)",
        "url": "https://newsletter.semianalysis.com/p/ai-capacity-constraints-cowos-and",
        "note": "'Nvidia's H100 is 7-die packaged on CoWoS-S.' Secondary source.",
    },
    "GCP-GPUS": {
        "title": "Google Cloud documentation: GPU machine types (A3 Mega: H100 SXM, nvidia-h100-mega-80gb)",
        "url": "https://docs.cloud.google.com/compute/docs/gpus",
        "note": "",
    },
    "GCP-GPUDIRECT": {
        "title": "Google Cloud documentation: GPUDirect-TCPXO on a3-megagpu-8g (8 H100 GPUs, 80 GB each)",
        "url": "https://docs.cloud.google.com/compute/docs/gpus/gpudirect",
        "note": "",
    },
    "CBP-N304787": {
        "title": "US CBP ruling NY N304787 (25 June 2019): NVIDIA Tesla V100 SXM2 classified 8473.30.1180",
        "url": "https://rulings.cbp.gov/ruling/N304787",
        "note": "Analogy only; no H100-specific ruling found.",
    },
    "ETO": {
        "title": "Georgetown CSET / ETO Chip Explorer data (commit 23058d9552bb84ab3efff9434342616538090fbd, 15 Sep 2026)",
        "url": "https://github.com/georgetown-cset/eto-chip-explorer/tree/23058d9552bb84ab3efff9434342616538090fbd/data",
        "note": "Type-level only: no facilities, lots, quantities or external identifiers. No HBM/memory fabrication inputs.",
    },
    # --- Tooling ---
    "PLAYGROUND-SRC": {
        "title": "uncefact/tests-untp, packages/untp-playground v0.4.2 (branch next, commit 2e3b80e7edd56fc2f7c4843b6d5d2525ec5b054f)",
        "url": "https://github.com/uncefact/tests-untp/tree/2e3b80e7edd56fc2f7c4843b6d5d2525ec5b054f/packages/untp-playground",
        "note": "Hosted at https://test.uncefact.org/untp-playground. Read from source; no credential uploaded.",
    },
    "RI-VERIFY": {
        "title": "UNTP Reference Implementation verify page (untp.showthething.com/verify); source uncefact/tests-untp packages/reference-implementation",
        "url": "https://github.com/uncefact/tests-untp/tree/next/packages/reference-implementation",
        "note": "Unsigned sample posted to /api/v1/credentials/verify returned UNSUPPORTED_CREDENTIAL_TYPE "
                "('Only EnvelopedVerifiableCredential is supported'). 0.7.0 Handlebars templates in src/templates/v0.7.0.",
    },
    # --- ODS ---
    "ODS": {
        "title": "Open Data Services reconstruction choice (calculation, classification or placeholder)",
        "url": "",
        "note": "Not a published fact. The field matrix explains each case.",
    },
}

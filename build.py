"""Build the OLMo 2 7B UNTP credentials, field matrix and sources list.

Every value is wrapped in a V() carrying its status, source and basis. The
build writes plain JSON credentials and records the provenance of each value
so the field matrix can be generated from the same data.

Run: .venv/bin/python build.py
"""

import csv
import json
import re
from pathlib import Path

from sources import ACCESSED, SOURCES

ROOT = Path(__file__).parent
SCHEMAS = ROOT / "schemas" / "v0.7.0"
CRED_DIR = ROOT / "credentials"

PUBLISHED = "published"
NOT_PUBLISHED = "not published"
NEEDS_EXT = "needs extension vocabulary"
ISSUER = "issuer-controlled"  # VC envelope values chosen by the (fictional) issuer
CONTAINER = "container"  # object present only to hold the fields beneath it

VC_CONTEXT = "https://www.w3.org/ns/credentials/v2"
UNTP_CONTEXT = "https://vocabulary.uncefact.org/untp/0.7.0/context/"
AIC_CONTEXT = "https://example.org/untp-ai/0.1/context.jsonld"
AIC = "https://example.org/untp-ai/0.1/"
AIC_UNIT = AIC + "unit#"
BASE = "https://example.org/untp-ai/"
LINK_TYPES = "https://test.uncefact.org/vocabulary/linkTypes/"
METRICS = "https://vocabulary.uncefact.org/performance-metrics/"
TOPICS = "https://vocabulary.uncefact.org/conformity-topics/"
CPC_SCHEME = "https://unstats.un.org/unsd/classifications/Econ/cpc/"
ISIC_SCHEME = "https://unstats.un.org/unsd/classifications/Econ/isic/"

DISCLAIMER = (
    "Reconstructed by Open Data Services (ODS) from public sources for the AI Supply Chains "
    "field work (September 2026). None of the parties named in this credential issued, "
    "reviewed or endorsed it. The issuer DID is fictional and the credential is unsigned. "
    "Field-by-field sources are in field-matrix.csv."
)


class V:
    """A value with provenance."""

    def __init__(self, value, status, src=(), loc="", basis="stated", note=""):
        self.value = value
        self.status = status
        self.src = [src] if isinstance(src, str) else list(src)
        self.loc = loc
        self.basis = basis
        self.note = note


def pub(value, src, loc="", basis="stated", note=""):
    return V(value, PUBLISHED, src, loc, basis, note)


def ext(value, src=(), loc="", basis="stated", note=""):
    return V(value, NEEDS_EXT, src, loc, basis, note)


def placeholder(value, note):
    """A required field with no published value."""
    return V(value, NOT_PUBLISHED, "ODS", "", "placeholder", note)


def iss(value, note=""):
    return V(value, ISSUER, "ODS", "", "issuer-controlled", note)


def unwrap(node, path, prov, present=None):
    """Strip V wrappers and record provenance against normalised JSON paths.
    `present` collects every path that exists in the output credential."""
    if present is not None:
        vals = present.setdefault(path, [])
        if not isinstance(node, (V, dict, list)):
            vals.append(node)
    if isinstance(node, V):
        prov.append((path, node))
        return unwrap(node.value, path, prov, present)
    if isinstance(node, dict):
        return {k: unwrap(v, f"{path}.{k}", prov, present) for k, v in node.items()}
    if isinstance(node, list):
        return [unwrap(v, f"{path}[]", prov, present) for v in node]
    return node


# ---------------------------------------------------------------- shared parts

def measure(value, unit):
    return {"value": value, "unit": unit}


def cls(code, name, scheme_id, scheme_name, definition=None):
    c = {"code": code, "name": name}
    if definition:
        c["definition"] = definition
    c["schemeId"] = scheme_id
    c["schemeName"] = scheme_name
    return c


def country_us(src, loc):
    return pub({"countryCode": "US", "countryName": "United States of America"}, src, loc)


COUNTRY_UNKNOWN = placeholder(
    {"countryCode": "ZZ", "countryName": "Not published"},
    "Required field. No public source states where this was produced. ZZ is the ISO 3166 "
    "user-assigned code, used here as an explicit placeholder.",
)

ISSUER_OBJ = iss({
    "type": ["CredentialIssuer"],
    "id": "did:web:example.org",
    "name": "Example reconstruction issuer (fictional; ODS AI Supply Chains prototype)",
}, "Fictional issuer. The DID does not resolve and nothing is signed.")

SELF_SCHEME = {"type": ["IdentifierScheme"], "id": "did:web:example.org",
               "name": "ODS reconstruction identifiers (self-issued, fictional)"}

AI2 = {
    "type": ["Party"],
    "id": pub("https://projects.propublica.org/nonprofits/organizations/824083177", "PROPUBLICA-AI2",
              note="No LEI exists (GLEIF-NONE). EIN register URL used as the resolvable party identifier."),
    "name": pub("The Allen Institute For Artificial Intelligence", "PROPUBLICA-AI2"),
    "description": pub("Ai2. Non-profit AI research institute; developer of OLMo 2.", "OLMO2"),
    "registeredId": pub("82-4083177", "PROPUBLICA-AI2",
                        note="Wikidata Q16002567 gives 91-2155317, which is the Allen Institute (bioscience)."),
    "idScheme": pub({"type": ["IdentifierScheme"], "id": "https://www.irs.gov/ein",
                     "name": "US IRS Employer Identification Number (via ProPublica Nonprofit Explorer)"},
                    "PROPUBLICA-AI2", basis="ODS-assigned"),
    "registrationCountry": country_us("PROPUBLICA-AI2", ""),
    "partyAddress": pub({
        "streetAddress": "3800 Latona Ave NE Ste 300",
        "postalCode": "98105-6405",
        "addressLocality": "Seattle",
        "addressRegion": "WA",
        "addressCountry": {"countryCode": "US", "countryName": "United States of America"},
    }, ["PROPUBLICA-AI2", "USASPENDING-AI2"]),
    "organisationWebsite": pub("https://allenai.org", "OLMO2"),
    "partyAlsoKnownAs": [pub({
        "type": ["Party"],
        "id": "https://www.usaspending.gov/recipient/6c5c3e27-835f-4647-8c4b-ee7239b4e69f-R/latest",
        "name": "THE ALLEN INSTITUTE FOR ARTIFICIAL INTELLIGENCE",
        "registeredId": "H2VSQE9MCUU5",
        "idScheme": {"type": ["IdentifierScheme"], "id": "https://sam.gov",
                     "name": "US SAM.gov Unique Entity Identifier (UEI)"},
    }, "USASPENDING-AI2", note="UEI confirmed via USAspending; not checked directly in SAM.gov.")],
}

AI2_REF = {"type": ["Party"], "id": AI2["id"], "name": AI2["name"], "registeredId": AI2["registeredId"]}

CIRRASCALE = {
    "type": ["Party"],
    "id": pub("https://www.cirrascale.com", "CIRRASCALE-WEB", loc="report fn 23",
              note="No registered identifier found (no LEI; USAspending match unconfirmed)."),
    "name": pub("Cirrascale Cloud Services", "OLMO2", "§6.1.1"),
    "organisationWebsite": pub("https://www.cirrascale.com", "OLMO2", "§6.1.1 fn 23"),
}

GOOGLE = {
    "type": ["Party"],
    "id": pub("https://lei.info/7ZW8QJWVPR4P1J1KQY45", "GLEIF-GOOGLE", basis="ODS-assigned",
              note="The report names 'Google Cloud'; linking it to Google LLC is an ODS inference."),
    "name": pub("Google LLC", "GLEIF-GOOGLE"),
    "description": pub("Named as 'Google Cloud' in the OLMo 2 report.", "OLMO2", "§6.1.2"),
    "registeredId": pub("7ZW8QJWVPR4P1J1KQY45", "GLEIF-GOOGLE"),
    "idScheme": {"type": ["IdentifierScheme"], "id": "https://www.gleif.org",
                 "name": "Legal Entity Identifier (GLEIF)"},
    "registrationCountry": pub({"countryCode": "US", "countryName": "United States of America"}, "GLEIF-GOOGLE"),
}


def envelope(kind, slug, name, subject, extension=True):
    ctx = [VC_CONTEXT, UNTP_CONTEXT] + ([AIC_CONTEXT] if extension else [])
    return {
        "type": iss([kind, "VerifiableCredential"]),
        "@context": iss(ctx, "Third entry is the proposed AI compute and models extension context "
                              "(fictional URL; local copy in extension/)."),
        "id": iss(f"{BASE}credentials/{slug}"),
        "issuer": ISSUER_OBJ,
        "validFrom": iss("2026-09-30T00:00:00Z"),
        "name": iss(name),
        "description": iss(DISCLAIMER, "VCDM 2.0 'description'; allowed by the UNTP schema's additionalProperties."),
        "credentialSubject": subject,
    }


def link(url, name, link_type=None, media_type=None):
    lk = {"linkURL": url, "linkName": name}
    if media_type:
        lk["mediaType"] = media_type
    if link_type:
        lk["linkType"] = LINK_TYPES + link_type
    return lk


REPORT_LINK = link("https://arxiv.org/abs/2501.00656v3",
                   "OLMo 2 technical report (arXiv:2501.00656v3)", media_type="text/html")


def topic(slug, name):
    return {"type": ["ConformityTopic"], "id": TOPICS + slug, "name": name}


def claim(cid, name, description, metric, value, criteria, date, topics_, evidence, *, period=None):
    c = {
        "type": ["Claim"],
        "id": f"{BASE}claims/{cid}",
        "name": name,
        "description": description,
        "referenceCriteria": criteria,
        "claimDate": date,
        "claimedPerformance": [{"metric": metric, "measure": value}],
        "conformityTopic": topics_,
        "evidence": evidence,
    }
    if period:
        c["applicablePeriod"] = period
    return c


METHOD_CRITERION = ext(
    [{"type": ["Criterion"], "id": "https://arxiv.org/abs/2501.00656v3#section-6.5",
      "name": "OLMo 2 report §6.5 environmental accounting method (not a published standard)"}],
    "OLMO2", "§6.5", basis="ODS-assigned",
    note="Claim requires a reference criterion. No standard for AI training energy or emissions "
         "accounting is cited, so the report's own method is referenced.",
)
PUE_CRITERION = ext(
    [{"type": ["Criterion"], "id": "https://www.iso.org/standard/63451.html",
      "name": "ISO/IEC 30134-2 Power usage effectiveness (PUE) - assumed; not cited by the report"}],
    "ODS", basis="ODS-assigned",
    note="The report gives PUE values without citing a standard. ISO/IEC 30134-2 is the usual PUE KPI standard; "
         "citing it here is an ODS assumption.",
)
REPORT_DATE = pub("2024-12-31", "OLMO2", "arXiv submission history v1",
                  basis="ODS-assigned", note="Date first published (v1); values unchanged in v2 and v3.")


def aic_metric(slug, name):
    return {"type": ["PerformanceMetric"], "id": f"{AIC}metric/{slug}", "name": name}


def untp_metric(slug, name):
    return {"type": ["PerformanceMetric"], "id": METRICS + slug, "name": name}


# ------------------------------------------------------------------ facilities

H100_DPP_ID = f"{BASE}product/nvidia-h100-sxm5-80gb"
H100_DPP_LINK = link(f"{BASE}credentials/h100-sxm5-passport", "NVIDIA H100 SXM5 80GB product passport (stretch)", "dpp")

JUPITER_ID = f"{BASE}facility/ai2-jupiter"
AUGUSTA_ID = f"{BASE}facility/ai2-augusta"
JUPITER_NAME = "Jupiter cluster (Ai2), Austin, Texas"
AUGUSTA_NAME = "Augusta cluster (Ai2 on Google Cloud), Council Bluffs, Iowa"
JUPITER_REF = {"type": ["Facility"], "id": iss(JUPITER_ID, "ODS-minted facility URI (see DFR)."),
               "name": pub(JUPITER_NAME, "OLMO2", "§6.1.1")}
AUGUSTA_REF = {"type": ["Facility"], "id": iss(AUGUSTA_ID, "ODS-minted facility URI (see DFR)."),
               "name": pub(AUGUSTA_NAME, "OLMO2", "§6.1.2")}

ISIC_6311 = pub(cls("6311", "Data processing, hosting and related activities", ISIC_SCHEME, "UN ISIC Rev.4"),
                "ISIC4", basis="ODS-assigned",
                note="The report describes a GPU cluster; the ISIC class is an ODS classification. "
                     "No class distinguishes AI training compute.")

NOT_PUBLISHED_ADDR = "Not published"


def facility_address(locality, region, src, loc):
    return {
        "streetAddress": placeholder(NOT_PUBLISHED_ADDR, "Required field; the report gives city only."),
        "postalCode": placeholder(NOT_PUBLISHED_ADDR, "Required field; the report gives city only."),
        "addressLocality": pub(locality, src, loc),
        "addressRegion": pub(region, src, loc),
        "addressCountry": country_us(src, loc),
    }


def h100(quantity, basis_note, spec):
    return {
        "equipmentType": cls("gpu-accelerator", "GPU accelerator", f"{AIC}productClass",
                             "AI compute and models product classes (proposed)"),
        "name": "NVIDIA H100 80GB HBM3 (SXM5)",
        "manufacturer": {"id": "https://www.nvidia.com", "name": "NVIDIA Corporation"},
        "productPassport": H100_DPP_LINK,
        "quantity": quantity,
        "quantityBasis": basis_note,
        **spec,
    }


def jupiter():
    equipment = ext([
        pub(h100(
            pub(measure(1024, "C62"), "OLMO2", "§6.1.1"),
            "stated",
            {
                "memoryCapacity": pub(measure(80, "E34"), "OLMO2", "§6.1.1"),
                "memoryType": pub("HBM3", "OLMO2", "§6.1.1"),
                "thermalDesignPower": pub(measure(700, "WTT"), "OLMO2", "§6.1.1"),
                "formFactor": pub("SXM5", ["NV-WP", "NV-PB-PCIE", "NV-PRODUCT"], basis="inferred",
                                  note="Report does not name the form factor. Of H100 SXM, PCIe and NVL, only SXM "
                                       "has 80 GB HBM3 at 700 W (Nvidia specs)."),
            }), "OLMO2", "§6.1.1"),
        pub({
            "equipmentType": cls("gpu-server", "GPU server node", f"{AIC}productClass",
                                 "AI compute and models product classes (proposed)"),
            "name": "GPU server (8x H100), 2x Intel Xeon Platinum 8468, 2 TB DDR5, 18 TB NVMe",
            "quantity": measure(128, "C62"),
            "quantityBasis": "stated",
            "systemMemory": measure(2, "E35"),
            "localStorage": measure(18, "E35"),
            "gpusPerNode": measure(8, "C62"),
            "interconnect": "8x 400 Gbps InfiniBand per server (RDMA), 2-tier rail-optimised full-bisection network",
            "manufacturer": placeholder({"id": f"{BASE}party/not-published", "name": "Not published"},
                                        "Server vendor not published."),
        }, "OLMO2", "§6.1.1", basis="stated",
            note="gpusPerNode = 1,024 GPUs / 128 servers (calculated)."),
        pub({
            "equipmentType": cls("storage-cluster", "Storage cluster", f"{AIC}productClass",
                                 "AI compute and models product classes (proposed)"),
            "name": "WEKA storage cluster: 1 PB NVMe SSD (11 servers) and 5 PB HDD (12 hosts)",
            "quantity": measure(1, "C62"),
            "quantityBasis": "stated",
            "capacity": measure(6, "E36"),
            "manufacturer": {"id": "https://www.weka.io", "name": "WEKA"},
        }, "OLMO2", "§6.1.1 fn 24", note="capacity = 1 PB + 5 PB (calculated)."),
    ], "OLMO2", "§6.1.1",
        note="UNTP 0.7.0 Facility has no property for installed equipment. materialUsage covers "
             "materials consumed, not capital equipment used.")

    subject = {
        "type": ["Facility"],
        "id": iss(JUPITER_ID, "No public facility register identifier exists; ODS-minted URI."),
        "name": pub(JUPITER_NAME, "OLMO2", "§6.1, §6.1.1"),
        "description": pub(
            "128-node GPU cluster used to train most of OLMo 2 7B. Operated by Cirrascale Cloud Services. "
            "Closed-loop cabinets with air-to-water heat transfer.", "OLMO2", "§6.1, §6.1.1"),
        "idScheme": iss(SELF_SCHEME, "UNTP says to use the facility owner's party ID if self-issued; owner not published."),
        "countryOfOperation": country_us("OLMO2", "§6.1.1"),
        "processCategory": [ISIC_6311],
        "relatedParty": [
            pub({"role": "operator", "party": CIRRASCALE}, "OLMO2", "§6.1.1 'operated by Cirrascale Cloud Services'"),
        ],
        "relatedDocument": [pub(REPORT_LINK, "OLMO2")],
        "locationInformation": placeholder({}, "Required object (no required members). No coordinates or plus code published."),
        "address": facility_address("Austin", "Texas", "OLMO2", "§6.1.1"),
        "performanceClaim": [
            ext(claim("jupiter-pue", "Power usage effectiveness (PUE)",
                      "PUE of the datacentre housing Jupiter, as stated in the OLMo 2 report.",
                      aic_metric("pue", "Power usage effectiveness (ratio)"),
                      pub(measure(1.2, "C62"), "OLMO2", "§6.1.1; Table 19"),
                      PUE_CRITERION, REPORT_DATE,
                      [topic("energy-optimization", "Energy Optimization")], [REPORT_LINK]),
                "OLMO2", "§6.1.1",
                note="Value published. No UNTP performance metric for PUE; aic metric proposed. Period not stated."),
            ext(claim("jupiter-grid-intensity", "Grid carbon intensity (Austin Energy)",
                      "Carbon intensity of the electricity supplier (Austin Energy), most recently reported.",
                      untp_metric("ghg-emissions-intensity", "GHG Emissions Intensity (kg CO2 per kWh supplied)"),
                      pub(measure(0.332, "KGM"), "OLMO2", "§6.5; Table 19"),
                      METHOD_CRITERION, REPORT_DATE,
                      [topic("greenhouse-gas-emissions", "Greenhouse Gas Emissions")], [REPORT_LINK]),
                "OLMO2", "§6.5",
                note="Value published. The UNTP pattern carries the denominator (per kWh) in the metric, not the unit; "
                     "Rec 20 has no kg/kWh code. This is a grid property, not a facility property."),
            ext(claim("jupiter-wue", "Water usage effectiveness, off-site (assumed)",
                      "Off-site WUE assumed by the report authors (Reig et al. 2020); on-site WUE assumed 0.",
                      aic_metric("wue-offsite", "Water usage effectiveness, off-site (litres per kWh)"),
                      pub(measure(1.29, "LTR"), "OLMO2", "§6.5; Table 19"),
                      METHOD_CRITERION, REPORT_DATE,
                      [topic("water-conservation", "Water Conservation")], [REPORT_LINK]),
                "OLMO2", "§6.5", note="An assumption in the report, not a measurement. No UNTP WUE metric."),
        ],
        "aic:installedEquipment": equipment,
        "aic:computeTenant": ext([AI2_REF], "OLMO2", "§6.1 'two Ai2 clusters'",
                                 note="PartyRole has no tenant/customer role. Ownership of the hardware is not stated."),
    }
    return envelope("DigitalFacilityRecord", "jupiter-facility-record",
                    "Digital Facility Record: Jupiter cluster (Ai2), Austin, Texas", subject)


def augusta():
    equipment = ext([
        pub(h100(
            pub(measure(1280, "C62"), "OLMO2", "§6.1.2", basis="calculated",
                note="160 nodes x 8 GPUs; the report does not state a total."),
            "calculated",
            {
                "memoryCapacity": pub(measure(80, "E34"), "GCP-GPUDIRECT",
                                      note="Not in the report for Augusta; from Google's a3-megagpu-8g documentation."),
                "memoryType": pub("HBM3", "GCP-GPUS", note="Paraphrase of Google documentation; not in the report."),
                "formFactor": pub("SXM5", "GCP-GPUS", note="Google: A3 Mega machine types have H100 SXM GPUs."),
                "thermalDesignPower": placeholder(measure(0, "WTT"),
                                                  "Not published for Augusta. Value 0 is a placeholder only."),
            }), "OLMO2", "§6.1.2"),
        pub({
            "equipmentType": cls("cloud-vm", "Cloud virtual machine (GPU)", f"{AIC}productClass",
                                 "AI compute and models product classes (proposed)"),
            "name": "Google Cloud A3 Mega VM (a3-megagpu-8g), 8x H100",
            "quantity": measure(160, "C62"),
            "quantityBasis": "stated",
            "gpusPerNode": measure(8, "C62"),
            "interconnect": "Dedicated Ethernet NIC per GPU; GPUDirect-TCPXO, gVNIC, compact placement",
            "manufacturer": {"id": "https://lei.info/7ZW8QJWVPR4P1J1KQY45", "name": "Google LLC"},
        }, "OLMO2", "§6.1.2 fn 26",
            note="Physical host hardware (servers, CPUs) not published; the report describes VMs."),
    ], "OLMO2", "§6.1.2",
        note="UNTP 0.7.0 Facility has no property for installed equipment. For cloud capacity the tenant "
             "sees VMs, not physical assets.")

    subject = {
        "type": ["Facility"],
        "id": iss(AUGUSTA_ID, "No public facility register identifier exists; ODS-minted URI."),
        "name": pub(AUGUSTA_NAME, "OLMO2", "§6.1, §6.1.2"),
        "description": pub(
            "160-node GPU cluster provided by Google Cloud; physical servers in Council Bluffs, Iowa. "
            "Air-cooled. Used for part of OLMo 2 7B training and most of OLMo 2 13B.", "OLMO2", "§6.1, §6.1.2"),
        "idScheme": iss(SELF_SCHEME, "UNTP says to use the facility owner's party ID if self-issued; owner not published."),
        "countryOfOperation": country_us("OLMO2", "§6.1.2"),
        "processCategory": [ISIC_6311],
        "relatedParty": [
            pub({"role": "serviceProvider", "party": GOOGLE}, "OLMO2", "§6.1.2 'provided by Google Cloud'",
                note="Datacentre operator not stated; 'provided by' mapped to serviceProvider."),
        ],
        "relatedDocument": [pub(REPORT_LINK, "OLMO2")],
        "locationInformation": placeholder({}, "Required object (no required members). No coordinates or plus code published."),
        "address": facility_address("Council Bluffs", "Iowa", "OLMO2", "§6.1.2"),
        "performanceClaim": [
            ext(claim("augusta-pue", "Power usage effectiveness (PUE), campus trailing twelve months",
                      "Trailing twelve-month PUE reported for the Iowa campus.",
                      aic_metric("pue", "Power usage effectiveness (ratio)"),
                      pub(measure(1.12, "C62"), "OLMO2", "§6.1.2; Table 19"),
                      PUE_CRITERION, REPORT_DATE,
                      [topic("energy-optimization", "Energy Optimization")], [REPORT_LINK]),
                "OLMO2", "§6.1.2",
                note="Campus-level, not cluster-level. Twelve-month period dates not stated. No UNTP PUE metric."),
            ext(claim("augusta-grid-intensity", "Grid carbon intensity (Iowa state average)",
                      "State of Iowa average carbon intensity used by the report. The text gives 0.352; Table 19 gives 0.351.",
                      untp_metric("ghg-emissions-intensity", "GHG Emissions Intensity (kg CO2 per kWh supplied)"),
                      pub(measure(0.352, "KGM"), "OLMO2", "§6.5 (text); Table 19 prints 0.351",
                          note="Unresolved inconsistency in all three arXiv versions. Text value used."),
                      METHOD_CRITERION, REPORT_DATE,
                      [topic("greenhouse-gas-emissions", "Greenhouse Gas Emissions")], [REPORT_LINK]),
                "OLMO2", "§6.5", note="State average, not the facility's supply."),
            ext(claim("augusta-wue", "Water usage effectiveness, off-site (assumed)",
                      "Off-site WUE assumed by the report authors (Reig et al. 2020); on-site WUE assumed 0.",
                      aic_metric("wue-offsite", "Water usage effectiveness, off-site (litres per kWh)"),
                      pub(measure(3.10, "LTR"), "OLMO2", "§6.5; Table 19"),
                      METHOD_CRITERION, REPORT_DATE,
                      [topic("water-conservation", "Water Conservation")], [REPORT_LINK]),
                "OLMO2", "§6.5", note="An assumption in the report, not a measurement."),
        ],
        "aic:installedEquipment": equipment,
        "aic:computeTenant": ext([AI2_REF], "OLMO2", "§6.1 'two Ai2 clusters'",
                                 note="PartyRole has no tenant/customer role."),
    }
    return envelope("DigitalFacilityRecord", "augusta-facility-record",
                    "Digital Facility Record: Augusta cluster (Ai2 on Google Cloud), Council Bluffs, Iowa", subject)


# ------------------------------------------------------------------- products

MODEL_REPO = "allenai/OLMo-2-1124-7B"
MODEL_COMMIT = "7df9a82518afdecae4e8c026b27adccc8c1f0032"
MODEL_ID = f"https://huggingface.co/{MODEL_REPO}/tree/{MODEL_COMMIT}"
OLMOMIX_COMMIT = "99ee6aaace88779d1ef099d36251b91101c1679b"
OLMOMIX_ID = f"https://huggingface.co/datasets/allenai/olmo-mix-1124/tree/{OLMOMIX_COMMIT}"
DOLMINO_COMMIT = "a319f19eef1e257417b11ea8c30da266ae175557"
DOLMINO_ID = f"https://huggingface.co/datasets/allenai/dolmino-mix-1124/tree/{DOLMINO_COMMIT}"

HF_SCHEME = ext({"type": ["IdentifierScheme"], "id": "https://huggingface.co",
                 "name": "Hugging Face Hub repository at a commit (proposed AI identifier rule: repo + commit + file hash)"},
                "HF-MODEL", basis="ODS-assigned",
                note="No registered identifier scheme exists for models or datasets.")

GRANULARITY = ext("batch", "ODS", basis="ODS-assigned",
                  note="A repository commit fixes the exact bytes, so it is treated as a batch. Digital copies are "
                       "identical, so model/batch/item granularity does not map cleanly.")

CPC_ONLINE = cls("84399", "Other on-line content n.e.c.", CPC_SCHEME, "UN CPC v2.1")


def product_category(aic_code, aic_name):
    return [
        ext(CPC_ONLINE, "CPC21", basis="ODS-assigned",
            note="Nearest CPC v2.1 subclass; CPC has no class for trained models or training datasets."),
        ext(cls(aic_code, aic_name, f"{AIC}productClass", "AI compute and models product classes (proposed)"),
            "ODS", basis="ODS-assigned"),
    ]


def dataset_placeholder_facility(note):
    return placeholder({"type": ["Facility"], "id": f"{BASE}facility/not-published", "name": "Not published"}, note)


def tokens(v):
    return measure(v, AIC_UNIT + "TOKEN")


def composition_row(name, category, tok, byte_tb, docs, licence):
    row = {"name": name}
    if category:
        row["category"] = category
    row["tokenCount"] = tokens(tok)
    row["byteSize"] = measure(byte_tb, "E35")
    row["documentCount"] = measure(docs, "C62")
    row["licence"] = licence
    return row


def olmo_mix():
    comp = [
        composition_row("DCLM-Baseline", None, 3.70e12, 21.3, 2.95e9, "CC-BY-4.0"),
        composition_row("Arxiv", None, 20.8e9, 0.0772, 3.95e6, "ODC-BY"),
        composition_row("pes2o", None, 58.6e9, 0.412, 38e6, "ODC-BY"),
        composition_row("starcoder", None, 83.0e9, 0.458, 78.7e6, "ODC-BY"),
        composition_row("Algebraic-stack", None, 11.8e9, 0.044, 2.83e6, "ODC-BY"),
        composition_row("OpenWebMath", None, 12.2e9, 0.04723, 2.89e6, "ODC-BY"),
        composition_row("Wiki", None, 3.66e9, 0.0181, 6.17e6, "ODC-BY"),
    ]
    subject = {
        "type": ["Product"],
        "id": pub(OLMOMIX_ID, "HF-OLMOMIX", basis="ODS-assigned", note="Hub URL at the commit; ODS identifier rule."),
        "name": pub("OLMo 2 (November 2024) pretraining set: olmo-mix-1124", "HF-OLMOMIX", "dataset card title"),
        "description": pub("Collection of data used to train OLMo-2-1124 models (stage 1 pretraining). "
                           "Mostly DCLM-Baseline with no additional filtering.", "HF-OLMOMIX", "dataset card"),
        "idScheme": HF_SCHEME,
        "modelNumber": pub("allenai/olmo-mix-1124", "HF-OLMOMIX", note="Repository ID used as model number."),
        "batchNumber": pub(OLMOMIX_COMMIT, "HF-OLMOMIX", "API field 'sha'",
                           note="Commit at access date. The repo was last modified 2025-08-19, after OLMo 2 "
                                "release; the revision actually used for training is not published."),
        "idGranularity": GRANULARITY,
        "productCategory": product_category("training-dataset", "Training dataset"),
        "relatedParty": [pub({"role": "producer", "party": AI2_REF}, "HF-OLMOMIX", "repo owner 'allenai'")],
        "relatedDocument": [
            pub(link("https://huggingface.co/datasets/allenai/olmo-mix-1124", "Hugging Face dataset card",
                     media_type="text/html"), "HF-OLMOMIX"),
            pub(REPORT_LINK, "OLMO2"),
        ],
        "producedAtFacility": dataset_placeholder_facility(
            "Required field. Where the dataset was assembled is not published."),
        "countryOfProduction": COUNTRY_UNKNOWN,
        "characteristics": {
            "aic:tokenCount": ext(tokens(3.90e12), "HF-OLMOMIX", "Total row",
                                  note="Rec 20 has no token unit; aic unit proposed."),
            "aic:byteSize": ext(measure(22.4, "E35"), "HF-OLMOMIX", "Total row",
                                note="Uncompressed. Rec 20 has a terabyte code, but UNTP Dimension has no data-size slot."),
            "aic:documentCount": ext(measure(3.08e9, "C62"), "HF-OLMOMIX", "Total row"),
            "aic:licence": ext("ODC-By-1.0", "HF-OLMOMIX", "Licensing Information",
                               note="Also subject to Common Crawl Terms of Use. Component licences differ (see composition)."),
            "aic:composition": ext(comp, "HF-OLMOMIX", "source table",
                                   note="UNTP materialProvenance needs mass fraction and origin country; neither applies. "
                                        "Composition by tokens is an extension."),
        },
    }
    return envelope("DigitalProductPassport", "olmo-mix-1124-passport",
                    "Digital Product Passport: olmo-mix-1124 (OLMo 2 pretraining data)", subject)


def dolmino_mix():
    comp = [
        composition_row("DCLM", "HQ Web Pages", 752e9, 4.56, 606e6, "CC-BY-4.0"),
        composition_row("Flan", "HQ Web Pages", 17.0e9, 0.0982, 57.3e6, "ODC-BY"),
        composition_row("Pes2o", "STEM Papers", 58.6e9, 0.413, 38.8e6, "ODC-BY"),
        composition_row("Wiki", "Encyclopedic", 3.7e9, 0.0162, 6.17e6, "ODC-BY"),
        composition_row("StackExchange", "CodeText", 1.26e9, 0.00772, 2.48e6, "CC-BY-SA-2.5/3.0/4.0"),
        composition_row("TuluMath", "Synth Math", 230e6, 0.00103, 220e3, "ODC-BY"),
        composition_row("DolminoSynthMath", "Synth Math", 28.7e6, 0.000163, 725e3, "ODC-BY"),
        composition_row("TinyGSM-MIND", "Synth Math", 6.48e9, 0.02552, 17e6, "ODC-BY"),
        composition_row("MathCoder2", "Synth Math", 3.87e9, 0.01848, 2.83e6, "Apache-2.0"),
        composition_row("Metamath-owmfilter", "Math", 84.2e6, 0.000741, 383e3, "CC-BY-SA-4.0"),
        composition_row("CodeSearchNet-owmfilter", "Math", 1.78e6, 0.0000298, 7.27e3, "ODC-BY"),
        composition_row("GSM8K", "Math", 2.74e6, 0.0000253, 17.6e3, "MIT"),
    ]
    mix50 = [
        {"name": "DCLM Baseline", "sourcePercent": 3.23, "mixPercent": 47.2},
        {"name": "FLAN", "sourcePercent": 50.0, "mixPercent": 16.6},
        {"name": "pes2o", "sourcePercent": 5.15, "mixPercent": 5.85},
        {"name": "Wiki", "sourcePercent": 100, "mixPercent": 7.11},
        {"name": "StackExchange", "sourcePercent": 100, "mixPercent": 2.45},
        {"name": "Stage 2 Math", "sourcePercent": 100, "mixPercent": 20.8},
    ]
    subject = {
        "type": ["Product"],
        "id": pub(DOLMINO_ID, "HF-DOLMINO", basis="ODS-assigned", note="Hub URL at the commit; ODS identifier rule."),
        "name": pub("DOLMino dataset mix for OLMo 2 stage 2 annealing: dolmino-mix-1124", "HF-DOLMINO", "dataset card title"),
        "description": pub("Mixture of high-quality data used for the second stage (mid-training) of OLMo 2. "
                           "Stage 2 uses a 50B, 100B or 300B token sample; OLMo 2 7B used the 50B sample three times "
                           "and averaged the results.", ["HF-DOLMINO", "OLMO2"], "dataset card; report §2.3, §4.5"),
        "idScheme": HF_SCHEME,
        "modelNumber": pub("allenai/dolmino-mix-1124", "HF-DOLMINO"),
        "batchNumber": pub(DOLMINO_COMMIT, "HF-DOLMINO", "API field 'sha'",
                           note="Commit at access date; last modified 2025-10-29. Training revision not published."),
        "idGranularity": GRANULARITY,
        "productCategory": product_category("training-dataset", "Training dataset"),
        "relatedParty": [pub({"role": "producer", "party": AI2_REF}, "HF-DOLMINO", "repo owner 'allenai'")],
        "relatedDocument": [
            pub(link("https://huggingface.co/datasets/allenai/dolmino-mix-1124", "Hugging Face dataset card",
                     media_type="text/html"), "HF-DOLMINO"),
            pub(REPORT_LINK, "OLMO2"),
        ],
        "producedAtFacility": dataset_placeholder_facility(
            "Required field. Where the dataset was assembled is not published."),
        "countryOfProduction": COUNTRY_UNKNOWN,
        "characteristics": {
            "aic:tokenCount": ext(tokens(843e9), "HF-DOLMINO", "Total row"),
            "aic:byteSize": ext(measure(5.14, "E35"), "HF-DOLMINO", "Total row"),
            "aic:documentCount": ext(measure(732e6, "C62"), "HF-DOLMINO", "Total row"),
            "aic:licence": ext("ODC-By-1.0", "HF-DOLMINO", "Licensing Information",
                               note="Also subject to Common Crawl Terms of Use; component licences differ."),
            "aic:composition": ext(comp, "HF-DOLMINO", "Source Sizes table"),
            "aic:sampleComposition": ext({"sampleSize": tokens(50e9), "components": mix50},
                                         "HF-DOLMINO", "Mix Compositions table, 50B column",
                                         note="The 50B sample is the one used for OLMo 2 7B (report §4.5)."),
        },
    }
    return envelope("DigitalProductPassport", "dolmino-mix-1124-passport",
                    "Digital Product Passport: dolmino-mix-1124 (OLMo 2 mid-training data)", subject)


def model_files():
    tree = json.loads((ROOT / "sources/snapshots/huggingface/model_tree.json").read_text())
    return [{"fileName": f["path"], "sha256": f["lfs"]["oid"], "byteSize": measure(f["size"], "AD")}
            for f in tree if f["path"].endswith(".safetensors")]


def olmo2_model():
    files = model_files()
    total_bytes = sum(f["byteSize"]["value"] for f in files)
    subject = {
        "type": ["Product"],
        "id": pub(MODEL_ID, "HF-MODEL", basis="ODS-assigned", note="Hub URL at the commit; ODS identifier rule."),
        "name": pub("OLMo 2 7B (OLMo-2-1124-7B)", ["HF-MODEL", "OLMO2"]),
        "description": pub("7B-parameter open language model (base, pretrained and mid-trained). Stage 1 on "
                           "olmo-mix-1124; stage 2 on three 50B-token samples of dolmino-mix-1124, averaged.",
                           ["OLMO2", "HF-MODEL"], "§2.3, §4.5"),
        "idScheme": HF_SCHEME,
        "modelNumber": pub(MODEL_REPO, "HF-MODEL"),
        "batchNumber": pub(MODEL_COMMIT, "HF-MODEL", "API field 'sha'",
                           note="Commit at access date (last modified 2025-01-06)."),
        "idGranularity": GRANULARITY,
        "productCategory": product_category("foundation-model", "Pretrained foundation model (base)"),
        "relatedParty": [pub({"role": "producer", "party": AI2}, ["OLMO2", "HF-MODEL"],
                             note="No 'developer' role in PartyRole; 'producer' used.")],
        "relatedDocument": [
            pub(link(f"{BASE}credentials/training-run-jupiter", "Training run at Jupiter (DTE)", "dte"), "ODS",
                basis="ODS-assigned"),
            pub(link(f"{BASE}credentials/training-run-augusta", "Training run at Augusta (DTE)", "dte"), "ODS",
                basis="ODS-assigned"),
            pub(link(f"{BASE}credentials/olmo-mix-1124-passport", "olmo-mix-1124 (DPP)", "dpp"), "ODS",
                basis="ODS-assigned"),
            pub(link(f"{BASE}credentials/dolmino-mix-1124-passport", "dolmino-mix-1124 (DPP)", "dpp"), "ODS",
                basis="ODS-assigned"),
            pub(link(f"https://huggingface.co/{MODEL_REPO}", "Hugging Face model card", media_type="text/html"),
                "HF-MODEL"),
            pub(REPORT_LINK, "OLMO2"),
        ],
        "producedAtFacility": ext(JUPITER_REF, "OLMO2", "§6.1 'bulk of the 7B training on Jupiter'",
                                  note="Single-valued in UNTP. Training was split across Jupiter and Augusta; "
                                       "Augusta is recorded in aic:producedAtFacilities and the DTEs."),
        "countryOfProduction": country_us("OLMO2", "§6.1.1, §6.1.2 (both clusters in the US)"),
        "characteristics": {
            "aic:architecture": ext("Olmo2ForCausalLM (decoder-only transformer)", "HF-MODEL-CONFIG", "architectures"),
            "aic:parameterCount": ext(measure(7298617344, AIC_UNIT + "PARAMETER"), "HF-MODEL",
                                      "safetensors.total", note="Rec 20 has no parameter unit."),
            "aic:layerCount": ext(32, "HF-MODEL-CONFIG", "num_hidden_layers"),
            "aic:hiddenSize": ext(4096, "HF-MODEL-CONFIG", "hidden_size"),
            "aic:contextLength": ext(measure(4096, AIC_UNIT + "TOKEN"), "HF-MODEL-CONFIG", "max_position_embeddings"),
            "aic:vocabularySize": ext(100352, "HF-MODEL-CONFIG", "vocab_size"),
            "aic:tensorDtype": ext("float32", "HF-MODEL-CONFIG", "torch_dtype"),
            "aic:licence": ext("Apache-2.0", "HF-MODEL", "cardData.license"),
            "aic:artefactFiles": ext(files, "HF-MODEL", "tree/main lfs.oid, size",
                                     note="Identifier rule: repo + commit + SHA-256 of each weights file."),
            "aic:totalArtefactSize": ext(measure(total_bytes, "AD"), "HF-MODEL", basis="calculated",
                                         note="Sum of the six safetensors files."),
            "aic:trainingCompute": ext(measure(1.8e23, AIC_UNIT + "FLOP"), "OLMO2", "Table 6",
                                       note="Approximation (6 x tokens x parameters, Kaplan et al.). Rec 20 has no FLOP unit."),
            "aic:trainingTokens": ext(measure(4.05e12, AIC_UNIT + "TOKEN"), "OLMO2", "§2.3",
                                      note="3.90T stage 1 + 3 x 50B stage 2. §3 and Table 3 say stage 1 stopped at 4T; "
                                           "unresolved inconsistency."),
            "aic:trainingData": ext([
                {"dataset": {"id": OLMOMIX_ID, "name": "olmo-mix-1124"},
                 "stage": "pretraining", "tokensUsed": tokens(3.90e12)},
                {"dataset": {"id": DOLMINO_ID, "name": "dolmino-mix-1124"},
                 "stage": "mid-training", "tokensUsed": tokens(150e9),
                 "note": "Three separate 50B-token runs with different data orders, then averaged"},
            ], ["OLMO2", "HF-MODEL"], "§2.3, §4.5; cardData.datasets"),
        },
        "performanceClaim": [
            ext(claim("olmo2-7b-gpu-energy", "Total GPU power, pretraining (before PUE)",
                      "Node power sampled every 25 ms, averaged over training and multiplied by node count. "
                      "Pretraining only; lower bound; excludes embodied emissions and inference.",
                      untp_metric("total-energy-consumption", "Total Energy Consumption"),
                      pub(measure(131, "MWH"), "OLMO2", "Table 19; §6.5"),
                      METHOD_CRITERION, REPORT_DATE,
                      [topic("energy-optimization", "Energy Optimization")], [REPORT_LINK]),
                "OLMO2", "Table 19",
                note="Computed with Jupiter's metrics for the whole 7B; no per-site split. Metric fit is approximate: "
                     "the figure excludes PUE overhead (x1.2 gives 157 MWh, ODS calculation)."),
            ext(claim("olmo2-7b-emissions", "Carbon emissions, pretraining (location-based)",
                      "P_GPU x PUE x carbon intensity. 131 MWh x 1.2 x 0.332 = 52.2 t (ODS check).",
                      untp_metric("total-ghg-emissions", "Total GHG Emissions"),
                      pub(measure(52, "TNE"), "OLMO2", "Table 19; §6.5",
                          note="Table 19 prints no unit. tCO2eq inferred from §6.5 ('about 154 tCO2 eq' = 52 + 101)."),
                      METHOD_CRITERION, REPORT_DATE,
                      [topic("greenhouse-gas-emissions", "Greenhouse Gas Emissions")], [REPORT_LINK]),
                "OLMO2", "Table 19",
                note="Pretraining only; not a product carbon footprint. Scope attribution not stated."),
            ext(claim("olmo2-7b-water", "Water consumption, pretraining (estimated)",
                      "P_GPU x PUE x (WUE on-site 0 + WUE off-site 1.29 L/kWh).",
                      untp_metric("water-consumption", "Water Consumption"),
                      pub(measure(202, "MTQ"), "OLMO2", "Table 19 (202 kL)", basis="converted",
                          note="202 kL = 202 m3; UNTP metric recommends MTQ."),
                      METHOD_CRITERION, REPORT_DATE,
                      [topic("water-conservation", "Water Conservation")], [REPORT_LINK]),
                "OLMO2", "Table 19"),
        ],
        "aic:producedAtFacilities": ext([JUPITER_REF, AUGUSTA_REF], "OLMO2", "§6.1",
                                        note="Share of training at each site not published."),
    }
    return envelope("DigitalProductPassport", "olmo-2-7b-passport",
                    "Digital Product Passport: OLMo 2 7B (allenai/OLMo-2-1124-7B)", subject)


# --------------------------------------------------------------------- events

def event_product(pid, name, model_number, commit, qty=None, disposition=None):
    p = {"product": {"type": ["Product"], "id": pid, "name": name, "idGranularity": "batch",
                     "modelNumber": model_number, "batchNumber": commit}}
    if qty is not None:
        p["quantity"] = qty
    if disposition:
        p["disposition"] = disposition
    return p


TRAINING_ACTIVITY = ext(cls("training", "Model training",
                            f"{AIC}activityType", "AI compute and models activity types (proposed)",
                            "Producing or updating model weights by optimisation over a dataset. Covers "
                            "pretraining and mid-training; the stage split by site is not published."),
                        "ODS", basis="ODS-assigned",
                        note="GS1 CBV BizStep has no training step. UNTP allows industry-specific schemes for activityType.")

EVENT_DATE_NOTE = ("Required field. Training dates are not published. The Hugging Face repository creation "
                   "time (2024-10-29T21:08:22Z) is used as a placeholder; it is not the event date.")


def training_event(site, facility_ref, facility_record, share_text, loc):
    fname = facility_ref["name"].value
    ev = {
        "type": iss(["MakeEvent", "LifecycleEvent"]),
        "id": iss(f"{BASE}event/olmo-2-7b-training-{site}"),
        "name": pub(f"OLMo 2 7B training at {fname.split(',')[0]}", "OLMO2", loc),
        "description": pub(f"Part of OLMo 2 7B training ({share_text}). Beaker moved workloads between clusters; "
                           "which stages or tokens ran here is not published.", "OLMO2", loc),
        "eventDate": placeholder("2024-10-29T21:08:22Z", EVENT_DATE_NOTE),
        "activityType": TRAINING_ACTIVITY,
        "relatedParty": [pub({"role": "producer", "party": AI2_REF}, "OLMO2", "§6.1",
                             note="Ai2 ran the training (Beaker). No 'trainer' role.")],
        "relatedDocument": [
            pub(REPORT_LINK, "OLMO2"),
            pub(link(facility_record, f"{fname} (DFR)", "dfr"), "ODS", basis="ODS-assigned",
                note="linkType 'dfr' follows the dpp/dcc/dte pattern; not confirmed in the 0.7.0 link-type vocabulary."),
        ],
        "inputProduct": [
            ext(event_product(OLMOMIX_ID, "olmo-mix-1124", "allenai/olmo-mix-1124", OLMOMIX_COMMIT,
                              disposition="active"), "OLMO2", "§2.3",
                note="Quantity (tokens at this site) not published. Datasets are not consumed by training; "
                     "'active' is the nearest disposition. No input role for 'training data' vs 'material'."),
            ext(event_product(DOLMINO_ID, "dolmino-mix-1124", "allenai/dolmino-mix-1124", DOLMINO_COMMIT,
                              disposition="active"), "OLMO2", "§2.3",
                note="Not published whether mid-training ran at this site; listed as a possible input."),
        ],
        "outputProduct": [
            ext(event_product(MODEL_ID, "OLMo 2 7B", MODEL_REPO, MODEL_COMMIT, disposition="new"),
                "OLMO2", "§6.1",
                note="Both events contribute to one output. UNTP assumes one make event per output at one facility."),
        ],
        "madeAtFacility": pub(facility_ref, "OLMO2", loc),
        "aic:equipmentUsed": ext([{
            "equipment": "NVIDIA H100 80GB HBM3 (SXM5)",
            "productPassport": H100_DPP_LINK,
            "gpuHours": placeholder(measure(0, AIC_UNIT + "GPU-HOUR"), "GPU-hours not published; 0 is a placeholder."),
        }], "OLMO2", loc,
            note="UNTP distinguishes inputs (inputProduct) from nothing else: no slot for equipment used but not "
                 "consumed. Extension proposed."),
        "aic:trainingShare": placeholder("not published", f"Report says only: {share_text}."),
    }
    return ev


def training_jupiter():
    ev = training_event("jupiter", JUPITER_REF, f"{BASE}credentials/jupiter-facility-record",
                        "the bulk of 7B training", "§6.1; §6.5")
    return envelope("DigitalTraceabilityEvent", "training-run-jupiter",
                    "Digital Traceability Event: OLMo 2 7B training at Jupiter", [ev])


def training_augusta():
    ev = training_event("augusta", AUGUSTA_REF, f"{BASE}credentials/augusta-facility-record",
                        "a minority share; 7B trained 'partially on both clusters'", "§6.1")
    return envelope("DigitalTraceabilityEvent", "training-run-augusta",
                    "Digital Traceability Event: OLMo 2 7B training at Augusta", [ev])


# --------------------------------------------------------------- stretch: H100

NVIDIA = {"type": ["Party"], "id": "https://www.nvidia.com", "name": "NVIDIA Corporation"}
TSMC = {"type": ["Party"], "id": "https://www.tsmc.com", "name": "Taiwan Semiconductor Manufacturing Company (TSMC)"}
SKHYNIX = {"type": ["Party"], "id": "https://www.skhynix.com", "name": "SK hynix Inc."}


def h100_passport():
    subject = {
        "type": ["Product"],
        "id": iss(H100_DPP_ID, "No public GTIN or registered part number for the SXM5 module; ODS-minted URI."),
        "name": pub("NVIDIA H100 Tensor Core GPU, SXM5, 80 GB HBM3", ["NV-PRODUCT", "NV-WP"]),
        "description": pub("Data-centre GPU accelerator module (Hopper architecture, GH100 die). "
                           "The lots installed at Jupiter and Augusta are not identified publicly.",
                           ["NV-BLOG", "NV-WP"]),
        "idScheme": iss(SELF_SCHEME),
        "modelNumber": placeholder("H100 SXM5 80GB",
                                   "Nvidia part number for the SXM5 module (699-2G520-...) appears only on reseller "
                                   "listings; unconfirmed."),
        "idGranularity": pub("model", "ODS", basis="ODS-assigned",
                             note="Model level: no lot, batch or serial numbers for the installed GPUs are published."),
        "productCategory": [
            pub(cls("45290", "Parts and accessories of computing machines", CPC_SCHEME, "UN CPC v2.1"),
                ["CPC21", "CPC-HS", "CBP-N304787"], basis="ODS-assigned",
                note="Via HS 8473.30 by analogy with CBP ruling N304787 (V100 SXM2). No H100 ruling found."),
            ext(cls("gpu-accelerator", "GPU accelerator", f"{AIC}productClass",
                    "AI compute and models product classes (proposed)"), "ODS", basis="ODS-assigned"),
        ],
        "relatedParty": [
            pub({"role": "brandOwner", "party": NVIDIA}, ["NV-PRODUCT", "NV-BLOG"],
                note="Nvidia is designer and brand owner. PartyRole has no 'designer' role."),
            pub({"role": "manufacturer", "party": TSMC}, "NV-BLOG",
                "'fabricated using the TSMC 4N process customized for NVIDIA'",
                note="TSMC fabricates the GH100 die, not the finished module; UNTP roles apply to the whole product."),
        ],
        "relatedDocument": [
            pub(link("https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/",
                     "NVIDIA Hopper Architecture In-Depth", media_type="text/html"), "NV-BLOG"),
            pub(link("https://www.nvidia.com/en-us/data-center/h100/", "NVIDIA H100 product page",
                     media_type="text/html"), "NV-PRODUCT"),
        ],
        "producedAtFacility": placeholder({"type": ["Facility"], "id": f"{BASE}facility/not-published",
                                           "name": "Not published"},
                                          "Required field. Module assembly site not published. Nvidia's 10-K names "
                                          "contract manufacturers (Hon Hai, Wistron, Fabrinet) without product mapping."),
        "countryOfProduction": COUNTRY_UNKNOWN,
        "characteristics": {
            "aic:architecture": ext("Hopper", "NV-BLOG"),
            "aic:die": ext("GH100", "NV-BLOG"),
            "aic:processNode": ext("TSMC 4N (customised for NVIDIA)", "NV-BLOG"),
            "aic:transistorCount": ext(measure(80e9, "C62"), "NV-BLOG"),
            "aic:dieArea": ext(measure(814, "MMK"), "NV-BLOG"),
            "aic:memoryCapacity": ext(measure(80, "E34"), ["NV-WP", "NV-PRODUCT"]),
            "aic:memoryType": ext("HBM3 (5 active stacks)", "NV-WP"),
            "aic:thermalDesignPower": ext(measure(700, "WTT"), ["NV-WP", "NV-PRODUCT"], note="'Up to 700W (configurable)'"),
            "aic:formFactor": ext("SXM5", "NV-WP"),
            "aic:components": ext([
                {"component": "GH100 GPU die", "supplier": TSMC, "process": "TSMC 4N",
                 "evidence": "NV-BLOG", "status": "confirmed"},
                {"component": "HBM3 memory stacks (5 active)", "supplier": SKHYNIX,
                 "evidence": "SKH-2022; TRENDFORCE-2024", "status": "confirmed for H100 HBM3 supply generally",
                 "note": "Samsung entry late 2023 'initially minor' (TrendForce, secondary). Which supplier's stacks "
                         "are in the Jupiter/Augusta GPUs is unknown."},
                {"component": "CoWoS-S 2.5D package (interposer)", "supplier": TSMC,
                 "evidence": "NV-10K; SEMIANALYSIS-2023", "status": "secondary sources",
                 "note": "Nvidia 10-K confirms CoWoS use generally; H100-specific CoWoS-S from SemiAnalysis/TechInsights."},
            ], ["NV-BLOG", "SKH-2022", "TRENDFORCE-2024", "NV-10K", "SEMIANALYSIS-2023"],
                note="UNTP materialProvenance needs mass fractions and origin countries, which are not published. "
                     "Component-level bill of materials proposed as an extension."),
            "aic:chipExplorerInputs": ext([
                {"etoId": "N2", "name": "Discrete GPUs", "type": "design_resource", "providers": "NVIDIA (P11), AMD, others"},
                {"etoId": "N0", "name": "Chip design", "type": "process", "stage": "S1 Design"},
                {"etoId": "N25", "name": "Photolithography", "type": "process", "stage": "S2 Fabrication"},
                {"etoId": "N69", "name": "Assembly and packaging", "type": "process", "stage": "S3 ATP"},
                {"etoId": "N109", "name": "Fabrication tools (for advanced packaging)", "type": "tool_resource"},
                {"etoId": "N78", "name": "Testing", "type": "process", "stage": "S3 ATP"},
                {"etoId": "N99", "name": "Finished logic chip", "type": "ultimate_output"},
            ], "ETO", "inputs.csv, sequence.csv, provision.csv",
                note="Chip Explorer is type-level; it has no firm-level foundry row for TSMC and no HBM inputs. "
                     "Mapping the H100 to these inputs is an ODS reading."),
        },
    }
    return envelope("DigitalProductPassport", "h100-sxm5-passport",
                    "Digital Product Passport (stretch): NVIDIA H100 SXM5 80GB, model level", subject)


CREDENTIALS = [
    # (file stem, builder, schema family, chain position)
    ("01-h100-sxm5-passport", h100_passport, "DPP", "1 chips (stretch)"),
    ("02-jupiter-facility-record", jupiter, "DFR", "2 sites"),
    ("03-augusta-facility-record", augusta, "DFR", "2 sites"),
    ("04-olmo-mix-1124-passport", olmo_mix, "DPP", "3 data"),
    ("05-dolmino-mix-1124-passport", dolmino_mix, "DPP", "3 data"),
    ("06-training-run-jupiter", training_jupiter, "DTE", "4 training runs"),
    ("07-training-run-augusta", training_augusta, "DTE", "4 training runs"),
    ("08-olmo-2-7b-passport", olmo2_model, "DPP", "5 model"),
]


# ------------------------------------------------------------- field matrix

def flatten_schema(schema, node, path, required, seen, out):
    if "$ref" in node:
        name = node["$ref"].split("/")[-1]
        target = dict(schema["$defs"][name])
        if "description" in node:
            target["description"] = node["description"]
        if name in seen:
            out.append((path, "object (recursive)", required, target.get("description", "")))
            return
        return flatten_schema(schema, target, path, required, seen | {name}, out)
    if "oneOf" in node and "properties" not in node:
        # DTE LifecycleEvent: flatten MakeEvent only (the event type used here)
        make = [o for o in node["oneOf"] if o.get("$ref", "").endswith("/MakeEvent")][0]
        return flatten_schema(schema, make, path, required, seen, out)
    typ = node.get("type", "")
    if typ == "array" and "items" in node:
        item = node["items"]
        if "$ref" in item or item.get("type") == "object":
            return flatten_schema(schema, {**item, "description": node.get("description", "")},
                                  path + "[]", required, seen, out)
        out.append((path, f"array<{item.get('type', '')}>", required, node.get("description", "")))
        return
    if typ == "object" or "properties" in node:
        out.append((path, "object", required, node.get("description", "")))
        req = set(node.get("required", []))
        for key, sub in node.get("properties", {}).items():
            flatten_schema(schema, sub, f"{path}.{key}", key in req, seen, out)
        return
    enum = node.get("enum")
    out.append((path, typ + (f" enum{enum}" if enum else ""), required, node.get("description", "")))


SCHEMA_FILES = {"DPP": "DigitalProductPassport.json", "DFR": "DigitalFacilityRecord.json",
                "DTE": "DigitalTraceabilityEvent.json", "DCC": "ConformityCredential.json"}

# Unfilled core fields that do not apply to the item, by credential family and path prefix.
NOT_APPLICABLE = {
    "DPP-digital": ["$.credentialSubject.packaging",
                    "$.credentialSubject.productLabel", "$.credentialSubject.expiryDate",
                    "$.credentialSubject.productImage", "$.credentialSubject.itemNumber"],
    "DPP-h100": ["$.credentialSubject.packaging", "$.credentialSubject.expiryDate",
                 "$.credentialSubject.batchNumber", "$.credentialSubject.itemNumber"],
    "DFR": [],
    "DTE": ["$.credentialSubject[].sensorData"],
    "ALL": ["$.credentialStatus", "$.renderMethod", "$.issuingSoftware", "$.validUntil",
            "$.issuer.issuerAlsoKnownAs"],
}
# Unfilled core fields where the concept applies but the core vocabulary does not fit.
NEEDS_EXT_UNFILLED = {
    "$.credentialSubject.materialProvenance": (
        {"DPP-digital", "DPP-h100"},
        "Composition of datasets and models is by tokens or components, not mass fraction and origin "
        "country; for the H100 no mass fractions are published. See aic:composition / aic:components."),
    "$.credentialSubject.dimensions": (
        {"DPP-digital"}, "No data-size dimension (bytes); see aic:byteSize / aic:totalArtefactSize."),
}


def short(value):
    s = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return s if len(s) <= 160 else s[:157] + "..."


def matrix_rows(stem, family, chain, prov, present):
    schema = json.loads((SCHEMAS / SCHEMA_FILES[family]).read_text())
    flat = []
    flatten_schema(schema, schema, "$", True, set(), flat)
    flat_paths = {p for p, *_ in flat}
    by_path = {}
    for path, v in prov:
        by_path.setdefault(path, []).append(v)
    kind = {"DPP": "DPP-h100" if "h100" in stem else "DPP-digital"}.get(family, family)
    na = NOT_APPLICABLE.get(kind, []) + NOT_APPLICABLE["ALL"]

    def src_text(vs):
        keys = []
        for v in vs:
            for s in v.src:
                if s not in keys:
                    keys.append(s)
        return "; ".join(keys)

    rows = []
    covered = set()
    for path, typ, req, desc in flat:
        vs = by_path.get(path)
        if vs is None:
            # inherit from the nearest wrapped ancestor
            anc = path
            while anc not in by_path and ("." in anc or "[" in anc):
                anc = re.sub(r"(\.[^.\[]+|\[\])$", "", anc)
                if anc == "$":
                    break
            vs_anc = by_path.get(anc)
        else:
            vs_anc = None
        applicable = "yes"
        if vs is None and path not in present:
            vs_anc = None  # absent from the credential: never inherit
        if vs is None and vs_anc is None and path in present:
            is_container = typ.startswith("object") or any(
                p.startswith(path + ".") or p.startswith(path + "[]") for p in present if p != path)
            if is_container:
                status, note = CONTAINER, "Structural: see the fields beneath."
            else:
                status, note = ISSUER, "Constant or structural value set by the issuer."
            rows.append({
                "chain": chain, "credential": stem, "family": family, "path": path,
                "in_core_schema": "yes", "required": "yes" if req else "no", "type": typ,
                "status": status, "applicable": "yes", "value": "", "basis": "", "source": "",
                "locator": "", "note": note, "schema_description": short(desc.replace("\n", " ")),
            })
            continue
        if vs is None and vs_anc is None:
            status, value, basis, src, loc, note = NOT_PUBLISHED, "", "", "", "", ""
            for pre, (kinds, why) in NEEDS_EXT_UNFILLED.items():
                if path.startswith(pre) and kind in kinds:
                    status, note = NEEDS_EXT, why
            if any(path.startswith(p) for p in na):
                applicable = "no"
                note = note or "Not applicable to this item or not used by this reconstruction."
        else:
            use = vs or vs_anc
            v = use[-1]
            status = v.status
            basis = v.basis
            src = src_text(use)
            loc = "; ".join(dict.fromkeys(x.loc for x in use if x.loc))
            note = "; ".join(dict.fromkeys(x.note for x in use if x.note))
            value = " | ".join(dict.fromkeys(short(x) for x in present.get(path, [])))
            if vs is None:
                note = (note + " " if note else "") + "(inherited from parent field)"
        covered.add(path)
        rows.append({
            "chain": chain, "credential": stem, "family": family, "path": path,
            "in_core_schema": "yes", "required": "yes" if req else "no", "type": typ,
            "status": status, "applicable": applicable, "value": value, "basis": basis,
            "source": src, "locator": loc, "note": note,
            "schema_description": short(desc.replace("\n", " ")),
        })
    # extension properties and any wrapped values not in the core schema
    seen_ext = set()
    for path, v in prov:
        if path in flat_paths or path in seen_ext:
            continue
        seen_ext.add(path)
        vs = by_path[path]
        rows.append({
            "chain": chain, "credential": stem, "family": family, "path": path,
            "in_core_schema": "no" if "aic:" in path else "yes (additional property)",
            "required": "no", "type": "extension" if "aic:" in path else "",
            "status": vs[-1].status, "applicable": "yes",
            "value": " | ".join(dict.fromkeys(short(x) for x in present.get(path, []))),
            "basis": vs[-1].basis, "source": src_text(vs),
            "locator": "; ".join(dict.fromkeys(x.loc for x in vs if x.loc)),
            "note": "; ".join(dict.fromkeys(x.note for x in vs if x.note)),
            "schema_description": "Proposed AI compute and models extension property" if "aic:" in path else "",
        })
    return rows


def dcc_rows():
    schema = json.loads((SCHEMAS / SCHEMA_FILES["DCC"]).read_text())
    flat = []
    flatten_schema(schema, schema, "$", True, set(), flat)
    return [{
        "chain": "all", "credential": "(no DCC produced)", "family": "DCC", "path": p,
        "in_core_schema": "yes", "required": "yes" if r else "no", "type": t,
        "status": NOT_PUBLISHED, "applicable": "yes", "value": "", "basis": "", "source": "", "locator": "",
        "note": "No third-party conformity assessment is published for any claim in this chain "
                "(PUE, grid intensity, energy, emissions, water, dataset licences).",
        "schema_description": short(d.replace("\n", " ")),
    } for p, t, r, d in flat]


# -------------------------------------------------------------------- outputs

def write_sources_md():
    lines = ["# Sources", "",
             f"All sources accessed {ACCESSED} unless noted. Keys are cited in `field-matrix.csv` "
             "(`source` column) and in `sources.py`.", "",
             "| Key | Source | URL | Note |", "|---|---|---|---|"]
    for key, s in SOURCES.items():
        note = s["note"].replace("|", "/")
        lines.append(f"| `{key}` | {s['title']} | {s['url']} | {note} |")
    (ROOT / "sources.md").write_text("\n".join(lines) + "\n")


def aic_terms(node, found):
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("aic:"):
                found.add(k)
            aic_terms(v, found)
    elif isinstance(node, list):
        for v in node:
            aic_terms(v, found)
    return found


def write_extension_context(terms):
    """JSON-LD context for the proposed extension. Each top-level aic: term carries a
    property-scoped context so nested keys land in the aic namespace, and nested
    value/unit reuse the UNTP Measure terms (unit codes expand against Rec 20)."""
    scoped = {
        "@vocab": AIC,
        "value": {"@id": "untp:value"},
        "unit": {"@id": "untp:unit", "@type": "@vocab",
                 "@context": {"@vocab": "https://vocabulary.uncefact.org/UnitMeasureCode#"}},
        "linkURL": {"@id": "untp:linkURL", "@type": "@id"},
        "linkName": {"@id": "untp:linkName"},
        "linkType": {"@id": "untp:linkType", "@type": "@id"},
        "mediaType": {"@id": "untp:mediaType"},
        "code": {"@id": "untp:code"},
        "schemeId": {"@id": "untp:schemeId", "@type": "@id"},
        "schemeName": {"@id": "untp:schemeName"},
        "definition": {"@id": "untp:definition"},
    }
    ctx = {"@version": 1.1, "aic": AIC, "untp": "https://vocabulary.uncefact.org/untp/"}
    for t in sorted(terms):
        ctx[t] = {"@id": t, "@context": scoped}
    doc = {"@context": ctx}
    (ROOT / "extension" / "untp-ai-context.jsonld").write_text(json.dumps(doc, indent=2) + "\n")


def main():
    CRED_DIR.mkdir(exist_ok=True)
    all_rows = []
    terms = set()
    for stem, builder, family, chain in CREDENTIALS:
        prov, present = [], {}
        cred = unwrap(builder(), "$", prov, present)
        aic_terms(cred, terms)
        (CRED_DIR / f"{stem}.json").write_text(json.dumps(cred, indent=2, ensure_ascii=False) + "\n")
        all_rows += matrix_rows(stem, family, chain, prov, present)
    write_extension_context(terms)
    all_rows += dcc_rows()
    fields = list(all_rows[0].keys())
    with open(ROOT / "field-matrix.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_rows)
    write_sources_md()
    unknown = {s for r in all_rows for s in r["source"].split("; ") if s} - set(SOURCES)
    assert not unknown, f"unknown source keys: {unknown}"
    print(f"wrote {len(CREDENTIALS)} credentials, {len(all_rows)} field-matrix rows")


if __name__ == "__main__":
    main()

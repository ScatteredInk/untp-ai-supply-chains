"""Two slide diagrams (16:9, 1600x900), ODS Visual Guidelines 2026.

  slides/diagram-1-chain.svg / .png           the chain, core vs extension links
  slides/diagram-2-model-passport.svg / .png  inside the OLMo 2 7B passport

Status counts come from slides/chain-fields.csv (run slides.py first).
PNGs are rendered at 2x with headless Chrome.

Run: .venv/bin/python diagrams.py
"""

import base64
import csv
import subprocess
from collections import Counter
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "slides"
W, H = 1600, 900

SUNBURST, PAGE, CREAM, SAGE, SKY = "#f46036", "#f5f5f5", "#efecca", "#a9cbb7", "#6fafe8"
G1, G2, G3, G4, INK = "#595959", "#cccccc", "#d9d9d9", "#f3f3f3", "#222222"
STATUS_FILL = {"published": SAGE, "needs extension vocabulary": SKY, "not published": SUNBURST}
FONT = "'Instrument Sans', Arial, sans-serif"


def font_css():
    faces = []
    for w in (400, 600, 700):
        data = base64.b64encode((OUT / "fonts" / f"InstrumentSans-{w}.woff2").read_bytes()).decode()
        faces.append(f"@font-face{{font-family:'Instrument Sans';font-weight:{w};"
                     f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")
    return "".join(faces)


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}">'
            f"<style>{font_css()}</style>"
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{G1}"/></marker>'
            '<marker id="ahx" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{SKY}"/></marker></defs>'
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>{body}</svg>')


def text(x, y, s, size=14, weight=400, fill=INK, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{e(s)}</text>')


def line(points, ext=False, arrow=True, width=2):
    d = "M" + " L".join(f"{x},{y}" for x, y in points)
    colour = SKY if ext else G1
    dash = ' stroke-dasharray="8 6"' if ext else ""
    mk = f' marker-end="url(#{"ahx" if ext else "ah"})"' if arrow else ""
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}"{dash}{mk}/>'


def label(x, y, s, ext=False, anchor="middle", size=14):
    """Field-name label on a white knock-out so it reads over lines."""
    w = len(s) * size * 0.56 + 12
    x0 = x - w / 2 if anchor == "middle" else x - 6 if anchor == "start" else x - w + 6
    return (f'<rect x="{x0:.0f}" y="{y - size - 2}" width="{w:.0f}" height="{size + 9}" fill="#ffffff"/>'
            + text(x, y, s, size, 600, SKY if ext else G1, anchor))


def status_counts():
    rows = list(csv.DictReader(open(OUT / "chain-fields.csv")))
    return {c: Counter(r["status"] for r in rows if r["credential"] == c)
            for c in dict.fromkeys(r["credential"] for r in rows)}


def status_bar(x, y, w, counts, h=10):
    total = sum(counts.values())
    out, cx = [], x
    for st in ("published", "needs extension vocabulary", "not published"):
        n = counts.get(st, 0)
        if not n:
            continue
        sw = w * n / total
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{sw:.1f}" height="{h}" fill="{STATUS_FILL[st]}"/>')
        cx += sw
    nums = " · ".join(str(counts.get(s, 0)) for s in ("published", "needs extension vocabulary", "not published"))
    out.append(text(x + w, y + h + 15, nums, 11, 400, G1, "end"))
    return "".join(out)


def node(x, y, w, h, kind, name, lines, counts, tag=None, highlight=False):
    fill = CREAM if highlight else "#ffffff"
    stroke, sw = (INK, 2.5) if highlight else (G2, 1.5)
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
           text(x + 14, y + 22, kind.upper(), 11, 600, G1, extra='letter-spacing="0.08em"'),
           text(x + 14, y + 46, name, 19 if highlight else 17, 700)]
    ly = y + 68
    for s in lines:
        out.append(text(x + 14, ly, s, 13, 400, G1))
        ly += 18
    if tag:
        tw = len(tag) * 12 * 0.56 + 14
        out.append(f'<rect x="{x + 14}" y="{ly - 12}" width="{tw:.0f}" height="19" fill="#ffffff" stroke="{SKY}" '
                   f'stroke-width="1.5" stroke-dasharray="4 3"/>' + text(x + 21, ly + 2, tag, 12, 600, SKY))
    out.append(status_bar(x + 14, y + h - 32, w - 28, counts))
    return "".join(out)


# ------------------------------------------------------------------ diagram 1

def diagram_chain():
    c = status_counts()
    cols = {"chips": (40, 220), "sites": (440, 240), "data": (720, 240), "train": (1060, 240), "model": (1380, 180)}
    top1, top2, nh = 255, 415, 132
    mid = (top1 + top2 + nh) / 2
    b = []
    headers = [("chips", "CHIPS", "stretch"), ("sites", "SITES", ""), ("data", "DATA", ""),
               ("train", "TRAINING RUNS", ""), ("model", "MODEL", "")]
    for k, h, note in headers:
        x, _ = cols[k]
        b.append(text(x, 230, h, 13, 700, G1, extra='letter-spacing="0.1em"'))
        if note:
            b.append(text(x + 62, 230, note, 12, 400, G1))

    x, w = cols["chips"]
    ch_y = top1
    b.append(node(x, ch_y, w, 150, "DPP", "NVIDIA H100 SXM5",
                  ["80 GB HBM3, 700 W", "model level: lots not", "published"], c["01-h100-sxm5-passport"]))
    x, w = cols["sites"]
    b.append(node(x, top1, w, nh, "DFR", "Jupiter, Austin TX", ["1,024 H100 · PUE 1.2"], c["02-jupiter-facility-record"]))
    b.append(node(x, top2, w, nh, "DFR", "Augusta, Council Bluffs IA", ["160 A3 Mega VMs · PUE 1.12"],
                  c["03-augusta-facility-record"]))
    x, w = cols["data"]
    b.append(node(x, top1, w, nh, "DPP", "olmo-mix-1124", ["3.90T tokens · pretraining"], c["04-olmo-mix-1124-passport"]))
    b.append(node(x, top2, w, nh, "DPP", "dolmino-mix-1124", ["843B tokens · mid-training"],
                  c["05-dolmino-mix-1124-passport"]))
    x, w = cols["train"]
    b.append(node(x, top1, w, nh + 10, "DTE · MakeEvent", "Training at Jupiter", [], c["06-training-run-jupiter"],
                  tag="activityType: aic training"))
    b.append(node(x, top2 + 10, w, nh + 10, "DTE · MakeEvent", "Training at Augusta", [],
                  c["07-training-run-augusta"], tag="activityType: aic training"))
    x, w = cols["model"]
    m_y = mid - 95
    b.append(node(x, m_y, w, 190, "DPP", "OLMo 2 7B",
                  ["allenai/OLMo-2-1124-7B", "131 MWh · 52 t CO2e", "202 m³ water"],
                  c["08-olmo-2-7b-passport"], highlight=True))

    def bus(x_from, x_to, ys_from, ys_to, name, ext):
        """Fan-in / fan-out between adjacent columns via a vertical bus."""
        bx = (x_from + x_to) / 2
        out = []
        for y in ys_from:
            out.append(line([(x_from, y), (bx, y)], ext, arrow=False))
        if len(ys_from) > 1 or len(ys_to) > 1:
            ys = ys_from + ys_to
            out.append(line([(bx, min(ys)), (bx, max(ys))], ext, arrow=False))
        for y in ys_to:
            out.append(line([(bx, y), (x_to - 2, y)], ext))
        return out, bx

    r1, r2 = top1 + nh / 2, top2 + nh / 2
    parts, bx = bus(cols["chips"][0] + cols["chips"][1], cols["sites"][0], [r1], [r1, r2], "", True)
    b += parts
    b.append(label(bx - 14, r2 + 5, "aic:installedEquipment", True, anchor="end"))
    parts, bx = bus(cols["data"][0] + cols["data"][1], cols["train"][0], [r1, r2], [r1 + 5, r2 + 15], "", False)
    b += parts
    b.append(line([(bx, r2 + 15), (bx, top2 + nh + 20 + 8)], arrow=False))
    b.append(label(bx, top2 + nh + 20 + 26, "inputProduct"))
    parts, bx = bus(cols["train"][0] + cols["train"][1], cols["model"][0], [r1 + 5, r2 + 15], [mid], "", False)
    b += parts
    b.append(line([(bx, r2 + 15), (bx, top2 + nh + 20 + 8)], arrow=False))
    b.append(label(bx, top2 + nh + 20 + 26, "outputProduct"))

    # sites -> training: madeAtFacility, routed under the data column
    sx = cols["sites"][0] + cols["sites"][1] / 2
    tx = cols["train"][0] + cols["train"][1] / 2
    yb = top2 + nh + 70
    b.append(line([(sx, top2 + nh), (sx, yb), (tx - 30, yb), (tx - 30, top2 + nh + 12)]))
    b.append(label((sx + tx) / 2, yb + 5, "madeAtFacility"))
    # model -> sites: producedAtFacility (one) + aic:producedAtFacilities (both)
    mx = cols["model"][0] + cols["model"][1] / 2
    yb2 = yb + 72
    b.append(line([(mx, m_y + 190), (mx, yb2), (sx - 50, yb2), (sx - 50, top2 + nh + 2)], True))
    b.append(label((sx + mx) / 2 + 60, yb2 + 5,
                   "producedAtFacility holds one site  ·  aic:producedAtFacilities holds both", True))
    # training -> chips: aic:equipmentUsed, routed above
    ex = cols["train"][0] + cols["train"][1] - 40
    cx = cols["chips"][0] + cols["chips"][1] - 50
    yt = 150
    b.append(line([(ex, top1), (ex, yt), (cx, yt), (cx, ch_y - 2)], True))
    b.append(label((ex + cx) / 2, yt + 5, "aic:equipmentUsed  (GPUs are used by training, not consumed)", True))

    # legend
    ly = 830
    b.append(line([(40, ly), (100, ly)], False))
    b.append(text(112, ly + 5, "core UNTP 0.7.0 property", 14, 400, G1))
    b.append(line([(330, ly), (390, ly)], True))
    b.append(text(402, ly + 5, "proposed aic: extension property", 14, 400, G1))
    lx = 690
    b.append(text(lx, ly + 5, "Fields per credential:", 14, 600, G1))
    lx += 158
    for st, lab in (("published", "published"), ("needs extension vocabulary", "needs extension vocabulary"),
                    ("not published", "not published")):
        b.append(f'<rect x="{lx}" y="{ly - 7}" width="22" height="12" fill="{STATUS_FILL[st]}"/>')
        b.append(text(lx + 30, ly + 5, lab, 14, 400, G1))
        lx += 30 + len(lab) * 7.9 + 26
    b.append(text(40, 870, "Reconstructed by ODS from public sources, 30 Sep 2026. Unsigned; fictional issuer. "
                           "Counts are the top-level fields beneath each credential subject.", 12, 400, G1))
    return svg("".join(b))


# ------------------------------------------------------------------ diagram 2

def diagram_passport():
    b = []
    # context strip: the chain with the model highlighted
    steps = ["chips", "sites", "data", "training runs", "model"]
    x = 40
    for i, s in enumerate(steps):
        w = len(s) * 8 + 26
        hl = s == "model"
        b.append(f'<rect x="{x}" y="28" width="{w}" height="28" fill="{CREAM if hl else "#ffffff"}" '
                 f'stroke="{INK if hl else G2}" stroke-width="{2 if hl else 1.2}"/>')
        b.append(text(x + w / 2, 47, s, 13, 700 if hl else 400, INK if hl else G1, "middle"))
        if i < len(steps) - 1:
            b.append(line([(x + w + 4, 42), (x + w + 30, 42)], width=1.5))
        x += w + 34

    cx, cy, cw = 40, 80, W - 80
    rh = 29
    core = [
        ("id", "huggingface.co/allenai/OLMo-2-1124-7B/tree/7df9a825…", "needs extension vocabulary", 1),
        ("modelNumber", "allenai/OLMo-2-1124-7B", "published", None),
        ("batchNumber", "7df9a82518afdecae4e8c026b27adccc8c1f0032  (commit)", "published", None),
        ("idGranularity", "batch", "needs extension vocabulary", 1),
        ("productCategory", "UN CPC 84399 Other on-line content n.e.c.  +  aic foundation-model", "needs extension vocabulary", None),
        ("relatedParty", "producer: The Allen Institute For Artificial Intelligence (EIN 82-4083177)", "published", None),
        ("producedAtFacility", "Jupiter cluster (Ai2), Austin, Texas", "needs extension vocabulary", 2),
        ("countryOfProduction", "US", "published", None),
        ("productionDate", "(empty)", "not published", 3),
        ("performanceClaim", "131 MWH total-energy-consumption · 52 TNE total-ghg-emissions · 202 MTQ water-consumption",
         "needs extension vocabulary", 3),
        ("materialProvenance, dimensions", "(empty) mass fractions and physical size do not apply", "needs extension vocabulary", None),
    ]
    ext = [
        ("aic:artefactFiles", "6 safetensors files, each with SHA-256, e.g. 880c0d9bd731…  (29.2 GB)", 1),
        ("aic:parameterCount", "7,298,617,344 PARAMETER", 4),
        ("aic:trainingCompute", "1.8 × 10²³ FLOP", 4),
        ("aic:trainingTokens", "4.05 × 10¹² TOKEN", 4),
        ("aic:trainingData", "olmo-mix-1124 3.90T TOKEN (pretraining) · dolmino-mix-1124 3 × 50B TOKEN (mid-training)", None),
        ("aic:producedAtFacilities", "Jupiter, Augusta", 2),
        ("aic:architecture", "Olmo2ForCausalLM  (+ aic:layerCount, aic:contextLength, aic:vocabularySize …)", None),
        ("aic:licence", "Apache-2.0", None),
    ]
    head = 64
    band_a = 34 + len(core) * rh + 10
    band_b = 34 + len(ext) * rh + 10
    ch = head + band_a + band_b + 10
    b.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{head}" fill="{CREAM}"/>')
    b.append(f'<line x1="{cx}" y1="{cy + head}" x2="{cx + cw}" y2="{cy + head}" stroke="{INK}" stroke-width="1"/>')
    b.append(text(cx + 20, cy + 24, "DIGITAL PRODUCT PASSPORT · credentialSubject", 12, 600, G1,
                  extra='letter-spacing="0.08em"'))
    b.append(text(cx + 20, cy + 50, "OLMo 2 7B", 22, 700))

    fx, vx = cx + 50, cx + 330

    def badge(x, y, n):
        return (f'<rect x="{x}" y="{y - 15}" width="20" height="20" fill="{INK}"/>'
                + text(x + 10, y, str(n), 13, 700, "#ffffff", "middle"))

    def rows(items, y0, is_ext):
        out = []
        y = y0
        for item in items:
            if is_ext:
                field, value, n = item
                st = "needs extension vocabulary"
            else:
                field, value, st, n = item
            out.append(f'<rect x="{cx + 20}" y="{y - 13}" width="16" height="16" fill="{STATUS_FILL[st]}"/>')
            out.append(text(fx, y, field, 15, 600, SKY if is_ext else INK))
            vcol = G1 if value.startswith("(empty)") else INK
            out.append(text(vx, y, value, 14.5, 400, vcol))
            out.append(f'<line x1="{cx + 20}" y1="{y + 10}" x2="{cx + cw - 20}" y2="{y + 10}" stroke="{G4}" stroke-width="1"/>')
            y += rh
        return out

    ya = cy + head
    b.append(f'<rect x="{cx}" y="{ya}" width="6" height="{band_a}" fill="{G2}"/>')
    b.append(text(cx + 20, ya + 26, "CORE UNTP 0.7.0 FIELDS", 12, 700, G1, extra='letter-spacing="0.1em"'))
    b += rows(core, ya + 26 + rh, False)
    yb = ya + band_a
    b.append(f'<line x1="{cx}" y1="{yb}" x2="{cx + cw}" y2="{yb}" stroke="{G2}" stroke-width="1"/>')
    b.append(f'<rect x="{cx}" y="{yb}" width="6" height="{band_b}" fill="{SKY}"/>')
    b.append(text(cx + 20, yb + 26, "PROPOSED aic: EXTENSION  (in characteristics, or beside core fields)", 12, 700, SKY,
                  extra='letter-spacing="0.1em"'))
    b += rows(ext, yb + 26 + rh, True)

    ly = cy + ch + 34
    lx = cx
    for st in ("published", "needs extension vocabulary", "not published"):
        b.append(f'<rect x="{lx}" y="{ly - 12}" width="16" height="16" fill="{STATUS_FILL[st]}"/>')
        b.append(text(lx + 24, ly + 1, st, 14, 400, G1))
        lx += 24 + len(st) * 7.9 + 30
    b.append(text(W - 40, ly + 1, "Values from Hugging Face (commit 7df9a825) and OLMo 2 report, Tables 6 and 19. "
                                  "Reconstructed by ODS; unsigned.", 12, 400, G1, "end"))
    return svg("".join(b))


def render_png(svg_path):
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    png = svg_path.with_suffix(".png")
    wrapper = svg_path.with_suffix(".render.html")
    wrapper.write_text(f'<html><body style="margin:0">{svg_path.read_text()}</body></html>')
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                    "--force-device-scale-factor=2", "--virtual-time-budget=3000",
                    f"--screenshot={png}", f"file://{wrapper}"], check=True, capture_output=True)
    wrapper.unlink()
    return png


def main():
    for name, fn in (("diagram-1-chain", diagram_chain), ("diagram-2-model-passport", diagram_passport)):
        p = OUT / f"{name}.svg"
        p.write_text(fn())
        print("wrote", p.name, render_png(p).name)


if __name__ == "__main__":
    main()

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


KNOCK = []  # label areas cut out of connector lines (keeps the background transparent)


def svg(body, w=W, h=H):
    holes = "".join(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="black"/>'
                    for x, y, w, h in KNOCK)
    KNOCK.clear()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">'
            f"<style>{font_css()}</style>"
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{G1}"/></marker>'
            '<marker id="ahx" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{SKY}"/></marker></defs>'
            f'<mask id="knock" maskUnits="userSpaceOnUse"><rect width="{w}" height="{h}" fill="white"/>{holes}</mask>'
            f'{body}</svg>')


def text(x, y, s, size=14, weight=400, fill=INK, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{e(s)}</text>')


def line(points, ext=False, arrow=True, width=2):
    d = "M" + " L".join(f"{x},{y}" for x, y in points)
    colour = SKY if ext else G1
    dash = ' stroke-dasharray="8 6"' if ext else ""
    mk = f' marker-end="url(#{"ahx" if ext else "ah"})"' if arrow else ""
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}"{dash}{mk} mask="url(#knock)"/>'


def label(x, y, s, ext=False, anchor="middle", size=14):
    """Field-name label on a white knock-out so it reads over lines."""
    w = len(s) * size * 0.56 + 12
    x0 = x - w / 2 if anchor == "middle" else x - 6 if anchor == "start" else x - w + 6
    KNOCK.append((x0, y - size - 2, w, size + 9))
    return (text(x, y, s, size, 600, SKY if ext else G1, anchor))


def status_counts():
    rows = list(csv.DictReader(open(OUT / "chain-fields.csv")))
    return {c: Counter(r["status"] for r in rows if r["credential"] == c)
            for c in dict.fromkeys(r["credential"] for r in rows)}


def status_bar(x, y, w, counts, h=12):
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
    out.append(text(x + w, y + h + 18, nums, 14, 400, G1, "end"))
    return "".join(out)


def node(x, y, w, h, kind, name, lines, counts, tag=None, highlight=False):
    fill = CREAM if highlight else "#ffffff"
    stroke, sw = (INK, 2.5) if highlight else (G2, 1.5)
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
           text(x + 14, y + 25, kind.upper(), 14, 600, G1, extra='letter-spacing="0.06em"'),
           text(x + 14, y + 53, name, 23 if highlight else 21, 700)]
    ly = y + 80
    for s in lines:
        out.append(text(x + 14, ly, s, 17, 400, G1))
        ly += 23
    if tag:
        tw = len(tag) * 14 * 0.56 + 14
        out.append(f'<rect x="{x + 14}" y="{ly - 16}" width="{tw:.0f}" height="24" fill="#ffffff" stroke="{SKY}" '
                   f'stroke-width="1.5" stroke-dasharray="4 3"/>' + text(x + 21, ly + 2, tag, 14, 600, SKY))
    out.append(status_bar(x + 14, y + h - 40, w - 28, counts))
    return "".join(out)


def legend_row(x, y, items, size=17):
    """items: ('line', ext, label) or ('box', status, label); laid out left to right."""
    out = []
    for kind, key, lab in items:
        if kind == "line":
            out.append(line([(x, y), (x + 56, y)], key))
            x += 68
        else:
            out.append(f'<rect x="{x}" y="{y - 8}" width="24" height="14" fill="{STATUS_FILL[key]}"/>')
            x += 34
        out.append(text(x, y + 6, lab, size, 400, G1))
        x += len(lab) * size * 0.53 + 40
    return "".join(out)


# ------------------------------------------------------------------ diagram 1

def diagram_chain():
    c = status_counts()
    cols = {"chips": (40, 230), "sites": (430, 250), "data": (720, 250), "train": (1060, 250), "model": (1370, 190)}
    top1, nh, gap = 250, 160, 28
    top2 = top1 + nh + gap
    mid = (top1 + top2 + nh) / 2
    b = []
    headers = [("chips", "CHIPS", "stretch"), ("sites", "SITES", ""), ("data", "DATA", ""),
               ("train", "TRAINING RUNS", ""), ("model", "MODEL", "")]
    for k, h, note in headers:
        x, _ = cols[k]
        b.append(text(x, 225, h, 17, 700, G1, extra='letter-spacing="0.08em"'))
        if note:
            b.append(text(x + 78, 225, note, 16, 400, G1))

    x, w = cols["chips"]
    ch_y = top1
    b.append(node(x, ch_y, w, nh, "DPP", "NVIDIA H100 SXM5", ["80 GB HBM3, 700 W"], c["01-h100-sxm5-passport"]))
    x, w = cols["sites"]
    b.append(node(x, top1, w, nh, "DFR", "Jupiter", ["Austin, Texas", "1,024 H100 · PUE 1.2"],
                  c["02-jupiter-facility-record"]))
    b.append(node(x, top2, w, nh, "DFR", "Augusta", ["Council Bluffs, Iowa", "160 A3 Mega VMs · PUE 1.12"],
                  c["03-augusta-facility-record"]))
    x, w = cols["data"]
    b.append(node(x, top1, w, nh, "DPP", "olmo-mix-1124", ["3.90T tokens", "pretraining"],
                  c["04-olmo-mix-1124-passport"]))
    b.append(node(x, top2, w, nh, "DPP", "dolmino-mix-1124", ["843B tokens", "mid-training"],
                  c["05-dolmino-mix-1124-passport"]))
    x, w = cols["train"]
    b.append(node(x, top1, w, nh, "DTE · MakeEvent", "Training at Jupiter", [], c["06-training-run-jupiter"],
                  tag="activityType: aic training"))
    b.append(node(x, top2, w, nh, "DTE · MakeEvent", "Training at Augusta", [],
                  c["07-training-run-augusta"], tag="activityType: aic training"))
    x, w = cols["model"]
    mh = 200
    m_y = mid - mh / 2
    b.append(node(x, m_y, w, mh, "DPP", "OLMo 2 7B", ["131 MWh", "52 t CO2e", "202 m³ water"],
                  c["08-olmo-2-7b-passport"], highlight=True))

    def bus(x_from, x_to, ys_from, ys_to, ext):
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
    below = top2 + nh + 34  # label row under the node rows
    parts, bx = bus(cols["chips"][0] + cols["chips"][1], cols["sites"][0], [r1], [r1, r2], True)
    b += parts
    b.append(label(bx - 16, r2 + 6, "aic:installedEquipment", True, anchor="end", size=17))
    for frm, to, name in (("data", "train", "inputProduct"), ("train", "model", "outputProduct")):
        ys_to = [mid] if to == "model" else [r1, r2]
        parts, bx = bus(cols[frm][0] + cols[frm][1], cols[to][0], [r1, r2], ys_to, False)
        b += parts
        b.append(line([(bx, r2), (bx, below - 20)], arrow=False))
        b.append(label(bx, below, name, size=17))

    # sites -> training: madeAtFacility, routed under the data column
    sx = cols["sites"][0] + cols["sites"][1] / 2
    tx = cols["train"][0] + cols["train"][1] / 2
    yb = below + 50
    b.append(line([(sx, top2 + nh), (sx, yb), (tx - 30, yb), (tx - 30, top2 + nh + 2)]))
    b.append(label((sx + tx) / 2, yb + 6, "madeAtFacility", size=17))
    # model -> sites: producedAtFacility + aic:producedAtFacilities
    mx = cols["model"][0] + cols["model"][1] / 2
    yb2 = yb + 62
    b.append(line([(mx, m_y + mh), (mx, yb2), (sx - 50, yb2), (sx - 50, top2 + nh + 2)], True))
    b.append(label((sx + mx) / 2 + 60, yb2 + 6, "producedAtFacility · aic:producedAtFacilities", True, size=17))
    # training -> chips: aic:equipmentUsed, routed above
    ex = cols["train"][0] + cols["train"][1] - 40
    cx = cols["chips"][0] + cols["chips"][1] - 50
    yt = 150
    b.append(line([(ex, top1), (ex, yt), (cx, yt), (cx, ch_y - 2)], True))
    b.append(label((ex + cx) / 2, yt + 6, "aic:equipmentUsed", True, size=17))

    b.append(legend_row(40, 850, [
        ("line", False, "core UNTP 0.7.0 property"), ("line", True, "proposed aic: extension property"),
        ("box", "published", "published"), ("box", "needs extension vocabulary", "needs extension vocabulary"),
        ("box", "not published", "not published")]))
    return svg("".join(b))


# ------------------------------------------------------------------ diagram 2

def diagram_passport():
    b = []
    cx, cy, cw = 40, 30, W - 80
    rh = 32
    core = [
        ("id", "huggingface.co/allenai/OLMo-2-1124-7B/tree/7df9a825…", "needs extension vocabulary"),
        ("modelNumber", "allenai/OLMo-2-1124-7B", "published"),
        ("batchNumber", "7df9a82518afdecae4e8c026b27adccc8c1f0032", "published"),
        ("idGranularity", "batch", "needs extension vocabulary"),
        ("productCategory", "UN CPC 84399 Other on-line content n.e.c. · aic foundation-model", "needs extension vocabulary"),
        ("relatedParty", "producer: The Allen Institute For Artificial Intelligence, EIN 82-4083177", "published"),
        ("producedAtFacility", "Jupiter", "needs extension vocabulary"),
        ("countryOfProduction", "US", "published"),
        ("productionDate", "—", "not published"),
        ("performanceClaim", "131 MWH total-energy-consumption · 52 TNE total-ghg-emissions · 202 MTQ water-consumption",
         "needs extension vocabulary"),
        ("materialProvenance, dimensions", "—", "needs extension vocabulary"),
    ]
    ext = [
        ("aic:artefactFiles", "6 safetensors files with SHA-256 · 29.2 GB"),
        ("aic:parameterCount", "7,298,617,344 PARAMETER"),
        ("aic:trainingCompute", "1.8 × 10²³ FLOP"),
        ("aic:trainingTokens", "4.05 × 10¹² TOKEN"),
        ("aic:trainingData", "olmo-mix-1124 3.90T TOKEN pretraining · dolmino-mix-1124 3 × 50B TOKEN mid-training"),
        ("aic:producedAtFacilities", "Jupiter, Augusta"),
        ("aic:architecture", "Olmo2ForCausalLM"),
        ("aic:licence", "Apache-2.0"),
    ]
    head = 70
    band_a = 38 + len(core) * rh + 8
    band_b = 38 + len(ext) * rh + 8
    ch = head + band_a + band_b + 6
    b.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{head}" fill="{CREAM}"/>')
    b.append(f'<line x1="{cx}" y1="{cy + head}" x2="{cx + cw}" y2="{cy + head}" stroke="{INK}" stroke-width="1"/>')
    b.append(text(cx + 20, cy + 26, "DIGITAL PRODUCT PASSPORT · credentialSubject", 15, 600, G1,
                  extra='letter-spacing="0.06em"'))
    b.append(text(cx + 20, cy + 57, "OLMo 2 7B", 27, 700))

    fx, vx = cx + 54, cx + 400

    def rows(items, y0, is_ext):
        out = []
        y = y0
        for item in items:
            field, value = item[0], item[1]
            st = "needs extension vocabulary" if is_ext else item[2]
            out.append(f'<rect x="{cx + 20}" y="{y - 16}" width="19" height="19" fill="{STATUS_FILL[st]}"/>')
            out.append(text(fx, y, field, 19, 600, SKY if is_ext else INK))
            out.append(text(vx, y, value, 18, 400, G1 if value == "—" else INK))
            out.append(f'<line x1="{cx + 20}" y1="{y + 11}" x2="{cx + cw - 20}" y2="{y + 11}" stroke="{G4}" stroke-width="1"/>')
            y += rh
        return out

    ya = cy + head
    b.append(f'<rect x="{cx}" y="{ya}" width="6" height="{band_a}" fill="{G2}"/>')
    b.append(text(cx + 20, ya + 28, "CORE UNTP 0.7.0 FIELDS", 15, 700, G1, extra='letter-spacing="0.08em"'))
    b += rows(core, ya + 28 + rh, False)
    yb = ya + band_a
    b.append(f'<line x1="{cx}" y1="{yb}" x2="{cx + cw}" y2="{yb}" stroke="{G2}" stroke-width="1"/>')
    b.append(f'<rect x="{cx}" y="{yb}" width="6" height="{band_b}" fill="{SKY}"/>')
    b.append(text(cx + 20, yb + 28, "PROPOSED aic: EXTENSION", 15, 700, SKY, extra='letter-spacing="0.08em"'))
    b += rows(ext, yb + 28 + rh, True)

    b.append(legend_row(cx, cy + ch + 30, [
        ("box", "published", "published"), ("box", "needs extension vocabulary", "needs extension vocabulary"),
        ("box", "not published", "not published")]))
    return svg("".join(b))


def render_png(svg_path, w=W, h=H):
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    png = svg_path.with_suffix(".png")
    wrapper = svg_path.with_suffix(".render.html")
    wrapper.write_text(f'<html><body style="margin:0;background:transparent">{svg_path.read_text()}</body></html>')
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000", f"--window-size={w},{h}",
                    "--force-device-scale-factor=2", "--virtual-time-budget=3000",
                    f"--screenshot={png}", f"file://{wrapper}"], check=True, capture_output=True)
    wrapper.unlink()
    return png


# ------------------------------------------------------------------ diagram 3

DATA_W, DATA_H = 1600, 240
OLIVE = "#c2b520"


def diagram_untp_data():
    """ODS-branded version of the four UNTP credential types: boxes only."""
    b = []
    boxes = [
        (["Digital Traceability", "Event"], SKY),
        (["Digital Product", "Passport"], SAGE),
        (["Digital Facility", "Record"], OLIVE),
        (["Conformity", "Credential"], SUNBURST),
    ]
    gap = 40
    bw = (DATA_W - 3 * gap) / 4
    bh, by = DATA_H, 0
    for i, (lines_, colour) in enumerate(boxes):
        x = i * (bw + gap)
        b.append(f'<rect x="{x:.0f}" y="{by}" width="{bw:.0f}" height="{bh}" fill="{colour}"/>')
        ty = by + (bh - 2 * 42) / 2 + 32
        for j, s in enumerate(lines_):
            b.append(text(x + bw / 2, ty + j * 42, s, 32, 700, INK, "middle"))
    return svg("".join(b), DATA_W, DATA_H)


def main():
    for name, fn in (("diagram-1-chain", diagram_chain), ("diagram-2-model-passport", diagram_passport)):
        p = OUT / f"{name}.svg"
        p.write_text(fn())
        print("wrote", p.name, render_png(p).name)
    p = OUT / "diagram-3-untp-data.svg"
    p.write_text(diagram_untp_data())
    print("wrote", p.name, render_png(p, DATA_W, DATA_H).name)


if __name__ == "__main__":
    main()

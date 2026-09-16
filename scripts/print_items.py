#!/usr/bin/env python3
"""Phase 5 print items (SKILL §8), built as millimetre-accurate SVG and exported to
*_RGB-preview.pdf with Inkscape.

Client data in CLAUDE.md is still unfilled, so every legally required field appears
as its literal [PLACEHOLDER]. Nothing is invented — German Impressum and §34c GewO
data must come from the client. Each sheet carries a NOT FOR PRINT bar until the
placeholders are replaced.

Inkscape cannot write PDF/X-4. These PDFs are RGB previews; 04_Print/README_PDFX4.md
explains the one-step Affinity export that produces the print files.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L  # noqa: E402

ROOT = L.ROOT
KIT = ROOT / "AV-Brand-Kit"
OUT = KIT / "04_Print"
SVGDIR = KIT / "01_Logo/SVG"

GREEN, CREAM, GOLD, WHITE, BLACK = (L.C["green"], L.C["cream"], L.C["gold"],
                                    L.C["white"], L.C["black"])
BLEED = 3.0      # mm
SLUG = 5.0       # mm of extra media for the crop marks

# --- client data, verbatim from the CLAUDE.md block. Unfilled entries stay literal.
CLIENT = {
    "company": "Auguste Viktoria Immobilien [RECHTSFORM]",
    "tagline": "Mehr als nur ein Zuhause",
    "street": "[STRASSE NR]",
    "city": "[PLZ ORT]",
    "phone": "[+49 ...]",
    "email": "[info@...]",
    "web": "[www....de]",
    "geschaeftsfuehrer": "[NAME]",
    "registergericht": "[AMTSGERICHT ... HRB ...]",
    "ust_idnr": "[DE...]",
    "gewo_34c": "Erlaubnis nach §34c GewO, erteilt durch [BEHÖRDE, ORT]",
    "sign_size_mm": (1000.0, 700.0),   # CLAUDE.md default; confirm with the printer
}

UNFILLED = re.compile(r"\[[^\]]+\]")


def has_placeholder() -> bool:
    return any(UNFILLED.search(str(v)) for v in CLIENT.values())


# ------------------------------------------------------------------- svg helpers
def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def logo_block(stem: str, x: float, y: float, w: float,
               align: str = "left", recolour: str | None = None) -> str:
    """Embed an exported plain SVG (text already outlined) as a nested <svg>,
    scaled so its width is `w` mm.

    `recolour` swaps black for another flat colour. The six shipped modes have no
    1-colour green, and the Stempel needs one, so the green seal is derived from the
    1c-black artwork rather than adding a seventh mode to the whole export matrix.
    """
    src = SVGDIR / f"{stem}.svg"
    raw = src.read_text()
    m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"', raw)
    vx, vy, vw, vh = (float(g) for g in m.groups())
    h = w * vh / vw
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    body = L._inner_svg(src)
    style = re.search(r"<style>.*?</style>", raw, re.S)
    style_s = style.group(0) if style else ""
    if recolour:
        for black in ("#000000", "#000", "black"):
            body = body.replace(black, recolour)
            style_s = style_s.replace(black, recolour)
    return (f'<svg x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'viewBox="{vx} {vy} {vw} {vh}" overflow="visible">'
            f'{style_s}{body}</svg>')


def logo_height(stem: str, w: float) -> float:
    src = SVGDIR / f"{stem}.svg"
    m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"', src.read_text())
    _, _, vw, vh = (float(g) for g in m.groups())
    return w * vh / vw


def text(x, y, s, size=3.0, fill=GREEN, family="Montserrat", weight="400",
         anchor="start", tracking=0.0, italic=False) -> str:
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.3f}" y="{y:.3f}" font-family="{family}" '
            f'font-size="{size:.3f}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{tracking:.3f}"{style}'
            f'>{esc(s)}</text>')


def crop_marks(mw: float, mh: float, tw: float, th: float) -> str:
    """Corner marks sitting in the slug, outside the bleed."""
    ox, oy = (mw - tw) / 2, (mh - th) / 2      # trim origin
    ln, gap = 4.0, BLEED + 0.6
    out = []
    for cx, sx in ((ox, -1), (ox + tw, 1)):
        for cy, sy in ((oy, -1), (oy + th, 1)):
            out.append(f'<line x1="{cx + sx * gap:.3f}" y1="{cy:.3f}" '
                       f'x2="{cx + sx * (gap + ln):.3f}" y2="{cy:.3f}"/>')
            out.append(f'<line x1="{cx:.3f}" y1="{cy + sy * gap:.3f}" '
                       f'x2="{cx:.3f}" y2="{cy + sy * (gap + ln):.3f}"/>')
    return ('<g id="crop-marks" stroke="#000000" stroke-width="0.12" '
            'fill="none">' + "".join(out) + "</g>")


def not_for_print(mw: float, mh: float) -> str:
    if not has_placeholder():
        return ""
    return (f'<g id="not-for-print" opacity="0.92">'
            f'<rect x="0" y="{mh - 4.6:.3f}" width="{mw:.3f}" height="4.6" '
            f'fill="#B4231F"/>'
            f'<text x="{mw / 2:.3f}" y="{mh - 1.4:.3f}" font-family="Montserrat" '
            f'font-size="2.5" font-weight="600" fill="#FFFFFF" text-anchor="middle" '
            f'letter-spacing="0.5">NOT FOR PRINT — unfilled [PLACEHOLDERS], '
            f'see AV-Brand-Kit/README.md</text></g>')


def sheet(name: str, tw: float, th: float, body: str, *, bg: str | None = None,
          marks: bool = True, banner: bool = True) -> str:
    """One print sheet. Media = trim + bleed + slug; content is drawn in trim
    coordinates via a translate, so every layout number below is a trim measurement."""
    pad = (BLEED + SLUG) if marks else 0.0
    mw, mh = tw + 2 * pad, th + 2 * pad
    bleed_rect = ""
    if bg:
        bleed_rect = (f'<rect x="{pad - BLEED:.3f}" y="{pad - BLEED:.3f}" '
                      f'width="{tw + 2 * BLEED:.3f}" height="{th + 2 * BLEED:.3f}" '
                      f'fill="{bg}"/>')
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{mw:.3f}mm" height="{mh:.3f}mm" viewBox="0 0 {mw:.3f} {mh:.3f}"
     id="{name}">
  <title>Auguste Viktoria Immobilien — {name}</title>
  <desc>Trim {tw:.0f}x{th:.0f} mm, bleed {BLEED:.0f} mm, slug {SLUG:.0f} mm.
  RGB preview only — export PDF/X-4 from Affinity, see 04_Print/README_PDFX4.md.</desc>
  <rect width="{mw:.3f}" height="{mh:.3f}" fill="#FFFFFF"/>
  {bleed_rect}
  <g transform="translate({pad:.3f} {pad:.3f})">
{body}
  </g>
  {crop_marks(mw, mh, tw, th) if marks else ""}
  {not_for_print(mw, mh) if banner else ""}
</svg>
"""


# ------------------------------------------------------------------------ items
def visitenkarte_front() -> str:
    tw, th = 85.0, 55.0
    body = "    " + logo_block("AV_stacked_full-dark", tw / 2, 0, 46, "center")
    h = logo_height("AV_stacked_full-dark", 46)
    body = ("    " + logo_block("AV_stacked_full-dark", tw / 2, (th - h) / 2,
                                46, "center"))
    return sheet("Visitenkarte_front_85x55", tw, th, body, bg=GREEN)


def visitenkarte_back() -> str:
    tw, th = 85.0, 55.0
    x, y = 9.0, 17.0
    rows = [
        (CLIENT["geschaeftsfuehrer"], 4.2, "600", GREEN, 0.0),
        ("[POSITION]", 2.9, "400", "#6B7A70", 0.25),
        (CLIENT["street"], 2.9, "400", GREEN, 0.0),
        (CLIENT["city"], 2.9, "400", GREEN, 0.0),
        ("T " + CLIENT["phone"], 2.9, "400", GREEN, 0.0),
        (CLIENT["email"], 2.9, "400", GREEN, 0.0),
        (CLIENT["web"], 2.9, "500", GOLD, 0.0),
    ]
    out, cy = [], y
    for s, size, weight, fill, tr in rows:
        out.append("    " + text(x, cy, s, size, fill, weight=weight, tracking=tr))
        cy += size * 1.75 if size > 3 else 4.4
    out.append(f'    <rect x="{x:.3f}" y="{y + 1.8:.3f}" width="14" height="0.35" '
               f'fill="{GOLD}"/>')
    out.append("    " + logo_block("AV_monogram_simple_1c-gold", tw - 8, th - 16,
                                   11, "right"))
    return sheet("Visitenkarte_back_85x55", 85.0, 55.0, "\n".join(out), bg=CREAM)


def briefpapier() -> str:
    tw, th = 210.0, 297.0
    m = 12.0
    out = ["    " + logo_block("AV_horizontal_full-light", m, m, 45)]
    ay = m + 4
    for i, s in enumerate([CLIENT["street"], CLIENT["city"], CLIENT["phone"],
                           CLIENT["web"]]):
        out.append("    " + text(tw - m, ay + i * 4.2, s, 2.9, "#4A5A50",
                                 anchor="end"))
    # footer rule + the full legal line
    fy = th - 22.0
    out.append(f'    <rect x="{m}" y="{fy:.3f}" width="{tw - 2 * m:.3f}" '
               f'height="0.3" fill="{GOLD}"/>')
    legal = [
        f'{CLIENT["company"]} · {CLIENT["street"]} · {CLIENT["city"]}',
        f'Geschäftsführer: {CLIENT["geschaeftsfuehrer"]} · '
        f'Registergericht: {CLIENT["registergericht"]} · USt-IdNr.: {CLIENT["ust_idnr"]}',
        CLIENT["gewo_34c"],
        f'T {CLIENT["phone"]} · {CLIENT["email"]} · {CLIENT["web"]}',
    ]
    for i, s in enumerate(legal):
        out.append("    " + text(tw / 2, fy + 5.0 + i * 3.4, s, 2.47, "#5A6A60",
                                 anchor="middle"))
    return sheet("Briefpapier_A4", tw, th, "\n".join(out), bg=WHITE)


def expose_cover() -> str:
    tw, th = 210.0, 297.0
    band_h = th * 0.28
    by = th - band_h
    out = [
        f'    <image x="{-BLEED}" y="{-BLEED}" width="{tw + 2 * BLEED:.3f}" '
        f'height="{th + 2 * BLEED:.3f}" preserveAspectRatio="xMidYMid slice" '
        f'xlink:href="{(ROOT / "assets/backgrounds/bg_expose_1800x2400.png").as_uri()}"/>',
        f'    <rect x="{-BLEED}" y="{by:.3f}" width="{tw + 2 * BLEED:.3f}" '
        f'height="{band_h + BLEED:.3f}" fill="{GREEN}"/>',
        "    " + logo_block("AV_stacked_1c-cream", tw / 2, by + 11, 62, "center"),
        "    " + text(tw / 2, th - 14.0, "EXPOSÉ · {{OBJEKTTITEL}}", 4.0, GOLD,
                      anchor="middle", tracking=1.4, weight="500"),
    ]
    return sheet("Expose_Cover_A4", tw, th, "\n".join(out))


def verkaufsschild() -> str:
    tw, th = CLIENT["sign_size_mm"]
    out = [
        "    " + logo_block("AV_stacked_1c-cream", tw / 2, th * 0.10, tw * 0.44,
                            "center"),
        "    " + text(tw / 2, th * 0.635, "ZU VERKAUFEN", tw * 0.088, CREAM,
                      family="Cinzel", anchor="middle", tracking=tw * 0.004),
        f'    <rect x="{tw * 0.30:.3f}" y="{th * 0.685:.3f}" '
        f'width="{tw * 0.40:.3f}" height="{tw * 0.0022:.3f}" fill="{GOLD}"/>',
        "    " + text(tw / 2, th * 0.795, CLIENT["phone"], tw * 0.048, CREAM,
                      anchor="middle", weight="500", tracking=tw * 0.002),
        "    " + text(tw / 2, th * 0.875, CLIENT["web"], tw * 0.040, GOLD,
                      anchor="middle", tracking=tw * 0.002),
    ]
    return sheet(f"Verkaufsschild_{tw:.0f}x{th:.0f}", tw, th, "\n".join(out),
                 bg=GREEN, marks=False)


def stempel(colour: str, label: str) -> str:
    d = 40.0
    r = d / 2
    ring = r - 1.2
    out = [
        f'    <circle cx="{r}" cy="{r}" r="{ring:.3f}" fill="none" '
        f'stroke="{colour}" stroke-width="0.8"/>',
        f'    <circle cx="{r}" cy="{r}" r="{ring - 2.6:.3f}" fill="none" '
        f'stroke="{colour}" stroke-width="0.35"/>',
        "    " + logo_block("AV_monogram_simple_1c-black", r, r - 5.0, 15,
                            "center", recolour=colour),
        f'    <path id="stamp-arc-{label}" fill="none" d="M {r - (ring - 4.2):.3f} {r} '
        f'a {ring - 4.2:.3f} {ring - 4.2:.3f} 0 1 1 {2 * (ring - 4.2):.3f} 0"/>',
        f'    <text font-family="Cinzel" font-size="2.6" fill="{colour}" '
        f'letter-spacing="0.42">'
        f'<textPath xlink:href="#stamp-arc-{label}" startOffset="50%" '
        f'text-anchor="middle">AUGUSTE VIKTORIA</textPath></text>',
        "    " + text(r, r + 12.2, "IMMOBILIEN", 2.2, colour, anchor="middle",
                      tracking=0.8),
    ]
    return sheet(f"Stempel_40mm_1c-{label}", d, d, "\n".join(out), marks=False,
                 banner=False)


ITEMS = {
    "Visitenkarte_front_85x55": visitenkarte_front,
    "Visitenkarte_back_85x55": visitenkarte_back,
    "Briefpapier_A4": briefpapier,
    "Expose_Cover_A4": expose_cover,
    (f"Verkaufsschild_{CLIENT['sign_size_mm'][0]:.0f}x"
     f"{CLIENT['sign_size_mm'][1]:.0f}"): verkaufsschild,
    "Stempel_40mm_1c-black": lambda: stempel(BLACK, "black"),
    "Stempel_40mm_1c-green": lambda: stempel(GREEN, "green"),
}


def readme_pdfx4() -> None:
    (OUT / "README_PDFX4.md").write_text(f"""# From RGB preview to print-ready PDF/X-4

1. Open the `*_RGB-preview.pdf` (or the matching `.svg`) in Affinity Designer or
   Publisher. The SVG keeps live vector geometry; the PDF is already outlined.
2. Set the document to CMYK, ICC profile **Coated FOGRA39 (ISO 12647-2:2004)**,
   under Document ▸ Colour.
3. Replace every `[PLACEHOLDER]` and `{{{{OBJEKTTITEL}}}}`. The red NOT FOR PRINT bar
   disappears once the source data in `CLAUDE.md` is filled and the sheet rebuilt.
4. Export ▸ PDF ▸ preset **PDF/X-4**, "Include bleed" on, bleed {BLEED:.0f} mm,
   crop marks on. Save as `*_PRINT.pdf`.
5. Order a proof before the first run. `{GREEN}` is very close to black on uncoated
   stock; ask the printer whether a spot colour or a rich-black build serves better.

Inkscape cannot write PDF/X-4, which is why this step is manual. Nothing in these
files is an obstacle to it — text is already converted to paths and bleed is already
{BLEED:.0f} mm on every side.
""")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for name, fn in ITEMS.items():
        svg = OUT / f"{name}.svg"
        svg.write_text(fn())
        pdf = OUT / f"{name}_RGB-preview.pdf"
        r = subprocess.run(["inkscape", str(svg), "--export-type=pdf",
                            "--export-text-to-path", "-o", str(pdf)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"{name}: {r.stderr[-500:]}")
        made += [svg.name, pdf.name]
        print(f"  {name:<34} {pdf.stat().st_size // 1024:>4} KB")
    readme_pdfx4()
    made.append("README_PDFX4.md")
    print(f"\n{len(made)} files in 04_Print")
    if has_placeholder():
        print("\nUnfilled client data — every sheet carries the NOT FOR PRINT bar:")
        for k, v in CLIENT.items():
            if UNFILLED.search(str(v)):
                print(f"  {k:<20} {v}")


if __name__ == "__main__":
    main()

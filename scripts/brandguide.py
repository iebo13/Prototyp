#!/usr/bin/env python3
"""Build AV-Brand-Kit/08_Brandguide/AV_Brandguide.pdf.

Twelve A4 landscape pages, written as HTML with the real fonts and the real token
values, then printed with headless Chromium. Every image on every page is a file
that was actually exported by the build, so the guide cannot drift from the kit.
"""
from __future__ import annotations

import html
import json
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L      # noqa: E402
import layouts as LY    # noqa: E402

ROOT = L.ROOT
KIT = ROOT / "AV-Brand-Kit"
OUT = KIT / "08_Brandguide"
TOK = json.loads((KIT / "00_Master/tokens.json").read_text())
C = L.C

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
    shutil.which("chromium"), shutil.which("google-chrome"),
]


def chrome() -> str:
    for c in CHROME_CANDIDATES:
        if c and pathlib.Path(c).is_file():
            return c
    raise RuntimeError("no headless Chromium found")


def uri(p: pathlib.Path) -> str:
    return p.resolve().as_uri()


def png(stem: str, w: int = 1000) -> str:
    return uri(KIT / f"01_Logo/PNG/{stem}_{w}px.png")


# --------------------------------------------------------------------------- CSS
CSS = f"""
@font-face {{ font-family:'Cinzel'; src:url('{uri(KIT / "07_Fonts/Cinzel-Variable.ttf")}'); }}
@font-face {{ font-family:'Montserrat'; src:url('{uri(KIT / "07_Fonts/Montserrat-Variable.ttf")}'); }}
@page {{ size: A4 landscape; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: Montserrat, Arial, sans-serif; color: {C['green']}; }}
.page {{
  width: 297mm; height: 210mm; page-break-after: always; position: relative;
  padding: 16mm 18mm 14mm; background: #FFFFFF; overflow: hidden;
}}
.page:last-child {{ page-break-after: auto; }}
.page.dark {{ background: {C['green']}; color: {C['cream']}; }}
.page.cream {{ background: {C['cream']}; }}
h1 {{ font-family: Cinzel, serif; font-weight: 600; font-size: 22pt; letter-spacing: .02em; }}
h2 {{ font-family: Cinzel, serif; font-weight: 600; font-size: 14pt; margin-bottom: 4mm; }}
h3 {{ font-size: 8pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase;
      color: {C['gold']}; margin-bottom: 2.5mm; }}
p  {{ font-size: 9.2pt; line-height: 1.6; max-width: 150mm; }}
.small {{ font-size: 7.6pt; line-height: 1.5; color: #5A6A60; }}
.dark .small {{ color: #9FB3A6; }}
.rule {{ height: .35mm; background: {C['gold']}; margin: 4mm 0 6mm; }}
.folio {{ position: absolute; bottom: 8mm; left: 18mm; right: 18mm;
          display: flex; justify-content: space-between;
          font-size: 7pt; letter-spacing: .12em; color: #8A9A90; }}
.dark .folio {{ color: #6E8377; }}
.grid {{ display: grid; gap: 5mm; }}
.g2 {{ grid-template-columns: repeat(2, 1fr); }}
.g3 {{ grid-template-columns: repeat(3, 1fr); }}
.g4 {{ grid-template-columns: repeat(4, 1fr); }}
.tile {{ border: .25mm solid #D9E0DB; border-radius: 1mm; padding: 4mm;
         display: flex; flex-direction: column; align-items: center;
         justify-content: center; min-height: 34mm; }}
.tile.on-green {{ background: {C['green']}; border-color: transparent; }}
.tile.on-cream {{ background: {C['cream']}; border-color: transparent; }}
.tile img {{ max-width: 100%; max-height: 26mm; object-fit: contain; }}
.cap {{ font-size: 6.6pt; letter-spacing: .1em; text-transform: uppercase;
        color: #7B8C82; margin-top: 3mm; text-align: center; }}
.on-green .cap, .on-cream .cap {{ color: #8FA396; }}
.on-cream .cap {{ color: #6B7A70; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.4pt; }}
th, td {{ text-align: left; padding: 2.4mm 3mm; border-bottom: .2mm solid #E2E8E4; }}
th {{ font-size: 7pt; letter-spacing: .12em; text-transform: uppercase;
      color: {C['gold']}; font-weight: 600; }}
td.mono {{ font-family: 'DejaVu Sans Mono', monospace; font-size: 7.8pt; }}
.sw {{ width: 9mm; height: 9mm; border-radius: 1mm; border: .2mm solid rgba(0,0,0,.12);
       display: inline-block; vertical-align: middle; }}
.dd {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; align-items: start; }}
.dd img {{ width: 100%; display: block; border-radius: 1mm; }}
.tag {{ font-size: 6.6pt; font-weight: 700; letter-spacing: .14em; padding: .8mm 2.4mm;
        border-radius: .8mm; color: #fff; display: inline-block; margin-bottom: 1.6mm; }}
.ok {{ background: #2E7D53; }}
.no {{ background: #B4231F; }}
.ddrow {{ margin-bottom: 4mm; }}
.ddtitle {{ font-size: 8.6pt; font-weight: 600; margin-bottom: 1.6mm; }}
.ddwhy {{ font-size: 7.2pt; color: #6B7A70; margin-bottom: 2.4mm; }}
.clear {{ position: relative; display: inline-block; }}
.clear .box {{ position: absolute; inset: 0; border: .4mm dashed {C['gold']}; }}
.note {{ background: #FFF6E8; border-left: 1mm solid {C['gold']};
         padding: 3mm 4mm; font-size: 7.6pt; line-height: 1.55; margin-top: 5mm; }}
.dark .note {{ background: rgba(209,169,118,.10); }}
.spec {{ font-size: 7.8pt; line-height: 1.75; }}
.spec b {{ font-weight: 600; }}
"""


def folio(n: int, label: str) -> str:
    return (f'<div class="folio"><span>AUGUSTE VIKTORIA IMMOBILIEN · BRAND GUIDE</span>'
            f'<span>{html.escape(label)} · {n:02d}</span></div>')


PAGES: list[str] = []


def page(label: str, body: str, cls: str = "") -> None:
    n = len(PAGES) + 1
    PAGES.append(f'<section class="page {cls}">{body}{folio(n, label)}</section>')


# ------------------------------------------------------------------------ pages
def build_pages() -> None:
    # 1 cover
    page("Cover", f"""
      <div style="height:100%;display:flex;flex-direction:column;
                  align-items:center;justify-content:center;">
        <img src="{png('AV_stacked_tagline_full-dark', 3000)}" style="width:118mm">
        <div style="margin-top:14mm;font-size:8pt;letter-spacing:.34em;
                    color:{C['gold']};">B R A N D &nbsp; G U I D E</div>
        <div style="margin-top:3mm;font-size:7pt;letter-spacing:.2em;color:#8FA396;">
          VERSION 1.0</div>
      </div>""", "dark")

    # 2 the mark
    page("The mark", f"""
      <h1>The mark</h1><div class="rule"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12mm;">
        <div>
          <p>Three things carry the brand, and they always appear together in the
          monogram: the <b>A and V</b>, set in Cinzel and overlapped so they read as
          one shape; the <b>mountain ridge</b>, a single gold line rising from the A's
          apex; and the <b>peacock feather</b>, whose quill follows the V's right
          stroke.</p>
          <p style="margin-top:4mm">The feather is the only ornament. It carries the
          one flash of colour in the identity and it earns that by being the only
          thing in the mark that is not a letter or a line. Everything else is
          cream, gold and the deep forest green the whole system sits on.</p>
          <p style="margin-top:4mm">Cinzel gives the name its Roman capitals.
          Montserrat carries IMMOBILIEN and the tagline, letterspaced wide so the
          two typefaces never compete.</p>
          <div class="note"><b>The one rule that matters.</b> The logo is artwork,
          not a layout. Place it, scale it proportionally, and leave it alone.</div>
        </div>
        <div class="tile on-green" style="min-height:0;height:118mm;">
          <img src="{png('AV_monogram_full-dark', 3000)}" style="max-height:100mm">
        </div>
      </div>""")

    # 3 layouts
    tiles = "".join(
        f'<div class="tile on-green"><img src="{png(f"AV_{l}_full-dark", 3000)}">'
        f'<div class="cap">{l.replace("_", " ")}</div></div>'
        for l in LY.LAYOUTS)
    page("Layouts", f"""
      <h1>Seven layouts</h1><div class="rule"></div>
      <p style="margin-bottom:5mm">Pick by the space you have, not by preference.
      Stacked is the default. Horizontal is for headers and anything wider than it is
      tall. The monogram alone is for avatars, favicons and stamps.</p>
      <div class="grid g4">{tiles}</div>""")

    # 4 clear space and minimum sizes
    rows = "".join(
        f"<tr><td>{l.replace('_', ' ')}</td><td class='mono'>{mm}</td>"
        f"<td class='mono'>{px}</td></tr>"
        for l, (mm, px) in LY.MIN_SIZE.items())
    page("Clear space", f"""
      <h1>Clear space and minimum size</h1><div class="rule"></div>
      <div style="display:grid;grid-template-columns:1.15fr 1fr;gap:12mm;">
        <div>
          <h3>Clear space</h3>
          <p>Keep a margin of <b>X</b> on all four sides, where X is the cap height of
          the A in AUGUSTE. Nothing enters that band: no type, no rule, no photo edge,
          no other logo. Every supplied file already has X baked into its viewBox, so
          placing the file flush against a box still leaves the margin standing.</p>
          <div class="tile on-green" style="margin-top:5mm;min-height:72mm;">
            <div class="clear">
              <img src="{png('AV_stacked_full-dark', 3000)}" style="max-height:52mm">
              <div class="box"></div>
            </div>
          </div>
          <div class="cap" style="text-align:left;margin-top:2mm">
            dashed line = the edge of the supplied file, X beyond the artwork</div>
        </div>
        <div>
          <h3>Minimum size</h3>
          <table><tr><th>Layout</th><th>Print</th><th>Screen</th></tr>{rows}</table>
          <div class="note">Below 64 px, swap to <b>monogram simple</b>. The
          multicolour feather turns to mud at that size; the one-colour silhouette
          keeps the eye readable.</div>
        </div>
      </div>""")

    # 5 colour modes
    mode_tiles = ""
    for mode, spec in L.MODES.items():
        dark_bg = spec["letters"] in ("cream", "white") or mode == "1c-gold"
        cls = "on-green" if dark_bg else "on-cream"
        mode_tiles += (
            f'<div class="tile {cls}"><img src="{png(f"AV_stacked_{mode}", 3000)}">'
            f'<div class="cap">{mode}</div></div>')
    page("Colour modes", f"""
      <h1>Six colour modes</h1><div class="rule"></div>
      <p style="margin-bottom:5mm">Two full-colour modes and four single-colour ones.
      The single-colour modes exist for embossing, engraving, stamps, fax-grade print
      and anywhere a second ink costs money. They are not a style choice.</p>
      <div class="grid g3">{mode_tiles}</div>
      <table style="margin-top:6mm">
        <tr><th>Mode</th><th>Letters</th><th>Ridge, rules, tagline</th>
            <th>Feather</th><th>Intended background</th></tr>
        <tr><td>full-dark</td><td>cream</td><td>gold</td><td>peacock / teal / gold</td>
            <td>green</td></tr>
        <tr><td>full-light</td><td>green</td><td>gold</td><td>peacock / teal / gold</td>
            <td>white or cream</td></tr>
        <tr><td>1c-cream</td><td>cream</td><td>cream</td><td>silhouette</td>
            <td>dark</td></tr>
        <tr><td>1c-white</td><td>white</td><td>white</td><td>silhouette</td>
            <td>dark</td></tr>
        <tr><td>1c-black</td><td>black</td><td>black</td><td>silhouette</td>
            <td>light</td></tr>
        <tr><td>1c-gold</td><td>gold</td><td>gold</td><td>silhouette</td>
            <td>either</td></tr>
      </table>""")

    # 6 + 7 do / don't
    import dodont
    cases = sorted(dodont.CASES)
    for half, (start, end) in enumerate(((0, 4), (4, 8))):
        rows_html = ""
        for n, title, why, _ in cases[start:end]:
            rows_html += f"""
              <div class="ddrow">
                <div class="ddtitle">{html.escape(title)}</div>
                <div class="ddwhy">{html.escape(why)}</div>
                <div class="dd">
                  <div><span class="tag no">DON'T</span>
                    <img src="{uri(ROOT / f'review/dodont/{n}_dont.png')}"></div>
                  <div><span class="tag ok">DO</span>
                    <img src="{uri(ROOT / f'review/dodont/{n}_do.png')}"></div>
                </div>
              </div>"""
        title = "Do and don't" if half == 0 else "Do and don't, continued"
        page("Do and don't", f"""
          <h1>{title}</h1><div class="rule"></div>
          <div class="grid g2">{rows_html}</div>""")

    # 8 colour
    crows = ""
    for name, v in TOK["colors"].items():
        c, m, y, k = v["cmyk_approx"]
        crows += (f"<tr><td><span class='sw' style='background:{v['hex']}'></span></td>"
                  f"<td>{name}</td><td class='mono'>{v['hex']}</td>"
                  f"<td class='mono'>{v['rgb'][0]} {v['rgb'][1]} {v['rgb'][2]}</td>"
                  f"<td class='mono'>{c} {m} {y} {k}</td>"
                  f"<td class='small'>{html.escape(v['use'])}</td></tr>")
    page("Colour", f"""
      <h1>Colour</h1><div class="rule"></div>
      <table><tr><th></th><th>Token</th><th>HEX</th><th>RGB</th>
        <th>CMYK approx.</th><th>Use</th></tr>{crows}</table>
      <div class="note"><b>Before any print run.</b> The CMYK column is an
      approximation computed from sRGB, not a measured separation. Proof it in
      Affinity against Coated FOGRA39. {C['green']} sits very close to black on
      uncoated stock — ask the printer whether a spot colour or a rich-black build
      serves the job better.</div>""")

    # 9 typography
    page("Typography", f"""
      <h1>Typography</h1><div class="rule"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12mm;">
        <div>
          <h3>Cinzel — display</h3>
          <div style="font-family:Cinzel;font-size:30pt;line-height:1.15;">Aa Vv</div>
          <div style="font-family:Cinzel;font-size:13pt;letter-spacing:.06em;
                      margin-top:3mm;">AUGUSTE VIKTORIA</div>
          <div class="spec" style="margin-top:4mm">
            <b>Use for</b> the company name, the monogram, headlines and section
            titles.<br>
            <b>Never</b> for body copy, captions or anything below 9 pt — the high
            stroke contrast breaks up.<br>
            <b>Tracking</b> +2 to +6 % in headlines. Roman capitals only.<br>
            <b>Licence</b> SIL OFL 1.1, shipped in 07_Fonts.
          </div>
        </div>
        <div>
          <h3>Montserrat — text</h3>
          <div style="font-size:30pt;line-height:1.15;font-weight:400;">Aa Vv</div>
          <div style="font-size:12pt;letter-spacing:.42em;margin-top:3mm;
                      font-weight:400;">IMMOBILIEN</div>
          <div style="font-size:8pt;letter-spacing:.3em;margin-top:3mm;font-weight:300;
                      color:{C['gold']};">MEHR ALS NUR EIN ZUHAUSE</div>
          <div class="spec" style="margin-top:4mm">
            <b>Use for</b> IMMOBILIEN, the tagline, body copy, tables, captions, the
            e-mail signature and every interface label.<br>
            <b>Weights</b> Light 300 for the tagline, Regular 400 for body,
            SemiBold 600 for emphasis. Nothing heavier.<br>
            <b>Tracking</b> 0.45 em on IMMOBILIEN, 0.30 em on the tagline, 0 in body
            copy.<br>
            <b>Fallback</b> Arial, then Helvetica, then the system sans.
          </div>
        </div>
      </div>
      <div class="note">Both faces are SIL OFL 1.1: free to use, embed and
      redistribute, including commercially. The licence text ships next to the fonts
      and must travel with them.</div>""")

    # 10 imagery
    page("Imagery", f"""
      <h1>Imagery</h1><div class="rule"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10mm;">
        <div>
          <p>Photography is calm, wide and unpeopled. Architecture at golden hour,
          deep green planting, soft haze on distance. Grade towards forest green,
          cream and gold; pull saturation down rather than up.</p>
          <div class="spec" style="margin-top:4mm">
            <b>Always</b> leave one third of the frame quiet for type.<br>
            <b>Never</b> a stock-looking handshake, a key close-up, or a sky
            oversaturated into cyan.<br>
            <b>Watermark</b> with the monogram at 9 % opacity, bottom-right, never
            across the subject.
          </div>
          <div class="note"><b>Placeholder.</b> The backgrounds in this kit were
          generated procedurally from the brand tokens, not photographed. Replace them
          with real photography before launch; the prompts to commission or generate
          them are in <span class="mono">assets/inbox/README.txt</span>.</div>
        </div>
        <div>
          <img src="{uri(KIT / '06_Web/hero_1920x800.jpg')}"
               style="width:100%;border-radius:1mm">
          <div class="cap" style="text-align:left">hero_1920x800 — left third kept
            clear for the headline</div>
          <img src="{uri(KIT / '03_Social/instagram_post_1080.png')}"
               style="width:52%;margin-top:4mm;border-radius:1mm">
          <div class="cap" style="text-align:left">instagram post template</div>
        </div>
      </div>""")

    # 11 applications
    page("Applications", f"""
      <h1>Applications</h1><div class="rule"></div>
      <div class="grid g4">
        <div class="tile"><img src="{uri(ROOT / 'review/dodont/2_do.png')}">
          <div class="cap">primary lockup</div></div>
        <div class="tile"><img src="{uri(KIT / '02_Favicon/icon-512.png')}">
          <div class="cap">favicon / app icon</div></div>
        <div class="tile"><img src="{uri(KIT / '03_Social/profile_1080.png')}">
          <div class="cap">social profile</div></div>
        <div class="tile"><img src="{uri(KIT / '05_Templates/email/banner_1200x400.png')}">
          <div class="cap">e-mail banner</div></div>
        <div class="tile"><img src="{uri(KIT / '03_Social/linkedin_banner_1584x396.png')}">
          <div class="cap">linkedin banner</div></div>
        <div class="tile"><img src="{uri(KIT / '06_Web/og_1200x630.png')}">
          <div class="cap">open graph card</div></div>
        <div class="tile"><img src="{uri(KIT / '03_Social/instagram_story_1080x1920.png')}"
             style="max-height:30mm"><div class="cap">story template</div></div>
        <div class="tile"><img src="{uri(KIT / '03_Social/google_business_cover_1024x576.png')}">
          <div class="cap">google business</div></div>
      </div>
      <div class="note">Print items — Visitenkarte, Briefpapier, Exposé cover,
      Verkaufsschild and the two Stempel — live in <b>04_Print</b> as RGB previews.
      They carry a red NOT FOR PRINT bar until the client data is filled in.</div>""")

    # 12 file index
    page("File index", f"""
      <h1>What is where</h1><div class="rule"></div>
      <table>
        <tr><th>Folder</th><th>Contents</th><th>Reach for it when</th></tr>
        <tr><td>00_Master</td><td>tokens.json, AV_master.svg, 42 layout SVGs</td>
            <td>you are changing the artwork itself</td></tr>
        <tr><td>01_Logo</td><td>SVG · PDF · EPS · PNG 1000/3000 · JPG — 238 files</td>
            <td>every normal use of the logo</td></tr>
        <tr><td>02_Favicon</td><td>ico, PNG set, webmanifest, head snippet</td>
            <td>a browser tab or an installed web app</td></tr>
        <tr><td>03_Social</td><td>eight platform sizes</td>
            <td>a profile, banner or post template</td></tr>
        <tr><td>04_Print</td><td>mm-accurate SVG + RGB-preview PDF, README_PDFX4</td>
            <td>anything going to a printer</td></tr>
        <tr><td>05_Templates</td><td>dotx, potx, docx, pptx, e-mail signature</td>
            <td>a letter, an invoice, a deck or a signature</td></tr>
        <tr><td>06_Web</td><td>header SVGs, hero, OG card, 9 % watermark</td>
            <td>the website</td></tr>
        <tr><td>07_Fonts</td><td>Cinzel + Montserrat variable TTF, both OFL texts</td>
            <td>installing the faces or handing them to a supplier</td></tr>
        <tr><td>08_Brandguide</td><td>this document</td>
            <td>briefing anyone who will touch the brand</td></tr>
        <tr><td>09_Motion</td><td>MP4 and WebM logo intro</td>
            <td>a video sting</td></tr>
      </table>
      <div class="note"><b>Three-line rule of thumb.</b>
      On green, use <b>full-dark</b>. On white or cream, use <b>full-light</b>.
      One ink, embossing or anything under 64 px, use a <b>1c</b> mode and the
      <b>simple monogram</b>.</div>""")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_pages()
    doc = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
           f"<title>Auguste Viktoria Immobilien — Brand Guide</title>"
           f"<style>{CSS}</style></head><body>{''.join(PAGES)}</body></html>")
    src = ROOT / "review/brandguide.html"
    src.write_text(doc)

    pdf = OUT / "AV_Brandguide.pdf"
    subprocess.run([
        chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
        "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=20000",
        f"--print-to-pdf={pdf}", uri(src),
    ], check=True, capture_output=True, timeout=300)
    print(f"  {len(PAGES)} pages -> {pdf.relative_to(ROOT)} "
          f"{pdf.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()

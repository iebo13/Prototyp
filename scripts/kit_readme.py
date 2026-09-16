#!/usr/bin/env python3
"""Write AV-Brand-Kit/README.md — the hand-off document that ships with the kit.

Generated rather than hand-written so the counts, the colour table and the list of
open placeholders can never drift from what is actually in the folder.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L      # noqa: E402
import layouts as LY    # noqa: E402

ROOT = L.ROOT
KIT = ROOT / "AV-Brand-Kit"
TOK = json.loads((KIT / "00_Master/tokens.json").read_text())

PLACEHOLDER = re.compile(r"\[[A-ZÄÖÜ][^\]\n]{2,60}\]|\{\{[A-Za-z_][A-Za-z0-9_]*\}\}")
SEARCH_EXT = {".svg", ".md", ".txt", ".html", ".json", ".xml", ".webmanifest"}
DOC_FILES = {"README.md", "README_PDFX4.md"}   # these *document* placeholders


def counts() -> dict[str, int]:
    return {d.name: sum(1 for _ in d.rglob("*") if _.is_file())
            for d in sorted(KIT.iterdir()) if d.is_dir()}


def placeholders() -> dict[str, list[str]]:
    found: dict[str, set[str]] = {}
    for p in KIT.rglob("*"):
        if (not p.is_file() or p.suffix.lower() not in SEARCH_EXT
                or p.name in DOC_FILES):
            continue
        for m in PLACEHOLDER.findall(p.read_text(errors="ignore")):
            found.setdefault(m, set()).add(str(p.relative_to(KIT)))
    return {k: sorted(v) for k, v in sorted(found.items())}


def main() -> None:
    cnt = counts()
    total = sum(cnt.values())
    ph = placeholders()

    colour_rows = "\n".join(
        f"| {n} | `{v['hex']}` | {v['rgb'][0]} {v['rgb'][1]} {v['rgb'][2]} | "
        f"{' '.join(str(c) for c in v['cmyk_approx'])} | {v['use']} |"
        for n, v in TOK["colors"].items())

    folder_rows = "\n".join(
        f"| `{name}` | {n} |" for name, n in cnt.items())

    minsize_rows = "\n".join(
        f"| {l.replace('_', ' ')} | {mm} | {px} |"
        for l, (mm, px) in LY.MIN_SIZE.items())

    ph_rows = ("\n".join(
        f"| `{k}` | {len(v)} | {', '.join(v[:3])}{' …' if len(v) > 3 else ''} |"
        for k, v in ph.items()) or "| — | 0 | none left |")

    (KIT / "README.md").write_text(f"""# Auguste Viktoria Immobilien — Brand Kit v1.0

{total} files. Everything here was built from one vector master; nothing was traced
from a screenshot and no image model ever drew the logo.

## Three-line rule of thumb

1. On green, use **full-dark**. On white or cream, use **full-light**.
2. One ink, embossing, engraving or anything under 64 px: use a **1c** mode and the
   **simple monogram**.
3. If you are unsure which file, take the **SVG**. It scales, it prints, and it is
   the same artwork as every other format here.

## Naming

```
AV_{{layout}}_{{mode}}[_{{width}}px][_on-{{background}}].{{ext}}
```

Seven layouts: `stacked` `stacked_tagline` `horizontal` `horizontal_tagline`
`monogram` `monogram_simple` `wordmark`.
Six modes: `full-dark` `full-light` `1c-cream` `1c-white` `1c-black` `1c-gold`.

## What is where

| Folder | Files |
|---|---|
{folder_rows}

- **00_Master** — `tokens.json`, the live-font master and the 42 layout sources.
  Change artwork here, never in an export.
- **01_Logo** — SVG, PDF, EPS, PNG at 1000 and 3000 px, and the two JPG
  combinations. This is the folder you will use every day.
- **02_Favicon** — `favicon.ico`, the PNG set, `site.webmanifest` and an HTML
  `<head>` snippet to paste as-is.
- **03_Social** — eight platform sizes, each exact.
- **04_Print** — millimetre-accurate SVG plus RGB-preview PDFs.
  Read `README_PDFX4.md` before sending anything to a printer.
- **05_Templates** — Word `.dotx`, PowerPoint `.potx`, an invoice, and the e-mail
  signature with its banner.
- **06_Web** — header SVGs, hero, Open Graph card, 9 % watermark.
- **07_Fonts** — Cinzel and Montserrat variable TTFs with both OFL texts.
- **08_Brandguide** — `AV_Brandguide.pdf`, 12 pages, A4 landscape.
- **09_Motion** — MP4 and WebM logo intro.

## Colour

| Token | HEX | RGB | CMYK approx. | Use |
|---|---|---|---|---|
{colour_rows}

**The CMYK column is an approximation computed from sRGB, not a measured
separation.** Proof it in Affinity against Coated FOGRA39 before any print run.
`{L.C['green']}` sits very close to black on uncoated stock — ask the printer whether a
spot colour or a rich-black build serves the job better.

## Minimum size

| Layout | Print | Screen |
|---|---|---|
{minsize_rows}

Clear space on all four sides is **X**, the cap height of the A in AUGUSTE. It is
already baked into every supplied file's viewBox.

## Type

**Cinzel** for the name, the monogram and headlines. **Montserrat** for IMMOBILIEN,
the tagline and all body copy — Light 300 for the tagline, Regular 400 for text,
SemiBold 600 for emphasis. Both are SIL OFL 1.1: free to use, embed and redistribute
commercially, provided the licence text travels with the font files. Both licences
are in `07_Fonts`.

## Open placeholders

Every one of these must be replaced before the file it sits in is published or
printed. Nothing legal was invented at build time: German Impressum data and the
§34c GewO authorisation must come from the client.

| Placeholder | Files | Where |
|---|---|---|
{ph_rows}

Each print sheet in `04_Print` carries a red **NOT FOR PRINT** bar while any
placeholder remains. Fill the client-data block in `CLAUDE.md`, then re-run
`python3 scripts/print_items.py` and the bar disappears.

## Known limitations of this build

- **Backgrounds are procedural, not photographic.** No image-model key was available,
  so the hero, the Open Graph card, the social templates and the Exposé cover use
  backgrounds generated from the brand tokens and the real ridge path. They are calm
  and on-brand, but they are not the photographs the brief describes. The exact
  prompts to commission or generate replacements are in
  `assets/inbox/README.txt`; drop a file in that folder and rebuild.
- **The feather is hand-authored vector, not a traced generation.** For this
  deliverable that is an improvement: it is already flat, already on-token, and has
  no stray nodes. Swapping in a generated one changes nothing downstream.
- **PDF/X-4 is a manual step.** Inkscape cannot write it. `04_Print/README_PDFX4.md`
  gives the five-line Affinity recipe.

## Rebuilding

```bash
python3 scripts/build_feather.py      # assets/feather.svg + feather_1c.svg
python3 scripts/fit_master.py         # master, fitted against ref/logo_AV.png
python3 scripts/build.py              # 42 layouts -> 238 files in 01_Logo
python3 scripts/backgrounds.py        # procedural backgrounds
python3 scripts/derive.py             # favicons, web, social, e-mail, motion
python3 scripts/print_items.py        # 04_Print
node    scripts/make_docx.js          # Word letterhead + invoice
node    scripts/make_pptx.js          # PowerPoint master
python3 scripts/office_templates.py   # .dotx / .potx conversion
python3 scripts/dodont.py             # brand-guide examples
python3 scripts/brandguide.py         # the guide PDF
python3 scripts/qa.py                 # the gate
```
""")
    print(f"wrote AV-Brand-Kit/README.md  ({total} files, {len(ph)} open placeholders)")


if __name__ == "__main__":
    main()

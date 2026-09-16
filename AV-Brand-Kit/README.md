# Auguste Viktoria Immobilien — Brand Kit v1.0

336 files. Everything here was built from one vector master; nothing was traced
from a screenshot and no image model ever drew the logo.

## Three-line rule of thumb

1. On green, use **full-dark**. On white or cream, use **full-light**.
2. One ink, embossing, engraving or anything under 64 px: use a **1c** mode and the
   **simple monogram**.
3. If you are unsure which file, take the **SVG**. It scales, it prints, and it is
   the same artwork as every other format here.

## Naming

```
AV_{layout}_{mode}[_{width}px][_on-{background}].{ext}
```

Seven layouts: `stacked` `stacked_tagline` `horizontal` `horizontal_tagline`
`monogram` `monogram_simple` `wordmark`.
Six modes: `full-dark` `full-light` `1c-cream` `1c-white` `1c-black` `1c-gold`.

## What is where

| Folder | Files |
|---|---|
| `00_Master` | 44 |
| `01_Logo` | 238 |
| `02_Favicon` | 9 |
| `03_Social` | 8 |
| `04_Print` | 15 |
| `05_Templates` | 8 |
| `06_Web` | 6 |
| `07_Fonts` | 5 |
| `08_Brandguide` | 1 |
| `09_Motion` | 2 |

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
| green | `#062014` | 6 32 20 | 100 0 100 70 | primary background, dark-mode base, 1c print on light |
| cream | `#EBE1CC` | 235 225 204 | 0 5 14 6 | wordmark/letters on dark |
| gold | `#D1A976` | 209 169 118 | 0 22 51 14 | mountains, rules, tagline, accents |
| peacock | `#337B56` | 51 123 86 | 100 0 51 41 | feather body |
| teal | `#21897F` | 33 137 127 | 100 0 12 37 | feather eye |
| white | `#FFFFFF` | 255 255 255 | 0 0 0 0 | 1c-white mode |
| black | `#000000` | 0 0 0 | 0 0 0 100 | 1c-black mode |

**The CMYK column is an approximation computed from sRGB, not a measured
separation.** Proof it in Affinity against Coated FOGRA39 before any print run.
`#062014` sits very close to black on uncoated stock — ask the printer whether a
spot colour or a rich-black build serves the job better.

## Minimum size

| Layout | Print | Screen |
|---|---|---|
| stacked | 25 mm | 120 px |
| stacked tagline | 30 mm | 150 px |
| horizontal | 40 mm | 180 px |
| horizontal tagline | 45 mm | 200 px |
| monogram | 8 mm | 32 px |
| monogram simple | 8 mm | 32 px |
| wordmark | 30 mm | 140 px |

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
| `[AMTSGERICHT ... HRB ...]` | 1 | 04_Print/Briefpapier_A4.svg |
| `[BEHÖRDE, ORT]` | 1 | 04_Print/Briefpapier_A4.svg |
| `[DE...]` | 1 | 04_Print/Briefpapier_A4.svg |
| `[NAME]` | 3 | 04_Print/Briefpapier_A4.svg, 04_Print/Visitenkarte_back_85x55.svg, 05_Templates/email/signature.html |
| `[PLACEHOLDER]` | 1 | 05_Templates/email/signature.html |
| `[PLZ ORT]` | 3 | 04_Print/Briefpapier_A4.svg, 04_Print/Visitenkarte_back_85x55.svg, 05_Templates/email/signature.html |
| `[POSITION]` | 2 | 04_Print/Visitenkarte_back_85x55.svg, 05_Templates/email/signature.html |
| `[RECHTSFORM]` | 2 | 04_Print/Briefpapier_A4.svg, 05_Templates/email/signature.html |
| `[STRASSE NR]` | 3 | 04_Print/Briefpapier_A4.svg, 04_Print/Visitenkarte_back_85x55.svg, 05_Templates/email/signature.html |
| `{{BANNER_URL}}` | 1 | 05_Templates/email/signature.html |
| `{{OBJEKTTITEL}}` | 1 | 04_Print/Expose_Cover_A4.svg |

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

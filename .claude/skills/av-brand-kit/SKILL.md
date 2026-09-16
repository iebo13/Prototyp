---
name: av-brand-kit
description: Build the complete Auguste Viktoria Immobilien brand kit (logo layouts, colour modes, all export formats, favicons, social, web, print, office templates, brand guide) from a rebuilt vector master. Use whenever the user mentions the AV logo, brand kit, exports, favicons, Visitenkarte, Briefpapier, Exposé, brand guide or any deliverable in this project.
---

# AV Brand Kit — recipes and rules

## 0. Toolchain (verify with `which` before starting; report anything missing)
- `inkscape` ≥ 1.2 (all vector conversions and rasterisation)
- `magick` (ImageMagick 7) — on Ubuntu it may be `convert`/`identify` (IM6); detect and adapt
- `ffmpeg`, `pngquant`, `svgo`, `python3` with `vtracer`, `Pillow`, `lxml`
- `nano-banana` CLI (Nano Banana 2 / Gemini; `-t` gives green-screen transparency via ffmpeg colorkey+despill)
- `openai` python package + `OPENAI_API_KEY` for GPT Image 2 (`background="transparent"`, preview since Aug 2026; if the API rejects it, generate on solid `#00FF00` and key with ffmpeg exactly like nano-banana `-t`)
- Fonts installed system-wide: Cinzel, Montserrat (`fc-list | grep -iE "cinzel|montserrat"`)
- Claude Code plugins: `document-skills` (docx, pptx, pdf, xlsx) and `example-skills` (canvas-design) from the `anthropic-agent-skills` marketplace

If `OPENAI_API_KEY` or `GEMINI_API_KEY` is missing, do not fake it: write the exact prompt to `assets/inbox/README.txt`, tell the user which file to drop into `assets/inbox/`, and continue with the phases that don't need it.

## 1. Tokens
Generate `AV-Brand-Kit/00_Master/tokens.json` from the table in CLAUDE.md, plus derived CMYK values computed with the FOGRA39-style approximation (note in the file that CMYK must be proofed in Affinity before print). Every script reads this file.

## 2. Master SVG — how to rebuild it
`AV-Brand-Kit/00_Master/AV_master.svg`, viewBox 0 0 1000 1000, live fonts, one `<g id="…">` per component:
- `#monogram`  — "A" and "V" in Cinzel. The V's left stroke overlaps the A's right leg exactly as in the reference; the A is slightly smaller and sits lower-left. Reproduce proportions by measuring the reference (`ref/logo_AV.png`), not by guessing.
- `#mountains` — a single open gold path: jagged ridge with three peaks rising from the A's apex to the top-right, ending in a long tail to the right. Stroke-width ≈ 1.2 % of viewBox, round joins, fill none.
- `#feather`   — `assets/feather.svg` (see §3), scaled so the quill runs along the V's right stroke and the eye sits top-right of the V.
- `#wordmark`  — "AUGUSTE VIKTORIA", Cinzel, small-caps look (large first letters A and V, rest ~72 % cap height), tracking ≈ 4 %.
- `#subline`   — "IMMOBILIEN", Montserrat Regular, letter-spacing ≈ 0.45 em, gold hairline rules left and right, vertically centred on the x-height.
- `#tagline`   — "MEHR ALS NUR EIN ZUHAUSE", Montserrat Light, letter-spacing ≈ 0.3 em, gold.
Colours via CSS classes on the `<svg>`: `.c-green .c-cream .c-gold .c-peacock .c-teal`. Nothing has a hard-coded fill.

Approval loop: render master and reference side by side with a 50 % blend overlay
```
inkscape AV_master.svg --export-type=png --export-width=1254 --export-background="#062014" -o review/master.png
magick ref/logo_AV.png review/master.png +append review/compare.png
magick ref/logo_AV.png review/master.png -compose blend -define compose:args=50 -composite review/overlay.png
```
Show both to the user and STOP.

## 3. Feather (the only traced element)
1. Generate with GPT Image 2 (`scripts/gen_gpt_image.py`), largest square size the API allows, `background="transparent"`, `output_format="png"`, prompt P1 (§9). Fallback: `nano-banana "<P1>" -t -s 2K -o feather -d assets`.
2. `vtracer --input assets/feather.png --output assets/feather_raw.svg --colormode color --mode spline --filter_speckle 8 --color_precision 6 --corner_threshold 60`
3. `svgo assets/feather_raw.svg --multipass -o assets/feather.svg`, then snap every fill to the nearest token colour (peacock, teal, gold, green) with a small lxml script; delete paths smaller than 0.2 % of the bbox.
4. Also produce `assets/feather_1c.svg`: union of all shapes (one silhouette) for 1-colour modes.
Tell the user that 10–15 min of node cleanup in Affinity on `feather.svg` is worth it before Phase 3 — offer to wait.

## 4. Layouts (each is its own SVG in `00_Master/layouts/`, viewBox includes clear space)
| id | content |
|---|---|
| `stacked` | monogram + wordmark + subline (the reference, minus tagline) |
| `stacked_tagline` | stacked + tagline |
| `horizontal` | monogram left (height = 1), gap 0.35, right block: wordmark over subline, block vertically centred |
| `horizontal_tagline` | horizontal + tagline under subline |
| `monogram` | A/V + mountains + feather only |
| `monogram_simple` | A/V + mountains + feather_1c silhouette — for anything ≤ 64 px |
| `wordmark` | wordmark + subline only |
Clear space = cap height of the wordmark "A" (call it X) on all four sides. Minimum widths: stacked 25 mm / 120 px, horizontal 40 mm / 180 px, monogram 8 mm / 32 px (use `monogram_simple` below 64 px).

## 5. Colour modes (class substitution on each layout SVG)
| mode | letters/wordmark | mountains, rules, tagline | feather | intended background |
|---|---|---|---|---|
| `full-dark`  | cream | gold | peacock/teal/gold | green |
| `full-light` | green | gold | peacock/teal/gold | white or cream |
| `1c-cream`   | cream | cream | feather_1c cream | dark |
| `1c-white`   | white | white | feather_1c white | dark |
| `1c-black`   | black | black | feather_1c black | light |
| `1c-gold`    | gold  | gold  | feather_1c gold | either |
Backgrounds are NOT part of the vector files (transparent). They are added only for the JPG exports and the mockups.

## 6. Export recipe (scripts/build.py — idempotent, Python subprocess calls)
For every layout × mode, from the outlined SVG:
```
inkscape in.svg --export-type=svg --export-text-to-path --export-plain-svg -o SVG/AV_{layout}_{mode}.svg
inkscape in.svg --export-type=pdf --export-text-to-path -o PDF/AV_{layout}_{mode}.pdf
inkscape in.svg --export-type=eps --export-text-to-path -o EPS/AV_{layout}_{mode}.eps
inkscape in.svg --export-type=png --export-width=1000 --export-background-opacity=0 -o PNG/AV_{layout}_{mode}_1000px.png
inkscape in.svg --export-type=png --export-width=3000 --export-background-opacity=0 -o PNG/AV_{layout}_{mode}_3000px.png
svgo SVG/ --multipass   # keep viewBox
```
JPGs (only these two combinations, 1000 + 3000 px):
```
magick PNG/AV_{layout}_full-dark_3000px.png  -background "#062014" -flatten -quality 92 JPG/AV_{layout}_full-dark_on-green_3000px.jpg
magick PNG/AV_{layout}_full-light_3000px.png -background "#FFFFFF" -flatten -quality 92 JPG/AV_{layout}_full-light_on-white_3000px.jpg
```
Naming is fixed: `AV_{layout}_{mode}[_{width}px][_on-{bg}].{ext}`. Print a per-folder file count at the end and a contact sheet:
```
magick montage PNG/*_1000px.png -tile 6x -geometry 300x300+10+10 -background "#888" review/contact_sheet.png
```

## 7. Derived assets
Favicons (`02_Favicon/`, from `monogram_simple`, full-dark on green, opaque, monogram at 72 % of the square):
```
inkscape monogram_simple_full-dark.svg --export-type=png --export-width=1024 --export-background="#062014" -o icon-1024.png
magick icon-1024.png -define icon:auto-resize=48,32,16 favicon.ico
magick icon-1024.png -resize 180x180 apple-touch-icon.png
magick icon-1024.png -resize 192x192 icon-192.png ; magick icon-1024.png -resize 512x512 icon-512.png
```
plus `site.webmanifest` and an HTML `<head>` snippet.

Web (`06_Web/`): header SVGs = `AV_horizontal_full-dark.svg` (dark UI) and `AV_horizontal_full-light.svg` (light UI), copied and renamed `header-dark.svg` / `header-light.svg`; hero 1920×800 (P4 background, `magick -resize 1920x -gravity center -extent 1920x800`, logo overlay optional, left third kept clear); OG 1200×630 (P2 16:9 background + horizontal full-dark logo centred at 60 % width); watermark:
```
magick PNG/AV_monogram_1c-cream_3000px.png -alpha set -channel A -evaluate multiply 0.09 +channel AV_watermark_9pct.png
```

Social (`03_Social/`, all PNG, logo composited with `magick … -gravity … -composite`): profile 1080² (green, gold ring at 86 % diameter, 8 px, `monogram_simple` cream at 52 %); LinkedIn 1584×396 (horizontal logo right-centred, left 30 % kept free for the profile-photo overlap); Facebook 820×312; Instagram post 1080² template (P2 background, logo bottom-centre at 28 % width, empty upper area); Story 1080×1920 (P3, logo top-centre); Google Business logo 720² and cover 1024×576; WhatsApp = profile.

Email (`05_Templates/email/`): banner 1200×400 (renders at 600×200), horizontal full-dark on green, tagline under it; `pngquant --quality=65-90 --speed 1 banner_1200x400.png -o banner_1200x400.png --force`; assert size < 60 KB, otherwise reduce to 1000×333 and retry. Also `signature.html`: table-based, inline CSS, Montserrat with Arial fallback, image `src` left as `{{BANNER_URL}}`.

Motion (`09_Motion/`, bonus):
```
ffmpeg -y -f lavfi -i color=c=0x062014:s=1920x1080:d=4 -loop 1 -t 4 -i PNG/AV_stacked_full-dark_1000px.png \
  -filter_complex "[1]scale=900:-1,fade=in:st=0.3:d=1[l];[0][l]overlay=(W-w)/2:(H-h)/2,fade=out:st=3.2:d=0.8" \
  -c:v libx264 -pix_fmt yuv420p AV_logo_intro.mp4
```
and a `.webm` (libvpx-vp9) of the same.

## 8. Print and office (`04_Print/`, `05_Templates/`)
Build print items as SVG with mm units, 3 mm bleed and crop marks, export PDF with Inkscape (text to path). Name them `*_RGB-preview.pdf` and state in the README that the final PDF/X-4 export happens in Affinity by opening the PDF (or SVG) and exporting with the PDF/X-4 preset, CMYK, FOGRA39. Do not claim PDF/X compliance for Inkscape output.
- Visitenkarte 85×55 mm (+3 mm bleed = 91×61 mm): front = stacked full-dark centred on green; back = name/title/contact in Montserrat on cream, monogram 1c-gold small bottom-right. Two-sided, 300 dpi bitmap check via `inkscape --export-dpi=300`.
- Briefpapier A4: horizontal logo top-left at 45 mm wide (12 mm margin), address line right-aligned, footer 7 pt Montserrat with the full legal line from CLAUDE.md, gold hairline above footer.
- Exposé cover A4: P5 background full-bleed, green band bottom 28 % with stacked logo cream and "EXPOSÉ · {{OBJEKTTITEL}}" placeholder.
- Verkaufsschild at `sign_size_mm`: green, stacked logo, "ZU VERKAUFEN" Cinzel, phone and web Montserrat, all vector.
- Stempel/Siegel: 40 mm circle, 1c-black and 1c-green, monogram centre, company name on the outer path.
- Rechnungsvorlage: A4 docx using the letterhead, table with Netto/MwSt/Brutto.
Word `.dotx` and PowerPoint `.potx`: build with the docx/pptx skills as .docx/.pptx first (header logo = PNG 3000 px scaled to 45 mm; slide master 16:9 with title slide on green + content slide on cream, P6 texture optional). Then convert: unzip, in `[Content_Types].xml` change the main part content type to `…wordprocessingml.template.main+xml` (Word) or `…presentationml.template.main+xml` (PowerPoint), rezip, rename to `.dotx`/`.potx`. Keep the .docx/.pptx too. Ask the user to confirm the template opens as "New from template" in Word/PowerPoint.

Brand guide (`08_Brandguide/AV_Brandguide.pdf`): 10–14 pages built as HTML (real fonts, tokens) and printed to PDF with headless Chromium (canvas-design/pdf skill approach), A4 landscape: cover · logo & story · layouts · clear space & minimum sizes · colour modes · do/don't (8 examples, rendered from the real files: no stretching, no recolouring, no drop shadow, no low-contrast background, no rotation, no outline, no busy photo behind, no tagline below minimum size) · colours HEX/RGB/CMYK · typography · imagery style · applications · file index.

## 9. Image-model prompts (use verbatim; never include the logo in a generation prompt)
P1 feather (GPT Image 2, transparent):
```
Single peacock feather, flat vector illustration, exactly four flat colours: green #337B56, teal #21897F, gold #D1A976, dark green #062014. No gradients, no texture, no shading, hard clean edges. The feather curves gently up to the right like a calligraphic stroke, thin gold spine, one eye near the top. Isolated object, nothing else in frame.
```
P2 background 1:1 and 16:9 (Nano Banana 2, 4K):
```
Subtle dark forest green textured paper background, colour #062014, faint fine hairline mountain silhouette in gold #D1A976 in the bottom-right corner, large empty calm area, premium minimal aesthetic, no text, no logo, no watermark, no people.
```
P3 story 9:16: P2 but "mountain silhouette along the bottom edge, empty upper two thirds".
P4 hero (21:9, 4K, crop to 1920×800):
```
Editorial real-estate photograph, elegant modern villa exterior at golden hour in {{region_for_hero}}, deep green pines, soft haze on distant peaks, warm cream and gold light, muted luxury colour grade in forest green #062014, cream #EBE1CC and gold #D1A976. Wide composition with the left third empty and calm for text overlay. No people, no text, no logos, no watermarks, ultra sharp.
```
P5 exposé cover (3:4, 4K):
```
Bright architectural interior photograph, high-ceilinged living room with large windows, warm daylight, neutral cream and oak tones with deep green accents, empty upper third for a title, no text, no people, no watermarks, editorial magazine quality.
```
P6 slide texture (16:9): `Very subtle cream paper texture #EBE1CC, almost plain, faint gold hairline rule at the bottom, nothing else, no text, no logo.`
P7 mockups (Nano Banana 2 with `-r` = a real exported PNG; presentation only, never a deliverable): `Photorealistic product mockup of a {{item}}, dark green #062014 material with the attached logo in gold foil, applied exactly as given — do not redraw, alter or restyle the logo. Soft studio light, shallow depth of field, 3:2.`

## 10. QA gate (run before every checkpoint; print a table)
- No `<text>` in any file under `01_Logo/**/SVG` (`grep -rl "<text" …` must be empty)
- Every PNG has an alpha channel (`magick identify -format "%[channels]\n"` contains `alpha`/`rgba`) except favicons, JPGs and social composites
- Widths exactly 1000 / 3000 px; favicons exactly 16/32/48/180/192/512; social sizes exact
- `banner_1200x400.png` < 60 KB
- Expected file count = layouts(7) × modes(6) × formats(5) + JPG(7×2×2) = 238 files in `01_Logo`; report the actual number and any delta
- Every SVG renders (`inkscape --query-all file.svg` exits 0) and a contact sheet exists in `review/`
- All placeholders `[…]` / `{{…}}` are listed in the report with their file locations

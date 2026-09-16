# Master prompt — paste everything between the lines into Claude Code, in the project folder

---------------------------------------------------------------------

You are building the complete brand kit for Auguste Viktoria Immobilien from the existing logo in `ref/logo_AV.png`. Read `CLAUDE.md` and `.claude/skills/av-brand-kit/SKILL.md` in full before you touch anything — the skill contains the exact tokens, layouts, colour modes, naming, commands, prompts and QA gate. Follow them literally. Do not improvise on naming, colours or geometry.

Work in phases. At every line marked CHECKPOINT you stop, show me what I ask for, and wait for my explicit "go". Commit to git at the end of each phase. End each phase with a short report: produced, counts, failed, skipped, open placeholders.

## Phase 0 — environment and skeleton
1. Verify the toolchain listed in SKILL.md §0 with `which` / version checks and `fc-list` for Cinzel and Montserrat. Print a table: tool, found, version. Tell me exactly what to install if anything is missing and stop.
2. Check for `OPENAI_API_KEY` and `GEMINI_API_KEY`. If either is missing, note it and plan to use `assets/inbox/` as described in the skill.
3. `git init` if needed. Create `ref/`, `assets/inbox/`, `scripts/`, `review/` and the full `AV-Brand-Kit/` tree from SKILL.md (00_Master … 09_Motion). Copy `ref_logo_AV.png` to `ref/logo_AV.png` if it isn't there yet.
4. Write `AV-Brand-Kit/00_Master/tokens.json` (SKILL §1) and `scripts/gen_gpt_image.py` (thin wrapper around the OpenAI Images API: model gpt-image-2, `background="transparent"`, `output_format="png"`, largest square size the current API reference allows — check the docs, don't guess; on a 400 for `background`, fall back to a solid #00FF00 background and key it with ffmpeg colorkey+despill).
5. Download Cinzel and Montserrat (variable TTFs) from github.com/google/fonts (`ofl/cinzel`, `ofl/montserrat`) into `AV-Brand-Kit/07_Fonts/` with their OFL.txt, and install them for Inkscape (`~/.fonts` or `~/Library/Fonts`, then `fc-cache -f`).
CHECKPOINT 0: show the tool table and the tree.

## Phase 1 — feather
Follow SKILL §3 exactly: generate `assets/feather.png` with prompt P1 (GPT Image 2 transparent; fallback nano-banana `-t`), vectorise with vtracer, clean with svgo + colour-snap script, produce `assets/feather.svg` and `assets/feather_1c.svg`. Render both to `review/feather.png` at 800 px on green and on white.
CHECKPOINT 1: show `review/feather.png`. Offer me the option to hand-clean `feather.svg` in Affinity before you continue.

## Phase 2 — master SVG (rebuild, not trace)
Build `AV-Brand-Kit/00_Master/AV_master.svg` per SKILL §2: measure the reference PNG (letter heights, baseline positions, the A/V overlap, mountain ridge points, feather angle, wordmark tracking, rule lengths) with Pillow and reproduce the proportions in the SVG. Live Cinzel/Montserrat text, CSS colour classes, one group per component. Produce `review/compare.png` and `review/overlay.png` with the commands in the skill.
CHECKPOINT 2: show both images and list the three biggest visible differences to the reference in your own words. I will give corrections; iterate until I say the master is approved. Do not start Phase 3 without that.

## Phase 3 — layouts, colour modes, exports
1. Create the 7 layout SVGs in `00_Master/layouts/` (SKILL §4) with clear space baked into the viewBox.
2. Write `scripts/build.py` (SKILL §6): layouts × 6 modes → SVG, PDF, EPS, PNG 1000/3000 transparent, the two JPG combinations, svgo pass, fixed naming, per-folder counts, contact sheet. Idempotent; a `--only layout=… mode=…` flag for reruns.
3. Run it. Run the QA gate (SKILL §10) and print the table.
CHECKPOINT 3: show `review/contact_sheet.png` and the QA table. Expected 238 files in `01_Logo`; explain any delta.

## Phase 4 — favicons, web, social, email, watermark, motion
Follow SKILL §7 for every item: favicon set + webmanifest + head snippet; header-dark/light SVGs; hero 1920×800 (P4 with `{{region_for_hero}}` from CLAUDE.md); OG 1200×630; watermark 9 %; all social sizes incl. Google Business; email banner < 60 KB + `signature.html`; MP4/WebM intro. Backgrounds via `nano-banana` with the prompts in SKILL §9 — generate 2 candidates each, pick the calmest, keep the raw files in `assets/`. Never let the model draw the logo; composite the real PNG.
CHECKPOINT 4: one montage of everything produced in this phase plus the banner file size.

## Phase 5 — print and office templates
Stop first if any placeholder in the "Client data" block of CLAUDE.md is still unfilled; list them and wait. Then follow SKILL §8: Visitenkarte (front/back), Briefpapier A4, Exposé cover, Verkaufsschild, Stempel, Rechnungsvorlage as SVG → `*_RGB-preview.pdf`; Word `.dotx` and PowerPoint `.potx` (title + content layouts) via the docx and pptx skills followed by the content-type conversion. Write `04_Print/README_PDFX4.md` explaining the Affinity PDF/X-4 step in five lines.
CHECKPOINT 5: page-1 previews of each print item as one montage.

## Phase 6 — brand guide, packaging, hand-off
1. Brand guide PDF per SKILL §8 (HTML → headless Chromium → `08_Brandguide/AV_Brandguide.pdf`), every image in it rendered from the real exported files, do/don't examples generated programmatically.
2. `AV-Brand-Kit/README.md`: what is where, which file to use when (3-line rule of thumb), naming convention, minimum sizes, colour table, font licence note, PDF/X-4 note, open placeholders.
3. Final QA gate over the whole tree, then `zip -r AV-Brand-Kit_v1.zip AV-Brand-Kit` and print the tree with sizes.
CHECKPOINT 6: final report. Then stop.

General: if a command fails, show the error and your fix before retrying; never silently skip a deliverable — mark it SKIPPED with a reason in the phase report.

---------------------------------------------------------------------

# Follow-up snippets (use as needed)

**Corrections at CHECKPOINT 2** (example):
```
Master corrections: the V is ~6 % too wide, its left stroke must overlap the A's right leg by about the stroke width; the mountain ridge starts exactly at the A's apex; feather angle ~38°, eye 12 % further right; wordmark tracking +2 %; IMMOBILIEN rules 10 % longer. Rebuild, regenerate compare.png and overlay.png, wait.
```

**Rerun one variant after Affinity cleanup of the feather:**
```
I replaced assets/feather.svg. Re-link it in AV_master.svg and all layouts, run scripts/build.py --only layout=all mode=all, rerun the QA gate, show the new contact sheet.
```

**Client mockups for the presentation (not deliverables):**
```
Generate 4 mockups with prompt P7 from the skill using nano-banana -r with the real exported PNGs: business card, office door sign, Verkaufsschild on a lawn, letterhead on a desk. Save to review/mockups/. Do not put them in AV-Brand-Kit.
```

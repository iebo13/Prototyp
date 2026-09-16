# Auguste Viktoria Immobilien — Brand Kit project

Read `.claude/skills/av-brand-kit/SKILL.md` before doing anything. It is the single source of truth for tokens, naming, export recipes and QA.

## Goal
Turn the existing stacked logo (`ref/logo_AV.png`) into a complete, print- and web-ready brand kit by REBUILDING it as vector — never by tracing the whole PNG and never by asking an image model to redraw it.

## Hard rules
1. The logo is never redrawn, restyled or "improved" by an AI image model. Image models are used ONLY for backgrounds, photos and client mockups; the real vector logo is composited on top afterwards.
2. Final SVGs contain no `<text>` elements — all type is converted to paths via Inkscape CLI. Fonts stay live only in `00_Master/AV_master.svg`.
3. Never rasterise a vector step that can stay vector. Bitmaps are produced only at the final export step.
4. Colours come from `00_Master/tokens.json`; never hard-code hex values elsewhere.
5. Stop at every CHECKPOINT in the prompt and wait for my approval before continuing.
6. Ask before spending API credits on more than 20 image generations, or before any command that deletes files.
7. `git commit` at the end of every phase with a message like `phase-3: layouts and exports`.
8. Every phase ends with a short written report: what was produced, file counts, anything that failed or was skipped.

## Brand tokens (canonical, sampled from the reference PNG)
| token   | hex     | use |
|---------|---------|-----|
| green   | #062014 | primary background, dark-mode base, 1c print on light |
| cream   | #EBE1CC | wordmark/letters on dark |
| gold    | #D1A976 | mountains, rules, tagline, accents |
| peacock | #337B56 | feather body |
| teal    | #21897F | feather eye |
| white   | #FFFFFF | 1c-white mode |
| black   | #000000 | 1c-black mode |

Fonts: **Cinzel** (name and monogram), **Montserrat** (IMMOBILIEN, tagline, body). Both Google Fonts / SIL OFL — ship the .ttf files in `07_Fonts/` with the licence.

## Client data (FILL IN BEFORE PHASE 5 — placeholders are deliberately obvious)
```
company:        Auguste Viktoria Immobilien [RECHTSFORM e.g. GmbH / e.K.]
tagline:        Mehr als nur ein Zuhause
street:         [STRASSE NR]
city:           [PLZ ORT]
phone:          [+49 ...]
email:          [info@...]
web:            [www....de]
geschaeftsfuehrer: [NAME]
registergericht:   [AMTSGERICHT ... HRB ...]   # if GmbH/UG; otherwise omit
ust_idnr:          [DE...]
gewo_34c:          Erlaubnis nach §34c GewO, erteilt durch [BEHÖRDE, ORT]
region_for_hero:   [e.g. Oberbayern / Allgäu / Bodensee]
sign_size_mm:      [ask the sign printer; default 1000x700]
```
If a placeholder is still unfilled when a phase needs it, stop and ask me — do not invent legal data.

## Layout of this repo
```
ref/            reference PNG (read-only)
assets/         intermediates (feather.png, backgrounds, raw generations)
scripts/        build.py, gen_gpt_image.py, helpers
review/         compare grids and contact sheets for my approval
AV-Brand-Kit/   the deliverable tree (see SKILL.md) — the only thing the client receives
```

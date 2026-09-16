# From RGB preview to print-ready PDF/X-4

1. Open the `*_RGB-preview.pdf` (or the matching `.svg`) in Affinity Designer or
   Publisher. The SVG keeps live vector geometry; the PDF is already outlined.
2. Set the document to CMYK, ICC profile **Coated FOGRA39 (ISO 12647-2:2004)**,
   under Document ▸ Colour.
3. Replace every `[PLACEHOLDER]` and `{{OBJEKTTITEL}}`. The red NOT FOR PRINT bar
   disappears once the source data in `CLAUDE.md` is filled and the sheet rebuilt.
4. Export ▸ PDF ▸ preset **PDF/X-4**, "Include bleed" on, bleed 3 mm,
   crop marks on. Save as `*_PRINT.pdf`.
5. Order a proof before the first run. `#062014` is very close to black on uncoated
   stock; ask the printer whether a spot colour or a rich-black build serves better.

Inkscape cannot write PDF/X-4, which is why this step is manual. Nothing in these
files is an obstacle to it — text is already converted to paths and bleed is already
3 mm on every side.

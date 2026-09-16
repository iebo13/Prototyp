# 05_Templates

| file | use |
|---|---|
| `Briefpapier_Vorlage.dotx` | Word letterhead. Open with File ▸ New ▸ From template. |
| `Briefpapier_Vorlage.docx` | the same letterhead as an ordinary document |
| `Rechnungsvorlage.docx` | A4 invoice on the letterhead, with Netto / MwSt / Brutto |
| `Praesentation_Vorlage.potx` | PowerPoint 16:9 master: title slide on green, content on cream |
| `Praesentation_Vorlage.pptx` | the same deck as an ordinary presentation |
| `email/banner_1200x400.png` | signature banner, renders at 600 × 200 |
| `email/signature.html` | table-based signature, inline CSS, Montserrat with Arial fallback |

Double-clicking a `.dotx` or `.potx` creates a **new document from the template**
rather than opening the template itself — that is the intended behaviour. To edit the
template, open it with File ▸ Open.

Every `[PLACEHOLDER]` and `{{TOKEN}}` must be replaced before use. The legal footer
carries the fields German law requires in business correspondence; none of them were
invented at build time.

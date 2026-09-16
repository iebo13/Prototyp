#!/usr/bin/env python3
"""Convert the generated .docx / .pptx into true Office templates (.dotx / .potx).

A template differs from a document only in the main part's content type, so the
conversion is: unzip, rewrite [Content_Types].xml, rezip. The .docx and .pptx are
kept alongside, as SKILL §8 asks.

Word:       …wordprocessingml.document.main+xml   -> …wordprocessingml.template.main+xml
PowerPoint: …presentationml.presentation.main+xml -> …presentationml.template.main+xml
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "AV-Brand-Kit/05_Templates"

SWAPS = {
    ".dotx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
              "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"),
    ".potx": ("application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
              "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"),
}


def convert(src: pathlib.Path, ext: str) -> pathlib.Path:
    old, new = SWAPS[ext]
    dst = src.with_suffix(ext)
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        with zipfile.ZipFile(src) as z:
            names = z.namelist()
            z.extractall(d)
        ct = d / "[Content_Types].xml"
        text = ct.read_text(encoding="utf-8")
        if old not in text:
            raise RuntimeError(f"{src.name}: main content type not found; "
                               f"cannot convert to {ext}")
        ct.write_text(text.replace(old, new), encoding="utf-8")
        # rewrite in the original entry order; [Content_Types].xml must stay first
        order = ["[Content_Types].xml"] + [n for n in names if n != "[Content_Types].xml"]
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
            for n in order:
                p = d / n
                if p.is_file():
                    z.write(p, n)
    return dst


VALIDATORS = {
    ".docx": "/mnt/skills/public/docx/scripts/office/validate.py",
    ".dotx": "/mnt/skills/public/docx/scripts/office/validate.py",
    ".pptx": "/mnt/skills/public/pptx/scripts/office/validate.py",
    ".potx": "/mnt/skills/public/pptx/scripts/office/validate.py",
}


def verify(path: pathlib.Path) -> str:
    """Schema, relationship and content-type validation of the OOXML package.

    LibreOffice is installed in this build environment but cannot load any file at
    all — it fails the same way on a plain .txt — so a render round-trip is not
    available here. The OOXML validators are the real check and they do run.
    """
    v = VALIDATORS.get(path.suffix)
    if not v or not pathlib.Path(v).exists():
        return "no validator available"
    r = subprocess.run([sys.executable, v, str(path)],
                       capture_output=True, text=True, timeout=240)
    tail = [ln for ln in r.stdout.strip().splitlines() if ln.strip()]
    if r.returncode != 0:
        return f"INVALID: {(tail[-1] if tail else r.stderr.strip())[:110]}"
    with zipfile.ZipFile(path) as z:
        parts = len(z.namelist())
    ct = "template" if path.suffix in SWAPS else "document"
    return f"valid OOXML {ct}, {parts} parts"


def main() -> None:
    made = []
    for name, ext in (("Briefpapier_Vorlage.docx", ".dotx"),
                      ("Praesentation_Vorlage.pptx", ".potx")):
        src = OUT / name
        if not src.exists():
            print(f"  {name}: MISSING — run make_docx.js / make_pptx.js first")
            continue
        dst = convert(src, ext)
        made.append(dst.name)
        print(f"  {src.name} -> {dst.name}  {dst.stat().st_size // 1024} KB")

    print("\nOOXML validation:")
    for p in sorted(OUT.glob("*")):
        if p.suffix in (".docx", ".pptx", ".dotx", ".potx"):
            print(f"  {p.name:<34} {verify(p)}")

    (OUT / "README.md").write_text("""# 05_Templates

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
""")
    made.append("README.md")
    print(f"\n{len(made)} files written")


if __name__ == "__main__":
    main()

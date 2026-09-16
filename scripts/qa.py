#!/usr/bin/env python3
"""QA gate for the AV brand kit (SKILL §10). Prints a table and exits non-zero on
any FAIL. Checks that do not apply yet (assets a later phase produces) report SKIP.

    python3 scripts/qa.py
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = ROOT / "AV-Brand-Kit"
LOGO = KIT / "01_Logo"
IM_ID = "magick" if shutil.which("magick") else "identify"


def identify(path: pathlib.Path, fmt: str) -> str:
    cmd = ([IM_ID, "identify", "-format", fmt, str(path)] if IM_ID == "magick"
           else [IM_ID, "-format", fmt, str(path)])
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


ROWS: list[tuple[str, str, str]] = []


def row(name: str, ok: bool | None, detail: str = "") -> None:
    ROWS.append((name, "PASS" if ok else ("SKIP" if ok is None else "FAIL"), detail))


# ---------------------------------------------------------------- 1 no live text
def check_no_text() -> None:
    svgs = list((LOGO / "SVG").glob("*.svg"))
    bad = [p.name for p in svgs if re.search(r"<text[\s>]", p.read_text())]
    row("no <text> in 01_Logo/SVG", not bad,
        f"{len(svgs)} files checked" + (f"; offenders: {bad[:4]}" if bad else ""))


# ------------------------------------------------------------------- 2 png alpha
def check_alpha() -> None:
    pngs = list((LOGO / "PNG").glob("*.png"))
    bad = [p.name for p in pngs
           if "a" not in identify(p, "%[channels]").lower()]
    row("01_Logo PNGs have alpha", not bad,
        f"{len(pngs)} files" + (f"; opaque: {bad[:4]}" if bad else ""))


# ------------------------------------------------------------------- 3 dimensions
def check_dimensions() -> None:
    bad = []
    for p in (LOGO / "PNG").glob("*.png"):
        m = re.search(r"_(\d+)px\.png$", p.name)
        if not m:
            bad.append(f"{p.name}: unparsable name")
            continue
        want = int(m.group(1))
        got = identify(p, "%w")
        if got != str(want):
            bad.append(f"{p.name}: {got} != {want}")
    row("01_Logo PNG widths exact", not bad, bad[0] if bad else "1000 / 3000 px")

    fav = KIT / "02_Favicon"
    if not any(fav.iterdir()):
        row("favicon sizes exact", None, "02_Favicon empty (phase 4)")
    else:
        want = {"icon-1024.png": 1024, "apple-touch-icon.png": 180,
                "icon-192.png": 192, "icon-512.png": 512,
                "icon-32.png": 32, "icon-16.png": 16}
        bad = [f"{n}: {identify(fav / n, '%w')} != {w}"
               for n, w in want.items()
               if (fav / n).exists() and identify(fav / n, "%w") != str(w)]
        missing = [n for n in want if not (fav / n).exists()]
        row("favicon sizes exact", not bad and not missing,
            ("missing " + ", ".join(missing)) if missing else
            (bad[0] if bad else f"{len(want)} icons"))

    soc = KIT / "03_Social"
    want_soc = {
        "profile_1080.png": (1080, 1080),
        "linkedin_banner_1584x396.png": (1584, 396),
        "facebook_cover_820x312.png": (820, 312),
        "instagram_post_1080.png": (1080, 1080),
        "instagram_story_1080x1920.png": (1080, 1920),
        "google_business_logo_720.png": (720, 720),
        "google_business_cover_1024x576.png": (1024, 576),
        "whatsapp_profile_1080.png": (1080, 1080),
    }
    if not soc.exists() or not any(soc.iterdir()):
        row("social sizes exact", None, "03_Social empty (phase 4)")
    else:
        bad, missing = [], []
        for n, (w, h) in want_soc.items():
            p = soc / n
            if not p.exists():
                missing.append(n)
                continue
            got = identify(p, "%wx%h")
            if got != f"{w}x{h}":
                bad.append(f"{n}: {got} != {w}x{h}")
        row("social sizes exact", not bad and not missing,
            ("missing " + ", ".join(missing[:3])) if missing else
            (bad[0] if bad else f"{len(want_soc)} images"))


# ------------------------------------------------------------------ 4 email banner
def check_banner() -> None:
    p = KIT / "05_Templates/email/banner_1200x400.png"
    if not p.exists():
        row("email banner < 60 KB", None, "not built yet (phase 4)")
        return
    kb = p.stat().st_size / 1024
    row("email banner < 60 KB", kb < 60, f"{kb:.1f} KB")


# ------------------------------------------------------------------- 5 file count
def check_count() -> None:
    import layouts as LY
    import avlogo as L
    n = sum(len(list(d.glob("*"))) for d in LOGO.iterdir() if d.is_dir())
    expected = len(LY.LAYOUTS) * len(L.MODES) * 5 + len(LY.LAYOUTS) * 2 * 2
    row("01_Logo file count", n == expected, f"{n} files, expected {expected}")


# ------------------------------------------------------------- 6 every svg renders
def check_renders() -> None:
    svgs = (list((LOGO / "SVG").glob("*.svg"))
            + list((KIT / "00_Master/layouts").glob("*.svg"))
            + [KIT / "00_Master/AV_master.svg"])
    bad = []
    for p in svgs:
        r = subprocess.run(["inkscape", "--query-all", str(p)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(p.name)
    row("every SVG renders", not bad,
        f"{len(svgs)} files" + (f"; failed: {bad[:3]}" if bad else ""))
    cs = ROOT / "review/contact_sheet.png"
    row("contact sheet exists", cs.exists(),
        f"{cs.stat().st_size // 1024} KB" if cs.exists() else "missing")


# ------------------------------------------------------------------ 7 placeholders
PLACEHOLDER = re.compile(r"\[[A-ZÄÖÜ][^\]\n]{2,60}\]|\{\{[A-Za-z_][A-Za-z0-9_]*\}\}")
SEARCH_EXT = {".svg", ".md", ".txt", ".html", ".json", ".xml", ".webmanifest"}
DOC_FILES = {"README.md", "README_PDFX4.md"}   # these *document* placeholders


def check_placeholders() -> None:
    found: dict[str, set[str]] = {}
    for p in KIT.rglob("*"):
        if (not p.is_file() or p.suffix.lower() not in SEARCH_EXT
                or p.name in DOC_FILES):
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        for m in PLACEHOLDER.findall(text):
            found.setdefault(m, set()).add(str(p.relative_to(KIT)))
    row("open placeholders", True, f"{len(found)} distinct")
    if found:
        print("\nOpen placeholders (each must be filled before print/publication):")
        for ph in sorted(found):
            locs = sorted(found[ph])
            print(f"  {ph:<28} {len(locs)} file(s): {', '.join(locs[:3])}"
                  + (" ..." if len(locs) > 3 else ""))


def main() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    check_no_text()
    check_alpha()
    check_dimensions()
    check_banner()
    check_count()
    check_renders()
    check_placeholders()

    print(f"\n{'check':<32}{'result':<8}detail")
    print("-" * 92)
    for name, res, detail in ROWS:
        print(f"{name:<32}{res:<8}{detail}")
    fails = [r for r in ROWS if r[1] == "FAIL"]
    skips = [r for r in ROWS if r[1] == "SKIP"]
    print(f"\n{len(ROWS) - len(fails) - len(skips)} pass, {len(fails)} fail, "
          f"{len(skips)} skip")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

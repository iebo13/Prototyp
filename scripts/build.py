#!/usr/bin/env python3
"""Export every layout x colour mode to SVG, PDF, EPS, PNG (1000 + 3000) and the two
JPG combinations, per SKILL §6. Idempotent: re-running overwrites in place.

    python3 scripts/build.py
    python3 scripts/build.py --only layout=stacked mode=full-dark
    python3 scripts/build.py --skip-raster        # vectors only, much faster

Naming is fixed:  AV_{layout}_{mode}[_{width}px][_on-{bg}].{ext}
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L      # noqa: E402
import layouts as LY    # noqa: E402

ROOT = L.ROOT
SRC = ROOT / "AV-Brand-Kit/00_Master/layouts"
LOGO = ROOT / "AV-Brand-Kit/01_Logo"

# ImageMagick 7 ships `magick`; Ubuntu's IM6 ships `convert`/`identify`/`montage`.
IM = "magick" if shutil.which("magick") else "convert"
IM_MONTAGE = ["magick", "montage"] if shutil.which("magick") else ["montage"]

JPG_BACKGROUNDS = {"full-dark": ("green", L.C["green"]),
                   "full-light": ("white", L.C["white"])}
PNG_WIDTHS = (1000, 3000)


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:4])}... failed:\n{r.stderr[-800:]}")


def inkscape(src: pathlib.Path, out: pathlib.Path, *extra: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["inkscape", str(src), *extra, "-o", str(out)])


def export_one(layout: str, mode: str, skip_raster: bool) -> list[str]:
    src = SRC / f"AV_{layout}_{mode}.svg"
    stem = f"AV_{layout}_{mode}"
    made = []

    inkscape(src, LOGO / "SVG" / f"{stem}.svg",
             "--export-type=svg", "--export-text-to-path", "--export-plain-svg")
    made.append(f"SVG/{stem}.svg")

    inkscape(src, LOGO / "PDF" / f"{stem}.pdf",
             "--export-type=pdf", "--export-text-to-path")
    made.append(f"PDF/{stem}.pdf")

    inkscape(src, LOGO / "EPS" / f"{stem}.eps",
             "--export-type=eps", "--export-text-to-path")
    made.append(f"EPS/{stem}.eps")

    if skip_raster:
        return made

    for w in PNG_WIDTHS:
        png = LOGO / "PNG" / f"{stem}_{w}px.png"
        inkscape(src, png, "--export-type=png", f"--export-width={w}",
                 "--export-background-opacity=0")
        made.append(f"PNG/{stem}_{w}px.png")

    if mode in JPG_BACKGROUNDS:
        label, hexv = JPG_BACKGROUNDS[mode]
        for w in PNG_WIDTHS:
            png = LOGO / "PNG" / f"{stem}_{w}px.png"
            jpg = LOGO / "JPG" / f"AV_{layout}_{mode}_on-{label}_{w}px.jpg"
            jpg.parent.mkdir(parents=True, exist_ok=True)
            run([IM, str(png), "-background", hexv, "-flatten",
                 "-quality", "92", str(jpg)])
            made.append(f"JPG/{jpg.name}")
    return made


def svgo_pass() -> None:
    if not shutil.which("svgo"):
        print("  svgo not found - skipping optimisation")
        return
    run(["svgo", "-f", str(LOGO / "SVG"), "--multipass",
         "--config", str(ROOT / "scripts/svgo.config.mjs")])


def contact_sheet() -> None:
    (ROOT / "review").mkdir(exist_ok=True)
    pngs = sorted(str(p) for p in (LOGO / "PNG").glob("*_1000px.png"))
    if not pngs:
        return
    run([*IM_MONTAGE, *pngs, "-tile", "6x", "-geometry", "300x300+10+10",
         "-background", "#888", str(ROOT / "review/contact_sheet.png")])


def counts() -> dict[str, int]:
    return {d.name: len(list(d.glob("*"))) for d in sorted(LOGO.iterdir()) if d.is_dir()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=[],
                    help="layout=NAME and/or mode=NAME (NAME may be 'all')")
    ap.add_argument("--skip-raster", action="store_true")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()

    sel = dict(kv.split("=", 1) for kv in args.only if "=" in kv)
    wanted_layouts = LY.LAYOUTS if sel.get("layout", "all") == "all" else [sel["layout"]]
    wanted_modes = list(L.MODES) if sel.get("mode", "all") == "all" else [sel["mode"]]

    LY.main()   # regenerate the layout sources first, so build.py is self-contained

    jobs = [(la, mo) for la in wanted_layouts for mo in wanted_modes]
    made: list[str] = []
    errors: list[str] = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(export_one, la, mo, args.skip_raster): (la, mo)
                for la, mo in jobs}
        for fut in cf.as_completed(futs):
            la, mo = futs[fut]
            try:
                made += fut.result()
            except Exception as exc:                     # noqa: BLE001
                errors.append(f"{la}/{mo}: {exc}")

    svgo_pass()
    if not args.skip_raster:
        contact_sheet()

    print(f"\nexported {len(made)} files from {len(jobs)} layout x mode combinations")
    for folder, n in counts().items():
        print(f"  01_Logo/{folder:<4} {n:>4} files")
    total = sum(counts().values())
    expected = len(LY.LAYOUTS) * len(L.MODES) * 5 + len(LY.LAYOUTS) * 2 * 2
    print(f"  {'total':<13} {total:>4} files (expected {expected}, "
          f"delta {total - expected:+d})")
    if errors:
        print("\nERRORS:")
        for e in errors:
            print("  " + e)
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Solve the type tracking analytically, rebuild the master, then diff it against
the reference and print the deltas that matter.

Run:  python3 scripts/fit_master.py          # solve, build, measure
      python3 scripts/fit_master.py --build  # build and measure only
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L  # noqa: E402

ROOT = L.ROOT
S = 1000.0 / 1254


def solve_all() -> dict:
    """Analytic tracking so each ink span lands on its measured target."""
    p = L.PARAMS
    out = {}
    out["wordmark"] = L.solve_wordmark_tracking()
    out["subline"] = L.solve_tracking(
        "IMMOBILIEN", L.FONT_TEXT, p["subline"]["size"],
        p["subline"]["right"] - p["subline"]["left"])
    # tagline: solve the word gap from the reference (~30.6) and then the tracking
    tg = p["tagline"]
    tg["word_gap"] = 30.6
    out["tagline"] = L.solve_tracking(
        tg["text"], L.FONT_TEXT, tg["size"], tg["right"] - tg["left"],
        weight="Light", word_gap=tg["word_gap"])
    return out


def apply(solved: dict) -> None:
    src = (ROOT / "scripts/avlogo.py").read_text()
    for key, val in solved.items():
        block = src.index(f'"{key}": {{')
        end = src.index("},", block)
        seg = src[block:end]
        import re
        seg2 = re.sub(r'"tracking": [-\d.]+', f'"tracking": {val}', seg)
        if key == "tagline" and '"word_gap"' not in seg2:
            seg2 = seg2.replace('"text":', f'"word_gap": {L.PARAMS["tagline"]["word_gap"]},\n        "text":')
        src = src[:block] + seg2 + src[end:]
    (ROOT / "scripts/avlogo.py").write_text(src)


def render(svg: pathlib.Path, png: pathlib.Path, width=1254) -> None:
    subprocess.run(
        ["inkscape", str(svg), "--export-type=png", f"--export-width={width}",
         "--export-background=#062014", "-o", str(png)],
        check=True, capture_output=True)


def measure(png: pathlib.Path) -> dict:
    import numpy as np
    from PIL import Image

    a = np.asarray(Image.open(png).convert("RGB")).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bg = np.array([6, 32, 20])
    ink = np.sqrt(((a - bg) ** 2).sum(axis=2)) > 42
    vb = lambda v: round(float(v) * S, 1)

    rows = ink.sum(axis=1)
    bands, st = [], None
    for y in range(a.shape[0]):
        if rows[y] > 2 and st is None:
            st = y
        elif rows[y] <= 2 and st is not None:
            if y - st > 4:
                bands.append((st, y - 1))
            st = None
    if st is not None:
        bands.append((st, a.shape[0] - 1))

    out = {"bands": []}
    for y0, y1 in bands:
        sub = ink[y0:y1 + 1, :]
        ys, xs = np.nonzero(sub)
        out["bands"].append({
            "y0": vb(y0), "y1": vb(y1),
            "x0": vb(xs.min()), "x1": vb(xs.max()),
            "w": vb(xs.max() - xs.min()), "h": vb(y1 - y0),
            "cx": vb((xs.min() + xs.max()) / 2),
        })
    cream = (r > 175) & (g > 165) & (b > 140) & ((r - b) < 62)
    gold = ink & (r > 120) & ((r - b) >= 62) & (g > 90)
    feath = ink & (g - r > 18) & (g > 50)
    for name, m in (("cream", cream), ("gold", gold), ("feather", feath)):
        mm = m[: int(590 / S), :]
        ys, xs = np.nonzero(mm)
        out[name] = ({"x0": vb(xs.min()), "x1": vb(xs.max()),
                      "y0": vb(ys.min()), "y1": vb(ys.max())}
                     if len(xs) else None)
    return out


LABELS = ["monogram", "wordmark", "subline", "tagline"]


def report(ref: dict, got: dict) -> int:
    print(f"{'feature':<22}{'reference':>22}{'master':>22}{'delta':>18}")
    print("-" * 84)
    bad = 0
    for i, lab in enumerate(LABELS):
        if i >= len(ref["bands"]) or i >= len(got["bands"]):
            print(f"{lab:<22}{'MISSING BAND':>22}")
            bad += 1
            continue
        a, b = ref["bands"][i], got["bands"][i]
        for k in ("x0", "x1", "y0", "y1"):
            d = round(b[k] - a[k], 1)
            flag = "" if abs(d) <= 4.0 else "   <-- off"
            if abs(d) > 4.0:
                bad += 1
            print(f"{lab + '.' + k:<22}{a[k]:>22}{b[k]:>22}{d:>18}{flag}")
    for name in ("cream", "gold", "feather"):
        a, b = ref.get(name), got.get(name)
        if not a or not b:
            continue
        for k in ("x0", "x1", "y0", "y1"):
            d = round(b[k] - a[k], 1)
            flag = "" if abs(d) <= 8.0 else "   <-- off"
            if abs(d) > 8.0:
                bad += 1
            print(f"{name + '.' + k:<22}{a[k]:>22}{b[k]:>22}{d:>18}{flag}")
    return bad


def main() -> None:
    if "--build" not in sys.argv:
        solved = solve_all()
        print("solved tracking:", json.dumps(solved))
        apply(solved)
        import importlib
        importlib.reload(L)

    (ROOT / "AV-Brand-Kit/00_Master/AV_master.svg").write_text(L.master_svg("full-dark"))
    render(ROOT / "AV-Brand-Kit/00_Master/AV_master.svg", ROOT / "review/master.png")

    ref = measure(ROOT / "ref/logo_AV.png")
    got = measure(ROOT / "review/master.png")
    (ROOT / "review/fit.json").write_text(json.dumps({"ref": ref, "master": got}, indent=2))
    n = report(ref, got)
    print(f"\n{n} measurements outside tolerance")

    for cmd in (
        ["convert", "ref/logo_AV.png", "review/master.png", "+append", "review/compare.png"],
        ["convert", "ref/logo_AV.png", "review/master.png", "-compose", "blend",
         "-define", "compose:args=50", "-composite", "review/overlay.png"],
    ):
        subprocess.run(cmd, cwd=ROOT, check=True)
    print("wrote review/compare.png and review/overlay.png")


if __name__ == "__main__":
    main()

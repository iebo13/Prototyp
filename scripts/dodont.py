#!/usr/bin/env python3
"""Generate the eight do/don't pairs for the brand guide.

Every image is produced from the real exported logo files — nothing is mocked up by
hand, so the guide always shows what the current artwork actually does.
Output: review/dodont/{n}_{do|dont}.png
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L  # noqa: E402

ROOT = L.ROOT
KIT = ROOT / "AV-Brand-Kit"
PNG = KIT / "01_Logo/PNG"
OUT = ROOT / "review/dodont"
IM = "magick" if shutil.which("magick") else "convert"

GREEN, CREAM, GOLD, WHITE = L.C["green"], L.C["cream"], L.C["gold"], L.C["white"]
W, H = 760, 460


def run(cmd: list[str]) -> None:
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(str(c) for c in cmd[:6])}...\n{r.stderr[-600:]}")


def plate(fg_cmds: list[str], out: pathlib.Path, bg: str = GREEN) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    run([IM, "-size", f"{W}x{H}", f"xc:{bg}", *fg_cmds, str(out)])


def logo(stem: str) -> str:
    return str(PNG / f"{stem}_3000px.png")


CASES = []


def case(n: int, title: str, why: str):
    def deco(fn):
        CASES.append((n, title, why, fn))
        return fn
    return deco


@case(1, "Do not stretch or squash", "Scale the logo proportionally, always.")
def c1():
    plate([logo("AV_stacked_full-dark"), "-resize", "440x260!",
           "-gravity", "center", "-composite"], OUT / "1_dont.png")
    plate([logo("AV_stacked_full-dark"), "-resize", "340x",
           "-gravity", "center", "-composite"], OUT / "1_do.png")


@case(2, "Do not recolour", "Use one of the six supplied colour modes.")
def c2():
    plate([logo("AV_stacked_1c-cream"), "-resize", "340x",
           "-fill", "#7B2FBE", "-colorize", "85",
           "-gravity", "center", "-composite"], OUT / "2_dont.png")
    plate([logo("AV_stacked_full-dark"), "-resize", "340x",
           "-gravity", "center", "-composite"], OUT / "2_do.png")


@case(3, "Do not add effects", "No drop shadow, glow, bevel or gradient.")
def c3():
    tmp = ROOT / "assets/_dd3.png"
    sh = ROOT / "assets/_dd3s.png"
    run([IM, logo("AV_stacked_full-dark"), "-resize", "340x", str(tmp)])
    # a black silhouette of the mark, blurred, as the shadow
    run([IM, str(tmp), "-alpha", "extract", "-blur", "0x7", str(sh)])
    run([IM, "-size", f"{W}x{H}", f"xc:{GREEN}",
         "(", str(sh), "-background", "black", "-alpha", "shape", ")",
         "-gravity", "center", "-geometry", "+9+13", "-composite",
         str(tmp), "-gravity", "center", "-geometry", "+0+0", "-composite",
         str(OUT / "3_dont.png")])
    run([IM, "-size", f"{W}x{H}", f"xc:{GREEN}", str(tmp),
         "-gravity", "center", "-composite", str(OUT / "3_do.png")])
    tmp.unlink(missing_ok=True)
    sh.unlink(missing_ok=True)


@case(4, "Keep the contrast", "Cream on green, green on cream. Never cream on gold.")
def c4():
    plate([logo("AV_stacked_1c-cream"), "-resize", "340x",
           "-gravity", "center", "-composite"], OUT / "4_dont.png", bg=GOLD)
    plate([logo("AV_stacked_full-light"), "-resize", "340x",
           "-gravity", "center", "-composite"], OUT / "4_do.png", bg=CREAM)


@case(5, "Do not rotate", "The logo sits level. No angles, no arcs.")
def c5():
    plate([logo("AV_stacked_full-dark"), "-resize", "340x",
           "-background", "none", "-rotate", "-14",
           "-gravity", "center", "-composite"], OUT / "5_dont.png")
    plate([logo("AV_stacked_full-dark"), "-resize", "340x",
           "-gravity", "center", "-composite"], OUT / "5_do.png")


@case(6, "Do not outline", "The mark is solid. Never hollow it out into a keyline.")
def c6():
    tmp = ROOT / "assets/_dd6.png"
    edge = ROOT / "assets/_dd6e.png"
    run([IM, logo("AV_stacked_1c-cream"), "-resize", "340x", str(tmp)])
    # outline = the alpha's edge, painted cream, so the mark reads hollow
    run([IM, str(tmp), "-alpha", "extract", "-morphology", "EdgeOut", "Diamond:2",
         "-background", CREAM, "-alpha", "shape", str(edge)])
    run([IM, "-size", f"{W}x{H}", f"xc:{GREEN}", str(edge),
         "-gravity", "center", "-composite", str(OUT / "6_dont.png")])
    run([IM, "-size", f"{W}x{H}", f"xc:{GREEN}", logo("AV_stacked_full-dark"),
         "-resize", "340x", "-gravity", "center", "-composite",
         str(OUT / "6_do.png")])
    tmp.unlink(missing_ok=True)
    edge.unlink(missing_ok=True)


@case(7, "Do not sit the logo on a busy area",
      "Place it on a calm field, or use the green panel.")
def c7():
    busy = ROOT / "assets/_dd_busy.png"
    run([IM, "-size", f"{W}x{H}", f"xc:{GREEN}",
         "-seed", "9", "+noise", "Random", "-blur", "0x2",
         "-modulate", "100,60,100", str(busy)])
    run([IM, str(busy), logo("AV_stacked_1c-cream"), "-resize", "340x",
         "-gravity", "center", "-composite", str(OUT / "7_dont.png")])
    run([IM, str(busy), "-fill", GREEN, "-colorize", "72",
         logo("AV_stacked_full-dark"), "-resize", "340x",
         "-gravity", "center", "-composite", str(OUT / "7_do.png")])
    busy.unlink(missing_ok=True)


@case(8, "Respect the minimum size",
      "Below 150 px wide, drop the tagline; below 64 px use the simple monogram.")
def c8():
    small = ROOT / "assets/_dd_small.png"
    run([IM, logo("AV_stacked_tagline_full-dark"), "-resize", "96x", str(small)])
    run([IM, "-size", f"{W}x{H}", f"xc:{GREEN}", str(small),
         "-gravity", "center", "-composite", str(OUT / "8_dont.png")])
    run([IM, logo("AV_monogram_simple_1c-cream"), "-resize", "96x", str(small)])
    run([IM, "-size", f"{W}x{H}", f"xc:{GREEN}", str(small),
         "-gravity", "center", "-composite", str(OUT / "8_do.png")])
    small.unlink(missing_ok=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for n, title, why, fn in CASES:
        fn()
        print(f"  {n}. {title}")
    print(f"\n{len(CASES) * 2} images in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

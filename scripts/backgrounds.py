#!/usr/bin/env python3
"""Procedural backgrounds standing in for the Nano Banana / GPT Image generations.

No GEMINI_API_KEY or OPENAI_API_KEY was available, so prompts P2-P5 could not run.
Rather than ship nothing, each background is built here from brand tokens and the
real mountain ridge path: deep green ground, a fine paper grain, and a gold hairline
mountain silhouette placed as the prompt describes.

These are deliberately calm and abstract. They are marked PLACEHOLDER in
AV-Brand-Kit/README.md; drop a generated image into assets/inbox/ to replace one.
"""
from __future__ import annotations

import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L  # noqa: E402

ROOT = L.ROOT
OUT = ROOT / "assets/backgrounds"


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _ridge_points(w: float, h: float, baseline: float, amp: float,
                  x0: float, x1: float) -> list[tuple[float, float]]:
    """The brand mountain ridge, rescaled into a box."""
    pts = L.PARAMS["ridge"]
    rx0 = min(p[0] for p in pts)
    rx1 = max(p[0] for p in pts)
    ry0 = min(p[1] for p in pts)
    ry1 = max(p[1] for p in pts)
    out = []
    for px, py in pts:
        u = (px - rx0) / (rx1 - rx0)
        v = (py - ry0) / (ry1 - ry0)
        out.append((x0 + u * (x1 - x0), baseline - amp * (1.0 - v)))
    return out


def make(name: str, w: int, h: int, *, ridge: str = "corner",
         grain: float = 5.0, seed: int = 7) -> pathlib.Path:
    """ridge: 'corner' (bottom-right), 'bottom' (full width), 'none'."""
    from PIL import Image, ImageDraw, ImageFilter

    base = _hex(L.C["green"])
    img = Image.new("RGB", (w, h), base)

    # --- paper grain: low-amplitude noise, blurred so it reads as texture not dither
    rnd = random.Random(seed)
    noise = Image.new("L", (w // 2, h // 2))
    noise.putdata([rnd.gauss(128, 34) for _ in range((w // 2) * (h // 2))])
    noise = noise.filter(ImageFilter.GaussianBlur(0.6)).resize((w, h), Image.BILINEAR)
    px = img.load()
    npx = noise.load()
    for y in range(h):
        for x in range(w):
            d = (npx[x, y] - 128) / 128.0 * grain
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, int(r + d))),
                        max(0, min(255, int(g + d))),
                        max(0, min(255, int(b + d))))

    # --- a very soft vignette lift towards the centre, so the ground is not flat
    glow = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-w * 0.25, -h * 0.35, w * 1.25, h * 1.35], fill=26)
    glow = glow.filter(ImageFilter.GaussianBlur(min(w, h) * 0.12))
    img = Image.composite(Image.new("RGB", (w, h), tuple(min(255, c + 14) for c in base)),
                          img, glow)

    # --- gold hairline mountains
    if ridge != "none":
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        gold = _hex(L.C["gold"])
        if ridge == "corner":
            pts = _ridge_points(w, h, baseline=h * 0.995, amp=h * 0.30,
                                x0=w * 0.50, x1=w * 1.02)
            width = max(2, round(min(w, h) * 0.0032))
            alpha = 58
        else:  # 'bottom'
            pts = _ridge_points(w, h, baseline=h * 0.995, amp=h * 0.17,
                                x0=-w * 0.04, x1=w * 1.04)
            width = max(2, round(min(w, h) * 0.0026))
            alpha = 52
        d.line(pts, fill=(*gold, alpha), width=width, joint="curve")
        # a second, fainter ridge behind, for depth
        back = [(x - w * 0.10, y - (pts[0][1] - min(p[1] for p in pts)) * 0.22)
                for x, y in pts]
        d.line(back, fill=(*gold, max(18, alpha // 2)), width=max(1, width - 1),
               joint="curve")
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.png"
    img.save(p, optimize=True)
    print(f"  {p.relative_to(ROOT)}  {w}x{h}")
    return p


def main() -> None:
    print("procedural backgrounds (PLACEHOLDER for prompts P2-P5):")
    make("bg_square_2048", 2048, 2048, ridge="corner", seed=11)      # P2 1:1
    make("bg_wide_2048x1152", 2048, 1152, ridge="corner", seed=23)   # P2 16:9
    make("bg_story_1080x1920", 1080, 1920, ridge="bottom", seed=31)  # P3 9:16
    make("bg_hero_2400x1000", 2400, 1000, ridge="corner", seed=47)   # P4 21:9
    make("bg_expose_1800x2400", 1800, 2400, ridge="bottom", seed=59) # P5 3:4


if __name__ == "__main__":
    main()

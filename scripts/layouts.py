#!/usr/bin/env python3
"""Generate the seven layout SVGs in 00_Master/layouts/, one file per layout x mode.

Clear space is baked into each viewBox: X on all four sides, where X is the cap
height of the wordmark's "A" (SKILL §4). Backgrounds are never part of the vector —
they are added only for the JPG exports and the mockups.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L  # noqa: E402

ROOT = L.ROOT
OUT = ROOT / "AV-Brand-Kit/00_Master/layouts"

# X = cap height of the wordmark A, the clear-space unit
X = round(L.PARAMS["wordmark"]["size_cap"] * 0.714, 2)   # 63.0

LAYOUTS = ["stacked", "stacked_tagline", "horizontal", "horizontal_tagline",
           "monogram", "monogram_simple", "wordmark"]

# Minimum sizes, quoted in the brand guide and the README.
MIN_SIZE = {
    "stacked": ("25 mm", "120 px"),
    "stacked_tagline": ("30 mm", "150 px"),
    "horizontal": ("40 mm", "180 px"),
    "horizontal_tagline": ("45 mm", "200 px"),
    "monogram": ("8 mm", "32 px"),
    "monogram_simple": ("8 mm", "32 px"),
    "wordmark": ("30 mm", "140 px"),
}


def _bbox_of(parts: list[str]) -> tuple[float, float, float, float]:
    """Design-space bbox of the components named in `parts`, from PARAMS."""
    p = L.PARAMS
    xs, ys = [], []
    if "monogram" in parts:
        xs += [273.5, 728.9]
        ys += [197.8, 572.6]
    if "wordmark" in parts:
        xs += [p["wordmark"]["left"], p["wordmark"]["right"]]
        ys += [p["wordmark"]["baseline"] - X, p["wordmark"]["baseline"] + 1.0]
    if "subline" in parts:
        xs += [p["subline"]["rule_left"][0], p["subline"]["rule_right"][1]]
        ys += [p["subline"]["baseline"] - 27.9, p["subline"]["baseline"]]
    if "tagline" in parts:
        xs += [p["tagline"]["left"], p["tagline"]["right"]]
        ys += [p["tagline"]["baseline"] - 16.0, p["tagline"]["baseline"]]
    return min(xs), min(ys), max(xs), max(ys)


def _group(name: str, body: str) -> str:
    return f'  <g id="{name}">\n{body}\n  </g>'


def _components(parts: list[str], mode: str, simple: bool = False) -> str:
    out = []
    if "monogram" in parts:
        out.append(_group("monogram", L.monogram_letters()))
        out.append(_group("mountains", L.mountains()))
        out.append(L.feather(mode if not simple else "1c-cream")
                   if not simple else _simple_feather(mode))
    if "wordmark" in parts:
        out.append(_group("wordmark", L.wordmark()))
    if "subline" in parts:
        out.append(_group("subline", L.subline()))
    if "tagline" in parts:
        out.append(_group("tagline", L.tagline()))
    return "\n".join(out)


def _simple_feather(mode: str) -> str:
    """monogram_simple always uses the 1-colour silhouette, tinted like the letters."""
    body = L._inner_svg(ROOT / "assets/feather_1c.svg")
    body = body.replace('fill="currentColor"', 'class="c-letter"')
    body = body.replace('stroke="currentColor"', 'class="c-letter-s"')
    return (f'  <g id="feather" transform="{L._feather_transform("feather_simple")}">\n'
            f'{body}\n  </g>')


def build(layout: str, mode: str) -> str:
    """One layout in one colour mode, clear space baked into the viewBox."""
    if layout in ("stacked", "stacked_tagline"):
        parts = ["monogram", "wordmark", "subline"]
        if layout == "stacked_tagline":
            parts.append("tagline")
        x0, y0, x1, y1 = _bbox_of(parts)
        body = _components(parts, mode)
        tx, ty = 0.0, 0.0

    elif layout in ("monogram", "monogram_simple"):
        parts = ["monogram"]
        x0, y0, x1, y1 = _bbox_of(parts)
        body = _components(parts, mode, simple=(layout == "monogram_simple"))
        tx, ty = 0.0, 0.0

    elif layout == "wordmark":
        parts = ["wordmark", "subline"]
        x0, y0, x1, y1 = _bbox_of(parts)
        body = _components(parts, mode)
        tx, ty = 0.0, 0.0

    else:  # horizontal / horizontal_tagline
        return _horizontal(layout, mode)

    vx, vy = x0 - X, y0 - X
    vw, vh = (x1 - x0) + 2 * X, (y1 - y0) + 2 * X
    return _wrap(layout, mode, vx, vy, vw, vh, body, tx, ty)


def _horizontal(layout: str, mode: str) -> str:
    """Monogram left at height 1, gap 0.35, right block (wordmark over subline
    [over tagline]) vertically centred on the monogram."""
    mx0, my0, mx1, my1 = 273.5, 197.8, 728.9, 572.6
    mh = my1 - my0
    gap = 0.35 * mh

    parts = ["wordmark", "subline"]
    if layout == "horizontal_tagline":
        parts.append("tagline")
    tx0, ty0, tx1, ty1 = _bbox_of(parts)
    th = ty1 - ty0

    # place the text block to the right of the monogram, vertically centred
    dx = (mx1 + gap) - tx0
    dy = (my0 + mh / 2 - th / 2) - ty0

    mono = "\n".join([
        _group("monogram", L.monogram_letters()),
        _group("mountains", L.mountains()),
        L.feather(mode),
    ])
    text = _components(parts, mode)
    body = (f'{mono}\n  <g id="lockup-text" transform="translate({L.f(dx)} {L.f(dy)})">\n'
            f'{text}\n  </g>')

    x0, y0 = mx0, min(my0, ty0 + dy)
    x1, y1 = tx1 + dx, max(my1, ty1 + dy)
    vx, vy = x0 - X, y0 - X
    vw, vh = (x1 - x0) + 2 * X, (y1 - y0) + 2 * X
    return _wrap(layout, mode, vx, vy, vw, vh, body, 0.0, 0.0)


def _wrap(layout: str, mode: str, vx, vy, vw, vh, body, tx, ty) -> str:
    inner = body if (tx, ty) == (0.0, 0.0) else (
        f'  <g transform="translate({L.f(tx)} {L.f(ty)})">\n{body}\n  </g>')
    mm, px = MIN_SIZE[layout]
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{L.f(vx)} {L.f(vy)} {L.f(vw)} {L.f(vh)}" '
        f'width="{L.f(vw)}" height="{L.f(vh)}" id="AV_{layout}_{mode}">',
        f"  <title>Auguste Viktoria Immobilien — {layout}, {mode}</title>",
        f"  <desc>Clear space {L.f(X)} units (cap height of the wordmark A) on all "
        f"four sides, baked into the viewBox. Minimum size {mm} / {px}. "
        f"Transparent by design — never add a background to this file.</desc>",
        L.style_block(mode),
        inner,
        "</svg>",
    ]) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for layout in LAYOUTS:
        for mode in L.MODES:
            (OUT / f"AV_{layout}_{mode}.svg").write_text(build(layout, mode))
            n += 1
    print(f"wrote {n} layout SVGs to {OUT.relative_to(ROOT)}")
    print(f"clear space X = {X} viewBox units")


if __name__ == "__main__":
    main()

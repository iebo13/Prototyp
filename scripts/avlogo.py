#!/usr/bin/env python3
"""Component library for the Auguste Viktoria Immobilien mark.

Every geometry number in PARAMS was derived by measuring ref/logo_AV.png
(see scripts/measure_ref.py and review/ref_measurements.json), then refined against
review/overlay.png. Coordinates are viewBox units on a 0 0 1000 1000 canvas.

Colour is never hard-coded here. Each element carries one of the classes
.c-green .c-cream .c-gold .c-peacock .c-teal and the colour mode supplies the rules,
so one geometry serves all six modes (SKILL §5).
"""
from __future__ import annotations

import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "AV-Brand-Kit/00_Master/tokens.json").read_text())
C = {k: v["hex"] for k, v in TOKENS["colors"].items()}

FONT_DISPLAY = "Cinzel"
FONT_TEXT = "Montserrat"

# --------------------------------------------------------------------------- params
PARAMS = {
    # --- monogram letters (Cinzel, cap height 0.700 em, A drawn height 0.714 em)
    # Cinzel A anchored on the measured apex (411.9, 264.8) and baseline 514.4.
    # The reference A is 8.6 % wider than stock Cinzel, applied about the apex so
    # both the apex and the left foot land on their measured positions.
    "A": {"size": 349.58, "x": 287.97, "baseline": 514.4,
          "apex_x": 411.9, "x_scale": 1.0863},
    # Cinzel V anchored on the measured vertex (483.6, 563.0). The reference V is
    # wider than stock Cinzel — its right arm runs out towards the mountain tail —
    # so a horizontal scale is applied about the vertex, which leaves the point put.
    "V": {"size": 370.0, "x": 346.1, "baseline": 557.8,
          "vertex_x": 483.6, "x_scale": 1.12},

    "ridge": [
        (441.0, 285.0), (452.0, 272.0), (466.5, 256.8), (476.1, 248.8),
        (485.6, 253.6), (504.8, 232.9), (523.9, 212.1), (533.5, 201.8),
        (543.1, 208.1), (562.2, 223.3), (581.3, 239.2), (590.9, 247.2),
        (600.5, 245.6), (619.6, 261.6), (629.2, 267.1), (638.8, 263.2),
        (648.3, 266.3), (667.5, 281.5), (686.6, 295.9), (705.7, 305.4),
        (724.9, 307.8),
    ],
    "ridge_width": 8.5,
    # short interior strokes: the snow-line notches visible on the main peak
    # the lightning-bolt notch down the right flank, as in the reference
    "ridge_detail": [
        [(562.0, 223.0), (574.0, 240.0), (559.0, 243.0),
         (573.0, 262.0), (558.0, 265.0), (570.0, 284.0), (556.0, 288.0)],
    ],
    "ridge_detail_width": 4.2,

    # --- feather placement: quill on the V's right stroke, eye up and to the right
    "feather": {"quill": (494.0, 572.0), "tip": (678.0, 306.0), "extra_rot": 0.0},
    # In 1-colour modes the feather and the V are the same colour, so the silhouette
    # is nudged clear of the V's right stroke instead of sitting on it.
    "feather_simple": {"quill": (528.0, 566.0), "tip": (700.0, 318.0), "extra_rot": 0.0},

    # --- wordmark AUGUSTE VIKTORIA (Cinzel, large initials + small caps)
    "wordmark": {
        "size_cap": 88.24,     # A and V
        "size_small": 70.30,   # the remaining letters
        "baseline": 656.3,
        "left": 98.1,
        "right": 911.5,
        "tracking": 5.2123,       # refined by fit_master.py
        "word_gap": 34.3,
    },

    # --- IMMOBILIEN + gold hairline rules
    "subline": {
        "size": 38.7,          # Montserrat cap height 0.700 em -> 27.1 units
        "baseline": 724.1,
        "left": 281.5,
        "right": 716.9,
        "tracking": 21.4942,      # refined by fit_master.py
        "rule_y": 709.7,
        "rule_w": 3.2,
        "rule_left": (133.2, 240.8),
        "rule_right": (756.8, 865.2),
    },

    # --- tagline
    "tagline": {
        "size": 22.7,          # cap height 15.9 units
        "baseline": 791.9,
        "left": 232.9,
        "right": 765.6,
        "tracking": 4.8792,       # refined by fit_master.py
        "word_gap": 30.6,
        "text": "MEHR ALS NUR EIN ZUHAUSE",
    },
}

MODES = {
    # mode           letters/wordmark  mountains/rules/tagline  feather
    "full-dark":  {"letters": "cream", "accent": "gold",  "feather": "full"},
    "full-light": {"letters": "green", "accent": "gold",  "feather": "full"},
    "1c-cream":   {"letters": "cream", "accent": "cream", "feather": "cream"},
    "1c-white":   {"letters": "white", "accent": "white", "feather": "white"},
    "1c-black":   {"letters": "black", "accent": "black", "feather": "black"},
    "1c-gold":    {"letters": "gold",  "accent": "gold",  "feather": "gold"},
}


# ------------------------------------------------------------------- font metrics
_METRIC_CACHE: dict[tuple[str, str], dict] = {}


def font_path(family: str, weight: str = "Regular") -> str:
    if family == "Cinzel":
        return str(ROOT / "AV-Brand-Kit/07_Fonts/Cinzel-Variable.ttf")
    return f"/usr/share/fonts/truetype/montserrat/Montserrat-{weight}.ttf"


def metrics(family: str, weight: str = "Regular") -> dict:
    """Advance widths and bboxes in em units, plus capHeight."""
    key = (family, weight)
    if key in _METRIC_CACHE:
        return _METRIC_CACHE[key]
    from fontTools.ttLib import TTFont
    from fontTools.pens.boundsPen import BoundsPen

    f = TTFont(font_path(family, weight))
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    adv, bbox = {}, {}
    for cp, gn in cmap.items():
        try:
            ch = chr(cp)
        except ValueError:
            continue
        adv[ch] = hmtx[gn][0] / upm
        bp = BoundsPen(gs)
        gs[gn].draw(bp)
        if bp.bounds:
            x0, y0, x1, y1 = bp.bounds
            bbox[ch] = (x0 / upm, y0 / upm, x1 / upm, y1 / upm)
    out = {
        "adv": adv,
        "bbox": bbox,
        "cap": (getattr(f["OS/2"], "sCapHeight", None) or 700) / upm,
    }
    _METRIC_CACHE[key] = out
    return out


# ------------------------------------------------------------------ svg fragments
def f(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def poly_d(pts, close=False) -> str:
    d = f"M {f(pts[0][0])} {f(pts[0][1])}" + "".join(
        f" L {f(x)} {f(y)}" for x, y in pts[1:])
    return d + (" Z" if close else "")


def monogram_letters() -> str:
    """Cinzel A and V, each horizontally scaled about its own anchor so the apex,
    the left foot and the V's vertex all land on their measured positions."""
    a, v = PARAMS["A"], PARAMS["V"]

    def scaled(letter: str, p: dict, anchor: float) -> str:
        return (
            f'    <g transform="translate({f(anchor)} 0) scale({p["x_scale"]} 1) '
            f'translate({f(-anchor)} 0)">\n'
            f'      <text class="c-letter" x="{f(p["x"])}" y="{f(p["baseline"])}" '
            f'font-family="{FONT_DISPLAY}" font-size="{f(p["size"])}">{letter}</text>\n'
            f'    </g>')

    return scaled("A", a, a["apex_x"]) + "\n" + scaled("V", v, v["vertex_x"])


def mountains() -> str:
    out = [f'    <path class="c-accent-s" fill="none" '
           f'stroke-width="{f(PARAMS["ridge_width"])}" stroke-linejoin="round" '
           f'stroke-linecap="round" d="{poly_d(PARAMS["ridge"])}"/>']
    for seg in PARAMS["ridge_detail"]:
        out.append(f'    <path class="c-accent-s" fill="none" '
                   f'stroke-width="{f(PARAMS["ridge_detail_width"])}" '
                   f'stroke-linejoin="round" stroke-linecap="round" '
                   f'd="{poly_d(seg)}"/>')
    return "\n".join(out)


def _feather_transform(key: str = "feather") -> str:
    """Map the feather's local quill->tip axis onto the placement in PARAMS."""
    import build_feather as bf  # local coords live with the generator

    lq, lt = bf.P0, bf.P3
    tq = PARAMS[key]["quill"]
    tt = PARAMS[key]["tip"]
    lvec = (lt[0] - lq[0], lt[1] - lq[1])
    tvec = (tt[0] - tq[0], tt[1] - tq[1])
    scale = math.hypot(*tvec) / math.hypot(*lvec)
    rot = (math.degrees(math.atan2(tvec[1], tvec[0]))
           - math.degrees(math.atan2(lvec[1], lvec[0]))
           + PARAMS[key]["extra_rot"])
    return (f'translate({f(tq[0])} {f(tq[1])}) rotate({rot:.2f}) '
            f'scale({scale:.5f}) translate({f(-lq[0])} {f(-lq[1])})')


def _inner_svg(path: pathlib.Path) -> str:
    """Body of an SVG file, without its root element, style block or title."""
    s = path.read_text()
    s = re.sub(r"<\?xml.*?\?>", "", s, flags=re.S)
    s = re.sub(r"^.*?<svg[^>]*>", "", s, flags=re.S)
    s = re.sub(r"</svg>\s*$", "", s, flags=re.S)
    s = re.sub(r"<title>.*?</title>", "", s, flags=re.S)
    s = re.sub(r"<style>.*?</style>", "", s, flags=re.S)
    return s.strip()


def feather(mode: str) -> str:
    """In 1-colour modes the feather and the letters share a colour, so the
    silhouette is placed clear of the V's right stroke rather than across it."""
    one_colour = MODES[mode]["feather"] != "full"
    src = ROOT / ("assets/feather_1c.svg" if one_colour else "assets/feather.svg")
    body = _inner_svg(src)
    if one_colour:
        body = body.replace('fill="currentColor"', 'class="c-letter"')
        body = body.replace('stroke="currentColor"', 'class="c-letter-s"')
    key = "feather_simple" if one_colour else "feather"
    return (f'    <g id="feather" transform="{_feather_transform(key)}">\n'
            f'{body}\n    </g>')


def glyph_positions(text: str, family: str, size: float, tracking: float,
                    left: float, weight: str = "Regular",
                    word_gap: float | None = None) -> tuple[list[str], list[float], float]:
    """Explicit x for every glyph, so the rendered layout is exactly what we compute
    and does not depend on how a renderer interprets letter-spacing.

    Returns (chars, xs, right_ink_edge).
    """
    m = metrics(family, weight)
    adv, bbox = m["adv"], m["bbox"]
    chars = [c for c in text if c != " "]
    x = left - bbox[chars[0]][0] * size
    xs, right = [], 0.0
    prev = None
    for ch in text:
        if ch == " ":
            gap = word_gap if word_gap is not None else adv.get(" ", 0.26) * size + tracking
            rsb = (adv[prev] - bbox[prev][2]) * size
            x += rsb + gap
            prev = " "
            continue
        if prev == " ":
            x -= bbox[ch][0] * size          # gap was measured ink-edge to ink-edge
        xs.append(x)
        right = x + bbox[ch][2] * size
        x += adv[ch] * size + tracking
        prev = ch
    return chars, xs, right


def ink_span(text: str, family: str, size: float, tracking: float,
             weight: str = "Regular", word_gap: float | None = None) -> float:
    _, _, right = glyph_positions(text, family, size, tracking, 0.0, weight, word_gap)
    return right


def solve_tracking(text: str, family: str, size: float, target: float,
                   weight: str = "Regular", word_gap: float | None = None) -> float:
    """Bisect the letter-spacing whose ink width equals target."""
    lo, hi = -0.5 * size, 2.0 * size
    for _ in range(90):
        mid = (lo + hi) / 2
        if ink_span(text, family, size, mid, weight, word_gap) < target:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 4)


def _text_run(text: str, family: str, size: float, tracking: float, baseline: float,
              left: float, cls: str, weight: str | None = None,
              word_gap: float | None = None) -> str:
    w = weight or "Regular"
    chars, xs, _ = glyph_positions(text, family, size, tracking, left, w, word_gap)
    fw = {"Light": "300", "Regular": "400"}.get(w, "400")
    xlist = " ".join(f(v) for v in xs)
    return (f'    <text class="{cls}" x="{xlist}" y="{f(baseline)}" '
            f'font-family="{family}" font-weight="{fw}" font-size="{f(size)}" '
            f'xml:space="preserve">{"".join(chars)}</text>')


def wordmark_layout(tracking: float) -> tuple[list[tuple[str, float, float]], float]:
    """(char, x, size) for every glyph of AUGUSTE VIKTORIA, plus the right ink edge.

    Large initials at size_cap, the remaining letters at small-cap height, all on one
    baseline — the small-caps look of the reference.
    """
    p = PARAMS["wordmark"]
    m = metrics(FONT_DISPLAY)
    adv, bbox = m["adv"], m["bbox"]
    out = []
    x = p["left"] - bbox["A"][0] * p["size_cap"]
    right = 0.0
    for wi, word in enumerate(("AUGUSTE", "VIKTORIA")):
        for ci, ch in enumerate(word):
            size = p["size_cap"] if ci == 0 else p["size_small"]
            if wi == 1 and ci == 0:
                x -= bbox[ch][0] * size
            out.append((ch, x, size))
            right = x + bbox[ch][2] * size
            x += adv[ch] * size + tracking
        if wi == 0:
            last = word[-1]
            rsb = (adv[last] - bbox[last][2]) * p["size_small"]
            x += -tracking + rsb + p["word_gap"]
    return out, right


def solve_wordmark_tracking() -> float:
    p = PARAMS["wordmark"]
    target = p["right"]
    lo, hi = -10.0, 60.0
    for _ in range(90):
        mid = (lo + hi) / 2
        if wordmark_layout(mid)[1] < target:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 4)


def wordmark() -> str:
    p = PARAMS["wordmark"]
    glyphs, _ = wordmark_layout(p["tracking"])
    big = [(c, x) for c, x, s in glyphs if s == p["size_cap"]]
    small = [(c, x) for c, x, s in glyphs if s != p["size_cap"]]
    out = []
    for items, size in ((big, p["size_cap"]), (small, p["size_small"])):
        xs = " ".join(f(x) for _, x in items)
        txt = "".join(c for c, _ in items)
        out.append(f'    <text class="c-letter" x="{xs}" y="{f(p["baseline"])}" '
                   f'font-family="{FONT_DISPLAY}" font-size="{f(size)}" '
                   f'xml:space="preserve">{txt}</text>')
    return "\n".join(out)


def subline() -> str:
    p = PARAMS["subline"]
    lx0, lx1 = p["rule_left"]
    rx0, rx1 = p["rule_right"]
    hw = p["rule_w"] / 2
    return "\n".join([
        _text_run("IMMOBILIEN", FONT_TEXT, p["size"], p["tracking"],
                  p["baseline"], p["left"], "c-accent-t"),
        f'    <rect class="c-accent" x="{f(lx0)}" y="{f(p["rule_y"] - hw)}" '
        f'width="{f(lx1 - lx0)}" height="{f(p["rule_w"])}"/>',
        f'    <rect class="c-accent" x="{f(rx0)}" y="{f(p["rule_y"] - hw)}" '
        f'width="{f(rx1 - rx0)}" height="{f(p["rule_w"])}"/>',
    ])


def tagline() -> str:
    p = PARAMS["tagline"]
    return _text_run(p["text"], FONT_TEXT, p["size"], p["tracking"], p["baseline"],
                     p["left"], "c-accent-t", weight="Light",
                     word_gap=p.get("word_gap"))


def style_block(mode: str) -> str:
    m = MODES[mode]
    letters, accent = C[m["letters"]], C[m["accent"]]
    css = [
        f".c-letter{{fill:{letters};stroke:none}}",
        f".c-letter-s{{stroke:{letters};fill:none}}",
        f".c-accent{{fill:{accent};stroke:none}}",
        f".c-accent-t{{fill:{accent};stroke:none}}",
        f".c-accent-s{{stroke:{accent};fill:none}}",
    ]
    if m["feather"] == "full":
        css += [
            f".f-body{{fill:{C['peacock']}}}",
            f".f-barb{{stroke:{C['peacock']};fill:none;stroke-linecap:round}}",
            f".f-barb-hi{{stroke:{C['teal']};fill:none;stroke-linecap:round}}",
            f".f-spine{{stroke:{C['gold']};fill:none;stroke-linecap:round}}",
            f".f-dark{{fill:{C['green']}}}",
            f".f-gold{{fill:{C['gold']}}}",
            f".f-teal{{fill:{C['teal']}}}",
        ]
    return "  <style>\n    " + "\n    ".join(css) + "\n  </style>"


def master_svg(mode: str = "full-dark") -> str:
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        'width="1000" height="1000" id="AV_master">',
        "  <title>Auguste Viktoria Immobilien — master logo</title>",
        "  <desc>Live-font master. Never ship this file; export from "
        "00_Master/layouts/ with text converted to paths.</desc>",
        style_block(mode),
        '  <g id="monogram">',
        monogram_letters(),
        "  </g>",
        '  <g id="mountains">',
        mountains(),
        "  </g>",
        feather(mode),
        '  <g id="wordmark">',
        wordmark(),
        "  </g>",
        '  <g id="subline">',
        subline(),
        "  </g>",
        '  <g id="tagline">',
        tagline(),
        "  </g>",
        "</svg>",
    ]) + "\n"


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    out = ROOT / "AV-Brand-Kit/00_Master/AV_master.svg"
    out.write_text(master_svg("full-dark"))
    print(f"wrote {out}")

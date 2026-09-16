#!/usr/bin/env python3
"""Author assets/feather.svg and assets/feather_1c.svg as clean vector.

SKILL §3 calls for GPT Image 2 + vtracer. Neither OPENAI_API_KEY nor GEMINI_API_KEY
was available in the build environment, so the feather is constructed here instead of
traced. That is strictly better for this deliverable: the output is already flat,
already on-token, has no speckle to filter and no nodes to hand-clean.

To swap in a generated feather later: drop the PNG into assets/inbox/ (see its
README.txt) and run the vtracer path from SKILL §3; nothing downstream changes,
because every consumer references assets/feather.svg by name.

Local coordinate system: 0 0 1000 1000, feather pointing up and to the right,
quill at the bottom-left, eye in the upper-right third.
"""
from __future__ import annotations

import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "AV-Brand-Kit/00_Master/tokens.json").read_text())
C = {k: v["hex"] for k, v in TOKENS["colors"].items()}

# ---------------------------------------------------------------- spine geometry
# Cubic Bezier for the shaft, from the quill (bottom-left) to the tip (top-right).
P0 = (168.0, 946.0)
P1 = (352.0, 742.0)
P2 = (548.0, 528.0)
P3 = (812.0, 214.0)


def bezier(t: float) -> tuple[float, float]:
    mt = 1.0 - t
    x = (mt**3 * P0[0] + 3 * mt**2 * t * P1[0] + 3 * mt * t**2 * P2[0] + t**3 * P3[0])
    y = (mt**3 * P0[1] + 3 * mt**2 * t * P1[1] + 3 * mt * t**2 * P2[1] + t**3 * P3[1])
    return x, y


def tangent(t: float) -> tuple[float, float]:
    mt = 1.0 - t
    dx = (3 * mt**2 * (P1[0] - P0[0]) + 6 * mt * t * (P2[0] - P1[0]) + 3 * t**2 * (P3[0] - P2[0]))
    dy = (3 * mt**2 * (P1[1] - P0[1]) + 6 * mt * t * (P2[1] - P1[1]) + 3 * t**2 * (P3[1] - P2[1]))
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def normal(t: float) -> tuple[float, float]:
    dx, dy = tangent(t)
    return -dy, dx


# Half-width of the plume envelope along the shaft. Narrow at the quill, widest
# just past the eye, then closing to a soft tip.
def half_width(t: float) -> float:
    # A long bare quill, then a compact plume in the upper half of the shaft.
    # The reference feather is exactly this: gold quill hugging the V's right
    # stroke, plume fanning up and away from it.
    if t < 0.42:                       # bare quill
        return 1.6 + 12.0 * (t / 0.42) ** 3.0
    u = (t - 0.42) / 0.58
    return 2.0 + 182.0 * math.sin(math.pi * u ** 0.88) ** 0.92


BACK = 0.34          # how far the plume reaches back over the quill
EYE_T = 0.675                          # where the eye sits along the shaft
EYE_OFF = 56.0                         # offset from the shaft, to the upper side


def eye_centre() -> tuple[float, float]:
    ex, ey = bezier(EYE_T)
    nx, ny = normal(EYE_T)
    return ex + nx * EYE_OFF, ey + ny * EYE_OFF


def fmt(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def envelope_path() -> str:
    """Outer silhouette of the plume, as one closed path."""
    steps = 84
    upper, lower = [], []
    for i in range(steps + 1):
        t = i / steps
        x, y = bezier(t)
        nx, ny = normal(t)
        w = half_width(t)
        upper.append((x + nx * w, y + ny * w))
        lower.append((x - nx * w * BACK, y - ny * w * BACK))
    pts = upper + lower[::-1]
    d = f"M {fmt(pts[0][0])} {fmt(pts[0][1])}"
    for x, y in pts[1:]:
        d += f" L {fmt(x)} {fmt(y)}"
    return d + " Z"


def barbs() -> list[tuple[str, float]]:
    """Tapered barb strokes radiating from the shaft. Returns (path_d, width)."""
    out = []
    n = 66
    for i in range(n):
        t = 0.405 + (1.0 - 0.405) * (i / (n - 1)) ** 0.94
        bx, by = bezier(t)
        nx, ny = normal(t)
        tx, ty = tangent(t)
        w = half_width(t)
        for side, shrink in ((1.0, 1.0), (-1.0, BACK)):
            # Barbs sweep forward, towards the tip.
            lead = 0.42 + 0.26 * t
            length = w * shrink * 0.97
            ex = bx + (nx * side * length) + tx * length * lead
            ey = by + (ny * side * length) + ty * length * lead
            cx = bx + (nx * side * length * 0.55) + tx * length * lead * 0.34
            cy = by + (ny * side * length * 0.55) + ty * length * lead * 0.34
            d = (f"M {fmt(bx)} {fmt(by)} Q {fmt(cx)} {fmt(cy)} {fmt(ex)} {fmt(ey)}")
            out.append((d, round(2.2 + 4.2 * math.sin(math.pi * t) ** 1.2, 2)))
    return out


def spine_path() -> str:
    return (f"M {fmt(P0[0])} {fmt(P0[1])} C {fmt(P1[0])} {fmt(P1[1])} "
            f"{fmt(P2[0])} {fmt(P2[1])} {fmt(P3[0])} {fmt(P3[1])}")


def build_full() -> str:
    ex, ey = eye_centre()
    ang = math.degrees(math.atan2(*reversed(tangent(EYE_T)))) + 90.0
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        'width="1000" height="1000" id="av-feather">',
        "  <title>Auguste Viktoria Immobilien — peacock feather</title>",
        "  <style>",
        "    .f-body{fill:%s}" % C["peacock"],
        "    .f-barb{stroke:%s;fill:none;stroke-linecap:round}" % C["peacock"],
        "    .f-barb-hi{stroke:%s;fill:none;stroke-linecap:round}" % C["teal"],
        "    .f-spine{stroke:%s;fill:none;stroke-linecap:round}" % C["gold"],
        "    .f-dark{fill:%s}" % C["green"],
        "    .f-gold{fill:%s}" % C["gold"],
        "    .f-teal{fill:%s}" % C["teal"],
        "  </style>",
        f'  <g id="feather-plume">',
        f'    <path class="f-body" d="{envelope_path()}" opacity="0.55"/>',
    ]
    bs = barbs()
    parts.append('    <g id="feather-barbs">')
    for i, (d, w) in enumerate(bs):
        cls = "f-barb-hi" if i % 7 == 3 else "f-barb"
        parts.append(f'      <path class="{cls}" stroke-width="{w}" d="{d}"/>')
    parts.append("    </g>")
    parts.append(f'    <path class="f-spine" stroke-width="7.5" d="{spine_path()}"/>')
    parts.append("  </g>")
    # ---- the eye: concentric ovals, largest first
    parts.append(f'  <g id="feather-eye" transform="rotate({ang:.1f} {ex:.1f} {ey:.1f})">')
    for rx, ry, cls, op in (
        (96, 116, "f-gold", 1.0),
        (79, 96, "f-dark", 1.0),
        (58, 72, "f-body", 1.0),
        (39, 50, "f-teal", 1.0),
        (19, 26, "f-dark", 1.0),
    ):
        parts.append(f'    <ellipse class="{cls}" cx="{ex:.1f}" cy="{ey:.1f}" '
                     f'rx="{rx}" ry="{ry}" opacity="{op}"/>')
    parts.append(f'    <ellipse class="f-gold" cx="{ex - 5:.1f}" cy="{ey - 8:.1f}" '
                 f'rx="5" ry="7" opacity="0.85"/>')
    parts.append("  </g>")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_1c() -> str:
    """Single-colour silhouette. The eye is punched through with even-odd so it stays
    legible at favicon size, where the multicolour feather turns to mud."""
    ex, ey = eye_centre()
    ang = math.degrees(math.atan2(*reversed(tangent(EYE_T)))) + 90.0
    # eye ring as an even-odd hole: approximate the ellipse with two arcs
    rx, ry = 72.0, 89.0
    ring = (f"M {ex - rx:.1f} {ey:.1f} "
            f"a {rx} {ry} 0 1 0 {2 * rx} 0 "
            f"a {rx} {ry} 0 1 0 {-2 * rx} 0 Z")
    irx, iry = 52.0, 65.0
    inner = (f"M {ex - irx:.1f} {ey:.1f} "
             f"a {irx} {iry} 0 1 0 {2 * irx} 0 "
             f"a {irx} {iry} 0 1 0 {-2 * irx} 0 Z")
    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
        'width="1000" height="1000" id="av-feather-1c" color="%s">' % C["cream"],
        "  <title>Auguste Viktoria Immobilien — peacock feather, 1 colour</title>",
        f'  <g transform="rotate({ang:.1f} {ex:.1f} {ey:.1f})" '
        'transform-origin="0 0" style="transform-box:view-box">',
        "  </g>",
        f'  <path fill="currentColor" fill-rule="evenodd" '
        f'd="{envelope_path()} {ring}"/>',
        f'  <path fill="currentColor" d="{inner}"/>',
        f'  <ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="17" ry="24" fill="none"/>',
        "</svg>",
    ]) + "\n"


def main() -> None:
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    (out / "feather.svg").write_text(build_full())
    (out / "feather_1c.svg").write_text(build_1c())
    ex, ey = eye_centre()
    print(f"wrote assets/feather.svg and assets/feather_1c.svg")
    print(f"  eye centre in local coords: ({ex:.1f}, {ey:.1f})")
    print(f"  quill {P0}  tip {P3}")


if __name__ == "__main__":
    main()

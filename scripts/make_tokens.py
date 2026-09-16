#!/usr/bin/env python3
"""Generate AV-Brand-Kit/00_Master/tokens.json from the canonical table in CLAUDE.md.

CMYK values are a FOGRA39-style approximation computed from sRGB with a simple
GCR/UCR model. They are indicative only and MUST be proofed in Affinity before print.
"""
import json, pathlib

TOKENS = {
    "green":   ("#062014", "primary background, dark-mode base, 1c print on light"),
    "cream":   ("#EBE1CC", "wordmark/letters on dark"),
    "gold":    ("#D1A976", "mountains, rules, tagline, accents"),
    "peacock": ("#337B56", "feather body"),
    "teal":    ("#21897F", "feather eye"),
    "white":   ("#FFFFFF", "1c-white mode"),
    "black":   ("#000000", "1c-black mode"),
}

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_cmyk(r, g, b):
    """Naive sRGB -> CMYK with 80% GCR, rounded to whole percent."""
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    k = 1.0 - max(rf, gf, bf)
    if k >= 1.0:
        return (0, 0, 0, 100)
    c = (1.0 - rf - k) / (1.0 - k)
    m = (1.0 - gf - k) / (1.0 - k)
    y = (1.0 - bf - k) / (1.0 - k)
    # 80 % grey component replacement keeps the deep green from going muddy
    k *= 0.80
    scale = 1.0 / (1.0 - k) if k < 1.0 else 1.0
    c, m, y = [min(1.0, v * scale) for v in (c, m, y)]
    return tuple(round(v * 100) for v in (c, m, y, k))

def main():
    out = {
        "_note": (
            "Canonical brand tokens for Auguste Viktoria Immobilien. "
            "Every script in scripts/ reads this file; never hard-code hex values elsewhere."
        ),
        "_cmyk_warning": (
            "CMYK values are a FOGRA39-style approximation computed from sRGB, not a "
            "measured separation. Proof them in Affinity (Document > Colour > CMYK, "
            "FOGRA39) before any print run. #062014 prints close to black on uncoated stock."
        ),
        "fonts": {
            "display": {"family": "Cinzel", "use": "monogram, wordmark", "licence": "SIL OFL 1.1"},
            "text":    {"family": "Montserrat", "use": "IMMOBILIEN subline, tagline, body", "licence": "SIL OFL 1.1"},
        },
        "colors": {},
    }
    for name, (hexv, use) in TOKENS.items():
        r, g, b = hex_to_rgb(hexv)
        c, m, y, k = rgb_to_cmyk(r, g, b)
        out["colors"][name] = {
            "hex": hexv,
            "rgb": [r, g, b],
            "rgb_css": f"rgb({r}, {g}, {b})",
            "cmyk_approx": [c, m, y, k],
            "cmyk_css": f"cmyk({c}%, {m}%, {y}%, {k}%)",
            "use": use,
        }
    p = pathlib.Path(__file__).resolve().parent.parent / "AV-Brand-Kit/00_Master/tokens.json"
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {p}")
    for n, v in out["colors"].items():
        print(f"  {n:8s} {v['hex']}  rgb{tuple(v['rgb'])}  cmyk{tuple(v['cmyk_approx'])}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Measure ref/logo_AV.png so the master SVG reproduces its proportions.

Segments the reference by colour distance to the brand tokens, then reports
bounding boxes and row/column profiles for each component in viewBox units
(0..1000), which is the coordinate system of AV_master.svg.
"""
import json, pathlib
from PIL import Image
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
img = Image.open(ROOT / "ref/logo_AV.png").convert("RGB")
W, H = img.size
a = np.asarray(img).astype(int)
S = 1000.0 / W  # scale px -> viewBox units

def to_vb(v):  return round(v * S, 1)

bg = np.array([6, 32, 20])
dist_bg = np.sqrt(((a - bg) ** 2).sum(axis=2))
ink = dist_bg > 42           # anything that is not background
cream = (a[:,:,0] > 150) & (a[:,:,1] > 140) & (a[:,:,2] > 110)   # cream+gold letters
gold  = (a[:,:,0] > 120) & (a[:,:,0] < 240) & (a[:,:,2] < 170) & (a[:,:,0] - a[:,:,2] > 35)
greenish = (a[:,:,1] - a[:,:,0] > 18) & (a[:,:,1] > 55)          # feather body

def bbox(mask, name):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    b = dict(name=name, x0=to_vb(xs.min()), x1=to_vb(xs.max()),
             y0=to_vb(ys.min()), y1=to_vb(ys.max()))
    b["w"] = round(b["x1"] - b["x0"], 1)
    b["h"] = round(b["y1"] - b["y0"], 1)
    b["cx"] = round((b["x0"] + b["x1"]) / 2, 1)
    b["px"] = len(xs)
    return b

# Row profile: find the horizontal bands that separate the components.
rows = ink.sum(axis=1)
bands, start = [], None
for y in range(H):
    if rows[y] > 2 and start is None:
        start = y
    elif rows[y] <= 2 and start is not None:
        if y - start > 4:
            bands.append((start, y - 1))
        start = None
if start is not None:
    bands.append((start, H - 1))

out = {"source_px": [W, H], "viewBox": 1000, "bands": [], "components": {}}
print(f"reference {W}x{H}  scale={S:.4f} px->vb\n")
print("horizontal bands (viewBox units):")
for i, (y0, y1) in enumerate(bands):
    band = np.zeros_like(ink); band[y0:y1+1, :] = ink[y0:y1+1, :]
    b = bbox(band, f"band{i}")
    out["bands"].append(b)
    print(f"  band{i}: y {to_vb(y0):7.1f} .. {to_vb(y1):7.1f}  h={to_vb(y1-y0):6.1f}"
          f"  x {b['x0']:7.1f} .. {b['x1']:7.1f}  w={b['w']:6.1f}  cx={b['cx']:6.1f}")

for name, mask in [("ink_all", ink), ("cream_all", cream), ("gold_all", gold),
                   ("feather_green", greenish)]:
    b = bbox(mask, name)
    out["components"][name] = b
    print(f"\n{name:14s} x {b['x0']:7.1f}..{b['x1']:7.1f} (w {b['w']:6.1f})"
          f"  y {b['y0']:7.1f}..{b['y1']:7.1f} (h {b['h']:6.1f})  px={b['px']}")

(ROOT / "review").mkdir(exist_ok=True)
(ROOT / "review/ref_measurements.json").write_text(json.dumps(out, indent=2))
print("\nwrote review/ref_measurements.json")

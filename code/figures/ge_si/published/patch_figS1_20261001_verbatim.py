# -*- coding: utf-8 -*-
"""Fig. S1: replace the noun phrase "Source-induced caveat / required" with the verb
phrase "Report the source-induced / caveat", matching Arial em=58 px @600 dpi."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')

D = r"E:\workbuddy\2026-10-01-15-13-22\_figs3"
FD = r"C:\Windows\Fonts\arial.ttf"
EM = 58
FILL = (255, 246, 229)
BLACK = (0, 0, 0)

src = os.path.join(D, "image1.png")
im = Image.open(src).convert("RGB")
a = np.array(im).copy()
print("image1", im.size)

# --- erase the two old text lines (bbox + 6 px margin) ----------------------
ZONES = [  # (y0,y1,x0,x1)
    (2251, 2305, 1293, 1898),   # "Source-induced caveat"
    (2325, 2390, 1486, 1702),   # "required"
]
for (y0, y1, x0, x1) in ZONES:
    before = int((a[y0:y1, x0:x1].astype(int).max(axis=2) < 200).sum())
    a[y0:y1, x0:x1] = FILL
    after = int((a[y0:y1, x0:x1].astype(int).max(axis=2) < 200).sum())
    print("  erase y[%d,%d] x[%d,%d]: 残余深色 %d -> %d" % (y0, y1, x0, x1, before, after))
    assert after == 0, "eraser left dark pixels"

out = Image.fromarray(a)
dr = ImageDraw.Draw(out)
ft = ImageFont.truetype(FD, EM)

NEW = [("Report the source-induced", 1595.5, 2299),
       ("caveat", 1594.0, 2372)]
for s, cx, base in NEW:
    dr.text((cx, base), s, font=ft, fill=BLACK, anchor="ms")
    bb = ft.getbbox(s)
    print("  drawn %-26s anchor=(%.1f,%d) advance=%.0f ink w=%d" % (s, cx, base, ft.getlength(s), bb[2] - bb[0]))

out.save(os.path.join(D, "image1_patched.png"))
out.crop((1150, 1980, 2020, 2480)).save(os.path.join(D, "s1_preview.png"))
print("saved image1_patched.png / s1_preview.png")

# --- verification ----------------------------------------------------------
b = np.array(out).copy()
mx = b.max(axis=2)
sub = mx[2250:2395, 1285:1905]
dark = sub < 200
rows = np.where(dark.any(axis=1))[0]
print("新文本行 y 段:", [int(r) + 2250 for r in (rows.min(), rows.max())])
runs = []
s0 = None
for i, v in enumerate(dark.sum(axis=1)):
    if v > 0:
        if s0 is None: s0 = i
    else:
        if s0 is not None:
            if i - s0 > 3: runs.append((s0 + 2250, i - 1 + 2250))
            s0 = None
if s0 is not None: runs.append((s0 + 2250, 2394))
print("行分段:", runs)
for (y0, y1) in runs:
    cc = np.where(dark[y0 - 2250:y1 - 2250 + 1].any(axis=0))[0]
    print("   y[%d,%d] x[%d,%d] w=%d" % (y0, y1, 1285 + cc.min(), 1285 + cc.max(), cc.max() - cc.min() + 1))

# -*- coding: utf-8 -*-
"""Fig. S1: replace the noun phrase "Source-induced caveat / required" with the verb
phrase "Report the source-induced / caveat", matching Arial em = 58 px @600 dpi.

Provenance
----------
`patch_figS1_20261001_verbatim.py` is the script that actually produced the published
figure on 2026-10-01, kept byte-for-byte. This file is the same script made runnable from
the archive. **Every decision that affects pixels is unchanged**: the two erase
rectangles, the fill colour, the interpolation-free erase (a rectangle fill, so no glyph
pixel is ever blended), the font, the em size, the two text anchors and their
coordinates. Only three things were changed:

  * the input directory became this file's own directory (the original read and wrote
    ``E:\\workbuddy\\2026-10-01-15-13-22\\_figs3\\``),
  * the output became ``FigS1_reapplied.png`` instead of ``image1_patched.png``, so that
    running this never overwrites the reference copy ``FigS1_published.png``,
  * the trailing self-check compares against that reference instead of only printing
    line extents.

Verified 2026-10-03: re-running against ``FigS1_pre_patch.png`` reproduces
``FigS1_published.png`` with **zero differing pixels**.

    changed: 17,589 px, bbox x[1260,1931] y[2256,2384] — 0.179 % of the 3189 x 3077 image

The pixel edit is therefore **script-level reproducible**. The base raster it is applied
to is not; see `README.md` for why, and for what that does and does not imply.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "FigS1_pre_patch.png")
DST = os.path.join(HERE, "FigS1_reapplied.png")
REF = os.path.join(HERE, "FigS1_published.png")

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
]
EM = 58
FILL = (255, 246, 229)
BLACK = (0, 0, 0)

ZONES = [                             # (y0, y1, x0, x1)
    (2251, 2305, 1293, 1898),         # "Source-induced caveat"
    (2325, 2390, 1486, 1702),         # "required"
]
NEW = [("Report the source-induced", 1595.5, 2299),
       ("caveat", 1594.0, 2372)]


def find_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit(
        "Arial not found. The published glyphs were rendered in Arial; another family "
        "would not reproduce them.\nTried:\n  " + "\n  ".join(FONT_CANDIDATES))


def apply(im):
    """Return the patched image. The input is not modified."""
    a = np.array(im.convert("RGB")).copy()
    for (y0, y1, x0, x1) in ZONES:
        n_before = int((a[y0:y1, x0:x1].astype(int).max(axis=2) < 200).sum())
        a[y0:y1, x0:x1] = FILL
        n_after = int((a[y0:y1, x0:x1].astype(int).max(axis=2) < 200).sum())
        print("  erase y[%d,%d] x[%d,%d]: dark px %d -> %d"
              % (y0, y1, x0, x1, n_before, n_after))
        assert n_after == 0, "eraser left dark pixels"
    out = Image.fromarray(a)
    dr = ImageDraw.Draw(out)
    ft = ImageFont.truetype(find_font(), EM)
    for s, cx, base in NEW:
        dr.text((cx, base), s, font=ft, fill=BLACK, anchor="ms")
        print("  drawn %-26s anchor=(%.1f,%d) advance=%.0f"
              % (s, cx, base, ft.getlength(s)))
    return out


def main():
    print("source : %s" % os.path.basename(SRC))
    out = apply(Image.open(SRC))
    out.save(DST)
    print("wrote  : %s (%s B)" % (os.path.basename(DST), format(os.path.getsize(DST), ",")))

    if not os.path.exists(REF):
        print("reference %s absent; wrote the reapplied copy only" % os.path.basename(REF))
        return 0
    ref = np.asarray(Image.open(REF).convert("RGB")).astype(int)
    cur = np.asarray(out).astype(int)
    assert ref.shape == cur.shape, "size differs: %s vs %s" % (cur.shape, ref.shape)
    d = np.abs(cur - ref).max(axis=2)
    n = int((d > 0).sum())
    print("vs %s: pixels differing = %d" % (os.path.basename(REF), n))
    if n:
        ys, xs = np.where(d > 0)
        print("  bbox x[%d,%d] y[%d,%d]" % (xs.min(), xs.max(), ys.min(), ys.max()))
    return 0 if n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

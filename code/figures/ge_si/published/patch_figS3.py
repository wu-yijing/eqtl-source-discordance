# -*- coding: utf-8 -*-
"""Fig. S3 panel (a): truncate the panel title, keeping the prefix the published figure
already carried.

    old title: (a) Endpoint detection boundary and single-gene power
    new title: (a) Endpoint detection boundary
    changed  : 10,587 px, bbox x[1164,1883] y[68,127]

Status: **reconstruction**, and a verified one. The 2026-10-01 session kept a runnable
script for Fig. S1 (`patch_figS1_20261001_verbatim.py`) but only the *parameters* for
Fig. S3, in its session record:

    新标题恰为旧标题的前缀，因此只擦除 x∈[1145,1894], y∈[58,137] 的后半段
    (and single-gene power)，保留原有字形像素不动，实现零重绘误差。

That recipe is completely specified, and this file is it. Verified 2026-10-03: applying it
to `FigS3_pre_patch.png` reproduces `FigS3_published.png` with **zero differing pixels**.

Why it is exact
---------------
The new title is a prefix of the old one, so nothing had to be redrawn: the surviving
glyphs are the original pixels. The erase rectangle is deliberately wider than the ink it
removes, and the panel background inside it is uniform white, so widening it changes
nothing — any window covering x[1164,1884) y[68,128) gives the same result.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "FigS3_pre_patch.png")
DST = os.path.join(HERE, "FigS3_reapplied.png")
REF = os.path.join(HERE, "FigS3_published.png")

X0, X1 = 1145, 1895      # documented erase window, x in [1145, 1894] inclusive
Y0, Y1 = 58, 138         # documented erase window, y in [58, 137] inclusive
FILL = (255, 255, 255)   # panel background inside the window is uniform white


def apply(im):
    """Return the truncated image. The input is not modified."""
    a = np.array(im.convert("RGB")).copy()
    zone = a[Y0:Y1, X0:X1]
    n_colours = len(np.unique(zone.reshape(-1, 3), axis=0))
    n_before = int((zone.astype(int).max(axis=2) < 200).sum())
    a[Y0:Y1, X0:X1] = FILL
    n_after = int((a[Y0:Y1, X0:X1].astype(int).max(axis=2) < 200).sum())
    print("  erase x[%d,%d) y[%d,%d): %d distinct colours, dark px %d -> %d"
          % (X0, X1, Y0, Y1, n_colours, n_before, n_after))
    assert n_after == 0, "eraser left dark pixels"
    return Image.fromarray(a)


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

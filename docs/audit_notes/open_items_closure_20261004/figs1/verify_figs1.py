#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_figs1.py — reproduce every number the Fig. S1 finding rests on.

Reads the two rasters this repository already ships under
`code/figures/ge_si/published/` and one or more candidate re-runs, and reports:

  1. size of each raster;
  2. differing pixels against `FigS1_pre_patch.png` after cropping to the smaller
     size — and after a **translation search** over +/-3 px, so a mere offset
     cannot be mistaken for a real difference;
  3. the amplitude histogram of the differences (how many differ by 1-8 grey
     levels vs by more than 64) — this is what separates a re-rasterisation from a
     different drawing;
  4. the row/column spread, i.e. whether the difference is local or whole-canvas.

Usage
-----
    python verify_figs1.py                       # uses the two shipped re-runs
    python verify_figs1.py --candidates a.png b.png
    python verify_figs1.py --json out.json

Everything here is Pillow + numpy. Pixels, not bytes: `ge_si/published/README.md`
records that the document stores its media re-encoded, so bytes are not comparable.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def rgb_on_white(path):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[3])
        return bg
    return im.convert("RGB")


def compare(cand, ref):
    """Best (fewest-differing-pixels) translation of `cand` against `ref`."""
    c = np.asarray(cand).astype(int)
    r = np.asarray(ref).astype(int)
    H, W, _ = r.shape
    h, w, _ = c.shape
    rows = []
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            y0, y1 = max(0, dy), min(H, dy + h)
            x0, x1 = max(0, dx), min(W, dx + w)
            if y0 >= y1 or x0 >= x1:
                continue
            a = r[y0:y1, x0:x1]
            b = c[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
            n = int((np.abs(a - b).max(2) > 0).sum())
            rows.append((n, dy, dx, a.shape[0] * a.shape[1], a, b))
    rows.sort(key=lambda t: t[0])
    n, dy, dx, tot, a, b = rows[0]
    d = np.abs(a - b).max(2)
    return {
        "candidate_size": [w, h],
        "reference_size": [W, H],
        "best_offset": [dy, dx],
        "differing_pixels": n,
        "overlap_pixels": tot,
        "pct": round(100.0 * n / tot, 4),
        "max_channel_difference": int(d.max()),
        "amplitude_1_to_8": int(((d > 0) & (d <= 8)).sum()),
        "amplitude_gt_8": int((d > 8).sum()),
        "amplitude_gt_64": int((d > 64).sum()),
        "rows_with_a_difference": int((d.sum(axis=1) > 0).sum()),
        "cols_with_a_difference": int((d.sum(axis=0) > 0).sum()),
    }


def find_published(explicit=None):
    """`code/figures/ge_si/published`, found by walking up from this file.

    The directory is reached by a different number of `..` depending on where this
    audit note lives, so it is searched for rather than assumed.
    """
    if explicit:
        return os.path.abspath(explicit)
    d = HERE
    while True:
        cand = os.path.join(d, "code", "figures", "ge_si", "published")
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def main():
    ap = argparse.ArgumentParser(description="reproduce the Fig. S1 pixel findings")
    ap.add_argument("--published-dir", default=None,
                    help="directory holding FigS1_pre_patch.png / FigS1_published.png "
                         "(default: found by walking up to code/figures/ge_si/published)")
    ap.add_argument("--candidates", nargs="*", default=None,
                    help="candidate re-runs (default: the two shipped here)")
    ap.add_argument("--json")
    a = ap.parse_args()

    pub = find_published(a.published_dir)
    if pub is None:
        print("could not locate code/figures/ge_si/published — pass --published-dir")
        return 2
    pre = rgb_on_white(os.path.join(pub, "FigS1_pre_patch.png"))
    aft = rgb_on_white(os.path.join(pub, "FigS1_published.png"))
    print("published_dir  %s" % pub)
    print("pre_patch      %s" % (pre.size,))
    print("published      %s" % (aft.size,))

    cands = a.candidates or [os.path.join(HERE, "rerun_published_greentext.png"),
                             os.path.join(HERE, "rerun_legacy_greentext.png")]
    out = {"pre_patch_size": list(pre.size), "published_size": list(aft.size),
           "candidates": {}}
    for p in cands:
        if not os.path.exists(p):
            print("\n%s  -> absent, skipped" % p)
            continue
        c = rgb_on_white(p)
        r = compare(c, pre)
        out["candidates"][os.path.basename(p)] = r
        print("\n%s" % os.path.basename(p))
        print("  size                        %s   (published %s)" % (c.size, pre.size))
        print("  best offset                 dy=%+d dx=%+d" % tuple(r["best_offset"]))
        print("  differing pixels            %d / %d = %.4f%%"
              % (r["differing_pixels"], r["overlap_pixels"], r["pct"]))
        print("  amplitude 1-8 / >8 / >64    %d / %d / %d"
              % (r["amplitude_1_to_8"], r["amplitude_gt_8"], r["amplitude_gt_64"]))
        print("  rows / cols with a diff     %d / %d"
              % (r["rows_with_a_difference"], r["cols_with_a_difference"]))

    # The published pair should differ by the recorded pixel edit. Note the two
    # numbers are not the same measurement: the archive's 17,589 is what its own
    # patch script changes (`verify_published.py` check 2, patch output vs
    # published); the count below is `pre_patch` vs `published` directly, so it
    # also carries anything else that happened between the two rasters.
    e = compare(aft, pre)
    out["published_vs_pre_patch"] = e
    print("\nFigS1_published vs FigS1_pre_patch, compared directly")
    print("  differing pixels            %d" % e["differing_pixels"])
    print("  for reference, the archive records 17,589 px for its own patch script;")
    print("  the two numbers measure different things (see the comment in this file).")

    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print("\nwrote %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())

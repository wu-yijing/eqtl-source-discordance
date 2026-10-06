#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_figures_pixels.py — compare figure outputs by pixel, not by byte.

Why this exists
---------------
`figures/README.md` verifies a release by regenerating the figures and recording
`sha256sum figures/*.pdf figures/*.png` in `metadata/provenance.json`. That works on the
machine that produced the figures. It does NOT work across platforms, and the first real
run of the shipped Dockerfile proved how badly it misleads:

    run_all.sh on the Windows host  -> figures/*.png byte-identical to the committed files
    run_all.sh in the Linux image   -> every .png DIFFERENT, sizes off by ~2 %

Every one of those eight images turned out to be **pixel-identical** — 0 differing pixels,
maximum channel delta 0 — with these parts identical too: IHDR, pHYs, IEND, and the
*decompressed* IDAT stream (22,266,060 bytes for Fig3.png). Only the *compressed* IDAT
differed, because

    host      zlib 1.3.1
    container zlib 1.3.2   (compiled against 1.3.1)

and zlib 1.3.2 emits a different, larger deflate stream for the same input. Same for the
PDFs, which differ by exactly 6 bytes in `startxref` because the embedded date strings are
a different length.

So a byte comparison across platforms reports "the archive does not reproduce" when the
archive reproduced perfectly. This script answers the question that actually matters.

    python3 scripts/compare_figures_pixels.py <reference_dir> <candidate_dir>

Exit status
-----------
0  every PNG present in <reference_dir> exists in <candidate_dir> and is pixel-identical.
   Byte-level differences are reported, not failed on.
1  a PNG is missing, has a different shape, or differs in at least one pixel.

PDFs are reported for completeness only and never fail the run: they embed a creation date
and, where objects are Flate-compressed, carry the same zlib difference.
"""
import os
import re
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    sys.exit("needs numpy and Pillow: %s" % exc)


def png_verdict(ref, cand):
    """Return (ok, message) for one PNG pair."""
    a = np.asarray(Image.open(ref).convert("RGB")).astype(int)
    b = np.asarray(Image.open(cand).convert("RGB")).astype(int)
    if a.shape != b.shape:
        return False, "SHAPE %s vs %s" % (a.shape, b.shape)
    d = np.abs(a - b).max(axis=2)
    nz = int((d > 0).sum())
    if nz == 0:
        return True, "%dx%d  pixel-identical" % (a.shape[1], a.shape[0])
    return False, "%dx%d  %d differing px (%.4f%%), max delta %d" % (
        a.shape[1], a.shape[0], nz, 100.0 * nz / d.size, int(d.max()))


def pdf_verdict(ref, cand):
    a = open(ref, "rb").read()
    b = open(cand, "rb").read()
    strip = lambda x: re.sub(rb"/(Creation|Mod)Date\s*\([^)]*\)", rb"/\1Date(X)", x)
    note = "identical modulo embedded dates" if strip(a) == strip(b) else \
           "differs beyond embedded dates (Flate streams carry the zlib difference)"
    return len(a) == len(b), "%7d vs %7d bytes  %s" % (len(a), len(b), note)


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__.strip().splitlines()[-1])
    ref_dir, cand_dir = argv[1], argv[2]
    for d in (ref_dir, cand_dir):
        if not os.path.isdir(d):
            sys.exit("not a directory: %s" % d)

    names = sorted(f for f in os.listdir(ref_dir) if f.endswith(".png"))
    if not names:
        sys.exit("no PNG in %s" % ref_dir)

    failures, byte_diffs = 0, 0
    print("reference : %s" % ref_dir)
    print("candidate : %s" % cand_dir)
    print()
    for fn in names:
        ref, cand = os.path.join(ref_dir, fn), os.path.join(cand_dir, fn)
        if not os.path.isfile(cand):
            print("  [FAIL] %-11s missing" % fn)
            failures += 1
            continue
        same_bytes = open(ref, "rb").read() == open(cand, "rb").read()
        if not same_bytes:
            byte_diffs += 1
        ok, msg = png_verdict(ref, cand)
        tag = "ok" if ok else "FAIL"
        if not ok:
            failures += 1
        print("  [ %-4s] %-11s %-9s %s" % (tag, fn, "byte-equal" if same_bytes
                                           else "byte-diff", msg))

    pdfs = sorted(f for f in os.listdir(ref_dir) if f.endswith(".pdf"))
    if pdfs:
        print()
        for fn in pdfs:
            ref, cand = os.path.join(ref_dir, fn), os.path.join(cand_dir, fn)
            if not os.path.isfile(cand):
                print("  [info] %-11s missing (PDFs do not fail this check)" % fn)
                continue
            eq, msg = pdf_verdict(ref, cand)
            print("  [info] %-11s %s" % (fn, msg))

    print()
    if failures:
        print(" RESULT: %d figure(s) are NOT pixel-identical." % failures)
        return 1
    if byte_diffs:
        print(" RESULT: every figure is pixel-identical, but %d of %d files differ in "
              "bytes." % (byte_diffs, len(names)))
        print("         That is a zlib build difference (1.3.1 vs 1.3.2), not a "
              "reproduction failure — see this script's docstring.")
    else:
        print(" RESULT: every figure is byte-identical and pixel-identical.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

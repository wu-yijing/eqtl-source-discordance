# -*- coding: utf-8 -*-
"""Verify that the published Fig. S1 / Fig. S3 rasters in this directory are exactly the
ones embedded in the submitted Supporting Information, and that the two pixel edits that
were applied to them are re-runnable.

Three checks, all of which must pass:

1. **Identity.** SHA-256 of the four rasters matches the values recorded below.
2. **Re-runnability.** `patch_figS1.apply()` and `patch_figS3.apply()` are run against the
   pre-patch rasters; the results must equal the published rasters pixel for pixel, and the
   number of changed pixels must equal the figure's recorded edit size.
3. **Not-the-generator** (optional, needs an out-of-tree copy). With `--si-copy DIR`, each
   published raster is compared against the media file extracted from the submitted
   Supporting Information; they must be *pixel*-identical even though they are not
   byte-identical (the document stores them re-encoded).

    python3 verify_published.py
    python3 verify_published.py --si-copy /path/to/extracted/word/media

Exit status: 0 if every check passes, 1 otherwise.
"""
import argparse
import hashlib
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    # name,                      bytes,   sha256,                                                             md5
    ("FigS1_pre_patch.png",      359530, "3acd720f48839e0088a6192c536543e3d1d920f7dc4c33d5f45decb344b6ae48", "a6302c63abcf5055a2931f8ad233542c"),
    ("FigS1_published.png",      359921, "a899405753d07cc77d5c10613b8719cc8e24128470d22199898f7842fa763095", "0dead347444b94f45bd4544e5b891fb4"),
    ("FigS3_pre_patch.png",      380110, "b25f48d9e06023c5acc452dd8e924cda8ceabb17ef588a262b4a4472b9e52d47", "64304462d898344620b0194aae1e88e7"),
    ("FigS3_published.png",      373615, "758c5b1d80d9da5866c9ce04b2d9d120a495e9d570f0857f5d044a668c2f7e26", "99e06c1014558e646c1d765757b234b8"),
]

# (pre-patch, published, changed pixels, bbox x0 x1 y0 y1)
EDITS = [
    ("FigS1", 17589, (1260, 1931, 2256, 2384)),
    ("FigS3", 10587, (1164, 1883,   68,  127)),
]

# The two patches are shipped as standalone, runnable recipes. Import them rather than
# re-implementing their logic, so this verifier cannot drift from what they do.
sys.path.insert(0, HERE)
import patch_figS1  # noqa: E402
import patch_figS3  # noqa: E402

MODULES = {"FigS1": patch_figS1, "FigS3": patch_figS3}

failures = []


def check(label, ok, detail=""):
    print("  %s %s%s" % ("ok  " if ok else "FAIL", label, ("  " + detail) if detail else ""))
    if not ok:
        failures.append(label)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--si-copy", metavar="DIR",
                    help="directory holding the SI media files (image1.png = Fig. S1, "
                         "image3.png = Fig. S3), e.g. <unzipped docx>/word/media")
    args = ap.parse_args()

    print("1. identity")
    for name, size, sha, _md5 in FILES:
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            check(name, False, "missing")
            continue
        got_size, got_sha = os.path.getsize(p), sha256(p)
        check(name, got_size == size and got_sha == sha,
              "%s B  %s" % (format(got_size, ","), got_sha[:16] + "..."))

    print("2. re-runnability of the two pixel edits")
    for fig, want_px, (x0, x1, y0, y1) in EDITS:
        mod = MODULES[fig]
        pre = Image.open(os.path.join(HERE, "%s_pre_patch.png" % fig))
        ref = np.asarray(Image.open(os.path.join(HERE, "%s_published.png" % fig))
                         .convert("RGB")).astype(int)
        got = np.asarray(mod.apply(pre).convert("RGB")).astype(int)
        if got.shape != ref.shape:
            check("%s re-run" % fig, False, "size %s vs %s" % (got.shape, ref.shape))
            continue
        d = np.abs(got - ref).max(axis=2)
        n_diff = int((d > 0).sum())
        check("%s re-run pixel-identical" % fig, n_diff == 0,
              "%d px differ" % n_diff)
        # the number of pixels the edit actually touches
        a = np.asarray(pre.convert("RGB")).astype(int)
        e = np.abs(a - ref).max(axis=2) > 12
        n_edit = int(e.sum())
        ys, xs = np.where(e)
        bbox = (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())) if n_edit else None
        check("%s edit size" % fig, n_edit == want_px and bbox == (x0, x1, y0, y1),
              "%s px, bbox %s (recorded %s px, bbox %s)"
              % (format(n_edit, ","), bbox, format(want_px, ","), (x0, x1, y0, y1)))

    if args.si_copy:
        print("3. identity with the submitted Supporting Information")
        for fig, media in (("FigS1", "image1.png"), ("FigS3", "image3.png")):
            p = os.path.join(args.si_copy, media)
            if not os.path.exists(p):
                check("%s vs %s" % (fig, media), False, "not found")
                continue
            pub = np.asarray(Image.open(os.path.join(HERE, "%s_published.png" % fig))
                             .convert("RGB")).astype(np.int16)
            si = np.asarray(Image.open(p).convert("RGB")).astype(np.int16)
            same_px = pub.shape == si.shape
            n_diff = -1
            if same_px:
                n_diff = int((np.abs(pub - si).max(axis=2) > 0).sum())
                same_px = n_diff == 0
            check("%s pixel-identical to %s" % (fig, media), same_px,
                  "size %s vs %s, %d px differ; bytes %s vs %s"
                  % (pub.shape[:2], si.shape[:2], n_diff,
                     sha256(os.path.join(HERE, "%s_published.png" % fig))[:16],
                     sha256(p)[:16]))
    else:
        print("3. identity with the submitted Supporting Information — skipped "
              "(pass --si-copy DIR to run)")

    print()
    if failures:
        print("%d check(s) FAILED: %s" % (len(failures), "; ".join(failures)))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

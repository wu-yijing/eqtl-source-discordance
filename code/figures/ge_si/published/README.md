# code/figures/ge_si/published/ — the published Fig. S1 / Fig. S3 rasters

The Supporting Information embeds its figures as bitmaps. This directory holds those
bitmaps, the pre-edit versions, and the two pixel edits that connect them — so that the
published *pixels* can be reproduced and checked, rather than taken on trust.

## What is here

| File | Size | px | SHA-256 | MD5 |
|---|---|---|---|---|
| `FigS1_published.png` | 359,921 B | 3189 × 3077 | `a899405753d07cc77d5c10613b8719cc8e24128470d22199898f7842fa763095` | `0dead347444b94f45bd4544e5b891fb4` |
| `FigS1_pre_patch.png` | 359,530 B | 3189 × 3077 | `3acd720f48839e0088a6192c536543e3d1d920f7dc4c33d5f45decb344b6ae48` | `a6302c63abcf5055a2931f8ad233542c` |
| `FigS3_published.png` | 373,615 B | 3990 × 1800 | `758c5b1d80d9da5866c9ce04b2d9d120a495e9d570f0857f5d044a668c2f7e26` | `99e06c1014558e646c1d765757b234b8` |
| `FigS3_pre_patch.png` | 380,110 B | 3990 × 1800 | `b25f48d9e06023c5acc452dd8e924cda8ceabb17ef588a262b4a4472b9e52d47` | `64304462d898344620b0194aae1e88e7` |
| `patch_figS1_20261001_verbatim.py` | — | — | — | — |
| `patch_figS1.py` | — | — | — | — |
| `patch_figS3.py` | — | — | — | — |
| `verify_published.py` | — | — | — | — |

The two `_published` files are **the rasters embedded in the submitted Supporting
Information**, verified pixel for pixel in check 3 below. All four document media parts
(`image1`–`image4`) are byte-identical between the submitted SI and the 2026-10-03 revision
of it, so that revision — which changed document *text* only — did not touch any figure.

## Verify

```bash
cd code/figures/ge_si/published
python3 verify_published.py                                   # checks 1 and 2
python3 verify_published.py --si-copy <unzipped docx>/word/media   # plus check 3
```

1. **Identity** — the four SHA-256 above.
2. **Re-runnability** — `patch_figS1.apply()` and `patch_figS3.apply()` are run against the
   pre-patch rasters. Both reproduce the published rasters with **zero differing pixels**,
   and the changed-pixel counts come out at the recorded 17,589 px (bbox x[1260,1931]
   y[2256,2384]) and 10,587 px (bbox x[1164,1883] y[68,127]).
3. **Identity with the submitted SI** — `FigS1_published.png` is pixel-identical to
   `word/media/image1.png` and `FigS3_published.png` to `word/media/image3.png`. They are
   **not byte-identical**: the document stores the media re-encoded (Fig. S1 at 600 dpi,
   optimised). Pixels are the right comparison; bytes are not.

## What was edited, and by what

| Figure | Edit | Pixels | Bounding box |
|---|---|---|---|
| Fig. S1 | middle branch box: `Source-induced caveat / required` → `Report the source-induced / caveat` | 17,589 | x[1260,1931] y[2256,2384] |
| Fig. S3 | panel (a) title truncated: `(a) Endpoint detection boundary and single-gene power` → `(a) Endpoint detection boundary` | 10,587 | x[1164,1883] y[68,127] |

Both are **interpolation-free**: Fig. S1 erases two rectangles to the box fill colour
`#FFF6E5` and draws the new text in Arial at em = 58 px with `anchor="ms"`; Fig. S3 erases
the second half of the title to white, which works because the new title is a *prefix* of
the old one, so the surviving glyphs are the original pixels. Neither edit resamples
anything, which is why both reproduce exactly.

`patch_figS1_20261001_verbatim.py` is the script as it was actually run, with its original
absolute paths. `patch_figS1.py` is the same script with the paths made relative, a
different output filename, and a self-check — the pixel-affecting constants are untouched.
`patch_figS3.py` is a **reconstruction** from the session record's parameters (the session
kept no script for Fig. S3); it is verified exact by check 2, so the reconstruction status
does not weaken it.

## What is *not* claimed: the base raster is not this generator's output

The rasters above are **not** what `../rebuild_fig1_2_9.py` produces. It produces
**3188 × 3076**; these are **3189 × 3077**. Measured on 2026-10-03:

- FFT phase correlation gives an optimal translation of **(0, 0)** with sub-pixel
  correction (0.21, −0.10) — so this is not a crop or a shift.
- After sub-pixel registration, **2.6 %** of pixels still differ (|Δ| > 24), distributed
  across **all twelve** text and box bands (y 92 → 2977, x 124 → 3064) — i.e. on every
  glyph stroke and every box border, with slightly more dark ink (+3.8 %) and slightly
  less anti-aliasing (−367 px in one sampled region).
- That is the signature of **the same vector artwork rasterised by a different renderer
  build** (matplotlib/Agg + FreeType), not of a content difference.
- Recovery was attempted and failed: resampling (6 filters, best 277,449 px differ), 1 px
  padding (four corners), font substitution (Arial / DejaVu Sans / Liberation Sans — all
  still 3188 × 3076), twelve rasterisation settings (`text.hinting` none / no_hinting /
  auto / native / either, `text.hinting_factor` 1 / 2 / 8, `text.antialiased=False`,
  `agg.path.chunksize=0`, `lines.antialiased=False`, `patch.antialiased=False` — **all**
  still 3188 × 3076, best 206,002 px differ), and a full-disk search for the original
  generator script.
- The current script **is** faithful to its own family: its output differs from the
  historical `before_figure_text_sync_20260923/FigS1.png` (also 3188 × 3076) in **one
  contiguous band only**, y[2256,2387], 20,026 px — exactly the text that was intentionally
  changed. The other 2,965 rows are identical.

So there are two raster families:

| Family | Size | Example | Producing path |
|---|---|---|---|
| A | 3188 × 3076 | `定稿补充图_FigS1-S5_20260915/.../_backup_before_600dpi_20260915_210047/FigS1.png` (441,493 B) | `../rebuild_fig1_2_9.py` regenerates this family |
| B | 3189 × 3077 | the four rasters here | **no script in this archive produces it** |

**The consequence, stated plainly:** the published figure is reproducible at
**artefact level** — exactly, and in a way anyone can re-check with the two recipes above —
but **not at script level**: re-running `../rebuild_fig1_2_9.py` gives the published
*content* in a different rasterisation. Do not describe the archive as regenerating the
published Fig. S1 from a script.

Anyone who needs the two to agree exactly has two options, and only two: ship the
regenerated figure instead of the pixel-edited one — which would discard the verified
17,589 px edit and turn a 0.179 % change into a full re-render — or accept the published
pixels as the artefact, which is what this directory does.

## Provenance

Both `_pre_patch` rasters are the media extracted from the Supporting Information before
the 2026-10-01 edit; their line-for-line identity with the working copies used that day was
checked on 2026-10-03 (zero differing pixels against
`2026-10-01-15-13-22/_figs3/image1.png` and `.../image3.png`, and against the copies
preserved in `_ge_fix_20260930/image1.png` and `投稿前定稿/Figures_Supplementary_SourceBackup/Figure_S1.png`
for Fig. S1). The 2026-10-01 session's own audit — which recorded the same 17,589 and
10,587 px and the same bounding boxes — is at
`GE投稿资料/_修订_20260930/_图件修订_20261001/README_图内文字修订_20261001.md`.

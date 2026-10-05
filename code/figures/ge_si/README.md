# code/figures/ge_si/ — Supporting Information figures, and the published rasters

Companion to `code/figures/ge_main/`, which covers the four main-text figures.

This directory holds **two different things**, and they must not be confused:

| | What | Reproduces |
|---|---|---|
| `rebuild_fig1_2_9.py` + `figstyle.py` + `prep_out.json` | a script that rebuilds the Fig. S1 flowchart | the published **content**, in raster family A — *not* the published raster |
| `published/` | the rasters embedded in the submitted SI, plus the two pixel edits | the published **raster**, pixel for pixel |

## The rebuild script

```bash
cd code/figures/ge_si
python3 -c "import importlib.util as iu; s=iu.spec_from_file_location('r','rebuild_fig1_2_9.py'); m=iu.module_from_spec(s); s.loader.exec_module(m); m.figure2()"
# writes out/Figure2.png — 3188 x 3076
```

| Function | Produces | SI item |
|---|---|---|
| `figure2()` | `out/Figure2.png` | the flowchart submitted as **SI Fig. S1**, in family A |
| `figure1()` / `figure9()` | — | superseded ancestors of main Fig. 1 and the earlier Fig. 9; retained, not used |

## SI Fig. S1 — the box text was corrected on 2026-10-03

The figure submitted as Fig. S1 carries, in its "> 75 %" box:

> Above the genome-wide 95% band **(66.1–68.2 %)** – treat as robust

and, in its middle box, "Report the source-induced caveat". Until 2026-10-03 no file in this
archive printed those strings — the figure had been pixel-edited on 2026-10-01 — and the
script printed two different ones:

1. **A stale number.** The script printed `66.4–70.1 %`, taken from an earlier calibration
   (`scz_threshold_calibration.py`, N = 2,511, point estimate 68.26 %). The published value,
   `66.1–68.2 %`, is the one consistent with the rest of the submission: SI Fig. S1's own
   caption says *"calibrated against the PGC3 SCZ genome-wide benchmark (95 % band
   66.1–68.2 % around 67.2 %; 8,315 complete-case genes)"*, and Table S24 gives that arm as
   5,584/8,315 = 67.2 %, CI 66.1–68.2. Two different universes, and the larger one governs.
   **The published figure was right; the script was the stale side.**
2. **Different wording** in the middle box.

Both are corrected, so the script now prints the published text. That is a text fix, and it
does not make the script reproduce the published raster — see below.

## What is and is not reproducible

**Two raster families exist, and the divide is not noise.**

| Family | Size | Example | Produced by |
|---|---|---|---|
| A | 3188 × 3076 | `定稿补充图_FigS1-S5_20260915/.../_backup_before_600dpi_20260915_210047/FigS1.png` (441,493 B) | `rebuild_fig1_2_9.py` — this family |
| B | 3189 × 3077 | the four rasters in `published/` | **no script in this archive** — *(2026-10-05: family B is not a second drawing; it is family A's **PDF**, rasterised at 600 dpi — `pt / 72 * 600` = 3189.00 × 3076.80 → 3189 × 3077. Residual 2,044 px, 0.02 %. See `docs/audit_notes/gap4_figs1_render_path_20261005/`.)* |

Measured 2026-10-03 (full detail in `published/README.md`):

- **The script is faithful to its own family.** Its output differs from the historical
  `before_figure_text_sync_20260923/FigS1.png` (also 3188 × 3076) in **one contiguous band
  only**, y[2256,2387], 20,026 px — exactly the text that was intentionally changed. The
  other 2,965 rows are identical. There is no re-render noise in the script.
- **Across families, the difference is real.** On the published raster, FFT phase
  correlation gives an optimal translation of **(0, 0)** — not a crop, not a shift — yet
  after sub-pixel registration **2.6 %** of pixels still differ, distributed across **all
  twelve** text and box bands. That is the same vector artwork rasterised by a different
  renderer build (matplotlib/Agg + FreeType), not a content difference.
- **The gap is not recoverable from here.** Resampling, 1 px padding, three font families
  and twelve rasterisation settings were all tried; none changes the output size, and the
  best leaves 206,002 px differing. The original generator for family B was searched for
  across the disk and not found.

**So, precisely:**

- the published **raster** is reproducible at **artefact level** — `published/` ships it,
  names its SHA-256, and reproduces it from the pre-patch raster via two re-runnable edits
  (`verify_published.py`, all checks passing);
- the published **raster is not reproducible at script level** — re-running
  `rebuild_fig1_2_9.py` gives the published *content* in a different rasterisation.

Do not describe this directory as regenerating the published Fig. S1 from a script. If a
future edit is needed, edit the family-B original and re-run the pixel recipe, or replace
the figure outright — but the second option discards a verified 17,589 px edit and turns a
0.179 % change into a full re-render.

## Inputs

`prep_out.json` supplies the values the flowchart annotates; `figstyle.py` is the style
module this generation of scripts imports (the main figures use `figstyle_ge.py`). Both ship
here, so the script runs with no external input. `published/` needs nothing but Pillow,
NumPy and Arial (for `patch_figS1.py`).

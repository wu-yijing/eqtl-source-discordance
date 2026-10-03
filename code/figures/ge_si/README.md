# code/figures/ge_si/ — Supporting Information figures whose generator is a script

Companion to `code/figures/ge_main/`, which covers the four main-text figures.

```bash
cd code/figures/ge_si
python3 -c "import importlib.util as iu; s=iu.spec_from_file_location('r','rebuild_fig1_2_9.py'); m=iu.module_from_spec(s); s.loader.exec_module(m); m.figure2()"
# writes out/Figure2.png — the figure submitted as SI Fig. S1
```

| Function | Produces | SI item |
|---|---|---|
| `figure2()` | `out/Figure2.png` | **SI Fig. S1** — exploratory diagnostic scheme (flowchart) |
| `figure1()` / `figure9()` | — | superseded ancestors of main Fig. 1 and the earlier Fig. 9; retained, not used |

## SI Fig. S1 — the box text was corrected on 2026-10-03

The figure submitted as Fig. S1 carries, in its "> 75 %" box:

> Above the genome-wide 95% band **(66.1–68.2 %)** – treat as robust

That value, and the wording of the middle box ("Report the source-induced caveat"), do not
appear in **any** file in this archive: the figure was pixel-edited on 2026-10-01, and until
now no script produced it. Two separate problems were behind that:

1. **A stale number.** The script printed `66.4–70.1 %`, taken from an earlier calibration
   (`scz_threshold_calibration.py`, N = 2,511, point estimate 68.26 %). The published value,
   `66.1–68.2 %`, is the one consistent with the rest of the submission: SI Fig. S1's own
   caption says *"calibrated against the PGC3 SCZ genome-wide benchmark (95 % band
   66.1–68.2 % around 67.2 %; 8,315 complete-case genes)"*, and Table S24 gives that arm as
   5,584/8,315 = 67.2 %, CI 66.1–68.2. Two different universes, and the larger one governs.
2. **Different wording** in the middle box.

Both are now corrected in `rebuild_fig1_2_9.py`, so the script prints the published text.

## What is and is not reproducible

The regenerated figure is **3,188 × 3,076 px**; the copy embedded in the Supporting
Information is **3,189 × 3,077 px**. Text and layout match box for box. The rasters are not
byte-identical: about 2 % of pixels differ, distributed uniformly across the whole image
rather than concentrated in the two edited boxes — the signature of a re-render, not of a
local edit. **So the script now produces the published figure's content, but cannot
regenerate the published raster.** Anyone who wants the two to agree exactly should take
the regenerated figure, not the pixel-edited one.

## Inputs

`prep_out.json` supplies the values the flowchart annotates; `figstyle.py` is the style
module this generation of scripts imports (the main figures use `figstyle_ge.py`). Both ship
here, so the script runs with no external input.

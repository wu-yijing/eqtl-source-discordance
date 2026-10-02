# ⚠️ DEPRECATED — do not use to reproduce the manuscript

This directory was named `figure_scripts/` until **2026-09-20**, when it was renamed to
`_DEPRECATED_figure_scripts_pre20260917/`.

## Why it is deprecated

These five scripts (`Fig4_axis_decomposition.py`, `Fig5_candidate_dumbbell.py`,
`Fig6_fdr_enrichment_3panel.py`, `Fig7_rnh1_crosscohort.py`, `Fig8_crosstrait_3genesets.py`)
read the **pre-correction** data layer `data/processed/`. That layer was produced before two
implementation defects were fixed:

1. the S-PrediXcan statistic was missing the **σᵢ (expression-variance) factor**, and
2. the PLINK `.bed` **2-bit genotype decoding** was wrong.

Consequence: dense-model genes had systematically inflated |Z|, so **running these scripts
reproduces retired values that contradict the published figures and the manuscript**:

| Gene (eQTLGen, DR) | value these scripts produce | current value |
|---|---|---|
| RNH1 | 13.318 | **2.3064** |
| TUBB | 48.516 | **11.8932** |
| CKAP4 | 4.7549 | **0.9874** |

The 2026-09-14 Zenodo release shipped exactly these scripts alongside figures that had been
generated from this layer; the error was found on 2026-09-17 and every affected figure was
regenerated from the official MetaXcan v0.8.1 recompute.

## What to use instead

**`figure_scripts_officialZ_20260917/`** — the only pipeline that reproduces
`figures/Fig1–Fig8` and `figures/FigS1–FigS6`. Chain of provenance and the full
before/after value table are in that directory's `README.md`.

The pre-correction data layer is likewise quarantined: `data/processed/` carries a
`_DEPRECATED_勿用_修正前数据_20260917.md` notice; the authoritative layer is
`data/processed_officialZ/`.

This directory is retained **only for audit** (so that the earlier release can be
reproduced verbatim). It is not referenced by the current `README.md` figure-set section.

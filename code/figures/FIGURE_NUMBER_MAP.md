# FIGURE_NUMBER_MAP — old (pre-submission) numbering vs the current manuscript

**Why this file exists.** The figure scripts in this directory were written against an
**earlier 8-figure layout**. The current manuscript has **four** main figures and **four**
Supporting Information figures. Filenames such as `02_redraw_Fig3.py` therefore do **not**
refer to Fig. 3 of the submitted paper. Renaming the scripts is deliberately avoided: the
numbers are load-bearing for the pipeline's documented execution order and for the
regression assertions each script runs.

**Read this table before touching anything in this directory.**

## Main figures

| Script | Old number | **Current manuscript** | Content | Evidence |
|---|---|---|---|---|
| — (script not in this repository) | Fig. 1 | **Fig. 1** | Overview of the analytical framework (six modules) | `code/figures/README.md` §"未覆盖项" states the Fig. 1 script lives outside this directory |
| `02_redraw_Fig3.py` | Fig. 3 | **Fig. 2** | Cross-source agreement scatter, 96 gene–phenotype pairs; inset ρ = 0.39 with gene-cluster bootstrap CI, direction consistency 68.8% | Reproduces 68.8% and ρ = 0.3896 (this repo: 0.3898 by independent recompute); the manuscript's Fig. 2 caption quotes exactly those two quantities |
| `06_redraw_Fig4.py` | Fig. 4 | **Fig. 3** | Axis-resolved partition: (a) ρ with Fisher-z CIs for the three arms; (b) Δρ forest from a paired gene-cluster bootstrap, B = 5,000, seed 20260915 | The manuscript's Fig. 3 caption states B = 5,000 and seed 20260915 — matching `fig4_bootstrap_officialZ.json`, produced by this script |
| `04_redraw_Fig8.py` | Fig. 8 | **Fig. 4** | Cross-trait generalisation, three gene sets | Reproduces ρ = 0.414 (n = 138) / 0.636 (n = 72) / 0.418 (n = 8,890); the manuscript's Fig. 4 legend uses ρ = +0.4138/138, +0.6362/72, +0.4184/8890 |
| `01_redraw_Fig5_Fig7.py` | Fig. 5 + Fig. 7 | **not in the current manuscript** | Candidate-gene dumbbell; RNH1 cross-cohort | Retained for provenance and for any future revision |
| `08_redraw_Fig6_labels_20260920.py` | Fig. 6 | **not in the current manuscript** | FDR-enrichment three-panel figure | Retained; the enrichment result now appears as Table 1 and Supporting Information tables |
| `03_redraw_Fig6.py` | Fig. 6 | — | **Hard-deprecation guard.** Exits 1 by design. | Do not "fix" its exit code; do not remove it. |

## Supporting Information figures

| Script | Old number | **Current manuscript** | Content |
|---|---|---|---|
| — (not in this repository) | Fig. S1 | **Fig. S1** | Exploratory diagnostic scheme (flowchart) |
| — (not in this repository) | — | **Fig. S2** | eQTL SNP-count distribution across gene groups (violin) |
| `10_redraw_FigS6_20260921.py` | Fig. S6 | **Fig. S3** | Endpoint calibration and spike-in positive control |
| — (not in this repository) | — | **Fig. S4** | Silver-stain SDS–PAGE (wet-lab image) |

> The previous Fig. S2 (|Z| density) was deleted at revision; subsequent supplementary
> figures were renumbered, which is why Old-S6 now sits at position S3.

## Consequences to keep in mind

1. **Do not rename the scripts** to match the manuscript. The mapping belongs here, not in the filenames.
2. **Two scripts produce figures the current manuscript does not contain** (`01_redraw_Fig5_Fig7.py`, `08_redraw_Fig6_labels_20260920.py`). They are kept because a revision may ask for them, and because they document the earlier figure set. Their output must not be presented as part of the current submission.
3. **`code/figures/README.md` still describes the old order and still names `10_redraw_FigS6_20260920.py`.** Where the two conflict, this file governs for the Fig. S6 choice — `..._20260921.py` supersedes `..._20260920.py` (it adds the log-scale axis label, the two in-panel reference lines, upright mathematical symbols, and the n = 222 detection-boundary row).

## Open item — needs author confirmation

The authoritative README records that **Fig. 2 (old numbering; covariate-balance SMD plot)**
was produced by scripts outside this directory. It has **no counterpart in the current
manuscript**. Confirm whether that figure was dropped at revision or moved into the
Supporting Information; record the answer here.

---

*Compiled 2026-10-02 from `code/figures/README.md`, the current manuscript's figure legends,
internal consistency of the reproduced values, and the `fig4_bootstrap_officialZ.json` seed.*

# ⚠️ DEPRECATED — self-implemented SCZ TWAS estimator

This directory was named `scz_replication/` until **2026-09-20**, when it was renamed to
`_DEPRECATED_scz_self_implemented/`.

## Why it is deprecated

The TWAS Z-scores here are produced by the **in-house** estimator

```
Z = (w′R⁻¹z) / √(w′R⁻¹w)      # LD from 1000G EUR, ridge 0.1
```

The current manuscript recomputes every S-PrediXcan statistic — including the genome-wide
schizophrenia arm — with the **unmodified official MetaXcan v0.8.1 binary**. The archived,
authoritative SCZ Z-matrix is therefore

**`data/processed_officialZ/scz_z_4arm_official.csv`** (`gene`, `eqZ`, `wbZ`, `ntZ`, `multiZ`).

The two pipelines do not agree, and the difference is large enough to change the headline
numbers:

| Quantity | This directory (`results/`) | Current (`data/processed_officialZ/`) |
|---|---|---|
| Complete-case denominator | 2,511 genes | **8,315** genes (pool 10,357) |
| Panel-only analogue (eQTLGen vs GTEx Whole_Blood) | *not computed here* | **ρ = +0.469** |
| Tissue-only analogue (GTEx Whole_Blood vs Nerve_Tibial) | ρ = 0.509 (71.21% concordant) | **ρ = +0.420** (66.8%) |
| Dual analogue (eQTLGen vs GTEx multi-tissue) — the "source axis" of the old 2×2 | ρ = 0.522 (68.26% concordant) | **ρ = +0.447** (66.2%) |
| Reversal rate, dual arm | 31.7% | **33.8%** |

`results/scz_twas_results_limit0.csv` is the per-gene TWAS Z of that earlier run; it is **not** the
per-gene Z behind any current table or figure.

## What to use instead

| Need | Use |
|---|---|
| SCZ per-gene Z, four arms | `data/processed_officialZ/scz_z_4arm_official.csv` |
| SCZ arm correlations, denominators, axis contrast | Additional file 1 — Table S15 (and Fig. 8) |
| Cluster-aware uncertainty of the primary (HOTAIR) arm | Additional file 1 — Table S16 |
| Summary of the current SCZ numbers | `README.md` → *SCZ 2×2 Decomposition Replication* |

## What is retained, and why

The scripts are kept **only for audit**: they document how the 2×2 decomposition was originally
built (`scz_twas.py` TWAS + decomposition; `build_weights_db.py` weight DB; `robustness_scz.py`
sparsity-stratified robustness; `scz_axis_difference_analysis.py` and
`scz_threshold_calibration.py` later refinements; `hk_replication_analysis.py`,
`make_fdr_ci_figures.py`, `make_replication_figure.py` side analyses; `make_figure9_scz.py` and
`make_robustness_fig.py` the iScience-era figure scripts, which write to a
`submission_iScience_v2/figures/` path that is **not tracked in this repository**;
`patch_manuscript_scz.py` / `patch_robustness.py` manuscript write-back helpers).

`m7_effect_size_supplement.json` is the frozen output of the corresponding script under
`scripts/python/` and describes the same generation.

**Do not run these scripts to reproduce the paper.** The in-repository path literals inside them
were updated on 2026-09-20 to follow this rename (18 literals across six files). Six literals across
four files point *outside* this repository and are left exactly as recorded, because they name the
2026-07/08 session directories in which the scripts were originally run and those directories are not
part of this repository: `E:/workbuddy/2026-07-15-20-17-22/scz_replication` (`hk_replication_analysis.py`,
`make_replication_figure.py`; one literal each) and
`E:/workbuddy/BMC Genomics投稿资料/TWAS-repo/scz_replication/results`
(`scz_axis_difference_analysis.py`, `scz_threshold_calibration.py`; two literals each). Every one of
these scripts still reads `data/processed/` (the pre-correction layer) and will reproduce retired
values.

The `note` field inside `m7_effect_size_supplement.json` (both here and in `data/processed/`) keeps
the original `scz_replication/results/*.json` wording on purpose: it is a frozen record of how that
file was produced on 2026-08-09, not a live path.

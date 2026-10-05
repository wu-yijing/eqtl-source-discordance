# `code/figures/recovered/` — the surviving generators of Fig. S1 and Fig. S2

Two figure scripts were believed lost: `figures/README.md` listed **Fig. S1** (diagnostic-scheme
flowchart) and **Fig. S2** (eQTLGen model-SNP-count violin) among the four figures with "no producing
script in this archive or either predecessor". Both were **recovered on 2026-10-03** from local
working directories that are not archived, and are shipped here verbatim.

They are shipped *verbatim* — absolute paths, `figstyle`/`prep_out.json` dependencies and all — because
that is the evidence. **One exception, made on 2026-10-05:** `gen_figs4.py` had its three hard-coded
2026-09 absolute paths replaced by a repository-relative lookup, so that **Fig. S2 is now runnable
from a clone** and wired into `code/run_all.sh` (which asserts its three published medians). Its
figure-producing logic is unchanged; the recovered copy is preserved by its SHA-256 in the provenance
table below. `rebuild_fig1_2_9.py` remains verbatim and is **not** wired into `code/run_all.sh`.

| File | Produces | Manuscript item |
|---|---|---|
| `rebuild_fig1_2_9.py` | `figure1()` — the six-module analytical framework; `figure2()` — the direction-consistency **flowchart**; `figure9()` — the cross-trait generalisation bar chart | main **Fig. 1**, **Fig. S1**, and the BMC-era Fig. 9 |
| `gen_figs4.py` | the eQTLGen **model-SNP-count violin** by gene group | **Fig. S2** |

## Provenance

| File | Recovered from | Revision taken |
|---|---|---|
| `rebuild_fig1_2_9.py` | `E:\workbuddy\2026-10-01-11-18-06\_fig\rebuild\rebuild_fig1_2_9.py` | 2026-10-01 (newest of three copies; the others are dated 2026-09-11) |
| `gen_figs4.py` | `E:\workbuddy\2026-09-14-22-57-53\review\gen_figs4.py` | 2026-09-14 (newest of two copies; 600 dpi + RGB conversion, added 2026-09-20) |

The byte-identical second copies, for cross-reference:
`E:\workbuddy\BMC Genomics投稿资料\_图件格式批次备份_20260920\scripts_figs4_fig1\{rebuild_fig1_2_9.py, gen_figs4.py}`.

## What each script reads

* `gen_figs4.py` reads `data/processed/eqtlgen_spredixcan_harmonized_results.csv` from the predecessor
  working tree. **That file ships here** — the same table is `data/superseded/eqtlgen_spredixcan_harmonized_results.csv`. Its
  universe is the harmonized eQTLGen arm — 61 genes carrying a valid S-PrediXcan Z **and** a numeric
  model-SNP count — which is exactly the **24/24/13** gene split the published Fig. S2 prints
  (median 374 / 632 / 669 SNPs).
* `rebuild_fig1_2_9.py` reads `figstyle.py` and `prep_out.json` from the predecessor build root and,
  for `figure2()`, no data at all — the flowchart is drawn from literals. Only the two `.png` figure
  boxes it also patches need the images.

## Divergence from the published figures — read this before regenerating

Neither script reproduces the published image byte for byte, and the reason is documented rather than
guessed:

* **The published Fig. S1 was pixel-edited, not re-run.** On 2026-10-01 the middle box was rewritten
  in place from `Source-induced caveat required` to `Report the source-induced caveat` — recorded,
  with the exact erase/redraw rectangle, in
  `E:\workbuddy\GE投稿资料\_修订_20260930\_图件修订_20261001\README_图内文字修订_20261001.md`. That same
  record states plainly that a full-disk search for an SI figure-generating script returned **nothing**
  (`FancyBboxPatch`, `violinplot`, `Source-induced caveat` and other signatures all missed) — which is
  why the edit was pixel-level.
* **The `> 75 %` box text does not match either.** Every surviving copy of the flowchart writes
  `Above the genome-wide 95% band (66.4-70.1%)`; the published Supporting Information prints
  `Above the genome-wide 95% band (66.1-68.2%)`. The band is computed by
  `scz_threshold_calibration.py` (N = 2,511; point estimate 68.26 %). **The script is therefore the
  ancestor, not the exact generator** of the published box, and a re-run will reproduce the *structure*
  but not that string.

So: **Fig. S2 is reproduced by `gen_figs4.py`** (same universe, same three medians). **Fig. S1 is
reproduced only structurally** — its published text carries an edit whose exact provenance is not on
disk. `figures/README.md` states which of the two is which.

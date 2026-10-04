# data/superseded/ — the pre-correction layer. Read this before using anything here.

**Origin.** These files were produced by an earlier in-house S-PrediXcan implementation with two
defects: a missing σᵢ expression-variance factor, and a PLINK 2-bit decoding error. Both
systematically inflated |Z| for densely modelled genes. The defects are disclosed in the
manuscript's Methods.

| Gene (eQTLGen, DR) | Value in this directory | Official MetaXcan v0.8.1 |
|---|---|---|
| TUBB | 48.52 | 11.89 |
| RNH1 | 13.32 | 2.31 |
| CKAP4 | 4.75 | 0.99 |
| RNH1 (GTEx Nerve_Tibial, DR) | 13.82 | 2.67 |

**Default rule: do not quote any number from this directory.** Values here disagree with the
manuscript's figures and text. The authoritative layer is [`../derived/`](../derived/).

---

## The exceptions — files here that ARE still used

Two kinds of content in this directory remain valid, and saying so precisely is the point of
this file. **Treating the whole directory as unusable is as wrong as treating all of it as current.**

| File | Why it is still usable |
|---|---|
| `mahalanobis_matched_pairs.csv` | Contains **covariates only** (gene length, GC content, eQTL SNP count, matched subclass). The two defects act on the *Z-score* computation and cannot propagate to covariates, so every covariate value here is still the one the manuscript reports. **Its 30 pairs, however, are the pre-correction pairing and no longer the reported one** (2026-10-04): the `subclass` column is the rank order of two lists each sorted by `PullDown_Unused` descending, not a matching output. The **control set** it records *is* what the documented specification selects — 30 of 30 — and Supporting Information Table S4 now carries the re-emitted pairing, shipped at [`../derived/mahalanobis_matched_pairs.csv`](../derived/mahalanobis_matched_pairs.csv). This file remains an input to the matched enrichment contrasts (Table S26); S26 is unaffected because both pairings select the same 30 controls. Full account: [`../../docs/audit_notes/s4_specification_sweep_20261004/`](../../docs/audit_notes/s4_specification_sweep_20261004/README.md). |
| `gtex_acat_o_results.csv`, `gtex_stouffer_integrated.csv` | The "archived working table" retained as the **equivalence cross-check** between the in-house implementation and the official binary. Referenced in Supporting Information Table S10. Maximum residual difference from the official binary: \|ΔZ\| = 3 × 10⁻⁸. **Never quote these as headline values** — they exist only to demonstrate the two implementations agree. |
| `m6_ne_weighted_sensitivity_results.txt`, `m7_effect_size_supplement.json` | Outputs of analyses that are part of the current pipeline (scripts kept at `code/analyses/m6_ne_weighted_sensitivity.py` and `code/analyses/m7_effect_size_supplement.py`). Their placement here reflects the old directory layout, not their status. |
| `enrichment_comparison.csv` | Superseded values, **but** `code/deprecated/python_early/` reads it. Kept so that the deprecated scripts remain runnable for audit purposes. |

## Files that are straightforwardly superseded

`candidate_comparison_DR.csv`, `covariate_matrix.csv`, `enrichment_comparison_harmonized.csv`,
`enrichment_comparison_BACKUP_before_candidate_fix.csv`, `eqtlgen_DR_pergene_FDR.csv`,
`eqtlgen_spredixcan_results.csv`, `eqtlgen_spredixcan_harmonized_results.csv`,
`eqtlgen_vs_gtex_comparison.csv`, `gtex_Nerve_Tibial_{DR,DN,DPN}.csv`,
`gtex_Whole_Blood_{DR,DN,DPN}.csv`, `layer_analysis.csv`, `viz_z_distribution.csv`.

## Other files here

| File | Note |
|---|---|
| `gigadb_metadata_form.csv` | For the **GigaDB** submission route, which was abandoned. No longer referenced anywhere. |
| `ukb_dr_official/` | **Moved out.** It was the authoritative official-MetaXcan UK Biobank cross-cohort arm and never belonged in this layer. Now at `../derived/ukb_dr/`. |
| `hk_reselect_20260830/` | **Moved in 2026-10-02.** The housekeeping Z layer, computed 2026-08-30 — before the 2026-09-17 σᵢ correction. Its values match the Supporting Information's Table S6 as it stood up to 2026-09-16 22:24, and are superseded by the values published from 2026-09-17 19:15 onward. Full evidence and the still-unresolved 8-gene anomaly: [`hk_reselect_20260830/PRECORRECTION_NOTICE.md`](hk_reselect_20260830/PRECORRECTION_NOTICE.md). |
| `_DEPRECATED_勿用_修正前数据_20260917.md`, `_WARNING_陈旧文件说明.md` | The original deprecation notices, retained as written. |

---

## Enforcement

- `code/run_all.sh` reads only `data/derived/` and refuses to proceed if a figure script references this directory.
- `code/figures/paths_config.py` exposes this path only as `FORBIDDEN`, so scripts can assert they are *not* reading it.
- No script in the supported pipeline has this directory as an input.

---

*Written 2026-10-02. The previous repository labelled this directory `data/processed/` and relied on two ad-hoc notice files inside it; the classification above is the first complete statement of what is and is not still usable.*

---

## Addendum 2026-10-02 — `s1_cluster_robustness/`

Two per-pair tables were **moved out of `data/derived/` and into this directory** after their values
were compared with the authoritative table:

| File | Value at ANXA1/DR | Generation |
|---|---|---|
| `data/derived/primary_arm_96pairs.csv` (authoritative) | 0.4283 / 0.9302 | official MetaXcan v0.8.1 |
| `s1_cluster_robustness/s1_primary_arm_96pairs.csv` | 1.2913 / 2.1391 | **v2.5.0 generation** |
| `s1_cluster_robustness/s1_anchor_102pairs.csv` | 1.2913 / 2.1391 | **v2.5.0 generation** |

The directory's own README states that its numbers were computed on this pre-correction layer and
that its code is **not** the script set behind the values the manuscript now reports. Their row
counts (96 and 102) are superficially similar to the authoritative table, which is exactly why they
were mis-filed in the first place — **compare values, not row counts.**

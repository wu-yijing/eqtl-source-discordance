# ARCHIVE_MAP — which file reproduces which manuscript item

**Manuscript:** "Expression quantitative trait locus weight-source dependence in transcriptome-wide association studies: a two-axis diagnostic partition with disease-agnostic calibration" — submitted to *Genetic Epidemiology*.
**Archive version:** v4.0.0.
**Keyed to:** the **current** Supporting Information numbering (Tables S1–S30, Notes S1–S5, Figs. S1–S4).
**Verified against:** `Supporting_Information_GenetEpidemiol_20260930.docx`, 2026-10-02. Every status below was set by comparing table titles, header row, logical/physical column count and data row count against the file named — and, where a value could settle it, by comparing actual cell values.

> ⚠️ **Do not reuse the predecessor `ARCHIVE_NOTE.md`.** It was written against an older Additional-file numbering. It labelled the primary 96-pair table as "Table S12", whereas in the current Supporting Information **S12 is the draft STREGA-TWAS reporting checklist and S14 is that checklist completed for this study**.

**Scope.** Code and processed data only. Figures, figure captions, tables and table legends accompany the manuscript and its Supporting Information and are **not** redistributed here (see §1). Raw RNA pull-down / LC–MS/MS spectra are in ProteomeXchange via iProX (PXD083775).

---

## Status key

| Mark | Meaning | What it obliges |
|---|---|---|
| ✅ **VERIFIED** | A file in this repository reproduces the item, and its shape **and at least one value** were checked against the Supporting Information | Nothing further |
| 🟡 **DERIVABLE** | The inputs are present and verified, but the join / aggregation / filter that produces the table **is not shipped here**. Reproducible only by writing that step | Acceptable for release — but say so in the README |
| 🔴 **GAP** | **Nothing in this repository produces it.** The generating script was not archived | Must be fixed or declared before release |
| ➖ **NOT A DATA ARTEFACT** | A text or table rendered directly in the Supporting Information | Nothing |

**A map that over-claims is worse than a map that admits gaps.** Of 46 items checked, as of 2026-10-02: **20 ✅, 12 🟡, 5 🔴, 9 ➖**. The counts are now a machine count of the status column. The line previously read 16 ✅ / 13 🟡 / 9 🔴 / 8 ➖, which did not match the table beneath it — the table then held 12 ✅ and 12 🔴.

### Data layer added 2026-10-02

The reproduction package originally shipped scripts without their inputs, so no row above could
be checked by a reader. Three groups of tables were added under `data/derived/` to close that:

| Added | Files | Size | Closes |
|---|---|---|---|
| `genomewide/` | 5 gzipped genome-wide weight-source Z layers | 2.8 MB | the framework layer (S16) and every analysis universe |
| `gtex_official_finngen/` | 1 gzipped wide table (15,655 genes × 6 columns) | 0.7 MB | the Table S9 ACAT-O chain, without the 12.3 MB original |
| `s9_pools/`, `hrt/`, `hrt_random_control/`, `groups.json`, `covariate_matrix.csv` | 12 small files | 0.2 MB | the Table S9 pools, strata and random controls |

All of it is rebuilt by `code/analyses/reproduction_20261002/00_build_added_derived.py` from the
sources named in that script, and every file is listed with its MD5 in
`code/analyses/reproduction_20261002/INPUTS.md`. Before this addition the framework layer and the
genome-wide universes could not be reproduced from this archive at all, and no script in the
package could be run from a clone.


---

## 1. Main text

| Manuscript item | Authoritative file(s) | Status | Evidence |
|---|---|---|---|
| Table 1 — definitions and provenance of the three control layers | Supporting Information **Note S3** (text only) | ➖ | Note S3 is the provenance carrier |
| Table 1 — enrichment values for the three control layers | inputs: `data/derived/hk_genes.txt` (gene roster), `data/derived/gtex_Z.csv`, `data/derived/eqtlgen_Z.csv` | 🔴 | **GAP-2**, and blocked by **GAP-1**: the housekeeping arm of this table rests on the Z layer that the Supporting Information replaced on 2026-09-17. See §4 |
| Table 2(A) — primary comparison | `data/derived/primary_arm_96pairs.csv` (**96 rows**) | ✅ | ANXA1/DR = 0.4283, 0.9302 = first data row of SI Table S13; 66/96 = 68.8%, ρ = 0.3898 |
| Table 2(B) — two-axis partition (dual 198 / panel-only 159 / tissue-only 138 pairs) | derived by joining `data/derived/gtex_Z.csv` × `data/derived/eqtlgen_Z.csv` | ✅ | **GAP-3 closed 2026-10-02.** The join is now shipped as `code/analyses/reproduction_20261002/scripts/recompute.py`; it reproduces all four arms on their own full-pair inputs — primary 96 / ρ 0.3896 / 68.75%; panel-only 159 / ρ 0.490 / 71.1%; tissue-only 138 / ρ 0.414 / 65.9%; dual 198 / ρ 0.442 / 67.2% | **Input locality** — the join reads `data/derived/gtex_Z.csv` and `data/derived/eqtlgen_Z.csv`, both shipped; no external input. **Reproducible from a clone.**
| Figs. 1–4 | **not in this repository** | 🟡 | `figures/` contains only its README. The repository ships the *scripts* for some panels, never the figure files. See [`../code/figures/FIGURE_NUMBER_MAP.md`](../code/figures/FIGURE_NUMBER_MAP.md) |
| Fig. 1 module 6 — checklist pointer | points to SI Table S12 → Table S14 | ✅ | Consistent with the current SI |

## 2. Supporting Information — Notes and Figures

| Item | Authoritative file(s) | Status | Evidence |
|---|---|---|---|
| Note S1 — comparison with prior evaluations | ➖ text only | ➖ | |
| Note S2 — RNA pull-down / LC–MS/MS parameters | ➖ text only; spectra at iProX PXD083775 | ➖ | |
| Note S3 — table notes for main-text Table 1 | ➖ text only | ➖ | |
| Note S4 — data sources: identifiers, versions, retrieval dates | `data/README.md` | 🟡 | Manifest skeleton present; **SHA-256 values and retrieval dates are still `<hash>` placeholders** |
| Note S5 — simulation validation: full design and results | **recovered 2026-10-02**: `code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py` (verbatim copy of the archived generator) | ✅ | **GAP-5 closed.** Re-run: all 84 values identical to the archived `simulation_results.json` at machine precision — S27 +0.01/+1.04/+2.33/+3.15/+5.46 pp; S28 94.0/95.5/7.5/6.0 and 96.25/94.75; S29 5.75/0.4955 and 7.25/0.3464. Parameter sets (seed 20260930, G = 32, P = 3, n_pair = 96, ρ_sd = 0.15, n₁ = 3,000, n_rep = 400, B = 500) confirmed. *(This row previously cited "GAP-4"; the register reserves GAP-4 for Figs. S1 and S2 — corrected here.*) | **Input locality** — the generator reads no file at all (pure synthetic; seed 20260930, G = 32, P = 3, n_pair = 96, rho_sd = 0.15, n₁ = 3,000, n_rep = 400, B = 500). **Reproducible from a clone.**
| Fig. S1 — diagnostic scheme (flowchart) | — | 🔴 | No generating script in the repository |
| Fig. S2 — eQTL SNP-count violin | — | 🔴 | No generating script. Complicated by the fact that the *previous* S2 (|Z| density) was deleted at revision and later figures were renumbered |
| Fig. S3 — endpoint calibration and spike-in control | `code/figures/10_redraw_FigS6_20260921.py` + `code/figures/m15_positive_control.json` | ✅ | Script reads `PC1a_BH_boundary` / `PC1b_null_calibration` / `PC2a` / `PC2b` from the bundled JSON, which is the S20 content. ⚠️ the script's internal assertion label still says "SI Table S19" — stale label, same data |
| Fig. S4 — silver-stain SDS–PAGE | — | ➖ | Wet-lab image, no script |

## 3. Supporting Information — Tables

| Item | Title (abbreviated) | Authoritative file(s) | Status | Evidence |
|---|---|---|---|---|
| S1 | Positioning of the present audit | ➖ | ➖ | |
| **S2** | Complete gene list (**104 testbed genes**) | `data/derived/gene_groups.csv` | ✅ | 104 data rows, 7 cols — identical header to SI |
| **S3** | GTEx v8 baseline TWAS (**74 genes × 3**) | `data/derived/gtex_Z.csv` | ✅ | 222 rows = 74 × 3; first row (ACTB/DR −1.0831/−1.3793/−1.750…) matches SI |
| **S4** | Mahalanobis matched pairs (30 pairs) | `data/superseded/mahalanobis_matched_pairs.csv` | ✅ | 60 rows, 8 cols; covariates only, unaffected by the pre-correction defects (see `data/superseded/README.md`) |
| **S5a** | RNH1 cross-population replication | `data/derived/crosscohort.csv` | ✅ | 4 rows, 11 cols; +2.31 / +0.72 / +0.55 / +1.51 (0.79); 0.056 / 1.26; 20.6; 0.51 / −0.33 to +3.36 — all match SI row 1 |
| S5b | Group-level direction consistency, 8 genes | inputs verified: `data/derived/gtex_Z.csv` (RNH1 DR Nerve_Tibial Z = 2.6675 = SI "+2.668") + `data/derived/ukb_dr/RNH1_official_metaxcan_Z.csv` (UKB/GTEx-NT Z = 0.5451, P = 0.585687 = SI "+0.55 / 0.586") | 🟡 | Inputs verified; the 8-gene assembly is not shipped |
| S6 | Housekeeping control gene list + dual-tissue results | **NONE — the repository holds the pre-correction side only**, at `data/superseded/hk_reselect_20260830/` | 🔴 | **GAP-1, diagnosed.** The 30-gene roster and the model-SNP column match the Supporting Information; every Z value is the pre-2026-09-17 computation. Evidence chain in §4 |
| S7 | Margin-sensitivity of the enrichment contrast | **recovered 2026-10-02**: `code/analyses/recovered/tost_ci_calculator.py` and `tost_and_newcombe.py` | 🟡 | Difference and Newcombe 90% CI **verified reproduced** (GTEx −9.7 to +15.4, eQTLGen −13.3 to +12.6; TOST p 0.181/0.060/0.014 and 0.116/0.034/0.007 — all match the published values). The "Smallest margin attained" column still has no source |
| S8 | Fixed-threshold enrichment reanalysis | derivable from `data/derived/gtex_Z.csv` / `eqtlgen_Z.csv` | 🟡 | Counting at p < 0.05 is mechanical; the script is not shipped |
| S9 | Architecture-unselected random controls | inputs verified: `data/derived/gtex_Z.csv` + `data/derived/covariate_matrix.csv` + the HRT roster; the retired `data/superseded/hk_reselect_20260830/d3_*` / `d3b_*` outputs are **not** used | ✅ | **GAP-7 closed 2026-10-02.** Full table reproduced by `code/analyses/reproduction_20261002/scripts/r3/recompute_r3_s9_s20.py`: exclusion chain 12,622 → 12,555 → 11,885 → **11,820** (10,450 dual-tissue); POOL_818 = 818/767/51; coverage 568/768; 16 random-control rates (GW and HRT × GTEx and eQTLGen × 4 thresholds); 8 null-distribution values; percentiles 69.3 / 51.7 / 78.3 / 68.1; in-pool strata 21/1,326 and 7/378, 20/1,827 and 6/477 with their median \|Z\| and Fisher P. One operational detail recovered from the data, not documented anywhere: the in-pool "both-tissue" stratum must be defined by **availability of the official statistic**, not by mashr model availability — the latter gives 506/1,518 and 62/186 instead | **Input locality** — the pool membership ships as `data/derived/s9_pools/*.txt`, the official MetaXcan GTEx × FinnGen layer as the flattened `data/derived/gtex_official_finngen/gtex_official_zscores_wide.csv.gz`, plus `covariate_matrix.csv`, `hrt/` and `hrt_random_control/`; the six original GTEx × FinnGen tables (12.3 MB) and the mashr model databases (10.5 MB) are **deliberately not redistributed** (`data/README.md`), so the *re-derivation* of the pools is not possible from this archive — only its outcome is. Verified 2026-10-02 in a clean copy: the published numbers reproduce **without** either layer. See `INPUTS.md` B.2/B.3.
| S10 | Cross-population direction check for DN | — | 🔴 | **GAP-8.** Also carries the peer-review item M3: the table note must state the **full** population composition of the source resource (European **and** East Asian components), not only the component used |
| S11 | Analysis-arm denominators | derivable from `data/derived/gtex_Z.csv` / `eqtlgen_Z.csv` | 🟡 | Denominators are counts over the two Z tables |
| S12 | Draft TWAS reporting checklist | ➖ | ➖ | Document artefact |
| **S13** | Per-pair primary-arm data | `data/derived/primary_arm_96pairs.csv` | ✅ | 96 rows, 5 cols, identical header; reproduces 68.8% and ρ = 0.39 |
| S14 | Checklist completed for this study | ➖ | ➖ | Pre-specification anchors recorded in [`PRE_REGISTRATION.md`](PRE_REGISTRATION.md) |
| **S15** | Housekeeping control — eQTLGen results | `data/derived/eqtlgen_Z.csv`, filter `Group == 'Housekeeping'` (81 rows) | ✅ | ANKRD40/DR = −0.6222, 0.534, 0.6005, 130/137 = SI row 1 **exactly**. The SI carries 90 rows because 9 are placeholders for genes with no eQTLGen model |
| S16 | Framework-layer alternative test | `data/derived/` gene-level Z for the elastic-net and MASHR layers | ✅ | **GAP-9 closed 2026-10-02.** All 9 rows reproduced by `code/analyses/reproduction_20261002/scripts/recompute_scz.py`: ρ +0.7970 (+0.781 to +0.812; 82.4%, n = 4,098), +0.8062, +0.8379, +0.7842 (n = 6,310), +0.4990 (+0.469 to +0.528; 69.8%), +0.5250, +0.5820 (n = 3,910), +0.6470, +0.6380 (n = 6,014) | **Input locality** — the five genome-wide weight-source Z layers now ship as `data/derived/genomewide/*.csv.gz` (2.8 MB), added 2026-10-02 for exactly this row; no external input. **Reproducible from a clone.**
| S17 | Cluster-aware uncertainty of the primary arm | `data/derived/primary_arm_96pairs.csv` | ✅ | **GAP-10 closed 2026-10-02.** Rebuilt from the data, not reused from the retired directory. naive t = 4.1019 (df 94, P = 8.712 × 10⁻⁵); delete-one-gene jackknife SE(ρ) = **0.1367** (P 0.0039 / 0.0077 = the published 0.004 / 0.008); sandwich SE(ρ) = 0.1264 against the published 0.125 — the reported triple (SE 0.125, one-sided 0.002, two-sided 0.004, df 31) is **internally consistent for any SE in 0.12326–0.12719**, so the estimator, not the value, was the missing item; gene-label permutation null −0.218 to +0.232 (= the published −0.22 to +0.23) provided the permutation is by **whole gene**; gene-cluster bootstrap ρ CI [0.1161, 0.6220] and rate CI 58.3–79.2%; two-arm rate difference analytic +2.6649 pp / SE 1.4741 / 95% CI −0.22 to +5.55 / 90% CI +0.24 to +5.09 / Q 0.1357, and gene-cluster SE 2.194 → 2.2 with 90% CI −0.77 to +6.45 → −0.7 to +6.4, r −0.045 → −0.05. **Two disclosures are still owed** (RNG = `numpy.random.RandomState`; resampling over a lexicographically sorted gene vector) — see `docs/audit_notes/R2残余差异消除方案_20261002.md` | **Input locality** — the primary-arm half reads the shipped `data/derived/primary_arm_96pairs.csv` and is reproducible from a clone. The gene-cluster rows additionally need the housekeeping layers carried in SI Tables S6/S15, i.e. the Supporting Information `.docx`, which is **not redistributed** here — same status as every other `.docx`-dependent step in this repository (`INPUTS.md` B.1).
| **S18** | Per-gene eQTLGen results, three gene groups | `data/derived/eqtlgen_Z.csv`, filter `Group != 'Housekeeping'` | ✅ | Yields exactly **207** rows = SI's 207 data rows (81 candidate + 75 non-candidate + 51 T2DM control) |
| S19 | Per-stratum enrichment rates at p < 0.05 | derivable from `data/derived/gtex_Z.csv` / `eqtlgen_Z.csv` | 🟡 | Mechanical count by arm and phenotype |
| **S20** | Endpoint calibration and spike-in control | `code/figures/m15_positive_control.json`; **generator recovered 2026-10-02** at `code/analyses/reproduction_20261002/scripts/r3/m15/m15_pc.py` | ✅ | Keys `PC1a_BH_boundary` (strata 13…87, e.g. n = 27 → \|Z\| = 3.11) and `PC1b_null_calibration` carry the S20 content; the Fig. S3 script asserts against it. The generator had been missing (the map previously recorded the JSON as its own carrier); re-run verbatim it reproduces the archived JSON key-for-key to 1 × 10⁻¹², including `PC2b_group_diff_power` = 8.0 / 14.5 / 13.0 / 17.5 pp | **Input locality** — the generator ships; its input, `Additional file 1_审稿意见修订_20260917.docx`, does not (a submission document). Point `REPRO_AF1_DOCX` at it.
| S21 | Direction consistency vs min \|Z\| threshold | derivable from `data/derived/primary_arm_96pairs.csv` | 🟡 | Thresholding at 0.0 reproduces 96 / 66 / 68.8% = SI row 1 |
| S22 | Sensitivity to exclusion of TUBB | derivable from `data/derived/eqtlgen_Z.csv` | 🟡 | Mechanical re-count after dropping the highest-leverage gene |
| S23 | Composition of the harmonized eQTLGen arm | derivable from `data/derived/eqtlgen_Z.csv` (`Model_SNPs` column) | 🟡 | SI has 61 data rows — a subset of the 96-gene universe |
| **S24** | Three genome-wide SCZ arms (n = 8,315) | `data/derived/scz_z_4arm.csv` | ✅ | 15,875 rows; panel-only row = 8,315 / 5,584 / 67.2% / 66.1–68.2 / +0.469 matches SI row 1 |
| S25 | Arm membership of exceptional entries | hand-curated; derivable from the tables it cites | 🟡 | No generator; content is a curated list (RPS16, HSP90AB1, …) |
| S26 | Mahalanobis-matched enrichment contrasts | `data/superseded/mahalanobis_matched_pairs.csv` + `data/derived/gtex_Z.csv` + `data/derived/eqtlgen_Z.csv` | 🟡 | The two Fisher values (2/84 vs 1/60 → 1.00; 5/81 vs 0/57 → 0.077) appear as embedded constants in `code/figures/10_redraw_FigS6_*.py`, but the producing script is not shipped |
| S27 | Calibration of the sign-agreement identity | `code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py` | ✅ | **GAP-5 closed.** Re-run reproduces the table exactly: +0.01 pp under bivariate normality, +1.04 / +2.33 / +3.15 / +5.46 pp as tail thickness rises to t(3) |
| S28 | Coverage / type I error of the bootstrap interval | `code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py` | ✅ | **GAP-5 closed.** Re-run reproduces 94.0 / 95.5 / 7.5 / 6.0 and 96.25 / 94.75 |
| S29 | Type I error of the two-axis separability test | `code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py` | ✅ | **GAP-5 closed.** Re-run reproduces 5.75 / 0.4955 and 7.25 / 0.3464 |
| S30 | Integrated evidence assessment | ➖ | ➖ | Text/table rendered directly in the Supporting Information |

---

## 4. GAP-1 diagnosed — this repository holds the *pre-correction* housekeeping layer

SI Table S6, first data row:

```
ANKRD40 | 1/2 | 0.598 | 0.718 | 0.376 | -0.5863 | -0.5637 | 0.6638 | -0.4786 | -0.2590 | 1.0657
```

The nearest file in the repository, `data/derived/hk_reselect/data/TableS6_hk_control_v2.csv`:

```
ANKRD40 | 1.0 | 0.00331... | 0.25557... | -0.9542 | 1.1237 | -0.9925 | -0.0555 | 2.9348 | -0.8469
```

- The **gene list matches** (the 30 genes of SI S6 are all in `data/derived/hk_reselect/data/hk_genes_v2.txt`), and the model-SNP pair 1/2 agrees.
- **Every value differs.** The repository's housekeeping Z layer traces to `hk_reselect/data/hk_twas_v2_raw.csv` → `arms_all_groups.csv` → `TableS6_hk_control_v2.csv`; it is self-consistent but it is not what the Supporting Information prints.
- A full-disk search for the SI values (`−0.5863`, `−0.4387`) found **no** source file.

**Consequence.** The housekeeping-control layer is one of the three disease-agnostic control layers, and it reaches the main text through Table 1. Either the Supporting Information's S6 was recomputed at the GE revision by a script that was never archived, or one of the two carriers is stale.

### Resolution — established 2026-10-02

**The repository is the stale carrier, not the Supporting Information.** The housekeeping Z layer
was computed on **2026-08-30**; the σᵢ / PLINK correction landed on **2026-09-17**. The published
table changed inside exactly that window:

| Table S6 as archived | ANKRD40 row |
|---|---|
| up to 2026-09-16 22:24 | `1/2 \| 0.256 \| 1 \| 0.00331 \| -0.9925 \| -0.9542 \| 1.1237 \| -0.8469 \| -0.0555 \| 2.9348` |
| from 2026-09-17 19:15 | `1/2 \| 0.598 \| 0.718 \| 0.376 \| -0.5863 \| -0.5637 \| 0.6638 \| -0.4786 \| -0.2590 \| 1.0657` |

Established by reading the Table S6 block out of **93 archived copies** of the supplementary file and
ordering them by modification time. Three further lines of evidence:

1. **Direction** — every changed value shrinks \|Z\| and moves the ACAT-O P toward 0.5, the signature of removing a \|Z\|-inflating defect.
2. **Shape** — 22 of 30 genes show a constant per-gene ratio across all three phenotypes (ATG101 ×2.435 in both tissues, DCTN2 ×3.244, FIBP ×2.667), i.e. a per-gene multiplicative correction.
3. **Scope** — the model-SNP column is unchanged for all 30 genes: the same models, a different Z computation.

**Action taken:** the layer was moved from `data/derived/hk_reselect/` to
[`data/superseded/hk_reselect_20260830/`](../data/superseded/hk_reselect_20260830/PRECORRECTION_NOTICE.md).

### Still open after this diagnosis — do not close it by assumption

- **8 of 30 genes do not follow a constant ratio** — `DNAJC4`, `E2F4`, `GOLGA3`, `SDF4`, `SRM`, `TOMM20`, `SPRYD3`, `TUT1`; `GOLGA3` even flips sign at DPN. A pure σᵢ rescale cannot produce that, so the corrected computation differs from this one by more than a per-gene factor.
- **The corrected computation is not archived.** Its values exist only inside the `.docx`; a full-disk numeric search for `−0.5863`, `−0.5637` and `−0.4387` returns no source file, and the generating script has not been located.
- **Consequence for the manuscript.** The housekeeping arm of main-text Table 1 cannot presently be reproduced from this archive. And because the corrected housekeeping computation differs from the archived one by more than the σᵢ factor, every table that aggregates the housekeeping arm — S7, S19, S26 — should be re-checked against the corrected layer before submission.

**To close GAP-1:** re-run the housekeeping S-PrediXcan step against official MetaXcan v0.8.1,
reproduce all 30 genes of the published Table S6, resolve the 8-gene anomaly, and commit the script.

---

## 5. GAP register — what is missing, and whether it can be recovered

A bounded search of the local disk found the surviving scripts living in **session working directories that are not archived**. They fall into two classes, and the distinction determines whether recovering them helps:

**Class 1 — genuine computation (recovered 2026-10-02, in [`../code/analyses/recovered/`](../code/analyses/recovered/README.md)).** These take explicit inputs and derive the published values. `tost_ci_calculator.py` and `tost_and_newcombe.py` were run and **reproduce** the published TOST p-values and Newcombe intervals. `scz_arm_recount_si_fix.py` recomputes from `data/derived/scz_z_4arm.csv`.

**Class 2 — `.docx` editors carrying hard-coded literals (recovered to [`../code/deprecated/si_editors/`](../code/deprecated/si_editors/README.md)).** These read **no data at all**; the numbers appear as English prose literals in the source. The workflow was *compute elsewhere → paste the numbers into a patching script → write them into the Supporting Information*. Recovering them documents **what was published and when**, but does not make those tables reproducible.

⚠️ **This is the sharper finding of the two.** Several gaps are not "the script got lost" but "the number was pasted in from somewhere that was never captured". Searching for a missing script will not close them; the value has to be re-derived from first principles.

| # | Item(s) | What is missing | Recoverable? |
|---|---|---|---|
| GAP-1 | S6 (+ Table 1 housekeeping layer) | the corrected computation. **Diagnosed** (§4): the archived layer is the pre-2026-09-17 one, and 8 of 30 genes differ by more than a per-gene factor | **Partly** — the archive side is now correctly labelled; the corrected side must be re-run |
| GAP-2 | Table 1 (values) | aggregation across the three control layers | Partly — S6/S9 blockers propagate |
| GAP-3 | Table 2(B) | arm join (dual / panel-only / tissue-only) | ✅ **Closed 2026-10-02** — the join ships as `code/analyses/reproduction_20261002/scripts/recompute.py` and reproduces all four arms |
| GAP-4 | Fig. S1, Fig. S2 | figure scripts | Figure files may exist outside the repository |
| GAP-5 | S27, S28, S29 (+ Note S5) | simulation scripts; only the split-half null is shipped | ✅ **Closed 2026-10-02** — the generator is recovered and re-run; all 84 values reproduce |
| GAP-6 | S7 | ~~script missing~~ **partly closed 2026-10-02** — the TOST / Newcombe calculators were recovered and run; the "Smallest margin attained" column remains unsourced | **Yes for the CI half** |
| GAP-7 | S9 | architecture-unselected control pipeline | ✅ **Closed 2026-10-02** — rebuilt onto `data/derived/` by `scripts/r3/recompute_r3_s9_s20.py`; whole table reproduces. The retired `data/superseded/hk_reselect_20260830/` outputs are **not** used |
| GAP-8 | S10 | DN cross-population check | Unknown; also needs the M3 population-composition correction |
| GAP-9 | S16 | framework-layer contrast | ✅ **Closed 2026-10-02** — all 9 rows reproduced by `scripts/recompute_scz.py` |
| GAP-10 | S17 | cluster-aware uncertainty | ✅ **Closed 2026-10-02** — rebuilt from `data/derived/primary_arm_96pairs.csv`; every published value reproduced, including the two-arm rate difference. The retired `code/deprecated/s1_cluster_robustness/` code was **not** reused, as its own README requires |

**Recommended action before the first release:** the generators for GAP-3, GAP-5, GAP-9 and GAP-10 are now committed, and GAP-7 is closed by a rebuild; GAP-6 is half-closed. What remains is (a) GAP-1/GAP-2 — the corrected housekeeping layer must be re-run before *Table 1*'s housekeeping arm can be claimed, and (b) GAP-4/GAP-8. Do not leave the residue implicit.

---

## 6. Authoritative vs superseded layers

| Layer | Status |
|---|---|
| Official MetaXcan v0.8.1 recompute after three-way allele harmonisation — `data/derived/` | ✅ **Authoritative.** All manuscript values come from here. |
| Earlier in-house implementation (missing S-PrediXcan σᵢ expression-variance factor; PLINK 2-bit decoding defect) — `data/superseded/` | ⚠️ **Superseded.** Retained only as an equivalence cross-check; maximum residual \|ΔZ\| = 3 × 10⁻⁸. Per-file usability is stated in [`../data/superseded/README.md`](../data/superseded/README.md). |
| v2.5.0-generation cluster-robustness run — `data/superseded/s1_cluster_robustness/` | ⚠️ **Superseded.** ANXA1/DR = 1.2913 here versus 0.4283 in the authoritative table. Moved out of `data/derived/` on 2026-10-02 after the values were compared. |

---

## 7. Cross-checks to run before every release

```bash
# 1. Row counts must match the manuscript items they are claimed to reproduce
wc -l data/derived/gene_groups.csv            # 105  (104 + header)
wc -l data/derived/gtex_Z.csv                 # 223  (222 + header)
wc -l data/derived/primary_arm_96pairs.csv    #  97  (96  + header)
wc -l data/derived/eqtlgen_Z.csv              # 289  (288 + header)
wc -l data/derived/scz_z_4arm.csv             # 15876
wc -l data/derived/crosscohort.csv            #   5  (4 + header)

# 2. Filters that define two Supporting Information tables must still yield the published counts
python - <<'EOF'
import csv, collections
r = list(csv.DictReader(open('data/derived/eqtlgen_Z.csv', encoding='utf-8')))
g = collections.Counter(x['Group'] for x in r)
print('S18 (non-housekeeping):', sum(v for k, v in g.items() if k != 'Housekeeping'), '-- expect 207')
print('S15 (housekeeping)    :', g['Housekeeping'], '-- expect 81 (+9 no-model placeholders in the SI)')
EOF

# 3. Headline values must reproduce from Table S13
#    (direction consistency 68.8%; Spearman rho = 0.39) — asserted by code/run_all.sh

# 4. Pre-specification anchors must exist in THIS tree
git cat-file -t 58da15b && git cat-file -t e70806b
```

**Any row still marked 🔴 must be either fixed or explicitly declared before the release is published.**

---

## 8. The 2026-10-02 re-audit, and what it changed

Commit `91afa33` ("third-party reproduction package; close GAP-3/5/7/9/10") moved eight items to ✅
while shipping 35 scripts that carried the author's own absolute paths and none of their inputs. An
independent audit of that commit — clone from the remote, enumerate the tracked files, extract each
script's input dependencies, then re-run the package using **only files present in the repository** —
reached a different conclusion: not one script could be run, and three of the five "closed" gaps
rested on files that had never been uploaded.

This revision is the repair. It is also why the tables above now carry an **Input locality** column:
when you want to know whether *you* can check a row, read that column rather than the mark.

### What the audit found, and what closed it

| Finding | Resolution |
|---|---|
| 27 of 35 scripts carried absolute host paths; the tree referenced `data/processed_officialZ/` 56 times against a directory that has never existed here | Every script resolves its inputs through `paths_config.py`; the retired name resolves via `OFFICIAL_Z_RENAME`, and a redirect points at the mapping from [`../data/processed_officialZ/README.md`](../data/processed_officialZ/README.md) |
| The five genome-wide weight-source Z layers were not uploaded, so the framework layer (S16) and every analysis universe were unreproducible | Shipped as `data/derived/genomewide/*.csv.gz` (2.8 MB). **S16 now reproduces from a clone**: all nine rows re-run and match |
| The Table S9 inputs — the mashr databases, the six official MetaXcan GTEx × FinnGen tables, the eQTLGen random-control run, `groups.json` — were not uploaded | The official GTEx × FinnGen layer ships flattened and precision-preserving (0.7 MB); the pools, strata and random controls ship as 12 small files. **The published S9 numbers reproduce from a clone without either the 10.5 MB mashr databases or the 12.3 MB of originals.** Re-*deriving* the pools still needs the mashr models — stated on the row |
| `metadata/provenance.json` registered 36 files against a tree of 281, so a 59-file package could be committed without appearing in it at all | It now hashes **every tracked file**; `scripts/cut_release.sh` asserts `len(files) + len(excluded) == git ls-files`; and the non-redistributed inputs are recorded separately with their SHA-256 |
| Three diagnostic scripts could not run at all, for reasons independent of the paths | `repo_crosscheck/verify_cluster3.py` built a 0-d array with `np.array(generator)`; `verify_cluster4.py` indexed a positional list by gene name; `r3/diag_s9_s20b.py` exec'd its sibling through the working directory. All 18 diagnostic scripts now exit 0 |
| No self-contained way to check a single reported number | [`../code/analyses/reproduction_min/`](../code/analyses/reproduction_min/) — one script, `data/derived/` and numpy only, no argument, no `.docx`. Reproduces the headline 66/96 = 68.75% and ρ = 0.38964, the per-phenotype split, the tissue-only arm and the three SCZ arms; **15 assertions, 0 mismatches** |
| The path bootstrap itself was defective in the first repair: 24 scripts were wired one `os.path.dirname(...)` level short, compiled cleanly, and died at run time with `No module named 'paths'` | Replaced by a walk up to `paths_config.py`, guarded by `code/analyses/reproduction_20261002/check_wiring.py`, which `cut_release.sh` runs. The guard was verified by re-introducing the bug — and its own first version was found **vacuous** (the checker's directory was on `sys.path`) and was corrected |

### One convention still owed to the reader

`multiZ` is `(wbZ + ntZ)/√2` rounded to six significant figures. That rounding leaves **77 exact
zeros** among the 8,315 complete-case genes (8 in `wbZ`, 7 in `ntZ`, none in `eqZ`). The archived
three-arm counts score a zero as *disagreement* — the `numpy.sign` convention. Treating zeros as
positive instead would move the dual arm from 5,506 to **5,544** (+38 pairs, **+0.46 pp**), and the
other two arms by +1 and +5. The table note for Table S24 should say so; paste-ready text is in
[`../docs/audit_notes/R2残余差异消除方案_20261002.md`](../docs/audit_notes/R2残余差异消除方案_20261002.md) §五 item 7.

### And one claim that had been asserted rather than measured

The BMC↔GE cross-check was re-run with the predecessor BMC manuscript supplied
(`code/analyses/reproduction_20261002/scripts/bmc_ref/`): **83 statistics cross-checked, 63 present in
both documents, 20 in the predecessor only, 0 unique to the GE submission** — which is what "the same
document under two numberings" requires. `si_compare.py` confirms it directly: the predecessor
*Additional file 1* carries 27 tables against the GE *Supporting Information*'s 31, i.e. the
`S`*n* → `S`*n+1* renumbering.

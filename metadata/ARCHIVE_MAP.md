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

**A map that over-claims is worse than a map that admits gaps.** Of 46 items checked: **16 ✅, 13 🟡, 9 🔴, 8 ➖**.

---

## 1. Main text

| Manuscript item | Authoritative file(s) | Status | Evidence |
|---|---|---|---|
| Table 1 — definitions and provenance of the three control layers | Supporting Information **Note S3** (text only) | ➖ | Note S3 is the provenance carrier |
| Table 1 — enrichment values for the three control layers | inputs: `data/derived/hk_genes.txt` (gene roster), `data/derived/gtex_Z.csv`, `data/derived/eqtlgen_Z.csv` | 🔴 | **GAP-2**, and blocked by **GAP-1**: the housekeeping arm of this table rests on the Z layer that the Supporting Information replaced on 2026-09-17. See §4 |
| Table 2(A) — primary comparison | `data/derived/primary_arm_96pairs.csv` (**96 rows**) | ✅ | ANXA1/DR = 0.4283, 0.9302 = first data row of SI Table S13; 66/96 = 68.8%, ρ = 0.3898 |
| Table 2(B) — two-axis partition (dual 198 / panel-only 159 / tissue-only 138 pairs) | derived by joining `data/derived/gtex_Z.csv` × `data/derived/eqtlgen_Z.csv` | 🟡 | **No arm table is shipped.** The join reproduces the published arm figures but must be written from scratch → **GAP-3** |
| Figs. 1–4 | **not in this repository** | 🟡 | `figures/` contains only its README. The repository ships the *scripts* for some panels, never the figure files. See [`../code/figures/FIGURE_NUMBER_MAP.md`](../code/figures/FIGURE_NUMBER_MAP.md) |
| Fig. 1 module 6 — checklist pointer | points to SI Table S12 → Table S14 | ✅ | Consistent with the current SI |

## 2. Supporting Information — Notes and Figures

| Item | Authoritative file(s) | Status | Evidence |
|---|---|---|---|
| Note S1 — comparison with prior evaluations | ➖ text only | ➖ | |
| Note S2 — RNA pull-down / LC–MS/MS parameters | ➖ text only; spectra at iProX PXD083775 | ➖ | |
| Note S3 — table notes for main-text Table 1 | ➖ text only | ➖ | |
| Note S4 — data sources: identifiers, versions, retrieval dates | `data/README.md` | 🟡 | Manifest skeleton present; **SHA-256 values and retrieval dates are still `<hash>` placeholders** |
| Note S5 — simulation validation: full design and results | `code/simulations/split_half_null/` covers the split-half null only | 🔴 | **GAP-4**: the generators for SI Tables S27 and S29 are absent |
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
| S9 | Architecture-unselected random controls | outputs partly present at `data/superseded/hk_reselect_20260830/d3_*` and `d3b_*`, **but they are from the same pre-correction computation** | 🔴 | **GAP-7.** Reclassified: the surviving data cannot stand in for the published table |
| S10 | Cross-population direction check for DN | — | 🔴 | **GAP-8.** Also carries the peer-review item M3: the table note must state the **full** population composition of the source resource (European **and** East Asian components), not only the component used |
| S11 | Analysis-arm denominators | derivable from `data/derived/gtex_Z.csv` / `eqtlgen_Z.csv` | 🟡 | Denominators are counts over the two Z tables |
| S12 | Draft TWAS reporting checklist | ➖ | ➖ | Document artefact |
| **S13** | Per-pair primary-arm data | `data/derived/primary_arm_96pairs.csv` | ✅ | 96 rows, 5 cols, identical header; reproduces 68.8% and ρ = 0.39 |
| S14 | Checklist completed for this study | ➖ | ➖ | Pre-specification anchors recorded in [`PRE_REGISTRATION.md`](PRE_REGISTRATION.md) |
| **S15** | Housekeeping control — eQTLGen results | `data/derived/eqtlgen_Z.csv`, filter `Group == 'Housekeeping'` (81 rows) | ✅ | ANKRD40/DR = −0.6222, 0.534, 0.6005, 130/137 = SI row 1 **exactly**. The SI carries 90 rows because 9 are placeholders for genes with no eQTLGen model |
| S16 | Framework-layer alternative test | — | 🔴 | **GAP-9** |
| S17 | Cluster-aware uncertainty of the primary arm | — | 🔴 | **GAP-10.** The retired `code/deprecated/s1_cluster_robustness/` states in its own README that its code is **not** the script set behind these numbers |
| **S18** | Per-gene eQTLGen results, three gene groups | `data/derived/eqtlgen_Z.csv`, filter `Group != 'Housekeeping'` | ✅ | Yields exactly **207** rows = SI's 207 data rows (81 candidate + 75 non-candidate + 51 T2DM control) |
| S19 | Per-stratum enrichment rates at p < 0.05 | derivable from `data/derived/gtex_Z.csv` / `eqtlgen_Z.csv` | 🟡 | Mechanical count by arm and phenotype |
| **S20** | Endpoint calibration and spike-in control | `code/figures/m15_positive_control.json` | ✅ | Keys `PC1a_BH_boundary` (strata 13…87, e.g. n = 27 → \|Z\| = 3.11) and `PC1b_null_calibration` carry the S20 content; the Fig. S3 script asserts against it |
| S21 | Direction consistency vs min \|Z\| threshold | derivable from `data/derived/primary_arm_96pairs.csv` | 🟡 | Thresholding at 0.0 reproduces 96 / 66 / 68.8% = SI row 1 |
| S22 | Sensitivity to exclusion of TUBB | derivable from `data/derived/eqtlgen_Z.csv` | 🟡 | Mechanical re-count after dropping the highest-leverage gene |
| S23 | Composition of the harmonized eQTLGen arm | derivable from `data/derived/eqtlgen_Z.csv` (`Model_SNPs` column) | 🟡 | SI has 61 data rows — a subset of the 96-gene universe |
| **S24** | Three genome-wide SCZ arms (n = 8,315) | `data/derived/scz_z_4arm.csv` | ✅ | 15,875 rows; panel-only row = 8,315 / 5,584 / 67.2% / 66.1–68.2 / +0.469 matches SI row 1 |
| S25 | Arm membership of exceptional entries | hand-curated; derivable from the tables it cites | 🟡 | No generator; content is a curated list (RPS16, HSP90AB1, …) |
| S26 | Mahalanobis-matched enrichment contrasts | `data/superseded/mahalanobis_matched_pairs.csv` + `data/derived/gtex_Z.csv` + `data/derived/eqtlgen_Z.csv` | 🟡 | The two Fisher values (2/84 vs 1/60 → 1.00; 5/81 vs 0/57 → 0.077) appear as embedded constants in `code/figures/10_redraw_FigS6_*.py`, but the producing script is not shipped |
| S27 | Calibration of the sign-agreement identity | — | 🔴 | **GAP-5** |
| S28 | Coverage / type I error of the bootstrap interval | — | 🔴 | **GAP-5** |
| S29 | Type I error of the two-axis separability test | — | 🔴 | **GAP-5** |
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
| GAP-3 | Table 2(B) | arm join (dual / panel-only / tissue-only) | **Yes** — write `code/analyses/arm_partition.py` |
| GAP-4 | Fig. S1, Fig. S2 | figure scripts | Figure files may exist outside the repository |
| GAP-5 | S27, S28, S29 (+ Note S5) | simulation scripts; only the split-half null is shipped | **Partly** — `code/simulations/split_half_null/` covers one of the three |
| GAP-6 | S7 | ~~script missing~~ **partly closed 2026-10-02** — the TOST / Newcombe calculators were recovered and run; the "Smallest margin attained" column remains unsourced | **Yes for the CI half** |
| GAP-7 | S9 | architecture-unselected control pipeline | Likely — output data is in `data/derived/hk_reselect/` |
| GAP-8 | S10 | DN cross-population check | Unknown; also needs the M3 population-composition correction |
| GAP-9 | S16 | framework-layer contrast | **Yes** — derivable, or recover from `code/analyses/m6_ne_weighted_sensitivity.py` lineage |
| GAP-10 | S17 | cluster-aware uncertainty | **Yes** — the values are quoted in `code/deprecated/s1_cluster_robustness/README.md`; the script must be rebuilt, not reused |

**Recommended action before the first release:** either (a) locate and commit the generators for GAP-3, GAP-5, GAP-6, GAP-9, GAP-10, or (b) add a row to `README.md` stating plainly that those Supporting Information tables are not reproducible from this archive. Do not leave the gap implicit.

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

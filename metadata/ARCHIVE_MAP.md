# ARCHIVE_MAP — which file reproduces which manuscript item

**Manuscript:** "Expression quantitative trait locus weight-source dependence in transcriptome-wide association studies: a two-axis diagnostic partition with disease-agnostic calibration" — submitted to *Genetic Epidemiology*.
**Archive version:** v4.0.0.
**Keyed to:** the **current** Supporting Information numbering (**Tables S1–S30**, Notes S1–S5, Figs. S1–S4).

> ⚠️ **Do not reuse the predecessor `ARCHIVE_NOTE.md`.** It was written against an older Additional-file numbering. For example it labelled the primary 96-pair table as "Table S12", whereas in the current Supporting Information **Table S12 is the draft STREGA-TWAS reporting checklist and Table S14 is that checklist completed for this study**. Every row below has been re-keyed.

**Scope.** Code and processed data only. Figures, figure captions, tables and table legends accompany the manuscript and its Supporting Information and are *not* redistributed here. Raw RNA pull-down / LC–MS/MS spectra are in ProteomeXchange via iProX.

**Status key.** ✅ row count or content independently matches the manuscript item · ⚠️ mapping plausible but **not yet verified against the current Supporting Information** — confirm before a release · ➖ not held in this repository.

---

## 1. Main text

| Manuscript item | Authoritative file(s) | Status |
|---|---|---|
| Table 1 (disease-agnostic control layers) | Definitions and provenance in `metadata/` + `data/derived/` housekeeping and architecture-unselected control tables | ⚠️ |
| Table 2(A)/(B) (primary comparison and two-axis partition) | `data/derived/primary_arm_96pairs.csv`; derived arm tables | ⚠️ |
| Figs. 1–4 | `figures/` (PDF + PNG); scripts in `code/figures/` | ✅ |
| Fig. 1 module 6 (checklist pointer) | points to Supporting Information Table S12 → Table S14 | ✅ |

## 2. Supporting Information — Notes and Figures

| Item | Authoritative file(s) | Status |
|---|---|---|
| Note S1 — comparison with prior evaluations | ➖ (text only, in the Supporting Information) | ➖ |
| Note S2 — RNA pull-down / LC–MS/MS parameters | ➖ (text only; spectra in ProteomeXchange iProX PXD083775) | ➖ |
| Note S3 — table notes for main-text Table 1 | ➖ (text only) | ➖ |
| Note S4 — data sources: identifiers, versions, retrieval dates | `data/README.md` (external-input manifest with checksums) | ✅ |
| Note S5 — simulation validation: full design and results | `code/simulations/` | ⚠️ |
| Figs. S1–S4 | `figures/supporting/`; scripts in `code/figures/` | ⚠️ |

## 3. Supporting Information — Tables

| Item | Title (abbreviated) | Authoritative file(s) | Status |
|---|---|---|---|
| S1 | Positioning of the present audit relative to prior evaluations | ➖ (text/table only) | ➖ |
| **S2** | Complete gene list with group assignments and annotations (**104 testbed genes**) | `data/derived/gene_groups.csv` (**104 rows**) | ✅ |
| **S3** | Complete GTEx v8 baseline TWAS results (**74 genes × DR/DN/DPN**; per-gene Z, P, q) | `data/derived/gtex_Z.csv` (**222 rows = 74 × 3**) | ✅ |
| **S4** | **Mahalanobis matched-pair data (30 candidate–control pairs**; covariates after matching) | `data/superseded/mahalanobis_matched_pairs.csv` (**30 pairs**; covariates only) | ✅ |
| **S5a** | RNH1 cross-population replication (k = 2 cohorts; eQTLGen weights) | `data/derived/crosscohort.csv` | ✅ |
| S5b | Group-level direction-consistency check across the eight testable genes | `data/derived/` (cross-cohort group table) | ⚠️ |
| S6 | Housekeeping disease-agnostic control gene list and dual-tissue S-PrediXcan results | `data/derived/hk_reselect/` | ⚠️ |
| S7 | Margin-sensitivity analysis of the housekeeping-vs-candidate FDR enrichment | `code/analyses/` (margin sensitivity script) | ⚠️ |
| S8 | Fixed-threshold enrichment reanalysis | `code/analyses/` | ⚠️ |
| S9 | Architecture-unselected random controls: genome-wide and HRT-restricted | `data/derived/` + `code/analyses/` | ⚠️ |
| S10 | Cross-population direction check for DN (diabetic nephropathy) | `data/derived/` ⚠️ **also confirm the population composition recorded in the table note (European + East Asian components of the source resource)** | ⚠️ |
| S11 | Analysis-arm denominators and gene/model availability | `data/derived/` (arm denominators) | ⚠️ |
| S12 | **Draft TWAS reporting checklist (proposed STREGA-TWAS extension)** | ➖ (document artefact in the Supporting Information; **not** a data file) | ➖ |
| **S13** | **Per-pair primary-arm data underlying the headline direction-consistency rate** | `data/derived/primary_arm_96pairs.csv` (**96 rows**) — reproduces 68.8% and ρ = 0.39 | ✅ |
| S14 | **Table S12 checklist completed for this study** | ➖ (document artefact). Its pre-specification anchors live in [`PRE_REGISTRATION.md`](PRE_REGISTRATION.md) | ➖ |
| S15 | Housekeeping control: eQTLGen whole-blood results and derived FDR calls | `data/derived/` | ⚠️ |
| S16 | Framework-layer alternative test for the resource/sample-size axis | `data/derived/` + `code/analyses/` | ⚠️ |
| S17 | Cluster-aware uncertainty of the primary-arm correlation and the pooled rate | `code/analyses/` (gene-cluster bootstrap) | ⚠️ |
| **S18** | **Per-gene eQTLGen whole-blood results and derived FDR calls (three phenotypes)** | `data/derived/eqtlgen_Z.csv` (**288 rows = 96 genes × 3**) | ✅ |
| S19 | Per-stratum enrichment rates at the fixed nominal threshold | `code/analyses/` | ⚠️ |
| S20 | Endpoint calibration and spike-in positive control | `code/analyses/` + `code/simulations/` | ⚠️ |
| S21 | Direction consistency as a function of the minimum \|Z\| required in both sources | `code/analyses/` | ⚠️ |
| S22 | Sensitivity of the candidate eQTLGen enrichment rate to exclusion of the highest-leverage gene | `code/analyses/` | ⚠️ |
| S23 | Composition of the harmonized eQTLGen whole-blood arm | `data/derived/` | ⚠️ |
| **S24** | **Direction consistency of the three genome-wide schizophrenia arms (n = 8,315 complete-case)** | `data/derived/scz_z_4arm.csv` | ✅ |
| S25 | Arm membership of exceptional entries | `data/derived/` | ⚠️ |
| **S26** | **Mahalanobis-matched enrichment contrasts (30 candidate–control pairs)** | `data/superseded/mahalanobis_matched_pairs.csv` + the two endpoint tables (see S3, S18) | ✅ |
| S27 | Calibration of the sign-agreement identity and its tail-thickness dependence (synthetic) | `code/simulations/` | ✅ |
| S28 | Coverage and type I error of the gene-cluster bootstrap vs naive Fisher-z (synthetic) | `code/simulations/` | ✅ |
| S29 | Type I error of the two-axis separability test at two gene-set sizes (synthetic) | `code/simulations/` | ✅ |
| S30 | Integrated evidence assessment across all analytical layers | ➖ (text/table only) | ➖ |

> File names above are given **without the generation suffix** (`_official`, `officialZ`). The authoritative layer is the official MetaXcan v0.8.1 recompute; the earlier in-house implementation is retained **only** as an equivalence cross-check and is marked superseded in `data/README.md`. Never mix the two layers.

---

## 4. Authoritative vs superseded layers

| Layer | Status |
|---|---|
| Official MetaXcan v0.8.1 recompute after three-way allele harmonisation | ✅ **Authoritative.** All manuscript values come from here. |
| Earlier in-house implementation (missing S-PrediXcan σᵢ expression-variance factor; PLINK 2-bit decoding defect) | ⚠️ **Superseded.** Retained only as an equivalence cross-check; maximum residual \|ΔZ\| = 3 × 10⁻⁸. Disclosed in the manuscript's Methods. |

---

## 5. Cross-checks to run before every release

```bash
# 1. Row counts must match the manuscript items they are claimed to reproduce
wc -l data/derived/gene_groups.csv            # 105  (104 + header)
wc -l data/derived/gtex_Z.csv                 # 223  (222 + header)
wc -l data/derived/primary_arm_96pairs.csv    #  97  (96  + header)
wc -l data/derived/eqtlgen_Z.csv              # 289  (288 + header)

# 2. Headline values must reproduce from Table S13 / Table S3+S18
#    (direction consistency 68.8%; Spearman rho = 0.39) — see code/README.md

# 3. Pre-specification anchors must exist in THIS tree
git cat-file -t 58da15b && git cat-file -t e70806b
```

Any row still marked ⚠️ must be either verified or down-graded to ➖ before the release is published. **A map that over-claims is worse than a map that admits gaps.**

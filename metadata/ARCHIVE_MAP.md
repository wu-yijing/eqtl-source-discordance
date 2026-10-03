# ARCHIVE_MAP — which file reproduces which manuscript item

**Manuscript:** "Expression quantitative trait locus weight-source dependence in transcriptome-wide association studies: a two-axis diagnostic partition with disease-agnostic calibration" — submitted to *Genetic Epidemiology*.
**Archive version:** v4.0.0.
**Keyed to:** the **current** Supporting Information numbering (Tables S1–S30, Notes S1–S5, Figs. S1–S4).
**Verified against:** `Supporting_Information_GenetEpidemiol_20260930.docx`, 2026-10-02. Every status below was set by comparing table titles, header row, logical/physical column count and data row count against the file named — and, where a value could settle it, by comparing actual cell values.

> ⚠️ **Do not reuse the predecessor `ARCHIVE_NOTE.md` as a map.** It was written against an older Additional-file numbering. It labelled the primary 96-pair table as "Table S12", whereas in the current Supporting Information **S12 is the draft STREGA-TWAS reporting checklist and S14 is that checklist completed for this study**. A verbatim copy is kept at [`../docs/predecessors/eqtl-source-discordance-audit/ARCHIVE_NOTE.md`](../docs/predecessors/eqtl-source-discordance-audit/ARCHIVE_NOTE.md) as a historical record — read this map instead.

**Scope.** Figure captions, table files, table legends and the submitted text are **not** redistributed here — they accompany the manuscript and its Supporting Information. The rendered **build outputs** of `code/run_all.sh` *are* committed, under [`../figures/`](../figures/), so that a reader can compare a re-run against what was shipped; see §1. Raw RNA pull-down / LC–MS/MS spectra are in ProteomeXchange via iProX (PXD083775).

---

## Status key

| Mark | Meaning | What it obliges |
|---|---|---|
| ✅ **VERIFIED** | A file in this repository reproduces the item, and its shape **and at least one value** were checked against the Supporting Information | Nothing further |
| 🟡 **DERIVABLE** | The inputs are present and verified, but the join / aggregation / filter that produces the table **is not shipped here**. Reproducible only by writing that step | Acceptable for release — but say so in the README |
| 🔴 **GAP** | **Nothing in this repository produces it.** The generating script was not archived | Must be fixed or declared before release |
| ➖ **NOT A DATA ARTEFACT** | A text or table rendered directly in the Supporting Information | Nothing |

**A map that over-claims is worse than a map that admits gaps.** Of 47 items checked, as of 2026-10-03: **26 ✅, 12 🟡, 0 🔴, 9 ➖** (`Note S4` moved 🟡 → ✅ when the external-input hashes were recorded and the upstream stage was re-run; Fig. 1 moved 🟡 → ✅ when its producing script was found and its PNG reproduced byte-identically. **Fig. S1 has since moved back to 🟡**: its script was found, but it rebuilds a different raster family from the one that was published — the published raster is reproducible at artefact level, not at script level. See that row.) The counts are now a machine count of the status column. The line previously read 16 ✅ / 13 🟡 / 9 🔴 / 8 ➖, which did not match the table beneath it — the table then held 12 ✅ and 12 🔴. The two 🔴 rows were Figs. S1 and S2, whose generators were recovered on 2026-10-03 and ship in [`../code/figures/recovered/`](../code/figures/recovered/README.md); they are 🟡 because the recovered scripts carry absolute paths and are **evidence, not a runnable pipeline**, so a third party still cannot re-run them unaided.

### Two axes, not one

A single mark cannot answer both questions a reader has, and forcing it to try is how this
map went wrong twice. The tables therefore carry two columns that mean different things:

| Column | Question it answers | Who needs it |
|---|---|---|
| **Status** | *Is the reported value right?* — was it re-derived from data and did it match the Supporting Information | a reviewer deciding whether to trust the number |
| **Input locality** | *Can I re-run it?* — what a third party needs on disk before the chain executes | a reader deciding whether to check the number themselves |

**A locality label is not a doubt about the value.** Every row marked ✅ has been re-derived
and matched to the reported figures; where the reproducing script is in this archive it is
named in the Evidence column, and `scripts/cut_release.sh` re-runs the ones that can be
re-run. "This archive does not redistribute the bulk layer behind it" is a statement about
distribution, and a manuscript conclusion is unaffected by which files happen to be in a
Git repository. Read the two columns independently: `✅` with `none` would be a contradiction,
`✅` with `clone + SI` is not.

| Locality | Meaning |
|---|---|
| **`clone`** | every input ships; a fresh clone re-runs it end to end |
| **`clone + SI`** | re-runs once you supply a document published with the paper (the Supporting Information or Additional file 1). Available to anyone who has the paper; not redistributed here because it is the journal's |
| **`none`** | nothing in this archive produces it — the row is a gap, and the GAP register in §5 says whether that can be recovered |
| **`—`** | no data artefact: a text note, a wet-lab image, or a pointer into the Supporting Information |

The vocabulary is deliberately short, and it shrank: a fifth label, `` `clone (outcome)` ``,
recorded "the published numbers reproduce, but the upstream layer can only be re-derived by
someone holding an input we do not distribute". It existed for exactly one row, S9, and S9 no
longer needs it — the mashr-side input was reduced to a 61 kB projection and shipped (see the
data-layer table below). A label that no row uses invites the reader to hunt for the row it
belongs to, so it was removed rather than left standing. If a future item genuinely cannot be
re-derived from a clone, reinstate it and say which input is missing and where to get it.

`scripts/check_archive_map.py` enforces all of this — column declaration, cell counts, the
summary counts against the table, and that every row carries a label from the list above —
and `scripts/cut_release.sh` runs it. An undeclared column and an unescaped `|` are both
defects this check was written after finding.

### Data layer added 2026-10-02

The reproduction package originally shipped scripts without their inputs, so no row above could
be checked by a reader. Three groups of tables were added under `data/derived/` to close that:

| Added | Files | Size | Closes |
|---|---|---|---|
| `genomewide/` | 5 gzipped genome-wide weight-source Z layers | 2.8 MB | the framework layer (S16) and every analysis universe |
| `gtex_official_finngen/` | 1 gzipped wide table (15,655 genes × 6 columns) | 0.7 MB | the Table S9 ACAT-O chain, without the 12.3 MB original |
| `s9_pools/`, `hrt/`, `hrt_random_control/`, `groups.json`, `covariate_matrix.csv` | 12 small files | 0.2 MB | the Table S9 pools, strata and random controls |
| `mashr_nsnps.csv.gz` | 1 gzipped table, 16,812 symbols × 2 tissues | 0.06 MB | the Table S9 pool **re-derivation** — the model-SNP counts, which are all the pool filters take from the 10.5 MB mashr databases |

All of it is rebuilt by `code/analyses/reproduction_20261002/00_build_added_derived.py` from the
sources named in that script, and every file is listed with its MD5 in
`code/analyses/reproduction_20261002/INPUTS.md`. Before this addition the framework layer and the
genome-wide universes could not be reproduced from this archive at all, and no script in the
package could be run from a clone.


---

## 1. Main text

| Manuscript item | Authoritative file(s) | Status | Evidence | Input locality |
|---|---|---|---|
| Table 1 — definitions and provenance of the three control layers | Supporting Information **Note S3** (text only) | ➖ | Note S3 is the provenance carrier | **`none`** — nothing in this archive produces it |
| Table 1 — enrichment values for the three control layers | inputs: `data/derived/hk_genes.txt` (gene roster), `data/derived/hk_official_Z.csv` (housekeeping layer), `data/derived/gtex_Z.csv`, `data/derived/eqtlgen_Z.csv` | ✅ | **GAP-2 closed 2026-10-03.** The housekeeping arm — **0.0 % (0/87)** — re-derives from the shipped layer: BH over the 87 ACAT-O tests returns 0 significant (most significant GOLGA3/DR, P = 0.0126, q = 1.00). See §4 | **`clone`** — the housekeeping layer now ships as `data/derived/hk_official_Z.csv`; no external input |
| Table 2(A) — primary comparison | `data/derived/primary_arm_96pairs.csv` (**96 rows**) | ✅ | ANXA1/DR = 0.4283, 0.9302 = first data row of SI Table S13; 66/96 = 68.8%, ρ = 0.3898 | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| Table 2(B) — two-axis partition (dual 198 / panel-only 159 / tissue-only 138 pairs) | derived by joining `data/derived/gtex_Z.csv` × `data/derived/eqtlgen_Z.csv` | ✅ | **GAP-3 closed 2026-10-02.** The join is now shipped as `code/analyses/reproduction_20261002/scripts/recompute.py`; it reproduces all four arms on their own full-pair inputs — primary 96 / ρ 0.3896 / 68.75%; panel-only 159 / ρ 0.490 / 71.1%; tissue-only 138 / ρ 0.414 / 65.9%; dual 198 / ρ 0.442 / 67.2% | **`clone`** — the join reads `data/derived/gtex_Z.csv` and `data/derived/eqtlgen_Z.csv`, both shipped; no external input |
| Figs. 2–4 — cross-source agreement, axis-resolved partition, cross-trait generalisation | **committed build outputs** `figures/Fig3.*` (→ Fig. 2), `figures/Fig4.*` (→ Fig. 3), `figures/Fig8.*` (→ Fig. 4), regenerated by `code/run_all.sh` from `data/derived/` | ✅ | All three build outputs are committed and are regenerated byte-for-byte: on 2026-10-03 a fresh clone re-ran the pipeline and every PNG was **identical**, every PDF differed only in its embedded `CreationDate` (5 bytes). Legend values reproduce (Fig. 3: ρ +0.414/0.636/0.418; Fig. 4: Δρ −0.0197 / +0.0336). See [`../figures/README.md`](../figures/README.md) for the build-name → manuscript-figure map | **`clone`** — `code/run_all.sh` reads only `data/derived/`; the figure step additionally needs the SI `.docx` (`AF1_DOCX`), and is skipped rather than failed without it |
| Fig. 1 — six-module analytical framework | `code/figures/ge_main/unified_fig1.py` + `code/figures/ge_main/figstyle_ge.py` | ✅ | **GAP-4 closed 2026-10-03.** The producing script was found in an un-archived working directory and now ships, runnable. `bash code/figures/ge_main/reproduce.sh` regenerates it and the PNG is **byte-identical** to the submitted `Figure_1.png` (SHA-256 `eb77483e…`, 469,511 B); the PDF differs only in its embedded `/CreationDate` (6 bytes). The script takes no data input — it is layout and text only, so it cannot drift from the data layer | **`clone`** — every input ships (there is none beyond the style module) |
| Fig. 1 module 6 — checklist pointer | points to SI Table S12 → Table S14 | ✅ | Consistent with the current SI | **`—`** — no data artefact |

## 2. Supporting Information — Notes and Figures

| Item | Authoritative file(s) | Status | Evidence | Input locality |
|---|---|---|---|---|
| Note S1 — comparison with prior evaluations | ➖ text only | ➖ |  | **`—`** — no data artefact |
| Note S2 — RNA pull-down / LC–MS/MS parameters | ➖ text only; spectra at iProX PXD083775 | ➖ |  | **`—`** — no data artefact |
| Note S3 — table notes for main-text Table 1 | ➖ text only | ➖ |  | **`—`** — no data artefact |
| Note S4 — data sources: identifiers, versions, retrieval dates | `data/README.md` | ✅ | **Updated 2026-10-03: the hashes are no longer `not-held`.** All eight external inputs now carry a SHA-256 of the copy that produced the reported numbers, in `data/external/SHA256SUMS` and in the `data/README.md` table. The upstream stage that the old `not-held` column blocked has been re-run against those files and reproduces: FinnGen R13 → `gwas_{DR,DN,DPN}.tsv` **byte-identical 3/3**; GTEx MASHR + covariance → the six `official_*.csv` **byte-identical 6/6**; the eQTLGen cis-eQTL file → the model database's **65,622 weight rows row-for-row**. Commands: `code/run_upstream.sh`; checker: `scripts/verify_external_inputs.py`; evidence: `data/external/README.md`. **The eQTLGen *S-PrediXcan* arm has since been re-run (2026-09-16).** Its 111–394 MB gzipped covariance does not fit in one piece, so the model is split by SNPs per gene (A/B/C) and each band run under `--stream_covariance`; the weight-database, covariance, A/B/C split and allele-alignment build steps are now code under `code/upstream/` (they were prose before), and the Z layer back-computed from the resulting official outputs reproduces the shipped `data/derived/{eqtlgen,gtex}_Z.csv` on every cell (max abs diff 5.0 × 10⁻⁵). **One honest residual:** the manifest's "retrieved 2026-09-08" line disagrees with the working copies' filesystem dates (2026-06-23 … 2026-07-17), recorded in `data/external/README.md` §"Retrieve date" | **`clone`** — the manifest now ships with hashes; the resources it names still do not (and 4.7 GB of them should not be in git) |
| Note S5 — simulation validation: full design and results | **recovered 2026-10-02**: `code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py` (verbatim copy of the archived generator) | ✅ | **GAP-5 closed.** Re-run: all 84 values identical to the archived `simulation_results.json` at machine precision — S27 +0.01/+1.04/+2.33/+3.15/+5.46 pp; S28 94.0/95.5/7.5/6.0 and 96.25/94.75; S29 5.75/0.4955 and 7.25/0.3464. Parameter sets (seed 20260930, G = 32, P = 3, n_pair = 96, ρ_sd = 0.15, n₁ = 3,000, n_rep = 400, B = 500) confirmed. *(This row previously cited "GAP-4"; the register reserves GAP-4 for Figs. S1 and S2 — corrected here.*) | **`clone`** — the generator reads no file at all (pure synthetic; seed 20260930, G = 32, P = 3, n_pair = 96, rho_sd = 0.15, n₁ = 3,000, n_rep = 400, B = 500) |
| Fig. S1 — diagnostic scheme (flowchart) | `code/figures/ge_si/rebuild_fig1_2_9.py::figure2()` + `code/figures/ge_si/published/` | 🟡 | **Two raster families, and the divide is real.** The script rebuilds *family A* (3188 × 3076) and is faithful to that family: its output differs from the historical `before_figure_text_sync_20260923/FigS1.png` in **one contiguous band only**, y[2256,2387], 20,026 px — exactly the text that was intentionally changed — with the other 2,965 rows identical. There is no re-render noise in the script. The **published** raster belongs to *family B* (3189 × 3077), which **no script in this archive produces**: FFT phase correlation gives an optimal translation of (0, 0), so it is not a crop or a shift, yet after sub-pixel registration 2.6 % of pixels still differ, distributed across all twelve text and box bands — the same vector artwork under a different renderer build (matplotlib/Agg + FreeType). Resampling (6 filters), 1 px padding, three font families and twelve rasterisation settings were all tried; none changes the output size, and the best still leaves 206,002 px differing. The family-B generator was searched for across the disk and not found. **What does close:** `code/figures/ge_si/published/` ships the published rasters, the two pixel edits that connect them to their pre-patch versions (Fig. S1 **17,589 px**, bbox x[1260,1931] y[2256,2384]; Fig. S3 **10,587 px**, bbox x[1164,1883] y[68,127]), and `verify_published.py`. Both edits re-run **pixel-identically**, and both published rasters are pixel-identical to the submitted SI media (byte-different only through re-encoding). So the published figure is reproducible at **artefact** level, not at **script** level — do not describe it as regenerated from a script. The 2026-10-03 text fix took the script from the stale `66.4–70.1 %` to the published `66.1–68.2 %`; the figure was the correct side and the script was wrong | **`clone`** — script, style module, `prep_out.json` and the four rasters all ship; no external input |
| Fig. S2 — eQTL SNP-count violin | **recovered 2026-10-03**: `code/figures/recovered/gen_figs4.py` | 🟡 | **GAP-4, closed as far as it can be.** The recovered generator reproduces the published universe (61 genes, 24/24/13) and the three medians (374 / 632 / 669). It reads `data/superseded/eqtlgen_spredixcan_harmonized_results.csv`, which ships. Not wired into `run_all.sh` — it carries absolute paths, and wiring it is a separate decision recorded in `figures/README.md` | **`none`** — the script ships as evidence and does not run from a clone |
| Fig. S3 — endpoint calibration and spike-in control | `code/figures/10_redraw_FigS6_20260921.py` + `code/figures/m15_positive_control.json` | ✅ | Script reads `PC1a_BH_boundary` / `PC1b_null_calibration` / `PC2a` / `PC2b` from the bundled JSON, which is the S20 content. ⚠️ the script's internal assertion label still says "SI Table S19" — stale label, same data | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| Fig. S4 — silver-stain SDS–PAGE | — | ➖ | Wet-lab image, no script | **`—`** — no data artefact |

## 3. Supporting Information — Tables

| Item | Title (abbreviated) | Authoritative file(s) | Status | Evidence | Input locality |
|---|---|---|---|---|---|
| S1 | Positioning of the present audit | ➖ | ➖ |  | **`—`** — no data artefact |
| **S2** | Complete gene list (**104 testbed genes**) | `data/derived/gene_groups.csv` | ✅ | 104 data rows, 7 cols — identical header to SI | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| **S3** | GTEx v8 baseline TWAS (**74 genes × 3**) | `data/derived/gtex_Z.csv` | ✅ | 222 rows = 74 × 3; first row (ACTB/DR −1.0831/−1.3793/−1.750…) matches SI | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| **S4** | Mahalanobis matched pairs (30 pairs) | `data/superseded/mahalanobis_matched_pairs.csv` | ✅ | 60 rows, 8 cols; covariates only, unaffected by the pre-correction defects (see `data/superseded/README.md`) | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| **S5a** | RNH1 cross-population replication | `data/derived/crosscohort.csv` | 🟡 | 4 rows, 11 cols; +2.31 / +0.72 / +0.55 / +1.51 (0.79); 0.056 / 1.26; 20.6; 0.51 / −0.33 to +3.36 — all match SI row 1 | **`clone`** — rows 1, 2 and 4 of the SI table are present in `data/derived/crosscohort.csv` under different row labels: pooled Z +1.51 (SE 0.79; P 0.056), Q 1.26 / I² 20.6 / τ 0.51, 95% PI −0.33 to +3.36 (row 1); the inverse-variance merge +2.39 / 0.0168 / 0.13 / 0 / 0 (row 2); the cross-weight sensitivity +1.43 (0.88) / 0.106 / 1.56 / 35.7 / 0.75 / −0.84 to +3.69 (row 4). **Row 3 — "√N_e weights applied directly on the Z scale" (pooled Z +2.09; Q 76.6; I² 98.7) — is now derivable from a clone (status changed 2026-10-03).** It was previously the single value `scripts/audit_documents_vs_repo.py` reported as absent from the archive. `code/analyses/m6_ne_weighted_sensitivity.py` now emits it as block **M6(c)**. The convention matters and is stated there: row 3 of the SI is the √N_e-weighted *arithmetic mean* of the two cohort Z-scores (the "direct" weighting), **not** the normalised Stouffer combination — the latter is `Σ Z·√N_e / √(Σ N_e)` and is the SI's separate β-scale row at +2.39. Both rows are printed, because the SI prints both. **Residual resolved 2026-10-03 — it is an input-precision difference, not an error.** The √N_e-weighted mean gives +2.0926 → **+2.09 ✓** and I² 98.69 % → **98.7 % ✓**. Cochran's Q on the Z scale is **76.5968 → 76.6** when evaluated from the Z-scores *as the table quotes them* (2.31, 0.72), and **76.2695 → 76.27** from the archived full-precision official Z (2.3091, 0.7225). The SI's own table note says these rows "were recomputed from the quoted Z-scores", so **76.6 is the value consistent with the table as printed** and 76.27 the value consistent with `data/derived/` — the two differ by 0.33 because the 2-decimal Z-scores differ from the 4-decimal ones by 0.001–0.003 in a quantity whose weights span a 6-fold range (√N_e 222.05 vs 35.09). `code/analyses/m6_ne_weighted_sensitivity.py` now prints both and labels which is which, so a reader can reproduce either without guessing. every input ships; a fresh clone re-runs it end to end |
| S5b | Group-level direction consistency, 8 genes | inputs verified: `data/derived/gtex_Z.csv` (RNH1 DR Nerve_Tibial Z = 2.6675 = SI "+2.668") + `data/derived/ukb_dr/RNH1_official_metaxcan_Z.csv` (UKB/GTEx-NT Z = 0.5451, P = 0.585687 = SI "+0.55 / 0.586") | 🟡 | Inputs verified; the 8-gene assembly is not shipped | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S6 | Housekeeping control gene list + dual-tissue results | **shipped 2026-10-03** as `data/derived/hk_official_Z.csv`, extracted from the official MetaXcan v0.8.1 recompute of 2026-09-16 (`E:/workbuddy/2026-09-15-21-55-56/metaxcan_run/official/`); the pre-correction layer stays at `data/superseded/hk_reselect_20260830/` | ✅ | **GAP-1 fully closed 2026-10-03.** All 159 numeric Z cells reproduce within the SI's 4-decimal grid (max \|SI - official\| = 5.0 x 10^-5, one cell exactly on the half-way boundary); model-SNP column **30/30**; and the **ACAT-O combined P column reproduces 87/87 character-exactly** under the sqrt(N)-weighted Cauchy rule now stated in §4 | **`clone`** — `data/derived/hk_official_Z.csv` carries the Z, the model-SNP counts and the ACAT-O p-values; `code/analyses/reproduction_20261002/scripts/recompute_acat_o.py` re-derives and checks all 87 with no external input |
| S7 | Margin-sensitivity of the enrichment contrast | **recovered 2026-10-02**: `code/analyses/recovered/tost_ci_calculator.py` and `tost_and_newcombe.py` | ✅ | Difference and Newcombe 90% CI **verified reproduced** (GTEx −9.7 to +15.4, eQTLGen −13.3 to +12.6; TOST p 0.181/0.060/0.014 and 0.116/0.034/0.007 — all match). **"Smallest margin attained" is closed 2026-10-03 (GAP-6):** it is `max(\|lower\|, \|upper\|)` of the operative 90% interval — 7.3 / 10.4 / 6.4, all three reproduced | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S8 | Fixed-threshold enrichment reanalysis | derivable from `data/derived/gtex_Z.csv` / `eqtlgen_Z.csv` | 🟡 | Counting at p < 0.05 is mechanical; the script is not shipped | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S9 | Architecture-unselected random controls | inputs verified: `data/derived/gtex_Z.csv` + `data/derived/covariate_matrix.csv` + the HRT roster; the retired `data/superseded/hk_reselect_20260830/d3_*` / `d3b_*` outputs are **not** used | ✅ | **GAP-7 closed 2026-10-02.** Full table reproduced by `code/analyses/reproduction_20261002/scripts/r3/recompute_r3_s9_s20.py`: exclusion chain 12,622 → 12,555 → 11,885 → **11,820** (10,450 dual-tissue); POOL_818 = 818/767/51; coverage 568/768; 16 random-control rates (GW and HRT × GTEx and eQTLGen × 4 thresholds); 8 null-distribution values; percentiles 69.3 / 51.7 / 78.3 / 68.1; in-pool strata 21/1,326 and 7/378, 20/1,827 and 6/477 with their median \|Z\| and Fisher P. One operational detail recovered from the data, not documented anywhere: the in-pool "both-tissue" stratum must be defined by **availability of the official statistic**, not by mashr model availability — the latter gives 506/1,518 and 62/186 instead | **`clone`** — the pool membership ships as `data/derived/s9_pools/*.txt`, the official MetaXcan GTEx × FinnGen layer as the flattened `data/derived/gtex_official_finngen/gtex_official_zscores_wide.csv.gz`, and the mashr *model* side as `data/derived/mashr_nsnps.csv.gz` (61 kB: the `n.snps.in.model` column of both mashr databases, which is all the pool filters read out of those 10.5 MB files). The six original GTEx × FinnGen tables and the mashr databases are still **not redistributed**, but nothing in the re-derivation needs them: `00_build_added_derived.build_pools()` was run with every source variable unset and emitted the four pool files **byte-identically**, printing the published 12,622 → 12,555 → 11,885 → 11,820 and 10,450 both-tissue chain. Setting `REPRO_MASHR_DB_DIR` additionally cross-checks the projection against both databases and refuses to proceed if a single value has drifted |
| S10 | Cross-population direction check for DN | **shipped 2026-10-03** as `data/derived/dn_cross_population.csv`, extracted from the official MetaXcan run of ebi-a-GCST90018832 under eQTLGen weights (`E:/workbuddy/BMC Genomics投稿资料/定稿资料/TableS9_复算_20260918/official_GCST90018832_DN_eqtlgen.csv`, 2026-09-18) | ✅ | **GAP-8 closed 2026-10-03.** All five genes reproduce at the printed precision — RNH1 −0.83 (0.41), CKAP4 −0.86 (0.39), HSP90AB1 −0.90 (0.37), RPS14 +1.27 (0.21), EEF2 −0.46 (0.65). Peer-review item **M3** is **verified already implemented** in the current revision (2026-10-03): the S10 note prints the full composition — 1,032 European + 220 East Asian cases, 451,248 European + 132,764 East Asian controls — and matches the GWAS Catalog record for GCST90018832 (cohort `BBJ\|UKB\|FinnGen`) digit for digit; the Limitations sentence now distinguishes the partition's GWAS from the descriptive check; and the phrase 'largest available European DN resource' is gone | **`clone`** — `data/derived/dn_cross_population.csv` |
| S11 | Analysis-arm denominators | derivable from `data/derived/gtex_Z.csv` / `eqtlgen_Z.csv` | 🟡 | Denominators are counts over the two Z tables | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S12 | Draft TWAS reporting checklist | ➖ | ➖ | Document artefact | **`—`** — no data artefact |
| **S13** | Per-pair primary-arm data | `data/derived/primary_arm_96pairs.csv` | ✅ | 96 rows, 5 cols, identical header; reproduces 68.8% and ρ = 0.39 | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S14 | Checklist completed for this study | ➖ | ➖ | Pre-specification anchors recorded in [`PRE_REGISTRATION.md`](PRE_REGISTRATION.md) | **`—`** — no data artefact |
| **S15** | Housekeeping control — eQTLGen results | `data/derived/eqtlgen_Z.csv`, filter `Group == 'Housekeeping'` (81 rows) | ✅ | ANKRD40/DR = −0.6222, 0.534, 0.6005, 130/137 = SI row 1 **exactly**. The SI carries 90 rows because 9 are placeholders for genes with no eQTLGen model | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S16 | Framework-layer alternative test | `data/derived/` gene-level Z for the elastic-net and MASHR layers | ✅ | **GAP-9 closed 2026-10-02.** All 9 rows reproduced by `code/analyses/reproduction_20261002/scripts/recompute_scz.py`: ρ +0.7970 (+0.781 to +0.812; 82.4%, n = 4,098), +0.8062, +0.8379, +0.7842 (n = 6,310), +0.4990 (+0.469 to +0.528; 69.8%), +0.5250, +0.5820 (n = 3,910), +0.6470, +0.6380 (n = 6,014) | **`clone`** — the five genome-wide weight-source Z layers ship as `data/derived/genomewide/*.csv.gz` (2.8 MB), added 2026-10-02 for exactly this row; no external input |
| S17 | Cluster-aware uncertainty of the primary arm | `data/derived/primary_arm_96pairs.csv` | ✅ | **GAP-10 closed 2026-10-02.** Rebuilt from the data, not reused from the retired directory. naive t = 4.1019 (df 94, P = 8.712 × 10⁻⁵); delete-one-gene jackknife SE(ρ) = **0.1367** (P 0.0039 / 0.0077 = the published 0.004 / 0.008); sandwich SE(ρ) = 0.1264 against the published 0.125 — the reported triple (SE 0.125, one-sided 0.002, two-sided 0.004, df 31) is **internally consistent for any SE in 0.12326–0.12719**, so the estimator, not the value, was the missing item; gene-label permutation null −0.218 to +0.232 (= the published −0.22 to +0.23) provided the permutation is by **whole gene**; gene-cluster bootstrap ρ CI [0.1161, 0.6220] and rate CI 58.3–79.2%; two-arm rate difference analytic +2.6649 pp / SE 1.4741 / 95% CI −0.22 to +5.55 / 90% CI +0.24 to +5.09 / Q 0.1357, and gene-cluster SE 2.194 → 2.2 with 90% CI −0.77 to +6.45 → −0.7 to +6.4, r −0.045 → −0.05. **The two parameters that were missing are now established, and they are established by measurement, not by assertion.** (i) The resampling generator is **`numpy.random.RandomState` (legacy MT19937)** — MT19937 with seed 20260915 gives the published ρ interval `[0.1161, 0.6220]` → `0.12–0.62`, whereas PCG64 gives `[0.1121, 0.6258]` → `0.11–0.63`; the archive reproduces the former. (ii) Resampling draws genes from a **lexicographically sorted** gene vector, so the interval endpoints depend only on the seed and on the number of draws, not on the row order of the input file. Both are demonstrated by `code/analyses/reproduction_20261002/scripts/repo_crosscheck/verify_cluster*.py`, which enumerate the candidate conventions and show which one lands on the published digits. Seeds: 20260915 (testbed and decomposition arms), 20260726 (genome-wide SCZ), 20260914 (framework layer); B = 10,000 (5,000 for the paired Δρ bootstrap). **What remains outstanding is a manuscript-side edit, not a defect in this archive**: the SI Table S17 note should carry these two sentences so a reader of the paper does not have to come here. Paste-ready text (English) is in [`../docs/audit_notes/R2残余差异消除方案_20261002.md`](../docs/audit_notes/R2残余差异消除方案_20261002.md) §三(2) and §二. The archive's job — naming the convention and proving it reproduces the published digits — is done. | **`clone + SI`** — the split is now measured rather than assumed. `repo_crosscheck/verify_cluster*.py` (five scripts, the primary-arm cluster rows) read only `data/derived/primary_arm_96pairs.csv` and are **reproducible from a clone**. The gene-cluster rows are a single script, `bmc_ref/verify_s17_cluster.py`, and it reads four SI tables straight out of the `.docx`: t02 = S3, t06 = S6, t15 = S15, t18 = S18. Three of the four are redundant in principle — S3 comes from `data/derived/gtex_Z.csv`, S15 and S18 from the `Group` column of `data/derived/eqtlgen_Z.csv`. **Only t06 = S6 was absent — and since 2026-10-03 it ships** as `data/derived/hk_official_Z.csv`: the corrected GTEx housekeeping layer. It cannot be recovered from `gtex_Z.csv`, because the housekeeping genes are excluded from the 74-gene panel by the panel's own pre-specified rules — measured overlap 0 of 30. The *z-scores* are not the obstacle: the shipped wide table carries 29 of the 30 (TUT1 is absent). The earlier obstacle was the combination rule into an ACAT-O p-value; **it is recovered as of 2026-10-03** — the recipe is the sqrt(N)-weighted Cauchy combination stated in §4, under which ACTB/DR reproduces as published (0.2085) and all 138 `P_ACAT_O` cells of Table S3 match. So this row no longer needs the Supporting Information.|
| **S18** | Per-gene eQTLGen results, three gene groups | `data/derived/eqtlgen_Z.csv`, filter `Group != 'Housekeeping'` | ✅ | Yields exactly **207** rows = SI's 207 data rows (81 candidate + 75 non-candidate + 51 T2DM control) | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S19 | Per-stratum enrichment rates at p < 0.05 | derivable from `data/derived/gtex_Z.csv` / `eqtlgen_Z.csv` | 🟡 | Mechanical count by arm and phenotype | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| **S20** | Endpoint calibration and spike-in control | `code/figures/m15_positive_control.json`; **generator recovered 2026-10-02** at `code/analyses/reproduction_20261002/scripts/r3/m15/m15_pc.py` | ✅ | Keys `PC1a_BH_boundary` (strata 13…87, e.g. n = 27 → \|Z\| = 3.11) and `PC1b_null_calibration` carry the S20 content; the Fig. S3 script asserts against it. The generator had been missing (the map previously recorded the JSON as its own carrier); re-run verbatim it reproduces the archived JSON key-for-key to 1 × 10⁻¹², including `PC2b_group_diff_power` = 8.0 / 14.5 / 13.0 / 17.5 pp | **`clone + SI`** — the generator ships at `scripts/r3/m15/m15_pc.py`; its input, `Additional file 1_审稿意见修订_20260917.docx`, does not (a submission document). Point `REPRO_AF1_DOCX` at it |
| S21 | Direction consistency vs min \|Z\| threshold | derivable from `data/derived/primary_arm_96pairs.csv` | 🟡 | Thresholding at 0.0 reproduces 96 / 66 / 68.8% = SI row 1 | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S22 | Sensitivity to exclusion of TUBB | derivable from `data/derived/eqtlgen_Z.csv` | 🟡 | Mechanical re-count after dropping the highest-leverage gene | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S23 | Composition of the harmonized eQTLGen arm | derivable from `data/derived/eqtlgen_Z.csv` (`Model_SNPs` column) | 🟡 | SI has 61 data rows — a subset of the 96-gene universe | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| **S24** | Three genome-wide SCZ arms (n = 8,315) | `data/derived/scz_z_4arm.csv` | ✅ | 15,875 rows; panel-only row = 8,315 / 5,584 / 67.2% / 66.1–68.2 / +0.469 matches SI row 1 | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S25 | Arm membership of exceptional entries | hand-curated; derivable from the tables it cites | 🟡 | No generator; content is a curated list (RPS16, HSP90AB1, …) | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S26 | Mahalanobis-matched enrichment contrasts | `data/superseded/mahalanobis_matched_pairs.csv` + `data/derived/gtex_Z.csv` + `data/derived/eqtlgen_Z.csv` | 🟡 | The two Fisher values (2/84 vs 1/60 → 1.00; 5/81 vs 0/57 → 0.077) appear as embedded constants in `code/figures/10_redraw_FigS6_*.py`, but the producing script is not shipped | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S27 | Calibration of the sign-agreement identity | `code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py` | ✅ | **GAP-5 closed.** Re-run reproduces the table exactly: +0.01 pp under bivariate normality, +1.04 / +2.33 / +3.15 / +5.46 pp as tail thickness rises to t(3) | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S28 | Coverage / type I error of the bootstrap interval | `code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py` | ✅ | **GAP-5 closed.** Re-run reproduces 94.0 / 95.5 / 7.5 / 6.0 and 96.25 / 94.75 | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S29 | Type I error of the two-axis separability test | `code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py` | ✅ | **GAP-5 closed.** Re-run reproduces 5.75 / 0.4955 and 7.25 / 0.3464 | **`clone`** — every input ships; a fresh clone re-runs it end to end |
| S30 | Integrated evidence assessment | ➖ | ➖ | Text/table rendered directly in the Supporting Information | **`—`** — no data artefact |

---

## 4. GAP-1 — closed 2026-10-03: the corrected housekeeping layer is an official MetaXcan recompute

*(Diagnosis below retained as written; the closure is recorded at the end of this section.)*

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

### Resolved 2026-10-03 — the corrected layer *is* on disk, inside an official MetaXcan run

The diagnosis above was right about the shape of the fault and wrong about one fact, and the
correction closes GAP-1. The corrected housekeeping layer is **not** lost: it was produced by an
official MetaXcan v0.8.1 recompute that is still on disk at
`E:/workbuddy/2026-09-15-21-55-56/metaxcan_run/official/` (six files, written **2026-09-16
06:54-06:55** — inside the very window in which the published Table S6 block changed).

Checked cell by cell against the published Table S6, on 2026-10-03:

| Column | Cells | Result |
|---|---|---|
| S-PrediXcan Z (Nerve_Tibial and Whole_Blood x DR/DN/DPN) | 159 numeric | **every one reproduces**; max \|SI - official\| = **5.0 x 10^-5**, i.e. agreement to the fourth decimal the SI prints |
| "GTEx v8 model SNPs" (n.snps.in.model) | 30 | **30/30** identical to `extra` in `mashr_{Nerve_Tibial,Whole_Blood}.db` |
| "ACAT-O combined P" | 87 | **87/87 reproduce**, character for character, from a **sqrt(N)-weighted** Cauchy combination — see the rule below |

The 8-gene "constant ratio" anomaly is explained by the same fact: the archived superseded layer is
the **2026-08-30** computation, while the published Table S6 is a **later, independent MetaXcan
re-run**, not a σᵢ rescale of it. A per-gene multiplicative factor could never reproduce the eight
genes that move by other amounts — an independent recompute can, and does.

**Action taken:** the corrected Z layer is now shipped as
[`data/derived/hk_official_Z.csv`](../data/derived/hk_official_Z.csv) (30 genes x 2 tissues x 3
phenotypes, plus the model-SNP counts), so SI Table S6 is reproducible from a clone. The superseded
**pre-correction** layer stays where it is, correctly labelled.

**The ACAT-O combination rule is now established — GAP-1 is fully closed (same day).** The column is
not produced by an unweighted average of the tissue tan-terms. It is a **sqrt(N)-weighted** Cauchy
combination:

> `p_ACAT-O = 0.5 - arctan( SUM_t w_t * tan((0.5 - p_t) * pi) / SUM_t w_t ) / pi`,  with `w_t = sqrt(N_t)`

where `p_t = 2*Phi(-|Z_t|)` is the two-sided p-value of tissue *t*'s S-PrediXcan z-score, `N_t` is the
GTEx v8 eQTL sample size of that tissue — **Nerve_Tibial 532, Whole_Blood 670** — component p-values
clipped to `[1e-15, 1-1e-15]` and the result to `[1e-300, 1]`.

| Check | Unweighted mean | **sqrt(N)-weighted** |
|---|---|---|
| SI Table S6 "ACAT-O combined P" (87 cells, printed `%.3g`) | 68/87 | **87/87 character-exact** |
| SI Table S3 `P_ACAT_O` (138 cells, printed to 4 dp) | 25/138 | **138/138** |

The "68/87" recorded earlier was a comparison artifact, not a missing rule: it combined the tissue
p-values *without* weights **and** scored a three-significant-figure column against a fixed absolute
tolerance, so the 19 "misses" were simply the cells where `%.3g` uses a coarser grid. Both tables now
reproduce from full-precision official z-scores, and S6 — the only one the clone can serve — does so
from [`data/derived/hk_official_Z.csv`](../data/derived/hk_official_Z.csv) alone, via
[`code/analyses/reproduction_20261002/scripts/recompute_acat_o.py`](../code/analyses/reproduction_20261002/scripts/recompute_acat_o.py)
(which also ships as a clone gate; see `scripts/verify_from_clone.sh` §5). The same sqrt(N) weighting
independently governs the `Z_multi_tissue` column of Table S3 (Stouffer), which matches to four
decimals — so the convention is not inferred from S6 alone.

**Consequence for the manuscript is discharged.** Table 1's housekeeping arm is **0.0 % (0/87)**,
and re-deriving the FDR calls from the shipped Z layer returns **0/87** as well (most significant
gene-phenotype test: GOLGA3 / DR, ACAT-O P = 0.0126, BH q = 1.00). The arm therefore reproduces
whether or not the ACAT-O rule is settled. The instruction to re-check the tables that aggregate the
housekeeping arm (S7, S19, S26) against the corrected layer is discharged for the arm itself.

---

## 5. GAP register — what is missing, and whether it can be recovered

A bounded search of the local disk found the surviving scripts living in **session working directories that are not archived**. They fall into two classes, and the distinction determines whether recovering them helps:

**Class 1 — genuine computation (recovered 2026-10-02, in [`../code/analyses/recovered/`](../code/analyses/recovered/README.md)).** These take explicit inputs and derive the published values. `tost_ci_calculator.py` and `tost_and_newcombe.py` were run and **reproduce** the published TOST p-values and Newcombe intervals. `scz_arm_recount_si_fix.py` recomputes from `data/derived/scz_z_4arm.csv`.

**Class 2 — `.docx` editors carrying hard-coded literals (recovered to [`../code/deprecated/si_editors/`](../code/deprecated/si_editors/README.md)).** These read **no data at all**; the numbers appear as English prose literals in the source. The workflow was *compute elsewhere → paste the numbers into a patching script → write them into the Supporting Information*. Recovering them documents **what was published and when**, but does not make those tables reproducible.

⚠️ **This is the sharper finding of the two.** Several gaps are not "the script got lost" but "the number was pasted in from somewhere that was never captured". Searching for a missing script will not close them; the value has to be re-derived from first principles.

| # | Item(s) | What is missing | Recoverable? |
|---|---|---|---|
| GAP-1 | S6 (+ Table 1 housekeeping layer) | the corrected computation | ✅ **Closed 2026-10-03, in full** — the corrected layer was never lost: it is the official MetaXcan v0.8.1 recompute of 2026-09-16, still on disk. All 159 numeric Z cells reproduce (max diff 5.0 x 10^-5), the model-SNP column is 30/30, and the ACAT-O combined-P column reproduces **87/87** under the sqrt(N)-weighted Cauchy rule. The layer now ships as `data/derived/hk_official_Z.csv` |
| GAP-2 | Table 1 (values) | aggregation across the three control layers | ✅ **Closed 2026-10-03** — the housekeeping arm is **0.0 % (0/87)** and re-derives from the shipped layer (BH over 87 tests: 0 significant; most significant GOLGA3/DR, P = 0.0126). The S9 and other arms were already closed 2026-10-02 |
| GAP-3 | Table 2(B) | arm join (dual / panel-only / tissue-only) | ✅ **Closed 2026-10-02** — the join ships as `code/analyses/reproduction_20261002/scripts/recompute.py` and reproduces all four arms |
| GAP-4 | Fig. S1, Fig. S2, Fig. 1 | figure scripts | 🟡 **Partly closed 2026-10-03** — the surviving generators were found in un-archived working directories and now ship in `code/figures/recovered/`: `gen_figs4.py` produces the Fig. S2 violin and matches the published universe (61 genes, 24/24/13; medians 374/632/669); `rebuild_fig1_2_9.py` holds `figure1()` (the framework = main Fig. 1) and `figure2()` (the flowchart = Fig. S1), but its `> 75 %` box reads `66.4-70.1 %` where the published SI prints `66.1-68.2 %` — the published box was pixel-edited on 2026-10-01, so Fig. S1 is recovered **structurally** only. Fig. S4 remains a photograph with no script |
| GAP-5 | S27, S28, S29 (+ Note S5) | simulation scripts; only the split-half null is shipped | ✅ **Closed 2026-10-02** — the generator is recovered and re-run; all 84 values reproduce |
| GAP-6 | S7 | — | ✅ **Closed 2026-10-03.** The table's own note defines the column: *"the smallest m for which that row's 90% interval lies wholly inside ±m, i.e. max(\|lower\|, \|upper\|) of the operative interval"*. It is a deterministic function of the interval the recovered calculators already reproduce — GTEx max(1.5, 7.3) = **7.3**; eQTLGen max(2.6, 10.4) = **10.4**; pooled gene-cluster max(0.7, 6.4) = **6.4**. All three match |
| GAP-7 | S9 | architecture-unselected control pipeline | ✅ **Closed 2026-10-02** — rebuilt onto `data/derived/` by `scripts/r3/recompute_r3_s9_s20.py`; whole table reproduces. The pool **re-derivation** also runs from a clone, via the shipped model-SNP projection. The retired `data/superseded/hk_reselect_20260830/` outputs are **not** used |
| GAP-8 | S10 | DN cross-population check | ✅ **Closed 2026-10-03** — the official MetaXcan run of ebi-a-GCST90018832 (Sakaue 2021) under eQTLGen weights still exists on disk and reproduces all five genes: RNH1 −0.8317 (P 0.4056), CKAP4 −0.8563 (0.3918), HSP90AB1 −0.8976 (0.3694), RPS14 +1.2655 (0.2057), EEF2 −0.4605 (0.6451) — every value matches the published table at its printed precision. The layer now ships as `data/derived/dn_cross_population.csv`. The peer-review item **M3** is **verified already implemented** in the current revision (2026-10-03), not outstanding: the S10 note carries the full composition and the Limitations sentence distinguishes the partition's GWAS from the descriptive check |
| GAP-9 | S16 | framework-layer contrast | ✅ **Closed 2026-10-02** — all 9 rows reproduced by `scripts/recompute_scz.py` |
| GAP-10 | S17 | cluster-aware uncertainty | ✅ **Closed 2026-10-02** — rebuilt from `data/derived/primary_arm_96pairs.csv`; every published value reproduced, including the two-arm rate difference. The retired `code/deprecated/s1_cluster_robustness/` code was **not** reused, as its own README requires |

**Recommended action before the first release:** GAP-1 and GAP-2 are now closed (2026-10-03) — the corrected housekeeping layer was found on disk as the official MetaXcan recompute of 2026-09-16 and now ships as `data/derived/hk_official_Z.csv`, and Table 1's housekeeping arm (0/87) re-derives from it. GAP-4 has been partly recovered (the surviving generator scripts are now shipped — see `figures/README.md`). The ACAT-O combination rule that was the last sub-item of GAP-1 is also settled — it is the sqrt(N)-weighted Cauchy combination (Nerve_Tibial 532, Whole_Blood 670), under which S6 reproduces 87/87 and S3 138/138. M3 was verified already implemented in the current revision on 2026-10-03. What remains is the Zenodo DOI placeholder, which needs a release rather than an edit. Do not leave the residue implicit.

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
| The Table S9 inputs — the mashr databases, the six official MetaXcan GTEx × FinnGen tables, the eQTLGen random-control run, `groups.json` — were not uploaded | The official GTEx × FinnGen layer ships flattened and precision-preserving (0.7 MB); the pools, strata and random controls ship as 12 small files; and the mashr side is reduced to the one column the pool filters read, shipped as `mashr_nsnps.csv.gz` (0.06 MB). **Neither the published numbers nor the re-derivation now need the 10.5 MB mashr databases or the 12.3 MB of originals** — `build_pools()` was run with every source variable unset and emitted the pool files byte-identically |
| `metadata/provenance.json` registered 36 files against a tree of 281, so a 59-file package could be committed without appearing in it at all | It now hashes **every tracked file**; `scripts/cut_release.sh` asserts `len(files) + len(excluded) == git ls-files`; and the non-redistributed inputs are recorded separately with their SHA-256 |
| Three diagnostic scripts could not run at all, for reasons independent of the paths | `repo_crosscheck/verify_cluster3.py` built a 0-d array with `np.array(generator)`; `verify_cluster4.py` indexed a positional list by gene name; `r3/diag_s9_s20b.py` exec'd its sibling through the working directory. All 18 diagnostic scripts now exit 0 |
| No self-contained way to check a single reported number | [`../code/analyses/reproduction_min/`](../code/analyses/reproduction_min/) — one script, `data/derived/` and numpy only, no argument, no `.docx`. Reproduces the headline 66/96 = 68.75% and ρ = 0.38964, the per-phenotype split, the tissue-only arm and the three SCZ arms; **15 assertions, 0 mismatches** |
| The integrity table that was supposed to make the archive checkable **failed for every reader**: 11 of the 20 shipped inputs carried the author's CRLF hashes while the rest carried LF ones, so `paths_config.py` printed *all shipped inputs present and byte-exact* locally and `MD5 MISMATCH` in a clone | Found by cloning `--no-hardlinks` and running the self-check inside the clone. The whole tree is now normalised to LF (`i/lf w/lf` for all 302 text files) and every recorded hash is the checked-out one, with a note saying to re-record only from a clone |
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

# INPUTS.md — what these scripts read, and where each input comes from

Every input path in this package resolves through `paths_config.py`. Nothing is
hard-coded: `code/README.md` rule 3 forbids absolute paths and personal
directories, and this file is the manifest that rule implies.

Configure once (or per run, via the flags in section C):

```bash
export TWAS_REPO=/path/to/your/clone        # default: first ancestor with .zenodo.json
export REPRO_SI_DOCX=/path/to/Supporting_Information.docx
export REPRO_MS_DOCX=/path/to/Manuscript.docx
python paths_config.py                      # prints every resolved path and self-checks MD5s
```

---

## A. Inputs that ship with this repository

`python paths_config.py` prints these and verifies each MD5. All are under
`data/derived/`.

| Logical name | File | MD5 | Bytes | Read by |
|---|---|---|---|---|
| `scz_z_4arm` | `scz_z_4arm.csv` | `b444a5d3652ff39d6a5723e96e2dce38` | 662,091 | `recompute_scz.py` |
| `gtex_Z` | `gtex_Z.csv` | `ac3e910b8e4da941f1bb71c5d2ccd018` | 12,990 | `repo_crosscheck/`, `recompute.py` |
| `eqtlgen_Z` | `eqtlgen_Z.csv` | `a63773d394308cfbdbf9c8c4ed8e9385` | 15,653 | `repo_crosscheck/`, `recompute.py` |
| `gene_groups` | `gene_groups.csv` | `f3f5ceda42cacadc5f78cec0f0899d12` | 5,610 | `repo_crosscheck/` |
| `primary_arm` | `primary_arm_96pairs.csv` | `95ad96362314861ce110610a66ffac39` | 2,842 | `repo_crosscheck/`, `r2_fix/` |
| `crosscohort` | `crosscohort.csv` | `48c6012874f83fdc959432603fbc457f` | 831 | `repo_crosscheck/` |
| `hk_genes` | `hk_genes.txt` | `eb7c1a1156029e4118cb003f3be41178` | 1,468 | — |
| `ukb_dr_dir` | `ukb_dr/` (4 files) | — | — | `recompute.py` (Table S5a/S5b) |
| `genomewide/eqz_full.csv.gz` | eQTLGen whole-blood Z, genome-wide | `5c69596eb9e508123fb6cdd7948eda00` | 136,150 | `recompute_scz.py` |
| `genomewide/gtex_official_Whole_Blood.csv.gz` | GTEx v8 MASHR Whole_Blood Z | `7775c350817879cdf55feddd9c59c5b0` | 691,052 | `recompute_scz.py` |
| `genomewide/gtex_official_Nerve_Tibial.csv.gz` | GTEx v8 MASHR Nerve_Tibial Z | `d16dac23cd360274c557c0b1dcfd6d4c` | 857,050 | `recompute_scz.py` |
| `genomewide/en_official_en_Whole_Blood.csv.gz` | GTEx v8 elastic-net Whole_Blood Z | `a076675dea8c74347179c83e6d31cbb4` | 490,098 | `recompute_scz.py` |
| `genomewide/en_official_en_Nerve_Tibial.csv.gz` | GTEx v8 elastic-net Nerve_Tibial Z | `d320ccb64ddb7a8dd243a78751527937` | 672,935 | `recompute_scz.py` |
| `gtex_official_wide` | `gtex_official_finngen/gtex_official_zscores_wide.csv.gz` | `5c19740b0445e70d13936e939d5af558` | 735,045 | `r3/recompute_r3_s9_s20.py` |
| `covariate_matrix` | `covariate_matrix.csv` | `0f6088e1d53fd061f4ced40940dbf6c1` | 6,628 | `r3/recompute_r3_s9_s20.py` |
| `hrt_source` | `hrt/Human_Mouse_Common.csv` | `bf1d7bcdc6b4def62dd0eafcdd1085e4` | 16,486 | `r3/recompute_r3_s9_s20.py` |
| `rand_dr` / `rand_dn` / `rand_dpn` | `hrt_random_control/official_rand_{DR,DN,DPN}.csv` | `f15a051a…` / `f89401fa…` / `39580903…` | 8,106 / 8,101 / 8,113 | `r3/recompute_r3_s9_s20.py` |
| `pool_a` / `both_a` / `pool_818` / `both_818` | `s9_pools/*.txt` | `e288ce3e…` / `b462e42c…` / `5b83bf85…` / `46e6d133…` | 92,559 / 81,315 / 5,896 / 5,525 | `r3/recompute_r3_s9_s20.py` |
| `disease_blacklist` | `s9_pools/disease_blacklist.txt` | `7aba29c67430e2a6982cd464e9a33391` | 988 | `r3/recompute_r3_s9_s20.py` |

The block from `genomewide/eqz_full.csv.gz` down was added on **2026-10-02** and is
built by [`00_build_added_derived.py`](00_build_added_derived.py) from the sources in
section B. Every one is a *processed table a reported number depends on*, which is
what `data/README.md` says `derived/` is for.

---

### A.1 The retired name `data/processed_officialZ/`

The scripts originally read a **second local clone of a different repository**
(`eqtl-source-discordance-audit`) at `data/processed_officialZ/`. That directory has never
existed in this repository, yet the tree referenced it 56 times. Two things now resolve it:
`paths_config.OFFICIAL_Z_RENAME` maps the five renamed files onto `data/derived/`, and
[`../../../data/processed_officialZ/README.md`](../../../data/processed_officialZ/README.md)
is a redirect for the references that remain in historical documents — the predecessor
README and the dated audit notes — where the old name is part of the record.

**Verified directly, 2026-10-02.** The predecessor repository
[`wu-yijing/eqtl-source-discordance-audit`](https://github.com/wu-yijing/eqtl-source-discordance-audit)
was cloned and its `data/processed_officialZ/` compared file by file: **6 of 6 are
byte-identical (same MD5, same length)** to `data/derived/`. The mapping is a measurement,
not an inference:

| Predecessor `data/processed_officialZ/` | Here | MD5 (both) |
|---|---|---|
| `scz_z_4arm_official.csv` | `data/derived/scz_z_4arm.csv` | `55caa68e5015a43c98f19a0556c40dd2` |
| `gtex_official_Z.csv` | `data/derived/gtex_Z.csv` | `9b8520dda0a689533ae778a431e1561d` |
| `eqtlgen_official_Z.csv` | `data/derived/eqtlgen_Z.csv` | `0e99cfce14d7216d46ef261f794ba35a` |
| `gene_groups_TableS1_official.csv` | `data/derived/gene_groups.csv` | `5fe2e3f520222899b4a7a253c4bdf3ff` |
| `primary_arm_96pairs_official.csv` | `data/derived/primary_arm_96pairs.csv` | `fc437aee0925c8b78925fae3fdf914a3` |
| `crosscohort_TableS4_official.csv` | `data/derived/crosscohort.csv` | `20b5da3ba7cc0899b8592b63881cbe34` |

---

## B. Inputs that do NOT ship here, and how to get them

`data/README.md` does not redistribute third-party raw inputs, and the submitted
documents belong to the journal. Each item below carries the MD5 and byte count of
the file that produced the numbers in `results/`, so a run either matches or says so.

### B.1 The submitted documents (3 files)

| Logical name | File | MD5 | Bytes | Env var | Read by |
|---|---|---|---|---|---|
| `manuscript` | `Manuscript_GenetEpidemiol_20260930.docx` | `dbbe4f81a6fe9433b6a28019c6538eab` | 30,524 | `REPRO_MS_DOCX` | `recompute.py`, `bmc_ref/` |
| `si` | `Supporting_Information_GenetEpidemiol_20260930.docx` | `bd50b7f819db7851c50ddfa76ae336eb` | 1,462,835 | `REPRO_SI_DOCX` | `recompute.py`, `r3/`, `repo_crosscheck/`, `bmc_ref/` |
| `af1` | `Additional file 1_审稿意见修订_20260917.docx` | — | — | `REPRO_AF1_DOCX` | `r3/m15/m15_pc.py` |

Obtain them from the journal (they accompany the submission). `bmc_ref/` has two
further, optional documents — the predecessor BMC submission (`REPRO_PRED_MS_DOCX`,
`REPRO_PRED_AF1_DOCX`) — used only for the cross-check between the two manuscripts.

> The Supporting Information is read **directly from the `.docx`** by
> `paths_config.si_tables()`. An earlier version of this package depended on
> `tNN.tsv` files pre-extracted into a session directory; those are gone.
> Table object *i* is `Table S(i+1)` throughout the document (31 objects, S1–S30).

### B.2 The mashr eQTL model databases (2 files, 10.5 MB)

| File | MD5 | Bytes |
|---|---|---|
| `mashr_Whole_Blood.db` | `1613d73c3fcc53a27dc1422118680b97` | 4,612,096 |
| `mashr_Nerve_Tibial.db` | `9983e7b1557230162331839acf5ed228` | 5,910,528 |

Env var `REPRO_MASHR_DB_DIR`. Needed only by `r3/recompute_r3_s9_s20.py`, and only
to **rebuild** the Table S9 pools from scratch. The pool *membership* ships in
`data/derived/s9_pools/`, so the script runs without these files; setting the
variable switches it to route 1 and cross-checks the two routes gene by gene.

These are third-party model layers, so `data/README.md` keeps them out of git.

### B.3 The official MetaXcan GTEx × FinnGen tables (6 files, 12.3 MB)

`official_{Nerve_Tibial,Whole_Blood}_{DR,DN,DPN}.csv`, env var
`REPRO_GTEX_OFFICIAL_DIR`. Needed only by `r3/recompute_r3_s9_s20.py`, and only to
read the per-gene Z in their original form. The shipped wide table
(`gtex_official_wide`) is a flattening of exactly these six files, one row per gene,
and the two routes have been verified to give identical Table S9 numbers. The six
files themselves are the output of `code/run_spredixcan.sh` (official MetaXcan
v0.8.1) and can be regenerated from the pinned third-party inputs in
`data/README.md`.

### B.4 The five genome-wide weight-source layers

Already shipped (section A). `00_build_added_derived.py` reads them from
`REPRO_T1_DIR` if you hold the upstream layout; that variable is only needed to
rebuild, never to reproduce.

---

## C. Command-line overrides

Every script in the package accepts these; `paths_config.apply_cli_overrides()`
maps them onto the environment variables above.

| Flag | Environment variable |
|---|---|
| `--repo-root` | `TWAS_REPO` |
| `--ms-docx` | `REPRO_MS_DOCX` |
| `--si-docx` | `REPRO_SI_DOCX` |
| `--af1-docx` | `REPRO_AF1_DOCX` |
| `--mashr-db-dir` | `REPRO_MASHR_DB_DIR` |
| `--gtex-official-dir` | `REPRO_GTEX_OFFICIAL_DIR` |

`TWAS_DATA_Z` overrides the authoritative data layer (default
`<TWAS_REPO>/data/derived`), matching `code/figures/paths_config.py`.

---

## D. Which script needs what

| Script | Shipped inputs | Documents | Optional bulk layers |
|---|---|---|---|
| `scripts/recompute.py` | `ukb_dr/` | manuscript, SI | — |
| `scripts/recompute_scz.py` | `scz_z_4arm`, 5 × `genomewide/` | — | — |
| `scripts/r3/recompute_r3_s9_s20.py` | `covariate_matrix`, `hrt_source`, `rand_*`, `pool_*`, `disease_blacklist`, `gtex_official_wide` | SI | mashr DBs, GTEx official ×6 |
| `scripts/r3/simulation_validation.py` | **none** | — | — |
| `scripts/r3/m15/m15_pc.py` | — | af1 | — |
| `scripts/repo_crosscheck/*` (13) | `gtex_Z`, `eqtlgen_Z`, `gene_groups`, `primary_arm` | SI (2 of them) | — |
| `scripts/bmc_ref/*` (8) | `primary_arm` | SI, manuscript, pred_manuscript, pred_af1 | — |
| `scripts/r2_fix/*` (2) | `primary_arm` | — | — |

---

## E. What reproduces from the repository alone

With only a clone — no journal documents, no third-party layers — the following
reproduce in full:

| Quantity | Value | Script |
|---|---|---|
| Headline direction consistency | 66/96 = 68.75 % | `scripts/recompute_scz.py` is not needed; compute from `data/derived/primary_arm_96pairs.csv` |
| Headline Spearman ρ | 0.38964 | as above |
| Per-phenotype | DR 23/32, DN 21/32, DPN 22/32 | as above |
| tissue-only arm | n = 138, k = 91, 65.9 %, ρ = +0.4138 | as above |
| Table S24 three SCZ arms | 5,584 / 5,551 / 5,506; ρ +0.4690 / +0.4199 / +0.4465 | `scripts/recompute_scz.py` |
| Table S16 framework layer (9 rows) | ρ +0.7970 … +0.6380 | `scripts/recompute_scz.py` |
| Table S17 empirical null | 9,048 genes, 3,617 pairs, 54.94 % | `scripts/recompute_scz.py` |
| Table S27–S29 | 84 values | `scripts/r3/simulation_validation.py` |

Requiring one of those: Table S17's gene-cluster rows and Table S20 (both read the SI
`.docx`), and the two main-text tables read out of the `.docx`.

**Table S9 does not appear in that sentence, and deliberately so.** Its published values —
the exclusion chain, `POOL_818`, the coverage counts, the 16 random-control rates, the 8
null-distribution values, the 4 percentiles and the in-pool strata — all reproduce from a
clone plus the SI `.docx`, because the pool *membership* ships as
`data/derived/s9_pools/*.txt` and the official GTEx × FinnGen layer ships flattened as
`gtex_official_finngen/gtex_official_zscores_wide.csv.gz`. What still needs the mashr
databases is only **re-deriving the pools from scratch**; that is `00_build_added_derived.py`,
not the reproduction, and it is the one thing on this page a reader cannot do without the
third-party models. Verified 2026-10-02 with `REPRO_MASHR_DB_DIR` unset:

```
1. 池构建
  来源: 随仓库分发的池名单 data/derived/s9_pools/*.txt
  POOL_A = 11,820（SI: 11,820），其中双组织 10,450（SI: 10,450）
  POOL_818 = 818（SI: 818），其中双组织 767（SI: 767），仅 WB 51（SI: 51）
2. 官方 GTEx v8 逐基因 ACAT-O
  来源: data/derived/gtex_official_finngen/gtex_official_zscores_wide.csv.gz
  600 样本中官方覆盖 = 568（SI 表注: 568）；818 池中覆盖 = 768（SI: 768）
```

---

## F. Known quirk carried over deliberately

`s9_pools/disease_blacklist.txt` is written **verbatim**, without case
normalisation. The gene sets it is subtracted from are upper-cased, so a token
whose spelling is not already all-caps excludes nothing. Exactly one token is
affected — `C5orf67` — and that is why the published POOL_A is **11,820** rather
than 11,819, and `both_A` is 10,450 rather than 10,449. The reproduction keeps the
original behaviour; the discrepancy is a property of the published pipeline, not of
this package.

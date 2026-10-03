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
| `mashr_nsnps` | `mashr_nsnps.csv.gz` | `e3b549b55a509ed211e28245f316044d` | 62,725 | `00_build_added_derived.py` (pool **re-derivation**) |
| `ukb_dr_dir` | `ukb_dr/` (4 files) | — | — | `recompute.py` (Table S5a/S5b) |
| `genomewide/eqz_full.csv.gz` | eQTLGen whole-blood Z, genome-wide | `5c69596eb9e508123fb6cdd7948eda00` | 136,150 | `recompute_scz.py` |
| `genomewide/gtex_official_Whole_Blood.csv.gz` | GTEx v8 MASHR Whole_Blood Z | `7775c350817879cdf55feddd9c59c5b0` | 691,052 | `recompute_scz.py` |
| `genomewide/gtex_official_Nerve_Tibial.csv.gz` | GTEx v8 MASHR Nerve_Tibial Z | `d16dac23cd360274c557c0b1dcfd6d4c` | 857,050 | `recompute_scz.py` |
| `genomewide/en_official_en_Whole_Blood.csv.gz` | GTEx v8 elastic-net Whole_Blood Z | `a076675dea8c74347179c83e6d31cbb4` | 490,098 | `recompute_scz.py` |
| `genomewide/en_official_en_Nerve_Tibial.csv.gz` | GTEx v8 elastic-net Nerve_Tibial Z | `d320ccb64ddb7a8dd243a78751527937` | 672,935 | `recompute_scz.py` |
| `gtex_official_wide` | `gtex_official_finngen/gtex_official_zscores_wide.csv.gz` | `5c19740b0445e70d13936e939d5af558` | 735,045 | `r3/recompute_r3_s9_s20.py` |
| `covariate_matrix` | `covariate_matrix.csv` | `5efef7f83d3b8808eb0a0e7492bc0e0e` | 6,523 | `r3/recompute_r3_s9_s20.py` |
| `hrt_source` | `hrt/Human_Mouse_Common.csv` | `8403fef37ede36089b4a32b7ef95bae9` | 15,355 | `r3/recompute_r3_s9_s20.py` |
| `rand_dr` / `rand_dn` / `rand_dpn` | `hrt_random_control/official_rand_{DR,DN,DPN}.csv` | `58985581…` / `951d7a62…` / `77885fdc…` | 8,050 / 8,045 / 8,057 | `r3/recompute_r3_s9_s20.py` |
| `pool_a` / `both_a` / `pool_818` / `both_818` | `s9_pools/*.txt` | `83f9895b…` / `906bbc67…` / `b080de50…` / `d61bf5c2…` | 80,739 / 70,865 / 5,078 / 4,758 | `r3/recompute_r3_s9_s20.py` |
| `disease_blacklist` | `s9_pools/disease_blacklist.txt` | `1a150a298639bc9122fafbea9df68fc5` | 844 | `r3/recompute_r3_s9_s20.py` |

> **The MD5s above are the hashes of the files as a fresh clone checks them out**, i.e. with LF
> endings. They are deliberately *not* the hashes of the author's original CRLF copies: the two
> differ by exactly one byte per line, and the first version of this table recorded the CRLF values
> for the newly added inputs while recording the LF values for the older ones. The result was that
> `paths_config.check_shipped()` passed on the machine that built the package and **failed for every
> reader who cloned it** — 11 of the shipped inputs reported `MD5 MISMATCH`. Found on 2026-10-02 by
> cloning and running `python paths_config.py` inside the clone; the whole tree is now normalised to
> LF and the values above are the checked-out ones. Re-record them only from a clone.

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
byte-identical line for line** to `data/derived/`. The mapping is a measurement,
not an inference. Note that the predecessor repository stores these files with CRLF endings, so the
MD5s quoted below differ from this archive's LF ones by exactly one byte per line — the *content* is
the same file; see the note under the section A table for why that distinction is load-bearing:

| Predecessor `data/processed_officialZ/` | Here | MD5 in the predecessor (CRLF) |
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
| `manuscript` | `Manuscript_GenetEpidemiol_20260930.docx` | `a6f7521b98efa0e2ef247664e2f0db3a` | 30,523 | `REPRO_MS_DOCX` | `recompute.py`, `bmc_ref/` |
| `si` | `Supporting_Information_GenetEpidemiol_20260930.docx` | `bd50b7f819db7851c50ddfa76ae336eb` | 1,462,835 | `REPRO_SI_DOCX` | `recompute.py`, `r3/`, `repo_crosscheck/`, `bmc_ref/` |
| `af1` | `Additional file 1_审稿意见修订_20260917.docx` | — | — | `REPRO_AF1_DOCX` | `r3/m15/m15_pc.py` — **optional since 2026-10-03.** The four tables S20's generator reads (S1, S2, S15, S18) also ship as `data/derived/{gene_groups,gtex_Z,eqtlgen_Z}.csv`, verified row for row identical to the document (104/104, 222/222, 90→81/81, 207/207, zero differing cells). Supply the document and it is used instead |

> **The manuscript hash changed on 2026-10-03, and only because of reference [39].**
> The revision that produced the archived `results/` carried MD5
> `dbbe4f81a6fe9433b6a28019c6538eab` (30,524 bytes). The revision now on disk is
> `a6f7521b98efa0e2ef247664e2f0db3a` (30,523 bytes) — one byte shorter, because reference [39]'s
> repository URL was repointed from the predecessor `…-audit` to this canonical repository.
> **No number in the manuscript or in the Supporting Information moved**, and the Supporting
> Information still matches its recorded hash exactly, so the archived results stand as published.
> The earlier value is recorded here rather than deleted, because a reader running against the
> pre-repoint file should get an explanation rather than a bare mismatch:
>
> | Revision of the manuscript | MD5 | Bytes | Difference |
> |---|---|---|---|
> | Before the [39] repoint (produced `results/`) | `dbbe4f81a6fe9433b6a28019c6538eab` | 30,524 | — |
> | Current (submitted) | `a6f7521b98efa0e2ef247664e2f0db3a` | 30,523 | reference [39] only |

Obtain them from the journal (they accompany the submission). `bmc_ref/` has two
further, optional documents — the predecessor BMC submission (`REPRO_PRED_MS_DOCX`,
`REPRO_PRED_AF1_DOCX`) — used only for the cross-check between the two manuscripts.

> The Supporting Information is read **directly from the `.docx`** by
> `paths_config.si_tables()`. An earlier version of this package depended on
> `tNN.tsv` files pre-extracted into a session directory; those are gone.
> Table object *i* is `Table S(i+1)` throughout the document (31 objects, S1–S30).

### B.2 The mashr eQTL model databases (2 files, 10.5 MB) — **optional as of 2026-10-02**

| File | MD5 | Bytes |
|---|---|---|
| `mashr_Whole_Blood.db` | `1613d73c3fcc53a27dc1422118680b97` | 4,612,096 |
| `mashr_Nerve_Tibial.db` | `9983e7b1557230162331839acf5ed228` | 5,910,528 |

Env var `REPRO_MASHR_DB_DIR`.

The pool filters read **one** column out of these files — `n.snps.in.model`, per gene, for two
tissues. That projection now ships as `data/derived/mashr_nsnps.csv.gz` (61 kB, section A), so
**nothing in this repository requires the databases any more**, including the pool
re-derivation. Set the variable anyway and `load_model_snps()` reads both databases as well and
refuses to continue unless every gene and every count agrees with the projection — a projection
that had silently drifted from the models it summarises would otherwise keep reproducing the
published chain while standing for nothing.

These are third-party model layers, so `data/README.md` keeps them out of git. Regenerating the
projection is the only operation that needs them.

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
| `scripts/r3/recompute_r3_s9_s20.py` | `covariate_matrix`, `hrt_source`, `rand_*`, `pool_*`, `disease_blacklist`, `gtex_official_wide`, `mashr_nsnps` | SI | mashr DBs (cross-check only), GTEx official ×6 (rebuild only) |
| `scripts/r3/simulation_validation.py` | **none** | — | — |
| `scripts/r3/m15/m15_pc.py` | — | af1 (optional since 2026-10-03; falls back to `data/derived/`) | — |
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
`gtex_official_finngen/gtex_official_zscores_wide.csv.gz`. **Re-deriving the pools from
scratch is also a clone-only operation as of 2026-10-02**: the mashr model databases were
10.5 MB of SQLite from which the pool filters read exactly one column, and that column now
ships as `data/derived/mashr_nsnps.csv.gz` (61 kB). Verified 2026-10-02 with every source
variable unset — `build_pools()` emitted all four pool files byte-identically and printed:

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

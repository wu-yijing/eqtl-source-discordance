# INPUTS — every input of the reproduction package, and whether it ships here

**Purpose.** After commit `91afa33` a third party could not run a single script in this
package: 27 of the 35 carried the author's own absolute paths, and not one of those paths
pointed into this repository. This file, together with `paths.py`, is the fix. Every input
is named once, here; `paths.py` resolves it; no script holds a host path.

**MD5 provenance.** Those marked *(log)* are copied from the run logs in `results/`, i.e.
they are the hashes the scripts themselves printed when they produced the archived numbers.
The rest were computed from the author's original copies, which were located so that the
package could be re-run and this file could be complete rather than aspirational. No hash
here is invented.

```
python scripts/recompute.py --list-inputs        # what this checkout can and cannot resolve
```

---

## 1. Distributed — ships in this repository

These resolve from the repository root with nothing supplied. They are the layer the
manuscript's headline numbers rest on.

| Logical name (`paths.derived(...)`) | Path | MD5 | Bytes |
|---|---|---|---|
| `gtex_Z` | `data/derived/gtex_Z.csv` | `9b8520dda0a689533ae778a431e1561d` | 13,213 |
| `eqtlgen_Z` | `data/derived/eqtlgen_Z.csv` | `0e99cfce14d7216d46ef261f794ba35a` | 15,942 |
| `gene_groups` | `data/derived/gene_groups.csv` | `5fe2e3f520222899b4a7a253c4bdf3ff` | 5,715 |
| `primary_arm_96pairs` | `data/derived/primary_arm_96pairs.csv` | `fc437aee0925c8b78925fae3fdf914a3` | 2,939 |
| `crosscohort` | `data/derived/crosscohort.csv` | `20b5da3ba7cc0899b8592b63881cbe34` | 836 |
| `scz_z_4arm` | `data/derived/scz_z_4arm.csv` | `55caa68e5015a43c98f19a0556c40dd2` | 677,967 |
| `hk_genes` | `data/derived/hk_genes.txt` | `c833bc29635ff5343cbc7732e63208d9` | 1,517 |
| `ukb_dr_dir` | `data/derived/ukb_dr/` (4 data files) | see below | — |
| `m15_json` | `code/figures/m15_positive_control.json` | `ba8bdc92eef814370378904ad2049257` | 16,985 |
| `covariate_matrix` | `data/superseded/covariate_matrix.csv` | `0f6088e1d53fd061f4ced40940dbf6c1` *(log)* | 6,628 |
| `human_mouse_common` | `data/superseded/hk_reselect_20260830/data/Human_Mouse_Common.csv` | `bf1d7bcdc6b4def62dd0eafcdd1085e4` *(log)* | 16,486 |

`data/derived/ukb_dr/`:

| File | MD5 | Bytes |
|---|---|---|
| `RNH1_official_metaxcan_Z.csv` | `a86b269851ea0b551ade201dcbc5dcb9` | 401 |
| `finngen_r13_dr_eqtlgen_official.csv` | `b048cc5f51bd1cfefa359296471e0ff2` | 14,281 |
| `ukb_gcst90043640_eqtlgen_official.csv` | `665a080311426f234f909dd407cb3ce0` | 14,455 |
| `ukb_gcst90043640_gtex_Nerve_Tibial_official.csv.gz` | `4b4a63d43063a5d3e89f89d2508375e5` | 893,782 |
| `ukb_gcst90043640_gtex_Whole_Blood_official.csv.gz` | `29fad841062f9ff70d421f80663c2202` | 720,863 |

### Two entries that sit outside `data/derived/`

- **`scz_z_4arm.csv`** — byte-identical (same MD5, same length) to the
  `scz_z_4arm_official.csv` the log records. The "newline difference" recorded in the
  2026-10-02 audit applies to the other derived tables, not this one: the SCZ layer is the
  same file under a shorter name, so `recompute_scz.py`'s MD5 self-check still passes.
- **`covariate_matrix.csv`** — the **one declared exemption**. It exists only in
  `data/superseded/`, and `data/README.md` says values in that layer must never be quoted.
  Nothing here quotes a value from it: S9's pool construction takes only the **104-gene
  panel roster** out of this file, and the roster is a fixed input, not an affected
  quantity. Recorded as an explicit exemption in `data/README.md` (audit P2-7).

---

## 2. Not distributed — supply with `--input NAME=PATH` or the environment variable

These are deliberately absent. `paths.external()` raises a message naming the file and
where it comes from if one is missing.

| Logical name | Env var | MD5 | Bytes | Needed by |
|---|---|---|---|---|
| `manuscript_docx` | `EQTL_MANUSCRIPT_DOCX` | `dbbe4f81a6fe9433b6a28019c6538eab` *(log)* | 30,524 | `recompute.py`, `bmc_ref/` |
| `si_docx` | `EQTL_SI_DOCX` | `bd50b7f819db7851c50ddfa76ae336eb` *(log)* | 1,462,835 | `recompute.py`, `r3/recompute_r3_s9_s20.py`, `bmc_ref/` |
| `t1_full_dir` | `EQTL_T1_FULL_DIR` | see below | ~7.4 MB | `recompute_scz.py` |
| `mashr_dir` | `EQTL_MASHR_DIR` | see below | 10.5 MB | `r3/recompute_r3_s9_s20.py` |
| `groups_json` | `EQTL_GROUPS_JSON` | `37583d2f4f553ab71d6b166a4d0a2b7a` *(log)* | 3,956 | `r3/recompute_r3_s9_s20.py` |
| `t1_s8rand_dir` | `EQTL_T1_S8RAND_DIR` | see below | 24.3 KB | `r3/recompute_r3_s9_s20.py` |
| `metaxcan_run_dir` | `EQTL_METAXCAN_RUN_DIR` | see below | 12.3 MB | `r3/recompute_r3_s9_s20.py` |
| `additional_file1_docx` | `EQTL_ADDITIONAL_FILE1` | `f69a679ab3fe6e2a8ff2f4ab0f5b9722` | 1,494,289 | `r3/m15/m15_pc.py` (**S20**) |
| `si_tables_dir` | `EQTL_SI_TABLES_DIR` | `65658e7e5896ac480dbb2b1ca6986032` (31 files concatenated) | 71,342 | `repo_crosscheck/`, `bmc_ref/` |
| `bmc_manuscript_docx` | `EQTL_BMC_MANUSCRIPT_DOCX` | `17415a48376ea24471e9422da7ec3429` | 91,385 | `bmc_ref/` |
| `bmc_additional_file1_docx` | `EQTL_BMC_ADDITIONAL_FILE1` | `6dc729b1ad790be4f048d67647d54fea` | 1,497,617 | `bmc_ref/` |

### Directory members

`t1_full_dir` — the six gene-level Z files of the full universe:

| File | MD5 | Bytes |
|---|---|---|
| `eqz_full.csv` | `7dd94816629bd19e6bc1eb0a7266be35` *(log)* | 376,658 |
| `gtex/official_Whole_Blood.csv` | `71a2ef9278f7e235cee467721f06d62c` *(log)* | 1,730,684 |
| `gtex/official_Nerve_Tibial.csv` | `ef3ee2e444878f3257e2e03267b6a2d1` *(log)* | 2,139,640 |
| `en/official_en_Whole_Blood.csv` | `8adf895c3cc7c6b89bdfaa5e086f8694` *(log)* | 1,253,372 |
| `en/official_en_Nerve_Tibial.csv` | `c6f46b04527c8f02606000e401e302e7` *(log)* | 1,707,928 |

`mashr_dir` — the GTEx v8 mashr model databases:

| File | MD5 | Bytes |
|---|---|---|
| `mashr_Whole_Blood.db` | `1613d73c3fcc53a27dc1422118680b97` *(log)* | 4,612,096 |
| `mashr_Nerve_Tibial.db` | `9983e7b1557230162331839acf5ed228` *(log)* | 5,910,528 |

`t1_s8rand_dir` — the eQTLGen random-control run:

| File | MD5 | Bytes |
|---|---|---|
| `official_rand_DR.csv` | `f15a051ad868739259f7191df05a0c62` | 8,106 |
| `official_rand_DN.csv` | `f89401fa280059ab4715b9acd1a7da4f` | 8,101 |
| `official_rand_DPN.csv` | `3958090369cee62a921a1aea077dd2a7` | 8,113 |

`metaxcan_run_dir` — the official MetaXcan v0.8.1 GTEx run, 2 tissues × 3 phenotypes:

| File | MD5 | Bytes |
|---|---|---|
| `official_Nerve_Tibial_DR.csv` | `966e43e6dec03669fdd13ef44b6866d9` | 2,259,160 |
| `official_Nerve_Tibial_DN.csv` | `1dc9106b31369aa5115322bd03fd0b7a` | 2,256,166 |
| `official_Nerve_Tibial_DPN.csv` | `92b942f7437b65bb0dc2658e1eb6bccb` | 2,254,949 |
| `official_Whole_Blood_DR.csv` | `57738c427b957c25a6f455f5ff22c4a0` | 1,837,692 |
| `official_Whole_Blood_DN.csv` | `cce57111298a024b5e9ed5101c048f74` | 1,835,601 |
| `official_Whole_Blood_DPN.csv` | `c4bceab533b56ce928cf4c69e87462d8` | 1,834,688 |

`si_tables_dir` — the 31 tables extracted from the Supporting Information, `t00.tsv`–`t30.tsv`
(71,342 bytes in total). Regenerate from `si_docx` by extracting each table to `tNN.tsv`.

---

## 3. The legacy `data/processed_officialZ/` paths

The scripts originally read a **second local clone of a different repository**
(`eqtl-source-discordance-audit`) at `data/processed_officialZ/`. That directory has never
existed in this repository, yet the tree referenced it 56 times. `paths.py` now maps it:

**Verified directly, 2026-10-02.** The predecessor repository
([`wu-yijing/eqtl-source-discordance-audit`](https://github.com/wu-yijing/eqtl-source-discordance-audit))
was cloned and its `data/processed_officialZ/` compared file by file: **6 of 6 are byte-identical
(same MD5, same length)** to `data/derived/`. The mapping below is a measurement, not an
inference from the 2026-10-02 audit. A redirect for anyone following an older reference lives at
[`../../../data/processed_officialZ/README.md`](../../../data/processed_officialZ/README.md).

| Legacy path | Resolves to | Equivalence established 2026-10-02 |
|---|---|---|
| `data/processed_officialZ/scz_z_4arm_official.csv` | `data/derived/scz_z_4arm.csv` | identical, MD5 `55caa68e…` |
| `data/processed_officialZ/{gtex,eqtlgen}_official_Z.csv` | `data/derived/{gtex,eqtlgen}_Z.csv` | 2,220 / 2,304 cells identical |
| `data/processed_officialZ/gene_groups_TableS1_official.csv` | `data/derived/gene_groups.csv` | identical (31 whitespace-only diffs) |
| `data/processed_officialZ/primary_arm_96pairs_official.csv` | `data/derived/primary_arm_96pairs.csv` | 480 cells identical |
| `data/processed_officialZ/crosscohort_TableS4_official.csv` | `data/derived/crosscohort.csv` | 44 cells identical |
| `data/processed/ukb_dr_official/` | `data/derived/ukb_dr/` | 4 files, all present |
| `data/processed/covariate_matrix.csv` | `data/superseded/covariate_matrix.csv` | identical, MD5 `0f6088e1…` |
| `data/hk_reselect_20260830/data/` | `data/superseded/hk_reselect_20260830/data/` | one `superseded/` level added |
| `Human_Mouse_Common_raw.csv` | `data/superseded/…/Human_Mouse_Common.csv` | byte-identical, MD5 `bf1d7bcd…` |
| `_review/m15_positive_control.json` | `code/figures/m15_positive_control.json` | identical |

---

## 4. What can and cannot be reproduced — read this before trusting a result

| Scope | Reproducible from this archive alone? |
|---|---|
| Everything in `code/analyses/reproduction_min/` — headline, per-phenotype, tissue-only arm, SCZ three arms | **Yes** — one script, `data/derived/` and numpy only, 15 assertions |
| Headline 68.75% / ρ 0.3896, per-phenotype split, tissue-only arm, SCZ three arms | **Yes** — `recompute.py`, `recompute_scz.py`, `data/derived/` only |
| SI S2, S3, S5a, S13, S15, S18, S24; main Table 2(A); S27–S29 and Note S5 | **Yes** |
| **S9** (architecture-unselected random controls) | **No** — needs `mashr_dir`, `groups_json`, `t1_s8rand_dir`, `metaxcan_run_dir` |
| **S16** (framework-layer alternative test) | **No** — needs the elastic-net side of `t1_full_dir`; no elastic-net Z ships here |
| **S17** (cluster-aware uncertainty) | **Partly** — the primary-arm half is reproducible from `data/derived/primary_arm_96pairs.csv`; the gene-cluster half needs the housekeeping layer carried only in the SI `.docx` |
| **S20** (endpoint calibration) | **No** — `m15_pc.py` is shipped, but its input `additional_file1_docx` is not |
| BMC↔GE cross-check | **No** — needs `si_tables_dir`, `bmc_manuscript_docx`, `bmc_additional_file1_docx`. **Re-run and verified 2026-10-02** once those were supplied: 83 statistics checked, 63 in both documents, 0 unique to the GE submission |

The four "No"/"Partly" rows are exactly the rows `metadata/ARCHIVE_MAP.md` marks 🟡 with the
note *"reproduced, but the inputs it rests on are not in this repository"*.

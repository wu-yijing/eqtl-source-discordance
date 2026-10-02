# Reproduction package — Supporting Information and main-text values (2026-10-02)

Third-party reproduction of every reported value that could be read out of the two submitted
documents:

- `Manuscript_GenetEpidemiol_20260930.docx`
- `Supporting_Information_GenetEpidemiol_20260930.docx` (31 tables, S1–S30)

Nothing in this directory is part of the authoritative data layer. It is **evidence of
reproducibility**, produced by scripts that read `data/derived/`, `code/`, and the two documents
above. The authoritative layers remain `data/derived/` and `figures/`.

> ### Revision note — second pass, 2026-10-02
>
> As first committed (`91afa33`) this package was runnable only by its author: **27 of its 35
> scripts carried absolute host paths and not one pointed into this repository.** The most-cited
> of them resolved to a *second local clone of a different repository*
> (`eqtl-source-discordance-audit`), and the tree referenced `data/processed_officialZ/` 56 times
> against a directory that does not exist here.
>
> Every input now resolves through [`paths.py`](paths.py), which defaults to this tree;
> [`INPUTS.md`](INPUTS.md) lists each input with the MD5 recorded in `results/`; the three
> construction-time `_patch*.py` scripts are deleted; and `scripts/cut_release.sh` now fails the
> release if `metadata/provenance.json` does not cover every tracked file.
>
> **One consequence is a status change, not just a code change:** S9, S16 and S17 are no longer
> marked ✅ in `metadata/ARCHIVE_MAP.md`. They *were* reproduced — but the inputs the reproduction
> rests on are **not in this repository**, so a third party cannot re-run them. See
> [§ What cannot be reproduced here](#what-cannot-be-reproduced-here).

## Result

| Grade | Definition | Count |
|---|---|---|
| **R1** | identical at the reported precision | **≈ 200 items** |
| **R2** | point estimate identical; residual is a rounding chain or an undisclosed implementation parameter | **3 items** |
| **R3** | generating script or data absent, and the value not recomputable | **0 items** |

**No reported value failed to reproduce, and no reported value was found to differ in its point
estimate.** The three R2 items and their remediation are set out in
`docs/audit_notes/R2残余差异消除方案_20261002.md`; the full account is in
`docs/audit_notes/复现核验_GE投稿两份文档_20261002.md`.

## What this package changes in `metadata/ARCHIVE_MAP.md`

| SI item | Was | Now | Evidence |
|---|---|---|---|
| **S9** — architecture-unselected random controls | 🔴 GAP-7 | **🟡** | **Reproduced, but the inputs it rests on are not in this repository.** The full table reproduces under `scripts/r3/recompute_r3_s9_s20.py`: exclusion chain 12,622→12,555→11,885→**11,820**, POOL_818 = 818/767/51, coverage 568/768, 16 random-control rates, 8 null-distribution values, 4 percentiles, in-pool strata 21/1,326 · 7/378 · 20/1,827 · 6/477. But the run needs the mashr databases, `groups.json`, `t1_s8rand/` and `metaxcan_run/`, none of which ship here. **Reclassified ✅ → 🟡 on 2026-10-02.** |
| **S16** — framework-layer alternative test | 🔴 GAP-9 | **🟡** | **Reproduced, but the inputs it rests on are not in this repository.** All 9 rows: ρ +0.7970 / +0.8062 / +0.8379 / +0.7842 / +0.4990 / +0.5250 / +0.5820 / +0.6470 / +0.6380 with their CIs. Five of the nine are elastic-net contrasts, and **no elastic-net Z is distributed here**. **Reclassified ✅ → 🟡 on 2026-10-02.** |
| **S17** — cluster-aware uncertainty | 🔴 GAP-10 | **🟡** | **Partly portable.** The primary-arm half reproduces from `data/derived/primary_arm_96pairs.csv`: naive t = 4.1019 (df 94, P = 8.712 × 10⁻⁵); jackknife SE(ρ) = 0.1367; sandwich SE(ρ) = 0.1264 (reported 0.125, inside the self-consistent band 0.12326–0.12719); permutation null −0.218 to +0.232; bootstrap ρ CI [0.1161, 0.6220]; rate CI 58.3–79.2%. **The gene-cluster rows** (two-arm rate difference +2.6649 pp / SE 1.4741 / 95% CI −0.22 to +5.55 / 90% CI +0.24 to +5.09 / Q 0.1357; gene-cluster SE 2.194 → 2.2; 90% CI −0.77 to +6.45 → −0.7 to +6.4; r −0.045 → −0.05) rest on the housekeeping layer carried only inside the SI `.docx`. **Reclassified ✅ → 🟡 on 2026-10-02.** |
| **S27, S28, S29** — simulation validation | 🔴 GAP-5 | ✅ | `simulation_validation.py` re-run: all 84 values identical to the archived `simulation_results.json` at machine precision. Pure synthetic — **no external input, so genuinely portable.** |
| Note S5 — simulation design and results | 🔴 GAP-4 | ✅ | Same run; parameter sets (seed 20260930, G = 32, P = 3, n_pair = 96, ρ_sd = 0.15, n₁ = 3,000, n_rep = 400, B = 500) and all three tables. |
| **S20** — endpoint calibration and positive control | ✅ | ✅ (script added) | `scripts/r3/m15/m15_pc.py` **is** the generator behind `code/figures/m15_positive_control.json`. Re-run verbatim (input/output paths only) reproduces the archived JSON key-for-key to 1 × 10⁻¹², including `PC2b_group_diff_power` = 8.0 / 14.5 / 13.0 / 17.5 pp. ⚠️ Its input, `Additional file 1_审稿意见修订_20260917.docx`, is **not** distributed — the ✅ rests on the JSON, which *is* shipped, not on the script being re-runnable. |
| **Table 2(B)** — two-axis partition | 🟡 | ✅ | `recompute.py` reproduces all four arms from `data/derived/` alone — primary 96 / ρ 0.3896 / 68.75%; panel-only 159 / ρ 0.490 / 71.1%; tissue-only 138 / ρ 0.414 / 65.9%; dual 198 / ρ 0.442 / 67.2%. **Genuinely portable.** |

Also reproduced in full, beyond the map's original scope: the BH q of SI Tables S3 and S18
(eQTLGen 12/12 strata, GTEx 9/9 strata on both the ACAT-O and Stouffer chains, max |Δq| = 0.000),
SI Table S5a (all 16 values across both rows), and the SCZ layer (S24, S23, S21, Table S16 of the
manuscript) including bootstrap interval endpoints.

## What cannot be reproduced here

A reader who clones this repository and nothing else can reproduce the headline chain, Table 2,
S2/S3/S5a/S13/S15/S18/S24, and S27–S29. They cannot reproduce these:

| Item | Blocking input | Ships here? |
|---|---|---|
| S9 — random-control table | `mashr_{Whole_Blood,Nerve_Tibial}.db`, `groups.json`, `t1_s8rand/`, `metaxcan_run/official/` | no — 3 of its 5 inputs |
| S16 — framework-layer contrast | the elastic-net side of the full-universe Z (`en/official_en_*.csv`) | no |
| S17 — **gene-cluster** rows | the housekeeping layer, carried only in the SI `.docx` (its t06/t15 blocks) | no |
| S20 — endpoint calibration | `Additional file 1_审稿意见修订_20260917.docx` | no (the *output* JSON does ship) |
| BMC↔GE cross-check (`bmc_ref/`) | `si_tables/*.tsv`, the predecessor BMC manuscript and Additional file | no |
| The **executable** run of the headline chain | the two submitted `.docx` | no — but the *values* reproduce from `data/derived/`, which does ship |
| SCZ universe beyond S24 (10,357 / 9,048 / 8,890 / 6,310 / 4,098 / 3,910 / 6,014) | `t1_full/` | partly — the SCZ four-arm table ships, the full universe does not |

[`INPUTS.md`](INPUTS.md) §4 carries the same statement; `paths.py` raises a message naming the
file and its source the moment one of these is missing, rather than dying on a `FileNotFoundError`.

## Layout

```
paths.py                          every input this package resolves — read this first
INPUTS.md                         each input, its MD5 (from results/), and whether it ships
scripts/
  recompute.py                    document-level recompute (SI S2/S3/S5a/S6/S13/S15/S18/S23 -> headline chain)
  recompute_scz.py                genome-wide SCZ layer + weight-fitting framework layer
  r3/                             R3 class: SI Tables S9, S20, S27-S29
    simulation_validation.py      verbatim copy of the archived generator for S27-S29
    recompute_r3_s9_s20.py        S9 null distributions and S20 endpoint calibration
    m15/m15_pc.py                 verbatim generator for S20 (from code/figures/m15_positive_control.json lineage)
  repo_crosscheck/                values re-derived from the official MetaXcan Z layer
  bmc_ref/                        cross-check of the two documents against the predecessor 2026-09-28 final manuscript
  r2_fix/                         estimators examined for the three residual R2 items
results/                          machine-readable outputs and run logs for every script above
```

## Running it

Requirements: Python 3.13.12, numpy 2.4.4, scipy 1.17.1, pandas 3.0.3 (and `python-docx` for
`r3/m15/m15_pc.py`). The environment is pinned in [`../../env/requirements.txt`](../../env/requirements.txt).

```
python scripts/recompute.py --list-inputs     # what this checkout can resolve, and what it cannot

python scripts/recompute.py --manuscript <main.docx> --si <si.docx>   # self-checks both MD5s
python scripts/recompute_scz.py --scz-z-dir <dir>                     # ~2 min 40 s
python scripts/r3/simulation_validation.py                            # no input needed
python scripts/r3/recompute_r3_s9_s20.py \
    --input mashr_dir=<dir> --input metaxcan_run_dir=<dir> \
    --input groups_json=<file> --input t1_s8rand_dir=<dir> --si <si.docx>
```

Every script takes `--repo-root` and a repeatable `--input NAME=PATH`; `--list-inputs` prints the
manifest. The three scripts that produce a published number (`recompute.py`, `recompute_scz.py`,
`r3/recompute_r3_s9_s20.py`) print the MD5 of each input on their first line, so a run either
matches the hashes recorded in `results/` or fails loudly. The 22 diagnostic scripts under
`repo_crosscheck/` and `bmc_ref/` do **not** print hashes — they were one-off cross-checks, and
their inputs do not ship.

**Scope of "outside the original working environment".** If the full input set is supplied, this
package runs anywhere: no script refers to a host path. With nothing supplied beyond the
repository, the portable subset is `recompute.py` (given the two `.docx`), `simulation_validation.py`,
and the primary-arm half of `S17`. The table above states which items need more.

## Caveats

- The two `.docx` documents are **not** distributed here (they accompany the submission). The
  scripts that read them now take `--manuscript` / `--si` / `--scz-z-dir`; this README previously
  claimed that and it was untrue.
- Two `R2` items and two parameter-disclosure items remain. They do not change any number's point
  estimate; see the remediation note.
- The reproduction was performed on Windows with a managed Python environment. The MD5 self-checks
  are the mechanism that makes runs comparable across platforms; note that `data/derived/` files
  are checked out with LF and will hash differently from CRLF copies, so compare content, not the
  raw file hash, for the derived tables.
- `results/*_out.txt` are **shell redirection artefacts** — captured stdout of the diagnostic
  scripts. They are not written by the scripts themselves, unlike `recompute_log.txt`,
  `recompute_scz_log.txt` and `recompute_r3_s9_s20_log.txt`, which each script writes. They are
  kept as a trace.

# Reproduction package — Supporting Information and main-text values (2026-10-02)

Third-party reproduction of every reported value that could be read out of the two submitted
documents, run **outside** the original working environment:

- `Manuscript_GenetEpidemiol_20260930.docx`
- `Supporting_Information_GenetEpidemiol_20260930.docx` (31 tables, S1–S30)

Nothing in this directory is part of the authoritative data layer. It is **evidence of
reproducibility**, produced by scripts that read `data/derived/`, `code/`, and the two documents
above. The authoritative layers remain `data/derived/` and `figures/`.

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

## What this closes in `metadata/ARCHIVE_MAP.md`

| SI item | Was | Now | Evidence |
|---|---|---|---|
| **S9** — architecture-unselected random controls | 🔴 GAP-7 | ✅ | Full table reproduced: exclusion chain 12,622→12,555→11,885→**11,820**, POOL_818 = 818/767/51, coverage 568/768, 16 random-control rates, 8 null-distribution values, 4 percentiles, and the in-pool strata 21/1,326 · 7/378 · 20/1,827 · 6/477 |
| **S16** — framework-layer alternative test | 🔴 GAP-9 | ✅ | All 9 rows: ρ +0.7970 / +0.8062 / +0.8379 / +0.7842 / +0.4990 / +0.5250 / +0.5820 / +0.6470 / +0.6380 with their CIs |
| **S17** — cluster-aware uncertainty | 🔴 GAP-10 | ✅ | naive t = 4.1019 (df 94, P = 8.712 × 10⁻⁵); jackknife SE(ρ) = 0.1367; sandwich SE(ρ) = 0.1264 (reported 0.125, inside the self-consistent band 0.12326–0.12719); permutation null −0.218 to +0.232; bootstrap ρ CI [0.1161, 0.6220]; rate CI 58.3–79.2%; and the two-arm rate difference — analytic rows +2.6649 / SE 1.4741 / 95% CI −0.22 to +5.55 / 90% CI +0.24 to +5.09 / Q 0.1357, gene-cluster rows SE 2.194 → 2.2, 90% CI −0.77 to +6.45 → −0.7 to +6.4, r −0.045 → −0.05 |
| **S27, S28, S29** — simulation validation | 🔴 GAP-5 | ✅ | `simulation_validation.py` re-run: all 84 values identical to the archived `simulation_results.json` at machine precision |
| Note S5 — simulation design and results | 🔴 GAP-4 | ✅ | Same run; parameter sets (seed 20260930, G = 32, P = 3, n_pair = 96, ρ_sd = 0.15, n₁ = 3,000, n_rep = 400, B = 500) and all three tables |
| **S20** — endpoint calibration and positive control | ✅ | ✅ (script added) | `scripts/r3/m15/m15_pc.py` **is** the generator behind `code/figures/m15_positive_control.json`. Re-run verbatim (input/output paths only) reproduces the archived JSON key-for-key to 1 × 10⁻¹², including `PC2b_group_diff_power` = 8.0 / 14.5 / 13.0 / 17.5 pp |

Also reproduced in full, beyond the map's original scope: the BH q of SI Tables S3 and S18
(eQTLGen 12/12 strata, GTEx 9/9 strata on both the ACAT-O and Stouffer chains, max |Δq| = 0.000),
SI Table S5a (all 16 values across both rows), and the SCZ layer (S24, S23, S21, Table S16 of the
manuscript) including bootstrap interval endpoints.

## Layout

```
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

Requirements: Python 3.13.12, numpy 2.4.4, scipy 1.17.1, pandas 3.0.3.

```
python scripts/recompute.py            # first block; self-checks the MD5 of both .docx inputs
python scripts/recompute_scz.py        # ~2 min 40 s
python scripts/r3/simulation_validation.py
python scripts/r3/recompute_r3_s9_s20.py
```

Scripts read the two submitted `.docx` files, `data/derived/`, and (for the SCZ and framework
layers) the six gene-level Z files named in the logs. The `repo_crosscheck/` and `bmc_ref/` scripts
additionally read `data/derived/` and the predecessor manuscript; they are diagnostic, and are what
established that the two supplementary files are the same document under two numberings.

Every script prints the MD5 of its inputs on its first line, so a run either matches the recorded
hashes or fails loudly.

## Caveats

- The two `.docx` documents are **not** distributed here (they accompany the submission). Scripts
  that read them take a path argument.
- Two `R2` items and two parameter-disclosure items remain. They do not change any number's point
  estimate; see the remediation note.
- The reproduction was performed on Windows with a managed Python environment; the MD5 self-checks
  are the mechanism that makes the runs comparable across platforms.

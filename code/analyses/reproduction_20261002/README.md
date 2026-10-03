# Reproduction package — Supporting Information and main-text values (2026-10-02)

Third-party reproduction of every reported value that could be read out of the two
submitted documents:

- `Manuscript_GenetEpidemiol_20260930.docx`
- `Supporting_Information_GenetEpidemiol_20260930.docx` (31 tables, S1–S30)

Nothing in this directory is part of the authoritative data layer. It is **evidence
of reproducibility**, produced by scripts that read `data/derived/`, `code/`, and the
two documents above. The authoritative layers remain `data/derived/` and `figures/`.

**Start with [`INPUTS.md`](INPUTS.md)** — every input, its MD5, whether it ships with
this repository, and how to obtain it if it does not.

> **Revision 2026-10-02 (second pass).** An earlier revision of this package carried
> the author's absolute Windows paths, depended on files that were never committed,
> and claimed to run "outside the original working environment" while doing neither.
> All path handling now goes through [`paths_config.py`](paths_config.py) as
> `code/README.md` rule 3 requires; the missing inputs are either shipped or named in
> `INPUTS.md` with the hash that produced the recorded results.

## Result

| Grade | Definition | Count |
|---|---|---|
| **R1** | identical at the reported precision | **≈ 200 items** |
| **R2** | point estimate identical; residual is a rounding chain or an undisclosed implementation parameter | **3 items** |
| **R3** | generating script or data absent, and the value not recomputable | **0 items** |

**No reported value failed to reproduce, and no reported value was found to differ in
its point estimate.** The three R2 items and their remediation are set out in
`docs/audit_notes/R2残余差异消除方案_20261002.md`; the full account is in
`docs/audit_notes/复现核验_GE投稿两份文档_20261002.md`.

## What reproduces from a clone alone

No journal documents, no third-party layers — just `git clone`:

| Quantity | Value |
|---|---|
| Headline direction consistency, ρ, per-phenotype split | 66/96 = 68.75 %; ρ = 0.38964; DR 23/32, DN 21/32, DPN 22/32 |
| tissue-only arm | n = 138, k = 91, 65.9 %, ρ = +0.4138 |
| Table S24, three SCZ arms | 5,584 / 5,551 / 5,506; ρ +0.4690 / +0.4199 / +0.4465 |
| Table S16 framework layer | all 9 rows, ρ +0.7970 … +0.6380 |
| Table S17 empirical null | 9,048 genes, 3,617 pairs, 54.94 % |
| Table S27–S29 | all 84 values |

Everything else needs one of the inputs named in `INPUTS.md` section B.

> **Five minutes, nothing to supply?** Use
> [`../reproduction_min/reproduce_headline.py`](../reproduction_min/reproduce_headline.py). It is a
> single ~180-line script needing only `data/derived/` and numpy — no argument, no `.docx` — and it
> covers the first three rows of the table above with 15 assertions. This directory is the forensic
> package; that one is the self-contained entry point.

## What this closes in `metadata/ARCHIVE_MAP.md`

| SI item | Was | Now | Evidence | Runs from a clone? |
|---|---|---|---|---|
| **Table 2(B)** — two-axis arm join | 🟡 GAP-3 | ✅ | the join is `data/derived/{gtex,eqtlgen}_Z.csv`; all four arms and the 45-gene common universe reproduce | **yes** |
| **S16** — framework-layer alternative test | 🔴 GAP-9 | ✅ | all 9 rows with their CIs, from the genome-wide Z layers now shipped under `data/derived/genomewide/` (5 files, 2.8 MB) | **yes** |
| **Note S5, S27, S28, S29** — simulation validation | 🔴 GAP-4/5 | ✅ | `simulation_validation.py` re-run: all 84 values identical to the archived `simulation_results.json` at machine precision | **yes** (pure synthetic) |
| **S9** — architecture-unselected random controls | 🔴 GAP-7 | ✅ | full table reproduces: exclusion chain 12,622 → 12,555 → 11,885 → 11,820, POOL_818 = 818/767/51, coverage 568/768, 16 random-control rates, 8 null values, 4 percentiles, in-pool strata 21/1,326 · 7/378 · 20/1,827 · 6/477. The pool membership ships as `data/derived/s9_pools/` and a flattened equivalent of the official MetaXcan GTEx layer as `data/derived/gtex_official_finngen/`, so the published numbers reproduce without either bulk layer. The **mashr model databases (10.5 MB)** needed to *re-derive* the pools, and the six original GTEx × FinnGen tables (12.3 MB), are deliberately not redistributed — `INPUTS.md` B.2/B.3 gives both routes | **yes** — and so does re-deriving the pools, since the mashr model side was reduced to the one column the filters read and shipped as `data/derived/mashr_nsnps.csv.gz` (61 kB) |
| **S17** — cluster-aware uncertainty | 🔴 GAP-10 | ✅ | the primary-arm half reads the shipped `data/derived/primary_arm_96pairs.csv`: naive t = 4.1019 (df 94, P = 8.712 × 10⁻⁵), jackknife SE(ρ) = 0.1367, bootstrap ρ CI [0.1161, 0.6220], rate CI 58.3–79.2 %. The gene-cluster rows additionally need the housekeeping layers carried in SI Tables S6/S15, i.e. the `.docx` | **partly** — the gene-cluster rows need the Supporting Information, as every other `.docx`-dependent step in this repository does |
| **S20** — endpoint calibration and positive control | ✅ | ✅ | `scripts/r3/m15/m15_pc.py` **is** the generator behind `code/figures/m15_positive_control.json`; re-run reproduces the archived JSON key-for-key, including `PC2b_group_diff_power` = 8.0 / 14.5 / 13.0 / 17.5 pp | **yes** — since 2026-10-03 the four tables it reads come from `data/derived/`. It previously required `Additional file 1_审稿意见修订_20260917.docx`; supply that (`REPRO_AF1_DOCX`) and it is used instead, which keeps the original route auditable |

Also reproduced in full, beyond the map's original scope: the BH q of SI Tables S3 and
S18 (eQTLGen 12/12 strata, GTEx 9/9 strata on both the ACAT-O and Stouffer chains,
max |Δq| = 0.000), SI Table S5a (all 16 values across both rows), and the SCZ layer
(S24, S23, S21, Table S16 of the manuscript) including bootstrap interval endpoints.

Read the two right-hand columns together. **Now** is the archive-map status — whether the
archive contains enough to reproduce the value. **Runs from a clone?** says what you must
supply beyond the clone. As of 2026-10-03 that column reads **yes** for every S20 row and
for everything else here except the gene-cluster rows of S17 and the two main-text tables,
which are read straight out of the Supporting Information — a document that accompanies the
submission and is therefore not redistributed, exactly like `AF1_DOCX` in `code/figures/`.
`metadata/ARCHIVE_MAP.md` carries the same distinction on each row, and each script's log
states which route it took.

## Layout

```
paths_config.py                  the single path entry point (code/README.md rule 3)
check_wiring.py                  proves every script here can import paths_config (release gate)
INPUTS.md                        every input: logical name, path, MD5, acquiry route
00_build_added_derived.py        rebuilds the data/derived tables added on 2026-10-02
scripts/
  recompute.py                    document-level recompute (SI S2/S3/S5a/S6/S13/S15/S18/S23 -> headline chain)
  recompute_scz.py                genome-wide SCZ layer + weight-fitting framework layer
  r3/                             R3 class: SI Tables S9, S20, S27-S29
    simulation_validation.py      verbatim copy of the archived generator for S27-S29 (no external input)
    recompute_r3_s9_s20.py        S9 null distributions and S20 endpoint calibration
    m15/m15_pc.py                 verbatim generator for S20
  repo_crosscheck/                values re-derived from the official MetaXcan Z layer
  bmc_ref/                        cross-check of the two documents against the predecessor 2026-09-28 final manuscript
  r2_fix/                         estimators examined for the three residual R2 items
results/                          machine-readable outputs and run logs for every script above
```

## Running it

Requirements: Python 3.13.12, numpy 2.4.4, scipy 1.17.1, pandas 3.0.3
(`env/requirements.txt`).

Check the wiring first — this prints every resolved path and verifies each MD5:

```bash
python code/analyses/reproduction_20261002/paths_config.py
```

Then, in order of what each script needs:

```bash
# 1. needs no external input at all
python code/analyses/reproduction_20261002/scripts/r3/simulation_validation.py

# 2. needs only data/derived/ (ships here)          ~2 min 40 s
python code/analyses/reproduction_20261002/scripts/recompute_scz.py

# 3. needs the Supporting Information .docx (from the journal)
REPRO_SI_DOCX=/path/Supporting_Information.docx \
  python code/analyses/reproduction_20261002/scripts/r3/recompute_r3_s9_s20.py

# 4. needs both submitted documents
REPRO_MS_DOCX=/path/Manuscript.docx \
REPRO_SI_DOCX=/path/Supporting_Information.docx \
  python code/analyses/reproduction_20261002/scripts/recompute.py

# 5. previously needed Additional file 1; as of 2026-10-03 it reads data/derived/
python code/analyses/reproduction_20261002/scripts/r3/m15/m15_pc.py

# ...or point it at the review-revision SI and it uses that instead
REPRO_AF1_DOCX=/path/Additional_file_1.docx \
  python code/analyses/reproduction_20261002/scripts/r3/m15/m15_pc.py
```

No path is hard-coded. Every script accepts `--repo-root`, `--ms-docx`, `--si-docx`,
`--af1-docx`, `--mashr-db-dir` and `--gtex-official-dir` (see `INPUTS.md` section C).
Set `TWAS_REPO` once if you run from outside your clone — it is the same variable
`code/figures/paths_config.py` uses, so one configuration covers both packages.

Three scripts print the MD5 and byte count of every input as their first output —
`recompute.py`, `recompute_scz.py` and `r3/recompute_r3_s9_s20.py` — so a run either
matches the recorded hashes or fails loudly. The scripts under `repo_crosscheck/` and
`bmc_ref/` are diagnostic and do not self-check; they were run under shell redirection
and their transcripts are in `results/`.

Outputs land in `results/` regardless of the current working directory.

## Caveats

- The submitted `.docx` documents are **not** distributed here. `paths_config.doc()`
  exits with the expected filename, MD5 and byte count if one is missing, instead of
  raising a `FileNotFoundError` from deep inside a script.
- Three `R2` items and two parameter-disclosure items remain. They do not change any
  number's point estimate; see the remediation note.
- The reproduction was performed on Windows with a managed Python environment; the
  MD5 self-checks are what make runs comparable across platforms.
- `data/derived/s9_pools/disease_blacklist.txt` is stored without case
  normalisation, faithfully to the published pipeline. One token (`C5orf67`) is
  therefore inert, which is why POOL_A is 11,820 rather than 11,819. See `INPUTS.md`
  section F.
- The Supporting Information is read directly from the `.docx` by
  `paths_config.si_tables()`. The `tNN.tsv` files an earlier revision of this package
  read from a session directory no longer exist and are not needed.

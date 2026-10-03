# code/analyses/recovered/

Scripts recovered on **2026-10-02** from unarchived session working directories. They are the
**only** generating code for several Supporting Information tables that had been recorded as gaps in
`metadata/ARCHIVE_MAP.md`.

Copied **verbatim**. Nothing was edited, not even the hard-coded Windows paths they carry — those
are part of the record. Anything needed to run them is noted below.

| File | Recovered from | What it computes | Runnable? |
|---|---|---|---|
| `tost_and_newcombe.py` | `2026-09-09-16-50-19/audit/_tost.py` | `newcombe_diff_ci()` — Newcombe hybrid-score CI for a difference of proportions; `tost_two_prop()` — two-proportion TOST. Function library, no `__main__`. | Import-only. Needs `numpy`, `scipy`. |
| `tost_ci_calculator.py` | `2026-09-11-19-30-45/ci_check.py` | The TOST p-values and Newcombe 90% CIs behind the margin-sensitivity table. Counts are explicit in the source (`46/84`, `42/81`, `44/84`, `38/72`), so it is fully self-contained. | **Yes** — see below. |
| `scz_arm_recount_si_fix.py` | `2026-09-22-14-24-45/work/si_fix.py` | Recomputes the per-arm direction-consistency counts and intervals of the genome-wide SCZ three-arm comparison **from the archived four-arm Z table** (`data/derived/scz_z_4arm.csv`). Dual role: it also renames a table and aligns a caption in the `.docx`. | Partly — the computation reads a file this repository holds; the `.docx` steps need the supplementary file. |

## `tost_ci_calculator.py` — verification

Its original output file (`2026-09-11-19-30-45/ci_check.txt`) survived, and it annotates itself:

```
TOST OLD GTEx  +/-10/15/20 = 0.181 / 0.060 / 0.014   (published 0.181 / 0.060 / 0.014)
TOST eQTLGen   +/-10/15/20 = 0.116 / 0.034 / 0.007   (published 0.116 / 0.034 / 0.007)
```

So this one script genuinely reproduces published numbers from explicit inputs. It is the strongest
kind of recovery: not just the code, but a demonstrated input → output match.

To run it in a clean environment:

```bash
python -m venv .venv && . .venv/bin/activate
pip install numpy scipy
python code/analyses/recovered/tost_ci_calculator.py
```

⚠️ It writes to the hard-coded path `E:\workbuddy\2026-09-11-19-30-45\ci_check.txt`. Redirect or edit
that line if the path is gone — the computation itself needs no external input.

## What these scripts are NOT

They are **not** the upstream computations for the tables that were pasted into the supplementary
file as prose. The table-writing scripts in [`../../deprecated/si_editors/`](../../deprecated/si_editors/README.md)
carry their numbers as **hard-coded English literals** and read no data at all. Recovering those
scripts therefore documents *what was published*, but does not make those tables reproducible.

**Still open after this recovery — restated 2026-10-03.** This list used to name *S6, S9, S10, S11,
S16, S17* and the S27–S29 generators, but five of those were closed later on 2026-10-02 and the
sentence was never updated, so this file contradicted `metadata/ARCHIVE_MAP.md`. Current state:

| SI item | Status |
|---|---|
| S9, S16, S17, S27, S28, S29 | **closed** 2026-10-02 — see `ARCHIVE_MAP.md` (GAP-5/7/9/10) and `code/analyses/reproduction_20261002/` |
| S6 | **closed 2026-10-03** for the Z and model-SNP columns — the corrected layer ships as `data/derived/hk_official_Z.csv`; only the ACAT-O combined-P column stays open (19/87 cells) |
| S10 | **open** (GAP-8) — DN cross-population check |
| S11 | reported as a denominators/availability table; no generating script |
| S7 | the CI half is recovered here (`tost_ci_calculator.py`); the "Smallest margin attained" column is unsourced (GAP-6) |

The authoritative register is `metadata/ARCHIVE_MAP.md`, not this file.


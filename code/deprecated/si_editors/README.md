# code/deprecated/si_editors/ — the scripts that wrote the Supporting Information

Recovered on **2026-10-02** from unarchived session directories. Copied **verbatim**.

These are **document editors, not analysis scripts.** Read the warning before treating any of them
as reproducibility material.

## ⚠️ The pattern these scripts expose

Every one of them writes values into the Supplementary Information `.docx` as **hard-coded English
prose literals**. None of them reads a data file to obtain those values. For example, in
`apply_d3_genomewide_control.py`:

```python
"...This random control reached an FDR enrichment of 69.1% (56/8..."
```

There is no computation behind that `69.1%` inside the script. The workflow was:

> compute elsewhere (unarchived) → paste the numbers as literals into a `.docx`-patching script → write them into the Supporting Information.

**Consequence:** recovering these scripts documents *exactly which numbers were published in which
table, on which date, by which edit* — which is genuinely useful for auditing the Supporting
Information. It does **not** make those tables reproducible. A reader who runs one of these will get
a `.docx` edit, not a computed table.

## Inventory

| File | Recovered from | What it edited into the Supporting Information |
|---|---|---|
| `apply_tost.py` | `2026-09-09-16-50-19/audit/_apply_tost.py` | TOST + power sentence in §2.5; the Additional-file description; a new table |
| `apply_d2_fixed_threshold.py` | `2026-09-11-19-30-45/apply_d2.py` | Fixed-threshold enrichment reanalysis → SI Table S9 (in that era's numbering) |
| `apply_d3_genomewide_control.py` | `2026-09-11-19-30-45/apply_d3.py` | Genome-wide random control → SI Table S10 |
| `apply_s11_hrt_restricted.py` | `2026-09-11-19-30-45/apply_s11.py` | HRT-restricted control → SI Table S11; data-availability statement |
| `apply_edits_20260911.py` | `2026-09-11-18-13-13/_apply_edits.py` | Batch manuscript revisions routed through the editor SDK |
| `apply_m1_m2.py` | `2026-09-14-21-25-36/apply_m1m2.py` | M1 (resource-axis alternative tests) and M2 (SESOI for the 0.10 margin) additions |
| `round4_checks.py` | `2026-09-18-07-04-15/.tmp/round4_checks.py` | Round-4 consistency checks across manuscript and supplementary file |

## Why keep them at all

1. **They are the audit trail for the SI.** Each carries the literal strings it inserted, so any published number can be traced to the edit that introduced it and to the date.
2. **They record which table number was which, when.** The Additional-file numbering moved repeatedly — the housekeeping table was S6 on 2026-09-11, S5 by 2026-09-13, and S6 again in the current Supporting Information. These scripts pin that history.
3. **They show what is missing.** Knowing that the values were literals tells the next person exactly what has to be re-derived, and that searching for a "missing script" will not help.

## What they are not

Not runnable as analysis. They:

- reference hard-coded Windows paths from 2026-09 that no longer exist (`E:\workbuddy\...\定稿资料\...`);
- need the specific `.docx` revision they were written against — running one against today's file would target text that is no longer there;
- import `python-docx`, and one of them (`apply_edits_20260911.py`) drives the local editor SDK through a `file_id` that is long gone.

They pass a syntax check; they are not executable as-is, and they are not meant to be.

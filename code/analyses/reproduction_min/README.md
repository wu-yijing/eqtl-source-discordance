# reproduction_min — five minutes, no arguments, no external input

Everything else in `code/analyses/` is a *forensic* package: it needs the two submitted
`.docx`, the mashr model databases, the full-universe Z layers, or a session directory. This
directory exists so that a reader who has nothing but a clone of this repository can still
verify the paper's headline numbers, and can see for themselves which claims stand on the
repository alone and which do not.

```
python code/analyses/reproduction_min/reproduce_headline.py
```

Requires Python ≥ 3.9 and **numpy only** — Spearman is computed as Pearson on average ranks,
so scipy is not needed and the arithmetic is in the file. No network, no argument, no `.docx`.

## What it reproduces

| Quantity | Where it is reported | Reproduced |
|---|---|---|
| Primary-arm direction consistency | Abstract, Results | **66/96 = 68.75%** |
| Primary-arm Spearman ρ | Abstract, Results, Table 2(A) | **0.38964** |
| Per-phenotype split DR / DN / DPN | Results | **23/32 · 21/32 · 22/32** |
| Tissue-only arm n · k · rate · ρ | Table 2(B) | **138 · 91 · 65.9% · +0.4138** |
| SCZ three arms k | Table S24 | **5,584 · 5,551 · 5,506** |
| SCZ three arms ρ | Table S24 | **+0.4690 · +0.4199 · +0.4465** |
| SCZ complete-case n | Table S24 | **8,315** |

The script exits non-zero if any archived value fails to reproduce. Current status: **15 checks (+1 ACAT-O section),
0 mismatches**.

Inputs, all inside this repository:

| File | Rows | Carries |
|---|---|---|
| `data/derived/primary_arm_96pairs.csv` | 96 | the primary arm |
| `data/derived/gtex_Z.csv` | 222 | the tissue-only arm (Whole_Blood vs Nerve_Tibial) |
| `data/derived/scz_z_4arm.csv` | 15,875 | the SCZ layer (8,315 complete-case) |

## The one convention the three-arm comparison rests on

`multiZ` is `(wbZ + ntZ)/√2` rounded to six significant figures. That rounding leaves
**77 exact zeros in the `multiZ` column** of the complete-case universe (8 in `wbZ`, 7 in `ntZ`,
none in `eqZ`).

The archived counts score a zero as **disagreement** — the convention of `numpy.sign`. Switching
to "positive counts as positive" (`Z > 0`) changes the arms by:

| Arm | `np.sign` | `Z > 0` | Δ |
|---|---:|---:|---:|
| panel-only | 5,584 | 5,585 | +1 |
| tissue-only | 5,551 | 5,556 | +5 |
| **dual** | **5,506** | **5,544** | **+38 (+0.46 pp)** |

So the dual arm — the one that carries the paper's headline SCZ contrast — moves by 0.46
percentage points on a convention that was never stated. The table note for Table S24 should
say so. Draft text is in `docs/audit_notes/R2残余差异消除方案_20261002.md`.

## What this does **not** cover, and why

Nothing here touches S9, S16, the gene-cluster half of S17, or S20. Those four need inputs that
are not redistributed with this archive — the mashr databases, `groups.json`, `t1_s8rand/`,
`metaxcan_run/`, the elastic-net Z layer, and the predecessor Additional file. They are marked 🟡
in [`metadata/ARCHIVE_MAP.md`](../../../metadata/ARCHIVE_MAP.md) and listed with their recorded
MD5 in [`../reproduction_20261002/INPUTS.md`](../reproduction_20261002/INPUTS.md) §2.

**This directory is the honest boundary of the archive.** If a value is not in the table above,
it is not reproducible from a clone alone.

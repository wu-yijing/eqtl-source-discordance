# code/figures/ge_main/ — the four manuscript main figures

These are the four figures accompanying the *Genetic Epidemiology* submission. They are a
**different set** from the build outputs under `figures/`, which belong to the earlier
BMC-generation layout and are produced by `code/figures/*.py` via `code/run_all.sh`.

```bash
bash code/figures/ge_main/reproduce.sh        # rebuild all four and compare hashes
```

## What it reproduces

| Script | Figure | Content | Inputs (all from `data/derived/`) |
|---|---|---|---|
| `unified_fig1.py` | **Fig. 1** | six-module analytical framework (flowchart) | none — pure layout and text |
| `unified_fig2.py` | **Fig. 2** | cross-source agreement, 96 pairs (ρ = 0.39, 68.8 %) | `primary_arm_96pairs.csv` |
| `unified_fig3.py` | **Fig. 3** | two-axis partition: three arm ρ with Fisher-z CIs, Δρ forest | `gtex_Z.csv`, `eqtlgen_Z.csv` |
| `unified_fig4.py` | **Fig. 4** | cross-trait generalisation, three gene sets | `gtex_Z.csv`, `scz_z_4arm.csv` |

`reproduce.sh` builds a small filename view of `data/derived/` because the scripts were
written against the predecessor repository's names (`gtex_official_Z.csv` and so on).
`INPUTS.md` section A.1 records that those five files are byte-identical to the tables in
`data/derived/`; nothing else about the scripts is changed.

## Result — measured 2026-10-03

```
Figure_1.png  eb77483eaf518887…   identical to the submitted figure
Figure_2.png  87ee0eaa83f37309…   identical to the submitted figure
Figure_3.png  152f45df76e8d4ab…   identical to the submitted figure
Figure_4.png  f29f2f56da3b6310…   identical to the submitted figure
```

All four PNGs are **byte-identical** to the files submitted with the manuscript. The four
PDFs are identical apart from the embedded `/CreationDate` (4–6 bytes), which is why
`reproduce.sh` compares the PNGs.

## Two things the figures need that the archive does not contain

Both were found by running this directory in the shipped container on 2026-10-06/07, and
both are now stated up front by `reproduce.sh` instead of surfacing as an unexplained
`[FAIL]`:

**1. Arial.** `figstyle_ge.py` sets `font.family = 'sans-serif'` with
`FONT_STACK = ['Arial', 'Helvetica', 'Liberation Sans', 'DejaVu Sans']`, and forces
`mathtext.rm = 'Arial'` so a single family is used throughout — the journal's requirement.
Arial is proprietary and is deliberately **not** in `env/Dockerfile`. Where none of the
first three is installed, matplotlib silently falls through to DejaVu Sans and every glyph
changes. Measured in the image, before the fallback was supplied:

| | vs the submitted figure |
|---|---|
| figure pixels | **4.3 % – 9.9 % differ**, max channel delta 250–255 |
| PDF size | roughly half (`Figure_1.pdf`: 56,276 → 26,986 bytes) |

That is a font substitution, not a broken archive — and the hash comparison cannot tell the
two apart, so `reproduce.sh` now reports which font it resolved *before* it compares. With
Arial made available to the container, all four figures come out **pixel-identical** to the
submitted ones (`scripts/compare_figures_pixels.py`, 0 differing pixels); the bytes still
differ, for the zlib reason in `figures/README.md`.

**2. The Supporting Information.** `unified_fig4.py` reads two of the numbers it plots out
of Note S4, so it needs the submitted SI document. Until 2026-10-07 it fell back to an
absolute path on one machine, which meant Figure 4 could not be produced anywhere else and
failed in the container with a `FileNotFoundError` naming a directory no reader has. It now
resolves from `SI_DOCX` (or `AF1_DOCX`), then from `manuscript/Supporting_Information.docx`,
and otherwise stops with the instruction. Without it, `reproduce.sh` skips Figure 4 by name
and exits non-zero — a skipped check is not a passed check.

## Before this directory existed

`figures/README.md` recorded that the four main figures **could not be assembled
end-to-end from this archive** — Fig. 2, 3 and 4 by the BMC-generation scripts, and Fig. 1
`only by hand`, from a recovered ancestor that carried absolute paths. That is no longer
the state: the producing scripts were located in an un-archived working directory and are
now here, runnable, with the comparison above as the evidence.

## Style

`figstyle_ge.py` is the shared style module — one font family, 160 mm width, 600 dpi,
colour-blind-safe palette, lowercase `(a)`/`(b)` panel labels. It is imported rather than
re-implemented per script, so the four figures cannot drift apart.

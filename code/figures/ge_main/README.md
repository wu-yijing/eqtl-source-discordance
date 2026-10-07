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

## Result — measured 2026-10-03, re-measured 2026-10-07

```
Figure_1.png  4c690d7c8219f2ad…   identical to the submitted figure
Figure_2.png  87ee0eaa83f37309…   identical to the submitted figure
Figure_3.png  67d8a519e4f801f6…   identical to the submitted figure
Figure_4.png  f29f2f56da3b6310…   identical to the submitted figure
```

All four PNGs are **byte-identical** to the files submitted with the manuscript. The four
PDFs are identical apart from the embedded `/CreationDate` (4–6 bytes), which is why
`reproduce.sh` compares the PNGs.

**Why two hashes moved (2026-10-07).** The manuscript's rev10 changed two of the four
figures, so the *recorded* hashes — not the code — were what had gone stale: the archive
still described the rev9 set while the submission had moved on.

| | earlier (rev9) | now (rev10) | what changed |
|---|---|---|---|
| `Figure_1.png` | `eb77483e…` | `4c690d7c…` | module 5's label, now *Three nested disease-agnostic control layers* (P3-3). Same canvas 3,780 × 2,645; only that text band differs |
| `Figure_3.png` | `152f45df…` | `67d8a519…` | panel (a) switched from Fisher-z to gene-cluster bootstrap intervals (M5); panel (b) grew from two rows to four (P2-3). Height 1,705 → 1,903 px |

The two scripts were revised in the same step, so the four figures still rebuild from a
clone alone: `unified_fig1.py` carries the new label, and `unified_fig3.py` now **reads**
the two genome-wide rows from
`code/analyses/reproduction_20261002/results/recompute_scz_results.json` instead of holding
them as constants — that JSON is the output of `scripts/recompute_scz.py` section 5, and the
figure step prints the values it read beside the manuscript's. `Figure_2` and `Figure_4`
were not revised; their hashes are unchanged.

## One thing the figures need that the archive cannot contain: Arial

Found by running this directory in the shipped container on 2026-10-06/07, and now stated up
front by `reproduce.sh` instead of surfacing as an unexplained `[FAIL]`:

`figstyle_ge.py` sets `font.family = 'sans-serif'` with
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

**Why `fonts-liberation` is not simply added to the image.** Liberation Sans is metric
compatible with Arial, so it is the obvious candidate. Measured on 2026-10-07 by installing it
in the shipped image: the difference falls from 4.5 / 9.9 / 7.3 / 4.3 % to
1.6 / 8.0 / 6.4 / 3.6 % of pixels for Fig. 1-4 — a large gain on Fig. 1, almost none on the
others, and **no figure matches the recorded hash**. It buys a better-looking failure in
exchange for a full image rebuild, so the image keeps the honest fallback and the recipe
above, and `reproduce.sh` reports a substitute as a substitute.

## The Supporting Information used to be required, and is not any more

`unified_fig4.py`'s housekeeping panel was read out of the submitted SI's Table S6, through
a hardcoded absolute path, so on any other machine — including the container — Figure 4 died
with a `FileNotFoundError` naming a directory no reader has. That dependency was never
necessary: Table S6 **is** `data/derived/hk_official_Z.csv`. GAP-1 was closed on 2026-10-03
by shipping that layer, and 2026-10-07 the substitution was verified the strong way — with
the journal document absent entirely, `reproduce.sh` rebuilds Figure 4 from the archive alone
and the PNG is **byte-identical** to the submitted figure. `scripts/check_fig4_hk_source.py`
guards the archive side (`n = 72`, `rho = +0.64`). The SI is no longer an input to any figure
here, and gate 14 no longer needs one.

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

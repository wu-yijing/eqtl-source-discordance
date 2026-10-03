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

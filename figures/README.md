# figures/

## Policy — stated, not implied

**`figures/` holds the rendered build outputs of `code/run_all.sh`, and they are committed.**

The predecessor archive excluded figures deliberately; this one includes them, for one reason:
a reader should be able to confirm that the archive reproduces the *published* figure, not merely a
numerically equivalent one. The previous revision left that choice unstated and shipped an empty
directory, so `.zenodo.json` ("contains no figures") and `README.md` ("archived figures exactly as
submitted") disagreed and neither was true. The policy is now: **commit the build outputs**.

The rule that makes this safe:

> **Everything in `figures/` is a build output.** If a file here differs from what `code/figures/`
> produces, the file is wrong, not the script. Regenerating (`AF1_DOCX=… bash code/run_all.sh`) is
> always the fix.

There is exactly one exclusion: the `_backup_before_*` directories some scripts create on their first
run are transient and are not committed.

## What `run_all.sh` produces, and what it corresponds to

The figure scripts were written against an **earlier 8-figure layout**, so their output filenames do
**not** match the submitted paper. `code/figures/FIGURE_NUMBER_MAP.md` is the authority; read it
before touching anything here. Summary:

| Build output | Producing script | **Current manuscript** |
|---|---|---|
| `Fig3.pdf` / `Fig3.png` | `02_redraw_Fig3.py` | **Fig. 2** — cross-source agreement scatter (96 pairs; ρ = 0.39, 68.8 %) |
| `Fig4.pdf` / `Fig4.png` | `06_redraw_Fig4.py` | **Fig. 3** — axis-resolved partition, ρ with Fisher-z CIs + Δρ forest |
| `Fig8.pdf` / `Fig8.png` | `04_redraw_Fig8.py` | **Fig. 4** — cross-trait generalisation, three gene sets |
| `FigS6.pdf` / `FigS6.png` | `10_redraw_FigS6_20260921.py` | **Fig. S3** — endpoint calibration and spike-in positive control |
| `Fig5.pdf` / `Fig5.png` | `01_redraw_Fig5_Fig7.py` | *not in the current manuscript* — candidate dumbbell |
| `Fig7.pdf` / `Fig7.png` | `01_redraw_Fig5_Fig7.py` | *not in the current manuscript* — RNH1 cross-cohort |
| `Fig6.pdf` / `Fig6.png` | `08_redraw_Fig6_labels_20260920.py` | *not in the current manuscript* — FDR-enrichment three-panel |

The three "not in the current manuscript" entries are kept because a revision may ask for them and
because they document the earlier figure set. **Their output must not be presented as part of the
current submission.**

## The four manuscript main figures — now regenerable

The four figures submitted to *Genetic Epidemiology* are a different set from the build
outputs above (which belong to the earlier BMC-generation layout). Their producing scripts
were found in an un-archived working directory and now ship, runnable:

    bash code/figures/ge_main/reproduce.sh

All four regenerate from `data/derived/` alone and are **byte-identical** to the submitted
PNGs. See `code/figures/ge_main/README.md`. Before 2026-10-03 this section read that the
main figures "cannot be assembled end-to-end from this archive — Fig. 2, 3 and 4 can,
Fig. 1 only by hand"; that is no longer the state.

## Figures whose producing script is not in `code/figures/`

`figures/README.md` used to require that a figure whose producing script is missing be *named*, not
left as an implicit claim. **Updated 2026-10-03:** two of the four were recovered from un-archived
working directories and now ship, verbatim, in [`../code/figures/recovered/`](../code/figures/recovered/README.md).

| Manuscript figure | Content | Producing script | Status |
|---|---|---|---|
| **Fig. 1** | Overview of the analytical framework (six modules) | **`ge_main/unified_fig1.py`** | ✅ **Regenerated and byte-identical** (PNG SHA-256 `eb77483e…`) |
| **Fig. S1** | Exploratory diagnostic scheme (flowchart) | **`ge_si/rebuild_fig1_2_9.py::figure2()`** | ✅ **Corrected and regenerated** — the script now prints the published text (66.1–68.2 %; "Report the source-induced caveat"). The published *raster* was pixel-edited on 2026-10-01 and is not byte-reproducible (~2 % pixel difference, uniform); see `ge_si/README.md` |
| **Fig. S2** | eQTL SNP-count distribution across gene groups (violin) | `recovered/gen_figs4.py` | ✅ **Recovered and matching** — same 61-gene universe (24/24/13) and the three published medians |
| **Fig. S4** | Silver-stain SDS–PAGE (wet-lab image) | none — and none is possible | ➖ a photograph of a gel, not a plot |

The two recovered scripts carry absolute paths and read the predecessor build root
(`figstyle.py`, `prep_out.json`); they are evidence, not a runnable pipeline, and are deliberately
**not** invoked by `code/run_all.sh`. Consequently the manuscript's four main figures still cannot be
assembled end-to-end from this archive — Fig. 2, 3 and 4 can, Fig. 1 only by hand — and that is
recorded rather than implied.

## Naming and format

| Item | Convention |
|---|---|
| File name | The **build** name the producing script writes (`Fig3`, `FigS6`, …). The manuscript numbering is the table above — do not rename files to match the paper, because then nothing here would be a build output |
| Vector | PDF, all text as text (no outlined fonts), fonts embedded |
| Raster | PNG, 600 dpi, RGB (not CMYK) |
| Panel labels | lowercase `(a)`, `(b)` — **no descriptive titles inside the image** |
| Font | one family across all figures (embed-shared style module, not per-script hard-coding) |
| Colour | colour-blind-safe palette; the same meaning gets the same colour across figures |

*(A prior revision shipped figures in two font families because each plotting script hard-coded its
own `font.family` instead of importing the shared style module. Keep the shared module.)*

## Verification before a release

```bash
# regenerate, then check every build output the pipeline claims to write
AF1_DOCX=/path/to/Supporting_Information.docx bash code/run_all.sh
for n in Fig3 Fig4 Fig5 Fig6 Fig7 Fig8 FigS6; do
  test -f figures/$n.pdf || echo "MISSING figures/$n.pdf"
  test -f figures/$n.png || echo "MISSING figures/$n.png"
done

sha256sum figures/*.pdf figures/*.png
```

Record the figure checksums in `metadata/provenance.json` (regenerated by
`scripts/collect_provenance.py`, which hashes every tracked file). A figure that cannot be
regenerated must be listed in `metadata/ARCHIVE_MAP.md` — see the table above.

## Superseded script

`10_redraw_FigS6_20260920.py` is superseded by `10_redraw_FigS6_20260921.py` (log-scale axis label,
two in-panel reference lines, upright mathematical symbols, the n = 222 detection-boundary row).
Where the two conflict, the `20260921` version governs — `FIGURE_NUMBER_MAP.md` says so, and
`run_all.sh` invokes only the `20260921` version.

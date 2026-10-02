# ⚠️ PRECORRECTION NOTICE — the Z values in this directory are superseded

**Moved here on 2026-10-02.** This directory previously sat in `data/derived/` (the authoritative
layer) under the name `hk_reselect/`. It does not belong there. Below is the evidence.

---

## What is wrong with the Z values here

The housekeeping control layer was computed on **2026-08-30** (`random.seed(20260830)`; the scripts
below carry that date). The σᵢ / PLINK corrections — the fix that replaced the in-house S-PrediXcan
implementation with the unmodified official MetaXcan v0.8.1 binary — landed on **2026-09-17**.
**Every Z score in this directory predates that fix.**

## How this was established

1. **Timeline of the published table.** Table S6 of the Supporting Information was tracked across
   all 93 archived copies of the manuscript's supplementary file. Its ANKRD40 row reads

   | up to | value |
   |---|---|
   | 2026-09-16 22:24 | `1/2 \| 0.256 \| 1 \| 0.00331 \| -0.9925 \| -0.9542 \| 1.1237 \| -0.8469 \| -0.0555 \| 2.9348` |
   | 2026-09-17 19:15 onward | `1/2 \| 0.598 \| 0.718 \| 0.376 \| -0.5863 \| -0.5637 \| 0.6638 \| -0.4786 \| -0.2590 \| 1.0657` |

   The change falls inside the documented 2026-09-17 correction window. **The values still in this
   directory are the pre-2026-09-17 side.**

2. **Direction.** Every changed value moves in the direction a σᵢ correction predicts: |Z| shrinks,
   and the ACAT-O combined P moves toward 0.5.

3. **Shape of the change.** 22 of the 30 genes show a **constant per-gene ratio** across all three
   phenotypes — e.g. ATG101 ×2.435 in both tissues, DCTN2 ×3.244, FIBP ×2.667 — which is the
   signature of a per-gene multiplicative correction. The model-SNP column is unchanged for all 30
   genes, so the same models were used and only the Z computation moved.

4. **The gene selection is *not* in question.** The 30-gene roster, the R1–R6 selection rules and
   the seed are unaffected. The current roster is preserved at `../../derived/hk_genes.txt`
   (byte-identical to `data/hk_genes_v2.txt` here).

## What is still unresolved — read before quoting anything

**8 of the 30 genes do not follow a constant ratio** — `DNAJC4`, `E2F4`, `GOLGA3`, `SDF4`, `SRM`,
`TOMM20`, `SPRYD3`, `TUT1`. `GOLGA3` even changes sign at DPN. A pure σᵢ rescale cannot produce
that, so the corrected computation differs from this one by more than a per-gene factor.

**The corrected computation is not archived.** Its output exists only inside the Supporting
Information `.docx`; a full-disk numeric search for the published values (`−0.5863`, `−0.5637`,
`−0.4387`) returns no source file, and the generating script has not been located.

**Consequences:**

- `TableS6_hk_control_v2.csv`, `hk_twas_v2_raw.csv`, `arms_all_groups.csv`, `Table2_v2.csv`,
  `hk_v2_summary.json`, `hrt_verify.*` and the `d3*` files here **must not be quoted** in a
  manuscript, a response letter or a figure.
- **The housekeeping layer of main-text Table 1 therefore cannot be reproduced from this
  repository.** That is a live gap, recorded as GAP-1 in `metadata/ARCHIVE_MAP.md`.
- The 8-gene anomaly needs the author's attention independently of the archival question: if the
  corrected housekeeping computation differs for reasons beyond the σᵢ fix, then every table that
  aggregates the housekeeping arm (S7, S19, S26) may need re-checking.

## What IS still usable here

| File | Why |
|---|---|
| `data/hk_genes_v2.txt`, `panel104.txt`, `hk_selection_meta.json`, `Human_Mouse_Common.csv` | Gene selection and its provenance — outcome-blind, unaffected by the Z defect |
| `README.md` | The R1–R6 rules and the filter flow, which the manuscript cites |
| `scripts/` | The method as run on 2026-08-30. Retained for provenance — **not** re-run against the corrected layer |

## To fix this properly

Re-run `scripts/02_spredixcan.py` (or its equivalent) against the official MetaXcan v0.8.1 binary,
reproduce the published Table S6 values for all 30 genes, resolve the 8-gene anomaly, and commit the
generating script. Until then, this directory is provenance, not data.

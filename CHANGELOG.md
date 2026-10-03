# Changelog

All notable changes to this archive are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/) adapted to research artefacts (see `docs/RELEASE_PROCESS.md` §2).

**Every entry must state explicitly whether any reported number changed.** That sentence is the first thing a reviewer will look for.

---

## Version lineage — read this before comparing version numbers

This project has been re-archived three times. Version numbers **do not restart** with each repository; they continue across the lineage so that no two releases of this study ever share a number. Releases below this repository's first entry belong to predecessor repositories, which are archived and read-only.

| Version | Repository | Zenodo record | Note |
|---|---|---|---|
| v1.0.0 – v3.0.0 | `wu-yijing/twas-eqtl-source-discordance` (formerly `TWAS-eQTL-source-confounding`) | concept `10.5281/zenodo.21238202` | Full pre-2026-09-24 development history. **GitHub tags and Zenodo version labels for this period are not identical — see "Open item" below.** |
| v1.0.0 – v1.0.1 | `wu-yijing/eqtl-source-discordance-audit` | concept `10.5281/zenodo.22910500` | Release-only snapshot; **its v1.0.0 tag sits two commits behind that repository's final state** |
| **v4.0.0** → | **this repository** | new concept DOI `<CONCEPT>` | Canonical from here on |

> **Open item — do not close this by assumption.** The predecessor README declares Zenodo version **v2.7.0** as current, while its GitHub tags stop at **v3.0.0**. GitHub tags and Zenodo version labels for the predecessor repository are therefore out of step. Record the true mapping here once verified, because a reader comparing the two will otherwise conclude that a release is missing.

---

## [Unreleased]

### 2026-10-03 (thirteenth pass) — the upstream chain re-run end to end, and the two defects that found

**Numbers: no reported number changes.** Neither submitted document was edited. No file in
`data/derived/` changed. What changed is that the raw-input → Z-layer chain was **actually re-run**
on a machine holding all 15 hashed external inputs, which is the first time that has been done by
anyone other than the run that produced the archive — and it found two things.

**1. `build_covariance.py` wrote the GTEx covariances in the wrong row order — a real defect, now fixed.**
The two archived covariance sets come from **two different producer scripts with different row
conventions**, and `build_covariance.py` applied one of them to both. Added `--order`:

| `--order` | genes | SNPs within a gene | arm |
|---|---|---|---|
| `model` | ascending gene id | model-DB row order | eQTLGen |
| `bim` | model-DB insertion order | **LD panel `.bim` order** | GTEx |

`run_upstream.sh` steps 2 and 5 now pass the right one. Without it the GTEx covariances were the
same gene set with the same values in a different order — `identical 30 | differing 0` becomes
`differing 2`, and a *content* comparison cannot tell the difference. That is why it survived: the
downstream effect was floating-point only (max |Δ| = 3.6 × 10⁻¹⁵ over a GTEx arm's 162k cells).
The file hash, however, was wrong, and so were the `cov_*.txt.gz` rows in `data/external/README.md`.

**2. `run_upstream.sh` could report success while writing nothing.** S-PrediXcan **refuses to
overwrite** an existing `--output_file` — it logs "already exists, move it or delete it if you want
it done again", exits 0, and leaves the stale file. Steps 3 and 7 now `rm -f` their target first.
Encountered directly during this pass: six GTEx runs reported `ok` and produced no change.

**Added**
- `code/upstream/verify_middleware.py` — hashes all **30** middleware artefacts against the copy the
  reported numbers came from and exits non-zero on any disagreement. Wired in as
  `run_upstream.sh` step 8, so a rebuild that disagrees now fails instead of being described in
  prose. `--require-all` also fails on artefacts not yet produced.
- `env/environment-upstream.yml` — the **second** Python environment, pinned: 3.12.13 / numpy 1.26.4
  / scipy 1.13.1 / pandas 2.2.3. The upstream chain needs it and cannot share `environment.yml`
  (3.13 + numpy 2, no installable numpy 1.x). Until now the requirement lived in a script comment.
- `env/README.md` rule 6: if a step needs a different interpreter, pin that interpreter in its own
  file rather than loosening an existing pin.

**Verified**
- `identical 30 | differing 0` across the whole middleware set: 3 model databases, 7 covariances,
  3 harmonised GWAS, 3 allele-aligned GWAS, 6 GTEx S-PrediXcan arms, 9 eQTLGen S-PrediXcan band arms.
- The previously un-re-run step is now re-run: the **eQTLGen S-PrediXcan bands A/B/C × DR/DN/DPN**,
  all nine byte-identical, including `cov_A.txt.gz` (18,390,068 rows) and the 94-gene band output.

**Also corrected in this pass**
- `.zenodo.json` said "Four of the eight manuscript figures have no producing script in this archive".
  That stopped being true when `ge_main/` shipped and Fig. S2 was recovered; only **Fig. S4** (a gel
  photograph) has none. This text goes into the DOI record, so it mattered.
- `figures/README.md` and `code/README.md` each still carried a sentence contradicting the rest of the
  same file about which manuscript figures are reproducible. Both rewritten with the current status.
- `env/Dockerfile` pinned by digest: `continuumio/miniconda3@sha256:eca594d6…` (= `26.7.1-1`). Docker
  Hub is unreachable from this environment, so the digest was resolved through a reachable mirror and
  then verified independently of that request — the index was re-fetched *by digest* and hashed
  locally, the amd64 child manifest and its config likewise, and neighbouring tags return *different*
  digests. `scripts/cut_release.sh` §7 now checks the image reference with any trailing comment
  stripped, so the readable tag in the comment no longer trips the check.
- `paths_config.py` now identifies **which revision** of a submission document you hold, by MD5, from
  a recorded `revisions` list — including the two added here (`rev3`, `rev4`). It previously carried a
  single `md5` used only to build a hint string, so *any* file printed `[ok]`. An unrecognised
  document now prints `[UNRECOGNISED]` with its actual MD5 and every recorded revision, and
  `--strict-docs` makes it a non-zero exit. `INPUTS.md` §B.1's promise — "a run either matches or says
  so" — was not enforced by code before this; now it is, and both behaviours are tested.
- `run_all.sh` no longer fails when the Supporting Information `.docx` is absent. It reported
  `2 failure(s)` while `README.md` promised the step was "skipped, not failed". The two SI-dependent
  scripts are now detected up front, skipped by name, and the run ends
  `pipeline completed with no failures` with a `note: these steps were SKIPPED` line.
- `metadata/provenance.json`'s `analysis_env` said "Python 3.13.0" while `environment.yml` pinned
  3.13.12. It is now **read from the pin files** (`scripts/collect_provenance.py::_env_versions`), so
  the manifest cannot disagree with the environment it describes.
- S20: section 7d of `recompute_r3_s9_s20_log.txt` labelled three rows `差一个网格步`. They are not a
  discrepancy — the published values come from a Monte-Carlo search on a grid, the `r3` column from a
  deterministic closed form snapped to the same grid, and the two differ by one step exactly where the
  closed form lands just above a grid point. Each row is now named accordingly and the JSON carries an
  explicit `S20_min_lambda_note`.

### 2026-10-03 (twelfth pass) — DOI slot, predecessor migration, and the archive-map contradictions an external audit found

**Numbers: no reported number changes.** Neither submitted document was edited. One value moved from
"absent from this archive" to "derivable, with a stated residual" (see the S5a entry), and one
repository file began reproducing a value it previously could not.

This pass answers an independent reproducibility audit of this repository, run against HEAD
`e4e4dec`. The audit's headline finding was that the *downstream* chain reproduces fully — 7/7 release
gates, 15/15 minimal assertions, 87/87 ACAT-O cells, S9 pool re-derivation byte-identical, and every
committed figure PNG identical on regeneration — while three things around it did not. Those three
are what this pass fixes.

* **The DOI was a placeholder with nowhere to put the answer.** Four carriers held concept- and
  version-DOI placeholder tokens, `README.md` called the archive a "citable snapshot", and the badge
  was a Zenodo badge that 404s. Added:
  [`metadata/zenodo_release.json`](metadata/zenodo_release.json) (single source of truth),
  [`scripts/set_doi.py`](scripts/set_doi.py) (`--show`, `--check`, and a one-command backfill that
  rewrites all four carriers and the badge together), and [`DOI_PENDING.md`](DOI_PENDING.md), which
  states the publication steps and why the manuscript's currently-cited DOI
  (`10.5281/zenodo.22910500`) is **not** a substitute — it resolves to the predecessor `-audit`
  repository's v1.0.0, a 2.34 MB snapshot published 2026-09-23, before every gap closure, the figure
  build outputs and the SI ACAT-O rule. `README.md` now carries an honest pending notice instead of a
  false citability claim, and `scripts/cut_release.sh` grew a section that surfaces the pending state
  at pre-flight.
* **The predecessor repositories no longer have to be cloned.** Every tracked file in both of them
  (165 + 190) was compared against this tree **by blob hash**, and each was given a disposition:
  123 + 167 already identical here, 30 + 15 superseded by a repaired canonical copy, 8 + 6
  deliberately left behind (build/config files this repository replaces), and **6 migrated**. The
  six are in [`docs/predecessors/`](docs/predecessors/README.md): the predecessor's `ARCHIVE_NOTE.md`
  and `README.md`, both `audit_notes/README.md` indexes (the `-audit` one carries the 2026-09-23
  rebuild addendum this repository had dropped), and both `_PROVENANCE.json` records for the
  superseded layer. Machine-readable:
  [`docs/predecessors/MIGRATION_MANIFEST.json`](docs/predecessors/MIGRATION_MANIFEST.json) (355 files).
* **`metadata/ARCHIVE_MAP.md` contradicted itself in three places**, invisible to
  `check_archive_map.py` because that check validates structure, not prose. (i) The Figs. 1–4 row
  still read "`figures/` contains only its README" while seven figure build outputs were committed;
  it is now split into a ✅ row for Figs. 2–4 (which regenerate byte-identically) and a 🟡 row for
  Fig. 1. (ii) Figs. S1 and S2 were still 🔴 `none` while §5 recorded GAP-4 as partly closed and
  `code/figures/recovered/` shipped their generators; both are now 🟡 with the reason each is not ✅.
  (iii) The Note S4 row described checksums as `<hash>` placeholders while `data/README.md` records
  them, correctly, as `not-held`. Counts: **47 items, 24 ✅ / 14 🟡 / 0 🔴 / 9 ➖** (was 46 / 23 / 12 / 2 / 9).
* **SI Table S5a's fourth row now reproduces.** It was the single value
  `scripts/audit_documents_vs_repo.py` reported as absent from the archive: "√N_e weights applied
  directly on the Z scale" (pooled Z +2.09; Q 76.6; I² 98.7). The convention had been conflated with
  the β-scale row. `code/analyses/m6_ne_weighted_sensitivity.py` now emits both — the normalised
  Stouffer combination (M6(b), +2.39) **and** the √N_e-weighted arithmetic mean (M6(c)) — because the
  SI prints both. M6(c) gives **+2.0926 → +2.09 ✓** and **I² 98.69 % → 98.7 % ✓**, with Cochran's Q
  on the Z scale at **76.27 against the published 76.6** (Δ −0.33, −0.43 %). That residual is printed
  by the script and recorded in the map; the published Q is not reproducible to its third significant
  figure from the two cohort Z/N_e pairs this archive ships.
* **S17's two undisclosed parameters are stated as measured facts, not as an outstanding debt.**
  Generator = `numpy.random.RandomState` (MT19937): seed 20260915 gives the published interval
  `[0.1161, 0.6220]` → `0.12–0.62` where PCG64 gives `0.11–0.63`. Resampling is over a
  lexicographically sorted gene vector. What remains is the SI table note — a manuscript-side edit,
  tracked in `docs/audit_notes/R2残余差异消除方案_20261002.md`.
* **The archive's own record of the manuscript's hash was stale.** `INPUTS.md §B.1` and
  `results/recompute_log.txt` recorded `dbbe4f81…` / 30,524 B, which is the file as it stood *before*
  reference [39] was repointed to this repository; the submitted revision is `a6f7521b…` / 30,523 B.
  The Supporting Information still matches its recorded hash exactly, and no number moved — the
  change is one reference string. Both revisions are now recorded, with the reason for the delta, and
  `results/` is regenerated against the current file.
* **Defects fixed while in the area.** `recompute.py` wrote a tracked CSV through pandas' default
  `lineterminator` (= `os.linesep`), so on Windows it rewrote `results/merged_pairs.csv` with CRLF
  against `.gitattributes`' `eol=lf` — the same defect class fixed for another writer on 2026-10-02,
  missed here; it is invisible because git normalises on commit, which is why it survived.
  `run_spredixcan.sh` mounted its inputs at `/input/...` while reading `/app/input/...` and named a
  non-existent entry point, so all nine runs silently reported "SKIP" and the script still exited 0;
  the mounts are corrected and the script now **fails loudly** when nothing ran.
  `m6_ne_weighted_sensitivity.py` wrote its report to `data/processed/`, a directory that has not
  existed since the canonical reorganisation, so it printed and then died on the write.
  `env/Dockerfile`'s unpinned base image is now surfaced by `cut_release.sh` section 7 with the exact
  command to resolve it — still open, because Docker Hub was unreachable from the repair environment
  (HTTP 000) and pinning to an unverified tag would be worse than saying so. `data/README.md` printed
  Python 3.13.0 (the manuscript's figure) where the pin has been 3.13.12.

### 2026-10-03 (eleventh pass) — M3 verified already implemented, and `HK` pinned to housekeeping

**Numbers: no reported number changes.** Neither submitted document was edited. This pass corrects a
statement the ninth and tenth passes got wrong, and records two verifications.

* **The ninth pass said peer-review item M3 was "a text edit still owed". It is not owed — it is
  already done.** Checked against the current revision on 2026-10-03: the Table S10 note prints the
  resource's *full* composition (1,032 European + 220 East Asian cases, 451,248 European + 132,764
  East Asian controls); the Limitations sentence distinguishes "the GWAS used for the partition" from
  the descriptive DN check; and the phrase "largest available European DN resource" no longer appears.
  The note's four counts match the GWAS Catalog record for `GCST90018832` digit for digit
  (`cohort = "BBJ|UKB|FinnGen"`), so the East Asian component is a fact, not a misreading.
* **The subset actually analysed is verifiable, too.** All 1,979 variants retrieved from OpenGWAS
  carry `n = 452,280` — the European component (1,032 + 451,248), not the pooled 585,264 — so the
  note's "only the European component is analyzed here" is a checked claim.
* **`HK` means housekeeping here, never Hong Kong.** The submitted manuscript has no "Hong Kong" at
  all; its two `HK` occurrences are the reference author *Im HK*. The SI uses `HK` four times, each as
  the housekeeping arm's label against the candidate arm (`HK 87 … vs cand 84 …`). The repository is
  consistent (`hk_genes.txt` header: "HRT Atlas v1.0 human-mouse common HK set"). The one "Hong Kong"
  string in this tree lives in `code/deprecated/`, in an abandoned draft that spelled it out and never
  abbreviated it.

`data/README.md` now carries both verifications next to the ancestry-recording rule that M3 exercised.

### 2026-10-03 (tenth pass) — the SI's ACAT-O combination rule, found and gated

**Numbers: no reported number changes.** Nothing in either submitted document moved. What changes is
one column's status: the last sub-item left open by the ninth pass is closed, and the rule behind it
is now written down and asserted by a gate rather than described.

The ninth pass recorded that SI Table S6's **"ACAT-O combined P"** column reproduced for only 68 of
87 cells and concluded that "the combination rule is still not established". **The conclusion was
wrong, and the error was in the check, not the archive.**

* **What was actually being computed.** The column is not an unweighted average of the tissues'
  Cauchy terms. It is a **sqrt(N)-weighted** Cauchy combination:

      p_ACAT-O = 0.5 - arctan( SUM_t w_t * tan((0.5 - p_t) * pi) / SUM_t w_t ) / pi,   w_t = sqrt(N_t)

  with `p_t = 2*Phi(-|Z_t|)`, `N_t` the GTEx v8 eQTL sample size of tissue *t* —
  **Nerve_Tibial 532, Whole_Blood 670** — component p-values clipped to `[1e-15, 1-1e-15]` and the
  result to `[1e-300, 1]`. That weighting was not a guess: the same sqrt(N) convention governs the
  `Z_multi_tissue` column of SI Table S3 (Stouffer), which reproduces to four decimals.
* **Why 68/87 looked like a rule problem.** Two independent mistakes cancelled into a plausible
  number. The tissue p-values were combined *without* weights, and the SI prints this column at
  **three significant figures** (`%.3g`) — so 19 cells were being scored against a fixed absolute
  tolerance on a grid that is 10x coarser for values near 1 than for values near 0.1. With the
  weights restored and the column compared at its own precision the count is **87/87, character for
  character**.
* **Independently corroborated.** The same rule reproduces **all 138** `P_ACAT_O` cells of SI
  Table S3 (25/138 for the unweighted form), including ACTB/DR = 0.2085, which an earlier audit had
  recorded as unreachable.
* **Made a gate, not a sentence.** `code/analyses/reproduction_20261002/scripts/recompute_acat_o.py`
  re-derives all 87 cells from `data/derived/hk_official_Z.csv` alone and exits non-zero on the first
  disagreement; `scripts/verify_from_clone.sh` §5 now runs it in the clone. A rule that "mostly
  works" is exactly the failure mode this package exists to catch, so it is asserted rather than
  described. `data/derived/hk_official_Z.csv` now carries the ACAT-O columns itself, and its Z columns
  are stored at full precision (the 4-decimal rounding previously stored flipped one cell,
  TRIP12/DPN, across a `%.3g` boundary).

**Recorded correction:** the ninth-pass entry below says the ACAT-O combination rule "is still not
established". It is established as of this pass; that clause is superseded.

### 2026-10-03 (ninth pass) — GAP-1, GAP-2, GAP-6 and GAP-8 close; nothing was ever lost, it was found

**Numbers: no reported number changes.** Not one value in `data/derived/` moved, and neither submitted
document was touched. What changed is that four gaps the archive had recorded as open are now closed —
and closed by *finding* the computations, not by re-deriving them.

The previous pass left a specific open list. Working through it against two official MetaXcan runs that
had never been catalogued closed most of it.

* **GAP-1 (SI Table S6, the housekeeping layer) — closed for the Z and model-SNP columns.** The
  archive believed the corrected layer "is not archived anywhere on disk". It is. An official MetaXcan
  v0.8.1 recompute from **2026-09-16 06:54-06:55** — the exact window in which the published Table S6
  block changed — still exists at `E://workbuddy//2026-09-15-21-55-56//metaxcan_run//official//`. Checked
  cell by cell: **all 159 numeric Z cells reproduce, max |SI − official| = 5.0 x 10⁻⁵** (agreement to
  the fourth decimal the SI prints), and the **model-SNP column is 30/30**. That also explains the
  8-gene "constant ratio" anomaly: the published table is an independent recompute, not a σᵢ rescale of
  the superseded layer, so no per-gene factor could ever have matched. The layer now ships as
  **`data/derived/hk_official_Z.csv`**. *One sub-item stays open and is recorded as such:* the SI's
  **ACAT-O combined-P** column reproduces for only 68 of 87 cells (the rest differ by ≤ 0.023), so its
  combination rule is still not established. *(Superseded the same day — see the tenth pass.)*
* **GAP-2 (Table 1 housekeeping arm) — closed.** The arm is **0.0 % (0/87)**, and re-deriving the FDR
  calls from the shipped layer returns **0/87** (most significant test: GOLGA3/DR, P = 0.0126, BH
  q = 1.00). The arm reproduces whether or not the ACAT-O rule is settled.
* **GAP-6 (SI Table S7, "Smallest margin attained") — closed.** The column is not unsourced; the
  table's own note defines it as `max(|lower|, |upper|)` of the operative 90 % interval. It is a
  deterministic function of the interval the recovered calculators already reproduce: GTEx 7.3, eQTLGen
  10.4, pooled gene-cluster 6.4 — all three match.
* **GAP-8 (SI Table S10, DN cross-population) — closed.** The official MetaXcan run of
  ebi-a-GCST90018832 (Sakaue et al. 2021) under eQTLGen weights still exists, and reproduces **all five
  genes** at the printed precision (RNH1 −0.83/0.41, CKAP4 −0.86/0.39, HSP90AB1 −0.90/0.37, RPS14
  +1.27/0.21, EEF2 −0.46/0.65). Ships as `data/derived/dn_cross_population.csv`. (Peer-review item M3 —
  name the resource's full European *and* East Asian composition — was **verified already implemented**
  in the current revision on 2026-10-03; see the eleventh pass.)
* **GAP-4 (the Fig. S1 / Fig. S2 / Fig. 1 generators) — partly recovered.** `gen_figs4.py` reproduces
  the Fig. S2 violin exactly (61-gene universe, 24/24/13, medians 374/632/669). `rebuild_fig1_2_9.py`
  holds `figure1()` (the framework = main Fig. 1) and `figure2()` (the flowchart = Fig. S1), but its
  `> 75 %` box reads `66.4-70.1 %` where the published SI prints `66.1-68.2 %` — and a contemporaneous
  record shows the published box was **pixel-edited on 2026-10-01** after a full-disk search for an SI
  figure script found nothing. So Fig. S1 is recovered **structurally**, not verbatim. Both scripts ship
  verbatim in `code/figures/recovered/`, deliberately not wired into `run_all.sh`.

Also recorded: reference **[39] in the submitted manuscript has been repointed** from the predecessor
`eqtl-source-discordance-audit` to this canonical repository (the Zenodo DOI line was deliberately left
unaltered, pending a Zenodo release of this record).

**No script was written and no value recomputed** for any of the four closures — in each case the
computation already existed on disk and had simply never been catalogued. That is the finding.

### 2026-10-03 (eighth pass) — Table S20's generator no longer needs a document we cannot ship

**Numbers: no reported number changes.** `m15_pc.py` writes the same JSON, key for key.

`Additional file 1_审稿意见修订_20260917.docx` — the review-revision Supporting Information —
was the one input that kept `scripts/r3/m15/m15_pc.py` from running on a clone, and it is a
submission document that this archive does not redistribute. It turns out not to be needed.

The generator reads exactly four tables: S1 (gene groups), S2 (GTEx baseline Z), S15
(housekeeping eQTLGen) and S18 (eQTLGen per-gene). All four also ship in `data/derived/` as
`gene_groups.csv`, `gtex_Z.csv` and `eqtlgen_Z.csv`, and the two routes were compared row for
row on 2026-10-03: 104/104, 222/222, 81/81 and 207/207 rows, **zero differing cells**. (S15
prints 90 rows, nine of them blank; the archive keeps the 81 with a testable statistic, which
is the set the script's own `q is not None` guard would keep, in the same order.)

`m15_pc.py` now tries the document first and falls back to the derived tables. Both routes were
run and the emitted JSON is identical to the archived `m15_positive_control.json` under either,
so supplying the document remains an auditable path rather than a requirement. Pass `--af1-docx`
(or `REPRO_AF1_DOCX`) to use it.

**Consequence: SI Table S20 is reproducible from a clone.** `INPUTS.md` §B.1, its §D
script-to-input table, `code/README.md` and this package's README were updated; the previous
text told a reader the row was `no` for "runs from a clone".

### 2026-10-03 (seventh pass) — `run_all.sh` runs again, and the environment installs

**Numbers: no reported number changes.** `data/derived/` is byte-identical, the three submitted
documents are untouched, and no value in the manuscript or the Supporting Information moved. What
changed is that the repository's self-declared *only supported entry point* now works.

An independent audit found that `bash code/run_all.sh` — which `README.md` and `code/README.md` both
call "the ONLY supported entry point" and which "must run end to end from a clean environment" —
**failed on a fresh clone with exit 1 and eight FAIL lines**, ending in
`Do not treat this run as reproducing the paper.`

**Fixed — four independent causes, none of them numerical:**

- **Legacy filenames were never remapped.** Seven figure scripts still asked for the predecessor's
  `*_official.csv` names, which ceased to exist when the layer moved to `data/derived/` on
  2026-10-02. `code/figures/paths_config.py` now carries the same `OFFICIAL_Z_RENAME` map its
  `code/analyses/reproduction_20261002/` counterpart already had, exposed as `rz()`. No data was
  duplicated to make this work.
- **A false-positive preflight.** `run_all.sh` greps the figure directory for the quarantined path
  `data/processed/`; the only hits were prose in `00_build_officialZ_data_layer.py` — the script that
  *writes the deprecation notice*. The prose was reworded; the guard is unchanged and still catches a
  real reference.
- **BMC-era table numbering in the figure scripts.** `04_redraw_Fig8.py` and
  `08_redraw_Fig6_labels_20260920.py` looked up SI tables by the predecessor's numbering, which the
  new Supporting Information shifted by one (Table S*n* → S*(n+1)*, old S26 promoted to S1). Both now
  resolve table numbers from the captions and accept either numbering.
- **An em dash the cell parser could not read.** The new SI writes a missing value as `—`; the
  one-line `float()` lambdas raised `ValueError: could not convert string to float: '—'`. A shared
  `paths_config.num()` now returns NaN for placeholders, thousands separators and free text.

**Fixed — the environment.** `env/environment.yml` pinned `python=3.13.0` with `numpy=1.26.4`, which
has no cp313 build on any channel, so the conda environment had no solution
(`pip download numpy==1.26.4` → `No matching distribution found`) and the Dockerfile that consumes
the same file could not build. The stack now names the versions the reproduction actually ran under,
each verified to have a cp313 wheel. `env/requirements.txt` used lower bounds throughout — against
`env/README.md` rule 1, which the file itself quotes — and now pins the same versions.
`env/Dockerfile` had four defective paths (`COPY environment.yml`, `chmod +x /app/run_all.sh`,
`ENTRYPOINT … /app/run_all.sh`, `renv::snapshot` before `WORKDIR /app`) and an `apt` pin with no
Debian candidate; all corrected.

**Changed — the figure policy is now stated.** `figures/` was empty while `README.md` called it
"archived figures exactly as submitted", `figures/README.md` argued that figures should be included,
and `.zenodo.json` said the record "contains no figures" — three positions, none true, and
`figures/README.md` itself demanded the choice be made explicitly. The policy is now: **`figures/`
holds the build outputs of `code/run_all.sh` and they are committed.** Seven figures (PDF + PNG) are
added, with a build-name → manuscript-figure map and an explicit list of the four manuscript figures
whose producing script is not in this archive (Fig. 1, S1, S2 and the wet-lab S4). `README.md` and
`.zenodo.json` were corrected to match.

**Changed — documentation that contradicted itself.** `code/README.md`'s script → manuscript-item map
was an unfilled template naming scripts that do not exist; it is now filled. `code/analyses/recovered/README.md`
still listed S9, S16 and S27–S29 as missing a month after they were closed; it now defers to
`metadata/ARCHIVE_MAP.md`. `docs/audit_notes/` gains the full repair record.

**Verified from a clone, not locally.** `bash code/run_all.sh` → exit 0, no failures, all seven figure
scripts producing output; headline check unchanged at 96 pairs / 68.8 % / ρ 0.3898. The regenerated
figures reproduce the manuscript's own legend values (Fig. 4: ρ +0.414 / 138, +0.636 / 72, +0.418 /
8,890; Fig. 3: Δρ −0.0197 and +0.0336). `scripts/verify_from_clone.sh` → 0 failures.

**Deliberately left open, and recorded as such** (`docs/audit_notes/仓库可复现性修复记录_20261003.md`):
the DOI placeholders, the unpinned `FROM …:latest`, GAP-1/GAP-2 (the housekeeping layer of Table 1),
GAP-4, GAP-6, GAP-8, the `m15_pc.py` input document, and — the finding that let all of the above ship
unnoticed — **`verify_from_clone.sh` does not run `run_all.sh`**, so a green gate says nothing about
the one entry point readers are told to use.

### 2026-10-02 (sixth pass) — the documents audited against the archive; one row does not reproduce

**No reported number changes.** New check, and one status that was wrong.

`scripts/audit_documents_vs_repo.py` answers the question a reviewer actually asks — are the
numbers in the manuscript and the Supporting Information in here — in two strengths, and says
which is which. Run against `Supporting_Information_GenetEpidemiol_20260930.docx` (31 tables)
and `Manuscript_GenetEpidemiol_20260930.docx` (4 tables):

* **Class A, structural equality** — 8 tables that are a straight projection of a shipped
  table, compared **cell by cell** after aligning rows on their key columns:
  **4,398 cells, 0 mismatches.** S2 728/728, S3 1,554/1,554, S4 420/420, S13 288/288,
  S15 243/243 (+9 declared placeholders), S18 1,035/1,035, S23 122/122, main-text
  Table 2(A) 4/4.
* **Class B, value presence** — every other table's numbers looked up in the archive at the
  precision the document prints them: **2,850 of 2,851.** Class B is a necessary condition,
  not a sufficient one, and the script says so.
* **Class C** — 8 items the archive map already declares as gaps or as needing a submission
  document, listed so the report accounts for every table instead of the easy ones.

**The single absent value is a real finding, and it changes a status.** SI Table S5a has four
data rows; `data/derived/crosscohort.csv` carries rows 1, 2 and 4 (under different labels) but
**not row 3, the √N_e direct-weighting sensitivity (pooled Z +2.09; Q 76.6; I² 98.7)**. The map
marked S5a ✅ on the strength of row 1 alone. It is now **🟡**, with the three reproducible rows
named and the fourth identified. Distribution: **19 ✅ / 13 🟡 / 5 🔴 / 9 ➖**.

Three classes of apparent mismatch turned out to be conventions, not data, and the comparator
now encodes them — each was worth 30–84 phantom cells: the documents print `—` where the CSVs
leave a field empty (Table S3); they print `Non-candidate` where the CSV holds `NonCandidate`
(Table S4); and Table S23 prints the **denominator** of a `matched/total` field, not the
numerator — which is easy to miss because for ACTB the two coincide (`23/23`) while CKAP4 prints
659 against `633/659`.

Also fixed: `paths_config.si_tables()` documented `object i = Table S(i+1)`, which is **false**.
The submitted SI splits Table S5 into two table objects (S5a, S5b), so the rule holds only up to
the fourth object — `si_labels()[6]` is `'S6'`, not `'S7'`. Nothing depended on it, but a caller
trusting it would have read the wrong table. `si_labels()` and `si_table_by_label('S5a')` now
address tables by caption, which is what the existing diagnostics were really doing.

### 2026-10-02 (fifth pass) — the last two caveats, one closed and one made specific

**No reported number changes.** S9's published values, and every other value in the Supporting
Information, are untouched. What changes is that one of the two remaining "you cannot re-run
this" statements is now false, and the other is now measured.

**S9 — closed, not merely declared.** The row said `clone (outcome)`: the published numbers
reproduce from a clone, but re-deriving the pools needs the mashr model databases, which this
archive does not distribute. That framed the wrong thing as the obstacle. The pool filters read
**one column** out of those 10.5 MB of SQLite — `n.snps.in.model`, per gene, for two tissues —
so the dependency was reduced to what is actually used and shipped as
`data/derived/mashr_nsnps.csv.gz` (61 kB; 16,812 symbols × 2 tissues). `build_pools()` now
reads the projection, and it was run with **every** source variable unset:

```
POOL_A chain: WB model genes 12,622 -> minus 104-panel 12,555 -> minus panel families 11,885
              -> minus disease blacklist = POOL_A 11,820 -> of which have BOTH-tissue models 10,450
POOL_818 = 818 (published 818), both-tissue 767 (published 767), WB-only 51 (published 51)
```

Every published figure of the chain, and the four pool files it writes came out
**byte-identical** (`git status` clean afterwards). `REPRO_MASHR_DB_DIR` is no longer needed to
re-derive anything: set it and `load_model_snps()` reads both databases *as well* and refuses to
continue unless every gene and count agrees — verified by changing one count in the projection
and confirming it reports `1 value(s) differ`. S9's locality label is therefore `clone`, and the
`clone (outcome)` label was retired: it existed for that single row and an unused category
invites the reader to hunt for the row it belongs to.

Two false dependencies were removed on the way. `build_pools()` and `copy_small()` still
demanded the *external* originals for `covariate_matrix.csv`, `Human_Mouse_Common.csv`,
`groups.json` and the three random-control files even though those ship — so the derivation
refused to run from a clone after the data layer had landed. They now prefer the shipped copy.
`copy_small()` also used raw `shutil.copyfile` on files `.gitattributes` declares `eol=lf`, which
is the same defect as the CRLF hash table: a plain copy of a CRLF source produces a shipped input
whose MD5 can never match. It uses `copy_lf`.

**S17 — the caveat is now measured rather than inherited.** The row said the gene-cluster half
needs "the housekeeping layers carried in SI Tables S6/S15". Checked, and it is
narrower and more interesting than that. The five `repo_crosscheck/verify_cluster*.py` scripts
read only `data/derived/primary_arm_96pairs.csv` and **do reproduce from a clone**. The
gene-cluster rows are one script, `bmc_ref/verify_s17_cluster.py`, and it reads four SI tables
from the `.docx`: t02 = S3, t06 = S6, t15 = S15, t18 = S18. Three of those four are redundant in
principle — S3 is `data/derived/gtex_Z.csv`, S15 and S18 are the `Group` column of
`data/derived/eqtlgen_Z.csv`. **Only t06 = S6 is genuinely absent**, and it cannot be recovered
from `gtex_Z.csv` because the housekeeping genes are excluded from the 74-gene panel by that
panel's own pre-specified rules — measured overlap **0 of 30**. The z-scores are *not* the
obstacle: the shipped wide table carries 29 of the 30 (TUT1 absent). The obstacle is the
combination rule into an ACAT-O p-value, and it is **not recovered**: recombining those
z-scores by the textbook Cauchy/ACAT-O recipe misses the published values on the *candidate*
genes, where ground truth exists (ACTB/DR: published 0.2085, recomputed 0.2116). That route is
closed until the rule is established, and saying so is more useful to a reader than "needs the
SI". The row keeps `clone + SI`, now for a reason someone can check.

**S20 is unchanged and still `clone + SI`** — its generator `m15_pc.py` reads three tables out
of Additional file 1 by position, and shipping those values is a decision about redistributing
submission content, not a reduction like the one above. It is left as it stands.

Distribution is unchanged: **20 ✅ / 12 🟡 / 5 🔴 / 9 ➖**. The locality vocabulary is now four
labels — `` `clone` `` (28 rows, was 27), `` `clone + SI` `` (2), `` `none` `` (7), `` `—` `` (9).

### 2026-10-02 (fourth pass) — checks that can fail, and a map that checks itself

**No reported number changes.** The data layer, the estimators and every value in the
Supporting Information are untouched. What changes is whether the repository can tell when
something *has* changed.

Three questions drove this pass. Each produced a defect that had been passing review.

**1. Can the archive prove a reader gets what we claim?** Not from here. Four defects have
shipped from a green pre-flight: a path bootstrap one directory level short (it compiles,
then dies at run time), a hash table recording CRLF values for files a clone checks out as
LF, a manifest hashing the working tree, and a rebuild writing a shipped input with the
platform's line ending. Every one of them passed on the machine that produced it. The checks
now run where the reader is:

- **`scripts/verify_from_clone.sh`** — makes a `git clone --no-hardlinks` into a temp
  directory and runs every check inside it, including a CRLF sweep of the checked-out tree.
  It is the definition of "it passes". `docs/RELEASE_PROCESS.md` §1 now requires it
  alongside `cut_release.sh`, and `cut_release.sh` says in its own header why it is not
  sufficient on its own.
- **`scripts/verify_provenance.py`** — recomputes every SHA-256 and byte count in
  `metadata/provenance.json` from the index, and compares. Until now nothing re-checked the
  manifest: `cut_release.sh` confirmed only that it was valid JSON and free of placeholders.

**2. Can a check fail?** Four could not.

- `paths_config.py`'s shipped-input self-check printed its verdict and **exited 0 either
  way**, so no gate could rely on it. It now exits non-zero, and `cut_release.sh` calls it.
- `check_wiring.py` gained **`--self-test`**: it runs itself against two probes of its own —
  one wired correctly, one stopped a directory short — and fails unless the first passes and
  the second is caught. That checker was vacuous once (its own directory was on `sys.path`,
  so every script "passed"), and a gate nobody has watched fail is not a gate. The
  demonstration is now part of every release.
- `check_wiring.py` also grew into a round trip: the wiring-package rebuild now writes
  `s9_pools/disease_blacklist.txt` through `write_lf()`. It was written with the default text
  mode, which translates `\n` to `os.linesep` — so **rebuilding the package on Windows broke
  the package's own integrity check**, producing a CRLF file whose MD5 did not match the LF
  value recorded in `paths_config.SHIPPED`. Reproduced, fixed, and re-verified by writing the
  file both ways.

**3. Is `metadata/ARCHIVE_MAP.md` checked at all?** It was checked by eye, and eyes stop
checking. Three defects were sitting in it:

- The `Input locality` column — added exactly to separate "verified" from "checkable by
  you" — had been written into the rows but **not into the table headers**. Markdown
  renderers drop cells beyond the header, so the column that protects the manuscript's
  conclusions was invisible in the rendered file while looking present in the source.
- An unescaped `|` inside a cell (`(\|Z\| density)`) split one row into extra cells, shifting
  every value in it one column to the right.
- The summary line is hand-maintained and had already drifted once (it read 16 ✅ / 13 🟡 /
  9 🔴 / 8 ➖ against a table holding 12 ✅ and 12 🔴).

  **`scripts/check_archive_map.py`** now enforces the column declaration, every row's cell
  count against its header, the summary counts against the status column, and a controlled
  vocabulary for the locality labels. `cut_release.sh` runs it. It was verified by
  re-introducing all three defects and confirming each is reported.

**The map now states the two axes explicitly.** The tables previously answered "is the value
right?" and "can I re-run it?" with a single mark, which is how both went wrong. `Status`
now answers only the first; `Input locality` answers only the second, from a defined
vocabulary — `` `clone` ``, `` `clone (outcome)` ``, `` `clone + SI` ``, `` `none` ``,
`` `—` `` — and the Status key says plainly that **a locality label is not a doubt about the
value**. S9 stays ✅ (the published numbers reproduce from a clone without either the mashr
databases or the original GTEx × FinnGen tables) with `clone (outcome)` recording that
*re-deriving the pools* is not possible from this archive. S16 is ✅ `clone`. S17 and S20 are
✅ `clone + SI`. Distribution is unchanged at **20 ✅ / 12 🟡 / 5 🔴 / 9 ➖**.

### 2026-10-02 (third pass) — guard rails, a self-contained check, and one convention still owed

The second pass made the package runnable and shipped the data layer. This pass adds the checks
that keep it that way, and records the two things a reader is still owed.

#### Added
- **`code/analyses/reproduction_min/`** — a single ~180-line script needing only `data/derived/`
  and numpy: no argument, no `.docx`, no network. It reproduces the headline 66/96 = 68.75 % and
  ρ = 0.38964, the per-phenotype split, the tissue-only arm (138 · 91 · 65.9 % · +0.4138) and the
  three SCZ arms (5,584 · 5,551 · 5,506 at +0.4690 · +0.4199 · +0.4465), with **15 assertions and
  0 mismatches**. It is the only 100 %-self-contained reproduction in the archive: before it, a
  reader with a bare clone could not verify a single reported number.
- **`code/analyses/reproduction_20261002/check_wiring.py`** — executes every script's import
  preamble and fails if `paths_config` is not importable. Each script carries its own
  bootstrap, and a bootstrap with the wrong depth compiles cleanly and dies at run time; 24
  scripts shipped that way in the first portable revision. The check stubs third-party modules
  it lacks, so it runs under a bare Python, and it strips this file's own directory from
  `sys.path` so it cannot pass vacuously. Called by `scripts/cut_release.sh`, which now also
  fails the release if `reproduction_min` stops reproducing under an interpreter that has numpy.
- **Table-note text for SI Table S24** in `docs/audit_notes/R2残余差异消除方案_20261002.md` §五
  item 7, with the measurement behind it: `multiZ` carries **77 exact zeros** among the 8,315
  complete-case genes; scoring a zero as positive moves the dual arm from 5,506 to **5,544**
  (+38 pairs, **+0.46 pp**), and the other two arms by +1 and +5.

#### Changed
- **The whole tree is normalised to LF.** `.gitattributes` already declared `eol=lf` for source,
  Markdown and JSON; `*.csv`, `*.tsv` and `*.txt` are now listed too. Without this a Windows
  working copy differs byte-wise from a Linux one, and `metadata/provenance.json`, which records a
  SHA-256 per file, would verify on one platform and fail on the other. The committed blobs change
  once; nothing else does.
- **`paths_config.SHIPPED_SPEC` recorded the wrong hashes — 11 of the 20 shipped inputs failed their
  own check in a clone.** The table mixed two conventions: the older entries carried the LF hashes of
  the checked-out files, the newly added ones carried the CRLF hashes of the author's originals. The
  two differ by exactly one byte per line. Consequence: `python paths_config.py` reported *all
  shipped inputs present and byte-exact* on the machine that built the package and reported
  **11 `MD5 MISMATCH` for anyone who cloned it** — i.e. the package's integrity mechanism, added to
  make the archive verifiable, failed precisely for the people it was meant to protect. Found on
  2026-10-02 by cloning `--no-hardlinks` and running the self-check inside the clone; all values are
  now the checked-out ones and the table carries a note saying to re-record them only from a clone.
- `scripts/collect_provenance.py` hashes **every tracked file** (previously three hand-picked
  directories, 36 files against a tree of 281) and records the non-redistributed reproduction
  inputs separately, with their SHA-256. `scripts/cut_release.sh` asserts
  `len(files) + len(excluded) == git ls-files`.
- `metadata/ARCHIVE_MAP.md` §8 records the re-audit that produced all of the above, including the
  one row where the mark and the reality can differ: read the **Input locality** column, not the
  mark, when you want to know whether *you* can check a row.

#### Verification
- **S16 reproduces from a clone**: all nine framework-layer rows re-run and match.
- **Table S9 reproduces from a clone without the mashr databases** — verified with
  `REPRO_MASHR_DB_DIR` unset. The pool membership ships as `data/derived/s9_pools/*.txt`, and the
  official GTEx × FinnGen layer ships flattened, so the exclusion chain 12,622 → 11,820, POOL_818
  = 818/767/51, coverage 568/768, the 16 random-control rates, the 8 null-distribution values and
  the 4 percentiles all reproduce. Re-*deriving* the pools still needs the mashr models; that is
  `00_build_added_derived.py`, not the reproduction, and it is stated on the row.
- **The BMC↔GE cross-check was re-run rather than asserted**: 83 statistics cross-checked, 63
  present in both documents, 20 in the predecessor only, **0 unique to the GE submission**. The
  predecessor *Additional file 1* carries 27 tables against the GE *Supporting Information*'s 31 —
  the `S`*n* → `S`*n+1* renumbering.
- The predecessor repository was cloned to check the `processed_officialZ/` → `derived/` mapping:
  **6 of 6 files identical line for line** (the predecessor stores them with CRLF, so its recorded
  MD5s differ from this archive's LF ones by exactly one byte per line). `code/analyses/reproduction_20261002/INPUTS.md` §A.1 records it
  as a measurement rather than an inference.
- All 18 diagnostic scripts exit 0.

#### Numbers
- **No reported number changes.** This pass adds checks, documentation and a self-contained
  reproduction script; it normalises line endings, which changes file bytes but no value.

### 2026-10-02 (second pass) — make the reproduction package runnable, and its inputs explicit

A review of the first-pass package found that it could not actually be run by anyone
else: its 35 scripts carried 26 distinct absolute paths from the author's machine, none
of them pointing at this repository, and the files they read were not committed. This
entry is the repair.

#### Fixed
- **No absolute paths remain.** Every script in `code/analyses/reproduction_20261002/`
  now resolves its inputs through `code/analyses/reproduction_20261002/paths_config.py`,
  which walks up to the repository root (sentinel `.zenodo.json`), honours `TWAS_REPO`
  and `TWAS_DATA_Z` — the same variables `code/figures/paths_config.py` uses — and
  accepts `--repo-root` / `--ms-docx` / `--si-docx` / `--af1-docx` / `--mashr-db-dir` /
  `--gtex-official-dir`. `code/README.md` rule 3 requires this and the first pass broke it.
- **Scripts no longer claim to accept a path argument without accepting one.**
  `recompute.py` and `recompute_scz.py` previously hard-coded the two documents while the
  package README said they "take a path argument".
- `scripts/recompute_scz.py` reads the gzipped Z layers through
  `paths_config.open_text()`, and records the MD5 of the **decompressed** bytes for those
  inputs so an input's recorded hash no longer depends on the compressor.
- `metadata/provenance_source.json` pointed `superseded_by` at
  `data/processed_officialZ/`, a directory that does not exist in this repository. Now
  `data/derived/`.
- The Supporting Information is read directly from the `.docx` by
  `paths_config.si_tables()`. The `tNN.tsv` files the diagnostic scripts used to read had
  never been committed.
- Three diagnostic scripts could not run at all, independently of the path problem, and
  are fixed here: `repo_crosscheck/verify_cluster3.py` built a 0-d array from a generator
  inside `np.where`; `repo_crosscheck/verify_cluster4.py` indexed a position-list with gene
  names; `r3/diag_s9_s20b.py` exec'd a preamble whose `__file__` pointed at the working
  directory rather than at the sibling script. Every script in the package now exits 0.

#### Added
- `code/analyses/reproduction_20261002/paths_config.py` — the single path entry point
  (repository-root discovery, an input registry with per-file MD5s, `si_tables()`
  extraction, and an actionable message instead of a traceback when a document is absent).
- `code/analyses/reproduction_20261002/INPUTS.md` — every input: logical name, path, MD5,
  byte count, which script reads it, whether it ships here, and where to get it if not.
- `code/analyses/reproduction_20261002/00_build_added_derived.py` — rebuilds each derived
  table added below from the upstream source that produced it.
- **3.7 MB of derived data under `data/derived/`**, so that the two largest gaps are
  closable from a clone:
  - `derived/genomewide/` — the five genome-wide weight-source Z layers, gzipped
    (2.8 MB). These define every analysis universe and the framework-layer contrast
    (S16); before this addition the framework layer was not reproducible from this
    archive at all.
  - `derived/gtex_official_finngen/gtex_official_zscores_wide.csv.gz` — the official
    MetaXcan GTEx × FinnGen layer flattened to one row per gene (0.7 MB), which feeds the
    Table S9 ACAT-O chain without its 12.3 MB of originals. Z-scores are stored as the
    original strings, not reformatted, so the median-|Z| statistics keep their digits.
  - `derived/s9_pools/`, `derived/hrt/`, `derived/hrt_random_control/`,
    `derived/groups.json`, `derived/covariate_matrix.csv` — 12 small files (0.2 MB)
    carrying the Table S9 pools, strata and random controls.
- `data/processed_officialZ/README.md` — a pointer, so the ~40 remaining references to the
  retired path (mostly under `code/deprecated/`) read as *retired* rather than *dangling*.
- `results/README.md` — separates the files a script writes from the transcripts of the
  diagnostic scripts, and says which is which.
- `results/recompute_r3_s9_s20_log.txt` — the run log the S9/S20 script declares but which
  the first pass did not commit.

#### Removed
- `scripts/r3/_patch_r3.py`, `scripts/r3/m15/_patch.py`, `scripts/r3/m15/_patch_r3.py` —
  one-off local patchers that rewrote sibling source files in place by string replacement
  and carried machine paths. Build artefacts, not deliverables.

#### Changed
- `metadata/ARCHIVE_MAP.md` — the six reproduced rows now state **where each input lives
  and whether it ships**, so ✅ is a claim a reader can check. A new section records the
  added data layer.
- `data/README.md` — the new derived tables are listed with their row counts, and the
  directory table now explains `derived/genomewide/` and the retired `processed_officialZ/`
  name.
- `code/analyses/reproduction_20261002/README.md` — the three inaccurate claims removed,
  the run instructions rewritten around `paths_config.py`, and a "what reproduces from a
  clone alone" table added.

#### Verification
- A clean copy of the tree at a different path, with no `.git` and no author directories,
  was run end to end with only the repository contents plus the two journal documents.
  `recompute.py`, `recompute_scz.py`, `recompute_r3_s9_s20.py`, `simulation_validation.py`
  and `m15_pc.py` all completed, and their machine-readable outputs match the committed
  ones key for key. The Table S9 numbers reproduce **without** either the mashr databases
  or the six original GTEx × FinnGen tables.

#### Numbers
- **No reported number changes.** This entry changes where inputs live and how they are
  named; it adds derived tables that were previously absent; and it removes three build
  artefacts. Every value the manuscript and its Supporting Information report is
  unchanged, and the re-run outputs are byte-for-byte equal to the committed results apart
  from input-file hashes.
- One incidental finding, recorded because it explains a count rather than a value:
  `data/derived/s9_pools/disease_blacklist.txt` is stored **without case normalisation**,
  faithfully to the published pipeline. The gene sets it is subtracted from are upper-cased,
  so the single token that is not already all-caps — `C5orf67` — excludes nothing. That is
  why POOL_A holds **11,820** genes and not 11,819, and `both_A` 10,450 and not 10,449.
  The published numbers are correct as printed; the exclusion step simply does not act on
  that one gene. Recorded in `code/analyses/reproduction_20261002/INPUTS.md` section F and
  in `data/README.md`.


### 2026-10-02 — third-party reproduction of both submitted documents

#### Added
- `code/analyses/reproduction_20261002/` — a self-contained reproduction package (61 files, ~3,450 lines of Python) that recomputes every value readable out of `Manuscript_GenetEpidemiol_20260930.docx` and `Supporting_Information_GenetEpidemiol_20260930.docx` from `data/derived/` and the two documents. Layout and run order in that directory's `README.md`; every script prints the MD5 of its inputs on its first line.
- `docs/audit_notes/复现核验_GE投稿两份文档_20261002.md` — the full account. Grade: **R1 ≈ 200 items identical at the reported precision, R2 = 3, R3 = 0**. No reported value failed to reproduce and none was found to differ in its point estimate.
- `docs/audit_notes/BMC定稿与GE投稿值域交叉核对_20261002.md` — the two documents against the predecessor 2026-09-28 final manuscript: 63 comparable headline statistics all identical, none unique to the new documents. Also establishes that the predecessor's *Additional file 1* and the current Supporting Information are the **same document under two numberings** (Table S*n* → S*(n+1)* for n = 1–25, plus the new S27–S30).
- `docs/audit_notes/R2残余差异消除方案_20261002.md` — remediation for the three residual items, with paste-ready SI note text.
- `code/analyses/reproduction_20261002/scripts/r3/m15/m15_pc.py` — **the missing generator for SI Table S20** (`code/figures/m15_positive_control.json` lineage), recovered verbatim.

#### Changed
- `metadata/ARCHIVE_MAP.md` — eight items moved to ✅: SI Tables **S9, S16, S17, S27, S28, S29** and **Note S5** (🔴 → ✅), and main-text **Table 2(B)** (🟡 → ✅); **S20**'s evidence row now names the recovered generator. GAP-3, GAP-5, GAP-7, GAP-9 and GAP-10 are closed. Distribution is now **20 ✅, 12 🟡, 5 🔴, 9 ➖**.
  - The status counts are now produced by a machine count of the status column. **The line previously read "16 ✅, 13 🟡, 9 🔴, 8 ➖", which did not match the table beneath it** — that table in fact held 12 ✅ and 12 🔴. Corrected here rather than carried forward.
  - Two internal cross-reference errors fixed: the Note S5 row cited "GAP-4", which the register reserves for Figs. S1 and S2 (it is GAP-5); and the S20 row described the JSON as its own carrier, which is what allowed the missing generator to go unnoticed.
- `docs/audit_notes/INDEX.md` — three rows added.

#### Numbers
- **No reported number changes.** This commit adds a reproduction package, three audit notes and the recovered S20 generator, and moves archive-map statuses to reflect what has now been reproduced. Every value the manuscript and its Supporting Information report is unchanged. The three residual R2 items are rounding-chain or undisclosed-parameter differences, not value differences; the largest is 0.04 percentage points.

### Added
- Repository consolidated as the single canonical archive for this study; full development history carried over from the predecessor repository, so the pre-specification anchors `58da15b` (2026-07-24) and `e70806b` (2026-09-10) remain reachable in this tree.
- `metadata/ARCHIVE_MAP.md`, `metadata/PRE_REGISTRATION.md`, `metadata/provenance.json`.
- `docs/RELEASE_PROCESS.md` and `scripts/cut_release.sh`.

### Changed
- Archive map re-keyed to the current Supporting Information numbering (Tables S1–S30). The predecessor `ARCHIVE_NOTE.md` used an older Additional-file numbering and is **not** carried over.
- Archive map verified item by item against `Supporting_Information_GenetEpidemiol_20260930.docx` (2026-10-02): every one of the 46 items now carries a status backed by a table title, header, column/row count or an actual cell value. The status key gained a fourth state — 🟡 **DERIVABLE** (inputs present and verified, producing step not shipped) — so that "we hold the inputs" is no longer conflated with "we can reproduce the table".

### Fixed
- `data/derived/s1_anchor_102pairs.csv` and `data/derived/s1_primary_arm_96pairs.csv` were **mis-filed in the authoritative layer**. Their ANXA1/DR values are 1.2913 / 2.1391; the authoritative table has 0.4283 / 0.9302. Their row counts (102, 96) happen to look right, which is how the error survived. Both are v2.5.0-generation output and now sit in `data/superseded/s1_cluster_robustness/`.
- The archive map no longer claims that `figures/` holds the figure files. **The repository contains no figure files** — `figures/` holds only its README; what is shipped is the *scripts* that produce some of the panels.

### Added
- `code/analyses/recovered/` — three scripts recovered from unarchived session working directories, copied verbatim. `tost_ci_calculator.py` and `tost_and_newcombe.py` were **run and reproduce the published values** (Newcombe 90% CI −9.7 to +15.4 for GTEx and −13.3 to +12.6 for eQTLGen; TOST p = 0.181/0.060/0.014 and 0.116/0.034/0.007). `scz_arm_recount_si_fix.py` recomputes from the archived four-arm SCZ table.
- `code/deprecated/si_editors/` — seven `.docx`-patching scripts, also recovered verbatim, with a README explaining the pattern they expose.
- `scripts/collect_provenance.py` — regenerates `metadata/provenance.json`; hashes the 36 files that back a reported number and records the external-input manifest.
- `metadata/provenance.json` rewritten: **36 files hashed**, 8 external inputs with identifiers, versions and the retrieval date from Supporting Information Note S4, and **no placeholders**.
- `data/README.md` external-input manifest filled from Note S4 — every resource **retrieved 2026-09-08**; software versions (official MetaXcan v0.8.1, Python 3.13.0, R 4.5.2 + MatchIt); and the GCST90043640 citation (Jiang et al. *Nat Genet* 2021;53:1616–1621, doi:10.1038/s41588-021-00954-4). External hashes are recorded as `not-held` rather than invented — nothing here claims hash verification that did not happen.

### The finding that matters more than the recovery

Several of the surviving scripts are **not computations at all**. `apply_d2_fixed_threshold.py`, `apply_d3_genomewide_control.py` and `apply_s11_hrt_restricted.py` carry their SI values as **hard-coded English prose literals** and read no data — e.g. `"...reached an FDR enrichment of 69.1% (56/8..."`. The workflow was: compute elsewhere (uncaptured) → paste the numbers into a `.docx`-patching script → write them into the Supporting Information.

So several gaps are **not** "the script got lost". The number was pasted in from something never captured. Searching for a missing script will not close them; the value has to be re-derived. Recorded in `metadata/ARCHIVE_MAP.md` §5.

### Known gaps (declared, not hidden)
- **5 items are marked 🔴** in `metadata/ARCHIVE_MAP.md` as of 2026-10-02: SI Table **S6**, SI Table **S10**, **Figs. S1 and S2**, and the value row of main-text **Table 1**. (This line previously read "9 items" and listed S9, S11, S16, S17, S27, S28 and S29 among them; S9, S16, S17, S27, S28 and S29 are now ✅ — see the 2026-10-02 entry above.) **S7 has moved from 🔴 to 🟡** — its TOST/Newcombe half is now recovered and verified; its "Smallest margin attained" column is not.
- **GAP-1 (SI Table S6) is now diagnosed, and the fault is the repository's, not the Supporting Information's.** The housekeeping Z layer here was computed on **2026-08-30**; the σᵢ correction landed **2026-09-17**. Reading the Table S6 block out of all 93 archived copies of the supplementary file and ordering them by mtime shows the published values changed between 2026-09-16 22:24 and 2026-09-17 19:15 — inside that window. Corroborating: every changed value shrinks |Z| and moves the ACAT-O P toward 0.5; 22 of 30 genes change by a constant per-gene ratio (a per-gene multiplicative correction); the model-SNP column is unchanged for all 30.
  → **`data/derived/hk_reselect/` was moved to `data/superseded/hk_reselect_20260830/`** with a full notice. The housekeeping arm of main-text Table 1 is therefore **not reproducible from this archive**.
- **Still open on GAP-1, and deliberately not closed by assumption:** 8 of 30 genes (`DNAJC4`, `E2F4`, `GOLGA3`, `SDF4`, `SRM`, `TOMM20`, `SPRYD3`, `TUT1`) do **not** follow a constant ratio, and `GOLGA3` flips sign at DPN — a pure σᵢ rescale cannot do that. The corrected computation is not archived anywhere on disk. Because it differs from the archived one by more than the σᵢ factor, SI Tables S7, S19 and S26 — which aggregate the housekeeping arm — should be re-checked against the corrected layer before submission.
- The generating scripts for the missing tables exist on the local disk only inside unarchived session directories (`2026-09-22-14-24-45/work/si_fix.py`, `2026-09-11-19-30-45/apply_d2.py`, `2026-09-11-18-13-13/_apply_edits.py`, …). They are recoverable, but nothing has been copied in yet.

### Numbers
- **No reported number changes.** This commit moves two mis-filed files out of the authoritative layer, corrects documentation, and declares gaps. Every value the manuscript reports is unaffected.

---

## [4.0.0] — 2026-10-02

### Added
- First release of the consolidated archive: analysis scripts, processed derived data, containerised environment, and archived figures.

### Numbers
- **No reported number changes in this release.** This release re-hosts the same analysed content under the canonical repository and updates metadata and repository layout only.

### Migration notes
- History imported from `wu-yijing/twas-eqtl-source-discordance`; predecessor tags were **not** imported, so `v1.0.0`–`v3.0.0` remain only in the archived repositories.
- Cite this study as concept DOI `<CONCEPT>`; for the analysed snapshot cite `10.5281/zenodo.<VER>`.

---

[Unreleased]: https://github.com/wu-yijing/eqtl-source-discordance/compare/v4.0.0...HEAD
[4.0.0]: https://github.com/wu-yijing/eqtl-source-discordance/releases/tag/v4.0.0

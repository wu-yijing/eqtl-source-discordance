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

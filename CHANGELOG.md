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

### Known gaps (declared, not hidden)
- 9 items are marked 🔴 in `metadata/ARCHIVE_MAP.md`: SI Tables S6, S7, S9, S10, S16, S17, S27, S28, S29, plus Figs. S1 and S2. No file in this repository produces them.
- **SI Table S6 is a discrepancy, not merely a gap.** Its 30 housekeeping genes match `data/derived/hk_reselect/` exactly, but every value checked differs (ANKRD40/DR GTEx-Nerve_Tibial Z: Supporting Information −0.5863, repository −0.9925; ACAT-O P 0.598 versus 0.2556). A full-disk search found no source for the published values. Because the housekeeping layer reaches the main text through Table 1, **this must be resolved before submission** — see `metadata/ARCHIVE_MAP.md` §4.
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

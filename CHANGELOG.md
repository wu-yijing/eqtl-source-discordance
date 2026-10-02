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

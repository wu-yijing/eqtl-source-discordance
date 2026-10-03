# eqtl-source-discordance

[![DOI: pending](https://img.shields.io/badge/DOI-pending%20release-orange)](DOI_PENDING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Analysis code, processed data and a containerized reproducibility environment for a methodological audit of **eQTL weight-source dependence in transcriptome-wide association studies (TWAS)**.

<!-- DOI_STATUS_BEGIN — managed by scripts/set_doi.py; the pending and published variants live together in that file. Do not edit this block by hand. -->
> ⚠️ **No published DOI yet.** This repository has not been deposited to Zenodo, so it has no citable
> identifier and the placeholders below are unresolved. Everything needed for the deposit is in the
> tree ([`.zenodo.json`](.zenodo.json), [`CITATION.cff`](CITATION.cff)); what was missing was a place
> to record the result. That is [`DOI_PENDING.md`](DOI_PENDING.md), and the backfill is one command:
> `python3 scripts/set_doi.py --concept … --version …`.
>
> Concept DOI `10.5281/zenodo.<CONCEPT>` · version DOI `10.5281/zenodo.<VER>` — **placeholders, not
> registered identifiers. Do not cite them.** See [`DOI_PENDING.md`](DOI_PENDING.md) for why the DOI
> already quoted by the associated manuscript (an earlier repository's `10.5281/zenodo.22910500`) is
> *not* a substitute: it resolves to a September 2026 snapshot that predates this repository's
> reproductions.
<!-- DOI_STATUS_END -->

---

## What this repository is

With the GWAS input and the analytic pipeline held fixed, we asked how much of a TWAS gene-candidacy result is determined by the choice of eQTL weight source (GTEx v8 versus eQTLGen). The audit

- measures source discordance on a 104-gene testbed across three diabetic microvascular complications,
- calibrates the resulting rates against disease-agnostic controls,
- benchmarks the framework genome-wide on an independent trait, and
- ships two reusable instruments: a dual-source sensitivity analysis, and a TWAS-specific reporting checklist extending STREGA.

This repository contains **code and processed data only**. Figures, figure captions, tables and table legends accompany the manuscript and its Supporting Information. Raw RNA pull-down / LC–MS/MS spectra are deposited separately in the ProteomeXchange Consortium via iProX.

---

## Quick start

```bash
git clone https://github.com/wu-yijing/eqtl-source-discordance.git
cd eqtl-source-discordance

# 1. Build the environment (choose one)
docker build -t eqtl-discordance -f env/Dockerfile .      # containerised
conda env create -f env/environment.yml                    # or conda
Rscript -e 'renv::restore()'                               # R side

# 2. Reproduce every reported value (and the figures)
bash code/run_all.sh

# Figures additionally need the Supporting Information .docx, which this archive
# does not redistribute. Point at your copy; otherwise the figure step is skipped.
AF1_DOCX=/path/to/Supporting_Information.docx bash code/run_all.sh
```

`code/run_all.sh` is the **only** supported entry point. It reads `data/derived/`, writes to a runtime output directory, and prints a value-by-value check against the manuscript. **It runs from a fresh clone** — verified by `scripts/verify_from_clone.sh`, which clones into a temp directory and runs every gate there. One input that is not redistributed here is needed by two of the six figure scripts: the Supporting Information `.docx`, pointed at with `AF1_DOCX`. Without it those two steps are **skipped and named, not failed** — the run still ends `pipeline completed with no failures` and prints a `note: these steps were SKIPPED, not failed:` line listing them. With it, all six figure scripts run and write into `figures/`. (Before 2026-10-03 those two scripts exited non-zero and the run ended `2 failure(s)`, which contradicted this paragraph; fixed in `code/run_all.sh`.)

External inputs that are not redistributed here are listed in [`data/README.md`](data/README.md), with identifiers, versions, retrieval dates and checksums. **They are linked, not copied.** [`data/external/SOURCES.tsv`](data/external/SOURCES.tsv) gives a direct download URL, the exact byte count, the licence and the redistribution decision for each of the fifteen; [`data/external/SHA256SUMS`](data/external/SHA256SUMS) gives the hash. One command joins them up:

```bash
python3 scripts/fetch_external_inputs.py --only finngen_R13_manifest   # one file, size- and hash-checked
python3 scripts/fetch_external_inputs.py --list                        # the whole set, no network
```

The full set is ~4.7 GB, which is one reason it is not in this repository. The other is that PGC3 may not be redistributed at any size.

---

## Repository layout

| Path | Contents |
|---|---|
| `code/` | Analysis, figure and simulation scripts (`code/README.md` maps each script to the manuscript item it produces) |
| `data/` | `derived/` — the tables every reported number is read from; `upstream/` — the middleware between the raw inputs and those tables, which is not obtainable elsewhere; `external/` — links, licences and hashes for the third-party inputs, which are **not** redistributed |
| `env/` | `Dockerfile`, `environment.yml`, `renv.lock`, `requirements.txt` |
| `figures/` | Build outputs of `code/figures/` (PDF + PNG), committed so a reader can compare a re-run against what was shipped. See `figures/README.md` for the build-name → manuscript-figure map and for the four manuscript figures whose producing script is not in this archive |
| `metadata/` | [`ARCHIVE_MAP.md`](metadata/ARCHIVE_MAP.md) — artefact → manuscript item; [`PRE_REGISTRATION.md`](metadata/PRE_REGISTRATION.md) — pre-specification anchors; [`zenodo_release.json`](metadata/zenodo_release.json) — the DOI registry; `provenance.json` — input checksums |
| `docs/` | [`RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md) — how releases and Zenodo archives are cut; [`audit_notes/`](docs/audit_notes/INDEX.md) — dated audit records; [`predecessors/`](docs/predecessors/README.md) — the predecessor repositories, and the files migrated out of them |
| `scripts/` | Release gates and maintenance: [`verify_from_clone.sh`](scripts/verify_from_clone.sh), [`cut_release.sh`](scripts/cut_release.sh), [`set_doi.py`](scripts/set_doi.py), [`collect_provenance.py`](scripts/collect_provenance.py), [`fetch_external_inputs.py`](scripts/fetch_external_inputs.py), [`verify_external_inputs.py`](scripts/verify_external_inputs.py), [`audit_documents_vs_repo.py`](scripts/audit_documents_vs_repo.py) |
| `DOI_PENDING.md` | The DOI slot, why it is empty, and the exact steps to fill it |

---

## Reproducibility notes

- **In a hurry?** [`code/analyses/reproduction_min/reproduce_headline.py`](code/analyses/reproduction_min/reproduce_headline.py)
  reproduces the headline result (66/96 = 68.75%, ρ = 0.38964), the per-phenotype split, the
  tissue-only arm (138 · 91 · 65.9% · ρ +0.4138) and the three SCZ arms (5,584 · 5,551 · 5,506 at
  ρ +0.4690 · +0.4199 · +0.4465) **from `data/derived/` alone** — one script, numpy only, no
  argument, no `.docx`, no network. 15 assertions; it exits non-zero if any archived value fails.
- All headline Z-scores are recomputed with the **unmodified official MetaXcan v0.8.1** binary after three-way allele harmonisation.
- An earlier in-house implementation is retained **only as an equivalence cross-check**; the maximum residual difference from the official binary was |ΔZ| = 3 × 10⁻⁸. Its layer is clearly marked as superseded in `data/README.md`.
- Every file **tracked in this repository** is hashed in `metadata/provenance.json`, regenerated by [`scripts/collect_provenance.py`](scripts/collect_provenance.py); `scripts/cut_release.sh` refuses a release whose manifest does not cover the tree.
- Inputs that are **not** redistributed here — the three submitted documents, the mashr model databases, the official MetaXcan GTEx × FinnGen originals — are listed in [`code/analyses/reproduction_20261002/INPUTS.md`](code/analyses/reproduction_20261002/INPUTS.md) section B, with the MD5/SHA-256 of the copy that produced the reported numbers, so a reader can confirm what they hold. They are *not* pinned by checksum in `provenance.json`, because this archive does not contain them. Where to *get* them is [`data/external/SOURCES.tsv`](data/external/SOURCES.tsv). One listed input, `gtex_v8_mashr_snp_covariance.txt.gz`, is a truncated download and is flagged as such there; no reported number reads it.
- `metadata/ARCHIVE_MAP.md` carries an **Input locality** column beside every status mark, and separates two questions a single mark cannot answer: **Status** says whether the reported value was re-derived and matched; **Input locality** says whether *you* can re-run it — `` `clone` ``, `` `clone (outcome)` ``, `` `clone + SI` ``, `` `none` ``, `` `—` ``. A locality label is **not** a doubt about a value: every ✅ row has been re-derived and matched, whatever the column beside it says. `scripts/check_archive_map.py` enforces the column, the counts and the vocabulary.
- **To check the check**, run [`scripts/verify_from_clone.sh`](scripts/verify_from_clone.sh): it clones the repository into a temp directory and runs every gate *there*, including a sweep for CRLF in the checked-out tree. Four defects have shipped from a green local pre-flight — a short path bootstrap, a hash table recording CRLF values for files a clone checks out as LF, a manifest hashing the working tree, a rebuild writing a shipped input with the platform's line ending — so "it passes here" is not the claim. "It passes in a clone" is.

---

## Licence

Code **and** processed data: **MIT** — see [`LICENSE`](LICENSE). This matches the data-availability statement of the associated manuscript.

---

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md). Every release entry states explicitly whether **any reported number changed**.

---

## Archived predecessors

Earlier repositories of this project are retained read-only for provenance:

| Repository | Zenodo concept DOI | Status |
|---|---|---|
| `wu-yijing/twas-eqtl-source-discordance` (formerly `TWAS-eQTL-source-confounding`) | `10.5281/zenodo.21238202` | Archived — full pre-2026-09-24 development history |
| `wu-yijing/eqtl-source-discordance-audit` | `10.5281/zenodo.22910500` | Archived — release-only snapshot. **This is the object the associated manuscript's Data availability statement currently resolves to**; see [`DOI_PENDING.md`](DOI_PENDING.md) |

**This repository is the canonical archive from v4.0.0 onward.** The version line continues across the predecessor repositories rather than restarting, so that no two releases in this project ever share a version number.

**Their contents no longer need to be fetched.** Every tracked file in both predecessors has been
compared against this tree by blob hash and given a disposition — identical here already, superseded
by a repaired copy here, migrated into [`docs/predecessors/`](docs/predecessors/README.md), or
deliberately left behind with a reason. The machine-readable record is
[`docs/predecessors/MIGRATION_MANIFEST.json`](docs/predecessors/MIGRATION_MANIFEST.json) (355 files),
and the six files actually copied out are listed in
[`docs/predecessors/README.md`](docs/predecessors/README.md).

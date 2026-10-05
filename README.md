# eqtl-source-discordance

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23129112.svg)](https://doi.org/10.5281/zenodo.23129112)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Analysis code, processed data and a containerized reproducibility environment for a methodological audit of **eQTL weight-source dependence in transcriptome-wide association studies (TWAS)**.

<!-- DOI_STATUS_BEGIN — managed by scripts/set_doi.py; the pending and published variants live together in that file. Do not edit this block by hand. -->
> **Archived, citable snapshot.** Cite the concept DOI `10.5281/zenodo.23129112` for the software and dataset —
> it always resolves to the latest archived version — or the version DOI `10.5281/zenodo.23129431` to refer to
> this exact analysed snapshot. Machine-readable form: [`CITATION.cff`](CITATION.cff). The registry
> of record is [`metadata/zenodo_release.json`](metadata/zenodo_release.json); the steps that
> produced it are in [`DOI_PENDING.md`](DOI_PENDING.md).
>
> *If you are reading this inside a Zenodo archive* of the repository, the two values above are the
> ones known when the tag was cut. The concept DOI is permanent; the version DOI may name the
> **previous** release, because a version DOI only comes into existence once its own deposit has been
> published — a tag cannot contain the DOI that its own publication mints. For the version DOI of the
> release you are reading, resolve the concept DOI, or read the registry on the current `main`.
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
- Inputs that are **not** redistributed here — the three submitted documents, the mashr model databases, the official MetaXcan GTEx × FinnGen originals — are listed in [`code/analyses/reproduction_20261002/INPUTS.md`](code/analyses/reproduction_20261002/INPUTS.md) section B, with the MD5/SHA-256 of the copy that produced the reported numbers, so a reader can confirm what they hold. They are *not* pinned by checksum in `provenance.json`, because this archive does not contain them. Where to *get* them is [`data/external/SOURCES.tsv`](data/external/SOURCES.tsv). One listed input, `gtex_v8_mashr_snp_covariance.txt.gz`, had been registered from a truncated download; it has since been traced to its source by a byte-level prefix match against Zenodo record `10.5281/zenodo.3518299`, re-hashed, and checked against the publisher's own checksum. No reported number ever read it.
- `metadata/ARCHIVE_MAP.md` carries an **Input locality** column beside every status mark, and separates two questions a single mark cannot answer: **Status** says whether the reported value was re-derived and matched; **Input locality** says whether *you* can re-run it — `` `clone` ``, `` `clone ≠ result` ``, `` `clone + SI` ``, `` `none` ``, `` `—` ``. A locality label is **not** a doubt about a value: every ✅ row has been re-derived and matched, whatever the column beside it says. `scripts/check_archive_map.py` enforces the column, the counts and the vocabulary.
- **No item is marked ❌ or 🔴 any more — and the paragraph that said one was is kept below, dated, because it is the reason the vocabulary exists.** SI Table S4 and SI Table S26 both reproduce, and `metadata/ARCHIVE_MAP.md` reports **30 ✅, 8 🟡, 0 🔴, 0 ❌, 9 ➖** (machine-counted by `scripts/check_archive_map.py`). What did not go away is narrower and is now an artefact rather than a warning: **S4's 30/30 depends on the order in which the 30 candidates are processed, and that order is only partly derivable** — positions 1–15 are the non-zero `PullDown_Unused` candidates sorted descending; positions 16–30 are a 15-way tie at 0.0 that no shipped key reproduces. The order ships as [`data/derived/s4_candidate_order.txt`](data/derived/s4_candidate_order.txt) and `scripts/check_s4_order.py` verifies it on every run. Over 500 permutations the control-set overlap is 26–30 of 30 (median 28) and 12 (2.4 %) also reach 30/30, so the order is **not unique**; no Table S26 contrast changes its significance call under any of them (P < 0.05 in 0 %). Read it as a specification-completeness gap, not a data-authenticity one. Record: [`docs/audit_notes/s4_order_sensitivity_20261005/`](docs/audit_notes/s4_order_sensitivity_20261005/README.md) and [`docs/audit_notes/s4_specification_sweep_20261004/`](docs/audit_notes/s4_specification_sweep_20261004/README.md).

  **The text this replaced, kept because the distinction it draws is the point — written 2026-10-04, superseded 2026-10-06, not rewritten.**
  > "One item is marked ❌ NOT REPRODUCED, and it is worth reading before the rest. SI Table S4 … re-running it returns a **different** matched set — best 2 of 30 control assignments over six conventions. The covariates agree exactly, so the input is right and the algorithm differs; the surviving explanation is the `MatchIt` version (4.7.2 installed, 4.5.5 in `env/renv.lock`) and it is narrowed rather than measured. The mark exists because 'we lost the script' (🔴) and 'we have the script and it disagrees' (❌) have different remedies … SI Table S26 is 🔴 and depends on S4."
  >
  > Both marks were withdrawn on measurement, not on argument: the ❌ because the control set does reproduce 30/30 in the submitted candidate order (and the `MatchIt` version was falsified as the explanation — 4.5.5 and 4.7.2 return an identical `match.matrix`), the 🔴 because S26's denominators 60 and 57 fall out of the Z layers the row itself names. Record: [`docs/audit_notes/open_items_closure_20261004/`](docs/audit_notes/open_items_closure_20261004/README.md). What survives from it is the ❌/🔴 distinction in `metadata/ARCHIVE_MAP.md`'s status key, which is why the vocabulary is still there with zero rows using it.
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
| `wu-yijing/eqtl-source-discordance-audit` | `10.5281/zenodo.22910500` | Archived — release-only snapshot. This is the object the associated manuscript's Data availability statement **used to** resolve to; as of 2026-10-04 that statement cites this repository's DOI instead. See [`DOI_PENDING.md`](DOI_PENDING.md) |

**This repository is the canonical archive from v4.0.1 onward** — the version line continues from `v4.0.0` (declared in earlier drafts but never tagged) rather than restarting, so that no two releases in this project ever share a version number.

**Their contents no longer need to be fetched.** Every tracked file in both predecessors has been
compared against this tree by blob hash and given a disposition — identical here already, superseded
by a repaired copy here, migrated into [`docs/predecessors/`](docs/predecessors/README.md), or
deliberately left behind with a reason. The machine-readable record is
[`docs/predecessors/MIGRATION_MANIFEST.json`](docs/predecessors/MIGRATION_MANIFEST.json) (355 files),
and the six files actually copied out are listed in
[`docs/predecessors/README.md`](docs/predecessors/README.md).

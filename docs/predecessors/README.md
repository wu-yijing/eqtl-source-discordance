# `docs/predecessors/` — what the predecessor repositories hold, and what was migrated here

This repository is the **canonical archive from v4.0.0 onward**. Two earlier repositories of the
same project are retained read-only for provenance, and several files in this tree still refer to
them. This directory exists so that a reader does not have to clone them to find out what they
contain, and so that every reference is traceable to a file rather than to a repository name.

Machine-readable companion: [`MIGRATION_MANIFEST.json`](MIGRATION_MANIFEST.json) — the disposition
of **every tracked file in both predecessors** (355 files), one record each.

---

## The two predecessors

| Repository | Snapshot read for this migration | Tracked files | What it is |
|---|---|---|---|
| [`wu-yijing/eqtl-source-discordance-audit`](https://github.com/wu-yijing/eqtl-source-discordance-audit) | HEAD `7e70f3d`, 2026-09-24 | 165 | Release-only snapshot of the BMC Genomics submission. **This is the object the manuscript's Data availability statement currently resolves to** (concept DOI `10.5281/zenodo.22910500`). |
| [`wu-yijing/twas-eqtl-source-discordance`](https://github.com/wu-yijing/twas-eqtl-source-discordance) | HEAD `162e113`, 2026-09-23 | 190 | Full pre-2026-09-24 development history, including the retired in-house SCZ pipeline. |

Both were verified on 2026-10-03 to be **public, not archived and not disabled** while this migration
was prepared, so no permission change was needed to read them.

> **Why this matters for a reader.** The manuscript's Data availability statement pairs a Zenodo DOI
> with a GitHub URL, and the two do not point at the same object: the DOI resolves to
> `eqtl-source-discordance-audit` **v1.0.0 (2026-09-23, a single 2.34 MB zip)**, while the URL names
> this canonical repository (v4.0.0). The Zenodo snapshot predates every gap closure recorded in
> [`../../metadata/ARCHIVE_MAP.md`](../../metadata/ARCHIVE_MAP.md), the seven committed figure build
> outputs, and the SI ACAT-O combination rule. See [`../../DOI_PENDING.md`](../../DOI_PENDING.md).

---

## Disposition of every predecessor file

Recomputed from blob hashes, not from path names — the predecessors use a **flat layout**
(`data/processed_officialZ/`, `scripts/python/`, `figure_scripts_officialZ_20260917/`) that this
repository reorganised, so a path has to be resolved by content before it can be called missing.

| Disposition | `-audit` | `twas-…` | Meaning |
|---|---|---|---|
| `content_identical_present_in_canonical` | 123 | 167 | A byte-identical blob already exists here under the canonical path. Nothing to copy. |
| `superseded_by_canonical_copy` | 30 | 15 | Same role, different bytes: the canonical copy was repaired after that snapshot (path bootstrap, CRLF, legacy data-layer name). **The canonical copy governs.** |
| `migrated_into_this_repository` | 4 | 2 | Copied verbatim into this directory by the migration below. |
| `not_migrated` | 8 | 6 | Build/configuration files for which this repository has its own replacement (`Dockerfile`, `environment.yml`, `requirements.txt`, `run_all.sh`, `.gitignore`, `data/README.md`), or a file superseded by one that already ships. Retained read-only in the predecessor. |
| **total** | **165** | **190** | |

The full path map between the predecessor layout and this one is
`MIGRATION_MANIFEST.json → path_root_map`.

---

## What was actually copied here, and how

Six files, copied **byte-for-byte and then normalised to LF** (every predecessor file is CRLF;
`.gitattributes` in this repository declares `eol=lf` for `*.md` and `*.json`). The source SHA-256
and the migrated SHA-256 of each are recorded in the manifest, so the normalisation is checkable
rather than assumed.

| Migrated file | From | Why it is worth carrying |
|---|---|---|
| [`eqtl-source-discordance-audit/ARCHIVE_NOTE.md`](eqtl-source-discordance-audit/ARCHIVE_NOTE.md) | `-audit` `ARCHIVE_NOTE.md` | The predecessor's own artefact → manuscript-item map, and the statement that v1.0.0 → v1.0.1 changed **no data file and no computed value**. This is the record of what the DOI-resolved object contains. |
| [`eqtl-source-discordance-audit/README.md`](eqtl-source-discordance-audit/README.md) | `-audit` `README.md` | The archive the manuscript's DOI resolves to, described in its own words. |
| [`eqtl-source-discordance-audit/audit_notes_README.md`](eqtl-source-discordance-audit/audit_notes_README.md) | `-audit` `audit_notes/README.md` | Contains the **2026-09-23 rebuild addendum** — the scope change that removed figure/table artefacts, the two inherited defects it repaired (four unparseable files in `s1_cluster_robustness/`, and a hard-coded path in `s1_scz_cluster.py`). This repository's [`../audit_notes/INDEX.md`](../audit_notes/INDEX.md) supersedes the index but does not carry that addendum. |
| [`twas-eqtl-source-discordance/audit_notes_README.md`](twas-eqtl-source-discordance/audit_notes_README.md) | `twas-…` `audit_notes/README.md` | The same index as it stood before the scan-archived rebuild. It differs from the `-audit` copy. |
| [`eqtl-source-discordance-audit/superseded_layer_PROVENANCE.json`](eqtl-source-discordance-audit/superseded_layer_PROVENANCE.json) | `-audit` `data/processed_officialZ/_PROVENANCE.json` | Machine-readable provenance of the **superseded (pre-σᵢ-correction) layer**: the reason it was deprecated, the 25 stale files, and the DOI of the archive it belonged to. |
| [`twas-eqtl-source-discordance/superseded_layer_PROVENANCE.json`](twas-eqtl-source-discordance/superseded_layer_PROVENANCE.json) | `twas-…` `data/processed_officialZ/_PROVENANCE.json` | The same record from the other predecessor. It differs in exactly one field — `official_reference` names that repository's DOI (`10.5281/zenodo.21238202`) instead of `22910501`. Both are kept so the DOI lineage is legible. |

### What was deliberately **not** copied

- **`figure_scripts_officialZ_20260917/`** (18 files) — already present here as
  [`../../code/figures/`](../../code/figures/), in repaired form. Copying the originals would put two
  versions of the same pipeline in one tree and make it ambiguous which one produces the figures.
- **`data/processed/` and `data/processed_officialZ/`** — already resolved by
  [`../../data/processed_officialZ/README.md`](../../data/processed_officialZ/README.md) (redirect)
  and [`../../data/superseded/README.md`](../../data/superseded/README.md) (classification).
- **`_DEPRECATED_scz_self_implemented/`, `_DEPRECATED_figure_scripts_pre20260917/`** — present here
  as [`../../code/deprecated/`](../../code/deprecated/).
- **Build and configuration files** — this repository has its own, and its own is stricter
  (pinned environment, gated entry point).

---

## How this directory is kept honest

- `MIGRATION_MANIFEST.json` is generated from `git ls-tree` blob hashes of both predecessors and of
  this repository, so `content_identical_present_in_canonical` is a measurement, not a claim.
- The migrated files are byte-identical to their sources **after** CRLF → LF normalisation, and both
  SHA-256 values are in the manifest.
- [`../../metadata/provenance.json`](../../metadata/provenance.json) covers everything here, because
  it hashes every file tracked in this repository.

*Migration performed 2026-10-03. Neither predecessor repository was modified.*

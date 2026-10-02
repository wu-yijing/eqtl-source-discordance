# data/

## What is and is not here

| Directory | Tracked in git? | Contents |
|---|---|---|
| `derived/` | **Yes** | Small processed tables that a reported number depends on. These *are* the artefact — a reader must be able to obtain them without re-running the pipeline. |
| `superseded/` | **Yes**, clearly marked | The earlier in-house implementation's output, retained **only** as an equivalence cross-check. Must never be quoted. |
| `external/` | **No** (git-ignored) | Third-party raw inputs. Not redistributed; obtain from the sources below. |

Large binaries belong in a repository, not in git: use Zenodo, figshare, or iProX (for the proteomics data) and record the accession here.

---

## External-input manifest

Every input that a reported number depends on must appear in this table, with its **identifier, version, retrieval date and checksum**. Machine-readable version: [`../metadata/provenance.json`](../metadata/provenance.json).

| Role | Source | Version | Identifier | Retrieved | SHA-256 |
|---|---|---|---|---|---|
| eQTL weight source A | GTEx v8 MASHR PredictDB models | v8 | `<url>` | `<YYYY-MM-DD>` | `<hash>` |
| eQTL weight source B | eQTLGen phase I cis-eQTL statistics | phase I | `<url>` | `<YYYY-MM-DD>` | `<hash>` |
| Primary GWAS — DR / DN / DPN | FinnGen | R13 | `<url>` | `<YYYY-MM-DD>` | `<hash>` |
| Cross-cohort GWAS | GWAS Catalog | — | GCST90043640 | `<YYYY-MM-DD>` | `<hash>` |
| Cross-population DN resource | GWAS Catalog | — | GCST90018832 | `<YYYY-MM-DD>` | `<hash>` |
| Independent-trait benchmark | PGC3 schizophrenia | wave 3 (European ancestry) | `<url>` | `<YYYY-MM-DD>` | `<hash>` |
| LD reference panel | 1000 Genomes EUR | — | `<url>` | `<YYYY-MM-DD>` | `<hash>` |
| Annotation | HRT Atlas | `<version>` | `<url>` | `<YYYY-MM-DD>` | `<hash>` |
| Proteomics | ProteomeXchange via iProX | — | **PXD083775** | `<YYYY-MM-DD>` | n/a |

### Ancestry fields — record the full picture

For every GWAS resource, record the **complete** population composition of the source, not only the component used in this analysis, and state separately which subset was used.

> GCST90018832, for example, is a cross-population diabetic-nephropathy resource that includes East Asian participants alongside European participants. A table note that lists only the European component is incomplete, and a Limitations statement that says "all GWAS analyzed here comprise participants of European ancestry" contradicts the Methods. Both defects existed in an earlier revision of this manuscript. This manifest exists to make that class of error impossible to introduce silently.

---

## Checksums

```bash
# record
sha256sum data/external/<file> >> data/external/SHA256SUMS
# verify
sha256sum -c data/external/SHA256SUMS
```

Re-verify at every release; a changed checksum on a pinned input is a change to what the archive claims to have analysed.

---

## Derived-table row counts

These are asserted in [`../metadata/ARCHIVE_MAP.md`](../metadata/ARCHIVE_MAP.md) and re-checked by `scripts/cut_release.sh`.

| File | Data rows | Supports |
|---|---|---|
| `derived/gene_groups_official.csv` | 104 | Supporting Information Table S2 |
| `derived/gtex_official_Z.csv` | 222 (74 genes × 3 phenotypes) | Supporting Information Table S3 |
| `derived/primary_arm_96pairs_official.csv` | 96 | Supporting Information Table S13 |
| `derived/eqtlgen_official_Z.csv` | 288 (96 genes × 3 phenotypes) | Supporting Information Table S18 |
| `derived/scz_z_4arm_official.csv` | 15,875 | Supporting Information Table S24 |

---

## Superseded layer

`superseded/` holds output from the earlier in-house implementation, which contained two defects: a missing S-PrediXcan σᵢ expression-variance factor, and a PLINK 2-bit decoding defect. Its maximum residual difference from the official MetaXcan v0.8.1 binary was |ΔZ| = 3 × 10⁻⁸. Both defects are disclosed in the manuscript's Methods.

**Values in `superseded/` must never be quoted in a manuscript, a response letter, or a figure.** The layer is retained solely so that the equivalence cross-check can be re-run.

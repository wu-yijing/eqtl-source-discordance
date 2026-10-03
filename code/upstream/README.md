# code/upstream/ — the raw-input → Z-layer build steps

`code/run_upstream.sh` turns the raw third-party inputs (FinnGen GWAS, GTEx
MASHR models, eQTLGen cis-eQTLs, 1000G EUR) into the Z layer that
`data/derived/` and everything downstream consumes. Two of its steps used to
assume a *middleware* that was never shipped and never built in code — the
scripts here are that middleware.

They are not part of `code/run_all.sh`: a reader who wants the reported values
needs `data/derived/`, not a 400 MB S-PrediXcan run. These are for the other
question — *was the Z layer itself produced from the inputs the archive names?*

| Script | Turns | Into |
|---|---|---|
| `build_eqtlgen_db.py` | the eQTLGen phase-I cis-eQTL summary statistics | an eQTLGen weight database in the official MetaXcan schema |
| `build_covariance.py` | a model database + `g1000_eur` (PLINK 1) | a gene-level SNP covariance `.txt.gz`. **Two row conventions** — see below |
| `align_gwas_to_model.py` | a FinnGen extract + a model database | a GWAS table whose effect allele **is** the model's |
| `split_model_by_size.py` | a model database | per-size-band databases, for memory-bounded S-PrediXcan runs |

`eqtlgen_gene_universe.txt` is the 114-symbol gene set the eQTLGen arm is
scored over (103 with a model, 11 without).

## `build_covariance.py` has two row conventions, because the two arms differ

The archived covariance files were produced by **two different producer scripts**
with **different row order**, and each set only reproduces byte-for-byte under its
own convention. `--order` selects it, and `run_upstream.sh` passes the right one per
arm:

| `--order` | genes | SNPs within a gene | arm | producer script in the audit |
|---|---|---|---|---|
| `model` | ascending gene id | model-DB row order | eQTLGen | `eq2_cov.py` |
| `bim` | model-DB insertion order | **LD panel `.bim` order** | GTEx | `mx8_pipeline.py` |

Measured, not inferred. `--order bim` reproduces `cov_Whole_Blood.txt.gz` and
`cov_Nerve_Tibial.txt.gz` with **0 differing lines**; `--order model` reproduces
`cov_A.txt.gz` (18,390,068 rows) cell for cell. For GTEx, the `.bim` convention
matches 11,382/11,382 within-gene SNP orders where a plain rsid sort matches 73.1 %
and the model-DB order 76.0 %.

**Why this was easy to get wrong.** Every wrong combination yields the *same gene
set, the same SNP pairs and the same values* — so a content comparison passes while
the file hash, and the `cov_*.txt.gz` rows in `data/external/README.md`, do not
reproduce. The first version of the script used `sorted()` genes plus model-DB SNP
order for both arms: correct by accident for the eQTLGen band (its genes are stored
ascending already), wrong for both GTEx tissues. The downstream consequence of the
GTEx ordering alone was floating-point only (max |Δ| = 3.6 × 10⁻¹⁵ over a GTEx arm's
162k cells), which is exactly why it survived a value-level check.

## Verification — the recovered steps reproduce the archived middleware

Each script below was run against the archived inputs and compared with the
copy the reported numbers came from. Comparison is by hash, not by inspection.

| Step | Output | Check | Result |
|---|---|---|---|
| `build_eqtlgen_db.py` | `eQTLGen_Whole_Blood.db` (4,866,048 B) | file SHA-256 | **byte-identical** — `413c4fff25c1820fd92f11f4370e25f3b82ea2ecd5a84ff0643d5f750312fa3c` |
| `build_covariance.py --order model` | `cov_A.txt.gz` (94 genes, 18,390,068 rows) | decompressed MD5 | **content-identical** — `ed58ccdfc590dc4498dd5ddc6c8b0ea2` |
| `build_covariance.py --order bim` | `cov_Whole_Blood.txt.gz` (1,498,762 B decompressed) | decompressed MD5 | **content-identical, 0 differing lines** — `31137589fc9ca1a261df19fba7f14e08` |
| `build_covariance.py --order bim` | `cov_Nerve_Tibial.txt.gz` (2,062,148 B decompressed) | decompressed MD5 | **content-identical, 0 differing lines** — `4ea16ad919cd0b90a693f54e8702eb59` |
| `align_gwas_to_model.py` | `gwas_{DR,DN,DPN}_aligned.tsv` | file MD5 | **byte-identical** — `3ea5fda0…` / `269358b0…` / `453e3226…` |
| `split_model_by_size.py` | `db_{A,B,C}.db` | file SHA-256 | **byte-identical** — A 3,469,312 B, B 1,007,616 B, C 380,928 B |
| `run_upstream.sh` step 1 | `gwas_{DR,DN,DPN}.tsv` | file MD5 | **byte-identical** — `390e4e9a…` / `25c53a64…` / `70c16fc9…` |
| `run_upstream.sh` step 3 | the 6 GTEx `official_*.csv` | file MD5 | **byte-identical 6/6** — e.g. Whole_Blood/DR `57738c427b957c25a6f455f5ff22c4a0` |
| `run_upstream.sh` step 7 | the 9 eQTLGen band outputs `official_eq_{A,B,C}_*` | file MD5 | **byte-identical 9/9** — e.g. `official_eq_A_DR.csv` `8590d52ee797ca76cc292e71d122f8a9` |

**The whole chain was re-run end to end on 2026-10-03** (raw third-party inputs →
`data/derived/`) with the unmodified official MetaXcan v0.8.1 under Python 3.12.13 /
numpy 1.26.4, on a machine holding all 15 hashed external inputs. Every middleware
artefact above came back byte-identical, including the eQTLGen bands
(`--order model`) and the GTEx covariance row order that `code/upstream/` had
previously got wrong. The intermediate `official_eq_{A,B,C}_*.csv` band outputs are
what the Z layer is assembled from; with all nine matching, the raw-input → Z-layer
chain has no un-run step.

The weight database is the one that matters most, because `data/external/README.md`
had described its build in prose only ("filtering this file on the 103 ENSG ids
... reproduces all 65,622 weight rows"). That sentence is now backed by a
script that writes the same 65,622 rows into the same 103-gene schema **and the
same file bytes**.

## Environment

`build_covariance.py` needs numpy; the other three are stdlib-only. The
archived run used Python 3.12 with numpy 1.x, the same interpreter the
unmodified MetaXcan 0.8.1 requires. That interpreter is now **pinned**, in
[`env/environment-upstream.yml`](../../env/environment-upstream.yml) — it cannot
share `env/environment.yml`, which pins Python 3.13 + numpy 2 and has no
installable numpy 1.x. See `code/run_upstream.sh` for the invocation.

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
| `build_covariance.py` | a model database + `g1000_eur` (PLINK 1) | a gene-level SNP covariance `.txt.gz` |
| `align_gwas_to_model.py` | a FinnGen extract + a model database | a GWAS table whose effect allele **is** the model's |
| `split_model_by_size.py` | a model database | per-size-band databases, for memory-bounded S-PrediXcan runs |

`eqtlgen_gene_universe.txt` is the 114-symbol gene set the eQTLGen arm is
scored over (103 with a model, 11 without).

## Verification — the recovered steps reproduce the archived middleware

Each script below was run against the archived inputs and compared with the
copy the reported numbers came from. Comparison is by hash, not by inspection.

| Step | Output | Check | Result |
|---|---|---|---|
| `build_eqtlgen_db.py` | `eQTLGen_Whole_Blood.db` (4,866,048 B) | file SHA-256 | **byte-identical** — `413c4fff25c1820fd92f11f4370e25f3b82ea2ecd5a84ff0643d5f750312fa3c` |
| `build_covariance.py` | `cov_eQTLGen_Whole_Blood.txt.gz` (39,366,329 rows) | decompressed MD5 (the `.gz` header carries an mtime) | **content-identical** — `7e07393d45c8927cf766425380d95b77`, 2,044,246,636 B both sides |
| `align_gwas_to_model.py` | `gwas_DN_aligned.tsv` (1,752,488 B) | file MD5 | **byte-identical** — `269358b089b2bf56a6eb8ae7df1cf831` |
| `split_model_by_size.py` | `db_{A,B,C}.db` | file size / gene count | **identical** — A 94 genes / 3,469,312 B, B 8 / 1,007,616 B, C 1 / 380,928 B |

The weight database is the one that matters most, because `data/external/README.md`
had described its build in prose only ("filtering this file on the 103 ENSG ids
... reproduces all 65,622 weight rows"). That sentence is now backed by a
script that writes the same 65,622 rows into the same 103-gene schema **and the
same file bytes**.

## Environment

`build_covariance.py` needs numpy; the other three are stdlib-only. The
archived run used Python 3.12 with numpy 1.x, the same interpreter the
unmodified MetaXcan 0.8.1 requires (see `code/run_upstream.sh`).

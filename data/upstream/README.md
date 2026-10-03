# data/upstream/ — the middleware, shipped so the Z layer can be checked

This directory carries the **as-produced outputs of `code/run_upstream.sh`** — the
middleware between the third-party raw inputs and the Z layer in `data/derived/`.

**Why it is here.** The archive already reproduces every reported value from
`data/derived/` alone, and `data/external/SHA256SUMS` pins all 15 third-party inputs
by hash. What a reader could not do, without fetching ~4.7 GB, was *check the layer in
between*: that `data/derived/` really did come from the inputs the archive names.
Shipping these 31 MiB of small artefacts makes that checkable in one command, with no
downloads and no toolchain.

**How to check it.**

```bash
python3 code/upstream/verify_middleware.py --run-dir data/upstream
```

That hashes every file below against the copy the reported numbers came from and exits
non-zero on any disagreement. It will report **27 identical, 3 missing** — the three
missing ones are the band covariances, which cannot be shipped (see below).

## What is NOT here, and why

| Artefact | Size | Why not shipped |
|---|---|---|
| `cov_A.txt.gz` | 175.2 MiB | **Over GitHub's hard 100 MiB per-file block.** GitHub rejects the push outright; the limit is not a preference. Also over the 50 MiB warning threshold. |
| `cov_C.txt.gz` | 106.4 MiB | Same — over the block. |
| `cov_B.txt.gz` | 94.6 MiB | Under the block, but shipping one band of three would not let anyone re-run the arm, and it would add 95 MiB to a 14 MiB repository for a file that is re-derivable. Recorded by content hash in `data/external/README.md` instead. |
| `cov_eQTLGen_Whole_Blood.txt.gz` | 394 MiB | Over the block. Its content MD5 (`7e07393d45c8927cf766425380d95b77`) is recorded in `data/external/README.md`. |

Everything above is rebuilt by `code/run_upstream.sh` steps 2 and 5 from the hashed
inputs in one command each, and its content hash is recorded — so its *identity* is
still pinned even where its bytes are not redistributed.

## Row order is load-bearing

`build_covariance.py` takes `--order`. The two arms use **different** row conventions,
because the archived files were produced by two different producer scripts:
`--order bim` for the GTEx tissues, `--order model` for the eQTLGen arm. See
`code/upstream/README.md`. Reproducing a file hash here requires the right one.

## Redistribution ledger — every third-party input, checked

The archive does not redistribute the 15 raw inputs. That is a decision, not an
omission, and this is the record of it. Sizes are the actual files; the licences were
read from the sources on 2026-10-03.

| Input | Size | Licence / terms as published | Redistributable? |
|---|---|---|---|
| GTEx v8 MASHR models (WB / NT) — PredictDB | 4.4 / 5.6 MiB | PredictDB publishes the site text and figures under **CC BY 4.0** and its code under MIT, and asks for citation. The model bundles themselves are a **citable Zenodo deposit**. | **Yes, with attribution** — but not re-hosted: the canonical copy is the deposit, and pointing at it is more useful than duplicating it |
| GTEx v8 expression SNP covariance (PredictDB) | 33.2 MiB | as above | as above |
| eQTLGen phase I cis-eQTL | 307.8 MiB | Resource offered to the community; **no licence entered** in the registry entry, and no explicit redistribution grant on the source site. | **No** — over the 100 MiB block *and* no explicit grant. Hash + URL recorded |
| FinnGen R13 DR / DN / DPN | 762–764 MiB each | Public "green" aggregate summary statistics; free for research after the 12-month embargo; acknowledgement and citation of Kurki et al. 2023 required. **No redistribution grant stated.** | **No** — over the block; terms do not grant redistribution |
| GCST90043640 (2 builds, UKB diabetic retinopathy) | 503.7 / 424.7 MiB | GWAS Catalog: summary statistics are released under **CC0** unless stated otherwise. | Licence **permits** it; **over the block** → not shipped |
| GCST90018832 (DN meta-analysis) | 170.1 MiB | as above (CC0) | Licence permits; over the block |
| PGC3 schizophrenia wave 3 | 228.6 MiB | PGC Data Access Terms: *"Investigators will not cross-post these data or make them available elsewhere — this website is the definitive source for these data"*, and use is *"NOT unrestricted"*. | **No — explicitly prohibited.** Over the block as well |
| 1000 Genomes Phase 3 EUR (`g1000_eur`, PredictDB bundle) | 487.9 MiB | Open data (1000 Genomes Project) | Licence permits; over the block |
| RNA pull-down / LC–MS/MS results (iProX) | 20.5 MiB | **The authors' own experiment**, deposited in ProteomeXchange via iProX under **PXD083775** (IPX0019439000 / IPX0019439001). | Under the block; **not duplicated** — the accession is the canonical, citable copy |
| MetaXcan v0.8.1 source | 6.2 MiB | **Apache 2.0**, upstream at `hakyimlab/MetaXcan` | Under the block; not duplicated — upstream is canonical and the tarball is hash-pinned here |
| FinnGen R13 endpoint manifest | 0.8 MiB | FinnGen green data (as above) | Under the block; small enough to ship, but it is not on the path that produces a reported value |

**Conclusion of the ledger.** Of the 15 inputs: 9 exceed GitHub's 100 MiB per-file hard
block and physically cannot be committed; 1 (PGC3) is under a no-cross-posting term and
must not be; 2 (GWAS Catalog) are CC0 and could be, but are over the block; and the 4
small ones are already available from a citable canonical location, so duplicating them
would add no reproducibility. Everything needed to *identify* each input — SHA-256,
byte count, source URL, version and retrieval date — is in
[`../external/README.md`](../external/README.md) and [`../README.md`](../README.md).

## Files

Total 31 MiB across 27 files; largest is 4.64 MiB. All are stored **verbatim**
(`.gitattributes`: `data/upstream/** -text`) because the official MetaXcan CSV outputs
are CRLF and the hashes below are hashes of those bytes — normalising them to LF would
make a fresh clone fail its own check.

| File | Check | Hash | Bytes | What it is |
|---|---|---|---|---|
| `cov/cov_Nerve_Tibial.txt.gz` | content_md5 | `4ea16ad919cd0b90a693f54e8702eb59` | 646,597 | GTEx NT — 14,007 genes / 38,519 rows |
| `cov/cov_Whole_Blood.txt.gz` | content_md5 | `31137589fc9ca1a261df19fba7f14e08` | 476,502 | GTEx WB — 11,382 genes / 27,985 rows |
| `eqtlgen/db_A.db` | sha256 | `f3a29eee9bf1aa4384de6b8627136c55988b077ff34af28431b3e2c9c2156d74` | 3,469,312 | band A — 94 genes / 3,469,312 B |
| `eqtlgen/db_B.db` | sha256 | `51777828c3607b5b172264f380cc9928ef19dc6b9e382abc460db0b9c8e8b966` | 1,007,616 | band B — 8 genes |
| `eqtlgen/db_C.db` | sha256 | `1617c517e030394b62a33f0466bd9904ae81b7e0e3c7cf3a20db27e84e4e66d8` | 380,928 | band C — 1 gene |
| `eqtlgen/eQTLGen_Whole_Blood.db` | sha256 | `413c4fff25c1820fd92f11f4370e25f3b82ea2ecd5a84ff0643d5f750312fa3c` | 4,866,048 | 103 genes / 65,622 weight rows |
| `eqtlgen/gwas_DN_aligned.tsv` | md5 | `269358b089b2bf56a6eb8ae7df1cf831` | 1,752,488 | re-signed onto the eQTLGen model alleles |
| `eqtlgen/gwas_DPN_aligned.tsv` | md5 | `453e3226eba6b10213aebe3a8f1e70e4` | 1,754,047 | re-signed onto the eQTLGen model alleles |
| `eqtlgen/gwas_DR_aligned.tsv` | md5 | `3ea5fda0c3cc1222318eab1f57049ae9` | 1,752,257 | re-signed onto the eQTLGen model alleles |
| `eqtlgen/official_eq_A_DN.csv` | md5 | `ae35c433289e695bfd97b6de66b5e140` | 14,260 | S-PrediXcan, eQTLGen band A x DN |
| `eqtlgen/official_eq_A_DPN.csv` | md5 | `2950f5cee032862bc0af82754cf71b82` | 14,256 | S-PrediXcan, eQTLGen band A x DPN |
| `eqtlgen/official_eq_A_DR.csv` | md5 | `8590d52ee797ca76cc292e71d122f8a9` | 14,261 | S-PrediXcan, eQTLGen band A x DR |
| `eqtlgen/official_eq_B_DN.csv` | md5 | `579082773814fe11b33ea5bf6cbaad10` | 1,398 | S-PrediXcan, eQTLGen band B x DN |
| `eqtlgen/official_eq_B_DPN.csv` | md5 | `817811fcc41790f09145f4acf4a97960` | 1,399 | S-PrediXcan, eQTLGen band B x DPN |
| `eqtlgen/official_eq_B_DR.csv` | md5 | `f704406684eda32bc6bd15ee8692ca6f` | 1,408 | S-PrediXcan, eQTLGen band B x DR |
| `eqtlgen/official_eq_C_DN.csv` | md5 | `1d6416923477fc69778bf4874f0fae3c` | 318 | S-PrediXcan, eQTLGen band C x DN |
| `eqtlgen/official_eq_C_DPN.csv` | md5 | `b01c432e5128ecc541de8f5203a4ccc0` | 318 | S-PrediXcan, eQTLGen band C x DPN |
| `eqtlgen/official_eq_C_DR.csv` | md5 | `aadc03b20c309434703f8f826311d38c` | 315 | S-PrediXcan, eQTLGen band C x DR |
| `gwas/gwas_DN.tsv` | md5 | `25c53a645397870098cbed30e17a0a1c` | 1,312,095 | FinnGen R13 extract, 37,192 rows |
| `gwas/gwas_DPN.tsv` | md5 | `70c16fc9783f225b55cc7dbc033fc5df` | 1,309,024 | FinnGen R13 extract, 37,192 rows |
| `gwas/gwas_DR.tsv` | md5 | `390e4e9abaea0464e112008a39958511` | 1,318,700 | FinnGen R13 extract, 37,192 rows |
| `official_Nerve_Tibial_DN.csv` | md5 | `1dc9106b31369aa5115322bd03fd0b7a` | 2,256,166 | S-PrediXcan, GTEx Nerve_Tibial x DN |
| `official_Nerve_Tibial_DPN.csv` | md5 | `92b942f7437b65bb0dc2658e1eb6bccb` | 2,254,949 | S-PrediXcan, GTEx Nerve_Tibial x DPN |
| `official_Nerve_Tibial_DR.csv` | md5 | `966e43e6dec03669fdd13ef44b6866d9` | 2,259,160 | S-PrediXcan, GTEx Nerve_Tibial x DR |
| `official_Whole_Blood_DN.csv` | md5 | `cce57111298a024b5e9ed5101c048f74` | 1,835,601 | S-PrediXcan, GTEx Whole_Blood x DN |
| `official_Whole_Blood_DPN.csv` | md5 | `c4bceab533b56ce928cf4c69e87462d8` | 1,834,688 | S-PrediXcan, GTEx Whole_Blood x DPN |
| `official_Whole_Blood_DR.csv` | md5 | `57738c427b957c25a6f455f5ff22c4a0` | 1,837,692 | S-PrediXcan, GTEx Whole_Blood x DR |

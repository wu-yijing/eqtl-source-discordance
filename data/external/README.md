# data/external/ — external-input manifest (hashes now recorded)
This directory is **git-ignored** (`.gitignore`: *"Raw third-party inputs are NOT redistributed. Keep only the manifest."*). The two files kept in version control are `SHA256SUMS` and this `README.md`.
`data/README.md` used to list all eight external inputs as **`not-held`, with no SHA-256** — the honest statement that the archive did not distribute them, but also the reason a reader could not check whether their download was the same file the reported numbers came from. **That column is now filled in.**
## What changed
| Before | After |
|---|---|
| `not-held` — no hash for any external input | **SHA-256 + MD5 + byte count for every input**, taken from the copy that produced the reported values |
| "nothing here is claimed to have been verified by hash" | every hash below was produced by hashing the actual file, and the upstream step it feeds has been re-run from it (§"Evidence") |
| S-PrediXcan "cannot be re-run from scratch" | all three upstream steps — the GTEx × FinnGen arm, the eQTLGen weight build, and the eQTLGen S-PrediXcan arm — have been re-run from these inputs and reproduce (byte-for-byte, or content-for-content for the gzipped covariances); the build code is under [`../../code/upstream/`](../../code/upstream/README.md) |
## The inputs
| Role | Canonical filename | Version / identifier | Bytes | SHA-256 | MD5 |
|---|---|---|---|---|---|
| eQTL weight source A — GTEx v8 MASHR, Whole_Blood | `mashr_Whole_Blood.db` | GTEx v8 / PredictDB mashr | 4,612,096 | `1f4abfeea5f0ed122e812112821cd3626f3cbde72044e5a283830e8c8e13ba0f` | `1613d73c3fcc53a27dc1422118680b97` |
| eQTL weight source A — GTEx v8 MASHR, Nerve_Tibial | `mashr_Nerve_Tibial.db` | GTEx v8 / PredictDB mashr | 5,910,528 | `48dda44649b12a046023301cdc537189a5395f266f1fb8adb3833602791a380c` | `9983e7b1557230162331839acf5ed228` |
| GTEx v8 SNP-level covariance (PredictDB mashr) | `gtex_v8_mashr_snp_covariance.txt.gz` | v8 | 2,362,720 | `5c90428be350797bcd8f855d54bddece888a63a9ea864e35fe39f6ea44b5a9c2` | `cc2a4c861095ea359da15cc31733702f` |
| eQTL weight source B — eQTLGen phase I cis-eQTL summary statistics | `2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz` | phase I, 2019-12-11, N = 31,684 | 322,775,879 | `8d963046d7b74cf3533c3510614cdc724e7ad0e325a3d2f7cca63ad13661b4c4` | `3073e2f39d0847692c053949e85723d9` |
| Primary GWAS — DR (FinnGen R13) | `finngen_R13_DM_RETINOPATHY_EXMORE.gz` | Data Freeze 13 (R13) · RETINOPATHY_EXMORE | 799,133,923 | `92652925b89943fd216510d82622baec424b7713076734728cb46443ccb4d79a` | `7cee13550d6075cad5941484013ab3f8` |
| Primary GWAS — DN (FinnGen R13) | `finngen_R13_DM_NEPHROPATHY.gz` | Data Freeze 13 (R13) · NEPHROPATHY | 801,346,330 | `9b17cbc3fb233df8113740a571f53e8efbfb0ee5f26ad23bd2640ffab35be69f` | `f6a494a2b6e24bbedc68470d91843437` |
| Primary GWAS — DPN (FinnGen R13) | `finngen_R13_DM_NEUROPATHY.gz` | Data Freeze 13 (R13) · NEUROPATHY | 800,964,581 | `5a7d603866e887b3d10dbd7b49d2f54aea79b535342e7bbc7c6058bb980f0c53` | `a40fd725f4bba44396b805d75f67b0bb` |
| FinnGen R13 endpoint manifest | `finngen_R13_manifest.tsv` | R13 | 820,805 | `c9caafa9b98ee5ef050a705766bd1c451fc2154fb8e81b069022012a2f75ae20` | `a70f4ecb57acf7c23e8f5d71be11d936` |
| Cross-cohort GWAS — UK Biobank diabetic retinopathy | `GCST90043640.h.tsv.gz` | — · GCST90043640 | 528,201,989 | `3776c85ada92559b4c6a66e27cbb0e40fa45963ce7c9f1131cd8df5e60878557` | `a802753ce87d30de09e3bc2df15c9b8c` |
| Cross-cohort GWAS — GCST90043640, GRCh37 build | `GCST90043640_buildGRCh37.tsv.gz` | — · GCST90043640 | 445,327,939 | `f84387729df2d608fa77907184f54dc32265a2c5b448a7ba81c8bc4a0c9518a3` | `9ac919a05dbd8f3e2c405520b6aa870e` |
| Independent-trait benchmark — PGC3 schizophrenia wave 3, European subset | `PGC3_SCZ_wave3.european.autosome.public.v3.vcf.tsv.gz` | wave 3 (scz2022) | 239,710,564 | `dbba3a85575c99fd1c2e3497d0c7a44539ccfdbf2e69742f8bdbda879230bcd7` | `6ebe2376f5cda972d37efa0f214c4df0` |
| LD reference panel — 1000 Genomes Phase 3, European | `g1000_eur.zip` | Phase 3 EUR | 511,626,945 | `83a48fd9dcaa0b9a874b18c63143a4ede93f05505b215b0bd8790130a0d7a954` | `1919cb5c79bbe7871aed71ae4abe6217` |
| Cross-population DN resource (GCST90018832 lineage) | `meta_egfr_dmstrat_stage1plus2.txt.gz` | — · GCST90018832 | 178,400,853 | `141114f3ae9add8a5b568b24b87bf833de4dff25fb94d66519c36f7fe8e3413f` | `ffe5a12a04492085043741ea2f0bad96` |
| Proteomics — RNA pull-down / LC-MS/MS results | `RNApull_down_MS_results.zip` | — · PXD083775 / iProX IPX0019439000 | 21,500,065 | `c50e44b1c9ab2dcca46576ec0859ae2b12baa91360f9e97a232a72d39c810a4c` | `cba90b3492f608a6005bbfb4c2f71783` |
| Toolchain — official MetaXcan (unmodified) | `MetaXcan-v0.8.1.tar.gz` | tag v0.8.1 | 6,484,124 | `3a6e1ceefef8961e10b4096e6768577ee46c67a8273087eb2d88e17be2d9f1d3` | `1cb55305a5abf81d154e0868bcd6db03` |

### Source and notes
- **mashr_Whole_Blood.db** — https://predictdb.org/post/2021/07/21/gtex-v8-models-on-eqtl-and-sqtl MD5 `1613d73c3fcc53a27dc1422118680b97` matches `INPUTS.md` §B.2 — the same copy the S9 pool filters read.
- **mashr_Nerve_Tibial.db** — https://predictdb.org/post/2021/07/21/gtex-v8-models-on-eqtl-and-sqtl MD5 `9983e7b1557230162331839acf5ed228` matches `INPUTS.md` §B.2.
- **2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz** — https://www.eqtlgen.org/ Verified to be the source of the eQTLGen arm weights: filtering this file on the 103 ENSG ids in the model database reproduces all **65,622 weight rows row-for-row** (content MD5 `8ec08cc9baaf313a602f4518d220c2f5` both sides).
- **GCST90043640.h.tsv.gz** — https://www.ebi.ac.uk/gwas/studies/GCST90043640 Downloaded as `34737426-GCST90043640-EFO_0003770.h (1).tsv.gz`. Downloaded as `34737426-GCST90043640-EFO_0003770.h (1).tsv.gz`; rename to the canonical name above to use `sha256sum -c` directly.
- **g1000_eur.zip** — https://www.internationalgenome.org/ PredictDB `g1000_eur` bundle; the eQTLGen gene covariance is computed from the `.bed/.bim/.fam` inside it.
- **RNApull_down_MS_results.zip** — https://www.iprox.cn/ Downloaded as `RNApull down MS实验结果.zip`. Downloaded as `RNApull down MS实验结果.zip`. The deposited archive is PXD083775; this is the working copy of the same experiment.

## Files that are derived, not external
**All 30 are machine-verified** by [`code/upstream/verify_middleware.py`](../../code/upstream/verify_middleware.py),
which `code/run_upstream.sh` step 8 now runs on every invocation — a rebuild that
disagrees exits non-zero instead of being described in prose.

| File | Built by | Hash of the archived copy |
|---|---|---|
| `eQTLGen_Whole_Blood.db` | [`build_eqtlgen_db.py`](../../code/upstream/build_eqtlgen_db.py) | file SHA-256 `413c4fff25c1820fd92f11f4370e25f3b82ea2ecd5a84ff0643d5f750312fa3c` · MD5 `aefbe7d485181145bd1e3ceffea2cfd6` (4,866,048 B) |
| `cov_Whole_Blood.txt.gz` | `build_covariance.py --order bim` | content MD5 `31137589fc9ca1a261df19fba7f14e08` (1,498,762 B decompressed, 11,382 genes / 27,985 rows) |
| `cov_Nerve_Tibial.txt.gz` | `build_covariance.py --order bim` | content MD5 `4ea16ad919cd0b90a693f54e8702eb59` (2,062,148 B decompressed, 14,007 genes / 38,519 rows) |
| `cov_eQTLGen_Whole_Blood.txt.gz` | `build_covariance.py --order model` | content MD5 `7e07393d45c8927cf766425380d95b77` (39,366,329 rows, 2,044,246,636 B decompressed) |
| `cov_A.txt.gz` | `build_covariance.py --order model` | content MD5 `ed58ccdfc590dc4498dd5ddc6c8b0ea2` (94 genes / 18,390,068 rows) |
| `cov_B.txt.gz` | `build_covariance.py --order model` | content MD5 `2a532e74469a340feaf0b7a791740151` (8 genes / 9,535,325 rows) |
| `cov_C.txt.gz` | `build_covariance.py --order model` | content MD5 `f30ebf0255d9eed610b6162a35be97c6` (1 gene / 11,440,936 rows) |
| `db_A.db` | [`split_model_by_size.py`](../../code/upstream/split_model_by_size.py) | file SHA-256 `f3a29eee9bf1aa4384de6b8627136c55988b077ff34af28431b3e2c9c2156d74` (94 genes / 3,469,312 B) |
| `db_B.db` | `split_model_by_size.py` | file SHA-256 `51777828c3607b5b172264f380cc9928ef19dc6b9e382abc460db0b9c8e8b966` (8 / 1,007,616 B) |
| `db_C.db` | `split_model_by_size.py` | file SHA-256 `1617c517e030394b62a33f0466bd9904ae81b7e0e3c7cf3a20db27e84e4e66d8` (1 / 380,928 B) |
| `gwas_DR.tsv` | `run_upstream.sh` step 1 | MD5 `390e4e9abaea0464e112008a39958511` |
| `gwas_DN.tsv` | step 1 | MD5 `25c53a645397870098cbed30e17a0a1c` |
| `gwas_DPN.tsv` | step 1 | MD5 `70c16fc9783f225b55cc7dbc033fc5df` |
| `gwas_DR_aligned.tsv` | [`align_gwas_to_model.py`](../../code/upstream/align_gwas_to_model.py) | MD5 `3ea5fda0c3cc1222318eab1f57049ae9` |
| `gwas_DN_aligned.tsv` | `align_gwas_to_model.py` | MD5 `269358b089b2bf56a6eb8ae7df1cf831` |
| `gwas_DPN_aligned.tsv` | `align_gwas_to_model.py` | MD5 `453e3226eba6b10213aebe3a8f1e70e4` |
| `official_Whole_Blood_{DR,DN,DPN}.csv` | step 3 (official MetaXcan v0.8.1) | MD5 `57738c427b957c25a6f455f5ff22c4a0` · `cce57111298a024b5e9ed5101c048f74` · `c4bceab533b56ce928cf4c69e87462d8` |
| `official_Nerve_Tibial_{DR,DN,DPN}.csv` | step 3 | MD5 `966e43e6dec03669fdd13ef44b6866d9` · `1dc9106b31369aa5115322bd03fd0b7a` · `92b942f7437b65bb0dc2658e1eb6bccb` |
| `official_eq_{A,B,C}_{DR,DN,DPN}.csv` (9) | step 7 (official MetaXcan, `--stream_covariance`) | MD5 `8590d52ee797ca76cc292e71d122f8a9` · `ae35c433289e695bfd97b6de66b5e140` · `2950f5cee032862bc0af82754cf71b82` · `f704406684eda32bc6bd15ee8692ca6f` · `579082773814fe11b33ea5bf6cbaad10` · `817811fcc41790f09145f4acf4a97960` · `aadc03b20c309434703f8f826311d38c` · `1d6416923477fc69778bf4874f0fae3c` · `b01c432e5128ecc541de8f5203a4ccc0` |

> **The full chain was re-run end to end on 2026-10-03** on a machine holding all 15
> hashed external inputs, with the unmodified official MetaXcan v0.8.1 under Python
> 3.12.13 / numpy 1.26.4. Result: `identical 30 | differing 0` once all three
> eQTLGen bands finished — the three `cov_A/B/C` and the nine
> `official_eq_{A,B,C}_*`. The raw-input → Z-layer chain therefore has no
> un-verified step.

> **Why the `.txt.gz` rows carry a *content* MD5, not a file hash.** A gzip stream
> embeds the wall-clock time it was written, so the same covariance built twice
> differs in the header (the archived `cov_eQTLGen_Whole_Blood.txt.gz` is 12 bytes
> larger than a re-run of the same content) while the decompressed bytes are
> identical. The content MD5 is the stable identifier; the plain-text and SQLite
> rows above are byte-identical on re-run and carry their file hash.

> **Row order inside a covariance file is load-bearing — and `build_covariance.py` had it wrong.**
> The archived covariances are ordered (1) **genes** in the model database's own order — first
> appearance in `weights`, i.e. `rowid` order, *not* alphabetical — and (2) **SNPs within a gene in
> the LD panel's `.bim` order**, not the model database's SNP order and not `sorted()` on the rsid.
> Measured directly against the archived `cov_Whole_Blood.txt.gz`: genes match
> first-appearance-restricted 11,382/11,382, and SNPs within gene match `.bim` order 11,382/11,382,
> where a plain rsid sort matches only 73.1 %.
> The first version of `code/upstream/build_covariance.py` used `sorted()` for genes and the model's
> row order for SNPs. That produced the same gene set, the same SNP pairs and the same values, so a
> *content* comparison passed — while the content MD5, and therefore the two GTEx rows above, did not
> reproduce. Found on 2026-10-03 by rebuilding both tissues and diffing line by line; fixed; both now
> rebuild to the content MD5s above with **0 differing lines**. The downstream effect of the wrong
> order was floating-point only (max |Δ| = 3.6 × 10⁻¹⁵ across the 162k cells of a GTEx arm), but the
> file hash claim was false, which is the part that matters here.

These are the intermediate layer `code/run_upstream.sh` rebuilds. They are **not** shipped, because they are re-derivable from the hashed inputs by one command each.

## Evidence that the upstream step executes
Every claim below was produced by re-running the official MetaXcan v0.8.1 binary against the hashed inputs and comparing with `cmp`, not by inspection.
| Step | Input → output | Result |
|---|---|---|
| FinnGen raw → harmonised GWAS | `finngen_R13_DM_{RETINOPATHY_EXMORE,NEPHROPATHY,NEUROPATHY}.gz` → `gwas_{DR,DN,DPN}.tsv` | **3/3 byte-identical** (MD5 `390e4e9a…`, `25c53a64…`, `70c16fc9…`) |
| S-PrediXcan, GTEx arm | `mashr_{Whole_Blood,Nerve_Tibial}.db` + `cov_*.txt.gz` + `gwas_*.tsv` → `official_*.csv` | **6/6 byte-identical** (e.g. Whole_Blood/DR MD5 `57738c427b957c25a6f455f5ff22c4a0`) |
| eQTLGen weights | eQTLGen cis-eQTL summary statistics → `eQTLGen_Whole_Blood.db` | **65,622/65,622 weight rows identical**, content MD5 `8ec08cc9baaf313a602f4518d220c2f5` both sides |
| S-PrediXcan, eQTLGen arm | `eQTLGen_Whole_Blood.db` + `cov_eQTLGen_Whole_Blood.txt.gz` + `gwas_*_aligned.tsv` → `official_eQTLGen_*.csv` | ✅ **re-run 2026-09-16** — the model was split by gene size (A/B/C) and each band run under `--stream_covariance`, which is what keeps the 111–394 MB covariance off the heap; 9/9 runs returned 0 |
| eQTLGen/GTEx Z layer | the official `official_*.csv` above → `data/derived/{eqtlgen,gtex}_Z.csv` | ✅ **reproduces the shipped layer** — every cell back-computed from the official outputs lands inside the archived tables' 4-decimal grid (eQTLGen 288/288, max abs diff 5.0 × 10⁻⁵; GTEx 360/360, max 5.0 × 10⁻⁵) |

The commands, in order, are in [`../../code/run_upstream.sh`](../../code/run_upstream.sh).
## Retrieve date — per resource, and the recommendation

Supporting Information Note S4 states one sentence for all eight resources: *"every resource was retrieved on 8 September 2026."* The hashed copies disagree for four of them.

| Resource | Date of the hashed copy | Basis |
|---|---|---|
| FinnGen R13 (3 files) | **2026-06-24** | download date of the `.gz` endpoints (manifest extracted 2026-06-25) |
| GCST90043640 (UKB DR) | **2026-06-23** | download date of the GRCh37 build; the harmonised `.h.tsv.gz` is 2026-06-24 |
| GCST90018832 (DN meta) | **2026-06-25** | download date of the deposit |
| PGC3 SCZ wave 3 | **2026-07-17** | download date of the European-subset VCF |
| eQTLGen phase I cis-eQTL | **2026-06-24** | download date of the summary statistics |
| 1000G phase 3 EUR | **2026-06-24** | download date of the `g1000_eur` bundle |
| Proteomics (iProX) | **2026-06-22** | date of the RNA pull-down LC-MS/MS result archive |
| GTEx v8 MASHR models | **2026-06-26** | extraction date of the PredictDB bundle; the `.db` payloads keep their **2019-10-03** build stamp inside the tarball |

**Recommendation — record per-resource dates, and label what each date is a date *of*.**

1. **Do not carry the blanket sentence forward.** One date for eight resources from five providers is both factually wrong here and uninformative: a reader uses a retrieval date to judge version drift at the *source*, which is a per-source question.
2. **State the verifiable thing.** The dates above are filesystem dates of the copies identified by the SHA-256 in this directory — a reader can check them. Where a resource arrives inside an archive, say so and give the payload's own build date separately (the MASHR row), because there the extraction date is the retrieval event and the internal timestamp is a property of the payload.
3. **Give both in the revised Note S4** — per-resource retrieval date **and** the SHA-256 that identifies the copy — so identity and timing are settled by the same passage.
4. **Do not restate 8 September 2026 as a retrieval date.** If that date records when this manifest was compiled or reviewed, say exactly that; a revision/compilation date presented as a retrieval date is the one option that is not available.

Until the Supporting Information is revised, the discrepancy lives here rather than being smoothed over — the same treatment `metadata/ARCHIVE_MAP.md` gives every other known gap.

## Verification
```bash
# from the repository root, with the inputs in this directory
sha256sum -c data/external/SHA256SUMS

# partial set tolerated; prints per-file ok / MISSING / MISMATCH
python3 scripts/verify_external_inputs.py --dir data/external
```

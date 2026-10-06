# INPUTS.md — what these scripts read, and where each input comes from

Every input path in this package resolves through `paths_config.py`. Nothing is
hard-coded: `code/README.md` rule 3 forbids absolute paths and personal
directories, and this file is the manifest that rule implies.

Configure once (or per run, via the flags in section C):

```bash
export TWAS_REPO=/path/to/your/clone        # default: first ancestor with .zenodo.json
export REPRO_SI_DOCX=/path/to/Supporting_Information.docx
export REPRO_MS_DOCX=/path/to/Manuscript.docx
python paths_config.py                      # prints every resolved path and self-checks MD5s
```

---

## A. Inputs that ship with this repository

`python paths_config.py` prints these and verifies each MD5. All are under
`data/derived/`.

| Logical name | File | MD5 | Bytes | Read by |
|---|---|---|---|---|
| `scz_z_4arm` | `scz_z_4arm.csv` | `b444a5d3652ff39d6a5723e96e2dce38` | 662,091 | `recompute_scz.py` |
| `gtex_Z` | `gtex_Z.csv` | `ac3e910b8e4da941f1bb71c5d2ccd018` | 12,990 | `repo_crosscheck/`, `recompute.py` |
| `eqtlgen_Z` | `eqtlgen_Z.csv` | `a63773d394308cfbdbf9c8c4ed8e9385` | 15,653 | `repo_crosscheck/`, `recompute.py` |
| `gene_groups` | `gene_groups.csv` | `f3f5ceda42cacadc5f78cec0f0899d12` | 5,610 | `repo_crosscheck/` |
| `primary_arm` | `primary_arm_96pairs.csv` | `95ad96362314861ce110610a66ffac39` | 2,842 | `repo_crosscheck/`, `r2_fix/` |
| `crosscohort` | `crosscohort.csv` | `48c6012874f83fdc959432603fbc457f` | 831 | `repo_crosscheck/` |
| `hk_genes` | `hk_genes.txt` | `eb7c1a1156029e4118cb003f3be41178` | 1,468 | — |
| `mashr_nsnps` | `mashr_nsnps.csv.gz` | `e3b549b55a509ed211e28245f316044d` | 62,725 | `00_build_added_derived.py` (pool **re-derivation**) |
| `ukb_dr_dir` | `ukb_dr/` (4 files) | — | — | `recompute.py` (Table S5a/S5b) |
| `genomewide/eqz_full.csv.gz` | eQTLGen whole-blood Z, genome-wide | `5c69596eb9e508123fb6cdd7948eda00` | 136,150 | `recompute_scz.py` |
| `genomewide/gtex_official_Whole_Blood.csv.gz` | GTEx v8 MASHR Whole_Blood Z | `7775c350817879cdf55feddd9c59c5b0` | 691,052 | `recompute_scz.py` |
| `genomewide/gtex_official_Nerve_Tibial.csv.gz` | GTEx v8 MASHR Nerve_Tibial Z | `d16dac23cd360274c557c0b1dcfd6d4c` | 857,050 | `recompute_scz.py` |
| `genomewide/en_official_en_Whole_Blood.csv.gz` | GTEx v8 elastic-net Whole_Blood Z | `a076675dea8c74347179c83e6d31cbb4` | 490,098 | `recompute_scz.py` |
| `genomewide/en_official_en_Nerve_Tibial.csv.gz` | GTEx v8 elastic-net Nerve_Tibial Z | `d320ccb64ddb7a8dd243a78751527937` | 672,935 | `recompute_scz.py` |
| `gtex_official_wide` | `gtex_official_finngen/gtex_official_zscores_wide.csv.gz` | `5c19740b0445e70d13936e939d5af558` | 735,045 | `r3/recompute_r3_s9_s20.py` |
| `covariate_matrix` | `covariate_matrix.csv` | `5efef7f83d3b8808eb0a0e7492bc0e0e` | 6,523 | `r3/recompute_r3_s9_s20.py` |
| `hrt_source` | `hrt/Human_Mouse_Common.csv` | `8403fef37ede36089b4a32b7ef95bae9` | 15,355 | `r3/recompute_r3_s9_s20.py` |
| `rand_dr` / `rand_dn` / `rand_dpn` | `hrt_random_control/official_rand_{DR,DN,DPN}.csv` | `58985581…` / `951d7a62…` / `77885fdc…` | 8,050 / 8,045 / 8,057 | `r3/recompute_r3_s9_s20.py` |
| `pool_a` / `both_a` / `pool_818` / `both_818` | `s9_pools/*.txt` | `83f9895b…` / `906bbc67…` / `b080de50…` / `d61bf5c2…` | 80,739 / 70,865 / 5,078 / 4,758 | `r3/recompute_r3_s9_s20.py` |
| `disease_blacklist` | `s9_pools/disease_blacklist.txt` | `1a150a298639bc9122fafbea9df68fc5` | 844 | `r3/recompute_r3_s9_s20.py` |

> **The MD5s above are the hashes of the files as a fresh clone checks them out**, i.e. with LF
> endings. They are deliberately *not* the hashes of the author's original CRLF copies: the two
> differ by exactly one byte per line, and the first version of this table recorded the CRLF values
> for the newly added inputs while recording the LF values for the older ones. The result was that
> `paths_config.check_shipped()` passed on the machine that built the package and **failed for every
> reader who cloned it** — 11 of the shipped inputs reported `MD5 MISMATCH`. Found on 2026-10-02 by
> cloning and running `python paths_config.py` inside the clone; the whole tree is now normalised to
> LF and the values above are the checked-out ones. Re-record them only from a clone.

The block from `genomewide/eqz_full.csv.gz` down was added on **2026-10-02** and is
built by [`00_build_added_derived.py`](00_build_added_derived.py) from the sources in
section B. Every one is a *processed table a reported number depends on*, which is
what `data/README.md` says `derived/` is for.

---

### A.1 The retired name `data/processed_officialZ/`

The scripts originally read a **second local clone of a different repository**
(`eqtl-source-discordance-audit`) at `data/processed_officialZ/`. That directory has never
existed in this repository, yet the tree referenced it 56 times. Two things now resolve it:
`paths_config.OFFICIAL_Z_RENAME` maps the five renamed files onto `data/derived/`, and
[`../../../data/processed_officialZ/README.md`](../../../data/processed_officialZ/README.md)
is a redirect for the references that remain in historical documents — the predecessor
README and the dated audit notes — where the old name is part of the record.

**Verified directly, 2026-10-02.** The predecessor repository
[`wu-yijing/eqtl-source-discordance-audit`](https://github.com/wu-yijing/eqtl-source-discordance-audit)
was cloned and its `data/processed_officialZ/` compared file by file: **6 of 6 are
byte-identical line for line** to `data/derived/`. The mapping is a measurement,
not an inference. Note that the predecessor repository stores these files with CRLF endings, so the
MD5s quoted below differ from this archive's LF ones by exactly one byte per line — the *content* is
the same file; see the note under the section A table for why that distinction is load-bearing:

| Predecessor `data/processed_officialZ/` | Here | MD5 in the predecessor (CRLF) |
|---|---|---|
| `scz_z_4arm_official.csv` | `data/derived/scz_z_4arm.csv` | `55caa68e5015a43c98f19a0556c40dd2` |
| `gtex_official_Z.csv` | `data/derived/gtex_Z.csv` | `9b8520dda0a689533ae778a431e1561d` |
| `eqtlgen_official_Z.csv` | `data/derived/eqtlgen_Z.csv` | `0e99cfce14d7216d46ef261f794ba35a` |
| `gene_groups_TableS1_official.csv` | `data/derived/gene_groups.csv` | `5fe2e3f520222899b4a7a253c4bdf3ff` |
| `primary_arm_96pairs_official.csv` | `data/derived/primary_arm_96pairs.csv` | `fc437aee0925c8b78925fae3fdf914a3` |
| `crosscohort_TableS4_official.csv` | `data/derived/crosscohort.csv` | `20b5da3ba7cc0899b8592b63881cbe34` |

---

## B. Inputs that do NOT ship here, and how to get them

`data/README.md` does not redistribute third-party raw inputs, and the submitted
documents belong to the journal. Each item below carries the MD5 and byte count of
the file that produced the numbers in `results/`, so a run either matches or says so.

### B.1 The submitted documents (3 files)

Every revision of the two submission documents that is known to exist is listed below. **The row marked "produced `results/`" is the copy the archived run was made against**; the revision rows are the later text-only edits, and the newest of them is what the next submission will carry.

`paths_config.py` resolves each document to a **`revisions` list** and *identifies which one you hold*, by MD5, naming the revision and saying whether it is the copy that produced `results/`. A supplied file that matches none of them prints `[UNRECOGNISED]` with its actual MD5 and byte count, plus every recorded revision. That is a `[UNRECOGNISED]` **notice, not a failure**, by default — a reader may legitimately hold a revision this archive has never seen — and `--strict-docs` turns it into a non-zero exit for release gates. *(Before 2026-10-03 the entry carried a single `md5` that was used only to build the "where to get it" hint, so any file at all printed `[ok]`; this paragraph's claim was not enforced by code. Fixed, and tested both ways.)*

| Document | Revision | File | MD5 | SHA-256 | Bytes |
|---|---|---|---|---|---|
| `manuscript` | pre-`[39]`-repoint | (earlier, not on disk) | `dbbe4f81a6fe9433b6a28019c6538eab` | — | 30,524 |
| `manuscript` | **produced `results/`** (submitted 2026-09-30) | `Manuscript_GenetEpidemiol_20260930.docx` | `a6f7521b98efa0e2ef247664e2f0db3a` | `ce48e337bb37a9724ec2039413d795da6ae3662c5fc4c85f52b168e83370f9a6` | 30,523 |
| `manuscript` | revision 2026-10-03 (rev2) | `Manuscript_GenetEpidemiol_20260930_rev2.docx` | `ee64dfde3903585c3dadfd8b3b257f50` | `69045bb6bd600850a32cc0e674313cca9407e37f1d1dfed79b6ece118f71c76c` | 30,524 |
| `manuscript` | revision 2026-10-03 (rev3) | `Manuscript_GenetEpidemiol_20260930_rev3.docx` | `bb9ce271dfddad5ab24cd06012298ab6` | `42dbfa1fcf8e8089069980c1730e8e75872e3569624b70d29062c7deb82446c3` | 30,720 |
| `manuscript` | **revision 2026-10-03 (rev4)** | `Manuscript_GenetEpidemiol_20260930_rev4.docx` | `709fca349e56d9361030c9e36ddf2548` | `793249b8f863890d43fc9ccdb1375fa21c06591a4e98a04987612fda7e890312` | 31,174 |
| `manuscript` | revision 2026-10-04 (rev5) | `Manuscript_GenetEpidemiol_20260930_rev5.docx` | `3449d5e01467f08e09094f9b85c94367` | `74925ccffc329f21…` | 31,167 |
| `manuscript` | revision 2026-10-04 (rev6: v4.0.2 identifiers) | `Manuscript_GenetEpidemiol_20260930_rev6.docx` | `ca7e22a9a2e10f091b061a72fa175c95` | `389c0c2adf2fbed8…` | 31,168 |
| `manuscript` | revision 2026-10-04 (rev7: `[39]` carrier → Zenodo) | `Manuscript_GenetEpidemiol_20260930_rev7.docx` | `27e9bf5cbf3785d930f27ee6f165c49f` | `ddf27dbb8f37d887…` | 31,190 |
| `manuscript` | **revision 2026-10-04 (rev8: R2 §一 unrounded-value parenthetical)** | `Manuscript_GenetEpidemiol_20260930_rev8.docx` | `7fed1b504c452e16333a59d1aef6510e` | `bae04123245dfd360dcc24b4dfa380f79f25ad8b404be3b3f7176b0aa31a11ba` | 31,223 |
| `manuscript` | **revision 2026-10-06 (rev9: the archive's commit citation brought up to date)** — newest, on disk | `Manuscript_GenetEpidemiol_20260930_rev9.docx` | `2c13e37093d86e364b8933fe32ff8afd` | `e0c1726be15b8aed9f1daf7c841567a70eef239393c1afa03831750a6da424d1` | 31,258 |
| `si` | **produced `results/`** (submitted 2026-09-30) | `Supporting_Information_GenetEpidemiol_20260930.docx` | `bd50b7f819db7851c50ddfa76ae336eb` | `132d5eb080f0021e6ee180c4b7736ada27e35a5d8e457d29815992945d17ac73` | 1,462,835 |
| `si` | revision 2026-10-03 (rev2) | `Supporting_Information_GenetEpidemiol_20260930_rev2.docx` | `72f955c9294d5228c57288ba93617f1e` | `81692586c4164286096f6c48fd289fa7ec32d6be9c2d7fbb4d32c09c02484dd8` | 1,463,194 |
| `si` | revision 2026-10-03 (rev1_dates, alternative take — not carried forward) | `Supporting_Information_…_rev1_dates.docx` | `0525627164458b587f0997180d9e63d9` | `3e468019c5457e1d…` | 1,560,626 |
| `si` | revision 2026-10-03 (rev1_dates_minimal — the take carried forward) | `Supporting_Information_…_rev1_dates_minimal.docx` | `a73ed9c8242254430b2dba142cb3de38` | `eb8bfe60cfd58d50…` | 1,463,041 |
| `si` | revision 2026-10-03 (rev3) | `Supporting_Information_…_rev3.docx` | `5446e5e0d42831009ee4a519a5703815` | `323cfa81543309ff…` | 1,463,257 |
| `si` | revision 2026-10-04 (rev4: v4.0.2 identifiers) | `Supporting_Information_…_rev4.docx` | `4fa20cde6614230a11afc1ca13529ed5` | `e69d7d324f54bf1e…` | 1,463,254 |
| `si` | revision 2026-10-04 (rev5: Note S4 Z value + S24 zero convention) | `Supporting_Information_…_rev5.docx` | `393d2399a8be2442c3be47ba548625ef` | `9109733b4e1b1bed…` | 1,561,171 |
| `si` | revision 2026-10-04 (rev6: rev5 text rebuilt on rev4 structure — the layout regression repaired, no text change) | `Supporting_Information_…_rev6.docx` | `5baf40f0fbba2fb1d50367bdc7fecb85` | `da8d464bc686b2b0f6b2259dadac7b3d1449337ea992ed35f668197823538269` | 1,463,543 |
| `si` | revision 2026-10-04 (rev7: R2 P1/P2 notes added to the Table S17 note — RNG, sorted-vector, permutation unit, sandwich/jackknife estimators) | `Supporting_Information_…_rev7.docx` | `d4ad6e348d577f55706a5d65af7ed37b` | `48135f7872b99bad125a0a0e7f0bcaf972f5575cdb9f017aae63cfe5054130e0` | 1,464,167 |
| `si` | **revision 2026-10-04 (rev8: Table S4 re-emitted — the 30 matched-control rows carry the pairing the documented specification produces; same 30 controls, same covariate values, and Table S26 is unchanged)** | `Supporting_Information_…_rev8.docx` | `08ca0b851bccad27161599db805c2222` | `8d0a0296d80b0fef654ff44e2e85f12ed8fa19cc307ce01cc162ee9ed148c15f` | 1,464,180 |
| `si` | **revision 2026-10-06 (rev9: Note S4's archive identifier brought in line with the manuscript — both now name the current main commit beside release v4.0.2)** — newest, on disk | `Supporting_Information_…_rev9.docx` | `502f79eb565ae648a6ada03041964b9c` | `f947007935a0deb0df0dff9f63787cc546342ce0720acbbc97e9025aaf625310` | 1,464,207 |
| `af1` | — | `Additional file 1_审稿意见修订_20260917.docx` | — | — | — |

`af1` is read by `r3/m15/m15_pc.py` and is **optional since 2026-10-03**: the four tables S20's generator reads (S1, S2, S15, S18) also ship as `data/derived/{gene_groups,gtex_Z,eqtlgen_Z}.csv`, verified row for row identical to the document (104/104, 222/222, 90→81/81, 207/207, zero differing cells). Supply the document and it is used instead.

Env vars: `REPRO_MS_DOCX`, `REPRO_SI_DOCX`, `REPRO_AF1_DOCX`. Read by `recompute.py`, `r3/`, `repo_crosscheck/`, `bmc_ref/`.

> **Revision history — no reported number moves in any of these steps.**
>
> | Document | Revision | MD5 | Bytes | What changed |
> |---|---|---|---|---|
> | manuscript | before the [39] repoint | `dbbe4f81a6fe9433b6a28019c6538eab` | 30,524 | — |
> | manuscript | [39] repointed to the canonical repository, and submitted | `a6f7521b98efa0e2ef247664e2f0db3a` | 30,523 | reference [39] only |
> | manuscript | 2026-10-03 revision | `ee64dfde3903585c3dadfd8b3b257f50` | 30,524 | Methods: `Python 3.13.0` → `3.13.12`, to agree with `env/environment.yml` |
> | manuscript | 2026-10-03 revision (rev3) | `bb9ce271dfddad5ab24cd06012298ab6` | 30,720 | reference `[39]` / Data availability rewritten: the cited Zenodo DOI now states that it resolves to the *predecessor* `eqtl-source-discordance-audit` snapshot and does not describe these materials, and that no citable DOI for the current version exists at submission; the canonical GitHub archive is cited with its commit. **This is the revision that closes the citation gap.** |
> | manuscript | 2026-10-03 revision (rev4) | `709fca349e56d9361030c9e36ddf2548` | 31,174 | further text revision; still no reported value or figure affected |
> | si | as submitted | `bd50b7f819db7851c50ddfa76ae336eb` | 1,462,835 | — |
> | si | 2026-10-03 revision | `72f955c9294d5228c57288ba93617f1e` | 1,463,194 | Note S4: per-resource retrieval dates replace the single-date sentence; Note S4 `Python 3.13.0` → `3.13.12`; Table S5a note: states that the row-3 heterogeneity statistics come from the quoted Z-scores, and gives the full-precision value (Q = 76.27) |
>
> Every one of these revisions is a text edit outside the analysis: **no reported value, table cell or figure changes**, which is why the archived `results/` stand. Both revisions were produced by rewriting only `word/document.xml` — every other part of each `.docx` is byte-identical to its predecessor, verified by per-part MD5.
>
> The earlier values are recorded here rather than deleted, because a reader running against an earlier file should get an explanation rather than a bare mismatch. When the 2026-10-03 revision is submitted, `results/` will still have been produced against the 2026-09-30 copies, and that is the pair this table exists to state.

Obtain them from the journal (they accompany the submission). `bmc_ref/` has two
further, optional documents — the predecessor BMC submission (`REPRO_PRED_MS_DOCX`,
`REPRO_PRED_AF1_DOCX`) — used only for the cross-check between the two manuscripts.

> The Supporting Information is read **directly from the `.docx`** by
> `paths_config.si_tables()`. An earlier version of this package depended on
> `tNN.tsv` files pre-extracted into a session directory; those are gone.
> Table object *i* is `Table S(i+1)` throughout the document (31 objects, S1–S30).

### B.2 The mashr eQTL model databases (2 files, 10.5 MB) — **optional as of 2026-10-02**

| File | MD5 | Bytes |
|---|---|---|
| `mashr_Whole_Blood.db` | `1613d73c3fcc53a27dc1422118680b97` | 4,612,096 |
| `mashr_Nerve_Tibial.db` | `9983e7b1557230162331839acf5ed228` | 5,910,528 |

Env var `REPRO_MASHR_DB_DIR`.

The pool filters read **one** column out of these files — `n.snps.in.model`, per gene, for two
tissues. That projection now ships as `data/derived/mashr_nsnps.csv.gz` (61 kB, section A), so
**nothing in this repository requires the databases any more**, including the pool
re-derivation. Set the variable anyway and `load_model_snps()` reads both databases as well and
refuses to continue unless every gene and every count agrees with the projection — a projection
that had silently drifted from the models it summarises would otherwise keep reproducing the
published chain while standing for nothing.

These are third-party model layers, so `data/README.md` keeps them out of git. Regenerating the
projection is the only operation that needs them.

### B.3 The official MetaXcan GTEx × FinnGen tables (6 files, 12.3 MB)

`official_{Nerve_Tibial,Whole_Blood}_{DR,DN,DPN}.csv`, env var
`REPRO_GTEX_OFFICIAL_DIR`. Needed only by `r3/recompute_r3_s9_s20.py`, and only to
read the per-gene Z in their original form. The shipped wide table
(`gtex_official_wide`) is a flattening of exactly these six files, one row per gene,
and the two routes have been verified to give identical Table S9 numbers. The six
files themselves are the output of `code/run_spredixcan.sh` (official MetaXcan
v0.8.1) and can be regenerated from the pinned third-party inputs in
`data/README.md`.

### B.4 The five genome-wide weight-source layers

Already shipped (section A). `00_build_added_derived.py` reads them from
`REPRO_T1_DIR` if you hold the upstream layout; that variable is only needed to
rebuild, never to reproduce.

---

## C. Command-line overrides

Every script in the package accepts these; `paths_config.apply_cli_overrides()`
maps them onto the environment variables above.

| Flag | Environment variable |
|---|---|
| `--repo-root` | `TWAS_REPO` |
| `--ms-docx` | `REPRO_MS_DOCX` |
| `--si-docx` | `REPRO_SI_DOCX` |
| `--af1-docx` | `REPRO_AF1_DOCX` |
| `--mashr-db-dir` | `REPRO_MASHR_DB_DIR` |
| `--gtex-official-dir` | `REPRO_GTEX_OFFICIAL_DIR` |
| `--strict-docs` | *(none — makes an unrecognised submission document a non-zero exit; see `report()`)* |

`TWAS_DATA_Z` overrides the authoritative data layer (default
`<TWAS_REPO>/data/derived`), matching `code/figures/paths_config.py`.

---

## D. Which script needs what

| Script | Shipped inputs | Documents | Optional bulk layers |
|---|---|---|---|
| `scripts/recompute.py` | `ukb_dr/` | manuscript, SI | — |
| `scripts/recompute_scz.py` | `scz_z_4arm`, 5 × `genomewide/` | — | — |
| `scripts/r3/recompute_r3_s9_s20.py` | `covariate_matrix`, `hrt_source`, `rand_*`, `pool_*`, `disease_blacklist`, `gtex_official_wide`, `mashr_nsnps` | SI | mashr DBs (cross-check only), GTEx official ×6 (rebuild only) |
| `scripts/r3/simulation_validation.py` | **none** | — | — |
| `scripts/r3/m15/m15_pc.py` | — | af1 (optional since 2026-10-03; falls back to `data/derived/`) | — |
| `scripts/repo_crosscheck/*` (13) | `gtex_Z`, `eqtlgen_Z`, `gene_groups`, `primary_arm` | SI (2 of them) | — |
| `scripts/bmc_ref/*` (8) | `primary_arm` | SI, manuscript, pred_manuscript, pred_af1 | — |
| `scripts/r2_fix/*` (2) | `primary_arm` | — | — |

---

## E. What reproduces from the repository alone

With only a clone — no journal documents, no third-party layers — the following
reproduce in full:

| Quantity | Value | Script |
|---|---|---|
| Headline direction consistency | 66/96 = 68.75 % | `scripts/recompute_scz.py` is not needed; compute from `data/derived/primary_arm_96pairs.csv` |
| Headline Spearman ρ | 0.38964 | as above |
| Per-phenotype | DR 23/32, DN 21/32, DPN 22/32 | as above |
| tissue-only arm | n = 138, k = 91, 65.9 %, ρ = +0.4138 | as above |
| Table S24 three SCZ arms | 5,584 / 5,551 / 5,506; ρ +0.4690 / +0.4199 / +0.4465 | `scripts/recompute_scz.py` |
| Table S16 framework layer (9 rows) | ρ +0.7970 … +0.6380 | `scripts/recompute_scz.py` |
| Table S17 empirical null | 9,048 genes, 3,617 pairs, 54.94 % | `scripts/recompute_scz.py` |
| Table S27–S29 | 84 values | `scripts/r3/simulation_validation.py` |

Requiring one of those: Table S17's gene-cluster rows and Table S20 (both read the SI
`.docx`), and the two main-text tables read out of the `.docx`.

**Table S9 does not appear in that sentence, and deliberately so.** Its published values —
the exclusion chain, `POOL_818`, the coverage counts, the 16 random-control rates, the 8
null-distribution values, the 4 percentiles and the in-pool strata — all reproduce from a
clone plus the SI `.docx`, because the pool *membership* ships as
`data/derived/s9_pools/*.txt` and the official GTEx × FinnGen layer ships flattened as
`gtex_official_finngen/gtex_official_zscores_wide.csv.gz`. **Re-deriving the pools from
scratch is also a clone-only operation as of 2026-10-02**: the mashr model databases were
10.5 MB of SQLite from which the pool filters read exactly one column, and that column now
ships as `data/derived/mashr_nsnps.csv.gz` (61 kB). Verified 2026-10-02 with every source
variable unset — `build_pools()` emitted all four pool files byte-identically and printed:

```
1. 池构建
  来源: 随仓库分发的池名单 data/derived/s9_pools/*.txt
  POOL_A = 11,820（SI: 11,820），其中双组织 10,450（SI: 10,450）
  POOL_818 = 818（SI: 818），其中双组织 767（SI: 767），仅 WB 51（SI: 51）
2. 官方 GTEx v8 逐基因 ACAT-O
  来源: data/derived/gtex_official_finngen/gtex_official_zscores_wide.csv.gz
  600 样本中官方覆盖 = 568（SI 表注: 568）；818 池中覆盖 = 768（SI: 768）
```

---

## F. Known quirk carried over deliberately

`s9_pools/disease_blacklist.txt` is written **verbatim**, without case
normalisation. The gene sets it is subtracted from are upper-cased, so a token
whose spelling is not already all-caps excludes nothing. Exactly one token is
affected — `C5orf67` — and that is why the published POOL_A is **11,820** rather
than 11,819, and `both_A` is 10,450 rather than 10,449. The reproduction keeps the
original behaviour; the discrepancy is a property of the published pipeline, not of
this package.

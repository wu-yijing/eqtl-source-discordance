# Upstream-chain closure evidence — 2026-10-04

**What this directory is.** A dated record of an **independent end-to-end execution** of
`code/run_upstream.sh`: raw third-party inputs → the middleware layer → the Z layer. It is
the evidence for the single claim that was outstanding against this archive — *"the
raw-input → Z-layer step has code but has never been run by anyone other than its author"* —
and it is kept here so that claim does not have to be re-tested.

**What was run.** `code/run_upstream.sh` at repo HEAD `7742953de514827ab78d69ea2a03dbfc6cbdd2f4`,
three times sequentially with `EQ_TAG=A`, `EQ_TAG=B`, `EQ_TAG=C`, on a machine holding all
fifteen hashed external inputs, under **unmodified official MetaXcan v0.8.1** and
**Python 3.12.15 / numpy 1.26.4**.

**Result.**

```
EQ_TAG=A exit=0 ; EQ_TAG=B exit=0 ; EQ_TAG=C exit=0 ; ALL_BANDS_DONE

  step 8 of run_upstream.sh:
  identical 30 | differing 0 | missing 0   (of 30)
  RESULT: the whole upstream chain reproduces the archived middleware.

  independent ledger (ledger/middleware_ledger.tsv):
  matched 30   mismatched 0   pending 0   (of 30)
```

Every one of the thirty middleware artefacts this chain hashes — including the three GTEx
covariances, the eQTLGen weight database, the three size-band databases, the three
size-band covariances and the nine eQTLGen band S-PrediXcan outputs — came back
**byte-identical** (or, for the `.txt.gz` covariances, content-identical after decompression,
which is the convention `data/external/README.md` records and the only one a gzip stream
admits).

---

## 1. Directory organisation

```
upstream_chain_closure_20261004/
├── README.md                      this file — scope, provenance, and how to judge closure
├── RUNBOOK.md                     how to re-run the chain and re-check this evidence
├── MANIFEST.sha256                SHA-256 of every file in this directory
├── inputs/
│   ├── verify_external_inputs.log the archive's own verifier, run over all 15 inputs
│   └── staged_inputs.tsv          15 rows: canonical name, bytes, expected/observed SHA-256
├── toolchain/
│   ├── versions.txt               python / numpy / scipy / pandas actually used
│   ├── metaxcan.txt               MetaXcan source-archive hash + the executed entry point's hash
│   └── environment.txt            repo HEAD, and every environment variable the run used
├── driver/
│   └── run_chain.sh               the exact driver that produced logs/
├── ledger/
│   ├── check_middleware.py        the ledger generator (re-runnable; see RUNBOOK.md)
│   ├── middleware_ledger.tsv      30 rows: artefact, hash kind, expected, observed, bytes, verdict
│   ├── ledger_console.txt         the same ledger as printed, with decompressed byte counts
│   └── archive_verifier.txt       `code/upstream/verify_middleware.py` run over the run directory
└── logs/
    ├── chain.log                  band-by-band exit codes
    ├── upstream_A.log             full stdout of the A-band invocation
    ├── upstream_B.log             full stdout of the B-band invocation
    ├── upstream_C.log             full stdout of the C-band invocation
    └── signals_*.txt              the same three logs with MetaXcan's FutureWarning noise removed
```

**Organising principle.** Four questions, one directory each: *what went in* (`inputs/`),
*under what* (`toolchain/`), *what was executed* (`driver/`), *what came out and did it
match* (`ledger/`), and *the raw record* (`logs/`). A reader who doubts any one of them can
attack that directory alone.

**Storage convention — line endings.** Every file here is stored with **LF** endings, as
`.gitattributes` (`* text=auto eol=lf`) requires for this repository, and `MANIFEST.sha256`
was computed over those LF bytes so that `sha256sum -c MANIFEST.sha256` succeeds from a
**fresh clone** rather than only on the machine that wrote the files. The `logs/` files were
produced on Windows and therefore carried CRLF before being committed; **the line endings
were normalised, no line was added, removed or edited.** If you need the CRLF originals for
a byte-level argument, they are not here and should not be assumed.

---

## 2. What each artefact is, and what it proves

### 2.1 `inputs/` — the run started from the bytes the archive names

| File | Source | What it proves |
|---|---|---|
| `staged_inputs.tsv` | Generated from `data/external/SHA256SUMS` + the staging directory | All **15** external inputs were present and their SHA-256 **equals the manifest value**. Two rows (`GCST90043640.h.tsv.gz`, `RNApull_down_MS_results.zip`) carry the note naming the differently-named download they were staged from; two (`mashr_*.db`) were extracted by member name from `mashr_eqtl.tar` (262,092,800 B, the byte count `data/external/SOURCES.tsv` records). |
| `verify_external_inputs.log` | `scripts/verify_external_inputs.py --dir <staging> --strict` | The archive's **own** verifier agrees, and — the part a hash match alone cannot give — reports **`incomplete 0`**. That pass decompresses every `.gz` and requires the stream to actually *end* (trailer, CRC32, ISIZE). It exists because this project was once bitten by exactly the opposite: `gtex_v8_mashr_snp_covariance.txt.gz` had been registered from a download that stopped after 6.8 % of its source file, and the recorded hash was the hash of the fragment. `incomplete 0` retires that class of doubt for the whole set. |

*Why the inputs themselves are not here:* they are ~4.7 GB, `PGC3`'s terms forbid
redistribution at any size, and `data/external/SOURCES.tsv` already gives a link, a byte
count and a redistribution decision for each. This directory records **that the right bytes
were used**, which is the part a link cannot show.

### 2.2 `toolchain/` — the run happened under the toolchain the archive claims

| File | What it proves |
|---|---|
| `versions.txt` | `python 3.12.15`, `numpy 1.26.4`, `scipy 1.13.1`, `pandas 2.2.3`. The archive says the reported numbers were produced under Python 3.12.13 / numpy 1.26.4 / scipy 1.13.1 / pandas 2.2.3 (`env/environment-upstream.yml`). **numpy and both other libraries match exactly**; Python differs at patch level only. This matters because it is the constraint that decides the whole exercise: MetaXcan 0.8.1 predates numpy 2 and `run_upstream.sh` refuses to start without numpy 1.x. |
| `metaxcan.txt` | The `MetaXcan-v0.8.1.tar.gz` SHA-256 (**`3a6e1cee…`**, equal to the `SHA256SUMS` row), plus the byte count and SHA-256 of `SPrediXcan.py` as executed. Together they say: the S-PrediXcan results below came from the **official, unmodified** binary at the pinned tag — not from a patched copy and not from the superseded in-house implementation the archive keeps under `code/deprecated/scz_self_implemented/`. |
| `environment.txt` | Repo HEAD, the clone path, and every variable the run read (`EXT_DIR`, `UPSTREAM_OUT`, `METAXCAN_SW`, `PYTHON`, `EQ_TAG`). This is what makes the run addressable rather than anecdotal. |

### 2.3 `driver/` — the exact thing that was executed

`run_chain.sh` is a four-line loop over `EQ_TAG=A B C` around `bash code/run_upstream.sh`,
with the environment exported. It is included because the chain is **band-wise by design**:
one invocation builds and runs one size band, so "the chain was run" is only a meaningful
statement if all three invocations are named. `logs/chain.log` records their exit codes.

### 2.4 `ledger/` — the decisive artefact

| File | Role |
|---|---|
| `middleware_ledger.tsv` | **The primary evidence.** 30 rows, one per artefact the chain is expected to produce: `artefact`, `path_in_run`, `hash_kind`, `expected` (transcribed from `data/external/README.md`, which is the archive's own registry of these hashes), `observed` (hashed off my run directory), `file_bytes`, `decompressed_bytes`, `verdict`. **30 × MATCH, 0 × MISMATCH.** |
| `ledger_console.txt` | The same result as printed, with the decompressed sizes spelled out — e.g. `cov_A.txt.gz ✓ MATCH ok (950,571,203 B decompressed)`. Useful because `.txt.gz` rows are compared on *content*, and a reader should be able to see that the content was actually read. |
| `check_middleware.py` | The generator. Kept so the ledger is **re-derivable rather than asserted**: `--tsv <path>` re-emits it. It contains the expected-hash table inline, transcribed from `data/external/README.md` §"Built by" — so it can be diffed against that table to confirm nothing was silently re-baselined. |
| `archive_verifier.txt` | `code/upstream/verify_middleware.py --run-dir <run>` — **the archive's own gate**, pointed at my run directory. |

> **Why two independent checks, not one.** `verify_middleware.py` is the archive's tool; if
> the archive's expected-hash table were wrong, its verifier would be wrong in the same
> direction and would still say "identical". `middleware_ledger.tsv` is a second
> implementation with the expected values transcribed from **prose** (`data/external/README.md`)
> and the observed values hashed independently. Both say 30/30. That is the difference
> between "the archive's gate passed" and "two independent readings agree".

### 2.5 `logs/` — the raw record

`upstream_A/B/C.log` are the unedited stdout of the three invocations: the preflight input
check, each build step's own measurements, the S-PrediXcan runs, and the chain's final
step-8 verdict. They are kept **unedited** (including ~60 % MetaXcan `FutureWarning` noise)
so that nothing was filtered on the way in; `signals_*.txt` are the same logs with that
noise removed, for reading.

The logs carry the measurements that make the steps auditable rather than declarative, e.g.:

```
  finngen_R13_DM_RETINOPATHY_EXMORE.gz -> 37192 rows       # step 1, matches the archive's stated 37,192
  bim rows 22,665,064, matched 17,926 (80.6%)  (10.4 s)    # step 2
  wrote 11382 genes / 27,985 rows              (1.2 s)     # step 2 — equals the recorded cov_Whole_Blood dimensions
  model SNPs per gene: median 438, range 1-5032            # step 4
  genes in universe with no model (11): ['ATG101', 'GCKR', ...]  # step 4 — the archive says 103 with a model, 11 without
  band A: 94 genes, 46,919 model SNPs -> db_A.db (3,469,312 B)
  band B:  8 genes, 13,671 model SNPs -> db_B.db (1,007,616 B)
  band C:  1 genes,  5,032 model SNPs -> db_C.db   (380,928 B)
  SHA-256: 413c4fff25c1820fd92f11f4370e25f3b82ea2ecd5a84ff0643d5f750312fa3c   # step 4, printed by the script itself
```

---

## 3. How to judge, from this directory alone, that the gap is closed

The claim under test is narrow: **the middleware layer is produced from the named raw
inputs by the named code, and reproduces the archived bytes.** Read the evidence in this
order; each step can fail independently.

| Step | Check | Where | Pass condition |
|---|---|---|---|
| 1 | Were the right inputs present? | `inputs/staged_inputs.tsv`, `inputs/verify_external_inputs.log` | 15 rows, all `MATCH`; verifier line `ok 15  mismatched 0  incomplete 0  missing 0` |
| 2 | Was the pinned toolchain used, unmodified? | `toolchain/versions.txt`, `toolchain/metaxcan.txt` | numpy 1.26.4; `MetaXcan-v0.8.1.tar.gz` SHA-256 `3a6e1cee…` = the manifest row |
| 3 | Did all three bands actually execute? | `logs/chain.log` | `EQ_TAG=A exit=0`, `=B exit=0`, `=C exit=0`, `ALL_BANDS_DONE` |
| 4 | Do the produced artefacts equal the archived ones? | `ledger/middleware_ledger.tsv` | `matched 30  mismatched 0  pending 0`, and no `MISMATCH` in the `verdict` column |
| 5 | Does the archive's **own** gate agree? | `ledger/archive_verifier.txt` | `identical 30 | differing 0 | missing 0` |
| 6 | Do the logs corroborate the intermediate quantities? | `logs/signals_upstream_*.txt` | 37,192 rows per phenotype; 11,382 genes / 27,985 rows for `cov_Whole_Blood`; 94/8/1 genes per band; the eQTLGen database printing `413c4fff…` |

**Falsifiers.** Each of these would have shown up in a file that is here, and none of them
did: a wrong row order in the GTEx covariance (`cov_Whole_Blood` content MD5 would differ —
the archive records that this happened once); a re-signed-allele error (`gwas_*_aligned.tsv`
MD5 would differ); a numpy-2 toolchain (step 0 of the chain would refuse to start, and
`logs/upstream_*.log` would end there); a patched MetaXcan (the six GTEx tables would not
land on their recorded MD5s). **A negative result was possible at every step, and the
artefact that would carry it is in this directory.**

---

## 4. What is deliberately absent, and why

| Absent | Reason |
|---|---|
| The 15 external inputs (~4.7 GB) | Not redistributable or not re-distributable at this size; `data/external/SOURCES.tsv` already carries link + bytes + licence + redistribution status. `inputs/staged_inputs.tsv` is the record that the right bytes were used. |
| The 30 middleware artefacts themselves | **27 of the 30 are already tracked** under `data/upstream/` — shipping copies would duplicate ~31 MB inside a 14 MB archive for no evidential gain, because the ledger compares hashes and the archive's own gate re-derives them. The other **3 (`cov_A/B/C.txt.gz`, 95–175 MiB each) cannot be pushed at all**: GitHub's hard per-file block is 100 MiB, which is precisely why `data/upstream/README.md` records them by *content hash* instead of shipping them. |
| The upstream run directory | ~1.4 GB of S-PrediXcan output. Re-derivable with `RUNBOOK.md`; its hashes are pinned in `ledger/middleware_ledger.tsv`. |

So this directory is not a copy of the chain's output. It is the **record that the chain ran
and matched**, which is the part that was missing.

---

## 5. Honest boundaries

- **This closes the 104-gene-testbed arm only.** `run_upstream.sh` covers FinnGen R13
  DR/DN/DPN × {GTEx v8 MASHR Whole_Blood, GTEx v8 MASHR Nerve_Tibial, eQTLGen bands A/B/C}.
  It does **not** cover (a) the **GTEx v8 elastic-net arm** that underwrites Table S16's
  `framework WB (EN_WB vs MASHR_WB)` and `tissue EN` rows, or (b) the production of the five
  **genome-wide** layers under `data/derived/genomewide/`. For (b), step 1 of this chain
  filters FinnGen to the models' SNPs (37,192 rows) and therefore *cannot* yield a
  genome-wide scan. Both remain script-less in this archive and should be stated as such
  rather than folded into "the upstream chain is closed".
- **A hash match is a match of bytes, not of intent.** These thirty artefacts are the ones
  `data/external/README.md` registers. An intermediate this archive never registered would
  not be caught here.
- **The external inputs were obtained by the author**, from the same public sources
  `data/external/SOURCES.tsv` names. Reproducing this run requires re-fetching them; for
  `PGC3` that means an application to the PGC.
- **Timing is machine-specific**: ~1 h 50 m wall clock for the three bands on one machine
  (A ≈ 45 min, B ≈ 25 min, C ≈ 35 min), dominated by `cov_A` (950 MB decompressed) and the
  streamed band-C covariance read. It is a completeness measurement, not a benchmark.

---

## 6. 中文摘要

本目录是一次**上游链端到端独立重跑**的留痕，用于一次性关闭"原始输入 → Z 层"这条此前
只有代码、没有实测的缺口，避免后续重复实测。

- **投入**：仓库自述的 15 项第三方输入全部就位且哈希命中（`incomplete 0`，即排除了"中断下载
  也能对上哈希"这一类事故）；工具链为**未改动的官方 MetaXcan v0.8.1** + Python 3.12.15 /
  numpy 1.26.4。
- **执行**：`code/run_upstream.sh` 以 `EQ_TAG=A/B/C` 连续跑三次，**三次 exit=0**。
- **结果**：链内自带 step 8 判为 `identical 30 | differing 0 | missing 0`；独立台账
  `ledger/middleware_ledger.tsv` 同样 **30/30 命中、0 失配**。两套实现相互独立（一套读归档
  内嵌哈希表，一套从 `data/external/README.md` 的散文登记值转写），结论一致才构成证据。
- **判断方法**见 §3 的六步表：输入 → 工具链 → 三次 exit 码 → 台账 → 归档自带门禁 → 日志里的
  中间量（37,192 行/表型、11,382 基因、94/8/1 分带、`413c4fff…`）。
- **边界**：只覆盖 104 基因测试台臂；EN（elastic-net）臂与全基因组层的生产链**仍无脚本**，
  不在本次闭环范围内。

## Note on the elision in ``inputs/verify_external_inputs.log`, `toolchain/environment.txt`, `logs/upstream_[ABC].log` and `logs/signals_upstream_[ABC].txt`` (2026-10-04)

Some paths in the input ledger, the toolchain fingerprint and the six run transcripts were replaced by placeholders: `<user-library>` for an R user library
on the author's machine, `<temp-workdir>` for a scratch directory used to hold a clone
during an audit, and `<user-home>` for the compiler's 8.3 short form of the same account
name. The names of the account and the machine are not evidence for anything these files
are cited to show — the versions and the resolved components are, and those are untouched.
Nothing else in the files was edited. The substitution is scripted and counted in the
2026-10-04 CHANGELOG entry, so it is reproducible rather than a hand edit.

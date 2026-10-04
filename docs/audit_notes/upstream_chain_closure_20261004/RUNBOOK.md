# RUNBOOK — re-running the upstream chain, and re-checking this evidence

Two procedures. **§1** reproduces the run. **§2** re-checks the evidence in this directory
without re-running anything (a few seconds for the ledger, ~3.5 min for the input pass).

---

## 0. Prerequisites

| Item | Requirement | Where the requirement comes from |
|---|---|---|
| The 15 external inputs | ~4.7 GB, each matching its row in `data/external/SHA256SUMS` | `data/external/SOURCES.tsv`. `PGC3` requires an application to the PGC; `RNApull_down_MS_results.zip` is this study's own deposit at iProX (PXD083775) |
| MetaXcan | tag **v0.8.1**, unmodified | `code/run_upstream.sh` header; hash in `toolchain/metaxcan.txt` |
| Interpreter | **Python 3.12 + numpy 1.x** | `env/environment-upstream.yml`. MetaXcan 0.8.1 predates numpy 2; `run_upstream.sh` step 0 refuses to start otherwise. **This cannot share `env/environment.yml`, which pins Python 3.13 + numpy 2.** |
| Disk | ≥ 4 GB for the run directory | `cov_A/B/C` decompress to 0.95 / 0.49 / 0.60 GB |

A self-contained interpreter avoids dependency surgery: a `python-build-standalone`
CPython 3.12 release plus `pip install numpy==1.26.4 scipy==1.13.1 pandas==2.2.3` is what
this run used.

### Staging the inputs under their canonical names

`verify_external_inputs.py` resolves canonical names first and falls back to the two
recorded download aliases, but staging under the canonical names keeps the ledger readable.
Two members also need extracting rather than copying:

```bash
mkdir -p /path/to/ext
cd /path/to/ext
# the 13 that arrive as single files (two of them under a different download name)
ln -s /src/34737426-GCST90043640-EFO_0003770.h\ \(1\).tsv.gz GCST90043640.h.tsv.gz
ln -s "/src/RNApull down MS实验结果.zip"                   RNApull_down_MS_results.zip
# ... and the rest verbatim: the three FinnGen files, the manifest, the eQTLGen cis-eQTL
# file, g1000_eur.zip, GCST90043640_buildGRCh37.tsv.gz, PGC3 vcf.tsv.gz, the meta_egfr
# file, MetaXcan-v0.8.1.tar.gz, gtex_v8_mashr_snp_covariance.txt.gz

# the two mashr model databases come out of the bundle
cd /path/to/mashr_eqtl.tar/dir
tar -xf mashr_eqtl.tar -C /path/to/ext eqtl/mashr/mashr_Whole_Blood.db eqtl/mashr/mashr_Nerve_Tibial.db
mv /path/to/ext/eqtl/mashr/*.db /path/to/ext/ && rm -rf /path/to/ext/eqtl
```

> **Windows/Git-Bash note.** `tar -xf E:/somewhere/mashr_eqtl.tar` fails with
> `Cannot connect to E: resolve failed` — GNU tar reads `host:path` as a remote spec. `cd`
> into the directory and use the bare filename, as above.

---

## 1. Reproduce the run

```bash
git clone https://github.com/wu-yijing/eqtl-source-discordance.git
cd eqtl-source-discordance

export EXT_DIR=/path/to/ext
export UPSTREAM_OUT=/path/to/_upstream_run
export METAXCAN_SW=/path/to/MetaXcan-0.8.1/software      # must contain SPrediXcan.py
export PYTHON=/path/to/python3.12

# one band per invocation; run all three
for band in A B C; do
  EQ_TAG=$band bash code/run_upstream.sh | tee "upstream_${band}.log"
done
```

Expected, in order:

1. `== 0. Preflight ==` → `ok 15  mismatched 0  incomplete 0  missing 0 (of 15)`, then
   `[ ok ] toolchain present (MetaXcan 0.8.1 + numpy 1.x)`.
2. `== 1 ==` → `finngen_R13_DM_*.gz -> 37192 rows` for each of DR / DN / DPN.
3. `== 2 ==` → `wrote 11382 genes / 27,985 rows` for `cov_Whole_Blood.txt.gz`.
4. `== 3 ==` → six `official_{Nerve_Tibial,Whole_Blood}_{DR,DN,DPN}.csv`.
5. `== 4 ==` → `eQTLGen_Whole_Blood.db (4,866,048 B)` and the printed SHA-256 `413c4fff…`.
6. `== 5 ==` → `band A: 94 genes …`, `band B: 8 genes …`, `band C: 1 genes …`.
7. `== 7 ==` → three `official_eq_<band>_*.csv` per invocation.
8. `== 8 ==` → `identical 30 | differing 0 | missing 0` on the **last** invocation, then
   `RESULT: upstream chain completed.`

If step 8 reports `missing`, that is the normal state on the first two invocations — it has
not produced the other bands yet. Only the third run's step 8 is the complete verdict.

---

## 2. Re-check this evidence without re-running the chain

**2a. The ledger, from the run directory** (~1–2 min; it decompresses `cov_A/B/C`, ~2 GB):

```bash
python ledger/check_middleware.py --tsv /tmp/ledger.tsv
diff /tmp/ledger.tsv ledger/middleware_ledger.tsv && echo "ledger reproduces"
```

The script carries `UPSTREAM_RUN_DIR` (default `E:/workbuddy/_upstream_20261004/run`); set
it if your run directory is elsewhere.

**2b. The archive's own gate, over your run directory** (seconds):

```bash
python code/upstream/verify_middleware.py --run-dir /path/to/your/run
```

**2c. The input pass** (~3.5 min; it decompresses every `.gz` to prove the streams end):

```bash
python scripts/verify_external_inputs.py --dir /path/to/ext --strict
diff <(...) inputs/verify_external_inputs.log    # paths and timings will differ; the counts must not
```

**2d. The toolchain claims:**

```bash
sha256sum /path/to/MetaXcan-v0.8.1.tar.gz     # must equal the row in toolchain/metaxcan.txt
sha256sum $METAXCAN_SW/SPrediXcan.py          # ditto
```

**2e. This directory's own integrity:**

```bash
sha256sum -c MANIFEST.sha256
```

---

## 3. Things that will bite

| Symptom | Cause |
|---|---|
| `bad: MetaXcan 0.8.1 needs numpy 1.x` | Wrong interpreter. `env/environment.yml` (Python 3.13 / numpy 2) cannot run this chain. |
| `[FAIL] …_aligned.tsv` or a covariance mismatch | Check `--order`: the GTEx arm needs `--order bim`, the eQTLGen arm `--order model`. The chain passes the right one per step; a hand-rolled invocation easily does not. Every wrong combination yields the *same gene set and the same values*, so a value-level check passes while the hash does not. |
| `SPrediXcan` writes nothing but exits 0 | It refuses to overwrite an existing `--output_file`. `run_upstream.sh` removes the target first; a manual invocation must too. |
| A `.txt.gz` row "differs" | `.txt.gz` rows are hashed on **decompressed content** by design — a gzip stream embeds its wall-clock time. Compare content, not file bytes. |
| Tar extraction fails on a Windows path | See the Git-Bash note in §0. |

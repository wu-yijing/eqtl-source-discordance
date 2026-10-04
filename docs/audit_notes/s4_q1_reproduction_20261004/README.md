# Q1 — does SI Table S4's control set, and the table's content, reproduce?

Date: 2026-10-04
Answer: **yes — 30 of 30 controls, and the re-emitted table is byte-identical to the file this
repository ships.** The R run below is a first-party re-run of
`../s4_specification_sweep_20261004/scripts/emit_S4_table.R`; its output is committed here so the
claim does not rest on that directory's provenance alone.

---

## The question, split from Q2

SI Table S4 raises two independent questions and they have different answers:

| | question | answer |
|---|---|---|
| **Q1** | does the **control set**, and the table's **content**, reproduce? | **yes — 30/30**, this note |
| **Q2** | does the submitted **pairing** (the `subclass` column) reproduce? | the column is a sort signature, not a matching output — the step is recovered and the rule verifies 30/30 as *a sort*, in [`../s4_pairing_provenance_20261004/`](../s4_pairing_provenance_20261004/README.md) |

They are not in tension: a real matching selected the controls (Q1 ✓), and something then numbered
them by `PullDown_Unused` descending (Q2). The two arms are the files this repository ships:

- **A** `data/superseded/mahalanobis_matched_pairs.csv` — the submitted file, md5 `e047ec426303a98bc939c270ecd5e44f`
- **B** `data/derived/mahalanobis_matched_pairs.csv` — the re-emitted file, md5 `38e49d56b3a919e7ec563b7ae22b068e`

## 1. Environment gate

The run is under the stack `env/renv.lock` pins, and the gate is checked before the run rather than
assumed:

```
$ PRELIB=<pinned-lib> Rscript --vanilla ../s4_specification_sweep_20261004/scripts/verify_pinned_env.R
R        : R version 4.5.2 (2025-10-31 ucrt)
MatchIt  : 4.5.5    (renv.lock pins 4.5.5  ) ==  <pinned-lib>/MatchIt
cobalt   : 4.5.2    (renv.lock pins 4.5.2  ) ==  <pinned-lib>/cobalt
optmatch : 0.10.6   (renv.lock pins 0.10.6 ) ==  <pinned-lib>/optmatch
PINNED STACK OK
```

The gate prints the **resolved directory** as well as the version, which is what caught the
`00LOCK-MatchIt` fallback in the earlier pass. Building the library from source is
`../s4_specification_sweep_20261004/RUNBOOK.md` §1.

## 2. The run

```bash
PRELIB=<pinned-lib> Rscript --vanilla \
  docs/audit_notes/s4_specification_sweep_20261004/scripts/emit_S4_table.R . <out-dir>
```

`logs/emit_S4_table_Q1.log`, verbatim:

```
MatchIt : 4.5.5 from <pinned-lib>/MatchIt
R       : R version 4.5.2 (2025-10-31 ucrt)

imputation reproduces the disclosed counts: 3 / 17 / 11
candidates 30 | pool (44 Non-Candidate) 44
matched pairs: 30 / 30 candidates

candidate SET vs submitted : TRUE
control   SET vs submitted : 30 / 30
  submitted control not selected :

-- Table S26 under the re-emitted pairing --
source     endpoint          candidate    matched-control  Fisher P
GTEx       BH q<0.05          2/84         1/60            1.000
GTEx       nominal p<0.05     8/84         7/60            0.784
eQTLGen    BH q<0.05          5/81         0/57            0.077
eQTLGen    nominal p<0.05     8/81         4/57            0.761
```

Every assertion the script carries is a `stopifnot`, not a print: the group-median imputation
counts (**3 / 17 / 11**, as Methods 1.9 discloses), the 30-row `match.matrix`, and the candidate
order being `PullDown_Unused` non-increasing. `EXIT=0`.

## 3. Verification, independent of the run

`scripts/verify_q1.py` consumes the run's output directory and re-derives Q1's claim from hashes and
cells — it does not re-run R, and it does not read the prose above:

```
A (submitted)      md5 e047ec426303a98bc939c270ecd5e44f  30 candidates / 30 controls
B (re-emitted)     md5 38e49d56b3a919e7ec563b7ae22b068e  30 candidates / 30 controls
this run           md5 38e49d56b3a919e7ec563b7ae22b068e
archive (shipped)  md5 38e49d56b3a919e7ec563b7ae22b068e

  [ok] hashes_match_B
  [ok] control_set_30_of_30
  [ok] difference_is_the_pairing_only

control set overlap  : 30 / 30
differing lines vs A : 28 / 61
pairing vs A         : 2 / 30  (Q2's question, not Q1's)

Q1 REPRODUCED
```

```bash
python docs/audit_notes/s4_q1_reproduction_20261004/scripts/verify_q1.py <out-dir> .
# exit 0; writes results/q1_verification.json
```

**Three independent facts**, and the third is what makes them worth stating separately:

1. **Hash identity.** The re-run's table, this repository's archive copy
   (`../s4_specification_sweep_20261004/results/mahalanobis_matched_pairs.csv`) and the shipped
   `data/derived/mahalanobis_matched_pairs.csv` are all md5 `38e49d56…` — byte-identical, confirmed
   with `cmp` as well as by hash.
2. **The control set is A's.** 30 of 30, and the script's own `submitted control not selected` line
   is empty — no submitted control is missing and none is substituted.
3. **The difference from A is the pairing and nothing else.** Exactly **28 of 61 lines** differ, and
   the candidate block is byte-identical. The residual pairing agreement with A is **2 of 30** —
   low, and expected: A's pairing is the rank-zip of Q2, B's is the nearest-neighbour output. Q1 is
   a claim about the *set*; the *pairing* is Q2's.

## 4. Before / after

| metric | A (submitted) | B (re-emitted) | this Q1 run | verdict |
|---|---|---|---|---|
| md5 | `e047ec42…` | `38e49d56…` | **`38e49d56…`** | = B |
| candidate set | 30 | 30 | 30 | identical |
| **control set** | 30 | 30 | 30 | **30/30 identical** |
| candidate block bytes | — | — | — | byte-identical to A |
| line difference vs A | — | 28 / 61 | 28 / 61 | matches the sweep |
| column layout | 8 cols | 8 cols | 8 cols | identical |
| Table S26 contrasts | — | 4 / 4 | **4 / 4** | unaffected |

## 5. What this closes, and the one residual

**Closed:** the control set and the table content reproduce from a clone under the pinned stack,
and the reproduction is byte-identical to what ships. The materials needed are all in this
repository (`data/derived/covariate_matrix.csv`, `data/superseded/mahalanobis_matched_pairs.csv`,
the two scripts) plus a self-built pinned R library (RUNBOOK §1).

**Residual, and it is the same one `emit_S4_table.R` states at the point of use:** the 30/30
depends on the **candidate processing order**, which is inherited from the submitted table's own
listing rather than derived — the cis-eQTL SNP counts tie, and the tie-break is not recoverable
from the shipped matrix. Every other order tested reaches 27–29 of 30 and 30 random permutations
never reach 30 (see `../s4_specification_sweep_20261004/`). So: **the control set reproduces, but
the order its reproduction depends on is inherited.** That is recorded in `ARCHIVE_MAP.md` §5
GAP-11 as well.

**Why this matters for the paper:** none of the reported numbers move. The re-emitted table selects
the same 30 controls, so Table S26's four contrasts are identical under either pairing — which is
re-confirmed here on the last four lines of the run log.

## Files

| file | what it is |
|---|---|
| `scripts/verify_q1.py` | independent verifier; consumes the run's output dir, exits non-zero on any failed check |
| `logs/emit_S4_table_Q1.log` | the run's stdout, verbatim |
| `results/mahalanobis_matched_pairs_Q1.csv` | the run's table; md5 `38e49d56b3a919e7ec563b7ae22b068e` |
| `results/S4_pairs_1to1_Q1.csv` | the run's 1:1 pairing list (30 rows) |
| `results/q1_verification.json` | the verifier's machine-readable output |
| `MANIFEST.sha256` | hashes of the above, as committed |

**Line endings.** The run's files were written CRLF by R on Windows; `.gitattributes` declares
`eol=lf`, so the committed blobs are LF-normalised — the same handling `docs/predecessors/README.md`
records for the six migrated predecessor files. Content is unaltered; the table's md5 above is
independent of the terminator because it is stated for the LF form that ships.

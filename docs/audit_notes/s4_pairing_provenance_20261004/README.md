# SI Table S4's `subclass` column — where the pairing came from

Date: 2026-10-04
Status: **the rule is recovered and verified 30/30; the one-off command is not, and is not needed to re-derive the column.**

`../s4_reported_run_20261004/` closed *which* matched set the manuscript reports, and
`../s4_specification_sweep_20261004/` closed the *control set*, leaving one sentence open:

> **Still open, and now precisely scoped:** what ran to produce A's `subclass` column. A real
> matching selected those 30 controls; something then sorted both arms by `PullDown_Unused`
> descending and numbered the result 1..30. Nothing on disk records that step, and the login dir
> is gone.

This note closes that sentence. The step is on disk, in two places, and the rule is executable.

---

## The answer in one line

`subclass` in `data/superseded/mahalanobis_matched_pairs.csv` (the submitted file, "A") is **the
1..30 rank of two lists each sorted by `PullDown_Unused` descending, zipped positionally** — one
list the 30 candidates, the other the 30 controls. It is a **sort signature, not a matching**;
and it was committed in the predecessor repository as **commit `1389407`**, whose diff to its
parent *is* the step.

## 1. The step, recovered from git history

The predecessors are real git repositories. In
`wu-yijing/TWAS-eQTL-source-confounding` (local mirror: `_mirror_twas-eqtl-source-discordance.git`,
refs `main 162e113` + tags `v1.0.0`, `v1.1.0`, `v2.0.0`, `v3.0.0`, `pre-chart-removal-20260923`):

```
$ git log --all --oneline -- data/processed/mahalanobis_matched_pairs.csv
1389407  Fix mahalanobis_matched_pairs.csv: use 44 high-confidence non-candidate pool
         (exclude 10 low-confidence); fix SMD calculation in 04_generate_all_figures.py …
         wu-yijing <…>   Tue Jun 30 16:04:39 2026 +0800
fdcb54c  Initial commit: analysis scripts and processed data for TWAS eQTL source …
```

| revision | md5 of `data/processed/mahalanobis_matched_pairs.csv` | what it is |
|---|---|---|
| `1389407` | **`e047ec426303a98bc939c270ecd5e44f`** | **byte-identical to A** (`data/superseded/…`) |
| `1389407^` (= `fdcb54c`) | `2766cd19c699d6310227e684ec8efa0a` | the genuine MatchIt output, **no `GC_pct` column** |

A is `e047ec42…` under **every** ref, so the file was written once and never revised afterwards.
The full diff is reproducible from the mirror:

```bash
git diff 1389407^ 1389407 -- data/processed/mahalanobis_matched_pairs.csv
```

`git diff --name-only` for that commit lists exactly two files, so the CSV hunk below is the whole
of the step:

```
-"Gene","Group","log10_Length","Length_bp","n_eQTL_SNPs","subclass","treated"
-"CKAP4","30_HOTAIR_Candidate",4.31357196843982,20585,2,"1",1
-"RP11-134O21.1","Background",4.31388830211387,20600,2,"1",0      <- real nearest neighbour
+"Gene","Group","log10_Length","Length_bp","n_eQTL_SNPs","GC_pct","subclass","treated"
+CKAP4,30_HOTAIR_Candidate,4.31355087133351,20585.0,1.5,47.8,1,1
+MYH9,NonCandidate,4.82439921664226,66742.0,2,40.5,1,0            <- rank-zip partner
```

Two changes, both explained: a `GC_pct` column is added, and `subclass` stops being a pairing ID
and becomes a rank.

### The corroborating banner

`analyses/logs/04_mahalanobis_matching_log.txt` in the same repository carries a `SUPERSEDED`
banner naming the operation:

> `对照池 = 全基因组背景基因；本日志记载的是当时的探索性结果。`
> `现稿（submitted manuscript）采用的是 harmonized 重分析：MatchIt 4.5.5，对照池 = 44 个高置信非候选基因`

which is `1389407`'s own subject line — *"use 44 high-confidence non-candidate pool (exclude 10
low-confidence)"* — stated in the log that sits beside the file.

## 2. The rule, executable and verified

`scripts/reconstruct_pairing.py` reads A and its covariates and asserts the rule:

```
candidate arm PullDown_Unused: [14.64, 11.37, 9.7, 6.5, 6.18, 4.99, …, 1.52, 0.0 ×15]
  non-increasing : True
control   arm PullDown_Unused: [14.19, 9.82, 7.84, 6.04, 5.17, 4.77, …, 2.01, 2.0 ×7]
  non-increasing : True

rank-zip rule re-derives the submitted pairing : 30 / 30
recovered TableS4 pairing == A subclass pairing  : 30 / 30

control SET, A vs the re-emitted (derived) table : 30 / 30
  (a real matching chose the controls -- the SET reproduces;
   only the PAIRING is the sort signature)
```

```bash
python docs/audit_notes/s4_pairing_provenance_20261004/scripts/reconstruct_pairing.py .
```

Both arms are individually non-increasing, which a matching output has no reason to be; and the
same 30 controls are selected by a real matching, which is why `../s4_specification_sweep_20261004/`
reproduces the **set** 30/30 while agreeing on the **pairing** in only 2–3 of 30. The set is a
measurement; the pairing is a sort.

## 3. The step's own downstream output, recovered

The rank-zip was consumed by the Table S5 emitter — present in all three repositories as
`scripts/python/07_generate_supplementary_tables.py`, whose Table S5 block is
`pair_groups[p['subclass']]` → `Pair_%02d`. That block is a **transformer, not a generator**: fed
the genuine source (`sha256 954c639c…`) it emits the genuine pairing
(`Pair_01 CKAP4↔RP11-134O21.1`); fed A it emits `Pair_01 CKAP4↔MYH9`.

A rendered instance survives in a deleted working directory (`…/submission_iScience_v2/tables/`,
recovered from the local recycle bin), and is copied here as
`results/recovered_TableS4_iScience_v2.csv`:

```
Pair_ID, Candidate_Gene, …, Control_Gene, …
Pair_01, CKAP4, …, MYH9,  NonCandidate, …
Pair_10, RNH1,  …, ANXA5, NonCandidate, …
Pair_11, RPL8,  …, NCL,   NonCandidate, …
```

**30 of 30 rows match A's `subclass` pairing** — the same file the script above checks against.
Its sibling `TableS5.csv` in that directory is the cross-population replication table and is
unrelated.

## 4. What this changes, and what it does not

| | before this note | after |
|---|---|---|
| the **rule** behind `subclass` | stated as a hypothesis in `../s4_specification_sweep_20261004/` | executable, asserted, 30/30 |
| the **step** that applied it | *"Nothing on disk records that step"* | commit `1389407`, diff retrievable from the mirror |
| the **producer script** (`07_…py`) | noted as a transformer | shipped here read-only as `scripts/07_generate_supplementary_tables_as_shipped.py` |
| the step's **downstream output** | not located | `results/recovered_TableS4_iScience_v2.csv`, 30/30 |
| the **one-off emitter** the author ran | recorded as lost | **still lost** — see below |

**Still not recovered, and stated plainly:** the one-off script the author ran to *write* the
rank-zip CSV before committing it. It is in no repository, not in the recycle bin, and not in any
dated working directory. Neither `03_enrichment_analysis.py` nor `07_generate_supplementary_tables.py`
writes that file; both only read it, which is consistent with an out-of-band emit followed by a
direct commit of the data file. **This does not leave the column unreproducible** — the rule is
fully determined and verifies 30/30 from A's own covariates — but it does mean the reconstruction
is a reconstruction of the *rule*, not a replay of the original *command*, and this note does not
claim otherwise.

## 5. Why the distinction matters for the paper

The submitted Table S4 pairs a candidate with a control that is that candidate's nearest
neighbour in **3 of 30** cases, because the pairing was never the matching's output. Every number
the manuscript reports from this table is a function of the **set** of 30 controls, not of which
candidate each is paired with — `../s4_specification_sweep_20261004/` re-runs Table S26 to show it
reproduces **4 of 4** contrasts identically under either pairing. The re-emitted
`data/derived/mahalanobis_matched_pairs.csv` therefore carries the same 30 controls with an honest
nearest-neighbour pairing, and **no reported number changes**. This note adds the provenance of the
column that was replaced, so the substitution is documented rather than unexplained.

## Files

| file | what it is |
|---|---|
| `scripts/reconstruct_pairing.py` | the rule, executable; asserts both arms and the 30/30 agreements |
| `scripts/07_generate_supplementary_tables_as_shipped.py` | the transformer that consumed the column, as shipped (read-only evidence) |
| `results/recovered_TableS4_iScience_v2.csv` | the rank-zip's rendered output, recovered from the recycle bin; matches A's pairing 30/30 |
| `results/recovered_TableS4_legend.txt` | its caption, as shipped |
| `MANIFEST.sha256` | hashes of the above, as committed |

**On the recovered copies' hashes.** The recovered files were written CRLF on the machine of
origin; `.gitattributes` here declares `eol=lf`, so the committed blobs are LF-normalised — exactly
as `docs/predecessors/README.md` records for the six migrated predecessor files. Both hashes are
given so the normalisation is checkable rather than assumed; the CRLF hash is reproduced by
re-expanding the committed file's `\n` to `\r\n`, and for the CSV it returns the md5 of the
recycle-bin original, which is how the copy is known to be lossless:

| file | md5 as recovered (CRLF) | md5 as committed (LF) |
|---|---|---|
| `results/recovered_TableS4_iScience_v2.csv` | `347159eb96c7a2677b15428cf001c7ac` | `f8ac74e75bf1f40716091a2e841622cf` |
| `results/recovered_TableS4_legend.txt` | `19a79ea3fd109b85128eb95370bae3a2` | `e51546af81e409090eafa50c385e0b2b` |
| `scripts/07_generate_supplementary_tables_as_shipped.py` | `4e66e785b41b8efa98eb3101509bdfb3` | `a0a23f10d862a7cd6ac34061d1e91d8a` |

Only line terminators differ; no content was altered.

## How to re-check

```bash
# the rule
python docs/audit_notes/s4_pairing_provenance_20261004/scripts/reconstruct_pairing.py .

# the step, from the predecessor mirror
cd _mirror_twas-eqtl-source-discordance.git
git log --all --oneline -- data/processed/mahalanobis_matched_pairs.csv     # 1389407, fdcb54c
git show 1389407:data/processed/mahalanobis_matched_pairs.csv  | md5sum     # e047ec42…  = A
git show 1389407^:data/processed/mahalanobis_matched_pairs.csv | md5sum     # 2766cd19…
git diff 1389407^ 1389407 -- data/processed/mahalanobis_matched_pairs.csv

# the transformer's Table S5 block
grep -n "pair_groups\[p\['subclass'\]\]" \
  docs/audit_notes/s4_pairing_provenance_20261004/scripts/07_generate_supplementary_tables_as_shipped.py
```

# SI Table S4 — the specification sweep, and where the divergence actually is: 2026-10-04

## The result

The previous pass (`../s4_matchit_version_test_20261004/`) removed the MatchIt
version from the list of explanations: 4.5.5 and 4.7.2 return the same answer. It
left two things unmeasured, and both are measured here.

**1. The archived control SET is reproduced exactly.** The documented specification
— nearest-neighbour matching on the Mahalanobis distance, 1:1, without replacement,
pool = the 44 `Non-Candidate` genes, group-median imputation, `m.order = "data"` —
run under the pinned MatchIt 4.5.5 with the candidates processed **in the order the
submitted table lists them**, selects **30 of the 30 archived controls**. Not 29.
Any other candidate order tested reaches 27–29; 30 random permutations reach at most
29 and hit 30 zero times. The submitted listing is `PullDown_Unused` non-increasing,
which is asserted in the emitting script, but it is *not* what
`order(pd, decreasing = TRUE)` returns from the covariate matrix — the cis-eQTL SNP
counts tie and the tie-break is not recoverable from the matrix alone. So the
processing order that reproduces the archive is the submitted table's own, and the
emitting script reads it from the submitted file rather than reconstructing it.

**2. What does not reproduce is the *pairing*, and it is now identified.** The
archived `subclass` column is the rank order of two lists each sorted by
`PullDown_Unused` descending: sorting both arms that way and zipping them reproduces
the archived pairing **30 of 30** — while the archived control is the candidate's
*nearest neighbour* in only 3 of 30 pairs (median rank 14 of 44, the previous pass's
diagnostic). Both statements are true at once, and together they say what happened:
the control set came from a real matching; the pairing in the file is a sort
signature laid over it.

| | MatchIt 4.5.5 (pinned) | MatchIt 4.7.2 (ambient) |
|---|---|---|
| Control SET, documented spec, submitted candidate order | **30 / 30** | **30 / 30** |
| Pairing, same run | 2 / 30 | 2 / 30 |
| Control SET, best over the sweep | 29 / 30 | 29 / 30 |
| Pairing, best over the sweep | 5 / 30 | 5 / 30 |
| Specifications fitted (usable) | 882 (714) | 882 (840) |
| `match.matrix` pairings identical between the versions | **yes, 30/30** | |

`full` matching is not swept: it is not a 1:1 design, `match.matrix` carries one
column per control, and reading column 1 would silently truncate it to a 1:1 subset
that is not what the method returns. The sweep covers `nearest` × {`m.order`:
default, `largest`, `closest`, `data`, `random`, `farthest`} × 3 distances × 7
covariate subsets × 3 row orders × 2 pools, plus `optimal`.

## A trap worth recording: `subclass` is not a pairing

`match.matrix` is identical between the two MatchIt versions — 30/30 rows, including
which control each candidate was given instead. `subclass` is not: MatchIt numbers it
in the order matches are formed, and that numbering differs between the versions on
these very inputs.

| candidate 1..10 (submitted order) | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| `subclass` under 4.5.5 | 1 | **12** | **23** | **25** | **26** | **27** | **28** | **29** | **30** | 2 |
| `subclass` under 4.7.2 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |

Aligning two runs on `subclass` therefore reports 1/30 agreement where the pairings
are in fact identical — a manufactured version difference. Every script here reads
the pairing from `match.matrix`; `scripts/compare_pairings.R` exists to make the trap
reproducible, and its log prints both the pairing and the two `subclass` vectors.

## Downstream: Table S26 is unaffected

Table S26 is a function of this pairing, so it was recomputed twice — once from the
submitted pairing, once from the re-emitted one — from the three inputs its
`ARCHIVE_MAP.md` row names. Both reproduce all four published contrasts exactly,
Fisher p-values included.

| weight source | endpoint | candidate | matched control | Fisher P | published |
|---|---|---|---|---|---|
| GTEx v8 multi-tissue ACAT-O | BH q < 0.05 | 2/84 | 1/60 | 1.000 | 2/84, 1/60, 1.00 |
| GTEx v8 multi-tissue ACAT-O | nominal p < 0.05 | 8/84 | 7/60 | 0.784 | 8/84, 7/60, 0.78 |
| eQTLGen whole blood | BH q < 0.05 | 5/81 | 0/57 | 0.077 | 5/81, 0/57, 0.077 |
| eQTLGen whole blood | nominal p < 0.05 | 8/81 | 4/57 | 0.761 | 8/81, 4/57, 0.76 |

`contrasts reproduced exactly: 4 / 4`, for both pairings — because the two pairings
select the *same 30 controls*, so every denominator (84 / 60 / 81 / 57) and every
contingency is identical by construction. **No reported number changes.**

This also settles the reasoning `ARCHIVE_MAP.md` used to move S26 to the red mark:
the matched-control denominators *are* derivable from the shipped inputs — 60 is the
number of (archived control × {DR, DN, DPN}) cells carrying a GTEx endpoint, 57 the
same for eQTLGen, 84 and 81 the candidate-arm equivalents. What was missing was a
script, not the construction. `scripts/s26_recompute.py` is that script, and it is
written from the archive rather than transcribed from the manuscript's values:
scipy is not required, and the imputation and endpoint rules are re-derived from the
documented specification.

## The re-emitted table

`scripts/emit_S4_table.R` produces the table the Methods describe, under the pinned
environment. It ships as **`data/derived/mahalanobis_matched_pairs.csv`**, and it
differs from `data/superseded/mahalanobis_matched_pairs.csv` in exactly one thing:

| | submitted file | re-emitted file |
|---|---|---|
| candidate block (30 rows) | — | **byte-identical** |
| control genes | the same 30 | the same 30, reordered into pair order |
| covariate values | — | unchanged (same 30 rows, permuted) |
| `subclass` | rank order | pair index (1..30) |
| lines differing | — | **28 of 60**, all in the control block |

`data/derived/mahalanobis_matched_pairs.csv`, md5 `38e49d56b3a919e7ec563b7ae22b068e`,
sha256 `b8758687e5822292…`, 3,623 B, LF, unquoted — formatted to match the submitted
file so that a diff isolates the pairing.

**Supporting Information `_rev8`** was rebuilt from `_rev7` by rewriting the 30
control rows of Table S4 (cell text only; every cell in that table holds one
paragraph with one run):

| | SI `_rev7` | SI `_rev8` |
|---|---|---|
| md5 / bytes | `d4ad6e348d577f55706a5d65af7ed37b` / 1,464,167 | `08ca0b851bccad27161599db805c2222` / 1,464,180 |
| pages / lines / words (WPS render) | 48 / 8,955 / 18,527 | **48 / 8,955 / 18,527** |
| pages whose text layer differs | — | **16 and 17** — where Table S4 sits |
| `w:tblPrEx` / `w:tblCellMar` / `w:tblBorders` / `w:insideH` | 2,160 / 2,220 / 2,222 / 8,722 | **unchanged** |
| package parts | 19 | **19**, all non-`document.xml` parts byte-identical |

The `_rev7` md5 agrees with the value `docs/audit_notes/INDEX.md` records for it,
which is how the base revision was confirmed rather than assumed. The `.docx` itself
is **not** distributed here — this repository's standing rule — so the build is
shipped as a script and the result as a hash and a page count.

## What this changes, and what it does not

- **Adds** one file to `data/derived/` and this directory.
- **Changes** no reported number: S26 reproduces 4/4 under either pairing, the
  candidate block and every covariate are untouched, and the main-text statement
  about Table S26 is qualitative.
- **Corrects** two entries in `metadata/ARCHIVE_MAP.md`: S4 leaves the red mark (the
  control set *is* reproduced; the pairing is now re-emitted rather than explained
  away), and S26 leaves it too, with the denominator argument it rested on withdrawn.
- **Does not** distribute either document, and does not touch `code/run_all.sh`.

## Files

```
scripts/verify_pinned_env.R       prove which MatchIt is loaded, and from where
scripts/emit_S4_table.R           re-emit Table S4; writes data/derived/…
scripts/diagnose_S4_order.R       is the control SET reproducible, and does the
                                  candidate order carry it?
scripts/sweep_specifications.R    the 882-specification sweep, pairing from match.matrix
scripts/compare_pairings.R        the subclass-vs-match.matrix trap, reproducible
scripts/s26_recompute.py          Table S26 from the archive (independent Fisher)
results/mahalanobis_matched_pairs.csv        the re-emitted table (= data/derived/…)
results/S4_pairs_1to1.csv                     pair index -> candidate -> control
results/pairing_matchit{455,472}.csv          match.matrix dumps, one per version
results/s4_sweep_matchit{455,472}.csv         every swept specification
results/s26_recompute.txt                     S26 under both pairings
logs/                                         full console transcripts of the above
```

Machine-local library paths are elided in `logs/` as `<isolated-library>` and
`<user-library>`. The version each arm loaded, and *which* package it resolved, are left
exactly as printed — that is the point of printing them, and it is what caught the
silent fallback in the earlier pass. Nothing else in a transcript is edited.

## Reproducing

```bash
R=/d/R/R-4.5.2/bin/Rscript.exe
PRELIB=<isolated library holding MatchIt 4.5.5 / cobalt 4.5.2 / optmatch 0.10.6>

$R --vanilla scripts/verify_pinned_env.R                      # must print PINNED STACK OK
$R --vanilla scripts/emit_S4_table.R . results                # 30/30 control set, 2/30 pairing
$R --vanilla scripts/diagnose_S4_order.R .                    # 30/30 on the submitted order only
$R --vanilla scripts/sweep_specifications.R . results/sweep.csv
python scripts/s26_recompute.py .                             # contrasts reproduced 4/4
```

`env/` carries the build recipe, including the one patch the pinned stack needs:
`optmatch 0.10.6` cannot compile against R ≥ 4.5 unpatched (see
[`../../env/README.md`](../../env/README.md) §"optmatch and R ≥ 4.5").

## Boundary

1. **What is settled.** The version does not enter this computation; the archived
   control set is reproduced exactly by the documented specification over the
   submitted candidate order; S26 reproduces exactly from the shipped inputs; the
   re-emitted Table S4 is the output of the shipped script on the shipped inputs.
2. **What is not.** How the submitted `subclass` column came to be sorted by
   `PullDown_Unused` is not recorded anywhere in this archive, and the rank-zip is a
   reconstruction that fits all 30 pairs rather than a recovered line of code. The
   submitted *candidate order* is likewise inherited, not derived: the emitting
   script reads it from the submitted table and says so.
3. **A third matched set — resolved 2026-10-04.** `Table_S2_Matched_Controls.csv`
   (2026-06-25) differs from the archived one on six controls, and a 2026-06-29
   genome-scale set shares none. Which one the manuscript reports is now settled by the
   manuscript's own numbers rather than by attribution: see
   [`../s4_reported_run_20261004/`](../s4_reported_run_20261004/README.md). The re-emitted
   table's claim is unchanged — it is what the documented specification produces.
4. **One honest residual.** The 30/30 control-set result depends on the submitted
   candidate order, and the tie-break inside `PullDown_Unused` is not recoverable
   from the shipped matrix. The file names what it reads and asserts the ordering is
   non-increasing; it does not claim the order is derivable.

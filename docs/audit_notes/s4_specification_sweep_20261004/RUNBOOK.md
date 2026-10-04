# RUNBOOK — SI Table S4: re-running the specification sweep and re-emitting the table

Everything below runs from the repository root. `$PRELIB` is a library holding the
pinned stack; building it is §1. Nothing here needs the network except the two
source tarballs in §1.

## 1. The pinned stack

`env/renv.lock` pins R 4.5.2, MatchIt 4.5.5, cobalt 4.5.2, optmatch 0.10.6. The
MatchIt version matters to this record — the question it answers is what the pinned
version does — so the stack is built from source rather than borrowed from whatever
happens to be installed.

```bash
R=/d/R/R-4.5.2/bin/Rscript.exe
RTOOLS=/d/R/rtools45
export PATH="$RTOOLS/usr/bin:$RTOOLS/x86_64-w64-mingw32.static.posix/bin:$PATH"
export RTOOLS45_HOME="D:/R/rtools45"

MIRROR=https://cloud.r-project.org/src/contrib/Archive
mkdir -p /tmp/s4dl && cd /tmp/s4dl
curl -LO $MIRROR/MatchIt/MatchIt_4.5.5.tar.gz
curl -LO $MIRROR/cobalt/cobalt_4.5.2.tar.gz
curl -LO $MIRROR/optmatch/optmatch_0.10.6.tar.gz

PRELIB=/e/workbuddy/_s4_pinned/rlib455        # adapt to taste
mkdir -p "$PRELIB"
"${R%Rscript.exe}" CMD INSTALL --library="$PRELIB" --no-multiarch MatchIt_4.5.5.tar.gz
"${R%Rscript.exe}" CMD INSTALL --library="$PRELIB" --no-multiarch cobalt_4.5.2.tar.gz

# optmatch 0.10.6 does NOT compile against R >= 4.5 as published: R 4.5 removed the
# un-prefixed Calloc/Free macros. The patch is imported from this repository.
tar -xzf optmatch_0.10.6.tar.gz
patch -p1 < <repo>/env/patches/optmatch-0.10.6-R4.5-calloc.patch
"${R%Rscript.exe}" CMD INSTALL --library="$PRELIB" --no-multiarch optmatch
```

Then, and this is not optional:

```bash
PRELIB="$PRELIB" $R --vanilla docs/audit_notes/s4_specification_sweep_20261004/scripts/verify_pinned_env.R
# must print:  PINNED STACK OK
```

The previous pass was nearly defeated by a leftover `00LOCK-MatchIt` in an isolated
library: R fell back to the user library although the run had been asked for 4.5.5,
and only printing the *resolved directory* caught it. `verify_pinned_env.R` prints
the version, the resolved directory and the pin for each package, and exits non-zero
on a mismatch.

## 2. The four measurements

```bash
D=docs/audit_notes/s4_specification_sweep_20261004

# is the control SET reproducible, and does the candidate order carry it?
PRELIB="$PRELIB" $R --vanilla $D/scripts/diagnose_S4_order.R .
#   expect: archived 30/30 | every other order 27-29 | 30 random orders max 29

# the wide sweep, pairing read from match.matrix
PRELIB="$PRELIB" $R --vanilla $D/scripts/sweep_specifications.R . $D/results/s4_sweep_matchit455.csv
#   expect: 882 fitted (714 usable), max control SET 29/30, max pairing 5/30
PRELIB=""          $R --vanilla $D/scripts/sweep_specifications.R . $D/results/s4_sweep_matchit472.csv
#   expect: identical maxima; the A/B is the same script with one variable changed

# re-emit the table
PRELIB="$PRELIB" $R --vanilla $D/scripts/emit_S4_table.R . $D/results
cp $D/results/mahalanobis_matched_pairs.csv data/derived/mahalanobis_matched_pairs.csv
#   expect: candidate SET true | control SET 30/30 | pairing 2/30

# S26 under both pairings
python $D/scripts/s26_recompute.py .
#   expect: contrasts reproduced exactly: 4 / 4   (twice)
```

To check the two versions directly, rather than through the sweep's maxima:

```bash
PRELIB="$PRELIB" $R --vanilla $D/scripts/compare_pairings.R . /tmp/p455.csv
PRELIB=""          $R --vanilla $D/scripts/compare_pairings.R . /tmp/p472.csv
diff <(grep -E '^ ?[0-9]+ ' /tmp/p455.csv) <(grep -E '^ ?[0-9]+ ' /tmp/p472.csv)   # empty
```

Do **not** align the two runs on `subclass`. Under 4.5.5 it runs `1, 12, 23, 25, …`
over the submitted candidate order; under 4.7.2 it runs `1, 2, 3, 4, …`. The pairing
is in `match.matrix`.

## 3. Rebuilding the Supporting Information revision

The `.docx` is not distributed here. `_rev8` was produced from `_rev7` by rewriting
the 30 control rows of Table S4 — cell text only, no row or cell moved, no other
table or paragraph touched — and verified by reading the result back:

```bash
python build_SI_rev8_S4.py       # writes _rev8 beside _rev7 and self-verifies
python render_and_check_SI.py    # WPS COM: export both to PDF and compare
```

Acceptance, all measured on this machine:

| check | expected |
|---|---|
| base revision | `_rev7` md5 `d4ad6e348d577f55706a5d65af7ed37b` — the value `INDEX.md` records for it |
| candidate block | byte-identical to `_rev7` |
| control block | the submitted 30 controls, reordered into pair order; `subclass` 1..30 |
| pairing read back off the column | equals `results/S4_pairs_1to1.csv` |
| pages / lines / words | 48 / 8,955 / 18,527 — identical to `_rev7` |
| pages whose text layer differs | 16 and 17 only |
| `w:tblPrEx`, `w:tblCellMar`, `w:tblBorders`, `w:insideH` | unchanged (2,160 / 2,220 / 2,222 / 8,722) |
| package parts | 19; every non-`document.xml` part byte-identical |

The four `w:tbl*` counts are the guard against the editor channel that cost this
project 2,160 `<w:tblPrEx>` in `SI _rev5`. A direct `document.xml` edit that only
sets run text cannot move them, and the check proves it rather than asserting it.

## 4. Checksums

```bash
cd docs/audit_notes/s4_specification_sweep_20261004 && sha256sum -c MANIFEST.sha256
cd ../../..  && python scripts/verify_provenance.py
bash scripts/verify_from_clone.sh          # the repository's own acceptance gate
```

`MANIFEST.sha256` here is generated from the **index** (the bytes a fresh clone
receives), not from the working tree, and LF-terminated text is hashed as LF — the
same rule `scripts/collect_provenance.py` uses and for the same reason.

## 5. Two disclosures about these transcripts

1. **Library paths are elided.** `logs/` prints `<isolated-library>` and `<user-library>`
   where the run printed a machine-local path. The version numbers and the resolved
   package are untouched, because those are the evidence: the earlier pass's silent
   fallback to 4.7.2 was visible *only* in the printed directory. Nothing else in a
   transcript has been edited.
2. **The 4.5.5 arm is not the arm that first ran.** The first attempt at this A/B was
   defeated by a leftover `00LOCK-MatchIt` and produced a 4.7.2 result for a run that had
   asked for 4.5.5. The lock was removed and the arm re-run; what is shipped is the
   re-run, and `verify_pinned_env.R` is the check that would have caught it if it
   recurred.

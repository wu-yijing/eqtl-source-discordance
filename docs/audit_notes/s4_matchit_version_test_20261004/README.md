# SI Table S4 — the MatchIt-version test, and its result: 2026-10-04

## The question, and the answer

The 2026-10-04 open-items pass ran six conventions against the archived Table S4 and matched
**2 of 30** control assignments. Every measured defect pointed away from the inputs and at the
algorithm, and the one explanation it could not rule out was the version:

> `MatchIt` **4.7.2** was installed; `env/renv.lock` pins **4.5.5**. `distance = "mahalanobis"`
> handling changed in the 4.6 line. Installing 4.5.5 from the CRAN archive requires compiling
> against Rtools — **a source install was started here and did not complete** — so the version
> effect is *narrowed, not yet measured*.

**It is now measured, and it is nil.**

| | MatchIt 4.5.5 | MatchIt 4.7.2 |
|---|---|---|
| Best agreement with the archived 30 pairs | **2 / 30** | **2 / 30** |
| Conventions giving an identical result | **18 / 18** | |
| Conventions giving an identical *per-pair mismatch string* | **18 / 18** | |

Not "similar" — **byte-identical**. All eighteen conventions, and the full text of which control
each candidate was assigned instead, agree between the two versions. The version does not enter
this computation.

**The surviving explanation is falsified. SI Table S4 was left ❌ NOT REPRODUCED, and the mark now
rests on a measured base rather than on a narrowed suspicion.**

> ***(2026-10-07 — the ❌ did not stand, and this note is what made that testable.)***
> `../s4_pairing_provenance_20261004/` then recovered the step that wrote the pairing
> (commit `1389407`), `../s4_specification_sweep_20261004/` re-emitted the table from
> the documented specification, and `../s4_q1_reproduction_20261004/` re-ran it
> first-party: the control set reproduces **30/30** and the table is byte-identical
> (`38e49d56…`). What this note establishes is untouched, and it is the load-bearing
> part — **the `MatchIt` version is falsified**, 18/18 conventions identical down to the
> per-pair mismatch strings, and the archived control is the candidate's nearest
> neighbour in only 3 of 30 pairs. Current status: `metadata/ARCHIVE_MAP.md`.

## 1. How the test was built

```
scripts/install_matchit455.R      compile MatchIt 4.5.5 from the CRAN archive into an
                                  isolated library
scripts/reproduce_S4_matchit455.R ONE script, run twice: lib = isolated (4.5.5) and
                                  lib = "" (the user library, 4.7.2)
scripts/diagnose_S4_distance.R    where the divergence actually is
```

The A/B design is the point: **the same script, the same inputs, the same 18 conventions**, with
only the library path changed. Each arm prints the version it loaded *and the directory it loaded
it from*, so a wrong-library run is visible rather than silent.

Compilation succeeded first time under Rtools 45 / GCC 14.3.0 (`logs/install_matchit455.log`);
the log's own tail is the proof of which build was used:

```
* installing *source* package 'MatchIt' ... this is package 'MatchIt' version '4.5.5'
g++ -std=gnu++17 ... -I"D:/R/rtools45/..." -c nn_matchC.cpp -o nn_matchC.o
* DONE (MatchIt)
```

Two things had to be got right, and both are recorded because both went wrong first:

1. **`Rscript -e '…'` segfaulted** (exit 139) with a multi-line `-e` argument under Git Bash. The
   scripts are therefore **files**, run with `Rscript --vanilla <file>`; nothing here depends on
   shell quoting.
2. **A leftover `00LOCK-MatchIt` in the isolated library made R silently fall back to 4.7.2** while
   the script had been *asked* for 4.5.5. The run printed `MatchIt 4.7.2 (loaded from
   …/win-library)` — which is exactly why the script prints the resolved directory and not just
   the version. The lock was removed and the arm re-run.

## 2. The 18 conventions

3 pools × 2 imputation rules × 3 `m.order` settings.

| | Pools | Imputation | `m.order` |
|---|---|---|---|
| shipped matrix | `44 Non-Candidate`; `Non-Candidate + T2DM Control` (= 74, what the shipped `.R` builds) | group-median impute; `na.omit` | `data`, `random` (seed 20260915), `closest` |
| producer matrix (`Table_S1_Covariate_Matrix_FINAL_v2.csv`, 54 non-candidates) | `39_NonCandidate_HOTAIR` | same | same |

`logs/ab_matchit455.log` and `logs/ab_matchit472.log` are the two full console transcripts;
`results/m455_conventions.csv` and `results/m472_conventions.csv` are the same content as data;
`results/version_comparison.txt` is the side-by-side.

**One correction to the earlier pass.** `m.order` accepts `"data"`, `"random"` and `"closest"` —
nothing else. MatchIt 4.5.5 says so explicitly ("The argument to `m.order` should be one of
"data", "random", or "closest"."), and 4.7.2 is the same. The earlier pass also *attempted*
`"largest"` and `"smallest"`; those calls raised errors and contributed nothing. The convention
count in that pass was therefore smaller than it looked, not larger — and note that `"random"` is
RNG-dependent, so it is a seed-sensitive convention rather than a version-sensitive one.

## 3. Where the divergence actually is

Version excluded, the next question is which *layer* differs. `diagnose_S4_distance.R` answers it
without invoking MatchIt at all: it computes the Mahalanobis distance from each candidate to every
control in the 44-gene pool and asks **where the archived control ranks**.

| Covariates | Covariance convention | Archived control is the nearest neighbour | Median rank (of 44) | Worst |
|---|---|---|---|---|
| all three | pool / candidates / pooled-centred | **3 / 30** | 14–15.5 | 39 |
| `length + eQTL SNPs` | all three | **3 / 30** | 12.5 | 40 |
| `eQTL SNPs only` | all three | **11 / 30** | 11 | 41 |
| `length + GC`, `GC + eQTL SNPs`, `length only`, `GC only` | all three | **3 / 30** | 14 | 39 |

Full table: `results/distance_diagnostic.csv` (`n = 30` in every row, i.e. all 30 archived
candidates and all 30 archived controls are present in the shipped matrix — the pairing exists in
principle; it just is not what this metric selects).

**The archived controls are not near neighbours of their candidates.** A median rank of 14 out of 44
means that for a typical pair, thirteen other controls sit closer to the candidate than the one the
archive recorded. That is decisive against "the algorithm is right and only the assignment order
differs": no greedy ordering, no tie-breaking rule and no `m.order` setting turns a rank-14 partner
into the selected one when a closer control is available and unused.

So the divergence is at the **distance specification** layer, and it is not resolved by any of the
21 combinations above (7 covariate subsets × 3 covariance conventions), nor by the 18 A/B
conventions. Consistent with `metadata/ARCHIVE_MAP.md` §3's row S4 and the third matched set the
2026-10-04 pass found on disk (`Table_S2_Matched_Controls.csv`, six controls different), the
simplest reading is that **the archived pairing was not produced by Mahalanobis nearest-neighbour
matching on these covariates** — but that is a reading, not a measurement, and it is not written
down as one.

## 4. What this does and does not change

- **Does**: removes the last surviving explanation from the record and replaces it with a
  measurement. `metadata/ARCHIVE_MAP.md` row S4 and GAP-11 are updated accordingly.
- **Does not**: change any reported number, any file in `data/`, or either submitted document.
  Nothing about the paper's conclusions turns on these 30 control assignments — the row was already
  ❌ at this point. *(2026-10-07: it no longer is; see the note at the head of this file.)*
- **Still owed**: the manuscript-side question is now sharper and simpler — *which* matched set does
  the paper report, and what produced it? `Table_S2_Matched_Controls.csv` and the archived file
  disagree on six controls, and neither is reproduced by any tested specification. That needs the
  original analysis log, not a search, and it cannot be settled from this repository.
  *(2026-10-07: both halves were settled without it — which set the paper reports by
  `../s4_reported_run_20261004/`, and what produced its pairing by
  `../s4_pairing_provenance_20261004/`. The measurement above stands.)*

## 5. Reproducing this

```bash
R=/d/R/R-4.5.2/bin/Rscript.exe

# 1. build MatchIt 4.5.5 into an isolated library
$R --vanilla scripts/install_matchit455.R

# 2. the A/B — same script, two libraries
$R --vanilla scripts/reproduce_S4_matchit455.R "E:/workbuddy/_s4_repro/rlib452" m455 <repo> out
$R --vanilla scripts/reproduce_S4_matchit455.R ""                            m472 <repo> out

# 3. where the divergence is
$R --vanilla scripts/diagnose_S4_distance.R <repo>
```

Requirements: R 4.5.2 (`D:\R\R-4.5.2`), Rtools (present; `pkgbuild::has_build_tools()` is TRUE),
and the CRAN archive reachable for the source tarball
(`cran.r-project.org/src/contrib/Archive/MatchIt/MatchIt_4.5.5.tar.gz`, 1,822,657 B).

**Dependency note.** MatchIt 4.5.5 needs `backports`, `chk`, `rlang`, `Rcpp`, and `RcppProgress` to
build. The versions on this machine are newer than `env/renv.lock` pins for `Rcpp` (1.1.1 vs
1.0.12); `Rcpp` is a *compile-time* dependency here and the distance arithmetic is double-precision
R, so it cannot move the result — and the A/B shows the result does not move.

`results/` and `logs/` carry `MANIFEST.sha256`. Nothing in this directory is a `.docx`.

## Note on the elision in ``logs/ab_matchit472.log` and `logs/install_matchit455.log`` (2026-10-04)

Some paths in the two A/B transcripts were replaced by placeholders: `<user-library>` for an R user library
on the author's machine, `<temp-workdir>` for a scratch directory used to hold a clone
during an audit, and `<user-home>` for the compiler's 8.3 short form of the same account
name. The names of the account and the machine are not evidence for anything these files
are cited to show — the versions and the resolved components are, and those are untouched.
Nothing else in the files was edited. The substitution is scripted and counted in the
2026-10-04 CHANGELOG entry, so it is reproducible rather than a hand edit.

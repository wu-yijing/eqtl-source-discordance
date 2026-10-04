# Changelog

All notable changes to this archive are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/) adapted to research artefacts (see `docs/RELEASE_PROCESS.md` §2).

**Every entry must state explicitly whether any reported number changed.** That sentence is the first thing a reviewer will look for.

---

## Version lineage — read this before comparing version numbers

This project has been re-archived three times. Version numbers **do not restart** with each repository; they continue across the lineage so that no two releases of this study ever share a number. Releases below this repository's first entry belong to predecessor repositories, which are archived and read-only.

| Version | Repository | Zenodo record | Note |
|---|---|---|---|
| v1.0.0 – v3.0.0 | `wu-yijing/twas-eqtl-source-discordance` (formerly `TWAS-eQTL-source-confounding`) | concept `10.5281/zenodo.21238202` | Full pre-2026-09-24 development history. **GitHub tags and Zenodo version labels for this period are not identical — see "Open item" below.** |
| v1.0.0 – v1.0.1 | `wu-yijing/eqtl-source-discordance-audit` | concept `10.5281/zenodo.22910500` | Release-only snapshot; **its v1.0.0 tag sits two commits behind that repository's final state** |
| **v4.0.1** → | **this repository** | concept DOI `10.5281/zenodo.23129112` | Canonical from here on. **v4.0.0 was declared in earlier drafts but never tagged, so v4.0.1 (2026-10-04) is the first released version of this repository.** |

> **Open item — do not close this by assumption.** The predecessor README declares Zenodo version **v2.7.0** as current, while its GitHub tags stop at **v3.0.0**. GitHub tags and Zenodo version labels for the predecessor repository are therefore out of step. Record the true mapping here once verified, because a reader comparing the two will otherwise conclude that a release is missing.

---

## [Unreleased]

### 2026-10-04 (twenty-sixth pass) — SI Table S4 is re-emitted; the control set reproduces and the pairing is a sort signature

Numbers: **no reported number changed.** One file was added to `data/derived/`; no reported value,
no denominator and no Fisher p-value moved, and the main-text sentence about Table S26 is
unchanged. Neither submitted document is distributed here.

The twenty-fifth pass removed the MatchIt version from the list of explanations for SI Table S4
and left the residue as "what produced the pairing is still unrecorded" — a reading, explicitly
not written down as a measurement. This pass measures it, and the answer is narrower and more
useful than either of the two earlier positions.

- **The submitted control SET is reproduced exactly — 30 of 30.** Nearest-neighbour matching on the
  Mahalanobis distance, 1:1, without replacement, pool = the 44 `Non-Candidate` genes, group-median
  imputation, `m.order = "data"`, under the pinned MatchIt 4.5.5, with the candidates processed **in
  the order the submitted table lists them**. Every other order tested reaches 27–29 of 30 and 30
  random permutations never reach 30. So the earlier ❌ was right that the shipped `.R` does not
  return the submitted file, and wrong to treat the input or the algorithm as the defect: the
  *selection* was never the problem.
- **What does not reproduce is the PAIRING, and it is identified.** The submitted `subclass` column
  is the rank order of two lists each sorted by `PullDown_Unused` descending — sorting both arms that
  way and zipping reproduces the submitted pairing **30 of 30** — which is exactly consistent with
  the previous pass's finding that the submitted control is the candidate's nearest neighbour in
  only **3 of 30** pairs (median rank 14 of 44). A real matching chose the controls; a sort
  signature wrote the pairs.
- **`data/derived/mahalanobis_matched_pairs.csv` is added**: Table S4 re-emitted from the documented
  specification under the pinned environment. It differs from the superseded file in exactly one
  respect — the candidate block is **byte-identical**, the same 30 controls appear reordered into
  pair order, and 28 of 60 lines differ. Supporting Information `_rev8` (not distributed here)
  carries it: pages 48 → 48, lines 8,955 → 8,955, only pages 16–17 of the text layer change, and the
  four `<w:tbl*>` counts that the editor channel destroyed in `_rev5` are unchanged.
- **Table S26 is unchanged, and the reason it was red does not hold.** S26 reproduces **4 of 4**
  contrasts from the three inputs its row names — denominators 84 / 60 / 81 / 57 included — and it
  reproduces identically under the re-emitted pairing, because both pairings select the same 30
  controls. The claim that the denominators "cannot be derived from the 30 archived pairs" was a
  join that had not been written down, not a construction that was never captured.
  `scripts/s26_recompute.py` now ships.
- **A trap is recorded for anyone who repeats this A/B:** `subclass` is numbered in the order
  matches are formed and is *not* the candidate order — non-monotone under 4.5.5
  (`1, 12, 23, 25, …`), monotone under 4.7.2 — so aligning two runs on `subclass` reports 1/30
  agreement where `match.matrix` shows the pairings are identical. Every script here reads the
  pairing from `match.matrix`.
- **`env/` now carries the one patch the pinned stack needs.** `optmatch 0.10.6` — the version
  `renv.lock` pins — does not compile against R ≥ 4.5 as published, because R 4.5 removed the
  un-prefixed `Calloc` / `Free` macros. `env/patches/optmatch-0.10.6-R4.5-calloc.patch` renames 63
  call sites across four files and changes nothing else; `env/README.md` documents it and its scope
  (`optimal` / `full` only — the reported matching is `nearest` and does not reach `optmatch`).
- **`metadata/ARCHIVE_MAP.md`:** S4 and S26 both leave the red mark and the ❌, both on measurement.
  S4's residual is stated rather than closed: the 30/30 depends on the *submitted candidate order*,
  which is inherited from the submitted file rather than derived, and which of the (at least two)
  matched sets on disk the manuscript reports is still unrecorded. §5 GAP-11 is closed with that
  attribution left open on purpose.

Evidence, scripts, both A/B arms and a `MANIFEST.sha256`:
[`docs/audit_notes/s4_specification_sweep_20261004/`](docs/audit_notes/s4_specification_sweep_20261004/README.md);
runbook: [`docs/audit_notes/s4_specification_sweep_20261004/RUNBOOK.md`](docs/audit_notes/s4_specification_sweep_20261004/RUNBOOK.md).

### 2026-10-04 (twenty-fifth pass) — the MatchIt-version explanation for S4 is tested and falsified

Numbers: **no reported number changed.** No file in `data/` changed, no reproducing script was
edited, and neither submitted document was touched.

The twenty-first pass left SI Table S4 with one surviving explanation: `MatchIt` 4.7.2 was
installed, `env/renv.lock` pins 4.5.5, and `distance = "mahalanobis"` handling changed in the 4.6
line. The source install "did not complete inside this session's budget", so the version effect was
recorded as **narrowed, not measured**. It is now measured.

**It is nil. 18 of 18 conventions agree between the two versions — down to the per-pair mismatch
strings — and both best-match the archive at 2 of 30.**

| | MatchIt 4.5.5 | MatchIt 4.7.2 |
|---|---|---|
| Best agreement with the archived 30 pairs | 2 / 30 | 2 / 30 |
| Identical results out of 18 conventions | 18 / 18 | |
| Identical per-pair mismatch strings | 18 / 18 | |

The A/B is designed so the library is the only variable: **one script, run twice**, with
`lib = <isolated>` and `lib = ""`, each printing the version it loaded *and the directory it came
from*. That second half earned its keep immediately — a leftover `00LOCK-MatchIt` in the isolated
library made R silently fall back to 4.7.2 while the run had been *asked* for 4.5.5, and the printed
directory is what caught it. (`Rscript -e '…'` with a multi-line argument also segfaulted under Git
Bash, so everything is a file run with `--vanilla`.)

The divergence was then localised without invoking MatchIt at all. `diagnose_S4_distance.R` computes
the Mahalanobis distance from each candidate to every control in the 44-gene pool and asks where the
archived control ranks:

- **the archived control is the nearest neighbour in 3 of 30 pairs; median rank 14 out of 44, worst 39**
- across 7 covariate subsets × 3 covariance conventions, the best is 11/30 (the eQTL-SNP count alone)

So this is not an assignment-order problem. With 30 candidates drawn from 44 controls, no greedy
ordering or tie-breaking rule selects a rank-14 partner while a closer control is available and
unused. **The pairing the archive ships is not what this metric selects** under any of the 18 A/B
conventions or 21 distance specifications. What produced it is still unrecorded; that question now
needs the original analysis log, not a search.

Added

- **`docs/audit_notes/s4_matchit_version_test_20261004/`** — 13 files: the build recipe
  (`install_matchit455.R`), the A/B runner (`reproduce_S4_matchit455.R`), the distance diagnostic
  (`diagnose_S4_distance.R`), both convention CSVs, the distance table, the side-by-side summary,
  four run logs and a `MANIFEST.sha256`. A scoped `.gitignore` exception re-includes this
  directory's logs for the same reason the upstream-chain record has one: here the logs are the
  artefact.

Changed

- **`metadata/ARCHIVE_MAP.md`** — row S4 and GAP-11 no longer carry "narrowed, not measured"; they
  carry the measurement, the falsification, and the localisation. The status stays **❌ NOT
  REPRODUCED** and `clone ≠ result`.
- **`docs/audit_notes/open_items_closure_20261004/README.md`** §1.3 now marks its own surviving
  explanation as falsified rather than leaving the earlier text to be read as current.
- **One correction to the earlier pass's wording.** `m.order` accepts `"data"`, `"random"` and
  `"closest"` — nothing else, in either version. That pass also *attempted* `"largest"` and
  `"smallest"`; those calls raised errors and contributed nothing, so the tested space was smaller
  than the phrase "m.order variants" implied. The count now stated is the count that ran.

Not done

- **`MASS`-based `matchit(distance = …)` variants** remain untried. The distance diagnostic covers
  the covariate-subset and covariance-convention space instead, which is where the evidence points.
- **The manuscript-side question** is unchanged and now sharper: which matched set does the paper
  report, and what produced it? `Table_S2_Matched_Controls.csv` and the archived file disagree on
  six controls and neither is reproduced.

### 2026-10-04 (twenty-fourth pass) — the R2 residual is closed: the P1/P2 notes are in the paper

Numbers: **no reported number changed.** No file in `data/` changed, and no reproducing script was
edited. This pass applies the paste-ready text that `docs/audit_notes/R2残余差异消除方案_20261002.md`
wrote on 2026-10-02, whose own closing line was "*做完 P1+P2 后，R2 = 0*". **R2 = 0 now holds.**

The three R2 items were never wrong numbers. Each was a report that had not written down what a
reproducer needs — the estimator, the RNG, the permutation unit, the input precision. The archive
had already established all four by measurement and said so in an audit note; the paper had not.
That gap is what this closes.

Applied

| Document | In | Out | Bytes | MD5 |
|---|---|---|---|---|
| SI | `…_rev6.docx` | **`…_rev7.docx`** | 1,463,543 → **1,464,167** | `d4ad6e348d577f55706a5d65af7ed37b` |
| Manuscript | `…_rev7.docx` | **`…_rev8.docx`** | 31,190 → **31,223** | `7fed1b504c452e16333a59d1aef6510e` |

- **SI, after the Table S17 note: two new paragraphs.** (i) The *Resampling details* disclosure
  (`numpy.random.RandomState`, legacy MT19937; seeds 20260915 / 20260726 / 20260914; B = 10,000,
  5,000 for the paired Δρ bootstrap) together with the resampling unit — genes drawn from a
  **lexicographically sorted** vector — and the permutation unit — gene labels permuted as **whole
  genes**, one permutation applied to all three phenotypes at once. That one paragraph closes three
  items at once: the endpoint drift under row reordering (item 3), the primary arm's ρ interval
  `0.12–0.62` (the MT19937 convention), and the permutation null `−0.22 ~ +0.23` (which the previous
  wording, "permuted within each phenotype", reproduces as −0.199/+0.199 instead). (ii) The
  **sandwich and delete-one-gene jackknife estimator definitions** (item 2). The reported
  `SE = 0.125` is **not** changed: the triple (SE 0.125, one-sided 0.002, two-sided 0.004, df 31) is
  internally consistent for any SE in [0.12326, 0.12719], so the estimator was the missing item.
- **Manuscript, paragraph 37, one parenthetical** (item 1): "exceeds that by 6.1 points **(6.01
  points when evaluated at the unrounded ρ = 0.3896 and rate = 68.75%)**". Both numbers are
  unchanged; the parenthetical names where the 0.04 pp difference between the manuscript's 6.1 and
  the SI's 6.05 comes from.

Added

- **`docs/audit_notes/r2_notes_closure_20261004/`** — `apply_r2_notes.py`, `verify_r2_notes.py` and
  the record.
  - `apply_r2_notes.py` **hard-codes no prose**: it extracts the four text blocks from the R2 note
    on every run and fails if it cannot find them, so editing the note breaks the tool rather than
    letting it drift. It rewrites only `word/document.xml`, cloning the adjacent note paragraph's
    `<w:pPr>` so the new paragraphs inherit the existing style instead of inventing one.
  - `verify_r2_notes.py` checks seven things independently: identical part tables with only
    `word/document.xml` rewritten; **exactly one contiguous insertion** in `document.xml`
    (SI `[3635677, 3635677)`, 2,736 chars; manuscript `[29182, 29182)`, 75 chars); run-for-run
    equality with the note's text; SI paragraph count 115 → 117 with two new paragraphs following
    paragraph 81 and **all 115 originals unchanged**; SI paragraph count and the four table markers
    (`tblPrEx` / `tblCellMar` / `tblBorders` / `insideH`) invariant — i.e. the rev5 layout
    regression is **not** reintroduced; Times New Roman glyph coverage; and every pre-existing
    numeric token preserved.
- **Docs revision registry** extended: manuscript rev8 and SI rev6/rev7 are registered by MD5 and
  byte count, so all seven on-disk pairs now report `[ok]` with the revision named rather than
  `[UNRECOGNISED]`.

One glyph substitution, measured rather than assumed

The estimator text needs `∈` (U+2208). fontTools against `times.ttf`, `timesbd.ttf` and
`timesi.ttf` shows Times New Roman covers **14 of the 15** code points the inserted text uses and
lacks exactly that one, so `Σ_{i∈g}` is written `Σ_{i in g}`. The applier asserts the source form is
present and the target form absent, and the verifier prints the substitution. The other four new
characters (`̃ ̄ Σ φ ỹ`) are new *to the document* but covered by the font, so no font embedding is
needed.

Not done

- **The PDF.** Both documents changed, so the page count and the per-page character comparison need
  a re-render on a machine that permits Office automation; this one does not (item 5 of the
  open-items record).
- **§五's P3 table notes.** Two of the seven were fixed on 2026-10-04 (Table S21's `median minimum
  absolute Z`, Table S24's zero convention); five remain.
- **Nothing is distributed.** Neither document ships with this repository — the standing rule — so
  the record carries their MD5/SHA-256 and the two scripts that reproduce them from the prior
  revisions.

### 2026-10-04 (twenty-third pass) — the hard-coded Z pair in `recompute.py`, and what removing it exposed

Numbers: **no reported number changed.** No file in `data/` changed, and neither submitted document
was touched. `results/merged_pairs.csv` is **byte-identical** before and after. The two tracked
outputs that *do* change are `recompute_log.txt` and `recompute_results.json`, because the script
now prints more than it did — that is the point of the pass.

**The defect was not a wrong number. It was a comparison that printed like a pass.**

`scripts/recompute.py` §3.12 hard-coded the two cohort Z-scores as literals:

```python
z_fin, z_ukb = 2.31, 0.72            # eQTLGen 权重下 FinnGen R13 / UKB 的 Z（表注所载取值）
```

and then printed its result beside the report's:

```
Cochran Q = 1.2641,  I² = 20.9%    (报告 Q = 1.26, I² = 20.6%)
```

20.9 on the left, 20.6 on the right, laid out as a verification. A reader — or a future maintainer,
or a third party checking the archive — sees a matched line. It is not matched, and nothing in the
output says so. The same line also mislabelled the two τ denominators: `(Q−df)/Σw` was called
"DL 约定" (it is not DL) and `(Q−df)/df` was called "表中约定" (it is, in fact, DL here, since
C = Σw − Σw²/Σw = k − 1 = df). Both mislabels were retracted in
`repo_crosscheck/verify_crosscohort_exact.py` on 2026-10-03 and the script was never brought into
line with that retraction.

Fixed

- **The literals are gone.** The Z-scores are read from the shipped
  `data/derived/ukb_dr/RNH1_official_metaxcan_Z.csv` (+2.3091, +0.7225, +0.5451), which the
  `ukb_dr_dir` entry already registers as an input — the same file the archive's own
  `data/derived/ukb_dr/README.md` documents.
- **Two conventions, both computed and both printed.** This is the treatment
  `m6_ne_weighted_sensitivity.py` already gives the √N_e row, and it is now the treatment S5a gets:
  **A** = the quoted two-decimal Z-scores — which is what the **SI's own Table S5a note declares**
  ("recomputed from the quoted Z-scores") — and **B** = the archived full-precision official Z.
- **A per-quantity verdict instead of a juxtaposition.** Each of the eight printed quantities now
  carries `口径A / 口径B / 报告值 / 判定`, and the two failure modes are separated: a genuine
  disagreement, and a value sitting exactly on a rounding half-step (where the last digit is decided
  by the rounding rule and not by the data).
- **Both S5a rows, not just the first.** Row 3 was equally hard-coded in spirit and is now computed
  from the same shipped file.
- The τ labels now match `verify_crosscohort_exact.py`.

What the honest version shows

| Row 1 (primary) | A (quoted, as the SI note declares) | B (archived exact) | printed | verdict |
|---|---|---|---|---|
| pooled Z | 1.52 | 1.52 | 1.51 | fails both — **and is exactly on the 1.515 half-step** |
| SE | 0.80 | 0.79 | 0.79 | B only |
| P | 0.057 | 0.056 | 0.056 | B only |
| Cochran Q | 1.26 | 1.26 | 1.26 | both ✓ |
| **I² (%)** | **20.9** | **20.5** | **20.6** | **neither** |
| τ | 0.51 | 0.51 | 0.51 | both ✓ |
| 95 % PI | −0.34~3.37 | −0.33~3.36 | −0.33~3.36 | B only |

and **row 3 is reproduced only by B — while the SI note declares A.**

So the finding is sharper than "a rounding difference". Row 1's I² is 0.0502 pp from the archived
exact value and 0.2892 pp from the quoted one; the quantity moves ~0.15 pp per 0.001 of |Z|, so it is
an input-precision residual of the same class as row 3's documented 76.6 / 76.27 — but it is *not*
in the class of "consistent with the convention the note states". `metadata/ARCHIVE_MAP.md` row S5a
previously said of this row **"— all match SI row 1"**; that was an eyeball check and it was wrong.
It now says what was measured.

Not done

- **Which Z pair actually produced row 1 is still unrecorded.** A narrow diagonal band of
  (Z_FinnGen, Z_UKB) pairs does reproduce the whole printed row — e.g. (2.3064, 0.7197) — and the
  band's lower FinnGen edge is exactly the pre-alignment value **+2.3064** that
  `data/derived/ukb_dr/README.md` documents ("the pre-aligned input used for the arm-level recompute
  returns Z = +2.3064, 728/898"). That is suggestive and it is **not** established, so it is recorded
  as a hypothesis and not as the explanation. Closing it needs the original analysis log, not a
  search.
- The rectification itself: three manuscript-side edits would close the residue — the SI note should
  say which Z-scores row 1 used, or the I² should be printed to the precision the inputs support.
  This archive cannot edit the paper.

### 2026-10-04 (twenty-second pass) — the map is corrected: S4 goes ✅ → ❌, S26 goes 🟡 → 🔴

Numbers: **no reported number changed.** No file in `data/` changed, neither submitted document
was touched, and no reproducing script was edited. This pass edits **one status column, four
prose carriers and two gates**, and its whole subject is that the previous pass found something
and left the map still saying otherwise.

**`metadata/ARCHIVE_MAP.md` was over-claiming two rows.** The twenty-first pass measured that
SI Table S4 does not reproduce. It recorded that in `docs/audit_notes/` and left
`metadata/ARCHIVE_MAP.md` untouched, so the document a reviewer actually reads still carried
`✅` and "a fresh clone re-runs it end to end" for a row whose re-run returns a different table.
A finding that is not written where the claim lives is not a correction.

The status column, machine-counted before and after:

| | ✅ | 🟡 | 🔴 | ❌ | ➖ | total |
|---|---|---|---|---|---|---|
| before | 26 | 12 | 0 | — | 9 | 47 |
| after | **25** | **11** | **1** | **1** | 9 | 47 |

Changed

- **`metadata/ARCHIVE_MAP.md` §3, row S4: ✅ → ❌, locality `clone` → `clone ≠ result`.** The old
  cell reasoned that every input ships, which was true and beside the point — the *script* ships
  too, and running it returns a different matched set. The row now carries the six conventions
  tried, the best result (**2 of 30** control assignments), the three measured defects, the one
  measured agreement (covariates 0 discrepancies over 60 rows) and the surviving unmeasured
  explanation (`MatchIt` 4.7.2 installed vs 4.5.5 in `env/renv.lock`). It also records the
  **third matched set** on disk (`Table_S2_Matched_Controls.csv`, six controls different), so any
  closure has to say which run the manuscript reports.
- **`metadata/ARCHIVE_MAP.md` §3, row S26: 🟡 → 🔴.** Its 🟡 rested on inputs being present. They
  are — but the producing script was never shipped *and* the matched-control denominators (60 and
  57) cannot be derived from the 30 archived pairs, so this is a construction that was never
  captured rather than a join waiting to be written. It also inherits S4.
- **A `❌ NOT REPRODUCED` mark, added to the Status key and its obligation.** The vocabulary had
  no way to say "the script runs and disagrees" — which is exactly why S4 kept a ✅ it had not
  earned. 🔴 and ❌ are kept apart on purpose: *we lost the script* and *we have the script and it
  disagrees* have different remedies, and reporting the second as the first is a misdescription.
- **A `clone ≠ result` locality label**, defined in §"Two axes, not one". The old vocabulary could
  say "the chain does not run here" (`none`) but not "the chain runs and returns something else".
- **§5 GAP register: GAP-11 opens** for S4 + S26, and says plainly that it is the first entry on
  that register which is a *finding* rather than a bookkeeping item. The closing paragraph now
  states the DOI placeholder **is resolved** (v4.0.1 / v4.0.2 are minted) and replaces it with
  the actual residue and its closure path.
- **`README.md`** — the locality list is corrected (`clone (outcome)` was removed on 2026-10-03
  and the list still carried it) and a paragraph now presents the ❌ row *before* the rest, since
  a reader deciding what to trust should meet it early.
- **`code/README.md`** — `analyses/run_mahalanobis_matching.R` was listed as reproducing "Table S4
  — the 30-gene Mahalanobis matching". It does not. The cell now says so.

Changed — the gates, because the vocabulary is part of them

- **`scripts/check_archive_map.py`**: `STATUS_MARKS` and `LOCALITY` now carry the two additions,
  the summary-line regex expects the five counts, and `--counts` returns six fields
  (`total ✅ 🟡 🔴 ❌ ➖`). The gate was not asserting anything false — it simply could not express
  the state, and neither could the map it checks. A vocabulary gap in the checker is what let the
  vocabulary gap in the map survive.
- **`scripts/cut_release.sh`**: reads fields 4 and 5 and reports 🔴 and ❌ **separately**, since
  they oblige different things. It previously read field 4 alone.

Verified

- `scripts/check_archive_map.py` → `13 tables, 47 item rows, 5 locality labels`; summary counts,
  column declaration and vocabulary all agree.
- `scripts/verify_provenance.py`, `metadata/provenance.json` regenerated over the new tree.

Not done, and deliberately

- **The Supporting Information still carries whatever it carries about S4.** This archive cannot
  edit the paper. The map is now honest and the paper is the remaining carrier of the old claim;
  that is stated in §5 rather than left for a reader to discover.
- **The `MatchIt 4.5.5` measurement.** Still narrowed, not measured — a source install needs
  Rtools. Until it runs, ❌ stands.

### 2026-10-04 (twenty-first pass) — the open items, closed or answered; S4 does not reproduce

Numbers: **no reported number changed.** No file in `data/` changed, no gate was changed, and
neither submitted document was touched. This pass registers the document revisions that were
on disk but unrecognised, restores the SI revision's package structure, and adds an audit note
recording what was and was not closed. **One of its findings is a negative one about this
archive's own status column, and it is the headline:**

**SI Table S4 does not reproduce, and `metadata/ARCHIVE_MAP.md` says it does.** The earlier
audit recorded S4 as blocked because "R 4.5.2 + MatchIt" were unavailable. A full-disk search
found them: R 4.5.2 at `D:\R\R-4.5.2`, and `MatchIt` / `cobalt` / `optmatch` in the user
library — but at **4.7.2 / 5.0.0 / 0.10.8** where `env/renv.lock` pins **4.5.5 / 4.5.2 /
0.10.6**. Six conventions were run against `data/superseded/mahalanobis_matched_pairs.csv`
(pool 74 as the shipped script builds it, pool 44 as the archived table implies, the producer's
pool 54, both `na.omit` and group-median imputation, and `m.order` variants). The best result
is **2 of 30** control assignments matching. Three defects were measured, not suspected:

- `code/analyses/run_mahalanobis_matching.R` builds its pool as `covar$Group != "Candidate"`,
  which adds the 30 T2DM controls. The archived table uses **only** the `44 Non-Candidate`
  group — all 30 archived controls carry that label and none of the T2DM controls appears.
- `data/derived/covariate_matrix.csv` has **44** non-candidates; the producer's own
  `Table_S1_Covariate_Matrix_FINAL_v2.csv` has **54**. The 10 absent genes are named in the note.
- The covariates agree **exactly**: every archived `log10_Length`, `Length_bp` and `GC_pct`
  matches the shipped matrix, 0 discrepancies over 60 rows. So the input is right and the
  algorithm differs — the surviving explanation is the `MatchIt` version, which is narrowed
  here but **not yet measured** (a source install of 4.5.5 needs Rtools and did not finish).

The group-median imputation *is* confirmed: it reproduces this archive's own disclosed counts
(3 of 30 candidates at median 1.5, 17 of 44 pool genes, 11 of 30 T2DM controls at 1.0).

Added

- `docs/audit_notes/open_items_closure_20261004/` — the record: the five items, the six-convention
  test matrix, three reproduction scripts so the negative result is checkable rather than
  asserted, and the two figures behind the Fig. S1 finding.
- **Docs revision registry.** `paths_config.py` now registers manuscript rev5/rev6/rev7 and SI
  rev1_dates / rev1_dates_minimal / rev3 / rev4 / rev5, with the two that produced the archived
  `results/` still marked `outcome=True`. Verified: `[UNRECOGNISED]` → `[ok]`, revision named.
- **`tools/rebuild_SI_rev5_structure.py`** and the rebuilt
  `Supporting_Information_GenetEpidemiol_20260930_rev6.docx`: the SI revision's two content
  edits re-applied to the **previous** revision's package. The regression being repaired is
  measured — package parts 19 → 25, `word/document.xml` −593 KB, `w:tblPrEx` 2,160 → 0,
  `w:tblCellMar` 2,220 → 62, `w:tblBorders` 2,222 → 62, with `styles.xml` unchanged, i.e.
  cell-level property exceptions dropped rather than moved into styles. The rebuild restores
  19 parts and all three counts to the previous revision's values while keeping the text
  **identical to the later revision**; only `word/document.xml` is rewritten.

Answered, in the negative

- **SI Fig. S1.** Both surviving generators (the in-tree `rebuild_fig1_2_9.py` and the
  2026-08-31 `make_main_figures.py`) were run here under the pinned matplotlib 3.10.8 and both
  emit **3188 × 3076**; the published raster is **3189 × 3077**. A three-way visual comparison
  shows the **same flowchart, box for box** — the difference is one parameterised string in the
  `> 75 %` box plus ~9 % of pixels differing at **1–8 grey levels** spread across the whole
  canvas, which is the signature of a font-rasterisation build rather than of different
  geometry. A translational search (±3 px) does not improve it, and neither does a 1-px pad on
  any corner. So this is a **font-pinning problem, not a lost generator** — a stronger and more
  actionable statement than "a different raster family", and it does not disturb the
  artefact-level closure (`ge_si/published/` + `verify_published.py`, 0 px differ).

Not done

- **The SI PDF.** WPS Office is installed but COM automation is refused by this machine's
  security policy, and no LibreOffice / Word / pandoc exists. The render, and the page-count
  and per-page character comparison that would follow it, need an environment that permits
  Word or WPS automation.
- **S4's version effect.** Installing `MatchIt 4.5.5` from the CRAN archive needs Rtools; the
  build was started and did not complete within the session. Until it does, "S4 does not
  reproduce" stands and "the `MatchIt` version is why" is a narrowing, not a measurement.

Added after the first draft of this entry — the reproducible artefacts

`docs/audit_notes/open_items_closure_20261004/` now carries the machinery, not just the
findings, so none of it has to be recomputed:

- **`figs1/gen_figS1.py`** — the SI Fig. S1 generator, self-contained: the recovered
  `figure2()` verbatim, its three working-directory dependencies removed (an unused
  `prep_out.json` lookup, `pandas`/`scipy` imports needed only by sibling figures), and the
  two strings the audit found to vary promoted to `--green-text {published,legacy}`. Verified
  to emit 3188 × 3076 under **both** matplotlib 3.10.8 and 3.10.9, byte-identically.
- **`figs1/verify_figs1.py`** + `figs1_verification.json` — reproduces every number in the
  note's §2.3, including the ±3 px translation search and the difference-amplitude histogram.
- **`figs1/rerun_published_greentext.png`** and **`rerun_legacy_greentext.png`** — the two
  re-runs, so the size and family claims are checkable without running matplotlib.
- **`si_structure/rebuild_SI_rev5_structure.py`** + **`verify_SI_structure.py`** +
  `si_structure_verification.json` — the rebuild and a verifier that recomputes the part count,
  the four `word/document.xml` markers, `styles.xml`'s invariance, and text equality. The three
  checks are recorded as `True`. **The rebuilt `.docx` is deliberately not shipped**, per this
  repository's standing rule that no manuscript or supplementary file is distributed from it.
- **`registry/check_doc_revision.py`** + `registry_verification.txt` — a read-only wrapper that
  asks the reproduction package which revision a `.docx` is, plus the before/after transcript
  and a control pair. Writing it surfaced one more thing worth recording: `doc_status()` only
  hashes when given a **logical** name; handed a raw path it returns `unchecked` **without
  hashing**, which reads as "nothing recorded" rather than "not checked".
- `MANIFEST.sha256` over all 16 files.

The Fig. S1 residual was also probed further and **narrowed to a single surviving cause**: the
difference is invariant across matplotlib 3.10.8 vs 3.10.9 (byte-identical), Arial vs DejaVu
Sans (Arial is closer, 9.3792 % vs 11.2880 %), six resampling filters and 49 translations — so
it is a text-rasterisation build, not a geometry, version, font-family or scaling effect.

### 2026-10-04 (twentieth pass) — the upstream chain is executed by someone else, and the record ships with it

Numbers: **no reported number changed.** No file in `data/derived/` or `data/upstream/` changed,
no reproducing script was edited, no gate was changed and neither submitted document was touched.
This pass adds an audit-notes directory and one index row; it changes no artefact the archive
already shipped.

`code/run_upstream.sh` is the one part of this archive whose claim rested on code rather than on
an execution: the middleware is registered by hash, the build scripts were recovered on 2026-10-03,
and the whole chain was re-run that day — **by its author**. Nothing here let a reader check that
the raw inputs in fact produce the registered bytes.

They do, and this pass records the run that shows it. All fifteen external inputs were verified
present and hash-matching with the archive's own `verify_external_inputs.py --strict`, including
its gzip-completeness pass (`incomplete 0`) — the check that exists because
`gtex_v8_mashr_snp_covariance.txt.gz` had once been registered from a download that stopped after
6.8 % of its source file. The chain was then run three times, `EQ_TAG=A`, `B`, `C`, under the
**unmodified official MetaXcan v0.8.1** and Python 3.12.15 / numpy 1.26.4. All three invocations
exited 0; step 8 reported `identical 30 | differing 0 | missing 0`; an independently written
ledger — expected values transcribed from `data/external/README.md`, observed values hashed off
the run directory — reported `matched 30  mismatched 0  pending 0`. Both readings agree, which is
the point: the archive's own verifier shares the archive's expected-hash table, so agreement
between the two is what rules out a table that is wrong in the same direction as the check.

Added

- `docs/audit_notes/upstream_chain_closure_20261004/` — the record, organised so each doubt can be
  attacked on its own: `inputs/` (the 15 inputs' verified bytes), `toolchain/` (versions, and the
  MetaXcan source-archive and executed-entry-point hashes), `driver/` (the three-band driver),
  `ledger/` (the ledger, its generator, and the archive verifier's own output), `logs/` (unedited
  stdout of all three invocations, plus warning-stripped reading copies) and a
  `MANIFEST.sha256` covering the twenty files so the directory is checkable on arrival.
  `README.md` §3 gives the six-step decision procedure and the falsifier each step would have
  caught; `RUNBOOK.md` gives the replay and the re-check commands.

Stated, not glossed

- The record's §5 carries the boundary explicitly: **this closes the 104-gene-testbed arm only.**
  `run_upstream.sh` does not cover the GTEx v8 elastic-net arm that underwrites Table S16's
  `framework WB (EN_WB vs MASHR_WB)` and `tissue EN` rows, nor the production of the five
  genome-wide layers under `data/derived/genomewide/` — step 1 of this chain filters FinnGen to
  the models' SNPs (37,192 rows) and therefore cannot yield a genome-wide scan. Both remain
  script-less in this archive, and folding them into "the upstream chain is closed" would be wrong.
- Line endings in the new directory are LF, as `.gitattributes` requires, and `MANIFEST.sha256`
  was computed over those bytes so it verifies from a fresh clone. The logs were produced on
  Windows and carried CRLF before normalisation; no line was added, removed or edited.

### 2026-10-04 (nineteenth pass) — one verdict for a missing dependency: gate 7 stops crying wolf

Numbers: no reported number changed. No file in `data/derived/` changed, no middleware artefact
changed, no reproducing script was edited and neither submitted document was touched. This pass
edits two gate scripts only, so the archive is the same archive; what changes is how a gate
reports a check it could not run.

`scripts/verify_from_clone.sh` gate 7 exists because `code/run_all.sh` — the one command
`README.md` tells a reader to run — was once broken from a fresh clone while every other gate
stayed green (see the seventh pass). It ended that way with `bad`, which is right when
`run_all.sh` fails for an archive reason and wrong when it fails because the interpreter cannot
`import numpy` and the run never starts. The same missing dependency was a **skip** everywhere
else: gate 5 said so, gate 8 said so, and `scripts/cut_release.sh` said so in as many words —
"Only a missing numpy is a skip, because that is a property of the interpreter, not of the
archive." One condition, three verdicts, and on an interpreter without NumPy the odd one out was
the false alarm: the reader sees a red FAIL for something the archive did not do wrong.

- **`[skip]` is now a first-class verdict in both gate scripts.** It is the same word
  `code/run_all.sh` already prints. A skip is neither a pass nor a failure: it is counted
  separately from both, and the summary prints the count. A run that skipped anything now ends
  with "every check that could run passed; N could not run here. Not a full verification"
  instead of borrowing the language of a clean pass — so a green board can no longer quietly
  mean a partly-verified one.
- **Gate 7 no longer reports a pass it did not earn, nor a failure it did not find.** With no
  NumPy on PATH it skips the *execution*, as gates 5 and 8 do — but a gate that can only skip is
  a gate that cannot fail, which is the very failure mode this script was written to end. So it
  still does the two checks that need no interpreter: `bash -n` on the entry point, and a sweep
  that every `.py` the entry point names is present in the tree.
- **Gates 5 and 7 now prefer an interpreter that can actually run the code.** Each tries `$PY`,
  then any other interpreter on PATH, so a reader who has NumPy anywhere gets the real check
  rather than a skip. Where the substitute differs from `$PY`, the gate says which one it used.
- **`scripts/cut_release.sh` adopts the same `[skip]`.** Its missing-NumPy line and its
  git-absent placeholder sweep were reported as `[ ok ]` and `[warn]`; both are `[skip]` now,
  and its summary prints a `skipped:` count alongside failures and warnings.

No claim in this archive changed and no number moved. Verified both ways: with an interpreter
that has NumPy the clone verifies 0 failure(s) / 0 skipped (all ten gates run, gate 5 at 15
checks / 0 mismatches and 87/87 ACAT-O, gate 8 at zero differing pixels); with a bare
interpreter it reports 0 failure(s) / 3 skipped, and names them.

## [4.0.2] — 2026-10-04

### 2026-10-04 (eighteenth pass) — the archive states its own DOI, and the status prose catches up

Numbers: no reported number changed. No file in `data/derived/` changed, no middleware artefact
changed, no reproducing script was edited and neither submitted document was touched. This pass edits
release metadata, one container label and the release tooling.

The v4.0.1 deposit exposed a class of drift that the DOI backfill cannot close by itself.
`scripts/set_doi.py` substitutes DOI *tokens* and rewrites two regions whole — the README status
block and `CITATION.cff`'s version-identifier block — but it does not rewrite prose that states the
*status*. Three consequences were found by inspection of the tree after the backfill, and all are
fixed here:

- `DOI_PENDING.md` still read "this repository has no published DOI yet", `Status: pending` and
  `Zenodo record: _not yet created_` after the record existed and the DOI had been filled in.
- `CITATION.cff` kept the comment "While that registry reports status \"pending\", the values below
  are unregistered placeholders and must not be cited" sitting directly above two live, citable DOIs,
  because that comment lies outside the managed block.
- `env/Dockerfile` still carried `LABEL version="4.0.0"`. The project version had never been
  propagated into the image label, and `cut_release.sh` checks the base-image digest but not this
  label, so nothing in the gate set could catch the drift.

The tooling fault behind the first two is fixed at the source, so that it cannot recur:

- `CFF_BLOCK_PUBLISHED` now **retains** its `#DOI_VERSION_IDENTIFIER_BEGIN` / `_END` markers. The
  first backfill consumed them, after which the block no longer matched: a second release would have
  moved `README.md` forward and left `CITATION.cff` frozen on v4.0.1's version DOI. The markers are
  the contract that makes the backfill repeatable.
- The two comment lines that introduce `CITATION.cff`'s identifier list are now managed as well, so a
  "pending / must not be cited" note cannot outlive the deposit.

Documentation corrected or dated in the same pass:

- `README.md` continues to name `eqtl-source-discordance-audit` (`10.5281/zenodo.22910500`) as the
  object the manuscript's Data availability statement *used* to resolve to, rather than the object it
  resolves to now; the published statement cites this repository's DOI. The same correction is made
  in `docs/predecessors/README.md`, which also no longer calls the canonical repository "v4.0.0".
- `metadata/zenodo_release.json`'s header comment no longer opens with "Until the canonical
  repository is published to Zenodo…", and its `note_on_predecessor_doi` records the mismatch as
  closed rather than current.
- `DOI_PENDING.md` keeps its filename — five carriers link to it and it is still the place a reader
  looks for how the deposit was made — but its status header is closed and its body is retained
  verbatim as the dated record it is (see the note at the top of that file).

Why a new version rather than an in-place edit of the record: the Zenodo archive of v4.0.1 is the tag
`71b038dc`, and the README inside it says "No published DOI yet" — a reader who downloads the archive
is told the deposit does not exist. A DOI can only be minted once its tag has been published, so no
tag can ever contain its *own* version DOI; what a tag *can* contain is the permanent concept DOI. The
README status block now says exactly that, so publishing v4.0.2 makes the archived README
self-describing instead of self-contradicting.

Checks: `verify_from_clone.sh` — 10 gates, 0 failures. `cut_release.sh` — 0 failures.
`set_doi.py --check` — every carrier resolves to a real DOI, no placeholder tokens.

## [4.0.1] — 2026-10-04

### 2026-10-04 (seventeenth pass) — the pinned environment could not build the figures it claims to build

**Numbers: no reported number changes.** No file in `data/derived/` changed, no middleware artefact
changed, and neither submitted document was edited.

A reproducibility pass re-checked every shipped input, both submitted documents and all four main
figures against the hashes this archive records, and found them correct. What it could not do was
*rebuild* them from the environment this archive pins, because two dependencies were not in it.

Fixed
- **Two dependencies that 21 shipped scripts import were not pinned.** `PIL` (Pillow) and `docx`
  (python-docx) appear in every script under `code/figures/`, in
  `code/figures/ge_si/published/{patch_figS1,patch_figS3,verify_published}.py`, in
  `ge_main/figstyle_ge.py` and in `r3/m15/m15_pc.py`. Neither `env/requirements.txt` nor
  `env/environment.yml` named them, so both Quick-start paths — `conda env create -f
  env/environment.yml` and `docker build -f env/Dockerfile` — produced an environment in which
  `bash code/figures/ge_main/reproduce.sh` aborts in its preflight (`python module missing: PIL`)
  and every `.docx`-reading step fails at import. Both are now pinned (`pillow==12.3.0`,
  `python-docx==1.2.0`); both resolve to cp313 wheels, as `env/README.md` rule 1 requires.
  **Verified from that environment on 2026-10-04: all four main-figure PNGs rebuild
  byte-identically** (`eb77483e…`, `87ee0eaa…`, `152f45df…`, `f29f2f56…`).

Added
- `data/README.md`: the `external/` row now says *which* files are tracked — the three manifest
  files — instead of "No (git-ignored)", which was false for them and left a reader guessing whether
  `SOURCES.tsv` and `SHA256SUMS` are in the clone at all.
- `data/README.md`: the **Table S24 zero-value convention** is recorded beside the `scz_z_4arm.csv`
  row it governs. `multiZ` carries **77 exact zeros** among the 8,315 complete-case genes; the
  archived three-arm counts score a zero as **disagreement** (`numpy.sign`), and treating zeros as
  positive instead moves the dual arm from 5,506 to 5,544 (**+0.46 pp**). The convention belongs in
  the SI table note, which is a submission-document edit; paste-ready wording is in
  `docs/audit_notes/R2残余差异消除方案_20261002.md` §五 item 7.

Corrected
- `figures/README.md` no longer contradicts itself. Its "Figures whose producing script is not in
  `code/figures/`" section still ended with the pre-2026-10-03 sentence *"the manuscript's four main
  figures still cannot be assembled end-to-end from this archive — Fig. 2, 3 and 4 can, Fig. 1 only
  by hand"*, directly beneath a section saying all four regenerate byte-identically. The stale
  sentence is replaced by a statement of what the limitation actually covers.
- `figures/README.md`: **Fig. S2 is 🟡, not ✅.** The recovered `gen_figs4.py` reproduces the
  published universe (61 genes, 24/24/13) and the three medians, but it carries hard-coded 2026-09
  paths and is not invoked by `run_all.sh`; `metadata/ARCHIVE_MAP.md` records its input locality as
  `none`. Marking it ✅ claimed more than the archive delivers.

Verified
- `bash scripts/verify_from_clone.sh` — **0 failures**, all 10 gates, from a fresh clone.
- `bash code/figures/ge_main/reproduce.sh` — four PNGs byte-identical to the submitted figures.
- `python code/analyses/reproduction_min/reproduce_headline.py` — 15 checks, 0 mismatches.

### 2026-10-03 (sixteenth pass) — the truncated input is traced to its source, and the class of bug is closed

**Numbers: no reported number changes.** No file in `data/derived/` changed, no middleware artefact
changed, and neither submitted document was edited.

The fifteenth pass found that `gtex_v8_mashr_snp_covariance.txt.gz` — registered as a 2,362,720-byte
input whose hash matched — was a truncated gzip stream, and left it open because its source was not
known. It is now traced, and the class of defect has a guard.

Traced
- **A full-disk search, then byte-level identity.** The gzip header of the held file names its original
  member (`gtex_v8_expression_mashr_snp_covariance.txt`) and carries mtime `2019-10-03 13:34:35 UTC`,
  the PredictDB GTEx v8 MASHR build date. The decisive test was a ranged request: the first 2,362,720
  bytes of
  `https://zenodo.org/records/3518299/files/gtex_v8_expression_mashr_snp_smultixcan_covariance.txt.gz`
  are **byte-for-byte** the local file — MD5 `cc2a4c861095ea359da15cc31733702f` over both.
- **The complete file reproduces the publisher's checksum.** 34,851,462 B; MD5
  `dda0eedeb842cfc272e76ad432753d73`, equal to the checksum Zenodo's API publishes for it; SHA-256
  `68dccc21c4e0293c51395a9ef1d464797a0482ba51ab47b93f92c4d0b49c84bb`; decompresses to 214,012,383 B
  across 2,508,317 rows, header `GENE RSID1 RSID2 VALUE`. Record `10.5281/zenodo.3518299`, licence
  CC-BY-4.0. The copy that had been registered was **6.78 %** of it.
- **The download dated 2026-07-16 21:42 is an artefact of the file being moved, not downloaded.** Four
  identical truncated copies exist on the machine; Chrome's download record independently shows the
  same Zenodo record in use on 2026-06-25. The originals were left where they were.

Added
- `scripts/verify_external_inputs.py` gained a **gzip-completeness pass**: for a `.gz` input present on
  disk the stream must *end* — trailer, CRC32 and ISIZE — or the file is reported `incomplete` and the
  exit status is non-zero. Measured over the whole set (4.67 GB, 2 m 31 s) against the **old** manifest:
  `ok 15  mismatched 0  incomplete 1  missing 0` — this file, and nothing else. `--no-integrity` skips
  the pass. **A hash match is no longer accepted as proof of a whole file**, which is the real lesson:
  an interrupted download hashes exactly like the artefact it failed to become.

Fixed
- `SOURCES.tsv` carries the URL, the true byte count and the licence; `SHA256SUMS` carries the SHA-256
  of the complete file; `provenance.json` follows. Link coverage is now fourteen of fifteen — the one
  without a link, PGC3, has none for a licence reason rather than an unknown one.
- `verify_external_inputs.py` accepts `gtex_v8_expression_mashr_snp_smultixcan_covariance.txt.gz` as an
  alias, because the PredictDB release names this file after its consumer rather than its contents.

### 2026-10-03 (fifteenth pass) — every third-party input now has a link, and one of them is a truncated file

**Numbers: no reported number changes.** No file in `data/derived/` changed, no middleware artefact
changed, and neither submitted document was edited.

The previous pass shipped the middleware (`data/upstream/`, 31 MiB) so a reader could check the Z layer
without the third-party inputs. This pass answers the other half: where to *get* those inputs. They were
already not stored — `data/external/*` is git-ignored — but the archive named only five of the fifteen by
URL, and only inside prose, so "not redistributed" was easier to read than to act on.

Added
- `data/external/SOURCES.tsv`: one row per input — direct download URL, exact byte count, licence as
  published, redistribution decision, and a note. Thirteen of the fifteen rows carried a working direct
  link when this pass ran, each requested on 2026-10-03 and matched against the recorded size; the
  fourteenth was added by the next pass. Four are stronger than a
  size check: the GWAS Catalog's **own** `md5sum.txt` gives `a802753ce87d30de09e3bc2df15c9b8c` and
  `9ac919a05dbd8f3e2c405520b6aa870e`, the MD5s recorded here for the two `GCST90043640` files; the
  eQTLGen and CKDGen servers report exactly the recorded 322,775,879 and 178,400,853 bytes; and the
  three FinnGen endpoints plus their manifest match by size.
- `scripts/fetch_external_inputs.py`: downloads from those links and verifies each file against
  `SHA256SUMS`. Resume-capable; streams a member out of a `.tar` without unpacking it whole (the
  PredictDB models live inside `mashr_eqtl.tar`); reports a file with no link as `NO-URL` with the
  reason attached; and **refuses to run at all when the two manifests disagree about which files
  exist** — a file in one and not the other is exactly how an unhashed download slips through.
- `scripts/verify_from_clone.sh` gate 10: that disagreement, checked at release time. Gate count 9 → 10.
- `data/external/README.md` §"What is stored and what is linked": the rule, and the four categories it
  was applied to.

Fixed
- **A listed input is a truncated download.** `gtex_v8_mashr_snp_covariance.txt.gz` fails `gzip -t`
  ("unexpected end of file"): it decompresses to 14,624,957 B and stops mid-token, at
  `ENSG00000172613.7 chr11_67314013_T_C_b38 chr11_6731`, after 1,099 genes. `SHA256SUMS` records the
  hash of *that* file, so `verify_external_inputs.py` reports it `ok` — a recorded hash cannot tell
  "the right bytes" from "the right bytes so far". **No reported number is affected**: nothing in the
  archive reads the file. Recorded as an open item with the evidence, URL column set to `-`.
  **Traced to its source and closed in the sixteenth pass.**
- **`meta_egfr_dmstrat_stage1plus2.txt.gz` was mis-attributed.** It was labelled "Cross-population DN
  resource (GCST90018832 lineage)". It is not a GWAS Catalog deposit — the GCST90018832 directory
  serves no file by that name — it is the CKDGen diabetes-stratified eGFR meta-analysis, served from
  the University of Regensburg (Winkler et al., Commun Biol 5, 580 (2022)), whose server reports the
  recorded byte count exactly.
- **`g1000_eur.zip` was attributed to PredictDB.** The filename is MAGMA's, and the held copy settles
  it: the archive contains `g1000_eur.synonyms`, which only the MAGMA distribution ships.
- **Every stated download size was wrong.** The archive said "~7.5 GB" in seven places; the fifteen
  byte counts in `SHA256SUMS` sum to 4.67 GB. Corrected in all seven. `fetch_external_inputs.py
  --list` recomputes the figure, so it can be re-derived rather than taken on trust.
- `data/external/SHA256SUMS` header carried three literal `/n` sequences where newlines were meant,
  running the two documented commands together on one line.
- `metadata/provenance.json`'s `source_url` fields were landing pages (`https://www.eqtlgen.org/`)
  rather than download links, and one resource carried the same `GCST90018832` mis-attribution fixed
  above. The id is now `CKDGen_eGFR_by_DM`, the direct URLs match `SOURCES.tsv`, and
  `collect_provenance.py` **cross-checks the two lists** — the same class of drift gate 10 catches
  between `SOURCES.tsv` and `SHA256SUMS`. Its summary line now separates resources (8) from files
  (15), which had been a standing source of "eight or fifteen?" confusion.

### 2026-10-03 (fourteenth pass) — the upstream middleware ships, and every third-party input's redistribution status is on the record

**Numbers: no reported number changes.** No file in `data/derived/` changed; neither submitted
document was edited. This pass only adds material that lets a reader *check* the Z layer.

**Added**
- **`data/upstream/` (27 files, 31 MiB)** — the as-produced outputs of `code/run_upstream.sh`:
  the eQTLGen weight database and its three size bands, both GTEx gene-level covariances, the
  three harmonised and three allele-aligned GWAS tables, and all 15 `official_*` / `official_eq_*`
  S-PrediXcan band outputs. Previously a reader had to fetch ~4.7 GB to check that `data/derived/`
  came from the inputs the archive names; now one command does it:
  `python3 code/upstream/verify_middleware.py --run-dir data/upstream` →
  `identical 27 | differing 0 | missing 3`.
- **`data/upstream/README.md`** — what ships, what cannot and why (four covariances are over
  GitHub's **100 MiB per-file hard block**, one of them by 2.7×), plus a **redistribution ledger**
  for all 15 third-party inputs: size, the licence as published, and whether the archive may pass
  it on. Two facts from that ledger decide it:
  - **9 of 15 inputs exceed GitHub's 100 MiB per-file block** and physically cannot be committed
    (FinnGen R13 ×3 at 762–764 MiB, GCST90043640 ×2 at 504/425 MiB, `g1000_eur` at 488 MiB,
    eQTLGen at 308 MiB, PGC3 at 229 MiB, GCST90018832 at 170 MiB).
  - **PGC3 may not be redistributed at all**, independently of size: its Data Access Terms state
    *"Investigators will not cross-post these data or make them available elsewhere"*. The GWAS
    Catalog inputs, by contrast, are CC0 — they fail on size, not on licence.
- **`scripts/verify_from_clone.sh` gate 9** — hashes the shipped middleware **inside a clone**.
  This is not belt-and-braces: some of it is CRLF, and `.gitattributes` would happily normalise it
  to LF, changing every byte and invalidating every recorded hash. That is the failure this archive
  already recorded once against `data/external/SHA256SUMS`. `.gitattributes` now carries
  `data/upstream/** -text` to keep the bytes verbatim, and gate 9 is what proves it held — verified
  by direct comparison of the stored blob against the working file for all 27 files.

**Fixed**
- `DOI_PENDING.md` still said `verify_from_clone.sh` runs "7 gates" (it was 8, now 9) and described
  `env/Dockerfile`'s base image as unpinned. Both corrected.

### 2026-10-03 (thirteenth pass) — the upstream chain re-run end to end, and the two defects that found

**Numbers: no reported number changes.** Neither submitted document was edited. No file in
`data/derived/` changed. What changed is that the raw-input → Z-layer chain was **actually re-run**
on a machine holding all 15 hashed external inputs, which is the first time that has been done by
anyone other than the run that produced the archive — and it found two things.

**1. `build_covariance.py` wrote the GTEx covariances in the wrong row order — a real defect, now fixed.**
The two archived covariance sets come from **two different producer scripts with different row
conventions**, and `build_covariance.py` applied one of them to both. Added `--order`:

| `--order` | genes | SNPs within a gene | arm |
|---|---|---|---|
| `model` | ascending gene id | model-DB row order | eQTLGen |
| `bim` | model-DB insertion order | **LD panel `.bim` order** | GTEx |

`run_upstream.sh` steps 2 and 5 now pass the right one. Without it the GTEx covariances were the
same gene set with the same values in a different order — `identical 30 | differing 0` becomes
`differing 2`, and a *content* comparison cannot tell the difference. That is why it survived: the
downstream effect was floating-point only (max |Δ| = 3.6 × 10⁻¹⁵ over a GTEx arm's 162k cells).
The file hash, however, was wrong, and so were the `cov_*.txt.gz` rows in `data/external/README.md`.

**2. `run_upstream.sh` could report success while writing nothing.** S-PrediXcan **refuses to
overwrite** an existing `--output_file` — it logs "already exists, move it or delete it if you want
it done again", exits 0, and leaves the stale file. Steps 3 and 7 now `rm -f` their target first.
Encountered directly during this pass: six GTEx runs reported `ok` and produced no change.

**Added**
- `code/upstream/verify_middleware.py` — hashes all **30** middleware artefacts against the copy the
  reported numbers came from and exits non-zero on any disagreement. Wired in as
  `run_upstream.sh` step 8, so a rebuild that disagrees now fails instead of being described in
  prose. `--require-all` also fails on artefacts not yet produced.
- `env/environment-upstream.yml` — the **second** Python environment, pinned: 3.12.13 / numpy 1.26.4
  / scipy 1.13.1 / pandas 2.2.3. The upstream chain needs it and cannot share `environment.yml`
  (3.13 + numpy 2, no installable numpy 1.x). Until now the requirement lived in a script comment.
- `env/README.md` rule 6: if a step needs a different interpreter, pin that interpreter in its own
  file rather than loosening an existing pin.

**Verified**
- `identical 30 | differing 0` across the whole middleware set: 3 model databases, 7 covariances,
  3 harmonised GWAS, 3 allele-aligned GWAS, 6 GTEx S-PrediXcan arms, 9 eQTLGen S-PrediXcan band arms.
- The previously un-re-run step is now re-run: the **eQTLGen S-PrediXcan bands A/B/C × DR/DN/DPN**,
  all nine byte-identical, including `cov_A.txt.gz` (18,390,068 rows) and the 94-gene band output.

**Also corrected in this pass**
- `.zenodo.json` said "Four of the eight manuscript figures have no producing script in this archive".
  That stopped being true when `ge_main/` shipped and Fig. S2 was recovered; only **Fig. S4** (a gel
  photograph) has none. This text goes into the DOI record, so it mattered.
- `figures/README.md` and `code/README.md` each still carried a sentence contradicting the rest of the
  same file about which manuscript figures are reproducible. Both rewritten with the current status.
- `env/Dockerfile` pinned by digest: `continuumio/miniconda3@sha256:eca594d6…` (= `26.7.1-1`). Docker
  Hub is unreachable from this environment, so the digest was resolved through a reachable mirror and
  then verified independently of that request — the index was re-fetched *by digest* and hashed
  locally, the amd64 child manifest and its config likewise, and neighbouring tags return *different*
  digests. `scripts/cut_release.sh` §7 now checks the image reference with any trailing comment
  stripped, so the readable tag in the comment no longer trips the check.
- `paths_config.py` now identifies **which revision** of a submission document you hold, by MD5, from
  a recorded `revisions` list — including the two added here (`rev3`, `rev4`). It previously carried a
  single `md5` used only to build a hint string, so *any* file printed `[ok]`. An unrecognised
  document now prints `[UNRECOGNISED]` with its actual MD5 and every recorded revision, and
  `--strict-docs` makes it a non-zero exit. `INPUTS.md` §B.1's promise — "a run either matches or says
  so" — was not enforced by code before this; now it is, and both behaviours are tested.
- `run_all.sh` no longer fails when the Supporting Information `.docx` is absent. It reported
  `2 failure(s)` while `README.md` promised the step was "skipped, not failed". The two SI-dependent
  scripts are now detected up front, skipped by name, and the run ends
  `pipeline completed with no failures` with a `note: these steps were SKIPPED` line.
- `metadata/provenance.json`'s `analysis_env` said "Python 3.13.0" while `environment.yml` pinned
  3.13.12. It is now **read from the pin files** (`scripts/collect_provenance.py::_env_versions`), so
  the manifest cannot disagree with the environment it describes.
- S20: section 7d of `recompute_r3_s9_s20_log.txt` labelled three rows `差一个网格步`. They are not a
  discrepancy — the published values come from a Monte-Carlo search on a grid, the `r3` column from a
  deterministic closed form snapped to the same grid, and the two differ by one step exactly where the
  closed form lands just above a grid point. Each row is now named accordingly and the JSON carries an
  explicit `S20_min_lambda_note`.

### 2026-10-03 (twelfth pass) — DOI slot, predecessor migration, and the archive-map contradictions an external audit found

**Numbers: no reported number changes.** Neither submitted document was edited. One value moved from
"absent from this archive" to "derivable, with a stated residual" (see the S5a entry), and one
repository file began reproducing a value it previously could not.

This pass answers an independent reproducibility audit of this repository, run against HEAD
`e4e4dec`. The audit's headline finding was that the *downstream* chain reproduces fully — 7/7 release
gates, 15/15 minimal assertions, 87/87 ACAT-O cells, S9 pool re-derivation byte-identical, and every
committed figure PNG identical on regeneration — while three things around it did not. Those three
are what this pass fixes.

* **The DOI was a placeholder with nowhere to put the answer.** Four carriers held concept- and
  version-DOI placeholder tokens, `README.md` called the archive a "citable snapshot", and the badge
  was a Zenodo badge that 404s. Added:
  [`metadata/zenodo_release.json`](metadata/zenodo_release.json) (single source of truth),
  [`scripts/set_doi.py`](scripts/set_doi.py) (`--show`, `--check`, and a one-command backfill that
  rewrites all four carriers and the badge together), and [`DOI_PENDING.md`](DOI_PENDING.md), which
  states the publication steps and why the manuscript's currently-cited DOI
  (`10.5281/zenodo.22910500`) is **not** a substitute — it resolves to the predecessor `-audit`
  repository's v1.0.0, a 2.34 MB snapshot published 2026-09-23, before every gap closure, the figure
  build outputs and the SI ACAT-O rule. `README.md` now carries an honest pending notice instead of a
  false citability claim, and `scripts/cut_release.sh` grew a section that surfaces the pending state
  at pre-flight.
* **The predecessor repositories no longer have to be cloned.** Every tracked file in both of them
  (165 + 190) was compared against this tree **by blob hash**, and each was given a disposition:
  123 + 167 already identical here, 30 + 15 superseded by a repaired canonical copy, 8 + 6
  deliberately left behind (build/config files this repository replaces), and **6 migrated**. The
  six are in [`docs/predecessors/`](docs/predecessors/README.md): the predecessor's `ARCHIVE_NOTE.md`
  and `README.md`, both `audit_notes/README.md` indexes (the `-audit` one carries the 2026-09-23
  rebuild addendum this repository had dropped), and both `_PROVENANCE.json` records for the
  superseded layer. Machine-readable:
  [`docs/predecessors/MIGRATION_MANIFEST.json`](docs/predecessors/MIGRATION_MANIFEST.json) (355 files).
* **`metadata/ARCHIVE_MAP.md` contradicted itself in three places**, invisible to
  `check_archive_map.py` because that check validates structure, not prose. (i) The Figs. 1–4 row
  still read "`figures/` contains only its README" while seven figure build outputs were committed;
  it is now split into a ✅ row for Figs. 2–4 (which regenerate byte-identically) and a 🟡 row for
  Fig. 1. (ii) Figs. S1 and S2 were still 🔴 `none` while §5 recorded GAP-4 as partly closed and
  `code/figures/recovered/` shipped their generators; both are now 🟡 with the reason each is not ✅.
  (iii) The Note S4 row described checksums as `<hash>` placeholders while `data/README.md` records
  them, correctly, as `not-held`. Counts: **47 items, 24 ✅ / 14 🟡 / 0 🔴 / 9 ➖** (was 46 / 23 / 12 / 2 / 9).
* **SI Table S5a's fourth row now reproduces.** It was the single value
  `scripts/audit_documents_vs_repo.py` reported as absent from the archive: "√N_e weights applied
  directly on the Z scale" (pooled Z +2.09; Q 76.6; I² 98.7). The convention had been conflated with
  the β-scale row. `code/analyses/m6_ne_weighted_sensitivity.py` now emits both — the normalised
  Stouffer combination (M6(b), +2.39) **and** the √N_e-weighted arithmetic mean (M6(c)) — because the
  SI prints both. M6(c) gives **+2.0926 → +2.09 ✓** and **I² 98.69 % → 98.7 % ✓**, with Cochran's Q
  on the Z scale at **76.27 against the published 76.6** (Δ −0.33, −0.43 %). That residual is printed
  by the script and recorded in the map; the published Q is not reproducible to its third significant
  figure from the two cohort Z/N_e pairs this archive ships.
* **S17's two undisclosed parameters are stated as measured facts, not as an outstanding debt.**
  Generator = `numpy.random.RandomState` (MT19937): seed 20260915 gives the published interval
  `[0.1161, 0.6220]` → `0.12–0.62` where PCG64 gives `0.11–0.63`. Resampling is over a
  lexicographically sorted gene vector. What remains is the SI table note — a manuscript-side edit,
  tracked in `docs/audit_notes/R2残余差异消除方案_20261002.md`.
* **The archive's own record of the manuscript's hash was stale.** `INPUTS.md §B.1` and
  `results/recompute_log.txt` recorded `dbbe4f81…` / 30,524 B, which is the file as it stood *before*
  reference [39] was repointed to this repository; the submitted revision is `a6f7521b…` / 30,523 B.
  The Supporting Information still matches its recorded hash exactly, and no number moved — the
  change is one reference string. Both revisions are now recorded, with the reason for the delta, and
  `results/` is regenerated against the current file.
* **Defects fixed while in the area.** `recompute.py` wrote a tracked CSV through pandas' default
  `lineterminator` (= `os.linesep`), so on Windows it rewrote `results/merged_pairs.csv` with CRLF
  against `.gitattributes`' `eol=lf` — the same defect class fixed for another writer on 2026-10-02,
  missed here; it is invisible because git normalises on commit, which is why it survived.
  `run_spredixcan.sh` mounted its inputs at `/input/...` while reading `/app/input/...` and named a
  non-existent entry point, so all nine runs silently reported "SKIP" and the script still exited 0;
  the mounts are corrected and the script now **fails loudly** when nothing ran.
  `m6_ne_weighted_sensitivity.py` wrote its report to `data/processed/`, a directory that has not
  existed since the canonical reorganisation, so it printed and then died on the write.
  `env/Dockerfile`'s unpinned base image is now surfaced by `cut_release.sh` section 7 with the exact
  command to resolve it — still open, because Docker Hub was unreachable from the repair environment
  (HTTP 000) and pinning to an unverified tag would be worse than saying so. `data/README.md` printed
  Python 3.13.0 (the manuscript's figure) where the pin has been 3.13.12.

### 2026-10-03 (eleventh pass) — M3 verified already implemented, and `HK` pinned to housekeeping

**Numbers: no reported number changes.** Neither submitted document was edited. This pass corrects a
statement the ninth and tenth passes got wrong, and records two verifications.

* **The ninth pass said peer-review item M3 was "a text edit still owed". It is not owed — it is
  already done.** Checked against the current revision on 2026-10-03: the Table S10 note prints the
  resource's *full* composition (1,032 European + 220 East Asian cases, 451,248 European + 132,764
  East Asian controls); the Limitations sentence distinguishes "the GWAS used for the partition" from
  the descriptive DN check; and the phrase "largest available European DN resource" no longer appears.
  The note's four counts match the GWAS Catalog record for `GCST90018832` digit for digit
  (`cohort = "BBJ|UKB|FinnGen"`), so the East Asian component is a fact, not a misreading.
* **The subset actually analysed is verifiable, too.** All 1,979 variants retrieved from OpenGWAS
  carry `n = 452,280` — the European component (1,032 + 451,248), not the pooled 585,264 — so the
  note's "only the European component is analyzed here" is a checked claim.
* **`HK` means housekeeping here, never Hong Kong.** The submitted manuscript has no "Hong Kong" at
  all; its two `HK` occurrences are the reference author *Im HK*. The SI uses `HK` four times, each as
  the housekeeping arm's label against the candidate arm (`HK 87 … vs cand 84 …`). The repository is
  consistent (`hk_genes.txt` header: "HRT Atlas v1.0 human-mouse common HK set"). The one "Hong Kong"
  string in this tree lives in `code/deprecated/`, in an abandoned draft that spelled it out and never
  abbreviated it.

`data/README.md` now carries both verifications next to the ancestry-recording rule that M3 exercised.

### 2026-10-03 (tenth pass) — the SI's ACAT-O combination rule, found and gated

**Numbers: no reported number changes.** Nothing in either submitted document moved. What changes is
one column's status: the last sub-item left open by the ninth pass is closed, and the rule behind it
is now written down and asserted by a gate rather than described.

The ninth pass recorded that SI Table S6's **"ACAT-O combined P"** column reproduced for only 68 of
87 cells and concluded that "the combination rule is still not established". **The conclusion was
wrong, and the error was in the check, not the archive.**

* **What was actually being computed.** The column is not an unweighted average of the tissues'
  Cauchy terms. It is a **sqrt(N)-weighted** Cauchy combination:

      p_ACAT-O = 0.5 - arctan( SUM_t w_t * tan((0.5 - p_t) * pi) / SUM_t w_t ) / pi,   w_t = sqrt(N_t)

  with `p_t = 2*Phi(-|Z_t|)`, `N_t` the GTEx v8 eQTL sample size of tissue *t* —
  **Nerve_Tibial 532, Whole_Blood 670** — component p-values clipped to `[1e-15, 1-1e-15]` and the
  result to `[1e-300, 1]`. That weighting was not a guess: the same sqrt(N) convention governs the
  `Z_multi_tissue` column of SI Table S3 (Stouffer), which reproduces to four decimals.
* **Why 68/87 looked like a rule problem.** Two independent mistakes cancelled into a plausible
  number. The tissue p-values were combined *without* weights, and the SI prints this column at
  **three significant figures** (`%.3g`) — so 19 cells were being scored against a fixed absolute
  tolerance on a grid that is 10x coarser for values near 1 than for values near 0.1. With the
  weights restored and the column compared at its own precision the count is **87/87, character for
  character**.
* **Independently corroborated.** The same rule reproduces **all 138** `P_ACAT_O` cells of SI
  Table S3 (25/138 for the unweighted form), including ACTB/DR = 0.2085, which an earlier audit had
  recorded as unreachable.
* **Made a gate, not a sentence.** `code/analyses/reproduction_20261002/scripts/recompute_acat_o.py`
  re-derives all 87 cells from `data/derived/hk_official_Z.csv` alone and exits non-zero on the first
  disagreement; `scripts/verify_from_clone.sh` §5 now runs it in the clone. A rule that "mostly
  works" is exactly the failure mode this package exists to catch, so it is asserted rather than
  described. `data/derived/hk_official_Z.csv` now carries the ACAT-O columns itself, and its Z columns
  are stored at full precision (the 4-decimal rounding previously stored flipped one cell,
  TRIP12/DPN, across a `%.3g` boundary).

**Recorded correction:** the ninth-pass entry below says the ACAT-O combination rule "is still not
established". It is established as of this pass; that clause is superseded.

### 2026-10-03 (ninth pass) — GAP-1, GAP-2, GAP-6 and GAP-8 close; nothing was ever lost, it was found

**Numbers: no reported number changes.** Not one value in `data/derived/` moved, and neither submitted
document was touched. What changed is that four gaps the archive had recorded as open are now closed —
and closed by *finding* the computations, not by re-deriving them.

The previous pass left a specific open list. Working through it against two official MetaXcan runs that
had never been catalogued closed most of it.

* **GAP-1 (SI Table S6, the housekeeping layer) — closed for the Z and model-SNP columns.** The
  archive believed the corrected layer "is not archived anywhere on disk". It is. An official MetaXcan
  v0.8.1 recompute from **2026-09-16 06:54-06:55** — the exact window in which the published Table S6
  block changed — still exists at `E://workbuddy//2026-09-15-21-55-56//metaxcan_run//official//`. Checked
  cell by cell: **all 159 numeric Z cells reproduce, max |SI − official| = 5.0 x 10⁻⁵** (agreement to
  the fourth decimal the SI prints), and the **model-SNP column is 30/30**. That also explains the
  8-gene "constant ratio" anomaly: the published table is an independent recompute, not a σᵢ rescale of
  the superseded layer, so no per-gene factor could ever have matched. The layer now ships as
  **`data/derived/hk_official_Z.csv`**. *One sub-item stays open and is recorded as such:* the SI's
  **ACAT-O combined-P** column reproduces for only 68 of 87 cells (the rest differ by ≤ 0.023), so its
  combination rule is still not established. *(Superseded the same day — see the tenth pass.)*
* **GAP-2 (Table 1 housekeeping arm) — closed.** The arm is **0.0 % (0/87)**, and re-deriving the FDR
  calls from the shipped layer returns **0/87** (most significant test: GOLGA3/DR, P = 0.0126, BH
  q = 1.00). The arm reproduces whether or not the ACAT-O rule is settled.
* **GAP-6 (SI Table S7, "Smallest margin attained") — closed.** The column is not unsourced; the
  table's own note defines it as `max(|lower|, |upper|)` of the operative 90 % interval. It is a
  deterministic function of the interval the recovered calculators already reproduce: GTEx 7.3, eQTLGen
  10.4, pooled gene-cluster 6.4 — all three match.
* **GAP-8 (SI Table S10, DN cross-population) — closed.** The official MetaXcan run of
  ebi-a-GCST90018832 (Sakaue et al. 2021) under eQTLGen weights still exists, and reproduces **all five
  genes** at the printed precision (RNH1 −0.83/0.41, CKAP4 −0.86/0.39, HSP90AB1 −0.90/0.37, RPS14
  +1.27/0.21, EEF2 −0.46/0.65). Ships as `data/derived/dn_cross_population.csv`. (Peer-review item M3 —
  name the resource's full European *and* East Asian composition — was **verified already implemented**
  in the current revision on 2026-10-03; see the eleventh pass.)
* **GAP-4 (the Fig. S1 / Fig. S2 / Fig. 1 generators) — partly recovered.** `gen_figs4.py` reproduces
  the Fig. S2 violin exactly (61-gene universe, 24/24/13, medians 374/632/669). `rebuild_fig1_2_9.py`
  holds `figure1()` (the framework = main Fig. 1) and `figure2()` (the flowchart = Fig. S1), but its
  `> 75 %` box reads `66.4-70.1 %` where the published SI prints `66.1-68.2 %` — and a contemporaneous
  record shows the published box was **pixel-edited on 2026-10-01** after a full-disk search for an SI
  figure script found nothing. So Fig. S1 is recovered **structurally**, not verbatim. Both scripts ship
  verbatim in `code/figures/recovered/`, deliberately not wired into `run_all.sh`.

Also recorded: reference **[39] in the submitted manuscript has been repointed** from the predecessor
`eqtl-source-discordance-audit` to this canonical repository (the Zenodo DOI line was deliberately left
unaltered, pending a Zenodo release of this record).

**No script was written and no value recomputed** for any of the four closures — in each case the
computation already existed on disk and had simply never been catalogued. That is the finding.

### 2026-10-03 (eighth pass) — Table S20's generator no longer needs a document we cannot ship

**Numbers: no reported number changes.** `m15_pc.py` writes the same JSON, key for key.

`Additional file 1_审稿意见修订_20260917.docx` — the review-revision Supporting Information —
was the one input that kept `scripts/r3/m15/m15_pc.py` from running on a clone, and it is a
submission document that this archive does not redistribute. It turns out not to be needed.

The generator reads exactly four tables: S1 (gene groups), S2 (GTEx baseline Z), S15
(housekeeping eQTLGen) and S18 (eQTLGen per-gene). All four also ship in `data/derived/` as
`gene_groups.csv`, `gtex_Z.csv` and `eqtlgen_Z.csv`, and the two routes were compared row for
row on 2026-10-03: 104/104, 222/222, 81/81 and 207/207 rows, **zero differing cells**. (S15
prints 90 rows, nine of them blank; the archive keeps the 81 with a testable statistic, which
is the set the script's own `q is not None` guard would keep, in the same order.)

`m15_pc.py` now tries the document first and falls back to the derived tables. Both routes were
run and the emitted JSON is identical to the archived `m15_positive_control.json` under either,
so supplying the document remains an auditable path rather than a requirement. Pass `--af1-docx`
(or `REPRO_AF1_DOCX`) to use it.

**Consequence: SI Table S20 is reproducible from a clone.** `INPUTS.md` §B.1, its §D
script-to-input table, `code/README.md` and this package's README were updated; the previous
text told a reader the row was `no` for "runs from a clone".

### 2026-10-03 (seventh pass) — `run_all.sh` runs again, and the environment installs

**Numbers: no reported number changes.** `data/derived/` is byte-identical, the three submitted
documents are untouched, and no value in the manuscript or the Supporting Information moved. What
changed is that the repository's self-declared *only supported entry point* now works.

An independent audit found that `bash code/run_all.sh` — which `README.md` and `code/README.md` both
call "the ONLY supported entry point" and which "must run end to end from a clean environment" —
**failed on a fresh clone with exit 1 and eight FAIL lines**, ending in
`Do not treat this run as reproducing the paper.`

**Fixed — four independent causes, none of them numerical:**

- **Legacy filenames were never remapped.** Seven figure scripts still asked for the predecessor's
  `*_official.csv` names, which ceased to exist when the layer moved to `data/derived/` on
  2026-10-02. `code/figures/paths_config.py` now carries the same `OFFICIAL_Z_RENAME` map its
  `code/analyses/reproduction_20261002/` counterpart already had, exposed as `rz()`. No data was
  duplicated to make this work.
- **A false-positive preflight.** `run_all.sh` greps the figure directory for the quarantined path
  `data/processed/`; the only hits were prose in `00_build_officialZ_data_layer.py` — the script that
  *writes the deprecation notice*. The prose was reworded; the guard is unchanged and still catches a
  real reference.
- **BMC-era table numbering in the figure scripts.** `04_redraw_Fig8.py` and
  `08_redraw_Fig6_labels_20260920.py` looked up SI tables by the predecessor's numbering, which the
  new Supporting Information shifted by one (Table S*n* → S*(n+1)*, old S26 promoted to S1). Both now
  resolve table numbers from the captions and accept either numbering.
- **An em dash the cell parser could not read.** The new SI writes a missing value as `—`; the
  one-line `float()` lambdas raised `ValueError: could not convert string to float: '—'`. A shared
  `paths_config.num()` now returns NaN for placeholders, thousands separators and free text.

**Fixed — the environment.** `env/environment.yml` pinned `python=3.13.0` with `numpy=1.26.4`, which
has no cp313 build on any channel, so the conda environment had no solution
(`pip download numpy==1.26.4` → `No matching distribution found`) and the Dockerfile that consumes
the same file could not build. The stack now names the versions the reproduction actually ran under,
each verified to have a cp313 wheel. `env/requirements.txt` used lower bounds throughout — against
`env/README.md` rule 1, which the file itself quotes — and now pins the same versions.
`env/Dockerfile` had four defective paths (`COPY environment.yml`, `chmod +x /app/run_all.sh`,
`ENTRYPOINT … /app/run_all.sh`, `renv::snapshot` before `WORKDIR /app`) and an `apt` pin with no
Debian candidate; all corrected.

**Changed — the figure policy is now stated.** `figures/` was empty while `README.md` called it
"archived figures exactly as submitted", `figures/README.md` argued that figures should be included,
and `.zenodo.json` said the record "contains no figures" — three positions, none true, and
`figures/README.md` itself demanded the choice be made explicitly. The policy is now: **`figures/`
holds the build outputs of `code/run_all.sh` and they are committed.** Seven figures (PDF + PNG) are
added, with a build-name → manuscript-figure map and an explicit list of the four manuscript figures
whose producing script is not in this archive (Fig. 1, S1, S2 and the wet-lab S4). `README.md` and
`.zenodo.json` were corrected to match.

**Changed — documentation that contradicted itself.** `code/README.md`'s script → manuscript-item map
was an unfilled template naming scripts that do not exist; it is now filled. `code/analyses/recovered/README.md`
still listed S9, S16 and S27–S29 as missing a month after they were closed; it now defers to
`metadata/ARCHIVE_MAP.md`. `docs/audit_notes/` gains the full repair record.

**Verified from a clone, not locally.** `bash code/run_all.sh` → exit 0, no failures, all seven figure
scripts producing output; headline check unchanged at 96 pairs / 68.8 % / ρ 0.3898. The regenerated
figures reproduce the manuscript's own legend values (Fig. 4: ρ +0.414 / 138, +0.636 / 72, +0.418 /
8,890; Fig. 3: Δρ −0.0197 and +0.0336). `scripts/verify_from_clone.sh` → 0 failures.

**Deliberately left open, and recorded as such** (`docs/audit_notes/仓库可复现性修复记录_20261003.md`):
the DOI placeholders, the unpinned `FROM …:latest`, GAP-1/GAP-2 (the housekeeping layer of Table 1),
GAP-4, GAP-6, GAP-8, the `m15_pc.py` input document, and — the finding that let all of the above ship
unnoticed — **`verify_from_clone.sh` does not run `run_all.sh`**, so a green gate says nothing about
the one entry point readers are told to use.

### 2026-10-02 (sixth pass) — the documents audited against the archive; one row does not reproduce

**No reported number changes.** New check, and one status that was wrong.

`scripts/audit_documents_vs_repo.py` answers the question a reviewer actually asks — are the
numbers in the manuscript and the Supporting Information in here — in two strengths, and says
which is which. Run against `Supporting_Information_GenetEpidemiol_20260930.docx` (31 tables)
and `Manuscript_GenetEpidemiol_20260930.docx` (4 tables):

* **Class A, structural equality** — 8 tables that are a straight projection of a shipped
  table, compared **cell by cell** after aligning rows on their key columns:
  **4,398 cells, 0 mismatches.** S2 728/728, S3 1,554/1,554, S4 420/420, S13 288/288,
  S15 243/243 (+9 declared placeholders), S18 1,035/1,035, S23 122/122, main-text
  Table 2(A) 4/4.
* **Class B, value presence** — every other table's numbers looked up in the archive at the
  precision the document prints them: **2,850 of 2,851.** Class B is a necessary condition,
  not a sufficient one, and the script says so.
* **Class C** — 8 items the archive map already declares as gaps or as needing a submission
  document, listed so the report accounts for every table instead of the easy ones.

**The single absent value is a real finding, and it changes a status.** SI Table S5a has four
data rows; `data/derived/crosscohort.csv` carries rows 1, 2 and 4 (under different labels) but
**not row 3, the √N_e direct-weighting sensitivity (pooled Z +2.09; Q 76.6; I² 98.7)**. The map
marked S5a ✅ on the strength of row 1 alone. It is now **🟡**, with the three reproducible rows
named and the fourth identified. Distribution: **19 ✅ / 13 🟡 / 5 🔴 / 9 ➖**.

Three classes of apparent mismatch turned out to be conventions, not data, and the comparator
now encodes them — each was worth 30–84 phantom cells: the documents print `—` where the CSVs
leave a field empty (Table S3); they print `Non-candidate` where the CSV holds `NonCandidate`
(Table S4); and Table S23 prints the **denominator** of a `matched/total` field, not the
numerator — which is easy to miss because for ACTB the two coincide (`23/23`) while CKAP4 prints
659 against `633/659`.

Also fixed: `paths_config.si_tables()` documented `object i = Table S(i+1)`, which is **false**.
The submitted SI splits Table S5 into two table objects (S5a, S5b), so the rule holds only up to
the fourth object — `si_labels()[6]` is `'S6'`, not `'S7'`. Nothing depended on it, but a caller
trusting it would have read the wrong table. `si_labels()` and `si_table_by_label('S5a')` now
address tables by caption, which is what the existing diagnostics were really doing.

### 2026-10-02 (fifth pass) — the last two caveats, one closed and one made specific

**No reported number changes.** S9's published values, and every other value in the Supporting
Information, are untouched. What changes is that one of the two remaining "you cannot re-run
this" statements is now false, and the other is now measured.

**S9 — closed, not merely declared.** The row said `clone (outcome)`: the published numbers
reproduce from a clone, but re-deriving the pools needs the mashr model databases, which this
archive does not distribute. That framed the wrong thing as the obstacle. The pool filters read
**one column** out of those 10.5 MB of SQLite — `n.snps.in.model`, per gene, for two tissues —
so the dependency was reduced to what is actually used and shipped as
`data/derived/mashr_nsnps.csv.gz` (61 kB; 16,812 symbols × 2 tissues). `build_pools()` now
reads the projection, and it was run with **every** source variable unset:

```
POOL_A chain: WB model genes 12,622 -> minus 104-panel 12,555 -> minus panel families 11,885
              -> minus disease blacklist = POOL_A 11,820 -> of which have BOTH-tissue models 10,450
POOL_818 = 818 (published 818), both-tissue 767 (published 767), WB-only 51 (published 51)
```

Every published figure of the chain, and the four pool files it writes came out
**byte-identical** (`git status` clean afterwards). `REPRO_MASHR_DB_DIR` is no longer needed to
re-derive anything: set it and `load_model_snps()` reads both databases *as well* and refuses to
continue unless every gene and count agrees — verified by changing one count in the projection
and confirming it reports `1 value(s) differ`. S9's locality label is therefore `clone`, and the
`clone (outcome)` label was retired: it existed for that single row and an unused category
invites the reader to hunt for the row it belongs to.

Two false dependencies were removed on the way. `build_pools()` and `copy_small()` still
demanded the *external* originals for `covariate_matrix.csv`, `Human_Mouse_Common.csv`,
`groups.json` and the three random-control files even though those ship — so the derivation
refused to run from a clone after the data layer had landed. They now prefer the shipped copy.
`copy_small()` also used raw `shutil.copyfile` on files `.gitattributes` declares `eol=lf`, which
is the same defect as the CRLF hash table: a plain copy of a CRLF source produces a shipped input
whose MD5 can never match. It uses `copy_lf`.

**S17 — the caveat is now measured rather than inherited.** The row said the gene-cluster half
needs "the housekeeping layers carried in SI Tables S6/S15". Checked, and it is
narrower and more interesting than that. The five `repo_crosscheck/verify_cluster*.py` scripts
read only `data/derived/primary_arm_96pairs.csv` and **do reproduce from a clone**. The
gene-cluster rows are one script, `bmc_ref/verify_s17_cluster.py`, and it reads four SI tables
from the `.docx`: t02 = S3, t06 = S6, t15 = S15, t18 = S18. Three of those four are redundant in
principle — S3 is `data/derived/gtex_Z.csv`, S15 and S18 are the `Group` column of
`data/derived/eqtlgen_Z.csv`. **Only t06 = S6 is genuinely absent**, and it cannot be recovered
from `gtex_Z.csv` because the housekeeping genes are excluded from the 74-gene panel by that
panel's own pre-specified rules — measured overlap **0 of 30**. The z-scores are *not* the
obstacle: the shipped wide table carries 29 of the 30 (TUT1 absent). The obstacle is the
combination rule into an ACAT-O p-value, and it is **not recovered**: recombining those
z-scores by the textbook Cauchy/ACAT-O recipe misses the published values on the *candidate*
genes, where ground truth exists (ACTB/DR: published 0.2085, recomputed 0.2116). That route is
closed until the rule is established, and saying so is more useful to a reader than "needs the
SI". The row keeps `clone + SI`, now for a reason someone can check.

**S20 is unchanged and still `clone + SI`** — its generator `m15_pc.py` reads three tables out
of Additional file 1 by position, and shipping those values is a decision about redistributing
submission content, not a reduction like the one above. It is left as it stands.

Distribution is unchanged: **20 ✅ / 12 🟡 / 5 🔴 / 9 ➖**. The locality vocabulary is now four
labels — `` `clone` `` (28 rows, was 27), `` `clone + SI` `` (2), `` `none` `` (7), `` `—` `` (9).

### 2026-10-02 (fourth pass) — checks that can fail, and a map that checks itself

**No reported number changes.** The data layer, the estimators and every value in the
Supporting Information are untouched. What changes is whether the repository can tell when
something *has* changed.

Three questions drove this pass. Each produced a defect that had been passing review.

**1. Can the archive prove a reader gets what we claim?** Not from here. Four defects have
shipped from a green pre-flight: a path bootstrap one directory level short (it compiles,
then dies at run time), a hash table recording CRLF values for files a clone checks out as
LF, a manifest hashing the working tree, and a rebuild writing a shipped input with the
platform's line ending. Every one of them passed on the machine that produced it. The checks
now run where the reader is:

- **`scripts/verify_from_clone.sh`** — makes a `git clone --no-hardlinks` into a temp
  directory and runs every check inside it, including a CRLF sweep of the checked-out tree.
  It is the definition of "it passes". `docs/RELEASE_PROCESS.md` §1 now requires it
  alongside `cut_release.sh`, and `cut_release.sh` says in its own header why it is not
  sufficient on its own.
- **`scripts/verify_provenance.py`** — recomputes every SHA-256 and byte count in
  `metadata/provenance.json` from the index, and compares. Until now nothing re-checked the
  manifest: `cut_release.sh` confirmed only that it was valid JSON and free of placeholders.

**2. Can a check fail?** Four could not.

- `paths_config.py`'s shipped-input self-check printed its verdict and **exited 0 either
  way**, so no gate could rely on it. It now exits non-zero, and `cut_release.sh` calls it.
- `check_wiring.py` gained **`--self-test`**: it runs itself against two probes of its own —
  one wired correctly, one stopped a directory short — and fails unless the first passes and
  the second is caught. That checker was vacuous once (its own directory was on `sys.path`,
  so every script "passed"), and a gate nobody has watched fail is not a gate. The
  demonstration is now part of every release.
- `check_wiring.py` also grew into a round trip: the wiring-package rebuild now writes
  `s9_pools/disease_blacklist.txt` through `write_lf()`. It was written with the default text
  mode, which translates `\n` to `os.linesep` — so **rebuilding the package on Windows broke
  the package's own integrity check**, producing a CRLF file whose MD5 did not match the LF
  value recorded in `paths_config.SHIPPED`. Reproduced, fixed, and re-verified by writing the
  file both ways.

**3. Is `metadata/ARCHIVE_MAP.md` checked at all?** It was checked by eye, and eyes stop
checking. Three defects were sitting in it:

- The `Input locality` column — added exactly to separate "verified" from "checkable by
  you" — had been written into the rows but **not into the table headers**. Markdown
  renderers drop cells beyond the header, so the column that protects the manuscript's
  conclusions was invisible in the rendered file while looking present in the source.
- An unescaped `|` inside a cell (`(\|Z\| density)`) split one row into extra cells, shifting
  every value in it one column to the right.
- The summary line is hand-maintained and had already drifted once (it read 16 ✅ / 13 🟡 /
  9 🔴 / 8 ➖ against a table holding 12 ✅ and 12 🔴).

  **`scripts/check_archive_map.py`** now enforces the column declaration, every row's cell
  count against its header, the summary counts against the status column, and a controlled
  vocabulary for the locality labels. `cut_release.sh` runs it. It was verified by
  re-introducing all three defects and confirming each is reported.

**The map now states the two axes explicitly.** The tables previously answered "is the value
right?" and "can I re-run it?" with a single mark, which is how both went wrong. `Status`
now answers only the first; `Input locality` answers only the second, from a defined
vocabulary — `` `clone` ``, `` `clone (outcome)` ``, `` `clone + SI` ``, `` `none` ``,
`` `—` `` — and the Status key says plainly that **a locality label is not a doubt about the
value**. S9 stays ✅ (the published numbers reproduce from a clone without either the mashr
databases or the original GTEx × FinnGen tables) with `clone (outcome)` recording that
*re-deriving the pools* is not possible from this archive. S16 is ✅ `clone`. S17 and S20 are
✅ `clone + SI`. Distribution is unchanged at **20 ✅ / 12 🟡 / 5 🔴 / 9 ➖**.

### 2026-10-02 (third pass) — guard rails, a self-contained check, and one convention still owed

The second pass made the package runnable and shipped the data layer. This pass adds the checks
that keep it that way, and records the two things a reader is still owed.

#### Added
- **`code/analyses/reproduction_min/`** — a single ~180-line script needing only `data/derived/`
  and numpy: no argument, no `.docx`, no network. It reproduces the headline 66/96 = 68.75 % and
  ρ = 0.38964, the per-phenotype split, the tissue-only arm (138 · 91 · 65.9 % · +0.4138) and the
  three SCZ arms (5,584 · 5,551 · 5,506 at +0.4690 · +0.4199 · +0.4465), with **15 assertions and
  0 mismatches**. It is the only 100 %-self-contained reproduction in the archive: before it, a
  reader with a bare clone could not verify a single reported number.
- **`code/analyses/reproduction_20261002/check_wiring.py`** — executes every script's import
  preamble and fails if `paths_config` is not importable. Each script carries its own
  bootstrap, and a bootstrap with the wrong depth compiles cleanly and dies at run time; 24
  scripts shipped that way in the first portable revision. The check stubs third-party modules
  it lacks, so it runs under a bare Python, and it strips this file's own directory from
  `sys.path` so it cannot pass vacuously. Called by `scripts/cut_release.sh`, which now also
  fails the release if `reproduction_min` stops reproducing under an interpreter that has numpy.
- **Table-note text for SI Table S24** in `docs/audit_notes/R2残余差异消除方案_20261002.md` §五
  item 7, with the measurement behind it: `multiZ` carries **77 exact zeros** among the 8,315
  complete-case genes; scoring a zero as positive moves the dual arm from 5,506 to **5,544**
  (+38 pairs, **+0.46 pp**), and the other two arms by +1 and +5.

#### Changed
- **The whole tree is normalised to LF.** `.gitattributes` already declared `eol=lf` for source,
  Markdown and JSON; `*.csv`, `*.tsv` and `*.txt` are now listed too. Without this a Windows
  working copy differs byte-wise from a Linux one, and `metadata/provenance.json`, which records a
  SHA-256 per file, would verify on one platform and fail on the other. The committed blobs change
  once; nothing else does.
- **`paths_config.SHIPPED_SPEC` recorded the wrong hashes — 11 of the 20 shipped inputs failed their
  own check in a clone.** The table mixed two conventions: the older entries carried the LF hashes of
  the checked-out files, the newly added ones carried the CRLF hashes of the author's originals. The
  two differ by exactly one byte per line. Consequence: `python paths_config.py` reported *all
  shipped inputs present and byte-exact* on the machine that built the package and reported
  **11 `MD5 MISMATCH` for anyone who cloned it** — i.e. the package's integrity mechanism, added to
  make the archive verifiable, failed precisely for the people it was meant to protect. Found on
  2026-10-02 by cloning `--no-hardlinks` and running the self-check inside the clone; all values are
  now the checked-out ones and the table carries a note saying to re-record them only from a clone.
- `scripts/collect_provenance.py` hashes **every tracked file** (previously three hand-picked
  directories, 36 files against a tree of 281) and records the non-redistributed reproduction
  inputs separately, with their SHA-256. `scripts/cut_release.sh` asserts
  `len(files) + len(excluded) == git ls-files`.
- `metadata/ARCHIVE_MAP.md` §8 records the re-audit that produced all of the above, including the
  one row where the mark and the reality can differ: read the **Input locality** column, not the
  mark, when you want to know whether *you* can check a row.

#### Verification
- **S16 reproduces from a clone**: all nine framework-layer rows re-run and match.
- **Table S9 reproduces from a clone without the mashr databases** — verified with
  `REPRO_MASHR_DB_DIR` unset. The pool membership ships as `data/derived/s9_pools/*.txt`, and the
  official GTEx × FinnGen layer ships flattened, so the exclusion chain 12,622 → 11,820, POOL_818
  = 818/767/51, coverage 568/768, the 16 random-control rates, the 8 null-distribution values and
  the 4 percentiles all reproduce. Re-*deriving* the pools still needs the mashr models; that is
  `00_build_added_derived.py`, not the reproduction, and it is stated on the row.
- **The BMC↔GE cross-check was re-run rather than asserted**: 83 statistics cross-checked, 63
  present in both documents, 20 in the predecessor only, **0 unique to the GE submission**. The
  predecessor *Additional file 1* carries 27 tables against the GE *Supporting Information*'s 31 —
  the `S`*n* → `S`*n+1* renumbering.
- The predecessor repository was cloned to check the `processed_officialZ/` → `derived/` mapping:
  **6 of 6 files identical line for line** (the predecessor stores them with CRLF, so its recorded
  MD5s differ from this archive's LF ones by exactly one byte per line). `code/analyses/reproduction_20261002/INPUTS.md` §A.1 records it
  as a measurement rather than an inference.
- All 18 diagnostic scripts exit 0.

#### Numbers
- **No reported number changes.** This pass adds checks, documentation and a self-contained
  reproduction script; it normalises line endings, which changes file bytes but no value.

### 2026-10-02 (second pass) — make the reproduction package runnable, and its inputs explicit

A review of the first-pass package found that it could not actually be run by anyone
else: its 35 scripts carried 26 distinct absolute paths from the author's machine, none
of them pointing at this repository, and the files they read were not committed. This
entry is the repair.

#### Fixed
- **No absolute paths remain.** Every script in `code/analyses/reproduction_20261002/`
  now resolves its inputs through `code/analyses/reproduction_20261002/paths_config.py`,
  which walks up to the repository root (sentinel `.zenodo.json`), honours `TWAS_REPO`
  and `TWAS_DATA_Z` — the same variables `code/figures/paths_config.py` uses — and
  accepts `--repo-root` / `--ms-docx` / `--si-docx` / `--af1-docx` / `--mashr-db-dir` /
  `--gtex-official-dir`. `code/README.md` rule 3 requires this and the first pass broke it.
- **Scripts no longer claim to accept a path argument without accepting one.**
  `recompute.py` and `recompute_scz.py` previously hard-coded the two documents while the
  package README said they "take a path argument".
- `scripts/recompute_scz.py` reads the gzipped Z layers through
  `paths_config.open_text()`, and records the MD5 of the **decompressed** bytes for those
  inputs so an input's recorded hash no longer depends on the compressor.
- `metadata/provenance_source.json` pointed `superseded_by` at
  `data/processed_officialZ/`, a directory that does not exist in this repository. Now
  `data/derived/`.
- The Supporting Information is read directly from the `.docx` by
  `paths_config.si_tables()`. The `tNN.tsv` files the diagnostic scripts used to read had
  never been committed.
- Three diagnostic scripts could not run at all, independently of the path problem, and
  are fixed here: `repo_crosscheck/verify_cluster3.py` built a 0-d array from a generator
  inside `np.where`; `repo_crosscheck/verify_cluster4.py` indexed a position-list with gene
  names; `r3/diag_s9_s20b.py` exec'd a preamble whose `__file__` pointed at the working
  directory rather than at the sibling script. Every script in the package now exits 0.

#### Added
- `code/analyses/reproduction_20261002/paths_config.py` — the single path entry point
  (repository-root discovery, an input registry with per-file MD5s, `si_tables()`
  extraction, and an actionable message instead of a traceback when a document is absent).
- `code/analyses/reproduction_20261002/INPUTS.md` — every input: logical name, path, MD5,
  byte count, which script reads it, whether it ships here, and where to get it if not.
- `code/analyses/reproduction_20261002/00_build_added_derived.py` — rebuilds each derived
  table added below from the upstream source that produced it.
- **3.7 MB of derived data under `data/derived/`**, so that the two largest gaps are
  closable from a clone:
  - `derived/genomewide/` — the five genome-wide weight-source Z layers, gzipped
    (2.8 MB). These define every analysis universe and the framework-layer contrast
    (S16); before this addition the framework layer was not reproducible from this
    archive at all.
  - `derived/gtex_official_finngen/gtex_official_zscores_wide.csv.gz` — the official
    MetaXcan GTEx × FinnGen layer flattened to one row per gene (0.7 MB), which feeds the
    Table S9 ACAT-O chain without its 12.3 MB of originals. Z-scores are stored as the
    original strings, not reformatted, so the median-|Z| statistics keep their digits.
  - `derived/s9_pools/`, `derived/hrt/`, `derived/hrt_random_control/`,
    `derived/groups.json`, `derived/covariate_matrix.csv` — 12 small files (0.2 MB)
    carrying the Table S9 pools, strata and random controls.
- `data/processed_officialZ/README.md` — a pointer, so the ~40 remaining references to the
  retired path (mostly under `code/deprecated/`) read as *retired* rather than *dangling*.
- `results/README.md` — separates the files a script writes from the transcripts of the
  diagnostic scripts, and says which is which.
- `results/recompute_r3_s9_s20_log.txt` — the run log the S9/S20 script declares but which
  the first pass did not commit.

#### Removed
- `scripts/r3/_patch_r3.py`, `scripts/r3/m15/_patch.py`, `scripts/r3/m15/_patch_r3.py` —
  one-off local patchers that rewrote sibling source files in place by string replacement
  and carried machine paths. Build artefacts, not deliverables.

#### Changed
- `metadata/ARCHIVE_MAP.md` — the six reproduced rows now state **where each input lives
  and whether it ships**, so ✅ is a claim a reader can check. A new section records the
  added data layer.
- `data/README.md` — the new derived tables are listed with their row counts, and the
  directory table now explains `derived/genomewide/` and the retired `processed_officialZ/`
  name.
- `code/analyses/reproduction_20261002/README.md` — the three inaccurate claims removed,
  the run instructions rewritten around `paths_config.py`, and a "what reproduces from a
  clone alone" table added.

#### Verification
- A clean copy of the tree at a different path, with no `.git` and no author directories,
  was run end to end with only the repository contents plus the two journal documents.
  `recompute.py`, `recompute_scz.py`, `recompute_r3_s9_s20.py`, `simulation_validation.py`
  and `m15_pc.py` all completed, and their machine-readable outputs match the committed
  ones key for key. The Table S9 numbers reproduce **without** either the mashr databases
  or the six original GTEx × FinnGen tables.

#### Numbers
- **No reported number changes.** This entry changes where inputs live and how they are
  named; it adds derived tables that were previously absent; and it removes three build
  artefacts. Every value the manuscript and its Supporting Information report is
  unchanged, and the re-run outputs are byte-for-byte equal to the committed results apart
  from input-file hashes.
- One incidental finding, recorded because it explains a count rather than a value:
  `data/derived/s9_pools/disease_blacklist.txt` is stored **without case normalisation**,
  faithfully to the published pipeline. The gene sets it is subtracted from are upper-cased,
  so the single token that is not already all-caps — `C5orf67` — excludes nothing. That is
  why POOL_A holds **11,820** genes and not 11,819, and `both_A` 10,450 and not 10,449.
  The published numbers are correct as printed; the exclusion step simply does not act on
  that one gene. Recorded in `code/analyses/reproduction_20261002/INPUTS.md` section F and
  in `data/README.md`.


### 2026-10-02 — third-party reproduction of both submitted documents

#### Added
- `code/analyses/reproduction_20261002/` — a self-contained reproduction package (61 files, ~3,450 lines of Python) that recomputes every value readable out of `Manuscript_GenetEpidemiol_20260930.docx` and `Supporting_Information_GenetEpidemiol_20260930.docx` from `data/derived/` and the two documents. Layout and run order in that directory's `README.md`; every script prints the MD5 of its inputs on its first line.
- `docs/audit_notes/复现核验_GE投稿两份文档_20261002.md` — the full account. Grade: **R1 ≈ 200 items identical at the reported precision, R2 = 3, R3 = 0**. No reported value failed to reproduce and none was found to differ in its point estimate.
- `docs/audit_notes/BMC定稿与GE投稿值域交叉核对_20261002.md` — the two documents against the predecessor 2026-09-28 final manuscript: 63 comparable headline statistics all identical, none unique to the new documents. Also establishes that the predecessor's *Additional file 1* and the current Supporting Information are the **same document under two numberings** (Table S*n* → S*(n+1)* for n = 1–25, plus the new S27–S30).
- `docs/audit_notes/R2残余差异消除方案_20261002.md` — remediation for the three residual items, with paste-ready SI note text.
- `code/analyses/reproduction_20261002/scripts/r3/m15/m15_pc.py` — **the missing generator for SI Table S20** (`code/figures/m15_positive_control.json` lineage), recovered verbatim.

#### Changed
- `metadata/ARCHIVE_MAP.md` — eight items moved to ✅: SI Tables **S9, S16, S17, S27, S28, S29** and **Note S5** (🔴 → ✅), and main-text **Table 2(B)** (🟡 → ✅); **S20**'s evidence row now names the recovered generator. GAP-3, GAP-5, GAP-7, GAP-9 and GAP-10 are closed. Distribution is now **20 ✅, 12 🟡, 5 🔴, 9 ➖**.
  - The status counts are now produced by a machine count of the status column. **The line previously read "16 ✅, 13 🟡, 9 🔴, 8 ➖", which did not match the table beneath it** — that table in fact held 12 ✅ and 12 🔴. Corrected here rather than carried forward.
  - Two internal cross-reference errors fixed: the Note S5 row cited "GAP-4", which the register reserves for Figs. S1 and S2 (it is GAP-5); and the S20 row described the JSON as its own carrier, which is what allowed the missing generator to go unnoticed.
- `docs/audit_notes/INDEX.md` — three rows added.

#### Numbers
- **No reported number changes.** This commit adds a reproduction package, three audit notes and the recovered S20 generator, and moves archive-map statuses to reflect what has now been reproduced. Every value the manuscript and its Supporting Information report is unchanged. The three residual R2 items are rounding-chain or undisclosed-parameter differences, not value differences; the largest is 0.04 percentage points.

### Added
- Repository consolidated as the single canonical archive for this study; full development history carried over from the predecessor repository, so the pre-specification anchors `58da15b` (2026-07-24) and `e70806b` (2026-09-10) remain reachable in this tree.
- `metadata/ARCHIVE_MAP.md`, `metadata/PRE_REGISTRATION.md`, `metadata/provenance.json`.
- `docs/RELEASE_PROCESS.md` and `scripts/cut_release.sh`.

### Changed
- Archive map re-keyed to the current Supporting Information numbering (Tables S1–S30). The predecessor `ARCHIVE_NOTE.md` used an older Additional-file numbering and is **not** carried over.
- Archive map verified item by item against `Supporting_Information_GenetEpidemiol_20260930.docx` (2026-10-02): every one of the 46 items now carries a status backed by a table title, header, column/row count or an actual cell value. The status key gained a fourth state — 🟡 **DERIVABLE** (inputs present and verified, producing step not shipped) — so that "we hold the inputs" is no longer conflated with "we can reproduce the table".

### Fixed
- `data/derived/s1_anchor_102pairs.csv` and `data/derived/s1_primary_arm_96pairs.csv` were **mis-filed in the authoritative layer**. Their ANXA1/DR values are 1.2913 / 2.1391; the authoritative table has 0.4283 / 0.9302. Their row counts (102, 96) happen to look right, which is how the error survived. Both are v2.5.0-generation output and now sit in `data/superseded/s1_cluster_robustness/`.
- The archive map no longer claims that `figures/` holds the figure files. **The repository contains no figure files** — `figures/` holds only its README; what is shipped is the *scripts* that produce some of the panels.

### Added
- `code/analyses/recovered/` — three scripts recovered from unarchived session working directories, copied verbatim. `tost_ci_calculator.py` and `tost_and_newcombe.py` were **run and reproduce the published values** (Newcombe 90% CI −9.7 to +15.4 for GTEx and −13.3 to +12.6 for eQTLGen; TOST p = 0.181/0.060/0.014 and 0.116/0.034/0.007). `scz_arm_recount_si_fix.py` recomputes from the archived four-arm SCZ table.
- `code/deprecated/si_editors/` — seven `.docx`-patching scripts, also recovered verbatim, with a README explaining the pattern they expose.
- `scripts/collect_provenance.py` — regenerates `metadata/provenance.json`; hashes the 36 files that back a reported number and records the external-input manifest.
- `metadata/provenance.json` rewritten: **36 files hashed**, 8 external inputs with identifiers, versions and the retrieval date from Supporting Information Note S4, and **no placeholders**.
- `data/README.md` external-input manifest filled from Note S4 — every resource **retrieved 2026-09-08**; software versions (official MetaXcan v0.8.1, Python 3.13.0, R 4.5.2 + MatchIt); and the GCST90043640 citation (Jiang et al. *Nat Genet* 2021;53:1616–1621, doi:10.1038/s41588-021-00954-4). External hashes are recorded as `not-held` rather than invented — nothing here claims hash verification that did not happen.

### The finding that matters more than the recovery

Several of the surviving scripts are **not computations at all**. `apply_d2_fixed_threshold.py`, `apply_d3_genomewide_control.py` and `apply_s11_hrt_restricted.py` carry their SI values as **hard-coded English prose literals** and read no data — e.g. `"...reached an FDR enrichment of 69.1% (56/8..."`. The workflow was: compute elsewhere (uncaptured) → paste the numbers into a `.docx`-patching script → write them into the Supporting Information.

So several gaps are **not** "the script got lost". The number was pasted in from something never captured. Searching for a missing script will not close them; the value has to be re-derived. Recorded in `metadata/ARCHIVE_MAP.md` §5.

### Known gaps (declared, not hidden)
- **5 items are marked 🔴** in `metadata/ARCHIVE_MAP.md` as of 2026-10-02: SI Table **S6**, SI Table **S10**, **Figs. S1 and S2**, and the value row of main-text **Table 1**. (This line previously read "9 items" and listed S9, S11, S16, S17, S27, S28 and S29 among them; S9, S16, S17, S27, S28 and S29 are now ✅ — see the 2026-10-02 entry above.) **S7 has moved from 🔴 to 🟡** — its TOST/Newcombe half is now recovered and verified; its "Smallest margin attained" column is not.
- **GAP-1 (SI Table S6) is now diagnosed, and the fault is the repository's, not the Supporting Information's.** The housekeeping Z layer here was computed on **2026-08-30**; the σᵢ correction landed **2026-09-17**. Reading the Table S6 block out of all 93 archived copies of the supplementary file and ordering them by mtime shows the published values changed between 2026-09-16 22:24 and 2026-09-17 19:15 — inside that window. Corroborating: every changed value shrinks |Z| and moves the ACAT-O P toward 0.5; 22 of 30 genes change by a constant per-gene ratio (a per-gene multiplicative correction); the model-SNP column is unchanged for all 30.
  → **`data/derived/hk_reselect/` was moved to `data/superseded/hk_reselect_20260830/`** with a full notice. The housekeeping arm of main-text Table 1 is therefore **not reproducible from this archive**.
- **Still open on GAP-1, and deliberately not closed by assumption:** 8 of 30 genes (`DNAJC4`, `E2F4`, `GOLGA3`, `SDF4`, `SRM`, `TOMM20`, `SPRYD3`, `TUT1`) do **not** follow a constant ratio, and `GOLGA3` flips sign at DPN — a pure σᵢ rescale cannot do that. The corrected computation is not archived anywhere on disk. Because it differs from the archived one by more than the σᵢ factor, SI Tables S7, S19 and S26 — which aggregate the housekeeping arm — should be re-checked against the corrected layer before submission.
- The generating scripts for the missing tables exist on the local disk only inside unarchived session directories (`2026-09-22-14-24-45/work/si_fix.py`, `2026-09-11-19-30-45/apply_d2.py`, `2026-09-11-18-13-13/_apply_edits.py`, …). They are recoverable, but nothing has been copied in yet.

### Numbers
- **No reported number changes.** This commit moves two mis-filed files out of the authoritative layer, corrects documentation, and declares gaps. Every value the manuscript reports is unaffected.

---

## [4.0.0] — 2026-10-02

### Added
- First release of the consolidated archive: analysis scripts, processed derived data, containerised environment, and archived figures.

### Numbers
- **No reported number changes in this release.** This release re-hosts the same analysed content under the canonical repository and updates metadata and repository layout only.

### Migration notes
- History imported from `wu-yijing/twas-eqtl-source-discordance`; predecessor tags were **not** imported, so `v1.0.0`–`v3.0.0` remain only in the archived repositories.
- Cite this study as concept DOI `10.5281/zenodo.23129112`; to refer to one analysed snapshot, cite that
  release's version DOI. It is not fixed at this entry: as of the v4.0.1 deposit it was
  `10.5281/zenodo.23129113`, and the value in force is the one recorded in
  [`metadata/zenodo_release.json`](metadata/zenodo_release.json).

---

[Unreleased]: https://github.com/wu-yijing/eqtl-source-discordance/compare/v4.0.2...HEAD
[4.0.2]: https://github.com/wu-yijing/eqtl-source-discordance/releases/tag/v4.0.2
[4.0.1]: https://github.com/wu-yijing/eqtl-source-discordance/releases/tag/v4.0.1
[4.0.0]: https://github.com/wu-yijing/eqtl-source-discordance/releases/tag/v4.0.0
<!-- v4.0.0 was declared but never tagged; the link above is kept as history and is deliberately dead. -->

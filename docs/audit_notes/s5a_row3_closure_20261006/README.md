# S5a row 3 — the value that looked missing, and where it was

**Date:** 2026-10-06 · **Repository HEAD at the time:** `06a1108`
**Closes:** the one numeric cell of the two submitted documents that
`scripts/audit_documents_vs_repo.py` reported as absent from the archive.

## The finding

Running the auditor against
`Supporting_Information_GenetEpidemiol_20260930_rev8.docx` + `Manuscript_..._rev8.docx`
printed:

```
   S5a     rows 1, 2 and 4 correspond to crosscohort.csv    34 / 35    <-- 1 value(s) not in the archive
             absent: 76.6
```

**76.6 was never missing.** `code/analyses/m6_ne_weighted_sensitivity.py` has computed it
since 2026-10-03 and ships in this repository. What was missing is the *path from the
script to the corpus*:

| Link | State before 2026-10-06 |
|---|---|
| script computes Q = 76.6 | ✅ yes — block **M6(c)** |
| script invoked by `code/run_all.sh` | ❌ no — it was never called by anything |
| output written where a corpus reader looks | ❌ no — it went to `data/superseded/` |
| `audit_documents_vs_repo.py` corpus roots | `data/derived/`, `code/analyses/reproduction_20261002/results/`, `code/figures/` |

`data/superseded/` is the quarantined layer, deliberately excluded from every corpus. So
the number was produced, written, and then placed somewhere no reader looks. The auditor's
verdict was correct about its corpus and wrong about the archive, which is exactly the
failure mode the `Status` / `Input locality` split exists to prevent — a locality claim
("not in the corpus") read as an authenticity claim ("not in the archive").

## What 76.6 is

SI Table S5a row 3, *"√N_e weights applied directly on the Z scale"*, for RNH1 / DR,
k = 2 (FinnGen R13 + UK Biobank GCST90043640, both under eQTLGen weights):

```
Z_FinnGen = +2.31   N_e = 49,304  = 4·15353·62519/77872      (15,353 cases / 62,519 controls)
Z_UKB     = +0.72   N_e =  1,231  = 4·308·456040/456348      (308 cases / 456,040 controls)

w_i = sqrt(N_e)                    ->  222.0450 , 35.0855
pooled  = Σ w·Z / Σ w              ->  +2.0930   (published +2.09)
Q       = Σ w·(Z − pooled)^2       ->   76.5968  (published 76.6)
I^2     = (Q − 1)/Q · 100          ->   98.69 %  (published 98.7)
```

This is **not** the same quantity as row 2. Row 2 is the normalised Stouffer combination
`Σ Z·√N_e / √(Σ N_e)` = +2.39 with Q evaluated on the β scale (0.13, I² = 0%). Same
weights, different scale, opposite heterogeneity verdict — which is the point the row
exists to make, and why the README of both predecessor repositories calls these statistics
"convention-dependent" with an ≈40-fold N_e gap at k = 2.

**76.6 comes from the 2-decimal Z-scores the table itself quotes** (2.31, 0.72), which is
what the SI's own table note declares. From the archived full-precision official Z
(2.3091, 0.7225) the same formula gives **76.27**. Both are printed by the script, because
the difference is input precision, not arithmetic.

## What changed

1. `code/analyses/m6_ne_weighted_sensitivity.py`
   - output moved from `data/superseded/` to
     `code/analyses/reproduction_20261002/results/m6_ne_weighted_sensitivity_results.txt`
     — tracked, and inside a corpus root;
   - new `--self-test` asserts pooled +2.09, Q = 76.6, I² = 98.7 % and exits non-zero on
     any mismatch.
2. `code/run_all.sh` — new step **3b**, runs the script with `--self-test` in every mode
   including `--verify-only`, so the row is checked on every pipeline run rather than
   printable on request.
3. `metadata/ARCHIVE_MAP.md` — S5a moved 🟡 → ✅ (counts 29/9 → 30/8, machine-checked).

## Measured, not argued

```
$ python3 code/analyses/m6_ne_weighted_sensitivity.py --self-test
-- self-test: SI Table S5a row 3, published values --
  [ ok ] pooled Z    got     2.0930   published     2.09
  [ ok ] Cochran Q   got    76.5968   published    76.60
  [ ok ] I^2 (%)     got    98.6945   published    98.70
  self-test: 0 mismatch(es)

$ bash code/run_all.sh --verify-only
== 3b. SI Table S5a row 3 — the sqrt(N_e) direct-weighting row ==
  [ ok ] m6_ne_weighted_sensitivity.py: SI Table S5a row 3 reproduces (+2.09 / Q 76.6 / I² 98.7%)
```

Re-running `scripts/audit_documents_vs_repo.py` now finds 35 / 35.

## Provenance of the numbers, for anyone who wants to check the inputs

`N_e` for both cohorts and the full-precision Z are recorded in three places, all in this
archive: the script docstring, `data/derived/ukb_dr/RNH1_official_metaxcan_Z.csv`, and
`code/analyses/reproduction_20261002/INPUTS.md`. The same computation appears in the two
predecessor repositories as `scripts/python/m6_ne_weighted_sensitivity.py` with output
`data/processed/m6_ne_weighted_sensitivity_results.txt` — that earlier output covers M6(b)
and M6(d) only; the M6(c) block (this row) was added in this repository on 2026-10-03.

## Lesson

A corpus check answers *"is this string somewhere in these directories"*. It cannot
answer *"can this archive produce this number"* unless the producing script is run and its
output lands where the corpus reads. The fix is therefore not to add the number to a file;
it is to run the script, put the output in the corpus, and assert the value — which is
what step 3b now does.

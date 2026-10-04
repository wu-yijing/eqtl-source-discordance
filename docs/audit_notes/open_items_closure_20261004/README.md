# Open-items closure attempt — 2026-10-04

Five items were left open by the two audits of 2026-10-04 (the three-document
reproducibility assessment, and the upstream-chain closure record). This directory is the
result of a full-disk search — including the Recycle Bin — plus the execution that search
made possible.

**Two closed, one half-closed, two closed as "not reproducible, and here is why".** Two of
the five moved in the *un*comfortable direction, and that is stated plainly rather than
rounded off.

| # | Item | Outcome |
|---|---|---|
| 1 | **SI Table S4 / S26** — R 4.5.2 + MatchIt not available | ❌ **Tested and it does NOT reproduce.** The environment *was* available (R 4.5.2 at `D:\R\R-4.5.2`, MatchIt/cobalt/optmatch in the win-library). Six conventions were run; the best matches **2 of 30** control assignments. Root causes measured, see §1. **This contradicts `metadata/ARCHIVE_MAP.md`, which marks S4 ✅ / `clone`.** |
| 2 | **SI Fig. S1 "family-B" generator** | 🟡 **Generator family identified; residual difference localised and explained.** Two independent generator families both emit 3188 × 3076; the published raster is 3189 × 3077. The three-way visual comparison shows the **same flowchart**; the difference is a **different green-box string** plus ~9 % of pixels differing at 1–8 grey levels (font rasterisation). Artefact-level closure was already in-tree and stands. See §2. |
| 3 | **Docs revision registry lags the submitted files** (`[UNRECOGNISED]`) | ✅ **Closed.** `paths_config.py` now registers manuscript rev5/rev6/rev7 and SI rev1_dates / rev1_dates_minimal / rev3 / rev4 / rev5. Verified: `[UNRECOGNISED]` → `[ok]` with the revision named. See §3. |
| 4 | **SI rev5 layout regression** (19 → 25 parts; `tblPrEx` 2,160 → 0) | ✅ **Structure restored.** Rebuilt from rev4's package with rev5's two content edits: 19 parts, `tblPrEx` 2,160, `tblCellPr`-family counts back to rev4's, and **text identical to rev5**. See §4. |
| 5 | **SI rev5 has no PDF** | ❌ **Blocked by environment, not by the file.** WPS Office is installed (`E:\Program Files\WPS Office`) but **COM automation is refused by this machine's security policy**, and no LibreOffice/Word/pandoc is present. The render must be done on a machine where Word/WPS automation is permitted. |

---

## 1. SI Table S4 / S26 — tested; it does not reproduce

### 1.1 The environment was available after all

A full-disk search found what the earlier audit recorded as absent:

| Component | Found at | Version | `env/renv.lock` pins |
|---|---|---|---|
| R | `D:\R\R-4.5.2\bin\Rscript.exe` | **4.5.2** | 4.5.2 ✅ |
| `MatchIt` | `<user-library>\MatchIt` | **4.7.2** | 4.5.5 ❌ |
| `cobalt` | same library | **5.0.0** | 4.5.2 ❌ |
| `optmatch` | same library | **0.10.8** | 0.10.6 ❌ |
| Rtools | present (`pkgbuild::has_build_tools()` → TRUE) | — | — |

So the earlier "需 R 4.5.2 + MatchIt，本批资料不含" was **wrong in the first half and right in
the second**: R matches exactly; the three packages are present but **three to two minor
versions above the lock file**.

### 1.2 What was run

`data/superseded/mahalanobis_matched_pairs.csv` is the archived S4 (60 rows = 30 pairs) and
itself states it is "identical to those in Supporting Information Table S4". Six conventions
were run against it, all from shipped inputs:

| # | Pool | eQTL SNP missing-value rule | `m.order` | Pairs | Control assignments matching the archive |
|---|---|---|---|---|---|
| 1 | 74 (Non-Candidate + T2DM Control, as the shipped `.R` builds it) | group-median impute | default | 30 | **1 / 30** |
| 2 | 44 (`Non-Candidate` only) | group-median impute | default | 30 | **1 / 30** |
| 3 | 44 | `na.omit` (the shipped script's Section 2) | default | 27 | **0 / 27** |
| 4 | 54 (the producer's own pool, see §1.3) | group-median impute | default | 30 | **1 / 30** |
| 5 | 44 | group-median impute | `data` | 30 | **1 / 30** |
| 6 | 44 | group-median impute | `random` | 30 | **2 / 30** |

**The imputation convention is confirmed, not guessed.** Running it reproduces the archive's
own NOTE to the digit: 3 of 30 candidates imputed at median 1.5, 17 of 44 pool genes at 1.5,
11 of 30 T2DM controls at 1.0 — exactly the counts `code/analyses/run_mahalanobis_matching.R`
discloses. That part of the recipe is right; the match still does not land.

### 1.3 Three concrete defects measured

1. **The shipped script builds the wrong pool.** `run_mahalanobis_matching.R` Section 2 takes
   `covar$Group != "Candidate"` — which includes the 30 T2DM controls, giving 74. The
   archived table uses **only** the `44 Non-Candidate` group: all 30 archived controls carry
   that label and **not one** T2DM control appears. A shipped script that cannot produce the
   shipped result in either direction.
2. **The shipped covariate matrix is not the producer's input.** `data/derived/covariate_matrix.csv`
   has **44** non-candidates; the producer's own
   `Table_S1_Covariate_Matrix_FINAL_v2.csv` (found in the working directory, 2026-06-25) has
   **54**. The 10 extra genes are `H2AJ, H3-7, RPL13, RPL17, RPL7A, RPS10P5, SERPINH1, TPM4,
   TUBB4B, VAT1`. The archived control set is a subset of the 44, so the pool *sizes* differ
   even though the *chosen* genes do not — and Mahalanobis nearest-neighbour is a global
   greedy assignment, so a larger pool changes the answer.
3. **The covariate values themselves agree.** Every `log10_Length`, `Length_bp` and `GC_pct`
   in the archived pairs matches the shipped matrix exactly (0 discrepancies over 60 rows × 3
   columns); the only apparent mismatches are the 13 rows whose `eQTL_SNPs_Mean` is blank in
   the shipped matrix and 1.5 in the archive — i.e. the imputation, as expected. **So the
   inputs are right and the algorithm is what differs.**

The remaining single explanation consistent with all of the above was the `MatchIt` version
(4.7.2 installed vs 4.5.5 locked): `distance = "mahalanobis"` handling changed in the 4.6
line. Installing 4.5.5 from the CRAN archive requires compiling against Rtools; a source
install was started here and did not complete inside this session's budget, so at the time
this note was written the version effect was **narrowed, not yet measured**.

> ✅ **Measured the same day, and it is nil — this explanation is falsified.** MatchIt 4.5.5 was
> compiled from the CRAN archive (Rtools 45 / GCC 14.3.0) and the same script, inputs and 18
> conventions were run under both versions. **18 of 18 conventions give an identical result,
> down to the per-pair mismatch strings**, and both best-match the archive at **2 of 30**. The
> divergence was then localised: the archived control is the candidate's Mahalanobis nearest
> neighbour in only **3 of 30** pairs (median rank **14 of 44**; best across 7 covariate subsets
> × 3 covariance conventions is 11/30 on the eQTL-SNP count alone). See
> [`../s4_matchit_version_test_20261004/`](../s4_matchit_version_test_20261004/README.md).
> `MASS`-based `matchit(distance = …)` variants were not exhausted; the distance diagnostic
> covers the specification space that was.

### 1.4 A second, independent discrepancy

The working directory holds `Table_S2_Matched_Controls.csv` (2026-06-25), a *third* matched
set: same 30 candidates, but **six different controls** —
`ATP5F1B, RPL13, RPL17, RPL7A, TPM4, TUBB4B` where the archived set has
`CCT3, GNA13, HNRNPK, MSN, PDIA3, UBA52`. So the match has been computed at least twice with
different results, and the archive ships the later one. Any closure of S4 has to name which
run the manuscript reports.

### 1.5 S26

S26 is **SI Table 27** ("Mahalanobis-matched enrichment contrasts"), whose four rows include
the two values `2/84 vs 1/60 → P = 1.00` and `5/81 vs 0/57 → P = 0.077`. Its inputs are the
matched pairs plus `data/derived/{gtex,eqtlgen}_Z.csv`, and both are shipped — but the
**matched-control denominators (60 and 57) are not derivable from the 30 pairs**, so the
contingency's construction is not documented anywhere in the archive. `ARCHIVE_MAP.md` records
it as 🟡 and that assessment stands; reproducing S4 first is a precondition.

### 1.6 Scripts

`reproduce_S4_pool44.R` (pool = 44, both imputation conventions, plus the 74-gene pool the
shipped script builds, for contrast) and `reproduce_S4_pool54.R` (the producer's 54-gene pool)
are shipped here so the negative result is checkable rather than asserted. Run with
`D:\R\R-4.5.2\bin\Rscript.exe`.

---

## 2. SI Fig. S1 — the generator family is identified

### 2.1 What was found

Two independent generators of the same flowchart:

| Generator | Found at | `figure2()` output |
|---|---|---|
| `rebuild_fig1_2_9.py` (in-tree, `code/figures/recovered/` and `ge_si/`) | repository | 3188 × 3076 RGB |
| `make_main_figures.py` (2026-08-31 working directory) | `E:\workbuddy\2026-08-31-19-21-52\_build\` | 3188 × 3076 RGBA |
| earlier draft `_genfig_s1.py` (2026-09-13) | working directory | 1816 × 2062 — a different layout, an earlier take |

Both live generators were **run here** under the pinned matplotlib 3.10.8 and both emit
**3188 × 3076**. The published raster is **3189 × 3077 RGB**.

### 2.2 The three-way visual comparison settles the design question

`figs1/design_comparison.png` puts, left to right, the re-run, the published pre-patch raster,
and the published raster. **All three are the same flowchart, box for box, arrow for arrow.**
The only textual difference is the green `> 75 %` box:

| | green-box text |
|---|---|
| generator (both families) as found | `Broadly consistent with the genome-wide expectation` |
| published (both rasters) | `Above the genome-wide 95% band (66.1-68.2%) - treat as robust` |

That string is a **parameter, not a different program** — `redraw_figS1_guard.py`
(2026-09-23) already carries it as a `GREEN_TEXT` variant, with the `baseline` value being
exactly the published sentence.

### 2.3 Why it still does not land, and what was ruled out

The generator is now reusable — `figs1/gen_figS1.py` is the drawing code, verbatim from the
recovered generator, with the two strings the audit found to vary promoted to parameters and
the working-directory dependencies removed. Every axis that could plausibly explain the
residual was then tested and **eliminated**:

| Test | Result |
|---|---|
| Candidate vs `FigS1_pre_patch.png`, cropped to the smaller size | **9.42 %** of pixels differ |
| ±3 px translation search (49 offsets), best = (dy = +1, dx = 0) | **9.3792 %** — no offset helps |
| `font.sans-serif = Arial` (the recovered style file's first choice) | **9.3792 %** |
| `font.sans-serif = DejaVu Sans` | 11.2880 % — **worse**, so the published run resolved Arial |
| matplotlib **3.10.8** (this archive's pin) | **9.3792 %** |
| matplotlib **3.10.9** (the version the submitted GE figures were drawn with) | **9.3792 % — identical to the byte** |
| Resampling to 3189 × 3077, 6 filters (NEAREST / BILINEAR / BICUBIC / LANCZOS / BOX / HAMMING) | 9.71 – 12.51 %, none an improvement |
| 1-px white pad on each of the four corners | 9.42 – 10.25 %, none an improvement |
| Difference amplitude (best offset) | **687,672** px differ by only **1–8** grey levels; 232,084 by more than 8; 123,924 by more than 64 |
| Spread | 2,857 of 3,076 rows and 2,941 of 3,188 columns contain at least one differing pixel |

Two alternative renderings of the **same** drawing code are emitted by `figs1/gen_figS1.py`
and shipped here — `rerun_published_greentext.png` (the published box wording) and
`rerun_legacy_greentext.png` (the wording both recovered generators contain). The published
wording lowers the difference from 9.7526 % to 9.3792 %, which is consistent with it being
the right string, but does not close the gap.

**Conclusion, at the boundary of what was measured.** The published Fig. S1 is the **same
figure** produced by the **same code family**, and the generator is no longer missing — it is
one file, parameterised, in this directory. What is *not* reproduced is a whole-canvas,
low-amplitude text-rasterisation difference (three quarters of the differing pixels differ by
1–8 grey levels) which is invariant across matplotlib version, font family, resampling filter
and translation. Since every in-session axis is exhausted, the surviving explanation is a
**different text-rasterisation build** on the machine that produced the published raster
(FreeType or Arial version). This is a font-pinning problem, not a lost-generator problem, and
it does not disturb the artefact-level closure (`ge_si/published/` + `verify_published.py`,
0 px differ), which remains the operative path.

---

## 3. Documentation registry — closed

`code/analyses/reproduction_20261002/paths_config.py`'s `DOCS[...]['revisions']` now carries
every revision on disk:

| Document | Revisions registered |
|---|---|
| `manuscript` | pre-`[39]`-repoint · as-submitted 2026-09-30 (**produced `results/`**) · rev2 · rev3 · rev4 · **rev5** · **rev6** · **rev7** |
| `si` | as-submitted 2026-09-30 (**produced `results/`**) · rev2 · **rev1_dates** · **rev1_dates_minimal** · **rev3** · **rev4** · **rev5** |

`doc()`'s `md5`/`bytes` hint now points at the newest revision (rev7 / rev5). Verified:

```
[ok] manuscript  revision 2026-10-04 (rev7: [39] carrier -> Zenodo) [md5 27e9bf5cbf37…, 31,190 bytes]
[ok] si          revision 2026-10-04 (rev5: Note S4 Z value + S24 convention) [md5 393d2399a8be…, 1,561,171 bytes]
```

The two revisions that produced the archived `results/` keep `outcome=True`, so the
"produced `results/`" statement is unchanged. Code-side comments record what each new
revision changed, and that **rev5 is the only one whose change is content, not identifiers**.

---

## 4. SI rev5 layout regression — structure restored

The regression, measured: package parts **19 → 25**, `word/document.xml` **−593 KB**,
`w:tblPrEx` **2,160 → 0**, `w:tblCellMar` 2,220 → 62, `w:tblBorders` 2,222 → 62, while
`styles.xml` is identical — i.e. cell-level property exceptions were **dropped**, not moved
into styles. Exactly the damage this project's own record describes for the editor channel.

`tools/rebuild_SI_rev5_structure.py` re-applies rev5's **two text edits** to rev4's
**package**:

1. `median minimum absolute Z = 1.24 versus` → `= 0.672 versus` (anchored uniquely; rev4 also
   contains a legitimate `1.246` table value)
2. the `numpy.sign` zero-value sentence inserted as a new run after
   `no gene-level clustering applies.`

Result — `Supporting_Information_GenetEpidemiol_20260930_rev6.docx`:

| | rev4 | **rev6 (new)** | rev5 |
|---|---|---|---|
| package parts | 19 | **19** | 25 |
| `w:tblPrEx` | 2,160 | **2,160** | 0 |
| `w:tblCellMar` | 2,220 | **2,220** | 62 |
| `w:tblBorders` | 2,222 | **2,222** | 62 |
| `w:insideH` | 8,722 | **8,722** | 7,642 |
| bytes | 1,463,254 | **1,463,543** | 1,561,171 |
| **text vs rev5** | — | **identical** | — |

- Only `word/document.xml` was rewritten; **every other part is byte-identical to rev4**
  (same name, compression method, timestamp, attributes), so the `docProps/` and `word/theme/`
  parts the editor channel had rebuilt are gone.
- `md5 5baf40f0fbba2fb1d50367bdc7fecb85`, `sha256 da8d464bc686b2b0f6b2259dadac7b3d1449337ea992ed35f668197823538269`, 1,463,543 B.

**Not done: the PDF.** WPS Office is installed but COM instantiation is refused by this
machine's security policy, and no LibreOffice / Word / pandoc exists. The render — and the
page-count and per-page character comparison that would follow it — needs an environment where
Word or WPS automation is permitted.

---

## 5. File inventory — what is here, which stage it belongs to, and whether it was verified

Every file below was produced **in this environment**, and every verification claim is
re-runnable from this directory. `MANIFEST.sha256` covers all of them.

| File | Analysis stage | What it is | Verification status |
|---|---|---|---|
| `README.md` | — | This report | — |
| `MANIFEST.sha256` | — | SHA-256 of every file here | Self-check by `sha256sum -c` |
| **`figs1/gen_figS1.py`** | ② Fig. S1 render | Self-contained generator: the recovered `figure2()` verbatim, both varying strings promoted to parameters, working-directory dependencies removed | ✅ **Runs**; emits 3188 × 3076 under matplotlib 3.10.8 **and** 3.10.9 (identical bytes) |
| `figs1/verify_figs1.py` | ② verification | Reproduces every number in §2.3: sizes, best-offset difference, amplitude histogram, row/column spread | ✅ **Runs** (Pillow + numpy; finds `ge_si/published/` by walking up) |
| `figs1/figs1_verification.json` | ② verification | Those numbers, machine-readable | ✅ Recorded output |
| `figs1/rerun_published_greentext.png` | ② intermediate | The generator run with the published `> 75 %` box wording — 3188 × 3076 | ✅ 9.3792 % vs published |
| `figs1/rerun_legacy_greentext.png` | ② intermediate | The generator run with the wording both recovered generators contain — 3188 × 3076 | ✅ 9.7526 % vs published |
| `figs1/design_comparison.png` | ② evidence image | Three-way: re-run ‖ published pre-patch ‖ published — shows the *same* flowchart | ✅ Visual |
| `figs1/pixel_difference_map.png` | ② evidence image | Re-run ‖ difference map — shows whole-canvas, low-amplitude | ✅ Visual |
| **`si_structure/rebuild_SI_rev5_structure.py`** | ④ SI structure | Re-applies the later revision's **two text edits** to the earlier revision's **package** | ✅ Runs; anchors asserted unique |
| `si_structure/verify_SI_structure.py` | ④ verification | Part count, `tblPrEx` / `tblCellMar` / `tblBorders` / `insideH`, `styles.xml` unchanged, and text equality | ✅ **Runs** (stdlib + python-docx) |
| `si_structure/si_structure_verification.json` | ④ verification | The recorded measurements and the three pass/fail checks | ✅ All three `True` |
| **`registry/check_doc_revision.py`** | ③ registry | Read-only: ask the reproduction package which revision a given `.docx` is | ✅ **Runs**; prints `[ok]` + the revision name |
| `registry/registry_verification.txt` | ③ verification | Before/after transcript, plus a control pair and one caveat found while writing it | ✅ Recorded transcript |
| `s4/reproduce_S4_pool44.R` | ① S4 | Pool = 44 (what the archived table implies) × both imputation rules × the shipped script's 74-gene pool | ✅ **Runs**; best 2/30 |
| `s4/reproduce_S4_pool54.R` | ① S4 | The producer's 54-gene pool, with and without a seed | ✅ **Runs**; best 1/30 |
| `s4/reproduce_S4_pool74.R` | ① S4 | Pool = 74 with group-median imputation | ✅ **Runs**; 1/30 |

**Deliberately not here.** `Supporting_Information_GenetEpidemiol_20260930_rev6.docx` — the
output of the rebuild in `si_structure/` — is **not** pushed. `docs/audit_notes/INDEX.md`
states as a standing rule that *no `.docx` manuscript or supplementary file is distributed
with this repository*, and a revision of a document under submission is exactly the kind of
file that rule exists for. The rebuild is fully reproducible without it: the script plus the
two prior revisions the author holds give a byte-identical result, and
`si_structure/si_structure_verification.json` records the checks. If it is ever wanted here,
say so and it is one `git add`.

## 6. Directory layout after the push

```
docs/audit_notes/open_items_closure_20261004/
├── README.md                            report + the file/status inventory above
├── MANIFEST.sha256                      SHA-256 of all 16 files
├── figs1/      (item ②)  generator + verifier + JSON + 4 PNGs
├── si_structure/ (item ④)  rebuild tool + verifier + JSON
├── registry/   (item ③)  revision checker + before/after transcript
└── s4/         (item ①)  3 reproduction scripts
```

## 7. Honest summary

Two of the five open items were **closed** (registry; SI structure), two were **closed in the
negative** (S4/S26 does not reproduce and `ARCHIVE_MAP.md` over-claims it; Fig. S1's residual
is a font-rasterisation build, not a missing generator), and one is **blocked by this
machine's policy** (the SI PDF render). The S4 result is the most consequential: a table the
archive marks ✅ / "a fresh clone re-runs it end to end" **does not re-run**, and three
distinct defects in the shipped path were measured rather than suspected.

## Note on the elision in `the `MatchIt` row of the environment table` (2026-10-04)

Some paths in that table cell were replaced by placeholders: `<user-library>` for an R user library
on the author's machine, `<temp-workdir>` for a scratch directory used to hold a clone
during an audit, and `<user-home>` for the compiler's 8.3 short form of the same account
name. The names of the account and the machine are not evidence for anything these files
are cited to show — the versions and the resolved components are, and those are untouched.
Nothing else in the files was edited. The substitution is scripted and counted in the
2026-10-04 CHANGELOG entry, so it is reproducible rather than a hand edit.

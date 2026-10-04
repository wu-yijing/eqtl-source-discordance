# Which matched set does the manuscript report? — 2026-10-04

## The question, and the answer

`../s4_specification_sweep_20261004/` closed SI Table S4 down to one open item: *which* of the
matched sets on disk the manuscript reports. It is answered here, **from the manuscript's own
numbers rather than from anyone's recollection or from the prose that describes the runs.**

The Genetic Epidemiology manuscript states the GTEx arm of the covariate-matched contrast as

> "Covariate-matched enrichment (Table S26) showed no candidate-over-control difference in the
> GTEx arm after matching on gene length, GC content and eQTL SNP count (**2.4% versus 1.7%;
> P = 1.00**), and a …"

Recomputing Table S26's contingency under each candidate control set separates them:

| set | where it is | control-set overlap with A | GTEx: candidate | GTEx: matched control | Fisher P | is it what the manuscript reports? |
|---|---|---|---|---|---|---|
| **A** archived pairing, shipped as SI Table S4 | `data/superseded/mahalanobis_matched_pairs.csv` | — | 2/84 = **2.4%** | 1/60 = **1.7%** | **1.00** | **yes — all three figures** |
| B 2026-06-25 run, 54-gene pool | `results/matched_set_20260625_pool54.csv` | 24 / 30 | 2/84 = 2.4% | 0/48 = **0.0%** | **0.53** | no |
| C 2026-06-29 run, genome-scale pool | `results/matched_set_20260629_genomescale.csv` | 0 / 30 | 2/84 = 2.4% | — | — | no — **not one of its 30 controls carries a GTEx endpoint**, so it cannot produce the sentence at all |

`scripts/identify_reported_matching.py` reproduces that table from a clone; its output is
`results/reported_run_identification.txt`. **Set A is the one the paper reports.** Everything
below is about what that implies.

## What A is, and what produced it

- **A is the artifact of the 2026-06-27 predecessor repository.** It is **byte-identical** to
  `TWAS-eQTL-source-confounding/data/processed/mahalanobis_matched_pairs.csv`
  — md5 `e047ec426303a98bc939c270ecd5e44f`, sha256 `636908dc7e99e9b0…` — so its lineage is that
  repository, not the 2026-06-25 working directory and not the 2026-06-29 one.
- **No command that produces A is recorded.** The two surviving prose descriptions of the
  matching that are filed next to A describe a *different* pool: `analyses/logs/04_mahalanobis_matching_log.txt`
  says the control arm came from "background genes from GTEx (full set of ~3,500+ potential
  controls) … Excluded: genes in candidate or non-candidate groups", and
  `analyses/logs/00_master_provenance.txt` repeats it ("Match 30 candidate genes from
  full-genome pool"). That is set **C**'s design. **A's 30 controls are all `44 Non-Candidate`
  genes**, which a pool that excludes the non-candidate group cannot select. So the two
  documents that look like A's provenance describe the run whose output is C.
- **The shipped generator cannot produce A either.** `code/analyses/run_mahalanobis_matching.R`
  — and its 2026-06-27 ancestor, which is where the defect comes from — selects the treated arm
  with `Group == "Candidate"`, a label the 104-row covariate matrix does not contain (its groups
  are `30 HOTAIR Candidate`, `44 Non-Candidate`, `30 T2DM Control`), and builds its pool as
  `Group != "Candidate"` = 74 genes. Against today's matrix that yields **0 treated**.
- **What A's control set *is* reproducible by** is the documented specification: pool = the 44
  `Non-Candidate` genes, `method = "nearest"`, `distance = "mahalanobis"`, ratio 1, no
  replacement, group-median imputation, MatchIt 4.5.5, candidates processed in the submitted
  table's own order — **30 of 30 controls**, with every other order tested reaching 27–29. See
  `../s4_specification_sweep_20261004/`. What that run does *not* reproduce is A's `subclass`
  column, which is a `PullDown_Unused`-descending rank-zip rather than a matching output.

## What the manuscript says about the matching

Worth recording because it is narrower than the earlier audits assumed:

- The **Genetic Epidemiology** manuscript never cites Table S4. It cites the *contrast* (Table
  S26), names the three matching covariates, and **names no pool** — the "pool of 44
  high-confidence non-candidate genes" sentence belongs to the **BMC Genomics** manuscript, and
  is not in this one. The reported sentence is reproduced by set A and only by set A.
- A's numbers surviving the re-emitted Table S4 (`../s4_specification_sweep_20261004/`) is what
  makes the S4 re-emission safe: the re-emitted pairing selects the *same 30 controls*, so the
  manuscript's 2.4% / 1.7% / P = 1.00 are untouched.

## The three sets, and why they differ

| | produced | pool the README/logs claim | controls actually selected | vs A |
|---|---|---|---|---|
| B | 2026-06-25, `run_matchit.R`, `Table_S2_Matched_Controls.csv` | 54 non-candidates (`noncand_54` is written out in the script) | 6 controls come from the 10 genes the 44-gene matrix does not have (`ATP5F1B`, `RPL13`, `RPL17`, `RPL7A`, `TPM4`, `TUBB4B`) | 24/30 |
| C | 2026-06-29, shipped as that era's `TableS5` | ~3,500 genome-wide, non-candidates excluded | `RP11-134O21.1`, `ZNF500`, `MVK`, `SPPL2A`, `AARS2`, `SLC35E4`, … — none in the 104-gene matrix | 0/30 |
| **A** | 2026-06-27 lineage; **shipped as SI Table S4** | *no surviving description of this run* | all 30 are `44 Non-Candidate` genes | — |

Two details in B and C that a reader will otherwise trip over:

- **B's control arm is labelled `30_T2DM_Control_Matched`** (and its header comment says the same),
  but the script selects the controls from `noncand_54`, not from T2DM controls. The label is a
  leftover from the study's intended design and is wrong about the contents.
- **C has no GTEx endpoint on its control arm at all** — its controls are outside the TWAS panel —
  which is why it cannot express Table S26's GTEx contrast, and why "the denominators cannot be
  derived" reasoning could never have been about C.

## What is closed, and what is not

- **Closed:** which set the manuscript reports, and by its numbers rather than by attribution.
  A's *control set* is reproducible by the documented specification (30/30), which is what the
  re-emitted SI Table S4 records; the two rival sets are excluded by measurement.
- **Still open, and now precisely scoped:** **what ran to produce A's `subclass` column.** A real
  matching selected those 30 controls; something then sorted both arms by `PullDown_Unused`
  descending and numbered the result 1..30. Nothing on disk records that step, and the login
  dir is gone. That is an attribution question about one column of one table, not a
  reproducibility question about the paper — and it is why the re-emitted table ships instead of
  a claim that A was reconstructed.

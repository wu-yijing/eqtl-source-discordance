# PRE_REGISTRATION — pre-specification anchors

This file records exactly which decisions were fixed **before** the analyses were run, and the commits that evidence it. It exists so that a reader can verify the manuscript's use of the word "pre-specified" without leaving this repository.

**Sense of "pre-specified" used here (and in the manuscript):** *repository-timestamped, not registry-registered* — the decision was committed to version control before the analysis was executed, and the commit is retained in this repository. It was not deposited in a clinical-trial-style registry.

---

## 1. Verification (run these first)

```bash
git cat-file -t 58da15b    # -> commit
git cat-file -t e70806b    # -> commit
git log -1 --date=iso --format='%h %ad %s' 58da15b
git log -1 --date=iso --format='%h %ad %s' e70806b
git merge-base --is-ancestor 58da15b HEAD && echo reachable
git merge-base --is-ancestor e70806b HEAD && echo reachable
```

If any of these fails, the archive no longer supports the manuscript's pre-specification claim and that claim must be withdrawn — not merely reworded.

> **Why this file is necessary.** In the predecessor arrangement the two commit identifiers were printed in the Supporting Information (Table S14, items 1c and 5a) while the only repository URL given anywhere in the submission pointed to a *different* repository that does not contain those commits. A reader following the citation could not locate them. Keeping the anchors here, in the same tree as the code, closes that gap.

---

## 2. Anchors

| Anchor | Commit | Date | What it pins |
|---|---|---|---|
| **A1** | `58da15b` | 2026-07-24 | The eQTL weight-source pair and the analysis design: GTEx v8 (MASHR, multi-tissue) versus eQTLGen whole blood, applied through S-PrediXcan with the GWAS input and pipeline held fixed. |
| **A2** | `e70806b` | 2026-09-10 | The decision thresholds: the **±15-percentage-point margin** for reading the candidate-versus-control enrichment contrast, and the comparison it applies to. |

Manuscript cross-references: Supporting Information Table S14 items **1c** and **5a**; Methods, *The HOTAIR testbed* and *Multiplicity and evidence grading*; Limitations.

---

## 3. Explicitly **not** pre-specified

Recording this is as important as recording the anchors above.

| Decision | Status | Note |
|---|---|---|
| The **0.10 margin in ρ** for the two-axis separability reading | **Post hoc** | Derived after the analyses were run; declared as such in the manuscript. |
| The three **disease-agnostic control layers** as finally constituted | Post hoc refinement | The *requirement* for disease-agnostic calibration is pre-specified; the specific layers and their final composition were fixed during analysis. |
| The genome-wide schizophrenia benchmark arm set | **Post hoc** | Added as an independent-trait generalisation check, not registered in advance. |
| The Mahalanobis-matched enrichment contrast (Tables S4 / S26) | **Post hoc** | Introduced at revision. |
| The three simulation experiments (Tables S27–S29) | **Post hoc verification** | Designed to test the inferential machinery the conclusions rest on; their seeds are recorded in the script headers. |

---

## 4. Change control

- **Never rewrite history.** These commits are audit anchors; `git push --force`, rebase and history rewriting are prohibited on any branch reachable from them.
- New pre-specified decisions are recorded by adding a row to §2 with the new commit and date. Do not edit an existing row.
- If an anchor ever becomes unreachable, add a `⚠️ BROKEN` row and open an issue — do not silently remove it.

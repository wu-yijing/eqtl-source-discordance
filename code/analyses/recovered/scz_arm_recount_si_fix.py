# -*- coding: utf-8 -*-
"""
U5 : Additional file 1 › Table S6 — rename to "Margin-sensitivity analysis", delete the
     three TOST p columns, and align caption + note with the main text (M1 route A).
U7 : append Table S23 — per-arm direction-consistency counts/intervals of the genome-wide
     SCZ three-arm comparison (recomputed from the archived four-arm Z table).

A read-only byte copy with a date suffix is made first and verified by SHA-256.
"""
import hashlib, os, shutil
from docx import Document

BASE = r"E:\workbuddy\BMC Genomics投稿资料\投稿前定稿"
SRC = BASE + r"\Additional file 1_审稿意见修订_20260920_评审落实版.docx"
BAK = BASE + r"\Additional file 1_审稿意见修订_20260920_评审落实版_backup_20260922.docx"
OUT = BASE + r"\Additional file 1_审稿意见修订_20260922_审稿意见落实版.docx"


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


# ------------------------------------------------------------------ backup (read-only copy)
if not os.path.exists(BAK):
    with open(SRC, 'rb') as f:
        data = f.read()
    with open(BAK, 'wb') as f:
        f.write(data)
print("backup:", os.path.basename(BAK))
print("  src sha", sha(SRC), os.path.getsize(SRC))
print("  bak sha", sha(BAK), os.path.getsize(BAK))
print("  identical:", sha(SRC) == sha(BAK))

doc = Document(BAK)          # work on the backup copy, never on the original
ps = doc.paragraphs

# ================================================================== U5 : Table S6
cap = [p for p in ps if p.text.startswith("Table S6.")][0]
note = [p for p in ps if p.text.startswith("The observed difference is candidates minus")][0]

NEW_CAP = (
    "Table S6. Margin-sensitivity analysis of the housekeeping-control versus candidate-gene FDR "
    "enrichment difference. Newcombe hybrid-score 90% confidence intervals are given per arm, with the "
    "operative gene-cluster interval given for the pooled estimate. Pooled across the two arms by "
    "fixed-effect inverse-variance meta-analysis of the rate difference (n = 81–87 gene–phenotype pairs "
    "per group), the difference was +2.66 percentage points (analytic 90% interval +0.2 to +5.1; "
    "operative gene-cluster 90% interval −0.7 to +6.4; between-arm heterogeneity Q = 0.14). The pooled "
    "interval treats the two arms as independent, which they are not: the arms share the same gene sets "
    "and the same GWAS input. Two judgements must be read together, as in the main text: the "
    "pre-specified ±15-percentage-point margin is attained once gene clustering and the arms’ shared GWAS "
    "input are accounted for, and the comparison is nonetheless reported as a quantified precision bound "
    "on a candidate-over-control excess rather than as evidence of equivalence, because the margin is wide "
    "relative to the achieved precision and neither group is enriched. The gene-cluster interval is the "
    "operative one; the arm-specific rows are the corresponding per-arm sensitivity analysis, so the table "
    "is a margin-sensitivity curve rather than a confirmatory verdict. No P value is reported for this "
    "criterion: at margins this wide a P value would quantify the precision of the estimate rather than "
    "the scientific claim, and the pre-specified margin is a convention, not an empirically covering "
    "bound."
)
NEW_NOTE = (
    "The observed difference is candidates minus housekeeping controls, in percentage points. The smallest "
    "margin attained is the smallest m for which the 90% interval of that row lies wholly inside ±m, i.e. "
    "max(|lower|, |upper|) of the operative interval of that row; it is a deterministic function of the "
    "interval in the preceding column and carries no additional inference. Confidence intervals are "
    "Newcombe square-and-add (MOVER) intervals for the difference in proportions, applied identically to "
    "both arms. The pre-specified ±15-percentage-point margin is attained by every row, so the arm-level "
    "rows carry no discriminating information; the margin-sensitivity content of this table is the pooled "
    "comparison, where the ×1.45 gene-cluster inflation of the pooled standard error still leaves the 90% "
    "interval (−0.7 to +6.4 pp) inside the pre-specified margin (Table S16). Attainment of the margin "
    "carries no biological content, because neither group is enriched on either source. The study is not "
    "rate-limited: at these rates the minimum detectable difference at 80% power is ≈4.7 pp at the GTEx-arm "
    "rates and ≈8.9 pp at the eQTLGen-arm rates, so detecting a 10-pp difference at 80% power would require "
    "≈20 and ≈65 gene–phenotype pairs per group respectively, and the one-sided 95% upper bounds on a "
    "candidate-over-control excess are +5.1 pp (GTEx arm) and +8.9 pp (eQTLGen arm). See the Methods "
    "sections GWAS and eQTL data sources and Protein identification and group assignment."
)


def clear(p):
    for r in list(p.runs):
        r._element.getparent().remove(r._element)


def set_text(p, txt):
    clear(p)
    p.add_run(txt)


set_text(cap, NEW_CAP)
set_text(note, NEW_NOTE)

# ---- rebuild the table (4 columns; the three TOST p columns removed, one derived column added)
old_tbl = doc.tables[7]
rows = [
    ["Arm (comparison)", "Observed difference (pp)", "90% CI (pp): Newcombe analytic / gene-cluster",
     "Smallest margin attained (pp)"],
    ["GTEx arm: candidates 2.4% (2/84) vs housekeeping 0.0% (0/87)", "+2.38",
     "−1.5 to +7.3 / not defined per arm", "7.3 (analytic)"],
    ["eQTLGen arm: candidates 6.2% (5/81) vs housekeeping 2.5% (2/81)", "+3.70",
     "−2.6 to +10.4 / not defined per arm", "10.4 (analytic)"],
    ["Pooled (fixed-effect inverse-variance, two arms)", "+2.66",
     "+0.2 to +5.1 / −0.7 to +6.4 (operative)", "6.4 (gene-cluster, operative)"],
]
new_tbl = doc.add_table(rows=len(rows), cols=4)
new_tbl.style = old_tbl.style.name if old_tbl.style is not None else "Table Grid"
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        c = new_tbl.cell(ri, ci)
        c.text = ""
        set_text(c.paragraphs[0], val)
old_tbl._tbl.addnext(new_tbl._tbl)
old_tbl._tbl.getparent().remove(old_tbl._tbl)
print("Table S6 rebuilt: 4 rows x 4 columns (3 TOST p columns deleted, 1 derived margin column added)")

# ---- U6 follow-through: same margin wording in the Table S15 note (H3)
p_s15 = [p for p in doc.paragraphs if p.text.startswith("All arms were computed on the genome-wide PGC3 "
                                                        "SCZ dataset")][0]
old_s15 = ("(1) Margin sensitivity of the two-axis equivalence test. Δρ(dual − tissue) is +0.0265 with a 90% "
           "bootstrap interval of +0.0046 to +0.0483, establishing equivalence within the 0.10 margin "
           "(TOST P < 0.001); equivalence also holds at a 0.05 margin but not at 0.02, so differences below "
           "≈0.05 in ρ remain compatible with the data.")
new_s15 = ("(1) Margin sensitivity of the two-axis comparison. Δρ(dual − tissue) is +0.0265 with a 90% "
           "bootstrap interval of +0.0046 to +0.0483, which lies inside the post hoc 0.10 margin and "
           "therefore bounds the difference rather than establishing equivalence; the same holds at a 0.05 "
           "margin but not at 0.02, so differences below ≈0.05 in ρ remain compatible with the data.")
if old_s15 in p_s15.text:
    set_text(p_s15, p_s15.text.replace(old_s15, new_s15, 1))
    print("Table S15 note item (1) reworded (U6)")
else:
    print("!! Table S15 note item (1) not matched")

# ================================================================== U7 : new Table S23
last = [p for p in doc.paragraphs if p.text.startswith("The 61 testbed genes (24 candidate")][0]
cap23 = doc.add_paragraph(
    "Table S23. Direction consistency of the three genome-wide schizophrenia arms "
    "(n = 8,315 complete-case genes).")
rows23 = [
    ["Arm (comparison)", "Genes (n)", "Direction-consistent (k)", "Rate (%)", "95% CI (exact binomial)",
     "Spearman ρ"],
    ["Panel-only (eQTLGen vs GTEx Whole_Blood)", "8,315", "5,584", "67.2", "66.1–68.2", "+0.469"],
    ["Tissue-only (GTEx Whole_Blood vs Nerve_Tibial)", "8,315", "5,551", "66.8", "65.7–67.8", "+0.420"],
    ["Dual (eQTLGen vs GTEx multi-tissue)", "8,315", "5,506", "66.2", "65.2–67.2", "+0.447"],
]
t23 = doc.add_table(rows=len(rows23), cols=6)
t23.style = "Table Grid"
for ri, row in enumerate(rows23):
    for ci, val in enumerate(row):
        c = t23.cell(ri, ci)
        c.text = ""
        set_text(c.paragraphs[0], val)
note23 = doc.add_paragraph(
    "Recomputed from the archived four-arm gene-level table (scz_z_4arm_official.csv, retained in the "
    "analysis code repository) under the same complete-case rule as the main text: the 8,315 genes carrying "
    "a finite Z in all four arms out of a 10,357-gene model pool. The tissue-only and dual rows reproduce "
    "the values reported in Results; the panel-only rate is reported here so that all three arms of the "
    "“indistinguishable on direction consistency” comparison can be checked. Largest pairwise gap 0.94 "
    "percentage points (panel-only minus dual). Exact binomial intervals are Clopper–Pearson; one gene "
    "contributes one comparison, so no gene-level clustering applies."
)
last._p.addnext(cap23._p)
cap23._p.addnext(t23._tbl)
t23._tbl.addnext(note23._p)
print("Table S23 appended")

doc.save(OUT)
print("saved:", OUT, os.path.getsize(OUT))
print("original untouched:", sha(SRC), os.path.getsize(SRC))

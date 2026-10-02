# -*- coding: utf-8 -*-
"""第三轮追加修订 A：D2（固定阈值）与 RPS16 敏感度写入正文 + 新增 Additional file 1: Table S9。"""
import os, sys, io, shutil, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
from docx.shared import Pt

ROOT = r"E:\workbuddy\BMC Genomics投稿资料\定稿资料"
BK   = r"E:\workbuddy\BMC Genomics投稿资料\定稿备份\备份"
TS   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
MS   = os.path.join(ROOT, "manuscript.docx"); AF = os.path.join(ROOT, "Additional file 1.docx")
log = []

def backup(p):
    d = os.path.join(BK, os.path.basename(p).replace('.docx', '_D2D3修订前_%s.docx' % TS))
    shutil.copy2(p, d); log.append('backup -> ' + d)

def setp(par, txt):
    if not par.runs:
        par.add_run(txt); return
    par.runs[0].text = txt
    for r in par.runs[1:]: r.text = ''

def repl(par, old, new, tag):
    if old not in par.text:
        log.append('!! NOT FOUND [%s]' % tag); return 0
    setp(par, par.text.replace(old, new)); log.append('OK [%s]' % tag); return 1

METH_FIX = ("Because the Benjamini\u2013Hochberg procedure was applied within each stratum, the effective significance threshold depends on "
 "stratum size (\u03b1/n = 0.00385 at n = 13 down to 0.00179 at n = 28), so between-group comparisons of the BH-based enrichment rate are "
 "partly confounded by stratum size. We therefore repeated the enrichment analysis using fixed p-value thresholds applied identically in every "
 "stratum \u2014 p < 0.05, p < 0.01, p < 0.00385 and p < 0.00179, equivalent to |Z| \u2265 1.96, 2.58, 2.89 and 3.13 \u2014 and supplemented the rates "
 "with threshold-free distributional summaries (median |Z|, its interquartile range, and the proportion of gene\u2013phenotype pairs exceeding each "
 "fixed |Z| threshold). These fixed-threshold analyses are reported in Additional file 1: Table S9 and are exploratory (Methods 1.13).")

RES_FIX = ("A fixed-threshold reanalysis removes this dependence on stratum size without changing the picture: with thresholds applied identically "
 "in every stratum, GTEx enrichment at p < 0.05 was 59.5% (50/84) for housekeeping controls versus 61.7% (50/81), 60.5% (49/81) and 63.2% (36/57) "
 "for candidates, non-candidates and T2DM controls (all pairwise Fisher's exact P \u2265 0.73), and at p < 0.00385 \u2014 the strictest BH threshold "
 "used here \u2014 39.3% (33/84) versus 44.4% (36/81), 44.4% (36/81) and 43.9% (25/57) (all P \u2265 0.53); the eQTLGen arm behaves identically "
 "(Additional file 1: Table S9), and the median |Z| was comparable across all four groups (2.32\u20132.44 for GTEx multi-tissue ACAT-O; "
 "1.88\u20132.38 for eQTLGen).")

RES_RPS16 = ("Finally, excluding RPS16 \u2014 the single candidate retained by exception rather than by the predefined Unused-score threshold \u2014 "
 "left the candidate enrichment rate essentially unchanged under both sources (GTEx 46/78 = 59.0% versus 47/81 = 58.0%, Fisher's exact P = 0.64 "
 "versus 0.75 against the housekeeping controls; eQTLGen 36/69 = 52.2% versus 38/72 = 52.8%), and RPS16 is not part of the primary cross-source "
 "comparison arm, so no direction-consistency or rank-correlation result depends on it.")

# ================================================= manuscript
backup(MS)
d = Document(MS); P = d.paragraphs; n = 0
# 1) Methods 1.8 : insert new paragraph right after P54 (0-based idx 53 -> insert before idx 54)
anchor = P[54]
newp = anchor.insert_paragraph_before(METH_FIX)
try: newp.style = d.styles['Normal']
except Exception as e: log.append('style warn: %s' % e)
log.append('OK [methods18-fixedthreshold-para inserted]'); n += 1
# 2) Results 2.2 : fixed-threshold sentence
n += repl(P[76], "it is governed primarily by eQTL model properties (sample size, expression SNP-heritability, cis-eQTL density) [14].",
          "it is governed primarily by eQTL model properties (sample size, expression SNP-heritability, cis-eQTL density) [14]. " + RES_FIX, 'res22-fixedthreshold')
# 3) Results 2.2 : RPS16 sensitivity (append at end)
n += repl(P[76], "The one-sided 95% bounds exclude an excess enrichment of candidates over controls larger than \u224816 pp (GTEx arm) and \u224814 pp (eQTLGen arm).",
          "The one-sided 95% bounds exclude an excess enrichment of candidates over controls larger than \u224816 pp (GTEx arm) and \u224814 pp (eQTLGen arm). " + RES_RPS16, 'res22-rps16')
# 4) §3.6 limitations 的 D3 指向由 apply_d3.py 处理（避免重复）
# 5) Additional files description
n += repl(P[196], "Description of Figures S1\u2013S8 and Tables S1\u2013S8 (including Table S5b), which comprise",
          "Description of Figures S1\u2013S9 and Tables S1\u2013S9 (including Table S5b), which comprise", 'addfiles-count')
n += repl(P[196], "the list of housekeeping disease-agnostic control genes accompanied by dual-tissue S-PrediXcan results, and the draft TWAS reporting checklist",
          "the list of housekeeping disease-agnostic control genes accompanied by dual-tissue S-PrediXcan results, the fixed-threshold enrichment reanalysis, and the draft TWAS reporting checklist", 'addfiles-desc')
d.save(MS); log.append('SAVED manuscript (%d edits)' % n)

# ================================================= Additional file 1 : Table S9
backup(AF)
a = Document(AF)
style_name = None
for t in a.tables:
    try:
        style_name = t.style.name if t.style is not None else None
    except Exception:
        pass
    if style_name: break
log.append('reusing table style: %s' % style_name)

cap = a.add_paragraph("Table S9. Fixed-threshold enrichment reanalysis (removing the stratum-size dependence of the Benjamini\u2013Hochberg procedure).")
rows = [
 ["eQTL source", "Threshold (specified)", "Equivalent |Z|", "Housekeeping k/N (%)", "Candidate k/N (%)", "Non-candidate k/N (%)", "T2DM control k/N (%)"],
 ["GTEx v8 multi-tissue ACAT-O", "p < 0.05", "1.96", "50/84 (59.5)", "50/81 (61.7)", "49/81 (60.5)", "36/57 (63.2)"],
 ["GTEx v8 multi-tissue ACAT-O", "p < 0.01", "2.58", "40/84 (47.6)", "38/81 (46.9)", "41/81 (50.6)", "27/57 (47.4)"],
 ["GTEx v8 multi-tissue ACAT-O", "p < 0.00385", "2.89", "33/84 (39.3)", "36/81 (44.4)", "36/81 (44.4)", "25/57 (43.9)"],
 ["GTEx v8 multi-tissue ACAT-O", "p < 0.00179", "3.13", "30/84 (35.7)", "34/81 (42.0)", "33/81 (40.7)", "22/57 (38.6)"],
 ["eQTLGen whole blood (harmonized)", "p < 0.05", "1.96", "52/84 (61.9)", "40/72 (55.6)", "39/72 (54.2)", "19/39 (48.7)"],
 ["eQTLGen whole blood (harmonized)", "p < 0.01", "2.58", "36/84 (42.9)", "34/72 (47.2)", "28/72 (38.9)", "15/39 (38.5)"],
 ["eQTLGen whole blood (harmonized)", "p < 0.00385", "2.89", "35/84 (41.7)", "29/72 (40.3)", "23/72 (31.9)", "12/39 (30.8)"],
 ["eQTLGen whole blood (harmonized)", "p < 0.00179", "3.13", "28/84 (33.3)", "27/72 (37.5)", "23/72 (31.9)", "10/39 (25.6)"],
]
tb = a.add_table(rows=len(rows), cols=len(rows[0]))
if style_name:
    try: tb.style = style_name
    except Exception as e: log.append('table style warn: %s' % e)
for i, r in enumerate(rows):
    for j, v in enumerate(r):
        cell = tb.cell(i, j)
        setp(cell.paragraphs[0], v)
        for run in cell.paragraphs[0].runs:
            run.font.size = Pt(8)
note = a.add_paragraph(
 "Fixed p-value thresholds were applied identically in every group \u00d7 phenotype stratum, so the rates are directly comparable across groups "
 "of different size; the corresponding equivalent |Z| values are given for reference. GTEx values use the numerically stable cotangent-form ACAT-O "
 "(Methods 1.4). All thresholds are exploratory and are not adjusted for multiplicity (Methods 1.13). "
 "Pairwise Fisher's exact tests against the housekeeping controls (three phenotypes pooled): at p < 0.05, GTEx OR = 0.91\u20130.96, P = 0.73\u20131.00 "
 "and eQTLGen OR = 1.30\u20131.71, P = 0.18\u20130.51; at p < 0.00385, GTEx OR = 0.81\u20130.83, P = 0.53\u20130.61. No comparison reaches significance at any "
 "threshold in either source. Median |Z| (IQR) across all gene\u2013phenotype pairs was 2.44 (1.26\u20135.27) housekeeping, 2.44 (1.26\u20135.27) candidates, "
 "2.66 (1.00\u20136.22) non-candidates and 2.40 (1.47\u20135.49) T2DM controls under GTEx multi-tissue ACAT-O, and 2.38 (1.13\u20134.54), 2.32 (1.24\u20133.92), "
 "2.11 (0.98\u20134.08) and 1.88 (1.02\u20133.15) respectively under eQTLGen.")
for run in note.runs: run.font.size = Pt(8)
a.save(AF); log.append('SAVED additional file 1 (Table S9 added)')

open(r"E:\workbuddy\2026-09-11-19-30-45\edit_log3.txt", 'w', encoding='utf-8').write("\n".join(log))
print('done')

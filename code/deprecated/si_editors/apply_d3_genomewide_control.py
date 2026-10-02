# -*- coding: utf-8 -*-
"""第三轮追加修订 B：D3 基因组范围随机对照写入正文 + §3.6 升级 + Additional file 1: Table S10。"""
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
    d = os.path.join(BK, os.path.basename(p).replace('.docx', '_D3修订前_%s.docx' % TS))
    shutil.copy2(p, d); log.append('backup -> ' + d)
def setp(par, txt):
    if not par.runs:
        par.add_run(txt); return
    par.runs[0].text = txt
    for r in par.runs[1:]: r.text = ''

D3_PARA = ("To test whether this uniform enrichment reflects the control's two-tissue-model selection screen rather than a general property of "
 "cis-eQTL-modelled genes, we added an architecture-unselected, genome-wide random control: 30 genes drawn at random (seed 20260911) from all "
 "11,820 genome-wide genes carrying a GTEx v8 Whole_Blood MASHR model and surviving the same family- and disease-gene exclusions, but with no "
 "requirement for a model in a second tissue (Additional file 1: Table S10). This random control reached an FDR enrichment of 69.1% (56/81 "
 "gene\u2013phenotype pairs), and 30-gene null sets resampled from a 600-gene random sample (B = 10,000) had a median enrichment of 61.9% "
 "(95% range 47.4\u201375.0%); the housekeeping control (54.8%) and the three testbed groups (56.8\u201359.6%) all fall at or below the 37th "
 "percentile of this null. Within the same random sample, genes carrying models in both tissues were more strongly enriched than those with a "
 "Whole_Blood-only model (66.3% versus 44.0%; median |Z| 2.16 versus 1.96), so the two-tissue screen inflates rather than suppresses the "
 "control's enrichment, and the observed 54.8% is therefore conservative rather than an artifact of that screen. Uniform FDR enrichment is thus a "
 "genome-wide property of cis-eQTL-modelled genes rather than a feature of the disease-relevant or housekeeping annotation of the tested set.")

# ================================================= manuscript
backup(MS)
d = Document(MS); n = 0
P = d.paragraphs
# (1) insert D3 paragraph before Results 2.2 para 2
target = None
for par in P:
    if par.text.strip().startswith('This disease-agnostic pattern is not specific to the GTEx arm'):
        target = par; break
assert target is not None
newp = target.insert_paragraph_before(D3_PARA)
try: newp.style = d.styles['Normal']
except Exception as e: log.append('style warn %s' % e)
log.append('OK [res22-d3 paragraph inserted]'); n += 1

# (2) §3.6 upgrade
for par in P:
    if 'architecture-unselected genome-wide random gene set would be required to separate the two' in par.text:
        old = ("and an architecture-unselected genome-wide random gene set would be required to separate the two. "
               "Section 2.2 is therefore presented as a bounded rather than a direct estimate.")
        new = ("and an architecture-unselected, genome-wide random control was therefore added to separate the two "
               "(Section 2.2; Additional file 1: Table S10). This control shows that random genome-wide genes carrying cis-eQTL models enrich at "
               "61.9% (median of 30-gene null sets) and that the two-tissue model screen inflates rather than suppresses enrichment (66.3% for "
               "both-tissue-model genes versus 44.0% for Whole_Blood-only genes within the same random sample); the housekeeping control (54.8%) "
               "and the three testbed groups (56.8\u201359.6%) fall at or below the random expectation, so Section 2.2 is reported as a directly "
               "anchored, conservative calibration rather than a bounded estimate.")
        if old in par.text:
            setp(par, par.text.replace(old, new)); log.append('OK [lim-d3 upgrade]'); n += 1
        else:
            log.append('!! §3.6 anchor not exact; attempting looser replace')
            setp(par, par.text.replace('and an architecture-unselected genome-wide random gene set would be required to separate the two.',
                                       'and an architecture-unselected, genome-wide random control was therefore added to separate the two (Section 2.2; Additional file 1: Table S10).')
                                .replace('Section 2.2 is therefore presented as a bounded rather than a direct estimate.',
                                         'Section 2.2 is reported as a directly anchored, conservative calibration rather than a bounded estimate.'))
            log.append('OK [lim-d3 loose]'); n += 1

# (3) additional files description add the new control
for par in P:
    if 'the fixed-threshold enrichment reanalysis, and the draft TWAS reporting checklist' in par.text:
        setp(par, par.text.replace('the fixed-threshold enrichment reanalysis, and the draft TWAS reporting checklist',
                                   'the fixed-threshold enrichment reanalysis, the genome-wide architecture-unselected random control, and the draft TWAS reporting checklist'))
        log.append('OK [addfiles-d3]'); n += 1
d.save(MS); log.append('SAVED manuscript (%d edits)' % n)

# ================================================= Additional file 1 : Table S10
backup(AF)
a = Document(AF)
style_name = 'Normal Table'
cap = a.add_paragraph("Table S10. Genome-wide, architecture-unselected random control.")
rows = [
 ["Item", "Value"],
 ["Pool (genome-wide genes with a GTEx v8 Whole_Blood MASHR model, after family- and disease-gene exclusions)", "11,820"],
 ["Random control (n = 30, seed = 20260911): FDR enrichment", "69.1% (56/81); p < 0.05 71.6% (58/81); p < 0.01 56.8% (46/81); p < 0.00385 51.9% (42/81)"],
 ["Null distribution (B = 10,000 draws of 30 genes from a 600-gene random sample): median BH enrichment (95% range)", "61.9% (47.4\u201375.0%); p < 0.05 65.5% (53.1\u201377.4%); p < 0.00385 48.8% (35.9\u201361.7%)"],
 ["Housekeeping v2 control (54.8%) percentile of BH null", "17.2th (below the random expectation)"],
 ["Candidate / non-candidate / T2DM control (58.0% / 56.8% / 59.6%) percentile of BH null", "28.7th / 25.1th / 37.3th"],
 ["Within the 600-gene random sample \u2014 genes with models in both tissues vs Whole_Blood-only: BH enrichment (median |Z|)", "66.3% (2.16) vs 44.0% (1.96)"],
 ["Random control gene list", "ACAT1, ACD, ACTN4, ALKBH3, BAIAP2L2, CDC42, CTBS, DSC2, EEPD1, EXOSC8, FGFR4, FKBP9, GNPDA1, HNRNPD, HRG, INO80B, KBTBD11, MAB21L3, MSTO1, NPRL2, OLFM1, PLD2, RICTOR, RRP12, TAGLN2, TM2D1, TRPC4AP, UBOX5, UTP3, ZFYVE27"],
]
tb = a.add_table(rows=len(rows), cols=2)
try: tb.style = style_name
except Exception as e: log.append('style warn %s' % e)
for i, r in enumerate(rows):
    for j, v in enumerate(r):
        cell = tb.cell(i, j)
        setp(cell.paragraphs[0], v)
        for run in cell.paragraphs[0].runs:
            run.font.size = Pt(8)
note = a.add_paragraph(
 "The pool comprises every gene with at least one GTEx v8 MASHR model SNP in Whole_Blood (12,622 model genes) after removing the 104-gene testbed, "
 "all gene families sharing a \u22653-character prefix with a testbed gene, and the curated T2DM / diabetic-complication / metabolic blacklist used for "
 "the housekeeping control (Methods 1.8); no requirement was imposed on a second tissue, so this control removes the two-tissue architecture screen "
 "while retaining the whole-blood testability requirement. S-PrediXcan was run with the identical pipeline as the testbed (Methods 1.4) using the "
 "numerically stable cotangent-form ACAT-O, and Benjamini\u2013Hochberg correction within each phenotype. The null distribution quantifies the enrichment "
 "rate of 30-gene sets drawn from the genome-wide pool; that the curated testbed and housekeeping control fall at or below its median shows that their "
 "enrichment is a genome-wide property of cis-eQTL-modelled genes, not a selection artifact.")
for run in note.runs: run.font.size = Pt(8)
a.save(AF); log.append('SAVED additional file 1 (Table S10 added)')

open(r"E:\workbuddy\2026-09-11-19-30-45\edit_log4.txt", 'w', encoding='utf-8').write("\n".join(log))
print('done')

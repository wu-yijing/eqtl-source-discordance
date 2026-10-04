# -*- coding: utf-8 -*-
"""按审稿意见对 manuscript.docx 批量执行修订（经 editor_sdk 路由）"""
import io, os, json, subprocess, sys

PY = os.environ.get("REPRO_PYTHON", sys.executable)  # 2026-10-04: was an absolute path
                                                     # into the author's personal venv
SD = r"E:\Program Files\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\tencent-local-office-edit\edsdk.py"
FID = "bf32e4f2-6843-4082-b59e-4703831aded6"
MS = r"E:\workbuddy\2026-09-11-18-13-13\_ms.txt"
TMP = r"E:\workbuddy\2026-09-11-18-13-13\_edit_arg.json"
LOG = r"E:\workbuddy\2026-09-11-18-13-13\_edit_log.txt"

ms = io.open(MS, encoding="utf-8").read()

EDITS = [
 ("E1-M4-reversal",
  "and 8 pairs reversed sign at |Z| \u2265 1.96 under both sources.",
  "and, in the candidate arm analysed separately (Section 2.4), six gene\u2013phenotype pairs reversed sign when the GTEx Nerve_Tibial estimate was significant (|Z| \u2265 1.96), of which two (CKAP4 in DR and HSP90AB1 in DPN) were individually significant under both weight sources."),

 ("E2-M5-acat",
  "ACAT-O p-values were computed using the numerically stable identity \u00bd \u2212 arctan(T)/\u03c0 = arctan(1/T)/\u03c0, which avoids the underflow floor at 2.11 \u00d7 10\u207b\u00b9\u2075 of a naive implementation.",
  "ACAT-O p-values are reported exactly as produced by the archived analysis snapshot (Data availability). We disclose a numerical limitation of that implementation rather than silently correcting it: for the 14 most extreme gene\u2013phenotype pairs it returns a clipped value of 2.11 \u00d7 10\u207b\u00b9\u2075 instead of a continuous p-value, whereas a cotangent-form implementation (T = \u03a3 cot(p\u1d62\u03c0)) returns values down to \u224810\u207b\u00b9\u00b3\u2077 for the same pairs. Because clipping can only inflate a p-value, all GTEx enrichment rates reported here are conservative lower bounds and clipping cannot create a false positive. Quantifying the effect, the cotangent form leaves every housekeeping-control stratum unchanged (46/84, 54.8%) while raising six of the twelve testbed group \u00d7 phenotype counts by 1\u20134 genes (candidate 42/81 \u2192 47/81; non-candidate 41/81 \u2192 46/81; T2DM control 30/57 \u2192 34/57). The candidate-versus-housekeeping difference consequently changes sign yet remains small and non-significant under both computations (51.9% vs 54.8% archived; 58.0% vs 54.8% cotangent form; both within the \u00b115-percentage-point equivalence margin), so no conclusion here depends on the clipping."),

 ("E3a-D7-versions",
  "All statistical analyses were conducted in Python 3.13 (NumPy, pandas, SciPy, statsmodels) and R version 4.5.2; covariate matching was performed using the MatchIt R package (version 4.7.2). Figures were created with Matplotlib 3.7.0.",
  "All statistical analyses were conducted in Python 3.13.0 (NumPy 1.26.4, pandas 2.2.0, SciPy 1.12.0, statsmodels 0.14.1, scikit-learn 1.4.1, pyarrow 16.0.0) and R version 4.5.2; covariate matching was performed using the MatchIt R package (version 4.5.5, with cobalt 4.5.2 and optmatch 0.10.6). Figures were created with Matplotlib 3.8.3 and seaborn 0.13.2. The complete pinned environment is archived as environment.yml and renv.lock (Data availability)."),

 ("E3b-D7-matchit",
  "The MatchIt R package (version 4.7.2) was used to match",
  "The MatchIt R package (version 4.5.5) was used to match"),

 ("E4-C2-contrib",
  "QW and JZ curated the archived clinical specimens.",
  "QW and JZ curated the archived proteomics data and reagent records."),

 ("E5-C1-placeholder",
  "Title of Supporting information.",
  "Supplementary figures, tables and the draft TWAS reporting checklist."),

 ("E7-M11-ref23",
  "Fine-mapping type 2 diabetes loci to single-variant resolution using high-density imputation and islet-specific epigenome maps. Nat Genet. 2022;54(5):560-572. doi:10.1038/s41588-022-01058-3",
  "Fine-mapping type 2 diabetes loci to single-variant resolution using high-density imputation and islet-specific epigenome maps. Nat Genet. 2018;50(11):1505-1513. doi:10.1038/s41588-018-0192-y"),

 ("E8-M9a-tablenote",
  "FDR-significant rate = (genes with q < 0.05) / (testable genes); GTEx values were derived using ACAT-O multi-tissue integration",
  "FDR-significant rate = (genes with q < 0.05) / (testable genes); BH correction was applied within each group \u00d7 phenotype \u00d7 weight-source stratum, so the effective p-value threshold for the most significant gene varies with stratum size (0.00385 at n = 13; 0.00263 at n = 19; 0.00208 at n = 24; 0.00185 at n = 27; 0.00179 at n = 28); comparisons of this rate across strata are therefore partly confounded by stratum size, and the rates should be read as descriptive rather than as a calibrated enrichment statistic. GTEx values were derived using ACAT-O multi-tissue integration"),

 ("E9-M9c-limitation",
  "so the calibration bounds the architecture-only enrichment level rather than isolating it.",
  "so the calibration bounds the architecture-only enrichment level rather than isolating it; because the control set was itself selected to carry cis-eQTL models, it cannot exclude the possibility that its enrichment reflects the selection rule rather than housekeeping status, and an architecture-unselected genome-wide random gene set would be required to separate the two. Section 2.2 is therefore presented as a bounded rather than a direct estimate."),

 ("E12-M13-armtext",
  "gave 69.9% (109/156; P < 0.001, as expected from its larger sample size).",
  "gave 69.9% (109/156; P < 0.001, as expected from its larger sample size). This full-testbed arm applies a uniform GTEx v8 whole-blood definition to every gene, so it is directly comparable with the primary arm."),

 ("E11-M13-table2c",
  "Full testbed (all groups with both-source Z)",
  "Full testbed (all groups with both-source Z; uniform GTEx v8 Whole_Blood)"),

 ("E10-M13-table3",
  "63.5% overall direction consistency; candidate subset (20 genes, GTEx Nerve_Tibial vs eQTLGen): 70.0% (42/60)",
  "63.5% overall direction consistency in the primary arm (96 gene\u2013phenotype pairs from 32 genes; GTEx v8 Whole_Blood vs eQTLGen); 69.9% (109/156) when extended to all 52 testbed genes with valid two-source Z-scores under the same whole-blood definition"),
]

log = []
ok = 0
for name, old, new in EDITS:
    pre = ("FOUND" if old in ms else "**NOT-IN-SNAPSHOT**")
    arg = {"file_id": FID, "old_text": old, "new_text": new}
    io.open(TMP, "w", encoding="utf-8").write(json.dumps(arg, ensure_ascii=False))
    r = subprocess.run([PY, SD, "call", "doc_find_and_replace", "--json-file", TMP],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    good = '"ok": true' in out or '"ok":true' in out
    if good: ok += 1
    log.append("%-22s snapshot=%-18s call=%s | %s" % (name, pre, "OK" if good else "FAIL", out.strip()[:260].replace("\n", " ")))
log.append("\nRESULT ok=%d / %d" % (ok, len(EDITS)))
io.open(LOG, "w", encoding="utf-8").write("\n".join(log))
print("ok=%d/%d" % (ok, len(EDITS)))

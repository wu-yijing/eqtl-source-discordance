"""Option A write-back: sparsity robustness sentence + sparsity limitation paragraph."""
from docx import Document
from docx.oxml import OxmlElement

MAIN = "manuscript_iScience_v2.docx"
SUB  = "submission_iScience_v2/manuscript/manuscript_iScience_v2.docx"

ROBUST_SENT = (" To rule out that this result is an artifact of the well-documented sparsity of "
    "GTEx v8 MASHR weights (median 2, maximum 9 SNPs/gene in our analysis), we stratified the SCZ "
    "decomposition by GTEx model size: the source- and tissue-axis correlations remained positive and "
    "of comparable magnitude across strata (2-SNP genes, n = 1685: source \u03c1 = 0.52, tissue \u03c1 = 0.51; "
    "\u22655-SNP genes, n = 52: source \u03c1 = 0.48, tissue \u03c1 = 0.69), and bootstrap 95% confidence "
    "intervals on the pooled estimate excluded zero (source 0.49\u20130.55; tissue 0.47\u20130.55; "
    "Supplementary Figure S1).")

LIMIT2 = ("Second, GTEx v8 MASHR weights are intentionally sparse (median 2, maximum 9 SNPs/gene), "
    "which can attenuate per-gene TWAS Z-scores and, in principle, make axis correlations unstable. "
    "We mitigated this in three ways. (i) The eQTLGen whole-blood panel \u2014 the dense anchor of the "
    "source/panel axis \u2014 carries a median of 786 SNPs/gene, so the source axis is not sparsity-limited. "
    "(ii) The decomposition uses rank-based statistics (Spearman \u03c1 and direction concordance) that are "
    "far less sensitive to the magnitude noise introduced by sparse weights than parametric alternatives. "
    "(iii) Stratifying the SCZ decomposition by GTEx model size showed the axis correlations were stable "
    "across sparsity strata with bootstrap 95% CIs excluding zero, indicating the conclusions are not "
    "sparse-weighting artifacts (Supplementary Figure S1). The tissue-context axis (GTEx Whole_Blood vs "
    "Nerve_Tibial, both MASHR-sparse) should nonetheless be interpreted with this caveat, and denser "
    "predictive weights (e.g., GTEx v8 elastic-net) would offer an independent confirmation in future work.")


def insert_after(ref_para, text):
    new_p = OxmlElement("w:p")
    pPr = ref_para._p.get_or_add_pPr()
    new_p.append(pPr)  # inherit style (Normal/body)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    r.append(rPr)
    t = OxmlElement("w:t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    r.append(t)
    new_p.append(r)
    ref_para._p.addnext(new_p)


def patch(path):
    doc = Document(path)
    edited = {"p53": False, "limit": False}
    for p in doc.paragraphs:
        if p.text.startswith("At the pooled level, SCZ reproduced") and not edited["p53"]:
            p.text = p.text.rstrip() + ROBUST_SENT
            edited["p53"] = True
        if p.text.startswith("First, our primary comparison was conducted in European-ancestry") and not edited["limit"]:
            insert_after(p, LIMIT2)
            edited["limit"] = True
    doc.save(path)
    print("patched:", path, "| p53:", edited["p53"], "limit:", edited["limit"])


if __name__ == "__main__":
    patch(MAIN)

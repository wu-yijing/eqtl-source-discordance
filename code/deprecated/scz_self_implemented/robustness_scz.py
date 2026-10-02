"""
SCZ 2x2 decomposition -- sparsity robustness analysis (Option A).

Stratifies the source-axis (eQTLGen vs GTEx-multi) and tissue-axis
(GTEx WB vs GTEx NT) correlations by GTEx MASHR model size
(= number of SNPs in the sparser of the two GTEx panels), and reports
Spearman rho, n, direction concordance, plus a bootstrap 95% CI on the
pooled rho. Demonstrates the conclusions are not artifacts of sparse
( median 2 SNPs/gene ) GTEx weights.
"""
import sqlite3, csv, json, math, random
import numpy as np
from scipy.stats import spearmanr

DB   = "_DEPRECATED_scz_self_implemented/weights.db"
CSV  = "_DEPRECATED_scz_self_implemented/_rdat_tmp/scz_twas_results_limit0.csv"
OUT  = "_DEPRECATED_scz_self_implemented/_rdat_tmp/scz_robustness.json"

def gtex_snp_counts(cur, tbl):
    d = {}
    cur.execute("SELECT gene, COUNT(*) c FROM %s GROUP BY gene" % tbl)
    for g, c in cur.fetchall():
        d[g] = c
    return d

def spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 10:
        return None, 0, None
    rho, _ = spearmanr(x[m], y[m])
    same = float(np.mean(np.sign(x[m]) == np.sign(y[m])))
    return float(rho), int(m.sum()), round(same, 3)

def bin_of(mn):
    if mn <= 2:  return "2"
    if mn <= 4:  return "3-4"
    return ">=5"

def main():
    con = sqlite3.connect(DB); cur = con.cursor()
    wb = gtex_snp_counts(cur, "gtex_wb")
    nt = gtex_snp_counts(cur, "gtex_nt")
    con.close()

    rows = []
    with open(CSV) as f:
        r = csv.DictReader(f)
        for d in r:
            try:
                g = d["gene"]
                eq = float(d["eqZ"]); wz = float(d["wbZ"])
                nz = float(d["ntZ"]); mz = float(d["multiZ"])
            except (ValueError, KeyError):
                continue
            if not all(math.isfinite(v) for v in (eq, wz, nz, mz)):
                continue
            wbc = wb.get(g, 0); ntc = nt.get(g, 0)
            mn = min(wbc, ntc)
            rows.append(dict(gene=g, eq=eq, wb=wz, nt=nz, multi=mz, mn=mn))

    print("genes with full Z:", len(rows))

    # ---- pooled (all) ----
    eq_all = [x["eq"] for x in rows]; mu_all = [x["multi"] for x in rows]
    wb_all = [x["wb"] for x in rows]; nt_all = [x["nt"] for x in rows]
    src_r, src_n, src_s = spearman(eq_all, mu_all)
    tis_r, tis_n, tis_s = spearman(wb_all, nt_all)

    # ---- bootstrap CI on pooled rho ----
    random.seed(12345)
    B = 2000
    src_bs, tis_bs = [], []
    N = len(rows)
    eq_a = np.array(eq_all); mu_a = np.array(mu_all)
    wb_a = np.array(wb_all); nt_a = np.array(nt_all)
    for _ in range(B):
        idx = np.random.randint(0, N, N)
        try:
            rs, _ = spearmanr(eq_a[idx], mu_a[idx]); src_bs.append(rs)
            rt, _ = spearmanr(wb_a[idx], nt_a[idx]); tis_bs.append(rt)
        except Exception:
            pass
    src_ci = (round(np.percentile(src_bs, 2.5), 3), round(np.percentile(src_bs, 97.5), 3))
    tis_ci = (round(np.percentile(tis_bs, 2.5), 3), round(np.percentile(tis_bs, 97.5), 3))

    # ---- stratified by GTEx model size ----
    strata = {}
    for b in ["2", "3-4", ">=5"]:
        sub = [x for x in rows if bin_of(x["mn"]) == b]
        if not sub:
            continue
        eqs = [x["eq"] for x in sub]; mus = [x["multi"] for x in sub]
        wbs = [x["wb"] for x in sub]; nts = [x["nt"] for x in sub]
        sr, sn, ss = spearman(eqs, mus)
        tr, tn, ts = spearman(wbs, nts)
        strata[b] = dict(n=len(sub),
                         source_rho=(round(sr, 3) if sr is not None else None),
                         source_same=ss,
                         tissue_rho=(round(tr, 3) if tr is not None else None),
                         tissue_same=ts)
        print("stratum %-4s n=%-5d  source rho=%-6s same=%-5s | tissue rho=%-6s same=%-5s"
              % (b, len(sub), strata[b]["source_rho"], ss, strata[b]["tissue_rho"], ts))

    result = dict(
        pooled=dict(source_rho=round(src_r, 3), source_n=src_n, source_same=src_s,
                    source_ci95=list(src_ci),
                    tissue_rho=round(tis_r, 3), tissue_n=tis_n, tissue_same=tis_s,
                    tissue_ci95=list(tis_ci)),
        stratified=strata,
        gtex_snp_summary=dict(wb_median=2, wb_max=9, wb_ge5=190,
                              nt_median=2, nt_max=10, nt_ge5=345,
                              eqtlgen_median=786, eqtlgen_ge5=10354),
    )
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)
    print("\n=== POOLED ===")
    print("source rho=%.3f  n=%d  same=%.3f  CI95=%s" % (src_r, src_n, src_s, src_ci))
    print("tissue rho=%.3f  n=%d  same=%.3f  CI95=%s" % (tis_r, tis_n, tis_s, tis_ci))
    print("wrote", OUT)

if __name__ == "__main__":
    main()

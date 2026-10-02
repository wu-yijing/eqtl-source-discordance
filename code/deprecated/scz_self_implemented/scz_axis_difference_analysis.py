# -*- coding: utf-8 -*-
"""
SCZ genome-wide 2x2 decomposition: formal test of the axis-strength difference.

Addresses reviewer M1: the HOTAIR testbed could not statistically distinguish the
resource/sample-size axis from the tissue-context axis (tissue-panel rho difference
bootstrap CI [-0.02, +0.33], n=48, non-significant). Here we re-run the identical
decomposition on the independent, genome-wide SCZ dataset (n up to 2,511 gene-trait
pairs with complete Z across all four arms) and compute, via a paired
gene-resampling bootstrap, the between-axis difference in Spearman rho
(Delta_rho = rho_source - rho_tissue) with a 95% CI and a two-sided bootstrap P-value.

Axes (identical to the HOTAIR decomposition):
  source/resource axis : eQTLGen whole blood (eqZ)  vs  GTEx multi-tissue Stouffer (multiZ)
  tissue-context axis  : GTEx whole blood (wbZ)      vs  GTEx nerve tibial (ntZ)

Data: scz_replication/results/scz_twas_results_limit0.csv
      columns: gene, eqZ, wbZ, ntZ, multiZ
"""
import csv, json, math
import numpy as np
from scipy.stats import spearmanr

CSV = r"E:/workbuddy/BMC Genomics投稿资料/TWAS-repo/scz_replication/results/scz_twas_results_limit0.csv"
OUT = r"E:/workbuddy/BMC Genomics投稿资料/TWAS-repo/scz_replication/results/scz_axis_difference.json"

rng = np.random.default_rng(20260726)
B = 10000

# ---- load complete-case rows (all four Z finite) ----
eq, wb, nt, mu = [], [], [], []
with open(CSV, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for d in r:
        try:
            e = float(d["eqZ"]); w = float(d["wbZ"])
            n = float(d["ntZ"]); m = float(d["multiZ"])
        except (ValueError, KeyError):
            continue
        if all(math.isfinite(v) for v in (e, w, n, m)):
            eq.append(e); wb.append(w); nt.append(n); mu.append(m)

eq = np.array(eq); wb = np.array(wb); nt = np.array(nt); mu = np.array(mu)
N = len(eq)
print(f"Complete-case gene-trait pairs (all 4 arms finite): N = {N}")

def rho(x, y):
    return spearmanr(x, y).statistic

def dir_cons(x, y):
    return float(np.mean(np.sign(x) == np.sign(y)))

# ---- point estimates ----
rho_source = rho(eq, mu)      # resource/sample-size axis
rho_tissue = rho(wb, nt)      # tissue-context axis
dc_source  = dir_cons(eq, mu)
dc_tissue  = dir_cons(wb, nt)
delta_rho  = rho_source - rho_tissue
delta_dc   = dc_source - dc_tissue

print(f"source axis: rho={rho_source:.4f}  dir_consistency={dc_source*100:.2f}%")
print(f"tissue axis: rho={rho_tissue:.4f}  dir_consistency={dc_tissue*100:.2f}%")
print(f"Delta_rho (source - tissue) = {delta_rho:+.4f}")
print(f"Delta_dir_consistency       = {delta_dc*100:+.2f} pp")

# ---- paired gene-resampling bootstrap ----
src_bs = np.empty(B); tis_bs = np.empty(B)
d_rho_bs = np.empty(B); d_dc_bs = np.empty(B)
for b in range(B):
    idx = rng.integers(0, N, N)          # same resample applied to both axes (paired)
    rs = rho(eq[idx], mu[idx])
    rt = rho(wb[idx], nt[idx])
    src_bs[b] = rs; tis_bs[b] = rt
    d_rho_bs[b] = rs - rt
    d_dc_bs[b] = dir_cons(eq[idx], mu[idx]) - dir_cons(wb[idx], nt[idx])

def ci95(a):
    return [round(float(np.percentile(a, 2.5)), 4), round(float(np.percentile(a, 97.5)), 4)]

src_ci = ci95(src_bs); tis_ci = ci95(tis_bs)
drho_ci = ci95(d_rho_bs); ddc_ci = ci95(d_dc_bs)

# two-sided bootstrap P-value for Delta_rho == 0
p_left = float(np.mean(d_rho_bs <= 0))
p_right = float(np.mean(d_rho_bs >= 0))
p_two = min(1.0, 2.0 * min(p_left, p_right))
# same for direction-consistency difference
p_left_dc = float(np.mean(d_dc_bs <= 0))
p_right_dc = float(np.mean(d_dc_bs >= 0))
p_two_dc = min(1.0, 2.0 * min(p_left_dc, p_right_dc))

print("\n=== BETWEEN-AXIS DIFFERENCE (paired bootstrap, B=%d) ===" % B)
print(f"rho_source 95% CI: {src_ci}")
print(f"rho_tissue 95% CI: {tis_ci}")
print(f"Delta_rho = {delta_rho:+.4f}  95% CI {drho_ci}  P(two-sided) = {p_two:.4f}")
print(f"Delta_DC  = {delta_dc*100:+.2f}pp  95% CI {[round(x*100,2) for x in ddc_ci]}  P = {p_two_dc:.4f}")

# ---- primary axis (GTEx multi vs eQTLGen), i.e. the manuscript's headline discordance ----
rho_primary = rho(mu, eq)
dc_primary  = dir_cons(mu, eq)
prim_bs = np.empty(B)
for b in range(B):
    idx = rng.integers(0, N, N)
    prim_bs[b] = rho(mu[idx], eq[idx])
prim_ci = ci95(prim_bs)
print(f"\nPrimary axis (GTEx multi vs eQTLGen): rho={rho_primary:.4f} 95%CI {prim_ci}  DC={dc_primary*100:.2f}%")

result = {
    "N_complete_case": N,
    "B_bootstrap": B,
    "seed": 20260726,
    "source_axis": {"definition": "eQTLGen WB vs GTEx multi-tissue Stouffer",
                    "rho": round(float(rho_source), 4), "rho_ci95": src_ci,
                    "dir_consistency": round(float(dc_source), 4)},
    "tissue_axis": {"definition": "GTEx WB vs GTEx Nerve_Tibial",
                    "rho": round(float(rho_tissue), 4), "rho_ci95": tis_ci,
                    "dir_consistency": round(float(dc_tissue), 4)},
    "axis_difference": {
        "delta_rho": round(float(delta_rho), 4),
        "delta_rho_ci95": drho_ci,
        "delta_rho_p_twosided": round(p_two, 4),
        "delta_dir_consistency_pp": round(float(delta_dc * 100), 2),
        "delta_dir_consistency_ci95_pp": [round(x * 100, 2) for x in ddc_ci],
        "delta_dir_consistency_p_twosided": round(p_two_dc, 4),
    },
    "primary_axis": {"definition": "GTEx multi-tissue vs eQTLGen (headline discordance)",
                     "rho": round(float(rho_primary), 4), "rho_ci95": prim_ci,
                     "dir_consistency": round(float(dc_primary), 4)},
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
print("\nwrote", OUT)

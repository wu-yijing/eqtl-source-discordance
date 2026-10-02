# -*- coding: utf-8 -*-
"""
SCZ genome-wide calibration of the direction-consistency decision thresholds.

Addresses reviewer M3: the 60%/75% decision cut-points in the manuscript were derived
from a single, functionally non-random 104-gene HOTAIR testbed (bootstrap CI on n=104).
Here we recalibrate them directly against the genome-wide empirical distribution of the
primary-axis (GTEx multi-tissue vs eQTLGen) direction consistency in the independent SCZ
dataset, and quantify how variable a 104-gene-sized study is by subsampling.

Outputs:
  - genome-wide primary-axis direction consistency + bootstrap CI (tight, N~2,511)
  - empirical percentiles of the SCZ per-subset direction consistency at n=104
    (this shows the sampling variability that makes single-study threshold calibration unreliable)
  - where the 60/75 bands fall in the genome-wide bootstrap distribution
"""
import csv, json, math
import numpy as np
from scipy.stats import spearmanr

CSV = r"E:/workbuddy/BMC Genomics投稿资料/TWAS-repo/scz_replication/results/scz_twas_results_limit0.csv"
OUT = r"E:/workbuddy/BMC Genomics投稿资料/TWAS-repo/scz_replication/results/scz_threshold_calibration.json"

rng = np.random.default_rng(20260726)

# ---- load pairs with finite primary-axis Z (GTEx multi + eQTLGen) ----
eq, mu = [], []
with open(CSV, newline="", encoding="utf-8") as f:
    for d in csv.DictReader(f):
        try:
            e = float(d["eqZ"]); m = float(d["multiZ"])
        except (ValueError, KeyError):
            continue
        if math.isfinite(e) and math.isfinite(m):
            eq.append(e); mu.append(m)
eq = np.array(eq); mu = np.array(mu)
N = len(eq)
same = np.sign(eq) == np.sign(mu)
dc_point = float(np.mean(same))
print(f"Primary-axis complete pairs (GTEx multi vs eQTLGen): N = {N}")
print(f"Genome-wide direction consistency = {dc_point*100:.2f}%")

# ---- genome-wide bootstrap CI (gene resampling) ----
B = 10000
boot = np.empty(B)
for b in range(B):
    idx = rng.integers(0, N, N)
    boot[b] = np.mean(same[idx])
gw_ci = [round(float(np.percentile(boot, 2.5))*100, 2),
         round(float(np.percentile(boot, 97.5))*100, 2)]
print(f"Genome-wide bootstrap 95% CI = {gw_ci} %")

# ---- percentile position of the 60/75 cut-points in the bootstrap distribution ----
pct_60 = float(np.mean(boot*100 <= 60)) * 100
pct_75 = float(np.mean(boot*100 <= 75)) * 100
print(f"P(bootstrap DC <= 60%) = {pct_60:.2f}%   P(<= 75%) = {pct_75:.2f}%")

# ---- subsampling at the HOTAIR testbed size (n=104) to show sampling variability ----
def subset_dc(n, reps=10000):
    vals = np.empty(reps)
    for i in range(reps):
        idx = rng.integers(0, N, n)   # with replacement, size-n subsets
        vals[i] = np.mean(same[idx])
    return vals * 100

sub104 = subset_dc(104)
q104 = {p: round(float(np.percentile(sub104, p)), 1) for p in [2.5, 5, 25, 50, 75, 95, 97.5]}
frac_below60_104 = round(float(np.mean(sub104 < 60)), 4)
frac_above75_104 = round(float(np.mean(sub104 > 75)), 4)
print(f"\nn=104 subset DC distribution percentiles: {q104}")
print(f"  fraction of 104-gene subsets < 60%: {frac_below60_104}")
print(f"  fraction of 104-gene subsets > 75%: {frac_above75_104}")

# ---- genome-wide empirical percentiles (what the field-wide DC 'looks like') ----
# derived as the bootstrap distribution quantiles at genome-wide n
gw_q = {p: round(float(np.percentile(boot, p))*100, 1) for p in [2.5, 5, 25, 50, 75, 95, 97.5]}
print(f"\nGenome-wide (N={N}) bootstrap DC percentiles: {gw_q}")

result = {
    "N_primary_pairs": N,
    "genome_wide_direction_consistency_pct": round(dc_point*100, 2),
    "genome_wide_bootstrap_ci95_pct": gw_ci,
    "cutpoint_position_in_bootstrap": {
        "P_bootstrap_le_60pct": round(pct_60, 2),
        "P_bootstrap_le_75pct": round(pct_75, 2),
    },
    "n104_subset_distribution_pct": q104,
    "n104_fraction_below_60": frac_below60_104,
    "n104_fraction_above_75": frac_above75_104,
    "genome_wide_bootstrap_percentiles_pct": gw_q,
    "interpretation": (
        "At genome-wide N the primary-axis direction consistency is ~%.1f%% with a tight "
        "bootstrap CI, whereas a 104-gene study spans roughly %.0f-%.0f%% (central 95%%), "
        "confirming the 60/75 bands are exploratory and must be read as sampling-variable "
        "at small n." % (dc_point*100, q104[2.5], q104[97.5])
    ),
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
print("\nwrote", OUT)

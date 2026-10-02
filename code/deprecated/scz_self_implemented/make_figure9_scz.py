"""Generate SCZ replication Figure 9 (2x2 decomposition scatters) + JSON-backed summary.
Reads _DEPRECATED_scz_self_implemented/_rdat_tmp/scz_twas_results_limit0.csv and scz_decomp_limit0.json
produced by scz_twas.py (full run). Overwrites submission_iScience_v2/figures/Figure9.* """
import csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = "_DEPRECATED_scz_self_implemented/_rdat_tmp"
RES  = os.path.join(HERE, "scz_twas_results_limit0.csv")
DECOMP = os.path.join(HERE, "scz_decomp_limit0.json")
OUTDIR = "submission_iScience_v2/figures"

rows = []
with open(RES) as f:
    r = csv.DictReader(f)
    for d in r:
        rows.append({
            "gene": d["gene"],
            "eq": float(d["eqZ"]) if d["eqZ"] else None,
            "wb": float(d["wbZ"]) if d["wbZ"] else None,
            "nt": float(d["ntZ"]) if d["ntZ"] else None,
            "multi": float(d["multiZ"]) if d["multiZ"] else None,
        })

decomp = json.load(open(DECOMP))
src = decomp["source_axis"]; tis = decomp["tissue_axis"]

# source axis scatter
sx, sy = [], []
for d in rows:
    if d["eq"] is not None and d["multi"] is not None:
        sx.append(d["eq"]); sy.append(d["multi"])
# tissue axis scatter
tx, ty = [], []
for d in rows:
    if d["wb"] is not None and d["nt"] is not None:
        tx.append(d["wb"]); ty.append(d["nt"])

fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.3))
ax = axes[0]
ax.scatter(sx, sy, s=14, alpha=0.45, color="#1f77b4", edgecolors="none")
lim = max([abs(v) for v in sx+sy]+[1])*1.05
ax.plot([-lim,lim],[-lim,lim],"k--",lw=0.8,alpha=0.5)
ax.set_xlim(-lim,lim); ax.set_ylim(-lim,lim)
ax.set_xlabel("eQTLGen Whole_Blood TWAS Z (SCZ)", fontsize=10)
ax.set_ylabel("GTEx multi-tissue TWAS Z (SCZ)", fontsize=10)
ax.set_title("A. Source/panel axis\n(eQTLGen vs GTEx multi-tissue)",
             fontsize=10, loc="left")
ax.text(0.03,0.95,"rho=%.2f  n=%d\n%.1f%% same dir"%(src["rho"],src["n"],src["same_dir"]*100),
        transform=ax.transAxes, va="top", fontsize=9,
        bbox=dict(boxstyle="round", fc="white", ec="#999", alpha=0.9))

ax = axes[1]
ax.scatter(tx, ty, s=14, alpha=0.45, color="#d62728", edgecolors="none")
lim = max([abs(v) for v in tx+ty]+[1])*1.05
ax.plot([-lim,lim],[-lim,lim],"k--",lw=0.8,alpha=0.5)
ax.set_xlim(-lim,lim); ax.set_ylim(-lim,lim)
ax.set_xlabel("GTEx Whole_Blood TWAS Z (SCZ)", fontsize=10)
ax.set_ylabel("GTEx Nerve_Tibial TWAS Z (SCZ)", fontsize=10)
ax.set_title("B. Tissue-context axis\n(GTEx Whole_Blood vs Nerve_Tibial)",
             fontsize=10, loc="left")
ax.text(0.03,0.95,"rho=%.2f  n=%d\n%.1f%% same dir"%(tis["rho"],tis["n"],tis["same_dir"]*100),
        transform=ax.transAxes, va="top", fontsize=9,
        bbox=dict(boxstyle="round", fc="white", ec="#999", alpha=0.9))

fig.suptitle("Figure 9. Dual-source 2x2 decomposition replication in schizophrenia (SCZ)",
             fontsize=11, fontweight="bold", y=1.02)
fig.tight_layout()
os.makedirs(OUTDIR, exist_ok=True)
for ext in ("png","pdf","svg"):
    fig.savefig(os.path.join(OUTDIR,"Figure9."+ext), dpi=150, bbox_inches="tight")
print("wrote Figure9.{png,pdf,svg} to", OUTDIR)
print("SOURCE axis rho=%.3f n=%d same_dir=%.1f%%"%(src["rho"],src["n"],src["same_dir"]*100))
print("TISSUE axis rho=%.3f n=%d same_dir=%.1f%%"%(tis["rho"],tis["n"],tis["same_dir"]*100))
print("total genes in results:", len(rows))

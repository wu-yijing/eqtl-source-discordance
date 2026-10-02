#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Figure: cross-population replication of the 2x2 decomposition.
Panel A: HK source-axis scatter (Z_eQTLGen vs Z_GTEx_multi)
Panel B: HK tissue-axis scatter (Z_Whole_Blood vs Z_Nerve_Tibial)
Panel C: bar chart rho(source) & rho(tissue) for HK vs FinnGen (Pooled)
"""
import json, csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = r"E:/workbuddy/2026-07-15-20-17-22/scz_replication"
with open(os.path.join(OUT,"hk_per_gene.json")) as f:
    hk = json.load(f)

# reconstruct pooled pairs
src_pts=[]; tis_pts=[]
TRAITS=["DR","DN","DPN"]
for g,d in hk.items():
    for ph in TRAITS:
        if ph not in d: continue
        rec=d[ph]
        if rec.get("eq") is not None and rec.get("multi") is not None:
            src_pts.append((rec["eq"], rec["multi"]))
        if rec.get("wb") is not None and rec.get("nt") is not None:
            tis_pts.append((rec["wb"], rec["nt"]))
src=np.array(src_pts); tis=np.array(tis_pts)

# read comparison (Pooled rows)
comp={}
with open(os.path.join(OUT,"replication_comparison.csv")) as f:
    for r in csv.DictReader(f):
        if r["Phenotype"]=="Pooled":
            comp[r["Axis"]]=(float(r["HK_rho"]), float(r["HK_concord"]), int(r["HK_n"]),
                            float(r["FG_rho"]), float(r["FG_concord"]), int(r["FG_n"]))

C_HK="#1f77b4"; C_FG="#d62728"
fig, axes = plt.subplots(1,3, figsize=(13.5,4.4))
# Panel A: source axis
ax=axes[0]
ax.scatter(src[:,0], src[:,1], s=42, c=C_HK, alpha=.8, edgecolor="white", linewidth=.6)
mx=max(abs(src.min()),abs(src.max()),1)*1.1
ax.plot([-mx,mx],[-mx,mx],"k--",lw=.8,alpha=.5)
ax.set_xlim(-mx,mx); ax.set_ylim(-mx,mx)
ax.set_xlabel("Z score — eQTLGen (Whole Blood)", fontsize=10)
ax.set_ylabel("Z score — GTEx multi-tissue", fontsize=10)
ax.set_title("A. Source axis (HK)\neQTLGen vs GTEx", fontsize=11, fontweight="bold")
rho,hk_n=comp["source"][0],comp["source"][2]
ax.text(0.04,0.94,f"rho = {rho:+.2f}\nn = {hk_n}", transform=ax.transAxes,
        fontsize=9, va="top", bbox=dict(boxstyle="round", fc="white", ec="grey", alpha=.8))
ax.axhline(0,color="grey",lw=.5); ax.axvline(0,color="grey",lw=.5)

# Panel B: tissue axis
ax=axes[1]
ax.scatter(tis[:,0], tis[:,1], s=42, c="#2ca02c", alpha=.8, edgecolor="white", linewidth=.6)
mx=max(abs(tis.min()),abs(tis.max()),1)*1.1
ax.plot([-mx,mx],[-mx,mx],"k--",lw=.8,alpha=.5)
ax.set_xlim(-mx,mx); ax.set_ylim(-mx,mx)
ax.set_xlabel("Z score — GTEx Whole Blood", fontsize=10)
ax.set_ylabel("Z score — GTEx Nerve Tibial", fontsize=10)
ax.set_title("B. Tissue axis (HK)\nWhole Blood vs Nerve Tibial", fontsize=11, fontweight="bold")
rho,tis_n=comp["tissue"][0],comp["tissue"][2]
ax.text(0.04,0.94,f"rho = {rho:+.2f}\nn = {tis_n}", transform=ax.transAxes,
        fontsize=9, va="top", bbox=dict(boxstyle="round", fc="white", ec="grey", alpha=.8))
ax.axhline(0,color="grey",lw=.5); ax.axvline(0,color="grey",lw=.5)

# Panel C: bar comparison
ax=axes[2]
labels=["Source axis\n(eQTLGen vs GTEx)","Tissue axis\n(WB vs Nerve Tibial)"]
hk_vals=[comp["source"][0], comp["tissue"][0]]
fg_vals=[comp["source"][3], comp["tissue"][3]]
x=np.arange(2); w=0.36
b1=ax.bar(x-w/2, hk_vals, w, label="HK (East Asian)", color=C_HK)
b2=ax.bar(x+w/2, fg_vals, w, label="FinnGen (European)", color=C_FG)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("Spearman rho", fontsize=10)
ax.set_title("C. Decomposition rho:\nHK vs FinnGen (Pooled)", fontsize=11, fontweight="bold")
ax.legend(fontsize=8, loc="upper left")
ax.axhline(0,color="grey",lw=.5)
for b,v in zip(b1,hk_vals): ax.text(b.get_x()+b.get_width()/2, v+0.02, f"{v:+.2f}", ha="center", fontsize=8)
for b,v in zip(b2,fg_vals): ax.text(b.get_x()+b.get_width()/2, v+0.02, f"{v:+.2f}", ha="center", fontsize=8)
ax.set_ylim(0,1.05)

plt.tight_layout()
for ext in ["png","pdf","svg"]:
    fig.savefig(os.path.join(OUT,f"Figure9_crosspop_replication.{ext}"), dpi=150 if ext=="png" else None, bbox_inches="tight")
print("Saved Figure9_crosspop_replication.{png,pdf,svg}")
print("HK source rho=%.3f (n=%d), tissue rho=%.3f (n=%d)"%(comp['source'][0],comp['source'][2],comp['tissue'][0],comp['tissue'][2]))
print("FG source rho=%.3f (n=%d), tissue rho=%.3f (n=%d)"%(comp['source'][3],comp['source'][5],comp['tissue'][3],comp['tissue'][5]))

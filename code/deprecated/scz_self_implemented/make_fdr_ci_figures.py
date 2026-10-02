# -*- coding: utf-8 -*-
"""
M4: regenerate FDR-enrichment figures (Figure 3, Figure S8) WITH Wilson 95% CI error bars.

The manuscript's FDR-enrichment rates come from small, curated gene sets (n=16-33 per
group), so every reported rate must carry a 95% CI. This script reads the per-group
tested/FDR-significant counts from enrichment_comparison.csv and draws grouped bar charts
with Wilson score 95% confidence intervals.

Outputs (PNG, publication-clean, white background):
  figures_2026/Figure3_FDR_enrichment_DR_CI.png
  figures_2026/FigureS8_FDR_enrichment_all_CI.png
  figures_2026/FigureS8_{trait}_CI.png
"""
import csv, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = r"E:/workbuddy/BMC Genomics投稿资料/TWAS-repo/data/processed/enrichment_comparison.csv"
OUTDIR = r"E:/workbuddy/BMC Genomics投稿资料/TWAS-repo/figures_2026"
os.makedirs(OUTDIR, exist_ok=True)

Z = 1.959963985  # 95%

def wilson(x, n):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = x / n
    denom = 1 + Z * Z / n
    center = (p + Z * Z / (2 * n)) / denom
    margin = (Z * math.sqrt((p * (1 - p) + Z * Z / (4 * n)) / n)) / denom
    return p * 100, (center - margin) * 100, (center + margin) * 100

# ---- load ----
rows = []
with open(CSV, newline="", encoding="utf-8") as f:
    for d in csv.DictReader(f):
        n_e = int(d["N_Tested_eqtl"]); x_e = int(d["N_FDR005_eqtl"])
        n_g = int(d["N_Tested_gtex"]); x_g = int(d["N_FDR005_gtex"])
        trait = d["Trait"]
        raw = d["Group_gtex"]
        label_map = {
            "30_HOTAIR_Candidate": "Candidate",
            "44_NonCandidate_HOTAIR": "Non-candidate",
            "30_T2DM_Control": "T2DM control",
        }
        grp = label_map.get(raw, raw)
        rows.append(dict(trait=trait, grp=grp, n_e=n_e, x_e=x_e, n_g=n_g, x_g=x_g))

def build(trait):
    sub = [r for r in rows if r["trait"] == trait]
    labels, gp, glo, ghi, ep, elo, ehi, ns = [], [], [], [], [], [], [], []
    for r in sub:
        g_p, g_lo, g_hi = wilson(r["x_g"], r["n_g"])
        e_p, e_lo, e_hi = wilson(r["x_e"], r["n_e"])
        labels.append(r["grp"]); ns.append((r["n_g"], r["n_e"]))
        gp.append(g_p); glo.append(g_p - g_lo); ghi.append(g_hi - g_p)
        ep.append(e_p); elo.append(e_p - e_lo); ehi.append(e_hi - e_p)
    return labels, gp, glo, ghi, ep, elo, ehi, ns

def draw(labels, gp, glo, ghi, ep, elo, ehi, ns, title, fname):
    x = np.arange(len(labels)); w = 0.38
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=300)
    ax.bar(x - w/2, gp, w, yerr=[glo, ghi], capsize=4, color="#C0392B",
           label="GTEx v8", error_kw=dict(ecolor="black", lw=1.1))
    ax.bar(x + w/2, ep, w, yerr=[elo, ehi], capsize=4, color="#2471A3",
           label="eQTLGen", error_kw=dict(ecolor="black", lw=1.1))
    ax.set_ylabel("FDR enrichment rate (%)", fontsize=11)
    ax.set_title(title, fontsize=11.5, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right", fontsize=9.5, frameon=False)
    for i, (g, e) in enumerate(ns):
        ax.annotate(f"n={g}", (x[i]-w/2, gp[i]), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=7, color="#7B241C")
        ax.annotate(f"n={e}", (x[i]+w/2, ep[i]), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=7, color="#1A5276")
    ax.text(0.01, -0.20, "Bars show FDR enrichment rate; error bars = Wilson 95% CI. "
            "Small per-group n (16-33) yields wide intervals.",
            transform=ax.transAxes, fontsize=7.5, style="italic", color="#555")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout()
    p = os.path.join(OUTDIR, fname)
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    print("wrote", p)

# Figure 3: DR only (matches manuscript Figure 3 caption)
labels, gp, glo, ghi, ep, elo, ehi, ns = build("DR")
draw(labels, gp, glo, ghi, ep, elo, ehi, ns,
     "Figure 3 (revised). Source-induced FDR enrichment shift in diabetic retinopathy (DR)\nwith Wilson 95% CI",
     "Figure3_FDR_enrichment_DR_CI.png")

# Combined S8 (all traits in one panel, 3 sub-panels)
fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.4), dpi=300, sharey=True)
for ax, trait in zip(axes, ["DR", "DN", "DPN"]):
    labels, gp, glo, ghi, ep, elo, ehi, ns = build(trait)
    x = np.arange(len(labels)); w = 0.38
    ax.bar(x - w/2, gp, w, yerr=[glo, ghi], capsize=3.5, color="#C0392B", label="GTEx v8")
    ax.bar(x + w/2, ep, w, yerr=[elo, ehi], capsize=3.5, color="#2471A3", label="eQTLGen")
    ax.set_title(trait, fontsize=11, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([l.replace(" ", "\n") for l in labels], fontsize=8)
    ax.set_ylim(0, 100)
    for i, (g, e) in enumerate(ns):
        ax.annotate(f"n={g}", (x[i]-w/2, gp[i]), textcoords="offset points",
                    xytext=(0, 5), ha="center", fontsize=6.5, color="#7B241C")
        ax.annotate(f"n={e}", (x[i]+w/2, ep[i]), textcoords="offset points",
                    xytext=(0, 5), ha="center", fontsize=6.5, color="#1A5276")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    if trait == "DR":
        ax.set_ylabel("FDR enrichment rate (%)", fontsize=11)
axes[0].legend(loc="upper right", fontsize=9, frameon=False)
fig.suptitle("Figure S8 (revised). FDR enrichment across all phenotypes and eQTL weight sources (Wilson 95% CI)",
             fontsize=11.5, fontweight="bold")
fig.text(0.5, 0.01, "Error bars = Wilson 95% CI; per-group n = 16-33.",
         ha="center", fontsize=7.5, style="italic", color="#555")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
p = os.path.join(OUTDIR, "FigureS8_FDR_enrichment_all_CI.png")
fig.savefig(p, bbox_inches="tight"); plt.close(fig)
print("wrote", p)

# per-trait S8 singles too
for trait, cap in [("DN", "diabetic nephropathy (DN)"), ("DPN", "diabetic peripheral neuropathy (DPN)")]:
    labels, gp, glo, ghi, ep, elo, ehi, ns = build(trait)
    draw(labels, gp, glo, ghi, ep, elo, ehi, ns,
         f"FDR enrichment — {cap} — with Wilson 95% CI", f"FigureS8_{trait}_CI.png")

print("DONE")

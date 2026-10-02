"""Stratified robustness bar chart for SCZ 2x2 decomposition."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

J = "_DEPRECATED_scz_self_implemented/_rdat_tmp/scz_robustness.json"
out_png = "_DEPRECATED_scz_self_implemented/_rdat_tmp/Figure_S_robustness.png"
out_pdf = "_DEPRECATED_scz_self_implemented/_rdat_tmp/Figure_S_robustness.pdf"

d = json.load(open(J))
strata = d["stratified"]
order = ["2", "3-4", ">=5"]
labels = ["2 SNPs\n(sparsest)", "3-4 SNPs", ">=5 SNPs\n(densest)"]
src = [strata[b]["source_rho"] for b in order]
tis = [strata[b]["tissue_rho"] for b in order]
ns  = [strata[b]["n"] for b in order]

x = range(len(order))
w = 0.36
fig, ax = plt.subplots(figsize=(7.2, 4.6))
b1 = ax.bar([i - w/2 for i in x], src, w, label="Source axis (eQTLGen vs GTEx-multi)", color="#2c7fb8")
b2 = ax.bar([i + w/2 for i in x], tis, w, label="Tissue axis (GTEx WB vs GTEx NT)", color="#d95f0e")
ax.axhline(0, color="k", lw=0.8)
ax.set_xticks(list(x)); ax.set_xticklabels(labels)
ax.set_ylabel("Spearman \u03c1")
ax.set_ylim(0, 0.8)
ax.set_title("SCZ 2\u00d72 decomposition is stable across GTEx MASHR model sparsity")
for i, (s, t, n) in enumerate(zip(src, tis, ns)):
    ax.text(i - w/2, s + 0.02, "%.2f" % s, ha="center", fontsize=9)
    ax.text(i + w/2, t + 0.02, "%.2f" % t, ha="center", fontsize=9)
    ax.text(i, -0.06, "n=%d" % n, ha="center", fontsize=8, transform=ax.get_xaxis_transform())
ax.legend(loc="upper right", fontsize=9)
ax.text(0.5, -0.18,
        "Pooled: source \u03c1=%.3f (95%% CI %.3f\u2013%.3f); tissue \u03c1=%.3f (95%% CI %.3f\u2013%.3f). n=%d gene\u2013tissue pairs."
        % (d["pooled"]["source_rho"], d["pooled"]["source_ci95"][0], d["pooled"]["source_ci95"][1],
           d["pooled"]["tissue_rho"], d["pooled"]["tissue_ci95"][0], d["pooled"]["tissue_ci95"][1],
           d["pooled"]["source_n"]),
        transform=ax.transAxes, ha="center", fontsize=8.5, color="#444")
plt.tight_layout()
plt.savefig(out_png, dpi=160, bbox_inches="tight")
plt.savefig(out_pdf, bbox_inches="tight")
print("wrote", out_png, "and", out_pdf)

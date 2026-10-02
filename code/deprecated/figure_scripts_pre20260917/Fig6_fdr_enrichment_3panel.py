# -*- coding: utf-8 -*-
"""
重绘手稿 Fig. 6：三面板 (a DR / b DN / c DPN) 的 eQTL 来源 FDR 富集率。
数据来自已验证的逐基因结果（GTEx 稳定式 ACAT-O + eQTLGen 和谐化 BH），非硬编码：
  GTEx   : 2026-09-11-19-30-45/recompute/panel_acat_recompute.csv (P_stable)
  eQTLGen: data/processed/eqtlgen_spredixcan_harmonized_results.csv (pvalue)
BH 分层 = group × phenotype × weight source（与手稿 Table 2 口径一致，已逐格复现 9/9 与 12/12）。
样式复刻原单面板图：红 #C0392B / 蓝 #2471A3，无图内标题，无上右框线。
"""
import io, os, sys, math
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = r'E:\workbuddy\TWAS-eQTL-source-confounding'
ACAT = r'E:\workbuddy\2026-09-11-19-30-45\recompute\panel_acat_recompute.csv'
OUTD = r'E:\workbuddy\BMC Genomics投稿资料\定稿图集_Fig1-8_20260914'
os.makedirs(OUTD, exist_ok=True)

TRAITS = [('DR', 'Diabetic retinopathy (DR)'), ('DN', 'Diabetic nephropathy (DN)'),
          ('DPN', 'Diabetic peripheral neuropathy (DPN)')]
GROUPS = [('Candidate', 'Candidate'), ('44 Non-Candidate', 'Non-candidate'), ('30 T2DM control', 'T2DM control')]
RED, BLUE = '#C0392B', '#2471A3'


def bh_q(p):
    p = np.asarray(p, float); m = len(p)
    o = np.argsort(p); q = p[o] * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(m); out[o] = np.minimum(q, 1.0); return out


def cp(k, n):
    lo = 0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k)
    return 100 * lo, 100 * hi


# ---- GTEx（稳定式 ACAT-O）----
g = pd.read_csv(ACAT).dropna(subset=['P_stable'])
gstats = {}
for (grp, t), s in g.groupby(['Group', 'Phenotype']):
    k = int((bh_q(s.P_stable.values) < 0.05).sum())
    gstats[(grp, t)] = (k, len(s))

# ---- eQTLGen（和谐化 BH）----
e = pd.read_csv(os.path.join(REPO, 'data', 'processed', 'eqtlgen_spredixcan_harmonized_results.csv'))
e = e[e.grp != 'Excluded_NonTestbed'].dropna(subset=['pvalue'])
e['grp2'] = e.grp.replace({'NonCandidate': '44 Non-Candidate', 'T2DM_Control': '30 T2DM control'})
estats = {}
for (grp, t), s in e.groupby(['grp2', 'trait']):
    k = int((bh_q(s.pvalue.values) < 0.05).sum())
    estats[(grp, t)] = (k, len(s))

print('%-8s %-18s %-12s %-12s' % ('Trait', 'Group', 'GTEx k/N', 'eQTLGen k/N'))
for t, _ in TRAITS:
    for grp, lab in GROUPS:
        print('%-8s %-18s %-12s %-12s' % (t, lab, '%s' % (gstats.get((grp, t)),), '%s' % (estats.get((grp, t)),)))

fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.5), dpi=300, sharey=True)
w = 0.38
x = np.arange(len(GROUPS))
for ax, (t, title) in zip(axes, TRAITS):
    gp, gp_lo, gp_hi, ep, ep_lo, ep_hi, lab_g, lab_e = [], [], [], [], [], [], [], []
    for grp, lab in GROUPS:
        kg, ng = gstats[(grp, t)]
        ke, ne = estats[(grp, t)]
        p = 100 * kg / ng; lo, hi = cp(kg, ng)
        gp.append(p); gp_lo.append(p - lo); gp_hi.append(hi - p); lab_g.append('%d/%d' % (kg, ng))
        p = 100 * ke / ne; lo, hi = cp(ke, ne)
        ep.append(p); ep_lo.append(p - lo); ep_hi.append(hi - p); lab_e.append('%d/%d' % (ke, ne))
    ax.bar(x - w / 2, gp, w, yerr=[gp_lo, gp_hi], capsize=3.5, color=RED,
           error_kw=dict(ecolor='black', lw=1.0), label='GTEx v8 ACAT-O')
    ax.bar(x + w / 2, ep, w, yerr=[ep_lo, ep_hi], capsize=3.5, color=BLUE,
           error_kw=dict(ecolor='black', lw=1.0), label='eQTLGen BH-FDR')
    for i in range(len(GROUPS)):
        ax.annotate('%.1f%%\n%s' % (gp[i], lab_g[i]), (x[i] - w / 2, gp[i] + gp_hi[i] + 2.5),
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#7B241C', linespacing=1.25)
        ax.annotate('%.1f%%\n%s' % (ep[i], lab_e[i]), (x[i] + w / 2, ep[i] + ep_hi[i] + 2.5),
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1A5276', linespacing=1.25)
    ax.set_xticks(x); ax.set_xticklabels([lab for _, lab in GROUPS], fontsize=9.5)
    ax.set_title(title, fontsize=10, pad=6)
    ax.set_ylim(0, 108)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=9)
    ax.text(-0.13, 1.055, ax.get_subplotspec().colspan.start == 0 and 'a' or
            ('b' if ax.get_subplotspec().colspan.start == 1 else 'c'),
            transform=ax.transAxes, fontsize=13, fontweight='bold')
axes[0].set_ylabel('FDR enrichment rate  (q < 0.05, %)', fontsize=10.5)
axes[2].legend(loc='upper right', fontsize=9, frameon=False)
fig.text(0.5, -0.045,
         'Bars: FDR enrichment rate (BH q < 0.05 / testable genes). Error bars: 95% Clopper-Pearson exact CI. '
         'BH correction applied within each group x phenotype x weight-source stratum; cross-stratum comparisons are descriptive.',
         ha='center', fontsize=7.6, style='italic', color='#555555')
plt.tight_layout()
for ext in ('png', 'pdf'):
    p = os.path.join(OUTD, 'Fig6.' + ext)
    fig.savefig(p, bbox_inches='tight')
    print('wrote', p, os.path.getsize(p), 'bytes')
plt.close(fig)

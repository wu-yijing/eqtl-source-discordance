# -*- coding: utf-8 -*-
"""D1: 重绘 Fig. 8 —— 三基因集的组织轴 Spearman ρ（全部实时计算，无硬编码值）。"""
import io, sys, os, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.major.width'] = 0.8
plt.rcParams['ytick.major.width'] = 0.8

R = r'E:\workbuddy\TWAS-eQTL-source-confounding'
HK = os.path.join(R, 'data', 'hk_reselect_20260830', 'data')
PR = os.path.join(R, 'data', 'processed')
OUT = r'E:\workbuddy\BMC Genomics投稿资料\定稿图集_Fig1-8_20260914'
TRAITS = ['DR', 'DN', 'DPN']


def rho_ci(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    rho = float(pd.Series(x).corr(pd.Series(y), method='spearman'))
    z = np.arctanh(rho); se = 1 / math.sqrt(n - 3)
    cons = float((np.sign(x) == np.sign(y)).mean())
    return rho, float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se)), n, cons


# ---------- 1. HOTAIR testbed（两组织齐全：50 基因 / 150 对，= Table 3b tissue-only 臂）----------
WB = pd.concat([pd.read_csv(os.path.join(PR, f'gtex_Whole_Blood_{t}.csv')).assign(trait=t) for t in TRAITS], ignore_index=True)
NT = pd.concat([pd.read_csv(os.path.join(PR, f'gtex_Nerve_Tibial_{t}.csv')).assign(trait=t) for t in TRAITS], ignore_index=True)
for d in (WB, NT):
    d['g'] = d.gene.str.upper()
mm = WB[['g', 'trait', 'zscore']].merge(NT[['g', 'trait', 'zscore']], on=['g', 'trait'],
                                        suffixes=('_WB', '_NT')).dropna()
c = mm.groupby('g').size()
mm = mm[mm.g.isin(c[c == 3].index)]
tb = rho_ci(mm.zscore_WB, mm.zscore_NT)
print('HOTAIR testbed : %d 基因 / %d 对  rho=%+.4f CI[%+.3f,%+.3f] 方向一致 %.1f%%' % (mm.g.nunique(), tb[3], tb[0], tb[1], tb[2], tb[4] * 100))

# ---------- 2. Housekeeping control ----------
arr = pd.read_csv(os.path.join(HK, 'arms_all_groups.csv'))
h = arr[(arr.grp == 'HK_v2')].dropna(subset=['z_Whole_Blood', 'z_Nerve_Tibial'])
hk = rho_ci(h.z_Whole_Blood, h.z_Nerve_Tibial)
print('Housekeeping   : %d 基因 / %d 对  rho=%+.4f CI[%+.3f,%+.3f]' % (h.gene.nunique(), hk[3], hk[0], hk[1], hk[2]))

# ---------- 3. PGC3 SCZ genome-wide ----------
scz = pd.read_csv(os.path.join(R, '_DEPRECATED_scz_self_implemented', 'results', 'scz_twas_results_limit0.csv')).dropna(subset=['wbZ', 'ntZ'])
sc = rho_ci(scz.wbZ, scz.ntZ)
print('PGC3 SCZ       : %d 对  rho=%+.4f CI[%+.3f,%+.3f]' % (sc[3], sc[0], sc[1], sc[2]))

SETS = [('PGC3 SCZ\n(genome-wide)', sc, '#2E75B6'),
        ('HOTAIR\ntestbed', tb, '#E8912A'),
        ('Housekeeping\ncontrol', hk, '#5B2C8D')]

# ================= 出图 =================
fig, ax = plt.subplots(figsize=(5.4, 4.3), dpi=300)
for i, (nm, (r_, lo, hi, n, _), col) in enumerate(SETS):
    ax.errorbar(i, r_, yerr=[[r_ - lo], [hi - r_]], fmt='o', ms=8, color=col,
                ecolor=col, elinewidth=1.3, capsize=5, zorder=3)
    lab = 'rho = %.2f' % r_
    if abs(round(r_, 3) - 0.448) < 0.002:
        lab = 'rho = %.2f' % r_
    ax.text(i, hi + 0.035, lab, ha='center', fontsize=7.2, fontweight='bold', color='#222222')
    ax.text(i, 0.030, 'n = %s' % format(n, ','), ha='center', fontsize=6.6, color='#555555')

ax.set_xticks(np.arange(3))
ax.set_xticklabels([s[0] for s in SETS], fontsize=7.6)
ax.set_ylabel('Spearman rho (GTEx Whole_Blood vs Nerve_Tibial)', fontsize=8.6)
ax.set_ylim(0, 0.92)
ax.set_xlim(-0.5, 2.5)
ax.tick_params(axis='y', labelsize=7.6)
ax.tick_params(axis='x', length=0)
for sp in ('top', 'right'):
    ax.spines[sp].set_visible(False)
for sp in ('left', 'bottom'):
    ax.spines[sp].set_color('black'); ax.spines[sp].set_linewidth(0.8)
fig.tight_layout()
for ext, kw in [('png', dict(dpi=600, facecolor='white')), ('pdf', dict(facecolor='white'))]:
    p = os.path.join(OUT, 'Fig8.%s' % ext)
    plt.savefig(p, **kw)
    print('已生成:', p)
plt.close()

print()
print('=== 与图内旧值的差异 ===')
print('  PGC3 SCZ    : 旧 0.509 [0.472, 0.545]  →  新 %.3f [%.3f, %.3f]（CI 由自助法改为 Fisher-z，与图注口径一致）' % (sc[0], sc[1], sc[2]))
print('  HOTAIR      : 旧 0.428 [0.285, 0.553] n=144  →  新 %.3f [%.3f, %.3f] n=%d' % (tb[0], tb[1], tb[2], tb[3]))
print('  Housekeeping: 旧 0.678 [0.5216, 0.7904] n=66  →  新 %.3f [%.3f, %.3f] n=%d（不变）' % (hk[0], hk[1], hk[2], hk[3]))

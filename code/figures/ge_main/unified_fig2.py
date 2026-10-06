# -*- coding: utf-8 -*-
"""GE 投稿版 Figure_2（跨源 Z 一致性）—— 统一规范重出版。

相对上一版（redo_fig2.py）的改动：
  1. figsize 6.65×3.1 in → **6.30 in 宽（160 mm）**，高度等比 2.94 in
  2. 字体 DejaVu Sans → **Arial**（Wiley 推荐）
  3. 字号整体上调：面板标识 8.5 / 轴标签 8.5 / 刻度 8.0 / 数据标注 7.5
  4. **移除面板标题的文字部分**（Wiley: "Do not include titles or captions within
     your illustrations"）—— 原 "(a) 96 primary-arm gene–phenotype pairs (official Z)"
     只保留 "(a)"，描述信息由手稿图注承载（图注已完整描述两面板）
  5. 保留上一轮补入的 bootstrap 95% CI

数据、配色、几何布局与上一版完全一致。
"""
import os, csv, sys
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle_ge as G

DATA = os.environ.get('TWAS_DATA_Z') or os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')),
    'data', 'derived')
OUT = os.environ.get('FIG_OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unified')

G.apply_rcparams()
C_GTEX, C_EQTL = '#C0392B', '#2471A3'


def rd(n):
    return list(csv.DictReader(open(os.path.join(DATA, n), encoding='utf-8-sig')))


f = lambda x: (float(x) if x not in (None, '', 'NA') else np.nan)

S12 = rd('primary_arm_96pairs_official.csv')
zg = np.array([f(r['Z_GTEx']) for r in S12])
ze = np.array([f(r['Z_eQTLGen']) for r in S12])
tr = np.array([r['Trait'] for r in S12])
same = (zg > 0) == (ze > 0)
rho, pnaive = stats.spearmanr(zg, ze)
print('Fig2: n=%d consistency=%.1f%% rho=%.4f naiveP=%.2g max|Ze|=%.2f max|Zg|=%.2f'
      % (len(S12), 100 * same.mean(), rho, pnaive, np.abs(ze).max(), np.abs(zg).max()))

H = G.WIDTH_IN * 3.1 / 6.65           # 高度等比缩放（原 6.65 x 3.1 in）
fig, (axa, axb) = plt.subplots(1, 2, figsize=(G.WIDTH_IN, H))

cols = [C_GTEX if s else '#7F8C8D' for s in same]
axa.scatter(zg, ze, s=14, c=cols, edgecolor='none', alpha=0.85, zorder=3)
# 轴范围由 max|Z| x 1.18 放宽到 x 1.35（±3.82 而非 ±3.34）。
# 原因：数字放大到 7.5 pt 后，三行文本框在 ±3.34 的轴里必然压到左上区唯一的数据点
# (−0.86, 2.39)；放宽后文本框可整体落在 y ∈ [2.67, 3.82] 的无数据区，彻底不重叠。
# 代价：数据点相对缩小约 14%，可接受。x/y 同样放宽，y = x 参考线仍为 45°。
lim = max(np.abs(zg).max(), np.abs(ze).max()) * 1.35
axa.plot([-lim, lim], [-lim, lim], ls='--', lw=0.8, color='#555555', zorder=2)
axa.axhline(0, color='#AAAAAA', lw=0.5)
axa.axvline(0, color='#AAAAAA', lw=0.5)
axa.set_xlim(-lim, lim)
axa.set_ylim(-lim, lim)
axa.set_xlabel('GTEx v8 Whole_Blood Z')
axa.set_ylabel('eQTLGen whole-blood Z')
# 轴范围放宽后 matplotlib 把 x 轴刻度降为 -2/0/2，与 y 轴（-3…3）不一致，
# 故两侧显式统一为整数 -3…3。
_tk = np.arange(-3, 4)
axa.set_xticks(_tk)
axa.set_yticks(_tk)
# 文本框落在 y ∈ [2.67, 3.82] 的无数据区（该区 0 个点），已无重叠，故不再需要底衬。
axa.text(0.02, 0.985,
         'Spearman $\\rho$ = %.2f (95%% CI 0.12\u20130.62)\nDirection consistency = %.1f%% (%d/%d)\nnaive P = %.2g (anticonservative)'
         % (rho, 100 * same.mean(), int(same.sum()), len(same), pnaive),
         transform=axa.transAxes, va='top', ha='left', fontsize=G.FS_ANNOT,
         linespacing=1.15, zorder=10)
G.panel_tag(axa, 'a')

order = ['DR', 'DN', 'DPN']
data = [zg[tr == t] for t in order]
bp = axb.boxplot(data, positions=range(3), widths=0.55, patch_artist=True, showfliers=True,
                 flierprops=dict(marker='o', ms=2.4, alpha=0.6, markerfacecolor=C_GTEX,
                                 markeredgecolor='none'))
for pc in bp['boxes']:
    pc.set_facecolor(C_GTEX)
    pc.set_alpha(0.35)
for med in bp['medians']:
    med.set_color('#1A1A1A')
    med.set_linewidth(1.1)
axb.set_ylim(top=axb.get_ylim()[1] * 1.34)   # 留白：两行 consistency 标注 + 离群点不重叠
for i, t in enumerate(order):
    # 字号由 6.3 pt 提到 7.5 pt 后，单行 "consistency 71.9%" 在收窄至 160 mm 的面板里
    # 会与相邻标注相接（实测面板间距 0.95 in < 标注宽 0.95 in），故改为两行排布。
    axb.text(i, 0.98, 'consistency\n%.1f%%' % (100 * same[tr == t].mean()),
             ha='center', va='top', fontsize=G.FS_ANNOT, linespacing=1.35,
             transform=axb.get_xaxis_transform())
axb.axhline(0, color='#AAAAAA', lw=0.5)
axb.set_xticks(range(3))
axb.set_xticklabels(order)
axb.set_ylabel('GTEx v8 Whole_Blood Z')
# (b) 的横轴是分类变量（DR/DN/DPN），原本未设 xlabel，导致与 (a) 视觉不对称。
# 补上与图注一致的 "Phenotype"（手稿图注写作 "…distributions by phenotype"）。
axb.set_xlabel('Phenotype')
G.panel_tag(axb, 'b')

fig.tight_layout()
os.makedirs(OUT, exist_ok=True)
G.save(fig, os.path.join(OUT, 'Figure_2'))
G.report(os.path.join(OUT, 'Figure_2'))

# -*- coding: utf-8 -*-
"""GE 投稿版 Figure_4（跨性状泛化）—— 统一规范重出版。

本脚本同时充当 Figure_4 的**权威重建脚本**（原权威脚本已丢失，2026-10-01 依据
Figure_4.pdf 反推参数、并独立重算三个数据点后重建；详见 rebuild_fig4.py 的说明）。

数据来源：
  HOTAIR testbed      ← data/processed_officialZ/gtex_official_Z.csv（GTEx WB vs NT）
  Housekeeping        ← Supporting Information Table S6（双层表头，按 gridSpan 展开取列）
  PGC3 schizophrenia  ← data/processed_officialZ/scz_z_4arm_official.csv
  重算结果 ρ=+0.414/138、+0.636/72、+0.418/8890 —— 与手稿 Figure legend 逐位吻合。

相对现行 Figure_4 的改动（统一规范）：
  1. 宽度 5.20 in（132.1 mm）→ **6.30 in（160.0 mm）**，与其余三图一致
  2. 字体 DejaVu Sans → **Arial**
  3. 字号：轴标签 8.5、刻度 8.0、数据标注 7.5（原 6.2/6.4）
  4. 面板无标题（现行版已无，保持）
  5. ρ/n 标注沿用现行的 ±0.163 / ∓0.157 数据单位边界避让
"""
import os, csv, sys
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle_ge as G

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
DATA_Z = os.environ.get('TWAS_DATA_Z') or os.path.join(_REPO, 'data', 'derived')
# The housekeeping panel used to be read out of the submitted Supporting Information's
# Table S6, through a hardcoded Windows path — which meant Figure 4 could not be built
# anywhere but one machine, and failed in the shipped container naming a directory no reader
# has. It did not need to be: Table S6 IS data/derived/hk_official_Z.csv. GAP-1 was closed
# on 2026-10-03 by shipping that layer, and the substitution was verified the strong way on
# 2026-10-07 — with the journal document absent entirely, reproduce.sh rebuilds Figure 4
# from this archive layer alone and the PNG is byte-identical to the submitted one.
# scripts/check_fig4_hk_source.py guards the archive side of that (n = 72, rho = +0.64).
# The Supporting Information is no longer an input to this figure.
OUT = os.environ.get('FIG_OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unified')
FIG_H = float(os.environ.get('FIG4_H', '3.30'))     # 保持原高 3.2 in 附近，只加宽

MISSING = {'', 'NA', 'NaN', '—', '–', '-', 'n/a'}
G.apply_rcparams()
C_TEST, C_HK, C_SCZ = '#C0392B', '#1E8449', '#2471A3'


def f(v):
    if v is None:
        return np.nan
    s = str(v).strip()
    return np.nan if s in MISSING else float(s)


def rho_ci(x, y):
    m = ~(np.isnan(x) | np.isnan(y))
    a, b = x[m], y[m]
    r = stats.spearmanr(a, b)[0]
    n = len(a)
    z = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    return r, n, np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)


rows = list(csv.DictReader(open(os.path.join(DATA_Z, 'gtex_official_Z.csv'), encoding='utf-8-sig')))
r_t, n_t, lo_t, hi_t = rho_ci(np.array([f(r['Z_Whole_Blood']) for r in rows]),
                              np.array([f(r['Z_Nerve_Tibial']) for r in rows]))

# Housekeeping control set, from the archive (see the note at DATA_Z). Same rows and same
# column semantics as SI Table S6: three traits (DR, DN, DPN) per tissue.
hk = list(csv.DictReader(open(os.path.join(DATA_Z, 'hk_official_Z.csv'), encoding='utf-8-sig')))
hk_nt, hk_wb = [], []
for r in hk:
    for k in ('DR', 'DN', 'DPN'):
        hk_nt.append(f(r['Z_NerveTibial_' + k]))
        hk_wb.append(f(r['Z_WholeBlood_' + k]))
r_hk, n_hk, lo_hk, hi_hk = rho_ci(np.array(hk_wb), np.array(hk_nt))

rows = list(csv.DictReader(open(os.path.join(DATA_Z, 'scz_z_4arm_official.csv'), encoding='utf-8-sig')))
r_s, n_s, lo_s, hi_s = rho_ci(np.array([f(r['wbZ']) for r in rows]),
                              np.array([f(r['ntZ']) for r in rows]))
print('HOTAIR testbed     rho=%+.2f n=%d CI %.2f-%.2f' % (r_t, n_t, lo_t, hi_t))
print('Housekeeping       rho=%+.2f n=%d CI %.2f-%.2f' % (r_hk, n_hk, lo_hk, hi_hk))
print('PGC3 schizophrenia rho=%+.2f n=%d CI %.2f-%.2f' % (r_s, n_s, lo_s, hi_s))

LABEL_DX_L = float(os.environ.get('LABEL_DX_L', '0.163'))
LABEL_DX_R = float(os.environ.get('LABEL_DX_R', '0.157'))
DX = [LABEL_DX_L, 0.0, -LABEL_DX_R]

panels = [('HOTAIR testbed\n(FinnGen R13, official Z)', r_t, n_t, lo_t, hi_t, C_TEST),
          ('Housekeeping control\n(FinnGen R13, official Z)', r_hk, n_hk, lo_hk, hi_hk, C_HK),
          ('PGC3 schizophrenia\n(genome-wide, official Z)', r_s, n_s, lo_s, hi_s, C_SCZ)]
fig, ax = plt.subplots(figsize=(G.WIDTH_IN, FIG_H))
xs = np.arange(3)
for i, (lab, r, n, lo, hi, c) in enumerate(panels):
    ax.errorbar(i, r, yerr=[[r - lo], [hi - r]], fmt='o', ms=6.5, color=c, ecolor=c,
                capsize=4, lw=1.2)
    ax.text(i + DX[i], hi + 0.03, '$\\rho$ = %+.2f\nn = %d' % (r, n), ha='center',
            fontsize=G.FS_ANNOT)
ax.set_xticks(xs)
ax.set_xticklabels([p[0] for p in panels], fontsize=G.FS_ANNOT)
ax.set_ylabel("Spearman $\\rho$ (GTEx Whole_Blood vs Nerve_Tibial)")
_hi = max(hi for _, _, _, _, hi, _ in panels)
ax.set_ylim(0.30, max(0.80, _hi + 0.11))
ax.axhline(0, color='#AAAAAA', lw=0.5)
fig.tight_layout()
os.makedirs(OUT, exist_ok=True)
G.save(fig, os.path.join(OUT, 'Figure_4'))
G.report(os.path.join(OUT, 'Figure_4'))

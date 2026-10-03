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
import os, csv, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle_ge as G

DATA_Z = os.environ.get('TWAS_DATA_Z') or r'E:\workbuddy\TWAS-eQTL-source-confounding\data\processed_officialZ'
SI = os.environ.get('SI_DOCX') or r'E:\workbuddy\GE投稿资料\_修订_20260930\Supporting_Information_GenetEpidemiol_20260930.docx'
OUT = os.environ.get('FIG_OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unified')
FIG_H = float(os.environ.get('FIG4_H', '3.30'))     # 保持原高 3.2 in 附近，只加宽

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
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


def cells_of(tr):
    out = []
    for tc in tr.findall(W + 'tc'):
        txt = ' '.join(x.text or '' for x in tc.iter(W + 't')).strip()
        span = 1
        tcPr = tc.find(W + 'tcPr')
        if tcPr is not None:
            gs = tcPr.find(W + 'gridSpan')
            if gs is not None:
                span = int(gs.get(W + 'val'))
        out.extend([txt] * span)
    return out


rows = list(csv.DictReader(open(os.path.join(DATA_Z, 'gtex_official_Z.csv'), encoding='utf-8-sig')))
r_t, n_t, lo_t, hi_t = rho_ci(np.array([f(r['Z_Whole_Blood']) for r in rows]),
                              np.array([f(r['Z_Nerve_Tibial']) for r in rows]))

z = zipfile.ZipFile(SI)
body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
T = None
for tb in [ch for ch in list(body) if ch.tag == W + 'tbl']:
    trs = tb.findall(W + 'tr')
    if 'S-PrediXcan Z, Nerve_Tibial' in ' '.join(cells_of(trs[0])) and \
       'S-PrediXcan Z, Whole_Blood' in ' '.join(cells_of(trs[0])):
        T = trs
        break
h0 = cells_of(T[0])
zi3 = [h0.index('S-PrediXcan Z, Nerve_Tibial') + k for k in range(3)]
zj3 = [h0.index('S-PrediXcan Z, Whole_Blood') + k for k in range(3)]
hk_nt, hk_wb = [], []
for tr in T[2:]:
    c = cells_of(tr)
    if not c or not c[0] or len(c) <= max(zi3 + zj3):
        continue
    for a, b in zip(zi3, zj3):
        hk_nt.append(f(c[a]))
        hk_wb.append(f(c[b]))
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

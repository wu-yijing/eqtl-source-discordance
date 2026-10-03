# -*- coding: utf-8 -*-
"""GE 投稿版 Figure_1（六模块分析框架）—— 统一规范重出版。

相对原版（2026-09-11 fig_rebuild/rebuild_fig1_2_9.py 的 figure1()）的改动：
  1. 输出宽度统一为 160 mm（原 146.8 mm）
  2. 字体 → Arial（原已用 Arial，经 figstyle 统一）
  3. 字号上调：编号 13→12、模块标题 8.6→9.0、说明文字 6.5/6.2→7.5
  4. 保留上一轮修正的模块 6 表号 "(Table S12)"

内容、配色、模块文案、连线弧线与原版逐字一致。
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MplPath

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle_ge as G

OUT = os.environ.get('FIG_OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unified')
G.apply_rcparams()
C_BLUE = '#2166AC'

# tight bbox 会把 7.2 in 的 figure 裁到 5.78 in（比例 0.8028）。
# 目标输出宽 160 mm = 6.2992 in → figsize 宽 = 6.2992 / 0.8028 ≈ 7.847 in
FS_W = float(os.environ.get('FIG1_W', '7.871'))
fig_h = FS_W * 5.0 / 7.2

fig, ax = plt.subplots(figsize=(FS_W, fig_h))
ax.axis('off')
ax.set_xlim(0, 1)
ax.set_ylim(-0.02, 1.0)
mods = [
    ("1", "Testbed construction", "104-gene HOTAIR-interactome panel\n30 candidate + 44 non-candidate\n+ 30 T2DM control"),
    ("2", "Dual-source S-PrediXcan TWAS", "GTEx v8 MASHR (Nerve_Tibial, Whole_Blood)\nvs eQTLGen whole blood (N = 31,684)"),
    ("3", "Cross-source agreement", "Spearman rho on Z-scores\npairwise direction consistency"),
    ("4", "Two-axis partition", "diagnostic heuristic (not structural)\nresource / sample-size axis\ntissue-context axis"),
    ("5", "Calibration & replication", "30 disease-agnostic housekeeping controls\nFinnGen R13 vs UK Biobank (DR)"),
    ("6", "Evidence integration", "STREGA-based TWAS reporting checklist\n(Table S12)"),
]
y0, h, w = 0.90, 0.128, 0.44
H4 = h + 0.024
hh = lambda k: (H4 if k == 3 else h)
for i, (num, title, sub) in enumerate(mods):
    y = y0 - i * (h + 0.028)
    col = 0.04 if i % 2 == 0 else 0.52
    ax.add_patch(FancyBboxPatch((col, y - hh(i)), w, hh(i),
                                boxstyle="round,pad=0.008,rounding_size=0.018",
                                fc="#EEF3FA" if i % 2 == 0 else "#F6F6F6",
                                ec="#5B7FA6", lw=1.0))
    ax.text(col + 0.028, y - h * 0.34, num, fontsize=12, fontweight="bold", color=C_BLUE, va="center")
    ax.text(col + 0.075, y - h * 0.30, title, fontsize=G.FS_MODTITLE, fontweight="bold", va="center")
    _fs, _ls, _dy = (7.2, 1.25, h * 0.74 - H4 * 0.677) if i == 3 else (G.FS_BODY, 1.45, 0.0)
    ax.text(col + 0.075, y - h * 0.74 + _dy, sub, fontsize=_fs, color="#444444",
            va="center", linespacing=_ls)
for i in range(len(mods) - 1):
    even = (i % 2 == 0)
    yb = y0 - i * (h + 0.028) - hh(i)
    ym = y0 - (i + 1) * (h + 0.028) - h * 0.55
    if even:
        s, c1, c2, e = (0.462, yb), (0.42, yb - 0.048), (0.42, ym), (0.52, ym)
    else:
        s, c1, c2, e = (0.538, yb), (0.58, yb - 0.048), (0.58, ym), (0.48, ym)
    ax.add_patch(FancyArrowPatch(
        path=MplPath([s, c1, c2, e],
                     [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4]),
        arrowstyle="-|>", mutation_scale=10, lw=1.1, color="#5B7FA6"))

os.makedirs(OUT, exist_ok=True)
# Fig.1 需要 bbox_inches='tight' 裁掉流程图外围留白（与原版一致）
for ext in ('png', 'pdf'):
    fig.savefig(os.path.join(OUT, 'Figure_1.' + ext), dpi=G.DPI,
                bbox_inches='tight', transparent=False, facecolor='white')
from PIL import Image as _I
_p = os.path.join(OUT, 'Figure_1.png')
_im = _I.open(_p)
if _im.mode != 'RGB':
    _im.convert('RGB').save(_p, dpi=(G.DPI, G.DPI))
plt.close(fig)
G.report(os.path.join(OUT, 'Figure_1'))

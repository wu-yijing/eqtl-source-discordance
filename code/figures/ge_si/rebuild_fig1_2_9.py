# -*- coding: utf-8 -*-
"""按同行评审意见重建 Figure 1 / 2 / 9。
修复项：
  m1  Fig.1 模块1 文字溢出文本框
  m2  Fig.1 模块6 "(Additional file: Table S7)" -> "Additional file 1: Table S7"
  M8  Fig.1 模块5 "true-negative" -> "disease-agnostic"
  m3  Fig.2 ">75%" 分支标签与统计结论对齐
  m8  Fig.9 红/绿 -> 色盲友好（蓝/橙/紫）
  m9  Fig.1/2/9 输出 600 dpi（原 300 dpi 下有效分辨率不足）
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MplPath

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as F

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
P = json.load(open(os.path.join(HERE, "prep_out.json"), encoding="utf-8"))
F.DPI = 600  # m9：提高栅格分辨率

# 色盲友好替代色（m8）
C_BLUE = "#2166AC"
C_ORANGE = "#E08214"
C_PURPLE = "#5E3C99"


def figure1():
    fig, ax = plt.subplots(figsize=(7.2, 5.0)); ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(-0.02, 1.0)
    mods = [
        ("1", "Testbed construction", "104-gene HOTAIR-interactome panel\n30 candidate + 44 non-candidate\n+ 30 T2DM control"),
        ("2", "Dual-source S-PrediXcan TWAS", "GTEx v8 MASHR (Nerve_Tibial, Whole_Blood)\nvs eQTLGen whole blood (N = 31,684)"),
        ("3", "Cross-source agreement", "Spearman rho on Z-scores\npairwise direction consistency"),
        ("4", "Two-axis decomposition", "diagnostic partition (not structural)\nresource / sample-size axis\ntissue-context axis"),
        ("5", "Calibration & replication", "30 disease-agnostic housekeeping controls\nFinnGen R13 vs UK Biobank (DR)"),
        # 2026-10-01 修正：原写 "(Additional file 1: Table S11)"，但 Supporting Information
        # 的 Table S11 = "Analysis-arm denominators and gene/model availability"（分母表），
        # checklist 实为 Table S12（正文 Discussion 亦有 "…in Table S12, with its completed
        # version for this study given in Table S14"）。同时去掉 "Additional file 1:" 前缀，
        # 与正文全篇裸引 "Table Sxx" 的体例一致。
        ("6", "Evidence integration", "STREGA-based TWAS reporting checklist\n(Table S12)"),
    ]
    y0, h, w = 0.90, 0.128, 0.44
    H4 = h + 0.024          # 2026-09-20 P2-4：模块4 多一行限定语，方框加高（字号不降，仍 >= 6 pt）
    hh = lambda k: (H4 if k == 3 else h)
    for i, (num, title, sub) in enumerate(mods):
        y = y0 - i * (h + 0.028)
        col = 0.04 if i % 2 == 0 else 0.52
        ax.add_patch(FancyBboxPatch((col, y - hh(i)), w, hh(i), boxstyle="round,pad=0.008,rounding_size=0.018",
                                    fc="#EEF3FA" if i % 2 == 0 else "#F6F6F6",
                                    ec="#5B7FA6", lw=1.0))
        ax.text(col + 0.028, y - h * 0.34, num, fontsize=13, fontweight="bold", color=C_BLUE, va="center")
        ax.text(col + 0.075, y - h * 0.30, title, fontsize=8.6, fontweight="bold", va="center")
        # P2-4：模块4 为三行（含 diagnostic partition 限定语）。方框只向下加高，
        # 故锚点须下移并收紧行距，否则三行块会顶到标题。其余模块保持原样。
        _fs, _ls, _dy = (6.2, 1.25, h * 0.74 - H4 * 0.677) if i == 3 else (6.5, 1.45, 0.0)
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
    F.save(fig, os.path.join(OUT, "Figure1"))


def figure2():
    fig, ax = plt.subplots(figsize=(6.6, 6.4)); ax.axis("off")

    def box(x, y, w, h, txt, fc, ec, fs=7.6, bold=False):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.01,rounding_size=0.02",
                                    fc=fc, ec=ec, lw=1.0))
        ax.text(x, y, txt, ha="center", va="center", fontsize=fs,
                fontweight="bold" if bold else "normal", linespacing=1.5)

    def arrow(x1, y1, x2, y2, label=None, rad=0.0, col="#444444"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9,
                                     lw=1.0, color=col, connectionstyle=f"arc3,rad={rad}"))
        if label:
            ax.text((x1 + x2) / 2 + 0.03, (y1 + y2) / 2, label, fontsize=6.6, color="#333333",
                    ha="left", va="center", style="italic")

    box(0.50, 0.955, 0.52, 0.075, "Single-source TWAS\n(report Z, model SNP count, matched SNPs)", "#E8EFF7", C_BLUE, bold=True)
    arrow(0.50, 0.915, 0.50, 0.855)
    box(0.50, 0.805, 0.56, 0.085, "Re-run under a second, independent\neQTL weight source (same GWAS, same pipeline)", "#E8EFF7", C_BLUE)
    arrow(0.50, 0.760, 0.50, 0.700)
    box(0.50, 0.650, 0.52, 0.085, "Compute cross-source concordance\nSpearman rho  +  direction consistency", "#FFF6E5", "#B9770E")
    arrow(0.50, 0.605, 0.50, 0.545)
    box(0.50, 0.495, 0.60, 0.085, "Is the finding direction-consistent\nacross the two eQTL weight sources?", "#F2F2F2", "#555555", bold=True)

    arrow(0.30, 0.450, 0.17, 0.360, rad=0.12)
    arrow(0.50, 0.450, 0.50, 0.360)
    arrow(0.70, 0.450, 0.83, 0.360, rad=-0.12)

    # m3：与 SI Fig. S1 图注对齐（2026-10-03 修正）。
    # 图注与 Table S24 一致：95% band 66.1-68.2% around 67.2%（8,315 complete-case genes，
    # 每基因一次比较）——即 PGC3 SCZ panel-only 臂的方向一致率及其 Clopper-Pearson 精确区间，
    # 口径见 Table S24 表注。此前框内写的 66.4-70.1% 出自 scz_threshold_calibration.py
    # （N=2,511，点估计 68.26%），属另一个（更小的）宇宙，与图注、Table S24 及 Methods 均不符。
    box(0.155, 0.285, 0.245, 0.145, "> 75%\ndirection consistency\n\nAbove the genome-wide\n95% band (66.1-68.2%) -\ntreat as robust",
        "#DFF2E1", "#4D9221", 7.0)
    box(0.500, 0.285, 0.245, 0.145, "60 - 75%\n\nReport the source-induced\ncaveat", "#FFF6E5", "#B9770E", 7.0)
    box(0.845, 0.285, 0.245, 0.145, "< 60%\n\nFlag as\neQTL-source-induced", "#FBE3E1", "#B03A2E", 7.0)

    arrow(0.155, 0.212, 0.155, 0.150)
    arrow(0.500, 0.212, 0.500, 0.150)
    arrow(0.845, 0.212, 0.845, 0.150)

    box(0.155, 0.100, 0.245, 0.095, "Still required:\ncross-cohort replication", "#E8EFF7", C_BLUE, 7.0)
    box(0.500, 0.100, 0.245, 0.095, "Still required:\ncross-cohort replication", "#FFF6E5", "#B9770E", 7.0)
    box(0.845, 0.100, 0.245, 0.095, "Do NOT advance to\nfunctional validation", "#FBE3E1", "#B03A2E", 7.0)

    ax.set_ylim(0.028, 1.015)
    F.save(fig, os.path.join(OUT, "Figure2"))


def figure9():
    """单面板：三个基因集的组织语境轴 rho（色盲友好配色）。"""
    sets = [("PGC3 SCZ\n(genome-wide)", 0.509, [0.472, 0.545], 2511, C_BLUE),
            ("HOTAIR\ntestbed", 0.428, [0.285, 0.553], 144, C_ORANGE),
            ("Housekeeping\ncontrol", 0.678, [0.5216, 0.7904], 66, C_PURPLE)]
    fig, ax = plt.subplots(figsize=(5.6, 4.4))
    x = np.arange(3)
    for i, (nm, r_, ci, n, c) in enumerate(sets):
        ax.errorbar(i, r_, yerr=[[r_ - ci[0]], [ci[1] - r_]], fmt="o", ms=8, color=c,
                    ecolor=c, elinewidth=1.3, capsize=5)
        ax.text(i, ci[1] + 0.035, f"rho = {r_:.2f}", ha="center", fontsize=7.2, fontweight="bold")
        ax.text(i, 0.03, f"n = {n:,}", ha="center", fontsize=6.2, color="#555555")
    ax.set_xticks(x); ax.set_xticklabels([s[0] for s in sets], fontsize=6.8)
    ax.set_ylabel("Spearman rho (GTEx Whole_Blood vs Nerve_Tibial)")
    ax.set_ylim(0, 0.92)
    ax.set_xlim(-0.5, 2.5)
    for lb in ax.get_xticklabels():
        lb.set_fontstyle("normal")
    F.despine(ax)
    fig.tight_layout()
    F.save(fig, os.path.join(OUT, "Figure9"))


if __name__ == "__main__":
    import traceback
    log = []
    for fn in (figure1, figure2, figure9):
        try:
            fn(); log.append("done %s" % fn.__name__)
        except Exception:
            log.append("FAIL %s\n%s" % (fn.__name__, traceback.format_exc()))
    open(os.path.join(HERE, "log.txt"), "w", encoding="utf-8").write("\n".join(log))

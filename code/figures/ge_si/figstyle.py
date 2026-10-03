# -*- coding: utf-8 -*-
"""BMC-style shared plotting utilities."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DPI = 300
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "font.size": 8,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7.5,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#333333",
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
})

# colourblind-safe palette
C_GTEX   = "#C0392B"   # red    - GTEx v8
C_EQTL   = "#2166AC"   # blue   - eQTLGen
C_GREY   = "#7F7F7F"
C_HK     = "#4D9221"   # green  - housekeeping
C_SIG    = "#E08214"   # orange - emphasised
C_LIGHT  = "#DCE6F1"

PHEN = ["DR", "DN", "DPN"]


def panel_label(ax, label, dx=0.0, dy=-0.16):
    """BMC-style lowercase panel label, centred BELOW the axes."""
    ax.text(0.5 + dx, dy, "(%s)" % label, transform=ax.transAxes,
            ha="center", va="top", fontsize=10, fontweight="bold")


def save(fig, path_base):
    """Save at >=300 dpi as PDF (vector) + PNG (raster)."""
    fig.savefig(path_base + ".pdf", dpi=DPI, bbox_inches="tight",
                transparent=False, facecolor="white")
    fig.savefig(path_base + ".png", dpi=DPI, bbox_inches="tight",
                transparent=False, facecolor="white")
    # 2026-09-20：matplotlib 默认写 RGBA，而图集其余图为 RGB（评审 m-14），统一转 RGB。
    from PIL import Image
    _p = path_base + ".png"
    _im = Image.open(_p)
    if _im.mode != "RGB":
        _im.convert("RGB").save(_p, dpi=(DPI, DPI))
    plt.close(fig)


def despine(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def note_unavailable(ax, title, detail):
    """Render an explicit 'source data not archived' notice in a panel."""
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#B03A2E"); s.set_linewidth(1.6); s.set_linestyle("--")
    ax.set_facecolor("#FDF2F0")
    ax.text(0.5, 0.84, "SOURCE DATA NOT ARCHIVED", transform=ax.transAxes,
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#B03A2E")
    ax.text(0.5, 0.62, title, transform=ax.transAxes, ha="center", va="center",
            fontsize=8.0, color="#333333", linespacing=1.5)
    ax.text(0.5, 0.34, detail, transform=ax.transAxes, ha="center", va="center",
            fontsize=6.8, color="#555555", linespacing=1.55)
    ax.text(0.5, 0.07, "Values are quoted from the manuscript-reported analysis\n"
                       "and could not be independently recomputed.", transform=ax.transAxes,
            ha="center", va="center", fontsize=6.6, color="#B03A2E", style="italic",
            linespacing=1.5)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_figS1.py — SI Fig. S1 (the dual-source decision flowchart), self-contained.

WHY THIS FILE EXISTS
====================
`metadata/ARCHIVE_MAP.md` recorded Fig. S1 as "recovered structurally only": the
in-tree generator rebuilds "a different raster family from the one that was
published". Two generators were then recovered and **both were run** for the audit
note in this directory. They emit **3188 x 3076**; the published raster is
**3189 x 3077**. A three-way visual comparison shows the *same* flowchart — the
only textual difference is the `> 75 %` box, and the only other difference is a
low-amplitude, whole-canvas difference whose signature is font rasterisation.

So this file is the drawing code, verbatim from the recovered generator, with the
two strings that the audit found to vary promoted to parameters, and **no**
dependency on the working directory it came from. It is the artefact behind the
finding; run it and compare against `ge_si/published/`.

PROVENANCE
==========
`figure2()` below is verbatim from
`E:\\workbuddy\\2026-08-31-19-21-52\\_build\\make_main_figures.py` (2026-08-31), with:
  * the module-level `import pandas / scipy / json` removed (figure2 uses none of them;
    they were imported for sibling figures);
  * `cal = P["scz_calib"]` dropped — the line was vestigial, `cal` is never read, and it
    was the only reference to the external `prep_out.json`;
  * the `> 75 %` box text and the rendering DPI promoted to parameters.
No coordinate, colour, font size or box geometry was changed.

The in-tree generator `code/figures/ge_si/rebuild_fig1_2_9.py::figure2()` is an
independent implementation of the same flowchart; it also emits 3188 x 3076.

USAGE
=====
    python gen_figS1.py [outdir] [--dpi 600] [--green-text published|legacy|CUSTOM]

    published  "Above the genome-wide\\n95% band (66.1-68.2%) -\\ntreat as robust"
               <- what the published raster shows (measured, see the audit note)
    legacy     "Broadly consistent with\\nthe genome-wide expectation"
               <- what both recovered generators contain as shipped

Then check the result with `verify_figs1.py`, which reproduces every number the
audit note reports.
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402

# --- style, the subset of _build/figstyle.py that figure2 needs ---------------
DPI = 600
plt.rcParams.update({
    "font.family": "sans-serif",
    # Arial first, as the recovered style file has it. Measured consequence:
    # Arial -> 9.379 % of pixels differ from the published raster;
    # DejaVu Sans -> 11.288 %. So the published run resolved Arial.
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "font.size": 8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

GREEN_TEXTS = {
    "published": "> 75%\ndirection consistency\n\nAbove the genome-wide\n95% band (66.1-68.2%) -\ntreat as robust",
    "legacy": "> 75%\ndirection consistency\n\nBroadly consistent with\nthe genome-wide expectation",
}


def save(fig, path_base, dpi):
    fig.savefig(path_base + ".pdf", dpi=dpi, bbox_inches="tight",
                transparent=False, facecolor="white")
    fig.savefig(path_base + ".png", dpi=dpi, bbox_inches="tight",
                transparent=False, facecolor="white")
    plt.close(fig)


def figure2(out_base, green_text, dpi):
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

    box(0.50, 0.955, 0.52, 0.075, "Single-source TWAS\n(report Z, model SNP count, matched SNPs)", "#E8EFF7", "#2166AC", bold=True)
    arrow(0.50, 0.915, 0.50, 0.855)
    box(0.50, 0.805, 0.56, 0.085, "Re-run under a second, independent\neQTL weight source (same GWAS, same pipeline)", "#E8EFF7", "#2166AC")
    arrow(0.50, 0.760, 0.50, 0.700)
    box(0.50, 0.650, 0.52, 0.085, "Compute cross-source concordance\nSpearman rho  +  direction consistency", "#FFF6E5", "#B9770E")
    arrow(0.50, 0.605, 0.50, 0.545)
    box(0.50, 0.495, 0.60, 0.085, "Is the finding direction-consistent\nacross the two eQTL weight sources?", "#F2F2F2", "#555555", bold=True)

    arrow(0.30, 0.450, 0.17, 0.360, rad=0.12)
    arrow(0.50, 0.450, 0.50, 0.360)
    arrow(0.70, 0.450, 0.83, 0.360, rad=-0.12)

    # the one string the audit found to differ between the generators and the publication
    box(0.155, 0.285, 0.245, 0.145, green_text, "#DFF2E1", "#4D9221", 7.0)
    box(0.500, 0.285, 0.245, 0.145, "60 - 75%\n\nSource-induced caveat\nrequired", "#FFF6E5", "#B9770E", 7.0)
    box(0.845, 0.285, 0.245, 0.145, "< 60%\n\nFlag as\neQTL-source-induced", "#FBE3E1", "#B03A2E", 7.0)

    arrow(0.155, 0.212, 0.155, 0.150)
    arrow(0.500, 0.212, 0.500, 0.150)
    arrow(0.845, 0.212, 0.845, 0.150)

    box(0.155, 0.100, 0.245, 0.095, "Still required:\ncross-cohort replication", "#E8EFF7", "#2166AC", 7.0)
    box(0.500, 0.100, 0.245, 0.095, "Still required:\ncross-cohort replication", "#FFF6E5", "#B9770E", 7.0)
    box(0.845, 0.100, 0.245, 0.095, "Do NOT advance to\nfunctional validation", "#FBE3E1", "#B03A2E", 7.0)

    ax.set_ylim(0.028, 1.015)  # top: box-1 upper edge; bottom: tight below box row
    # the bottom calibration note was removed by the author; it lives in the caption
    save(fig, out_base, dpi)


def main():
    ap = argparse.ArgumentParser(description="SI Fig. S1 generator (self-contained)")
    ap.add_argument("outdir", nargs="?", default=".", help="output directory")
    ap.add_argument("--dpi", type=int, default=DPI)
    ap.add_argument("--green-text", default="published",
                    help="published | legacy | a literal string")
    ap.add_argument("--name", default="FigureS1")
    a = ap.parse_args()

    green = GREEN_TEXTS.get(a.green_text, a.green_text)
    os.makedirs(a.outdir, exist_ok=True)
    print("matplotlib %s" % matplotlib.__version__)
    print("dpi        %d" % a.dpi)
    print("green box  %r" % green)
    figure2(os.path.join(a.outdir, a.name), green, a.dpi)
    print("wrote %s/%s.png and .pdf" % (a.outdir, a.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())

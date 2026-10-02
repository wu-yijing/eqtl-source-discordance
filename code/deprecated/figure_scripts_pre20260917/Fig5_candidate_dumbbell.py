# -*- coding: utf-8 -*-
"""Fig. 5 重出脚本（2026-09-14 重写）。

修复内容
--------
旧脚本 `regen_figure6_notitle.py` 读取 `tables/Table1.csv` 与 `data/processed/candidate_comparison_DR.csv`，
二者含 **2026-07-25 版旧管线的 eQTLGen Z**（RNH1 11.617 而权威值 13.318；TUBB 匹配 SNP 146/830 而权威 359/1848），
重跑会画出与手稿不符的图（平均 |ΔZ| 3.33，最大 13.01）。旧脚本已移入 `figure_scripts_旧版_勿用_20260914/`。

本脚本的数据来源（唯一）
------------------------
  * eQTLGen 臂：`data/processed/eqtlgen_spredixcan_harmonized_results.csv`（2026-09-09，权威）
  * GTEx 臂  ：`data/processed/gtex_Nerve_Tibial_DR.csv`
**脚本内不含任何数据型字面量**；`GENE_ORDER` 仅为展示顺序（作图排版选择），不承载数值。

基因集口径
----------
手稿图注：the 11 DR candidate genes with the largest |Z| under eQTLGen weights。
实际口径为：候选组 ∩ DR ∩ **同时具备 GTEx Nerve_Tibial Z 值**，按 |Z_eQTLGen| 降序取前 11。
（YWHAQ 2.231、EIF4H 1.720 的 |Z| 更高但缺 GTEx 值，故第 11 名为 ACTB 1.565。）
脚本会断言所选集合与预期集合一致，数据一旦变化即报错而非静默出图。
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO = r'E:\workbuddy\TWAS-eQTL-source-confounding'
PROC = os.path.join(REPO, 'data', 'processed')
OUTDIR = r'E:\workbuddy\BMC Genomics投稿资料\定稿图集_Fig1-8_20260914'

EQ_FILE = os.path.join(PROC, 'eqtlgen_spredixcan_harmonized_results.csv')
GT_FILE = os.path.join(PROC, 'gtex_Nerve_Tibial_DR.csv')

TRAIT = 'DR'
GROUP = 'Candidate'
N_GENES = 11
# 展示顺序（仅为排版；与已发表图一致，数值一律来自数据）
GENE_ORDER = ['RNH1', 'RPS18', 'RPS25', 'CKAP4', 'TUBB', 'RPLP0',
              'ACTB', 'DDX5', 'RPL13A', 'XRCC6', 'RPS16']

C_GTEX = '#C0392B'
C_EQTL = '#2471A3'
THRESHOLDS = (1.96, 2.89)   # 图内虚线参考线（与 Methods 报告的固定 |Z| 阈值一致）

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.linewidth'] = 0.8


def load():
    eq = pd.read_csv(EQ_FILE)
    gt = pd.read_csv(GT_FILE)
    for d in (eq, gt):
        d['G'] = d.gene.str.upper()
    return eq, gt


def select(gt):
    """返回 (选中基因列表按 |Z_eQTLGen| 降序, 完整候选表)"""
    cand = gt[(gt.grp == GROUP) & (gt.trait == TRAIT)].copy()
    cand = cand.sort_values('zscore', key=lambda s: -s.abs())
    return cand


def main():
    eq, gt = load()
    cand = select(eq)

    gtx = gt[gt.trait == TRAIT][['G', 'zscore']].rename(columns={'zscore': 'Z_GTEx'})
    m = cand[['G', 'gene', 'zscore', 'n_snps_model', 'n_snps_matched']].merge(gtx, on='G', how='left')
    print('候选组(gene) DR 共 %d 个；其中有 GTEx Nerve_Tibial Z 的 %d 个'
          % (len(m), m.Z_GTEx.notna().sum()))

    plot = m[m.Z_GTEx.notna()].head(N_GENES).copy()
    got = set(plot.gene)
    expect = set(GENE_ORDER)
    print('按 |Z_eQTLGen| 降序的前 %d 个（限有 GTEx 值者）: %s' % (N_GENES, list(plot.gene)))
    assert got == expect, '所选基因集与预期不一致：多 %s / 缺 %s' % (got - expect, expect - got)
    print('✅ 基因集与已发表 Fig. 5 一致')

    plot = plot.set_index('gene').loc[GENE_ORDER].reset_index()
    plot['Z_eQTLGen'] = plot.zscore

    print()
    print('=== 出图数值（全部来自数据）===')
    print('%-8s %10s %10s %10s %10s' % ('gene', 'eQTLGen', 'GTEx', 'n_model', 'n_matched'))
    for _, r in plot.iterrows():
        print('%-8s %+10.2f %+10.2f %10d %10d'
              % (r.gene, r.Z_eQTLGen, r.Z_GTEx, r.n_snps_model, r.n_snps_matched))

    # 与已发表值的一致性自检
    PUB = {'RNH1': (+13.3, +13.8), 'RPS18': (+13.4, +6.8), 'RPS25': (+2.8, +3.8), 'CKAP4': (+4.8, -3.2),
           'TUBB': (+48.5, +2.8), 'RPLP0': (+2.9, +1.9), 'ACTB': (+1.6, -1.8), 'DDX5': (-3.9, +1.2),
           'RPL13A': (+3.3, -0.8), 'XRCC6': (+3.9, +0.4), 'RPS16': (-2.3, -0.1)}
    bad = 0
    for _, r in plot.iterrows():
        pe, pg = PUB[r.gene]
        if round(r.Z_eQTLGen, 1) != pe or round(r.Z_GTEx, 1) != pg:
            bad += 1
            print('  !! %s 与已发表值不符：eQTLGen %.2f vs %.1f ; GTEx %.2f vs %.1f'
                  % (r.gene, r.Z_eQTLGen, pe, r.Z_GTEx, pg))
    print('  与已发表图 5 的 22 个数值比对：%s' % ('全部一致' if bad == 0 else '%d 项不符' % bad))

    # ---------------- 出图 ----------------
    n = len(plot)
    fig, ax = plt.subplots(figsize=(7.0, 3.80), dpi=300)
    y = np.arange(n)[::-1]
    bh, off = 0.36, 0.20

    ax.barh(y + off, plot.Z_GTEx, height=bh, color=C_GTEX, edgecolor='black', linewidth=0.5, zorder=3)
    ax.barh(y - off, plot.Z_eQTLGen, height=bh, color=C_EQTL, edgecolor='black', linewidth=0.5, zorder=3)

    for yi, g_, ve, vg in zip(y, plot.gene, plot.Z_eQTLGen, plot.Z_GTEx):
        for val, dy in ((vg, off), (ve, -off)):
            ax.text(val + (0.6 if val >= 0 else -0.6), yi + dy, '%+.1f' % val,
                    ha='left' if val >= 0 else 'right', va='center', fontsize=7.4, color='#333333', zorder=5)

    ax.axvline(0, color='black', lw=1.0, zorder=2)
    for t in THRESHOLDS:
        for s in (-1, 1):
            ax.axvline(s * t, color='#888888', ls=(0, (1.6, 1.6)), lw=0.9, zorder=1)

    ax.set_yticks(y)
    ax.set_yticklabels(plot.gene, fontsize=9)
    ax.set_ylim(-0.75, n - 0.25)
    ax.set_xlim(-11.5, 52.5)
    ax.set_xticks(np.arange(-10, 51, 10))
    ax.set_xlabel('S-PrediXcan TWAS Z-score (DR)', fontsize=10)
    ax.tick_params(axis='x', labelsize=8.5)
    ax.tick_params(axis='y', length=0)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        ax.spines[sp].set_color('black')
        ax.spines[sp].set_linewidth(0.8)

    ax.legend(handles=[Line2D([0], [0], marker='s', color='w', markerfacecolor=C_GTEX, markersize=9,
                              label='GTEx v8 Nerve_Tibial'),
                       Line2D([0], [0], marker='s', color='w', markerfacecolor=C_EQTL, markersize=9,
                              label='eQTLGen')],
              loc='lower right', fontsize=8.5, frameon=False)

    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.175, top=0.975)
    for ext, kw in (('png', dict(dpi=600, facecolor='white')), ('pdf', dict(facecolor='white'))):
        p = os.path.join(OUTDIR, 'Fig5.%s' % ext)
        plt.savefig(p, **kw)
        print('已生成:', p)
    plt.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())

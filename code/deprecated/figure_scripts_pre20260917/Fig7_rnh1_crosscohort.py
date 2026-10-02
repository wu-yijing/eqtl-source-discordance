# -*- coding: utf-8 -*-
"""Fig. 7 重出脚本（2026-09-16 更新：第二队列由 ieu-b-4803 换为 GCST90043640）。

2026-09-16 变更
--------------
原 panel (b) 的第二队列是 `ieu-b-4803`。该数据集编号**经核查不存在于 IEU OpenGWAS**
（2026-09-16 对全库 50,057 条逐一比对；同批次 `ieu-b-4795`–`ibu-4807` 整段下架），
其 formerly carried Z = +0.95 无数据、无脚本支撑。已按"换真实可核数据集 + 如实披露"处理：
第二队列改为 **UKB GCST90043640**（308 cases / 456,040 controls），
两队列**均用 eQTLGen 全血权重**、**均用未改动的官方 MetaXcan v0.8.1** 重算。

旧脚本 `regen_figure8_rnh1_notitle.py` **不含任何数据读取**：panel (a) 的两组 Z
（gtex_z / eqtl_z）与 panel (b) 的五项研究 Z 全部写死，且取值已过期。
旧脚本已移入 `figure_scripts_旧版_勿用_20260914/`。

本脚本的数据来源
----------------
  * panel (a) GTEx 臂  ：`data/processed/gtex_Nerve_Tibial_{DR,DN,DPN}.csv`
  * panel (a) eQTLGen  ：`data/processed/eqtlgen_spredixcan_harmonized_results.csv`
  * panel (b) 两队列 Z ：`data/processed/ukb_dr_official/RNH1_official_metaxcan_Z.csv`
    （FinnGen R13 DR 与 UKB GCST90043640，均为 eQTLGen 权重 + 官方 MetaXcan v0.8.1）
  * panel (b) 的合并统计量（Q / I² / τ / SE / 95% PI）**由两个队列 Z 实时推导**

⚠️ panel (a) 仍读取两个臂的**作者实现**输出；这两个臂的官方化重算在另一批次完成，
   完成后本脚本的 panel (a) 才会自动更新。**在此之前不要出图**（否则 panel(a) 与 panel(b)
   会对同一量给出互相矛盾的数值）。
**脚本内不含任何数据型字面量**（PIS 相关常数除外，均注明来源）。

口径说明
--------
方法 2.10：合并 Z 为两队列 Z 的**算术平均**（各队列按单位方差 SE = 1 输入），
故 pooled = (+2.3091 + 0.7225)/2 = +1.516；SE 依随机效应模型（含 τ²）计算。
√N_e 加权的敏感性重算见 `scripts/python/m6_ne_weighted_sensitivity.py`。
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
TABS5 = os.path.join(REPO, 'tables', 'TableS5.csv')
UKB_OFFICIAL = os.path.join(PROC, 'ukb_dr_official', 'RNH1_official_metaxcan_Z.csv')
GENE = 'RNH1'
PHENOS = ['DR', 'DN', 'DPN']

C_GTEX = '#C0392B'
C_EQTL = '#2471A3'
C_POOL = '#666666'
C_PI = '#D68910'
# 第二队列显示标签（数值取自 ukb_dr_official/RNH1_official_metaxcan_Z.csv 的
# 「UKB GCST90043640 / eQTLGen whole blood」行）
UKB_DISPLAY_LABEL = 'UK Biobank\nGCST90043640'
UKB_WEIGHT_ROW = 'eQTLGen whole blood'

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.linewidth'] = 0.8


def read_panel_a():
    gtex, eqtl = {}, {}
    for ph in PHENOS:
        g = pd.read_csv(os.path.join(PROC, 'gtex_Nerve_Tibial_%s.csv' % ph))
        g['G'] = g.gene.str.upper()
        gtex[ph] = float(g.loc[g.G == GENE, 'zscore'].iloc[0])
    e = pd.read_csv(EQ_FILE)
    e['G'] = e.gene.str.upper()
    for ph in PHENOS:
        eqtl[ph] = float(e.loc[(e.G == GENE) & (e.trait == ph), 'zscore'].iloc[0])
    return gtex, eqtl


def read_panel_b():
    """panel (b) 的两队列 Z：均取自官方 MetaXcan 归档，且均为 eQTLGen 权重。"""
    o = pd.read_csv(UKB_OFFICIAL)
    o['GWAS'] = o['GWAS'].astype(str)
    fin = o[(o.GWAS.str.contains('FinnGen')) & (o['Weight source'] == UKB_WEIGHT_ROW)]
    ukb = o[(o.GWAS.str.contains('GCST90043640')) & (o['Weight source'] == UKB_WEIGHT_ROW)]
    if len(fin) != 1 or len(ukb) != 1:
        raise SystemExit('官方归档 %s 中未找到唯一的 RNH1 eQTLGen 权重行' % UKB_OFFICIAL)
    z_fin = float(fin.S_PrediXcan_Z.iloc[0])
    z_ukb = float(ukb.S_PrediXcan_Z.iloc[0])
    n_fin = int(fin.N_e.iloc[0])
    n_ukb = int(ukb.N_e.iloc[0])
    t = pd.read_csv(TABS5)
    ds = t.Dataset.astype(str)
    meta_rows = t[ds.str.contains('FinnGen', na=False) & ds.str.contains(r'k = 2', na=False, regex=True)]
    if len(meta_rows) != 1:
        raise SystemExit('TableS5.csv 中无法唯一定位 k = 2 合并行（命中 %d 行）' % len(meta_rows))
    meta = meta_rows.iloc[0]
    het_rows = t[ds.str.contains('Cochran Q', na=False)]
    if len(het_rows) != 1:
        raise SystemExit('TableS5.csv 中无法唯一定位异质性行（命中 %d 行）' % len(het_rows))
    het = het_rows.iloc[0]
    return (z_fin, z_ukb, n_fin, n_ukb, float(meta.Z_score), str(meta.Note),
            str(het.Dataset), str(het.Z_score), str(het.P_value), str(het.Note))


def dersimonian_laird(z1, z2):
    """两研究、单位方差（SE = 1）的 DL 随机效应。返回全部合并统计量。"""
    y = np.array([z1, z2], float)
    v = np.ones(2)                                    # 单位方差输入（Methods 2.10）
    w = 1.0 / v
    mu_fe = float(np.sum(w * y) / np.sum(w))
    Q = float(np.sum(w * (y - mu_fe) ** 2))
    k = 2
    C = float(np.sum(w) - np.sum(w ** 2) / np.sum(w))
    tau2 = max(0.0, (Q - (k - 1)) / C)
    tau = float(np.sqrt(tau2))
    I2 = max(0.0, (Q - (k - 1)) / Q) * 100 if Q > 0 else 0.0
    ws = 1.0 / (v + tau2)
    pooled = float(np.sum(ws * y) / np.sum(ws))
    se = float(np.sqrt(1.0 / np.sum(ws)))
    pi_lo = pooled - 1.96 * np.sqrt(tau2 + se ** 2)   # 正态近似（k = 2，Higgins t 需 k ≥ 3）
    pi_hi = pooled + 1.96 * np.sqrt(tau2 + se ** 2)
    from scipy import stats as st
    p_q = float(st.chi2.sf(Q, k - 1))
    p_pool = float(2 * st.norm.sf(abs(pooled / se)))
    return dict(Q=Q, tau=tau, I2=I2, pooled=pooled, se=se, pi=(pi_lo, pi_hi),
                p_q=p_q, p_pool=p_pool, ci=(pooled - 1.96 * se, pooled + 1.96 * se))


def main():
    gtex, eqtl = read_panel_a()
    z_fin, z_ukb, n_fin, n_ukb, z_pool_rec, meta_note, q_rec, i2_rec, p_q_rec, note_rec = read_panel_b()

    print('=== panel (a) 数据（全部来自文件）===')
    for ph in PHENOS:
        print('  %-4s GTEx v8 Nerve_Tibial %+7.2f ; eQTLGen %+7.2f' % (ph, gtex[ph], eqtl[ph]))

    print()
    print('=== panel (b) 输入（官方 MetaXcan v0.8.1，均 eQTLGen 权重）===')
    print('  FinnGen R13 (discovery)         Z = %+.4f   N_e = %d' % (z_fin, n_fin))
    print('  %-31s Z = %+.4f   N_e = %d' % (UKB_DISPLAY_LABEL.replace('\n', ' '), z_ukb, n_ukb))

    d = dersimonian_laird(z_fin, z_ukb)
    print()
    print('=== panel (b) 合并统计量（由两个 Z 实时推导）===')
    print('  pooled Z = %+.3f   SE = %.2f   P_pooled = %.3f' % (d['pooled'], d['se'], d['p_pool']))
    print('  Cochran Q = %.2f (P = %.1e)   I² = %.1f%%   τ = %.2f' % (d['Q'], d['p_q'], d['I2'], d['tau']))
    print('  95%% PI = [%+.2f, %+.2f]   合并 95%% CI = [%+.2f, %+.2f]' % (d['pi'][0], d['pi'][1], d['ci'][0], d['ci'][1]))
    print()
    print('=== 与 tables/TableS5.csv 记录值比对 ===')
    import re as _re
    rec = {
        'pooled Z': (round(d['pooled'], 2), round(z_pool_rec, 2)),
        'Q': (round(d['Q'], 1), float(_re.search(r'Q = ([\d.]+)', q_rec).group(1))),
        'I²': (round(d['I2'], 1), float(_re.search(r'([\d.]+)%', i2_rec).group(1))),
        'P_het': (round(d['p_q'], 2), float(p_q_rec)),
        'τ': (round(d['tau'], 2), float(_re.search(r'tau = ([\d.]+)', note_rec).group(1))),
        'SE': (round(d['se'], 2), float(_re.search(r'SE = ([\d.]+)', meta_note).group(1))),
    }
    bad = 0
    for lab, (mine, recorded) in rec.items():
        ok = abs(mine - recorded) < 0.02
        bad += (not ok)
        print('  %-9s 本机 %8.3f   记录 %8.3f   %s' % (lab, mine, recorded, 'OK' if ok else '<<<不符'))
    print('  比对结果:', '全部一致' if bad == 0 else '%d 项不符' % bad)

    # ---------------- 出图 ----------------
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(10.6, 5.3), dpi=300,
                                     gridspec_kw={'width_ratios': [1.0, 1.15], 'wspace': 0.34})
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.115, top=0.94)

    # ---- (a) ----
    x = np.arange(len(PHENOS))
    w = 0.38
    vg = [gtex[p] for p in PHENOS]
    ve = [eqtl[p] for p in PHENOS]
    ax_a.bar(x - w / 2, vg, w, color=C_GTEX, edgecolor='black', linewidth=0.6, zorder=3)
    ax_a.bar(x + w / 2, ve, w, color=C_EQTL, edgecolor='black', linewidth=0.6, zorder=3)
    for i in range(len(PHENOS)):
        ax_a.text(x[i] - w / 2, vg[i] + 0.25, '%+.2f' % vg[i], ha='center', va='bottom',
                  fontsize=8, fontweight='bold', color='#7B241C')
        ax_a.text(x[i] + w / 2, ve[i] + 0.25, '%+.2f' % ve[i], ha='center', va='bottom',
                  fontsize=8, fontweight='bold', color='#1A5276')
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(PHENOS, fontsize=10)
    ax_a.set_ylabel('RNH1 TWAS Z-score', fontsize=10.5)
    ax_a.set_ylim(0, 16)
    ax_a.set_yticks(np.arange(0, 17, 2))
    ax_a.tick_params(axis='y', labelsize=9)
    ax_a.legend(handles=[Line2D([0], [0], marker='s', color='w', markerfacecolor=C_GTEX, markersize=10,
                                label='GTEx v8 Nerve_Tibial'),
                         Line2D([0], [0], marker='s', color='w', markerfacecolor=C_EQTL, markersize=10,
                                label='eQTLGen')],
                loc='upper center', fontsize=9, frameon=False)
    ax_a.text(0.015, 0.965, '(a)', transform=ax_a.transAxes, ha='left', va='top',
              fontsize=12, fontweight='bold', color='black', zorder=10)
    for sp in ('top', 'right'):
        ax_a.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        ax_a.spines[sp].set_color('black')

    # ---- (b) ----
    rows = [('FinnGen R13\n(discovery)', z_fin, C_GTEX, 1.0),
            (UKB_DISPLAY_LABEL, z_ukb, C_EQTL, 1.0)]
    y = np.array([2.0, 1.0])
    for (lab, z, col, se), yi in zip(rows, y):
        ax_b.errorbar(z, yi, xerr=se, fmt='s', ms=9, color=col, ecolor=col,
                      elinewidth=1.4, capsize=5, capthick=1.4, zorder=4)

    # 橙色线 = 95% 预测区间（贯穿），其端帽为 PI 界限
    ax_b.plot(list(d['pi']), [0, 0], color=C_PI, lw=1.8, zorder=2, solid_capstyle='butt')
    for v in d['pi']:
        ax_b.plot([v, v], [-0.10, 0.10], color=C_PI, lw=1.8, zorder=2)
    # 合并估计的 95% CI：仅以短竖线标出两端（与已发表版一致）
    for v in d['ci']:
        ax_b.plot([v, v], [-0.075, 0.075], color='black', lw=1.3, zorder=3)
    ax_b.errorbar(d['pooled'], 0, xerr=d['se'], fmt='s', ms=10, color=C_POOL, ecolor='none', zorder=5)

    ax_b.axvline(0, color='black', ls=(0, (4, 3)), lw=1.0, zorder=1)
    ax_b.set_yticks(list(y) + [0.0])
    ax_b.set_yticklabels([r[0] for r in rows] + ['Random-effects\npooled'], fontsize=9)
    ax_b.set_ylim(-0.55, 2.6)
    lo = min(d['pi'][0], d['ci'][0], z_ukb, z_fin) - 0.6
    hi = max(d['pi'][1], d['ci'][1], z_ukb, z_fin) + 0.6
    ax_b.set_xlim(lo, hi)
    step = 1.0 if (hi - lo) <= 12 else 2.0
    ax_b.set_xticks(np.arange(np.ceil(lo), np.floor(hi) + 1e-9, step))
    ax_b.set_xlabel('RNH1 TWAS Z-score (DR, eQTLGen weights)', fontsize=10.5)
    ax_b.tick_params(axis='x', labelsize=9)
    ax_b.tick_params(axis='y', length=0)
    ax_b.text(0.015, 0.98, '(b)', transform=ax_b.transAxes, ha='left', va='top',
              fontsize=12, fontweight='bold', color='black', zorder=10)
    for sp in ('top', 'right'):
        ax_b.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        ax_b.spines[sp].set_color('black')

    for ext, kw in (('png', dict(dpi=600, facecolor='white')), ('pdf', dict(facecolor='white'))):
        p = os.path.join(OUTDIR, 'Fig7.%s' % ext)
        plt.savefig(p, **kw)
        print('已生成:', p)
    plt.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())

# -*- coding: utf-8 -*-
"""GE 投稿版 Figure_3（轴分解）—— 统一规范重出版。

数据来源与算法照搬 06_redraw_Fig4.py（2026-09-20 生成现行 Figure_3.pdf）：
  (a) 三臂 Spearman ρ 取 Table 2(B) 官方值 0.4904 / 0.4138 / 0.4421（n = 159/138/198），
      CI 用 Fisher-z 精确式；
  (b) Δρ 在 45 基因共同宇宙（135 对）上做配对基因簇 bootstrap（B = 5,000, seed 20260915）。

相对原版的改动：
  1. 宽度 6.65 in（168.9 mm，超版心）→ **6.30 in（160.0 mm）**
  2. 字体 DejaVu Sans → **Arial**
  3. 字号：面板标识 8.5（去描述文字）、轴标签 8.5、刻度 8.0、数据标注 7.5
  4. **移除面板标题的描述部分**（Wiley: 图内不得有标题），只保留 (a)/(b)
  5. x 轴类别标签精简：原三行 '(GTEx Whole_Blood' 峰值宽 0.948 in，收窄后三点间距
     0.92 in（width_ratios 1.5:1.25）会重叠；改为去掉 "GTEx" 前缀、并把括号内容
     改写成 "A vs B" 两行，峰值宽降至 0.85 in。臂的组织定义由手稿图注
     ("definitions and n: Table 2") 承载，信息不丢失。
"""
import os, csv, sys
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle_ge as G

DATA = os.environ.get('TWAS_DATA_Z') or r'E:\workbuddy\TWAS-eQTL-source-confounding\data\processed_officialZ'
OUT = os.environ.get('FIG_OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unified')
G.apply_rcparams()
C_PAN, C_TIS, C_DUA = '#2471A3', '#1E8449', '#C0392B'
rng = np.random.default_rng(20260915)


def rd(n):
    return list(csv.DictReader(open(os.path.join(DATA, n), encoding='utf-8-sig')))


f = lambda x: (float(x) if x not in (None, '', 'NA') else np.nan)
GT = {(r['Gene'], r['Trait']): r for r in rd('gtex_official_Z.csv')}
EQ = {(r['Gene'], r['Trait']): r for r in rd('eqtlgen_official_Z.csv')}
Ze = lambda k: f(EQ[k]['Z_eQTLGen']) if k in EQ else np.nan
Zw = lambda k: f(GT[k]['Z_Whole_Blood']) if k in GT else np.nan
Zn = lambda k: f(GT[k]['Z_Nerve_Tibial']) if k in GT else np.nan
Zm = lambda k: f(GT[k]['Z_multi_tissue']) if k in GT else np.nan

# ---- 共同宇宙：45 基因 / 135 对 ----
allk = sorted(set(GT) | set(EQ))
common = [k for k in allk if not any(np.isnan(v) for v in (Ze(k), Zw(k), Zn(k), Zm(k)))]
genes = sorted(set(k[0] for k in common))
print('共同宇宙: %d 对 / %d 基因' % (len(common), len(genes)))


def rho(x, y):
    m = ~(np.isnan(x) | np.isnan(y))
    return stats.spearmanr(x[m], y[m])[0]


ZK = np.array([[Ze(k), Zw(k), Zn(k), Zm(k)] for k in common])
GK = np.array([k[0] for k in common])
arm_rho = lambda Z: (rho(Z[:, 0], Z[:, 1]), rho(Z[:, 1], Z[:, 2]), rho(Z[:, 0], Z[:, 3]))
p0, t0, d0 = arm_rho(ZK)
print('共同宇宙 ρ: panel=%.4f tissue=%.4f dual=%.4f' % (p0, t0, d0))

# ---- 配对基因簇 bootstrap（B = 5,000, seed 20260915）----
B = 5000
dp, dt = [], []
for _ in range(B):
    gs = rng.choice(genes, size=len(genes), replace=True)
    idx = np.concatenate([np.where(GK == g)[0] for g in gs])
    Zb = ZK[idx]
    p, t, d = arm_rho(Zb)
    dp.append(d - p)
    dt.append(d - t)
dp, dt = np.array(dp), np.array(dt)
res = dict(delta_dual_panel=dict(point=round(float(d0 - p0), 4),
                                 ci95=[round(float(np.percentile(dp, 2.5)), 3),
                                       round(float(np.percentile(dp, 97.5)), 3)],
                                 p=round(float(2 * min((dp > 0).mean(), (dp < 0).mean())), 3)),
           delta_dual_tissue=dict(point=round(float(d0 - t0), 4),
                                  ci95=[round(float(np.percentile(dt, 2.5)), 3),
                                        round(float(np.percentile(dt, 97.5)), 3)],
                                  p=round(float(2 * min((dt > 0).mean(), (dt < 0).mean())), 3)))
print('bootstrap:', {k: v for k, v in res.items()})

# ---- 出图 ----
FULL = [('panel-only\nWhole_Blood vs\neQTLGen', 0.4904, 0.21, 0.55, C_PAN),
        ('tissue-only\nWhole_Blood vs\nNerve_Tibial', 0.4138, 0.27, 0.54, C_TIS),
        ('dual-mismatch\nmulti-tissue vs\neQTLGen', 0.4421, 0.32, 0.55, C_DUA)]
nn = [159, 138, 198]
CIF = []
for r_, n_ in zip([0.4904, 0.4138, 0.4421], nn):
    z = np.arctanh(r_)
    se = 1 / np.sqrt(n_ - 3)
    CIF.append((np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)))

fig, (axa, axb) = plt.subplots(1, 2, figsize=(G.WIDTH_IN, G.WIDTH_IN * 3.0 / 6.65),
                               gridspec_kw={'width_ratios': [1.5, 1.25]})
xs = np.arange(3)
# 字号提到 7.5 pt 后，"ρ = 0.490"（约 0.62 in）居中在端点上会越出轴区
# （端点距默认边界仅 0.089 in）。做法：端点标注向内错开 0.15 数据单位，
# 同时把 xlim 由默认 (-0.1, 2.1) 放宽到 (-0.28, 2.28)，两侧各留约 0.2 单位。
DX3 = [0.15, 0.0, -0.15]
for i, ((lab, r_, lo, hi, c), (clo, chi), n_) in enumerate(zip(FULL, CIF, nn)):
    axa.errorbar(i, r_, yerr=[[r_ - clo], [chi - r_]], fmt='o', ms=6.5, color=c, ecolor=c,
                 capsize=4, lw=1.2)
    axa.text(i + DX3[i], chi + 0.015, '$\\rho$ = %.3f\nn = %d' % (r_, n_), ha='center',
             fontsize=G.FS_ANNOT)
axa.set_xticks(xs)
axa.set_xticklabels([p[0] for p in FULL], fontsize=G.FS_ANNOT)
axa.set_ylabel('Spearman $\\rho$ (Fisher-z 95% CI)')
axa.set_xlim(-0.28, 2.28)
axa.set_ylim(0.15, 0.68)
G.panel_tag(axa, 'a')

rows = [('dual \u2212 panel-only', res['delta_dual_panel'], C_PAN),
        ('dual \u2212 tissue-only', res['delta_dual_tissue'], C_TIS)]
for i, (lab, d, c) in enumerate(rows):
    lo, hi = d['ci95']
    axb.errorbar(d['point'], i, xerr=[[d['point'] - lo], [hi - d['point']]], fmt='s', ms=6.5,
                 color=c, ecolor=c, capsize=4, lw=1.2)
    # "P = 0.78"（约 0.55 in ≈ 0.115 数据单位）置于 CI 右端外侧会超出 x 轴范围；
    # 居中于 point 又会被 x = 0 的虚线穿过（dual−panel 的 point = −0.020）。
    # 处置：置于误差棒正上方、自 x = max(point, 0) + 0.02 起左对齐。
    axb.text(max(d['point'], 0.0) + 0.02, i + 0.30, 'P = %.2f' % d['p'], ha='left',
             va='bottom', fontsize=G.FS_ANNOT)
axb.axvline(0, color='#333333', lw=0.8, ls='--')
axb.set_yticks([0, 1])
axb.set_yticklabels([r_[0] for r_ in rows], fontsize=G.FS_ANNOT)
axb.set_xlabel('$\\Delta\\rho$ (paired gene-cluster bootstrap, B = 5,000)', fontsize=G.FS_ANNOT)
axb.set_xlim(-0.30, 0.30)
axb.set_ylim(-0.85, 1.95)
G.panel_tag(axb, 'b')

fig.tight_layout()
os.makedirs(OUT, exist_ok=True)
G.save(fig, os.path.join(OUT, 'Figure_3'))
G.report(os.path.join(OUT, 'Figure_3'))

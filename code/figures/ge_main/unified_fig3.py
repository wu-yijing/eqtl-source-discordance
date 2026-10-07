# -*- coding: utf-8 -*-
"""GE 投稿版 Figure_3（轴分解）—— 统一规范重出版，并含手稿 rev10 修订。

数据来源与算法：
  (a) 三臂 Spearman ρ 与 95% 区间 —— **gene-cluster bootstrap**（B = 10,000,
      seed = 20260915），与 Table 2(B) / Table S17 的区间口径一致；
  (b) Δρ 森林图四行：
      · 上两行 = 45 基因共同宇宙（配对基因簇 bootstrap，B = 5,000，seed = 20260915），
        与已投稿原版同一代码路径，**数值未变**；
      · 下两行 = 基因组范围 SCZ 基准（8,315 基因）。这两行**读自本仓库自带的
        `code/analyses/reproduction_20261002/results/recompute_scz_results.json`
        的 `delta_rho_scz`**，不在本脚本里写死：该 JSON 由
        `scripts/recompute_scz.py` 第 5 节以三个 genome-wide 层
        （eqz_full / GTEx Whole_Blood / GTEx Nerve_Tibial，均随本仓库分发）
        与 seed = 20260726、B = 10,000 算出。脚本运行时会把它读到的值与
        稿件报告值逐项比对打印，不一致即 fail。

  ⚠ 这两行的取值依赖**输入文件的行序**（基因簇 bootstrap 的索引按行序建立），
  `recompute_scz.py` 的 `load()` 因此明确保留文件行序。按字典序重排会得到
  CI 上界 0.0530 而非本稿的 0.0524 —— 该差异是复算行序造成的，不是稿件误差。

相对上一版（rev9 投稿版）的改动：
  1. (a) 三臂区间由 Fisher-z 精确式改为 **gene-cluster bootstrap**
     （peer-review M5：表注 / 图注 / 正文三处口径原本不一致）
  2. (b) 2 行 → **4 行**，补上此前只出现在正文与表注里的基因组范围两组 Δρ（P2-3）
  3. 面板高度 3.0/6.65 → 3.35/6.65；轴标签由 "Fisher-z 95% CI" 改为
     "gene-cluster bootstrap 95% CI"
  4. 基因组范围两行不再写死常数，改为读 `recompute_scz_results.json`（见上）

保留：160.0 mm 宽（G.WIDTH_IN）、Arial、字号体系、面板标识 (a)/(b) 而**无**面板标题
（Wiley: 图内不得有标题）、x 轴类别标签的两行式改写（理由见下方原版注释）。
"""
import os, csv, sys, json
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle_ge as G

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
DATA = os.environ.get('TWAS_DATA_Z') or os.path.join(REPO, 'data', 'derived')
SCZ_JSON = os.environ.get('SCZ_AXIS_JSON') or os.path.join(
    REPO, 'code', 'analyses', 'reproduction_20261002', 'results', 'recompute_scz_results.json')
OUT = os.environ.get('FIG_OUT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unified')
G.apply_rcparams()
C_PAN, C_TIS, C_DUA = '#2471A3', '#1E8449', '#C0392B'
C_PAN_GW, C_TIS_GW = '#5DADE2', '#52BE80'
rng = np.random.default_rng(20260915)            # testbed Delta-rho  (unchanged)
rng_a = np.random.default_rng(20260915)          # panel (a) cluster CIs


def rd(n):
    return list(csv.DictReader(open(os.path.join(DATA, n), encoding='utf-8-sig')))


f = lambda x: (float(x) if x not in (None, '', 'NA', 'nan') else np.nan)
GT = {(r['Gene'], r['Trait']): r for r in rd('gtex_official_Z.csv')}
EQ = {(r['Gene'], r['Trait']): r for r in rd('eqtlgen_official_Z.csv')}
Ze = lambda k: f(EQ[k]['Z_eQTLGen']) if k in EQ else np.nan
Zw = lambda k: f(GT[k]['Z_Whole_Blood']) if k in GT else np.nan
Zn = lambda k: f(GT[k]['Z_Nerve_Tibial']) if k in GT else np.nan
Zm = lambda k: f(GT[k]['Z_multi_tissue']) if k in GT else np.nan


def rho(x, y):
    return stats.spearmanr(x, y)[0]


# ---------------------------------------------------------------- panel (a)
def arm_ci(pairfn, B=10000):
    keys = sorted(k for k in set(GT) | set(EQ)
                  if not (np.isnan(pairfn(k)[0]) or np.isnan(pairfn(k)[1])))
    genes = sorted(set(k[0] for k in keys))
    g = np.array([k[0] for k in keys])
    x = np.array([pairfn(k)[0] for k in keys])
    y = np.array([pairfn(k)[1] for k in keys])
    r0 = rho(x, y)
    ib = {gg: np.where(g == gg)[0] for gg in genes}
    bs = []
    for _ in range(B):
        gs = rng_a.choice(genes, size=len(genes), replace=True)
        idx = np.concatenate([ib[gg] for gg in gs])
        bs.append(rho(x[idx], y[idx]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return r0, lo, hi, len(keys), len(genes)


A_PAN = arm_ci(lambda k: (Zw(k), Ze(k)))
A_TIS = arm_ci(lambda k: (Zw(k), Zn(k)))
A_DUA = arm_ci(lambda k: (Zm(k), Ze(k)))
print('panel (a) cluster intervals:')
for nm, v in (('panel-only', A_PAN), ('tissue-only', A_TIS), ('dual', A_DUA)):
    print('  %-12s rho=%.4f  CI %.3f-%.3f  n=%d  genes=%d' % (nm, v[0], v[1], v[2], v[3], v[4]))

# ---------------------------------------------------------------- panel (b)
# testbed Delta-rho on the 45-gene common universe -- verbatim from the rev9 script
allk = sorted(set(GT) | set(EQ))
common = [k for k in allk if not any(np.isnan(v) for v in (Ze(k), Zw(k), Zn(k), Zm(k)))]
genes = sorted(set(k[0] for k in common))
ZK = np.array([[Ze(k), Zw(k), Zn(k), Zm(k)] for k in common])
GK = np.array([k[0] for k in common])
arm_rho = lambda Z: (rho(Z[:, 0], Z[:, 1]), rho(Z[:, 1], Z[:, 2]), rho(Z[:, 0], Z[:, 3]))
p0, t0, d0 = arm_rho(ZK)

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
print('panel (b) testbed bootstrap:', res)

# ------------------------------------------- panel (b), genome-wide rows
# Read, do not hardcode. See the module docstring: these values depend on the row
# order of the shipped genome-wide layers, and recompute_scz.py is their generator.
if not os.path.exists(SCZ_JSON):
    raise SystemExit('genome-wide rows: %s not found (set SCZ_AXIS_JSON)' % SCZ_JSON)
with open(SCZ_JSON, encoding='utf-8') as fh:
    _scz = json.load(fh)['delta_rho_scz']


def _pick(word):
    for k, v in _scz.items():
        if word in k.replace('\u2212', '-').replace('\u2013', '-'):
            return dict(point=v['point'], ci95=list(v['ci95']), p=v['p_twosided'])
    raise SystemExit('delta_rho_scz has no entry for %r' % word)


GW = {'panel': _pick('panel'), 'tissue': _pick('tissue')}
REPORTED = {'panel': (-0.0226, [-0.0355, -0.0094], 0.0006),
            'tissue': (0.0265, [0.0002, 0.0524], 0.0484)}
print('panel (b) genome-wide rows, read from %s' % os.path.relpath(SCZ_JSON, REPO))
_bad = 0
for k in ('panel', 'tissue'):
    pt, ci, pv = REPORTED[k]
    got = GW[k]
    same = (abs(got['point'] - pt) < 1e-12 and got['ci95'] == ci and abs(got['p'] - pv) < 1e-12)
    _bad += 0 if same else 1
    print('  %-7s archive: point %+.4f  ci95 %s  P=%.4f   manuscript: %+.4f  %s  %.4f   %s'
          % (k, got['point'], got['ci95'], got['p'], pt, ci, pv, 'ok' if same else 'MISMATCH'))
if _bad:
    raise SystemExit('the archive artefact disagrees with the manuscript on %d genome-wide row(s)' % _bad)

# ---------------------------------------------------------------- draw
fig, (axa, axb) = plt.subplots(1, 2, figsize=(G.WIDTH_IN, G.WIDTH_IN * 3.35 / 6.65),
                               gridspec_kw={'width_ratios': [1.5, 1.35]})
xs = np.arange(3)
DX3 = [0.15, 0.0, -0.15]
FULL = [('panel-only\nWhole_Blood vs\neQTLGen', A_PAN, C_PAN),
        ('tissue-only\nWhole_Blood vs\nNerve_Tibial', A_TIS, C_TIS),
        ('dual-mismatch\nmulti-tissue vs\neQTLGen', A_DUA, C_DUA)]
for i, ((lab, (r_, lo, hi, nn, ng), c), dx) in enumerate(zip(FULL, DX3)):
    axa.errorbar(i, r_, yerr=[[r_ - lo], [hi - r_]], fmt='o', ms=6.5, color=c, ecolor=c,
                 capsize=4, lw=1.2)
    axa.text(i + dx, hi + 0.02, '$\\rho$ = %.3f\nn = %d' % (r_, nn), ha='center',
             fontsize=G.FS_ANNOT)
axa.set_xticks(xs)
axa.set_xticklabels([p[0] for p in FULL], fontsize=G.FS_ANNOT)
axa.set_ylabel('Spearman $\\rho$ (gene-cluster bootstrap 95% CI)')
axa.set_xlim(-0.28, 2.28)
axa.set_ylim(0.14, 0.76)
G.panel_tag(axa, 'a')

ROWS = [
    (3.0, 'testbed\ndual \u2212 panel-only', dict(res['delta_dual_panel'], fmt2=True), C_PAN),
    (2.0, 'testbed\ndual \u2212 tissue-only', dict(res['delta_dual_tissue'], fmt2=True), C_TIS),
    (-0.7, 'genome-wide\ndual \u2212 panel-only', GW['panel'], C_PAN_GW),
    (-1.7, 'genome-wide\ndual \u2212 tissue-only', GW['tissue'], C_TIS_GW),
]
for y, lab, d, c in ROWS:
    lo, hi = d['ci95']
    axb.errorbar(d['point'], y, xerr=[[d['point'] - lo], [hi - d['point']]], fmt='s', ms=6.5,
                 color=c, ecolor=c, capsize=4, lw=1.2)
    lab = '%.2f' % d['p'] if d.get('fmt2') else ('%.4f' % d['p'] if d['p'] < 0.001 else '%.3f' % d['p'])
    axb.text(max(d['point'], 0.0) + 0.02, y + 0.30, 'P = ' + lab,
             ha='left', va='bottom', fontsize=G.FS_ANNOT)
axb.axvline(0, color='#333333', lw=0.8, ls='--')
axb.axhline(-0.35, color='#999999', lw=0.6, ls=':')
axb.set_yticks([r[0] for r in ROWS])
axb.set_yticklabels([r[1] for r in ROWS], fontsize=G.FS_ANNOT)
axb.set_xlabel('$\\Delta\\rho$ (paired bootstrap)', fontsize=G.FS_ANNOT)
axb.set_xlim(-0.30, 0.30)
axb.set_ylim(-2.6, 4.0)
G.panel_tag(axb, 'b')

fig.tight_layout()
os.makedirs(OUT, exist_ok=True)
G.save(fig, os.path.join(OUT, 'Figure_3'))
G.report(os.path.join(OUT, 'Figure_3'))

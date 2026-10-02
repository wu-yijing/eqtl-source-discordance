# -*- coding: utf-8 -*-
"""
================================================================================
 SCZ 全基因组层 + 权重拟合框架层 —— 重算（补齐此前"不可复现"的 8 类量）
================================================================================
输入（只读，全部随本仓库分发）：
  A. data/derived/scz_z_4arm.csv
       四臂 SCZ 逐基因 Z：gene, eqZ, wbZ, ntZ, multiZ
  B. data/derived/genomewide/eqz_full.csv.gz                  eQTLGen 全血逐基因 Z
  C. data/derived/genomewide/gtex_official_Whole_Blood.csv.gz  GTEx v8 MASHR 全血 zscore
  D. data/derived/genomewide/gtex_official_Nerve_Tibial.csv.gz GTEx v8 MASHR 胫神经 zscore
  E. data/derived/genomewide/en_official_en_Whole_Blood.csv.gz GTEx v8 elastic-net 全血 zscore
  F. data/derived/genomewide/en_official_en_Nerve_Tibial.csv.gz GTEx v8 elastic-net 胫神经 zscore

被复算的报告值：
  · Table S24（三臂 SCZ，n = 8,315）
  · Table S17 的经验零分布（available-case 9,048；min|Z| < 0.5）
  · Fig. 4 的 PGC3 SCZ 点（n = 8,890）
  · Results / Discussion 的 Δρ(SCZ) = +0.0265 与 −0.0226 及其 CI / P
  · Table S16 的 9 行框架层对比

固定参数（全部取自论文表注/图注）：
  seed = 20260726, B = 10000   （Table S17 注 / scz_axis_difference_official.json）
  seed = 20260914, B = 10000   （Table S16 注）
================================================================================
"""
# ---------------------------------------------------------------------------
# Path resolution (added 2026-10-02). Satisfies code/README.md rule 3:
# "No absolute paths, no personal directories."
# ---------------------------------------------------------------------------
import os as _os
import sys as _sys


def _repro_pkg():
    d = _os.path.dirname(_os.path.abspath(__file__))
    for _ in range(6):
        if _os.path.exists(_os.path.join(d, 'paths_config.py')):
            return d
        d = _os.path.dirname(d)
    raise RuntimeError('paths_config.py not found above %s' % __file__)


_sys.path.insert(0, _repro_pkg())
import paths_config as PC        # noqa: E402
PC.apply_cli_overrides()
# ---------------------------------------------------------------------------

import os, csv, json, math, hashlib, sys
import numpy as np
from scipy.stats import spearmanr, binomtest, rankdata

OUTD = PC.RESULTS              # 产物统一落在包的 results/（2026-10-02 起）
os.makedirs(OUTD, exist_ok=True)

# All six gene-level Z layers ship with this repository (data/derived/ and
# data/derived/genomewide/); see INPUTS.md section A.
F_A = PC.get('scz_z_4arm')
F_B = PC.get('gw_eqz')
F_C = PC.get('gw_gtex_wb')
F_D = PC.get('gw_gtex_nt')
F_E = PC.get('gw_en_wb')
F_F = PC.get('gw_en_nt')

SEED_AXIS, B_AXIS = 20260726, 10000     # Δρ 与经验零分布自助法
SEED_FW,   B_FW   = 20260914, 10000     # 框架层自助法

LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); LOG.append(s); print(s)

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def load(p, col):
    """读 CSV -> {ensembl(去版本号): float}，保持文件行序（自助法索引依赖该顺序）。"""
    d = {}
    for r in csv.DictReader(PC.open_text(p)):
        try: d[r['gene'].split('.')[0]] = float(r[col])
        except Exception: pass
    return d

def load4(p):
    """读四臂官方 CSV -> 四个 dict（保持行序）。"""
    cols = {k: {} for k in ('eqZ', 'wbZ', 'ntZ', 'multiZ')}
    for r in csv.DictReader(PC.open_text(p)):
        for k in cols:
            v = (r[k] or '').strip()
            if v not in ('', 'NA', 'NaN'): cols[k][r['gene'].split('.')[0]] = float(v)
    return cols

rho  = lambda x, y: float(spearmanr(x, y).statistic)

def sp(a, b):
    """Spearman = 平均秩上的 Pearson。与 scipy.spearmanr 逐位等价，但快 1–2 个数量级，
    用于自助法内循环（本轮需 ~10^5 次秩相关）。"""
    ra = rankdata(a).astype(np.float64); rb = rankdata(b).astype(np.float64)
    ra -= ra.mean(); rb -= rb.mean()
    return float(ra @ rb / math.sqrt((ra @ ra) * (rb @ rb)))

same = lambda x, y: float(np.mean(np.sign(x) == np.sign(y)))
def cp95(k, n):
    ci = binomtest(k, n).proportion_ci(confidence_level=0.95, method='exact')
    return [round(100 * ci.low, 1), round(100 * ci.high, 1)]
def fisher_ci(r, n):
    z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
    return [round(float(np.tanh(z - 1.96 * se)), 4), round(float(np.tanh(z + 1.96 * se)), 4)]

R = {}

# ============================================================ 0. 输入校验
log('=' * 78); log('0. 输入文件校验'); log('=' * 78)
INPUTS = {'scz_z_4arm_official.csv': F_A, 'eqz_full.csv': F_B,
          'official_Whole_Blood.csv': F_C, 'official_Nerve_Tibial.csv': F_D,
          'official_en_Whole_Blood.csv': F_E, 'official_en_Nerve_Tibial.csv': F_F}
R['inputs'] = PC.describe_inputs(INPUTS)
for k, rec in R['inputs'].items():
    extra = ('  content_md5=%s' % rec['content_md5']) if 'content_md5' in rec else ''
    log(f"  {k:32s} md5={rec['md5']} bytes={rec['bytes']:,}{extra}")

# ============================================================ 1. 宇宙与分母
log('\n' + '=' * 78); log('1. 分析宇宙与分母（对照稿件声明）'); log('=' * 78)
A4 = load4(F_A)
eq  = load(F_B, 'eqz');   wb = load(F_C, 'zscore'); nt = load(F_D, 'zscore')
ewb = load(F_E, 'zscore'); ent = load(F_F, 'zscore')

S = lambda *ds: set.intersection(*[set(d) for d in ds])
uni = {
    'A eqZ 模型池 (稿件 10,357)':            len(eq),
    'B complete-case 四臂 (稿件 8,315)':      len(S(eq, wb, nt)),
    'C panel-only available (稿件 9,048)':    len(S(eq, wb)),
    'D tissue-only available (稿件 8,890)':   len(S(wb, nt)),
    'E 两框架全血 (稿件 6,310)':              len(S(ewb, wb)),
    'F 框架共同宇宙 (稿件 4,098)':            len(S(ewb, ent, wb, nt)),
    'G 资源宇宙 U+eQTLGen (稿件 3,910)':      len(S(eq, ewb, ent, wb, nt)),
    'H allele-check (稿件 6,014)':            len(S(ewb, eq)),
}
R['universes'] = {}
for k, v in uni.items():
    R['universes'][k] = v
    log(f'  {k:40s} = {v:,}')
# 官方 CSV 自洽性
m_ok = A4['multiZ'].keys() & A4['wbZ'].keys() & A4['ntZ'].keys()
mx = max(abs((A4['wbZ'][g] + A4['ntZ'][g]) / math.sqrt(2) - A4['multiZ'][g]) for g in m_ok)
log(f'\n  自洽性: multiZ ≡ (wbZ+ntZ)/√2，最大绝对差 = {mx:.2e}（CSV 六位有效数字取整）')
R['multiZ_identity_maxdiff'] = mx

# ============================================================ 2. Table S24 三臂
log('\n' + '=' * 78); log('2. Table S24 —— 三臂 SCZ 方向一致性（complete-case, n = 8,315）'); log('=' * 78)
CC = sorted(S(eq, wb, nt))                      # 与 t1_derived.py 同序（sorted）
E  = np.array([eq[g] for g in CC]); WBv = np.array([wb[g] for g in CC])
NTv = np.array([nt[g] for g in CC]); MUv = (WBv + NTv) / math.sqrt(2)
N = len(CC)
ARMS24 = [('panel-only (eQTLGen vs GTEx WB)', E, WBv, 5584, 67.2, 0.469),
          ('tissue-only (GTEx WB vs NT)',     WBv, NTv, 5551, 66.8, 0.420),
          ('dual (eQTLGen vs GTEx multi)',    E, MUv, 5506, 66.2, 0.447)]
rng = np.random.default_rng(SEED_AXIS)
idx = [rng.integers(0, N, N) for _ in range(B_AXIS)]
R['tableS24'] = {}
for name, x, y, k_rep, rate_rep, rho_rep in ARMS24:
    k = int((np.sign(x) == np.sign(y)).sum()); rate = 100 * k / N
    r = rho(x, y)
    boots = np.array([sp(x[i], y[i]) for i in idx])
    ci = [round(float(np.percentile(boots, 2.5)), 4), round(float(np.percentile(boots, 97.5)), 4)]
    log(f'  {name:32s} k={k}  rate={rate:.2f}% (报告 {k_rep} / {rate_rep}%)  '
        f'rho={r:+.4f} (报告 {rho_rep:+.3f})  boot95% CI {ci}')
    R['tableS24'][name] = dict(n=N, k=k, rate_pct=round(rate, 2), cp95=cp95(k, N),
                               rho=round(r, 4), rho_ci95_boot=ci)
rev = 100 * (1 - R['tableS24']['dual (eQTLGen vs GTEx multi)']['rate_pct'] / 100)
log(f'  dual 臂反转率 = {rev:.2f}%  (Abstract 报告 33.8% 反转)')
R['scz_reversal_pct'] = round(rev, 2)

# ============================================================ 3. Fig.4 SCZ 点
log('\n' + '=' * 78); log('3. Fig. 4 的 PGC3 SCZ 点（tissue 轴, available-case）'); log('=' * 78)
TW = sorted(S(wb, nt))
x3 = np.array([wb[g] for g in TW]); y3 = np.array([nt[g] for g in TW])
r3 = rho(x3, y3); ci3 = fisher_ci(r3, len(TW))
log(f'  n={len(TW):,}  rho={r3:+.4f}  Fisher-z 95% CI {ci3}   (Fig.4: +0.42, n=8,890, CI 0.40–0.44)')
R['fig4_scz'] = dict(n=len(TW), rho=round(r3, 4), ci95_fisherz=ci3)

# ============================================================ 4. Table S17 经验零分布
log('\n' + '=' * 78); log('4. Table S17 经验零分布（panel-only available-case，min|Z| < 0.5）'); log('=' * 78)
AC = sorted(S(eq, wb))
dc_all = same(np.array([eq[g] for g in AC]), np.array([wb[g] for g in AC]))
sub = np.array([min(abs(eq[g]), abs(wb[g])) < 0.5 for g in AC])
sb = np.array([np.sign(eq[g]) == np.sign(wb[g]) for g in AC])[sub]
dc_null = float(sb.mean())
rng0 = np.random.default_rng(SEED_AXIS)
bb = np.array([sb[rng0.integers(0, len(sb), len(sb))].mean() for _ in range(B_AXIS)])
nci = [round(float(np.percentile(bb, 2.5)) * 100, 2), round(float(np.percentile(bb, 97.5)) * 100, 2)]
mnz = np.array([min(abs(eq[g]), abs(wb[g])) for g in AC])
log(f'  available-case 基因数 = {len(AC):,} (报告 9,048)   全 available-case 一致率 = {100*dc_all:.2f}% (报告 67.08%)')
log(f'  min|Z| < 0.5 对 = {int(sub.sum()):,} (报告 3,617)   一致 {int(sb.sum()):,} → {100*dc_null:.2f}% '
    f'(报告 54.9% = 1,987/3,617)')
log(f'  bootstrap 95% CI = {nci}%   (报告 53.33–56.51)')
log(f'  中位 min|Z| = {np.median(mnz):.2f} (报告 1.24)；中位 |Z|(全模型) 见 Table S17 注')
R['empirical_null'] = dict(available_case_genes=len(AC), dc_available_pct=round(100*dc_all, 2),
                           min_absZ_below_0p5_pairs=int(sub.sum()), consistent=int(sb.sum()),
                           dc_pct=round(100*dc_null, 2), boot_ci95_pct=nci,
                           median_min_absZ=round(float(np.median(mnz)), 2))

# ============================================================ 5. Δρ 双轴检验
log('\n' + '=' * 78); log(f'5. Δρ(SCZ) 双轴检验（配对基因重抽样自助法, B={B_AXIS}, seed={SEED_AXIS}）'); log('=' * 78)
multi = {g: (wb[g] + nt[g]) / math.sqrt(2) for g in wb if g in nt}   # 行序同 wb
CCm = [g for g in multi if g in eq]                                   # 与 t1_extra.py 完全同序
Em = np.array([eq[g] for g in CCm]); WBm = np.array([wb[g] for g in CCm])
NTm = np.array([nt[g] for g in CCm]); MUm = np.array([multi[g] for g in CCm])
Nm = len(CCm)
r_p, r_t, r_d = rho(Em, WBm), rho(WBm, NTm), rho(Em, MUm)
log(f'  complete-case N = {Nm:,}')
log(f'  panel-only ρ = {r_p:+.4f}   tissue-only ρ = {r_t:+.4f}   dual ρ = {r_d:+.4f}')
log(f'  （Table S24 同一点估计：0.469 / 0.420 / 0.447）')
rng2 = np.random.default_rng(SEED_AXIS)
d_pt = np.empty(B_AXIS); d_pp = np.empty(B_AXIS)
for b in range(B_AXIS):
    i = rng2.integers(0, Nm, Nm)
    d_pt[b] = sp(Em[i], MUm[i]) - sp(WBm[i], NTm[i])
    d_pp[b] = sp(Em[i], MUm[i]) - sp(Em[i], WBm[i])
ciq = lambda a, q: [round(float(np.percentile(a, q)), 4), round(float(np.percentile(a, 100 - q)), 4)]
p2  = lambda a: round(min(1.0, 2 * min(float(np.mean(a <= 0)), float(np.mean(a >= 0)))), 4)
R['delta_rho_scz'] = {}
for nm, arr, pt, rep_pt, rep_ci, rep_p in [
        ('dual − tissue', d_pt, r_d - r_t, 0.0265, [0.0002, 0.0524], 0.0484),
        ('dual − panel',  d_pp, r_d - r_p, -0.0226, [-0.0355, -0.0094], 0.0006)]:
    log(f'  Δρ({nm}) 点估计 {pt:+.4f} (报告 {rep_pt:+.4f})  95% CI {ciq(arr,2.5)} (报告 {rep_ci})  '
        f'90% CI {ciq(arr,5)}  P={p2(arr)} (报告 {rep_p})')
    R['delta_rho_scz'][nm] = dict(point=round(float(pt), 4), ci95=ciq(arr, 2.5), ci90=ciq(arr, 5), p_twosided=p2(arr))
# 精度比（8–9 倍）
hw_scz = [(R['delta_rho_scz']['dual − panel']['ci95'][1] - R['delta_rho_scz']['dual − panel']['ci95'][0]) / 2,
          (R['delta_rho_scz']['dual − tissue']['ci95'][1] - R['delta_rho_scz']['dual − tissue']['ci95'][0]) / 2]
log(f'\n  SCZ 区间半宽: Δρ(dual−panel)={hw_scz[0]:.4f}  Δρ(dual−tissue)={hw_scz[1]:.4f}')
log(f'  测试台半宽（见主报告 3.5 节）: Δρ(dual−panel)=0.1072  Δρ(dual−tissue)=0.2455')
log(f'  → 宽度比 = {0.1072/hw_scz[0]:.1f}× 与 {0.2455/hw_scz[1]:.1f}×   (Discussion 称"8- to 9-fold narrower")')
R['precision_ratio'] = {'scz_halfwidth': [round(h, 4) for h in hw_scz],
                        'ratio_dual_panel': round(0.1072 / hw_scz[0], 1),
                        'ratio_dual_tissue': round(0.2455 / hw_scz[1], 1)}

# ============================================================ 6. Table S16 框架层
log('\n' + '=' * 78); log(f'6. Table S16 —— 权重拟合框架层（B={B_FW}, seed={SEED_FW}）'); log('=' * 78)
U  = sorted(S(ewb, ent, wb, nt))
UR = [g for g in U if g in eq]
WBonly = sorted(S(ewb, eq))
g_ = lambda d, k: np.array([d[x] for x in k])
e_wb, e_nt = g_(ewb, U), g_(ent, U)
a_wb, a_nt = g_(wb, U),  g_(nt, U)
e_mu, a_mu = (e_wb + e_nt) / math.sqrt(2), (a_wb + a_nt) / math.sqrt(2)
log(f'  共同宇宙 U = {len(U):,} (报告 4,098)   U∩eQTLGen = {len(UR):,} (报告 3,910)   EN_WB∩eQTLGen = {len(WBonly):,} (报告 6,014)')
ARMS16 = [
    ('framework WB  (EN_WB vs MASHR_WB)', e_wb, a_wb, 0.797, [0.781, 0.812], 82.4),
    ('framework NT  (EN_NT vs MASHR_NT)', e_nt, a_nt, 0.806, [0.791, 0.821], 82.7),
    ('framework multi (EN vs MASHR, WB+NT)', e_mu, a_mu, 0.838, [0.825, 0.850], 83.7),
    ('tissue MASHR  (MASHR_WB vs MASHR_NT)', a_wb, a_nt, 0.499, [0.469, 0.528], 69.8),
    ('tissue EN     (EN_WB vs EN_NT)', e_wb, e_nt, 0.525, [0.498, 0.551], 70.7),
]
RES16 = [('resource MASHR (eQTLGen vs MASHR_WB)', g_(eq, UR), g_(wb, UR), 0.582, 72.8),
         ('resource EN    (eQTLGen vs EN_WB)',    g_(eq, UR), g_(ewb, UR), 0.647, 75.3)]
CHK16 = ('allele-check (EN_WB vs eQTLGen, all scored)', g_(ewb, WBonly), g_(eq, WBonly), 0.638, 74.6)

rng3 = np.random.default_rng(SEED_FW)
boot = {k[0]: np.empty(B_FW) for k in ARMS16}
for b in range(B_FW):
    i = rng3.integers(0, len(U), len(U))
    for nm, x, y, _, _, _ in ARMS16:
        boot[nm][b] = sp(x[i], y[i])
R['tableS16'] = {}
log(f'\n  {"arm":38s} {"重算 rho":>9s} {"95% CI":>18s} {"DC%":>7s}   报告')
for nm, x, y, r_rep, ci_rep, dc_rep in ARMS16:
    r = rho(x, y); d = 100 * same(x, y)
    lo, hi = np.percentile(boot[nm], [2.5, 97.5])
    log(f'  {nm:38s} {r:+9.4f} [{lo:+.3f}, {hi:+.3f}] {d:6.1f}%   {r_rep:+.3f} {ci_rep} {dc_rep}%')
    R['tableS16'][nm] = dict(n=len(U), rho=round(r, 4), rho_ci95=[round(float(lo), 4), round(float(hi), 4)],
                             dc_pct=round(d, 2))
for nm, x, y, r_rep, dc_rep in RES16:
    r = rho(x, y); d = 100 * same(x, y)
    log(f'  {nm:38s} {r:+9.4f} {"-":>18s} {d:6.1f}%   {r_rep:+.3f} {dc_rep}%  (n={len(UR):,})')
    R['tableS16'][nm] = dict(n=len(UR), rho=round(r, 4), dc_pct=round(d, 2))
nm, x, y, r_rep, dc_rep = CHK16
r = rho(x, y); d = 100 * same(x, y)
log(f'  {nm:38s} {r:+9.4f} {"-":>18s} {d:6.1f}%   {r_rep:+.3f} {dc_rep}%  (n={len(WBonly):,})')
R['tableS16'][nm] = dict(n=len(WBonly), rho=round(r, 4), dc_pct=round(d, 2))

# 框架-组织 Δρ（配对自助法）
for a, b_, rep, repci, repp in [
        ('framework WB  (EN_WB vs MASHR_WB)', 'tissue MASHR  (MASHR_WB vs MASHR_NT)', 0.298, [0.268, 0.328], '<0.001'),
        ('tissue EN     (EN_WB vs EN_NT)',    'tissue MASHR  (MASHR_WB vs MASHR_NT)', 0.026, [0.002, 0.050], 0.035)]:
    dd = boot[a] - boot[b_]
    pt = R['tableS16'][a]['rho'] - R['tableS16'][b_]['rho']
    log(f'\n  Δρ({a.split()[0]} {a.split()[1]} − tissue MASHR) = {pt:+.4f} '
        f'(报告 {rep:+.3f})  自助法 95% CI {ciq(dd,2.5)} (报告 {repci})  P={p2(dd)} (报告 {repp})')
    R.setdefault('framework_delta', {})[f'{a} minus {b_}'] = dict(
        point=round(float(pt), 4), ci95=ciq(dd, 2.5), p_twosided=p2(dd))
# 框架全血 6,310 宇宙
FULL = sorted(S(ewb, wb))
r_full = rho(g_(ewb, FULL), g_(wb, FULL)); d_full = 100 * same(g_(ewb, FULL), g_(wb, FULL))
log(f'\n  框架 WB 在 6,310 宇宙: ρ = {r_full:+.4f} (报告 0.784), DC = {d_full:.1f}% (报告 82.1%)')
R['framework_full6310'] = dict(n=len(FULL), rho=round(r_full, 4), dc_pct=round(d_full, 2))

json.dump(R, open(os.path.join(OUTD, 'recompute_scz_results.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1, default=str)
open(os.path.join(OUTD, 'recompute_scz_log.txt'), 'w', encoding='utf-8').write('\n'.join(LOG))
log('\n[完成] recompute_scz_results.json / recompute_scz_log.txt 已写出')

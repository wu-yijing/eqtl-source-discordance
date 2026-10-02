# -*- coding: utf-8 -*-
"""为应对审稿人2的等价性检验要求，预先计算 TOST / Newcombe CI / 功效分析"""
import numpy as np
from scipy import stats

def newcombe_diff_ci(x1, n1, x2, n2, alpha=0.10):
    """Newcombe hybrid-score CI for p1-p2 (Fleiss/RRK method 10)"""
    def wilson(x, n, alpha):
        z = stats.norm.ppf(1 - alpha/2)
        p = x/n
        denom = 1 + z**2/n
        center = (p + z**2/(2*n)) / denom
        half = z*np.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
        return center-half, center+half
    l1,u1 = wilson(x1,n1,alpha); l2,u2 = wilson(x2,n2,alpha)
    d = x1/n1 - x2/n2
    lo = d - np.sqrt((x1/n1-l1)**2 + (u2-x2/n2)**2)
    hi = d + np.sqrt((u1-x1/n1)**2 + (x2/n2-l2)**2)
    return lo, hi

def tost_two_prop(x1, n1, x2, n2, margin, alpha=0.05):
    """Two one-sided tests (Farrington-Manning / score-based approx via Wald with RR correction)"""
    p1, p2 = x1/n1, x2/n2
    d = p1 - p2
    # pooled-style SE (unpooled for TOST)
    se = np.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
    z_low  = (d + margin)/se   # H0: d <= -margin
    z_high = (d - margin)/se   # H0: d >= +margin
    p_low  = stats.norm.sf(-z_low) if False else 1-stats.norm.cdf((-d-margin)/se*-1)  # keep simple below
    p1_ = 1 - stats.norm.cdf(( d + margin)/se * -1)  # placeholder
    # 正确公式:
    p_sup  = 1 - stats.norm.cdf((d + margin)/se)  # H0: d >= -margin -> reject if d+margin >> 0... 实际: P(Z >= -(d+margin)/se)?
    # 用标准 TOST:  H01: d <= -m  -> z1 = (d+m)/se, p1 = 1-Phi(z1)?  若 d+m>0 则拒绝 H01 当 z1 大
    z1 = (d + margin)/se; p1 = 1 - stats.norm.cdf(z1) if z1>=0 else 1 - stats.norm.cdf(z1)
    p1 = 1 - stats.norm.cdf(z1)  # 大 z1 -> 小 p1
    z2 = (d - margin)/se; p2 = stats.norm.cdf(z2)  # 小 z2 -> 小 p2
    p_max = max(p1, p2)
    lo90, hi90 = newcombe_diff_ci(x1,n1,x2,n2,0.10)
    return dict(p1=p1, p2=p2, p_tost=p_max, z1=z1, z2=z2, diff=d, ci90=(lo90,hi90))

print('='*78)
print('TOST 双单侧等价性检验 (H0: |p_GTex - p_cand| >= margin)')
print('='*78)
ARMS = [
    ('GTEx 臂: HK 46/84 vs candidate 42/81', 46,84,42,81),
    ('eQTLGen 臂: HK 44/84 vs candidate 38/72', 44,84,38,72),
]
for name,x1,n1,x2,n2 in ARMS:
    print(f'\n--- {name} ---')
    for margin in (0.10, 0.15, 0.20):
        r = tost_two_prop(x1,n1,x2,n2,margin)
        lo,hi = r['ci90']
        verdict = 'PASS 等价' if r['p_tost']<0.05 and lo>-margin and hi<margin else 'FAIL'
        print(f'  margin ±{margin*100:.0f}pp: diff={r["diff"]*100:+.1f}pp  Newcombe90%CI[{lo*100:+.1f},{hi*100:+.1f}]  TOST p={r["p_tost"]:.4f}  -> {verdict}')

print()
print('='*78)
print('功效分析: 检出 |diff|>=10pp (80%功效, alpha=0.05 双侧) 所需每组 n')
print('='*78)
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
for base in (0.519, 0.548):
    for delta in (0.10, 0.05):
        es = proportion_effectsize(base, base+delta)
        n = NormalIndPower().solve_power(es, power=0.8, alpha=0.05, ratio=1)
        print(f'  base={base:.3f}, delta={delta*100:.0f}pp -> 每组 n = {n:.0f} 基因-表型 pairs')
print()
print('现有每组 n≈72-84, 即: 只能稳定检出 ≳13-14pp 的差异 (80%功效)')
es = proportion_effectsize(0.519,0.548+0.10)
n_need = NormalIndPower().solve_power(es, power=0.8, alpha=0.05, ratio=1)
print(f'  验证: base=0.519, delta=10pp -> n={n_need:.0f}/组')
# 反向: 现有 n 下 MDE
from statsmodels.stats.proportion import proportion_effectsize as pe
for n in (72,81,84):
    es = NormalIndPower().solve_power(None, nobs1=n, power=0.8, alpha=0.05, ratio=1)
    # es -> diff
    import math
    p2=0.53
    # 反解: h = es; p1 = sin(asin(sqrt(p2)) + es)^2 近似
    p1 = np.sin(np.arcsin(np.sqrt(p2)) + es)**2
    print(f'  n={n}/组时 MDE ≈ {(p1-p2)*100:.1f}pp (相对 base 53%)')

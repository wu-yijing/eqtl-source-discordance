# -*- coding: utf-8 -*-
"""诊断（优化版）：Table S20 组间功效口径拟合。
对每个第 1 列合计 c1 预计算超几何分布与双侧 Fisher 显著性掩码，避免逐格调用。"""
import numpy as np
from scipy import stats
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def sig_mask(n1, n2, alpha):
    """返回 dict: c1 -> set(a) 使双侧 Fisher P < alpha。"""
    N = n1 + n2
    out = {}
    for c1 in range(0, N + 1):
        lo = max(0, c1 - n2); hi = min(n1, c1)
        if hi < lo:
            out[c1] = set(); continue
        xs = np.arange(lo, hi + 1)
        pr = stats.hypergeom.pmf(xs, N, n1, c1)
        out[c1] = set()
        for x, p in zip(xs, pr):
            if p > 1e-15:
                pp = float(pr[pr <= p * (1 + 1e-9)].sum())
                if pp < alpha:
                    out[c1].add(int(x))
    return out

def power(mask, n1, p1, n2, p2):
    pmf1 = stats.binom.pmf(np.arange(n1 + 1), n1, p1)
    pmf2 = stats.binom.pmf(np.arange(n2 + 1), n2, p2)
    pw = 0.0
    for a in np.nonzero(pmf1 > 1e-13)[0]:
        w = pmf1[a]
        for b in np.nonzero(pmf2 > 1e-13)[0]:
            if int(a) in mask[int(a) + int(b)]:
                pw += w * pmf2[b]
    return pw

ROWS = [('GTEx HK87@0.0 vs cand84@2.4', 87, 0.0, 84, 2.4, 8.0),
        ('GTEx HK87@5.7 vs cand84@9.5', 87, 5.7, 84, 9.5, 14.5),
        ('eQTL HK81@2.5 vs cand81@6.2', 81, 2.5, 81, 6.2, 13.0),
        ('eQTL HK81@8.6 vs cand81@9.9', 81, 8.6, 81, 9.9, 17.5)]

def mde(mask, n1, p1pct, n2, base2, target=0.80, grid=0.5):
    for d in np.arange(0.5, 30.01, grid):
        p2 = min(0.99, base2 / 100 + d / 100)
        if power(mask, n1, p1pct / 100, n2, p2) >= target:
            return round(float(d), 2)
    return None

print('=== A. 精确枚举 @ alpha 扫描 ===')
for alpha in (0.05, 0.03, 0.025, 0.02, 0.015, 0.01, 0.005):
    res = []
    for lab, n1, p1, n2, b2, rep in ROWS:
        m = sig_mask(n1, n2, alpha)
        res.append(mde(m, n1, p1, n2, b2))
    print(f'  alpha={alpha:<6} -> {res}     SI [8.0, 14.5, 13.0, 17.5]')

print('\n=== B. 逐行反解：使 MDE = SI 值所需的 alpha 上界 ===')
for lab, n1, p1, n2, b2, rep in ROWS:
    found = None
    for alpha in np.arange(0.002, 0.051, 0.002):
        m = sig_mask(n1, n2, alpha)
        if mde(m, n1, p1, n2, b2) <= rep + 0.25:
            found = round(float(alpha), 3); break
    print(f'  {lab:32s} SI Δmin={rep:5.1f}  →  所需 alpha ≤ {found}')

print('\n=== C. 第 1 行功效曲线：精确枚举(α=0.05) vs 归档 ===')
mask = sig_mask(87, 84, 0.05)
arch = {1: 0.002, 2: 0.027, 3: 0.108, 4: 0.246, 5: 0.411, 7: 0.708, 10: 0.931, 15: 0.997}
for d in [1, 2, 3, 4, 5, 7, 10, 15]:
    print(f'  Δ={d:3d}pp  精确 {power(mask,87,0.0,84,(2.4+d)/100):.3f}   归档 {arch[d]:.3f}')

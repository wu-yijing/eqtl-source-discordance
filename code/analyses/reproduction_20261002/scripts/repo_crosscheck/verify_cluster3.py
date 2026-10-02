# -*- coding: utf-8 -*-
"""sandwich SE 变体搜索 + 基因标签置换检验；并给出 ICC 的 ANOVA 佐证。"""
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

import csv, math
import numpy as np
from scipy.stats import rankdata, t as tdist, f as fdist

P = PC.get('primary_arm')
rows=list(csv.DictReader(open(P,encoding='utf-8-sig')))
x=np.array([float(r['Z_GTEx']) for r in rows]); y=np.array([float(r['Z_eQTLGen']) for r in rows])
gene=[r['Gene'] for r in rows]; trait=np.array([r['Trait'] for r in rows])
same=np.array([1.0 if str(r['Same']).strip().lower()=='true' else 0.0 for r in rows])
gs=list(dict.fromkeys(gene)); K=len(gs); N=len(rows)
idx=[np.where(np.array(gene)==g)[0] for g in gs]

def prep(a,b):
    ra=rankdata(a)- (len(a)+1)/2.0; rb=rankdata(b)-(len(b)+1)/2.0
    return ra,rb
def rho_of(a,b):
    xa,xb=prep(a,b)
    return float(xa@xb/math.sqrt((xa@xa)*(xb@xb)))
r_obs=rho_of(x,y)

print('='*100); print('A. sandwich SE(ρ) 变体搜索（目标 0.125）'); print('='*100)
xa,xb=prep(x,y); Sxx=xa@xa; Syy=xb@xb
phi_full = xa*xb/math.sqrt(Sxx*Syy) - r_obs/2*(xa*xa/Sxx + xb*xb/Syy)
phi_simple = xa*xb/math.sqrt(Sxx*Syy)
for nm,phi in [('完整影响函数(含 ρ/2 修正)',phi_full),('仅 x̃ỹ 项',phi_simple)]:
    s=sum(phi[i].sum()**2 for i in idx)
    for sc,lab in [(K/(K-1),'×K/(K−1)'),(1.0,'×1'),(N/(N-1),'×N/(N−1)'),(K/(K-1)*N/(N-2),'×K/(K−1)·N/(N−2)')]:
        se=math.sqrt(sc*s)
        mark='  <== 命中' if abs(se-0.125)<2e-4 else ''
        print(f'  {nm:24s} {lab:22s} SE = {se:.4f}{mark}')
print(f'  报告值: 0.125（one-sided P = 0.002 / two-sided 0.004, df 31）')

print()
print('='*100); print('B. ICC 的 ANOVA 佐证（作用于主臂方向一致率）'); print('='*100)
k_g=np.array([same[i].sum() for i in idx]); n_g=np.array([len(i) for i in idx])
grand=same.mean(); mbar=N/K
SSB=float((n_g*(np.array([same[i].mean() for i in idx])-grand)**2).sum()); dfB=K-1; MSB=SSB/dfB
SSW=float(sum(((same[i]-same[i].mean())**2).sum() for i in idx)); dfW=N-K; MSW=SSW/dfW
F=MSB/MSW; pF=float(fdist.sf(F,dfB,dfW))
icc=(MSB-MSW)/(MSB+(mbar-1)*MSW)
print(f'  SSB={SSB:.6f} (df {dfB}) MSB={MSB:.6f}   SSW={SSW:.6f} (df {dfW}) MSW={MSW:.6f}')
print(f'  F({dfB},{dfW}) = {F:.4f}  P = {pF:.4f}')
print(f'  ICC = {icc:+.6f}    DEFF = {1+(mbar-1)*icc:.4f}')
print(f'  含 12 个基因 k_g=3、12 个 k_g=2、6 个 k_g=1、2 个 k_g=0  →  组间差异不显著但不为零')
print(f'  README 记录: MSB 0.278226（一致）/ MSW 0.281250（对不上；若 MSW=0.28125 需 SSW=18，而直算 SSW=12）')
print(f'  自洽性检验：README 自己的 sandwich/naive = {0.1284/0.0880:.2f}× 、jackknife/naive = {0.1367/0.0880:.2f}×'
      f' → 与 ICC≈0/DEFF=1 不相容，与 ICC≈0.14/DEFF≈1.28 相容')

print()
print('='*100); print('C. 基因标签置换检验（B=10000, seed 20260915）'); print('='*100)
# 域内置换：在每个表型内把 eQTLGen 的 Z 在基因间随机重排，保留每基因的对数
traits=list(dict.fromkeys(trait))
for tag,fac in [('RandomState(MT19937)',lambda: np.random.RandomState(20260915)),
                ('default_rng(PCG64)',lambda: np.random.default_rng(20260915))]:
    rng=fac(); B=10000; null=np.empty(B)
    ty={t:np.where(trait==t)[0] for t in traits}
    for b in range(B):
        yp=y.copy()
        for t in traits:
            ii=ty[t]
            sub=np.asarray(gene)[ii]                      # 该表型下的基因名（与 ii 对齐）
            gs_t=list(dict.fromkeys(sub))
            pos={g: np.flatnonzero(sub == g) for g in gs_t}
            order=rng.permutation(len(gs_t))
            for j, g in enumerate(gs_t):
                src = gs_t[order[j]]
                yp[ii[pos[g]]] = y[ii[pos[src]]]
        null[b]=rho_of(x,yp)
    lo,hi=np.percentile(null,2.5),np.percentile(null,97.5)
    Pperm=(np.abs(null)>=abs(r_obs)).mean()
    print(f'  {tag:22s} null 2.5–97.5 pct = {lo:+.3f} to {hi:+.3f}   P = {"<0.001" if Pperm==0 else f"{Pperm:.4f}"}')
print(f'  报告: null 2.5–97.5 percentiles −0.22 to 0.23; P < 0.001')

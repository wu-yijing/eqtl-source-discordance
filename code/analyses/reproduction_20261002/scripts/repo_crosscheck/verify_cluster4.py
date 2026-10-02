# -*- coding: utf-8 -*-
"""sandwich 的回归型 CR1 变体 + 基因标签置换检验（修正版）。"""
import csv, math
import numpy as np
from scipy.stats import rankdata, t as tdist

P=r'E:/workbuddy/eqtl-source-discordance-audit/data/processed_officialZ/primary_arm_96pairs_official.csv'
rows=list(csv.DictReader(open(P,encoding='utf-8-sig')))
x=np.array([float(r['Z_GTEx']) for r in rows]); y=np.array([float(r['Z_eQTLGen']) for r in rows])
gene=np.array([r['Gene'] for r in rows]); trait=np.array([r['Trait'] for r in rows])
gs=list(dict.fromkeys(gene)); K=len(gs); N=len(rows)
idx=[np.where(gene==g)[0] for g in gs]
def prep(a):  return rankdata(a)-(len(a)+1)/2.0
xa=prep(x); xb=prep(y)
Sxx=xa@xa; Syy=xb@xb
r_obs=float(xa@xb/math.sqrt(Sxx*Syy))
print(f'ρ = {r_obs:.6f}   naive Fisher SE(ρ) = {(1-r_obs**2)/math.sqrt(N-3):.4f}')

print()
print('='*100); print('A. 回归型 CR1（cluster-robust）SE'); print('='*100)
slope=float(xa@xb/Sxx)                          # ỹ 对 x̃ 回归
res=xb-slope*xa
for sc,lab in [(K/(K-1),'×K/(K−1)'), ((K/(K-1))*((N-1)/(N-2)),'×K/(K−1)·(N−1)/(N−2)'), (1.0,'×1')]:
    meat=sum(res[i].sum()**2 for i in idx)
    se_slope=math.sqrt(sc*meat/Sxx**2)
    se_rho=se_slope*math.sqrt(Sxx/Syy)
    z=r_obs/se_rho
    print(f'  CR1 {lab:26s} SE(ρ) = {se_rho:.4f}  (SE(slope)={se_slope:.5f})  '
          f'one-sided {tdist.sf(z,K-1):.4f}  two-sided {2*tdist.sf(abs(z),K-1):.4f}')
print(f'  报告 SE = 0.125，one-sided 0.002 / two-sided 0.004（df 31）')
# 是否就是 bootstrap SD？
print()
print('='*100); print('B. 对照：基因簇自助法 ρ 的 SD（B=10000）'); print('='*100)
for tag,fac in [('MT19937',lambda: np.random.RandomState(20260915)),('PCG64',lambda: np.random.default_rng(20260915))]:
    rng=fac(); B=10000; R=np.empty(B)
    for b in range(B):
        pick=[gs[j] for j in rng.choice(K,size=K,replace=True)]
        ii=np.concatenate([idx[j] for j in pick])
        a=prep(x[ii]); c=prep(y[ii])
        R[b]=float(a@c/math.sqrt((a@a)*(c@c)))
    print(f'  {tag:8s} bootstrap SD(ρ) = {R.std(ddof=1):.4f}   (SE 候选)')
print(f'  报告 sandwich 0.125 / jackknife 0.137（已由 delete-one-gene jackknife 逐位复现为 0.1367）')

print()
print('='*100); print('C. 基因标签置换检验（B=10000, seed 20260915）'); print('='*100)
traits=list(dict.fromkeys(trait))
M={t:np.array([np.where((gene==g)&(trait==t))[0][0] for g in gs]) for t in traits}
for tag,fac in [('RandomState(MT19937)',lambda: np.random.RandomState(20260915)),
                ('default_rng(PCG64)',lambda: np.random.default_rng(20260915))]:
    rng=fac(); B=10000; null=np.empty(B)
    for b in range(B):
        yp=y.copy()
        for t in traits:
            m=M[t]; yp[m]=y[m][rng.permutation(K)]
        a=prep(x); c=prep(yp)
        null[b]=float(a@c/math.sqrt((a@a)*(c@c)))
    lo,hi=np.percentile(null,2.5),np.percentile(null,97.5)
    Pperm=float((np.abs(null)>=abs(r_obs)).mean())
    print(f'  {tag:22s} null 2.5–97.5 pct = {lo:+.3f} to {hi:+.3f}   P = {"< 0.001" if Pperm==0 else f"{Pperm:.4f}"}')
print(f'  报告: null 2.5–97.5 percentiles −0.22 to 0.23; P < 0.001')

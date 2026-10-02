# -*- coding: utf-8 -*-
"""主臂簇稳健性（仓库 README §Cluster-Robustness / AF1 Table S16）逐项核验。
确定性量：naive t、sandwich SE、jackknife SE、ICC、DEFF —— 无随机性，应逐位复现。
随机量：基因簇自助法 ρ/一致率区间、基因标签置换 P —— 受 (RNG, seed, B) 影响，需说明。
输入: data/derived/primary_arm_96pairs.csv（随本仓库分发）
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

import csv, math, random
import numpy as np
from scipy.stats import rankdata, norm

P = PC.get('primary_arm')
rows=list(csv.DictReader(open(P,encoding='utf-8-sig')))
zg=np.array([float(r['Z_GTEx']) for r in rows]); ze=np.array([float(r['Z_eQTLGen']) for r in rows])
gene=np.array([r['Gene'] for r in rows]); trait=np.array([r['Trait'] for r in rows])
same=(np.sign(zg)==np.sign(ze)).astype(float)
gs=list(dict.fromkeys(gene)); K=len(gs); N=len(rows)
idxmap={g:np.where(gene==g)[0] for g in gs}
n_g=np.array([len(idxmap[g]) for g in gs])
k_g=np.array([same[idxmap[g]].sum() for g in gs])
p_hat=k_g.sum()/N

def rho(a,b):
    ra=rankdata(a); rb=rankdata(b); ra=ra-ra.mean(); rb=rb-rb.mean()
    return float(ra@rb/math.sqrt((ra@ra)*(rb@rb)))
rho_obs=rho(zg,ze)

print('='*100); print('A. 确定性量（无随机性）'); print('='*100)
# naive t on rho
t_naive=rho_obs*math.sqrt((N-2)/(1-rho_obs**2)); p_naive=2*norm.sf(abs(t_naive))
print(f'  naive t(ρ)      = {t_naive:.4f}  df={N-2}  P={p_naive:.3e}     报告 t=4.10, df 94, P=8.8e-5')
# sandwich SE of the ratio estimator p
var_p=(K/(K-1))*np.sum((k_g-p_hat*n_g)**2)/(N**2)
se_sand=math.sqrt(var_p)
z_sand=(p_hat-0.5)/se_sand
print(f'  sandwich SE(p)  = {se_sand:.4f}   报告 0.125    one-sided P={norm.sf(z_sand):.4f}  two-sided P={2*norm.sf(abs(z_sand)):.4f}  (df {K-1})')
print(f'                    报告：one-sided 0.002 / two-sided 0.004, df 31')
# jackknife SE
jk=[]
for g in gs:
    m=np.ones(N,bool); m[idxmap[g]]=False
    jk.append(same[m].mean())
jk=np.array(jk); jkm=jk.mean()
se_jk=math.sqrt((K-1)/K*np.sum((jk-jkm)**2))
z_jk=(p_hat-0.5)/se_jk
print(f'  jackknife SE(p) = {se_jk:.4f}   报告 0.137    one-sided P={norm.sf(z_jk):.4f}  two-sided P={2*norm.sf(abs(z_jk)):.4f}')
print(f'                    报告：one-sided 0.004 / two-sided 0.008, df 31')
# ICC / DEFF (one-way ANOVA over gene clusters, m̄ = 3)
mbar=N/K
grand=same.mean()
MSB=np.sum(n_g*(np.array([same[idxmap[g]].mean() for g in gs])-grand)**2)/(K-1)
MSW=sum(((same[idxmap[g]]-same[idxmap[g]].mean())**2).sum() for g in gs)/(N-K)
icc_raw=(MSB-MSW)/(MSB+(mbar-1)*MSW); icc=max(0.0,icc_raw); deff=1+(mbar-1)*icc
print(f'  ICC  raw={icc_raw:+.6f} -> clip {icc:.3f}   (MSB={MSB:.6f} / MSW={MSW:.6f}, m̄={mbar:.0f})')
print(f'  DEFF = {deff:.3f}                     报告 ICC 0.000 / DEFF 1.000')
print(f'  Clopper–Pearson 95% CI = ', end='')
from scipy.stats import binomtest
c=binomtest(int(k_g.sum()),N).proportion_ci(0.95,method='exact')
print(f'{100*c.low:.2f}-{100*c.high:.2f}%   报告 58.5-77.8%')

print(); print('='*100); print('B. 随机量：基因簇自助法（B=10000）'); print('='*100)
def run_boot(rng_factory, B=10000):
    R=np.empty(B); D=np.empty(B)
    rng=rng_factory()
    for b in range(B):
        pick=[gs[j] for j in rng.choice(K,size=K,replace=True)]
        idx=np.concatenate([idxmap[g] for g in pick])
        R[b]=rho(zg[idx],ze[idx]); D[b]=float(same[idx].mean())
    return R,D
def ci(a): return float(np.percentile(a,2.5)), float(np.percentile(a,97.5))
for tag,fac in [('numpy RandomState(MT19937)', lambda: np.random.RandomState(20260915)),
                ('numpy default_rng(PCG64)',  lambda: np.random.default_rng(20260915)),
                ('RandomState seed 20260910', lambda: np.random.RandomState(20260910))]:
    R,D=run_boot(fac)
    r=ci(R); d=ci(D)
    print(f'  {tag:28s} rho CI=[{r[0]:+.4f},{r[1]:+.4f}] -> 两位小数 {r[0]:.2f}–{r[1]:.2f} | '
          f'rate CI=[{100*d[0]:.1f},{100*d[1]:.1f}]')
print(f'  报告                                                  rho CI=  0.12–0.62        | rate CI=[58.3,79.2]')

print(); print('='*100); print('C. ρ 下端点对 RNG 的稳健性扫描（各 12 个种子 × B=10000）'); print('='*100)
for tag,fac in [('MT19937', lambda s: np.random.RandomState(s)), ('PCG64', lambda s: np.random.default_rng(s))]:
    lows=[]
    for s in [20260915,20260910,1,2,3,4,5,6,7,8,42,12345]:
        R,_=run_boot(lambda s=s: fac(s))
        lows.append(float(np.percentile(R,2.5)))
    lows=np.array(lows)
    print(f'  {tag:8s} ρ 下端点: 均值 {lows.mean():.4f}  范围 [{lows.min():.4f},{lows.max():.4f}]  '
          f'落在 [0.115,0.125) 的种子数 {((lows>=0.115)&(lows<0.125)).sum()}/12')

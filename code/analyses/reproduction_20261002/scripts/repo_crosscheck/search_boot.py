# -*- coding: utf-8 -*-
"""系统搜索主臂基因簇自助法的实现组合，目标是复现报告区间
   ρ 95% CI = 0.12–0.62 ; 一致率 95% CI = 58.3–79.2%   (seed 20260915, B=10000)
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

import csv, math, random, itertools
import numpy as np
from scipy.stats import rankdata, spearmanr

P = PC.get('primary_arm')
rows=list(csv.DictReader(open(P,encoding='utf-8-sig')))
zg=np.array([float(r['Z_GTEx']) for r in rows]); ze=np.array([float(r['Z_eQTLGen']) for r in rows])
gene=np.array([r['Gene'] for r in rows])
def rho(a,b):
    ra=rankdata(a); rb=rankdata(b); ra=ra-ra.mean(); rb=rb-rb.mean()
    return float(ra@rb/math.sqrt((ra@ra)*(rb@rb)))
print(f'观测: n={len(rows)} k={int((np.sign(zg)==np.sign(ze)).sum())} rho={rho(zg,ze):.6f}')
print('目标: rho CI = 0.12-0.62 ; rate CI = 58.3-79.2%')
print()

def boot(RNG, order, method, B=10000):
    gs=[g for g in (sorted(set(gene)) if order=='sorted' else list(dict.fromkeys(gene)))]
    idxmap={g:np.where(gene==g)[0] for g in gs}
    G=len(gs)
    R=np.empty(B); D=np.empty(B)
    if RNG=='pcg':
        rng=np.random.default_rng(20260915)
        draw=lambda: (rng.choice(G,size=G,replace=True) if method=='choice' else rng.integers(0,G,G))
    elif RNG=='rs':
        rs=np.random.RandomState(20260915)
        draw=lambda: (rs.choice(G,size=G,replace=True) if method=='choice' else rs.randint(0,G,G))
    else:
        rr=random.Random(20260915)
        draw=lambda: (rr.choices(range(G),k=G) if method=='choice' else [rr.randrange(G) for _ in range(G)])
    for b in range(B):
        pick=draw(); idx=np.concatenate([idxmap[gs[j]] for j in pick])
        R[b]=rho(zg[idx],ze[idx]); D[b]=float(np.mean(np.sign(zg[idx])==np.sign(ze[idx])))
    return R,D

def ci(a): return (float(np.percentile(a,2.5)), float(np.percentile(a,97.5)))
def ci_fisher(a):
    z=np.arctanh(np.clip(a,-0.999999,0.999999))
    return (float(np.tanh(np.percentile(z,2.5))), float(np.tanh(np.percentile(z,97.5))))

hits=[]
for RNG,order,method in itertools.product(['pcg','rs','pyrand'],['csv','sorted'],['choice','integers']):
    R,D=boot(RNG,order,method)
    r1=ci(R); r2=ci_fisher(R); d1=ci(D)
    tag=f'{RNG:7s} order={order:6s} {method:8s}'
    m1='  <== rho 命中' if abs(r1[0]-0.12)<5e-3 and abs(r1[1]-0.62)<5e-3 else ''
    m2='  <== fisher-z 命中' if abs(r2[0]-0.12)<5e-3 and abs(r2[1]-0.62)<5e-3 else ''
    m3='  <== rate 命中' if abs(100*d1[0]-58.3)<0.1 and abs(100*d1[1]-79.2)<0.1 else ''
    print(f'  {tag}  rho=[{r1[0]:+.3f},{r1[1]:+.3f}]  fisher=[{r2[0]:+.3f},{r2[1]:+.3f}]  '
          f'rate=[{100*d1[0]:.1f},{100*d1[1]:.1f}]{m1}{m2}{m3}')
    if m1 or m2 or m3: hits.append((tag,r1,r2,d1))
print()
print('命中组合:',[h[0] for h in hits] if hits else '无')

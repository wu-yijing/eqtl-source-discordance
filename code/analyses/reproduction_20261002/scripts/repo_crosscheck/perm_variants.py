# -*- coding: utf-8 -*-
"""基因标签置换的四种变体，目标复现 null 2.5–97.5 = −0.22 to 0.23（B=10000, seed 20260915）"""
import csv, math
import numpy as np
from scipy.stats import rankdata
import sys as _sys, os as _os
_p = _os.path.dirname(_os.path.abspath(__file__))
while _p != _os.path.dirname(_p) and not _os.path.isfile(_os.path.join(_p, 'paths.py')):
    _p = _os.path.dirname(_p)
_sys.path.insert(0, _p)
import paths as _paths          # noqa: E402  集中路径解析：向上找到 paths.py
_paths.bootstrap_args()   # 消费 --repo-root / --input（本脚本无自有 parser）
P=str(_paths.derived('primary_arm_96pairs'))
rows=list(csv.DictReader(open(P,encoding='utf-8-sig')))
x=np.array([float(r['Z_GTEx']) for r in rows]); y=np.array([float(r['Z_eQTLGen']) for r in rows])
gene=np.array([r['Gene'] for r in rows]); trait=np.array([r['Trait'] for r in rows])
gs=list(dict.fromkeys(gene)); K=len(gs); N=len(rows)
def prep(a): return rankdata(a)-(len(a)+1)/2.0
def rho(a,b):
    p=prep(a); q=prep(b); return float(p@q/math.sqrt((p@p)*(q@q)))
r_obs=rho(x,y)
traits=list(dict.fromkeys(trait))
M={t:np.array([np.where((gene==g)&(trait==t))[0][0] for g in gs]) for t in traits}
vals={t:{'x':x[M[t]],'y':y[M[t]]} for t in traits}

def run(variant, fac, B=10000):
    rng=fac(); null=np.empty(B)
    for b in range(B):
        if variant=='per_trait_y':          # 每个表型内置换 eQTLGen 的 Z（README 所述）
            yp=y.copy()
            for t in traits:
                m=M[t]; yp[m]=vals[t]['y'][rng.permutation(K)]
        elif variant=='per_trait_x':        # 每个表型内置换 GTEx 的 Z
            xp=x.copy()
            for t in traits:
                m=M[t]; xp[m]=vals[t]['x'][rng.permutation(K)]
        elif variant=='block_y':            # 基因整块置换（三个表型同时换）
            yp=y.copy()
            perm=rng.permutation(K)
            for i,t in enumerate(traits):
                m=M[t]; yp[m]=vals[t]['y'][np.roll(perm,0)]
        elif variant=='free':               # 全部 96 对自由置换
            yp=y[rng.permutation(N)]
        if variant=='per_trait_x': null[b]=rho(xp,y)
        else: null[b]=rho(x,yp)
    return null
for v in ['per_trait_y','per_trait_x','block_y','free']:
    for tagn,fac in [('MT',lambda: np.random.RandomState(20260915)),('PCG',lambda: np.random.default_rng(20260915))]:
        n=run(v,fac)
        lo,hi=np.percentile(n,[2.5,97.5]); Pp=float((np.abs(n)>=abs(r_obs)).mean())
        sd=n.std(ddof=1)
        print(f'  {v:13s} {tagn:4s} null 2.5–97.5 = {lo:+.3f} to {hi:+.3f}  SD={sd:.3f}  P={"<0.001" if Pp==0 else f"{Pp:.4f}"}')
print('  报告: null 2.5–97.5 = −0.22 to 0.23 ; P < 0.001')

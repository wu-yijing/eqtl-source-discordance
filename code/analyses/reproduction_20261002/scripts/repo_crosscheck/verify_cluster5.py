# -*- coding: utf-8 -*-
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
from scipy.stats import rankdata, t as tdist
P = PC.get('primary_arm')
rows=list(csv.DictReader(open(P,encoding='utf-8-sig')))
x=np.array([float(r['Z_GTEx']) for r in rows]); y=np.array([float(r['Z_eQTLGen']) for r in rows])
gene=np.array([r['Gene'] for r in rows]); trait=np.array([r['Trait'] for r in rows])
gs=list(dict.fromkeys(gene)); K=len(gs); N=len(rows)
IDX={g:np.where(gene==g)[0] for g in gs}
def prep(a): return rankdata(a)-(len(a)+1)/2.0
def rho(a,b):
    p=prep(a); q=prep(b); return float(p@q/math.sqrt((p@p)*(q@q)))
r_obs=rho(x,y)
print(f'ρ = {r_obs:.6f}   naive Fisher SE(ρ) = {(1-r_obs**2)/math.sqrt(N-3):.4f}')
print()
print('='*100); print('B. 基因簇自助法 ρ 的 SD（B=10000）'); print('='*100)
for tag,fac in [('MT19937',lambda: np.random.RandomState(20260915)),('PCG64',lambda: np.random.default_rng(20260915))]:
    rng=fac(); B=10000; R=np.empty(B)
    for b in range(B):
        pick=[gs[j] for j in rng.choice(K,size=K,replace=True)]
        ii=np.concatenate([IDX[g] for g in pick])
        R[b]=rho(x[ii],y[ii])
    lo,hi=np.percentile(R,[2.5,97.5])
    print(f'  {tag:8s} SD(ρ)={R.std(ddof=1):.4f}   95%CI=[{lo:+.4f},{hi:+.4f}] → 两位 {lo:.2f}–{hi:.2f}')
print('  报告：sandwich SE 0.125 / jackknife SE 0.137 / bootstrap ρ CI 0.12–0.62')
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
        null[b]=rho(x,yp)
    lo,hi=np.percentile(null,[2.5,97.5]); Pp=float((np.abs(null)>=abs(r_obs)).mean())
    print(f'  {tag:22s} null 2.5–97.5 pct = {lo:+.3f} to {hi:+.3f}   P = {"< 0.001" if Pp==0 else f"{Pp:.4f}"}')
print('  报告：null 2.5–97.5 percentiles −0.22 to 0.23；P < 0.001')

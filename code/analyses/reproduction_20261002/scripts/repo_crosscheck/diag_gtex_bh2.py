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

import csv, numpy as np
D = PC.DERIVED
def load(fn): return list(csv.DictReader(open(D+'\\'+fn,encoding='utf-8-sig')))
def num(x):
    s=str(x).strip().replace('+','')
    try: return float(s)
    except ValueError: return float('nan')
def bh_q(p):
    p=np.asarray(p,float); m=len(p); o=np.argsort(p); q=np.empty(m); prev=1.0
    for i in range(m-1,-1,-1):
        j=o[i]; prev=min(prev, p[j]*m/(i+1)); q[j]=prev
    return q
G=load('gtex_Z.csv'); T1=load('gene_groups.csv')
grp={r['Gene']:r['Group'] for r in T1}
missing=[r['Gene'] for r in G if r['Gene'] not in grp]
print('gtex 层中无分组的基因:',sorted(set(missing))[:10],'共',len(set(missing)))
print()
for pcol,qcol in [('P_ACAT_O','FDR_q_ACAT_O'),('P_Stouffer','FDR_q_Stouffer')]:
    for domain in ('Trait','GroupTrait','Group','All'):
        buckets={}
        for r in G:
            g=grp.get(r['Gene'],'?')
            k={'Trait':r['Trait'],'GroupTrait':(g,r['Trait']),'Group':g,'All':'all'}[domain]
            buckets.setdefault(k,[]).append(r)
        ok=bad=0; worst=0; wk=''
        for k,rows in buckets.items():
            p=np.array([num(r[pcol]) for r in rows]); qq=np.array([num(r[qcol]) for r in rows])
            if not np.isfinite(p).any(): continue
            q=bh_q(p); d=np.nanmax(np.abs(q-qq))
            if d<1e-4: ok+=1
            else:
                bad+=1
                if d>worst: worst=d; wk=f'{k}(m={len(rows)})'
        print(f'  {pcol:12s} 域={domain:11s} 完全一致 {ok:2d} / 不一致 {bad:2d}   max|Δq|={worst:.3e}  {wk}')

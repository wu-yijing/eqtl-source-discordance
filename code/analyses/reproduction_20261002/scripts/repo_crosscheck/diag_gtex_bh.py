# -*- coding: utf-8 -*-
import csv, numpy as np
from scipy import stats
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import paths as _paths          # noqa: E402  集中路径解析，见 ../paths.py
D=str(_paths.derived('gtex_Z').parent)
G=list(csv.DictReader(open(D+r'\gtex_official_Z.csv',encoding='utf-8-sig')))
def num(x):
    s=str(x).strip().replace('+','')
    try: return float(s)
    except ValueError: return float('nan')
def bh_q(p):
    p=np.asarray(p,float); m=len(p); o=np.argsort(p); q=np.empty(m); prev=1.0
    for i in range(m-1,-1,-1):
        j=o[i]; prev=min(prev, p[j]*m/(i+1)); q[j]=prev
    return q
for tr in ('DR','DN','DPN'):
    rows=[r for r in G if r['Trait']==tr]
    pp=np.array([num(r['P_ACAT_O']) for r in rows]); qq=np.array([num(r['FDR_q_ACAT_O']) for r in rows])
    print(f'--- Trait={tr}  m={len(rows)}  非缺失P={np.isfinite(pp).sum()}')
    q=bh_q(pp)
    d=np.abs(q-qq)
    print(f'    max|Δq|={np.nanmax(d):.3e}  中位|Δq|={np.nanmedian(d):.3e}  行内最小P={np.nanmin(pp):.4f} 最小q_表={np.nanmin(qq):.4f}')
    idx=np.argsort(-d)[:3]
    for i in idx:
        print(f'      {rows[i]["Gene"]:10s} P={pp[i]:.4f} q_表={qq[i]:.4f} q_复算={q[i]:.4f}  Z_ACAT?  Zmt={rows[i]["Z_multi_tissue"]}')
    # 全域
    q_all=bh_q(np.array([num(r['P_ACAT_O']) for r in G])); qq_all=np.array([num(r['FDR_q_ACAT_O']) for r in G])
    print(f'    [全域 m=222] max|Δq|={np.nanmax(np.abs(q_all-qq_all)):.3e}')
    # 用 Stouffer 侧
    qs=bh_q(np.array([num(r['P_Stouffer']) for r in rows])); qqs=np.array([num(r['FDR_q_Stouffer']) for r in rows])
    print(f'    [Stouffer 分层] max|Δq|={np.nanmax(np.abs(qs-qqs)):.3e}')

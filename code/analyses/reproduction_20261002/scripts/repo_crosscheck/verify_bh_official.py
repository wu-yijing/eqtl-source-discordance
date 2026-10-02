# -*- coding: utf-8 -*-
"""用仓库官方 Z 层（全精度）复算 BH q，检验 Table S3 / S18 的取整假设。
输入: eqtl-source-discordance-audit/data/processed_officialZ/{gtex,eqtlgen}_official_Z.csv
"""
import csv, math, numpy as np
from scipy import stats

D=r'E:/workbuddy/eqtl-source-discordance-audit/data/processed_officialZ'
def load(fn):
    return list(csv.DictReader(open(D+'\\'+fn, encoding='utf-8-sig')))

def num(x):
    s=str(x).strip().replace('+','')
    if s in ('','—','NA','nan','not included'): return float('nan')
    try: return float(s)
    except ValueError: return float('nan')

def bh_q(p):
    p=np.asarray(p,float); m=len(p); o=np.argsort(p); q=np.empty(m); prev=1.0
    for i in range(m-1,-1,-1):
        j=o[i]; prev=min(prev, p[j]*m/(i+1)); q[j]=prev
    return q

print('='*100)
print('A. GTEx 官方层（gtex_official_Z.csv）：用 Z 精确重建 P，再复算 BH q')
print('='*100)
G=load('gtex_official_Z.csv')
print(f'  行数 {len(G)}  列 {list(G[0].keys())}')
# ACAT-O 侧
for pcol,qcol,zcol in [('P_ACAT_O','FDR_q_ACAT_O',None),('P_Stouffer','FDR_q_Stouffer',None)]:
    ok=bad=0; worst=0; worst_key=''
    keys=sorted({(r['Gene'],r['Trait']) for r in G})
    grp={}
    for r in G: grp.setdefault(r['Trait'],[]).append(r)
    for tr,rows in sorted(grp.items()):
        pp=np.array([num(r[pcol]) for r in rows],float)
        qq=np.array([num(r[qcol]) for r in rows],float)
        if np.isnan(pp).all(): continue
        q=bh_q(pp)
        d=np.nanmax(np.abs(q-qq))
        if d<1e-4: ok+=1
        else:
            bad+=1
            if d>worst: worst=d; worst_key=f'{tr}(m={len(rows)})'
    print(f'  {pcol:12s} 域=按表型分层:  完全一致 {ok} 层 / 不一致 {bad} 层   max|Δq|={worst:.3e} {worst_key}')
# 合并单一全域
pp=np.array([num(r['P_ACAT_O']) for r in G],float); qq=np.array([num(r['FDR_q_ACAT_O']) for r in G],float)
q=bh_q(pp); print(f'  单一全域 (m={len(pp)}): max|Δq| = {np.nanmax(np.abs(q-qq)):.3e}')

print()
print('='*100)
print('B. eQTLGen 官方层（eqtlgen_official_Z.csv）：用 Z 精确重建 P，再复算 BH q')
print('='*100)
E=load('eqtlgen_official_Z.csv')
print(f'  行数 {len(E)}  列 {list(E[0].keys())}')
from collections import Counter
print('  Trait 分布:',dict(Counter(r['Trait'] for r in E)))
print('  Group 分布:',dict(Counter(r['Group'] for r in E)))
print('  Z 与 P 的关系检验:')
zs=np.array([num(r['Z_eQTLGen']) for r in E],float)
ps=np.array([num(r['P']) for r in E],float)
p_from_z=2*stats.norm.sf(np.abs(zs))
ok=np.abs(p_from_z-ps)<5e-4
print(f'    |2Φ(−|Z|) − 表中P| < 5e-4 的比例 = {ok.mean():.3f}  (n={ok.sum()}/{len(ok)})')
print(f'    最大偏差 = {np.nanmax(np.abs(p_from_z-ps)):.3e}  ← 若与 3 位小数舍入量级相当，则表中 P 是 3 位小数')
print()
qcols={}
for (g,t),rows in sorted({(r['Group'],r['Trait']):None for r in E}.items()):
    pass
groups={}
for r in E: groups.setdefault((r['Group'],r['Trait']),[]).append(r)
for use_z in (False,True):
    ok=bad=0; worst=0; wk=''
    for (g,t),rows in sorted(groups.items()):
        if use_z: p=np.array([num(r['Z_eQTLGen']) for r in rows],float); p=2*stats.norm.sf(np.abs(p))
        else:     p=np.array([num(r['P']) for r in rows],float)
        qq=np.array([num(r['BH_q']) for r in rows],float)
        if np.isnan(p).all(): continue
        q=bh_q(p); d=np.nanmax(np.abs(q-qq))
        if d<1e-4: ok+=1
        else:
            bad+=1
            if d>worst: worst=d; wk=f'{g}/{t}(m={len(rows)})'
    tag='用 Z 重建 P' if use_z else '用表中 3 位小数 P'
    print(f'  {tag:18s} 域=组×表型: 一致 {ok}/{ok+bad} 层   max|Δq|={worst:.3e}  {wk}')
# 单一全域
p=np.array([num(r['Z_eQTLGen']) for r in E],float); p=2*stats.norm.sf(np.abs(p))
qq=np.array([num(r['BH_q']) for r in E],float); q=bh_q(p)
print(f'  单一全域 (m={len(p)}, 用Z): max|Δq| = {np.nanmax(np.abs(q-qq)):.3e}')

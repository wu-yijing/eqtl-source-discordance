# -*- coding: utf-8 -*-
"""尝试闭合 GE SI Table S17 的 gene-cluster 行：
   pooled SE 2.2 pp / 90% CI −0.7~+6.4 / r = −0.05 / cov −0.63 pp²
数据: GE SI 表 S3(t02, GTEx 候选/非候选/T2DM)、S6(t06, 管家 GTEx ACAT-O P)、
      S18(t18, eQTLGen 三组)、S15(t15, 管家 eQTLGen BH q)；全部直接取自 SI .docx
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

import csv, math, re, numpy as np
_SI = PC.si_tables(PC.doc('si'))
def rows(fn):
    """fn is like 't06.tsv'; Table object i is Table S(i+1), so resolve by object."""
    i = int(re.match(r't(\d+)\.tsv', fn).group(1))
    return _SI[i]['rows']
def num(x):
    s=str(x).strip().replace('+','')
    try: return float(s)
    except ValueError: return float('nan')
TRAITS=['DR','DN','DPN']
def bh(p):
    p=np.asarray(p,float); m=len(p); o=np.argsort(p); q=np.empty(m); prev=1.0
    for i in range(m-1,-1,-1):
        j=o[i]; prev=min(prev,p[j]*m/(i+1)); q[j]=prev
    return q

# ---------- GTEx 臂 ----------
S3=rows('t02.tsv')[1:]
candG={}   # gene -> {trait: q}
for tr in TRAITS:
    sub=[r for r in S3 if r[1]==tr and r[0] in CANDS] if False else None
# 先确定候选基因集合（由 S18 的 Group 列）
S18=rows('t18.tsv')[1:]
CANDS=sorted({r[0] for r in S18 if r[2]=='Candidate'})
T2D=set(r[0] for r in S18 if r[2]=='T2DM control')
NONC=set(r[0] for r in S18 if r[2]=='Non-candidate')
print(f'候选 {len(CANDS)} 基因, 非候选 {len(NONC)}, T2DM对照 {len(T2D)}')

def gtex_q(subgenes, pcol=7):
    """按 组×表型 做 BH；返回 {gene: {trait: q}}"""
    out={}
    for tr in TRAITS:
        lst=[(r[0], num(r[pcol])) for r in S3 if r[1]==tr and r[0] in subgenes]
        lst=[(g,p) for g,p in lst if p==p]
        if not lst: continue
        q=bh([p for _,p in lst])
        for (g,_),qq in zip(lst,q): out.setdefault(g,{})[tr]=float(qq)
    return out
gqC=gtex_q(set(CANDS)); 
# 管家：S6 的 ACAT-O P 在第 2..4 列
S6=rows('t06.tsv')
hdr=S6[1]; body=S6[2:]
hkP={}
for r in body:
    g=r[0].strip()
    if not g: continue
    for k,tr in enumerate(TRAITS):
        v=num(r[2+k])
        if v==v: hkP.setdefault(g,{})[tr]=v
HKG=list(hkP)
hkQ={}
for tr in TRAITS:
    lst=[(g,hkP[g][tr]) for g in HKG if tr in hkP[g]]
    if not lst: continue
    q=bh([p for _,p in lst])
    for (g,_),qq in zip(lst,q): hkQ.setdefault(g,{})[tr]=float(qq)
print(f'GTEx 管家 {len(HKG)} 基因有 ACAT-O P')

# ---------- eQTLGen 臂 ----------
eq={}
for r in S18:
    g,t=r[0],r[1];  
    if r[2] in ('Candidate','Non-candidate','T2DM control'):
        q=num(r[5]) if False else num(r[5])
        eq.setdefault(g,{})[t]=q
eqH={}
for r in rows('t15.tsv')[1:]:
    eqH.setdefault(r[0],{})[r[1]]=num(r[4])

def per_gene(qmap):
    k={}; n={}
    for g,d in qmap.items():
        kk=sum(1 for t in TRAITS if t in d and d[t]==d[t] and d[t]<0.05)
        nn=sum(1 for t in TRAITS if t in d and d[t]==d[t])
        k[g]=kk; n[g]=nn
    return k,n
kC_gt,nC_gt=per_gene(gqC); kH_gt,nH_gt=per_gene(hkQ)
kC_eq,nC_eq=per_gene(eq);  kH_eq,nH_eq=per_gene(eqH)

def both(k1,n1,k2,n2,genes):
    return [g for g in genes if n1.get(g,0)>0 and n2.get(g,0)>0]
BC=both(kC_gt,nC_gt,kC_eq,nC_eq,CANDS)
BH=both(kH_gt,nH_gt,kH_eq,nH_eq,HKG)
print(f'两臂均可测：候选 {len(BC)} 基因, 管家 {len(BH)} 基因  （S17 正文称 26 与 26）')
print(f'  候选 GTEx 可测对数 {sum(nC_gt[g] for g in BC)}, eQTLGen {sum(nC_eq[g] for g in BC)}')
print(f'  管家 GTEx 可测对数 {sum(nH_gt[g] for g in BH)}, eQTLGen {sum(nH_eq[g] for g in BH)}')

def diff(gsub,ksub,ngt,keq,neq):
    """返回 (d_GTEx, d_eQTLGen) 单位 pp：候选率 − 管家率"""
    Kgt=sum(ksub[g] for g in gsub); Ngt=sum(ngt[g] for g in gsub)
    Keq=sum(keq[g] for g in gsub); Neq=sum(neq[g] for g in gsub)
    return 100*(Kgt/Ngt - Keq/Neq) if False else None
print()
print('=== 观测差 ===')
Kgt=sum(kC_gt[g] for g in BC); Ngt=sum(nC_gt[g] for g in BC)
Heq=sum(kH_gt[g] for g in BH); Mgt=sum(nH_gt[g] for g in BH)
a=100*(Kgt/Ngt - Heq/Mgt)
Keq=sum(kC_eq[g] for g in BC); Neq=sum(nC_eq[g] for g in BC)
Leq=sum(kH_eq[g] for g in BH); Peq=sum(nH_eq[g] for g in BH)
b=100*(Keq/Neq - Leq/Peq)
print(f'  GTEx 臂: 候选 {Kgt}/{Ngt} vs 管家 {Heq}/{Mgt} → {a:+.2f} pp   （报告 +2.38）')
print(f'  eQTLGen 臂: 候选 {Keq}/{Neq} vs 管家 {Leq}/{Peq} → {b:+.2f} pp   （报告 +3.70）')

print()
print('=== 配对基因簇自助法（B=10000，seed 20260915）===')
univ_C=np.array(BC); univ_H=np.array(BH)
def draw(rng,k):
    return rng.integers(0,k,k) if hasattr(rng,'integers') else rng.randint(0,k,k)
for tag,fac in [('MT19937',lambda: np.random.RandomState(20260915)),
                ('PCG64', lambda: np.random.default_rng(20260915))]:
    rng=fac(); B=10000
    da=np.empty(B); db=np.empty(B)
    for i in range(B):
        c=univ_C[draw(rng,len(univ_C))]
        h=univ_H[draw(rng,len(univ_H))]
        d1=100*(sum(kC_gt[g] for g in c)/sum(nC_gt[g] for g in c) - sum(kH_gt[g] for g in h)/sum(nH_gt[g] for g in h))
        d2=100*(sum(kC_eq[g] for g in c)/sum(nC_eq[g] for g in c) - sum(kH_eq[g] for g in h)/sum(nH_eq[g] for g in h))
        da[i]=d1; db[i]=d2
    va,vb=da.var(ddof=1),db.var(ddof=1); cov=np.cov(da,db,ddof=1)[0,1]; r=cov/math.sqrt(va*vb)
    wa,wb=1/(1.663**2), 1/(3.182**2); W=wa+wb
    se=math.sqrt((wa*wa*va + wb*wb*vb + 2*wa*wb*cov))/W
    dbar=(wa*a+wb*b)/W
    print(f'  {tag}: SD(GTEx)={math.sqrt(va):.3f}  SD(eQTLGen)={math.sqrt(vb):.3f}  cov={cov:+.3f} pp²  r={r:+.3f}')
    print(f'         pooled SE = {se:.3f} pp   90% CI = {dbar-1.6449*se:+.2f} to {dbar+1.6449*se:+.2f}')
print()
print('  S17 报告: cov = −0.63 pp² ; r = −0.05 ; pooled SE = 2.2 pp ; 90% CI = −0.7 to +6.4 pp')
print()
print('=== cov / r 的种子稳定性（MT19937，B=10000，12 个种子）===')
import statistics as st
cs=[];rs=[];ss=[]
for sd in [20260915,20260910,1,2,3,4,5,6,7,8,42,12345]:
    rg=np.random.RandomState(sd); da2=np.empty(10000); db2=np.empty(10000)
    for i in range(10000):
        c=univ_C[rg.randint(0,len(univ_C),len(univ_C))]; h=univ_H[rg.randint(0,len(univ_H),len(univ_H))]
        da2[i]=100*(sum(kC_gt[g] for g in c)/sum(nC_gt[g] for g in c) - sum(kH_gt[g] for g in h)/sum(nH_gt[g] for g in h))
        db2[i]=100*(sum(kC_eq[g] for g in c)/sum(nC_eq[g] for g in c) - sum(kH_eq[g] for g in h)/sum(nH_eq[g] for g in h))
    cv=np.cov(da2,db2,ddof=1)[0,1]; rr=cv/math.sqrt(da2.var(ddof=1)*db2.var(ddof=1))
    wa,wb=1/1.663**2,1/3.182**2; W=wa+wb
    se2=math.sqrt(wa*wa*da2.var(ddof=1)+wb*wb*db2.var(ddof=1)+2*wa*wb*cv)/W
    cs.append(cv); rs.append(rr); ss.append(se2)
print(f'  cov: 均值 {st.mean(cs):+.3f}  范围 [{min(cs):+.3f},{max(cs):+.3f}]   (报告 −0.63)')
print(f'  r  : 均值 {st.mean(rs):+.3f}  范围 [{min(rs):+.3f},{max(rs):+.3f}]   (报告 −0.05)')
print(f'  SE : 均值 {st.mean(ss):.3f}   范围 [{min(ss):.3f},{max(ss):.3f}]    (报告 2.2)')

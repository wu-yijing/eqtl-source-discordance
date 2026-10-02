# -*- coding: utf-8 -*-
"""穷举 sandwich SE(ρ)=0.125 的候选估计量，并核验 A13 恒等式的取整链。"""
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
gene=np.array([r['Gene'] for r in rows])
gs=list(dict.fromkeys(gene)); K=len(gs); N=len(rows); IDX={g:np.where(gene==g)[0] for g in gs}
xa=rankdata(x)-(N+1)/2; yb=rankdata(y)-(N+1)/2
Sxx=xa@xa; Syy=yb@yb
rho=float(xa@yb/math.sqrt(Sxx*Syy))
print(f'ρ = {rho:.6f}   K={K} genes, N={N} pairs')
print('='*96); print('A. sandwich SE(ρ) 候选估计量穷举（目标 0.1250）'); print('='*96)
phi = xa*yb/math.sqrt(Sxx*Syy) - rho/2*(xa*xa/Sxx + yb*yb/Syy)
ph0 = xa*yb/math.sqrt(Sxx*Syy)
Sg  = np.array([phi[IDX[g]].sum() for g in gs]); Sg0=np.array([ph0[IDX[g]].sum() for g in gs])
# 逐基因 ρ（每基因 3 对）
rg=np.array([ (lambda a,b: float((rankdata(a)-(len(a)+1)/2)@(rankdata(b)-(len(b)+1)/2)/
        math.sqrt(((rankdata(a)-(len(a)+1)/2)**2).sum()*((rankdata(b)-(len(b)+1)/2)**2).sum())))(x[IDX[g]],y[IDX[g]]) for g in gs])
cands={
 'A 影响函数 sqrt(K/(K−1)Σφg²)':          math.sqrt(K/(K-1)*np.sum(Sg**2)),
 'B 影响函数 sqrt(Σφg²)':                  math.sqrt(np.sum(Sg**2)),
 'C 影响函数 sqrt(N/(N−1)Σφg²)':           math.sqrt(N/(N-1)*np.sum(Sg**2)),
 'D 影响函数 sqrt((K−1)/K·Σφg²)':          math.sqrt((K-1)/K*np.sum(Sg**2)),
 'E 仅 x̃ỹ sqrt(K/(K−1)Σφg²)':            math.sqrt(K/(K-1)*np.sum(Sg0**2)),
 'F 影响函数 sqrt(K/(K−1)Σφg²/(K−1))':     math.sqrt(K/(K-1)*np.sum(Sg**2)/(K-1)),
 'G 影响函数 sqrt(Σφg²/K)':                math.sqrt(np.sum(Sg**2)/K),
 'H Fisher 朴素 SE(ρ)=(1−ρ²)/√(N−3)':      (1-rho**2)/math.sqrt(N-3),
 'I OLS 斜率 SE 的 ρ 换算':                math.sqrt((1-rho**2)/(N-2)),
 'J 逆方差 √(Σφ²)/N×K':                    math.sqrt(np.sum(phi**2))*K/N,
 'K 基因级 ρ 伪值 SE':                      math.sqrt(np.sum((rg-rg.mean())**2)/(K*(K-1))),
 'L 基因级 ρ SE (K²)':                      math.sqrt(np.sum((rg-rg.mean())**2)/K**2),
 'M Fisher-z 的基因刀切':                   None,
}
# M: 对 z 做基因刀切，再换算回 ρ
zobs=math.atanh(rho); zj=[]
for g in gs:
    m=np.ones(N,bool); m[IDX[g]]=False
    a=rankdata(x[m])-(len(x[m])+1)/2; b=rankdata(y[m])-(len(y[m])+1)/2
    zj.append(math.atanh(float(a@b/math.sqrt((a@a)*(b@b)))))
zj=np.array(zj); cands['M Fisher-z 的基因刀切']=(1-rho**2)*math.sqrt((K-1)/K*((zj-zj.mean())**2).sum())
# N: ρ 的基因刀切（已知 0.1367）
jj=[]
for g in gs:
    m=np.ones(N,bool); m[IDX[g]]=False
    a=rankdata(x[m])-(len(x[m])+1)/2; b=rankdata(y[m])-(len(y[m])+1)/2
    jj.append(float(a@b/math.sqrt((a@a)*(b@b))))
jj=np.array(jj); cands['N ρ 的基因刀切']=math.sqrt((K-1)/K*((jj-jj.mean())**2).sum())
for k,v in cands.items():
    if v is None: continue
    mark='   ← 命中 0.125' if abs(v-0.125)<2.5e-4 else ''
    print(f'  {k:44s} {v:.4f} → 三位 {v:.3f}{mark}')
print(f'  报告值: 0.125')

print(); print('='*96); print('B. A13 恒等式超额：取整链核验'); print('='*96)
rate=66/96*100
for lab,r_,rt in [('用四舍五入显示值 (ρ=0.39, 68.80%)',0.39,68.80),
                  ('用未取整值 (ρ=0.389639, 68.75%)',rho,rate)]:
    ident=100*(0.5+math.asin(r_)/math.pi)
    print(f'  {lab:38s} 恒等式预测 {ident:.4f}%  观测 {rt:.4f}%  超额 {rt-ident:+.4f} pp')
print()
print(f'  ρ 取 0.390 时预测 = {100*(0.5+math.asin(0.390)/math.pi):.4f}%  → 68.75−62.70 = {68.75-100*(0.5+math.asin(0.390)/math.pi):+.4f}')
print(f'  报告 "6.05 points"↔"62.7%"：用 ρ=0.39 与 68.75% 得 {68.75-100*(0.5+math.asin(0.39)/math.pi):+.4f} pp；用 68.80% 得 {68.80-100*(0.5+math.asin(0.39)/math.pi):+.4f} pp')
print(f'  用精确 ρ 与精确率（68.75%）：{rate-100*(0.5+math.asin(rho)/math.pi):+.4f} pp')

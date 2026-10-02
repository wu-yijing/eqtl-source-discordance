# -*- coding: utf-8 -*-
"""核验 GE SI Table S17 末三行（两臂合并率的差）—— 由表内四个计数精确复算。
GTEx 臂：候选 2/84 (2.4%) vs 管家 0/87 (0.0%)  → 差 +2.38 pp（BMC 正文给 +2.38）
eQTLGen 臂：候选 5/81 (6.2%) vs 管家 2/81 (2.5%) → 差 +3.70 pp
"""
import math
def binom_se(k,n):
    p=k/n; return math.sqrt(p*(1-p)/n)
cases=[('GTEx v8 (ACAT-O multi-tissue)', 2,84, 0,87, 2.38),
       ('eQTLGen whole blood',           5,81, 2,81, 3.70)]
rows=[]
for lab,k1,n1,k2,n2,rep in cases:
    d=100*(k1/n1-k2/n2)
    se=100*math.sqrt(binom_se(k1,n1)**2 + binom_se(k2,n2)**2)
    rows.append((lab,d,se))
    print(f'  {lab:30s} 差 = {d:+.2f} pp （正文 {rep:+.2f}）  独立对 SE = {se:.3f} pp')
w=[1/r[2]**2 for r in rows]; W=sum(w)
dbar=sum(wi*r[1] for wi,r in zip(w,rows))/W
se_pool=math.sqrt(1/W)
Q=sum(wi*(r[1]-dbar)**2 for wi,r in zip(w,rows))
print()
print(f'  固定效应逆方差合并：差 = {dbar:+.4f} pp   报告 +2.66')
print(f'  独立对模型 SE      = {se_pool:.4f} pp   报告 1.5 pp')
print(f'  95% CI = {dbar-1.96*se_pool:+.2f} to {dbar+1.96*se_pool:+.2f}   报告 −0.22 to +5.55')
print(f'  90% CI = {dbar-1.6449*se_pool:+.2f} to {dbar+1.6449*se_pool:+.2f}   报告 +0.2 to +5.1')
print(f'  Cochran Q = {Q:.4f} (df 1)   报告 0.14')
print()
print('  → S17 的「analytic independent-pair」四行（+2.66 / SE 1.5 / 95% CI −0.22~+5.55 / 90% CI +0.2~+5.1）')
print('    与 Q = 0.14 均**逐位复现**。')
print('  → 剩余的 gene-cluster 行（SE 2.2 pp / 90% CI −0.7~+6.4 / r = −0.05 / cov −0.63 pp²）')
print('    需按基因簇配对自助法重算，本轮未闭合。')

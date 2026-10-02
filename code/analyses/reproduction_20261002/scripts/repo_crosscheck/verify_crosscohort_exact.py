# -*- coding: utf-8 -*-
"""Table S5a（RNH1 跨队列合并）逐位核验 —— 用官方 MetaXcan v0.8.1 的精确 Z。
输入 Z 来源: data/derived/ukb_dr/RNH1_official_metaxcan_Z.csv
   FinnGen R13 DR        / eQTLGen weights        : Z = +2.3091, N_e = 49,304
   UKB GCST90043640      / eQTLGen weights        : Z = +0.7225, N_e =  1,231
   UKB GCST90043640      / GTEx MASHR Nerve_Tibial: Z = +0.5451, N_e =  1,231
算法: 等权单位方差 k=2 合并 + DerSimonian–Laird(1986) τ² = (Q − df)/C, C = Σw − Σw²/Σw
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import paths as _paths          # noqa: E402  集中路径解析，见 ../paths.py
import math
def pnorm2(z): return math.erfc(abs(z)/math.sqrt(2))

def meta(zs):
    k=len(zs); df=k-1
    pooled=sum(zs)/k
    Q=sum((z-pooled)**2 for z in zs)
    C=k-(k)/k                       # w_i = 1/v_i = 1 → C = Σw − Σw²/Σw = k − 1
    tau2=max(0.0,(Q-df)/C); tau=math.sqrt(tau2)
    w=1.0/(1.0+tau2)                # 每队列 v_i = 1
    se=math.sqrt(1.0/(k*w))
    zre=pooled/se
    I2=max(0.0,(Q-df)/Q)*100 if Q>0 else 0.0
    lo=pooled-1.96*math.sqrt(se**2+tau2); hi=pooled+1.96*math.sqrt(se**2+tau2)
    return dict(pooled=pooled,Q=Q,I2=I2,tau=tau,se=se,p=pnorm2(zre),lo=lo,hi=hi,C=C)

CASES=[
 ('第 1 行｜eQTLGen 权重（k=2）', [2.3091,0.7225],
  dict(pooled=1.51,se=0.79,p=0.056,Q=1.26,I2=20.6,tau=0.51,lo=-0.33,hi=3.36)),
 ('第 3 行｜跨权重敏感性（FinnGen×eQTLGen + UKB×GTEx NT，k=2）', [2.3091,0.5451],
  dict(pooled=1.43,se=0.88,p=0.106,Q=1.56,I2=35.7,tau=0.75,lo=-0.84,hi=3.69)),
]
print('='*104)
print('Table S5a（RNH1 跨队列随机效应合并）逐位核验   [DL 分母 C = Σw − Σw²/Σw = k−1 = 1]')
print('='*104)
allok=True
for lab,zs,rep in CASES:
    m=meta(zs)
    print(f'\n{lab}   Z = {zs[0]:+.4f}, {zs[1]:+.4f}')
    rows=[('pooled Z',m['pooled'],rep['pooled'],2),('SE',m['se'],rep['se'],2),
          ('P',m['p'],rep['p'],3),("Cochran Q",m['Q'],rep['Q'],2),
          ('I² (%)',m['I2'],rep['I2'],1),('τ',m['tau'],rep['tau'],2),
          ('PI 下端',m['lo'],rep['lo'],2),('PI 上端',m['hi'],rep['hi'],2)]
    for nm,got,want,nd in rows:
        ok=abs(round(got,nd)-round(want,nd))<1e-9
        allok &= ok
        print(f'   {nm:10s} 复算 {got:>+9.4f}   报告 {want:>+8.2f}   在{nd}位小数下{"一致 ✓" if ok else "不符 ✗"}')
print()
print('='*104)
print('总判定:', '全部 16 个数值在报告精度下逐位一致 ✓' if allok else '存在不符 ✗')
print('='*104)
print("""说明：
  · 上一轮报告曾判定「表注称 DL 但实际用的是 τ²=(Q−df)/df」——该判定错误，现予撤回。
    错因是对 DL 分母取错：DL 的 C = Σw − Σw²/Σw（本例 k=2、v=1 → C = 2−1 = 1），
    并非 Σw（=2）。等权单位方差下 C 恰等于 df，故「除以 C」与「除以 df」数值相同。
  · 第 3 行此前差在 +0.55 vs +0.5451：官方文件给出 GTEx MASHR Nerve_Tibial 侧 Z = +0.5451，
    用精确值后 pooled/Q/I²/τ/SE/P/PI 全部逐位命中。""")

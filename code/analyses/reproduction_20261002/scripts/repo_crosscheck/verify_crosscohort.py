# -*- coding: utf-8 -*-
"""核验 Table S5a（RNH1 跨队列合并）与 DerSimonian-Laird 的标签一致性。
数据来源: data/derived/crosscohort.csv（随本仓库分发）
算法来源: 同仓 scripts/python/m6_ne_weighted_sensitivity.py (dl_random_effects, 第 65-75 行)
"""
import math

def pnorm2(z): return math.erfc(abs(z)/math.sqrt(2))

def meta_equw(zs, tau_denom):
    """等权单位方差 k=2 合并。tau_denom ∈ {'C_DL','sum_w','df'} 指定 tau^2 的分母。"""
    k=len(zs); df=k-1
    pooled=sum(zs)/k                      # 无权重算术均值（每个队列方差=1）
    Q=sum((z-pooled)**2 for z in zs)
    if tau_denom=='C_DL':   C = k - (k)/k          # = Σw − Σw²/Σw = k − k/k = k−1，w=1
    elif tau_denom=='sum_w': C = k                  # 我上一轮误用的分母
    elif tau_denom=='df':    C = df                 # 我上一轮误称的"表中口径"
    tau2=max(0.0,(Q-df)/C); tau=math.sqrt(tau2)
    w=[1.0/(1.0+tau2)]*k                            # v_i = 1
    pooled_re=sum(wi*z for wi,z in zip(w,zs))/sum(w)
    se=math.sqrt(1.0/sum(w))
    zre=pooled_re/se
    I2=max(0.0,(Q-df)/Q)*100 if Q>0 else 0.0
    I2_roundQ=max(0.0,(round(Q,2)-df)/round(Q,2))*100 if Q>0 else 0.0
    pi=(pooled_re-1.96*math.sqrt(se**2+tau2), pooled_re+1.96*math.sqrt(se**2+tau2))
    return dict(pooled=pooled, Q=Q, I2=I2, I2_rQ=I2_roundQ, tau=tau, se=se,
                p=pnorm2(zre), pi=pi)

R1={'pooled':1.51,'SE':0.79,'P':0.056,'Q':1.26,'I2':20.6,'tau':0.51,'PI':(-0.33,3.36)}
R3={'pooled':1.43,'SE':0.88,'P':0.106,'Q':1.56,'I2':35.7,'tau':0.75,'PI':(-0.84,3.69)}

print('='*96)
print('A. 第一行（eQTLGen 权重，k=2）：Z = +2.31（FinnGen R13 DR）与 +0.72（UKB GCST90043640）')
print('='*96)
zs=[2.31,0.72]
for den in ('C_DL','sum_w','df'):
    m=meta_equw(zs,den)
    print(f"  tau^2 分母 = {den:6s}: tau={m['tau']:.3f} SE={m['se']:.4f} P={m['p']:.4f} "
          f"PI=({m['pi'][0]:+.2f},{m['pi'][1]:+.2f})")
m=meta_equw(zs,'C_DL')
print(f"  共同量: pooled={m['pooled']:+.3f} (报 {R1['pooled']:+.2f})  Q={m['Q']:.4f} (报 {R1['Q']})")
print(f"          I2(Q未取整)={m['I2']:.2f}%  I2(Q取整1.26)={m['I2_rQ']:.2f}% (报 {R1['I2']}%)")
print(f"  >> 报告值 tau=0.51 / SE=0.79 / P=0.056 对应分母 = C_DL（真 DL）")

print()
print('='*96)
print('B. 第三行（跨权重，k=2）：Z = +2.31 与 +0.55')
print('='*96)
zs3=[2.31,0.55]
for den in ('C_DL','sum_w','df'):
    m3=meta_equw(zs3,den)
    print(f"  tau^2 分母 = {den:6s}: tau={m3['tau']:.3f} SE={m3['se']:.4f} P={m3['p']:.4f} "
          f"PI=({m3['pi'][0]:+.2f},{m3['pi'][1]:+.2f})")
m3=meta_equw(zs3,'C_DL')
print(f"  共同量: pooled={m3['pooled']:+.3f} (报 {R3['pooled']:+.2f})  Q={m3['Q']:.4f} (报 {R3['Q']})"
      f"  I2={m3['I2']:.2f}% / Q取整 {m3['I2_rQ']:.2f}% (报 {R3['I2']}%)")

print()
print('='*96)
print('C. 结论')
print('='*96)
print('  DL(1986) 的 tau^2 = (Q − df)/C，其中 C = Σw − Σw²/Σw。')
print('  本题 k=2、每队列方差 v=1（w=1）：C = 2 − 2/2 = 1 = df。')
print('  故等权单位方差下"除以 C"与"除以 df"数值恰好相同 → 表中 tau=0.51 是真 DL，不是另一种约定。')
print('  上一轮用 tau^2=(Q−df)/Σw（Σw=2）得 tau=0.363，属公式分母取错，需撤回该条判定。')

# -*- coding: utf-8 -*-
"""主臂簇稳健性的确定性量逐项核验（README §Cluster-Robustness / AF1 Table S16）。
均作用于 Spearman ρ = 0.3896 与方向一致率 66/96，df = K−1 = 31，K = 32 基因簇。
"""
import csv, math
import numpy as np
from scipy.stats import rankdata, t as tdist, binomtest

P=r'E:/workbuddy/eqtl-source-discordance-audit/data/processed_officialZ/primary_arm_96pairs_official.csv'
rows=list(csv.DictReader(open(P,encoding='utf-8-sig')))
x=np.array([float(r['Z_GTEx']) for r in rows]); y=np.array([float(r['Z_eQTLGen']) for r in rows])
gene=[r['Gene'] for r in rows]
same_src=np.array([1.0 if str(r['Same']).strip().lower()=='true' else 0.0 for r in rows])
same_calc=(np.sign(x)==np.sign(y)).astype(float)
print('=== 0. 一致性列自校验 ===')
print(f'  CSV 的 Same 列 与 sign(Z_GTEx)==sign(Z_eQTLGen) 不一致的行数 = {int((same_src!=same_calc).sum())}')
same=same_src
gs=list(dict.fromkeys(gene)); K=len(gs); N=len(rows)
idx=[np.where(np.array(gene)==g)[0] for g in gs]
k_g=np.array([same[i].sum() for i in idx]); n_g=np.array([len(i) for i in idx])
p_hat=k_g.sum()/N
print(f'  K={K} 基因, N={N} 对, Σk={int(k_g.sum())}, p={p_hat:.5f}')
from collections import Counter
print(f'  k_g 分布: {dict(sorted(Counter(k_g.tolist()).items()))}')

# 秩标准化
def rho_of(xx,yy):
    ra=rankdata(xx); rb=rankdata(yy); ra=ra-ra.mean(); rb=rb-rb.mean()
    return float(ra@rb/math.sqrt((ra@ra)*(rb@rb)))
r_obs=rho_of(x,y)
print(f'  ρ = {r_obs:.6f}')

print()
print('='*100); print('A. 确定性量'); print('='*100)
# 1) naive t 与 P（用 t 分布）
t_naive=r_obs*math.sqrt((N-2)/(1-r_obs**2))
print(f'  1) naive t = {t_naive:.4f} (df {N-2})   P(双侧,t) = {2*tdist.sf(abs(t_naive),N-2):.3e}   报告 t=4.10, P=8.8e-5')

# 2) ρ 的簇稳健 sandwich SE（影响函数法）
ra=rankdata(x).astype(float); rb=rankdata(y).astype(float)
xa=ra-ra.mean(); yb=rb-rb.mean()
Sxx=xa@xa; Syy=yb@yb
phi=xa*yb/math.sqrt(Sxx*Syy) - r_obs/2*(xa*xa/Sxx + yb*yb/Syy)
print(f'  2) 影响函数 Σφ_i = {phi.sum():+.3e}（应为 0）')
s1=sum(phi[i].sum()**2 for i in idx)
se_sand_c=math.sqrt((K/(K-1))*s1/N**2)
se_sand_u=math.sqrt((K/(K-1))*s1)
se_fisher=(1-r_obs**2)/math.sqrt(N-3)
print(f'     sandwich SE(ρ) [÷n²]         = {se_sand_c:.4f}')
print(f'     sandwich SE(ρ) [不除]         = {se_sand_u:.4f}')
print(f'     对照：Fisher-z naive SE(ρ)    = {se_fisher:.4f}')
for nm,v in [('÷n²',se_sand_c),('不除',se_sand_u)]:
    z=r_obs/v
    print(f'     {nm:4s} → z={z:.4f}  one-sided P={tdist.sf(z,K-1):.4f}  two-sided P={2*tdist.sf(abs(z),K-1):.4f}')
print(f'     报告：SE = 0.125，one-sided 0.002 / two-sided 0.004（df 31）')

# 3) ρ 的 delete-one-gene jackknife SE
jk=[]
for g in range(K):
    m=np.ones(N,bool); m[idx[g]]=False
    jk.append(rho_of(x[m],y[m]))
jk=np.array(jk); jkm=jk.mean()
se_jk_c=math.sqrt((K-1)/K*((jk-jkm)**2).sum())
se_jk_u=math.sqrt(((jk-jkm)**2).sum())
print(f'  3) jackknife SE(ρ) [标准式 √((K−1)/K · Σ)] = {se_jk_c:.4f}')
print(f'     jackknife SE(ρ) [不乘 (K−1)/K）      = {se_jk_u:.4f}')
for nm,v in [('标准式',se_jk_c),('不乘',se_jk_u)]:
    z=r_obs/v
    print(f'     {nm:4s} → z={z:.4f}  one-sided P={tdist.sf(z,K-1):.4f}  two-sided P={2*tdist.sf(abs(z),K-1):.4f}')
print(f'     报告：SE = 0.137，one-sided 0.004 / two-sided 0.008（df 31）')

# 4) ICC / DEFF（在方向一致率上）
mbar=N/K; grand=same.mean()
MSB=(n_g*(np.array([same[i].mean() for i in idx])-grand)**2).sum()/(K-1)
SSW=sum(((same[i]-same[i].mean())**2).sum() for i in idx); MSW=SSW/(N-K)
icc_raw=(MSB-MSW)/(MSB+(mbar-1)*MSW)
print(f'  4) ICC raw = {icc_raw:+.6f} → clip {max(0,icc_raw):.3f}   (MSB={MSB:.6f}, MSW={MSW:.6f}, Σ(k−k̄)²={SSW:.4f})')
print(f'     DEFF = {1+(mbar-1)*max(0,icc_raw):.3f}          报告 ICC 0.000 / DEFF 1.000')
print(f'     S1 记录所载: MSB 0.278226 / MSW 0.281250 / ICC raw −0.003597  (SSW 应为 18.0)')

# 5) Clopper–Pearson
c=binomtest(int(k_g.sum()),N).proportion_ci(0.95,method='exact')
print(f'  5) Clopper–Pearson 95% = {100*c.low:.2f}–{100*c.high:.2f}%      报告 58.5–77.8%')

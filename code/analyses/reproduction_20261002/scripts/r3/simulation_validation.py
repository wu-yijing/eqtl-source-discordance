# -*- coding: utf-8 -*-
"""R6 模拟（增强版）：提高重复数 + 追加自由度扫描"""
import sys, io, json
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SEED = 20260930
G, P, NPAIR = 32, 3, 96
RHO_OBS, RHO_SD = 0.39, 0.15
rng = np.random.default_rng(SEED)

def rank(x):
    order = np.argsort(x); r = np.empty(len(x), float)
    r[order] = np.arange(1, len(x) + 1)
    s = np.sort(x); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j+1] == s[i]: j += 1
        if j > i: r[x == s[i]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return r

def spearman(a, b):
    ra, rb = rank(a) - 0, rank(b) - 0
    ra = ra - ra.mean(); rb = rb - rb.mean()
    d = np.sqrt((ra**2).sum() * (rb**2).sum())
    return float((ra * rb).sum() / d) if d > 0 else 0.0

def gen(rho_pair, df=None):
    n = len(rho_pair); a = rng.standard_normal(n)
    if df is None:
        e = rng.standard_normal(n)
    else:
        e = rng.standard_t(df, n) / np.sqrt(df / (df - 2)) if df > 2 else rng.standard_t(3, n)
    b = rho_pair * a + np.sqrt(1 - rho_pair**2) * e
    return a, b

genes = np.repeat(np.arange(G), P)

# ---------- Sim 1: 恒等式校准 + 自由度扫描 ----------
print("=" * 70)
print("SIM 1  符号一致率恒等式：校准确认 / 尾部厚度扫描")
print("=" * 70)
N1 = 3000
print(f"  （每格 {N1} 次重复 × {NPAIR} 对）")
sim1 = []
for tag, df in [('normal', None), ('t(10)', 10), ('t(5)', 5), ('t(4)', 4), ('t(3)', 3)]:
    row = {'dist': tag}
    for rt in [0.0, 0.39, 0.8]:
        obs = np.mean([np.mean(np.sign(gen(np.full(NPAIR, rt), df)[0]) ==
                               np.sign(gen(np.full(NPAIR, rt), df)[1])) for _ in range(N1)])
        # 上面写法会重复生成，改为一次生成成对值
        obs = []
        for _ in range(N1):
            a, b = gen(np.full(NPAIR, rt), df)
            obs.append(np.mean(np.sign(a) == np.sign(b)))
        obs = float(np.mean(obs)); pred = 0.5 + np.arcsin(rt) / np.pi
        row[f'rho{rt}'] = dict(obs=obs, pred=pred, diff_pp=100*(obs-pred))
    sim1.append(row)
    r = row['rho0.39']
    print(f"  {tag:7s} ρ=0.39 → 观测 {100*r['obs']:6.2f}% | 恒等式 {100*r['pred']:6.2f}% | 偏离 {r['diff_pp']:+6.2f} pp")
print(f"  【本稿实测】ρ=0.39 → 一致率 68.75% | 恒等式 62.75% | 偏离 +6.05 pp")

# ---------- Sim 2: 区间覆盖率 ----------
print()
print("=" * 70)
print("SIM 2  基因簇 bootstrap 区间 vs naive t 区间")
print("=" * 70)
NREP2, B2 = 400, 500
sim2 = []
for rt in [0.0, 0.39]:
    cc = cn = rc = rn = 0
    for _ in range(NREP2):
        rho_g = rng.normal(rt, RHO_SD, G).clip(-0.95, 0.95)
        rp = np.repeat(rho_g, P)
        a, b = gen(rp)
        true_rho = float(rp.mean()); rho_hat = spearman(a, b)
        vals = []
        gs_pool = np.arange(G)
        for k in range(B2):
            gs = rng.choice(gs_pool, size=G, replace=True)
            idx = np.concatenate([np.where(genes == g)[0] for g in gs])
            vals.append(spearman(a[idx], b[idx]))
        lo, hi = np.percentile(vals, [2.5, 97.5])
        if lo <= true_rho <= hi: cc += 1
        z = np.arctanh(rho_hat); se = 1/np.sqrt(NPAIR-3)
        nl, nh = np.tanh(z-1.96*se), np.tanh(z+1.96*se)
        if nl <= true_rho <= nh: cn += 1
        if rt == 0.0:
            if not (lo <= 0 <= hi): rc += 1
            if not (nl <= 0 <= nh): rn += 1
    sim2.append(dict(rho_true=rt, cov_cluster=100*cc/NREP2, cov_naive=100*cn/NREP2,
                     type1_cluster=100*rc/NREP2, type1_naive=100*rn/NREP2))
    s = f"  ρ_true={rt:.2f}  覆盖率 cluster={100*cc/NREP2:5.1f}%  naive={100*cn/NREP2:5.1f}%"
    if rt == 0: s += f"   I 类错误 cluster={100*rc/NREP2:5.1f}%  naive={100*rn/NREP2:5.1f}%"
    print(s)

# ---------- Sim 3: 分离性检验 I 类错误 ----------
print()
print("=" * 70)
print("SIM 3  两轴分解 Δρ 检验的 I 类错误（Δρ = 0 时）")
print("=" * 70)
NREP3, B3 = 400, 500
sim3 = []
for gsize in [32, 64]:
    gg = np.repeat(np.arange(gsize), P); uniq = np.unique(gg)
    rej = 0; w = []
    for _ in range(NREP3):
        rho_g = rng.normal(0.39, RHO_SD, gsize).clip(-0.95, 0.95)
        rp = np.repeat(rho_g, P)
        a1, b1 = gen(rp); a2, b2 = gen(rp)
        bd = np.empty(B3)
        for k in range(B3):
            gs = rng.choice(uniq, size=len(uniq), replace=True)
            idx = np.concatenate([np.where(gg == g)[0] for g in gs])
            bd[k] = spearman(a2[idx], b2[idx]) - spearman(a1[idx], b1[idx])
        lo, hi = np.percentile(bd, [2.5, 97.5]); w.append(hi - lo)
        if not (lo <= 0 <= hi): rej += 1
    sim3.append(dict(genes=gsize, pairs=gsize*P, type1=100*rej/NREP3, ci_width=float(np.mean(w))))
    print(f"  {gsize:3d} 基因（{gsize*P:3d} 对）  I 类错误 = {100*rej/NREP3:5.1f}%  平均 95% CI 宽度 = {np.mean(w):.3f}")

json.dump(dict(seed=SEED, G=G, P=P, npair=NPAIR, rho_sd=RHO_SD,
               n1=N1, nrep2=NREP2, B2=B2, nrep3=NREP3, B3=B3,
               sim1=sim1, sim2=sim2, sim3=sim3),
          open('_sim_results.json', 'w'), indent=1, ensure_ascii=False)
print("\n结果已写入 _sim_results.json")

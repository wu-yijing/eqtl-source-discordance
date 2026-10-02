# -*- coding: utf-8 -*-
"""M15 阳性对照（全向量化版）"""
import os, json
import numpy as np
from collections import Counter
from scipy import stats
from docx import Document
from docx.table import Table
from docx.oxml.ns import qn

AF = r"E:\workbuddy\BMC Genomics投稿资料\定稿资料\Additional file 1_审稿意见修订_20260917.docx"
OUT_DIR = r"E:\workbuddy\GE投稿资料\_重算_20261002\r3\m15"
RNG = np.random.default_rng(20260917)
O = {}
SQ2 = np.sqrt(2)

doc = Document(AF)
tabs = [b for ch in doc.element.body.iterchildren()
        for b in ([Table(ch, doc)] if ch.tag == qn('w:tbl') else [])]
grid = lambda i: [[c.text.strip() for c in r.cells] for r in tabs[i].rows]
drows = lambda i, k=2: [r for r in grid(i)[1:] if len(r) >= k and r[0]]
f = lambda x: (float(x) if x not in (None, '', 'NA', 'nan') else None)

def bh_counts(Z, q=0.05):
    """Z: (B, n) -> 每行 BH q<0.05 显著个数"""
    P = 2 * stats.norm.sf(np.abs(Z))
    P = np.sort(P, axis=1)
    m = P.shape[1]
    thr = q * np.arange(1, m + 1) / m
    ok = P <= thr
    idx = m - 1 - np.argmax(ok[:, ::-1], axis=1)
    return np.where(ok.any(axis=1), idx + 1, 0)

# ---------- 分组与官方 Z ----------
S1 = grid(0); G = {}
for r in S1[1:]:
    if not r[0]:
        continue
    g = r[1]
    G[r[0]] = ('Candidate' if ('Candidate' in g and 'Non' not in g)
               else 'Non-Candidate' if 'Non-Candidate' in g
               else 'T2DM control' if 'T2DM' in g else g)
S2 = grid(1); i2 = {n: k for k, n in enumerate(S2[0])}
GTEX = {(r[0], r[1]): dict(z_nt=f(r[i2['Z_Nerve_Tibial']]), z_wb=f(r[i2['Z_Whole_Blood']]),
                           z_mt=f(r[i2['Z_multi_tissue']]), p_acat=f(r[i2['P_ACAT_O']]),
                           q_acat=f(r[i2['FDR_q_ACAT_O']])) for r in drows(1, 10)}
EQ = {(r[0], r[1]): dict(z=f(r[3]), p=f(r[4]), q=f(r[5]), snps=r[6],
                        fdr=(r[7].strip().lower() in ('yes', 'true', '1'))) for r in drows(18, 8)}

# ---------- 反转清单 ----------
rev = {}
for tag, key in [('Nerve_Tibial', 'z_nt'), ('Whole_Blood', 'z_wb'), ('multi_tissue', 'z_mt')]:
    hits = []
    for (g, t), gt in GTEX.items():
        if G.get(g) != 'Candidate':
            continue
        e = EQ.get((g, t)); zg = gt[key]
        if e is None or zg is None or e['z'] is None:
            continue
        if abs(zg) >= 1.96 and abs(e['z']) >= 1.96 and (zg > 0) != (e['z'] > 0):
            hits.append(dict(gene=g, trait=t, gtex_z=round(zg, 2), eqtlgen_z=round(e['z'], 2)))
    rev['GTEx ' + tag] = dict(n=len(hits), genes=sorted(set(h['gene'] for h in hits)), hits=hits)
O['sign_reversals_official'] = rev
rev2 = []
for (g, t), gt in GTEX.items():
    if G.get(g) != 'Candidate':
        continue
    e = EQ.get((g, t)); zg = gt['z_nt']
    if e is None or zg is None or e['z'] is None or abs(zg) < 1.96:
        continue
    if (zg > 0) != (e['z'] > 0):
        rev2.append(dict(gene=g, trait=t, gtex_nt=round(zg, 2), eqtlgen=round(e['z'], 2)))
O['GTExNT_significant_reversals_any_eqtlgen'] = dict(n=len(rev2),
                                                      genes=sorted(set(h['gene'] for h in rev2)), hits=rev2)
O['spot_check'] = {g: {t: dict(official=GTEX.get((g, t)), eqtlgen=EQ.get((g, t))) for t in ['DR', 'DN', 'DPN']}
                   for g in ['CKAP4', 'HSP90AB1', 'HSP90B1', 'XRCC6']}

# ---------- PC-1a BH 检出边界 ----------
O['PC1a_BH_boundary'] = {str(n): dict(min_p=round(0.05 / n, 6),
                                      min_absZ=round(float(stats.norm.isf(0.025 / n)), 3))
                         for n in [13, 17, 19, 25, 27, 28, 29, 30, 51, 57, 75, 81, 84, 87, 90, 96, 222, 500, 9000]}
# ---------- PC-1b 零假设校准 ----------
B0 = 20000
cal = {}
for n in [17, 27, 28, 84, 87, 90, 222, 9000]:
    c = bh_counts(RNG.normal(size=(B0, n)), 0.05)
    cal[str(n)] = dict(P_any_significant=round(float((c > 0).mean()), 4),
                       mean_n_sig=round(float(c.mean()), 3),
                       pred_boundary_absZ=O['PC1a_BH_boundary'][str(n)]['min_absZ'] if str(n) in O['PC1a_BH_boundary'] else None)
O['PC1b_null_calibration'] = cal

POOL = {'GTEx': np.array([v['z_mt'] for v in GTEX.values() if v['z_mt'] is not None]),
        'eQTLGen': np.array([v['z'] for v in EQ.values() if v['z'] is not None])}
O['null_pool'] = {k: dict(n=int(len(v)), mean=round(float(v.mean()), 3),
                          sd=round(float(v.std(ddof=1)), 3),
                          max_abs=round(float(np.abs(v).max()), 2)) for k, v in POOL.items()}

# ---------- PC-2a 单基因 spike-in 功率曲线（向量化） ----------
STRATA = [('GTEx|Candidate (n=28)', 28, 'GTEx'), ('GTEx|T2DM control (n=19)', 19, 'GTEx'),
          ('GTEx|Housekeeping (n=29)', 29, 'GTEx'), ('GTEx|pooled HK (n=87)', 87, 'GTEx'),
          ('GTEx|pooled cand (n=84)', 84, 'GTEx'),
          ('eQTLGen|Candidate (n=27)', 27, 'eQTLGen'), ('eQTLGen|T2DM control (n=17)', 17, 'eQTLGen'),
          ('eQTLGen|Housekeeping (n=27)', 27, 'eQTLGen'), ('eQTLGen|pooled (n=81)', 81, 'eQTLGen')]
LAMS = [2.0, 2.5, 2.89, 3.13, 3.5, 4.0, 5.0]
B = 4000
PC2 = {}
for lab, n, src in STRATA:
    pool = POOL[src]
    cur = {}
    for k in [1, 2, 3, 5]:
        if k > n:
            continue
        for lam in LAMS:
            null = RNG.choice(pool, size=(B, n - k), replace=True)
            spike = RNG.normal(lam, 1.0, size=(B, k))
            Z = np.concatenate([null, spike], axis=1)
            cur[f'k={k}|lam={lam}'] = round(float((bh_counts(Z) >= 1).mean()), 3)
    mdl = None
    for lam in np.arange(1.5, 6.001, 0.05):
        Z = np.concatenate([RNG.normal(0, 1, size=(B, n - 1)), RNG.normal(lam, 1, size=(B, 1))], axis=1)
        if (bh_counts(Z) >= 1).mean() >= 0.8:
            mdl = round(float(lam), 2); break
    PC2[lab] = dict(n=n, source=src, curves=cur, min_lambda_80pct_k1=mdl)
O['PC2a_single_gene_power'] = PC2

# ---------- PC-2b 组间差的最小可检百分点（精确 Fisher 功效） ----------
def fisher_pv_grid(n1, n2):
    A = np.arange(n1 + 1); Bn = np.arange(n2 + 1)
    Pv = np.empty((n1 + 1, n2 + 1))
    for i, a in enumerate(A):
        for j, b in enumerate(Bn):
            Pv[i, j] = stats.fisher_exact([[a, n1 - a], [b, n2 - b]])[1]
    return A, Bn, Pv
def power(n1, p1, n2, p2, A, Bn, Pv, alpha=0.05):
    Pa = stats.binom.pmf(A, n1, p1); Pb = stats.binom.pmf(Bn, n2, p2)
    return float(((Pv < alpha) * np.outer(Pa, Pb)).sum())
PB = {}
for lab, n1, r1, n2, r2 in [('GTEx (HK 87 @0.0% vs cand 84 @2.4%)', 87, 0.000, 84, 0.024),
                            ('GTEx (HK 87 @5.7% vs cand 84 @9.5%)', 87, 0.057, 84, 0.095),
                            ('eQTLGen (HK 81 @2.5% vs cand 81 @6.2%)', 81, 0.025, 81, 0.062),
                            ('eQTLGen (HK 81 @8.6% vs cand 81 @9.9%)', 81, 0.086, 81, 0.099)]:
    A, Bn, Pv = fisher_pv_grid(n1, n2)
    md = None
    for d in np.arange(0.5, 30.01, 0.5):
        if power(n1, r1, n2, min(0.99, r1 + d / 100), A, Bn, Pv) >= 0.8:
            md = round(float(d), 1); break
    PB[lab] = dict(min_detectable_abs_diff_pp=md,
                   power_at_observed=None,
                   power_curve={str(round(d, 1)): round(power(n1, r1, n2, min(0.99, r1 + d / 100), A, Bn, Pv), 3)
                                for d in [1, 2, 3, 4, 5, 7, 10, 15]})
O['PC2b_group_diff_power'] = PB

# ---------- PC-3 终点实际发火 ----------
fired = []
for (g, t), v in GTEX.items():
    if v['q_acat'] is not None and v['q_acat'] < 0.05:
        fired.append(dict(source='GTEx', gene=g, trait=t, q=round(v['q_acat'], 4), group=G.get(g)))
for r in drows(15, 6):
    q = f(r[4])
    if q is not None and q < 0.05:
        fired.append(dict(source='eQTLGen', gene=r[0], trait=r[1], q=round(q, 4), group='Housekeeping'))
for r in drows(18, 8):
    if r[7].strip().lower() in ('yes', 'true', '1'):
        fired.append(dict(source='eQTLGen', gene=r[0], trait=r[1], q=f(r[5]), group=G.get(r[0])))
O['PC3_endpoint_fired'] = fired
O['PC3_counts'] = {f'{a}|{b}': c for (a, b), c in Counter((x['source'], x['group']) for x in fired).items()}

json.dump(O, open(os.path.join(OUT_DIR, 'm15_positive_control.json'), 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False, default=str)

print('=== 反转：双来源 |Z|>=1.96 且反向 ===')
for k, v in rev.items():
    print('  %-22s n=%d  %s' % (k, v['n'], v['genes']))
print('=== 仅 GTEx NT 显著但与 eQTLGen 反向 === n=%d %s' %
      (O['GTExNT_significant_reversals_any_eqtlgen']['n'], O['GTExNT_significant_reversals_any_eqtlgen']['genes']))
print()
print('=== PC-1a BH 检出边界 ===')
for n in [17, 19, 27, 28, 29, 81, 84, 87, 222, 9000]:
    print('  n=%5d  min|Z| = %.3f' % (n, O['PC1a_BH_boundary'][str(n)]['min_absZ']))
print()
print('=== PC-1b 零假设校准 ===')
for k, v in cal.items():
    print('  n=%5s  P(any)=%.4f  mean=%.3f' % (k, v['P_any_significant'], v['mean_n_sig']))
print()
print('=== PC-2b 组间差最小可检（80% power）===')
for k, v in PB.items():
    print('  %-42s Δmin = %s pp   power@obs = %s' % (k, v['min_detectable_abs_diff_pp'], v['power_at_observed']))
    print('       power curve:', v['power_curve'])
print()
print('=== PC-2a 单基因 80% 功率最小 λ ===')
for k, v in PC2.items():
    print('  %-30s n=%3d  minλ=%s' % (k, v['n'], v['min_lambda_80pct_k1']))
print()
print('=== PC-3 终点发火 ===', O['PC3_counts'])
for x in fired:
    print('   ', x)

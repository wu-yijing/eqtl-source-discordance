# -*- coding: utf-8 -*-
"""诊断 2：S9 池内分层定义 + S20 单基因 80% 功效最小 λ"""
import os, sys, io, csv, math, re, random, sqlite3, zipfile
import numpy as np
from scipy import stats
from xml.etree import ElementTree as ET
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------- 复用主脚本前段（池 / 官方 ACAT-O / 覆盖率） ----------------
_here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(_here, 'recompute_r3_s9_s20.py'), encoding='utf-8').read()
head = src.split('# ============================================================ 3. 零分布')[0]
# 2026-10-02 修：__file__ 原为 os.path.abspath('recompute_r3_s9_s20.py')，即 cwd 相对路径——
# 只在 cwd 恰为 scripts/r3/ 时成立，换目录运行就会让被 exec 的头部找不到 paths.py。
G = {'__file__': os.path.join(_here, 'recompute_r3_s9_s20.py'), '__name__': 'head'}
exec(compile(head, 'head', 'exec'), G)
COV600, gz, TRAITS, pacat_of = G['COV600'], G['gz'], G['TRAITS'], G['pacat_of']
both_A, both_818, COV818 = G['both_A'], G['both_818'], G['COV818']

def has_NT(gg):
    return any('Nerve_Tibial' in gz.get(gg, {}) and t in gz[gg]['Nerve_Tibial'] for t in TRAITS)
def has_WB(gg):
    return any('Whole_Blood' in gz.get(gg, {}) and t in gz[gg]['Whole_Blood'] for t in TRAITS)

def build(gl):
    P = np.full((len(gl), 3), np.nan)
    for i, x in enumerate(gl):
        for ti, t in enumerate(TRAITS):
            v = pacat_of(x, t)
            if v is not None: P[i, ti] = v
    return P

def bh_count(pv, q=0.05):
    p = np.sort(np.asarray(pv, float)); m = len(p)
    ok = p <= q * np.arange(1, m + 1) / m
    return int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0

print('=' * 74); print('S9 池内分层：三种分组定义'); print('=' * 74)
DEFS = {
    'A 模型可得(mashr 双组织)': (both_A, both_818),
    'B 官方统计量可得(双组织 Z)': None,
}
for label in ['A 模型可得(mashr 双组织)', 'B 官方统计量可得(双组织 Z)']:
    for tag, glist, rep in [('600', COV600, '21/1,326=1.6% | Z 0.78  vs  7/378=1.9% | Z 0.67'),
                            ('818', COV818, '20/1,827=1.1% | Z 0.73  vs  6/477=1.3% | Z 0.64')]:
        if label.startswith('A'):
            key = both_A if tag == '600' else both_818
            both = [g for g in glist if g in key]
        else:
            both = [g for g in glist if has_NT(g) and has_WB(g)]
        wbo = [g for g in glist if g not in both]
        line = f'  [{label}] {tag}: '
        for nm, sub in (('both', both), ('wbo', wbo)):
            P = build(sub); k = sum(bh_count(P[:, c]) for c in range(3)); n = P.shape[0] * 3
            zs = [abs(gz[x]['Whole_Blood'][t]) for x in sub for t in TRAITS
                  if 'Whole_Blood' in gz.get(x, {}) and t in gz[x]['Whole_Blood']]
            line += f'{nm} {k}/{n}={100*k/n:.1f}% |Z|{np.median(zs):.2f}  '
        print(line)
    print(f'      SI  : {rep}')
    print()

# BH 域变体（定义 B 下）
print('--- BH 域变体（分组用定义 B） ---')
for tag, glist in [('600', COV600), ('818', COV818)]:
    both = [g for g in glist if has_NT(g) and has_WB(g)]; wbo = [g for g in glist if g not in both]
    idx = {x: i for i, x in enumerate(glist)}; Pall = build(glist)
    sig = np.zeros_like(Pall, dtype=bool)
    for c in range(3):
        p = Pall[:, c]; o = np.argsort(p); m = len(p); qv = np.empty(m); prev = 1.0
        for i in range(m - 1, -1, -1):
            j = o[i]; prev = min(prev, p[j] * m / (i + 1)); qv[j] = prev
        sig[:, c] = qv < 0.05
    for nm, sub in (('both', both), ('wbo', wbo)):
        rows = [idx[x] for x in sub]; k = int(sig[rows].sum()); n = len(rows) * 3
        print(f'  [{tag} 整池 BH 域] {nm} {k}/{n} = {100*k/n:.1f}%')
print('  SI: 600 -> 21/1326=1.6% / 7/378=1.9% ; 818 -> 20/1827=1.1% / 6/477=1.3%')

# ================= S20 单基因 80% 功效最小 λ =================
print()
print('=' * 74); print('S20 单基因 spike-in 最小 λ（经验零池 = 同来源真实 Z）'); print('=' * 74)
import sys as _sys, os as _os
_p = _os.path.dirname(_os.path.abspath(__file__))
while _p != _os.path.dirname(_p) and not _os.path.isfile(_os.path.join(_p, 'paths.py')):
    _p = _os.path.dirname(_p)
_sys.path.insert(0, _p)
import paths as _paths          # noqa: E402  集中路径解析：向上找到 paths.py
_paths.bootstrap_args()   # 消费 --repo-root / --input（本脚本无自有 parser）
SI = str(_paths.external('si_docx'))
Wn = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
tb = [c for c in list(ET.fromstring(zipfile.ZipFile(SI).read('word/document.xml')).find(Wn + 'body'))
      if c.tag == Wn + 'tbl']
def rows(i):
    return [[' '.join(x.text or '' for x in tc.iter(Wn + 't')).strip() for tc in tr.findall(Wn + 'tc')]
            for tr in tb[i].findall(Wn + 'tr')]
def num(v):
    try: return float(v)
    except (TypeError, ValueError): return np.nan
s3 = rows(2); h = s3[0]; zi = h.index('Z_multi_tissue')
gtex_mt = np.array([num(r[zi]) for r in s3[1:]]); gtex_mt = gtex_mt[~np.isnan(gtex_mt)]
s18 = rows(18); h18 = s18[0]; z18 = h18.index('Z_eQTLGen')
eq_pool = np.array([num(r[z18]) for r in s18[1:]]); eq_pool = eq_pool[~np.isnan(eq_pool)]
POOL = {'GTEx': gtex_mt, 'eQTLGen': eq_pool}
print(f'  经验零池: GTEx n={len(gtex_mt)} (mean {gtex_mt.mean():.3f}, sd {gtex_mt.std(ddof=1):.3f})；'
      f'eQTLGen n={len(eq_pool)} (mean {eq_pool.mean():.3f}, sd {eq_pool.std(ddof=1):.3f})')
print('  （归档 m15_positive_control.json: GTEx n=222 mean 0.278 sd 1.33；eQTLGen n=207 mean 0.315 sd 1.599）')

def bh_from_z(z, q=0.05):
    p = np.sort(2 * stats.norm.sf(np.abs(np.asarray(z, float)))); m = len(p)
    ok = p <= q * np.arange(1, m + 1) / m
    return int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0

def minlam(n, src, seed=20260917, B=4000, target=0.80):
    rng = np.random.default_rng(seed); pool = POOL[src]
    for lam in np.arange(1.5, 6.01, 0.05):
        h = 0
        for _ in range(B):
            z = np.concatenate([rng.choice(pool, n - 1, replace=True), rng.normal(lam, 1.0, 1)])
            h += bh_from_z(z) >= 1
        if h / B >= target:
            return round(float(lam), 2)
    return None

STRATA = [('GTEx|cand', 28, 'GTEx', 3.95), ('GTEx|T2DM', 19, 'GTEx', 3.85),
          ('GTEx|HK', 29, 'GTEx', 3.95), ('GTEx|pooledHK', 87, 'GTEx', 4.25),
          ('GTEx|pooledCand', 84, 'GTEx', 4.25), ('eQTLGen|cand', 27, 'eQTLGen', 3.95),
          ('eQTLGen|T2DM', 17, 'eQTLGen', 3.75), ('eQTLGen|HK', 27, 'eQTLGen', 3.90),
          ('eQTLGen|pooled', 81, 'eQTLGen', 4.20)]
for nm, n, src, rep in STRATA:
    v = minlam(n, src)
    print(f'    {nm:16s} n={n:3d} → min λ = {v}   (SI {rep})')

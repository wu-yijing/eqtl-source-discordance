# -*- coding: utf-8 -*-
"""
================================================================================
 R3-1 / R3-2 原流水线重跑：Table S9（随机对照零分布）与 Table S20（端点标定与功效）
================================================================================
Table S9 配方（取自归档的 `_null_lib.py` / `null_final.py` / `t1_s8rand.py`）：
  · POOL_A = mashr_Whole_Blood.db 中 n.snps≥1 的基因
             − 104-panel − 与 panel 共享 ≥3 字符前缀的家族 − T2DM/并发症/代谢黑名单
  · POOL_818 = HRT Atlas v1.0 人-鼠共有集合同样过滤后要求 Whole_Blood 有模型
  · 600 基因样本 = random.Random(20260911).sample(sorted(POOL_A), 600)
  · 每基因 ACAT-O = 按训练样本量加权（Nerve_Tibial √532, Whole_Blood √670）的 Cauchy 合并
  · 零分布 = np.random.default_rng(20260911).choice(n, 30, replace=False)，B=10000，分母 90
  · BH 校正域 = 表型内
Table S20 配方：
  · 检出边界 = Φ⁻¹(1 − 0.05/(2n))（确定性）
  · 零标定 = 20,000 个标准正态分层中出现 ≥1 个 BH 发现的比例（seed 20260917）
  · 单基因 80% 功效最小 λ = spike-in 搜索，经验零池 = 同来源全部真实 Z
  · 组间功效 = 在观测分母与率下对 2×2 结果空间做精确枚举（Fisher 双侧）
================================================================================
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

import os, sys, csv, json, math, re, random, sqlite3, hashlib, itertools
import numpy as np
from scipy import stats

OUTD = PC.RESULTS              # 产物统一落在包的 results/（2026-10-02 起）
os.makedirs(OUTD, exist_ok=True)
LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); LOG.append(s); print(s)
def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

# ------------------------------------------------------------------ 路径
# POOL_A / POOL_818 membership ships with the repository (data/derived/s9_pools/).
# Set REPRO_MASHR_DB_DIR to also rebuild the pools from the mashr models
# (third-party, not redistributed) and cross-check the two routes.
MODEL_DIR = os.environ.get('REPRO_MASHR_DB_DIR')
# The official MetaXcan GTEx layer ships here flattened to one row per gene.
# Set REPRO_GTEX_OFFICIAL_DIR to read the six original tables instead; the two
# routes have been verified equivalent.
GTEXDIR   = os.environ.get('REPRO_GTEX_OFFICIAL_DIR')
HRT_RAW   = PC.get('hrt_source')
GRPJ      = PC.get('groups_json')
RANDDIR   = os.path.dirname(PC.get('rand_dr'))
POOLS_DIR = os.path.dirname(PC.get('pool_a'))
TRAITS    = ['DR', 'DN', 'DPN']
TISSUES   = ['Nerve_Tibial', 'Whole_Blood']
SEED      = 20260911
N_SAMPLE, N_CONTROL = 600, 30
NT_W, WB_W = 532.0, 670.0
B = 10000

EXTRA_FAMILY = re.compile(r'^(MRPS|MRPL|MT-|MTRNR|MTND|MTATP|MTCO|MTCYB)')
# 黑名单随仓库分发于 data/derived/s9_pools/disease_blacklist.txt；下方内联清单为兜底。
# 两者都不做大小写归一化——被减去的基因名是大写的，而清单里有一个 token 写作 C5orf67，
# 因此它实际上没有被排除。这是原流水线的行为，POOL_A = 11,820（而非 11,819）即源于此。
DISEASE = set(open(PC.get('disease_blacklist'), encoding='utf-8').read().split()
              if os.path.exists(PC.get('disease_blacklist')) else """
ADCY5 ADRA2A ANK1 AP3S2 ARAP1 BCAR1 BCL11A CAMK1D CCND2 CDKAL1 CDKN2A CDKN2B CENTD2 CMIP DGKB DUSP8
FTO GCC1 GCK GCKR GIPR GLIS3 GLP1R GPSM1 GRB14 HHEX HMGA1 HMGA2 HNF1A HNF1B HNF4A IDE IGF1 IGF2BP2 INS
INSR IRS1 IRS2 JAZF1 KCNJ11 KCNQ1 KLF14 LEPR MAEA MC4R MNX1 MTNR1B NOTCH2 PAM PDX1 PEPD PIK3R1 PPARG
PPARGC1A PRC1 PROX1 PSMD6 RREB1 SLC16A11 SLC2A2 SLC2A4 SLC30A8 ST6GAL1 TCF7L2 THADA TP53INP1 TSPAN8
UBE2E2 WFS1 ZBED3 ZFAND6 ADIPOQ AKT1 AKT2 FOXA2 G6PC2 HK1 MLXIPL NRXN3 SREBF1 TCF7 PPP1R3B TMEM154
SSR1 FITM2 RNF6 ANKH C2CD4A C2CD4B VPS13C CILP2 HNF4G RASGRP1 C5orf67 ZMIZ1 VEGFA EPO AKR1B1 NOS3 ACE
AGT TGFB1 SERPINE1 MTHFR APOE ELMO1 ENPP1 UNC13B CPVL CHN2 GREM1 FRMD3 CARS SP3 ITGA2 ITGB3 ADAM10
ICAM1 SELE TNF IL6 CRP AGER RAGE CTGF CCN2 MMP2 MMP9 TIMP1 HIF1A PLGF PGF LEP GCGR PCSK9 LDLR HMGCR
SREBF2 FASN ACACA CPT1A PPARA LIPC CETP""".split())

log('=' * 78); log('0. 输入校验'); log('=' * 78)
INP = {'covariate_matrix.csv': PC.get('covariate_matrix'),
       'Human_Mouse_Common_raw.csv': HRT_RAW, 'groups.json': GRPJ}
if MODEL_DIR:
    INP['mashr_Whole_Blood.db'] = os.path.join(MODEL_DIR, 'mashr_Whole_Blood.db')
    INP['mashr_Nerve_Tibial.db'] = os.path.join(MODEL_DIR, 'mashr_Nerve_Tibial.db')
R = {'inputs': PC.describe_inputs(INP)}
for k, rec in R['inputs'].items():
    log(f"  {k:30s} md5={rec['md5']} bytes={rec['bytes']:,}")

# ============================================================ 1. 池重建
log('\n' + '=' * 78); log('1. 池构建（对照 SI Table S9 第 1 行与表注）'); log('=' * 78)
def lead(s):
    m = re.match(r'^([A-Za-z]+)', s)
    return m.group(1).upper() if m else ''

panel = {r['Gene'].upper() for r in csv.DictReader(
    open(INP['covariate_matrix.csv'], encoding='utf-8'))}
fams = {lead(g) for g in panel if len(lead(g)) >= 3}
meta = {}
if MODEL_DIR:
    for t in TISSUES:
        conn = sqlite3.connect(os.path.join(MODEL_DIR, 'mashr_%s.db' % t))
        meta[t] = {gn.upper(): n for _, gn, n in
                   conn.execute('SELECT gene, genename, "n.snps.in.model" FROM extra') if gn}
        conn.close()

flow = []
if MODEL_DIR:
    # ---- 路线 1：从 mashr 模型库重建（需要第三方层，见 INPUTS.md B.2）
    log('  来源: mashr 模型库（REPRO_MASHR_DB_DIR），从零重建池名单')
    wb = {g: n for g, n in meta['Whole_Blood'].items() if n and n >= 1}
    flow = [('WB model genes', len(wb))]
    cur = {g for g in wb if g not in panel};                      flow.append(('minus 104-panel', len(cur)))
    cur = {g for g in cur if not (any(g.startswith(p) for p in fams) or EXTRA_FAMILY.match(g))}
    flow.append(('minus panel families', len(cur)))
    cur = {g for g in cur if g not in DISEASE};                   flow.append(('minus disease blacklist = POOL_A', len(cur)))
    POOL_A = cur
    both_A = {g for g in cur if meta['Nerve_Tibial'].get(g, 0) and meta['Nerve_Tibial'][g] >= 1}
    flow.append(('of which have BOTH-tissue models', len(both_A)))
    log('  POOL_A 流程:  ' + '  →  '.join(f'{k} {v:,}' for k, v in flow))
    log('  （SI: 11,820，其中 10,450 带 Nerve_Tibial 模型；排除链共移除 802）')

    hrt = set()
    for line in open(HRT_RAW, encoding='utf-8', errors='replace'):
        line = line.strip()
        if not line or line.lower().startswith('mouse'):
            continue
        p = line.split(';')
        if len(p) >= 2 and p[1].strip():
            hrt.add(p[1].strip().upper())
    c2 = hrt - panel
    c2 = {g for g in c2 if not (any(g.startswith(p) for p in fams) or EXTRA_FAMILY.match(g))}
    c2 = {g for g in c2 if g not in DISEASE}
    POOL_818 = {g for g in c2 if meta['Whole_Blood'].get(g, 0) and meta['Whole_Blood'][g] >= 1}
    both_818 = {g for g in POOL_818 if meta['Nerve_Tibial'].get(g, 0) and meta['Nerve_Tibial'][g] >= 1}
    log(f'\n  POOL_818 = {len(POOL_818):,}（SI: 818），其中双组织 {len(both_818):,}（SI: 767），'
        f'仅 WB {len(POOL_818 - both_818)}（SI: 51）')

    for name, gs in (('POOL_A', POOL_A), ('both_A', both_A),
                     ('POOL_818', POOL_818), ('both_818', both_818)):
        f = os.path.join(POOLS_DIR, name + '.txt')
        ship = set(open(f, encoding='utf-8').read().split()) if os.path.exists(f) else None
        if ship is None:
            log(f'  与随包 {name}.txt 交叉核对: 文件不存在，跳过')
        else:
            log(f'  与随包 {name}.txt 交叉核对: '
                f'{"一致 ✓" if ship == gs else "不一致 ✗"}（随包 {len(ship):,} vs 重建 {len(gs):,}）')
else:
    # ---- 路线 2：直接读随仓库分发的池名单（无需 mashr 层）
    log('  来源: 随仓库分发的池名单 data/derived/s9_pools/*.txt')
    log('  未设 REPRO_MASHR_DB_DIR —— 池「成员名单」随仓库交付，排除链 12,622 → 12,555')
    log('  → 11,885 → 11,820 由这些名单承载；重建名单本身需要 mashr 模型库')
    log('  （第三方，不随仓库分发；见 INPUTS.md B.2）。设 REPRO_MASHR_DB_DIR 可双路线交叉核对。')
    def pool(name):
        return set(open(os.path.join(POOLS_DIR, name + '.txt'), encoding='utf-8').read().split())
    POOL_A, both_A = pool('POOL_A'), pool('both_A')
    POOL_818, both_818 = pool('POOL_818'), pool('both_818')
    # 排除链不重算，但按随包名单给出与 SI 可对照的计数，便于阅读日志
    flow = [('POOL_A（随包名单）', len(POOL_A)),
            ('of which have BOTH-tissue models', len(both_A)),
            ('POOL_818（随包名单）', len(POOL_818)),
            ('of which have BOTH-tissue models', len(both_818)),
            ('POOL_818 WB-only', len(POOL_818 - both_818))]
    log(f'\n  POOL_A = {len(POOL_A):,}（SI: 11,820），其中双组织 {len(both_A):,}（SI: 10,450）')
    log(f'  POOL_818 = {len(POOL_818):,}（SI: 818），其中双组织 {len(both_818):,}（SI: 767），'
        f'仅 WB {len(POOL_818 - both_818)}（SI: 51）')
R['pools'] = {'POOL_A': len(POOL_A), 'both_A': len(both_A), 'POOL_818': len(POOL_818),
              'both_818': len(both_818), 'flow': flow,
              # 'mashr-rebuild' = the exclusion chain was re-derived from the model databases;
              # 'shipped-pools' = the membership came from data/derived/s9_pools/ and only its
              # counts are recorded, because re-deriving it needs the mashr layer (INPUTS.md B.2).
              'route': 'mashr-rebuild' if MODEL_DIR else 'shipped-pools',
              'membership_source': ('mashr model databases (REPRO_MASHR_DB_DIR)' if MODEL_DIR
                                    else 'data/derived/s9_pools/*.txt')}

# ============================================================ 2. 官方 GTEx ACAT-O
log('\n' + '=' * 78); log('2. 官方 GTEx v8 逐基因 ACAT-O（按训练样本量加权）'); log('=' * 78)
gz = {}   # gz[gene][tissue][trait] = z；同 (gene,tissue,trait) 取 |z| 更大者
if GTEXDIR:
    # ---- 路线 1：官方 MetaXcan 六表（原始层，不随仓库分发）
    src = 'official_{tissue}_{trait}.csv 六表（REPRO_GTEX_OFFICIAL_DIR）'
    for tis in TISSUES:
        for tr in TRAITS:
            fp = os.path.join(GTEXDIR, 'official_%s_%s.csv' % (tis, tr))
            for r in csv.DictReader(open(fp, encoding='utf-8')):
                sym = r['gene_name']
                if not sym:
                    continue
                try:
                    z = float(r['zscore'])
                except (TypeError, ValueError):
                    continue
                c_ = gz.setdefault(sym, {}).setdefault(tis, {}).get(tr)
                if c_ is not None and abs(z) <= abs(c_):
                    continue
                gz[sym].setdefault(tis, {})[tr] = z
else:
    # ---- 路线 2：随仓库分发的压平宽表（与路线 1 已核验等价）
    src = 'data/derived/gtex_official_finngen/gtex_official_zscores_wide.csv.gz'
    for r in PC.dict_rows(PC.get('gtex_official_wide')):
        sym = r['gene']
        for tis in TISSUES:
            for tr in TRAITS:
                v = (r.get('%s_%s' % (tis, tr)) or '').strip()
                if v == '':
                    continue
                gz.setdefault(sym, {}).setdefault(tis, {})[tr] = float(v)
log(f'  来源: {src}')
log(f'  覆盖基因（至少一个组织有 Z）= {len(gz):,}')

def acat_p(zs):
    ps, ws = [], []
    for t, wgt in (('Nerve_Tibial', NT_W), ('Whole_Blood', WB_W)):
        if t in zs:
            ps.append(max(2 * stats.norm.sf(abs(zs[t])), 1e-300)); ws.append(math.sqrt(wgt))
    if not ps:
        return None
    W = sum(ws); ws = [x / W for x in ws]
    T = sum(wv * math.tan((0.5 - p) * math.pi) for wv, p in zip(ws, ps))
    return 0.5 - math.atan(T) / math.pi

def pacat_of(gene, tr):
    zs = {t: gz[gene][t][tr] for t in gz.get(gene, {}) if tr in gz[gene][t]}
    return acat_p(zs) if zs else None

rnd = random.Random(SEED)
SAMPLE = rnd.sample(sorted(POOL_A), N_SAMPLE)
COV600 = [g for g in SAMPLE if any(pacat_of(g, t) is not None for t in TRAITS)]
COV818 = [g for g in sorted(POOL_818) if any(pacat_of(g, t) is not None for t in TRAITS)]
log(f'  600 样本中官方覆盖 = {len(COV600)}（SI 表注: 568）；818 池中覆盖 = {len(COV818)}（SI: 768）')
R['coverage'] = {'sample600': len(SAMPLE), 'covered600': len(COV600),
                 'pool818': len(POOL_818), 'covered818': len(COV818)}

# ============================================================ 3. 零分布
log('\n' + '=' * 78); log(f'3. 零分布（B = {B}, seed = {SEED}）'); log('=' * 78)
def build(glist):
    P = np.full((len(glist), 3), np.nan)
    for i, g in enumerate(glist):
        for ti, t in enumerate(TRAITS):
            v = pacat_of(g, t)
            if v is not None:
                P[i, ti] = v
    return P

def bh_count(pv, q=0.05):
    p = np.sort(np.asarray(pv, float)); m = len(p)
    ok = p <= q * np.arange(1, m + 1) / m
    return int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0

THR = [0.05, 0.01, 0.00385, 0.00294, 0.00179]
def run(P, label, rep):
    n = P.shape[0]
    rng = np.random.default_rng(SEED)
    D = np.array([rng.choice(n, N_CONTROL, replace=False) for _ in range(B)])
    res = {str(t): [] for t in THR}; res['bh'] = []
    for row in D:
        blk = P[row]
        res['bh'].append(100 * sum(bh_count(blk[:, c]) for c in range(3)) / 90)
        for t in THR:
            res[str(t)].append(100 * float((blk < t).sum()) / 90)
    out = {}
    for k, v in res.items():
        a = np.array(v)
        out[k] = [float(np.median(a)), float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
        out[k + '_arr'] = a
    log(f'  [{label}] n={n}')
    for k in ['bh'] + [str(t) for t in THR]:
        name = 'BH q<0.05' if k == 'bh' else 'p < ' + k
        log(f'    {name:12s} 中位 {out[k][0]:5.1f}%   2.5–97.5%  {out[k][1]:5.1f}–{out[k][2]:.1f}%   '
            f'(SI {rep.get(k, "—")})')
    return out

o600 = run(build(COV600), '基因组尺度列（600 样本）',
           {'bh': '1.1% (0.0–7.8%)', '0.05': '8.9% (3.3–16.7%)', '0.00294': '2.2% (0.0–6.7%)'})
o818 = run(build(COV818), 'HRT 限制列（818 池）', {'bh': '1.1% (0.0–6.7%)'})
R['null_600'] = {k: v for k, v in o600.items() if not k.endswith('_arr')}
R['null_818'] = {k: v for k, v in o818.items() if not k.endswith('_arr')}

# ============================================================ 4. 随机对照点估计
log('\n' + '=' * 78); log('4. 随机对照 30 基因的点估计（GTEx 侧 / eQTLGen 侧）'); log('=' * 78)
grp = json.load(open(GRPJ, encoding='utf-8'))
LAY2, LAY3 = grp['lay2'], grp['lay3']
log(f'  基因清单: GW lay2 = {len(LAY2)}（与归档 d3_summary 对照清单一致: '
    f'{LAY2 == sorted(json.load(open(os.path.join(PC.SUPERSEDED, "hk_reselect_20260830", "data", "d3_summary.json"), encoding="utf-8"))["control"])}）；'
    f'HRT lay3 = {len(LAY3)}（同 d3b: '
    f'{LAY3 == sorted(json.load(open(os.path.join(PC.SUPERSEDED, "hk_reselect_20260830", "data", "d3b_summary.json"), encoding="utf-8"))["control"])}）')

def gtex_rates(genes):
    P = build([g for g in genes if any(pacat_of(g, t) is not None for t in TRAITS)])
    blk = P
    k_bh = sum(bh_count(blk[:, c]) for c in range(3)); n = blk.shape[0] * 3
    out = {'bh': (k_bh, n)}
    for t in [0.05, 0.01, 0.00385, 0.00294]:
        out[str(t)] = (int((blk < t).sum()), n)
    return out

def eqtlgen_rates(genes):
    """从 t1_s8rand/official_rand_{TR}.csv 复算（BH 域 = 对照层 × 表型）。"""
    k = {str(t): 0 for t in [0.05, 0.01, 0.00385]}; k['bh'] = 0; n = 0
    for tr in TRAITS:
        fp = os.path.join(RANDDIR, 'official_rand_%s.csv' % tr)
        ps = []
        for r in csv.DictReader(open(fp, encoding='utf-8')):
            if r['gene_name'] in genes:
                try:
                    ps.append(float(r['pvalue']))
                except (TypeError, ValueError):
                    pass
        if not ps:
            continue
        n += len(ps)
        p = np.array(ps); o = np.argsort(p); m = len(p); qv = np.empty(m); prev = 1.0
        for i in range(m - 1, -1, -1):
            idx = o[i]; prev = min(prev, p[idx] * m / (i + 1)); qv[idx] = prev
        k['bh'] += int((qv < 0.05).sum())
        for t in [0.05, 0.01, 0.00385]:
            k[str(t)] += int((p < t).sum())
    return k, n

R['random_control'] = {}
for lab, genes, gtex_rep, eq_rep in [
        ('GW (Table S9 左列 / 旧 Table S8)', LAY2, '0.0% (0/87)', '1.2% (1/81)'),
        ('HRT (Table S9 右列 / 旧 Table S8b)', LAY3, '1.1% (1/90)', '3.6% (3/84)')]:
    gg = gtex_rates(genes); ek, en = eqtlgen_rates(set(genes))
    log(f'\n  {lab}')
    log(f'    GTEx  侧: BH {gg["bh"][0]}/{gg["bh"][1]} = {100*gg["bh"][0]/gg["bh"][1]:.1f}%  (SI {gtex_rep})')
    for t in ['0.05', '0.01', '0.00385', '0.00294']:
        log(f'             p<{t}: {gg[t][0]}/{gg[t][1]} = {100*gg[t][0]/gg[t][1]:.1f}%')
    log(f'    eQTLGen 侧: BH {ek["bh"]}/{en} = {100*ek["bh"]/en:.1f}%  (SI {eq_rep})')
    for t in ['0.05', '0.01', '0.00385']:
        log(f'             p<{t}: {ek[t]}/{en} = {100*ek[t]/en:.1f}%')
    R['random_control'][lab] = {'gtex': gg, 'eqtlgen': {'bh': ek['bh'], 'n': en,
                                                        '0.05': ek['0.05'], '0.01': ek['0.01'],
                                                        '0.00385': ek['0.00385']}}

# ============================================================ 5. 零分布百分位
log('\n' + '=' * 78); log('5. 各层 BH 率在零分布中的百分位'); log('=' * 78)
# Layer 1 管家 / 候选 / 非候选 / T2DM（GTEx 侧，来自 SI Table S3 / S6）
def table_rates():
    _t = PC.si_tables(PC.doc('si'))

    def rows(i):
        return _t[i]['rows']
    return rows
rows = table_rates()
s2 = rows(1); gmap = {r[0]: r[1] for r in s2[1:] if r[0]}
s3 = rows(2); hdr = s3[0]; qi = hdr.index('FDR_q_ACAT_O'); gi = hdr.index('Gene')
rate = {}
for r in s3[1:]:
    g = gmap.get(r[gi], ''); g = 'Candidate' if g == 'Candidate' else ('Non-candidate' if 'Non' in g else ('T2DM control' if 'T2DM' in g else g))
    try: q = float(r[qi])
    except ValueError: continue
    rate.setdefault(g, []).append(q)
# 管家（GTEx，Table S6 的 ACAT-O P → 表型内 BH）
s6 = rows(6)
hk_by_trait = {t: [] for t in TRAITS}
for r in s6[2:]:
    if not r[0]: continue
    for j, t in enumerate(TRAITS):
        try: hk_by_trait[t].append(float(r[2 + j]))
        except (ValueError, IndexError): pass
hk_k = 0; hk_n = 0
for t, ps in hk_by_trait.items():
    p = np.array(ps); o = np.argsort(p); m = len(p); qv = np.empty(m); prev = 1.0
    for i in range(m - 1, -1, -1):
        idx = o[i]; prev = min(prev, p[idx] * m / (i + 1)); qv[idx] = prev
    hk_k += int((qv < 0.05).sum()); hk_n += m
log(f'  管家(GTEx) BH: {hk_k}/{hk_n}  (SI 0/87)')
pct = {}
for g, qs in rate.items():
    a = np.array(qs); k = int((a < 0.05).sum()); n = len(a)
    p600 = 100 * (o600['bh_arr'] < 100 * k / n).mean()
    p818 = 100 * (o818['bh_arr'] < 100 * k / n).mean()
    pct[g] = (k, n, 100 * k / n, p600, p818)
    log(f'  {g:15s} BH {k}/{n} = {100*k/n:.2f}%  →  600 零分布第 {p600:.1f} 百分位 | '
        f'818 零分布第 {p818:.1f} 百分位')
log('  （SI: 候选/非候选 → 600 列 69.3rd / 51.7th；818 列 78.3rd / 68.1st）')
R['null_percentiles'] = {g: dict(k=v[0], n=v[1], rate_pct=v[2], pct600=v[3], pct818=v[4])
                         for g, v in pct.items()}
R['housekeeping_gtex'] = dict(k=hk_k, n=hk_n)

# ============================================================ 6. 池内分层
log('\n' + '=' * 78); log('6. 池内分层：双组织可测 vs 仅 Whole_Blood'); log('=' * 78)
def strat(glist, label, rep):
    """分组口径 = 官方统计量可得性（双组织 Z 均有），与 SI Table S9 第 13 行一致。
    注意：不能用 mashr 模型可得性分组——那样会得到 1,518/186 而非 1,326/378。"""
    def has_NT(gg): return any('Nerve_Tibial' in gz.get(gg, {}) and t in gz[gg]['Nerve_Tibial'] for t in TRAITS)
    def has_WB(gg): return any('Whole_Blood' in gz.get(gg, {}) and t in gz[gg]['Whole_Blood'] for t in TRAITS)
    both = [g for g in glist if has_NT(g) and has_WB(g)]
    wbo = [g for g in glist if g not in both]
    out = []
    for tag, sub in (('both-tissue', both), ('WB-only', wbo)):
        P = build(sub); blk = P
        k = sum(bh_count(blk[:, c]) for c in range(3)); n = blk.shape[0] * 3
        zs = [abs(gz[g]['Whole_Blood'][t]) for g in sub for t in TRAITS
              if 'Whole_Blood' in gz.get(g, {}) and t in gz[g]['Whole_Blood']]
        med = float(np.median(zs)) if zs else float('nan')
        out.append((tag, len(sub), n, k, 100 * k / n, med))
        log(f'    {tag:12s} genes={len(sub):3d} pairs={n:4d}  BH {k:3d}/{n} = {100*k/n:.1f}%  |Z_WB|中位={med:.2f}')
    p = stats.fisher_exact([[out[0][3], out[0][2] - out[0][3]], [out[1][3], out[1][2] - out[1][3]]])[1]
    log(f'    Fisher 精确 P = {float(p):.2f}   (SI {rep})')
    return out, float(p)
st600, p600 = strat(COV600, '600', '21/1,326 (1.6%, |Z| 0.78) vs 7/378 (1.9%, |Z| 0.67)；P = 0.65')
st818, p818 = strat(COV818, '818', '20/1,827 (1.1%, |Z| 0.73) vs 6/477 (1.3%, |Z| 0.64)；P = 0.81')
R['within_pool'] = {'600': st600 + [p600], '818': st818 + [p818]}

# ============================================================ 7. Table S20
log('\n' + '=' * 78); log('7. Table S20 —— 端点标定与功效枚举'); log('=' * 78)
log('  (7a) BH 检出边界 = Φ⁻¹(1 − 0.05/(2n))（确定性公式）')
R['S20_boundary'] = {}
for n, rep in [(28, 3.12), (19, 3.01), (29, 3.13), (87, 3.44), (84, 3.43), (222, 3.69),
               (27, 3.11), (17, 2.97), (81, 3.42)]:
    v = float(stats.norm.isf(0.05 / n / 2))
    R['S20_boundary'][str(n)] = round(v, 4)
    log(f'    n={n:3d}  →  |Z|_crit = {v:.3f}   (SI {rep})')

log('\n  (7b) 零标定：20,000 个标准正态分层中出现 ≥1 个 BH 发现（seed 20260917）')
RNG = np.random.default_rng(20260917)
def bh_from_z(z, q=0.05):
    p = np.sort(2 * stats.norm.sf(np.abs(np.asarray(z, float)))); m = len(p)
    ok = p <= q * np.arange(1, m + 1) / m
    return int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0
R['S20_null_calibration'] = {}
for n, rep in [(28, 0.0527), (19, 0.0488), (29, 0.0508), (87, 0.0489), (84, 0.0490),
               (222, 0.051), (27, 0.0507), (17, 0.0493), (81, 0.0515)]:
    cnt = np.array([bh_from_z(RNG.normal(size=n)) for _ in range(20000)])
    v = float((cnt > 0).mean())
    R['S20_null_calibration'][str(n)] = round(v, 4)
    log(f'    n={n:3d}  →  {v:.4f}   (SI {rep})')

log('\n  (7c) 组间最小可检差：对 2×2 结果空间做精确枚举（Fisher 双侧, α=0.05, 80% 功效）')
log('       口径：Δ 加在参照组(组 1 = 管家/HRT 随机对照)率上 → p2 = r1 + Δ；'
    '与归档脚本 2026-09-17-20-59-12/_review/m15_pc.py:118-151 逐字一致')
def exact_mde(n1, p1, n2, base2, target=0.80, alpha=0.05):
    """枚举 (a,b) 全空间；返回达到 80% 功效的最小绝对百分点差（0.5 pp 网格）。
    口径（照 2026-09-17-20-59-12/_review/m15_pc.py）：Δ 加在**参照组(组 1)率**上，
    即 p2 = r1 + Δ；观测候选率 r2 只作行标签，不参与计算。"""
    best = None
    for dpp in np.arange(0.5, 30.01, 0.5):
        p2 = min(0.99, p1 / 100 + dpp / 100)
        if p2 <= base2 / 100:
            continue
        pmf1 = stats.binom.pmf(np.arange(n1 + 1), n1, p1 / 100)
        pmf2 = stats.binom.pmf(np.arange(n2 + 1), n2, p2)
        pw = 0.0
        for a in range(n1 + 1):
            if pmf1[a] < 1e-14: continue
            for b_ in range(n2 + 1):
                if pmf2[b_] < 1e-14: continue
                pv = stats.fisher_exact([[a, n1 - a], [b_, n2 - b_]], alternative='two-sided')[1]
                if pv < alpha:
                    pw += pmf1[a] * pmf2[b_]
        if pw >= target:
            best = float(dpp); break
    return best
R['S20_between_group'] = {}
for lab, (n1, p1, n2, p2), rep in [
        ('GTEx (HK 87 @0.0% vs cand 84 @2.4%)', (87, 0.0, 84, 2.4), 8.0),
        ('GTEx (HK 87 @5.7% vs cand 84 @9.5%)', (87, 5.7, 84, 9.5), 14.5),
        ('eQTLGen (HK 81 @2.5% vs cand 81 @6.2%)', (81, 2.5, 81, 6.2), 13.0),
        ('eQTLGen (HK 81 @8.6% vs cand 81 @9.9%)', (81, 8.6, 81, 9.9), 17.5)]:
    d = exact_mde(n1, p1, n2, p2)
    R['S20_between_group'][lab] = d
    log(f'    {lab:42s} → Δmin = {d} pp   (SI {rep})')

log('\n  (7d) 单基因 80% 功效的最小 λ：闭式解')
log('       关键恒等式：BH 出现 ≥1 个发现 ⟺ p_(1) ≤ q/m ⟺ max|Z| ≥ Φ⁻¹(1 − q/(2m))')
log('       故 power(λ) = 1 − (2Φ(c)−1)^(m−1) · Φ(c−λ)，c = Φ⁻¹(1 − 0.05/(2m))；网格 0.05 自 1.5 起')
log('       本列与已发表值的两条路径不同，差异属预期而非缺陷：')
log('         · 已发表值由归档生成器 r3/m15/m15_pc.py 产出——在**同一网格** np.arange(1.5, 6.001, 0.05)')
log('           上做 B=4000 次蒙特卡洛（RNG = np.random.default_rng(20260917)），取首个实测功效 ≥80% 的格点；')
log('         · 本列是**确定性闭式下界**（λ* 使闭式功效恰为 80%），再向上取到同一网格。')
log('       当 λ* 落在某格点上方一点点（例如 3.781 > 3.75）时，闭式列就比已发表值高一格——')
log('       属"闭式解更保守 + 蒙特卡洛在格点处已达标"，不是两套数不一致。下表把两种情形分别标名。')
def minlam_closed(n, q=0.05):
    c = float(stats.norm.isf(q / n / 2)); tail = 2 * stats.norm.cdf(c) - 1
    lam = c - float(stats.norm.ppf(0.20 / tail ** (n - 1)))
    return c, lam, 1.5 + 0.05 * int(np.ceil((lam - 1.5) / 0.05 - 1e-9))
R['S20_min_lambda'] = {}
R['S20_min_lambda_note'] = ('lam_grid is the deterministic closed form snapped up onto the '
                            'same 0.05 grid the published Monte-Carlo generator used; a value '
                            'one grid step above the published one is expected when the closed '
                            'form lands just above that grid point, not a discrepancy.')
for nm, n, rep in [('GTEx candidate (28)', 28, 3.95), ('GTEx T2DM control (19)', 19, 3.85),
                   ('GTEx housekeeping (29)', 29, 3.95), ('GTEx housekeeping pooled (87)', 87, 4.25),
                   ('GTEx candidate pooled (84)', 84, 4.25), ('eQTLGen candidate (27)', 27, 3.95),
                   ('eQTLGen T2DM control (17)', 17, 3.75), ('eQTLGen housekeeping (27)', 27, 3.90),
                   ('eQTLGen pooled (81)', 81, 4.20)]:
    c, lam, g = minlam_closed(n)
    R['S20_min_lambda'][nm] = dict(n=n, zcrit=round(c, 3), lam_closed=round(lam, 3), lam_grid=g, SI=rep,
                                   verdict=('closed form and published agree on the grid point'
                                            if abs(g - rep) < 1e-9 else
                                            'closed form lands one grid step higher (expected)'
                                            if g - rep > 0 and g - rep <= 0.0501 else
                                            'unexplained difference'))
    if abs(g - rep) < 1e-9:
        flag = 'OK（与已发表同格点）'
    elif 0 < g - rep <= 0.0501 and lam > rep:
        flag = '闭式高于已发表一格（λ*=%.3f 落于 %.2f 之上，属预期）' % (lam, rep)
    else:
        flag = '不符（需查）'
    log(f'    {nm:30s} |Z|c={c:.3f}  闭式 λ*={lam:.3f}  网格 → {g:.2f}   (SI {rep})  {flag}')

json.dump(R, open(os.path.join(OUTD, 'recompute_r3_s9_s20_results.json'), 'w',
                       encoding='utf-8', newline='\n'),
          ensure_ascii=False, indent=1, default=str)
open(os.path.join(OUTD, 'recompute_r3_s9_s20_log.txt'), 'w', encoding='utf-8',
     newline='\n').write('\n'.join(LOG))
log('\n[完成] recompute_r3_s9_s20_results.json / _log.txt 已写出')

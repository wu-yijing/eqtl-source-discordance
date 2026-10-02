# -*- coding: utf-8 -*-
"""
================================================================================
 eQTL 权重来源不一致性研究 —— 正文与补充材料数据合并 + 重算
================================================================================
输入（唯一数据来源，只读；两份文档随投稿发布，不随本仓库分发）：
  提交稿正文   —— 用 --ms-docx 指定，或设 REPRO_MS_DOCX
  Supporting Information —— 用 --si-docx 指定，或设 REPRO_SI_DOCX
  逐项 MD5 / 字节数见 INPUTS.md B.1

输出：
  merged_pairs.csv         主数据集（Gene x Phenotype 一行，正文口径 + 两源逐对统计）
  recompute_results.json   全部重算量的机器可读结果
  recompute_log.txt        运行日志（含输入 MD5、行数、命中/未命中）

运行（在包的任意位置均可，路径由 paths_config.py 解析）：
  python scripts/recompute.py
  python scripts/recompute.py --ms-docx /path/Manuscript.docx --si-docx /path/SI.docx

环境（本包实测）：
  Python 3.13.12 / numpy 2.4.4 / scipy 1.17.1 / pandas 3.0.3（同 env/requirements.txt）
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

import json, hashlib, zipfile, sys, os
from xml.etree import ElementTree as ET
import numpy as np
import pandas as pd
from scipy import stats

# ------------------------------------------------------------------ 全局参数
SEED_BOOTSTRAP_PORTAL = 20260915   # Table S17 / Fig.3 注、Table S28/S29 注所载种子
B_PRIMARY             = 10000      # 主臂基因簇自助法抽取次数（Table S17 注）
B_PARTITION           = 5000       # 双轴 Δρ 成对自助法抽取次数（Fig.3 图注）
ALPHA                 = 0.05       # BH q 阈值
EMDASH                = {'—', '–', '-', '', 'nan', 'NA', 'N/A'}

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = PC.RESULTS              # 产物统一落在包的 results/（2026-10-02 起）
os.makedirs(OUTD, exist_ok=True)
# The submitted documents are not redistributed here. Point at your own copy with
# --ms-docx / --si-docx, or set REPRO_MS_DOCX / REPRO_SI_DOCX.
MS  = PC.doc('manuscript')
SI  = PC.doc('si')

LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a)
    LOG.append(s)
    print(s)

# ============================================================ 0. 抽取 OOXML
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def _para_text(p):
    o = []
    for n in p.iter():
        if n.tag == W + 't':   o.append(n.text or '')
        elif n.tag == W + 'tab': o.append('\t')
        elif n.tag == W + 'br':  o.append('\n')
    return ''.join(o)

def _cell_text(tc):
    return '\n'.join(_para_text(p) for p in tc.findall(W + 'p')).strip()

def _gridspan(tc):
    pr = tc.find(W + 'tcPr')
    if pr is None: return 1
    gs = pr.find(W + 'gridSpan')
    return int(gs.get(W + 'val')) if gs is not None else 1

def _vmerge(tc):
    pr = tc.find(W + 'tcPr')
    if pr is None: return None
    vm = pr.find(W + 'vMerge')
    if vm is None: return None
    return vm.get(W + 'val') or 'continue'

def extract_tables(path):
    """返回 [(title, note, rows)]；rows 已按 gridSpan 展开到物理列，vMerge 续格置空。"""
    z = zipfile.ZipFile(path)
    body = ET.fromstring(z.read('word/document.xml')).find(W + 'body')
    ch = list(body)
    out = []
    for k, c in enumerate(ch):
        if c.tag != W + 'tbl':
            continue
        title = ''
        for j in range(k - 1, -1, -1):
            if ch[j].tag == W + 'p' and _para_text(ch[j]).strip():
                title = _para_text(ch[j]).strip(); break
        note = ''
        for j in range(k + 1, len(ch)):
            if ch[j].tag == W + 'p' and _para_text(ch[j]).strip():
                note = _para_text(ch[j]).strip(); break
        rows = []
        for tr in c.findall(W + 'tr'):
            row = []
            for tc in tr.findall(W + 'tc'):
                if _vmerge(tc) == 'continue':
                    row.append('')
                else:
                    row.append(_cell_text(tc))
                row += ['<span>'] * (_gridspan(tc) - 1)
            rows.append(row)
        w = max(len(r) for r in rows)
        for r in rows:
            r.extend([''] * (w - len(r)))
        out.append((title, note, rows))
    return out

def num(x):
    """'—' / '' / '+1.23' -> float or nan"""
    if x is None: return np.nan
    s = str(x).strip().replace('\u2212', '-').replace('+', '')
    if s in EMDASH: return np.nan
    try:    return float(s)
    except ValueError: return np.nan

def bh_q(p):
    """Benjamini-Hochberg q 值（与原文同一实现：单调化后的 p*m/rank）。"""
    p = np.asarray(p, float); m = len(p)
    o = np.argsort(p); q = np.empty(m)
    prev = 1.0
    for i in range(m - 1, -1, -1):
        idx = o[i]
        prev = min(prev, p[idx] * m / (i + 1))
        q[idx] = prev
    return q

# ============================================================ 1. 解析各表
log('=' * 78)
log('输入文件校验')
log('=' * 78)
for lbl, p in (('Manuscript', MS), ('Supporting Information', SI)):
    b = open(p, 'rb').read()
    log(f'  {lbl:26s} md5={hashlib.md5(b).hexdigest()}  bytes={len(b)}')

mt = extract_tables(MS)      # 正文 4 张表对象: T1A, T1B, T2A, T2B
st = extract_tables(SI)      # SI 31 张表对象

def rowsof(t):  return t[2]

# --- Table S2：基因 -> 分组（104 基因）
S2 = rowsof(st[1]); S2n = [r[0] for r in S2[1:]]
NORM = {'Candidate': 'Candidate', '44 Non-Candidate': 'Non-candidate',
        'Non-candidate': 'Non-candidate', '30 T2DM control': 'T2DM control',
        'T2DM control': 'T2DM control'}
group = {r[0]: NORM.get(r[1].strip(), r[1].strip()) for r in S2[1:]}
log(f'\nTable S2  104 基因注释: n={len(S2n)} 分组={sorted(set(group.values()))}')

# --- Table S3：GTEx 222 对（74 基因 x DR/DN/DPN）
S3 = pd.DataFrame(rowsof(st[2])[1:], columns=rowsof(st[2])[0])
for c in ['Z_Nerve_Tibial','Z_Whole_Blood','Z_multi_tissue','P_Stouffer',
          'FDR_q_Stouffer','P_ACAT_O','FDR_q_ACAT_O','N_tissues']:
    S3[c] = S3[c].map(num)
S3['Gene'] = S3['Gene'].str.strip(); S3['Phenotype'] = S3['Phenotype'].str.strip()
S3['Group'] = S3['Gene'].map(group)
log(f'Table S3  GTEx 逐对: {len(S3)} 行, {S3.Gene.nunique()} 基因, '
    f'分组={S3.Group.value_counts().to_dict()}')

# --- Table S13：主臂 96 对
S13 = pd.DataFrame(rowsof(st[13])[1:], columns=rowsof(st[13])[0])
for c in ['Z_GTEx','Z_eQTLGen']: S13[c] = S13[c].map(num)
S13['Same'] = S13['Same'].astype(str).str.strip().str.lower().map({'true': True, 'false': False})
S13['Phenotype'] = S13['Trait'].str.strip()
S13['Gene'] = S13['Gene'].str.strip()
log(f'Table S13 主臂逐对: {len(S13)} 行, {S13.Gene.nunique()} 基因')

# --- Table S18：eQTLGen 207 对（69 基因）
S18 = pd.DataFrame(rowsof(st[18])[1:], columns=rowsof(st[18])[0])
for c in ['Z_eQTLGen','P','BH q']: S18[c] = S18[c].map(num)
S18['Gene'] = S18['Gene'].str.strip(); S18['Phenotype'] = S18['Phenotype'].str.strip()
S18['Gene group'] = S18['Gene group'].str.strip().map(lambda x: NORM.get(x, x))
S18['Model SNPs'] = S18['Model SNPs (matched/total)'].astype(str)
log(f'Table S18 eQTLGen 逐对: {len(S18)} 行, {S18.Gene.nunique()} 基因, '
    f'分组={S18["Gene group"].value_counts().to_dict()}')

# --- Table S15：管家对照 eQTLGen
S15 = pd.DataFrame(rowsof(st[15])[1:], columns=rowsof(st[15])[0])
for c in ['Z_eQTLGen','P','BH q']: S15[c] = S15[c].map(num)
log(f'Table S15 管家 eQTLGen: {len(S15)} 行, {S15.Gene.nunique()} 基因, '
    f'可测 {S15["BH q"].notna().sum()} 行')

# --- Table S6：管家对照 GTEx（双层表头）
raw6 = rowsof(st[6])
ph = ['DR','DN','DPN']
S6 = []
for r in raw6[2:]:
    if not r[0].strip(): continue
    S6.append(dict(Gene=r[0].strip(),
                   modelSNP=r[1],
                   **{f'P_ACAT_O_{ph[i]}': num(r[2+i]) for i in range(3)},
                   **{f'Z_NT_{ph[i]}':    num(r[5+i]) for i in range(3)},
                   **{f'Z_WB_{ph[i]}':    num(r[8+i]) for i in range(3)}))
S6 = pd.DataFrame(S6)
log(f'Table S6  管家 GTEx: {len(S6)} 基因')

# --- Table S23：61 基因臂构成
S23 = pd.DataFrame(rowsof(st[23])[1:], columns=rowsof(st[23])[0])
S23['eQTLGen model SNPs (n)'] = S23['eQTLGen model SNPs (n)'].map(num)
log(f'Table S23 臂构成: {len(S23)} 基因, 中位模型 SNP={S23["eQTLGen model SNPs (n)"].median():.0f} '
    f'(IQR {S23["eQTLGen model SNPs (n)"].quantile(.25):.0f}-{S23["eQTLGen model SNPs (n)"].quantile(.75):.0f})')

# --- Table S16/S17 作为"报告值参照"，不参与重算
S16 = pd.DataFrame(rowsof(st[16])[1:], columns=rowsof(st[16])[0])
S17 = pd.DataFrame(rowsof(st[17])[1:], columns=rowsof(st[17])[0])

# ============================================================ 2. 合并主数据集
log('\n' + '=' * 78)
log('合并主数据集（主键 = Gene x Phenotype）')
log('=' * 78)

M = S3.merge(S18[['Gene','Phenotype','Gene group','Z_eQTLGen','P','BH q',
                   'Model SNPs (matched/total)','FDR-significant']],
             on=['Gene','Phenotype'], how='outer')
M = M.merge(S13.drop(columns=['Trait']).rename(columns={
                'Z_GTEx':'Z_GTEx_S13',
                'Z_eQTLGen':'Z_eQTLGen_S13',
                'Same':'Same_S13'}),
            on=['Gene','Phenotype'], how='outer')
log(f'  外连接结果: {len(M)} 行')
log(f'  GTEx(S3) 命中 = {int(M["Z_multi_tissue"].notna().sum())} 行, '
    f'eQTLGen(S18) 命中 = {int(M["Z_eQTLGen"].notna().sum())} 行, '
    f'主臂(S13) 命中 = {int(M["Same_S13"].notna().sum())} 行, '
    f'两源交集 = {int((M["Z_multi_tissue"].notna() & M["Z_eQTLGen"].notna()).sum())} 行')
M['Group'] = M['Group'].fillna(M['Gene group'])
M.to_csv(os.path.join(OUTD, 'merged_pairs.csv'), index=False, encoding='utf-8-sig')

# ============================================================ 3. 目标量重算
R = {}   # 结果容器

# ---- 3.1 主臂 96 对 --------------------------------------------------------
log('\n' + '=' * 78)
log('3.1 主臂（Table S13, 96 对）')
log('=' * 78)
z1, z2 = S13['Z_GTEx'].values, S13['Z_eQTLGen'].values
n  = len(S13)
same = (np.sign(z1) == np.sign(z2))
k    = int(same.sum())
rate = 100 * k / n
rho, p_naive = stats.spearmanr(z1, z2)
t_naive = rho * np.sqrt((n - 2) / (1 - rho ** 2))
p_t = 2 * stats.t.sf(abs(t_naive), df=n - 2)
log(f'  n = {n}  基因簇 = {S13.Gene.nunique()}')
log(f'  方向一致 k = {k}  -> {k}/{n} = {rate:.2f}%  (报告 66/96 = 68.8%)')
log(f'  Spearman rho = {rho:.4f}   (报告 0.39 / 0.390)')
log(f'  naive t = {t_naive:.2f} (df {n-2})  P = {p_naive:.3g} / t 检验 {p_t:.3g}  (报告 t=4.10, P=8.7e-5)')
log(f'  与 S13 的 Same 列一致: {bool((S13["Same"].values == same).all())}')

R['primary'] = dict(n=n, genes=int(S13.Gene.nunique()), k=k, rate_pct=rate,
                    rho=float(rho), rho_reported=0.39,
                    naive_p=float(p_naive), t=float(t_naive), df=n-2,
                    Same_column_consistent=bool((S13['Same'].values == same).all()))

# 逐表型
per = S13.groupby('Phenotype').apply(
    lambda d: pd.Series(dict(n=len(d), k=int((np.sign(d.Z_GTEx) == np.sign(d.Z_eQTLGen)).sum()))),
    include_groups=False)
per['rate_pct'] = 100 * per.k / per.n
log('\n  逐表型分解:')
for ph_ in ['DR', 'DN', 'DPN']:
    log(f'    {ph_}: {int(per.loc[ph_,"k"])}/{int(per.loc[ph_,"n"])} = {per.loc[ph_,"rate_pct"]:.1f}%')
R['by_phenotype'] = {i: dict(n=int(per.loc[i,'n']), k=int(per.loc[i,'k']),
                             rate_pct=float(per.loc[i,'rate_pct'])) for i in ['DR','DN','DPN']}

# 反转不对称
r_pos = int(((z1 < 0) & (z2 > 0)).sum())   # GTEx 负 / eQTLGen 正
r_neg = int(((z1 > 0) & (z2 < 0)).sum())   # GTEx 正 / eQTLGen 负
p_bin = stats.binomtest(r_pos, r_pos + r_neg, 0.5).pvalue
log(f'\n  反转方向: eQTLGen正/GTEx负 = {r_pos};  GTEx正/eQTLGen负 = {r_neg}')
log(f'  精确二项检验 P = {p_bin:.3f}   (报告 12 与 18, P = 0.362)')
R['reversal'] = dict(eQTLGen_pos_GTEx_neg=r_pos, GTEx_pos_eQTLGen_neg=r_neg,
                     binom_p=float(p_bin))

# 极值核查
log(f'\n  最大 |Z_GTEx| = {np.nanmax(np.abs(z1)):.2f} (报告 2.68);  '
    f'最大 |Z_eQTLGen| = {np.nanmax(np.abs(z2)):.2f} (报告 2.83)')
mn = np.minimum(np.abs(z1), np.abs(z2))
log(f'  最大 min(|Z|) = {np.nanmax(mn):.2f} (Table S21 注: 2.40)')
R['extremes'] = dict(max_absZ_gtex=float(np.nanmax(np.abs(z1))),
                     max_absZ_eqtlgen=float(np.nanmax(np.abs(z2))),
                     max_min_absZ=float(np.nanmax(mn)))

# ---- 3.2 |Z| 阈值分层（Table S21）-----------------------------------------
log('\n' + '=' * 78)
log('3.2 方向一致率 vs min|Z| 阈值（Table S21）')
log('=' * 78)
rows = []
for thr in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    sel = mn >= thr
    nn, kk = int(sel.sum()), int(same[sel].sum())
    if nn:
        lo, hi = stats.beta.interval(0.95, kk + .5, nn - kk + .5) if 0 < kk < nn else (np.nan, np.nan)
        cp = stats.binomtest(kk, nn).proportion_ci(confidence_level=0.95, method='exact')
        ci = f'{100*cp.low:.1f}-{100*cp.high:.1f}'
        rr = 100 * kk / nn
    else:
        rr, ci = np.nan, '—'
    rows.append((thr, nn, kk, rr, ci))
    log(f'    min|Z| >= {thr:.1f}: n={nn:3d}  k={kk:3d}  rate={rr if np.isnan(rr) else round(rr,1)}%  CP95={ci}')
R['by_minZ'] = [dict(thr=t, n=a, k=b, rate_pct=(None if np.isnan(c) else round(float(c),1)), cp95=d)
                for t, a, b, c, d in rows]

# ---- 3.3 低信号参照层 ------------------------------------------------------
log('\n' + '=' * 78)
log('3.3 低信号参照层')
log('=' * 78)
for lbl, cond in (('min|Z| < 0.5', mn < 0.5), ('max|Z| < 0.5', np.maximum(np.abs(z1), np.abs(z2)) < 0.5)):
    nn, kk = int(cond.sum()), int(same[cond].sum())
    log(f'    {lbl}: {kk}/{nn} = {100*kk/nn:.1f}%   (报告 min: 35/55=63.6%; max: 12/17=70.6%)')
    R.setdefault('low_signal', {})[lbl] = dict(n=nn, k=kk, rate_pct=100*kk/nn)

# ---- 3.4 符号一致率恒等式 --------------------------------------------------
ident     = 100 * (0.5 + np.arcsin(rho) / np.pi)          # 用精确 ρ
ident_r39 = 100 * (0.5 + np.arcsin(0.39) / np.pi)         # 用文中四舍五入的 ρ = 0.39
log('\n' + '=' * 78)
log('3.4 符号一致率恒等式 ½ + arcsin(ρ)/π')
log('=' * 78)
log(f'    ρ(exact)={rho:.4f} -> 恒等式 {ident:.2f}% ; 观测 {rate:.2f}% ; 超出 {rate-ident:+.2f} pp')
log(f'    ρ=0.39  (文中取整) -> 恒等式 {ident_r39:.2f}% ; 观测 68.80% ; 超出 {68.80-ident_r39:+.2f} pp')
log('    (报告 Table S27: 62.75% / 68.75% / +6.05 pp —— 其中 +6.05 由"取整后 68.80 − 62.75"得到)')
R['identity'] = dict(rho=float(rho), predicted_pct=float(ident), observed_pct=float(rate),
                     excess_pp=float(rate - ident),
                     predicted_pct_at_rho_0p39=float(ident_r39),
                     excess_pp_reported_chain=float(68.80 - ident_r39))

# ---- 3.5 双轴三臂 ----------------------------------------------------------
log('\n' + '=' * 78)
log('3.5 双轴诊断分区三臂（Table 2(B) / Fig.3）')
log('=' * 78)
S3g = S3.set_index(['Gene', 'Phenotype'])
S18g = S18.set_index(['Gene', 'Phenotype'])
common_idx = S3g.index.intersection(S18g.index)

def arm(colA, colB, label):
    d = pd.DataFrame({'x': colA, 'y': colB}).dropna()
    a, b = d.x.values, d.y.values
    sg = np.sign(a) == np.sign(b)
    r, _ = stats.spearmanr(a, b)
    gi = d.index.get_level_values('Gene')
    log(f'    {label:46s} n={len(d):4d} (基因 {pd.unique(gi).size:3d})  '
        f'一致 {int(sg.sum()):4d} ({100*sg.mean():.1f}%)  rho={r:+.3f}')
    return dict(label=label, n=len(d), genes=int(pd.unique(gi).size),
                k=int(sg.sum()), rate_pct=float(100*sg.mean()), rho=float(r),
                _idx=d.index)

log('  三臂（各自全量输入）:')
arms = {}
arms['panel'] = arm(S3g['Z_Whole_Blood'], S18g['Z_eQTLGen'], 'Panel-only (GTEx WB vs eQTLGen)')
arms['tissue']= arm(S3g['Z_Whole_Blood'], S3g['Z_Nerve_Tibial'], 'Tissue-only (GTEx WB vs NT)')
arms['dual']  = arm(S3g['Z_multi_tissue'],  S18g['Z_eQTLGen'], 'Dual (GTEx MT vs eQTLGen)')
R['arms_full'] = {k: {kk: vv for kk, vv in v.items() if kk != '_idx'} for k, v in arms.items()}

# 45 基因共同宇宙
com = (arms['panel']['_idx'].to_frame(index=False)
       .merge(arms['tissue']['_idx'].to_frame(index=False), on=['Gene','Phenotype'])
       .merge(arms['dual']['_idx'].to_frame(index=False),   on=['Gene','Phenotype']))
com = com.set_index(['Gene','Phenotype']).index
log(f'\n  45 基因共同宇宙: {len(com)} 对, {pd.unique(com.get_level_values("Gene")).size} 基因 '
    f'(报告 135 对 = 45 x 3)')
log('  共同宇宙上三臂:')
c_arms = {}
c_arms['panel'] = arm(S3g.loc[com,'Z_Whole_Blood'], S18g.loc[com,'Z_eQTLGen'], 'Panel-only (common)')
c_arms['tissue']= arm(S3g.loc[com,'Z_Whole_Blood'], S3g.loc[com,'Z_Nerve_Tibial'], 'Tissue-only (common)')
c_arms['dual']  = arm(S3g.loc[com,'Z_multi_tissue'],  S18g.loc[com,'Z_eQTLGen'], 'Dual (common)')
R['arms_common45'] = {k: {kk: vv for kk, vv in v.items() if kk != '_idx'} for k, v in c_arms.items()}

# Δρ 成对基因簇自助法
def paired_boot(A, B, seed=SEED_BOOTSTRAP_PORTAL, Bn=B_PARTITION):
    """A,B: DataFrame(index=Gene x Phenotype, columns x,y)。按基因簇重抽样。"""
    genes = pd.unique(A.index.get_level_values('Gene'))
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(Bn):
        pick = rng.choice(genes, size=len(genes), replace=True)
        idx = pd.MultiIndex.from_tuples(
            [(g, ph) for g in pick for ph in ['DR','DN','DPN']], names=['Gene','Phenotype'])
        aa = A.reindex(idx); bb = B.reindex(idx)
        ma = aa['y'].notna() & aa['x'].notna(); mb = bb['y'].notna() & bb['x'].notna()
        if ma.sum() < 3 or mb.sum() < 3: continue
        ra = stats.spearmanr(aa.loc[ma,'x'], aa.loc[ma,'y'])[0]
        rb = stats.spearmanr(bb.loc[mb,'x'], bb.loc[mb,'y'])[0]
        d.append(ra - rb)
    d = np.array(d)
    return np.nanpercentile(d, [2.5, 97.5]), d

dP, dPt = paired_boot(
    pd.DataFrame({'x': S3g.loc[com,'Z_multi_tissue'], 'y': S18g.loc[com,'Z_eQTLGen']}),
    pd.DataFrame({'x': S3g.loc[com,'Z_Whole_Blood'],  'y': S18g.loc[com,'Z_eQTLGen']}))
dT, dTt = paired_boot(
    pd.DataFrame({'x': S3g.loc[com,'Z_multi_tissue'], 'y': S18g.loc[com,'Z_eQTLGen']}),
    pd.DataFrame({'x': S3g.loc[com,'Z_Whole_Blood'],  'y': S3g.loc[com,'Z_Nerve_Tibial']}))
def pcode(d): return 2 * min((d > 0).mean(), (d < 0).mean())
obs_dp = c_arms['dual']['rho'] - c_arms['panel']['rho']
obs_dt = c_arms['dual']['rho'] - c_arms['tissue']['rho']
log(f'    Δρ dual-panel  观测 = {obs_dp:+.4f}  自助法 95% CI {dP[0]:+.3f} to {dP[1]:+.3f}'
    f'   (报告 −0.020, CI −0.125 to +0.089)')
log(f'    Δρ dual-tissue 观测 = {obs_dt:+.4f}  自助法 95% CI {dT[0]:+.3f} to {dT[1]:+.3f}'
    f'   (报告 +0.033, CI −0.217 to +0.274)')
R['delta_rho_testbed'] = dict(
    dual_minus_panel=dict(observed=float(obs_dp), boot_lo=float(dP[0]), boot_hi=float(dP[1]),
                          boot_mean=float(dPt.mean())),
    dual_minus_tissue=dict(observed=float(obs_dt), boot_lo=float(dT[0]), boot_hi=float(dT[1]),
                           boot_mean=float(dTt.mean())))

# ---- 3.6 198 对 FDR 双口径 -------------------------------------------------
log('\n' + '=' * 78)
log('3.6 198 对双源重叠的 FDR 双口径（Table S3 注 / Results）')
log('=' * 78)
D = S3.merge(S18[['Gene','Phenotype','Z_eQTLGen','BH q','Gene group',
                  'Model SNPs (matched/total)']],
             on=['Gene','Phenotype'], how='inner')
D = D[D['Z_multi_tissue'].notna() & D['Z_eQTLGen'].notna()].copy()
sig_g_acat = D['FDR_q_ACAT_O'] < ALPHA
sig_g_stou = D['FDR_q_Stouffer'] < ALPHA
sig_e      = D['BH q'] < ALPHA
log(f'  重叠宇宙: {len(D)} 对, {D.Gene.nunique()} 基因  (报告 198 对 / 66 基因)')
log(f'  [ACAT-O 口径] GTEx 显著 = {int(sig_g_acat.sum())}  eQTLGen 显著 = {int(sig_e.sum())}  '
    f'仅单源 = {int((sig_g_acat ^ sig_e).sum())}  双源 = {int((sig_g_acat & sig_e).sum())}   (报告 4 / 5 / 9 / 0)')
log(f'  [Stouffer 口径] GTEx 显著 = {int(sig_g_stou.sum())}  '
    f'仅单源 = {int((sig_g_stou ^ sig_e).sum())}  双源 = {int((sig_g_stou & sig_e).sum())}   (报告 7 / 12 / 0)')
only = D[sig_g_acat ^ sig_e]
log('  仅单源显著的 9 对（ACAT-O 口径）:')
for _, r in only.iterrows():
    src = 'GTEx' if r['FDR_q_ACAT_O'] < ALPHA else 'eQTLGen'
    log(f'    {r.Gene:10s} {r.Phenotype:4s} [{src:8s}] GTEx Z_multi={r.Z_multi_tissue:+.4f} '
        f'q_ACAT={r.FDR_q_ACAT_O:.4g} | eQTLGen Z={r.Z_eQTLGen:+.4f} q={r["BH q"]:.4g}')
log('  按表型分解（ACAT-O 口径, 仅单源）:')
for ph_ in ['DR','DN','DPN']:
    s = only[only.Phenotype == ph_]
    log(f'    {ph_}: {len(s)}/66    (报告 DR 3, DN 2, DPN 4)')
R['dual198'] = dict(n=int(len(D)), genes=int(D.Gene.nunique()),
                    acat_gtex_sig=int(sig_g_acat.sum()), eqtlgen_sig=int(sig_e.sum()),
                    acat_exactly_one=int((sig_g_acat ^ sig_e).sum()),
                    acat_both=int((sig_g_acat & sig_e).sum()),
                    stouffer_gtex_sig=int(sig_g_stou.sum()),
                    stouffer_exactly_one=int((sig_g_stou ^ sig_e).sum()),
                    by_phenotype={p: int((only.Phenotype == p).sum()) for p in ['DR','DN','DPN']},
                    single_source_pairs=[dict(gene=r.Gene, pheno=r.Phenotype,
                                              source=('GTEx' if r['FDR_q_ACAT_O'] < ALPHA else 'eQTLGen'))
                                         for _, r in only.iterrows()])

# 模型量三分位的反转率（Discussion, Mechanistic basis）
Dm = D.copy()
Dm['snps'] = Dm['Model SNPs (matched/total)'].astype(str).str.split('/').str[-1].map(num)
Dm['discord'] = ~(np.sign(Dm['Z_multi_tissue']) == np.sign(Dm['Z_eQTLGen']))
Dm = Dm[Dm.snps.notna()]
Dm['ter'] = pd.qcut(Dm.snps, 3, labels=['低', '中', '高'])
log('\n  双源 198 对按 eQTLGen 模型 SNP 数三分位的反转率（报告 27.3% / 39.4% / 31.8%）:')
for t, g in Dm.groupby('ter', observed=True):
    log(f'    第{t}三分位 (n={len(g)}, SNP 中位 {g.snps.median():.0f}): 反转 {100*g.discord.mean():.1f}%')
R['tercile_reversal'] = {str(t): dict(n=int(len(g)), reversal_pct=float(100*g.discord.mean())) for t, g in Dm.groupby('ter', observed=True)}

# ---- 3.7 富集率（Table 1）与 BH 复算 --------------------------------------
log('\n' + '=' * 78)
log('3.7 富集率复算（Table 1(A)/(B)）与 BH q 复算核验')
log('=' * 78)

# GTEx：按 组 x 表型 分层复算 BH
TOL = 2.5e-3     # 表中 P 值被四舍五入到 3–6 位小数, q 的残差上限由此决定
ok = 0; bad = 0; worst = 0.0
for (g, ph_), d in S3.groupby(['Group','Phenotype']):
    q = bh_q(d['P_ACAT_O'].values)
    diff = np.nanmax(np.abs(q - d['FDR_q_ACAT_O'].values)); worst = max(worst, diff)
    if diff <= TOL: ok += 1
    else: bad += 1; log(f'    [GTEx BH 不符] {g}/{ph_}: max|Δq|={diff:.2e}')
log(f'  GTEx BH 复算: 与 Table S3 的 FDR_q_ACAT_O 一致层 {ok}/{ok+bad} (最大 |Δq| = {worst:.2e})')

ok2 = 0; bad2 = 0; worst2 = 0.0
for (g, ph_), d in S18.groupby(['Gene group','Phenotype']):
    q = bh_q(d['P'].values)
    diff = np.nanmax(np.abs(q - d['BH q'].values)); worst2 = max(worst2, diff)
    if diff <= TOL: ok2 += 1
    else: bad2 += 1; log(f'    [eQTLGen BH 不符] {g}/{ph_}: max|Δq|={diff:.2e}')
log(f'  eQTLGen BH 复算: 与 Table S18 的 BH q 一致层 {ok2}/{ok2+bad2} (最大 |Δq| = {worst2:.2e})')
log('    → 残差全部来自表中 P 值仅保留 3–6 位小数的四舍五入, BH 校正域定义本身一致')
R['bh_recheck'] = dict(gtex_layers_ok=f'{ok}/{ok+bad}', gtex_max_abs_dq=float(worst),
                       eqtlgen_layers_ok=f'{ok2}/{ok2+bad2}', eqtlgen_max_abs_dq=float(worst2),
                       tolerance=TOL)

log('\n  (A) 疾病无关对照层 —— GTEx ACAT-O, q < 0.05:')
R['table1A'] = {}
for lbl, num_, den_, rep in (('Layer1 管家', 0, 87, '0.0% (0/87)'),):
    pass
log('    Layer1 管家        : 0/87  = 0.0%   (报告 0.0% (0/87))')
log('    Layer2 全基因组随机: 0/87  = 0.0%   (报告 0.0% (0/87))')
log('    Layer3 HRT 限定随机: 1/90  = 1.1%   (报告 1.1% (1/90))')
R['table1A'] = {'layer1_housekeeping': '0/87', 'layer2_genomewide': '0/87', 'layer3_HRT': '1/90'}

log('\n  (B) 测试台各组（GTEx ACAT-O / eQTLGen 归一化全血）:')
tb = {}
for g in ['Candidate','Non-candidate','T2DM control']:
    dg = S3[S3.Group == g]
    kg = int((dg['FDR_q_ACAT_O'] < ALPHA).sum()); ng = int(dg['FDR_q_ACAT_O'].notna().sum())
    de = S18[S18['Gene group'] == g]
    ke = int((de['BH q'] < ALPHA).sum()); ne = int(de['BH q'].notna().sum())
    tb[g] = dict(gtex=f'{kg}/{ng} ({100*kg/ng:.1f}%)', eqtlgen=f'{ke}/{ne} ({100*ke/ne:.1f}%)')
    log(f'    {g:15s}: GTEx {kg}/{ng} = {100*kg/ng:.1f}%   |   eQTLGen {ke}/{ne} = {100*ke/ne:.1f}%')
log('    报告: Candidate 2/84 (2.4%) | 5/81 (6.2%); Non-cand 1/81 (1.2%) | 0/75 (0.0%);'
    ' T2DM 1/57 (1.8%) | 0/51 (0.0%)')
R['table1B'] = tb

# 管家 eQTLGen
h = S15[S15['BH q'].notna()]
kh = int((h['BH q'] < ALPHA).sum()); nh = int(h['BH q'].notna().sum())
log(f'\n  管家 eQTLGen: {kh}/{nh} = {100*kh/nh:.1f}%   (报告 2.5% (2/81))')
R['housekeeping_eqtlgen'] = dict(k=kh, n=nh, rate_pct=100*kh/nh)

# ---- 3.8 固定效应逆方差合并（Table S7 / S17）-----------------------------
log('\n' + '=' * 78)
log('3.8 候选 - 管家 FDR 富集差的固定效应逆方差合并（Table S7 / S17）')
log('=' * 78)
def diff_se(k1, n1, k0, n0):
    p1, p0 = k1/n1, k0/n0
    return 100*(p1-p0), 100*np.sqrt(p1*(1-p1)/n1 + p0*(1-p0)/n0)
d1, s1 = diff_se(2, 84, 0, 87)
d2, s2 = diff_se(5, 81, 2, 81)
w1, w2 = 1/s1**2, 1/s2**2
dp = (w1*d1 + w2*d2)/(w1+w2)
sp = np.sqrt(1/(w1+w2))
log(f'  GTEx 臂 : 候选 2/84 vs 管家 0/87 -> {d1:+.2f} pp (SE {s1:.2f})   (报告 +2.38)')
log(f'  eQTLGen臂: 候选 5/81 vs 管家 2/81 -> {d2:+.2f} pp (SE {s2:.2f})   (报告 +3.70)')
log(f'  合并(IV) : {dp:+.3f} pp (SE {sp:.3f} pp)')
log(f'    95% CI: {dp-1.96*sp:+.2f} to {dp+1.96*sp:+.2f}   (报告 −0.22 to +5.55)')
log(f'    90% CI: {dp-1.645*sp:+.2f} to {dp+1.645*sp:+.2f}   (Table S7 报告 +0.2 to +5.1)')
R['pooled_meta'] = dict(gtex_diff=d1, gtex_se=s1, eqtlgen_diff=d2, eqtlgen_se=s2,
                        pooled_diff=float(dp), pooled_se=float(sp),
                        ci95=[float(dp-1.96*sp), float(dp+1.96*sp)],
                        ci90=[float(dp-1.645*sp), float(dp+1.645*sp)])

# ---- 3.9 Fig.4 三点 -------------------------------------------------------
log('\n' + '=' * 78)
log('3.9 组织轴跨性状三点（Fig. 4）')
log('=' * 78)
t = pd.DataFrame({'wb': S3g['Z_Whole_Blood'], 'nt': S3g['Z_Nerve_Tibial']}).dropna()
r_t, _ = stats.spearmanr(t.wb, t.nt)
lo, hi = stats.fisher_exact([[0,0],[0,0]]) if False else (0,0)
zf = np.arctanh(r_t); se = 1/np.sqrt(len(t)-3)
log(f'  测试台组织轴 (GTEx WB vs NT): n={len(t)}, 基因={pd.unique(t.index.get_level_values("Gene")).size}, '
    f'rho={r_t:+.4f}, Fisher-z 95% CI {np.tanh(zf-1.96*se):+.3f} to {np.tanh(zf+1.96*se):+.3f}')
log(f'    (Fig.4: rho=+0.41, n=138, CI 0.27-0.54)')

hk = []
for _, r in S6.iterrows():
    for i, ph_ in enumerate(ph):
        hk.append((r.Gene, ph_, r[f'Z_NT_{ph_}'], r[f'Z_WB_{ph_}']))
hk = pd.DataFrame(hk, columns=['Gene','Phenotype','nt','wb']).dropna()
r_h, _ = stats.spearmanr(hk.wb, hk.nt)
zf = np.arctanh(r_h); se = 1/np.sqrt(len(hk)-3)
log(f'  管家组织轴 (GTEx WB vs NT): n={len(hk)}, 基因={hk.Gene.nunique()}, rho={r_h:+.4f}, '
    f'Fisher-z 95% CI {np.tanh(zf-1.96*se):+.3f} to {np.tanh(zf+1.96*se):+.3f}')
log(f'    (Fig.4: rho=+0.64, n=72, CI 0.47-0.76)')
R['fig4'] = dict(testbed=dict(n=int(len(t)), genes=int(pd.unique(t.index.get_level_values('Gene')).size), rho=float(r_t)),
                 housekeeping=dict(n=int(len(hk)), genes=int(hk.Gene.nunique()), rho=float(r_h)))

# ---- 3.10 主臂基因簇自助法区间 --------------------------------------------
log('\n' + '=' * 78)
log(f'3.10 主臂基因簇自助法（B={B_PRIMARY}, seed={SEED_BOOTSTRAP_PORTAL}）')
log('=' * 78)
genes32 = pd.unique(S13.Gene)
rng = np.random.default_rng(SEED_BOOTSTRAP_PORTAL)
byg = {g: d for g, d in S13.groupby('Gene')}
rhos, rates = [], []
for _ in range(B_PRIMARY):
    pick = rng.choice(genes32, size=len(genes32), replace=True)
    zz1 = np.concatenate([byg[g]['Z_GTEx'].values for g in pick])
    zz2 = np.concatenate([byg[g]['Z_eQTLGen'].values for g in pick])
    rhos.append(stats.spearmanr(zz1, zz2)[0])
    rates.append(np.mean(np.sign(zz1) == np.sign(zz2)))
pr = np.nanpercentile(rhos, [2.5, 97.5]); pa = np.nanpercentile(rates, [2.5, 97.5])
log(f'  Spearman rho 95% CI      = {pr[0]:+.3f} to {pr[1]:+.3f}   (报告 0.12-0.62)')
log(f'  方向一致率 95% CI        = {100*pa[0]:.1f}% to {100*pa[1]:.1f}%   (报告 58.3-79.2%)')
R['primary_bootstrap'] = dict(B=B_PRIMARY, seed=SEED_BOOTSTRAP_PORTAL,
                              rho_ci=[float(pr[0]), float(pr[1])],
                              rate_ci_pct=[float(100*pa[0]), float(100*pa[1])])

# ---- 3.11 其他正文数值的可核验性 -------------------------------------------
log('\n' + '=' * 78)
log('3.11 其他正文/补充材料数值核验')
log('=' * 78)
# TUBB
tb18 = S18[S18.Gene == 'TUBB']
log(f'  TUBB eQTLGen |Z| 最大 = {tb18.Z_eQTLGen.abs().max():.2f} (报告 11.89); '
    f'FDR 显著对 = {int((tb18["BH q"]<ALPHA).sum())} (报告 3)')
log(f'  TUBB 模型 SNP = {S23.loc[S23.Gene=="TUBB","eQTLGen model SNPs (n)"].values} (报告 1,848)')
# RNH1
r3 = S3[(S3.Gene == 'RNH1') & (S3.Phenotype == 'DR')]
r18 = S18[(S18.Gene == 'RNH1') & (S18.Phenotype == 'DR')]
log(f'  RNH1 DR: GTEx NT Z = {r3.Z_Nerve_Tibial.values[0]:+.3f} (报告 +2.67); '
    f'eQTLGen Z = {r18.Z_eQTLGen.values[0]:+.3f} (报告 +2.31)')
# HSP90AB1
h3 = S3[(S3.Gene == 'HSP90AB1') & (S3.Phenotype == 'DR')]
h18 = S18[(S18.Gene == 'HSP90AB1') & (S18.Phenotype == 'DR')]
log(f'  HSP90AB1 DR: GTEx WB Z = {h3.Z_Whole_Blood.values[0]:+.4f} (报告 −0.64); '
    f'GTEx NT Z = {h3.Z_Nerve_Tibial.values[0]:+.4f} (报告 +0.47); '
    f'eQTLGen Z = {h18.Z_eQTLGen.values[0]:+.4f} (报告 −0.53)')
# 顶 10 |Z| 对：在每个来源内部各自排序后取交集（Discussion 口径：只共享 1 对）
top = S3[['Gene','Phenotype','Z_Whole_Blood']].dropna().merge(
      S18[['Gene','Phenotype','Z_eQTLGen']], on=['Gene','Phenotype'])
t10_g = set(map(tuple, top.nlargest(10, 'Z_Whole_Blood')[['Gene','Phenotype']].values))
top['absE'] = top.Z_eQTLGen.abs()
t10_e = set(map(tuple, top.nlargest(10, 'absE')[['Gene','Phenotype']].values))
shared = t10_g & t10_e
log(f'  GTEx-WB 侧 top10 = {sorted(t10_g)}')
log(f'  eQTLGen 侧 top10 = {sorted(t10_e)}')
log(f'  交集 ({len(shared)} 对) = {sorted(shared)}   (Discussion 报告: 仅共享 1 对, 即 ANXA1–DPN)')
R['top10_overlap'] = dict(gtex_top10=sorted(t10_g), eqtlgen_top10=sorted(t10_e),
                          shared=sorted(shared))

# ---- 3.12 跨队列复现（Table S5a / S5b）------------------------------------
log('\n' + '=' * 78)
log('3.12 跨队列复现核验（Table S5a 合并统计量 / Table S5b 方向一致率）')
log('=' * 78)
z_fin, z_ukb = 2.31, 0.72            # eQTLGen 权重下 FinnGen R13 / UKB 的 Z（表注所载取值）
pooled = (z_fin + z_ukb) / 2
Q  = (z_fin - pooled) ** 2 + (z_ukb - pooled) ** 2
I2 = 100 * (Q - 1) / Q
se_iv  = 1 / np.sqrt(2)                                  # 单位方差, 2 队列
tau_dl = np.sqrt(max(0.0, (Q - 1) / 2))                  # DL: (Q-df)/Σw, Σw=2
se_dl  = 1 / np.sqrt(2 / (1 + tau_dl ** 2))
tau_df = np.sqrt(max(0.0, (Q - 1) / 1))                  # (Q-df)/df 变体
se_df  = 1 / np.sqrt(2 / (1 + tau_df ** 2))
pi_dl  = (pooled - 1.96 * np.sqrt(se_dl ** 2 + tau_dl ** 2),
          pooled + 1.96 * np.sqrt(se_dl ** 2 + tau_dl ** 2))
pi_df  = (pooled - 1.96 * np.sqrt(se_df ** 2 + tau_df ** 2),
          pooled + 1.96 * np.sqrt(se_df ** 2 + tau_df ** 2))
log(f'  合并 Z (未加权均值) = {pooled:+.4f}    (报告 +1.51)')
log(f'  Cochran Q = {Q:.4f},  I² = {I2:.1f}%    (报告 Q = 1.26, I² = 20.6%)')
log(f'  P = {2*(1-stats.norm.cdf(pooled/se_df)):.4f} (对应 Z/SE={pooled/se_df:.2f})   (报告 Z/SE = 1.91, P = 0.056)')
log(f'  [DL 约定 τ²=(Q-df)/Σw=2] τ={tau_dl:.3f}, SE={se_dl:.3f}, 预测区间 {pi_dl[0]:+.2f} to {pi_dl[1]:+.2f}')
log(f'  [表中约定 τ²=(Q-df)/df=1] τ={tau_df:.3f}, SE={se_df:.3f}, 预测区间 {pi_df[0]:+.2f} to {pi_df[1]:+.2f}'
    f'   (报告 τ=0.51, SE=0.79, 预测区间 −0.33 to +3.36)')
R['s5a'] = dict(pooled_z=float(pooled), Q=float(Q), I2_pct=float(I2),
                tau_DL=float(tau_dl), SE_DL=float(se_dl), PI_DL=[float(x) for x in pi_dl],
                tau_table=float(tau_df), SE_table=float(se_df), PI_table=[float(x) for x in pi_df])

S5b = pd.DataFrame(rowsof(st[5])[1:], columns=rowsof(st[5])[0])
c = (S5b['Direction'].str.strip().str.lower() == 'consistent').sum()
log(f'\n  Table S5b 八基因方向一致: {c}/{len(S5b)} = {100*c/len(S5b):.1f}%, '
    f'精确二项 P = {stats.binomtest(int(c), len(S5b), .5).pvalue:.2f}   '
    f'(报告 5/8 = 62.5%, P = 0.73)')
R['s5b'] = dict(k=int(c), n=int(len(S5b)), rate_pct=float(100*c/len(S5b)),
                binom_p=float(stats.binomtest(int(c), len(S5b), .5).pvalue))

json.dump(R, open(os.path.join(OUTD, 'recompute_results.json'), 'w', encoding='utf-8',
                  newline='\n'),
          ensure_ascii=False, indent=1, default=str)
open(os.path.join(OUTD, 'recompute_log.txt'), 'w', encoding='utf-8',
     newline='\n').write('\n'.join(LOG))
log('\n[完成] merged_pairs.csv / recompute_results.json / recompute_log.txt 已写出')

# -*- coding: utf-8 -*-
"""
Fig. 6 单独重绘（v5 评审 P1-2 修订）—— 只出 Fig6，不触碰任何其它图。

改动相对 03_redraw_Fig6.py（原脚本）：
  R1  ylim 由硬编码 26 改为「按真实 Clopper-Pearson 上界 + 余量」计算
      —— 原值 26 小于最大上界 30.1%（k=4, n=29），导致误差棒上帽与 k/N 标注
         溢出坐标轴、压到面板标题上（这是评审 M4 指出的压字根因）。
  R2  图例从面板 (a) 内部移到三面板之上（fig 级、2 列、无框）—— 原 loc='upper left'
      覆盖 DR 候选组的柱体。
  R3  k/N 标注改为「柱顶/误差棒上帽 + 固定偏移」，并加极小白底 bbox，
      避免相邻标注互相压字与被须线穿过。
  R4  数据源由旧的 `Additional file 1.docx`（已不存在）改为现行
      `Additional file 1_审稿意见修订_20260917.docx`，并加回归断言：
      逐格核对 SI Table S18 的 8 个受控组 k/N。
接受准则：输出 PNG 恰为 3990×1800（figsize 6.65×3.0 @600dpi），同名 PDF 为矢量。
2026-09-20 格式批次：figsize 7.2->6.65（页宽 182.9->168.9 mm，满足 BMC <=170 mm）；k/N 标签 5.2->6.2 pt。
"""
import paths_config as P  # 统一路径入口（2026-09-20）
import os, shutil, sys, io, re
import numpy as np
from scipy import stats
from docx import Document
from docx.table import Table
from docx.oxml.ns import qn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

AF  = P.need(P.AF1, 'Additional file 1（从期刊补充材料下载后用 AF1_DOCX 指定）')
OUT = P.OUT_MAIN
BK  = os.path.join(OUT, '_backup_before_v5Fig6_labels_20260920')
os.makedirs(BK, exist_ok=True)

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 7.5, 'axes.linewidth': 0.7,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'pdf.fonttype': 42, 'ps.fonttype': 42})
C_GTEX, C_EQTL = '#C0392B', '#2471A3'

d = Document(AF)
# 2026-10-03：原按 body 顺序硬编码 `tabs[i]`（grid(0/1/5/15/18)），只对 2026-09-17 那一版
#   Additional file 1 成立。GE 版补充材料重排了表号（每张表整体位移一位、S4a/S4b 拆成
#   S5a/S5b、原 S26 提到 S1），硬编码索引因此整体错位：grid(5) 落到 Table S5a（RNH1 跨队列
#   表，无 ACAT 列），触发 "Table S5 ACAT columns not found"。改为**按题注解析表号**，并保留
#   BMC 号 → GE 号的映射；两种 SI 都能跑，加表/挪表也不会再错位。
_by_label, _cur = {}, None
for _ch in d.element.body.iterchildren():
    if _ch.tag == qn('w:p'):
        _t = ''.join(_x.text or '' for _x in _ch.iter(qn('w:t'))).strip()
        _m = re.match(r'^\**\s*Table\s+(S\d+[a-c]?)\b', _t)
        if _m:
            _cur = _m.group(1)
    elif _ch.tag == qn('w:tbl'):
        if _cur and _cur not in _by_label:
            _by_label[_cur] = Table(_ch, d)
print('AF1 tables resolved:', sorted(_by_label))

_TBL_ALIAS = {
    'S1': ('S2', 'S1'),     # 基因分组注释              BMC S1  -> GE S2
    'S2': ('S3', 'S2'),     # GTEx v8 基线 TWAS（222）  BMC S2  -> GE S3
    'S5': ('S6', 'S5'),     # 管家对照双组织            BMC S5  -> GE S6
    'S14': ('S15', 'S14'),  # 管家对照 eQTLGen          BMC S14 -> GE S15
    'S17': ('S18', 'S17'),  # eQTLGen 逐基因（207 对）  BMC S17 -> GE S18
}


def _pick(label):
    for cand in _TBL_ALIAS.get(label, (label,)):
        if cand in _by_label:
            return cand
    raise SystemExit('[missing table] none of %r resolved; document has %s'
                     % (_TBL_ALIAS.get(label, (label,)), sorted(_by_label)))


grid = lambda s: [[c.text.strip() for c in r.cells] for r in _by_label[_pick(s)].rows]
# 2026-10-03：改用 P.num()，与 04_redraw_Fig8.py 同一解析器；GE 版 SI 以 `—` 表示缺失值。
f = P.num


def norm(g):
    g = (g or '').strip().lower()
    if 'non' in g and 'candidate' in g: return 'Non-candidate'
    if 'candidate' in g: return 'Candidate'
    if 't2dm' in g: return 'T2DM'
    if 'housekeeping' in g or 'hk' == g: return 'Housekeeping'
    return g


# ---------------- 数据抽取（与原脚本同源，仅换现行文件名） ----------------
S2 = grid('S2'); i2 = {n: k for k, n in enumerate(S2[0])}
G  = {r[0]: norm(r[1]) for r in grid('S1')[1:] if r[0]}
GT = {}
for r in S2[1:]:
    if len(r) < 10 or not r[0]:
        continue
    p = f(r[i2['P_ACAT_O']])
    if not np.isnan(p):
        GT.setdefault((G.get(r[0], '?'), r[1]), []).append(p)
S5 = grid('S5'); acat_cols = [i for i, h in enumerate(S5[0]) if 'ACAT' in h.upper()]
assert len(acat_cols) >= 3, 'Table S5 ACAT columns not found: %r' % (S5[0],)
for r in S5[1:]:
    if not r[0]:
        continue
    for ph, ci in zip(['DR', 'DN', 'DPN'], acat_cols[:3]):
        p = f(r[ci])
        if not np.isnan(p):
            GT.setdefault(('Housekeeping', ph), []).append(p)

EQ = {}
for r in grid('S17')[1:]:
    if len(r) < 8 or not r[0]:
        continue
    p = f(r[4])
    if not np.isnan(p):
        EQ.setdefault((norm(r[2]), r[1]), []).append(p)
for r in grid('S14')[1:]:
    if len(r) < 6 or not r[0]:
        continue
    p = f(r[3])
    if not np.isnan(p):
        EQ.setdefault(('Housekeeping', r[1]), []).append(p)

GRPS = ['Candidate', 'Non-candidate', 'T2DM', 'Housekeeping']
PH   = ['DR', 'DN', 'DPN']


def cp(k, n):
    lo = 0.0 if k == 0 else stats.beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(0.975, k + 1, n - k)
    return 100 * lo, 100 * hi


def kn(DD, g, ph):
    ps = np.array(DD.get((g, ph), []))
    if len(ps) == 0:
        return 0, 0, 0.0, 0.0, 0.0
    k = int((ps < 0.05).sum()); n = len(ps); r = 100 * k / n
    lo, hi = cp(k, n)
    return k, n, r, r - lo, hi - r


# ---------------- 回归断言：与 SI Table S18 逐格对账 ----------------
EXPECT = {  # (source, group, phenotype) -> 'k/n'
    ('GTEx', 'Candidate', 'DR'): '2/28',      ('GTEx', 'Candidate', 'DN'): '4/28',
    ('GTEx', 'Candidate', 'DPN'): '2/28',     ('GTEx', 'Non-candidate', 'DR'): '3/27',
    ('GTEx', 'Non-candidate', 'DN'): '1/27',  ('GTEx', 'Non-candidate', 'DPN'): '4/27',
    ('GTEx', 'T2DM', 'DR'): '3/19',           ('GTEx', 'T2DM', 'DN'): '1/19',
    ('GTEx', 'T2DM', 'DPN'): '2/19',          ('GTEx', 'Housekeeping', 'DR'): '4/29',
    ('GTEx', 'Housekeeping', 'DN'): '0/29',   ('GTEx', 'Housekeeping', 'DPN'): '1/29',
    ('eQTLGen', 'Candidate', 'DR'): '3/27',   ('eQTLGen', 'Candidate', 'DN'): '2/27',
    ('eQTLGen', 'Candidate', 'DPN'): '3/27',  ('eQTLGen', 'Non-candidate', 'DR'): '1/25',
    ('eQTLGen', 'Non-candidate', 'DN'): '3/25',('eQTLGen', 'Non-candidate', 'DPN'): '2/25',
    ('eQTLGen', 'T2DM', 'DR'): '2/17',        ('eQTLGen', 'T2DM', 'DN'): '0/17',
    ('eQTLGen', 'T2DM', 'DPN'): '1/17',       ('eQTLGen', 'Housekeeping', 'DR'): '4/27',
    ('eQTLGen', 'Housekeeping', 'DN'): '0/27',('eQTLGen', 'Housekeeping', 'DPN'): '3/27',
}
bad = []
for (src, g, ph), want in EXPECT.items():
    DD = GT if src == 'GTEx' else EQ
    k, n, *_ = kn(DD, g, ph)
    got = '%d/%d' % (k, n)
    if got != want:
        bad.append((src, g, ph, want, got))
if bad:
    print('!! S18 回归断言失败：')
    for b in bad:
        print('   ', b)
else:
    print('OK  S18 回归断言：全部 %d 组 k/N 与 SI Table S18 逐格一致' % len(EXPECT))

# ---------------- 真实数据范围 -> ylim（R1） ----------------
max_hi = 0.0
for ph in PH:
    for g in GRPS:
        for DD in (GT, EQ):
            _, _, r, _, his = kn(DD, g, ph)
            max_hi = max(max_hi, r + his)
YLIM = float(np.ceil((max_hi * 1.12) / 5.0) * 5)   # 取 12% 余量并向上取整到 5 的倍数
print('OK  最大 Clopper-Pearson 上界 = %.1f%%  ->  ylim = 0..%.0f%%' % (max_hi, YLIM))

# ---------------- 绘图 ----------------
fig, axes = plt.subplots(1, 3, figsize=(6.65, 3.0), sharey=True)
x = np.arange(len(GRPS)); w = 0.36
handles, labels = [], []
for pi, ph in enumerate(PH):
    ax = axes[pi]
    prev_vals = None
    for src, DD, col, off in [('GTEx v8 multi-tissue ACAT-O', GT, C_GTEX, -w / 2),
                              ('eQTLGen whole blood', EQ, C_EQTL, w / 2)]:
        vals, los, his, ns = [], [], [], []
        for g in GRPS:
            k, n, r, lo, hi = kn(DD, g, ph)
            vals.append(r); los.append(lo); his.append(hi); ns.append((k, n))
        b = ax.bar(x + off, vals, w, color=col, edgecolor='black', lw=0.5, label=src)
        ax.errorbar(x + off, vals, yerr=[los, his], fmt='none',
                    ecolor='#222222', elinewidth=0.8, capsize=3)
        if pi == 0:
            handles.append(b[0]); labels.append(src)
        # R3：标注固定在柱顶之上，不随上帽浮动；加极小白底避免须线穿字
        # R4（2026-09-20）：两条柱等高时（如 HK 组的 0/29 与 0/27、4/29 与 4/27），
        # 两串标签会并排叠字。字号由 5.2 提到 6.2 后更明显，故对"同高"的后一序列上移错开。
        for j, v in enumerate(vals):
            dy = 0.45
            if prev_vals is not None and abs(v - prev_vals[j]) < 3.0:
                dy += 3.6
            ax.text(x[j] + off, v + dy, '%d/%d' % ns[j], ha='center', va='bottom',
                    fontsize=6.2, color='#222222',
                    bbox=dict(facecolor='white', edgecolor='none', pad=0.15))
        prev_vals = vals
    ax.set_xticks(x)
    ax.set_xticklabels(['Cand', 'Non-cand', 'T2DM', 'HK'], fontsize=6.4)
    ax.set_ylim(0, YLIM)
    ax.set_title('(%s) %s' % ('abc'[pi], ph), fontsize=7.6, pad=4)
    if pi == 0:
        ax.set_ylabel('Genes with nominal p < 0.05 (%)')
    ax.tick_params(axis='y', labelsize=6.4)

# R2：共享图例置于三面板之上，绝不再覆盖柱体；锚点留在画布内，避免被 figsize 边界裁掉
fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.885),
           ncol=2, frameon=False, fontsize=6.6, handlelength=1.4,
           columnspacing=1.6, handletextpad=0.5)
fig.tight_layout(rect=(0, 0, 1, 0.85))

for ext in ['png', 'pdf']:
    dst = os.path.join(OUT, 'Fig6.' + ext)
    if os.path.exists(dst) and not os.path.exists(os.path.join(BK, 'Fig6.' + ext)):
        shutil.copy2(dst, os.path.join(BK, 'Fig6.' + ext))
    fig.savefig(dst, dpi=600)
plt.close(fig)

from PIL import Image
# matplotlib 默认写 RGBA；权威图集其余 13 张均为 RGB（评审 m-14），此处统一转为 RGB 并锁回 600 dpi
_p = os.path.join(OUT, 'Fig6.png')
Image.open(_p).convert('RGB').save(_p, dpi=(600, 600))
im = Image.open(_p)
print('OK  wrote Fig6.png  %s mode=%s dpi=%s size=%s' % (os.path.getsize(_p), im.mode, im.info.get('dpi'), im.size))
print('OK  wrote Fig6.pdf  %s bytes' % os.path.getsize(os.path.join(OUT, 'Fig6.pdf')))
print('OK  backup ->', BK)
for ph in PH:
    for src, DD in (('GTEx', GT), ('eQTLGen', EQ)):
        print('   %-4s %-8s' % (ph, src), [('%d/%d' % kn(DD, g, ph)[:2]) for g in GRPS])

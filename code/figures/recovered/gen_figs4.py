# -*- coding: utf-8 -*-
"""Fig. S4 (authoritative re-generation) — eQTLGen model SNP counts by gene group.

Universe (matches the harmonized eQTLGen arm = Table S10 row "eQTLGen whole-blood
(harmonized reanalysis)", 61 genes / 183 gene-phenotype pairs, and the denominators
already used by Fig. S3: 72 / 72 / 39 = 24 / 24 / 13 genes x 3 phenotypes):

  gene has (i) a numeric n_snps_model and (ii) a valid harmonized S-PrediXcan Z,
  i.e. the same 61 genes that carry an eQTLGen statistic.

Outputs into OUTDIR:  FigS4.png / FigS4.pdf  and  _numbers_figs4.json
"""
import os, csv, json, math, shutil, collections
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'pdf.fonttype': 42, 'ps.fonttype': 42})   # 2026-09-20: 消除 Type3 字型

# ---- paths (2026-10-05) -----------------------------------------------------
# Was: three hard-coded 2026-09 absolute paths into the predecessor build root and a
# personal supplement-figure directory. Resolved now, so nothing personal ships
# (code/README.md rule 3) and the figure can be produced from a clone.
#
# INPUT: the harmonized eQTLGen S-PrediXcan table, which ships here at
#   data/superseded/eqtlgen_spredixcan_harmonized_results.csv
# That layer is the pre-correction Z layer and is otherwise never an input. Fig. S2 uses
# only its **model SNP counts** (`n_snps_model` — a property of the fitted model, not
# changed by the sigma_i / PLINK corrections) and a valid Z as a **presence** filter for
# the universe; it does not use the Z values. Override with $FIG_S2_INPUT.
def _repo_root(start):
    d = start
    for _ in range(8):
        if os.path.exists(os.path.join(d, '.zenodo.json')):
            return d
        p = os.path.dirname(d)
        if p == d:
            break
        d = p
    return os.path.dirname(os.path.dirname(start))

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = _repo_root(_HERE)
INPUT = os.environ.get('FIG_S2_INPUT') or os.path.join(
    _REPO, 'data', 'superseded', 'eqtlgen_spredixcan_harmonized_results.csv')
if not os.path.exists(INPUT):
    raise SystemExit('missing input: %s\n  set FIG_S2_INPUT to the harmonized eQTLGen '
                     'S-PrediXcan table (ships as data/superseded/'
                     'eqtlgen_spredixcan_harmonized_results.csv).' % INPUT)
OUTDIR = os.environ.get('FIG_S2_OUT') or os.path.join(_REPO, '..', '_figs2_out')
NUMDIR = OUTDIR
os.makedirs(OUTDIR, exist_ok=True)

RED, BLUE, GREEN = '#C0392B', '#2471A3', '#27AE60'
PALETTE = {'Candidate': RED, 'NonCandidate': BLUE, 'T2DM_Control': GREEN}
LABEL = {'Candidate': 'Candidate', 'NonCandidate': 'Non-candidate', 'T2DM_Control': 'T2DM control'}
ORDER = ['Candidate', 'NonCandidate', 'T2DM_Control']


def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except Exception:
        return None


def style(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=9)


# ---------------------------------------------------------------- inputs
rows = list(csv.DictReader(open(INPUT, encoding='utf-8-sig')))
per = {}
for r in rows:
    g = r['gene']
    if g in per:
        continue
    if num(r['zscore']) is None or num(r['pvalue']) is None:
        continue
    v = num(r['n_snps_model'])
    if v is None:
        continue
    per[g] = (r['grp'], v)

by_group = collections.defaultdict(list)
for g, (grp, v) in per.items():
    if grp in ORDER:
        by_group[grp].append(v)

NUM = {'universe': 'harmonized eQTLGen arm: valid S-PrediXcan Z + numeric n_snps_model',
       'genes_total': sum(len(v) for v in by_group.values()),
       'groups': {}}
for g in ORDER:
    v = sorted(by_group[g])
    a = np.array(v, dtype=float)
    NUM['groups'][g] = {'n': len(v), 'median': float(np.median(a)),
                        'q1': float(np.percentile(a, 25)), 'q3': float(np.percentile(a, 75)),
                        'min': float(a.min()), 'max': float(a.max())}
allv = sorted(x for g in ORDER for x in by_group[g])
a = np.array(allv, dtype=float)
NUM['overall'] = {'n': len(allv), 'median': float(np.median(a)),
                  'q1': float(np.percentile(a, 25)), 'q3': float(np.percentile(a, 75))}

# ---------------------------------------------------------------- figure
fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=600)
xs = np.arange(len(ORDER))
rng = np.random.default_rng(20260915)
ymax = max(max(v) for v in by_group.values())
ytop = 1.32 * ymax
for i, g in enumerate(ORDER):
    v = np.array(sorted(by_group[g]), dtype=float)
    parts = ax.violinplot([v], positions=[i], widths=0.72, showextrema=False)
    for b in parts['bodies']:
        b.set_facecolor(PALETTE[g]); b.set_alpha(0.30); b.set_edgecolor(PALETTE[g]); b.set_linewidth(1.2)
    jit = (rng.random(len(v)) - 0.5) * 0.17
    ax.scatter(np.full(len(v), i) + jit, v, s=17, color=PALETTE[g],
               edgecolor='white', linewidth=0.35, zorder=3)
    med = float(np.median(v))
    ax.plot([i - 0.26, i + 0.26], [med, med], color='black', lw=1.6, zorder=4)
    ax.text(i, 1.235 * ymax, 'median = %d' % med, ha='center', va='bottom',
            fontsize=9.2, fontweight='bold', color='#222222', zorder=6)
    ax.text(i, 1.075 * ymax, 'n = %d genes' % len(v), ha='center', va='bottom',
            fontsize=8.2, color='#555555', zorder=6)

ax.set_xticks(xs)
ax.set_xticklabels([LABEL[g] for g in ORDER], fontsize=9.5)
ax.set_xlim(-0.6, len(ORDER) - 0.4)
ax.set_ylim(0, ytop)
ax.set_yticks(np.arange(0, ymax + 1, 1000))
ax.set_ylabel('Number of eQTL SNPs in model', fontsize=10)
style(ax)
fig.tight_layout()
out_png = os.path.join(OUTDIR, 'FigS4.png')
for ext in ('png', 'pdf'):
    fig.savefig(os.path.join(OUTDIR, 'FigS4.' + ext), dpi=600, bbox_inches='tight')
plt.close(fig)
# 2026-09-20：matplotlib 默认写 RGBA，而图集其余图为 RGB（评审 m-14），统一转 RGB。
from PIL import Image as _Image
_im = _Image.open(out_png)
if _im.mode != 'RGB':
    _im.convert('RGB').save(out_png, dpi=(600, 600))

# archive the superseded option-B draft, if present
old = os.path.join(OUTDIR, 'FigS4_选项B_权威管线_未采用.png')
if os.path.exists(old):
    arch = os.path.join(OUTDIR, '_superseded')
    os.makedirs(arch, exist_ok=True)
    shutil.move(old, os.path.join(arch, 'FigS4_选项B_权威管线_未采用.png'))

json.dump(NUM, open(os.path.join(NUMDIR, '_numbers_figs4.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)

print(json.dumps(NUM, ensure_ascii=False, indent=2))
print()
print('written:', out_png, os.path.getsize(out_png), 'bytes')

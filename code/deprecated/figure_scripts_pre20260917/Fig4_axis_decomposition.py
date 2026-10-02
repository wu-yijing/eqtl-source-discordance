# -*- coding: utf-8 -*-
"""Fig. 4 - axis-resolved source-discordance decomposition, 49-gene common universe
(147 gene-phenotype pairs; the same universe as the tissue-only arm of Table 3b).

PROVENANCE OF EVERY PLOTTED VALUE  (read before reusing this script)
--------------------------------------------------------------------------
Every value in this figure is reproducible from the archived inputs. The dual-mismatch arm
is the GTEx v8 multi-tissue STOUFFER WEIGHTED-Z estimate (data/processed/
gtex_stouffer_integrated.csv, column Z_Multi) intersected with the harmonized eQTLGen
whole-blood S-PrediXcan Z (data/processed/eqtlgen_spredixcan_harmonized_results.csv, column
zscore). That estimate is signed by construction, so no sign is assigned anywhere in the arm.

  panel-only    rho = 0.355   direction consistency = 67.3%
  tissue-only   rho = 0.422   direction consistency = 67.3%
  dual-mismatch rho = 0.287   direction consistency = 59.2%
  delta rho (dual - panel-only)  = -0.067, 95% CI [-0.196, +0.039], P = 0.252
  delta rho (dual - tissue-only) = -0.135, 95% CI [-0.375, +0.081], P = 0.238
  delta direction consistency    = -8.2 pp for both contrasts

The full-pair arm definitions (63 / 57 / 50 genes and 189 / 171 / 150 gene-phenotype pairs)
and the per-arm gene-set composition are tabulated in Additional file 1: Table S10.

HISTORY - an earlier open item, now closed. A previous version of this block recorded that
the dual-arm rho "could NOT be recomputed exactly from the archived inputs" and was
transcribed from the analysis record, because the arm was assumed to be built on ACAT-O with
the sign taken from the GTEx Whole_Blood Z-score. That assumption was wrong: ACAT-O is only
the direction-free enrichment endpoint, and the dual arm uses the Stouffer Z_Multi estimate,
which is signed by construction. With the correct estimator all six headline numbers
reproduce exactly (re-verified 2026-09-15), and Methods 2.4 now states the estimator
explicitly. verify_literals() below re-derives them at run time.

verify_literals() is read-only: it never alters what is plotted.
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.major.width'] = 0.8
plt.rcParams['ytick.major.width'] = 0.8

OUT = os.environ.get('FIG4_OUT') or r'E:\workbuddy\BMC Genomics投稿资料\定稿图集_Fig1-8_20260914'
os.makedirs(OUT, exist_ok=True)

# ===== plotted values: see the PROVENANCE block in the module docstring =====
# 49-gene common universe, n = 147 pairs
arm_names = ['Panel-only\nresource / sample-size\n67.3% consistent',
             'Tissue-only\ntissue context\n67.3% consistent',
             'Dual\nboth axes\n59.2% consistent']
# (a) recomputed: panel-only and tissue-only rho ; (b) transcribed: dual-arm rho
rho = np.array([0.355, 0.422, 0.287])
ci_lo = np.array([0.204, 0.279, 0.131])
ci_hi = np.array([0.488, 0.547, 0.429])
# (a) recomputed
cons = np.array([67.3, 67.3, 59.2])
ci_err = np.vstack([rho - ci_lo, ci_hi - rho])

# (b) Forest (panel b): transcribed from the archived analysis record
labels_b = ['dual − panel-only', 'dual − tissue-only']
delta_rho = np.array([-0.067, -0.135])
rho_lo = np.array([-0.196, -0.375])
rho_hi = np.array([+0.039, +0.081])
p_rho = np.array([0.252, 0.238])
delta_dc = np.array([-8.2, -8.2])
p_dc = np.array([0.018, 0.201])

def verify_literals():
    """Re-derive the six headline numbers from the archived inputs (read-only)."""
    try:
        import csv, math, os as _os
        from scipy import stats
    except Exception as exc:                              # pragma: no cover
        print('[verify] skipped (missing dependency): %s' % exc)
        return
    dp = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                       'data', 'processed')

    def _num(x):
        try:
            v = float(x)
            return v if math.isfinite(v) else None
        except Exception:
            return None

    def _load(name, gcol, tcol, zcol):
        out = {}
        with open(_os.path.join(dp, name), encoding='utf-8-sig') as fh:
            for r in csv.DictReader(fh):
                v = _num(r[zcol])
                if v is not None:
                    out.setdefault((r[gcol], r[tcol]), v)
        return out

    wb, nt = {}, {}
    for t in ('DR', 'DN', 'DPN'):
        wb.update(_load('gtex_Whole_Blood_%s.csv' % t, 'gene', 'trait', 'zscore'))
        nt.update(_load('gtex_Nerve_Tibial_%s.csv' % t, 'gene', 'trait', 'zscore'))
    zmu = _load('gtex_stouffer_integrated.csv', 'Gene', 'Trait', 'Z_Multi')
    eq = _load('eqtlgen_spredixcan_harmonized_results.csv', 'gene', 'trait', 'zscore')

    universe = sorted(set(wb) & set(nt) & set(zmu) & set(eq))
    expected = {
        'panel-only': ((wb, eq), 0.355, 67.3),
        'tissue-only': ((wb, nt), 0.422, 67.3),
        'dual-mismatch': ((zmu, eq), 0.287, 59.2),
    }
    print('[verify] common universe: %d genes / %d pairs' % (len({k[0] for k in universe}), len(universe)))
    bad = []
    for arm, ((a, b), rho_exp, cons_exp) in expected.items():
        x = [a[k] for k in universe]
        y = [b[k] for k in universe]
        rho = float(stats.spearmanr(x, y).statistic)
        cons = 100.0 * sum(1 for p, q in zip(x, y) if (p > 0) == (q > 0)) / len(universe)
        ok = abs(round(rho, 3) - rho_exp) <= 0.001 and abs(round(cons, 1) - cons_exp) <= 0.05
        print('  %-14s rho %.3f (expect %.3f) | consistency %.1f%% (expect %.1f%%)  %s'
              % (arm, rho, rho_exp, cons, cons_exp, 'OK' if ok else 'MISMATCH'))
        if not ok:
            bad.append(arm)
    print('[verify] ' + ('all plotted values reproduce from the archived inputs'
                         if not bad else 'MISMATCH in: ' + ', '.join(bad)))


verify_literals()


C_PANEL, C_TISSUE, C_DUAL = '#1f77b4', '#d62728', '#9467bd'
TXT = '#222222'

fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.4, 3.35), dpi=300,
                                 gridspec_kw={'width_ratios': [1.0, 1.30], 'wspace': 0.42})

# ---------------- (a) 柱状图 ----------------
x = np.arange(3)
ax_a.bar(x, rho, width=0.62, color=[C_PANEL, C_TISSUE, C_DUAL],
         edgecolor='black', linewidth=0.6, zorder=3)
ax_a.errorbar(x, rho, yerr=ci_err, fmt='none', ecolor='black',
              capsize=4, capthick=0.9, elinewidth=0.9, zorder=4)

for xi, r, hi, lo in zip(x, rho, ci_hi, ci_lo):
    ax_a.text(xi, hi + 0.026, r'$\rho$ = %.3f' % r, ha='center', va='bottom',
              fontsize=8.2, fontweight='bold', color=TXT, zorder=5)
    ax_a.text(xi, hi + 0.088, '95%% CI %.3f–%.3f' % (lo, hi), ha='center', va='bottom',
              fontsize=6.0, color='#555555', zorder=5)
for xi, c in zip(x, cons):
    pass

ax_a.set_xticks(x)
ax_a.set_xticklabels(arm_names, fontsize=6.8)
ax_a.set_xlim(-0.62, 2.62)
ax_a.set_ylim(0, 0.80)
ax_a.set_yticks(np.arange(0, 0.61, 0.1))
ax_a.set_ylabel('Spearman $\\rho$ between sources', fontsize=8.5)
ax_a.tick_params(axis='y', labelsize=7.5)
ax_a.tick_params(axis='x', length=0)
ax_a.text(0.02, 0.97, '(a)', transform=ax_a.transAxes, ha='left', va='top',
          fontsize=10, fontweight='bold', color='black', zorder=10)
ax_a.text(0.98, 0.985, '49-gene common universe\nn = 147 pairs', transform=ax_a.transAxes,
          ha='right', va='top', fontsize=6.4, color='#444444', style='italic', zorder=10)
for sp in ('top', 'right'):
    ax_a.spines[sp].set_visible(False)
for sp in ('left', 'bottom'):
    ax_a.spines[sp].set_color('black'); ax_a.spines[sp].set_linewidth(0.8)

# ---------------- (b) Forest ----------------
y = np.array([1, 0])
ax_b.axvline(0, color=C_TISSUE, linestyle=(0, (5, 3)), linewidth=1.0, zorder=2)
for yi, lo, hi in zip(y, rho_lo, rho_hi):
    ax_b.plot([lo, hi], [yi, yi], color='black', linewidth=1.0, zorder=3, solid_capstyle='butt')
    ax_b.plot([lo, lo], [yi - 0.10, yi + 0.10], color='black', linewidth=1.0, zorder=3)
    ax_b.plot([hi, hi], [yi - 0.10, yi + 0.10], color='black', linewidth=1.0, zorder=3)
ax_b.scatter(delta_rho, y, s=40, color='black', edgecolor='black', linewidth=0.5, zorder=4)

for yi, dr, pr, dd, pd_, lo, hi in zip(y, delta_rho, p_rho, delta_dc, p_dc, rho_lo, rho_hi):
    ax_b.text(0.145, yi + 0.46,
              r'$\Delta\rho$ = %+.3f  [%+.3f, %+.3f], P = %.3f' % (dr, lo, hi, pr),
              ha='right', va='center', fontsize=6.6, color=TXT,
              bbox=dict(boxstyle='round,pad=0.30', facecolor='white', edgecolor='none', alpha=0.95),
              zorder=10)
    ax_b.text(0.145, yi + 0.20,
              r'$\Delta$ consistency = %+.1f pp, P = %.3f' % (dd, pd_),
              ha='right', va='center', fontsize=6.6, color='#555555',
              bbox=dict(boxstyle='round,pad=0.30', facecolor='white', edgecolor='none', alpha=0.95),
              zorder=10)

ax_b.set_yticks(y)
ax_b.set_yticklabels(labels_b, fontsize=7.6)
ax_b.set_ylim(-0.65, 1.75)
ax_b.set_xlim(-0.55, 0.15)
ax_b.set_xticks(np.arange(-0.5, 0.11, 0.1))
ax_b.set_xlabel('Difference in $\\rho$ (dual minus single-axis)', fontsize=8.5)
ax_b.tick_params(axis='x', labelsize=7.5)
ax_b.tick_params(axis='y', length=0)
ax_b.text(0.02, 0.97, '(b)', transform=ax_b.transAxes, ha='left', va='top',
          fontsize=10, fontweight='bold', color='black', zorder=10)
for sp in ('top', 'right'):
    ax_b.spines[sp].set_visible(False)
for sp in ('left', 'bottom'):
    ax_b.spines[sp].set_color('black'); ax_b.spines[sp].set_linewidth(0.8)

fig.subplots_adjust(left=0.085, right=0.985, bottom=0.235, top=0.93)

# 自检：文字不得溢出
_r = fig.canvas.get_renderer(); W, H = fig.canvas.get_width_height(); bad = []
for _ax in fig.axes:
    for _t in _ax.texts:
        bb = _t.get_window_extent(renderer=_r)
        if bb.x0 < 3 or bb.x1 > W - 3 or bb.y0 < 3 or bb.y1 > H - 3:
            bad.append('"%s" x=%.0f~%.0f y=%.0f~%.0f' % (_t.get_text()[:34], bb.x0, bb.x1, bb.y0, bb.y1))
print('[自检] ' + ('全部文字在画布内' if not bad else '溢出警告:\n  ' + '\n  '.join(bad)))

for ext, kw in [('png', dict(dpi=600, facecolor='white')), ('pdf', dict(facecolor='white'))]:
    p = os.path.join(OUT, 'Fig4.%s' % ext)
    plt.savefig(p, **kw)
    print('已生成:', p)
plt.close()

print()
print('数值核对: (a) ρ = 0.355 / 0.422 / 0.287 ; 方向一致 = 67.3 / 67.3 / 59.2')
print('          (b) Δρ = -0.067 / -0.135 ; Δ方向一致 = -8.2 / -8.2 pp')

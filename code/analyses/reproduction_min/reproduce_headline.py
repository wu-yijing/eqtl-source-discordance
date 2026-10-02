#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 reproduction_min — the values any reader can verify in five minutes
================================================================================

This is the **only** reproduction script in the archive that needs nothing but
`data/derived/`. No `.docx`, no model database, no session directory, no network,
no argument. It reproduces:

  · the headline result        primary arm 66/96 = 68.75%, Spearman rho = 0.38964
  · its per-phenotype split    DR 23/32, DN 21/32, DPN 22/32
  · the tissue-only arm        n = 138, k = 91, 65.9%, rho = +0.4138
  · the three SCZ arms         k 5,584 / 5,551 / 5,506; rho +0.4690 / +0.4199 / +0.4465

and it quantifies the one convention the three-arm comparison depends on: exact
zeros in the `multiZ` column (see the note printed at the end).

Inputs, all inside this repository:
  data/derived/primary_arm_96pairs.csv    96 rows
  data/derived/gtex_Z.csv                 222 rows
  data/derived/scz_z_4arm.csv             15,875 rows

Usage
-----
    python code/analyses/reproduction_min/reproduce_headline.py
    python code/analyses/reproduction_min/reproduce_headline.py --repo-root <dir>

Requires only numpy. Spearman is computed as Pearson on average ranks, so that
scipy is not needed and the arithmetic is visible.

Expected output is tabulated in README.md beside this file. The script exits
non-zero if any of the four archived values fails to reproduce.
================================================================================
"""
import argparse
import csv
import math
import os
import sys

import numpy as np

# --------------------------------------------------------------- locate the data
def repo_root(start=None):
    here = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    p = here
    while True:
        if os.path.isdir(os.path.join(p, 'data', 'derived')):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            raise SystemExit('cannot find data/derived/ above %s — pass --repo-root' % here)
        p = parent


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def fnum(x):
    x = (x or '').strip()
    return None if x in ('', 'NA', 'NaN', 'nan') else float(x)


def vsign(a, b):
    """Fraction of pairs whose signs agree; a zero sign counts as disagreement."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    return float(np.mean(np.sign(a) == np.sign(b)))


def avgrank(x):
    """Average (fractional) ranks, ties shared — what Spearman needs."""
    x = np.asarray(x, float)
    order = np.argsort(x, kind='mergesort')
    ranks = np.empty(len(x), float)
    ranks[order] = np.arange(1, len(x) + 1, dtype=float)
    # average the ranks of equal values
    sx = x[order]
    i = 0
    while i < len(sx):
        j = i
        while j + 1 < len(sx) and sx[j + 1] == sx[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return ranks


def spearman(a, b):
    ra, rb = avgrank(a), avgrank(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    return float(ra @ rb / math.sqrt((ra @ ra) * (rb @ rb)))


EXPECT = []          # (label, got, want, tol) — every check the audit's table makes
def check(label, got, want, tol=5e-5):
    ok = abs(got - want) <= tol
    EXPECT.append((label, got, want, ok))
    print('  %-34s %12s   archived %-12s %s'
          % (label, ('%.5f' % got).rstrip('0').rstrip('.'), want, 'ok' if ok else 'MISMATCH'))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument('--repo-root', default=None, metavar='DIR')
    args = ap.parse_args()
    D = os.path.join(repo_root(args.repo_root), 'data', 'derived')

    # ------------------------------------------------- 1. headline (primary arm)
    print('1. Primary arm — data/derived/primary_arm_96pairs.csv')
    P = read_rows(os.path.join(D, 'primary_arm_96pairs.csv'))
    zg = np.array([float(r['Z_GTEx']) for r in P])
    ze = np.array([float(r['Z_eQTLGen']) for r in P])
    same = np.sign(zg) == np.sign(ze)
    check('direction consistency k/%d' % len(P), int(same.sum()) / len(P) * 100, 68.75)
    check('Spearman rho', spearman(zg, ze), 0.38964)
    for trait, want in (('DR', 23), ('DN', 21), ('DPN', 22)):
        s = np.array([r['Trait'] == trait for r in P])
        k = int(same[s].sum())
        check('  %s k/32' % trait, k / 32 * 100, want / 32 * 100)
    print()

    # ------------------------------------------------- 2. tissue-only arm (GTEx)
    print('2. Tissue-only arm — data/derived/gtex_Z.csv (Whole_Blood vs Nerve_Tibial)')
    G = read_rows(os.path.join(D, 'gtex_Z.csv'))
    x, y = [], []
    for r in G:
        a, b = fnum(r['Z_Whole_Blood']), fnum(r['Z_Nerve_Tibial'])
        if a is not None and b is not None:
            x.append(a); y.append(b)
    check('tissue-only n', len(x), 138, 0)
    check('tissue-only k/n %', vsign(x, y) * 100, 65.9, 0.05)
    check('tissue-only rho', spearman(x, y), 0.4138)
    print()

    # ------------------------------------------------- 3. SCZ three arms
    print('3. SCZ three arms — data/derived/scz_z_4arm.csv (complete case)')
    S = read_rows(os.path.join(D, 'scz_z_4arm.csv'))
    cols = ('eqZ', 'wbZ', 'ntZ', 'multiZ')
    V = {c: np.array([np.nan if fnum(r[c]) is None else fnum(r[c]) for r in S], float) for c in cols}
    cc = ~np.isnan(V['eqZ']) & ~np.isnan(V['wbZ']) & ~np.isnan(V['ntZ'])
    eq, wb, nt, mu = V['eqZ'][cc], V['wbZ'][cc], V['ntZ'][cc], V['multiZ'][cc]
    check('complete-case n', int(cc.sum()), 8315, 0)
    for label, a, b, wk, wr in (('panel-only (eQTLGen vs WB)', eq, wb, 5584, 0.4690),
                                ('tissue-only (WB vs NT)',   wb, nt, 5551, 0.4199),
                                ('dual (eQTLGen vs multiZ)', eq, mu, 5506, 0.4465)):
        check('%s k' % label, vsign(a, b) * len(a), wk, 0.5)
        check('%s rho' % label, spearman(a, b), wr)
    print()

    # ------------------------------------------------- 4. the zero-value convention
    print('4. The convention this depends on — exact zeros, complete case only')
    z = {c: int(np.sum(V[c][cc] == 0.0)) for c in cols}
    print('     exact zeros: multiZ=%d  wbZ=%d  ntZ=%d  eqZ=%d' % (z['multiZ'], z['wbZ'], z['ntZ'], z['eqZ']))
    strict = [(int(np.sum(np.sign(a) == np.sign(b))),
               int(np.sum((a > 0) == (b > 0))))
              for a, b in ((eq, wb), (wb, nt), (eq, mu))]
    for label, (ks, kp) in zip(('panel-only', 'tissue-only', 'dual'), strict):
        print('     %-12s np.sign k=%d   (Z>0) k=%d   delta %+d' % (label, ks, kp, kp - ks))
    print('     -> a zero is scored as DISAGREEMENT under np.sign, which is what the')
    print('        archived three-arm counts use. Treating zeros as positive moves the')
    print('        dual arm by +%d pairs (+%.2f pp). State the convention in the table note.'
          % (strict[2][1] - strict[2][0], (strict[2][1] - strict[2][0]) / int(cc.sum()) * 100))
    print()

    bad = [e for e in EXPECT if not e[3]]
    print('=' * 78)
    print('checks: %d   mismatches: %d' % (len(EXPECT), len(bad)))
    if bad:
        for label, got, want, _ in bad:
            print('   MISMATCH %s: got %.6f, archived %s' % (label, got, want))
        return 1
    print('all four archived values reproduce from data/derived/ alone.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

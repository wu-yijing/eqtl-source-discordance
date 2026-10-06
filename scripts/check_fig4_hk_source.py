#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_fig4_hk_source.py — the housekeeping panel of Figure 4 must come from the archive.

Why this exists
---------------
`unified_fig4.py`'s housekeeping panel used to be read out of the submitted Supporting
Information's Table S6, via a hardcoded Windows path. That made Figure 4 unbuildable
anywhere but one machine, and it was unnecessary: Table S6 IS
`data/derived/hk_official_Z.csv` — GAP-1 was closed on 2026-10-03 by shipping that layer.
On 2026-10-07 the two were compared directly and agree exactly: 30 genes, 72 tissue-trait
pairs, Spearman rho = +0.64. The script now reads the archive layer, and Figure 4 rebuilds
with no journal document at all — verified byte-identical on the producing machine.

That equivalence is the reason the figure is reproducible, so it is worth a check rather
than a comment: an edit to `hk_official_Z.csv` that changes the housekeeping panel would
otherwise show up only as "Figure 4 no longer matches", with the cause three steps away.

What it asserts
---------------
`data/derived/hk_official_Z.csv` yields exactly the panel Figure 4 plots: n = 72 pairs
(30 genes x 3 traits) and rho = +0.64 at two decimals.

The equivalence with the old SI route is not re-derived here, and deliberately so: the
figure's own hash is the better evidence. `reproduce.sh` rebuilds Figure 4 from this
archive layer alone and gets the submitted PNG byte for byte, on a machine where the
Supporting Information is not present at all. Re-extracting Table S6 to compare an
intermediate rho would be a weaker check than the one gate 14 already runs.

Exit 0 = the panel is still the one Figure 4 plots. Non-zero = it is not.

    python3 scripts/check_fig4_hk_source.py
"""
import csv
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSV_PATH = os.path.join(REPO, 'data', 'derived', 'hk_official_Z.csv')

TRAITS = ('DR', 'DN', 'DPN')
WANT_N = 72
WANT_RHO_2DP = 0.64

MISSING = {'', 'NA', 'NaN', '\u2014', '\u2013', '-', 'n/a'}


def val(s):
    s = (s or '').strip()
    return np.nan if s in MISSING else float(s)


def rho_from_archive():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8-sig')))
    nt, wb = [], []
    for r in rows:
        for k in TRAITS:
            nt.append(val(r.get('Z_NerveTibial_' + k)))
            wb.append(val(r.get('Z_WholeBlood_' + k)))
    nt, wb = np.array(nt), np.array(wb)
    m = ~(np.isnan(nt) | np.isnan(wb))
    return len(rows), int(m.sum()), stats.spearmanr(wb[m], nt[m]).statistic


def main():
    fails = 0
    if not os.path.isfile(CSV_PATH):
        print('  [FAIL] missing %s' % os.path.relpath(CSV_PATH, REPO))
        return 1

    genes, n, rho = rho_from_archive()
    print('  archive layer : data/derived/hk_official_Z.csv')
    print('                  %d genes, n=%d pairs, rho=%+.4f  -> %+.2f'
          % (genes, n, rho, rho))
    if n == WANT_N:
        print('  [ ok ] pair count matches Figure 4 (n=%d)' % WANT_N)
    else:
        print('  [FAIL] n=%d, Figure 4 plots n=%d' % (n, WANT_N))
        fails += 1
    if round(rho, 2) == WANT_RHO_2DP:
        print('  [ ok ] rho matches Figure 4 (+%.2f)' % WANT_RHO_2DP)
    else:
        print('  [FAIL] rho=%+.4f -> %+.2f, Figure 4 plots %+.2f'
              % (rho, round(rho, 2), WANT_RHO_2DP))
        fails += 1

    print()
    if fails:
        print(' RESULT: %d check(s) failed — Figure 4\'s housekeeping panel is no longer '
              'the one the archive recorded.' % fails)
        return 1
    print(' RESULT: Figure 4\'s housekeeping panel still comes from the archive layer.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

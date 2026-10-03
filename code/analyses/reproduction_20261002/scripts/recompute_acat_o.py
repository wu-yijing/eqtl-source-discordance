# -*- coding: utf-8 -*-
"""
================================================================================
 SI Table S6, column "ACAT-O combined P" — the combination rule, re-derived
================================================================================
Input (ships with this repository):
  data/derived/hk_official_Z.csv
        The corrected housekeeping layer: 30 genes x 2 GTEx tissues
        (Nerve_Tibial, Whole_Blood) x 3 phenotypes (DR, DN, DPN). The Z columns
        are the official MetaXcan v0.8.1 S-PrediXcan z-scores; the ACAT-O columns
        are derived below from those z-scores and nothing else.

The rule (established 2026-10-03, after an earlier attempt at the unweighted
Cauchy combination reproduced only 68 of 87 cells):

    p_ACAT-O = 0.5 - arctan( SUM_t  w_t * tan((0.5 - p_t) * pi)
                             / SUM_t w_t ) / pi
    w_t = sqrt(N_t),  N_t = GTEx v8 eQTL sample size of tissue t
    N(Nerve_Tibial) = 532,  N(Whole_Blood) = 670
    p_t = 2 * Phi(-|Z_t|)
    component p-values clipped to [1e-15, 1 - 1e-15]; result clipped to [1e-300, 1]

The combination is therefore **sqrt(N)-weighted**, not a plain average of the
tissue tan-terms. The same weighting governs the Z_multi_tissue column of
SI Table S3 (Stouffer, sqrt(N)), which was verified on that table first.

Verification. This script reproduces all 87 published values of the S6
"ACAT-O combined P" column; the Supporting Information prints that column at
three significant figures (`%.3g`), and every one of the 87 matches
character-for-character at that precision. The same rule also reproduces the
138 published P_ACAT_O values of SI Table S3 from full-precision official
z-scores (that check needs z-scores to more than the 4 decimals that
`data/derived/gtex_Z.csv` stores, so it is recorded here rather than run).

Exit code 0 = the column reproduces. Non-zero = it does not.
================================================================================
"""
# ---------------------------------------------------------------------------
# Path resolution (same bootstrap every runnable script in this package uses).
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

import csv
import os
import math
import sys
import numpy as np
from scipy.stats import norm

GTEX_N = {'Nerve_Tibial': 532, 'Whole_Blood': 670}
TIS = ('Nerve_Tibial', 'Whole_Blood')
PH = ('DR', 'DN', 'DPN')
COL = {('Nerve_Tibial', 'DR'): 'Z_NerveTibial_DR', ('Nerve_Tibial', 'DN'): 'Z_NerveTibial_DN',
       ('Nerve_Tibial', 'DPN'): 'Z_NerveTibial_DPN', ('Whole_Blood', 'DR'): 'Z_WholeBlood_DR',
       ('Whole_Blood', 'DN'): 'Z_WholeBlood_DN', ('Whole_Blood', 'DPN'): 'Z_WholeBlood_DPN'}

# The 87 published values, transcribed from SI Table S6 (three significant figures).
PUBLISHED_S6_ACAT_O = {
    'ANKRD40': {'DR': '0.598', 'DN': '0.718', 'DPN': '0.376'},
    'AP3M1': {'DR': '0.449', 'DN': '0.696', 'DPN': '0.788'},
    'ATG101': {'DR': '0.668', 'DN': '0.747', 'DPN': '0.604'},
    'CFDP1': {'DR': '0.62', 'DN': '0.946', 'DPN': '0.828'},
    'CUL1': {'DR': '0.191', 'DN': '0.93', 'DPN': '0.121'},
    'DCTN2': {'DR': '0.252', 'DN': '0.632', 'DPN': '0.0597'},
    'DNAJC4': {'DR': '0.233', 'DN': '0.477', 'DPN': '0.638'},
    'E2F4': {'DR': '0.96', 'DN': '0.755', 'DPN': '0.703'},
    'FIBP': {'DR': '0.531', 'DN': '0.253', 'DPN': '0.627'},
    'GOLGA3': {'DR': '0.0133', 'DN': '0.217', 'DPN': '0.695'},
    'KDM4B': {'DR': '0.451', 'DN': '0.432', 'DPN': '0.232'},
    'LSM12': {'DR': '0.0206', 'DN': '0.36', 'DPN': '0.0953'},
    'MAPK1IP1L': {'DR': '0.867', 'DN': '0.295', 'DPN': '0.295'},
    'MCMBP': {'DR': '0.473', 'DN': '0.24', 'DPN': '0.2'},
    'PSMC1': {'DR': '0.28', 'DN': '0.378', 'DPN': '0.45'},
    'RABGGTB': {'DR': '0.824', 'DN': '0.67', 'DPN': '0.845'},
    'RBX1': {'DR': '0.952', 'DN': '0.0786', 'DPN': '0.486'},
    'RNF181': {'DR': '0.786', 'DN': '0.746', 'DPN': '0.646'},
    'RNPS1': {'DR': '0.931', 'DN': '0.784', 'DPN': '0.785'},
    'SDF4': {'DR': '0.872', 'DN': '0.697', 'DPN': '0.0547'},
    'SDHAF2': {'DR': '0.0144', 'DN': '0.65', 'DPN': '0.404'},
    'SEC13': {'DR': '0.911', 'DN': '0.873', 'DPN': '0.0406'},
    'SF3B4': {'DR': '0.608', 'DN': '0.919', 'DPN': '0.0572'},
    'SPRYD3': {'DR': '0.0374', 'DN': '0.635', 'DPN': '0.764'},
    'SRM': {'DR': '0.354', 'DN': '0.911', 'DPN': '0.932'},
    'STX4': {'DR': '0.265', 'DN': '0.348', 'DPN': '0.793'},
    'TOMM20': {'DR': '0.32', 'DN': '0.62', 'DPN': '0.354'},
    'TRIP12': {'DR': '0.959', 'DN': '0.853', 'DPN': '0.882'},
    'TUT1': {'DR': '—', 'DN': '—', 'DPN': '—'},
    'U2AF2': {'DR': '0.3', 'DN': '0.551', 'DPN': '0.745'},
}

def z2p(z):
    return 2 * norm.sf(abs(z))

def acat_o(ps, ws):
    """sqrt(N)-weighted Cauchy combination (ACAT-O), stable for extreme p."""
    p = np.clip(np.asarray(ps, float), 1e-15, 1 - 1e-15)
    w = np.asarray(ws, float)
    w = w / w.sum()
    t = float(np.sum(w * np.tan((0.5 - p) * np.pi)))
    return float(np.clip(0.5 - np.arctan(t) / np.pi, 1e-300, 1.0))

def main():
    src = os.path.join(PC.DERIVED, 'hk_official_Z.csv')
    rows = list(csv.DictReader(open(src, encoding='utf-8')))
    out_dir = PC.RESULTS
    os.makedirs(out_dir, exist_ok=True)
    rec = []
    n_cmp = 0
    bad = []
    for r in rows:
        gene = r['Gene']
        for ph in PH:
            pv, ws = [], []
            for t in TIS:
                v = r.get(COL[(t, ph)], '')
                if v not in ('', None):
                    pv.append(z2p(float(v)))
                    ws.append(GTEX_N[t] ** 0.5)
            if not pv:
                continue
            p = acat_o(pv, ws)
            rec.append((gene, ph, '%.12g' % p, '%.3g' % p))
            pub = PUBLISHED_S6_ACAT_O.get(gene, {}).get(ph, '')
            if pub:
                n_cmp += 1
                if '%.3g' % p != pub:
                    bad.append((gene, ph, pub, '%.3g' % p))
    dst = os.path.join(out_dir, 'hk_acat_o.csv')
    with open(dst, 'w', newline='', encoding='utf-8') as f:
        f.write('Gene,Phenotype,ACAT_O,ACAT_O_3sf\n')
        for g, ph, full, sf in rec:
            f.write('%s,%s,%s,%s\n' % (g, ph, full, sf))
    print('[acat-o] input  : %s' % src)
    print('[acat-o] written: %s (%d rows)' % (dst, len(rec)))
    print('[acat-o] rule   : sqrt(N)-weighted Cauchy, N = %s' % GTEX_N)
    print('[acat-o] SI S6 "ACAT-O combined P" reproduced: %d/%d at three significant figures'
          % (n_cmp - len(bad), n_cmp))
    for b in bad[:20]:
        print('    MISMATCH %s/%s published %s recomputed %s' % b)
    return 0 if not bad and n_cmp == 87 else 1

if __name__ == '__main__':
    sys.exit(main())

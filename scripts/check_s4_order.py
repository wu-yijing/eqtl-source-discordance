#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_s4_order.py — make SI Table S4's candidate processing order explicit and checked.

The problem this closes
-----------------------
SI Table S4 reproduces 30/30 only when the 30 candidates are processed in one particular
order, and that order was never an artefact: it existed only as the row order of
`data/derived/mahalanobis_matched_pairs.csv`. A reader could therefore reproduce the
*numbers* without ever being able to name the *specification* they had just used, and the
archive could not say whether a re-run used the submitted order or another one.

So the order is now a file (`data/derived/s4_candidate_order.txt`) and this script checks
it. It is deliberately a checker, not a matcher: it does not re-run MatchIt (that is
`emit_S4_table.R`'s job, and gate 12 of verify_from_clone.sh runs it). It verifies that
the shipped order and the shipped matched table agree, and it re-states — from the data,
not from prose — exactly how much of the order is derivable and how much is carried.

What it asserts
---------------
1. the order file exists, holds 30 unique gene symbols, and every one is a candidate;
2. that sequence equals the candidate rows of `mahalanobis_matched_pairs.csv`
   (`treated == 1`) in file order;
3. the `PullDown_Unused` sequence is non-increasing over the order — the stated
   convention — and the tie at the tail is measured and reported, not assumed;
4. positions 1..k (the non-zero-score block) are exactly the candidates sorted by
   `PullDown_Unused` descending, so the derivable part really is derivable.

Exit 0 = every check passed. Non-zero = the order file and the matched table disagree,
which would mean Table S4 is no longer specified by anything in this archive.

    python3 scripts/check_s4_order.py           # check
    python3 scripts/check_s4_order.py --print   # also print the order with its scores
"""
import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ORDER = os.path.join(REPO, 'data', 'derived', 's4_candidate_order.txt')
PAIRS = os.path.join(REPO, 'data', 'derived', 'mahalanobis_matched_pairs.csv')
COVAR = os.path.join(REPO, 'data', 'derived', 'covariate_matrix.csv')

FAILS = []


def ok(msg):
    print('  [ ok ] %s' % msg)


def bad(msg):
    print('  [FAIL] %s' % msg)
    FAILS.append(msg)


def read_order(path):
    out = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            s = line.strip()
            if s and not s.startswith('#'):
                out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument('--print', dest='do_print', action='store_true',
                    help='print the order with each gene\'s PullDown_Unused score')
    args = ap.parse_args()

    for p in (ORDER, PAIRS, COVAR):
        if not os.path.isfile(p):
            bad('missing required input: %s' % os.path.relpath(p, REPO))
            return 1

    order = read_order(ORDER)
    pairs = list(csv.DictReader(open(PAIRS, encoding='utf-8')))
    covar = {r['Gene']: r for r in csv.DictReader(open(COVAR, encoding='utf-8'))}

    # 1. shape -----------------------------------------------------------------
    if len(order) != 30:
        bad('order file has %d genes, expected 30' % len(order))
    else:
        ok('order file: 30 genes')
    if len(set(order)) != len(order):
        bad('order file contains duplicate genes')
    else:
        ok('order file: no duplicates')
    not_cand = [g for g in order
                if covar.get(g, {}).get('Group', '') != '30 HOTAIR Candidate']
    if not_cand:
        bad('not candidates: %s' % ', '.join(not_cand))
    else:
        ok('order file: every gene is a 30_HOTAIR_Candidate')

    # 2. agreement with the shipped matched table ------------------------------
    from_pairs = [r['Gene'] for r in pairs if str(r['treated']).strip() == '1']
    if order == from_pairs:
        ok('order file == candidate rows of mahalanobis_matched_pairs.csv (30/30)')
    else:
        bad('order file disagrees with mahalanobis_matched_pairs.csv')
        for i, (a, b) in enumerate(zip(order, from_pairs)):
            if a != b:
                bad('  first disagreement at position %d: order=%s, table=%s'
                    % (i + 1, a, b))
                break

    # 3. the stated convention, and the size of the tie ------------------------
    def score(g):
        v = covar.get(g, {}).get('PullDown_Unused', '')
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    scores = [score(g) for g in order]
    if any(s is None for s in scores):
        bad('a gene has no PullDown_Unused score: %s'
            % ', '.join(g for g, s in zip(order, scores) if s is None))
        return report()
    mono = all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
    if mono:
        ok('PullDown_Unused is non-increasing over the order (the stated convention)')
    else:
        bad('PullDown_Unused is NOT non-increasing over the order')

    tail = scores[-1]
    tie = sum(1 for s in scores if abs(s - tail) < 1e-12)
    print('  [info] %d of 30 candidates tie at PullDown_Unused = %g; positions %d-%d '
          'are not derivable from any shipped key' % (tie, tail, 30 - tie + 1, 30))

    # 4. the derivable block really is derivable -------------------------------
    nonzero = [(g, score(g)) for g in order if abs(score(g) - tail) >= 1e-12]
    by_score = [g for g, _ in sorted(nonzero, key=lambda t: -t[1])]
    if by_score == [g for g, _ in nonzero]:
        ok('positions 1-%d are exactly the non-zero-score candidates sorted descending'
           % len(nonzero))
    else:
        bad('the non-zero-score block is not sorted by PullDown_Unused descending')

    if args.do_print:
        print()
        print('  %-4s %-12s %s' % ('pos', 'gene', 'PullDown_Unused'))
        for i, (g, s) in enumerate(zip(order, scores)):
            print('  %-4d %-12s %g' % (i + 1, g, s))
        print()

    return report()


def report():
    print()
    if FAILS:
        print('  RESULT: %d check(s) failed — SI Table S4 is no longer specified by an '
              'artefact in this archive.' % len(FAILS))
        return 1
    print('  RESULT: the candidate order is explicit, agrees with the matched table, and '
          'its derivable part is derivable.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

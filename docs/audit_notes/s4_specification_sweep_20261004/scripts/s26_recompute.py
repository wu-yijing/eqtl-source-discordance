#!/usr/bin/env python
"""s26_recompute.py -- recompute Supporting Information Table S26 from the archive.

Table S26 (Mahalanobis-matched enrichment contrasts) is the downstream consumer of
Table S4: its denominators are the testable candidate and matched-control pairs.
This script rebuilds it from the three inputs ARCHIVE_MAP names for that row --

    data/superseded/mahalanobis_matched_pairs.csv   (or data/derived/..., see --pairs)
    data/derived/gtex_Z.csv
    data/derived/eqtlgen_Z.csv

-- and prints the published values beside the recomputed ones.

WHY THIS EXISTS
---------------
ARCHIVE_MAP.md moved S26 to the red mark on the reasoning that "the matched-control
denominators 60 and 57 cannot be derived from the 30 archived pairs" and that the
producing script is not shipped. The second half is true. The first half is not: the
denominators fall out of the Z layers the row itself lists -- 60 is the number of
(archived control gene x {DR, DN, DPN}) cells that carry a GTEx endpoint, 57 the
same for eQTLGen, 84 and 81 the candidate-arm equivalents -- and with them the table
reproduces on all four contrasts, Fisher p-values included. So this is a join that
was not written down, not a construction that was never captured.

Fisher's exact test is implemented here from math.comb (two-sided, the sum of tables
no more likely than the observed one); scipy is not required.

Usage:  python scripts/s26_recompute.py <repo-root>
                                    [--pairs <csv>] [--pairs2 <csv>]
"""
import argparse
import csv
import math
import os

TRAITS = ("DR", "DN", "DPN")
ARMS = [("GTEx v8 multi-tissue ACAT-O", "BH q < 0.05", "gtex", "FDR_q_ACAT_O", 0.05),
        ("GTEx v8 multi-tissue ACAT-O", "nominal p < 0.05", "gtex", "P_ACAT_O", 0.05),
        ("eQTLGen whole blood", "BH q < 0.05", "eq", "BH_q", 0.05),
        ("eQTLGen whole blood", "nominal p < 0.05", "eq", "P", 0.05)]
PUBLISHED = {("GTEx v8 multi-tissue ACAT-O", "BH q < 0.05"): ("2/84", "1/60", 1.00, (0.417, 1.000, 1.000)),
             ("GTEx v8 multi-tissue ACAT-O", "nominal p < 0.05"): ("8/84", "7/60", 0.78, (0.636, 0.385, 0.636)),
             ("eQTLGen whole blood", "BH q < 0.05"): ("5/81", "0/57", 0.077, (0.504, 1.000, 0.504)),
             ("eQTLGen whole blood", "nominal p < 0.05"): ("8/81", "4/57", 0.76, (0.632, 1.000, 0.632))}


def fisher_two_sided(a, b, c, d):
    n, r1, r2, c1 = a + b + c + d, a + b, c + d, a + c

    def prob(x):
        return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)

    obs = prob(a)
    return min(1.0, sum(prob(x) for x in range(max(0, c1 - r2), min(r1, c1) + 1)
                        if prob(x) <= obs + 1e-12))


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def pairs_of(path):
    rows = load(path)
    return ([r["Gene"] for r in rows if str(r["treated"]).strip() in ("1", 1)],
            [r["Gene"] for r in rows if str(r["treated"]).strip() in ("0", 0)])


def present(v):
    return str(v).strip() not in ("", "NA", "nan", "None", "+nan")


def count(genes, tab, fld):
    pos = tot = 0
    per = {t: [0, 0] for t in TRAITS}
    for g in genes:
        for t in TRAITS:
            r = tab.get((g, t))
            if r is None or not present(r.get(fld, "")):
                continue
            tot += 1
            per[t][1] += 1
            try:
                v = float(str(r[fld]).replace("+", ""))
            except ValueError:
                continue
            if v < 0.05:
                pos += 1
                per[t][0] += 1
    return pos, tot, per


def run(label, cand, ctrl, tabs):
    print(f"\n================ {label} ================")
    print(f"candidates={len(cand)}  matched controls={len(ctrl)}")
    hdr = f"{'weight source':<30} {'endpoint':<17} {'candidate':<14} {'matched-control':<16} {'Fisher P':<9} per-phenotype (DR / DN / DPN)"
    print(hdr)
    n_match = 0
    for src, ep, key, fld, _ in ARMS:
        cp, ct, cper = count(cand, tabs[key], fld)
        kp, kt, kper = count(ctrl, tabs[key], fld)
        p = fisher_two_sided(cp, ct - cp, kp, kt - kp)
        per = [fisher_two_sided(cper[t][0], cper[t][1] - cper[t][0],
                                kper[t][0], kper[t][1] - kper[t][0]) for t in TRAITS]
        pc, pk, pp, pper = PUBLISHED[(src, ep)]
        same = f"{cp}/{ct}" == pc and f"{kp}/{kt}" == pk
        n_match += same
        print(f"{src:<30} {ep:<17} {f'{cp}/{ct}':<14} {f'{kp}/{kt}':<16} {p:<9.3f} "
              + " / ".join(f"{x:.3f}" for x in per))
        print(f"{'':<30} published      {pc:<14} {pk:<16} {pp:<9} "
              + " / ".join(f"{x:.3f}" for x in pper) + ("   == MATCH" if same else "   != DIFFERS"))
    print(f"contrasts reproduced exactly: {n_match} / {len(ARMS)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--pairs", default=None)
    ap.add_argument("--pairs2", default=None)
    a = ap.parse_args()
    pairs1 = a.pairs or os.path.join(a.repo, "data/superseded/mahalanobis_matched_pairs.csv")
    pairs2 = a.pairs2 or os.path.join(a.repo, "data/derived/mahalanobis_matched_pairs.csv")
    tabs = {"gtex": {(r["Gene"], r["Trait"]): r for r in load(os.path.join(a.repo, "data/derived/gtex_Z.csv"))},
            "eq": {(r["Gene"], r["Trait"]): r for r in load(os.path.join(a.repo, "data/derived/eqtlgen_Z.csv"))}}
    c1, k1 = pairs_of(pairs1)
    run(f"A. submitted S4 pairing ({os.path.relpath(pairs1, a.repo)})", c1, k1, tabs)
    if os.path.exists(pairs2):
        c2, k2 = pairs_of(pairs2)
        if set(k2) == set(k1):
            print("\n[note] the two pairings select the SAME 30 controls, so every")
            print("       denominator and every contrast is identical by construction.")
        run(f"B. re-emitted S4 pairing ({os.path.relpath(pairs2, a.repo)})", c2, k2, tabs)


if __name__ == "__main__":
    main()

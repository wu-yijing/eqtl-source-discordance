#!/usr/bin/env python
"""identify_reported_matching.py -- which matched set does the manuscript report?

Three matched candidate/control sets for the same 30 genes exist on disk, and the
manuscript does not name one. This identifies it by its numbers rather than by its
provenance prose: the Genetic Epidemiology manuscript states the GTEx arm of the
covariate-matched contrast as

    "Covariate-matched enrichment (Table S26) showed no candidate-over-control
     difference in the GTEx arm after matching on gene length, GC content and eQTL
     SNP count (2.4% versus 1.7%; P = 1.00)"

(the sentence is in the manuscript, which is not distributed here; the three
percentages are public in Supporting Information Table S26). Recompute Table S26's
contingency under each candidate control set and the sentence picks one out.

Usage:  python scripts/identify_reported_matching.py <repo-root>
"""
import csv
import math
import os
import sys

TRAITS = ("DR", "DN", "DPN")
ARMS = [("GTEx v8 multi-tissue ACAT-O", "FDR_q_ACAT_O", "gtex"),
        ("eQTLGen whole blood", "BH_q", "eq")]
# what the manuscript reports, for the GTEx arm
REPORTED_GTE_X = (2.4, 1.7, 1.00)


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = [ln for ln in fh if not ln.startswith("#")]
    return list(csv.DictReader(rows))


def read_pairs(path):
    rows = load(path)
    if "Control_Gene" in rows[0]:                       # wide layout (2026-06-29)
        return ([r["Candidate_Gene"] for r in rows], [r["Control_Gene"] for r in rows])
    if "treated" in rows[0]:                            # long layout with a flag
        cand = [r["Gene"] for r in rows if str(r["treated"]).strip() == "1"]
        ctrl = [r["Gene"] for r in rows if str(r["treated"]).strip() == "0"]
        return cand, ctrl
    # long layout carrying only a group label (2026-06-25). The label of the control arm
    # there is a leftover name from the study's earlier design — "30_T2DM_Control_Matched"
    # — for controls drawn from the 54 non-candidates, so it is matched on the candidate
    # label rather than on the control label.
    cand = [r["Gene"] for r in rows if "HOTAIR" in r["Group"]]
    ctrl = [r["Gene"] for r in rows if "HOTAIR" not in r["Group"]]
    return cand, ctrl


def fisher(a, b, c, d):
    n, r1, r2, c1 = a + b + c + d, a + b, c + d, a + c

    def pr(x):
        return math.comb(r1, x) * math.comb(r2, c1 - x) / math.comb(n, c1)

    obs = pr(a)
    return min(1.0, sum(pr(x) for x in range(max(0, c1 - r2), min(r1, c1) + 1)
                        if pr(x) <= obs + 1e-12))


def arm(genes, tab, fld):
    pos = tot = 0
    for g in genes:
        for t in TRAITS:
            r = tab.get((g, t))
            if r is None or str(r.get(fld, "")).strip() in ("", "NA", "nan", "None"):
                continue
            tot += 1
            try:
                v = float(str(r[fld]).replace("+", ""))
            except ValueError:
                continue
            if v < 0.05:
                pos += 1
    return pos, tot


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    here = os.path.dirname(os.path.abspath(__file__))
    res = os.path.join(here, "..", "results")

    tabs = {"gtex": {(r["Gene"], r["Trait"]): r for r in load(os.path.join(repo, "data/derived/gtex_Z.csv"))},
            "eq": {(r["Gene"], r["Trait"]): r for r in load(os.path.join(repo, "data/derived/eqtlgen_Z.csv"))}}

    sets = [("A  archived / shipped as SI Table S4",
             os.path.join(repo, "data/superseded/mahalanobis_matched_pairs.csv")),
            ("B  2026-06-25 run, 54-gene pool",
             os.path.join(res, "matched_set_20260625_pool54.csv")),
            ("C  2026-06-29 run, genome-scale pool",
             os.path.join(res, "matched_set_20260629_genomescale.csv"))]

    print("The manuscript reports, for the GTEx arm: %.1f%% vs %.1f%%, P = %.2f"
          % REPORTED_GTE_X)
    print()
    verdict = None
    for label, path in sets:
        cand, ctrl = read_pairs(path)
        print(f"== {label}")
        print(f"   source: {os.path.relpath(path, os.path.join(here, '..', '..', '..'))}")
        print(f"   candidates {len(cand)} | controls {len(ctrl)} | shared with A: "
              f"{len(set(ctrl) & set(read_pairs(sets[0][1])[1]))}/30")
        row = {}
        for src, fld, key in ARMS:
            cp, ct = arm(cand, tabs[key], fld)
            kp, kt = arm(ctrl, tabs[key], fld)
            if not ct or not kt:
                print(f"   {src:<30} no testable pairs at all "
                      f"(cand {cp}/{ct}, ctrl {kp}/{kt}) -- cannot produce the sentence")
                row[src] = None
                continue
            p = fisher(cp, ct - cp, kp, kt - kp)
            print(f"   {src:<30} cand {cp}/{ct} = {100*cp/ct:4.1f}%  "
                  f"ctrl {kp}/{kt} = {100*kp/kt:4.1f}%  P = {p:.2f}")
            row[src] = (round(100 * cp / ct, 1), round(100 * kp / kt, 1), round(p, 2))
        g = row.get("GTEx v8 multi-tissue ACAT-O")
        if g and g == REPORTED_GTE_X:
            verdict = label
        print()
    print("VERDICT:", (f"the manuscript's numbers are {verdict}'s" if verdict
                       else "no candidate set reproduces the reported numbers"))
    print("         (the other sets either give a different percentage/p-value, or have "
          "no GTEx endpoint at all)")


if __name__ == "__main__":
    main()

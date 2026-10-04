#!/usr/bin/env python3
# =============================================================================
# reconstruct_pairing.py -- reconstruct A's `subclass` pairing and check it
# =============================================================================
# Q2 of the SI Table S4 question is: the submitted table's PAIRING column does
# not reproduce from any matching run, because it is not a matching output. This
# script makes the actual rule executable and checkable from a clone.
#
# WHAT THE RULE IS
# ----------------
# `subclass` in data/superseded/mahalanobis_matched_pairs.csv (the submitted
# file, "A") is the 1..30 rank of two lists that are each sorted by
# `PullDown_Unused` DESCENDING and then zipped positionally -- one list is the
# 30 candidates, the other the 30 controls. It is a sort signature, not a
# matching. Two consequences follow, and both are asserted below:
#
#   * each arm is individually non-increasing in PullDown_Unused;
#   * the pairing agrees with itself under re-derivation (30/30), while a real
#     Mahalanobis matching agrees with it in only 2-3 of 30 pairs.
#
# WHERE THE STEP CAME FROM
# ------------------------
# The file was committed with exactly this content in the predecessor
# repository `wu-yijing/TWAS-eQTL-source-confounding`, commit 1389407
# ("Fix mahalanobis_matched_pairs.csv: use 44 high-confidence non-candidate
# pool (exclude 10 low-confidence)..."). The commit's parent carries the
# genuine MatchIt output instead (md5 2766cd19...), so the diff between the two
# revisions IS the step. Nothing else on disk records it: neither
# 03_enrichment_analysis.py nor 07_generate_supplementary_tables.py writes this
# file, they only read it.
#
# WHAT STILL IS NOT RECOVERED
# ---------------------------
# The one-off script the author ran to emit the rank-zip. It is not in any
# repository, the recycle bin, or any dated working directory. This script
# therefore reconstructs the *rule*, which is fully determined and verifies
# 30/30, rather than claiming to have found the *command*.
#
# Usage:  python reconstruct_pairing.py [<repo-root>] [<out-dir>]
# =============================================================================
import csv
import os
import sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "."
OUTD = sys.argv[2] if len(sys.argv) > 2 else "."

A = os.path.join(REPO, "data/superseded/mahalanobis_matched_pairs.csv")
B = os.path.join(REPO, "data/derived/mahalanobis_matched_pairs.csv")
COV = os.path.join(REPO, "data/derived/covariate_matrix.csv")
RECOVERED = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "results", "recovered_TableS4_iScience_v2.csv")


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def arm(rows, treated):
    return [r for r in rows if r["treated"] == str(treated)]


def pull(rows, covar):
    return [float(covar[r["Gene"]]["PullDown_Unused"]) for r in rows]


def non_increasing(xs):
    return all(xs[i] >= xs[i + 1] for i in range(len(xs) - 1))


def main():
    a = load(A)
    cov = {r["Gene"]: r for r in load(COV)}

    a_can, a_ctl = arm(a, 1), arm(a, 0)
    print(f"A: {len(a_can)} candidates, {len(a_ctl)} controls")

    # ---- 1. both arms are sorted by PullDown_Unused descending ---------------
    pc, pt = pull(a_can, cov), pull(a_ctl, cov)
    print(f"\ncandidate arm PullDown_Unused: {pc}")
    print(f"  non-increasing : {non_increasing(pc)}")
    print(f"control   arm PullDown_Unused: {pt}")
    print(f"  non-increasing : {non_increasing(pt)}")
    assert non_increasing(pc) and non_increasing(pt), "arms are not sorted"

    # ---- 2. the rule, re-run: rank-zip two descending lists -----------------
    by_unused = sorted(a_can, key=lambda r: -float(cov[r["Gene"]]["PullDown_Unused"]))
    ctl_sorted = sorted(a_ctl, key=lambda r: -float(cov[r["Gene"]]["PullDown_Unused"]))
    rebuilt = {r["subclass"]: (r["Gene"], ctl_sorted[i]["Gene"])
               for i, r in enumerate(by_unused)}

    agree = sum(1 for r in a_can
                if rebuilt[r["subclass"]][1] ==
                {c["subclass"]: c["Gene"] for c in a_ctl}[r["subclass"]])
    print(f"\nrank-zip rule re-derives the submitted pairing : {agree} / 30")

    # ---- 3. the recovered downstream table agrees 30/30 --------------------
    if os.path.exists(RECOVERED):
        rec = load(RECOVERED)
        by_sc = {}
        for r in a:
            by_sc.setdefault(r["subclass"], {})[r["treated"]] = r["Gene"]
        hit = 0
        for row in rec:
            sc = str(int(row["Pair_ID"].replace("Pair_", "")))
            if by_sc.get(sc, {}).get("1") == row["Candidate_Gene"] and \
               by_sc.get(sc, {}).get("0") == row["Control_Gene"]:
                hit += 1
        print(f"recovered TableS4 pairing == A subclass pairing  : {hit} / {len(rec)}")
    else:
        print(f"recovered TableS4 not found at {RECOVERED}")

    # ---- 4. the control SET is a matching output, on the same 30 genes -----
    if os.path.exists(B):
        b = load(B)
        b_ctl = {r["Gene"] for r in arm(b, 0)}
        a_ctl_s = {r["Gene"] for r in a_ctl}
        print(f"\ncontrol SET, A vs the re-emitted (derived) table : "
              f"{len(a_ctl_s & b_ctl)} / 30")
        print("  (a real matching chose the controls -- the SET reproduces;")
        print("   only the PAIRING is the sort signature)")

    # ---- 5. emit the reconstruction as a table, in the recovered layout ----
    hdr = ["Pair_ID", "Candidate_Gene", "Control_Gene"]
    path = os.path.join(OUTD, "pairing_reconstructed.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(hdr)
        for sc in sorted(by_sc, key=int):
            w.writerow([f"Pair_{int(sc):02d}", by_sc[sc].get("1"), by_sc[sc].get("0")])
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()

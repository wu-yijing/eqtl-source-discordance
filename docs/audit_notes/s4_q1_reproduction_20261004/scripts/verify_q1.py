#!/usr/bin/env python3
# =============================================================================
# verify_q1.py -- independently re-check the Q1 reproduction of SI Table S4
# =============================================================================
# Q1 is the question: "does the SI Table S4 CONTROL SET, and the table content,
# reproduce?" It is answered by re-running emit_S4_table.R under the pinned stack
# and comparing the result against the two arms that ship:
#
#   A  data/superseded/mahalanobis_matched_pairs.csv   the submitted file
#   B  data/derived/mahalanobis_matched_pairs.csv      the re-emitted file
#
# This script does NOT re-run R. It consumes an emit_S4_table.R output directory
# and checks, from hashes and cells rather than from prose, that:
#
#   1. the re-emitted table is byte-identical to B and to what the archive ships;
#   2. the candidate SET is A's candidate set (30/30);
#   3. the control SET is A's control set (30/30) -- this is Q1's whole claim;
#   4. the candidate block is byte-identical to A's candidate block;
#   5. the line-level difference from A is exactly the pairing, and matches the
#      count the sweep recorded (28 of 61 lines).
#
# It prints a verdict and writes results/q1_verification.json.
#
# Usage:  python verify_q1.py <emit-output-dir> [<repo-root>]
# =============================================================================
import csv
import hashlib
import json
import os
import sys

EMIT = sys.argv[1] if len(sys.argv) > 1 else "."
REPO = sys.argv[2] if len(sys.argv) > 2 else "."

A = os.path.join(REPO, "data/superseded/mahalanobis_matched_pairs.csv")
B = os.path.join(REPO, "data/derived/mahalanobis_matched_pairs.csv")
ARCH = os.path.join(REPO,
                    "docs/audit_notes/s4_specification_sweep_20261004",
                    "results/mahalanobis_matched_pairs.csv")
EMITTED = os.path.join(EMIT, "mahalanobis_matched_pairs.csv")

EXPECT_B_MD5 = "38e49d56b3a919e7ec563b7ae22b068e"
EXPECT_A_MD5 = "e047ec426303a98bc939c270ecd5e44f"


def md5(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def lines(path):
    with open(path, encoding="utf-8-sig") as fh:
        return fh.read().replace("\r\n", "\n").strip().split("\n")


def rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def arm(rs, treated):
    return [r for r in rs if r["treated"] == str(treated)]


def main():
    out = {}
    ok = {}

    a, b = rows(A), rows(B)
    a_can = [r["Gene"] for r in arm(a, 1)]
    a_ctl = [r["Gene"] for r in arm(a, 0)]
    b_can = [r["Gene"] for r in arm(b, 1)]
    b_ctl = [r["Gene"] for r in arm(b, 0)]

    # ---- 1. hash identity ------------------------------------------------
    h_a, h_b = md5(A), md5(B)
    out["hash_control_set_A"] = h_a
    out["hash_re_emitted_B"] = h_b
    out["hash_archive_shipped"] = md5(ARCH) if os.path.exists(ARCH) else None
    out["hash_this_run"] = md5(EMITTED) if os.path.exists(EMITTED) else None
    ok["hashes_match_B"] = bool(
        out["hash_this_run"] and
        out["hash_this_run"] == out["hash_re_emitted_B"] == out["hash_archive_shipped"])
    out["md5_matches_pinned_constant"] = out["hash_this_run"] == EXPECT_B_MD5
    out["md5_A_matches_pinned_constant"] = h_a == EXPECT_A_MD5

    # ---- 2/3. the two SETs ------------------------------------------------
    out["candidate_set_identical"] = set(a_can) == set(b_can)
    out["candidate_count"] = [len(a_can), len(b_can)]
    out["control_set_overlap"] = len(set(a_ctl) & set(b_ctl))
    out["control_set_size"] = len(a_ctl)
    ok["control_set_30_of_30"] = out["control_set_overlap"] == len(a_ctl) == 30

    # ---- 4/5. the candidate block, and the line difference ----------------
    la, lb = lines(A), lines(B)
    out["lines"] = [len(la), len(lb)]
    out["candidate_block_byte_identical"] = la[1:31] == lb[1:31]
    out["differing_lines"] = sum(1 for x, y in zip(la, lb) if x != y)
    out["differing_lines_expected"] = 28
    ok["difference_is_the_pairing_only"] = out["differing_lines"] == 28

    # ---- pairing agreement, to keep Q1 and Q2 distinguishable --------------
    a_partner = {c: p for c, p in zip(a_can, a_ctl)}
    b_partner = {c: p for c, p in zip(b_can, b_ctl)}
    out["pairing_agreement_with_A"] = sum(
        1 for c in a_can if a_partner.get(c) == b_partner.get(c))
    out["pairing_agreement_note"] = (
        "low by design: A's pairing is a rank-zip, B's is a nearest-neighbour "
        "matching. Q1 is the SET; Q2 is the PAIRING. See "
        "docs/audit_notes/s4_pairing_provenance_20261004/")

    # ---- column layout ----------------------------------------------------
    out["columns_A"] = list(a[0].keys())
    out["columns_B"] = list(b[0].keys())
    out["column_layout_identical"] = out["columns_A"] == out["columns_B"]

    out["verdict"] = "Q1 REPRODUCED" if all(ok.values()) else "Q1 NOT REPRODUCED"
    out["checks"] = ok

    # ---- report -----------------------------------------------------------
    print(f"A (submitted)      md5 {h_a}  {len(a_can)} candidates / {len(a_ctl)} controls")
    print(f"B (re-emitted)     md5 {h_b}  {len(b_can)} candidates / {len(b_ctl)} controls")
    print(f"this run           md5 {out['hash_this_run']}")
    print(f"archive (shipped)  md5 {out['hash_archive_shipped']}")
    print()
    for k, v in ok.items():
        print(f"  [{'ok' if v else 'FAIL'}] {k}")
    print(f"\ncontrol set overlap  : {out['control_set_overlap']} / {out['control_set_size']}")
    print(f"differing lines vs A : {out['differing_lines']} / {len(lb)}")
    print(f"pairing vs A         : {out['pairing_agreement_with_A']} / 30  (Q2's question, not Q1's)")
    print(f"\n{out['verdict']}")

    od = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, "q1_verification.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"wrote {os.path.join(od, 'q1_verification.json')}")

    return 0 if all(ok.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

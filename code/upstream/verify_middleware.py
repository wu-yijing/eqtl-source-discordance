#!/usr/bin/env python3
"""Verify the middleware that `code/run_upstream.sh` rebuilds.

The upstream chain was, until 2026-10-03, only ever *described* as working: the
archive recorded hashes in prose and nothing could fail if a rebuild disagreed.
That is how a real defect survived — `build_covariance.py` wrote the GTEx
covariances in the wrong row order, which changes the file bytes while leaving
the gene set, the SNP pairs and every value identical. A content check passed;
the recorded hash did not.

This script turns that class of failure into a non-zero exit. It hashes each
middleware artefact a rebuild produces and compares it with the copy the
reported numbers came from.

    python3 code/upstream/verify_middleware.py --run-dir /path/to/_upstream_run/out

There is also a **shipped copy** of most of this middleware, at `data/upstream/`, added
on 2026-10-03 so the Z layer's provenance can be checked without the ~4.7 GB of
third-party inputs. Point this script at that directory to verify a fresh clone:

    python3 code/upstream/verify_middleware.py --run-dir data/upstream
    # identical 27 | differing 0 | missing 3   <- the 3 are the band covariances,
    # which are over GitHub's 100 MiB per-file block and cannot be shipped

`scripts/verify_from_clone.sh` gate 9 runs exactly that, because the shipped artefacts
include CRLF files (the official MetaXcan CSV outputs) and a `.gitattributes` rule
normalising them to LF would change every byte and silently invalidate every hash here.

Every expectation below is also recorded in `data/external/README.md`
(§"Files that are derived") so the two can be compared by eye.

THE FOUR SQLite ARTEFACTS ARE CHECKED BY CONTENT, NOT BY BYTES (2026-10-05)
--------------------------------------------------------------------------
`eqtlgen/*.db` used to be pinned by `file-sha256`. A SQLite file's byte image
depends on the writing library's version: the same schema and the same rows in the
same order can be written to a different page layout with the same byte count, so a
rebuild under a different `sqlite3.sqlite_version` reported DIFFERS with nothing
different. That is exactly what happened on 2026-10-05 — a local re-run of the whole
chain produced all four databases with identical size, identical schema, identical
rows and identical `COUNT(*)` per table, and still failed this check.

They are now pinned by a `content_sha256_db`: SHA-256 over the schema plus every row
of every table in a deterministic (all-columns) order — the same canonical form
`docs/audit_notes/upstream_recheck_20261005/scripts/compare_db_content.py` uses, and
the `.db` analogue of the `content_md5` the `.txt.gz` covariances already use. The
writer version is reported on every run, because it is what the byte image depends on.

Exit status: 0 if every artefact that is present matches; 1 if any differs.
Absent artefacts are reported as MISSING and do not by themselves fail the run,
because a partial rebuild (say, only the GTEx arm) is a legitimate thing to
check — pass --require-all to make them failures too.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import sqlite3
import sys

# (relative path from --run-dir, kind, expected, label)
#   kind: 'sha256' file hash | 'md5' file hash | 'content_md5' md5 of the
#         decompressed bytes (a gzip stream embeds an mtime, so the file hash of
#         the same content differs run to run; the content hash does not) |
#         'content_sha256_db' sha256 of a SQLite database's schema + every row
#         (a SQLite file's byte image depends on the writer's library version, so
#         the file hash of the same content differs run to run; this does not).
EXPECTED = [
    ("eqtlgen/eQTLGen_Whole_Blood.db", "content_sha256_db",
     "7bfe1c08e14ed88837b0acf9c6eb5f601c73c1303384192f30d3c203b2e710ba",
     "eQTLGen weight database"),
    ("eqtlgen/db_A.db", "content_sha256_db",
     "54082ecddfe1ba848ff7dae24c01ec27c8792d8021e1370cac84d36961a9739e",
     "eQTLGen band A model database"),
    ("eqtlgen/db_B.db", "content_sha256_db",
     "d29895db795f66eb1ddc20df2fb988e7c3939a8ea3b1e924990e1521caddbbc6",
     "eQTLGen band B model database"),
    ("eqtlgen/db_C.db", "content_sha256_db",
     "60b910090e6de9f0f8321e471fc6810e8fa46957de330bd5cfc5ef433873a8e7",
     "eQTLGen band C model database"),
    ("cov/cov_Whole_Blood.txt.gz", "content_md5",
     "31137589fc9ca1a261df19fba7f14e08", "GTEx Whole_Blood gene covariance"),
    ("cov/cov_Nerve_Tibial.txt.gz", "content_md5",
     "4ea16ad919cd0b90a693f54e8702eb59", "GTEx Nerve_Tibial gene covariance"),
    ("eqtlgen/cov_A.txt.gz", "content_md5",
     "ed58ccdfc590dc4498dd5ddc6c8b0ea2", "eQTLGen band A covariance"),
    ("eqtlgen/cov_B.txt.gz", "content_md5",
     "2a532e74469a340feaf0b7a791740151", "eQTLGen band B covariance"),
    ("eqtlgen/cov_C.txt.gz", "content_md5",
     "f30ebf0255d9eed610b6162a35be97c6", "eQTLGen band C covariance"),
    ("gwas/gwas_DR.tsv", "md5", "390e4e9abaea0464e112008a39958511",
     "FinnGen DR -> harmonised GWAS"),
    ("gwas/gwas_DN.tsv", "md5", "25c53a645397870098cbed30e17a0a1c",
     "FinnGen DN -> harmonised GWAS"),
    ("gwas/gwas_DPN.tsv", "md5", "70c16fc9783f225b55cc7dbc033fc5df",
     "FinnGen DPN -> harmonised GWAS"),
    ("eqtlgen/gwas_DR_aligned.tsv", "md5", "3ea5fda0c3cc1222318eab1f57049ae9",
     "allele-aligned GWAS DR"),
    ("eqtlgen/gwas_DN_aligned.tsv", "md5", "269358b089b2bf56a6eb8ae7df1cf831",
     "allele-aligned GWAS DN"),
    ("eqtlgen/gwas_DPN_aligned.tsv", "md5", "453e3226eba6b10213aebe3a8f1e70e4",
     "allele-aligned GWAS DPN"),
    ("official_Whole_Blood_DR.csv", "md5", "57738c427b957c25a6f455f5ff22c4a0",
     "S-PrediXcan GTEx Whole_Blood x DR"),
    ("official_Whole_Blood_DN.csv", "md5", "cce57111298a024b5e9ed5101c048f74",
     "S-PrediXcan GTEx Whole_Blood x DN"),
    ("official_Whole_Blood_DPN.csv", "md5", "c4bceab533b56ce928cf4c69e87462d8",
     "S-PrediXcan GTEx Whole_Blood x DPN"),
    ("official_Nerve_Tibial_DR.csv", "md5", "966e43e6dec03669fdd13ef44b6866d9",
     "S-PrediXcan GTEx Nerve_Tibial x DR"),
    ("official_Nerve_Tibial_DN.csv", "md5", "1dc9106b31369aa5115322bd03fd0b7a",
     "S-PrediXcan GTEx Nerve_Tibial x DN"),
    ("official_Nerve_Tibial_DPN.csv", "md5", "92b942f7437b65bb0dc2658e1eb6bccb",
     "S-PrediXcan GTEx Nerve_Tibial x DPN"),
]
for _tag in ("A", "B", "C"):
    for _ph, _h in (("DR", {"A": "8590d52ee797ca76cc292e71d122f8a9",
                            "B": "f704406684eda32bc6bd15ee8692ca6f",
                            "C": "aadc03b20c309434703f8f826311d38c"}[_tag]),
                    ("DN", {"A": "ae35c433289e695bfd97b6de66b5e140",
                            "B": "579082773814fe11b33ea5bf6cbaad10",
                            "C": "1d6416923477fc69778bf4874f0fae3c"}[_tag]),
                    ("DPN", {"A": "2950f5cee032862bc0af82754cf71b82",
                             "B": "817811fcc41790f09145f4acf4a97960",
                             "C": "b01c432e5128ecc541de8f5203a4ccc0"}[_tag])):
        EXPECTED.append(("eqtlgen/official_eq_%s_%s.csv" % (_tag, _ph), "md5", _h,
                         "S-PrediXcan eQTLGen band %s x %s" % (_tag, _ph)))


def file_digest(path, alg):
    h = hashlib.new(alg)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_md5(path):
    h = hashlib.md5()
    with gzip.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_sha256_db(path):
    """SHA-256 over a SQLite database's schema and every row, in a fixed order.

    Canonical form, shared with
    docs/audit_notes/upstream_recheck_20261005/scripts/compare_db_content.py:
    for each (type, name, sql) of sqlite_master, then for each table the rows
    ordered by all of its columns. Page layout, free-list state and the writer's
    library version do not enter the hash; the schema and the data do.
    """
    con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
    try:
        cur = con.cursor()
        h = hashlib.sha256()
        schema = cur.execute(
            "SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' "
            "ORDER BY type, name").fetchall()
        for t, n, s in schema:
            h.update(("%s|%s|%s\n" % (t, n, s)).encode("utf-8"))
        for t, n, _s in schema:
            if t != "table":
                continue
            cols = [c[1] for c in cur.execute('PRAGMA table_info("%s")' % n).fetchall()]
            order = ",".join('"%s"' % c for c in cols)
            for r in cur.execute('SELECT * FROM "%s" ORDER BY %s' % (n, order)):
                h.update(("%s|%s\n" % (n, "|".join("" if v is None else str(v)
                                                   for v in r))).encode("utf-8"))
        return h.hexdigest()
    finally:
        con.close()


def actual(path, kind):
    if kind == "sha256":
        return file_digest(path, "sha256")
    if kind == "md5":
        return file_digest(path, "md5")
    if kind == "content_sha256_db":
        return content_sha256_db(path)
    return content_md5(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-dir", required=True,
                    help="the upstream output directory (UPSTREAM_OUT)")
    ap.add_argument("--require-all", action="store_true",
                    help="treat a MISSING artefact as a failure too")
    ap.add_argument("--quiet", action="store_true", help="print only failures")
    args = ap.parse_args()

    if not args.quiet:
        print("sqlite3 library : %s" % sqlite3.sqlite_version)
        print("                  (the four .db artefacts are pinned by CONTENT, because their")
        print("                   byte image depends on this version; see the module docstring)")
        print()

    ok = bad = missing = 0
    for rel, kind, want, label in EXPECTED:
        p = os.path.join(args.run_dir, rel)
        if not os.path.exists(p):
            missing += 1
            if not args.quiet:
                print("  [ MISSING ] %-38s %s" % (rel, label))
            continue
        got = actual(p, kind)
        if got == want:
            ok += 1
            if not args.quiet:
                print("  [   ok    ] %-38s %s" % (rel, label))
        else:
            bad += 1
            print("  [ DIFFERS ] %-38s %s" % (rel, label))
            print("              %s expected %s" % (kind, want))
            print("              %s got      %s" % (kind, got))
            if kind == "content_md5":
                print("              a same-content file with a different row order "
                      "lands here: check --order on build_covariance.py")
            if kind == "content_sha256_db":
                print("              the schema or the rows differ — not the page layout. "
                      "Compare by hand with "
                      "docs/audit_notes/upstream_recheck_20261005/scripts/compare_db_content.py")

    print()
    print("identical %d | differing %d | missing %d   (of %d)"
          % (ok, bad, missing, len(EXPECTED)))
    if bad:
        print("RESULT: the rebuild does NOT reproduce the archived middleware.")
        return 1
    if missing and args.require_all:
        print("RESULT: --require-all, and %d artefact(s) were not produced." % missing)
        return 1
    if missing:
        print("RESULT: every artefact present matches (%d not produced in this run)." % missing)
    else:
        print("RESULT: the whole upstream chain reproduces the archived middleware.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

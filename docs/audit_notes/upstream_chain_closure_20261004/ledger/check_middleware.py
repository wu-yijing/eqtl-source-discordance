#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""边跑边对账：把上游链已产出的中间件与 data/external/README.md 登记哈希逐一比对。

用法：
    python check_middleware.py                     # 逐行打印判定
    python check_middleware.py --tsv ledger.tsv    # 同时输出机器可读台账
"""
import argparse
import gzip
import hashlib
import os
import sys

RUN_DEFAULT = "E:/workbuddy/_upstream_20261004/run"
RUN = os.environ.get("UPSTREAM_RUN_DIR", RUN_DEFAULT)

# kind: 'file-md5' | 'file-sha256' | 'content-md5'
REC = [
    ("eQTLGen_Whole_Blood.db", "eqtlgen/eQTLGen_Whole_Blood.db", "file-sha256",
     "413c4fff25c1820fd92f11f4370e25f3b82ea2ecd5a84ff0643d5f750312fa3c", 4866048),
    ("cov_Whole_Blood.txt.gz", "cov/cov_Whole_Blood.txt.gz", "content-md5",
     "31137589fc9ca1a261df19fba7f14e08", 1498762),
    ("cov_Nerve_Tibial.txt.gz", "cov/cov_Nerve_Tibial.txt.gz", "content-md5",
     "4ea16ad919cd0b90a693f54e8702eb59", 2062148),
    ("cov_A.txt.gz", "eqtlgen/cov_A.txt.gz", "content-md5",
     "ed58ccdfc590dc4498dd5ddc6c8b0ea2", None),
    ("cov_B.txt.gz", "eqtlgen/cov_B.txt.gz", "content-md5",
     "2a532e74469a340feaf0b7a791740151", None),
    ("cov_C.txt.gz", "eqtlgen/cov_C.txt.gz", "content-md5",
     "f30ebf0255d9eed610b6162a35be97c6", None),
    ("db_A.db", "eqtlgen/db_A.db", "file-sha256",
     "f3a29eee9bf1aa4384de6b8627136c55988b077ff34af28431b3e2c9c2156d74", 3469312),
    ("db_B.db", "eqtlgen/db_B.db", "file-sha256",
     "51777828c3607b5b172264f380cc9928ef19dc6b9e382abc460db0b9c8e8b966", 1007616),
    ("db_C.db", "eqtlgen/db_C.db", "file-sha256",
     "1617c517e030394b62a33f0466bd9904ae81b7e0e3c7cf3a20db27e84e4e66d8", 380928),
    ("gwas_DR.tsv", "gwas/gwas_DR.tsv", "file-md5",
     "390e4e9abaea0464e112008a39958511", None),
    ("gwas_DN.tsv", "gwas/gwas_DN.tsv", "file-md5",
     "25c53a645397870098cbed30e17a0a1c", None),
    ("gwas_DPN.tsv", "gwas/gwas_DPN.tsv", "file-md5",
     "70c16fc9783f225b55cc7dbc033fc5df", None),
    ("gwas_DR_aligned.tsv", "eqtlgen/gwas_DR_aligned.tsv", "file-md5",
     "3ea5fda0c3cc1222318eab1f57049ae9", None),
    ("gwas_DN_aligned.tsv", "eqtlgen/gwas_DN_aligned.tsv", "file-md5",
     "269358b089b2bf56a6eb8ae7df1cf831", None),
    ("gwas_DPN_aligned.tsv", "eqtlgen/gwas_DPN_aligned.tsv", "file-md5",
     "453e3226eba6b10213aebe3a8f1e70e4", None),
]
GTEX = {"Whole_Blood": {"DR": "57738c427b957c25a6f455f5ff22c4a0",
                        "DN": "cce57111298a024b5e9ed5101c048f74",
                        "DPN": "c4bceab533b56ce928cf4c69e87462d8"},
        "Nerve_Tibial": {"DR": "966e43e6dec03669fdd13ef44b6866d9",
                         "DN": "1dc9106b31369aa5115322bd03fd0b7a",
                         "DPN": "92b942f7437b65bb0dc2658e1eb6bccb"}}
for tis, d in GTEX.items():
    for ph, h in d.items():
        REC.append(("official_%s_%s.csv" % (tis, ph), "official_%s_%s.csv" % (tis, ph),
                    "file-md5", h, None))
EQ = {"A": {"DR": "8590d52ee797ca76cc292e71d122f8a9", "DN": "ae35c433289e695bfd97b6de66b5e140",
            "DPN": "2950f5cee032862bc0af82754cf71b82"},
      "B": {"DR": "f704406684eda32bc6bd15ee8692ca6f", "DN": "579082773814fe11b33ea5bf6cbaad10",
            "DPN": "817811fcc41790f09145f4acf4a97960"},
      "C": {"DR": "aadc03b20c309434703f8f826311d38c", "DN": "1d6416923477fc69778bf4874f0fae3c",
            "DPN": "b01c432e5128ecc541de8f5203a4ccc0"}}
for band, d in EQ.items():
    for ph, h in d.items():
        REC.append(("official_eq_%s_%s.csv" % (band, ph), "eqtlgen/official_eq_%s_%s.csv" % (band, ph),
                    "file-md5", h, None))


def digest(path, kind):
    if kind == "file-md5":
        h = hashlib.md5()
        with open(path, "rb") as f:
            for b in iter(lambda: f.read(1 << 22), b""):
                h.update(b)
        return h.hexdigest()
    if kind == "file-sha256":
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for b in iter(lambda: f.read(1 << 22), b""):
                h.update(b)
        return h.hexdigest()
    h = hashlib.md5()
    n = 0
    with gzip.open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
            n += len(b)
    return h.hexdigest(), n


ok = miss = bad = 0
rows = []
print("%-28s %-12s %s" % ("artefact", "verdict", "detail"))
print("-" * 92)
for name, rel, kind, expect, size in REC:
    p = os.path.join(RUN, rel)
    if not os.path.exists(p):
        miss += 1
        rows.append((name, rel, kind, expect, "", "", "", "pending"))
        print("%-28s %-12s not produced yet" % (name, "· pending"))
        continue
    raw = os.path.getsize(p)
    got = digest(p, kind)
    n = None
    if isinstance(got, tuple):
        got, n = got
    if got == expect:
        ok += 1
        extra = " (%s B decompressed)" % format(n, ",") if n else ""
        rows.append((name, rel, kind, expect, got, str(raw), str(n or ""), "MATCH"))
        print("%-28s %-12s ok%s" % (name, "✓ MATCH", extra))
    else:
        bad += 1
        rows.append((name, rel, kind, expect, got, str(raw), str(n or ""), "MISMATCH"))
        print("%-28s %-12s expect %s got %s" % (name, "✗ MISMATCH", expect[:16], got[:16]))
print("-" * 92)
print("matched %d   mismatched %d   pending %d   (of %d)" % (ok, bad, miss, len(REC)))

ap = argparse.ArgumentParser(add_help=False)
ap.add_argument("--tsv", default=None)
args, _ = ap.parse_known_args()

if args.tsv:
    with open(args.tsv, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("artefact\tpath_in_run\thash_kind\texpected\tobserved\t"
                 "file_bytes\tdecompressed_bytes\tverdict\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    print("ledger written: %s" % args.tsv)

sys.exit(1 if bad else 0)

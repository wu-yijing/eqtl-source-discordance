#!/usr/bin/env python3
"""Split a MetaXcan model database into size groups.

Why this exists
---------------
The eQTLGen gene covariance for the largest genes is very large. Running the
unmodified MetaXcan binary over the whole model at once needs the whole
covariance in memory. The archived run avoided that by partitioning the model
by the number of SNPs per gene and running the binary once per partition with
`--stream_covariance`:

    A: n_snps <= 1500           (the bulk of genes)
    B: 1500 < n_snps <= 3000
    C: n_snps > 3000            (a single gene in the archived model)

Each partition gets its own database and — via `build_covariance.py` — its own
covariance file. S-PrediXcan output is then concatenated; the partition is an
implementation detail of the run, not of the model.

Usage
-----
    python3 code/upstream/split_model_by_size.py \
        --model-db /path/to/eQTLGen_Whole_Blood.db \
        --out-dir  /path/to/eqtlgen
"""
from __future__ import annotations

import argparse
import io
import os
import sqlite3
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

BANDS = (("A", 0, 1500), ("B", 1500, 3000), ("C", 3000, 10 ** 12))

SCHEMA = [
    "CREATE TABLE weights (rsid TEXT, gene TEXT, weight REAL, ref_allele TEXT, eff_allele TEXT)",
    "CREATE TABLE extra (gene TEXT, genename TEXT, `n.snps.in.model` INTEGER, "
    "`pred.perf.R2` REAL, `pred.perf.pval` REAL, `pred.perf.qval` REAL)",
    "CREATE INDEX ix_w_gene ON weights(gene)",
]


def band_of(n):
    for tag, lo, hi in BANDS:
        if n <= hi and n > lo:
            return tag
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model-db", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    con = sqlite3.connect(args.model_db)
    genes = {}
    for gene, rsid, weight, ref, eff in con.execute(
            "SELECT gene, rsid, weight, ref_allele, eff_allele FROM weights"):
        genes.setdefault(gene, []).append((rsid, weight, ref, eff))
    names = dict(con.execute("SELECT gene, genename FROM extra"))
    con.close()

    groups = {}
    for gene, items in genes.items():
        groups.setdefault(band_of(len(items)), []).append(gene)

    for tag, _lo, _hi in BANDS:
        members = sorted(groups.get(tag, []))
        if not members:
            continue
        out = os.path.join(args.out_dir, "db_%s.db" % tag)
        if os.path.exists(out):
            os.remove(out)
        c = sqlite3.connect(out)
        for stmt in SCHEMA:
            c.execute(stmt)
        wbuf, ebuf = [], []
        for gene in members:
            items = genes[gene]
            for rsid, weight, ref, eff in items:
                wbuf.append((rsid, gene, weight, ref, eff))
            ebuf.append((gene, names.get(gene, gene), len(items), None, None, None))
            if len(wbuf) >= 200000:
                c.executemany("INSERT INTO weights VALUES (?,?,?,?,?)", wbuf)
                wbuf.clear()
        if wbuf:
            c.executemany("INSERT INTO weights VALUES (?,?,?,?,?)", wbuf)
        c.executemany("INSERT INTO extra VALUES (?,?,?,?,?,?)", ebuf)
        c.commit()
        c.close()
        print("band %s: %d genes, %s model SNPs -> %s (%s B)" % (
            tag, len(members), format(sum(len(genes[g]) for g in members), ","),
            out, format(os.path.getsize(out), ",")))


if __name__ == "__main__":
    main()

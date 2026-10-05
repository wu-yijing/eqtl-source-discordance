#!/usr/bin/env python3
"""Build an eQTLGen weight database in the official MetaXcan schema.

This is the step `data/external/README.md` used to describe in prose only
("filtering this file on the 103 ENSG ids ... reproduces all 65,622 weight
rows"). The rule is short and is implemented here so it can be re-run rather
than trusted:

    AssessedAllele -> eff_allele
    OtherAllele    -> ref_allele
    Zscore         -> weight          (eQTLGen ships a Z, not a beta)
    Gene           -> gene            (ENSG id, as it appears in the source)
    GeneSymbol     -> genename

Rows are kept only for the genes of the analysis universe, and a `weights`
table plus an `extra` table are written so that the result is a drop-in
`--model_db_path` for the unmodified MetaXcan `SPrediXcan.py`.

Reproducibility note
--------------------
Run against the archived inputs (the eQTLGen phase-I cis-eQTL file, and the
114-symbol universe shipped beside this script) this writes a database whose
*file* SHA-256 is
    413c4fff25c1820fd92f11f4370e25f3b82ea2ecd5a84ff0643d5f750312fa3c
i.e. byte-for-byte the copy the reported eQTLGen Z layer came from. The build
is deterministic given the same inputs: the sqlite pragmas, the row order and
the 200,000-row flush size are fixed, and no timestamp is written.

Usage
-----
    python3 code/upstream/build_eqtlgen_db.py \
        --cis-eqtl /path/to/2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz \
        --gene-symbols code/upstream/eqtlgen_gene_universe.txt \
        --out /path/to/eQTLGen_Whole_Blood.db
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import os
import sqlite3
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

PLINK_SAFE_FLUSH = 200000

SCHEMA = [
    "CREATE TABLE weights (rsid TEXT, gene TEXT, weight REAL, ref_allele TEXT, eff_allele TEXT)",
    "CREATE TABLE extra (gene TEXT, genename TEXT, `n.snps.in.model` INTEGER, "
    "`pred.perf.R2` REAL, `pred.perf.pval` REAL, `pred.perf.qval` REAL)",
    "CREATE INDEX ix_w_gene ON weights(gene)",
]

DEFAULT_UNIVERSE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "eqtlgen_gene_universe.txt")


def read_universe(path):
    genes = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                genes.add(line.upper())
    return genes


def sha256_file(path, chunk=1 << 20):
    m = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            m.update(block)
    return m.hexdigest()


def build(cis_eqtl, universe, out):
    if os.path.exists(out):
        os.remove(out)
    con = sqlite3.connect(out)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    for stmt in SCHEMA:
        con.execute(stmt)

    t0 = time.time()
    buf = []
    n_row = 0
    n_keep = 0
    kept_genes = {}

    with gzip.open(cis_eqtl, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("\t")
        ci = {h: i for i, h in enumerate(header)}
        need = ("SNP", "AssessedAllele", "OtherAllele", "Zscore", "Gene", "GeneSymbol")
        missing = [c for c in need if c not in ci]
        if missing:
            raise SystemExit("cis-eQTL file is missing column(s): %s" % ", ".join(missing))
        i_snp, i_ass, i_oth, i_z, i_g, i_sym = (ci[c] for c in need)
        for line in f:
            n_row += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= i_sym:
                continue
            symbol = parts[i_sym].upper()
            if symbol not in universe:
                continue
            try:
                weight = float(parts[i_z])
            except ValueError:
                continue
            gid = parts[i_g]
            buf.append((parts[i_snp], gid, weight, parts[i_oth], parts[i_ass]))
            kept_genes[gid] = symbol
            n_keep += 1
            if len(buf) >= PLINK_SAFE_FLUSH:
                con.executemany("INSERT INTO weights VALUES (?,?,?,?,?)", buf)
                buf.clear()
    if buf:
        con.executemany("INSERT INTO weights VALUES (?,?,?,?,?)", buf)

    print("scanned %s rows, kept %s; genes with a model %d/%d  (%.1f s)" % (
        format(n_row, ","), format(n_keep, ","), len(kept_genes), len(universe),
        time.time() - t0))

    counts = dict(con.execute("SELECT gene, COUNT(*) FROM weights GROUP BY gene").fetchall())
    rows = [(g, sym, int(counts.get(g, 0)), None, None, None)
            for g, sym in kept_genes.items()]
    con.executemany("INSERT INTO extra VALUES (?,?,?,?,?,?)", rows)
    con.commit()

    print("extra rows = %d" % len(rows))
    if counts:
        ordered = sorted(counts.values())
        print("model SNPs per gene: median %d, range %d-%d" % (
            ordered[len(ordered) // 2], ordered[0], ordered[-1]))
    no_model = sorted(universe - set(kept_genes.values()))
    print("genes in universe with no model (%d): %s" % (len(no_model), no_model))
    con.close()

    digest = sha256_file(out)
    print("wrote: %s  (%s B)" % (out, format(os.path.getsize(out), ",")))
    print("SHA-256: %s" % digest)
    return digest


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cis-eqtl", required=True,
                    help="eQTLGen phase-I cis-eQTL summary statistics (.txt.gz)")
    ap.add_argument("--gene-symbols", default=DEFAULT_UNIVERSE,
                    help="analysis gene universe, one symbol per line (default: the "
                         "shipped 114-symbol file)")
    ap.add_argument("--out", required=True, help="output SQLite model database")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    build(args.cis_eqtl, read_universe(args.gene_symbols), args.out)


if __name__ == "__main__":
    main()

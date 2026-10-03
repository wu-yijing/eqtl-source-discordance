#!/usr/bin/env python3
"""Build a gene-level SNP covariance file for a MetaXcan model database.

This is the "GTEx gene-level covariance" / "eQTLGen cov" middleware that
`code/run_upstream.sh` used to require the user to supply, with a comment that
said "if you do not have it, build it with MetaXcan's own tools ... or reuse
the one your run produced". The build is short enough to just do here.

Method (matches the archived run)
---------------------------------
* Sample count N and byte stride come from the PLINK 1 `.fam` (stride = ceil(N/4)).
* PLINK 1 2-bit encoding is decoded as 00 = hom-A1 (dosage 0), 01 = missing,
  10 = heterozygote (dosage 1), 11 = hom-A2 (dosage 2). Missing calls are
  mean-imputed for the SNP (`g1000_eur` has none, but the rule is stated).
* The dosage matrix is read *streamed* from the `.bed`, one variant at a time,
  so peak memory is O(N) per variant plus the variants a single gene uses —
  not O(variants x N).
* For every gene, `numpy.cov(ddof=1)` is taken over the dosages of the SNPs in
  its model, and the **upper triangle** (i <= j) is written, genes in ascending
  model-DB order and SNPs within a gene in model order.

The `.bed` may be given either as a plain PLINK prefix (`--plink-prefix`) or
inside a zip (`--plink-zip`, with `--bfile-stem` naming the members), which is
how the archived `g1000_eur.zip` ships.

Usage
-----
    python3 code/upstream/build_covariance.py \
        --model-db   /path/to/mask.db \
        --plink-zip  /path/to/g1000_eur.zip --bfile-stem g1000_eur \
        --out        /path/to/cov_Whole_Blood.txt.gz
"""
from __future__ import annotations

import argparse
import gzip
import io
import os
import sqlite3
import sys
import time
import zipfile

import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# uncompressed bytes to pull from the .bed per read; kept modest so peak memory
# stays O(N) per variant even for a 500-sample panel
READ_MB = 64


def model_snps_by_gene(db):
    con = sqlite3.connect(db)
    genes = {}
    for gene, rsid in con.execute("SELECT gene, rsid FROM weights"):
        genes.setdefault(gene, []).append(rsid)
    con.close()
    return genes


def index_bim(lines, need):
    """rsid -> row index for the rsids we need (first occurrence wins)."""
    idx_of = {}
    n = 0
    for line in lines:
        parts = line.split()
        if len(parts) >= 6 and parts[1] in need and parts[1] not in idx_of:
            idx_of[parts[1]] = n
        n += 1
    return idx_of, n


def decode_variant(raw, stride, n_samples):
    """PLINK 1 2-bit -> dosage (float32), missing -> NaN."""
    calls = np.empty(stride * 4, dtype=np.uint8)
    for shift in range(4):
        calls[shift::4] = (raw >> (2 * shift)) & 3
    calls = calls[:n_samples]
    d = np.full(n_samples, np.nan, dtype=np.float32)
    d[calls == 0] = 0.0
    d[calls == 2] = 1.0
    d[calls == 3] = 2.0
    if np.isnan(d).any():
        mean = np.nanmean(d)
        d = np.where(np.isnan(d), 0.0 if np.isnan(mean) else mean, d)
    return d


def load_dosages(need, fam_path, bim_iter, bed_opener):
    n = sum(1 for _ in open(fam_path, encoding="utf-8", errors="replace"))
    stride = (n + 3) // 4

    t0 = time.time()
    idx_of, n_bim = index_bim(bim_iter, need)
    print("bim rows %s, matched %s (%.1f%%)  (%.1f s)" % (
        format(n_bim, ","), format(len(idx_of), ","),
        100.0 * len(idx_of) / max(1, len(need)), time.time() - t0))

    want = {v: k for k, v in idx_of.items()}
    dosages = {}
    t0 = time.time()
    with bed_opener() as bed:
        magic = bed.read(3)
        if magic != b"\x6c\x1b\x01":
            raise SystemExit("not a PLINK 1 .bed (magic %r)" % magic)
        per_read = stride * max(1, (READ_MB << 20) // stride)
        base = 0
        while True:
            block = bed.read(per_read)
            if not block:
                break
            k = len(block) // stride
            if k == 0:
                break
            arr = np.frombuffer(block[:k * stride], dtype=np.uint8).reshape(k, stride)
            for j in range(k):
                rsid = want.get(base + j)
                if rsid is not None:
                    dosages[rsid] = decode_variant(arr[j], stride, n)
            base += k
    print("dosages ready: %s SNPs x %d samples  (%.1f s)" % (
        format(len(dosages), ","), n, time.time() - t0))
    return dosages


def write_covariance(gene_snps, dosages, out):
    n_rows = 0
    n_gene = 0
    t0 = time.time()
    with gzip.open(out, "wt", encoding="utf-8", newline="", compresslevel=1) as f:
        f.write("GENE\tRSID1\tRSID2\tVALUE\n")
        for gene in sorted(gene_snps):
            rsids = [r for r in gene_snps[gene] if r in dosages]
            if not rsids:
                continue
            mat = np.vstack([dosages[r] for r in rsids]).astype(np.float64)
            cov = np.atleast_2d(np.cov(mat, ddof=1))
            iu = np.triu_indices(len(rsids))
            vals = cov[iu]
            a = np.asarray(rsids, dtype=object)[iu[0]]
            b = np.asarray(rsids, dtype=object)[iu[1]]
            for s in range(0, len(vals), 400000):
                e = min(s + 400000, len(vals))
                f.write("\n".join(
                    "%s\t%s\t%s\t%.10g" % (gene, a[i], b[i], vals[i])
                    for i in range(s, e)))
                f.write("\n")
            n_rows += len(vals)
            n_gene += 1
    print("wrote %d genes / %s rows  (%.1f s)" % (
        n_gene, format(n_rows, ","), time.time() - t0))
    print("file: %s  (%s B)" % (out, format(os.path.getsize(out), ",")))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model-db", required=True, help="MetaXcan model database")
    ap.add_argument("--out", required=True, help="output covariance .txt.gz")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--plink-prefix", help="PLINK 1 bfile prefix (path without extension)")
    src.add_argument("--plink-zip", help="zip containing the .bed/.bim/.fam")
    ap.add_argument("--bfile-stem", default=None,
                    help="member stem inside --plink-zip (default: the zip basename)")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    gene_snps = model_snps_by_gene(args.model_db)
    need = {r for v in gene_snps.values() for r in v}
    print("genes %d, distinct model SNPs %s" % (len(gene_snps), format(len(need), ",")))

    if args.plink_prefix:
        fam = args.plink_prefix + ".fam"
        bim_iter = open(args.plink_prefix + ".bim", encoding="utf-8", errors="replace")
        bed_opener = lambda: open(args.plink_prefix + ".bed", "rb")
        dosages = load_dosages(need, fam, bim_iter, bed_opener)
    else:
        stem = args.bfile_stem or os.path.splitext(os.path.basename(args.plink_zip))[0]
        zf = zipfile.ZipFile(args.plink_zip)
        names = zf.namelist()
        member = lambda ext: next(n for n in names if n.endswith(stem + ext))
        fam_member, bim_member, bed_member = member(".fam"), member(".bim"), member(".bed")
        # read the small .fam/.bim eagerly; stream the .bed
        import tempfile
        with tempfile.NamedTemporaryFile("wb", suffix=".fam", delete=False) as tf:
            tf.write(zf.read(fam_member))
            fam = tf.name
        bim_iter = io.StringIO(zf.read(bim_member).decode("utf-8", "replace"))
        dosages = load_dosages(need, fam, bim_iter, lambda: zf.open(bed_member))

    write_covariance(gene_snps, dosages, args.out)


if __name__ == "__main__":
    main()

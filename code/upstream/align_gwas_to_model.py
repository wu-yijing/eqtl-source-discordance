#!/usr/bin/env python3
"""Align a GWAS file onto a MetaXcan model's effect allele, for S-PrediXcan.

MetaXcan does **not** flip a GWAS effect allele onto the model's. So before a
GWAS can be run against an eQTLGen model, the Z must be re-signed onto the
model alleles — otherwise every allele-reversed SNP contributes with the wrong
sign.

The archived run did this by writing a small table in which the "effect allele"
column *is* the model's `eff_allele` and the beta column carries the signed Z
with `se = 1` (MetaXcan then recomputes `z = beta / se = beta`).

Alignment rule (identical to the archived harmonisation)
-------------------------------------------------------
    FinnGen (ref, alt) == (model ref, model eff)  -> keep Z
    FinnGen (ref, alt) == (model eff, model ref)  -> negate Z
    otherwise                                     -> drop the SNP

Only SNPs present in the model database are written.

Usage
-----
    python3 code/upstream/align_gwas_to_model.py \
        --model-db /path/to/eQTLGen_Whole_Blood.db \
        --gwas     /path/to/finngen_R13_DM_NEPHROPATHY.gz \
        --out      /path/to/gwas_DN_aligned.tsv
"""
from __future__ import annotations

import argparse
import gzip
import io
import os
import sqlite3
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def model_alleles(db):
    """rsid -> (ref_allele, eff_allele), upper-cased."""
    con = sqlite3.connect(db)
    alleles = {}
    for rsid, ref, eff in con.execute("SELECT rsid, ref_allele, eff_allele FROM weights"):
        alleles.setdefault(rsid, (ref.upper(), eff.upper()))
    con.close()
    return alleles


def align(alleles, gwas_path, out):
    n_line = n_keep = n_flip = n_drop = 0
    t0 = time.time()
    with gzip.open(gwas_path, "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("\t")
        ci = {h.lower().lstrip("#"): i for i, h in enumerate(header)}
        need = ("rsids", "beta", "sebeta", "alt", "ref")
        missing = [c for c in need if c not in ci]
        if missing:
            raise SystemExit("GWAS file is missing column(s): %s" % ", ".join(missing))
        i_rs, i_b, i_se, i_alt, i_ref = (ci[c] for c in need)
        bound = max(i_rs, i_b, i_se, i_alt, i_ref)
        with open(out, "w", encoding="utf-8", newline="") as o:
            o.write("snp\tbeta\tse\talt\tref\n")
            for line in f:
                n_line += 1
                parts = line.rstrip("\n").split("\t")
                if len(parts) <= bound:
                    continue
                rsid = parts[i_rs]
                if rsid not in alleles and "," in rsid:
                    rsid = next((t.strip() for t in rsid.split(",") if t.strip() in alleles),
                                None)
                    if rsid is None:
                        continue
                elif rsid not in alleles:
                    continue
                ref_m, eff_m = alleles[rsid]
                ref_g = parts[i_ref].upper()
                alt_g = parts[i_alt].upper()
                try:
                    z = float(parts[i_b]) / float(parts[i_se])
                except ValueError:
                    continue
                if ref_g == ref_m and alt_g == eff_m:
                    pass
                elif ref_g == eff_m and alt_g == ref_m:
                    z = -z
                    n_flip += 1
                else:
                    n_drop += 1
                    continue
                o.write("%s\t%.10g\t1\t%s\t%s\n" % (rsid, z, eff_m, ref_m))
                n_keep += 1
    print("read %s rows -> kept %s (flipped %d, allele-mismatch dropped %d)  (%.1f s)" % (
        format(n_line, ","), format(n_keep, ","), n_flip, n_drop, time.time() - t0))
    print("wrote: %s  (%s B)" % (out, format(os.path.getsize(out), ",")))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model-db", required=True, help="MetaXcan model database")
    ap.add_argument("--gwas", required=True, help="GWAS summary statistics (.gz)")
    ap.add_argument("--out", required=True, help="output aligned table (.tsv)")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    alleles = model_alleles(args.model_db)
    print("distinct model SNPs %s" % format(len(alleles), ","))
    align(alleles, args.gwas, args.out)


if __name__ == "__main__":
    main()

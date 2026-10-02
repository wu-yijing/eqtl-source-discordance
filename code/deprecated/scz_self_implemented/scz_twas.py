import sqlite3, gzip, sys, time, math
import numpy as np

WDB   = "_DEPRECATED_scz_self_implemented/weights.db"
BIM   = "E:/workbuddy/2026-06-24-05-57-20/tools/ldref/g1000_eur.bim"
FAM   = "E:/workbuddy/2026-06-24-05-57-20/tools/ldref/g1000_eur.fam"
BED   = "E:/workbuddy/2026-06-24-05-57-20/tools/ldref/g1000_eur.bed"
SCZ   = "_DEPRECATED_scz_self_implemented/PGC3_SCZ_wave3.european.autosome.public.v3.vcf.tsv.gz"
TARGET= "_DEPRECATED_scz_self_implemented/_rdat_tmp/target_genes.txt"
NEED  = "_DEPRECATED_scz_self_implemented/_rdat_tmp/needed_rsids.txt"
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 0   # 0 = all

RIDGE = 0.1   # regularization on LD correlation matrix
EQ_CONV = "ref"   # eQTLGen top1 weight effect allele = ref(V5); flipped from alt after sign-sanity (rho went -0.48 -> +)

# ---------- 1. bim scan (needed rsids only) + variant index ----------
needed = set(l.strip() for l in open(NEED) if l.strip())
print("needed rsids:", len(needed), flush=True)
bimd = {}          # rsid -> (A1, A2)  [needed only]
needed_idx = []    # (bim_index, rsid) for needed rsids, in bim order
with open(BIM) as f:
    for idx, line in enumerate(f):
        p = line.rstrip("\n").split("\t")
        if len(p) < 6:
            continue
        rsid, A1, A2 = p[1], p[4], p[5]
        if rsid in needed:
            bimd[rsid] = (A1, A2)
            needed_idx.append((idx, rsid))
print("needed rsids present in bim:", len(needed_idx), flush=True)

N_samples = sum(1 for _ in open(FAM))
print("samples:", N_samples, flush=True)

# ---------- 2. extract genotypes for needed rsids via seek ----------
print("extracting genotypes from bed (seek) ...", flush=True)
bytes_per_var = (N_samples + 3) // 4
geno = {}   # rsid -> np.int8 A2-copy-count (0/1/2), -1 missing
t0 = time.time()
with open(BED, "rb") as bf:
    for idx, rsid in needed_idx:
        bf.seek(3 + idx * bytes_per_var)
        raw = bf.read(bytes_per_var)
        if len(raw) < bytes_per_var:
            continue
        arr = np.zeros(N_samples, dtype=np.int8)
        for j in range(N_samples):
            bits = (raw[j >> 2] >> (2 * (j & 3))) & 3
            if bits == 0:
                arr[j] = 0      # hom A1
            elif bits == 2:
                arr[j] = 1      # het
            elif bits == 3:
                arr[j] = 2      # hom A2
            else:
                arr[j] = -1     # missing
        geno[rsid] = arr
print("genotypes extracted:", len(geno), "in %.1fs" % (time.time() - t0), flush=True)

# ---------- 3. SCZ GWAS (subset) ----------
# columns: CHROM ID POS A1 A2 FCAS FCON IMPINFO BETA SE PVAL NCAS NCON NEFF
print("parsing SCZ GWAS (subset) ...", flush=True)
scz = {}   # rsid -> (Z, A1_gwas)
with gzip.open(SCZ, "rt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        if len(p) < 11:
            continue
        rsid = p[1]
        if rsid not in needed:
            continue
        try:
            beta = float(p[8]); se = float(p[9])
        except ValueError:
            continue
        if se <= 0 or se != se:
            continue
        a1 = p[3]   # A1 = effect allele
        scz[rsid] = (beta / se, a1)
print("SCZ rsids kept:", len(scz), flush=True)

# ---------- 4. TWAS helper ----------
def twas_for_gene(rows):
    # rows: list of (rsid, ref, eff_allele, w)  [eff_allele = panel effect allele]
    W, Z, G = [], [], []
    for rsid, ref, eff, w in rows:
        if rsid not in scz or rsid not in geno or rsid not in bimd:
            continue
        A1, A2 = bimd[rsid]
        # panel effect-allele sign relative to A2
        if eff == A2:
            s = 1
        elif eff == A1:
            s = -1
        else:
            continue   # ambiguous / palindromic
        zval, a1g = scz[rsid]
        # GWAS effect-allele sign relative to A2
        if a1g == A2:
            t = 1
        elif a1g == A1:
            t = -1
        else:
            continue
        W.append(s * w)
        Z.append(t * zval)
        G.append(geno[rsid])
    if len(W) < 2:
        return None
    W = np.array(W, float); Z = np.array(Z, float)
    G = np.array(G, float)   # snps x samples
    for k in range(G.shape[0]):
        m = G[k] == -1
        if m.any():
            mean = G[k][~m].mean() if (~m).any() else 0.0
            G[k, m] = mean
    R = np.corrcoef(G)
    R = np.nan_to_num(R)
    R += RIDGE * np.eye(len(W))
    try:
        Ri = np.linalg.inv(R)
    except np.linalg.LinAlgError:
        Ri = np.linalg.pinv(R)
    num = W @ Ri @ Z
    den = math.sqrt(max(W @ Ri @ W, 1e-12))
    return num / den

# ---------- 5. per-gene TWAS ----------
con = sqlite3.connect(WDB); cur = con.cursor()
def fetch_panel(tbl, gene):
    if tbl == "eqtlgen":
        cur.execute("SELECT rsid, ref, alt, w FROM eqtlgen WHERE gene=?", (gene,))
        out = []
        for (r, ref, alt, w) in cur.fetchall():
            eff = alt if EQ_CONV == "alt" else ref
            out.append((r, ref, eff, w))
        return out
    else:
        cur.execute("SELECT rsid, ref, eff, w FROM %s WHERE gene=?" % tbl, (gene,))
        return [(r, ref, eff, w) for (r, ref, eff, w) in cur.fetchall()]

genes = [l.strip() for l in open(TARGET) if l.strip()]
if LIMIT:
    genes = genes[:LIMIT]
print("computing TWAS for", len(genes), "genes ...", flush=True)

res = {"gene": [], "eq": [], "wb": [], "nt": [], "multi": []}
t0 = time.time()
for gi, g in enumerate(genes):
    eq_rows = fetch_panel("eqtlgen", g)
    wb_rows = fetch_panel("gtex_wb", g)
    nt_rows = fetch_panel("gtex_nt", g)
    eqz = twas_for_gene(eq_rows)
    wbz = twas_for_gene(wb_rows)
    ntz = twas_for_gene(nt_rows)
    multi = None if (wbz is None or ntz is None) else (wbz + ntz) / math.sqrt(2)
    res["gene"].append(g); res["eq"].append(eqz); res["wb"].append(wbz)
    res["nt"].append(ntz); res["multi"].append(multi)
    if gi % 200 == 0:
        print("  %d/%d  (%.1fs)" % (gi, len(genes), time.time() - t0), flush=True)
con.close()

# ---------- 6. decomposition ----------
import json
def spearman(x, y):
    xs = [a for a, b in zip(x, y) if a is not None and b is not None]
    ys = [b for a, b in zip(x, y) if a is not None and b is not None]
    if len(xs) < 4:
        return None, 0, 0
    from scipy.stats import spearmanr
    r, p = spearmanr(xs, ys)
    same = float(np.mean(np.sign(xs) == np.sign(ys)))
    return float(r), int(len(xs)), same

src_r, src_n, src_same = spearman(res["eq"], res["multi"])
tis_r, tis_n, tis_same = spearman(res["wb"], res["nt"])

print("\n=== SANITY: corr(eqtlgen_Z, gtex_multi_Z) ===", flush=True)
print("  r =", round(src_r, 4) if src_r is not None else None,
      "n =", src_n, "same_dir =", round(src_same, 3) if src_same else None, flush=True)

print("\n=== SCZ 2x2 decomposition (limit=%d) ===" % LIMIT, flush=True)
print("  SOURCE axis (eQTLGen vs GTEx multi): rho=%s n=%d same_dir=%.1f%%" % (
    round(src_r, 3) if src_r is not None else None, src_n, src_same * 100 if src_same else 0), flush=True)
print("  TISSUE axis (GTEx WB vs GTEx NT):     rho=%s n=%d same_dir=%.1f%%" % (
    round(tis_r, 3) if tis_r is not None else None, tis_n, tis_same * 100 if tis_same else 0), flush=True)

out = {
    "limit": LIMIT, "total_genes": len(genes), "eq_conv": EQ_CONV,
    "source_axis": {"rho": src_r, "n": src_n, "same_dir": src_same,
                    "note": "eQTLGen_Whole_Blood vs GTEx multi-tissue Stouffer(WB,NT)"},
    "tissue_axis": {"rho": tis_r, "n": tis_n, "same_dir": tis_same,
                    "note": "GTEx Whole_Blood vs GTEx Nerve_Tibial"},
}
json.dump(out, open("_DEPRECATED_scz_self_implemented/_rdat_tmp/scz_decomp_limit%d.json" % LIMIT, "w"), indent=2)
print("\nwrote scz_decomp_limit%d.json" % LIMIT, flush=True)

# also persist per-gene Z for downstream analysis
import csv as _csv
with open("_DEPRECATED_scz_self_implemented/_rdat_tmp/scz_twas_results_limit%d.csv" % LIMIT, "w", newline="") as fh:
    wcsv = _csv.writer(fh)
    wcsv.writerow(["gene", "eqZ", "wbZ", "ntZ", "multiZ"])
    for i in range(len(res["gene"])):
        def f(v): return ("" if v is None else "%.6g" % v)
        wcsv.writerow([res["gene"][i], f(res["eq"][i]), f(res["wb"][i]),
                       f(res["nt"][i]), f(res["multi"][i])])
print("wrote scz_twas_results_limit%d.csv" % LIMIT, flush=True)

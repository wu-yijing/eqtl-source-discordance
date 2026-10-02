import sqlite3, csv, gzip, os, sys

OUT = "_DEPRECATED_scz_self_implemented/weights.db"
EQ_CSV = "_DEPRECATED_scz_self_implemented/_rdat_tmp/eqtlgen_weights.csv.gz"
WB_DB = r"E:/workbuddy/2026-06-26-23-06-20/mashr_eqtl/eqtl/mashr/mashr_Whole_Blood.db"
NT_DB = r"E:/workbuddy/2026-06-23-05-43-40/mashr_extracted/eqtl/mashr/mashr_Nerve_Tibial.db"

if os.path.exists(OUT):
    os.remove(OUT)
con = sqlite3.connect(OUT)
con.execute("CREATE TABLE eqtlgen (gene TEXT, rsid TEXT, ref TEXT, alt TEXT, w REAL)")
con.execute("CREATE TABLE gtex_wb (gene TEXT, rsid TEXT, ref TEXT, eff TEXT, w REAL)")
con.execute("CREATE TABLE gtex_nt (gene TEXT, rsid TEXT, ref TEXT, eff TEXT, w REAL)")
con.execute("CREATE INDEX IF NOT EXISTS ix_eq ON eqtlgen(gene)")
con.execute("CREATE INDEX IF NOT EXISTS ix_wb ON gtex_wb(gene)")
con.execute("CREATE INDEX IF NOT EXISTS ix_nt ON gtex_nt(gene)")

print("loading eQTLGen weights from gzip csv ...")
n = 0
buf = []
with gzip.open(EQ_CSV, "rt") as f:
    r = csv.reader(f); next(r)
    for gene, rsid, pos, ref, alt, w in r:
        buf.append((gene, rsid, ref, alt, float(w)))
        n += 1
        if len(buf) >= 200000:
            con.executemany("INSERT INTO eqtlgen VALUES (?,?,?,?,?)", buf)
            buf.clear()
if buf:
    con.executemany("INSERT INTO eqtlgen VALUES (?,?,?,?,?)", buf)
print("  eQTLGen rows:", n)

def load_gtex(db, table):
    c = sqlite3.connect(db); cur = c.cursor()
    cur.execute("SELECT gene, rsid, ref_allele, eff_allele, weight FROM weights")
    buf = []
    for gene, rsid, ref, eff, w in cur.fetchall():
        buf.append((gene, rsid, ref, eff, float(w)))
    c.close()
    con.executemany(f"INSERT INTO {table} VALUES (?,?,?,?,?)", buf)
    print(f"  {table} rows:", len(buf))

print("loading GTEx WB ...")
load_gtex(WB_DB, "gtex_wb")
print("loading GTEx NT ...")
load_gtex(NT_DB, "gtex_nt")

# distinct rsids across all panels
rs = set()
for tbl in ("eqtlgen", "gtex_wb", "gtex_nt"):
    for (r,) in con.execute(f"SELECT DISTINCT rsid FROM {tbl}"):
        rs.add(r)
print("distinct rsids across panels:", len(rs))
open("_DEPRECATED_scz_self_implemented/_rdat_tmp/needed_rsids.txt", "w").write("\n".join(sorted(rs)))

con.commit(); con.close()
print("weights.db built.")

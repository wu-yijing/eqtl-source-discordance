#!/usr/bin/env python3
"""HK-only S-PrediXcan - inline version, no backtick issues"""
import sqlite3, os, math, gzip, sys, time
import numpy as np
import pandas as pd
from scipy import stats

t0 = time.time()
# 2026-10-05: was the author's mashr model directory; now an environment lookup, like
# PLINK_PREFIX below, so no personal directory ships in code (code/README.md rule 3).
# The two model databases are registered external inputs — see data/external/SOURCES.tsv
# (`mashr_Whole_Blood.db`, `mashr_Nerve_Tibial.db`).
MODEL_DIR = os.environ.get('REPRO_MASHR_DB_DIR')
if not MODEL_DIR or not os.path.isdir(MODEL_DIR):
    sys.exit("REPRO_MASHR_DB_DIR is unset or not a directory. Fetch the two mashr eQTL "
             "model databases named in data/external/SOURCES.tsv and point "
             "REPRO_MASHR_DB_DIR at the directory holding mashr_Whole_Blood.db and "
             "mashr_Nerve_Tibial.db.")
# 2026-10-04: the LD panel prefix used to be an absolute path into the author's machine.
# It is the same file the archive already registers as an external input —
# `g1000_eur.zip`, see data/external/SOURCES.tsv — so it is now named by an environment
# variable and the script stops with a reason instead of failing later on a missing path.
PLINK_PREFIX = os.environ.get('REPRO_G1000_EUR_PREFIX')
if not PLINK_PREFIX:
    sys.exit("REPRO_G1000_EUR_PREFIX is unset. Fetch data/external/SOURCES.tsv row "
             "`g1000_eur.zip`, unpack it, and point REPRO_G1000_EUR_PREFIX at the "
             "PLINK prefix (without the .bed/.bim/.fam suffix).")
# 2026-10-05: was the author's GWAS directory; now an environment lookup (rule 3). These
# are the FinnGen R13 DR/DN/DPN summary statistics, registered in data/external/SOURCES.tsv.
GWAS_DIR = os.environ.get('REPRO_FINNGEN_DIR')
if not GWAS_DIR or not os.path.isdir(GWAS_DIR):
    sys.exit("REPRO_FINNGEN_DIR is unset or not a directory. Fetch the FinnGen R13 DR / DN "
             "/ DPN summary statistics named in data/external/SOURCES.tsv and point "
             "REPRO_FINNGEN_DIR at the directory holding them.")

HK_ONLY = ['B2M','UBC','TBP','HPRT1','GUSB','SDHA','HMBS','YWHAZ','PPIA','IPO8',
           'POLR2A','TFRC','ALDOA','PGK1','LDHA','TPI1','NONO','PUM1','PSMG2',
           'EEF1A1','RPL32','RPS20','CYC1']

for tissue in ['Nerve_Tibial', 'Whole_Blood']:
    for pheno in ['DR', 'DN', 'DPN']:
        print(f'=== {tissue} x {pheno} ===', flush=True)
        
        model_db = os.path.join(MODEL_DIR, f'mashr_{tissue}.db')
        conn = sqlite3.connect(model_db)
        
        extra = {}
        col_n = 'n.snps.in.model'
        q = 'SELECT gene, genename, "' + col_n + '" FROM extra'
        for row in conn.execute(q).fetchall():
            extra[row[1].upper()] = {'id': row[0], 'n_snps': row[2]}
        
        available = {g: extra[g.upper()] for g in HK_ONLY if g.upper() in extra}
        missing = [g for g in HK_ONLY if g.upper() not in extra]
        print(f'  Available: {len(available)}, Missing: {missing}', flush=True)
        
        if len(available) == 0:
            print(f'  No HK genes in model - skipping', flush=True)
            conn.close()
            continue
        
        # PLINK
        class PlinkReader:
            def __init__(self, prefix):
                self.bed = prefix + '.bed'
                self.bim = prefix + '.bim'
                with open(prefix + '.fam') as f: self.n = sum(1 for _ in f)
                self.snps = []
                with open(self.bim) as f:
                    for line in f:
                        p = line.strip().split()
                        self.snps.append({'rsid': p[1]})
                self.n_snps = len(self.snps)
                self.bpp = math.ceil(self.n / 4)
                print(f'  PLINK: {self.n} ind, {self.n_snps} SNPs', flush=True)
            def get_idx(self, rsid):
                for i, s in enumerate(self.snps):
                    if s['rsid'] == rsid: return i
                return -1
            def read(self, idx):
                with open(self.bed, 'rb') as f:
                    f.seek(3 + idx * self.bpp)
                    raw = f.read(self.bpp)
                d = np.zeros(self.n, dtype=np.float64)
                for i in range(self.n):
                    g = (raw[i//4] >> (i%4)*2) & 3
                    d[i] = 0.0 if g==0 else (1.0 if g==1 else (2.0 if g==2 else np.nan))
                m = np.nanmean(d)
                if np.isnan(m): m = 0.0
                return np.nan_to_num(d, nan=m)
        
        plink = PlinkReader(PLINK_PREFIX)
        
        # GWAS
        gw = {}
        gwas_map = {'DR': 'finngen_R13_DM_RETINOPATHY_EXMORE.gz',
                    'DN': 'finngen_R13_DM_NEPHROPATHY.gz',
                    'DPN': 'finngen_R13_DM_NEUROPATHY.gz'}
        gwas_file = os.path.join(GWAS_DIR, gwas_map[pheno])
        print(f'  Loading GWAS...', flush=True)
        with gzip.open(gwas_file, 'rt') as f:
            hdr = f.readline().strip().split('\t')
            cm = {h.lower(): i for i, h in enumerate(hdr)}
            for line in f:
                parts = line.strip().split('\t')
                rsid = parts[cm.get('rsids', 0)]
                if ':' in rsid and not rsid.startswith('rs'):
                    rsid = rsid.split(':')[0]
                try:
                    beta = float(parts[cm['beta']])
                    se = float(parts[cm['sebeta']])
                    if se > 0:
                        gw[rsid] = beta / se
                except:
                    pass
        print(f'  GWAS: {len(gw)} variants', flush=True)
        
        # Compute TWAS
        results = []
        for gname, info in available.items():
            gene = info['id']
            rows = conn.execute('SELECT rsid, weight, ref_allele, eff_allele FROM weights WHERE gene=?', (gene,)).fetchall()
            mod = [{'rsid': r[0], 'weight': r[1]} for r in rows]
            
            w, zs, matched = [], [], []
            for s in mod:
                if s['rsid'] in gw:
                    w.append(s['weight'])
                    zs.append(gw[s['rsid']])
                    matched.append(s)
            
            if len(matched) == 0:
                continue
            
            w_a = np.array(w)
            zs_a = np.array(zs)
            
            if len(matched) == 1:
                idx = plink.get_idx(matched[0]['rsid'])
                if idx < 0: continue
                d = plink.read(idx)
                ve = np.var(d, ddof=1)
                if ve <= 0: ve = 2*0.05*0.95
                pv = w_a[0]**2 * ve
                twas_z = w_a[0] * zs_a[0] / math.sqrt(pv) if pv > 0 else 0
            else:
                dl = []
                for s in matched:
                    idx = plink.get_idx(s['rsid'])
                    if idx < 0: break
                    dl.append(plink.read(idx))
                if len(dl) != len(matched): continue
                dm = np.vstack(dl).T
                cv = np.cov(dm, rowvar=False)
                pv = w_a @ cv @ w_a
                if pv <= 0: continue
                twas_z = np.dot(w_a, zs_a) / math.sqrt(pv)
            
            p = 2 * stats.norm.sf(abs(twas_z))
            results.append({'gene': gname, 'tissue': tissue, 'trait': pheno,
                           'zscore': round(twas_z, 4), 'pvalue': p,
                           'n_snps_matched': len(matched)})
            print(f'  {gname}: Z={twas_z:.2f}', flush=True)
        
        conn.close()
        
        # Save (2026-10-05). This step merges the recomputed HK rows into a previously
        # produced full run's per-tissue/trait CSV, replacing that file's HK rows. Its two
        # output paths used to be hard-coded — one of them the author's personal directory
        # (code/README.md rule 3). The directory is now an environment lookup; where it is
        # unset nothing is written, which is what already happened when the file was absent.
        # This step never *creates* a full run's file; it only updates one that exists.
        df_new = pd.DataFrame(results)
        out_dir = os.environ.get('REPRO_HK_OUT')
        if not out_dir:
            print('  [skip] REPRO_HK_OUT unset — recomputed HK rows were not merged into a '
                  'full run output (set it to the directory holding '
                  'gtex_<tissue>_<pheno>.csv).', flush=True)
        else:
            out = os.path.join(out_dir, f'gtex_{tissue}_{pheno}.csv')
            if os.path.exists(out):
                df_existing = pd.read_csv(out)
                existing_hk_mask = df_existing['gene'].str.upper().isin([g.upper() for g in HK_ONLY])
                df_remaining = df_existing[~existing_hk_mask]
                df_combined = pd.concat([df_remaining, df_new], ignore_index=True)
                df_combined.to_csv(out, index=False)
                print(f'  Saved to {out}: {len(df_combined)} rows', flush=True)
            else:
                print(f'  [skip] {out} does not exist — nothing to merge into.', flush=True)

print(f'\nTotal time: {time.time()-t0:.1f}s', flush=True)
print('ALL DONE!', flush=True)

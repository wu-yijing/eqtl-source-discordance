#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cross-population replication of the 2x2 eQTL-source x tissue decomposition.
- HK (East Asian) cohort: hk_twas_results.csv
- FinnGen (European) cohort: repo processed CSVs
Source axis = eQTLGen (Whole_Blood) vs GTEx multi-tissue (Stouffer WB+NT)
Tissue axis = GTEx Whole_Blood vs GTEx Nerve_Tibial
Unit of analysis = (gene x trait) pair; 'Pooled' uses all pairs across traits.
"""
import csv, math, os, json
import numpy as np
from scipy import stats

OUT = r"E:/workbuddy/2026-07-15-20-17-22/scz_replication"
HK = r"E:/workbuddy/2026-07-01-21-06-50/hk_twas_results.csv"
FG_CMP = r"E:/workbuddy/2026-06-27-20-58-07/TWAS-eQTL-source-confounding/data/processed/eqtlgen_vs_gtex_comparison.csv"
FG_STO = r"E:/workbuddy/2026-06-27-20-58-07/TWAS-eQTL-source-confounding/data/processed/gtex_stouffer_integrated.csv"
N_WB, N_NT = 670, 532  # GTEx tissue sample sizes (run_spredixcan.sh)

def fnum(s):
    if s is None: return None
    s = str(s).strip()
    if s in ("", "NA", "NaN", "None"): return None
    try: return float(s)
    except: return None

def stouffer(wb, nt):
    parts = []
    if wb is not None: parts.append((wb, N_WB))
    if nt is not None: parts.append((nt, N_NT))
    if not parts: return None
    if len(parts) == 1: return parts[0][0]
    num = sum(z*math.sqrt(n) for z,n in parts)
    den = math.sqrt(sum(n for _,n in parts))
    return num/den

def pair_stats(a, b):
    a2=[]; b2=[]; conc=0; n=0
    for x,y in zip(a,b):
        if x is None or y is None: continue
        a2.append(x); b2.append(y); n+=1
        if (x>0)==(y>0): conc+=1
    if n < 3:
        return dict(rho=None, p=None, concordance=None, n=n)
    rho,p = stats.spearmanr(a2,b2)
    return dict(rho=float(rho), p=float(p), concordance=100.0*conc/n, n=n)

# ---------------- load HK ----------------
hk = {}
with open(HK, encoding="utf-8-sig", errors="replace") as f:
    for row in csv.DictReader(f):
        ph=row["Phenotype"].strip(); g=row["Gene"].strip()
        hk.setdefault(ph, {})[g] = dict(
            wb=fnum(row.get("GTEx_Whole_Blood_Z")),
            nt=fnum(row.get("GTEx_Nerve_Tibial_Z")),
            eq=fnum(row.get("eQTLGen_Z")))

def axes_from_recs(recs):
    wb=[]; nt=[]; eq=[]; multi=[]
    for d in recs:
        wb.append(d.get("wb")); nt.append(d.get("nt")); eq.append(d.get("eq"))
        multi.append(stouffer(d.get("wb"), d.get("nt")))
    return pair_stats(eq, multi), pair_stats(wb, nt)

hk_results={}
hk_recs_all=[]
for ph in ["DR","DN","DPN"]:
    recs=[hk[ph][g] for g in hk[ph]]
    hk_results[ph]=axes_from_recs(recs)
    hk_recs_all+=recs
hk_results["Pooled"]=axes_from_recs(hk_recs_all)

# ---------------- load FinnGen ----------------
fg_cmp={}; fg_sto={}
with open(FG_CMP, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        fg_cmp.setdefault(row["Trait"].strip(), {})[row["Gene"].strip()] = \
            dict(eq=fnum(row["Z_eQTLGen"]), gtex=fnum(row["Z_GTEx"]))
with open(FG_STO, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        fg_sto.setdefault(row["Trait"].strip(), {})[row["Gene"].strip()] = \
            dict(wb=fnum(row["Z_Whole_Blood"]), nt=fnum(row["Z_Nerve_Tibial"]))

def fg_axes(eg_list, wn_list):
    eq=[x[0] for x in eg_list]; gtex=[x[1] for x in eg_list]
    wb=[x[0] for x in wn_list]; nt=[x[1] for x in wn_list]
    return pair_stats(eq, gtex), pair_stats(wb, nt)

fg_results={}; eg_all=[]; wn_all=[]
for ph in ["DR","DN","DPN"]:
    eg=[(d["eq"],d["gtex"]) for d in fg_cmp.get(ph,{}).values()]
    wn=[(d["wb"],d["nt"]) for d in fg_sto.get(ph,{}).values()]
    fg_results[ph]=fg_axes(eg, wn)
    eg_all+=eg; wn_all+=wn
fg_results["Pooled"]=fg_axes(eg_all, wn_all)

# ---------------- report ----------------
def fmt(d):
    if d["n"]<3 or d["rho"] is None: return f"n={d['n']} (insufficient)"
    return f"rho={d['rho']:+.3f}, concord={d['concordance']:.1f}%, n={d['n']}"

print("="*92)
print("CROSS-POPULATION 2x2 DECOMPOSITION REPLICATION  (unit = gene x trait pair)")
print("Source axis = eQTLGen(Whole_Blood) vs GTEx multi-tissue | Tissue axis = GTEx WB vs NT")
print("="*92)
for ph in ["DR","DN","DPN","Pooled"]:
    hk_s,hk_t=hk_results[ph]; fg_s,fg_t=fg_results[ph]
    print(f"\n[{ph}]")
    print(f"  SOURCE axis : HK {fmt(hk_s):48s} | FinnGen {fmt(fg_s)}")
    print(f"  TISSUE axis : HK {fmt(hk_t):48s} | FinnGen {fmt(fg_t)}")

rows=[]
for ph in ["DR","DN","DPN","Pooled"]:
    hk_s,hk_t=hk_results[ph]; fg_s,fg_t=fg_results[ph]
    for axis,(hk_d,fg_d) in [("source",(hk_s,fg_s)),("tissue",(hk_t,fg_t))]:
        rows.append(dict(Phenotype=ph, Axis=axis,
            HK_rho=hk_d["rho"], HK_concord=hk_d["concordance"], HK_n=hk_d["n"],
            FG_rho=fg_d["rho"], FG_concord=fg_d["concordance"], FG_n=fg_d["n"]))
with open(os.path.join(OUT,"replication_comparison.csv"),"w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["Phenotype","Axis","HK_rho","HK_concord","HK_n","FG_rho","FG_concord","FG_n"])
    w.writeheader(); w.writerows(rows)
print("\nSaved replication_comparison.csv")

# HK per-gene Z for figures
hk_genes={}
for ph in ["DR","DN","DPN"]:
    for g,d in hk.get(ph,{}).items():
        hk_genes.setdefault(g,{})[ph]=dict(wb=d["wb"],nt=d["nt"],eq=d["eq"],multi=stouffer(d["wb"],d["nt"]))
with open(os.path.join(OUT,"hk_per_gene.json"),"w") as f:
    json.dump(hk_genes, f, indent=1)
print("Saved hk_per_gene.json  (n genes =", len(hk_genes),")")

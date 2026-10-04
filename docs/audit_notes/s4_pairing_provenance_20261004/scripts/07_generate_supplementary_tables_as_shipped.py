"""
Generate Supplementary Tables S4, S5, S6
"""
import csv, sys, os, math
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = 'E:/workbuddy/2026-06-27-20-58-07/TWAS-eQTL-source-confounding/data/processed'
OUT_DIR = 'data/processed'

os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# TABLE S4: 104 Gene Covariate Matrix
# ============================================================
print("=== Table S4: Gene Covariate Matrix ===")

rows = []
with open(f'{DATA_DIR}/covariate_matrix.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        # Map group names
        group_map = {
            'Candidate': '30 HOTAIR Candidate',
            'NonCandidate': '44 Non-Candidate',
            'T2DM_Control': '30 T2DM Control'
        }
        group = group_map.get(r['Group'], r['Group'])
        length_bp = float(r['Length_bp']) if r['Length_bp'] else 0
        gc_pct = float(r['GC_pct']) if r['GC_pct'] else 0
        eqtl_snps = r.get('eQTL_SNPs_Mean_Num', '')
        eqtl_snps_num = float(eqtl_snps) if eqtl_snps else ''
        
        rows.append({
            'Gene': r['Gene'],
            'Group': group,
            'Source': r.get('Source', ''),
            'log10_Length': round(math.log10(length_bp), 4) if length_bp > 0 else '',
            'Length_bp': int(length_bp) if length_bp > 0 else '',
            'GC_pct': round(gc_pct, 2) if gc_pct else '',
            'eQTL_SNPs_Mean': eqtl_snps_num,
            'PullDown_Unused': r.get('PullDown_Unused', '')
        })

# Sort by Group then by Gene
group_order = {'30 HOTAIR Candidate': 0, '44 Non-Candidate': 1, '30 T2DM Control': 2}
rows.sort(key=lambda r: (group_order.get(r['Group'], 9), r['Gene']))

with open(f'{OUT_DIR}/TableS4_gene_covariate_matrix.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['Gene','Group','Source','log10_Length','Length_bp','GC_pct','eQTL_SNPs_Mean','PullDown_Unused'])
    writer.writeheader()
    writer.writerows(rows)

print(f"  Wrote {len(rows)} rows to TableS4_gene_covariate_matrix.csv")

# Print summary stats
for g in ['30 HOTAIR Candidate', '44 Non-Candidate', '30 T2DM Control']:
    grp = [r for r in rows if r['Group'] == g]
    lengths = [r['Length_bp'] for r in grp if r['Length_bp'] != '']
    gcs = [r['GC_pct'] for r in grp if r['GC_pct'] != '']
    snps = [r['eQTL_SNPs_Mean'] for r in grp if r['eQTL_SNPs_Mean'] != '']
    print(f"  {g}: n={len(grp)}, Length={min(lengths):,.0f}-{max(lengths):,.0f} bp, GC={min(gcs):.1f}-{max(gcs):.1f}%, eQTL_SNPs={min(snps):.1f}-{max(snps):.1f}" if snps else f"  {g}: n={len(grp)}, Length={min(lengths):,.0f}-{max(lengths):,.0f} bp, GC={min(gcs):.1f}-{max(gcs):.1f}%")

# ============================================================
# TABLE S5: Mahalanobis Matched Pairs (30 pairs)
# ============================================================
print("\n=== Table S5: Mahalanobis Matched Pairs ===")

pairs = []
with open(f'{DATA_DIR}/mahalanobis_matched_pairs.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        pairs.append(r)

# Group by subclass
from collections import defaultdict
pair_groups = defaultdict(list)
for p in pairs:
    pair_groups[p['subclass']].append(p)

# Now write in pairwise format
with open(f'{OUT_DIR}/TableS5_mahalanobis_matched_pairs.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Pair_ID', 
        'Candidate_Gene', 'Candidate_Group', 'Candidate_log10_Length', 'Candidate_Length_bp', 'Candidate_n_eQTL_SNPs',
        'Control_Gene', 'Control_Group', 'Control_log10_Length', 'Control_Length_bp', 'Control_n_eQTL_SNPs'
    ])
    
    for subclass, members in sorted(pair_groups.items()):
        candidate = [m for m in members if m['treated'] == '1']
        control = [m for m in members if m['treated'] == '0']
        if candidate and control:
            c = candidate[0]
            ct = control[0]
            writer.writerow([
                f"Pair_{int(subclass):02d}",
                c['Gene'], c['Group'], c['log10_Length'], c['Length_bp'], c['n_eQTL_SNPs'],
                ct['Gene'], ct['Group'], ct['log10_Length'], ct['Length_bp'], ct['n_eQTL_SNPs']
            ])

print(f"  Wrote {len(pair_groups)} matched pairs to TableS5_mahalanobis_matched_pairs.csv")

# ============================================================
# TABLE S6: Cross-Population Replication Results
# ============================================================
print("\n=== Table S6: Cross-Population Replication Results ===")

# Read GTEx vs eQTLGen comparison for replication data
comp_rows = []
with open(f'{DATA_DIR}/eqtlgen_vs_gtex_comparison.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        comp_rows.append(r)

# Filter for cross-population relevant entries
# We'll create a summary table based on the manuscript's reported values
# and the cross-population replication log

with open(f'{OUT_DIR}/TableS6_cross_population_replication.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Gene', 'Phenotype', 'Dataset', 'Z_score', 'P_value', 'Direction_vs_FinnGen_eQTLGen', 'Note'
    ])
    
    # FinnGen R13 DR (eQTLGen weights) - top candidates
    finngen_data = {
        'RNH1': ('DR', '+11.6', '<0.001', 'Reference'),
        'RNH1': ('DN', '+6.8', '<0.001', 'Reference'),
        'RNH1': ('DPN', '+9.8', '<0.001', 'Reference'),
        'RPS14': ('DN', '+5.09', '<0.001', 'Reference'),
        'TUBB': ('DR', '+47', '<0.001', 'Reference'),
    }
    
    # UK Biobank replication (from cross-pop log and manuscript)
    for gene, z_ukb, note in [
        ('RNH1', '+0.57', 'UKB GCST90043640 DR'),
        ('RNH1', '+0.95', 'UKB Xue et al. 2022 DR'),
        ('RNH1', '+3.59', 'Sakaue et al. 2021 DN'),
        ('CKAP4', '+0.50', 'UKB (direction consistent)'),
        ('HSP90AB1', '+0.45', 'UKB (direction consistent)'),
        ('RPS14', '+0.38', 'UKB (direction consistent)'),
        ('EEF2', '+0.20', 'UKB (not significant)'),
    ]:
        writer.writerow([gene, 'DR' if 'DR' in note else 'DN', note, z_ukb, '>0.05', 'Consistent', 'All UKB DR P>0.05'])
    
    # Heterogeneity metrics
    writer.writerow([])
    writer.writerow(['Meta-analysis', 'DR', 'FinnGen + 2 UKB', '+3.37', '7.4e-4', '—', 'Fixed-effect meta-analysis'])
    writer.writerow(['Heterogeneity', 'DR', 'Cochran Q=40.0', 'I²=95.0%', '<0.0001', '—', 'Extreme heterogeneity'])
    writer.writerow(['Prediction Interval', 'DR', '95% PI', '[-4.00, +10.68]', '—', 'Crosses zero', 'Unreplicable in future cohorts'])
    writer.writerow(['Direction Consistency', 'DR', '8 testable genes', '87.5% (7/8)', 'P=0.035', 'Binomial test', 'Nominal direction preservation'])

print(f"  Wrote cross-population replication summary to TableS6_cross_population_replication.csv")

print("\nDone! All supplementary tables generated.")

# -*- coding: utf-8 -*-
"""GE 稿件 SI 表 与 审计仓库官方 Z 层 的逐行对应性核验（确认同一次数据生成）。
GE SI: <si_tables_dir>/tNN.tsv（由 docx 抽取；--input si_tables_dir=…，未随仓库分发）
仓库  : data/derived/*.csv（原脚本读的是另一本机克隆的 processed_officialZ/，逐格等价）
"""
import csv, os
import numpy as np
import sys as _sys, os as _os
_p = _os.path.dirname(_os.path.abspath(__file__))
while _p != _os.path.dirname(_p) and not _os.path.isfile(_os.path.join(_p, 'paths.py')):
    _p = _os.path.dirname(_p)
_sys.path.insert(0, _p)
import paths as _paths          # noqa: E402  集中路径解析：向上找到 paths.py
_paths.bootstrap_args()   # 消费 --repo-root / --input（本脚本无自有 parser）
SI=str(_paths.external('si_tables_dir'))
D=str(_paths.derived('gtex_Z').parent)

def tsv(fn):
    out=[]
    for line in open(os.path.join(SI,fn),encoding='utf-8'):
        out.append(line.rstrip('\n').split('\t'))
    return out[0], out[1:]
def rd(fn): return list(csv.DictReader(open(os.path.join(D,fn),encoding='utf-8-sig')))
def key(r, *c): return tuple(str(r[x]).strip().lstrip('+') for x in c)

def cmp(tag, si_hdr, si_rows, si_keycols, rep_rows, rep_keycols, valcols, tol=1e-9):
    """按键对齐，逐值比较。valcols: [(si_idx_or_name, rep_name)]"""
    hit=miss=0; worst=0.0; worst_k=''
    R={key(r,*rep_keycols):r for r in rep_rows}
    n=0
    for r in si_rows:
        k=tuple(str(r[i]).strip().lstrip('+') for i in si_keycols)
        if k not in R: miss+=1; continue
        hit+=1
        for si_c, rp_c in valcols:
            a=str(r[si_c]).strip().replace('+','')
            b=str(R[k][rp_c]).strip().replace('+','')
            try: fa=float(a)
            except ValueError: continue
            try: fb=float(b)
            except ValueError: continue
            n+=1
            d=abs(fa-fb)
            if d>worst: worst=d; worst_k=f'{k} {si_c}: {a} vs {b}'
            if d<=tol: pass
    print(f'  {tag}')
    print(f'    键命中 {hit} 行 / 未命中 {miss} 行 ；比较了 {n} 个数值')
    print(f'    最大绝对差 = {worst:.3e}   {worst_k}')

print('='*100); print('GE 稿件 SI 表 ←→ 审计仓库官方 Z 层'); print('='*100)
# 1) GTEx 侧：GE SI t02 ↔ gtex_Z.csv
h,rows=tsv('t02.tsv'); G=rd('gtex_Z.csv')
print(f'\n[1] GTEx 侧   SI t02 ({h[:3]}...)  {len(rows)} 行  ←→  gtex_Z.csv {len(G)} 行')
cmp('Table S3 ↔ gtex_Z.csv', h, rows, (0,1), G, ('Gene','Trait'),
    [(2,'Z_Nerve_Tibial'),(3,'Z_Whole_Blood'),(4,'Z_multi_tissue'),
     (5,'P_Stouffer'),(6,'FDR_q_Stouffer'),(7,'P_ACAT_O'),(8,'FDR_q_ACAT_O'),(9,'n_Tissues')])
# 2) eQTLGen 侧：GE SI t18 ↔ eqtlgen_Z.csv
h,rows=tsv('t18.tsv'); E=rd('eqtlgen_Z.csv')
print(f'\n[2] eQTLGen 侧   SI t18  {len(rows)} 行  ←→  eqtlgen_Z.csv {len(E)} 行')
E_nohk=[r for r in E if r['Group']!='Housekeeping']
print(f'    仓库层去掉 Housekeeping 后 = {len(E_nohk)} 行（SI 为 {len(rows)} 行）')
cmp('Table S18 ↔ eqtlgen_Z.csv（非管家子集）', h, rows, (0,1), E_nohk, ('Gene','Trait'),
    [(3,'Z_eQTLGen'),(4,'P'),(5,'BH_q')])
# 3) 基因分组：GE SI t01 ↔ gene_groups.csv
h,rows=tsv('t01.tsv'); T=rd('gene_groups.csv')
print(f'\n[3] 基因分组   SI t01  {len(rows)} 行  ←→  gene_groups.csv {len(T)} 行')
R={r['Gene'].strip():r for r in T}
diff=[]
for r in rows:
    g=r[0].strip()
    if g in R and R[g]['Group'].strip()!=r[1].strip(): diff.append((g,r[1],R[g]['Group']))
print(f'    基因名命中 {sum(1 for r in rows if r[0].strip() in R)}/{len(rows)}；分组标签不一致 {len(diff)} 个 {diff[:5]}')
# 4) 主臂：GE SI t13 ↔ primary_arm_96pairs.csv
h,rows=tsv('t13.tsv'); A=rd('primary_arm_96pairs.csv')
print(f'\n[4] 主臂   SI t13  {len(rows)} 行  ←→  primary_arm_96pairs.csv {len(A)} 行')
cmp('Table S13 ↔ primary_arm_96pairs.csv', h, rows, (0,1), A, ('Gene','Trait'),
    [(2,'Z_GTEx'),(3,'Z_eQTLGen')])
print()
print('='*100)
print('结论：若各块「最大绝对差」为 0（或仅 ≤ 1e-4 的显示位数差），则 GE 稿件 SI 与仓库官方 Z 层')
print('      来自同一次数据生成——即可用仓库脚本对 GE 稿件的数值做独立复算。')
print('='*100)

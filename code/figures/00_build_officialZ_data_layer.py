# -*- coding: utf-8 -*-
"""
⚠️ DEPRECATED AS A BUILD STEP (2026-10-06) — FORENSICS ONLY, AND IT NOW REFUSES BY DEFAULT.
It reads the Supporting Information .docx and writes data/derived/ from it; data/derived/
is the layer every reported value is reproduced from, so this is a loop. See the
CIRCULARITY GUARD below and the authoritative path: code/run_upstream.sh.

P0 收口 Step 1：建立官方 Z 单一数据源 + 隔离标记陈旧数据层
- 从 Supporting Information 的官方表导出 data/derived/
- 在 data/superseded/ 保留弃用说明（不删除任何文件）

⚠️ 2026-10-02 — 路径随仓库重排更新；**表索引尚未随新 SI 重新校验**。
    本文按 `tabs[i]` 的**序号**读表，序号来自旧的 Additional file 1 版式
    （读的是第 2/4/14/16/19 张表）。现行 Supporting Information 已重排为
    Tables S1–S30 且插入了新表，序号**很可能已经错位**。
    → 使用前必须逐表核对：先用 `AF1_DOCX` 指向现行 SI，打印各表首行确认对应关系，
      再把下面的 `grid(i)` 序号改正。**在核对完成前，不要把本脚本的输出当作权威数据层。**
"""
import os, csv, json, shutil, sys
from docx import Document
from docx.table import Table
from docx.oxml.ns import qn
import paths_config as P  # 统一路径入口（2026-09-20）

AF = P.need(P.AF1, 'Additional file 1（从期刊补充材料下载后用 AF1_DOCX 指定）')
REPO = P.REPO
# 2026-10-02 — path update for the reorganized repository:
#   authoritative layer:  data/processed_officialZ/  ->  data/derived/
#   pre-correction layer: the former `data/processed` ->  data/superseded/
#   (2026-10-03: the trailing slash is deliberately omitted above. `code/run_all.sh`
#    greps this directory for the quarantined path and treated this comment as a live
#    reference, failing its own preflight. The guard matches a real path — i.e. the
#    directory name followed by `/` or a quote — so prose must not spell it that way.)
PROC = os.path.join(REPO, 'data', 'superseded')
NEW = os.path.join(REPO, 'data', 'derived')
META = os.path.join(REPO, 'metadata')

# ---------------------------------------------------------------------------
# CIRCULARITY GUARD — added 2026-10-06
# ---------------------------------------------------------------------------
# This script reads the Supporting Information .docx and writes data/derived/ from it.
# data/derived/ is the layer every reported value is reproduced FROM. Deriving it from a
# document that reports those values means the chain is a loop: run this and every
# downstream "reproduction" becomes a tautology — the numbers match because they were
# copied out of the document that printed them.
#
# It is therefore not a build step and must never be one. It is kept because it documents
# how the layer was first assembled, and because its table indices are a historical
# record; but writing data/derived/ is refused unless --allow-circular-write is passed,
# and even then the output goes to a directory whose name says what it is.
#
# The authoritative path from inputs to data/derived/ is code/run_upstream.sh (raw
# third-party inputs -> data/upstream/ -> the Z layer), verified by gate 9 of
# scripts/verify_from_clone.sh. Use that.
if '--allow-circular-write' not in sys.argv:
    print(__doc__.splitlines()[0] if __doc__ else '')
    print('  REFUSED: this script derives data/derived/ FROM the Supporting Information,')
    print('           which is itself derived from data/derived/. Running it would make')
    print('           every downstream "reproduction" circular.')
    print('')
    print('  The authoritative path is:  raw inputs -> code/run_upstream.sh -> data/derived/')
    print('  To run this anyway (forensics only), pass --allow-circular-write; the output')
    print('  then goes to data/superseded/_from_docx_NOT_authoritative/ and is not an input')
    print('  to anything.')
    raise SystemExit(2)

NEW = os.path.join(REPO, 'data', 'superseded', '_from_docx_NOT_authoritative')
print('  --allow-circular-write given: writing to %s' % os.path.relpath(NEW, REPO))
print('  This output is NOT an input to any pipeline step.')
os.makedirs(NEW, exist_ok=True)

d = Document(AF)
tabs = [b for ch in d.element.body.iterchildren()
        for b in ([Table(ch, d)] if ch.tag == qn('w:tbl') else [])]
grid = lambda i: [[c.text.strip() for c in r.cells] for r in tabs[i].rows]

def write_csv(name, header, rows):
    p = os.path.join(NEW, name)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print('  written %-38s %d rows' % (name, len(rows)))

# ---- GTEx 官方（Table S2）----
S2 = grid(1); h2 = S2[0]
gt = [r for r in S2[1:] if len(r) >= 10 and r[0]]
write_csv('gtex_Z.csv',
          ['Gene', 'Trait', 'Z_Nerve_Tibial', 'Z_Whole_Blood', 'Z_multi_tissue',
           'P_Stouffer', 'FDR_q_Stouffer', 'P_ACAT_O', 'FDR_q_ACAT_O', 'n_Tissues'],
          [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]] for r in gt])

# ---- eQTLGen 官方（Table S17 测试集 + Table S14 housekeeping）----
S17 = grid(18)
eq = [r for r in S17[1:] if len(r) >= 8 and r[0]]
rows = [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]] for r in eq]
try:
    S14 = grid(15)
    for r in S14[1:]:
        if len(r) >= 6 and r[0] and r[2]:
            rows.append([r[0], r[1], 'Housekeeping', r[2], r[3], r[4], r[5], 'Yes' if float(r[4]) < 0.05 else 'No'])
except Exception as e:
    print('  S14 merge skipped:', e)
write_csv('eqtlgen_Z.csv',
          ['Gene', 'Trait', 'Group', 'Z_eQTLGen', 'P', 'BH_q', 'Model_SNPs', 'FDR_significant'], rows)

# ---- 主比较 96 对（Table S12）----
S12 = grid(13)
write_csv('primary_arm_96pairs.csv', S12[0], [r for r in S12[1:] if len(r) >= 5 and r[0]])

# ---- 跨队列（Table S4）----
S4 = grid(3)
write_csv('crosscohort.csv', S4[0], [r for r in S4[1:] if len(r) >= 8 and r[0]])

# ---- 组分配（Table S1）----
S1 = grid(0)
write_csv('gene_groups.csv', S1[0], [r for r in S1[1:] if len(r) >= 2 and r[0]])

# ---- 弃用声明 ----
DEP = """# ⚠️ 本目录（旧名 data/processed，现已并入 data/superseded）已作废 —— 请勿用于出图或统计

**作废日期**：2026-09-17
**原因**：本目录下的 S-PrediXcan 输出产生于 **实现缺陷修正之前**。该版本的自研 S-PrediXcan 例程
（1）在多 SNP 模型的分母中遗漏了 σᵢ 表达方差因子，（2）PLINK 2-bit 基因型解码错误。
两个缺陷都会**系统性放大密模型基因的 |Z|**。

**证据（同基因同一统计量对比）**

| 基因（DR） | 本目录的值 | 官方 MetaXcan v0.8.1 的值 | 倍数 |
|---|---|---|---|
| TUBB（eQTLGen） | 48.516 | 11.8932 | ×4.1 |
| RNH1（eQTLGen） | 13.318 | 2.3064 | ×5.8 |
| RNH1（GTEx Nerve_Tibial） | 13.8246 | 2.6675 | ×5.2 |
| CKAP4（eQTLGen） | 4.7549 | 0.9874 | ×4.8 |
| CKAP4（GTEx Nerve_Tibial） | −3.2266 | −0.5622 | ×5.7 |
| DDX5（eQTLGen） | −3.8681 | −0.0049 | ×789 |

**受影响的下游产物（均已确认或需重绘）**

| 产物 | 读取的本目录文件 | 状态 |
|---|---|---|
| Figure 5（候选基因 dumbbell） | `eqtlgen_spredixcan_harmonized_results.csv`, `gtex_Nerve_Tibial_DR.csv` | ✅ 已重绘（2026-09-17） |
| Figure 7（RNH1 跨队列） | `eqtlgen_spredixcan_harmonized_results.csv`, `gtex_Nerve_Tibial_{DR,DN,DPN}.csv` | ✅ 已重绘（2026-09-17） |
| Figure 6（FDR 富集三面板） | `eqtlgen_spredixcan_harmonized_results.csv`（eQTLGen 侧） | ⏳ 待按同一流程重绘 |
| Figure 8（跨性状三基因集） | `gtex_Whole_Blood_{t}.csv`, `gtex_Nerve_Tibial_{t}.csv` | ⏳ 待按同一流程重绘 |
| Figure 2 / 4（协变量平衡 / 双轴分解） | 需确认是否读取本目录 | ⏳ 待确认 |
| Figure S2 / S3 / S5 | `_data_testbed_eqtlgen.csv`（同源） | ✅ 已重绘（2026-09-17） |
| 主稿 Table 4 的 RNH1 / CKAP4 行 | 同源 | ✅ 已更正（2026-09-17） |
| Additional file 1 Table S4 的 √N_e 行 | 旧 Z 对导出 | ✅ 已更正（2026-09-17） |

**请改用**：`data/processed_officialZ/`（由官方 MetaXcan v0.8.1 结果导出，与稿件 SI 中的
Table S2 / S12 / S14 / S17 / Table S4 逐值一致）。

**建议**：出图脚本一律从 `data/processed_officialZ/` 读数；本目录保留仅作历史对照，
并在下次归档（Zenodo/GitHub）时于 README 中标注为 superseded。
"""
# 2026-10-02: the pre-correction layer already carries its deprecation notice at
# data/superseded/ in the reorganized repository; do not rewrite it here.
print('  pre-correction layer: %s (notice not rewritten)' % PROC)

STALE = [f for f in sorted(os.listdir(PROC)) if f.endswith(('.csv', '.json', '.txt')) and 'DEPRECATED' not in f]
meta = dict(deprecated_at='2026-09-17',
            reason='pre-correction S-PrediXcan (missing sigma_i factor; PLINK 2-bit decoding bug)',
            superseded_by='data/derived/',
            official_reference='Supporting Information tables S2/S3/S13/S18/S5a; legacy concept DOI 10.5281/zenodo.21238202',
            stale_files=STALE)
os.makedirs(META, exist_ok=True)
open(os.path.join(META, 'provenance_source.json'), 'w', encoding='utf-8').write(
    json.dumps(meta, indent=1, ensure_ascii=False))
print('  %d pre-correction files listed' % len(STALE))
print('\nfiles now in data/derived:', sorted(os.listdir(NEW)))

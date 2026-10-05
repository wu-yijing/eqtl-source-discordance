# R 侧路径与规范卫生收口 —— 2026-10-05

本记录的输入是两份文档标出的"仍未闭合 6 项"：

- `../未闭合项核查_基于复现评估报告_20261005.md`（工作区 `2026-10-04-22-18-05/`，**不在本仓库内**）§2「仍未闭合（6 项）」；
- 其上游依据 `仓库复现可行性评估_eqtl-source-discordance_20261004.md`（核验 HEAD `0b5bd887`，同样不在本仓库内）§4 / §6。

本目录记录对其中六项的处置，**逐项实跑**，不转述。

---

## 0. 一句话结论

> **6 项全部闭合**：其中 5 项由本机改动 + 门禁坐实，第 6 项（上游全链）以**本机第一手 22/30 + 仓库归档的独立第三方 30/30** 两条腿闭环；过程中另发现 3 类既有缺陷（3 个审计目录的 `MANIFEST.sha256` 陈旧、1 处杂散 `</content>`、`.db` 哈希口径对 SQLite 版本敏感且版本未入档）。
> **三项"绝对路径"属仓库明确声明逐字节保留的历史记录，未改写**，理由见 §3——这是判断，不是遗漏。
> **核心判定不受影响**：数值级 / 图件级 / 门禁级三层未被触碰，且 12 道门禁在**全新克隆**中 **0 failure / 0 skip** 全绿。

---

## 1. 六项逐条

### 1.1 ✅ §2.1 `run_mahalanobis_matching.R` 非交互调用 —— 已修复

**原状**：`Rscript code/analyses/run_mahalanobis_matching.R` 报
`Error in sys.frame(1) : not that many frames on the stack`（`dirname → normalizePath → path.expand → sys.frame`），`EXIT=1`。

**根因（两处，逐层暴露）**：

| # | 缺陷 | 修复 |
|---|---|---|
| a | `SCRIPT_DIR <- dirname(normalizePath(sys.frame(1)$ofile))` —— `ofile` 只在 `source()` 下存在，`Rscript` 下 `sys.frame(1)` 直接崩 | 改为从 `commandArgs()` 的 `--file=` 取脚本目录，`source()` 回落 `ofile`，仓库根由 `.zenodo.json` 哨兵定位（符合 `code/README.md` 规则 3，无绝对路径） |
| b | 引导修好后暴露：`covar$Group == "Candidate"` 匹配不到任何行（矩阵的真实标签是 `30 HOTAIR Candidate`），treated 臂为空 | 标签改为逐字取用；池明确为"全部非候选"（74 基因，本脚本自身约定） |
| c | 再暴露：结尾 `summary(m.out)$sum.all[, c("Diff.Adj","Diff.Unadj")]` 在 MatchIt 4.7.x 下 `subscript out of bounds` | 改为版本无关的列名探测 |

**另**：输入由不存在的 `data/processed/` 改指随库的 `data/derived/covariate_matrix.csv`；输出改到 `$MAHALANOBIS_OUT`（默认 `<repo>/../_mahalanobis_out`），**绝不覆盖 `data/derived/` 的归档表**。

**实测**：

```
$ Rscript --vanilla code/analyses/run_mahalanobis_matching.R
  Treated (candidates): 27        # 3 个候选因 eQTL_SNPs_Mean 缺失被 na.omit 掉（脚本自身的 complete-case 视角）
  Control pool:         46
  Matched pairs: 27 / 27 (100%)
  Output written: .../_mahalanobis_out/mahalanobis_matched_pairs.csv
EXIT=0
```

**性质说明**：该脚本仍是**前身生成器**，池为 74 基因（含 30 个 T2DM 对照），与归档 SI Table S4（池 = 44 `Non-Candidate`）不同——这是 `GAP-11` 已记录的事实，本次**未改变其算法**，只让它能跑、不覆盖、并标明权威生成器在哪。

### 1.2 ✅ §2.1 权威生成器迁入 `code/` 正式路径 —— 已完成

`git mv docs/audit_notes/s4_specification_sweep_20261004/scripts/emit_S4_table.R code/analyses/emit_S4_table.R`

- 内容除一处防御性补丁（`dir.create(OUTD, ...)`，使生成器自建输出目录）外逐字节不变；
- 原审计目录加日期戳承续指针 `docs/audit_notes/s4_specification_sweep_20261004/MOVED_20261005.md`，**正文不改写**；
- 该目录 `MANIFEST.sha256` 同步重建（移除迁出条目、纳入指针文件）。

**实测（新路径、默认库 MatchIt 4.7.2）**：

```
$ Rscript --vanilla code/analyses/emit_S4_table.R . <out>
imputation reproduces the disclosed counts: 3 / 17 / 11
matched pairs: 30 / 30 candidates
candidate SET vs submitted : TRUE
control   SET vs submitted : 30 / 30
-- Table S26 under the re-emitted pairing --  (4 行，全部命中)
EXIT=0
```

### 1.3 ✅ §2.2 R 侧无门禁 —— 已补第 12 道门禁

`scripts/verify_from_clone.sh` 新增：

```
== 12. the SI Table S4 / S26 R path runs from the clone ==
```

- **有 Rscript 且 MatchIt 可加载时**：跑 `code/analyses/emit_S4_table.R`，断言 `candidate SET vs submitted : TRUE` 且 `control   SET vs submitted : 30 / 30`；不满足即 **FAIL**。
- **无 Rscript / MatchIt 不加载时**：`[skip]`（沿用门禁 5/7/8 的判据——读者环境不是归档缺陷）。
- 打印 `MatchIt` 版本与 `env/renv.lock` 的 pin（`4.5.5`）：相符 `[ ok ]`、不符 `[ warn ]`。**不强制版本**，因为控制集在 4.5.5 与 4.7.2 下实测相同（30/30 行 `match.matrix`，见 `s4_matchit_version_test_20261004/`）。

这直接回答了原报告的措辞："S4/S26 这条线至今没有一个'读者能一键跑通'的 R 路径"——现在有，而且 **由门禁携带**。

### 1.4 ⚠️→✅ §2.3 正式路径硬编码绝对路径 —— 9 处销除，3 处按声明保留

**处置**（`code/` 下非 `deprecated/`）：

| 脚本 | 原绝对路径 | 处置 |
|---|---|---|
| `analyses/m7_effect_size_supplement.py` | `E:/workbuddy/TWAS-eQTL-source-confounding` | → `$TWAS_M7_REPO`（未设则报错退出） |
| `analyses/robustness_check.py` | 3 处 GigaScience/临时目录 | → `$TWAS_ROBUSTNESS_{DATA,TABLES,OUT}` |
| `analyses/run_hk_control.py` | `MODEL_DIR` / `GWAS_DIR` / 输出路径 3 处 | → `$REPRO_MASHR_DB_DIR` / `$REPRO_FINNGEN_DIR` / `$REPRO_HK_OUT` |
| `analyses/round4_recompute/.../r14_recompute.py` | 2 处 | → `$TWAS_ROUND4_{BASE,GROUPS}` |
| `analyses/round4_recompute/.../r4_exact.py` | 2 处 | 同上 |
| `simulations/split_half_null/splithalf_null_simulation.py` | `BASE` | → `$TWAS_SPLITHALF_BASE` |
| `figures/recovered/gen_figs4.py` | 3 处 | → 仓库相对解析（见 §1.5） |

**保留（3 处，逐字节声明）**：`analyses/recovered/tost_ci_calculator.py`、`analyses/recovered/scz_arm_recount_si_fix.py`、`figures/ge_si/published/patch_figS1_20261001_verbatim.py`。
理由：这三个文件的存在**就是为了逐字节保留**（`code/analyses/recovered/README.md`："Nothing was edited, not even the hard-coded Windows paths they carry — those are part of the record"；`patch_figS1.py` 的 docstring 亦声明 `*_verbatim.py` 为"kept byte-for-byte"）。改写它们会销毁其唯一价值。**每处均已在 README 中披露并给出替代路径**。

**另**：`figures/ge_si/published/patch_figS1.py:15` 的"绝对路径"实为 **docstring 里的文字说明**（记录原始路径），非可执行路径——原报告将其计入违规，此处更正：**它不是违规**。
`figures/ge_main/unified_fig{2,3,4}.py` 三处为 `os.environ.get(...) or <默认>` 的**回退值**，`run_all.sh` 注入环境变量，属良性（原报告已作区分）。

### 1.5 ✅ §2.4 SI Fig. S2 提升到 clone 级 —— 已完成

- `code/figures/recovered/gen_figs4.py` 三处绝对路径销除：输入改为解析随库的
  `data/superseded/eqtlgen_spredixcan_harmonized_results.csv`（可用 `$FIG_S2_INPUT` 覆盖），输出到 `$FIG_S2_OUT`；并**自建输出目录**。
- **输入合法性**：该表是 pre-correction 层，但 Fig. S2 只用它的**模型 SNP 数** `n_snps_model`（拟合模型属性，不受 sigma_i / PLINK 修正影响）+ 有效 Z 的**存在性**做宇宙过滤；不用其 Z 值。此为 `run_all.sh` 唯一一处读 superseded 层的记录在案例外。
- **接入 `code/run_all.sh`**，每次运行断言三个发表中位数：

```
  [ ok ] recovered/gen_figs4.py (SI Fig. S2): medians 374 / 632 / 669 reproduce
```

- 文档同步：`figures/README.md`（Fig. S2 行 🟡→✅ / `none`→`clone`）、`metadata/ARCHIVE_MAP.md`（Fig. S2 行 + 汇总计数 27✅/11🟡 → **28✅/10🟡**，`check_archive_map.py` 已通过）、`code/README.md`、`code/figures/recovered/README.md`。

### 1.6 ✅ §2.6 stdout 重包致"看似卡死" —— 已消除

原报告称 `recompute_scz.py` 与 `simulation_validation.py` 用 `TextIOWrapper` 重包 stdout。**实测更正**：`recompute_scz.py` **并未**重包（全文件无 `io`/`sys.stdout` 赋值）；它只是 `print` 未 flush，管道下同样块缓冲。

两处根因、同一处置：

- 重包者加行缓冲：`io.TextIOWrapper(..., line_buffering=True)`——覆盖 `code/` 下非 `deprecated/`、非 `recovered/` 的**全部 10 处**（含 `code/upstream/` 4 个、`08_redraw_Fig6_labels_20260920.py`、`diag_s20.py`、`diag_s9_s20b.py`、`r14_recompute.py`、`r4_exact.py`、`simulation_validation.py`）；
- `recompute_scz.py` 的唯一输出点 `print(s)` → `print(s, flush=True)`。

**字节不变**（只改刷新时机；内容仍逐行入 `LOG` 并落 `results/`）。

### 1.7 ✅ §2.5 上游全链（raw → Z）—— 闭环（本机第一手 22/30 + 独立第三方 30/30）

见 §4。

---

## 2. 过程中发现并修复的既有缺陷

### 2.1 审计目录 `MANIFEST.sha256` 陈旧（3 个目录，**无门禁覆盖**）

全仓 7 个 `docs/audit_notes/*/MANIFEST.sha256` 逐一重算，结果：

| 目录 | 陈旧条目 |
|---|---|
| `open_items_closure_20261004` | `README.md` ×1 |
| `s4_matchit_version_test_20261004` | `README.md` + 3 个 logs/results |
| `upstream_chain_closure_20261004` | `README.md` + 8 个 logs/toolchain |
| 其余 4 个（含本次重建的 `s4_specification_sweep_20261004`） | 无 |

- 成因有两类：README 在 MANIFEST 生成后又被编辑；`.log` 未被 `.gitattributes` 显式声明（只受兜底规则 `* text=auto eol=lf` 管，结果同为 LF），而 MANIFEST 记录的是**规范化之前的 CRLF 工作副本**哈希。
- **git 侧干净**（`git status` 空），即漂移先于本次工作，非本次改动所致。
- **已修复（2026-10-05，应要求）**：3 个目录的 `MANIFEST.sha256` 均按**当前提交字节**重算，并在各目录留下日期戳说明 `MANIFEST_REPAIR_20261005.md`（载明漂移条目与成因）。重算后 `sha256sum -c` 分别 **17 / 13 / 21 条全通过**。**未改动任何被哈希文件的内容**。同时把 `*.log` 显式写入 `.gitattributes`（`text eol=lf`），消除该歧义。`upstream_chain_closure_20261004/ledger/`（含主证据 `middleware_ledger.tsv`）**未漂移**，其 30/30 结论不受影响。
- 仍建议：给 `docs/audit_notes/*/MANIFEST.sha256` 补一道门禁（§5 待办 2），否则同类漂移仍会复现。

### 2.2 杂散 `</content>`（1 处）

`code/figures/recovered/README.md` 末行原为一枚孤立的 `</content>`（写入残留）。全仓扫描确认**仅此一处**，已删除。

### 2.3 `.db` 中间件的哈希口径对 SQLite 版本敏感，且版本未入档

见 §4.2 —— `middleware_ledger.tsv` 与 `code/upstream/verify_middleware.py` 对 4 个 SQLite 库用 `file-sha256`，而库的物理页布局随 SQLite 写入器版本变化；归档 `toolchain/versions.txt` 未记录 sqlite 版本。本机（Python 3.12.3 / SQLite 3.45.1）复建的四库**尺寸与内容与归档完全一致，仅字节不同**。建议：入档 sqlite 版本，并对 `.db` 改用内容级比对。

---

## 3. 未做 / 明确例外的三件事

1. **`code/analyses/recovered/`、`patch_figS1_20261001_verbatim.py` 的绝对路径不改**——理由见 §1.4。
2. **`code/figures/README.md` 的中文"未覆盖项"段**提到"Fig. 2 …… 其生成脚本不在本目录（`定稿资料` 侧的 `gen_figs4.py` 系列）"。该段的图号体系与英文表不同（疑似指协变量平衡 SMD 图），**语义存疑，未擅改**，留待作者确认（§5 待办）。
3. **不推送远端**：本轮全部改动仅落在本地克隆的提交里。

---

## 4. 上游全链本机实测（§2.5）

### 4.1 材料与环境

- **15 项第三方输入**：`/e/workbuddy/_ext_stage_20261004/`（4.4 GB），文件名与 `data/external/SHA256SUMS` 逐一对应。
- **本机第一步实测**：

```
$ python scripts/verify_external_inputs.py --dir /e/workbuddy/_ext_stage_20261004
ok 15   mismatched 0   incomplete 0   missing 0   (of 15)
```

- **第二解释器环境**：`E:/Python312`（3.12.3）建 venv，装 `numpy 1.26.4 / scipy 1.13.1 / pandas 2.2.3`——对齐 `env/environment-upstream.yml`。
- **官方 MetaXcan v0.8.1**：由 `MetaXcan-v0.8.1.tar.gz` 解包，`METAXCAN_SW=.../MetaXcan-0.8.1/software`。

### 4.2 运行与结果

**未在本机重跑完整 3 带**：按"调取仓库前期已归档的验证资料"的思路，改为**本机第一手 + 仓库既有独立验证**两条腿。

#### (a) 本机第一手（`UPSTREAM_OUT=E:/workbuddy/_upstream_run`）

| 步骤 | 实测 |
|---|---|
| 0 输入哈希 | `ok 15 / mismatched 0 / incomplete 0 / missing 0` |
| 1 FinnGen 归并 | DR / DN / DPN **各 37,192 行**——与 `run_upstream.sh` 注释记载的 37,192 一致 |
| 2 GTEx 协方差 | `cov_Whole_Blood.txt.gz`（476,502 B）、`cov_Nerve_Tibial.txt.gz`（646,597 B）生成 |
| 3 GTEx S-PrediXcan | 6/6 生成，且 6 个文件**字节数与归档逐一相同**（NT: 2,259,160 / 2,256,166 / 2,254,949；WB: 1,837,692 / 1,835,601 / 1,834,688） |
| 4 eQTLGen 权重库 | `eQTLGen_Whole_Blood.db` 4,866,048 B（= 归档） |
| 5 分带 | `db_A/B/C` = 3,469,312 / 1,007,616 / 380,928 B（**三者字节数均 = 归档**）+ `cov_A.txt.gz` 183,659,809 B（= 归档） |
| 6 对齐 | `gwas_{DR,DN,DPN}_aligned.tsv` 生成 |
| 7 eQTLGen S-PrediXcan | A 带 3/3 生成，字节数 14,261 / 14,260 / 14,256（**= 归档**） |
| 8 中间件校验 | `python code/upstream/verify_middleware.py --run-dir <run>` → **`identical 18 | differing 4 | missing 8`（of 30）** |

**那 4 个 `differing` 全是 SQLite `.db`**，且尺寸与内容都相同：

```
eqtlgen/eQTLGen_Whole_Blood.db  归档=4,866,048  本机=4,866,048
eqtlgen/db_A.db                 归档=3,469,312  本机=3,469,312
eqtlgen/db_B.db                 归档=1,007,616  本机=1,007,616
eqtlgen/db_C.db                 归档=  380,928  本机=  380,928

内容级比对（schema + 全表逐行有序 SHA-256）：
  eQTLGen_Whole_Blood.db  MATCH   weights 65,622 / extra 103
  db_A.db                 MATCH   weights 46,919 / extra  94
  db_B.db                 MATCH   weights 13,671 / extra   8
  db_C.db                 MATCH   weights  5,032 / extra   1
```

**成因**：仓库 `toolchain/versions.txt` 记录了 `python 3.12.15 / numpy 1.26.4 / scipy 1.13.1 / pandas 2.2.3`，**未记录 sqlite 库版本**；本机为 `python 3.12.3 + SQLite 3.45.1`。SQLite 的物理页布局随写入器版本变化，而 `middleware_ledger.tsv` 对 `.db` 用的是 `hash_kind = file-sha256`（`.gz` 用 `content-md5`）。**故这 4 项的"字节可复现性"依赖 Python/SQLite 版本，而该版本未入档。**

**8 个 missing** = `cov_B.txt.gz` / `cov_C.txt.gz`（本机未构建，99 MB / 111 MB，构建耗时）+ 6 个 B/C 带 S-PrediXcan 输出。即 **B、C 两带未在本机重跑**。

#### (b) 调取仓库前期已归档的独立验证

| 材料（均在仓库内） | 内容 |
|---|---|
| `docs/audit_notes/upstream_chain_closure_20261004/README.md` | 2026-10-04 由**作者以外的一方**在 HEAD `7742953` 端到端执行：`EQ_TAG=A/B/C` 三次 `exit=0`，step 8 → `identical 30 | differing 0 | missing 0` |
| `.../ledger/middleware_ledger.tsv` | 30 行台账，**30 × MATCH / 0 × MISMATCH**；期望值转录自 `data/external/README.md` 散文（**第二实现**，独立于归档自带校验器） |
| `.../ledger/archive_verifier.txt` | 归档自带 `verify_middleware.py` 指向该次运行目录的输出 |
| `.../toolchain/` | python 3.12.15 / numpy 1.26.4 / scipy 1.13.1 / pandas 2.2.3；MetaXcan v0.8.1 tarball SHA-256 = `SHA256SUMS` 行；`SPrediXcan.py` 执行件哈希 |
| `.../inputs/` | 15 项输入 staging 台账 + 归档自有校验器输出（含关键的 `incomplete 0`） |
| `.../logs/upstream_A/B/C.log` | 三次运行的完整 stdout |
| `data/upstream/`（随库 31 MiB） | 中间件本体。`verify_middleware.py --run-dir data/upstream` → **27 identical / 3 missing**（缺的 3 个分带协方差超出 GitHub 100 MiB 硬限，无法分发，改用内容哈希钉住） |

#### (c) 结论

- **第一手**：GTEx 臂 6 项 + GWAS 归并 3 项 + 对齐 3 项 + GTEx 协方差 2 项 + eQTLGen A 带 4 项 —— **18 项字节级通过**；4 个 SQLite 库**内容级通过**；合计 **22/30 由本机独立坐实**。
- **其余 8 项**（B、C 两带）：由 **2026-10-04 独立第三方的 30/30 归档台账**坐实。
- **新发现（建议修）**：`.db` 的 `file-sha256` 口径对 SQLite 写入器版本敏感，而该版本未入档 → 建议 `toolchain/versions.txt` 增记 `sqlite3.sqlite_version`，并把 `.db` 也改为**内容级**比对（与 `.gz` 一致）。**不影响本次结论**（内容已验证相同），但会让"30/30"在将来更换 Python 补丁版本时仍可复现。

**第 5 项判定：闭环** —— "原始数据 → 中间件 → Z 层"这一段，现有**本机第一手 22/30** 与**独立第三方 30/30** 双重支撑，且两者差异点已定位到"SQLite 字节镜像"这一可解释、并附修补建议的具体项。

---

## 5. 待办（本轮明确留下的）

| # | 事项 |
|---|---|
| 1 | ~~3 个审计目录的 `MANIFEST.sha256` 重建（§2.1）~~ **2026-10-05 已完成**；`.gitattributes` 已为 `*.log` 增补显式 `text eol=lf` |
| 2 | 给 `docs/audit_notes/*/MANIFEST.sha256` 增一道门禁——当前**没有任何门禁校验它们**，这正是 §2.1 能长期存在的原因 |
| 3 | 确认 `code/figures/README.md` 中文"未覆盖项"段的图号语义（§3.2） |
| 4 | `run_mahalanobis_matching.R` 是否应彻底退役（移入 `deprecated/`）——鉴于其池约定与归档表不同，保留为"对照生成器"还是退役，属编辑决定 |
| 5 | **`.db` 哈希口径**（§2.3 / §4.2）：`toolchain/versions.txt` 增记 `sqlite3.sqlite_version`；`middleware_ledger.tsv` 与 `verify_middleware.py` 对 `.db` 改用内容级比对（与 `.gz` 的 `content-md5` 一致） |
| 6 | 若要完全第一手：补跑上游链 B、C 两带（构建 `cov_B` / `cov_C` 约 99 / 111 MB，加 6 次 S-PrediXcan），即可把本机口径从 22/30 推到 26/30 字节级 + 4 内容级 |

---

*本记录的全部状态来自 2026-10-05 本机实跑（R 4.5.2 + MatchIt 4.7.2/4.5.5、Python 3.13.12 主环境、Python 3.12.3 上游环境、MetaXcan v0.8.1）。除运行产物外未改动仓库受控文件以外的东西；`git status` 自检干净后提交。*

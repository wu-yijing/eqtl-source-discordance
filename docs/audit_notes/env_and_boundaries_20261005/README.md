# R 环境还原路径与复现边界的实测记录 —— 2026-10-05

本记录处理 2026-10-05 交付报告《三项复现缺口核验与收口报告》§2 / §3 列为"仍存边界"的四项。
**逐项实跑**，不转述。

---

## 1. ✅ `renv.lock` → R 环境：路径已实测走通，但它是**两步**，不是"一键"

### 1.1 原状（问题为真）

`env/README.md` 原文写：*"`renv.lock` | R dependencies. Restore with `Rscript -e 'renv::restore()'`."*
但仓库**没有 `renv/` 目录、没有 `.Rprofile`** —— 即该命令此前**从未有人执行过**，也就从未被任何门禁携带。

### 1.2 实测（本机 R 4.5.2 / renv 1.3.0 / Rtools45）

在**临时目录**（`/tmp/renvtest`，显式 `library=` 指向临时库，**不触碰系统库**；系统库 MatchIt 4.7.2 事后复核未变）：

```
$ Rscript -e 'renv::restore(project=getwd(), library="<tmp>/rlib", prompt=FALSE)'
The following package(s) will be updated:
- MatchIt         [4.7.2 -> 4.5.5]
- Rcpp            [1.1.1-1.1 -> 1.0.12]
- RcppArmadillo   [15.2.7-1 -> 0.12.8.4.0]
- cobalt          [5.0.0 -> 4.5.2]
- optmatch        [0.10.8 -> 0.10.6]
...
y RcppArmadillo 0.12.8.4.0   [copied from cache in 2.4s]
y cobalt 4.5.2               [copied from cache in 0.54s]
y Rcpp 1.0.12                [copied from cache in 2.9s]
y MatchIt 4.5.5              [copied from cache]
...
map.cc:164:28: error: 'Calloc' was not declared in this scope; did you mean 'calloc'?
ERROR: compilation failed for package 'optmatch'
```

**`optmatch` 0.10.6 在 R ≥ 4.5 下编译失败** —— 与 `env/README.md` §"optmatch and R ≥ 4.5 — one patch is required" 的预言**逐字一致**（R 4.5 移除了未加前缀的 `Calloc`/`Free`）。即 **`restore()` 单独跑永远无法收尾**，这不是环境意外，是归档已披露的设计。

### 1.3 套用随库补丁后收尾

```
$ tar -xzf optmatch_0.10.6.tar.gz && cd optmatch
$ patch -p2 < env/patches/optmatch-0.10.6-R4.5-calloc.patch      # 59 处调用改名，无其它内容
$ R CMD INSTALL --no-multiarch --library=<tmp>/rlib optmatch
* DONE (optmatch)
```

补丁落地计数（`R_Calloc` / `R_Free` 出现次数）：`map.cc 8`、`r_smahal.cc 2`、`smahal.cc 45`、`subsetInfSparseMatrix.cc 4`，合计 **59**，与 `env/README.md` 记的 63 处同源（口径含 `C` 而非 `R_` 前缀的少量行）。

### 1.4 用还原出的库验证结果（关键一步）

```
$ R_LIBS=<tmp>/rlib Rscript --vanilla code/analyses/emit_S4_table.R . <out>
MatchIt : 4.5.5 from <tmp>/rlib/MatchIt
R       : R version 4.5.2 (2025-10-31 ucrt)
imputation reproduces the disclosed counts: 3 / 17 / 11
matched pairs: 30 / 30 candidates
candidate SET vs submitted : TRUE
control   SET vs submitted : 30 / 30
  submitted control not selected :
EXIT=0
```

**即：`env/renv.lock` → 还原（+ 补丁）→ 完整钉版栈 → SI Table S4 控制集 30/30，全链走通。**

### 1.5 判定与后果

- **`renv.lock` 可还原**，路径已由本机实测坐实；`env/README.md` 的命令已按实测更正为**两步**。
- **它不适合做成离线克隆门禁**：还原需要网络（CRAN archive）与编译（Rtools），而 `verify_from_clone.sh` 的其余门禁**一律离线**。故仍不由门禁携带——但这不是"未验证"，而是"已验证 + 已知不适合门禁化"，两者不同。
- **一步到位是做不到的**，且这不是缺陷：`optmatch` 只被 `method = "optimal"` 与 `method = "full"` 触达，而报告所依据的匹配是 `method = "nearest"` + `distance = "mahalanobis"`，**根本不碰 `optmatch`**。

---

## 2. ✅ SI Fig. S1 残差 2,044 px：已测到**栅格化器下限**

在 PyMuPDF 1.27.2.3 下把同一份 `FigureS1.pdf` 用四种调用方式栅格化，与发表件比较：

| 调用 | 结果 |
|---|---|
| `get_pixmap(dpi=600)` | 3189 × 3077，20,364 px 不同（含改字） |
| `get_pixmap(matrix=Matrix(600/72, 600/72))` | **完全相同** |
| `get_pixmap(dpi=600, alpha=False, annots=False)` | **完全相同** |

本机**不存在**任何其它 PDF 栅格化器（`gs` / `pdftoppm` / `magick` / `mutool` / `qpdf` 均缺）。

**判定**：那 2,044 px（0.0208 %，单行文字）是"两个栅格化器对同一 PDF 的字形抗锯齿"差，**在本机不可再降**。注意它**不影响**发表件本身的可复现性——`ge_si/published/` + `verify_published.py` 仍以 **0 px** 逐像素复现提交的 SI 媒体（门禁 8）。

---

## 3. ✅ SI Table S4 的候选人处理顺序：确认**不可**由随库矩阵推导

30 个候选按 `PullDown_Unused` 非递增排列，前 15 名取值互异，**后 15 名全部并列于 0**——顺序的不确定性**只**在这 15 个之内。

投稿件中该并列块的顺序为：

```
XRCC5, H2AFV, RPS13, XRCC6, ACTB, RPS3, DDX5, EIF4H, ILF2, RPL23A,
HNRNPA3, YWHAQ, RPL13A, RPS18, RPS25
```

逐键检验（均**不符**）：

| 键 | 升序结果（前 4） | 降序结果（前 4） |
|---|---|---|
| `Gene` | ACTB, DDX5, EIF4H, H2AFV | YWHAQ, XRCC6, XRCC5, RPS3 |
| `Length_bp` | RPS25, ACTB, RPL23A, RPS18 | XRCC5, YWHAQ, XRCC6, ILF2 |
| `GC_pct` | XRCC5, XRCC6, RPS3, DDX5 | ACTB, RPL13A, RPS18, HNRNPA3 |
| `eQTL_SNPs_Mean` | RPS3, DDX5, ACTB, RPL13A | XRCC5, H2AFV, RPS13, XRCC6 |
| `covariate_matrix.csv` 行序 | ACTB, DDX5, EIF4H, H2AFV | — |
| `panel104.txt` 顺序 | ACTB, DDX5, EIF4H, H2AFV, … | YWHAQ, XRCC6, XRCC5, RPS3, … |

**判定**：该顺序**不是**任何可辨识排序键的产物，**不可由随库矩阵或原始面板文件推导**——`ARCHIVE_MAP.md` §5 GAP-11 的表述（"tie-break 不可从随库矩阵恢复"）**成立**。
**但这是归因缺口，不是复现缺口**：该顺序**随库分发**（在 `data/derived/mahalanobis_matched_pairs.csv` 的候选块，与投稿件逐字节相同），`emit_S4_table.R` 从它读取，故 **30/30 仍可从一次全新克隆复现**（门禁 12）。

---

## 4. ⏸ `subclass` 列的一次性命令

*规则*已从 git 历史恢复（前身库提交 `1389407` 的 diff 即该步骤），并 **30/30 验证**（`s4_pairing_provenance_20261004/scripts/reconstruct_pairing.py`）。*写该列的那条一次性命令本身*未恢复。本轮**未取得新证据**，维持原表述。

---

## 5. 材料

| 文件 | 内容 |
|---|---|
| `MANIFEST.sha256` | 本目录受控文件哈希 |

复现环境：R 4.5.2（`D:/R/R-4.5.2`）+ renv 1.3.0 + Rtools45；Python 3.13.14 + PyMuPDF 1.27.2.3。
证据目录（本机，不入库）：`/tmp/renvtest/`（`restore2.log`、`op/install.log`、`s4.log`）。

*本记录数值全部来自 2026-10-05 本机实跑；除本目录新增文件与 `env/README.md` 的一处命令更正外，未改动仓库其它受控文件的内容。*

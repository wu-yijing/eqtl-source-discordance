# 复现笔记清理：过时"未复现"标记的处置与保留策略

日期：2026-10-07
范围：仓库内所有"未复现 / NOT REPRODUCED"类标记及其配套说明
结论：**清理只动了"现状断言"，没有动任何一条负结果、任何一次测量、任何一个数值。**

---

## 0. 一句话结论

`SI Table S4` 与 `SI Table S26` 现在已经复现，`metadata/ARCHIVE_MAP.md` 长期计数为
**0 🔴 / 0 ❌**，但"报告旧状态的散文"仍留在五处载体中。本次把散文改成与现状一致，
**保留**它下面每一条仍然成立的发现，并保留下这套词汇本身。

## 1. 清理前先验证"确实已复现"

删除任何标记之前，先用仓库自带的工具把"未复现"这一判断本身推翻，而不是靠文本比对：

| 命令 | 结果 |
|---|---|
| `python code/analyses/reproduction_min/reproduce_headline.py` | `checks: 15   mismatches: 0` |
| `python scripts/check_s4_order.py` | 顺序文件 == 表内候选行 30/30；`PullDown_Unused` 非增；positions 16–30 仍不可导出 |
| `python docs/audit_notes/s4_q1_reproduction_20261004/scripts/verify_q1.py <out-dir> .` | **Q1 REPRODUCED**；控制集 30/30；差异仅 28/61 行（配对）；`q1_verification.json` 与已提交版本**逐字节相同** |
| `python docs/audit_notes/s4_specification_sweep_20261004/scripts/s26_recompute.py .` | **4 / 4 contrasts MATCH**，两种配对下分母 84/60/81/57 一致 |
| `python scripts/check_archive_map.py` | 47 行、30 ✅ / 8 🟡 / **0 🔴 / 0 ❌** / 9 ➖ |
| `bash scripts/verify_from_clone.sh` | **0 failure / 4 skip**；门禁 12 独立复现 `emit_S4_table.R` → 控制集 30/30、插补计数 3/17/11 |

`verify_q1.py` 需按文档传入"本次运行输出目录"；直接以 `.` 调用会因读不到该次运行的
`.csv` 而打印 `Q1 NOT REPRODUCED`。这是调用方式问题，不是档案缺陷——记录于此，因为它
正是"标记看起来仍成立、其实已过时"的典型来源。

## 2. 分诊规则：三类，处置不同

清理不按"文件里有没有 ❌"来删，而按**这句话是对现状的断言，还是对某一天测量的记录**来分：

| 类 | 判据 | 处置 |
|---|---|---|
| **A 过时的现状断言** | 无日期化、面向读者的文档里，用现在时描述一个已经不成立的状态 | **删除或改写**为与现状一致 |
| **B 日期化记录中被推翻的判定** | `docs/audit_notes/*_2026xxxx/` 的笔记正文 | **不删正文**；在该处就地加日期化更正，指明被哪一次 pass 推翻 |
| **C 仍然有效的机制与负结果** | 状态键、门禁脚本、发布规则、以及仍成立的负结果 | **一律不动** |

## 3. 逐项清单

### 3.1 删除（A 类）

| 文件 | 原表述 | 处置 |
|---|---|---|
| `README.md` | 保留段 `**The text this replaced, kept because the distinction it draws is the point — written 2026-10-04, superseded 2026-10-06, not rewritten.**` 及其下整段引文（"One item is marked ❌ NOT REPRODUCED…SI Table S26 is 🔴"） | **整段删除** |
| `README.md` | 上一条 bullet 开头 `No item is marked ❌ or 🔴 any more — and the paragraph that said one was is kept below…` | 改为 `**No item is marked ❌ or 🔴.**`，不再向下指 |
| `metadata/ARCHIVE_MAP.md` | 计数行后半段：`The line previously read 16 ✅ / 13 🟡 / 9 🔴 / 8 ➖…The two 🔴 rows were Figs. S1 and S2…` | **删除**；保留"计数由门禁机器核对"这一仍有效的机制 |
| `metadata/ARCHIVE_MAP.md` | `The ❌ and the 🔴 below are what that audit found` | 改为 `What that audit found, and how each row was moved back, is below`（下方已无此类行，指针是错的） |
| `metadata/ARCHIVE_MAP.md` | `as S4 now demonstrates — ❌ with clone` | 改为 `while S4 stood that way on 2026-10-04 — ❌ with clone was not one either`（S4 已不是 ❌ 行） |
| `metadata/ARCHIVE_MAP.md` | §5 GAP-11 结论 `Still unrecorded, and now down to a single column: how that set's subclass column came to be sorted … no artefact records that step` | 改为**已归属**：该步骤是前身仓库 commit `1389407`，规则可从克隆复现 30/30；仍缺的只是作者当时写 rank-zip 的那条一次性命令 |
| `docs/audit_notes/INDEX.md` | 两行摘要的收尾判定：`S4 stays ❌ NOT REPRODUCED…still unrecorded`、`ARCHIVE_MAP.md marks S4 ✅ / clone — that over-claims` | 改为"当时的判定 + 由哪一次 pass 推翻 + 现状" |

### 3.2 就地日期化更正（B 类，不删发现）

| 文件 | 处置 |
|---|---|
| `docs/audit_notes/s4_matchit_version_test_20261004/README.md` | 判定句加日期化更正块：`❌` 未成立，由 `s4_pairing_provenance_20261004`（commit `1389407`）、`s4_specification_sweep_20261004`、`s4_q1_reproduction_20261004` 三次 pass 推翻；**本笔记的结论本身不动**——MatchIt 版本被证伪、18/18 约定逐字符相同、归档对照仅 3/30 为最近邻 |
| 同上，末节 | `the row was already ❌ and stays ❌` → `…was already ❌ at this point` + 日期化指向文件头更正 |
| 同上，"Still owed" 项 | 追加日期化说明：该问题两半均已被 `s4_reported_run_20261004` 与 `s4_pairing_provenance_20261004` 解决 |
| `docs/audit_notes/open_items_closure_20261004/README.md` | `This contradicts ARCHIVE_MAP.md, which marks S4 ✅ / clone` → 过去时 + 日期化说明"✅ 是当日靠测量重新挣得，而非被撤回"；§7 诚实小结同样追加 |

`results/version_comparison.txt` 等**运行产物一律不改**——那是证据，不是论述。读者由笔记
正文的日期化更正得知其判定已被推翻。

### 3.3 明确保留（C 类）

| 对象 | 保留理由 |
|---|---|
| `ARCHIVE_MAP.md` 状态键中 `🔴 GAP` / `❌ NOT REPRODUCED` 两行定义 | 门禁按此校验；`cut_release.sh` 按此报告阻断行 |
| `ARCHIVE_MAP.md` §"Two axes, not one" 与 `clone ≠ result` 定义 | 仍是 locality 词表的一部分，`check_archive_map.py` 逐行校验 |
| §7 发布前交叉检查、`Any row still marked 🔴 or ❌…` 发布规则 | 面向未来行，不是对现状的断言 |
| `scripts/check_archive_map.py`、`cut_release.sh`、`compare_figures_pixels.py` | 机制本体 |
| `s4_specification_sweep_20261004`、`s4_reported_run_20261004`、`s4_pairing_provenance_20261004`、`s4_order_sensitivity_20261005` | 成功路径的记录，全部仍有效 |
| 仍在生效的负结果：shipped `.R` 不返回提交表；S4 候选顺序 positions 16–30 不可导出；Fig. S1 family-B 栅格无法脚本级复现；`data/upstream` 四个 `.db` 的字节复现依赖未入档的 SQLite 版本；`cov_A/B/C` 超出 GitHub 单文件上限 | 这些都是"复现"可信度的来源，删掉它们等于把 ✅ 变成没有依据的 ✅ |

## 4. 结构处理：为什么这样删不会误删有价值的内容

清理后的笔记结构分四层，各层职责不同，因此"删除"只发生在最上面一层：

1. **证据层（永不改）** — `results/*.csv`、`*.txt`、`*.log`、`*.json`：某次运行的产物。
   即便其判定后来被推翻，它仍是"当时确实这么测出来"的唯一凭据。
2. **日期化笔记层（正文不改，只加日期化更正）** — `docs/audit_notes/*_2026xxxx/`。
   每个目录的 `MANIFEST.sha256` 记录其文件哈希，`check_audit_manifests.py` 逐条校验；
   本次改动后相应清单已重建。
3. **索引层（承载"当前处置"）** — `docs/audit_notes/INDEX.md`。新增阅读规则：日期化笔记
   记录"当天测到什么"，**某个产物的当前状态一律以 `metadata/ARCHIVE_MAP.md` 为准**；
   判定被推翻时，由索引行指出是哪一次 pass 推翻的。
4. **现状层（唯一可以对现状作断言的地方）** — `README.md`、`metadata/ARCHIVE_MAP.md`。
   本次删除全部发生在这一层。

三条防止误删的操作约定：

- **先证明标记已过时，再删**：先用仓库自带脚本复算，而不是靠读文本判断（§1）。
- **删除以"句"为单位，配唯一命中断言**：清理脚本对每处替换断言命中数必须为 1，
  锚点漂移即报错退出，避免静默改错位置（脚本见仓库外的 `_ge_cleanup_20261007/`）。
- **删除的东西仍可回溯**：被删的 README 段落保存在 git 历史与 `CHANGELOG.md` 中；
  被推翻的判定保存在日期化笔记正文与 `CHANGELOG.md` 的历次 pass 条目中。

## 5. 核验

改动后本地三项门禁全绿，并从克隆复检（下表计数取自 `3fc4345`，其树为 tracked 583）：

```
check_archive_map.py      : 13 tables, 47 item rows, 5 locality labels   [ ok ]
check_audit_manifests.py  : 16 audit-note directories, every manifest matches   [ ok ]
verify_provenance.py      : manifest 582 entries / tracked 583 / 1 exclusion   [ ok ]
verify_from_clone.sh      : 0 failure(s), 4 check(s) skipped
```

4 项 skip 均为本机解释器缺 NumPy / Pillow / matplotlib 所致，脚本自己声明
"A skipped check is not a passed check"，故不声称全量通过。`metadata/provenance.json`
与两个受影响目录的 `MANIFEST.sha256` 已按仓库机制重建。

**计数随本次记录自身 +1。** `ab23462` 加入本文件后，树为 tracked **584** / hashed 583 / 1 exclusion，
克隆门禁 11 相应打印 `(584 files)`——两张表相差 1 是这一条文件所致，不是两次运行的口径差异。
两个提交已于 2026-10-07 推送；推送前先 `git fetch` 确认远端未移动（`0 behind / 2 ahead`），
故为快进，远端 `main` = `ab23462`。

## 6. 未处理项（有意留下）

- **`CHANGELOG.md` 的历史条目**（含历次 `❌`/`🔴` 记述）逐字保留：它是追加式历史，
  不是现状断言。本次新增的 `## [Unreleased]` 条目**未编 pass 序号**——该文件最后一条
  编号条目是"(twenty-ninth pass, 2026-10-04)"，而 10-05 至 10-07 的工作尚未编号，
  贸然续号会与既有体例冲突。
- **`metadata/ARCHIVE_MAP.md` §8 关于 2026-10-02 复核的历史叙述**保留：记录的是已修复
  缺陷的来由，非现状断言。
- **`docs/audit_notes/open_items_closure_20261004/README.md` 的表格 `Outcome` 单元格**
  中 `❌ Tested and it does NOT reproduce` 予以保留：该测量（shipped `.R` 六种约定下
  最好仅 2/30）今天仍然成立，被判销的只是"整表不可复现"这一结论。

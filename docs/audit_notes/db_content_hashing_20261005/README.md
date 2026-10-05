# `.db` 改内容级口径 + SQLite 版本入档 —— 2026-10-05

闭合 `未复现项清单_eqtl-source-discordance_20261005.md` 的 **C-1**。

## 0. 一句话结论

> 上游链的四个 eQTLGen SQLite 库此前按 **`file-sha256`** 钉，而 SQLite 文件的**字节镜像取决于写入器库版本**：同一份 schema、同样的行、同样的字节数，换个 SQLite 版本写出来就是不同的字节。
> 后果：**一台机器把整条上游链完整重跑、30 件中间件内容全同，仍被自家校验器判 `DIFFERS`**。
> 现在这四个库改按 **`content_sha256_db`**（schema + 全表逐行，规范序）钉，与 `.txt.gz` 早已采用的 `content_md5` 同一口径；写入器版本入档。
> **效果**：本机重跑目录由 `identical 26 | differing 4 | missing 0` 变为 **`identical 30 | differing 0 | missing 0`**，校验器给出 `RESULT: the whole upstream chain reproduces the archived middleware.`

---

## 1. 原状（是缺陷，不是口径分歧）

| | |
|---|---|
| 钉法 | `code/upstream/verify_middleware.py` 对 4 个 `.db` 用 `kind = "sha256"`（文件字节） |
| 症状 | 2026-10-05 本机把 A/B/C 三带整链跑完，**尺寸相同、schema 相同、逐行相同、`COUNT(*)` 相同**，仍打印 `differing 4` 与 `RESULT: the rebuild does NOT reproduce the archived middleware.` |
| 成因 | `middleware_ledger.tsv` 与校验器记录的期望值是 **Python 3.12.15 那一跑**的字节；本机是 **SQLite 3.45.1**。页布局随写入器版本变 |
| 版本档 | `toolchain/versions.txt` 当时只记 `python / numpy / scipy / pandas`，**未记 sqlite** → 该依赖此前不可见 |

## 2. 处置

### 2.1 校验器改内容级

`code/upstream/verify_middleware.py`：

- 新增 `content_sha256_db(path)`，规范形式与随库的
  `docs/audit_notes/upstream_recheck_20261005/scripts/compare_db_content.py` **一致**：
  `sqlite_master`（`type, name, sql`，排序）→ 每张表按其**全部列**排序后逐行 `name|v1|v2|…`。
- 4 条 `EXPECTED` 由 `"sha256"` 改为 `"content_sha256_db"`，期望值取自归档副本
  （`data/upstream/eqtlgen/*.db`）：

| artefact | content SHA-256（schema + 全表逐行） | 表行数 |
|---|---|---|
| `eQTLGen_Whole_Blood.db` | `7bfe1c08e14ed88837b0acf9c6eb5f601c73c1303384192f30d3c203b2e710ba` | weights 65,622 / extra 103 |
| `db_A.db` | `54082ecddfe1ba848ff7dae24c01ec27c8792d8021e1370cac84d36961a9739e` | weights 46,919 / extra 94 |
| `db_B.db` | `d29895db795f66eb1ddc20df2fb988e7c3939a8ea3b1e924990e1521caddbbc6` | weights 13,671 / extra 8 |
| `db_C.db` | `60b910090e6de9f0f8321e471fc6810e8fa46957de330bd5cfc5ef433873a8e7` | weights 5,032 / extra 1 |

- 每次运行**打印 `sqlite3.sqlite_version`** 并说明这四个 `.db` 为何按内容钉。
- `DIFFERS` 分支对新的 kind 给出专门提示（"schema 或数据不同，不是页布局"）。

### 2.2 版本入档

- `docs/audit_notes/upstream_chain_closure_20261004/toolchain/versions.txt`：**增记 `sqlite3 3.45.1`**（带日期戳说明）。
- `env/environment-upstream.yml`：**尾部加注**该依赖与它为何被记录。
- `data/external/README.md`（清单的第二实现）：四个 `.db` 行**并排给出 content SHA-256**，并加一段注明"content 那个才是承重的、file SHA-256 保留是因为它记录归档了什么"。

## 3. 实测

```
$ python3 code/upstream/verify_middleware.py --run-dir data/upstream
sqlite3 library : 3.53.1
identical 27 | differing 0 | missing 3   (of 30)          # 3 = 分带协方差，超 GitHub 100 MiB 上限

$ python3 code/upstream/verify_middleware.py --run-dir <本机重跑目录>
identical 30 | differing 0 | missing 0   (of 30)
RESULT: the whole upstream chain reproduces the archived middleware.
```

**注意**：`data/upstream` 那一条用的是**主环境** Python 3.13 的 SQLite 3.53.1，而归档 `.db` 是 3.45.1 写的 —— 在旧口径下这照样会 `DIFFERS`；改内容级后为 `ok`。这正是改动的意义所在：**内容对就是复现，写入器版本不再是判据。**

## 4. 没有改的东西（是判断，不是遗漏）

- **`middleware_ledger.tsv` 不改写**：它是 **2026-10-04 那次第三方运行的记录**，当时四库**字节级也相同**（写入器同为 3.12.15 系）。改写它会销毁"那次运行确实 30/30 字节相同"这一事实。其 `hash_kind = file-sha256` 是**历史口径**，保留。
- **`ledger/check_middleware.py` 的行为不改**：它是产出该台账的、绑定那次运行的脚本；其 `file-sha256` 与台账同源。**实时校验器是 `code/upstream/verify_middleware.py`，它已改。**（两处口径不同是**有意的**：一处记录历史，一处定义现在。）
- 已在上表第 3 行给出可直接核对的替代路径。

## 5. 材料

| 文件 | 变更 |
|---|---|
| `code/upstream/verify_middleware.py` | 新增 `content_sha256_db()`；4 条 `.db` 改 kind 与新期望值；打印 sqlite 版本；docstring 加"THE FOUR SQLite ARTEFACTS ARE CHECKED BY CONTENT"一节 |
| `data/external/README.md` | 四个 `.db` 行并排 content SHA-256；新增说明段 |
| `docs/audit_notes/upstream_chain_closure_20261004/toolchain/versions.txt` | 增记 sqlite3 版本 |
| `env/environment-upstream.yml` | 尾部加注 |
| `MANIFEST.sha256` | 本目录受控文件哈希 |

*本记录数值全部来自 2026-10-05 本机实跑（主环境 Python 3.13.14 / SQLite 3.53.1；上游环境 SQLite 3.45.1）。无任何已报告数值改变。*

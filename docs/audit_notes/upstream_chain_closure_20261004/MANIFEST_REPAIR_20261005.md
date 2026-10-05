# `MANIFEST.sha256` 修复 —— 2026-10-05

本目录的 `MANIFEST.sha256` 与**已提交的字节**不符，本次按当前提交内容重算。**未改动任何被哈希文件的内容**：只重算 `MANIFEST.sha256`，并新增本说明。

## 重算前的漂移条目（9 项）

| 条目 | 说明 |
|---|---|
| `README.md` | 在 MANIFEST 生成之后又被编辑，哈希未同步 |
| `inputs/verify_external_inputs.log` | 同上 |
| `logs/upstream_A.log` | 见下"关于日志的行尾" |
| `logs/upstream_B.log` | 同上 |
| `logs/upstream_C.log` | 同上 |
| `logs/signals_upstream_A.txt` | 同上 |
| `logs/signals_upstream_B.txt` | 同上 |
| `logs/signals_upstream_C.txt` | 同上 |
| `toolchain/environment.txt` | 在 MANIFEST 生成之后又被编辑 |

`ledger/` 下的四项 —— 包括**主证据** `middleware_ledger.tsv` 与 `archive_verifier.txt` —— **未漂移**，即该目录的核心结论不受本项影响。

## 关于日志的行尾

本目录 `README.md` 明写：

> `MANIFEST.sha256` was computed over those LF bytes so that `sha256sum -c MANIFEST.sha256`
> succeeds from a **fresh clone** … The `logs/` files were produced on Windows and therefore
> carried CRLF before being committed; the line endings were normalised.

重算前的 `MANIFEST.sha256` **并未**做到这一点（其对日志记录的是规范化之前的哈希）。本次重算使该声明**首次成立**：哈希现在取自已提交的 LF 字节。

仓库 `.gitattributes` 显式列出 `*.csv/*.tsv/*.txt` 等类型，但**未列出 `*.log`**；`.log` 只受兜底规则 `* text=auto eol=lf` 管。两条路径**都**使 checkout 得到 LF，因此漂移的机制不是"checkout 出了 CRLF"，而是：**重算前的 `MANIFEST.sha256` 记录的是规范化之前的 CRLF 工作副本哈希**。本次重算改为对已提交的 LF 字节取哈希。

（`*.log` 现已在 `.gitattributes` 中显式声明为 `text eol=lf`，与其上方"Data and run logs … Listed explicitly"的注释意图一致；该声明不改变任何已存 blob，也不触发重规范化。）

## 成因

`docs/audit_notes/*/MANIFEST.sha256` **没有任何门禁校验** —— `scripts/verify_from_clone.sh`、`scripts/cut_release.sh`、`scripts/check_archive_map.py` 都不读它。因此在 MANIFEST 之后编辑目录内文件、或按 CRLF 计数哈希，都不会触发任何失败。

`git status --porcelain` 对本目录为空，即漂移**先于本次修复**。

## 修复方式

以当前工作树（= git 索引 = 全新克隆所得到的字节）为准重新计算：

```bash
cd <this-dir>
find . -type f ! -name 'MANIFEST.sha256' | sed 's|^\./||' | LC_ALL=C sort \
  | while read -r f; do printf '%s  %s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$f"; done \
  > MANIFEST.sha256
sha256sum -c MANIFEST.sha256
```

## 关联记录

- `../r_path_and_hygiene_closure_20261005/README.md` §2.1（发现与成因）
- 待办：给 `docs/audit_notes/*/MANIFEST.sha256` 补一道门禁；并考虑在 `.gitattributes` 为 `*.log` 增补显式 `text eol=lf`，从源头消除该漂移类别。

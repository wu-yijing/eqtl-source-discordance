# `MANIFEST.sha256` 修复 —— 2026-10-05

本目录的 `MANIFEST.sha256` 与**已提交的字节**不符，本次按当前提交内容重算。**未改动任何被哈希文件的内容**：只重算 `MANIFEST.sha256`，并新增本说明。

## 重算前的漂移条目

| 条目 | 说明 |
|---|---|
| `README.md` | 在 MANIFEST 生成之后又被编辑，哈希未同步 |
| `logs/ab_matchit472.log` | 同上；该 log 亦属"MANIFEST 之后补记"的一类 |
| `logs/install_matchit455.log` | 同上 |
| `results/m472_conventions.csv` | 同上 |

## 成因

`docs/audit_notes/*/MANIFEST.sha256` **没有任何门禁校验** —— `scripts/verify_from_clone.sh`、`scripts/cut_release.sh`、`scripts/check_archive_map.py` 都不读它。因此在 MANIFEST 之后编辑目录内文件不会触发任何失败，漂移可以长期存在。

`git status --porcelain` 对本目录为空，即漂移**先于本次修复**，非本次改动所致。

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
- 待办：给 `docs/audit_notes/*/MANIFEST.sha256` 补一道门禁，否则同类漂移仍会复现。

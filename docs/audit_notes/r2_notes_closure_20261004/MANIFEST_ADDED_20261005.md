# 本目录补登 MANIFEST —— 2026-10-05

本目录（2026-10-04 建立）是 `docs/audit_notes/` 下**唯一没有 `MANIFEST.sha256` 的目录**。
2026-10-05 给 `docs/audit_notes/*/MANIFEST.sha256` 补门禁时发现该缺口：门禁要求**每个审计目录都必须有清单**（内容未登记的审计记录不可核验），故在此补登。

- 补登内容：本目录现有受控文件的 SHA-256（`README.md`、`apply_r2_notes.py`、`verify_r2_notes.py`，以及本说明文件）。
- **未改动任何既有文件的内容**；本目录原有正文与脚本逐字节不变。
- 门禁：`scripts/check_audit_manifests.py`（`scripts/verify_from_clone.sh` 第 13 道）。

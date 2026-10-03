# Audit notes

Dated audit notes **shipped with this repository**. They record cross-carrier consistency checks and
deprecation decisions that bear directly on the figures and data archived here.

They are deliberately kept separate from `analysis_reports/`, which is a **local-only working
directory** and is listed in `.gitignore` (internal working notes — not published).

| Note | Date | What it records |
|---|---|---|
| `AF1与主稿图表同步核查报告_20260920.md` | 2026-09-20 | *Additional file 1* vs the manuscript: figure/table numbering, captions, cross-references and values all in sync; one **duplicated figure** was found and removed, with before/after verification at both the docx and PDF layers |
| `补充图目录版本谱系判定_20260920.md` | 2026-09-20 | Which supplementary-figure directory is current, decided by **content hash** rather than timestamps: `figures/` here is byte-identical to the current directory (12/12 files) and to the images embedded in *Additional file 1* (6/6, vs 0/16 for the superseded directory). The superseded directory was given a `_DEPRECATED_勿用_` prefix |
| `S1重建与SCZ改名收口执行记录_20260920.md` | 2026-09-20 | The record behind commits `d7de5a8` and `14d2289`: the in-house SCZ pipeline renamed to `_DEPRECATED_scz_self_implemented/`, the S1 section rebuilt onto `data/processed_officialZ/`, and the manuscript title unified across every carrier (README, `.zenodo.json`, Zenodo record) |

No `.docx` manuscript or supplementary file is distributed with this repository; the notes refer to
them only by file name and by values already public in `README.md`.

> 本目录的文件以中文撰写，与项目内部的审计记录体例一致。图集与数值的权威来源仍是 `figures/` 与
> `data/processed_officialZ/`；`README.md` 是这些结论的英文摘要。

# Audit notes

Dated audit notes **shipped with this repository**. They record cross-carrier consistency checks and
deprecation decisions that bear directly on the figures and data archived here.

They are deliberately kept separate from `analysis_reports/`, which is a **local-only working
directory** and is listed in `.gitignore` (internal working notes — not published).

> ⚠️ **Path note (2026-10-02).** The dated notes below are kept as written. Where one names
> `data/processed_officialZ/` — the predecessor repository's layout for the layer this archive now
> calls **`data/derived/`** — the two are byte-identical, 6 files of 6 (verified 2026-10-02 against
> a clone of the predecessor repository). Mapping and redirect:
> [`../../data/processed_officialZ/README.md`](../../data/processed_officialZ/README.md).

| Note | Date | What it records |
|---|---|---|
| `AF1与主稿图表同步核查报告_20260920.md` | 2026-09-20 | *Additional file 1* vs the manuscript: figure/table numbering, captions, cross-references and values all in sync; one **duplicated figure** was found and removed, with before/after verification at both the docx and PDF layers |
| `补充图目录版本谱系判定_20260920.md` | 2026-09-20 | Which supplementary-figure directory is current, decided by **content hash** rather than timestamps: `figures/` here is byte-identical to the current directory (12/12 files) and to the images embedded in *Additional file 1* (6/6, vs 0/16 for the superseded directory). The superseded directory was given a `_DEPRECATED_勿用_` prefix |
| `S1重建与SCZ改名收口执行记录_20260920.md` | 2026-09-20 | The record behind commits `d7de5a8` and `14d2289`: the in-house SCZ pipeline renamed to `_DEPRECATED_scz_self_implemented/`, the S1 section rebuilt onto `data/processed_officialZ/`, and the manuscript title unified across every carrier (README, `.zenodo.json`, Zenodo record) |
| `复现核验_GE投稿两份文档_20261002.md` | 2026-10-02 | Full third-party reproduction of both submitted documents (31 SI tables + main text), run outside the original environment. Grade: **R1 ≈ 200 items identical at the reported precision, R2 = 3, R3 = 0**. Closes `metadata/ARCHIVE_MAP.md` gaps GAP-4, GAP-5, GAP-7, GAP-9 and GAP-10 — SI Tables S9, S16, S17, S27, S28 and S29 move 🔴 → ✅ — and supplies the missing generator for S20. Records the three self-corrections made during the audit |
| `BMC定稿与GE投稿值域交叉核对_20261002.md` | 2026-10-02 | The two submitted documents against the predecessor 2026-09-28 final manuscript: 63 comparable headline statistics **all identical, none unique to the new documents**. Establishes that *Additional file 1* and the new Supporting Information are the **same document under two numberings** (Table S*n* → S*(n+1)* for n = 1–25, plus the new S27–S30) |
| `R2残余差异消除方案_20261002.md` | 2026-10-02 | The three residual R2 items and how to close them. **None is a wrong number** — each is an undisclosed parameter or a rounding chain. Contains paste-ready SI note text; completing the two P1 items sets **R2 = 0** |
| `仓库可复现性修复记录_20261003.md` | 2026-10-03 | Independent audit found that `code/run_all.sh` — the repository's self-declared only entry point — **failed from a fresh clone (exit 1, 8 failures)**, and that neither the conda nor the Docker environment was installable. Records the four root causes (legacy filenames never remapped, a false-positive preflight, BMC-era table numbering still in the figure scripts, an em-dash value the cell parser could not read), the environment fixes, the figure policy now stated, and **what was deliberately left open** (DOI placeholder, unpinned base image, GAP-1/2/4/6/8, and the gate-coverage gap that let this ship). No reported number changed |

No `.docx` manuscript or supplementary file is distributed with this repository; the notes refer to
them only by file name and by values already public in `README.md`.

> 本目录的文件以中文撰写，与项目内部的审计记录体例一致。图集与数值的权威来源仍是 `figures/` 与
> `data/derived/`（2026-10-02 之前称 `data/processed_officialZ/`）；`README.md` 是这些结论的英文摘要。

# 图脚本与数据来源（2026-09-14）

> 📌 **路径附注（2026-09-20 补记）**：本页正文按 2026-09-14 当时的目录名**原样保留**，以保全审计追溯链。
> 其中一项已因改名失效：`scz_replication/results/scz_twas_results_limit0.csv` 现为
> `_DEPRECATED_scz_self_implemented/results/scz_twas_results_limit0.csv`（2026-09-20 改名，该自实现管线已弃用，
> 现行 SCZ 权威值为 `data/processed_officialZ/scz_z_4arm_official.csv`）。本页其余数据层路径
> `data/processed/…` 同样属**修正前**世代，现行层为 `data/processed_officialZ/`。


本目录下的 5 个脚本**均由数据实时计算**，不含数据型字面量（仅展示顺序、颜色等样式常量）。

| 图 | 脚本 | 数据来源 |
|---|---|---|
| Fig. 4 | `Fig4_axis_decomposition.py` | GTEx 逐组织 Z（`data/processed/gtex_Whole_Blood_{DR,DN,DPN}.csv`、`gtex_Nerve_Tibial_{DR,DN,DPN}.csv`）、`eqtlgen_spredixcan_harmonized_results.csv`、`panel_acat_recompute.csv` |
| Fig. 5 | `Fig5_candidate_dumbbell.py` | `eqtlgen_spredixcan_harmonized_results.csv` + `gtex_Nerve_Tibial_DR.csv` |
| Fig. 6 | `Fig6_fdr_enrichment_3panel.py` | `panel_acat_recompute.csv`（列 P_stable）+ `eqtlgen_spredixcan_harmonized_results.csv` |
| Fig. 7 | `Fig7_rnh1_crosscohort.py` | `gtex_Nerve_Tibial_{DR,DN,DPN}.csv` + `eqtlgen_spredixcan_harmonized_results.csv` + `tables/TableS5.csv` |
| Fig. 8 | `Fig8_crosstrait_3genesets.py` | GTEx 逐组织 Z + `data/hk_reselect_20260830/data/arms_all_groups.csv` + `scz_replication/results/scz_twas_results_limit0.csv` |

前 4 个脚本带自检：运行时断言所选基因集或派生统计量与稿件记录值一致，数据一旦变化即报错，而非静默出图。

## ⚠️ 使用前必读

**不要使用以下两个文件**：`data/processed/candidate_comparison_DR.csv`、`tables/Table1.csv`。

二者的 eQTLGen Z 属 **2026-07-25 版旧管线**；与权威表逐行比对 **60 行配对无一相同**，平均 |ΔZ| = 3.33、最大 13.01：

| 基因–表型 | 旧文件 | 权威表 | 手稿 |
|---|---|---|---|
| RNH1–DR | 11.617 | **13.318** | **+13.32** |
| TUBB–DR Z | 47.83 | **48.5** | **+48.5** |
| TUBB 匹配 SNP | 146 / 830 | **359 / 1,848** | **359 of 1,848** |

**权威文件是 `data/processed/eqtlgen_spredixcan_harmonized_results.csv`（2026-09-09）。**

## 旧版脚本

不能复现手稿图的旧脚本已移入 `../figure_scripts_旧版_勿用_20260914/`（9 个，附 `README_为何勿用.md`）。

详细原因见《出图脚本硬编码审计报告_20260914.md》与《Fig8重算重出报告_20260914.md》。

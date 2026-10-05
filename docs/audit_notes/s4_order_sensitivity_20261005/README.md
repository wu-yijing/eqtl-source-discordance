# SI Table S4 的顺序敏感性 —— 2026-10-05

本记录回答一个问题：

> 表 S4 的控制集只在"按投稿件的候选人顺序处理"时才 30/30 复现，而该顺序**不可由随库矩阵推导**。
> 那么，**换一个同样站得住的顺序，任何已报告的结论会不会变？**

**答案是：不会。** 下面是把顺序当成自由参数扫出来的实测，不是论证。

---

## 0. 结论

> **顺序影响的是"哪 30 个对照"，不是"得出什么结论"。**
>
> - 候选臂是固定的 30 个基因，**任何顺序下都不变**（84 / 81 个有结局的格，其中 2 / 5 个显著）。顺序**只**移动对照臂。
> - 500 个随机候选人顺序：对照集与投稿集重叠 **26–30 / 30**（中位 28），其中 **12 个（2.4 %）同样达到 30 / 30** —— 投稿顺序**不是唯一解**。
> - **表 S26 四个对比的显著性判定，500 个顺序 + 4 个确定性顺序无一改变**（全部 `P < 0.05` 占比 **0 %**）。
>
> 因此：这是**规格完备性**（specification completeness）问题，不是数据真实性问题。下面给出两条各自的处置。

---

## 1. 实测

`ORDER_SENSITIVITY` 脚本（`scripts/order_sensitivity.R`）把匹配固定为归档规格（`method="nearest"`、`distance="mahalanobis"`、`ratio=1`、`replace=FALSE`、`m.order="data"`、池 = 44 个 `Non-Candidate`、群中位数插补、MatchIt 4.5.5），只变**候选人的处理顺序**。

### 1.1 候选臂不随顺序变（构造上即如此）

| 对比 | 候选臂显著 / 有结局 |
|---|---|
| GTEx `FDR_q_ACAT_O` (BH q<0.05) | 2 / 84 |
| GTEx `P_ACAT_O` (nominal) | 8 / 84 |
| eQTLGen `BH_q` (BH q<0.05) | 5 / 81 |
| eQTLGen `P` (nominal) | 8 / 81 |

### 1.2 确定性顺序

| 顺序 | 对照集重叠 | GTEx BH q | GTEx nominal | eQTLGen BH q | eQTLGen nominal |
|---|---|---|---|---|---|
| **投稿顺序** | **30 / 30** | 1/60 → 1.000 | 7/60 → 0.784 | **0/57 → 0.077** | 4/57 → 0.761 |
| 字母序 | 29 / 30 | 1/60 → 1.000 | 7/60 → 0.784 | 0/54 → 0.157 | 4/54 → 0.762 |
| PullDown 稳定排序 | 28 / 30 | 1/57 → 1.000 | 7/57 → 0.593 | 0/54 → 0.157 | 4/54 → 0.762 |
| PullDown 反序 | 27 / 30 | 1/60 → 1.000 | 7/60 → 0.784 | 0/51 → 0.156 | 4/51 → 0.766 |
| 协变量矩阵行序 | 29 / 30 | 1/60 → 1.000 | 7/60 → 0.784 | 0/54 → 0.157 | 4/54 → 0.762 |

### 1.3 500 个随机顺序

```
control-set overlap with the submitted set : min 26, median 28, max 30 of 30
permutations reaching 30/30                : 12        (2.4 %)

per-contrast distribution (candidate side fixed):
  GTEx FDR_q_ACAT_O (BH q<0.05)   ctrl cells 54..66 | ctrl sig 0..1 | P 0.507..1.000 | P<0.05 in 0%
  GTEx P_ACAT_O (nominal)         ctrl cells 54..66 | ctrl sig 4..7 | P 0.556..1.000 | P<0.05 in 0%
  eQTLGen BH_q (BH q<0.05)        ctrl cells 48..60 | ctrl sig 0..0 | P 0.072..0.157 | P<0.05 in 0%
  eQTLGen P (nominal)             ctrl cells 48..60 | ctrl sig 4..4 | P 0.558..1.000 | P<0.05 in 0%
```

**读法**：对照臂的显著数只在 `0–1`（GTEx BH q）、`4–7`（GTEx nominal）、`0`（eQTLGen BH q）、`4`（eQTLGen nominal）之间浮动，**没有一个顺序把任何对比推过 0.05**；eQTLGen BH q 的 P 始终落在 `0.072–0.157`，始终是"未达显著"，而投稿顺序给出的 `0.0769` **不是**最小值（最小 0.072）——即投稿顺序并未被挑成"最有利"的那个。

---

## 2. 对 v1 表述的更正（原表述被采样量限制，是对的但不完整）

`code/analyses/emit_S4_table.R` 与 `metadata/ARCHIVE_MAP.md` §5 GAP-11 记：

> "over 30 random permutations the best overlap is 29 of 30" / "30 random permutations reach at most 29 and hit 30 zero times"

**该陈述在 30 次采样下成立，但在 500 次采样下不成立**：30/30 **可达**，频率约 **2.4 %**（500 次中 12 次）。这不推翻任何结论，反而**削弱**了"投稿顺序是唯一能得 30/30 的顺序"这一疑虑——原句容易被误读为"只有投稿顺序能到 30/30"，实测并非如此。

---

## 3. 两条处置

### 3.1 复现性（已闭合，无需改动数据）

顺序**随库分发**——它在 `data/superseded/mahalanobis_matched_pairs.csv` 的候选块里（与投稿件逐字节相同），`emit_S4_table.R` 从它读取。故 **一份全新克隆仍能给出 30/30**（门禁 12）。若要更显式，可把该顺序单独落成一个具名规格输入；本轮判断**不必**：它已经在受库管理的文件里，且已被断言 `PullDown_Unused` 非递增。

### 3.2 完备性（本节即处置：把自由度写下来，并给出它的量级）

规格里**存在一个自由度**：候选人处理顺序。它未被 Methods 写明，且不可由协变量推导。处置不是"消除"它（做不到），而是**把它连同量级一起披露**。建议正文/表注加一句：

> The candidates are processed in the order in which Table S4 lists them. That order is `PullDown_Unused` non-increasing; because 15 candidates tie at zero, the within-tie order is not recoverable from the shipped covariate matrix. Across 500 random candidate orders, the selected control set overlaps the reported one in 26–30 of 30 (median 28; 12 of 500 also reach 30 of 30), and **no Table S26 contrast changes its significance call** (the candidate arm is order-invariant; eQTLGen BH q P ranges 0.072–0.157, all others P ≥ 0.51).

---

## 4. 材料

| 文件 | 内容 |
|---|---|
| `scripts/order_sensitivity.R` | 扫描脚本：固定匹配规格、只变顺序；输出重叠分布与四个 S26 对比的分布 |
| `MANIFEST.sha256` | 本目录受控文件哈希 |

复现命令：

```
PRELIB=<pinned-lib> Rscript scripts/order_sensitivity.R <repo-root> 500
```

环境：R 4.5.2 + MatchIt 4.5.5（`env/renv.lock` 钉版）；随机种子 `20261005`（固定，可复现）。

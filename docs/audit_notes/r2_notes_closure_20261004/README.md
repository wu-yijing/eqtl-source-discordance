# R2 注记落稿 —— 2026-10-04

`docs/audit_notes/R2残余差异消除方案_20261002.md` 把 R2 的三项残差诊断完毕，并给出可直接
粘贴的英文；那份文件结尾写着：

> **做完 P1+P2 后，R2 = 0，R1 覆盖两文档的全部报告值。**

本目录记录**执行那一步**的过程与产物。R2 三项**都不是数值错**，而是"报告没有把复现所需的
信息写全"，因此本次落稿**不改动任何已报告数值**——只补披露。

## 1. 落稿结果

| 文档 | 输入 | 输出 | 字节 | MD5 | SHA-256 |
|---|---|---|---|---|---|
| SI | `…_rev6.docx` | **`…_rev7.docx`** | 1,463,543 → **1,464,167** | `d4ad6e348d577f55706a5d65af7ed37b` | `48135f7872b99bad125a0a0e7f0bcaf972f5575cdb9f017aae63cfe5054130e0` |
| 正文 | `…_rev7.docx` | **`…_rev8.docx`** | 31,190 → **31,223** | `7fed1b504c452e16333a59d1aef6510e` | `bae04123245dfd360dcc24b4dfa380f79f25ad8b404be3b3f7176b0aa31a11ba` |

输入的哈希（供回溯）：

| 输入 | 字节 | MD5 |
|---|---|---|
| `Supporting_Information_…_rev6.docx` | 1,463,543 | `5baf40f0fbba2fb1d50367bdc7fecb85` |
| `Manuscript_…_rev7.docx` | 31,190 | `27e9bf5cbf3785d930f27ee6f165c49f` |

> SI 的输入取 **rev6** 而不是 rev5：rev5 的包结构有回归（部件 19 → 25、`w:tblPrEx`
> 2,160 → 0），rev6 是同一内容落在 rev4 结构上的重建件，见
> [`../open_items_closure_20261004/`](../open_items_closure_20261004/README.md) §4。
> 本次输出 rev7 仍是 **19 部件、四项标记计数与 rev6 完全相同**（见 §3 检查 5），
> 即没有把那个回归带回来。

## 2. 落了什么

### SI Table S17 表注之后，新增两段

**段 1**（方案 §三(2) 的 "Resampling details" + §四 的置换单元，合并为一段）：

> **Resampling details.** All resampling procedures draw genes from a **lexicographically
> sorted** gene vector, so the reported interval endpoints depend only on the seed and on the
> number of draws. The generator is `numpy.random.RandomState` (legacy MT19937); seeds are
> 20260915 (testbed and decomposition arms), 20260726 (genome-wide SCZ) and 20260914 (framework
> layer), with B = 10,000 (5,000 for the paired Δρ bootstrap). Gene labels are permuted as whole
> genes — one permutation applied simultaneously to all three phenotypes — so that each gene
> contributes its three pairs together; B = 10,000.

这一段**一次关闭三项**：自助法端点随基因行序变化（方案第 3 项）、主臂 ρ 区间
0.12–0.62 的 RNG 口径（方案 §四 第一行）、以及置换检验 −0.22 ~ +0.23 的置换单元
（方案 §四 第二行 —— 现描述给的是 −0.199/+0.199）。

**段 2**（方案 §二，估计量）：

> **Cluster-robust (sandwich) standard error of the rank correlation.** With x̃ and ỹ denoting
> the mean-centred ranks … SE_sandwich(ρ) = √( Σ_g ( Σ_{i in g} φ_i )² ). The delete-one-gene
> jackknife standard error is SE_jackknife(ρ) = … K = 32. Both are referred to the t distribution
> with df = K − 1 = 31.

关闭方案第 2 项。**表 S17 的 `SE = 0.125` 没有改**——方案的判定是三元组
`(SE 0.125, 一侧 P 0.002, 双侧 P 0.004, df 31)` 本身自洽（t(31) 下任何 SE ∈ [0.12326, 0.12719]
都给同样的显示值），所以缺的是估计量，不是数字。

### 正文第 37 段，就地加一个括号

> …and the observed 68.8% exceeds that by 6.1 points **(6.01 points when evaluated at the
> unrounded ρ = 0.3896 and rate = 68.75%)**, indicating…

关闭方案第 1 项。原句用两个取整值相减（68.8 − 62.7 = 6.1），SI 表 S27 注写的是同一个量的
另一显示精度（68.80 − 62.7525 = 6.0475 → 6.05）。两者都对，只是读者会以为冲突；括号把
差额 0.04 pp 的来源写明。**两个数字都没改。**

> 关于范围：方案 §一 的目标句在**正文**里，不在 SI。SI 表 S27 的表注写的是 "+6.05-point
> excess"，与显示值口径一致，无需改动。故 P1 全在 SI、P2 在正文——本次两支都做了；
> 若不要正文这一处，`Manuscript_…_rev7.docx` 原样未动，撤销即弃用 rev8。

## 3. 怎么复核

```bash
PY=<python>
python apply_r2_notes.py \
    --si  <SI_rev6.docx>  --si-out <SI_rev7.docx> \
    --ms  <MS_rev7.docx>  --ms-out <MS_rev8.docx>

python verify_r2_notes.py \
    --si-in <SI_rev6.docx> --si-out <SI_rev7.docx> \
    --ms-in <MS_rev7.docx> --ms-out <MS_rev8.docx>
```

`apply_r2_notes.py` **不硬编码**任何段落：每次运行都从 `../R2残余差异消除方案_20261002.md`
现抽 A/C/D/E 四块；抽不到就报错退出。所以方案一旦被改动，脚本会失败而不是悄悄分叉。

`verify_r2_notes.py` 七项，全部通过：

| # | 检查 | 结果 |
|---|---|---|
| 1 | 部件表相同；除 `word/document.xml` 外逐部件逐字节相同 | ✓ SI 19 / 正文 16 部件 |
| 2 | `document.xml` 与输入**只有一处纯插入** | ✓ SI `[3635677, 3635677)`，2,736 字符；正文 `[29182, 29182)`，75 字符 |
| 3 | 插入串 = 方案现抽文本，逐字符相等；新增段 `<w:pPr>` 与表注段相同 | ✓ 6 个 run 全等；2 段均继承 |
| 4 | SI 段数 115 → 117 且新段紧随第 81 段；原有 115 段逐段未变。正文段数不变、恰好 1 段变化且变化仅为括号 | ✓ |
| 5 | SI 的 `tblPrEx` / `tblCellMar` / `tblBorders` / `insideH` 四项计数不变 | ✓ 回归未复发 |
| 6 | 插入文本的每个非 ASCII 字符在 Times New Roman 有字形覆盖 | ✓ 12 种，5 种为本文档新引入 |
| 7 | 输入里出现过的数值 token 一个不少 | ✓ SI 新增 token 仅 `19937 / 20260726 / 5,000`；正文新增仅 `0.3896 / 6.01 / 68.75` |

## 4. 一处字形替换，以及为什么

方案 §二 的公式里有一个字符 **Times New Roman 没有覆盖**：`∈`（U+2208，"属于"）。
用 fontTools 对 `times.ttf` / `timesbd.ttf` / `timesi.ttf` 实测，15 个候选码位中
**唯缺这一个**（其余 Σ U+03A3、φ U+03C6、ỹ U+1EF9、组合波浪 ̃ U+0303、组合长音 ̄ U+0304
均有覆盖）。故：

```
Σ_{i∈g}   →   Σ_{i in g}
```

**这是全文唯一一处替换**，`apply_r2_notes.py` 会断言"源形在、目标形不在"，验证器检查 3
也会把这一处打印出来。除此之外两段与方案逐字符相同。

新增的 5 个字符（`̃ ̄ Σ φ ỹ`）在文档里是**新引入**的，但字体覆盖已实测，不需要嵌入字体。

## 5. 这次没做的事

- **SI 的 PDF 仍未产出。** 正文与 SI 都改了，分页与逐页字符比对需要在允许 Office 自动化
  的机器上渲染（本机 WPS COM 被安全策略拒绝，见
  [`../open_items_closure_20261004/README.md`](../open_items_closure_20261004/README.md) §5）。
- **方案 §五 的 7 项表注（P3）未落。** 其中表 S21 的 `median minimum absolute Z` 已于
  2026-10-04 修正、表 S24 的零值约定已写入，其余 5 项待办。
- **本文档不含任何 `.docx`。** 本仓的既有规则是稿件与补充材料不随仓分发；两份产物在
  投稿工作目录里，本目录只记录其哈希与复核方法。

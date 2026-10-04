#!/usr/bin/env Rscript
# =============================================================================
# diagnose_S4_distance.R — 把 S4 的不复现分解为"距离度量"还是"指派"
# =============================================================================
# 版本已被排除（4.5.5 → 1/30，4.7.2 → 2/30）。下一步要问的是：差异发生在哪一层？
#
#   层次 1（距离度量）：某候选项下，归档选中的那个对照，是不是也是"最近"的？
#   层次 2（指派规则）：距离对，但贪心顺序/平局打破不同，导致换人。
#
# 做法：按候选基因逐个算到池中每个对照的马氏距离（协方差按三种常见约定各算一遍），
# 看归档选中的对照在候选最近邻中的排名。
#
# 用法：Rscript diagnose_S4_distance.R <repo>
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
repo <- if (length(args) >= 1) args[1] else "."

covar <- read.csv(file.path(repo, "data", "derived", "covariate_matrix.csv"),
                  stringsAsFactors = FALSE, na.strings = c("", "NA", "N/A"))
for (g in unique(covar$Group)) {
  i <- which(covar$Group == g & is.na(covar$eQTL_SNPs_Mean))
  if (length(i)) covar$eQTL_SNPs_Mean[i] <- median(covar$eQTL_SNPs_Mean[covar$Group == g],
                                                  na.rm = TRUE)
}
cand <- covar[covar$Group == "30 HOTAIR Candidate", ]
pool <- covar[covar$Group == "44 Non-Candidate", ]

X <- function(d) as.matrix(cbind(log10(d$Length_bp), d$GC_pct, d$eQTL_SNPs_Mean))
Xt <- X(cand); Xc <- X(pool)

arch <- read.csv(file.path(repo, "data", "superseded", "mahalanobis_matched_pairs.csv"),
                 stringsAsFactors = FALSE)
arch$treated <- trimws(as.character(arch$treated))
## 以**候选基因名**为键（不能依赖 split/vapply 的 list 名，那会是 subclass 序号）
ref <- character(0)
for (x in split(arch, arch$subclass)) {
  ctl <- x$Gene[x$treated == "0"]; trt <- x$Gene[x$treated == "1"]
  if (length(ctl) == 1 && length(trt) == 1) ref[trt] <- ctl
}
cat(sprintf("归档配对：%d 对（候选名匹配随库矩阵 %d；对照名匹配池 %d）\n",
            length(ref), sum(names(ref) %in% cand$Gene), sum(ref %in% pool$Gene)))

mdist <- function(a, B, S) {
  ## a: 1×p 行向量；B: n×p；S: p×p 协方差（用广义逆）
  d <- sweep(B, 2, a, "-")
  Si <- MASS::ginv(S)
  sqrt(rowSums((d %*% Si) * d))
}

conventions <- list(
  "cov of pool (controls only)"          = cov(Xc),
  "cov of candidates (treated only)"     = cov(Xt),
  "cov pooled over both, centred by own group means" = cov(rbind(sweep(Xt, 2, colMeans(Xt)),
                                                                 sweep(Xc, 2, colMeans(Xc))))
)

## 也测协变量子集：若归档那一对并非三协变量马氏距离下的近邻，那问题可能在用了哪些协变量
SUBSETS <- list(
  "all three"            = 1:3,
  "length + GC"          = c(1, 2),
  "length + eQTL SNPs"   = c(1, 3),
  "GC + eQTL SNPs"       = c(2, 3),
  "length only"          = 1,
  "GC only"              = 2,
  "eQTL SNPs only"       = 3
)

report <- list()
for (sn in names(SUBSETS)) {
  for (nm in names(conventions)) {
    idx <- SUBSETS[[sn]]
    S <- conventions[[nm]][idx, idx, drop = FALSE]
    if (any(!is.finite(S)) || det(S) == 0) { next }
    ranks <- numeric(0); atmin <- 0L
    for (g in names(ref)) {
      i <- match(g, cand$Gene); j <- match(ref[[g]], pool$Gene)
      if (is.na(i) || is.na(j)) next
      dd <- mdist(Xt[i, idx, drop = FALSE], Xc[, idx, drop = FALSE], S)
      r <- rank(dd, ties.method = "min")[j]
      ranks <- c(ranks, r); if (r == 1) atmin <- atmin + 1L
    }
    report[[length(report) + 1]] <- data.frame(
      covariates = sn, convention = nm, n = length(ranks),
      archived_control_is_nearest = atmin,
      rank_median = if (length(ranks)) median(ranks) else NA_real_,
      rank_max = if (length(ranks)) max(ranks) else NA_real_)
  }
}

out <- do.call(rbind, report)
out <- out[order(-out$archived_control_is_nearest, out$rank_median), ]
print(out, row.names = FALSE)
p <- file.path(dirname(normalizePath(repo)), "_s4_repro", "ab", "distance_diagnostic.csv")
dir.create(dirname(p), showWarnings = FALSE, recursive = TRUE)
write.csv(out, p, row.names = FALSE)
cat(sprintf("\n写入 %s\n", p))

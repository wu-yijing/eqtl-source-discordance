#!/usr/bin/env Rscript
# =============================================================================
# reproduce_S4_matchit455.R — SI Table S4 的决定性版本对照试验
# =============================================================================
# 目的：把上一轮"MatchIt 版本是唯一存活解释"（收窄但未实测）变成实测。
#
# 做法：**同一个脚本**在两个库下各跑一遍 —— 隔离库（MatchIt 4.5.5，renv.lock 钉
# 的版本）与用户库（MatchIt 4.7.2）。两者只有 MatchIt 版本不同，输入、口径、
# 全部候选约定完全一致。若答案变化 → 版本是原因；若不变 → 版本被排除。
#
# 用法：
#   Rscript reproduce_S4_matchit455.R <lib 或 ""> <tag> <repo> <outdir>
#     lib  = 要前置到 .libPaths() 的库目录（"" = 不前置，用用户库）
#     tag  = 输出文件名前缀（如 m455 / m472）
#
# 输出：<outdir>/<tag>_conventions.csv（逐约定一行）与 <tag>_pairs.csv（逐对明细）
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
lib  <- if (length(args) >= 1) args[1] else ""
tag  <- if (length(args) >= 2) args[2] else "run"
repo <- if (length(args) >= 3) args[3] else "."
outd <- if (length(args) >= 4) args[4] else "."
dir.create(outd, showWarnings = FALSE, recursive = TRUE)

if (nzchar(lib)) .libPaths(c(lib, .libPaths()))
suppressMessages(library(MatchIt))
VER <- as.character(packageVersion("MatchIt"))
LIB <- dirname(dirname(getNamespaceInfo("MatchIt", "path")))
cat(sprintf("MatchIt %s   (loaded from %s)\n", VER, LIB))
cat(sprintf("R %s.%s\n", R.version$major, R.version$minor))

COVFILE <- file.path(repo, "data", "derived", "covariate_matrix.csv")
ARCHIVE <- file.path(repo, "data", "superseded", "mahalanobis_matched_pairs.csv")
#: 生产者自己的协变量矩阵（54 个非候选），不随库分发；有则跑，无则跳过
PROD <- "E:/workbuddy/2026-06-25-15-17-49/outputs/Table_S1_Covariate_Matrix_FINAL_v2.csv"

## ---- 读归档答案 ------------------------------------------------------------
## 注意：按 subclass 分组后必须显式以**候选基因名**作为键。
## `vapply(split(x, x$subclass), ...)` 会用 list 名（subclass 序号）覆盖内层
## setNames() 的名字，于是比对会退化成"按 subclass 序号对齐"而不是按基因对齐
## —— 这是本脚本第一版的实际缺陷，已改。
by_gene <- function(d, treated_col = "treated") {
  sp <- split(d, d$subclass)
  out <- character(0)
  for (x in sp) {
    ctl <- x$Gene[x[[treated_col]] == "0"]
    trt <- x$Gene[x[[treated_col]] == "1"]
    if (length(ctl) == 1 && length(trt) == 1) out[trt] <- ctl
  }
  out
}

arch <- read.csv(ARCHIVE, stringsAsFactors = FALSE)
arch$treated <- trimws(as.character(arch$treated))
ref <- by_gene(arch)
ref <- ref[!is.na(ref) & nzchar(ref)]
cat(sprintf("归档配对：%d 对\n", length(ref)))
stopifnot(length(ref) == 30)

## ---- 工具 ------------------------------------------------------------------
impute_group_median <- function(d) {
  for (g in unique(d$Group)) {
    i <- which(d$Group == g & is.na(d$eQTL_SNPs_Mean))
    if (length(i)) d$eQTL_SNPs_Mean[i] <- median(d$eQTL_SNPs_Mean[d$Group == g], na.rm = TRUE)
  }
  d
}

norm_groups <- function(d) {
  ## 两份矩阵的 Group 标签不同（随库 "30 HOTAIR Candidate"/"44 Non-Candidate"/
  ## "30 T2DM Control"；生产者 "30_..." / "39_..."），统一成角色
  g <- d$Group
  d$role <- ifelse(grepl("Candidate", g) & !grepl("Non", g), "cand",
            ifelse(grepl("T2DM", g), "t2dm", "nca"))
  d
}

run_one <- function(dat, pool_roles, impute, m.order, label) {
  d <- if (impute) impute_group_median(dat) else dat
  cand <- d[d$role == "cand", ]
  pool <- d[d$role %in% pool_roles, ]
  cand <- cand[!is.na(cand$eQTL_SNPs_Mean), ]
  pool <- pool[!is.na(pool$eQTL_SNPs_Mean), ]
  md <- rbind(
    data.frame(Gene = cand$Gene, log10_Length = log10(cand$Length_bp), GC_pct = cand$GC_pct,
               eQTL_SNPs_Mean = cand$eQTL_SNPs_Mean, treated = 1, stringsAsFactors = FALSE),
    data.frame(Gene = pool$Gene, log10_Length = log10(pool$Length_bp), GC_pct = pool$GC_pct,
               eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean, treated = 0, stringsAsFactors = FALSE))
  md <- na.omit(md)
  err <- NULL
  if (m.order == "random") set.seed(20260915)   # random 依赖 RNG，固定种子才可复现
  m <- tryCatch(
    matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean, data = md,
            method = "nearest", distance = "mahalanobis", ratio = 1, replace = FALSE,
            m.order = m.order),
    error = function(e) { err <<- conditionMessage(e); NULL })
  if (is.null(m)) return(list(label = label, pairs = NA_integer_, checked = NA_integer_,
                              ok = NA_integer_,
                              mismatch = paste0("matchit() errored: ", err)))
  dd <- match.data(m)
  dd$treated <- as.character(dd$treated)          # match.data 给的是数值，统一成字符
  got <- by_gene(dd)
  common <- intersect(names(ref), names(got))
  same <- sum(ref[common] == got[common])
  list(label = label, pairs = length(got), checked = length(common), ok = same,
       mismatch = paste(sprintf("%s:%s->%s", common, ref[common], got[common])[
                          ref[common] != got[common]], collapse = "; "))
}

## ---- 约定矩阵 --------------------------------------------------------------
## m.order 的合法取值经实测为 "data" / "random" / "closest"（4.5.5 与 4.7.2 相同；
## "largest"/"smallest" 会报错）。上一轮把 largest/smallest 计入"已试约定"，此处更正。
ORDERS <- c("data", "random", "closest")

covar <- norm_groups(read.csv(COVFILE, stringsAsFactors = FALSE,
                              na.strings = c("", "NA", "N/A")))
cat(sprintf("随库矩阵：候选 %d，非候选 %d，T2DM %d\n",
            sum(covar$role == "cand"), sum(covar$role == "nca"), sum(covar$role == "t2dm")))

grid <- list()
for (pool in list(c("nca"), c("nca", "t2dm")))
  for (imp in c(TRUE, FALSE))
    for (ord in ORDERS)
      grid[[length(grid) + 1]] <- list(dat = covar, pool = pool, imp = imp, ord = ord,
        label = sprintf("shipped pool=%s imp=%s order=%s",
                        paste(pool, collapse = "+"), imp, ord))

if (file.exists(PROD)) {
  prod <- norm_groups(read.csv(PROD, stringsAsFactors = FALSE,
                               na.strings = c("", "NA", "N/A")))
  cat(sprintf("生产者矩阵：候选 %d，非候选 %d，T2DM %d\n",
              sum(prod$role == "cand"), sum(prod$role == "nca"), sum(prod$role == "t2dm")))
  for (imp in c(TRUE, FALSE))
    for (ord in ORDERS)
      grid[[length(grid) + 1]] <- list(dat = prod, pool = c("nca"), imp = imp, ord = ord,
        label = sprintf("producer pool=nca imp=%s order=%s", imp, ord))
} else {
  cat("生产者矩阵不在磁盘上，跳过其约定\n")
}

## ---- 跑 -------------------------------------------------------------------
res <- lapply(grid, function(g)
  run_one(g$dat, g$pool, g$imp, g$ord, g$label))
out <- do.call(rbind, lapply(res, function(r)
  data.frame(label = r$label, pairs = r$pairs, checked = r$checked,
             control_assignments_matching_archive = r$ok, mismatch = r$mismatch,
             stringsAsFactors = FALSE)))
out$matchit_version <- VER
out$matchit_lib <- LIB
write.csv(out, file.path(outd, sprintf("%s_conventions.csv", tag)), row.names = FALSE)

cat("\n=== 逐约定：与归档 30 对逐对比较 ===\n")
for (i in seq_len(nrow(out)))
  cat(sprintf("  %-46s pairs=%2s  命中 %2s/30\n", out$label[i],
              out$pairs[i], out$control_assignments_matching_archive[i]))
best <- max(out$control_assignments_matching_archive, na.rm = TRUE)
cat(sprintf("\n最佳命中：%d / %d（MatchIt %s, %s）\n", best, length(ref), VER, tag))
cat(sprintf("写入 %s\n", file.path(outd, sprintf("%s_conventions.csv", tag))))

#!/usr/bin/env Rscript
# =============================================================================
# reproduce_S4_pool44.R — SI Table S4, pool = "44 Non-Candidate" only
# =============================================================================
# Measured from the archived pair file: all 30 archived controls carry
# Group == "44 Non-Candidate", and none of the 30 "30 T2DM Control" genes is
# used. The shipped code/analyses/run_mahalanobis_matching.R builds its pool as
# `covar$Group != "Candidate"`, which would add the 30 T2DM controls -> 74.
# This script uses the pool the archived table implies, and both imputation
# conventions, so the three variants can be told apart.
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
repo <- if (length(args) >= 1) args[1] else "."
outd <- if (length(args) >= 2) args[2] else "."
dir.create(outd, showWarnings = FALSE, recursive = TRUE)

suppressMessages(library(MatchIt))
cat("MatchIt:", as.character(packageVersion("MatchIt")), "\n")

covar <- read.csv(file.path(repo, "data", "derived", "covariate_matrix.csv"),
                  stringsAsFactors = FALSE, na.strings = c("", "NA", "N/A"))

impute_group_median <- function(d) {
  for (g in unique(d$Group)) {
    idx <- which(d$Group == g & is.na(d$eQTL_SNPs_Mean))
    if (length(idx)) d$eQTL_SNPs_Mean[idx] <- median(d$eQTL_SNPs_Mean[d$Group == g], na.rm = TRUE)
  }
  d
}

run_match <- function(dat, tag, pool_labels) {
  cand <- dat[dat$Group == "30 HOTAIR Candidate", ]
  pool <- dat[dat$Group %in% pool_labels, ]
  md <- rbind(
    data.frame(Gene = cand$Gene, Group = "Treated",
               log10_Length = log10(cand$Length_bp), GC_pct = cand$GC_pct,
               eQTL_SNPs_Mean = cand$eQTL_SNPs_Mean, treated = 1, stringsAsFactors = FALSE),
    data.frame(Gene = pool$Gene, Group = "Control",
               log10_Length = log10(pool$Length_bp), GC_pct = pool$GC_pct,
               eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean, treated = 0, stringsAsFactors = FALSE))
  md <- na.omit(md)
  m <- matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean, data = md,
               method = "nearest", distance = "mahalanobis", ratio = 1, replace = FALSE)
  d <- match.data(m)
  sm <- summary(m, un = FALSE)$sum.matched
  cat(sprintf("[%s] pool=%d treated=%d pairs=%d  postSMD len %.4f gc %.4f eqtl %.4f\n",
              tag, sum(md$treated == 0), sum(md$treated == 1), sum(d$treated == 1),
              abs(sm["log10_Length", "Std. Mean Diff."]),
              abs(sm["GC_pct", "Std. Mean Diff."]),
              abs(sm["eQTL_SNPs_Mean", "Std. Mean Diff."])))
  d$Length_bp <- round(10 ^ d$log10_Length)
  write.csv(d[, c("Gene", "Group", "log10_Length", "Length_bp", "eQTL_SNPs_Mean",
                  "GC_pct", "subclass", "treated")],
            file.path(outd, sprintf("pool44_%s.csv", tag)), row.names = FALSE)
}

POOL <- "44 Non-Candidate"
run_match(impute_group_median(covar), "imputed", POOL)
run_match(covar, "naomit", POOL)
# and the pool the shipped script actually builds, for contrast
run_match(impute_group_median(covar), "imputed_pool74", c(POOL, "30 T2DM Control"))
cat("\nwrote pool44_{imputed,naomit}.csv and pool44_imputed_pool74.csv\n")

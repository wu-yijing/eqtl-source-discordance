#!/usr/bin/env Rscript
# =============================================================================
# reproduce_S4.R — SI Table S4 (30 Mahalanobis matched pairs) from a fresh clone
# =============================================================================
# The archive ships code/analyses/run_mahalanobis_matching.R, whose own NOTE says
# its Section-2 na.omit filtering does NOT reproduce the published pairs and that
# group-median imputation of eQTL_SNPs_Mean must be applied first. This script
# runs BOTH conventions on the same input so the difference is measured, not
# asserted, and writes both pair sets for comparison against
# data/superseded/mahalanobis_matched_pairs.csv.
#
#   Rscript reproduce_S4.R <repo_root> <out_dir>
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
repo <- if (length(args) >= 1) args[1] else "."
outd <- if (length(args) >= 2) args[2] else "."
dir.create(outd, showWarnings = FALSE, recursive = TRUE)

suppressMessages({library(MatchIt); library(cobalt)})
cat("R        :", R.version.string, "\n")
cat("MatchIt  :", as.character(packageVersion("MatchIt")), "\n")
cat("cobalt   :", as.character(packageVersion("cobalt")), "\n\n")

covar <- read.csv(file.path(repo, "data", "derived", "covariate_matrix.csv"),
                  stringsAsFactors = FALSE, na.strings = c("", "NA", "N/A"))
cat("covariate matrix rows:", nrow(covar), "\n")
print(table(covar$Group))

run_match <- function(dat, tag) {
  cand <- dat[dat$Group == "30 HOTAIR Candidate", ]
  pool <- dat[dat$Group != "30 HOTAIR Candidate", ]
  md <- rbind(
    data.frame(Gene = cand$Gene, Group = "Treated",
               log10_Length = log10(cand$Length_bp), GC_pct = cand$GC_pct,
               eQTL_SNPs_Mean = cand$eQTL_SNPs_Mean, treated = 1,
               stringsAsFactors = FALSE),
    data.frame(Gene = pool$Gene, Group = "Control",
               log10_Length = log10(pool$Length_bp), GC_pct = pool$GC_pct,
               eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean, treated = 0,
               stringsAsFactors = FALSE))
  md <- na.omit(md)
  cat(sprintf("\n[%s] treated %d / controls %d\n", tag,
              sum(md$treated == 1), sum(md$treated == 0)))
  m <- matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean, data = md,
               method = "nearest", distance = "mahalanobis",
               ratio = 1, replace = FALSE)
  d <- match.data(m)
  cat(sprintf("[%s] matched pairs: %d\n", tag, sum(d$treated == 1)))
  sm <- summary(m, un = FALSE)
  bal <- sm$sum.matched
  cat(sprintf("[%s] post-match SMD: length %.4f  gc %.4f  eqtl %.4f\n", tag,
              abs(bal["log10_Length", "Std. Mean Diff."]),
              abs(bal["GC_pct", "Std. Mean Diff."]),
              abs(bal["eQTL_SNPs_Mean", "Std. Mean Diff."])))
  d$Length_bp <- round(10 ^ d$log10_Length)
  write.csv(d[, c("Gene", "Group", "log10_Length", "Length_bp",
                  "eQTL_SNPs_Mean", "GC_pct", "subclass", "treated")],
            file.path(outd, sprintf("matched_pairs_%s.csv", tag)), row.names = FALSE)
  invisible(d)
}

# ---- Convention A: group-median imputation (what the NOTE says reproduces) ----
A <- covar
for (g in unique(A$Group)) {
  idx <- which(A$Group == g & is.na(A$eQTL_SNPs_Mean))
  med <- median(A$eQTL_SNPs_Mean[A$Group == g], na.rm = TRUE)
  if (length(idx) > 0) {
    cat(sprintf("impute [%s]: %d gene(s) -> median %.4f\n", g, length(idx), med))
    A$eQTL_SNPs_Mean[idx] <- med
  }
}
dA <- run_match(A, "imputed")

# ---- Convention B: na.omit only (what the shipped Section 2 does) ----
dB <- run_match(covar, "naomit")

cat("\nwrote:", file.path(outd, "matched_pairs_imputed.csv"), "and _naomit.csv\n")

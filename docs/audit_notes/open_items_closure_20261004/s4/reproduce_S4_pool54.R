#!/usr/bin/env Rscript
# =============================================================================
# reproduce_S4_pool54.R — decisive test: S4 with the 54-gene pool the producer used
# =============================================================================
# `data/derived/covariate_matrix.csv` ships 44 non-candidates; the producer's own
# Table_S1_Covariate_Matrix_FINAL_v2.csv has 54. This runs the match on the
# 54-gene pool and compares against data/superseded/mahalanobis_matched_pairs.csv.
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
v2  <- args[1]                     # Table_S1_Covariate_Matrix_FINAL_v2.csv
outd <- args[2]
dir.create(outd, showWarnings = FALSE, recursive = TRUE)
suppressMessages(library(MatchIt))
cat("MatchIt:", as.character(packageVersion("MatchIt")), "\n")

d <- read.csv(v2, stringsAsFactors = FALSE, na.strings = c("", "NA", "N/A"))
cat("rows:", nrow(d), "\n"); print(table(d$Group))

d$eQTL_SNPs_Mean <- ifelse(is.na(d$eQTL_SNPs_Max) & is.na(d$eQTL_SNPs_Min), NA,
                    ifelse(is.na(d$eQTL_SNPs_Max), d$eQTL_SNPs_Min,
                    ifelse(is.na(d$eQTL_SNPs_Min), d$eQTL_SNPs_Max,
                           (d$eQTL_SNPs_Max + d$eQTL_SNPs_Min) / 2)))
cat("missing eQTL_SNPs_Mean after Max/Min mean:", sum(is.na(d$eQTL_SNPs_Mean)), "\n")

impute <- function(x) {
  for (g in unique(x$Group)) {
    i <- which(x$Group == g & is.na(x$eQTL_SNPs_Mean))
    if (length(i)) {
      m <- median(x$eQTL_SNPs_Mean[x$Group == g], na.rm = TRUE)
      cat(sprintf("  impute %-22s %2d -> %.4f\n", g, length(i), m))
      x$eQTL_SNPs_Mean[i] <- m
    }
  }
  x
}

run <- function(x, tag, seed) {
  cand <- x[x$Group == "30_HOTAIR_Candidate", ]
  pool <- x[x$Group != "30_HOTAIR_Candidate", ]
  md <- rbind(
    data.frame(Gene = cand$Gene, log10_Length = log10(cand$Length_bp), GC_pct = cand$GC_pct,
               eQTL_SNPs_Mean = cand$eQTL_SNPs_Mean, treated = 1, stringsAsFactors = FALSE),
    data.frame(Gene = pool$Gene, log10_Length = log10(pool$Length_bp), GC_pct = pool$GC_pct,
               eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean, treated = 0, stringsAsFactors = FALSE))
  md <- na.omit(md)
  if (!is.null(seed)) set.seed(seed)
  m <- matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean, data = md,
               method = "nearest", distance = "mahalanobis", ratio = 1, replace = FALSE)
  r <- match.data(m)
  cat(sprintf("[%s seed=%s] pool %d treated %d -> pairs %d\n", tag,
              ifelse(is.null(seed), "-", seed), sum(md$treated == 0), sum(md$treated == 1),
              sum(r$treated == 1)))
  r$Length_bp <- round(10 ^ r$log10_Length)
  write.csv(r[, c("Gene", "log10_Length", "Length_bp", "eQTL_SNPs_Mean", "GC_pct", "subclass", "treated")],
            file.path(outd, sprintf("pool54_%s.csv", tag)), row.names = FALSE)
}

for (s in list(NULL, 42)) run(impute(d), ifelse(is.null(s), "noseed", paste0("seed", s)), s)
cat("\ndone\n")

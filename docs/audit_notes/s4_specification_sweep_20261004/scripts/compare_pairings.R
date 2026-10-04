# =============================================================================
# compare_pairings.R -- dump the pairing of the documented specification
# =============================================================================
# Run once per library and diff the two outputs. The pairing is taken from
# match.matrix. `subclass` is deliberately NOT used to align the two runs:
# MatchIt numbers subclass in the order matches are formed, and that numbering
# differs between 4.5.5 and 4.7.2 for identical input (4.5.5: 1, 12, 23, 25, ...;
# 4.7.2: 1, 2, 3, 4, ...). Aligning on subclass therefore reports a difference
# that is not in the matching. This file exists to make that trap reproducible.
#
# Usage:  PRELIB=<lib> Rscript compare_pairings.R <repo-root> <out-file>
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
REPO <- if (length(args) >= 1) args[1] else "."
OUTF <- if (length(args) >= 2) args[2] else "pairing.csv"
PRELIB <- Sys.getenv("PRELIB"); if (PRELIB != "") .libPaths(c(PRELIB, .libPaths()))
suppressMessages(library(MatchIt))
cat("MatchIt:", as.character(packageVersion("MatchIt")), "from", find.package("MatchIt"), "\n")

covar <- read.csv(file.path(REPO, "data/derived/covariate_matrix.csv"), stringsAsFactors = FALSE)
covar$eQTL_SNPs_Mean <- as.numeric(covar$eQTL_SNPs_Mean)
imp <- aggregate(eQTL_SNPs_Mean ~ Group, data = covar, FUN = median, na.rm = TRUE)
for (i in seq_len(nrow(imp))) {
  k <- which(covar$Group == imp$Group[i] & is.na(covar$eQTL_SNPs_Mean))
  if (length(k)) covar$eQTL_SNPs_Mean[k] <- imp$eQTL_SNPs_Mean[i]
}
arch <- read.csv(file.path(REPO, "data/superseded/mahalanobis_matched_pairs.csv"), stringsAsFactors = FALSE)
ORD <- arch$Gene[arch$treated == 1]
ca <- covar[covar$Group == "30 HOTAIR Candidate", ]
ca <- ca[match(ORD, ca$Gene), ]
pool <- covar[covar$Group == "44 Non-Candidate", ]
d <- rbind(
  data.frame(Gene = ca$Gene, log10_Length = log10(ca$Length_bp), GC_pct = ca$GC_pct,
             eQTL_SNPs_Mean = ca$eQTL_SNPs_Mean, treated = 1, stringsAsFactors = FALSE),
  data.frame(Gene = pool$Gene, log10_Length = log10(pool$Length_bp), GC_pct = pool$GC_pct,
             eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean, treated = 0, stringsAsFactors = FALSE))
rownames(d) <- d$Gene
m <- matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean, data = d,
             method = "nearest", distance = "mahalanobis",
             ratio = 1, replace = FALSE, m.order = "data")
md <- match.data(m)
mm <- m$match.matrix
out <- data.frame(candidate = rownames(mm), control = as.character(mm[, 1]),
                  subclass_this_version = md$subclass[md$treated == 1][match(rownames(mm), md$Gene[md$treated == 1])],
                  stringsAsFactors = FALSE)
cat("subclass by candidate order  :", paste(head(out$subclass_this_version, 10), collapse = ", "), "...\n")
cat("subclass monotone in that order:", !is.unsorted(out$subclass_this_version), "\n")
cat("subclass == pair index         :", identical(out$subclass_this_version, seq_len(30)), "\n\n")
for (i in seq_len(nrow(out))) cat(sprintf("%2d %-10s %s\n", i, out$candidate[i], out$control[i]))
write.csv(out, OUTF, row.names = FALSE)

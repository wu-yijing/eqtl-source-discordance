# diagnose_S4_order.R -- is the archived control SET reproducible, and does the
# candidate processing order carry the result?
# -----------------------------------------------------------------------------
# Runs the documented specification (nearest + Mahalanobis, ratio 1, replace =
# FALSE, pool = the 44 non-candidates) under many candidate orders and both
# MatchIt versions, and reports the overlap with the archived control set.
# Usage: Rscript diagnose_S4_order.R <repo-root>
args <- commandArgs(trailingOnly = TRUE)
REPO <- if (length(args) >= 1) args[1] else "."
PRELIB <- Sys.getenv("PRELIB"); if (PRELIB != "") .libPaths(c(PRELIB, .libPaths()))
suppressMessages(library(MatchIt))
cat("MatchIt:", as.character(packageVersion("MatchIt")), "from", find.package("MatchIt"), "\n\n")

covar <- read.csv(file.path(REPO, "data/derived/covariate_matrix.csv"), stringsAsFactors = FALSE)
covar$eQTL_SNPs_Mean <- as.numeric(covar$eQTL_SNPs_Mean)
imp <- aggregate(eQTL_SNPs_Mean ~ Group, data = covar, FUN = median, na.rm = TRUE)
for (i in seq_len(nrow(imp))) {
  k <- which(covar$Group == imp$Group[i] & is.na(covar$eQTL_SNPs_Mean))
  if (length(k)) covar$eQTL_SNPs_Mean[k] <- imp$eQTL_SNPs_Mean[i]
}
CAND <- "30 HOTAIR Candidate"; NONCAN <- "44 Non-Candidate"
canddf <- covar[covar$Group == CAND, ]; pool <- covar[covar$Group == NONCAN, ]
arch <- read.csv(file.path(REPO, "data/superseded/mahalanobis_matched_pairs.csv"), stringsAsFactors = FALSE)
a_ctl <- arch$Gene[arch$treated == 0]; a_can <- arch$Gene[arch$treated == 1]
cat("archived candidates (first 8):", paste(head(a_can, 8), collapse = " "), "\n")
pd <- covar$PullDown_Unused[match(a_can, covar$Gene)]
cat("archived candidate order is PullDown-descending? ",
    identical(a_can, a_can[order(pd, decreasing = TRUE)]), "\n")
cat("archived candidate order is the matrix order?    ", identical(a_can, canddf$Gene), "\n")
cat("archived candidate order is the PullDown file order (NA last)? ",
    identical(a_can, a_can[order(pd, decreasing = TRUE, na.last = TRUE)]), "\n\n")

run_order <- function(order_genes, m.order) {
  ca <- canddf[match(order_genes, canddf$Gene), ]
  d <- rbind(
    data.frame(Gene = ca$Gene, log10_Length = log10(ca$Length_bp), GC_pct = ca$GC_pct,
               eQTL_SNPs_Mean = ca$eQTL_SNPs_Mean, treated = 1, stringsAsFactors = FALSE),
    data.frame(Gene = pool$Gene, log10_Length = log10(pool$Length_bp), GC_pct = pool$GC_pct,
               eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean, treated = 0, stringsAsFactors = FALSE))
  m <- tryCatch(matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean, data = d,
                        method = "nearest", distance = "mahalanobis",
                        ratio = 1, replace = FALSE, m.order = m.order),
                error = function(e) e)
  if (inherits(m, "error")) return(list(ok = FALSE, msg = conditionMessage(m)))
  md <- match.data(m)
  ctl <- md$Gene[md$treated == 0]
  list(ok = TRUE, set = length(intersect(ctl, a_ctl)),
       ctl = ctl[order(md$subclass[md$treated == 0])])
}

orders <- list(
  archived        = a_can,
  matrix          = canddf$Gene,
  alphabetical    = sort(canddf$Gene),
  pullDown_desc   = canddf$Gene[order(covar$PullDown_Unused[match(canddf$Gene, covar$Gene)], decreasing = TRUE)],
  pullDown_asc    = canddf$Gene[order(covar$PullDown_Unused[match(canddf$Gene, covar$Gene)])],
  reverse_matrix  = rev(canddf$Gene),
  length_asc      = canddf$Gene[order(canddf$Length_bp)],
  random          = { set.seed(20261004); sample(canddf$Gene) }
)
for (mo in c("data", "closest")) {
  cat("---- m.order =", mo, "----\n")
  for (nm in names(orders)) {
    r <- run_order(orders[[nm]], mo)
    if (!r$ok) { cat(sprintf("  %-15s ERROR %s\n", nm, r$msg)); next }
    cat(sprintf("  %-15s control SET overlap %2d/30\n", nm, r$set))
  }
}

cat("\n---- 30 random orders (m.order = data) ----\n")
hits <- integer(0)
for (i in 1:30) {
  set.seed(1000 + i)
  r <- run_order(sample(canddf$Gene), "data")
  if (r$ok) hits <- c(hits, r$set)
}
cat("  overlaps:", paste(hits, collapse = " "), "\n")
cat(sprintf("  n = %d | max = %d | 30/30 count = %d\n", length(hits), max(hits), sum(hits == 30)))

cat("\n---- archived order, the OTHER pool and both versions ----\n")
r2 <- run_order(a_can, "data")
cat("  archived order control set == archived control set: ",
    identical(sort(r2$ctl), sort(a_ctl)), "\n")
cat("  pairing agreement with archive under archived order: ",
    { d <- rbind(
        data.frame(Gene = canddf[match(a_can, canddf$Gene), ]$Gene, treated = 1, stringsAsFactors = FALSE),
        data.frame(Gene = r2$ctl, treated = 0, stringsAsFactors = FALSE));
      a_part <- a_ctl[match(arch$subclass[arch$treated == 1], arch$subclass[arch$treated == 0])]
      sum(a_part == r2$ctl) }, " / 30\n")

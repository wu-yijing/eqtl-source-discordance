# =============================================================================
# order_sensitivity.R -- does the reported claim depend on the candidate order?
# =============================================================================
# SI Table S4's control set reproduces 30/30 only when the candidates are processed
# in the submitted table's own order. That order is not derivable from the shipped
# covariate matrix (15 candidates tie at PullDown_Unused = 0). The question this
# script answers is NOT "can the order be recovered" -- it cannot -- but:
#
#   does any reported conclusion move if a different (equally defensible) order is used?
#
# The candidate arm is fixed: it is the same 30 genes in every run, so its endpoint
# counts (84 / 81 cells, 2 and 5 significant) are order-invariant. Only the *control*
# arm moves. This script therefore sweeps the order and reports the distribution of
#   (a) overlap between the produced control set and the submitted one, and
#   (b) every Table S26 contrast, whose candidate side is constant.
#
# Usage: PRELIB=<pinned-lib> Rscript order_sensitivity.R <repo-root> [n_perm]
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
REPO    <- if (length(args) >= 1) args[1] else "."
NPERM   <- if (length(args) >= 2) as.integer(args[2]) else 500L
PRELIB  <- Sys.getenv("PRELIB"); if (PRELIB != "") .libPaths(c(PRELIB, .libPaths()))
suppressMessages(library(MatchIt))
cat("MatchIt :", as.character(packageVersion("MatchIt")), "\n\n")

covar <- read.csv(file.path(REPO, "data/derived/covariate_matrix.csv"), stringsAsFactors = FALSE)
covar$eQTL_SNPs_Mean <- as.numeric(covar$eQTL_SNPs_Mean)
imp <- aggregate(eQTL_SNPs_Mean ~ Group, data = covar, FUN = median, na.rm = TRUE)
for (i in seq_len(nrow(imp))) {
  k <- which(covar$Group == imp$Group[i] & is.na(covar$eQTL_SNPs_Mean))
  if (length(k)) covar$eQTL_SNPs_Mean[k] <- imp$eQTL_SNPs_Mean[i]
}
CAND <- "30 HOTAIR Candidate"; NONCAN <- "44 Non-Candidate"
canddf <- covar[covar$Group == CAND, ]; pool <- covar[covar$Group == NONCAN, ]

ARCH <- file.path(REPO, "data/superseded/mahalanobis_matched_pairs.csv")
arch <- read.csv(ARCH, stringsAsFactors = FALSE)
a_can <- arch$Gene[arch$treated == 1]; a_ctl <- arch$Gene[arch$treated == 0]

# ---- the documented matching, as a function of the candidate order ----------
match_controls <- function(order_genes) {
  cd <- canddf[match(order_genes, canddf$Gene), ]
  d <- rbind(
    data.frame(Gene = cd$Gene, log10_Length = log10(cd$Length_bp), GC_pct = cd$GC_pct,
               eQTL_SNPs_Mean = cd$eQTL_SNPs_Mean, treated = 1, stringsAsFactors = FALSE),
    data.frame(Gene = pool$Gene, log10_Length = log10(pool$Length_bp), GC_pct = pool$GC_pct,
               eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean, treated = 0, stringsAsFactors = FALSE))
  rownames(d) <- d$Gene
  m <- matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean, data = d,
               method = "nearest", distance = "mahalanobis",
               ratio = 1, replace = FALSE, m.order = "data")
  as.character(m$match.matrix[, 1])
}

# ---- Table S26 machinery (identical to emit_S4_table.R §6) -------------------
TRAITS <- c("DR", "DN", "DPN")
gtex <- read.csv(file.path(REPO, "data/derived/gtex_Z.csv"), stringsAsFactors = FALSE)
eqg  <- read.csv(file.path(REPO, "data/derived/eqtlgen_Z.csv"), stringsAsFactors = FALSE)
arm <- function(genes, tab, fld) {
  v <- tab[tab$Gene %in% genes & tab$Trait %in% TRAITS, c("Gene", "Trait", fld)]
  v <- v[!is.na(v[[fld]]) & v[[fld]] != "", ]
  num <- suppressWarnings(as.numeric(gsub("\\+", "", as.character(v[[fld]]))))
  list(pos = sum(!is.na(num) & num < 0.05), n = nrow(v))
}
CONTRASTS <- list(c("GTEx FDR_q_ACAT_O (BH q<0.05)", "gtex", "FDR_q_ACAT_O"),
                  c("GTEx P_ACAT_O (nominal)",        "gtex", "P_ACAT_O"),
                  c("eQTLGen BH_q (BH q<0.05)",       "eq",   "BH_q"),
                  c("eQTLGen P (nominal)",            "eq",   "P"))
s26 <- function(genes) {
  do.call(rbind, lapply(CONTRASTS, function(s) {
    tab <- if (s[2] == "gtex") gtex else eqg
    ca <- arm(a_can, tab, s[3]); ck <- arm(genes, tab, s[3])
    p <- fisher.test(matrix(c(ca$pos, ca$n - ca$pos, ck$pos, ck$n - ck$pos),
                            nrow = 2, byrow = TRUE))$p.value
    data.frame(label = s[1], ca_pos = ca$pos, ca_n = ca$n,
               ck_pos = ck$pos, ck_n = ck$n, P = p, stringsAsFactors = FALSE)
  }))
}

# ---- 0. candidate arm is order-invariant ------------------------------------
base <- s26(a_ctl)
cat("candidate arm (order-invariant by construction):\n")
print(base[, c("label", "ca_pos", "ca_n")], row.names = FALSE)

# ---- 1. the submitted order --------------------------------------------------
ctl0 <- match_controls(a_can)
cat(sprintf("\nsubmitted order        : control set %d / 30 of the submitted controls\n",
            length(intersect(ctl0, a_ctl))))
print(s26(ctl0)[, c("label", "ck_pos", "ck_n", "P")], row.names = FALSE)

# ---- 2. deterministic alternative orders ------------------------------------
alt <- list(
  "alphabetical"      = sort(canddf$Gene),
  "PullDown (stable)" = canddf$Gene[order(-canddf$PullDown_Unused)],
  "PullDown reversed" = rev(canddf$Gene[order(-canddf$PullDown_Unused)]),
  "matrix row order"  = canddf$Gene
)
cat("\ndeterministic alternatives:\n")
for (nm in names(alt)) {
  ct <- match_controls(alt[[nm]])
  s <- s26(ct)
  cat(sprintf("  %-18s overlap %2d/30 | ctrl sim: %s | %s\n", nm, length(intersect(ct, a_ctl)),
              paste(sprintf("%d/%-3d", s$ck_pos, s$ck_n), collapse = " "),
              paste(sprintf("%.3f", s$P), collapse = " ")))
}

# ---- 3. random permutations --------------------------------------------------
set.seed(20261005)
ov <- integer(NPERM); res <- vector("list", NPERM)
for (i in seq_len(NPERM)) {
  ct <- match_controls(sample(a_can))
  ov[i] <- length(intersect(ct, a_ctl))
  res[[i]] <- s26(ct)
}
cat(sprintf("\n%d random candidate permutations:\n", NPERM))
cat(sprintf("  control-set overlap with the submitted set : min %d, median %.0f, max %d of 30\n",
            min(ov), median(ov), max(ov)))
cat(sprintf("  permutations reaching 30/30                : %d\n", sum(ov == 30)))

cat("\n  per-contrast distribution over the permutations (candidate side is fixed):\n")
for (j in seq_along(CONTRASTS)) {
  ck_pos <- sapply(res, function(r) r$ck_pos[j]); ck_n <- sapply(res, function(r) r$ck_n[j])
  pv <- sapply(res, function(r) r$P[j])
  cat(sprintf("   %-32s ctrl cells %s..%s | ctrl sig %d..%d | P %.3f..%.3f | P<0.05 in %.0f%% | reported (2/84 vs 1/60 -> 1.000 etc.)\n",
              CONTRASTS[[j]][1], min(ck_n), max(ck_n), min(ck_pos), max(ck_pos),
              min(pv), max(pv), 100 * mean(pv < 0.05)))
}
cat("\n  reported values for reference:\n")
print(base[, c("label", "ck_pos", "ck_n", "P")], row.names = FALSE)

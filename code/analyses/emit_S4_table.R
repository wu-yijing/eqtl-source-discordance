# =============================================================================
# emit_S4_table.R -- re-emit SI Table S4 under the specification the Methods state
# =============================================================================
# Produces Supporting Information Table S4 (Mahalanobis matched-pair data, 30
# candidate-control pairs) from the shipped inputs, under the environment
# env/renv.lock pins:
#
#   R 4.5.2, MatchIt 4.5.5, cobalt 4.5.2, optmatch 0.10.6
#   method = "nearest", distance = "mahalanobis", ratio = 1, replace = FALSE,
#   m.order = "data"
#   treated   = the 30 HOTAIR candidates
#   pool      = the 44 genes labelled "44 Non-Candidate" (Methods 1.9: "controls
#               drawn from a pool of 44 high-confidence non-candidate genes")
#   covariates = log10(Length_bp), GC_pct, cis-eQTL SNP count (additional file
#               Table S3), with the group-median imputation Methods 1.9 discloses
#   candidate processing order = the listing order of the submitted Table S4
#
# THE PAIRING IS READ FROM match.matrix, NOT FROM subclass
# -------------------------------------------------------
# MatchIt numbers `subclass` in the order matches are formed, and that numbering
# is NOT the candidate data order -- and it changed between 4.5.5 (non-monotone
# over the treated units: 1, 12, 23, 25, ...) and 4.7.2 (monotone: 1, 2, 3, ...).
# The two versions nevertheless return the *same* pairing: 30/30 identical rows
# of match.matrix. Reading the pairing off `subclass` therefore compares two
# different labellings and manufactures a difference that is not there -- which
# is why this script, and any comparison against it, uses match.matrix.
#
# Usage:  Rscript emit_S4_table.R <repo-root> <out-dir>
#         (the pinned library must be first on .libPaths(); see verify_pinned_env.R)
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
REPO <- if (length(args) >= 1) args[1] else "."
OUTD <- if (length(args) >= 2) args[2] else "."
PRELIB <- Sys.getenv("PRELIB"); if (PRELIB != "") .libPaths(c(PRELIB, .libPaths()))
# 2026-10-05: create the output directory if absent. write.csv() below does not make it,
# so a reader (or the release gate) that passes a fresh path used to fail on the last
# step with "cannot open the connection".
dir.create(OUTD, showWarnings = FALSE, recursive = TRUE)

suppressMessages(library(MatchIt))
cat("MatchIt :", as.character(packageVersion("MatchIt")), "from", find.package("MatchIt"), "\n")
cat("R       :", R.version.string, "\n\n")

# ---- 1. inputs --------------------------------------------------------------
covar <- read.csv(file.path(REPO, "data/derived/covariate_matrix.csv"), stringsAsFactors = FALSE)
covar$eQTL_SNPs_Mean <- as.numeric(covar$eQTL_SNPs_Mean)

# group-median imputation, as Methods 1.9 discloses. The counts it produces are
# the archive's own disclosure (3 of 30 candidates; 17 of the 44 non-candidates;
# 11 of the 30 T2DM controls) and are asserted below rather than assumed.
imp <- aggregate(eQTL_SNPs_Mean ~ Group, data = covar, FUN = median, na.rm = TRUE)
n_imp <- integer(0)
for (i in seq_len(nrow(imp))) {
  k <- which(covar$Group == imp$Group[i] & is.na(covar$eQTL_SNPs_Mean))
  if (length(k)) covar$eQTL_SNPs_Mean[k] <- imp$eQTL_SNPs_Mean[i]
  n_imp[imp$Group[i]] <- length(k)
}
stopifnot(n_imp[["30 HOTAIR Candidate"]] == 3,
          n_imp[["44 Non-Candidate"]] == 17,
          n_imp[["30 T2DM Control"]] == 11)
cat("imputation reproduces the disclosed counts: 3 / 17 / 11\n")

CAND <- "30 HOTAIR Candidate"; NONCAN <- "44 Non-Candidate"
canddf <- covar[covar$Group == CAND, ]
pool <- covar[covar$Group == NONCAN, ]
cat(sprintf("candidates %d | pool (44 Non-Candidate) %d\n", nrow(canddf), nrow(pool)))

# ---- 2. candidate processing order -----------------------------------------
# Taken from the submitted Table S4's own listing. It is PullDown_Unused
# non-increasing (asserted), which is how the submitted table presents the
# candidates -- but it is NOT what order(..., decreasing = TRUE) returns from the
# covariate matrix, because the cis-eQTL SNP counts tie and the tie-break is not
# recoverable from the matrix alone. The order that reproduces the submitted
# control SET is this one: over 30 random permutations the best overlap is 29 of
# 30, and the seven deterministic alternatives tested (matrix, alphabetical,
# PullDown, reverse, length, ...) reach 27-29. See the order diagnostic.
ARCH <- file.path(REPO, "data/superseded/mahalanobis_matched_pairs.csv")
arch <- read.csv(ARCH, stringsAsFactors = FALSE)
ORDER <- arch$Gene[arch$treated == 1]
stopifnot(setequal(ORDER, canddf$Gene))
stopifnot(!is.unsorted(-covar$PullDown_Unused[match(ORDER, covar$Gene)]))
canddf <- canddf[match(ORDER, canddf$Gene), ]

# ---- 3. the documented matching ---------------------------------------------
d <- rbind(
  data.frame(Gene = canddf$Gene, log10_Length = log10(canddf$Length_bp),
             GC_pct = canddf$GC_pct, eQTL_SNPs_Mean = canddf$eQTL_SNPs_Mean,
             treated = 1, stringsAsFactors = FALSE),
  data.frame(Gene = pool$Gene, log10_Length = log10(pool$Length_bp),
             GC_pct = pool$GC_pct, eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean,
             treated = 0, stringsAsFactors = FALSE))
rownames(d) <- d$Gene
m <- matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean, data = d,
             method = "nearest", distance = "mahalanobis",
             ratio = 1, replace = FALSE, m.order = "data")
mm <- m$match.matrix
stopifnot(nrow(mm) == 30, ncol(mm) == 1)
pairs <- data.frame(pair = seq_len(nrow(mm)), candidate = rownames(mm),
                    control = as.character(mm[, 1]), stringsAsFactors = FALSE)
stopifnot(identical(pairs$candidate, canddf$Gene))
cat(sprintf("matched pairs: %d / 30 candidates\n", nrow(pairs)))

# ---- 4. agreement with the submitted table ---------------------------------
a_can <- arch$Gene[arch$treated == 1]; a_ctl <- arch$Gene[arch$treated == 0]
cat(sprintf("\ncandidate SET vs submitted : %s\n", setequal(pairs$candidate, a_can)))
cat(sprintf("control   SET vs submitted : %d / 30\n", length(intersect(pairs$control, a_ctl))))
cat(sprintf("  submitted control not selected : %s\n",
            paste(setdiff(a_ctl, pairs$control), collapse = ", ")))
# The submitted file lists both arms in subclass order 1..30, so the submitted
# partner of a_can[j] is a_ctl[j]; re-index onto this script's candidate order.
a_partner <- a_ctl[match(pairs$candidate, a_can)]
cat(sprintf("PAIRING agreement with submitted : %d / 30\n", sum(pairs$control == a_partner)))

# ---- 5. write the re-emitted table, in the submitted file's own column layout
# Column layout, quoting and numeric formatting are copied from the submitted
# file byte-for-byte, so that a diff between the two isolates the pairing.
#   Length_bp is written with one decimal (the submitted file's own convention);
#   log10_Length, GC_pct and n_eQTL_SNPs are written as plain numerics so R's
#   default 15-significant-digit conversion reproduces the submitted strings
#   ("1.5", "1", "45") rather than "1.0" / "45.0".
GRP <- function(t) ifelse(t == 1, "30_HOTAIR_Candidate", "NonCandidate")
block <- function(df, t) {
  data.frame(Gene = df$Gene, Group = GRP(t),
             log10_Length = log10(df$Length_bp),
             Length_bp = sprintf("%.1f", df$Length_bp),
             n_eQTL_SNPs = df$eQTL_SNPs_Mean,
             GC_pct = df$GC_pct,
             subclass = seq_len(30), treated = as.integer(t),
             stringsAsFactors = FALSE)
}
cp <- pool[match(pairs$control, pool$Gene), ]
out <- rbind(block(canddf, 1), block(cp, 0))
f <- file.path(OUTD, "mahalanobis_matched_pairs.csv")
write.csv(out, f, row.names = FALSE, quote = FALSE)
# R's text-mode connection translates LF to CRLF on Windows, and .gitattributes
# asks for LF (`* text=auto eol=lf`). Rewrite the bytes so a diff against the
# submitted file isolates the pairing rather than the line terminator.
raw <- readBin(f, "raw", file.info(f)$size)
raw <- raw[!(raw == as.raw(13) & c(raw[-1], as.raw(0)) == as.raw(10))]
writeBin(raw, f)
cat(sprintf("\nwrote %s (%d rows, LF, no quoting) -- %d bytes\n", f, nrow(out), length(raw)))
write.csv(pairs, file.path(OUTD, "S4_pairs_1to1.csv"), row.names = FALSE)

# ---- 6. Table S26 is a function of this pairing: recompute it ---------------
TRAITS <- c("DR", "DN", "DPN")
gtex <- read.csv(file.path(REPO, "data/derived/gtex_Z.csv"), stringsAsFactors = FALSE)
eqg <- read.csv(file.path(REPO, "data/derived/eqtlgen_Z.csv"), stringsAsFactors = FALSE)
arm <- function(genes, tab, fld) {
  v <- tab[tab$Gene %in% genes & tab$Trait %in% TRAITS, c("Gene", "Trait", fld)]
  v <- v[!is.na(v[[fld]]) & v[[fld]] != "", ]
  num <- suppressWarnings(as.numeric(gsub("\\+", "", as.character(v[[fld]]))))
  list(pos = sum(!is.na(num) & num < 0.05), n = nrow(v), num = num)
}
cat("\n-- Table S26 under the re-emitted pairing --\n")
cat(sprintf("%-10s %-12s %-12s %-16s %s\n", "source", "endpoint", "candidate", "matched-control", "Fisher P"))
for (s in list(c("GTEx", "gtex", "FDR_q_ACAT_O", "BH q<0.05"),
               c("GTEx", "gtex", "P_ACAT_O", "nominal p<0.05"),
               c("eQTLGen", "eq", "BH_q", "BH q<0.05"),
               c("eQTLGen", "eq", "P", "nominal p<0.05"))) {
  tab <- if (s[2] == "gtex") gtex else eqg
  ca <- arm(pairs$candidate, tab, s[3]); ck <- arm(pairs$control, tab, s[3])
  p <- fisher.test(matrix(c(ca$pos, ca$n - ca$pos, ck$pos, ck$n - ck$pos), nrow = 2, byrow = TRUE))$p.value
  cat(sprintf("%-10s %-12s %2d/%-9d %2d/%-13d %.3f\n", s[1], s[4], ca$pos, ca$n, ck$pos, ck$n, p))
}

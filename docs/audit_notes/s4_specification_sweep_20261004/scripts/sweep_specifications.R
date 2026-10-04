# =============================================================================
# sweep_specifications.R -- how far the specification space gets towards SI Table S4
# =============================================================================
# Companion to docs/audit_notes/s4_matchit_version_test_20261004/ (which ran 18
# conventions under two MatchIt versions). This widens the same question: not
# "do the two versions agree" but "does ANY specification reproduce the table".
#
# Distance x method x covariate subset x row order x pool x m.order, each fitted
# against the archived pairs, with two metrics per specification:
#
#   control SET overlap  -- how many of the 30 archived controls the run selects
#   PAIR agreement       -- how many of the 30 candidate-control PAIRS it reproduces
#
# The pairing is read from match.matrix, never from subclass: MatchIt numbers
# subclass in the order matches form, that order changed between 4.5.5 and 4.7.2,
# and reading the pairing off subclass therefore manufactures a version
# difference that is not in the data (see emit_S4_table.R's header).
#
# Usage:  Rscript sweep_specifications.R <repo-root> <out-file> [tag]
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
REPO <- if (length(args) >= 1) args[1] else "."
OUTF <- if (length(args) >= 2) args[2] else "s4_sweep.csv"
TAG <- if (length(args) >= 3) args[3] else "run"
PRELIB <- Sys.getenv("PRELIB"); if (PRELIB != "") .libPaths(c(PRELIB, .libPaths()))
suppressMessages({library(MatchIt); library(cobalt)})

cat("MatchIt :", as.character(packageVersion("MatchIt")), "from", find.package("MatchIt"), "\n")
cat("cobalt  :", as.character(packageVersion("cobalt")), "\n")
cat("R       :", R.version.string, "\ntag     :", TAG, "\n")

covar <- read.csv(file.path(REPO, "data/derived/covariate_matrix.csv"), stringsAsFactors = FALSE)
covar$eQTL_SNPs_Mean <- as.numeric(covar$eQTL_SNPs_Mean)
imp <- aggregate(eQTL_SNPs_Mean ~ Group, data = covar, FUN = median, na.rm = TRUE)
for (i in seq_len(nrow(imp))) {
  k <- which(covar$Group == imp$Group[i] & is.na(covar$eQTL_SNPs_Mean))
  if (length(k)) covar$eQTL_SNPs_Mean[k] <- imp$eQTL_SNPs_Mean[i]
}
CAND <- "30 HOTAIR Candidate"; NONCAN <- "44 Non-Candidate"
candidate <- covar[covar$Group == CAND, ]
mk <- function(d) rbind(
  data.frame(Gene = candidate$Gene, log10_Length = log10(candidate$Length_bp),
             GC_pct = candidate$GC_pct, eQTL_SNPs_Mean = candidate$eQTL_SNPs_Mean,
             treated = 1, stringsAsFactors = FALSE),
  data.frame(Gene = d$Gene, log10_Length = log10(d$Length_bp),
             GC_pct = d$GC_pct, eQTL_SNPs_Mean = d$eQTL_SNPs_Mean,
             treated = 0, stringsAsFactors = FALSE))
POOLS <- list(pool74 = mk(covar[covar$Group != CAND, ]), pool44 = mk(covar[covar$Group == NONCAN, ]))

arch <- read.csv(file.path(REPO, "data/superseded/mahalanobis_matched_pairs.csv"), stringsAsFactors = FALSE)
a_t <- arch[arch$treated == 1, ]; a_c <- arch[arch$treated == 0, ]
arch_partner <- setNames(a_c$Gene[match(a_t$subclass, a_c$subclass)], a_t$Gene)
cat(sprintf("archive: %d pairs; candidates %s ...\n", nrow(a_t), paste(head(a_t$Gene, 4), collapse = ",")))

evaluate <- function(md, method, distance, m.order, covset, seed = 20261004) {
  if (!is.null(m.order) && m.order == "random") set.seed(seed)
  f <- as.formula(paste("treated ~", paste(covset, collapse = " + ")))
  d <- md; rownames(d) <- d$Gene
  mm <- tryCatch(
    if (is.null(m.order)) matchit(f, data = d, method = method, distance = distance, ratio = 1, replace = FALSE)
    else matchit(f, data = d, method = method, distance = distance, ratio = 1, replace = FALSE, m.order = m.order),
    error = function(e) e)
  if (inherits(mm, "error"))
    return(list(ok = FALSE, msg = conditionMessage(mm), agree = NA_integer_,
                set_ov = NA_integer_, n_ctrl = NA_integer_))
  M <- mm$match.matrix
  # `full` matching is not a 1:1 design: match.matrix has one column per control
  # and reading column 1 would silently truncate it to a 1:1 subset that is not
  # what the method returns. Only 1:1 methods are swept, and the control set is
  # read from every column so the count cannot be understated.
  if (ncol(M) != 1)
    return(list(ok = FALSE, msg = "not a 1:1 design", agree = NA_integer_,
                set_ov = NA_integer_, n_ctrl = NA_integer_))
  got <- M[, 1]
  names(got) <- rownames(M)
  common <- intersect(a_t$Gene, names(got))
  agree <- sum(!is.na(got[common]) & got[common] == arch_partner[common])
  ctl <- unique(as.character(M))
  list(ok = TRUE, msg = "", agree = agree,
       set_ov = length(intersect(ctl, a_c$Gene)), n_ctrl = length(ctl))
}

COVSETS <- list(c("log10_Length", "GC_pct", "eQTL_SNPs_Mean"), c("log10_Length", "GC_pct"),
                c("log10_Length", "eQTL_SNPs_Mean"), c("GC_pct", "eQTL_SNPs_Mean"),
                "log10_Length", "GC_pct", "eQTL_SNPs_Mean")
pd_of <- function(g) covar$PullDown_Unused[match(g, covar$Gene)]
ORDERS <- list(asis = function(d) d, gene = function(d) d[order(d$Gene), ],
               pd_desc = function(d) { dd <- d; dd$pd <- pd_of(dd$Gene); dd[order(dd$pd, decreasing = TRUE), ] })

res <- list(); k <- 0
run <- function(dat, method, distance, m.order, covset, label) {
  r <- evaluate(dat, method, distance, m.order, covset); k <<- k + 1
  res[[k]] <<- data.frame(label = label, method = method, distance = distance,
                          m.order = if (is.null(m.order)) "<default>" else m.order,
                          covset = paste(covset, collapse = "+"), ok = r$ok,
                          agree = r$agree, set_ov = r$set_ov, n_ctrl = r$n_ctrl,
                          msg = r$msg, stringsAsFactors = FALSE)
}
for (pn in names(POOLS)) for (on in names(ORDERS)) for (cs in seq_along(COVSETS))
  for (dist in c("mahalanobis", "glm", "gam")) {
    d <- ORDERS[[on]](POOLS[[pn]])
    lab <- sprintf("%s_%s_%s", pn, on, dist)
    run(d, "nearest", dist, NULL, COVSETS[[cs]], lab)
    for (mo in c("largest", "closest", "data", "random", "farthest"))
      run(d, "nearest", dist, mo, COVSETS[[cs]], lab)
    run(d, "optimal", dist, NULL, COVSETS[[cs]], lab)
  }
R <- do.call(rbind, res); ok <- R[R$ok, ]
one <- ok[ok$n_ctrl == 30, ]
cat(sprintf("\nspecifications fitted %d (errors %d) | 1:1 %d\n", nrow(R), sum(!R$ok), nrow(one)))
cat(sprintf("max control SET overlap (1:1) : %d / 30\n", max(one$set_ov)))
cat(sprintf("max PAIR agreement      (1:1) : %d / 30\n", max(one$agree)))
cat(sprintf("specs with agreement >= 8     : %d\n", sum(one$agree >= 8)))
cat("\nTop 8 by pair agreement:\n")
print(head(one[order(-one$agree, -one$set_ov), c("label", "method", "distance", "m.order",
                                                 "covset", "agree", "set_ov")], 8), row.names = FALSE)
write.csv(R, OUTF, row.names = FALSE)
cat(sprintf("\nwrote %s\n", OUTF))

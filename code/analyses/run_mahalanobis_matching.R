#!/usr/bin/env Rscript
# =============================================================================
# run_mahalanobis_matching.R
# Mahalanobis covariate matching for TWAS candidate gene enrichment validation
# =============================================================================
# This script reproduces the matching of 30 HOTAIR candidate genes against
# a background gene pool using MatchIt.
#
# STATUS (2026-10-05): this is the PREDECESSOR generator, kept for provenance. It
# RUNS again — the path bootstrap below was broken from a clone and is fixed — but
# it does NOT return the archived SI Table S4: it builds its pool as
# `Group != "Candidate"`, which admits the 30 T2DM controls where the archived
# table uses the `44 Non-Candidate` group alone. It therefore writes to a scratch
# directory, never over `data/derived/`. For the authoritative re-emission of the
# table the Methods describe, run the supported generator:
#         Rscript code/analyses/emit_S4_table.R <repo-root> <out-dir>
# See metadata/ARCHIVE_MAP.md GAP-11 and code/README.md.
#
# Input:  data/derived/covariate_matrix.csv  (pool of genes with covariates)
# Output: <OUT_DIR>/mahalanobis_matched_pairs.csv  (matched pairs)
#         <OUT_DIR>/Fig5_Love_Plot.pdf             (covariate balance diagnostic)
# =============================================================================

# ---- 0. Setup --------------------------------------------------------------
# Path bootstrap (rewritten 2026-10-05). The previous one read
#     SCRIPT_DIR <- dirname(normalizePath(sys.frame(1)$ofile))
# `ofile` is set only when this file is `source()`d; under the documented
# non-interactive invocation `Rscript run_mahalanobis_matching.R` there is no such
# frame, and `sys.frame(1)` aborted with
#     Error in sys.frame(1) : not that many frames on the stack
#     Calls: dirname -> normalizePath -> path.expand -> sys.frame
# so the script could not be run the way README.md says to run it. Resolve the
# script directory from `--file=` under Rscript, fall back to `ofile` under
# `source()`, and locate the repository root by its sentinel — no absolute paths
# (code/README.md rule 3).
script_dir <- function() {
  a <- commandArgs(trailingOnly = FALSE)
  f <- grep("^--file=", a, value = TRUE)
  if (length(f)) return(dirname(normalizePath(sub("^--file=", "", f[1]))))
  of <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
  if (!is.null(of)) return(dirname(normalizePath(of)))
  getwd()
}
find_repo <- function(start) {
  d <- start
  for (i in 1:8) {
    if (file.exists(file.path(d, ".zenodo.json"))) return(d)
    p <- dirname(d); if (identical(p, d)) break; d <- p
  }
  normalizePath(file.path(start, "..", ".."))
}
SCRIPT_DIR  <- script_dir()
PROJECT_DIR <- Sys.getenv("TWAS_REPO", unset = "")
if (!nzchar(PROJECT_DIR)) PROJECT_DIR <- find_repo(SCRIPT_DIR)
DATA_DIR <- Sys.getenv("TWAS_DATA_Z",
                       unset = file.path(PROJECT_DIR, "data", "derived"))
OUT_DIR  <- Sys.getenv("MAHALANOBIS_OUT",
                       unset = file.path(PROJECT_DIR, "..", "_mahalanobis_out"))
FIG_DIR  <- OUT_DIR

dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)
cat(sprintf("[Mahalanobis] repo root  : %s\n", PROJECT_DIR))
cat(sprintf("[Mahalanobis] data dir   : %s\n", DATA_DIR))
cat(sprintf("[Mahalanobis] output dir : %s\n", OUT_DIR))
cat("[Mahalanobis] NOTE: predecessor generator; see header. Authoritative table:\n")
cat("               Rscript code/analyses/emit_S4_table.R <repo-root> <out-dir>\n")

# ---- 1. Load data ----
cat("[Mahalanobis] Loading covariate matrix...\n")
covar <- read.csv(file.path(DATA_DIR, "covariate_matrix.csv"),
                  stringsAsFactors = FALSE)

# =============================================================================
# NOTE (2026-09-11): provenance of missing eQTL SNP counts
# -----------------------------------------------------------------------------
# The archived outputs (mahalanobis_matched_pairs.csv, Additional file 1
# Table S4) were generated with group-median imputation of eQTL_SNPs_Mean for
# genes with no significant cis-eQTL model in the corresponding weight-source
# run: 3 of 30 candidates (HSPA8, RPS18, RPS25; median 1.5), 17 of 44 pool
# genes (10 of which entered the matched control set; median 1.5), and 11 of
# 30 T2DM control genes (median 1.0). The na.omit-style filtering in Section 2
# below therefore does NOT reproduce those outputs as-is; it is retained to
# document the complete-case sensitivity view. To reproduce the published
# matched pairs, impute eQTL_SNPs_Mean with the median of observed values
# within each Group (Candidate / Non-Candidate / T2DM Control) BEFORE the
# filtering steps. See manuscript Methods 1.9 for the full disclosure.
# =============================================================================

# ---- 2. Prepare matching data ----
# 2026-10-05: the treated arm was empty because the group label was wrong. The
# covariate matrix's `Group` values are "30 HOTAIR Candidate" / "44 Non-Candidate" /
# "30 T2DM Control"; the literal "Candidate" that used to be here matched no row, so
# this script aborted even once its path bootstrap was fixed. The label is now used
# verbatim. (This generator's pool is every non-candidate gene — 44 Non-Candidate +
# 30 T2DM Control = 74 — which is its own convention; the archived SI Table S4 uses
# the 44 Non-Candidate group alone. See the header and GAP-11 in ARCHIVE_MAP.md.)
CANDIDATE_LABEL <- "30 HOTAIR Candidate"

# Select candidate genes (treated)
candidate <- covar[covar$Group == CANDIDATE_LABEL, ]
candidate <- candidate[!is.na(candidate$eQTL_SNPs_Mean), ]

# Create matching pool: every gene that is not a candidate
pool <- covar[covar$Group != CANDIDATE_LABEL, ]
pool <- pool[!is.na(pool$eQTL_SNPs_Mean), ]

# Prepare matching dataframe
# Add treated flag: 1 = candidate, 0 = background
matching_data <- rbind(
    data.frame(
        Gene = candidate$Gene,
        Group = "Treated",
        log10_Length = log10(candidate$Length_bp),
        GC_pct = candidate$GC_pct,
        eQTL_SNPs_Mean = candidate$eQTL_SNPs_Mean,
        treated = 1,
        stringsAsFactors = FALSE
    ),
    data.frame(
        Gene = pool$Gene,
        Group = "Control",
        log10_Length = log10(pool$Length_bp),
        GC_pct = pool$GC_pct,
        eQTL_SNPs_Mean = pool$eQTL_SNPs_Mean,
        treated = 0,
        stringsAsFactors = FALSE
    )
)

cat(sprintf("  Treated (candidates): %d\n", sum(matching_data$treated == 1)))
cat(sprintf("  Control pool:         %d\n", sum(matching_data$treated == 0)))

# Remove rows with missing values
matching_data <- na.omit(matching_data)
cat(sprintf("  After NA removal:     %d treated, %d controls\n",
    sum(matching_data$treated == 1),
    sum(matching_data$treated == 0)))

# ---- 3. Run Mahalanobis matching ----
cat("[Mahalanobis] Running MatchIt (Mahalanobis, nearest neighbor, ratio=1)...\n")

library(MatchIt)
library(cobalt)

m.out <- matchit(treated ~ log10_Length + GC_pct + eQTL_SNPs_Mean,
                 data = matching_data,
                 method = "nearest",
                 distance = "mahalanobis",
                 ratio = 1,
                 replace = FALSE)

m.data <- match.data(m.out)

cat(sprintf("  Matched pairs: %d / %d (%.0f%%)\n",
    nrow(m.data[m.data$treated == 1, ]),
    sum(matching_data$treated == 1),
    nrow(m.data[m.data$treated == 1, ]) / sum(matching_data$treated == 1) * 100))

# ---- 4. Extract matched pairs ----
pairs <- m.data[, c("Gene", "Group", "log10_Length", "GC_pct",
                     "eQTL_SNPs_Mean", "subclass", "treated")]
colnames(pairs)[colnames(pairs) == "log10_Length"] <- "log10_Length"
colnames(pairs)[colnames(pairs) == "eQTL_SNPs_Mean"] <- "n_eQTL_SNPs"
# Add Length_bp back
pairs$Length_bp <- round(10^pairs$log10_Length)

# Write output. Deliberately NOT into the data layer: this predecessor generator's
# matched set differs from the archived SI Table S4 (see the header), so writing over
# data/derived/mahalanobis_matched_pairs.csv would clobber the shipped table. Output
# goes to OUT_DIR. NOTE also that this script applies no group-median imputation, so
# genes with a missing cis-eQTL SNP count are dropped (the "complete-case" view); the
# archived table imputes them (see Section 2's note above).
output_file <- file.path(OUT_DIR, "mahalanobis_matched_pairs.csv")
write.csv(pairs, output_file, row.names = FALSE)
cat(sprintf("  Output written: %s\n", output_file))

# ---- 5. Balance diagnostics (Love Plot) ----
cat("[Mahalanobis] Generating Love Plot (covariate balance diagnostic)...\n")

pdf(file.path(FIG_DIR, "Fig5_Love_Plot.pdf"), width = 8, height = 5)
love.plot(m.out,
          binary = "std",
          stats = c("mean.diffs"),
          threshold = 0.1,
          abs = TRUE,
          var.order = "unadjusted",
          line = TRUE,
          colors = c("#E74C3C", "#3498DB"),
          shapes = c(18, 16),
          sample.names = c("Before Matching", "After Matching"),
          title = "Covariate Balance: Mahalanobis Matching",
          labels = c(
              log10_Length = "log10(Gene Length)",
              GC_pct = "GC Content (%)",
              eQTL_SNPs_Mean = "eQTL SNPs (mean)"
          ))
dev.off()
cat(sprintf("  Love Plot saved: %s\n", file.path(FIG_DIR, "Fig5_Love_Plot.pdf")))

# ---- 6. Print SMD summary ------------------------------------------------
# 2026-10-05: this used to index a fixed pair of column names,
# summary(m.out)$sum.all[, c("Diff.Adj", "Diff.Unadj")]. Those names are not stable
# across MatchIt generations — under the installed 4.7.x the summary carries
# "Std. Mean Diff." / "Mean Diff." instead — so the access raised
# "subscript out of bounds" and the script exited 1 on its last line. Print whichever
# set the installed version provides.
cat("\n[Mahalanobis] Standardized Mean Differences:\n")
summary_matched <- summary(m.out, standardize = TRUE)
sa <- summary_matched$sum.all
cols <- intersect(c("Diff.Adj", "Diff.Unadj", "Std. Mean Diff.", "Mean Diff."),
                  colnames(sa))
if (length(cols)) print(sa[, cols, drop = FALSE]) else print(sa)

cat("\n[Mahalanobis] Matching complete.\n")

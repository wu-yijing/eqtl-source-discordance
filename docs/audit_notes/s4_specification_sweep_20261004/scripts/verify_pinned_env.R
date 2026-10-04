# =============================================================================
# verify_pinned_env.R -- prove which MatchIt is loaded, and where it came from
# =============================================================================
# The first MatchIt A/B (docs/audit_notes/s4_matchit_version_test_20261004/) was
# almost defeated by a leftover 00LOCK-MatchIt in the isolated library: R silently
# fell back to the user library although the run had been *asked* for 4.5.5, and
# nothing in the output said so. Every script in this repository's S4 work
# therefore prints the resolved version AND the directory it came from. Run this
# first; it exits non-zero when the stack does not match env/renv.lock.
#
# Usage:  PRELIB=<isolated-lib> Rscript verify_pinned_env.R
# =============================================================================
PRELIB <- Sys.getenv("PRELIB")
if (PRELIB != "") .libPaths(c(PRELIB, .libPaths()))
suppressMessages({library(MatchIt); library(cobalt)})
want <- list(MatchIt = "4.5.5", cobalt = "4.5.2", optmatch = "0.10.6")
got <- sapply(names(want), function(p) as.character(utils::packageVersion(p)))
cat("R        :", R.version.string, "\n")
for (p in names(want)) {
  flag <- if (identical(unname(got[[p]]), want[[p]])) "==" else "!="
  cat(sprintf("%-9s: %-8s (renv.lock pins %-7s) %s  %s\n",
              p, got[[p]], want[[p]], flag, find.package(p, quiet = TRUE)))
}
f <- formals(MatchIt::matchit)
cat("\nmatchit() defaults in the loaded MatchIt:\n")
for (n in c("method", "distance", "ratio", "replace", "m.order")) {
  v <- if (n %in% names(f)) deparse(f[[n]]) else "<absent>"
  cat(sprintf("  %-9s = %s\n", n, v))
}
ok <- all(mapply(identical, unname(as.list(got)), want))
cat(if (ok) "\nPINNED STACK OK\n" else "\nSTACK DOES NOT MATCH renv.lock\n")
quit(status = if (ok) 0 else 1)

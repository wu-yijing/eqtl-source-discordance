#!/usr/bin/env bash
# =============================================================================
# env/setup_r_env.sh — build the pinned R environment, patch included
# =============================================================================
# `Rscript -e 'renv::restore()'` does NOT finish on R >= 4.5, and that is not a
# misconfiguration: R 4.5 removed the un-prefixed Calloc / Free macros from its headers,
# so optmatch 0.10.6 — the version renv.lock pins — fails to compile with
#     map.cc:47:18: error: 'Calloc' was not declared in this scope
# env/README.md has said so in prose since 2026-10-04; this script is the prose made
# executable, so the remedy is a command rather than a paragraph to copy by hand.
#
# Two steps, in order:
#   1. renv::restore()            — fetches and installs MatchIt 4.5.5, cobalt, Rcpp,
#                                   RcppArmadillo, then dies on optmatch
#   2. patch + R CMD INSTALL      — builds optmatch 0.10.6 from the same official source
#                                   with the four Calloc/Free call sites renamed
#
# The patch changes names only. No algorithm, argument, tolerance or data structure is
# touched (env/README.md, "optmatch and R >= 4.5").
#
#   bash env/setup_r_env.sh                      # restore into a temp library, then patch
#   bash env/setup_r_env.sh --lib /path/to/rlib  # choose the library
#   bash env/setup_r_env.sh --check              # verify an existing library, no network
#
# Requires: network, and a working C++ toolchain (Rtools on Windows).
# Exit 0 = MatchIt 4.5.5 and optmatch 0.10.6 are both loadable from the target library.
# =============================================================================

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/.." && pwd)"
PATCH="${HERE}/patches/optmatch-0.10.6-R4.5-calloc.patch"
LOCK="${HERE}/renv.lock"

MATCHIT_WANT="4.5.5"
OPTMATCH_WANT="0.10.6"

LIB=""
CHECK=0
while [ $# -gt 0 ]; do
  case "$1" in
    --lib)   LIB="${2:-}"; shift 2 ;;
    --check) CHECK=1; shift ;;
    -h|--help) sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

pass=0; fail=0
ok()   { printf '  [ ok ] %s\n' "$*"; pass=$((pass+1)); }
bad()  { printf '  [FAIL] %s\n' "$*"; fail=$((fail+1)); }
step() { printf '\n== %s ==\n' "$*"; }

RSCRIPT="${RSCRIPT:-$(command -v Rscript || command -v Rscript.exe)}"
[ -n "${RSCRIPT}" ] || { echo "  [FAIL] no Rscript on PATH (set RSCRIPT=...)"; exit 1; }

step "0. Preflight"
ok "Rscript: ${RSCRIPT}"
[ -f "${LOCK}" ]  || { bad "renv.lock missing at ${LOCK}"; exit 1; }
ok "renv.lock present (MatchIt ${MATCHIT_WANT}, optmatch ${OPTMATCH_WANT})"
[ -f "${PATCH}" ] || { bad "optmatch patch missing at ${PATCH}"; exit 1; }
ok "optmatch patch present"

# Which library?  Never the system one by default: this script installs a pinned stack
# and the system library must survive it unchanged.
if [ -z "${LIB}" ]; then
  LIB="${R_LIB_TARGET:-$(mktemp -d 2>/dev/null || echo "${REPO}/../_rlib_target")}/rlib"
fi
mkdir -p "${LIB}" 2>/dev/null
step "1. Target library"
ok "library: ${LIB}"

ver() { # package version as seen from LIB
  R_LIBS="${LIB}" "${RSCRIPT}" -e \
    "cat(as.character(tryCatch(packageVersion('$1'), error=function(e) NA)))" 2>/dev/null \
    | tr -d '\r' | tail -1
}

if [ "${CHECK}" -eq 1 ]; then
  step "2. Verification only (--check, no network)"
  m="$(ver MatchIt)"; o="$(ver optmatch)"
  [ "${m}" = "${MATCHIT_WANT}" ] && ok "MatchIt ${m}" || bad "MatchIt is '${m}', expected ${MATCHIT_WANT}"
  [ "${o}" = "${OPTMATCH_WANT}" ] && ok "optmatch ${o}" || bad "optmatch is '${o}', expected ${OPTMATCH_WANT}"
else
  step "2. renv::restore() — expected to stop at optmatch"
  # `renv::restore()` is allowed to fail here: on R >= 4.5 it always does, at optmatch,
  # after everything else has installed. Failing for any OTHER reason must not be
  # swallowed, so the log is kept and grepped for the signature.
  LOG="$(mktemp 2>/dev/null || echo "${LIB}/_restore.log")"
  ( cd "${REPO}" && RENV_PATHS_LIBRARY="${LIB}" "${RSCRIPT}" -e \
      "renv::activate(); renv::restore(prompt = FALSE)" ) > "${LOG}" 2>&1
  rc=$?
  if [ "${rc}" -eq 0 ]; then
    ok "renv::restore() finished (optmatch may already have been installable — R < 4.5?)"
  elif grep -qiE "Calloc|Free.*was not declared|optmatch" "${LOG}"; then
    ok "renv::restore() stopped at optmatch with the expected R >= 4.5 Calloc/Free error"
  else
    bad "renv::restore() failed for an unexpected reason; log: ${LOG}"
    tail -15 "${LOG}" | sed 's/^/         /'
  fi

  step "3. Build optmatch ${OPTMATCH_WANT} with the patch"
  BUILD="$(mktemp -d 2>/dev/null || echo "${LIB}/_build")"
  mkdir -p "${BUILD}"
  TARBALL="${BUILD}/optmatch_${OPTMATCH_WANT}.tar.gz"
  # Current CRAN first, then the Archive: 0.10.6 is not the newest release, so on most
  # days only the Archive path resolves.
  URLS="https://cloud.r-project.org/src/contrib/optmatch_${OPTMATCH_WANT}.tar.gz
https://cloud.r-project.org/src/contrib/Archive/optmatch/optmatch_${OPTMATCH_WANT}.tar.gz"
  got=0
  for u in ${URLS}; do
    if command -v curl >/dev/null 2>&1; then
      curl -fsSL -o "${TARBALL}" "${u}" && { got=1; break; }
    elif command -v wget >/dev/null 2>&1; then
      wget -q -O "${TARBALL}" "${u}" && { got=1; break; }
    else
      bad "neither curl nor wget is available — cannot fetch the optmatch source"
      break
    fi
  done
  if [ "${got}" -eq 1 ]; then
    ok "source fetched: optmatch_${OPTMATCH_WANT}.tar.gz"
    ( cd "${BUILD}" && tar -xzf "${TARBALL}" ) || bad "could not extract the tarball"
    ( cd "${BUILD}" && patch -p1 --forward -i "${PATCH}" ) \
      && ok "patch applied (Calloc/Free -> R_Calloc/R_Free, names only)" \
      || bad "patch did not apply cleanly"
    if ( cd "${BUILD}" && R_LIBS="${LIB}" "${RSCRIPT}" -e \
         "install.packages('optmatch', repos = NULL, type = 'source', lib = '${LIB}')" ) \
         > "${BUILD}/install.log" 2>&1; then
      ok "optmatch ${OPTMATCH_WANT} installed from the patched source"
    else
      bad "R CMD INSTALL of the patched optmatch failed:"
      tail -12 "${BUILD}/install.log" | sed 's/^/         /'
    fi
  else
    bad "could not download optmatch ${OPTMATCH_WANT} from CRAN or the Archive"
  fi
fi

step "4. Result"
m="$(ver MatchIt)"; o="$(ver optmatch)"
[ "${m}" = "${MATCHIT_WANT}" ] && ok "MatchIt ${m}" || bad "MatchIt is '${m}', expected ${MATCHIT_WANT}"
[ "${o}" = "${OPTMATCH_WANT}" ] && ok "optmatch ${o}" || bad "optmatch is '${o}', expected ${OPTMATCH_WANT}"

echo
if [ "${fail}" -gt 0 ]; then
  echo " RESULT: ${fail} failure(s). The pinned R stack is not complete."
  exit 1
fi
echo " RESULT: MatchIt ${MATCHIT_WANT} + optmatch ${OPTMATCH_WANT} loadable from ${LIB}"
echo "         (SI Table S4's control set reproduces 30/30 under this stack — see"
echo "          docs/audit_notes/env_and_boundaries_20261005/.)"
exit 0

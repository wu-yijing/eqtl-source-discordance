#!/usr/bin/env bash
# =============================================================================
# code/figures/ge_main/reproduce.sh — rebuild the four manuscript main figures
# =============================================================================
# `code/run_all.sh` produces the BMC-generation build outputs under `figures/`.
# THIS script produces the four figures that accompany the Genetic Epidemiology
# submission, which are a different set, from a different style module.
#
# All four regenerate from `data/derived/` alone. The scripts were written against
# the predecessor repository's data directory, where the same four tables carried
# different filenames; this script builds that filename view so nothing in the
# figure scripts has to change.
#
#   bash code/figures/ge_main/reproduce.sh
#   bash code/figures/ge_main/reproduce.sh --keep     # keep the rebuilt PNGs
#
# Exit code 0 = every PNG matched the recorded hash.
# =============================================================================

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/../../.." && pwd)"
DATA_Z="${REPO}/data/derived"
WORK="${GE_MAIN_OUT:-${REPO}/../_ge_main_run}"
KEEP=0
[ "${1:-}" = "--keep" ] && KEEP=1

PY="${PYTHON:-$(command -v python3 || command -v python)}"
MISMATCH=0

step() { printf '\n== %s ==\n' "$1"; }
ok()   { printf '  [ ok ] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; MISMATCH=$((MISMATCH + 1)); }

echo "====================================================================="
echo " Genetic Epidemiology main figures — rebuild (Figure 1-4)"
echo " repo      : ${REPO}"
echo " data      : ${DATA_Z}"
echo " output    : ${WORK}"
echo " python    : ${PY}"
echo "====================================================================="

mkdir -p "${WORK}/data" "${WORK}/out"

# ---------------------------------------------------------------------------
step "0. Preflight"
# ---------------------------------------------------------------------------
for m in numpy scipy matplotlib PIL; do
  "${PY}" -c "import $m" >/dev/null 2>&1 \
    && ok "python module: $m" \
    || { bad "python module missing: $m"; exit 1; }
done

# ---------------------------------------------------------------------------
step "1. Filename view of data/derived/ that the figure scripts read"
# ---------------------------------------------------------------------------
# The scripts name the predecessor repository's files. Every one maps onto a table
# in data/derived/ that INPUTS.md section A.1 records as byte-identical to it.
declare -A MAP=(
  [primary_arm_96pairs_official.csv]="primary_arm_96pairs.csv"
  [gtex_official_Z.csv]="gtex_Z.csv"
  [eqtlgen_official_Z.csv]="eqtlgen_Z.csv"
  [scz_z_4arm_official.csv]="scz_z_4arm.csv"
)
for dst in "${!MAP[@]}"; do
  src="${DATA_Z}/${MAP[$dst]}"
  if [ -f "$src" ]; then
    cp "$src" "${WORK}/data/${dst}"
    ok "${dst}  <-  data/derived/${MAP[$dst]}"
  else
    bad "missing ${src}"
  fi
done

# ---------------------------------------------------------------------------
step "2. Render"
# ---------------------------------------------------------------------------
for n in 1 2 3 4; do
  if ( cd "${HERE}" && TWAS_DATA_Z="${WORK}/data" FIG_OUT="${WORK}/out" \
        "${PY}" "unified_fig${n}.py" ) > "${WORK}/fig${n}.log" 2>&1; then
    ok "unified_fig${n}.py"
  else
    bad "unified_fig${n}.py failed — see ${WORK}/fig${n}.log"
    tail -5 "${WORK}/fig${n}.log" | sed 's/^/         /'
  fi
done

# ---------------------------------------------------------------------------
step "3. Compare against the recorded hashes"
# ---------------------------------------------------------------------------
# SHA-256 of the submitted PNGs. A PNG is deterministic given the data and the
# style module, so this is an equality test, not a similarity test.
declare -A WANT=(
  [1]=eb77483eaf5188871de97a9cffabfe86278b717ef26f4f83d722eb969b80bafb
  [2]=87ee0eaa83f3730938305f669747943101797cde5952ba5cdc0ef33c568e97b0
  [3]=152f45df76e8d4ab9426b2314d85c38dcde930c741165af25993359ab0a001bf
  [4]=f29f2f56da3b63107df27145aced3a5ffa6b16b73c2b068afaae6e81324912d1
)
for n in 1 2 3 4; do
  p="${WORK}/out/Figure_${n}.png"
  if [ ! -f "$p" ]; then bad "Figure_${n}.png not produced"; continue; fi
  if command -v sha256sum >/dev/null 2>&1; then
    # GNU coreutils prefixes the whole line with a backslash when the file name needs
    # escaping, and on Windows a path containing a backslash always does. That made
    # `cut -d' ' -f1` return "\eb77483e…" and every figure compare as different while
    # being identical — found by gate 14 of scripts/verify_from_clone.sh on 2026-10-06,
    # which runs this script with its output inside a temp directory whose path has a
    # backslash in it. Strip the escape marker before comparing.
    got="$(sha256sum "$p" | cut -d' ' -f1)"
    got="${got#\\}"
  else
    got="$("${PY}" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$p")"
  fi
  if [ "$got" = "${WANT[$n]}" ]; then
    ok "Figure_${n}.png  ${got:0:16}…  identical to the submitted figure"
  else
    bad "Figure_${n}.png  ${got:0:16}…  != ${WANT[$n]:0:16}…"
  fi
done

printf '\n  note: the PDFs are byte-identical apart from the embedded /CreationDate\n'
printf '        (4-6 bytes), which is why the comparison is made on the PNGs.\n'

echo
echo "====================================================================="
if [ "$MISMATCH" -gt 0 ]; then
  echo " RESULT: ${MISMATCH} failure(s). The main figures do not reproduce."
  exit 1
fi
echo " RESULT: all four main figures reproduce byte-identically."
[ "$KEEP" = "1" ] && echo " Outputs kept at: ${WORK}/out" || echo " Outputs at: ${WORK}/out"
echo "====================================================================="
exit 0

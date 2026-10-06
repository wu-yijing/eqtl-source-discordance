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
  # unified_fig4.py's housekeeping panel used to come from the Supporting Information's
  # Table S6. That document is the journal's and is not redistributed here — but it was
  # never the source of record: the layer ships as data/derived/hk_official_Z.csv and the
  # two agree exactly (30 genes, 72 pairs, rho +0.64). Added 2026-10-07.
  [hk_official_Z.csv]="hk_official_Z.csv"
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
# Font preflight. figstyle_ge.py typesets these figures in Arial
# (FONT_STACK = Arial -> Helvetica -> Liberation Sans -> DejaVu Sans, and mathtext.rm is
# forced to Arial so a single family is used throughout, as the journal requires). Arial is
# proprietary and is NOT in the container image, so there the stack silently falls through
# to DejaVu Sans and every glyph changes: measured in the shipped image, 4.3 %-9.9 % of
# pixels differed from the submitted figures and the PDFs came out at half the size. That is
# a font substitution, not a broken archive — but the hash comparison below cannot tell the
# two apart, so say which one it is before it runs. A metric-compatible substitute
# (Liberation Sans) lands between the two and is reported as such: measured, it still leaves
# 1.6 %-8.0 % of pixels different, so it is a better-looking fallback rather than a fix.
FONT_USED=$("${PY}" - <<'PY' 2>/dev/null
from matplotlib import font_manager as fm
for name in ['Arial', 'Helvetica', 'Liberation Sans']:
    try:
        fm.findfont(name, fallback_to_default=False)
        print(name)
        break
    except Exception:
        continue
else:
    print('DejaVu Sans')
PY
)
case "$FONT_USED" in
  Arial)
    ok "font: Arial   (the family the submitted figures are set in)"
    ;;
  Helvetica|Liberation\ Sans)
    printf '\n  !! Font: %s — a metric-compatible SUBSTITUTE for Arial, not Arial.\n' "$FONT_USED"
    printf '     Line breaks and spacing will be right; the glyphs will not. Measured with\n'
    printf '     Liberation Sans in this image: 1.6 %%-8.0 %% of pixels still differ from the\n'
    printf '     submitted figures, so they will NOT match the recorded hashes. Supply Arial\n'
    printf '     to verify them (see the mount recipe below); adding fonts-liberation to the\n'
    printf '     image was measured on 2026-10-07 and does not close the gap, which is why it\n'
    printf '     is not in env/Dockerfile.\n\n'
    ;;
  *)
    printf '\n  !! No Arial, Helvetica or Liberation Sans on this machine — matplotlib will use\n'
    printf '     DejaVu Sans, so the figures below CANNOT match the submitted ones whatever\n'
    printf '     the data says. This is a font substitution, not a data or code difference.\n'
    printf '     Measured in this image: 4.3 %%-9.9 %% of pixels differ and the PDFs halve in\n'
    printf '     size. To verify them, supply Arial (proprietary; not redistributable here).\n'
    printf '     Inside the container that is one mount, e.g.\n'
    printf '       docker run ... -v "C:/Windows/Fonts:/mnt/winfonts:ro" ... -c \\\n'
    printf '         "mkdir -p /usr/share/fonts/truetype/arial && \\\n'
    printf '          cp /mnt/winfonts/arial*.ttf /usr/share/fonts/truetype/arial/ && \\\n'
    printf '          rm -rf /root/.cache/matplotlib && bash code/figures/ge_main/reproduce.sh"\n\n'
    ;;
esac

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
  if [ ! -f "$p" ]; then
    bad "Figure_${n}.png not produced"
    continue
  fi
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

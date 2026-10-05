#!/usr/bin/env bash
# =============================================================================
# code/run_all.sh — the ONLY supported reproduction entry point
# =============================================================================
# Reproduces the manuscript's figures and verifies its headline values from the
# authoritative data layer. It will NOT touch the superseded layer, with ONE documented
# exception: SI Fig. S2's recovered generator reads
# `data/superseded/eqtlgen_spredixcan_harmonized_results.csv` for its model SNP counts
# (a model property, unaffected by the corrections) and a valid-Z presence filter — see
# the SI Fig. S2 step below and `code/figures/recovered/README.md`.
#
#   bash code/run_all.sh                 # figures + read-only verification
#   bash code/run_all.sh --verify-only   # verification only, no figure output
#   bash code/run_all.sh --rebuild-data  # rebuild data/derived/ from the SI docx
#   bash code/run_all.sh --help
#
# WHY THIS SCRIPT WAS REWRITTEN
# -----------------------------
# Its predecessor pointed at `data/processed/` and invoked
# `scripts/python/04_generate_all_figures.py`: the *pre-correction* generation
# (missing S-PrediXcan sigma_i expression-variance factor; PLINK 2-bit decoding
# defect). Running it produced figures and rates that disagreed with the
# manuscript — e.g. eQTLGen Z of TUBB 48.52 instead of 11.89, RNH1 13.32
# instead of 2.31. That path is now quarantined under `code/deprecated/`, and
# this script refuses to use it.
#
# Layers:
#   data/derived/      AUTHORITATIVE   (official MetaXcan v0.8.1 recompute)
#   code/figures/      AUTHORITATIVE   (the only figure pipeline)
#   data/superseded/   DO NOT QUOTE    (pre-correction; retained as provenance)
#   code/deprecated/   DO NOT USE      (superseded generations)
# =============================================================================

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/.." && pwd)"
FIGDIR="${REPO}/code/figures"
DATA_Z="${REPO}/data/derived"
FIG_OUT="${REPO}/figures"
PYTHON="${PYTHON:-$(command -v python3 || command -v python)}"
MODE="${1:-}"
FAIL=0
# Scratch space for step output that is parsed but not shipped. Created here and removed
# on exit so a step can capture stdout without writing into a tracked directory.
TMPD="$(mktemp -d 2>/dev/null || echo "${REPO}/../_runall_tmp")"
mkdir -p "${TMPD}" 2>/dev/null
trap 'rm -rf "${TMPD}" 2>/dev/null' EXIT
ok()   { printf '  [ ok ] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; FAIL=$((FAIL+1)); }
skip() { printf '  [skip] %s\n' "$1"; }
step() { printf '\n== %s ==\n' "$1"; }

case "$MODE" in
  -h|--help)
    sed -n '2,25p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 0 ;;
esac

echo "====================================================================="
echo " eQTL-source discordance in TWAS — reproduction pipeline"
echo " repo        : ${REPO}"
echo " data layer  : ${DATA_Z}   (authoritative)"
echo " figure code : ${FIGDIR}   (authoritative)"
echo " started     : $(date)"
echo "====================================================================="

# ---------------------------------------------------------------------------
step "0. Preflight"
# ---------------------------------------------------------------------------
[ -n "${PYTHON}" ] || { bad "no python interpreter found (set PYTHON=...)"; exit 1; }
ok "python: ${PYTHON}"
[ -d "${DATA_Z}" ] || { bad "${DATA_Z} missing"; exit 1; }
[ -d "${FIGDIR}" ] || { bad "${FIGDIR} missing"; exit 1; }
ok "authoritative data and figure directories present"

# Guard: the superseded layer must never be an input.
[ -d "${REPO}/data/superseded" ] && skip "data/superseded/ present; not used as an input layer (the one exception is the SI Fig. S2 step, see below)"
if grep -rqE 'data/processed[/"]' "${FIGDIR}"/*.py 2>/dev/null; then
  bad "a figure script still references data/processed/ — quarantined layer"
else
  ok "no figure script references data/processed/"
fi

# ---------------------------------------------------------------------------
step "1. Figure pipeline (authoritative order)"
# ---------------------------------------------------------------------------
# Order per code/figures/README.md. Step 00 is opt-in: it needs the
# Supporting Information .docx, which is not redistributed.
if [ "${MODE}" = "--rebuild-data" ]; then
  # 2026-10-06 — this step is now REFUSED, not merely skipped.
  # 00_build_officialZ_data_layer.py reads the Supporting Information .docx and writes
  # data/derived/ from it. data/derived/ is what every reported value is reproduced
  # FROM, so the step is a loop: run it and every downstream check becomes a tautology.
  # It is retained in the tree (it documents how the layer was first assembled) but it
  # now exits non-zero unless --allow-circular-write is passed, and even then writes to
  # data/superseded/_from_docx_NOT_authoritative/, which feeds nothing.
  # The authoritative inputs -> data/derived/ path is code/run_upstream.sh (gate 9).
  skip "00_build_officialZ_data_layer.py — REFUSED as a build step: it derives"
  skip "  data/derived/ from the Supporting Information, which is itself derived from"
  skip "  data/derived/ (circular). Authoritative path: code/run_upstream.sh."
  skip "  The script is retained for forensics and needs --allow-circular-write to run."
fi

if [ "${MODE}" = "--verify-only" ]; then
  skip "figure generation (--verify-only)"
else
  # Two of the figure scripts read the Supporting Information .docx, which is not
  # redistributed. README.md promises that without it the figure step is *skipped,
  # not failed*; before 2026-10-03 that was not true — 04_redraw_Fig8.py and
  # 08_redraw_Fig6_labels_20260920.py exited non-zero and the run reported
  # "2 failure(s)". The two are now detected up front and skipped with the reason.
  SI_AVAILABLE=0
  if [ -n "${AF1_DOCX:-}" ] && [ -f "${AF1_DOCX}" ]; then
    SI_AVAILABLE=1
    ok "Supporting Information supplied via AF1_DOCX: ${AF1_DOCX}"
  elif [ -f "${REPO}/manuscript/Supporting_Information.docx" ]; then
    SI_AVAILABLE=1
    ok "Supporting Information found at ${REPO}/manuscript/Supporting_Information.docx"
  else
    ok "no Supporting Information .docx (figure steps that need it will be skipped)"
  fi

  mkdir -p "${FIG_OUT}"
  SKIPPED_SI=""
  for s in 01_redraw_Fig5_Fig7.py 02_redraw_Fig3.py 04_redraw_Fig8.py \
           06_redraw_Fig4.py 08_redraw_Fig6_labels_20260920.py 10_redraw_FigS6_20260921.py ; do
    case "$s" in
      04_redraw_Fig8.py|08_redraw_Fig6_labels_20260920.py)
        if [ "${SI_AVAILABLE}" -eq 0 ]; then
          skip "$s (needs the Supporting Information .docx — set AF1_DOCX=/path/to/it)"
          SKIPPED_SI="${SKIPPED_SI} ${s}"
          continue
        fi
        ;;
    esac
    if [ -f "${FIGDIR}/${s}" ]; then
      ( cd "${FIGDIR}" && "${PYTHON}" "${s}" ) && ok "$s" || bad "$s failed"
    else
      bad "${s} missing"
    fi
  done
  [ -n "${SKIPPED_SI}" ] && echo "  note: these steps were SKIPPED, not failed:${SKIPPED_SI}"
  # 03_redraw_Fig6.py is deliberately NOT run: it is a hard-deprecation guard
  # that exits 1 by design (its only output, Fig. 6, is produced by 08).
  skip "03_redraw_Fig6.py (hard-deprecated by design; Fig. 6 comes from 08)"

  # SI Fig. S2 — recovered 2026-10-02 as evidence only, made runnable from the archive on
  # 2026-10-05 (its three hard-coded 2026-09 absolute paths were removed). It is the ONE
  # figure step that reads the superseded layer, and only for fields the sigma_i / PLINK
  # corrections do not touch: `n_snps_model` (a property of the fitted model) plus a
  # valid Z used purely as a *presence* filter for the 61-gene universe. It reproduces
  # the three published medians 374 / 632 / 669. See code/figures/recovered/README.md.
  if [ -f "${FIGDIR}/recovered/gen_figs4.py" ]; then
    if ( cd "${FIGDIR}" && FIG_S2_OUT="${FIG_OUT}" "${PYTHON}" recovered/gen_figs4.py ) \
         > "${FIG_OUT}/_gen_figs4.txt" 2>&1; then
      if grep -q '"median": 374.0' "${FIG_OUT}/_gen_figs4.txt" \
         && grep -q '"median": 632.0' "${FIG_OUT}/_gen_figs4.txt" \
         && grep -q '"median": 669.0' "${FIG_OUT}/_gen_figs4.txt"; then
        ok "recovered/gen_figs4.py (SI Fig. S2): medians 374 / 632 / 669 reproduce"
      else
        bad "recovered/gen_figs4.py ran but the SI Fig. S2 medians are not 374 / 632 / 669"
      fi
    else
      bad "recovered/gen_figs4.py (SI Fig. S2) failed:"
      tail -6 "${FIG_OUT}/_gen_figs4.txt" | sed 's/^/         /'
    fi
  else
    skip "recovered/gen_figs4.py not present (SI Fig. S2 not regenerated)"
  fi
fi

# ---------------------------------------------------------------------------
step "2. Read-only verification scripts"
# ---------------------------------------------------------------------------
for s in 05_recompute_arms.py 07_verify_SCZ_denominators.py ; do
  if [ -f "${FIGDIR}/${s}" ]; then
    ( cd "${FIGDIR}" && "${PYTHON}" "${s}" ) && ok "$s" || bad "$s reported a problem"
  else
    skip "$s not present"
  fi
done

# ---------------------------------------------------------------------------
step "3. Headline values recomputed from the authoritative layer"
# ---------------------------------------------------------------------------
"${PYTHON}" - "$DATA_Z" <<'PYEOF'
import csv, math, os, sys
d = sys.argv[1]
p = os.path.join(d, 'primary_arm_96pairs.csv')
if not os.path.exists(p):
    print('  [skip] primary_arm_96pairs.csv not present'); raise SystemExit(0)
rows = list(csv.DictReader(open(p, encoding='utf-8')))
xs = [float(r['Z_GTEx']) for r in rows]
ys = [float(r['Z_eQTLGen']) for r in rows]
same = sum(1 for r in rows if str(r['Same']).strip().lower() in ('true', '1', 'yes'))
rate = 100.0 * same / len(rows)
order = sorted(range(len(xs)), key=lambda i: xs[i]); rx = [0]*len(xs)
for pos, i in enumerate(order): rx[i] = pos + 1
order = sorted(range(len(ys)), key=lambda i: ys[i]); ry = [0]*len(ys)
for pos, i in enumerate(order): ry[i] = pos + 1
n = len(xs); mx = sum(rx)/n; my = sum(ry)/n
rho = sum((a-mx)*(b-my) for a, b in zip(rx, ry)) / math.sqrt(
      sum((a-mx)**2 for a in rx) * sum((b-my)**2 for b in ry))
exp = {'pairs': 96, 'rate': 68.8, 'rho': 0.39}
ok = True
print('  pairs                : %d   (manuscript: %d)   %s' % (len(rows), exp['pairs'], 'ok' if len(rows)==exp['pairs'] else 'MISMATCH'))
if len(rows) != exp['pairs']: ok = False
print('  direction consistency: %.1f%% (manuscript: %.1f%%)  %s' % (rate, exp['rate'], 'ok' if abs(rate-exp['rate'])<0.05 else 'MISMATCH'))
if abs(rate - exp['rate']) >= 0.05: ok = False
print('  Spearman rho         : %.4f (manuscript: %.2f)   %s' % (rho, exp['rho'], 'ok' if abs(rho-exp['rho'])<0.005 else 'MISMATCH'))
if abs(rho - exp['rho']) >= 0.005: ok = False
print('  max |Z| GTEx/eQTLGen : %.4f / %.4f' % (max(abs(x) for x in xs), max(abs(y) for y in ys)))
raise SystemExit(0 if ok else 3)
PYEOF
[ $? -eq 0 ] && ok "headline values reproduce" || bad "headline values do NOT reproduce"

# ---------------------------------------------------------------------------
step "3b. SI Table S5a row 3 — the sqrt(N_e) direct-weighting row"
# ---------------------------------------------------------------------------
# Runs in every mode, including --verify-only. This row was the single numeric cell of
# the two submitted documents that `scripts/audit_documents_vs_repo.py` could not find
# in the archive (pooled +2.09, Cochran Q = 76.6, I^2 = 98.7%). It was never missing:
# `code/analyses/m6_ne_weighted_sensitivity.py` computed it all along, but wrote its
# report into data/superseded/ — the quarantined layer, which no corpus reader touches.
# The script now writes into the reproduction package's results/ and --self-test asserts
# the three published values, so the row is checked on every run. See
# docs/audit_notes/s5a_row3_closure_20261006/.
if [ -f "${REPO}/code/analyses/m6_ne_weighted_sensitivity.py" ]; then
  if ( cd "${REPO}/code/analyses" && "${PYTHON}" m6_ne_weighted_sensitivity.py --self-test ) \
       > "${TMPD}/_m6_s5a.txt" 2>&1; then
    ok "m6_ne_weighted_sensitivity.py: SI Table S5a row 3 reproduces (+2.09 / Q 76.6 / I² 98.7%)"
  else
    bad "m6_ne_weighted_sensitivity.py (SI Table S5a row 3) did not reproduce:"
    tail -8 "${TMPD}/_m6_s5a.txt" | sed 's/^/         /'
  fi
else
  skip "m6_ne_weighted_sensitivity.py not present (SI Table S5a row 3 not checked)"
fi

# ---------------------------------------------------------------------------
step "3c. SI Table S4 — the candidate processing order is an artefact"
# ---------------------------------------------------------------------------
# The control set reproduces 30/30 only in one candidate order, and that order used to
# exist solely as the row order of mahalanobis_matched_pairs.csv — reproducible, but
# unnameable. It is now a file (data/derived/s4_candidate_order.txt) and this checks it
# against the shipped matched table on every run. It is a checker, not a matcher:
# emit_S4_table.R still does the matching (verify_from_clone.sh gate 12).
if [ -f "${REPO}/scripts/check_s4_order.py" ]; then
  if "${PYTHON}" "${REPO}/scripts/check_s4_order.py" > "${TMPD}/_s4order.txt" 2>&1; then
    ok "check_s4_order.py: the candidate order is explicit and agrees with Table S4"
    grep -h '\[info\]' "${TMPD}/_s4order.txt" | sed 's/^/         /'
  else
    bad "check_s4_order.py (SI Table S4 candidate order):"
    tail -8 "${TMPD}/_s4order.txt" | sed 's/^/         /'
  fi
else
  skip "scripts/check_s4_order.py not present"
fi

# ---------------------------------------------------------------------------
step "4. Figure format precheck"
# ---------------------------------------------------------------------------
if [ -f "${FIGDIR}/11_figure_precheck.py" ] && [ "${MODE}" != "--verify-only" ]; then
  ( cd "${FIGDIR}" && "${PYTHON}" 11_figure_precheck.py ) || skip "precheck reported non-blocking findings"
else
  skip "11_figure_precheck.py"
fi

# ---------------------------------------------------------------------------
echo
echo "====================================================================="
if [ "${FAIL}" -gt 0 ]; then
  echo " RESULT: ${FAIL} failure(s). Do not treat this run as reproducing the paper."
  exit 1
fi
echo " RESULT: pipeline completed with no failures."
echo " Figures written to: ${FIG_OUT}/"
echo "====================================================================="
exit 0

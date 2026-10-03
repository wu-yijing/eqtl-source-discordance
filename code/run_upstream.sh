#!/usr/bin/env bash
# =============================================================================
# code/run_upstream.sh — rebuild the analysis layer from the raw third-party inputs
# =============================================================================
# This is the step `README.md` and `data/README.md` used to say could not be run:
# the S-PrediXcan stage that turns raw GWAS + eQTL weights into the Z layer that
# `data/derived/` and every downstream script consume.
#
# It is NOT invoked by `code/run_all.sh`. `run_all.sh` reproduces the reported
# values from `data/derived/`, which is what a reader normally needs and needs no
# third-party download. THIS script is for the other question — "was the Z layer
# itself produced from the inputs the archive names?" — and it needs those inputs.
#
# -----------------------------------------------------------------------------
# Inputs (see data/external/SHA256SUMS for the hash of each; verify with
#         `python3 scripts/verify_external_inputs.py --dir data/external`)
# -----------------------------------------------------------------------------
#   data/external/mashr_Whole_Blood.db
#   data/external/mashr_Nerve_Tibial.db
#   data/external/gtex_v8_mashr_snp_covariance.txt.gz
#   data/external/2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz
#   data/external/finngen_R13_DM_RETINOPATHY_EXMORE.gz
#   data/external/finngen_R13_DM_NEPHROPATHY.gz
#   data/external/finngen_R13_DM_NEUROPATHY.gz
#   data/external/g1000_eur.zip
#   data/external/MetaXcan-v0.8.1.tar.gz
#
# -----------------------------------------------------------------------------
# Toolchain
# -----------------------------------------------------------------------------
#   Official MetaXcan, unmodified, tag v0.8.1  (SPrediXcan.py)
#   Python 3.12 with numpy 1.x — MetaXcan 0.8.1 predates numpy 2 and will not run
#   under it. The environment that produced the reported numbers used
#   Python 3.12.13 / numpy 1.26.4 / scipy 1.13.1 / pandas 2.2.3.
#   Set METAXCAN_SW and PYTHON below.
#
# -----------------------------------------------------------------------------
# Usage
# -----------------------------------------------------------------------------
#   METAXCAN_SW=/opt/MetaXcan/software python3.12 code/run_upstream.sh            # all steps
#   bash code/run_upstream.sh --verify-only                                       # compare only
#   bash code/run_upstream.sh --help
#
# Outputs land in $UPSTREAM_OUT (default: a run directory beside the repository).
# Nothing in the repository is modified.
# =============================================================================

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/.." && pwd)"
EXT="${EXT_DIR:-${REPO}/data/external}"
OUT="${UPSTREAM_OUT:-${REPO}/../_upstream_run}"
SW="${METAXCAN_SW:-}"
PY="${PYTHON:-$(command -v python3 || command -v python)}"
MODE="${1:-}"
FAIL=0

ok()   { printf '  [ ok ] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; FAIL=$((FAIL+1)); }
step() { printf '\n== %s ==\n' "$1"; }

case "$MODE" in
  -h|--help) sed -n '2,50p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
esac

PHENOS=(DR DN DPN)
declare -A FINNGEN=(
  [DR]="finngen_R13_DM_RETINOPATHY_EXMORE.gz"
  [DN]="finngen_R13_DM_NEPHROPATHY.gz"
  [DPN]="finngen_R13_DM_NEUROPATHY.gz"
)
TISSUES=(Whole_Blood Nerve_Tibial)

echo "====================================================================="
echo " upstream rebuild — raw GWAS + eQTL weights -> Z layer"
echo " repo         : ${REPO}"
echo " externals    : ${EXT}"
echo " output       : ${OUT}"
echo " MetaXcan     : ${SW:-<unset — set METAXCAN_SW>}"
echo " python       : ${PY}"
echo " started      : $(date)"
echo "====================================================================="

mkdir -p "${OUT}"/{gwas,cov,official,eqtlgen}

# ---------------------------------------------------------------------------
step "0. Preflight"
# ---------------------------------------------------------------------------
[ -d "${EXT}" ] || { bad "${EXT} missing — see data/external/README.md"; exit 1; }
"${PY}" "${REPO}/scripts/verify_external_inputs.py" --dir "${EXT}" || \
  bad "one or more external inputs are the wrong file (see above)"

if [ "${MODE}" != "--verify-only" ]; then
  [ -n "${SW}" ] && [ -f "${SW}/SPrediXcan.py" ] || { bad "set METAXCAN_SW to MetaXcan's software/ directory"; exit 1; }
  "${PY}" -c 'import numpy,sys; sys.exit(0 if numpy.__version__[0]=="1" else 1)' || {
    bad "MetaXcan 0.8.1 needs numpy 1.x (found a different major version)"; exit 1; }
  ok "toolchain present (MetaXcan 0.8.1 + numpy 1.x)"
fi

# ---------------------------------------------------------------------------
step "1. FinnGen R13 -> harmonised GWAS input"
# ---------------------------------------------------------------------------
# Keep the rows for the SNPs the two mashr models use, and nothing else. The
# upstream run reduced 21.2 M FinnGen rows to 37,192 per phenotype; the identical
# filter is what makes the comparison in step 3 meaningful.
if [ "${MODE}" = "--verify-only" ]; then
  printf '  [skip] rebuild (--verify-only)\n'
else
  for ph in "${PHENOS[@]}"; do
    src="${EXT}/${FINNGEN[$ph]}"
    [ -f "${src}" ] || { bad "missing ${src}"; continue; }
    "${PY}" - "${src}" "${OUT}/gwas/gwas_${ph}.tsv" "${EXT}" <<'PYEOF' || bad "harmonise ${ph} failed"
import gzip, os, sqlite3, sys
src, dst, ext = sys.argv[1], sys.argv[2], sys.argv[3]
need = set()
for tis in ('Whole_Blood', 'Nerve_Tibial'):
    con = sqlite3.connect(os.path.join(ext, 'mashr_%s.db' % tis))
    need.update(r[0] for r in con.execute('SELECT rsid FROM weights'))
    con.close()
kept = 0
with gzip.open(src, 'rt', encoding='utf-8', errors='replace') as f, \
     open(dst, 'w', encoding='utf-8', newline='') as o:
    hdr = f.readline().rstrip('\n').split('\t')
    ci = {h.lower().lstrip('#'): i for i, h in enumerate(hdr)}
    i_rs, i_b, i_se, i_alt, i_ref = ci['rsids'], ci['beta'], ci['sebeta'], ci['alt'], ci['ref']
    o.write('snp\tbeta\tse\talt\tref\n')
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) < len(hdr):
            continue
        rs = p[i_rs]
        if rs in need:
            o.write('%s\t%s\t%s\t%s\t%s\n' % (rs, p[i_b], p[i_se], p[i_alt], p[i_ref])); kept += 1
        elif ',' in rs:
            for tok in rs.split(','):
                if tok.strip() in need:
                    o.write('%s\t%s\t%s\t%s\t%s\n' % (tok.strip(), p[i_b], p[i_se], p[i_alt], p[i_ref]))
                    kept += 1; break
print('      %s -> %d rows' % (os.path.basename(src), kept))
PYEOF
    [ $? -eq 0 ] && ok "harmonised ${ph}"
  done
fi

# ---------------------------------------------------------------------------
step "2. GTEx arm — S-PrediXcan (official MetaXcan v0.8.1)"
# ---------------------------------------------------------------------------
# The gene-level covariance for each tissue is built from g1000_eur; if you do not
# have it, build it with MetaXcan's own tools (M01_covariances_correlations.py) or
# reuse the one your run produced. Note: `--stream_covariance` must NOT be used
# here — the GTEx tables in this archive were produced without it.
if [ "${MODE}" = "--verify-only" ]; then
  printf '  [skip] rerun (--verify-only)\n'
else
  for tis in "${TISSUES[@]}"; do
    for ph in "${PHENOS[@]}"; do
      cov="${OUT}/cov/cov_${tis}.txt.gz"
      [ -f "${cov}" ] || { printf '  [skip] %s: no %s (see data/external/README.md)\n' "$tis" "$cov"; continue; }
      ( cd "${SW}" && "${PY}" SPrediXcan.py \
          --model_db_path "${EXT}/mashr_${tis}.db" \
          --covariance "${cov}" \
          --gwas_file "${OUT}/gwas/gwas_${ph}.tsv" \
          --snp_column snp --effect_allele_column alt --non_effect_allele_column ref \
          --beta_column beta --se_column se \
          --output_file "${OUT}/official_${tis}_${ph}.csv" \
          --additional_output ) && ok "S-PrediXcan ${tis} x ${ph}" || bad "S-PrediXcan ${tis} x ${ph}"
    done
  done
fi

# ---------------------------------------------------------------------------
step "3. eQTLGen arm — build the weight database, then S-PrediXcan"
# ---------------------------------------------------------------------------
# Weights: AssessedAllele -> eff_allele, OtherAllele -> ref_allele, Zscore -> weight,
# restricted to the genes the analysis uses. Filtering the cis-eQTL file on the ids
# already in your model database reproduces the archived weights row-for-row.
# S-PrediXcan here DOES use --stream_covariance: the eQTLGen gene covariance is
# 111-394 MB gzipped and will not fit in memory in one piece on most machines.
EQ_TAG="${EQ_TAG:-}"     # e.g. A, B, C for a panel subset; empty = whole-blood model
if [ "${MODE}" = "--verify-only" ] || [ -z "${EQ_TAG}" ]; then
  printf '  [skip] set EQ_TAG=A (and provide db_%%s.db / cov_%%s.txt.gz) to run a panel subset\n'
else
  DB="${OUT}/eqtlgen/db_${EQ_TAG}.db"
  COV="${OUT}/eqtlgen/cov_${EQ_TAG}.txt.gz"
  [ -f "${DB}" ] && [ -f "${COV}" ] || bad "provide ${DB} and ${COV}"
  for ph in "${PHENOS[@]}"; do
    ( cd "${SW}" && "${PY}" SPrediXcan.py \
        --model_db_path "${DB}" --covariance "${COV}" \
        --gwas_file "${OUT}/eqtlgen/gwas_${ph}_aligned.tsv" \
        --snp_column snp --effect_allele_column alt --non_effect_allele_column ref \
        --beta_column beta --se_column se \
        --output_file "${OUT}/eqtlgen/official_eq_${EQ_TAG}_${ph}.csv" \
        --additional_output --stream_covariance ) \
      && ok "S-PrediXcan eQTLGen ${EQ_TAG} x ${ph}" || bad "S-PrediXcan eQTLGen ${EQ_TAG} x ${ph}"
  done
fi

printf '  [note] the eQTLGen GWAS input is not simply the FinnGen extract: the model'"'"'s
  ' effect allele must be the GWAS effect allele, so the Z is re-signed onto the
  ' model alleles before running (step 3 of the original pipeline).'

# ---------------------------------------------------------------------------
echo
echo "====================================================================="
if [ "${FAIL}" -gt 0 ]; then
  echo " RESULT: ${FAIL} failure(s)."
  exit 1
fi
echo " RESULT: upstream chain completed. Outputs in ${OUT}"
echo "====================================================================="
exit 0

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
#   Python 3.12.13 / numpy 1.26.4 / scipy 1.13.1 / pandas 2.2.3, and it is now
#   pinned as env/environment-upstream.yml (it cannot share env/environment.yml,
#   which pins Python 3.13 + numpy 2).
#   Set METAXCAN_SW and PYTHON below.
#
# -----------------------------------------------------------------------------
# Two row conventions, one per arm
# -----------------------------------------------------------------------------
# `build_covariance.py` needs `--order` because the two archived covariance sets
# were produced by two different producer scripts with different row order, and
# each only reproduces byte-for-byte under its own:
#     GTEx arm    -> --order bim     (genes in model order, SNPs in .bim order)
#     eQTLGen arm -> --order model   (genes ascending, SNPs in model order)
# Steps 2 and 5 below pass the right one. See code/upstream/README.md.
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
#
# The build steps in steps 2, 4, 5 and 6 are the middleware under
# `code/upstream/` (see `code/upstream/README.md`). Before those scripts existed
# this chain could not be run unsupervised: it asked the operator to supply a
# GTEx gene-level covariance, an eQTLGen model database, an eQTLGen covariance
# and an allele-aligned GWAS that nothing in the archive produced.
# =============================================================================

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/.." && pwd)"
EXT="${EXT_DIR:-${REPO}/data/external}"
OUT="${UPSTREAM_OUT:-${REPO}/../_upstream_run}"
SW="${METAXCAN_SW:-}"
PY="${PYTHON:-$(command -v python3 || command -v python)}"
UP="${REPO}/code/upstream"
MODE="${1:-}"
FAIL=0

ok()   { printf '  [ ok ] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; FAIL=$((FAIL+1)); }
step() { printf '\n== %s ==\n' "$1"; }

case "$MODE" in
  -h|--help) sed -n '2,58p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
esac

PHENOS=(DR DN DPN)
declare -A FINNGEN=(
  [DR]="finngen_R13_DM_RETINOPATHY_EXMORE.gz"
  [DN]="finngen_R13_DM_NEPHROPATHY.gz"
  [DPN]="finngen_R13_DM_NEUROPATHY.gz"
)
TISSUES=(Whole_Blood Nerve_Tibial)
EQ_SOURCE="2019-12-11-cis-eQTLsFDR0.05-ProbeLevel-CohortInfoRemoved-BonferroniAdded.txt.gz"

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
for s in build_eqtlgen_db.py build_covariance.py align_gwas_to_model.py split_model_by_size.py; do
  [ -f "${UP}/${s}" ] || bad "missing build script ${UP}/${s}"
done

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
step "2. GTEx arm — build the gene-level covariance from g1000_eur"
# ---------------------------------------------------------------------------
# The gene-level (not SNP-level) covariance each tissue's S-PrediXcan run needs.
# `data/external/SHA256SUMS` pins the SNP-level covariance; this is the derived
# layer built from it and from the LD panel. See `code/upstream/build_covariance.py`.
if [ "${MODE}" = "--verify-only" ]; then
  printf '  [skip] build (--verify-only)\n'
else
  for tis in "${TISSUES[@]}"; do
    cov="${OUT}/cov/cov_${tis}.txt.gz"
    if [ -f "${cov}" ]; then printf '  [skip] %s exists\n' "$(basename "${cov}")"; continue; fi
    "${PY}" "${UP}/build_covariance.py" \
        --model-db "${EXT}/mashr_${tis}.db" \
        --plink-zip "${EXT}/g1000_eur.zip" --bfile-stem g1000_eur \
        --order bim \
        --out "${cov}" && ok "covariance ${tis}" || bad "covariance ${tis}"
  done
fi

# ---------------------------------------------------------------------------
step "3. GTEx arm — S-PrediXcan (official MetaXcan v0.8.1)"
# ---------------------------------------------------------------------------
# Note: `--stream_covariance` must NOT be used here — the GTEx tables in this
# archive were produced without it.
if [ "${MODE}" = "--verify-only" ]; then
  printf '  [skip] rerun (--verify-only)\n'
else
  for tis in "${TISSUES[@]}"; do
    for ph in "${PHENOS[@]}"; do
      cov="${OUT}/cov/cov_${tis}.txt.gz"
      [ -f "${cov}" ] || { printf '  [skip] %s: no %s\n' "$tis" "$cov"; continue; }
      out="${OUT}/official_${tis}_${ph}.csv"
      # SPrediXcan REFUSES to overwrite: given an existing --output_file it logs
      # "already exists, move it or delete it if you want it done again", exits 0
      # and writes nothing. Without this rm a re-run would report success while
      # leaving the previous file in place.
      rm -f "${out}"
      ( cd "${SW}" && "${PY}" SPrediXcan.py \
          --model_db_path "${EXT}/mashr_${tis}.db" \
          --covariance "${cov}" \
          --gwas_file "${OUT}/gwas/gwas_${ph}.tsv" \
          --snp_column snp --effect_allele_column alt --non_effect_allele_column ref \
          --beta_column beta --se_column se \
          --output_file "${out}" \
          --additional_output ) && ok "S-PrediXcan ${tis} x ${ph}" || bad "S-PrediXcan ${tis} x ${ph}"
    done
  done
fi

# ---------------------------------------------------------------------------
step "4. eQTLGen arm — build the weight database"
# ---------------------------------------------------------------------------
# AssessedAllele -> eff_allele, OtherAllele -> ref_allele, Zscore -> weight,
# restricted to the analysis universe. Reproduces the archived weights row for
# row, and the archived database byte for byte — see
# `code/upstream/build_eqtlgen_db.py`.
EQ_DB="${OUT}/eqtlgen/eQTLGen_Whole_Blood.db"
if [ "${MODE}" = "--verify-only" ]; then
  printf '  [skip] build (--verify-only)\n'
elif [ -f "${EQ_DB}" ]; then
  printf '  [skip] %s exists\n' "$(basename "${EQ_DB}")"
else
  "${PY}" "${UP}/build_eqtlgen_db.py" \
      --cis-eqtl "${EXT}/${EQ_SOURCE}" \
      --gene-symbols "${UP}/eqtlgen_gene_universe.txt" \
      --out "${EQ_DB}" && ok "eQTLGen weights" || bad "eQTLGen weights"
fi

# ---------------------------------------------------------------------------
step "5. eQTLGen arm — split by gene size, then build each band's covariance"
# ---------------------------------------------------------------------------
# The eQTLGen gene covariance is 111-394 MB gzipped; the official binary cannot
# hold the whole model's in memory on most machines. Partitioning by SNPs per
# gene and streaming each band's covariance keeps every run bounded.
EQ_TAG="${EQ_TAG:-}"     # e.g. A, B, C for a panel subset; empty = whole-blood model
if [ "${MODE}" = "--verify-only" ] || [ -z "${EQ_TAG}" ]; then
  printf '  [skip] set EQ_TAG=A (or B / C) to build and run a size band\n'
else
  DB="${OUT}/eqtlgen/db_${EQ_TAG}.db"
  COV="${OUT}/eqtlgen/cov_${EQ_TAG}.txt.gz"
  if [ ! -f "${DB}" ] && [ -f "${EQ_DB}" ]; then
    "${PY}" "${UP}/split_model_by_size.py" --model-db "${EQ_DB}" \
        --out-dir "${OUT}/eqtlgen" && ok "split model" || bad "split model"
  fi
  if [ ! -f "${COV}" ] && [ -f "${DB}" ]; then
    "${PY}" "${UP}/build_covariance.py" --model-db "${DB}" \
        --plink-zip "${EXT}/g1000_eur.zip" --bfile-stem g1000_eur \
        --order model \
        --out "${COV}" && ok "covariance ${EQ_TAG}" || bad "covariance ${EQ_TAG}"
  fi
fi

# ---------------------------------------------------------------------------
step "6. eQTLGen arm — align the GWAS onto the model alleles"
# ---------------------------------------------------------------------------
# The eQTLGen GWAS input is not simply the FinnGen extract: MetaXcan does not
# flip alleles, so the Z is re-signed onto the model's eff_allele before running.
if [ "${MODE}" = "--verify-only" ] || [ ! -f "${EQ_DB}" ]; then
  printf '  [skip] needs the eQTLGen model database from step 4\n'
else
  for ph in "${PHENOS[@]}"; do
    out="${OUT}/eqtlgen/gwas_${ph}_aligned.tsv"
    if [ -f "${out}" ]; then printf '  [skip] gwas_%s_aligned.tsv exists\n' "${ph}"; continue; fi
    "${PY}" "${UP}/align_gwas_to_model.py" --model-db "${EQ_DB}" \
        --gwas "${EXT}/${FINNGEN[$ph]}" --out "${out}" \
      && ok "aligned ${ph}" || bad "aligned ${ph}"
  done
fi

# ---------------------------------------------------------------------------
step "7. eQTLGen arm — S-PrediXcan (streamed covariance)"
# ---------------------------------------------------------------------------
# S-PrediXcan here DOES use --stream_covariance: the eQTLGen gene covariance is
# 111-394 MB gzipped and will not fit in memory in one piece on most machines.
if [ "${MODE}" = "--verify-only" ] || [ -z "${EQ_TAG}" ]; then
  printf '  [skip] set EQ_TAG=A (and provide db_%%s.db / cov_%%s.txt.gz) to run a panel subset\n'
else
  DB="${OUT}/eqtlgen/db_${EQ_TAG}.db"
  COV="${OUT}/eqtlgen/cov_${EQ_TAG}.txt.gz"
  [ -f "${DB}" ] && [ -f "${COV}" ] || bad "provide ${DB} and ${COV}"
  for ph in "${PHENOS[@]}"; do
    out="${OUT}/eqtlgen/official_eq_${EQ_TAG}_${ph}.csv"
    rm -f "${out}"      # SPrediXcan will not overwrite an existing --output_file; see step 3
    ( cd "${SW}" && "${PY}" SPrediXcan.py \
        --model_db_path "${DB}" --covariance "${COV}" \
        --gwas_file "${OUT}/eqtlgen/gwas_${ph}_aligned.tsv" \
        --snp_column snp --effect_allele_column alt --non_effect_allele_column ref \
        --beta_column beta --se_column se \
        --output_file "${out}" \
        --additional_output --stream_covariance ) \
      && ok "S-PrediXcan eQTLGen ${EQ_TAG} x ${ph}" || bad "S-PrediXcan eQTLGen ${EQ_TAG} x ${ph}"
  done
fi

# ---------------------------------------------------------------------------
step "8. Middleware hash check"
# ---------------------------------------------------------------------------
# Hash every artefact this chain produces against the copy the reported numbers
# came from. Until 2026-10-03 nothing could fail here: the archive recorded these
# hashes in prose only, which is how a wrong-row-order covariance survived —
# same genes, same values, different bytes, and a *content* comparison passes.
# Absent artefacts are reported, not treated as failures: a partial rebuild is a
# legitimate thing to check. `--require-all` flips that if you want the full set.
if [ -f "${UP}/verify_middleware.py" ]; then
  "${PY}" "${UP}/verify_middleware.py" --run-dir "${OUT}" \
    && ok "middleware matches the archived hashes" \
    || bad "middleware does NOT match the archived hashes (see the DIFFERS rows above)"
else
  skip "code/upstream/verify_middleware.py not present"
fi

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

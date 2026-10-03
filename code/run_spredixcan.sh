#!/bin/bash
# =============================================================================
# run_spredixcan.sh — S-PrediXcan 运行脚本（参考/可选）
# =============================================================================
# 此脚本记录了 S-PrediXcan 的完整命令行调用，供完整管道复现使用。
# 需要挂载外部大文件（FinnGen GWAS、GTEx 模型库、1000G LD 参考面板）。
#
# 使用方式:
#   docker run --rm \
#     -v /path/to/finngen_data:/app/input/finngen \
#     -v /path/to/gtex_models:/app/input/gtex \
#     -v /path/to/eqtlgen_models:/app/input/eqtlgen \
#     -v /path/to/1000g:/app/input/1000g \
#     -v $(pwd)/output:/app/output \
#     twas-eqtl-repro \
#     bash /app/code/run_spredixcan.sh
#
# NOTE ON THE MOUNT POINTS. They are /app/input/... to match INPUT_DIR below. An earlier
# revision of this header mounted them at /input/... while the script read /app/input/...,
# so every model and GWAS file resolved to a path that did not exist and the script printed
# "SKIP: missing model or GWAS file" for all nine runs — a silent no-op that looked like a
# successful run. The entry-point path was wrong too (/app/run_spredixcan.sh; the file lives
# under code/). Both fixed 2026-10-03.
#
# This script is NOT invoked by code/run_all.sh. It documents the upstream step, which needs
# three layers this archive does not redistribute (see data/README.md, all rows `not-held`).
# =============================================================================

set -euo pipefail

# Loud-failure accounting. A previous revision printed "SKIP: missing model or GWAS file" for
# every run and still exited 0, so an unconfigured invocation was indistinguishable from a
# successful one. At least one run must actually execute.
RAN=0
SKIPPED=0

INPUT_DIR="/app/input"
OUTPUT_DIR="/app/output"
SPREDIXCAN="/opt/MetaXcan/software/SPrediXcan.py"
COVARIANCE="${INPUT_DIR}/1000g/g1000_eur_covariance.txt.gz"

echo "====================================================================="
echo " S-PrediXcan Execution Script (Reference)"
echo "====================================================================="
echo " Input directory: ${INPUT_DIR}"
echo " Output directory: ${OUTPUT_DIR}"
echo "====================================================================="

# =============================================================================
# PART A: GTEx v8 TWAS (Baseline)
# =============================================================================
echo ""
echo "=== PART A: GTEx v8 TWAS ==="

for TISSUE in "Nerve_Tibial" "Whole_Blood"; do
    MODEL="${INPUT_DIR}/gtex/GTEx_v8_MASHR_${TISSUE}.db"
    for PHENO in "DR" "DN" "DPN"; do
        GWAS="${INPUT_DIR}/finngen/finngen_R13_DM_${PHENO}.gz"
        OUTPUT="${OUTPUT_DIR}/gtex_${TISSUE}_${PHENO}.csv"

        echo "  Running: ${TISSUE} × ${PHENO}..."
        if [ -f "${MODEL}" ] && [ -f "${GWAS}" ]; then
            python3 "${SPREDIXCAN}" \
                --model_db_path "${MODEL}" \
                --covariance "${COVARIANCE}" \
                --gwas_file "${GWAS}" \
                --snp_column rsid \
                --effect_allele_column alt \
                --non_effect_allele_column ref \
                --beta_column beta \
                --se_column se \
                --pvalue_column pval \
                --output_file "${OUTPUT}" \
                --additional_output \
                2>&1 | tail -5
            echo "    Output: ${OUTPUT}"
            RAN=$((RAN + 1))
        else
            echo "    SKIP: missing model or GWAS file (${MODEL} , ${GWAS})"
            SKIPPED=$((SKIPPED + 1))
        fi
    done
done

# =============================================================================
# Multi-tissue integration (Stouffer)
# =============================================================================
echo ""
echo "=== Multi-tissue Stouffer integration ==="
echo "  (Manual step: requires per-tissue output files from above)"
echo "  Formula: Z_combined = sum(w_i * Z_i) / sqrt(sum(w_i^2))"
echo "    where w_i = sqrt(N_i), N_i = tissue sample size"
echo "  Tissues: Nerve_Tibial (N=532) + Whole_Blood (N=670)"

# =============================================================================
# PART B: eQTLGen TWAS (Sensitivity)
# =============================================================================
echo ""
echo "=== PART B: eQTLGen TWAS ==="

MODEL="${INPUT_DIR}/eqtlgen/eQTLGen_Whole_Blood.db"
for PHENO in "DR" "DN" "DPN"; do
    GWAS="${INPUT_DIR}/finngen/finngen_R13_DM_${PHENO}.gz"
    OUTPUT="${OUTPUT_DIR}/eqtlgen_Whole_Blood_${PHENO}.csv"

    echo "  Running: eQTLGen × ${PHENO}..."
    if [ -f "${MODEL}" ] && [ -f "${GWAS}" ]; then
        python3 "${SPREDIXCAN}" \
            --model_db_path "${MODEL}" \
            --covariance "${COVARIANCE}" \
            --gwas_file "${GWAS}" \
            --snp_column rsid \
            --effect_allele_column alt \
            --non_effect_allele_column ref \
            --beta_column beta \
            --se_column se \
            --pvalue_column pval \
            --output_file "${OUTPUT}" \
            --additional_output \
            2>&1 | tail -5
        echo "    Output: ${OUTPUT}"
        RAN=$((RAN + 1))
    else
        echo "    SKIP: missing model or GWAS file (${MODEL} , ${GWAS})"
        SKIPPED=$((SKIPPED + 1))
    fi
done

echo ""
echo "====================================================================="
echo " S-PrediXcan runs complete: ${RAN} run, ${SKIPPED} skipped."
echo "====================================================================="
if [ "${RAN}" -eq 0 ]; then
    echo ""
    echo " ERROR: nothing ran. Every model and GWAS path was missing, which means the input"
    echo "        layers are not mounted where this script reads them. Check the -v mounts in"
    echo "        the header: they must land under /app/input/. Exiting non-zero so an"
    echo "        unconfigured invocation cannot be mistaken for a successful one."
    echo ""
    exit 1
fi
echo " Next steps: Run downstream analysis with:"
echo "   bash /app/code/run_all.sh"
echo "====================================================================="

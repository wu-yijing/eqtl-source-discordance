#!/usr/bin/env bash
# 独立重跑上游链：raw third-party inputs -> Z layer
set -uo pipefail
REPO=/tmp/repoaudit/eqtl-source-discordance
export EXT_DIR="E:/workbuddy/_ext_stage_20261004"
export UPSTREAM_OUT="E:/workbuddy/_upstream_20261004/run"
export METAXCAN_SW="E:/workbuddy/_upstream_20261004/MetaXcan-0.8.1/software"
export PYTHON="E:/workbuddy/_py312_psa/python/python.exe"
LOGD="E:/workbuddy/_upstream_20261004/logs"
mkdir -p "$LOGD"
cd "$REPO"
for band in A B C; do
  echo "################ EQ_TAG=$band ################"
  EQ_TAG=$band bash code/run_upstream.sh > "$LOGD/upstream_$band.log" 2>&1
  echo "EQ_TAG=$band exit=$?  (log: $LOGD/upstream_$band.log)"
done
echo "ALL_BANDS_DONE"

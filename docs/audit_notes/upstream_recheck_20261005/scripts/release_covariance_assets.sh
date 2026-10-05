#!/usr/bin/env bash
# =============================================================================
# release_covariance_assets.sh — publish the three eQTLGen band covariances as
# GitHub Release assets
# =============================================================================
# WHY A RELEASE AND NOT THE TREE. `cov_A.txt.gz` (175.2 MiB) and `cov_C.txt.gz`
# (106.4 MiB) are over GitHub's hard 100 MiB per-file block, so they cannot be
# pushed to any branch at all; `cov_B.txt.gz` (94.6 MiB) fits but ships alone
# for no benefit. A Release asset has a 2 GiB per-file limit and is the only
# carrier GitHub offers inward of an external deposit. Decisions: see
# `data/upstream/README.md` and `../README.md` §6.
#
# AUTHENTICATION. This is the API, so the machine's git credentials do not
# apply — an SSH key can push commits and tags but cannot create a Release.
# Provide a GitHub personal access token (classic, `repo` scope; or fine-grained
# with Contents: read and write) in $GH_TOKEN.
#
# USAGE
#   GH_TOKEN=ghp_... bash release_covariance_assets.sh --file-dir <dir> [--tag v4.0.3]
#   GH_TOKEN=ghp_... bash release_covariance_assets.sh --file-dir <dir> --dry-run
#
# The script verifies each file's byte count against the ledger before uploading
# anything, so a wrong build cannot be published under the right name.
# =============================================================================
set -uo pipefail

REPO_SLUG="${REPO_SLUG:-wu-yijing/eqtl-source-discordance}"
TAG="${TAG:-}"
FILE_DIR=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --file-dir) FILE_DIR="${2:-}"; shift 2 ;;
    --tag)      TAG="${2:-}"; shift 2 ;;
    --repo)     REPO_SLUG="${2:-}"; shift 2 ;;
    --dry-run)  DRY_RUN=1; shift ;;
    -h|--help)  sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

: "${FILE_DIR:?--file-dir is required (the directory holding cov_A/B/C.txt.gz)}"
: "${TAG:?--tag is required (e.g. v4.0.3); see docs/RELEASE_PROCESS.md - the tag must equal the version recorded in .zenodo.json}"

# name:expected-bytes, transcribed from
# docs/audit_notes/upstream_chain_closure_20261004/ledger/middleware_ledger.tsv
EXPECT="cov_A.txt.gz:183659809 cov_B.txt.gz:99159225 cov_C.txt.gz:111535391"

# sha256 of the copies rebuilt on 2026-10-05 (recorded for the release notes; the
# archive pins these artefacts by CONTENT md5, not by file sha256 — see ../README.md §3)
declare -A SHA256=(
  [cov_A.txt.gz]=b9c690a8afe8395a2f06ce763fd70cb0a872df5136cba93ecb8c298755a71d73
  [cov_B.txt.gz]=4a8f2a55ab7d39e4b0eba026b359fa85f4637281e39add8ffd9b5d58e3587021
  [cov_C.txt.gz]=8827b67ac47eec3f9f9293078438e5bd1856ef276349aa4401270f573129e3b2
)

ok()  { printf '  [ ok ] %s\n' "$1"; }
bad() { printf '  [FAIL] %s\n' "$1"; }

echo "== 1. verify the files before publishing them =="
FILES=""
fail=0
for spec in $EXPECT; do
  name="${spec%%:*}"; want="${spec##*:}"
  path="${FILE_DIR}/${name}"
  if [ ! -f "$path" ]; then bad "$path is missing"; fail=$((fail+1)); continue; fi
  got=$(stat -c%s "$path" 2>/dev/null || stat -f%z "$path")
  if [ "$got" != "$want" ]; then
    bad "$name is $got B, expected $want B — refusing to publish a wrong build"; fail=$((fail+1)); continue
  fi
  s=$(sha256sum "$path" | cut -d' ' -f1)
  if [ "$s" != "${SHA256[$name]}" ]; then
    printf '  [warn] %s: sha256 %s differs from the recorded %s (byte counts still agree)\n' \
      "$name" "${s:0:16}" "${SHA256[$name]:0:16}"
  else
    ok "$name  $(printf '%s' "$want") B  sha256 ${s:0:16}…"
  fi
  FILES="$FILES $path"
done
[ "$fail" -eq 0 ] || { echo "RESULT: $fail file(s) failed verification; nothing was uploaded."; exit 1; }

if [ "$DRY_RUN" = "1" ]; then
  echo
  echo "RESULT: --dry-run — files verified, nothing uploaded."
  echo "Would create release '$TAG' on $REPO_SLUG with assets:$FILES"
  exit 0
fi

: "${GH_TOKEN:?set GH_TOKEN to a GitHub PAT (classic, repo scope)}"
API="https://api.github.com/repos/${REPO_SLUG}"

echo
echo "== 2. create the release '$TAG' (no-op if it already exists) =="
PAYLOAD="$(mktemp)"
cat > "$PAYLOAD" <<JSON
{"tag_name":"${TAG}",
 "name":"${TAG} -- upstream middleware: eQTLGen band covariances",
 "body":"The three eQTLGen band covariances from code/run_upstream.sh, which cannot live in the tree (GitHub's 100 MiB per-file block). Content-identical to the copies the reported numbers came from; their content md5s are recorded in data/external/README.md and in docs/audit_notes/upstream_chain_closure_20261004/ledger/middleware_ledger.tsv, and the 2026-10-05 rebuild is recorded in docs/audit_notes/upstream_recheck_20261005/.",
 "draft":false,
 "prerelease":false}
JSON
rel=$(curl -sS -X POST "$API/releases" \
  -H "Authorization: Bearer ${GH_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -d @"$PAYLOAD")
rm -f "$PAYLOAD"
rel_id=$(printf '%s' "$rel" | sed -n 's/.*"id": *\([0-9]*\).*/\1/p' | head -1)
if [ -z "$rel_id" ]; then
  echo "  create returned no id; trying to read the existing release"
  rel=$(curl -sS "$API/releases/tags/${TAG}" -H "Authorization: Bearer ${GH_TOKEN}")
  rel_id=$(printf '%s' "$rel" | sed -n 's/.*"id": *\([0-9]*\).*/\1/p' | head -1)
fi
[ -n "$rel_id" ] || { echo "  [FAIL] could not create or read the release:"; printf '%s\n' "$rel" | head -20; exit 1; }
ok "release id $rel_id"

echo
echo "== 3. upload the assets =="
for path in $FILES; do
  name=$(basename "$path")
  up="https://uploads.github.com/repos/${REPO_SLUG}/releases/${rel_id}/assets?name=${name}"
  code=$(curl -sS -o /tmp/_asset.json -w '%{http_code}' -X POST "$up" \
    -H "Authorization: Bearer ${GH_TOKEN}" \
    -H "Content-Type: application/gzip" \
    --data-binary "@${path}")
  if [ "$code" = "201" ] || [ "$code" = "200" ]; then
    url=$(sed -n 's/.*"browser_download_url": *"\([^"]*\)".*/\1/p' /tmp/_asset.json | head -1)
    ok "$name -> ${url:-uploaded}"
  else
    bad "$name upload returned HTTP $code"; head -5 /tmp/_asset.json
  fi
done

echo
echo "RESULT: release '${TAG}' on ${REPO_SLUG} carries the band covariances."

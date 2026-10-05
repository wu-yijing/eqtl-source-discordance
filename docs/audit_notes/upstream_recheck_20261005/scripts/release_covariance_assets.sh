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
#   # attach to an EXISTING release, creating no tag (the default in this archive:
#   # a version tag is only cut when the maintainer does a unified release)
#   GH_TOKEN=ghp_... bash release_covariance_assets.sh --file-dir <dir> --release-id <id>
#
#   # or create a release on a tag (only when a version release is intended)
#   GH_TOKEN=ghp_... bash release_covariance_assets.sh --file-dir <dir> --tag v4.0.3
#
#   GH_TOKEN=ghp_... bash release_covariance_assets.sh --file-dir <dir> --release-id <id> --dry-run
#
# The script verifies each file's byte count against the ledger before uploading
# anything, so a wrong build cannot be published under the right name. Uploading is
# idempotent: a same-named asset already on the release is replaced, not duplicated.
# =============================================================================
set -uo pipefail

REPO_SLUG="${REPO_SLUG:-wu-yijing/eqtl-source-discordance}"
TAG="${TAG:-}"
RELEASE_ID="${RELEASE_ID:-}"
FILE_DIR=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --file-dir)   FILE_DIR="${2:-}"; shift 2 ;;
    --tag)        TAG="${2:-}"; shift 2 ;;
    --release-id) RELEASE_ID="${2:-}"; shift 2 ;;
    --repo)       REPO_SLUG="${2:-}"; shift 2 ;;
    --dry-run)    DRY_RUN=1; shift ;;
    -h|--help)    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

: "${FILE_DIR:?--file-dir is required (the directory holding cov_A/B/C.txt.gz)}"
if [ -z "$RELEASE_ID" ] && [ -z "$TAG" ]; then
  echo "give --release-id <id> to attach to an existing release without creating a tag," >&2
  echo "or --tag vX.Y.Z to create one (docs/RELEASE_PROCESS.md requires the tag to equal" >&2
  echo "the version recorded in .zenodo.json)." >&2
  exit 2
fi

# Python is needed only to read ids out of the release JSON; the archive requires
# python3 for its release gates anyway.
PYBIN="${PYBIN:-}"
if [ -z "$PYBIN" ]; then
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PYBIN="$c"; break; fi
  done
fi
jget() { "$PYBIN" -c 'import json,sys
key = sys.argv[1]
d = json.load(sys.stdin)
if isinstance(d, dict):
    d = [d]
val = None
if key.startswith("asset:"):
    name = key[6:]
    val = next((a["id"] for a in d if a.get("name") == name), None)
else:
    val = d[0].get(key) if d else None
print("" if val is None else val)' "$1"; }

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
  if [ -n "$RELEASE_ID" ]; then
    echo "Would attach to the EXISTING release ${RELEASE_ID} (no tag created), assets:${FILES}"
  else
    echo "Would create the release on tag '${TAG}', assets:${FILES}"
  fi
  exit 0
fi

: "${GH_TOKEN:?set GH_TOKEN to a GitHub PAT (classic, repo scope)}"
API="https://api.github.com/repos/${REPO_SLUG}"

echo
if [ -n "$RELEASE_ID" ]; then
  echo "== 2. attach to the existing release $RELEASE_ID (no tag is created) =="
  rel=$(curl -sS "$API/releases/${RELEASE_ID}" -H "Authorization: Bearer ${GH_TOKEN}")
  rel_id=$(printf '%s' "$rel" | jget id)
  tag_shown=$(printf '%s' "$rel" | jget tag_name)
  [ -n "$rel_id" ] || { echo "  [FAIL] could not read release ${RELEASE_ID}:"; printf '%s\n' "$rel" | head -20; exit 1; }
  ok "release $rel_id on tag ${tag_shown:-?}"
else
  echo "== 2. create the release on tag '$TAG' (no-op if it already exists) =="
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
  rel_id=$(printf '%s' "$rel" | jget id)
  if [ -z "$rel_id" ]; then
    echo "  create returned no id; trying to read the existing release"
    rel=$(curl -sS "$API/releases/tags/${TAG}" -H "Authorization: Bearer ${GH_TOKEN}")
    rel_id=$(printf '%s' "$rel" | jget id)
  fi
  [ -n "$rel_id" ] || { echo "  [FAIL] could not create or read the release:"; printf '%s\n' "$rel" | head -20; exit 1; }
  ok "release id $rel_id"
fi

echo
echo "== 3. upload the assets =="
# GitHub rejects a second asset of the same name (HTTP 422), so a re-run must replace
# rather than duplicate: list what is already there and delete a same-named entry first.
existing=$(curl -sS "$API/releases/${rel_id}/assets?per_page=100" \
  -H "Authorization: Bearer ${GH_TOKEN}")
for path in $FILES; do
  name=$(basename "$path")
  old_id=$(printf '%s' "$existing" | jget "asset:${name}" 2>/dev/null || true)
  if [ -n "$old_id" ]; then
    dc=$(curl -sS -o /dev/null -w '%{http_code}' -X DELETE \
      "$API/releases/assets/${old_id}" -H "Authorization: Bearer ${GH_TOKEN}")
    echo "  replaced the existing asset ${name} (DELETE ${dc})"
  fi
  up="https://uploads.github.com/repos/${REPO_SLUG}/releases/${rel_id}/assets?name=${name}"
  code=$(curl -sS -o /tmp/_asset.json -w '%{http_code}' -X POST "$up" \
    -H "Authorization: Bearer ${GH_TOKEN}" \
    -H "Content-Type: application/gzip" \
    --data-binary "@${path}")
  if [ "$code" = "201" ] || [ "$code" = "200" ]; then
    url=$(sed -n 's/.*"browser_download_url": *"\([^"]*\)".*/\1/p' /tmp/_asset.json | head -1)
    ok "$name -> ${url:-uploaded}"
  else
    bad "$name upload returned HTTP $code"
    if [ "$code" = "404" ]; then
      echo "         HTTP 404 from uploads.github.com is how GitHub reports a token that"
      echo "         cannot write. A classic PAT needs the 'public_repo' scope (or 'repo');"
      echo "         a fine-grained PAT needs Contents: Read and write on this repository."
      echo "         Read-only calls still succeed with an unscoped token, so the failure"
      echo "         looks like a missing release rather than a permission error. Check the"
      echo "         token with:  curl -sS -D - -o /dev/null -H \"Authorization: Bearer \$GH_TOKEN\" \\"
      echo "                        https://api.github.com/user | grep -i x-oauth-scopes"
      echo "         An empty value there means no scopes are granted."
    fi
    head -5 /tmp/_asset.json
  fi
done

echo
echo "== 4. confirm what the release now carries =="
final=$(curl -sS "$API/releases/${rel_id}/assets?per_page=100" \
  -H "Authorization: Bearer ${GH_TOKEN}")
"$PYBIN" - "$final" <<'PYEOF'
import json, sys
d = json.loads(sys.argv[1])
if not d:
    print('  no assets'); raise SystemExit(1)
for a in d:
    print('  %-16s %12s B  %s' % (a['name'], a['size'], a['browser_download_url']))
PYEOF

echo
echo "RESULT: release ${rel_id} on ${REPO_SLUG} carries the band covariances."

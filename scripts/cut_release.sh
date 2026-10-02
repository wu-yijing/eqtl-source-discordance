#!/usr/bin/env bash
# cut_release.sh — pre-flight checks for cutting a release of this archive.
#
# Usage:  bash scripts/cut_release.sh [vX.Y.Z]
#         If the version is omitted it is read from .zenodo.json.
#
# Exit code 0 = all checks passed. Non-zero = do NOT cut the release.
# This script performs READ-ONLY checks. It never commits, tags or pushes.

set -uo pipefail

FAIL=0
WARN=0
ok()   { printf '  [ ok ] %s\n' "$1"; }
warn() { printf '  [warn] %s\n' "$1"; WARN=$((WARN+1)); }
bad()  { printf '  [FAIL] %s\n' "$1"; FAIL=$((FAIL+1)); }

need() { command -v "$1" >/dev/null 2>&1 || { bad "required tool not found: $1"; return 1; }; }

echo "== 0. tools =="
need git && ok "git $(git --version | awk '{print $3}')"
need python || need python3
PY=$(command -v python3 || command -v python)
[ -n "${PY:-}" ] && ok "python: $PY"

echo
echo "== 1. repository state =="
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
[ "$BRANCH" = "main" ] && ok "on main" || warn "on '$BRANCH', not 'main'"

if [ -z "$(git status --porcelain)" ]; then ok "working tree clean"; else bad "working tree is dirty — commit or stash first"; git status --short | sed 's/^/         /'; fi

git fetch --quiet 2>/dev/null
if git status -sb | grep -q '\[behind'; then bad "local branch is behind the remote"; else ok "not behind remote"; fi

echo
echo "== 2. version agreement =="
VER="${1:-}"
if [ -z "$VER" ]; then
  VER="v$($PY -c "import json;print(json.load(open('.zenodo.json',encoding='utf-8'))['version'])" 2>/dev/null)"
fi
echo "  target version: ${VER:-<unresolved>}"

if [ -f .zenodo.json ]; then
  $PY -m json.tool .zenodo.json > /dev/null 2>&1 && ok ".zenodo.json is valid JSON" || bad ".zenodo.json is not valid JSON"
  ZV=$($PY -c "import json;print(json.load(open('.zenodo.json',encoding='utf-8')).get('version',''))" 2>/dev/null)
  [ "$ZV" = "${VER#v}" ] && ok ".zenodo.json version matches (${ZV})" || bad ".zenodo.json version '${ZV}' != '${VER#v}'"
  ZC=$($PY -c "import json;d=json.load(open('.zenodo.json',encoding='utf-8'));print(len(d.get('creators',[])))" 2>/dev/null)
  [ "${ZC:-0}" -ge 1 ] && ok ".zenodo.json declares ${ZC} creator(s)" || bad ".zenodo.json has no creators — Zenodo will fall back to the GitHub account name"
else
  bad ".zenodo.json missing at repository root"
fi

if [ -f CITATION.cff ]; then
  grep -q "^version: *${VER#v}" CITATION.cff && ok "CITATION.cff version matches" || warn "CITATION.cff version does not match ${VER#v}"
else
  warn "CITATION.cff missing"
fi

if [ -f CHANGELOG.md ]; then
  grep -q "^## \[${VER#v}\]" CHANGELOG.md && ok "CHANGELOG.md has a section for ${VER#v}" || bad "CHANGELOG.md has no '## [${VER#v}]' section"
  grep -qi "number" CHANGELOG.md || warn "CHANGELOG.md does not state whether reported numbers changed"
else
  bad "CHANGELOG.md missing"
fi

echo
echo "== 3. audit anchors (must remain reachable) =="
for c in 58da15b e70806b; do
  if git cat-file -t "$c" >/dev/null 2>&1; then
    git merge-base --is-ancestor "$c" HEAD 2>/dev/null && ok "$c reachable from HEAD" || bad "$c exists but is NOT an ancestor of HEAD"
  else
    bad "$c missing — the manuscript's pre-specification claim cannot be supported"
  fi
done

echo
echo "== 4. data hygiene =="
BIG=$(git ls-files -z 2>/dev/null | xargs -0 -I{} sh -c 'test -f "{}" && echo "$(wc -c <"{}") {}"' 2>/dev/null | awk '$1>104857600' | head -5)
[ -z "$BIG" ] && ok "no tracked file over 100 MB" || { bad "tracked file(s) over 100 MB:"; echo "$BIG" | sed 's/^/         /'; }

STRAY=$(git ls-files 2>/dev/null | grep -E '^(figs|results|outputs|logs|tmp)/' | head -5)
[ -z "$STRAY" ] && ok "no runtime output directories tracked" || { warn "runtime output tracked:"; echo "$STRAY" | sed 's/^/         /'; }

if [ -f metadata/provenance.json ]; then
  $PY -m json.tool metadata/provenance.json > /dev/null 2>&1 && ok "metadata/provenance.json is valid JSON" || bad "metadata/provenance.json is not valid JSON"
  grep -q '<hash' metadata/provenance.json && warn "metadata/provenance.json still contains placeholders" || ok "provenance.json has no placeholders"
else
  warn "metadata/provenance.json missing"
fi

if [ -f metadata/ARCHIVE_MAP.md ]; then
  # The status key is four-state (VERIFIED / DERIVABLE / GAP / n-a). ⚠️ is no longer a
  # status — it now marks layer caveats, so counting it would be misleading. Count GAP
  # rows instead: those are the ones a release should consciously accept.
  # NOTE: `grep -c` exits 1 on no match, so `|| echo 0` would append a second line.
  N=$(grep -c '🔴' metadata/ARCHIVE_MAP.md 2>/dev/null) || N=0
  N=${N:-0}
  if [ "$N" -eq 0 ]; then
    ok "ARCHIVE_MAP.md has no GAP rows"
  else
    warn "ARCHIVE_MAP.md has $N row(s) marked GAP — each must be fixed or explicitly declared in README before release"
  fi
else
  warn "metadata/ARCHIVE_MAP.md missing"
fi

echo
echo "== 5. labelling placeholders =="
PH=$(git ls-files -z 2>/dev/null | xargs -0 grep -l '<CONCEPT>\|<VER>\|PLACEHOLDER' 2>/dev/null | head -10)
[ -z "$PH" ] && ok "no <CONCEPT>/<VER> placeholders left" || { warn "placeholders still present in:"; echo "$PH" | sed 's/^/         /'; }

echo
echo "=================================================="
printf ' failures: %d   warnings: %d\n' "$FAIL" "$WARN"
if [ "$FAIL" -gt 0 ]; then
  echo " RESULT: DO NOT CUT THIS RELEASE until the failures above are resolved."
  exit 1
fi
echo " RESULT: pre-flight passed. Next: commit, then"
echo "         git tag -a ${VER:-vX.Y.Z} -m '${VER:-vX.Y.Z}'"
echo "         git push origin main --follow-tags"
echo "         then publish the release at https://github.com/wu-yijing/eqtl-source-discordance/releases/new"
exit 0

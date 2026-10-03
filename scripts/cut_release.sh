#!/usr/bin/env bash
# cut_release.sh — pre-flight checks for cutting a release of this archive.
#
# Usage:  bash scripts/cut_release.sh [vX.Y.Z]
#         If the version is omitted it is read from .zenodo.json.
#
# Exit code 0 = all checks passed. Non-zero = do NOT cut the release.
# This script performs READ-ONLY checks. It never commits, tags or pushes.
#
# THIS RUNS WHERE THE AUTHOR WORKS, which is exactly why it is not sufficient. Four
# defects have shipped from here that passed locally and failed for every reader: a path
# bootstrap one directory short, a hash table recording CRLF values for files a clone
# checks out as LF, a manifest hashing the working tree, and a rebuild that wrote a
# shipped input with the platform's line ending. Before publishing, run
#
#     bash scripts/verify_from_clone.sh
#
# which re-runs everything in a fresh `git clone --no-hardlinks`.

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

  # --- coverage gate ---------------------------------------------------------
  # The manifest must account for every tracked file: len(files)+len(excluded)
  # == `git ls-files`. Without this the 2026-10-02 upload shipped a 59-file
  # reproduction package that provenance.json registered zero times, while the
  # README claimed every input was pinned by checksum. A count comparison is
  # crude but it is exactly the check that was missing.
  GATE=$("${PY}" - <<'PYEOF' 2>/dev/null
import json, subprocess
d = json.load(open('metadata/provenance.json', encoding='utf-8'))
raw = subprocess.run(['git', 'ls-files', '-z'], stdout=subprocess.PIPE, check=True).stdout
tracked = len([x for x in raw.split(b'\0') if x])
print(len(d.get('files', [])) + len(d.get('excluded', [])), tracked)
PYEOF
)
  MAN=$(printf '%s' "$GATE" | awk '{print $1}')
  TRACK=$(printf '%s' "$GATE" | awk '{print $2}')
  if [ -z "${MAN:-}" ] || [ -z "${TRACK:-}" ]; then
    bad "could not read the provenance coverage counts — is git available?"
  elif [ "$MAN" -eq "$TRACK" ]; then
    ok "provenance.json covers the tracked tree ($MAN entries = git ls-files)"
  else
    bad "provenance.json covers $MAN of $TRACK tracked files — run scripts/collect_provenance.py"
  fi
  # --- the hashes must actually be right, not merely present -----------------
  # The coverage gate above counts entries; it says nothing about whether they
  # match. verify_provenance.py recomputes every SHA-256 from the INDEX — the bytes
  # a clone receives — and compares. Without this the manifest could be stale and
  # the release would still pass.
  if [ -f scripts/verify_provenance.py ]; then
    if VP=$("$PY" scripts/verify_provenance.py 2>&1); then
      ok "$(printf '%s' "$VP" | grep 'manifest:' | head -1 | sed 's/^ *//')"
    else
      bad "metadata/provenance.json does not match the tree:"
      printf '%s\n' "$VP" | grep -E 'FAIL|do not agree' | head -6 | sed 's/^/         /'
    fi
  else
    warn "scripts/verify_provenance.py missing — the manifest is never re-checked"
  fi
else
  warn "metadata/provenance.json missing"
fi

if [ -f metadata/ARCHIVE_MAP.md ]; then
  # The GAP count comes from scripts/check_archive_map.py (--counts), which reads the
  # status column of the item tables. Counting 🔴 in the whole file — the obvious way,
  # used here before — also counts the status key that defines the mark and the summary
  # line that reports it, and so over-report. A count taken from the wrong universe is
  # the same defect class as the drifted summary line this map has already had once.
  #
  # Note also why this is not grep: under Git Bash on Windows, grep fails to match the
  # 4-byte emoji and silently returns 0, which would report "no GAP rows" on a file
  # containing five of them.
  if [ -f scripts/check_archive_map.py ]; then
    # NOT `set -- $(...)`: that would clobber $1, which holds the target version.
    AMC=$("$PY" scripts/check_archive_map.py --counts 2>/dev/null)
    N=$(printf '%s' "$AMC" | awk '{print $4}')
  else
    N=$("${PY}" -c "
t = open('metadata/ARCHIVE_MAP.md', encoding='utf-8').read()
print(t.count('\U0001F534'))
" 2>/dev/null) || N=0
  fi
  N=${N:-0}
  if [ "$N" -eq 0 ]; then
    ok "ARCHIVE_MAP.md has no GAP rows"
  else
    warn "ARCHIVE_MAP.md has $N row(s) marked GAP — each must be fixed or explicitly declared in README before release"
  fi
  # --- the map must be checkable, not just present ---------------------------
  # The GAP count above reads the status column. It cannot see the markdown
  # structure, and that is where the map has actually gone wrong: a summary count
  # that drifted from the table, an `Input locality` column added to the rows but
  # not to the headers (so Markdown renderers dropped it), and an unescaped pipe
  # that shifted a row one column to the right. check_archive_map.py checks all
  # three, plus the column declaration and the locality vocabulary.
  if [ -f scripts/check_archive_map.py ]; then
    if AM=$("$PY" scripts/check_archive_map.py 2>&1); then
      ok "$(printf '%s' "$AM" | tail -1 | sed 's/^ *//; s/^\[ ok \] //')"
    else
      bad "metadata/ARCHIVE_MAP.md is structurally unsound:"
      printf '%s\n' "$AM" | grep -E 'problem|    - ' | head -8 | sed 's/^/         /'
    fi
  else
    warn "scripts/check_archive_map.py missing — the map is checked by eye only"
  fi
else
  warn "metadata/ARCHIVE_MAP.md missing"
fi

echo
echo "== 4b. reproduction-package wiring =="
# The bootstrap that lets each script find paths_config.py is duplicated per script. A wrong
# number of os.path.dirname(...) levels compiles fine and dies at run time with
# "No module named 'paths_config'" — which is what shipped in the first portable revision of
# the package. This executes every script's preamble and fails if `paths_config` is not
# importable. It stubs third-party modules that this interpreter lacks, so it works
# under a bare Python.
WIRE="code/analyses/reproduction_20261002/check_wiring.py"
if [ -f "$WIRE" ]; then
  if "$PY" "$WIRE" > /dev/null 2>&1; then
    N=$("$PY" "$WIRE" 2>/dev/null | awk '/^wired:/ {print $2}')
    ok "every reproduction-package script imports paths_config (${N:-?} wired)"
  else
    bad "at least one reproduction-package script cannot import paths_config — run: $PY $WIRE"
  fi
else
  warn "$WIRE missing"
fi

# --- the gate must prove it can fail ----------------------------------------
# check_wiring.py was itself vacuous in its first version, because the directory it lives
# in was already on sys.path, so every script "passed". This makes the demonstration part
# of every release instead of a thing somebody once did by hand.
if [ -f "$WIRE" ]; then
  if ST=$("$PY" "$WIRE" --self-test 2>&1); then
    ok "check_wiring --self-test: the checker passes a good bootstrap and catches a short one"
  else
    bad "check_wiring --self-test FAILED — the wiring gate cannot be trusted:"
    printf '%s\n' "$ST" | grep -E 'FAIL|->' | head -4 | sed 's/^/         /'
  fi
fi

# --- a shipped input that is present but altered -----------------------------
# paths_config records an MD5 and a byte count per shipped input. The self-check used to
# print its verdict and exit 0 either way; it now exits non-zero, which is what makes it
# usable here. This is the check that would have caught the CRLF hash table.
PC="code/analyses/reproduction_20261002/paths_config.py"
if [ -f "$PC" ]; then
  if "$PY" "$PC" > /dev/null 2>&1; then
    ok "paths_config: every shipped input present and byte-exact"
  else
    bad "paths_config reports a shipped input missing or altered — run: $PY $PC"
  fi
else
  warn "$PC missing"
fi

if [ -f code/analyses/reproduction_min/reproduce_headline.py ]; then
  # This one is a hard check when it can be made: if numpy is present and a reported
  # value no longer reproduces, the release must not go out. Only a missing numpy is
  # a skip, because that is a property of the interpreter, not of the archive.
  if "$PY" -c "import numpy" > /dev/null 2>&1; then
    if "$PY" code/analyses/reproduction_min/reproduce_headline.py > /dev/null 2>&1; then
      ok "reproduction_min reproduces the headline values from data/derived/ alone"
    else
      bad "reproduction_min FAILED under $PY — a reported value no longer reproduces"
    fi
  else
    ok "reproduction_min: skipped, $PY has no numpy (interpreter limitation, not an archive fault)"
  fi
fi

echo
echo "== 5. labelling placeholders =="
PH=$(git ls-files -z 2>/dev/null | xargs -0 grep -l '<CONCEPT>\|<VER>\|PLACEHOLDER' 2>/dev/null | head -10)
[ -z "$PH" ] && ok "no <CONCEPT>/<VER> placeholders left" || { warn "placeholders still present in:"; echo "$PH" | sed 's/^/         /'; }

echo
echo "== 6. DOI registry =="
# The DOI cannot exist yet at pre-flight time: Zenodo mints it from the release this
# script is about to authorise. So an unresolved placeholder is expected here and is a
# warning, NOT a failure — but it must be visible, because the one thing that must not
# happen is a release that claims to be citable while every DOI in the tree is a token.
if [ -f scripts/set_doi.py ]; then
  if "$PY" scripts/set_doi.py --check > /dev/null 2>&1; then
    ok "every DOI carrier resolves to a real identifier"
  else
    warn "DOI is still pending. Publish to Zenodo, then:"
    echo "         python3 scripts/set_doi.py --concept 10.5281/zenodo.<N> \\" | sed 's/^/  /'
    echo "             --version 10.5281/zenodo.<M> --record <url> --release-date <YYYY-MM-DD>" | sed 's/^/  /'
    echo "         See DOI_PENDING.md. Until then do not describe the archive as citable." | sed 's/^/  /'
  fi
else
  warn "scripts/set_doi.py missing — the DOI registry is not checkable"
fi

echo
echo "== 7. container base image is pinned =="
# env/README.md rule 1 requires an exact pin. `FROM ...:latest` is not one. This cannot be
# resolved offline (Docker Hub is unreachable from some repair environments), so it warns
# with the exact command rather than failing the release on an environment-only issue.
FROM_LINE=$(grep -m1 '^FROM' env/Dockerfile 2>/dev/null || true)
case "$FROM_LINE" in
  *:latest*|*"${FROM_LINE%%:*}"|"")
    warn "env/Dockerfile does not pin its base image: ${FROM_LINE:-<no FROM line>}"
    echo "         Resolve a digest and pin:  docker buildx imagetools inspect <image>:<tag>" | sed 's/^/  /'
    echo "         then:  FROM <image>@sha256:<digest>   (keep the readable tag in a comment)" | sed 's/^/  /'
    ;;
  *)
    ok "env/Dockerfile pins a base image: ${FROM_LINE}"
    ;;
esac

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

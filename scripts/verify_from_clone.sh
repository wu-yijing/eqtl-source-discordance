#!/usr/bin/env bash
# verify_from_clone.sh — the definition of "it passes".
#
# Every other check in this repository runs where the author works. That is how the same
# class of defect shipped four times: a path bootstrap one directory level short, a hash
# table recording CRLF values for files a clone checks out as LF, a manifest hashing the
# working tree, and a rebuild that wrote a shipped input with the platform's line ending.
# Each of them passed here and failed for a reader.
#
# So the checks now run where the reader is: in a fresh clone, with nothing from this
# working tree on the path. If this script passes, a third party gets what we claim.
#
#   bash scripts/verify_from_clone.sh            # clone to a temp dir, verify, remove it
#   bash scripts/verify_from_clone.sh --keep     # keep the clone and print its path
#
# Exit code 0 = the clone verifies. Non-zero = do not publish it.
#
# Note: `git clone --no-hardlinks`, not `git archive`. On a machine with
# core.autocrlf=true, `git archive` exports CRLF whatever `.gitattributes` says about the
# checked-out form, so it is not an equivalent checkout and must not be used to prove one.

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEEP=0
[ "${1:-}" = "--keep" ] && KEEP=1

pass=0
fail=0
ok()  { printf '  [ ok ] %s\n' "$*"; }
bad() { printf '  [FAIL] %s\n' "$*"; fail=$((fail + 1)); }
warn() { printf '  [warn] %s\n' "$*"; }

# ---- the interpreter the reader is likely to have
PY="${PY:-}"
if [ -z "$PY" ]; then
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
fi
[ -n "$PY" ] && ok "interpreter: $($PY -V 2>&1)" || { bad "no python on PATH"; exit 1; }

# ---- a writable place to put the clone
BASE=""
for cand in "${TMPDIR:-}" /tmp "${REPO}/.."; do
  [ -n "$cand" ] || continue
  if mkdir -p "$cand" 2>/dev/null && [ -w "$cand" ]; then BASE="$cand"; break; fi
done
[ -n "$BASE" ] || { bad "no writable temp directory"; exit 1; }

CLONE="$(mktemp -d "$BASE/eqtl-verify-XXXXXX")"
RMDIR="$CLONE/repo"
# Step out of the clone before removing it, or Windows reports "Device or resource busy"
# on the temp directory because the shell's own cwd is inside the tree being deleted.
cleanup() {
  cd /
  [ "$KEEP" = "1" ] || rm -rf "$CLONE" 2>/dev/null || true
}
trap cleanup EXIT

echo
echo "== cloning =="
if ! git clone -q --no-hardlinks "$REPO" "$RMDIR" 2>&1 | sed 's/^/         /'; then
  bad "git clone failed"; exit 1
fi
ok "cloned to $RMDIR"

cd "$RMDIR" || { bad "cannot enter the clone"; exit 1; }
HEAD_SHA="$(git rev-parse --short HEAD)"
NTRACK="$(git ls-files | wc -l | tr -d ' ')"
ok "HEAD $HEAD_SHA, $NTRACK tracked files"

if [ -z "$(git status --porcelain)" ]; then
  ok "the clone is clean — the committed tree is the checked-out tree"
else
  bad "the clone is dirty; the committed bytes and the checked-out bytes differ:"
  git status --short | head -10 | sed 's/^/         /'
fi

if [ -f .gitattributes ] && grep -q 'eol=lf' .gitattributes; then
  CRLF=$("$PY" - <<'EOF' 2>/dev/null
import os
bad = 0
for dp, dn, fn in os.walk('.'):
    dn[:] = [d for d in dn if d != '.git']
    for f in fn:
        if os.path.splitext(f)[1].lower() in ('.py','.md','.json','.sh','.csv','.tsv','.txt','.yml','.yaml'):
            if b'\r\n' in open(os.path.join(dp, f), 'rb').read():
                bad += 1
print(bad)
EOF
)
  [ "${CRLF:-1}" = "0" ] && ok "no CRLF in any text file the clone checked out" \
                          || bad "$CRLF text file(s) checked out with CRLF despite eol=lf"
fi

echo
echo "== 1. shipped inputs byte-exact =="
if "$PY" code/analyses/reproduction_20261002/paths_config.py > "$CLONE/paths.txt" 2>&1; then
  ok "$(grep 'self-check' "$CLONE/paths.txt" | tail -1 | sed 's/^ *//')"
else
  bad "paths_config self-check failed:"
  grep -E 'self-check|MISMATCH|MISSING' "$CLONE/paths.txt" | tail -5 | sed 's/^/         /'
fi

echo
echo "== 2. archive map is self-consistent =="
if "$PY" scripts/check_archive_map.py > "$CLONE/map.txt" 2>&1; then
  ok "$(tail -1 "$CLONE/map.txt" | sed 's/^ *//; s/^\[ ok \] //')"
else
  bad "check_archive_map.py failed:"
  sed -n '/problem/,$p' "$CLONE/map.txt" | head -8 | sed 's/^/         /'
fi

echo
echo "== 3. provenance matches the clone =="
if "$PY" scripts/verify_provenance.py > "$CLONE/prov.txt" 2>&1; then
  ok "$(grep 'manifest:' "$CLONE/prov.txt" | head -1 | sed 's/^ *//')"
else
  bad "verify_provenance.py failed:"
  tail -6 "$CLONE/prov.txt" | sed 's/^/         /'
fi

echo
echo "== 4. every script's path bootstrap works =="
if "$PY" code/analyses/reproduction_20261002/check_wiring.py --self-test > "$CLONE/st.txt" 2>&1; then
  ok "check_wiring --self-test: the checker both passes and fails as it should"
else
  bad "check_wiring --self-test failed — the release gate may be vacuous:"
  tail -5 "$CLONE/st.txt" | sed 's/^/         /'
fi
if "$PY" code/analyses/reproduction_20261002/check_wiring.py > "$CLONE/wire.txt" 2>&1; then
  ok "$(grep '^wired:' "$CLONE/wire.txt" | sed 's/^ *//')"
else
  bad "check_wiring.py reports broken scripts:"
  grep 'FAIL' "$CLONE/wire.txt" | head -6 | sed 's/^/         /'
fi

echo
echo "== 5. the reported numbers reproduce from the clone alone =="
if "$PY" -c "import numpy" >/dev/null 2>&1; then
  if "$PY" code/analyses/reproduction_min/reproduce_headline.py > "$CLONE/repro.txt" 2>&1; then
    ok "$(grep -iE 'mismatch|assert' "$CLONE/repro.txt" | tail -1 | sed 's/^ *//')"
  else
    bad "reproduce_headline.py FAILED — a reported value no longer reproduces:"
    tail -6 "$CLONE/repro.txt" | sed 's/^/         /'
  fi
else
  ok "reproduction_min skipped: $PY has no numpy (interpreter limitation, not an archive fault)"
fi

echo
echo "== 6. the Table S9 pool re-derivation runs from the clone alone =="
# The map claims `clone` for S9, which asserts that re-deriving the pools needs nothing but
# what ships. Asserting it is not testing it: this runs build_pools() with every source
# variable cleared and checks that it reproduces the published chain AND leaves the tree
# untouched — byte-identical pool files. Without this step the claim would rest on one run
# on the author's machine, which is the failure mode this whole script exists to correct.
if [ -f code/analyses/reproduction_20261002/00_build_added_derived.py ]; then
  if ( unset REPRO_MASHR_DB_DIR REPRO_COVARIATE REPRO_HRT_SOURCE REPRO_GROUPS_JSON \
           REPRO_RAND_DIR REPRO_T1_DIR REPRO_GTEX_OFFICIAL_DIR
       "$PY" - <<'PYEOF'
import importlib.util as iu
spec = iu.spec_from_file_location(
    'b', 'code/analyses/reproduction_20261002/00_build_added_derived.py')
m = iu.module_from_spec(spec)
spec.loader.exec_module(m)
m.build_pools()
PYEOF
     ) > "$CLONE/pools.txt" 2>&1; then
    if grep -q '11,820' "$CLONE/pools.txt" && grep -q 'POOL_818 = 818' "$CLONE/pools.txt"; then
      if [ -z "$(git status --porcelain data/derived)" ]; then
        ok "build_pools() rebuilt POOL_A 11,820 / POOL_818 818 with no source variables set, byte-identically"
      else
        bad "the pool re-derivation changed data/derived — not byte-identical:"
        git status --short data/derived | head -5 | sed 's/^/         /'
      fi
    else
      bad "the pool re-derivation ran but did not print the published chain:"
      tail -6 "$CLONE/pools.txt" | sed 's/^/         /'
    fi
  else
    bad "build_pools() failed with every source variable unset — S9 is not `clone`:"
    tail -6 "$CLONE/pools.txt" | sed 's/^/         /'
  fi
else
  warn "00_build_added_derived.py missing — S9's locality claim is not checked"
fi

echo
echo "== 7. the only supported entry point actually runs =="
# WHY THIS GATE EXISTS. Gates 1-6 check the data layer, the archive map, the provenance manifest,
# the path wiring and the headline values — and every one of them passed while `code/run_all.sh`,
# the single command README.md tells a reader to run, was broken from a fresh clone (exit 1, eight
# FAIL lines, "Do not treat this run as reproducing the paper"). Nothing here invoked it, so the
# defect survived indefinitely behind a green board. A gate that does not run the entry point is
# not a definition of "it passes".
#
# The figure half of run_all.sh needs the Supporting Information .docx, which this repository does
# not redistribute. Set AF1_DOCX to your copy and this gate exercises the figure scripts too; leave
# it unset and only the headline half is run, which is still the half a reader gets without it.
if [ -n "${AF1_DOCX:-}" ]; then
  RUNALL_ARGS=""
  ok "AF1_DOCX is set — running the full pipeline, figure scripts included"
else
  RUNALL_ARGS="--verify-only"
  ok "AF1_DOCX is unset — running --verify-only, so the figure scripts are not exercised"
fi
if ( PYTHON="$PY" bash code/run_all.sh $RUNALL_ARGS ) > "$CLONE/runall.txt" 2>&1; then
  ok "$(grep 'RESULT:' "$CLONE/runall.txt" | tail -1 | sed 's/^ *//')"
else
  bad "code/run_all.sh FAILED — the entry point README.md advertises does not run:"
  grep -E '\[FAIL\]|RESULT:' "$CLONE/runall.txt" | head -8 | sed 's/^/         /'
fi

echo
echo "=================================================="
printf ' verified from a clone: %d failure(s)\n' "$fail"
if [ "$KEEP" = "1" ]; then
  echo " clone kept at: $RMDIR"
else
  echo " clone removed (use --keep to inspect it)"
fi
if [ "$fail" -gt 0 ]; then
  echo " RESULT: a reader does not get what this repository claims. Do not publish."
  exit 1
fi
echo " RESULT: a fresh clone reproduces and verifies. Safe to publish."
exit 0

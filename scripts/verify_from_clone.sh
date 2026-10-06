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
# Exit 0 does not always mean every check ran. A check whose runtime dependency the
# interpreter lacks (NumPy, Pillow) reports [skip] and is counted in the summary: a run
# with skips is "nothing that ran failed", which is weaker than "everything ran". Read the
# skipped count before quoting a green result.
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
skip=0
ok()   { printf '  [ ok ] %s\n' "$*"; }
bad()  { printf '  [FAIL] %s\n' "$*"; fail=$((fail + 1)); }
warn() { printf '  [warn] %s\n' "$*"; }
# A check that could not be run is neither a pass nor a failure. Folding it into the pass
# count is how a green board grows over an unverified claim; folding it into the failure
# count turns a property of the reader's interpreter into a defect in the archive. It gets
# its own category here, and the summary prints the count, so "verified" never silently
# means "partly verified". This is the same [skip] the pipeline itself prints
# (code/run_all.sh), and the same verdict cut_release.sh gives a missing dependency.
skip() { printf '  [skip] %s\n' "$*"; skip=$((skip + 1)); }

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
  # This used to walk the tree for a fixed set of text extensions and fail on any CRLF.
  # That is too blunt once part of the tree is *deliberately* verbatim: `data/upstream/`
  # ships the official MetaXcan CSV outputs, which are CRLF, and `.gitattributes` marks
  # them `-text` so the recorded hashes stay valid. Ask git instead of guessing —
  # `git ls-files --eol` reports the index eol, the working-tree eol, and the attribute
  # that decided it, so "git intends LF but the checkout is not LF" becomes a precise
  # test rather than an extension list. A `-text` file being CRLF is the point of it.
  EOL_BAD=$(git ls-files --eol | awk '$2 ~ /^w\/(crlf|mixed)$/ && $3 != "attr/-text"' | wc -l | tr -d ' ')
  EOL_VERBATIM=$(git ls-files --eol | awk '$3 == "attr/-text"' | wc -l | tr -d ' ')
  if [ "${EOL_BAD:-1}" = "0" ]; then
    ok "every file git intends as LF is checked out as LF (${EOL_VERBATIM} stored verbatim by design)"
    git ls-files --eol | awk '$2 ~ /^w\/(crlf|mixed)$/' | head -3 | sed 's/^/         verbatim: /'
  else
    bad "$EOL_BAD file(s) checked out with CRLF although .gitattributes asks for LF:"
    git ls-files --eol | awk '$2 ~ /^w\/(crlf|mixed)$/ && $3 != "attr/-text"' | head -10 | sed 's/^/         /'
    echo "         (a recorded SHA-256/MD5 for these would not survive a clone)" | sed 's/^/  /'
  fi
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
# NumPy is the one runtime dependency the data layer has, and gates 5 and 7 both start code
# that imports it. Where the interpreter the reader has cannot import NumPy, that code
# cannot start — a property of the interpreter, not a defect in the archive — so both gates
# *skip* rather than fail. Each prefers $PY, then any other interpreter on PATH, so a reader
# who has NumPy anywhere still gets the real check instead of a skip.
NUMPY_PY=""
for c in "${PY:-}" python3 python; do
  [ -n "$c" ] || continue
  command -v "$c" >/dev/null 2>&1 || continue
  if "$c" -c "import numpy" >/dev/null 2>&1; then NUMPY_PY="$c"; break; fi
done
if [ -n "$NUMPY_PY" ]; then
  if [ "$NUMPY_PY" != "$PY" ]; then
    ok "reproducing with $NUMPY_PY (it has NumPy; \$PY does not)"
  fi
  if "$NUMPY_PY" code/analyses/reproduction_min/reproduce_headline.py > "$CLONE/repro.txt" 2>&1; then
    ok "$(grep -iE 'mismatch|assert' "$CLONE/repro.txt" | tail -1 | sed 's/^ *//')"
  else
    bad "reproduce_headline.py FAILED — a reported value no longer reproduces:"
    tail -6 "$CLONE/repro.txt" | sed 's/^/         /'
  fi

  # SI Table S6 carries a second kind of reported value: the "ACAT-O combined P" column,
  # which is *derived* rather than read off a run, and whose combination rule was only
  # settled on 2026-10-03. A rule stated in prose is not a verified rule — and the wrong
  # rule here looks plausible (the unweighted Cauchy combination reproduces 68 of 87 cells,
  # which reads like "mostly right"). This re-derives all 87 from
  # data/derived/hk_official_Z.csv and exits non-zero if a single one disagrees with the
  # published three-significant-figure value, so the gate carries the claim.
  if [ -f code/analyses/reproduction_20261002/scripts/recompute_acat_o.py ]; then
    if "$NUMPY_PY" code/analyses/reproduction_20261002/scripts/recompute_acat_o.py > "$CLONE/acat.txt" 2>&1; then
      ok "$(grep -i 'reproduced' "$CLONE/acat.txt" | tail -1 | sed 's/^ *//')"
    else
      bad "recompute_acat_o.py FAILED — the SI Table S6 ACAT-O column no longer reproduces:"
      tail -8 "$CLONE/acat.txt" | sed 's/^/         /'
    fi
  fi
else
  skip "reproduction_min and the ACAT-O re-derivation were not run: no interpreter on PATH can import NumPy (interpreter limitation, not an archive fault)"
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
if [ -n "$NUMPY_PY" ]; then
  if ( PYTHON="$NUMPY_PY" bash code/run_all.sh $RUNALL_ARGS ) > "$CLONE/runall.txt" 2>&1; then
    ok "$(grep 'RESULT:' "$CLONE/runall.txt" | tail -1 | sed 's/^ *//')"
  else
    bad "code/run_all.sh FAILED — the entry point README.md advertises does not run:"
    grep -E '\[FAIL\]|RESULT:' "$CLONE/runall.txt" | head -8 | sed 's/^/         /'
  fi
else
  # run_all.sh cannot start without NumPy: its headline half imports it. Skipping is the
  # right verdict — the same one gate 5 reaches on the same missing dependency — but a gate
  # that only skips is a gate that cannot fail, and this repository has already shipped one
  # defect behind exactly that. So it still does the two things that need no interpreter:
  # the advertised entry point must parse, and every script it names must be in the tree.
  if bash -n code/run_all.sh 2> "$CLONE/runall_syn.txt"; then
    ok "code/run_all.sh parses under bash -n (execution skipped: no NumPy on PATH)"
  else
    bad "code/run_all.sh does not parse — the advertised entry point is syntactically broken:"
    head -5 "$CLONE/runall_syn.txt" | sed 's/^/         /'
  fi
  RUNALL_REFS=$(grep -v '^[[:space:]]*#' code/run_all.sh | grep -oE '[A-Za-z0-9_]+\.py' | sort -u)
  RUNALL_NREFS=$(printf '%s\n' $RUNALL_REFS | sed '/^$/d' | wc -l | tr -d ' ')
  REF_MISSING=""
  for b in $RUNALL_REFS; do
    git ls-files | grep -qE "(^|/)$b$" || REF_MISSING="$REF_MISSING $b"
  done
  if [ -z "$REF_MISSING" ]; then
    ok "code/run_all.sh names $RUNALL_NREFS script(s), all present in the tree"
  else
    bad "code/run_all.sh names script(s) absent from the tree:$REF_MISSING"
  fi
  skip "code/run_all.sh was not executed: no interpreter on PATH can import NumPy (interpreter limitation, not an archive fault)"
fi

echo
echo "== 8. the published SI rasters reproduce, pixel for pixel =="
# WHY THIS GATE EXISTS. `metadata/ARCHIVE_MAP.md`, `figures/README.md` and
# `code/figures/ge_si/README.md` now claim that the rasters embedded in the submitted
# Supporting Information are reproducible at *artefact* level: the published pixel content,
# plus the 2026-10-01 edits that connect it to the pre-patch versions. A claim about
# reproducibility is worth exactly what a reader can re-run, so this gate re-runs it.
# `verify_published.py` checks the four SHA-256, re-applies both edits, and requires zero
# differing pixels — it also restates the changed-pixel counts and bounding boxes against
# the recorded 17,589 px (Fig. S1) and 10,587 px (Fig. S3), so the archive cannot silently
# drift from what it says it ships.
#
# It needs Pillow and NumPy; the Fig. S1 edit additionally needs Arial, because that is the
# family the published glyphs were drawn in. Where those are missing this gate *warns*
# rather than fails — a font absent from the reader's machine says nothing about the
# archive. Run it directly with:
#     cd code/figures/ge_si/published && python3 verify_published.py
PUB_PY=""
for c in "$PY" python3 python; do
  [ -n "$c" ] || continue
  command -v "$c" >/dev/null 2>&1 || continue
  if "$c" -c "import numpy, PIL" >/dev/null 2>&1; then PUB_PY="$c"; break; fi
done
if [ -z "$PUB_PY" ]; then
  skip "no interpreter with Pillow + NumPy on PATH (tried \$PY, python3, python) — the published-raster check was not run"
else
  ok "published-raster check: $PUB_PY"
  if ( cd code/figures/ge_si/published && "$PUB_PY" verify_published.py ) > "$CLONE/pub.txt" 2>&1; then
    ok "$(tail -1 "$CLONE/pub.txt")"
    grep -E 'edit size|pixel-identical' "$CLONE/pub.txt" | sed 's/^ */         /'
  elif grep -q 'Arial not found' "$CLONE/pub.txt"; then
    warn "Arial is absent, so the Fig. S1 glyph re-draw could not be checked here; the checks that do not need it still ran:"
    grep -E '^  (ok|FAIL)' "$CLONE/pub.txt" | head -6 | sed 's/^/         /'
  else
    bad "verify_published.py FAILED — the published rasters do not reproduce from a clone:"
    grep -E '^  FAIL|FAILED' "$CLONE/pub.txt" | head -8 | sed 's/^/         /'
  fi
fi

echo "== 9. the shipped upstream artefacts hash to what the archive claims =="
# WHY THIS GATE EXISTS. `data/upstream/` ships the as-produced middleware so a reader can check
# the Z layer's provenance without the ~4.7 GB of third-party inputs. Some of those artefacts are
# CRLF — the official MetaXcan CSV outputs are — and `.gitattributes` would happily normalise them
# to LF, which changes every byte of the file and makes every recorded hash wrong. That is exactly
# the failure this archive has already hit once, recorded against `data/external/SHA256SUMS`
# ("11 of the shipped inputs reported MD5 MISMATCH"). `.gitattributes` sets `data/upstream/** -text`
# to prevent it, but a claim about checked-out bytes can only be settled by hashing checked-out
# bytes — which is what running this inside a clone does.
if [ -f code/upstream/verify_middleware.py ] && [ -d data/upstream ]; then
  if "$PY" code/upstream/verify_middleware.py --run-dir data/upstream > "$CLONE/mw.txt" 2>&1; then
    ok "$(grep -E '^identical' "$CLONE/mw.txt" | sed 's/^ *//')"
  else
    bad "the shipped middleware does not hash to the recorded values — the checked-out bytes differ from the bytes they were hashed as:"
    grep -E 'DIFFERS|expected|got' "$CLONE/mw.txt" | head -8 | sed 's/^/         /'
  fi
else
  bad "code/upstream/verify_middleware.py or data/upstream/ is missing"
fi

echo "== 10. the two external-input manifests name the same files =="
# WHY THIS GATE EXISTS. `data/external/SHA256SUMS` says which bytes, `data/external/SOURCES.tsv`
# says where to get them. Both are hand-maintained, so they can drift: add an input to one and
# forget the other, and a reader either downloads a file nobody hashed, or is handed a hash for a
# file with no source. `fetch_external_inputs.py` refuses to run in that state — this gate is what
# makes the refusal visible at release time instead of on the reader's first attempt. It touches
# no network, so it is safe inside a clone.
if [ -f scripts/fetch_external_inputs.py ] && [ -f data/external/SOURCES.tsv ]; then
  if "$PY" scripts/fetch_external_inputs.py --check-manifests > "$CLONE/mf.txt" 2>&1; then
    ok "$(grep -E '^manifests' "$CLONE/mf.txt" | sed 's/^ *//') — same file set in both"
  else
    bad "data/external/SOURCES.tsv and data/external/SHA256SUMS disagree:"
    grep -E '\[FAIL\]' "$CLONE/mf.txt" | head -6 | sed 's/^/         /'
  fi
else
  bad "scripts/fetch_external_inputs.py or data/external/SOURCES.tsv is missing"
fi

echo "== 11. no tracked file is empty =="
# WHY THIS GATE EXISTS. A zero-byte file passes every check this archive had: it hashes, it
# verifies, its byte count matches the manifest, and the path bootstrap never opens it. That is
# not hypothetical — on 2026-10-04 a normaliser opened three evidence files with "wb" before
# reading them, which truncates, and MANIFEST.sha256 and provenance.json were then regenerated
# over the emptied results and reported a clean board. A hash proves a file is *unchanged*; it
# cannot prove the file says anything. This gate can only fail in one direction, which is the
# point. No tracked path is a placeholder today, so there is no allowlist.
# NB: the clone lives at $RMDIR (= $CLONE/repo), not at $CLONE. The first version of this
# gate wrote `cd "$CLONE"`, which is the temp parent and not a repository — `git ls-files`
# returned nothing and the gate passed over an empty file set. Found by printing the file
# count: a checker that reports "(0 files)" is not checking anything.
EMPTY="$(cd "$RMDIR" && git ls-files -z | while IFS= read -r -d '' f; do [ -s "$f" ] || printf '%s\n' "$f"; done)"
if [ -z "$EMPTY" ]; then
  ok "every tracked file has content ($(cd "$RMDIR" && git ls-files | wc -l | tr -d ' ') files)"
else
  bad "tracked file(s) with zero bytes — a hash cannot tell an empty file from a full one:"
  printf '%s\n' "$EMPTY" | head -8 | sed 's/^/         /'
fi

echo
echo "== 12. the SI Table S4 / S26 R path runs from the clone =="
# WHY THIS GATE EXISTS. Every gate above is Python. SI Table S4 — and Table S26, which
# is a function of its pairing — is produced in R under env/renv.lock, and until
# 2026-10-05 nothing here touched R: this script named R, Rscript, renv and MatchIt
# zero times, so "the R side restores from renv.lock" was asserted in prose and checked
# nowhere, and the shipped `code/analyses/run_mahalanobis_matching.R` did not run under
# `Rscript` at all. This gate runs the supported generator
# (`code/analyses/emit_S4_table.R`) and asserts the one load-bearing claim: it returns
# the archived control set, 30 of 30.
#
# Verdict policy, the same as gates 5, 7 and 8: R and MatchIt belong to the reader, not
# the archive. Where Rscript is absent, or MatchIt does not load, the gate *skips*.
# Where it runs it must return 30/30 or it *fails*. The MatchIt version is printed but
# not enforced — the archived control set is identical under 4.5.5 and 4.7.2 (30/30 rows
# of match.matrix; see docs/audit_notes/s4_matchit_version_test_20261004/), so a reader
# holding 4.7.2 is not holding a different result. Set $RSCRIPT to pick an interpreter;
# set $PRELIB (read by the generator) to prepend the pinned library.
RSCRIPT="${RSCRIPT:-}"
if [ -z "$RSCRIPT" ]; then
  for c in Rscript R; do
    if command -v "$c" >/dev/null 2>&1; then RSCRIPT="$c"; break; fi
  done
fi
if [ -z "$RSCRIPT" ]; then
  skip "the SI Table S4 R path was not run: no Rscript on PATH (interpreter limitation, not an archive fault)"
elif ! "$RSCRIPT" --vanilla -e 'suppressMessages(library(MatchIt))' >/dev/null 2>&1; then
  skip "the SI Table S4 R path was not run: Rscript is present but MatchIt does not load (install it, or point \$RSCRIPT at an interpreter that has it)"
else
  PIN_MIT=$(awk '/"MatchIt"/{f=1} f&&/"Version"/{gsub(/[^0-9.]/,"");print;exit}' env/renv.lock)
  GOT_MIT=$("$RSCRIPT" --vanilla -e 'cat(as.character(packageVersion("MatchIt")))' 2>/dev/null | tr -d '\r')
  if [ -n "$PIN_MIT" ] && [ "$GOT_MIT" = "$PIN_MIT" ]; then
    ok "MatchIt $GOT_MIT matches env/renv.lock"
  else
    warn "MatchIt $GOT_MIT differs from env/renv.lock's $PIN_MIT — informational: the S4 control set is measured identical under both, see s4_matchit_version_test_20261004/"
  fi
  mkdir -p "$CLONE/s4_r_out"
  if "$RSCRIPT" --vanilla code/analyses/emit_S4_table.R "$RMDIR" "$CLONE/s4_r_out" > "$CLONE/s4_r.txt" 2>&1; then
    if grep -q 'candidate SET vs submitted : TRUE' "$CLONE/s4_r.txt" \
       && grep -q 'control   SET vs submitted : 30 / 30' "$CLONE/s4_r.txt"; then
      ok "emit_S4_table.R returns the archived control set (30 / 30; candidate set TRUE)"
      grep -E 'imputation reproduces|matched pairs:' "$CLONE/s4_r.txt" | sed 's/^ */         /'
    else
      bad "emit_S4_table.R ran but did not return the archived control set:"
      grep -E 'control +SET vs submitted|candidate SET vs submitted|Error' "$CLONE/s4_r.txt" | head -6 | sed 's/^/         /'
    fi
  else
    bad "emit_S4_table.R FAILED — the SI Table S4 R path does not run from a clone:"
    tail -8 "$CLONE/s4_r.txt" | sed 's/^/         /'
  fi
fi

echo
echo "== 13. every audit note's MANIFEST.sha256 describes the tree it ships with =="
# WHY THIS GATE EXISTS. Every `docs/audit_notes/*/` note ships a `MANIFEST.sha256` hashing its own
# files, and until 2026-10-05 **no gate read any of them**. Three had silently drifted (READMEs
# edited after the manifest was generated; `.log` files hashed as CRLF before `.gitattributes`
# normalised them), and a fourth was wrong from the moment it was written — a 2026-10-05 "repair"
# edited its own note after computing that note's row and committed both together. Every one of
# those was found by hand, during unrelated work; none by a check. A digest nobody verifies records
# intent, not state.
#
# The directory must also *have* a manifest: an audit note whose contents are unregistered is not a
# checkable record. That requirement is what surfaced `r2_notes_closure_20261004/`, the one note
# that had never registered itself.
#
# The checker's own self-test runs first, for the reason gate 4 states: a gate that cannot fail is
# not a gate, and this repository has already shipped one defect behind exactly that.
if [ -f scripts/check_audit_manifests.py ]; then
  if "$PY" scripts/check_audit_manifests.py --self-test > "$CLONE/man_st.txt" 2>&1; then
    ok "check_audit_manifests --self-test: the checker both passes and fails as it should"
  else
    bad "check_audit_manifests --self-test failed — the release gate may be vacuous:"
    tail -5 "$CLONE/man_st.txt" | sed 's/^/         /'
  fi
  if "$PY" scripts/check_audit_manifests.py > "$CLONE/man.txt" 2>&1; then
    ok "$(grep '^checked' "$CLONE/man.txt" | sed 's/^ *//')"
  else
    bad "an audit note's MANIFEST.sha256 does not describe the tree that ships:"
    grep 'FAIL' "$CLONE/man.txt" | head -6 | sed 's/^/         /'
  fi
else
  bad "scripts/check_audit_manifests.py is missing — the audit manifests are unchecked"
fi

echo
echo "== 14. the four manuscript main figures rebuild byte-identically =="
# WHY THIS GATE EXISTS. Every gate above covers a number, a table, or a figure that
# `code/run_all.sh` produces. The four figures submitted to *Genetic Epidemiology* are a
# different set: they come from `code/figures/ge_main/`, they are not written by
# `run_all.sh`, and — as gate 7 itself says when it runs `--verify-only` — the figure
# step is not exercised there either. So the single most visible artefact in the paper,
# and the only one a reviewer looks at before reading anything, sat outside every gate:
# "Fig. 1-4 are byte-identical to the submitted PNGs" was a claim in
# `code/figures/ge_main/README.md`, verified by hand on 2026-10-03 and by nothing since.
#
# This gate runs it. Verdict policy, the same as gates 5, 7, 8 and 12: matplotlib and
# Pillow belong to the reader, not the archive. Where they are absent the gate *skips*;
# where it runs, all four PNGs must match or it *fails*.
#
# 2026-10-07 — Figure 4 additionally needs the submitted Supporting Information, because
# unified_fig4.py reads two of the numbers it plots out of Note S4, and that document is the
# journal's: it is not redistributed here and `manuscript/` does not exist in a clone. So
# the gate passes $SI_DOCX/$AF1_DOCX through when the caller has one, and where it does not,
# it requires the three figures it *can* check and records the fourth as a skip by name —
# never as a pass, and not as a failure either, since nothing about the archive is in doubt.
FIG_PY="${NUMPY_PY:-$PY}"
GE_SI="${SI_DOCX:-${AF1_DOCX:-}}"
if [ -z "$FIG_PY" ] || ! "$FIG_PY" -c "import numpy, scipy, matplotlib, PIL" >/dev/null 2>&1; then
  skip "the four main figures were not rebuilt: no interpreter with NumPy + SciPy + matplotlib + Pillow on PATH (set \$PY to one that has them)"
else
  mkdir -p "$CLONE/ge_main_out"
  ( cd "$CLONE/repo" && GE_MAIN_OUT="$CLONE/ge_main_out" PYTHON="$FIG_PY" SI_DOCX="$GE_SI" \
      bash code/figures/ge_main/reproduce.sh ) > "$CLONE/ge_main.txt" 2>&1
  n=$(grep -c 'identical to the submitted figure' "$CLONE/ge_main.txt")
  if [ "$n" -eq 4 ]; then
    ok "ge_main/reproduce.sh: all four main figures (Fig. 1-4) reproduce byte-identically"
    grep 'identical to the submitted figure' "$CLONE/ge_main.txt" | sed 's/^ */         /'
  elif [ "$n" -eq 3 ] && grep -q 'Figure 4 is NOT VERIFIED' "$CLONE/ge_main.txt"; then
    ok "ge_main/reproduce.sh: Fig. 1-3 reproduce byte-identically"
    grep 'identical to the submitted figure' "$CLONE/ge_main.txt" | sed 's/^ */         /'
    skip "Figure 4 was NOT verified: no Supporting Information supplied (set \$SI_DOCX or \$AF1_DOCX, or place manuscript/Supporting_Information.docx). unified_fig4.py reads two of its numbers from the SI's Note S4."
  else
    bad "ge_main/reproduce.sh: only $n of 4 figures matched the submitted PNGs:"
    grep -E 'FAIL|differ|NOT VERIFIED' "$CLONE/ge_main.txt" | head -8 | sed 's/^/         /'
  fi
fi

echo
echo "=================================================="
printf ' verified from a clone: %d failure(s), %d check(s) skipped\n' "$fail" "$skip"
if [ "$skip" -gt 0 ]; then
  echo " A skipped check is not a passed check: it needs something this environment does"
  echo " not have — a Python dependency (NumPy, Pillow, matplotlib), or the journal's"
  echo " Supporting Information, which Figure 4 reads two numbers from and which this"
  echo " archive does not redistribute. Each skip above names its own cause and its fix."
  echo " Until you supply it, the claims those checks carry are unverified for you,"
  echo " whatever the failure count says."
fi
if [ "$KEEP" = "1" ]; then
  echo " clone kept at: $RMDIR"
else
  echo " clone removed (use --keep to inspect it)"
fi
if [ "$fail" -gt 0 ]; then
  echo " RESULT: a reader does not get what this repository claims. Do not publish."
  exit 1
fi
if [ "$skip" -gt 0 ]; then
  echo " RESULT: every check that could run passed; $skip could not run here. Not a full verification."
else
  echo " RESULT: a fresh clone reproduces and verifies. Safe to publish."
fi
exit 0

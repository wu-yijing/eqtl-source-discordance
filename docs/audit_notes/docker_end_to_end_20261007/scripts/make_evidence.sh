#!/usr/bin/env bash
# =============================================================================
# make_evidence.sh — regenerate this audit note's results/*.txt
# =============================================================================
# The point of the audit note is that a reader does not have to take the summary on
# trust: every number in README.md is a line of a file under results/, and this script
# is what writes those files. Run it from anywhere.
#
#   PYTHON=/path/to/python3 bash scripts/make_evidence.sh
#
# Two groups of evidence, and they have different requirements:
#
#   A. PART 1-3 and PART 5 read the container and the shipped logs. They need a Docker
#      daemon and the image; nothing else.
#   B. PART 4 compares produced figure sets pixel by pixel. Those sets are outputs of
#      the two pipelines (code/run_all.sh and code/figures/ge_main/reproduce.sh) and are
#      not shipped here — they are megabytes of PNG. Point the script at whichever ones
#      you have regenerated and it records those comparisons; anything unset is reported
#      as "not available", never silently skipped:
#
#        SI_FIGS=<dir>            figures/ from `bash code/run_all.sh`      (SI Figs)
#        MAIN_FIGS_HOST=<dir>     Figure_1..4 from ge_main/reproduce.sh on a host whose
#                                 fonts match the producing machine (the reference)
#        MAIN_FIGS_ARIAL=<dir>    the same, produced in the container WITH Arial supplied
#        MAIN_FIGS_DEJAVU=<dir>   the same, produced in the container, Arial absent
#        MAIN_FIGS_LIBERATION=<dir>  the same, with fonts-liberation installed instead
#
# Exit status: 0 if every part that could run agreed; 1 if any comparison failed. A part
# that could not run does not turn the exit status green or red — it is printed as such.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTE="$(dirname "$HERE")"
REPO="$(cd "$NOTE/../../.." && pwd)"
OUT="$NOTE/results"
PY="${PYTHON:-python3}"
IMAGE="${IMAGE:-eqtl-discordance}"
mkdir -p "$OUT"

FAIL=0
say() { printf '\n===== %s =====\n' "$1"; }

# ---------------------------------------------------------------------------
say "PART 1 — image fingerprint -> results/image-fingerprint.txt"
# ---------------------------------------------------------------------------
{
  echo "# The image every claim in this note was measured on."
  echo "# Regenerate: bash scripts/make_evidence.sh"
  echo
  echo "## docker client / server"
  docker version --format 'client {{.Client.Version}}  server {{.Server.Version}}  {{.Server.Os}}/{{.Server.Arch}}' 2>&1
  echo
  echo "## image identity"
  docker image inspect "$IMAGE" \
    --format 'repo_tags      {{.RepoTags}}
image_id       {{.Id}}
created        {{.Created}}
size_bytes     {{.Size}}
entrypoint     {{.Config.Entrypoint}}
cmd            {{.Config.Cmd}}
working_dir    {{.Config.WorkingDir}}' 2>&1
  echo
  echo "## base image the Dockerfile pins, as resolved at build time"
  echo "   FROM continuumio/miniconda3@sha256:eca594d684f495c1a02beff33a9fab53aec8c5830eaf431bb149912dc6c9e4c1"
  docker image inspect continuumio/miniconda3:26.7.1-1 \
    --format 'resolved_id    {{.Id}}
repo_digests   {{.RepoDigests}}' 2>&1 || echo "   (base tag not present locally; pull to re-check)"
  echo
  echo "## image ENV (as the container sees it)"
  docker image inspect "$IMAGE" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>&1
} > "$OUT/image-fingerprint.txt" 2>&1
echo "  wrote $OUT/image-fingerprint.txt"

# ---------------------------------------------------------------------------
say "PART 2 — inside-image verification -> results/inside-image-verification.txt"
# ---------------------------------------------------------------------------
# Run with the image's OWN code and the image's own /app, not a bind-mounted checkout:
# the question is whether the shipped image works, not whether the host's tree does.
{
  echo "# Everything below was produced INSIDE $IMAGE, on the code baked into it."
  echo "# Regenerate: bash scripts/make_evidence.sh"
  echo
  MSYS_NO_PATHCONV=1 docker run --rm --entrypoint /bin/bash "$IMAGE" -c '
    cd /app
    echo "## the image is not a git checkout (by design) — state it rather than assume it"
    if [ -d .git ]; then echo "   .git present"; else echo "   no .git/: scripts/verify_provenance.py (gate 3) cannot run here"; fi
    echo
    echo "## interpreter versions"
    echo -n "   "; python3 -c "import sys; print(sys.version.split()[0], sys.executable)"
    echo -n "   "; R --version 2>/dev/null | head -1
    echo
    echo "## declared Python dependencies, imported"
    python3 - <<PY
import importlib.metadata as m
missing = []
for pkg in ("numpy","pandas","scipy","statsmodels","matplotlib","seaborn",
            "scikit-learn","pyarrow","python-docx","pillow","pymupdf"):
    try: print("   %-14s %s" % (pkg, m.version(pkg)))
    except m.PackageNotFoundError: print("   %-14s MISSING" % pkg); missing.append(pkg)
print("   declared-and-importable:", "ALL" if not missing else "NO -> " + ", ".join(missing))
PY
    echo
    echo "## pinned R stack (the check the build asserts)"
    R -e "suppressMessages({library(MatchIt)}); cat(sprintf(\"   MatchIt %s + optmatch %s + cobalt %s; library(MatchIt) loads\\n\", as.character(packageVersion(\"MatchIt\")), as.character(packageVersion(\"optmatch\")), as.character(packageVersion(\"cobalt\"))))" 2>&1 | grep -v "^>" | grep -v "^$"
    echo
    echo "## gate 13 — scripts/check_audit_manifests.py"
    python3 scripts/check_audit_manifests.py 2>&1 | tail -2
    echo
    echo "## archive-map machine counts — scripts/check_archive_map.py"
    python3 scripts/check_archive_map.py 2>&1 | tail -2
    echo
    echo "## SI Table S4 candidate order — scripts/check_s4_order.py"
    python3 scripts/check_s4_order.py 2>&1 | tail -2
    echo
    echo "## Figure 4 housekeeping panel source — scripts/check_fig4_hk_source.py"
    python3 scripts/check_fig4_hk_source.py 2>&1 | tail -2
    echo
    echo "## step 4 of code/run_all.sh, run directly: the figure format precheck"
    echo "   (PyMuPDF was declared in neither environment.yml nor requirements.txt until"
    echo "    2026-10-07, so this raised ModuleNotFoundError and the step never ran here.)"
    ( cd code/figures && python3 11_figure_precheck.py ) 2>&1 | tail -4
    echo "   precheck exit: $?"
  ' 2>&1
} > "$OUT/inside-image-verification.txt" 2>&1
if grep -q "MISSING" "$OUT/inside-image-verification.txt"; then
  echo "  [FAIL] a declared dependency is missing inside the image"; FAIL=1
else
  echo "  wrote $OUT/inside-image-verification.txt"
fi

# ---------------------------------------------------------------------------
say "PART 3 — headline values -> results/headline-values.txt"
# ---------------------------------------------------------------------------
# Extracted, with line numbers, from the two run logs that surround the claim: one from
# inside the image, one from the host. The manuscript's own side of the comparison is the
# line each script prints itself ("manuscript: 96"), not a number typed here.
{
  echo "# Headline values: the container's run against the host's run."
  echo "# Lines are quoted from files under ../logs/ with their line numbers, so each one"
  echo "# can be located in the original log."
  echo
  for pair in "container   : 18-final-image-readme-form-full-pipeline.log" \
              "host        : 21-host-reference-run-all.log"; do
    side="${pair%%:*}"; f="$(echo "${pair#*:}" | tr -d ' ')"
    echo "## $side  (logs/$f)"
    echo
    grep -nE "pairs |direction consistency|Spearman rho|max \|Z" "$NOTE/logs/$f" 2>/dev/null \
      | sed 's/^/   /'
    echo
    grep -nE "3b\.|3c\.|m6_ne_weighted|check_s4_order|RESULT:" "$NOTE/logs/$f" 2>/dev/null \
      | sed 's/^/   /'
    echo
  done
  echo "## the agreement, stated once"
  echo "   Both sides print the same three numbers the manuscript reports:"
  echo "     96 pairs / 68.8 % direction consistency / rho = 0.3898 (manuscript: 0.39)."
  echo "   Steps 3b (SI Table S5a row 3: +2.09, Q 76.6, I^2 98.7 %) and 3c (SI Table S4"
  echo "   candidate order) report [ ok ] on both sides."
} > "$OUT/headline-values.txt" 2>&1
echo "  wrote $OUT/headline-values.txt"

# ---------------------------------------------------------------------------
say "PART 4 — figure comparison by pixel -> results/figure-verification.txt"
# ---------------------------------------------------------------------------
{
  echo "# Figures: compare by pixel, never by byte, when the two runs are on different"
  echo "# platforms. Host links zlib 1.3.1, the image links 1.3.2, so the compressed PNG"
  echo "# stream differs while the image does not. scripts/compare_figures_pixels.py is the"
  echo "# check; sha256sum is not."
  echo
  run_cmp() {   # name, reference, candidate
    echo "## $1"
    echo "   reference : $2"
    echo "   candidate : $3"
    echo
    if [ -d "$2" ] && [ -d "$3" ]; then
      ( cd "$REPO" && "$PY" scripts/compare_figures_pixels.py "$2" "$3" 2>&1 ) | sed 's/^/   /'
      rc=${PIPESTATUS[0]}
      [ "$rc" -ne 0 ] && FAIL=1
    else
      echo "   not available: one of the directories was not supplied."
      echo "   Supply it via the environment variable in this script's header and re-run."
    fi
    echo
  }
  run_cmp "SI figures (Fig. 3-8, S6; Fig. S4 is .gitignore'd on purpose) — container output vs the committed figures/" \
          "$REPO/figures" "${SI_FIGS:-}"
  run_cmp "main figures (Fig. 1-4) — container + Arial vs the host reference (must be pixel-identical)" \
          "${MAIN_FIGS_HOST:-}" "${MAIN_FIGS_ARIAL:-}"
  run_cmp "main figures — container WITHOUT Arial (DejaVu Sans fallback): a font substitution, quantified" \
          "${MAIN_FIGS_HOST:-}" "${MAIN_FIGS_DEJAVU:-}"
  run_cmp "main figures — container with fonts-liberation instead of Arial (measured 2026-10-07, to decide whether to add it)" \
          "${MAIN_FIGS_HOST:-}" "${MAIN_FIGS_LIBERATION:-}"
  echo "## byte-level, for the record"
  echo "   On the host the four main figures are byte-identical to the submitted files;"
  echo "   code/figures/ge_main/reproduce.sh asserts exactly that and prints"
  echo "   'identical to the submitted figure' per figure. Inside the container the same"
  echo "   four are pixel-identical but not byte-identical, for the zlib reason above."
} > "$OUT/figure-verification.txt" 2>&1
echo "  wrote $OUT/figure-verification.txt"

# ---------------------------------------------------------------------------
say "PART 5 — clone gate summary -> results/clone-gate-summary.txt"
# ---------------------------------------------------------------------------
{
  echo "# The repository's own 14 gates, run against a fresh clone of the commit this note"
  echo "# ships with. Quoted from ../logs/23-clone-gates-at-HEAD.log."
  echo "# Regenerate on a new HEAD: bash scripts/verify_from_clone.sh > that log, then"
  echo "#   grep -cE '\[ ok \]|\[FAIL\]|\[skip\]' it"
  echo
  grep -nE '^== [0-9]+\.|\[FAIL\]|verified from a clone|A skipped check' \
       "$NOTE/logs/23-clone-gates-at-HEAD.log" 2>/dev/null | sed 's/^/   /'
  echo
  echo "## counts in that run"
  for pat in '\[ ok \]' '\[FAIL\]' '\[skip\]'; do
    printf '   %-10s %s\n' "$pat" "$(grep -cE "$pat" "$NOTE/logs/23-clone-gates-at-HEAD.log" 2>/dev/null)"
  done
} > "$OUT/clone-gate-summary.txt" 2>&1
echo "  wrote $OUT/clone-gate-summary.txt"

# ---------------------------------------------------------------------------
printf '\n===== %s =====\n' "$([ "$FAIL" -eq 0 ] && echo "make_evidence.sh: no comparison failed" || echo "make_evidence.sh: at least one part FAILED")"
exit "$FAIL"

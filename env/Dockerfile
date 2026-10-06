# =============================================================================
# Dockerfile — eQTL-source discordance in TWAS: reproducibility environment
# =============================================================================
# Purpose: reproduce every reported downstream value and every figure from the
#          processed data layer shipped in this repository.
#
# Build and run (from the repository root — the build context matters, see the
# COPY paths below):
#   docker build -t eqtl-discordance -f env/Dockerfile .
#   docker run --rm -v "$PWD/figures:/app/figures" eqtl-discordance
#
# ⚠️ 2026-10-03 — this file could not build. Four path/ordering defects were fixed
#    here; each one is commented in place:
#      1. `COPY environment.yml` — the file lives at `env/environment.yml` and the
#         build context is the repository root, so the COPY had no source.
#      2. `chmod +x /app/run_all.sh` — the scripts live at `code/`, not at the root.
#         The `2>/dev/null || true` swallowed the failure, so it went unnoticed.
#      3. `ENTRYPOINT ["/bin/bash", "/app/run_all.sh"]` — that path never existed.
#      4. `renv::snapshot(lockfile='/app/renv.lock')` ran before `WORKDIR /app`, so
#         /app did not exist yet; had it succeeded it would have overwritten the
#         shipped `env/renv.lock` with a machine-local snapshot. The R layer now
#         *restores* from the shipped lock instead of writing a new one.
#    Also fixed: `apt-get install r-base-core=4.5.2-1` had no candidate — this base
#    image is Debian bookworm, whose R is 4.2.x — so apt failed before the conda
#    step was reached. R now comes from conda-forge, where the pin does resolve.
#
#    CLOSED 2026-10-03: the base image is now pinned by digest.
#
#    hub.docker.com and registry.hub.docker.com are still unreachable from this
#    environment, so `docker buildx imagetools inspect` could not be used. The digest
#    below was therefore resolved through a reachable Docker Hub mirror
#    (docker.1panel.live, an OCI-distribution proxy) and then verified independently of
#    that request:
#      * `:latest` and the dated tag `26.7.1-1` return the same index digest, so the
#        readable tag is recorded as the comment on the FROM line;
#      * the index was re-fetched *by digest* and its bytes hashed locally — the local
#        SHA-256 equals the digest the registry reported (content-addressed round-trip);
#      * the linux/amd64 child manifest was then fetched by its own digest and again
#        hashed locally to the same value, and its config + 4 layers resolve
#        (320,420,972 bytes), so the digest names a real, pullable image;
#      * neighbouring tags return *different* digests (26.5.3 -> 1808b31e…,
#        26.3.2-2 -> a297bed7…, 26.1.1-1 -> b0024730…, v25.11.1 -> 5df7c31c…), which is
#        the sanity check that the tag-to-digest mapping is genuine rather than constant.
#    Re-verify with `scripts/cut_release.sh` section 7, which now checks this pin.
#
# ✅ 2026-10-06 — THE IMAGE HAS NOW BEEN BUILT, and this is what that first build found
#    and what it proved. Before this date the file had never been built; it could not be.
#
#    Build-fatal:   (a) the pinned tag was a trailing comment on the FROM line — BuildKit
#                   refuses the file at parse time, so the build never reached the pull;
#                   (b) no C/C++ toolchain, although renv compiles Rcpp, RcppArmadillo,
#                   cobalt, MatchIt and optmatch from source.
#    Also fixed:    (c) renv's transactional install rolled back the twenty packages that
#                   HAD built when restore() stopped at optmatch, leaving the patched
#                   optmatch build with no dependencies — the two-step remedy was
#                   collapsing back into a one-step failure; (d) *.log excluded, which
#                   broke scripts/check_audit_manifests.py (gate 13) inside the image;
#                   (e) a Stage-2 header that implied S-PrediXcan runs here, which it
#                   cannot (Python 3.13 + numpy 2.4.4 vs MetaXcan 0.8.1's numpy 1.x).
#
#    MEASURED, on Docker Desktop 29.8.2 (linux/amd64), after those fixes:
#      * `docker build -t eqtl-discordance -f env/Dockerfile .`   ->  EXIT=0, image 3.74 GB;
#      * the Calloc/Free failure was reproduced for the first time —
#            map.cc:181:3: error: 'Free' was not declared in this scope; did you mean 'free'?
#            ERROR: compilation failed for package 'optmatch'
#        — and then the patch step reports `* DONE (optmatch)`;
#      * the version assertion prints `R stack OK: MatchIt 4.5.5 + optmatch 0.10.6`;
#      * `docker run --rm eqtl-discordance` -> EXIT=0, "pipeline completed with no
#        failures", headline values reproduced inside the container (96 pairs, 68.8 %,
#        rho = 0.3898), and steps 3b/3c both [ ok ];
#      * inside the image: R 4.5.2, `library(MatchIt)` loads, numpy 2.4.4 + matplotlib
#        3.10.8 import, and gate 13 reports "checked 15 audit-note directories".
#    (Gate 3, verify_provenance.py, does not run in a container: it compares the manifest
#     against `git ls-files` and .git/ is excluded from the image by design.)
#
#    ONE THING THE CONTAINER DOES NOT REPRODUCE BYTE-FOR-BYTE, and why it is not a defect:
#    `figures/*.png` come out ~2 % larger here than the committed files, because this image
#    links zlib 1.3.2 while the figures were produced with zlib 1.3.1. All eight images are
#    PIXEL-identical (0 differing pixels; the decompressed IDAT streams match byte for
#    byte). Do not "verify" a container run with `sha256sum figures/*.png` — use
#    `scripts/compare_figures_pixels.py`, and see figures/README.md §"Compare by pixel".
#
#    AND ONE IT CANNOT REPRODUCE AT ALL without help from outside: the four manuscript main
#    figures (code/figures/ge_main/) are typeset in ARIAL. Arial is proprietary, so it is
#    deliberately not installed here; matplotlib falls through to DejaVu Sans and 4.3 %-9.9 %
#    of the pixels change (the PDFs halve in size). Supplying Arial makes all four
#    pixel-identical — measured 2026-10-07 — and reproduce.sh now reports which font it
#    resolved before it compares anything, so the substitution can no longer be mistaken for
#    a data or code difference. Recipe: code/figures/ge_main/README.md.
# =============================================================================

# The readable tag is recorded here rather than as a trailing comment on the FROM line:
# BuildKit's parser reads a trailing `#` on an instruction line as further arguments and
# refuses the file (`FROM requires either one or three arguments`). This was the first
# thing that failed when the image was actually built for the first time, on 2026-10-06 —
# it never reached the pull, let alone the reproduciblity claims below.
#   pinned as  : continuumio/miniconda3:26.7.1-1  (== :latest, resolved 2026-10-03)
FROM continuumio/miniconda3@sha256:eca594d684f495c1a02beff33a9fab53aec8c5830eaf431bb149912dc6c9e4c1 AS base

LABEL maintainer="Yijing Wu <ellwyj1@outlook.com>"
LABEL description="eQTL-source discordance in TWAS — reproducibility environment (eqtl-source-discordance)"
LABEL version="4.0.2"

# =============================================================================
# Stage 1: system dependencies + conda environment
# =============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    patch \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libgit2-dev \
    wget \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*
# `build-essential` and `patch` were missing until 2026-10-06. renv installs Rcpp,
# RcppArmadillo, cobalt, MatchIt and optmatch **from source**, so without a compiler the
# R layer cannot complete at all; `patch` is what applies the optmatch fix below. Neither
# had ever been needed because the image had never been built.

# Fix 1: the manifest is at env/environment.yml, and the build context is the
# repository root (`docker build -f env/Dockerfile .`).
COPY env/environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy && \
    rm /tmp/environment.yml

# =============================================================================
# Stage 2: MetaXcan (S-PrediXcan) — the SOURCE TREE, not a runnable S-PrediXcan
# =============================================================================
# 2026-10-06 — read this before promising anything with it. The image's Python is
# 3.13.12 with numpy 2.4.4 (env/environment.yml), and official MetaXcan v0.8.1 predates
# numpy 2: `code/run_upstream.sh` asserts `numpy.__version__[0] == "1"` and stops
# otherwise, and `code/run_spredixcan.sh` calls whatever `python3` is first on PATH —
# here, 3.13. So the upstream chain CANNOT run inside this image, by construction.
# The correct environment for it is env/environment-upstream.yml (Python 3.12 +
# numpy 1.x), which cannot coexist with this one.
#
# The tree is still fetched because it is what the archive's upstream stage is defined
# against (release v0.8.1, unmodified), and having it present makes that verifiable
# without a second download. Nothing in the ENTRYPOINT uses it.

RUN git clone https://github.com/hakyimlab/MetaXcan.git /opt/MetaXcan && \
    cd /opt/MetaXcan && \
    git checkout tags/v0.8.1 && \
    find /opt/MetaXcan -name "*.pyc" -delete

ENV PATH="/opt/MetaXcan/software:${PATH}"

# =============================================================================
# Stage 3: project files, then the R side restored from the shipped lockfile
# =============================================================================

WORKDIR /app
COPY . /app/

# R comes from conda-forge into the same environment (see the header note).
RUN conda install -y -n twas-eqtl -c conda-forge r-base=4.5.2 && \
    conda clean -afy

# Fix 4: restore the R package set from the lockfile that ships with the archive
# (MatchIt 4.5.5, cobalt 4.5.2, optmatch 0.10.6 — see env/renv.lock). The previous
# revision instead *wrote* /app/renv.lock at a point where /app did not exist.
#
# 2026-10-06 — this is TWO steps, not one, for the reason env/README.md has stated in
# prose since 2026-10-04 and env/setup_r_env.sh performs: on R >= 4.5 `renv::restore()`
# cannot finish, because optmatch 0.10.6 still calls the un-prefixed `Calloc` / `Free`
# macros that R 4.5 removed. The single `R -e "renv::restore(...)"` line this replaces
# would therefore have failed the whole build. `library = .libPaths()[1]` restores into
# the conda R's own library, so `library(MatchIt)` resolves without $PRELIB — which is
# how `code/analyses/emit_S4_table.R` looks for it.
ENV PATH="/opt/conda/envs/twas-eqtl/bin:${PATH}"
ENV CONDA_DEFAULT_ENV="twas-eqtl"

RUN R -e "install.packages('renv', repos='https://cloud.r-project.org')"

# Step 1 of 3 — everything except optmatch, with renv's transactional rollback OFF.
#
# That last clause is not decoration; it is the defect the first real build of this
# two-step remedy exposed on 2026-10-06. restore() stops at optmatch exactly as predicted
# ("dependencies 'Rcpp', 'dplyr', 'tibble', 'rlemon' are not available"), but renv's
# default transactional install then REVERTED the twenty packages that had already built
# — so the patched optmatch next door had nothing to link against and step 2 failed too.
# The rollback was collapsing the two-step remedy back into a one-step failure.
RUN R -e "options(renv.config.install.transactional = FALSE); renv::restore(lockfile='/app/env/renv.lock', library=.libPaths()[1], prompt=FALSE)" \
    || echo "renv::restore() stopped before finishing — expected on R >= 4.5 (optmatch); the patched build is the next step"

# Step 2 of 3 — a safety net that does not depend on the option above having worked: if
# optmatch's own dependencies are still missing, install them before trying to build it.
RUN R -e "need <- c('Rcpp', 'dplyr', 'tibble', 'rlemon'); have <- rownames(installed.packages()); miss <- need[!need %in% have]; if (length(miss)) { cat('installing missing optmatch dependencies:', paste(miss, collapse=', '), '\n'); renv::install(miss, library=.libPaths()[1], prompt=FALSE) } else cat('optmatch dependencies already present:', paste(need, collapse=', '), '\n')"

# Step 3 of 3 — the same official optmatch 0.10.6 source, with the four Calloc/Free call
# sites renamed by env/patches/optmatch-0.10.6-R4.5-calloc.patch (63 sites, names only;
# no algorithm, argument, tolerance or data structure is touched).
RUN cd /tmp && \
    wget -q https://cloud.r-project.org/src/contrib/Archive/optmatch/optmatch_0.10.6.tar.gz && \
    tar -xzf optmatch_0.10.6.tar.gz && \
    patch -p1 --forward -i /app/env/patches/optmatch-0.10.6-R4.5-calloc.patch && \
    R CMD INSTALL --no-multiarch optmatch && \
    rm -rf /tmp/optmatch*

# Now that optmatch 0.10.6 is present, the rest of the lockfile (RcppArmadillo, cobalt,
# MatchIt) can finish. Without this second restore the build would ship an environment
# where `library(MatchIt)` fails — which is the only R package any script here needs.
RUN R -e "options(renv.config.install.transactional = FALSE); renv::restore(lockfile='/app/env/renv.lock', library=.libPaths()[1], prompt=FALSE)"

# The build fails here if the pinned stack is not actually loadable — the check the
# one-line version never made. MatchIt is what SI Table S4 runs on.
RUN R -e "stopifnot(as.character(packageVersion('MatchIt')) == '4.5.5', as.character(packageVersion('optmatch')) == '0.10.6'); cat('R stack OK: MatchIt', as.character(packageVersion('MatchIt')), '+ optmatch', as.character(packageVersion('optmatch')), '\n')"

# Fix 2: the entry points live under code/
RUN chmod +x /app/code/run_all.sh /app/code/run_spredixcan.sh

# Output directory, normally bind-mounted from the host
RUN mkdir -p /app/figures

# =============================================================================
# Entry point
# =============================================================================

# Fix 3: the script is code/run_all.sh, not /app/run_all.sh.
ENTRYPOINT ["/bin/bash", "/app/code/run_all.sh"]

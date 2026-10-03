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
#    OPEN ITEM: the base image tag is `latest`, which env/README.md rule 1 forbids.
#    Still open as of 2026-10-03: hub.docker.com and registry.hub.docker.com were both
#    unreachable from the environment that repaired this file (curl exit 56, HTTP 000), so
#    no dated tag or digest could be verified. Pinning to a tag that was never resolved
#    would be worse than leaving `latest` and saying so.
#
#    To close it, from a machine with Docker Hub access:
#        docker buildx imagetools inspect continuumio/miniconda3:latest
#    then replace the FROM line with the digest form, keeping the readable tag as a comment:
#        FROM continuumio/miniconda3@sha256:<digest>   # continuumio/miniconda3:<dated tag>
#    scripts/cut_release.sh section 7 warns until this is done.
# =============================================================================

FROM continuumio/miniconda3:latest AS base

LABEL maintainer="Yijing Wu <ellwyj1@outlook.com>"
LABEL description="eQTL-source discordance in TWAS — reproducibility environment (eqtl-source-discordance)"
LABEL version="4.0.0"

# =============================================================================
# Stage 1: system dependencies + conda environment
# =============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libgit2-dev \
    wget \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Fix 1: the manifest is at env/environment.yml, and the build context is the
# repository root (`docker build -f env/Dockerfile .`).
COPY env/environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy && \
    rm /tmp/environment.yml

# =============================================================================
# Stage 2: MetaXcan (S-PrediXcan), pinned to the version the manuscript used
# =============================================================================

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
ENV PATH="/opt/conda/envs/twas-eqtl/bin:${PATH}"
ENV CONDA_DEFAULT_ENV="twas-eqtl"
RUN R -e "install.packages('renv', repos='https://cloud.r-project.org')" && \
    R -e "renv::restore(lockfile='/app/env/renv.lock', prompt=FALSE)"

# Fix 2: the entry points live under code/
RUN chmod +x /app/code/run_all.sh /app/code/run_spredixcan.sh

# Output directory, normally bind-mounted from the host
RUN mkdir -p /app/figures

# =============================================================================
# Entry point
# =============================================================================

# Fix 3: the script is code/run_all.sh, not /app/run_all.sh.
ENTRYPOINT ["/bin/bash", "/app/code/run_all.sh"]

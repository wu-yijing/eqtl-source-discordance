# Command record — what was run, in order

Every command below was run from the repository root
(`E:\workbuddy\eqtl-source-discordance`) on 2026-10-06/07, on Docker Desktop 29.8.2
(linux/amd64, overlay2). Each entry names the log it produced under [`../logs/`](../logs/),
so the command and its output can be read together.

Shell is Git Bash on Windows. Two consequences appear repeatedly and are worth stating once:

* `MSYS_NO_PATHCONV=1` is needed on `docker run` calls whose arguments contain absolute
  container paths (`-w /work`, `--entrypoint /bin/bash`), otherwise Git Bash rewrites them
  into Windows paths before `docker.exe` sees them.
* Host paths in `-v` use the `E:/...` form, which the Docker CLI accepts directly.

---

## 1. Base image

```bash
docker pull continuumio/miniconda3:26.7.1-1
```

Docker Hub (`registry-1.docker.io`) is unreachable from this machine — Docker Desktop has no
proxy and the connection is refused at CONNECT — so pulls go through the registry mirror
configured in `~/.docker/daemon.json` (user-configured on 2026-10-06). The pull resolved to

```
Digest: sha256:eca594d684f495c1a02beff33a9fab53aec8c5830eaf431bb149912dc6c9e4c1
```

which is **the digest `env/Dockerfile` pins**, so the pin was verified against the registry
rather than taken on trust. `results/image-fingerprint.txt` is the file that re-checks it —
and it is **not shipped**: it is written by PART 1 of `scripts/make_evidence.sh`, which needs
a running daemon, and the daemon could not start on the packaging host (README §0).

Logs: `03-build-3-mirror-configured-layer-stalls.log` (earlier, stalled attempts);
`../results/image-fingerprint.txt` (PART 1, not shipped — README §0).

## 2. Build

```bash
docker build --progress=plain -t eqtl-discordance -f env/Dockerfile .
```

Run repeatedly while the environment was being fixed; each attempt is kept because each one
found a different defect, and a fix without the failure it fixes is only an assertion:

| # | Log | Outcome |
|---|---|---|
| 1 | `01-build-1-parse-error.log` | **BuildKit refuses the file**: the pinned tag was a trailing comment on the `FROM` line |
| 2 | `02-build-2-parse-fixed-registry-unreachable.log` | parses now; fails fetching the base image (network, not the repository) |
| 3 | `03-build-3-mirror-configured-layer-stalls.log` | mirror configured; `FROM` digest resolves; the 315 MB rootfs layer stalls |
| 4 | `04-build-4-renv-worker-timeout-at-r-packages.log` | apt + conda + pip complete; `renv::restore()` fails after 59 min |
| 5 | `05-probe-renv-transactional-rollback.log` | probe run identifying the real cause (below) |
| 6 | `06-build-5-success-three-step-r-layer.log` | **EXIT=0** — image built |
| 7 | `07-build-6-at-HEAD-47a0935.log` | **EXIT=0** — rebuilt so the image carries the current code |
| 8 | *(rebuilt 2026-10-07 09:01; **log not kept**)* | the rebuild after `pymupdf` was declared, so step 4 runs inside it. It **did** run — the image it produced imports `fitz` — but its log was not among the files that survived the session. Restored at packaging time by rebuilding with the daemon up: **`logs/25-build-7-rebuild-after-pymupdf.log`** |
| 9 | `27-build-8-rebuild-after-the-defect-9-fix.log` | **EXIT=0** — rebuilt again after `code/run_all.sh`'s step-4 verdict test was corrected (README §0.3, defect 9) |

The R layer is the part that is not obvious, so it is stated plainly: on R ≥ 4.5
`renv::restore()` **cannot** finish, because `optmatch 0.10.6` calls the un-prefixed
`Calloc` / `Free` macros R 4.5 removed. That was documented. What the first real build added
is that renv's **transactional install then rolled back the twenty packages that had already
built** when `restore()` stopped at optmatch, so the patched optmatch next door had nothing to
link against — the two-step remedy was collapsing back into the one-step failure it exists to
avoid. The fix is three steps, not two: restore with
`options(renv.config.install.transactional = FALSE)`, install optmatch's dependencies if they
are still absent, build optmatch 0.10.6 from the same official source with
`env/patches/optmatch-0.10.6-R4.5-calloc.patch`, then restore the remainder.

## 3. Run — the two forms `env/README.md` documents

**Form 1 — the image's own code, figures bind-mounted out.** This is the form in
`env/README.md`'s smoke test and in `README.md`'s Quick start:

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "<host>/out/figures:/app/figures" \
  -v "<host>/_si.docx:/app/_si.docx" \
  -e AF1_DOCX=/app/_si.docx \
  eqtl-discordance
```

Log: `18-final-image-readme-form-full-pipeline.log` → **EXIT=0**,
`RESULT: pipeline completed with no failures`.

Re-run at packaging time against the rebuilt image, which is what finally exercises step 4:

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "<host>/final_d/figures:/app/figures" \
  -v "<host>/_si.docx:/app/_si.docx" \
  -e AF1_DOCX=/app/_si.docx \
  eqtl-discordance
```

Logs: `26-run-step-4-runs-and-misreports-clean-as-skip.log` → **EXIT=0**, step 4 runs for the
first time and its clean verdict is reported as a `[skip]` (defect 9, README §0.3); and
`28-run-step-4-reports-ok.log` → **EXIT=0**,
`[ ok ] 11_figure_precheck.py: page size, font type, min point size and dpi all within limits`,
after the fix.

**Form 2 — a checkout on disk, running *that* copy's `code/run_all.sh`.** Mounting the tree
means the code under test is the host's, which is what you want while editing:

```bash
MSYS_NO_PATHCONV=1 docker run --rm --entrypoint /bin/bash \
  -v "<host>/repo:/work" -w /work -e AF1_DOCX=/work/_si.docx \
  eqtl-discordance -c 'bash code/run_all.sh'
```

Log: `11-run-mount-work-entrypoint-corrected.log` → **EXIT=0**, figures in `/work/figures/`.

> **`--entrypoint` is not optional here, and leaving it out fails silently.**
> The image sets `ENTRYPOINT ["/bin/bash", "/app/code/run_all.sh"]`, so in
> `docker run … eqtl-discordance bash code/run_all.sh` the trailing words are appended to
> that entrypoint **as arguments**. Nothing runs them. The image's own `/app/code/run_all.sh`
> runs instead, with `REPO=/app`, prints `Figures written to: /app/figures/`, and under
> `--rm` discards every figure at exit — **while reporting success.** That is
> `10-run-mount-work-entrypoint-not-honoured.log`, kept as the negative.

## 4. Main figures — `code/figures/ge_main/reproduce.sh`

`code/run_all.sh` does not produce Fig. 1–4; they come from this second entry point, so it
was run in the container separately.

All three conditions below were re-run at packaging time against the **rebuilt** image
(README §0.5). Every output is byte-identical to what the earlier image produced, so the
`[FAIL]` lines in the packaging-time logs are the same recorded-hash mismatch §4.3 explains,
not a regression.

**With Arial supplied** (the only way the four figures can match the submitted ones — see
`../logs/20-final-image-ge-main-with-arial.log`):

```bash
MSYS_NO_PATHCONV=1 docker run --rm --entrypoint /bin/bash \
  -v "C:/Windows/Fonts:/mnt/winfonts:ro" \
  -v "<host>/ge_main_out:/out" -e GE_MAIN_OUT=/out \
  eqtl-discordance -c "mkdir -p /usr/share/fonts/truetype/arial && \
      cp /mnt/winfonts/arial*.ttf /usr/share/fonts/truetype/arial/ && \
      rm -rf /root/.cache/matplotlib && \
      bash code/figures/ge_main/reproduce.sh"
```

**Without Arial** (documented fallback; a font substitution, quantified):

```bash
MSYS_NO_PATHCONV=1 docker run --rm --entrypoint /bin/bash \
  -v "<host>/ge_main_out:/out" -e GE_MAIN_OUT=/out \
  eqtl-discordance -c "bash code/figures/ge_main/reproduce.sh"
```

**Reference on the host**, same script, same inputs — this is what "the figures reproduce"
means, and it is the side the container is compared against:

```bash
export PYTHON=<interpreter with numpy scipy matplotlib pillow>
export GE_MAIN_OUT=<host>/ge_main_ref
bash code/figures/ge_main/reproduce.sh
```

Logs: `12-…` through `17-…`, `19-…`, `20-…`, `22-host-reference-ge-main.log`.

## 5. Repository's own gates

```bash
PY=<python> PYTHON=<python> bash scripts/verify_from_clone.sh
```

The gate script clones `HEAD` and runs 14 checks **against that clone**, so it must be run
after committing — otherwise it verifies the previous commit.

Log: `23-clone-gates-at-HEAD.log` (at `47a0935`), and `24-clone-gates-at-the-packaged-commit.log`
(re-run at packaging time, at `5c4defc` — the commit that stages this note, so gate 13 reports
16 audit-note directories against 15 in the earlier run).

## 6. Figure comparison

```bash
python3 scripts/compare_figures_pixels.py <reference_dir> <candidate_dir>
```

Exit status is non-zero only for a missing file, a shape change or a real pixel difference.
Byte differences are reported and do not fail the run, because across platforms they are
expected: the host links zlib 1.3.1, the image links 1.3.2, and the compressed IDAT stream
differs while the image does not.

## 7. Evidence generation — `scripts/make_evidence.sh`

The five files under `results/` are written by one script, against the image and the produced
figure sets. At packaging time, with the daemon up:

```bash
PYTHON=<python with numpy + Pillow> \
SI_FIGS=<host>/final_d/figures \
MAIN_FIGS_HOST=<host>/_host_run/ge_main/out \
MAIN_FIGS_ARIAL=<host>/final_d/ge_main_arial/out \
MAIN_FIGS_DEJAVU=<host>/final_d/ge_main_dejavu/out \
MAIN_FIGS_LIBERATION=<host>/final_d/ge_main_liberation/out \
bash scripts/make_evidence.sh
```

**EXIT=0.** The three comparisons that must agree do; the two font-substitution comparisons
are declared `expect-diff` — their difference *is* the result (§4.3) — while a missing file or
a shape change in them still fails the run. PART 1 and PART 2 are the two that need the
daemon (`docker image inspect`, `docker run`).

Two defects in the packaging code itself were found by running this pass and `code/run_all.sh`
— README §0.3: a clean step 4 reported as a skip, and an image identity replaced by a
Go-template error on the image's absent `Cmd` key.

---

## What was *not* run, and why

* `docker buildx imagetools inspect continuumio/miniconda3` — Docker Hub is unreachable from
  this machine; the digest was resolved through the mirror instead.
* The upstream S-PrediXcan chain (`code/run_upstream.sh`) inside the container — by
  construction it cannot run there: the image is Python 3.13 + numpy 2.4.4 and MetaXcan
  v0.8.1 predates numpy 2. `code/run_upstream.sh` asserts numpy 1.x and stops. Its
  environment is `env/environment-upstream.yml`; the chain has been run and recorded
  separately in `docs/audit_notes/upstream_chain_closure_20261004/`.
* `scripts/verify_provenance.py` (gate 3) inside the container — it compares the manifest
  against `git ls-files`, and `.git/` is excluded from the image by design.

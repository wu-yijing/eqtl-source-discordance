# env/

Environment pinning. The goal is that a reader in five years reproduces the analysis bit-for-bit, or fails loudly and immediately.

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Containerised environment. **Built and run for the first time on 2026-10-06, after five defects were fixed — see the header of the file for all of them and for the measurements.** Until that date the file had never been built, and it could not be: a trailing comment on the `FROM` line made BuildKit reject it at parse time, so the build never reached the pull. The later failures it had been carrying unseen were a missing C/C++ toolchain, a `renv::restore()` that R ≥ 4.5 cannot complete *and* whose transactional rollback then undid the packages that had succeeded, `*.log` excluded from the context so gate 13 failed inside the image, and a Stage-2 comment implying S-PrediXcan runs there. With those fixed: `docker build` → EXIT 0, image 3.74 GB; `docker run --rm eqtl-discordance` → EXIT 0, "pipeline completed with no failures", headline values reproduced in the container. Built on Docker Desktop 29.8.2 / linux-amd64 — the first host to reach a registry, so this is one measured build rather than a matrix. The conda path below remains the one the offline gates exercise. |
| `environment.yml` | Conda environment for the Python side, with explicit version pins. |
| `environment-upstream.yml` | **Second** Python environment for `code/run_upstream.sh` only: Python 3.12 + numpy 1.x, which the official MetaXcan v0.8.1 needs and which cannot coexist with `environment.yml`'s Python 3.13 + numpy 2. Not needed to reproduce any reported value. |
| `renv.lock` | R dependencies. **Do not hand-run this:** use `bash env/setup_r_env.sh` (or `bash env/setup_r_env.sh --check` to verify an existing library). It performs both steps — `Rscript -e 'renv::restore()'`, **then** apply `patches/optmatch-0.10.6-R4.5-calloc.patch` and `R CMD INSTALL` — because on R ≥ 4.5 `restore()` alone cannot finish, by design; see below. **Verified end to end on 2026-10-05** — the restored stack gives MatchIt 4.5.5 and SI Table S4's control set 30/30: [`../docs/audit_notes/env_and_boundaries_20261005/`](../docs/audit_notes/env_and_boundaries_20261005/README.md). `--check` was run against that pinned library on 2026-10-06 and reports MatchIt 4.5.5 + optmatch 0.10.6. The full (network) path of `setup_r_env.sh` has **not** been executed here — this machine has no Rtools build of its own for it to exercise — so it is shipped as the executable form of the two prose steps, not as a measured run. |
| `requirements.txt` | Pip-level pins, for readers who cannot use conda. |
| `patches/optmatch-0.10.6-R4.5-calloc.patch` | **Required** to build `optmatch` 0.10.6 — the version `renv.lock` pins — against R ≥ 4.5. See below. |

## Rules

1. **Pin exact versions.** `numpy>=1.26` is not a pin. `numpy==1.26.4` is.
2. **Record the MetaXcan version explicitly** and prefer the **unmodified official binary**. If any wrapper is applied, say so in the script header and quantify the residual difference. *(This manuscript's headline values are recomputed with the official MetaXcan v0.8.1 binary after three-way allele harmonisation; an earlier in-house implementation is retained only as an equivalence cross-check.)*
3. **Rebuild from scratch before a release.** A container that only builds on the author's machine does not reproduce anything.
4. **Record the toolchain versions** (`python`, `R`, `matplotlib`, `scipy`, `PLINK`, `MetaXcan`) in `metadata/provenance.json` under `generated_by`.
5. **No network access at analysis time.** All inputs are fetched and checksummed in a separate, explicit step.
6. **If a step needs a different interpreter, pin that interpreter in its own file.** The upstream S-PrediXcan chain needs Python 3.12 + numpy 1.x and cannot share `environment.yml` (Python 3.13 + numpy 2). Stating the requirement in a script header is not a pin: `environment-upstream.yml` is. Add a file rather than loosening an existing pin.

## optmatch and R ≥ 4.5 — one patch is required

`renv.lock` pins `optmatch` **0.10.6**, and that version **does not compile** against
R 4.5.x as published. R 4.5 removed the un-prefixed `Calloc` / `Free` macros from the
R headers, so four of its C++ sources fail with

```
map.cc:47:31: error: expected primary-expression before ')' token
map.cc:47:18: error: 'Calloc' was not declared in this scope; did you mean 'calloc'?
```

`patches/optmatch-0.10.6-R4.5-calloc.patch` rewrites those calls to `R_Calloc` /
`R_Free` — the names R itself moved to in 4.5 — and does nothing else. It touches
four files (`src/map.cc`, `src/smahal.cc`, `src/r_smahal.cc`,
`src/subsetInfSparseMatrix.cc`) and 63 call sites; every changed line is a rename,
and the diff has no other content. **No algorithm, argument, tolerance or data
structure is altered**, which is what makes it acceptable under rule 1 above: this is
the official source rebuilt with the spelling the pinned R requires, not a substitute
implementation. Apply it after unpacking, and before `R CMD INSTALL`:

```bash
tar -xzf optmatch_0.10.6.tar.gz
patch -p1 < env/patches/optmatch-0.10.6-R4.5-calloc.patch
R CMD INSTALL --no-multiarch optmatch
```

**Scope of the omission if someone declines to patch.** `optmatch` is reached only by
`matchit(method = "optimal")` and `method = "full"`. The analysis whose environment
this file pins reaches it only through `method = "optimal"`, which was swept as a
sensitivity and never produced the best agreement with the reported table; the
reported matching itself is `method = "nearest"` with `distance = "mahalanobis"`,
which does not touch `optmatch` at all. So an unpatched environment reproduces the
reported result, and fails loudly rather than silently for the two methods that need
the package — which is the correct failure mode under rule 3. Readers on R ≤ 4.4 do
not need the patch at all.

Background, and the measurement that motivated writing this down:
[`../docs/audit_notes/s4_specification_sweep_20261004/README.md`](../docs/audit_notes/s4_specification_sweep_20261004/README.md).

## Smoke test

```bash
docker build -t eqtl-discordance -f env/Dockerfile .

# 1. Run the image's own copy of the code, and get the figures out on the host.
docker run --rm -v "$PWD/figures:/app/figures" eqtl-discordance

# 2. To run the checkout on your disk instead (e.g. you changed something), you MUST
#    override the entrypoint. See the warning below for why.
docker run --rm --entrypoint /bin/bash -v "$PWD:/work" -w /work \
    -e AF1_DOCX=/work/Supporting_Information.docx eqtl-discordance -c 'bash code/run_all.sh'
```

> ⚠️ **`docker run … eqtl-discordance bash code/run_all.sh` does NOT do what it looks like,
> and this file told readers to use it until 2026-10-07.** The image sets
> `ENTRYPOINT ["/bin/bash", "/app/code/run_all.sh"]`, so a trailing command is passed to that
> entrypoint as *arguments* — it is not executed. Measured: the invocation ran the image's own
> `/app/code/run_all.sh` instead of the mounted one, printed
> `Figures written to: /app/figures/`, and with `--rm` every figure was discarded at exit. It
> reported success while doing none of what was asked. Anything after the image name is only
> a *command* if the image has no `ENTRYPOINT`, or if you pass `--entrypoint` and give the
> shell a `-c` string as above; form 1 avoids the question entirely and is the one to use.

The smoke test must pass from a clean clone before any release that changes code. Record the result in the `CHANGELOG.md` entry for that version.

The figures that form 1 writes will **not** be byte-identical to the committed `figures/*.png`
unless you are on the machine that produced them — this image links zlib 1.3.2, the committed
files were made with 1.3.1, and the compressed IDAT differs while the images are pixel-identical.
Compare them with `scripts/compare_figures_pixels.py`, not with `sha256sum`; see
[`../figures/README.md`](../figures/README.md) §"Compare by pixel, not by byte".

# env/

Environment pinning. The goal is that a reader in five years reproduces the analysis bit-for-bit, or fails loudly and immediately.

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Containerised environment. The recommended path — it is the only one that pins the OS layer too. |
| `environment.yml` | Conda environment for the Python side, with explicit version pins. |
| `environment-upstream.yml` | **Second** Python environment for `code/run_upstream.sh` only: Python 3.12 + numpy 1.x, which the official MetaXcan v0.8.1 needs and which cannot coexist with `environment.yml`'s Python 3.13 + numpy 2. Not needed to reproduce any reported value. |
| `renv.lock` | R dependencies. Restore with `Rscript -e 'renv::restore()'`. |
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
docker run --rm -v "$PWD:/work" -w /work eqtl-discordance bash code/run_all.sh
```

The smoke test must pass from a clean clone before any release that changes code. Record the result in the `CHANGELOG.md` entry for that version.

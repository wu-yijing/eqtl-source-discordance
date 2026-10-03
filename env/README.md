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

## Rules

1. **Pin exact versions.** `numpy>=1.26` is not a pin. `numpy==1.26.4` is.
2. **Record the MetaXcan version explicitly** and prefer the **unmodified official binary**. If any wrapper is applied, say so in the script header and quantify the residual difference. *(This manuscript's headline values are recomputed with the official MetaXcan v0.8.1 binary after three-way allele harmonisation; an earlier in-house implementation is retained only as an equivalence cross-check.)*
3. **Rebuild from scratch before a release.** A container that only builds on the author's machine does not reproduce anything.
4. **Record the toolchain versions** (`python`, `R`, `matplotlib`, `scipy`, `PLINK`, `MetaXcan`) in `metadata/provenance.json` under `generated_by`.
5. **No network access at analysis time.** All inputs are fetched and checksummed in a separate, explicit step.
6. **If a step needs a different interpreter, pin that interpreter in its own file.** The upstream S-PrediXcan chain needs Python 3.12 + numpy 1.x and cannot share `environment.yml` (Python 3.13 + numpy 2). Stating the requirement in a script header is not a pin: `environment-upstream.yml` is. Add a file rather than loosening an existing pin.

## Smoke test

```bash
docker build -t eqtl-discordance -f env/Dockerfile .
docker run --rm -v "$PWD:/work" -w /work eqtl-discordance bash code/run_all.sh
```

The smoke test must pass from a clean clone before any release that changes code. Record the result in the `CHANGELOG.md` entry for that version.

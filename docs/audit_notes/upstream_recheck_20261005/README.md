# Upstream re-check — the B and C bands, re-run on a third machine (2026-10-05)

**What this directory is.** A dated record of completing `code/run_upstream.sh`'s
**B and C bands** on a machine that is neither the author's nor the one behind
[`../upstream_chain_closure_20261004/`](../upstream_chain_closure_20261004/README.md), and
of the one thing that came out of it: the four eQTLGen `*.db` artefacts are **identical in
content but not in bytes** across the two runs, and the reason is a dependency the archive
does not pin.

**Why it was needed.** The 2026-10-05 re-check of the earlier six open items ran the chain
only as far as band A. The three band covariances are the one class of middleware GitHub
cannot distribute, so the question "is the missing data on GitHub?" was asked and answered
first — see §1 — and then bands B and C were built locally.

---

## 0. Result

```
$ python3 code/upstream/verify_middleware.py --run-dir <run-dir>
  ...
  identical 26 | differing 4 | missing 0   (of 30)
  RESULT: the rebuild does NOT reproduce the archived middleware.
```

| Verdict | Count | Which |
|---|---|---|
| byte-identical | **26** | both GTEx covariances; all three `cov_{A,B,C}.txt.gz`; the three harmonised GWAS; the three allele-aligned GWAS; the six GTEx S-PrediXcan outputs; **all nine** eQTLGen band S-PrediXcan outputs |
| differing in bytes, **identical in content** | **4** | `eQTLGen_Whole_Blood.db`, `db_A.db`, `db_B.db`, `db_C.db` — see §3 |
| missing | **0** | — |

So the chain reproduces **30 of 30 artefacts at content level** and 26 of 30 at byte level on
this machine. The archive's own gate still prints "does NOT reproduce", because it pins the
four databases by `file-sha256`; the rest of this note is about that four.

## 1. Was the missing data on GitHub? No.

Checked before rebuilding:

| Where it could have been | Result |
|---|---|
| `data/upstream/` in the repository | ❌ ships **no** `cov_A/B/C.txt.gz`. `data/upstream/README.md` says why: `cov_A` (175.2 MiB) and `cov_C` (106.4 MiB) are over GitHub's hard 100 MiB per-file block and cannot be pushed *at all*; `cov_B` (94.6 MiB) is under it, but shipping one band of three would not let anyone re-run the arm. Their **content hashes** are recorded in `data/external/README.md` instead |
| GitHub **Releases** of `wu-yijing/eqtl-source-discordance` | ❌ two releases exist (`v4.0.1`, `v4.0.2`) and **neither carries assets** |
| other branches | ❌ `git ls-remote --heads origin` → `main` only |

The band databases (`db_A/B/C.db`) and the nine band S-PrediXcan outputs **do** ship, so the
only genuinely absent artefacts were the three covariances — one of which (`cov_A`) the
2026-10-05 pass had already built. Bands B and C were therefore rebuilt from the hashed
inputs, as the archive intends.

## 2. What was run

Steps 5–7 of `code/run_upstream.sh` for `EQ_TAG=B` and `EQ_TAG=C`: build each band's
covariance, then run S-PrediXcan once per phenotype. Bands A's own artefacts were produced
earlier the same day.

| Step | Artefact | Bytes on this run | Ledger (`../upstream_chain_closure_20261004/ledger/middleware_ledger.tsv`) | Verdict |
|---|---|---|---|---|
| 5 | `eqtlgen/cov_B.txt.gz` | 99,159,225 | 99,159,225 | ✅ **equal file size**, content-md5 matches |
| 5 | `eqtlgen/cov_C.txt.gz` | 111,535,391 | 111,535,391 | ✅ equal file size, content-md5 matches |
| 7 | `official_eq_B_DR.csv` | 1,408 | 1,408 | ✅ byte-identical |
| 7 | `official_eq_B_DN.csv` | 1,398 | 1,398 | ✅ byte-identical |
| 7 | `official_eq_B_DPN.csv` | 1,399 | 1,399 | ✅ byte-identical |
| 7 | `official_eq_C_DR.csv` | 315 | 315 | ✅ byte-identical |
| 7 | `official_eq_C_DN.csv` | 318 | 318 | ✅ byte-identical |
| 7 | `official_eq_C_DPN.csv` | 315 | 315 | ✅ byte-identical |

S-PrediXcan ran **unmodified, official MetaXcan v0.8.1**, with `--stream_covariance`, one
process per band × phenotype; every invocation exited 0. Full verifier output:
`evidence/verify_middleware.txt`.

## 3. The four databases: same size, same content, different bytes

```
eQTLGen_Whole_Blood.db   4,866,048 B  both   weights 65,622 / extra 103   content MATCH
db_A.db                  3,469,312 B  both   weights 46,919 / extra  94   content MATCH
db_B.db                  1,007,616 B  both   weights 13,671 / extra   8   content MATCH
db_C.db                    380,928 B  both   weights  5,032 / extra   1   content MATCH
```

The content comparison is reproducible:
`scripts/compare_db_content.py <archived-db> <rebuilt-db> …` hashes the schema and then
every row of every table in a deterministic order (it is the `.db` analogue of the *content*
comparison the archive already applies to the `.txt.gz` rows). Output:
`evidence/db_content_compare.txt`.

**Cause.** A SQLite file's physical page image depends on the writer's library version.
This run used **Python 3.12.3 / SQLite 3.45.1**; the 2026-10-04 closure used **Python
3.12.15**, and `sqlite3.sqlite_version` is recorded **neither** in
`env/environment-upstream.yml` **nor** in that closure's `toolchain/versions.txt`. Nothing
was patched: the tarball hash and the executed `SPrediXcan.py` hash are the pinned ones
(`evidence/toolchain.txt`).

**What this means for the archive, stated plainly.** The four `.db` rows are pinned by
`file-sha256`, so their reproducibility is **conditional on an unpinned dependency**. This is
not a wrong number and not a lost step — the content is verified identical — but it is a
claim that is weaker than it looks, and it will fire again for any reader whose Python
carries a different SQLite.

**Recommendation (recorded, not applied here).**

1. `env/environment-upstream.yml` and `toolchain/versions.txt` should record
   `sqlite3.sqlite_version`.
2. `middleware_ledger.tsv` and `verify_middleware.py` should compare `.db` on **content**
   (as they already do for `.txt.gz`), keeping the byte hash as a secondary column.

## 4. Environment

`evidence/toolchain.txt`: MetaXcan tarball SHA-256
`3a6e1cee…` (= the `SHA256SUMS` row), `SPrediXcan.py` SHA-256 `94e79ae2…`, and
python 3.12.3 / numpy 1.26.4 / scipy 1.13.1 / pandas 2.2.3 / **sqlite3 3.45.1**. All 15
external inputs were verified against `data/external/SHA256SUMS` first: `ok 15 /
mismatched 0 / incomplete 0 / missing 0`.

## 5. How this relates to the other records

| Record | Relationship |
|---|---|
| [`../upstream_chain_closure_20261004/`](../upstream_chain_closure_20261004/README.md) | the independent end-to-end execution; **30/30 by file-sha256 on Python 3.12.15**. This note does not contradict it — it identifies the dependency that makes that 30/30 conditional |
| [`../r_path_and_hygiene_closure_20261005/`](../r_path_and_hygiene_closure_20261005/README.md) | the six open items; its §4.2 is this note's summary |
| `data/upstream/README.md` | the shipping policy that puts `cov_{A,B,C}` out of reach and records their content hashes |

## 6. Publishing the three band covariances — route chosen, NOT yet executed

Of the thirty artefacts, **27 already ship** in `data/upstream/` and are byte-identical to
this rebuild. The three that do not are the band covariances, and they cannot live in the
tree: GitHub rejects any file over 100 MiB, `cov_A` (175.2 MiB) and `cov_C` (106.4 MiB) are
over it, and `cov_B` (94.6 MiB) ships alone for no benefit — the archive's own reasoning, in
`data/upstream/README.md`.

The carrier chosen on 2026-10-05 is a **GitHub Release asset** (2 GiB per file).

| Asset | Bytes | sha256 of this rebuild | Content md5 (the archive's pin) |
|---|---|---|---|
| `cov_A.txt.gz` | 183,659,809 | `b9c690a8afe8395a2f06ce763fd70cb0a872df5136cba93ecb8c298755a71d73` | `ed58ccdfc590dc4498dd5ddc6c8b0ea2` |
| `cov_B.txt.gz` | 99,159,225 | `4a8f2a55ab7d39e4b0eba026b359fa85f4637281e39add8ffd9b5d58e3587021` | `2a532e74469a340feaf0b7a791740151` |
| `cov_C.txt.gz` | 111,535,391 | `8827b67ac47eec3f9f9293078438e5bd1856ef276349aa4401270f573129e3b2` | `f30ebf0255d9eed610b6162a35be97c6` |

`scripts/release_covariance_assets.sh` performs it. It verifies each byte count against
`../upstream_chain_closure_20261004/ledger/middleware_ledger.tsv` **before uploading
anything**, so a wrong build cannot be published under the right name, then creates the
release and attaches the three files:

```bash
GH_TOKEN=<a classic PAT with repo scope> \
  bash scripts/release_covariance_assets.sh --file-dir <dir with cov_A/B/C.txt.gz> --tag v4.0.3
# add --dry-run to verify and stop
```

**Maintainer decision (2026-10-05): no new tag now.** The upstream rebuild is deliberately
*not* being cut as its own version: other results are still to be folded in, and the version
release will be done once, later. The covariances are therefore attached to the **existing**
release — `v4.0.2`, release id **402753097**, which carried no assets — which is why the
script takes `--release-id` and creates no tag in that mode:

```bash
GH_TOKEN=<a PAT that can write to this repository> PYBIN=python3 \
  bash scripts/release_covariance_assets.sh --file-dir <dir> --release-id 402753097
# --dry-run verifies the local files and stops
```

**Status: executed and blocked on token scope — the release still carries 0 assets.** The
attempt of 2026-10-05 reached the uploads and every one returned **HTTP 404** from
`uploads.github.com`, while the read calls (repo, release, asset list) all succeeded. The
diagnosis is not a missing release: it is a token with **no scopes at all** —

```
$ curl -sS -D - -o /dev/null -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/user | grep -i x-oauth-scopes
X-OAuth-Scopes:                 # empty
```

GitHub answers 404 rather than 403 for a write an unscoped token may not perform, so a
permission failure is indistinguishable from a missing resource until the scope header is
read. Both `Authorization: Bearer` and `Authorization: token` were tried, with a 1-byte probe
file, and both returned 404 — the request format is not the problem.

**What unblocks it**, in order of least privilege:

1. **A fine-grained PAT** — Resource owner `wu-yijing`; Repository access → only
   `eqtl-source-discordance`; Repository permissions → **Contents: Read and write** (Releases
   and their assets fall under Contents). Then re-run the command above.
2. **A classic PAT with `public_repo`** (the repository is public, so `public_repo` is
   sufficient; `repo` also works). A classic token's scopes are not editable after creation,
   so this means generating a new one.
3. **No credential at all** — the three files are on the machine that did the rebuild; on the
   release page, `Edit`/`Draft` → attach `cov_A.txt.gz`, `cov_B.txt.gz`, `cov_C.txt.gz` →
   update. Verification afterwards needs only read access, which works today.

The script now prints the scope diagnosis itself when it sees 404, so the next attempt names
the cause instead of showing a bare "Not Found".

**Recorded for the unified release, when it comes.** `docs/RELEASE_PROCESS.md` requires the
tag to equal `.zenodo.json`'s `version` (currently **4.0.2**), so a version release means
`v4.0.3` plus moving `CHANGELOG.md`'s `[Unreleased]` section to `[4.0.3]` and bumping
`.zenodo.json` and `CITATION.cff`. Publishing a Release also **triggers the Zenodo webhook**,
which archives a new version of the repository at that tag; the covariances themselves live
only as GitHub Release assets, because Zenodo archives the git tree and not release assets.

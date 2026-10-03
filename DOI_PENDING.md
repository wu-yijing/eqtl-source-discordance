# DOI_PENDING — this repository has no published DOI yet

**Status: `pending`.** The canonical repository has not been published to Zenodo, so every DOI in
this tree is an explicitly unresolved placeholder. `metadata/zenodo_release.json` is the single
source of truth; [`scripts/set_doi.py`](scripts/set_doi.py) fills the carriers from it.

| Field | Value |
|---|---|
| Status | pending |
| Version to be released | whatever `.zenodo.json` declares — not duplicated here, so the two cannot disagree |
| Concept DOI | `10.5281/zenodo.23129112` |
| Version DOI | `10.5281/zenodo.23129113` |
| Zenodo record | _not yet created_ |

> **Do not cite the placeholders.** They are not registered, resolve to nothing, and the README
> badge is deliberately a static "pending" shield rather than a Zenodo badge that would 404.

---

## Why this file exists rather than a DOI

The associated manuscript's Data availability statement pairs a Zenodo DOI with a GitHub URL, and
in its current form the two **do not name the same object**:

| Carrier | Names | What a reader actually gets |
|---|---|---|
| Zenodo `10.5281/zenodo.22910500` / `.22910501` | `wu-yijing/eqtl-source-discordance-audit` | **v1.0.0, published 2026-09-23, a single 2.34 MB zip.** The predecessor release-only snapshot. |
| GitHub URL in reference [39] | `wu-yijing/eqtl-source-discordance` | **This repository**, v4.0.1, 412 tracked files, HEAD `652918dc`. |

The Zenodo snapshot predates, and therefore does not contain:

- every gap closure recorded in [`metadata/ARCHIVE_MAP.md`](metadata/ARCHIVE_MAP.md) — GAP-1…GAP-10,
  including `data/derived/hk_official_Z.csv` and `data/derived/dn_cross_population.csv`;
- the seven committed figure build outputs under [`figures/`](figures/);
- the SI Table S6 ACAT-O combination rule (the sqrt(*N*)-weighted Cauchy combination) and
  `scripts/recompute_acat_o.py`;
- the clone-only Table S9 pool re-derivation and the whole `code/analyses/reproduction_20261002/`
  package.

In other words a reader who follows the DOI gets the revision in which most of this repository's
reproducibility claims cannot yet be checked. Publishing this repository is what closes that gap;
it is not a documentation edit.

---

## How to publish, and then fill the DOI

Zenodo cannot issue a DOI for a repository that is not yet in the record, so the order is fixed:
release first, DOI second, backfill third.

### 1. Cut the release on this side

```bash
bash scripts/cut_release.sh          # pre-flight; it warns, correctly, that the DOI is pending
git add -A
python3 scripts/collect_provenance.py   # after staging: it hashes the index, not the worktree
bash scripts/verify_from_clone.sh       # 10 gates, inside a fresh clone
```

### 2. Publish to Zenodo

`.zenodo.json` is already in the tree and supplies title, description, creators, licence,
keywords and `version`. Two routes:

- **GitHub integration (recommended).** On <https://zenodo.org/account/settings/github/> enable
  the repository, then create a GitHub **release** whose tag matches `.zenodo.json`'s `version`
  (e.g. version `4.0.0` → tag `v4.0.0`). Zenodo archives the tag and mints the DOI.
- **Manual upload.** Deposit a source archive of the tag at <https://zenodo.org/deposit> and
  publish it.

Either way you get **two** identifiers: a **concept DOI** (stable, always resolves to the newest
version) and a **version DOI** (pins this exact snapshot). Record both.

> ⚠️ Publish as a **new** record for this repository. Do **not** reuse
> `10.5281/zenodo.22910500` — that concept belongs to `eqtl-source-discordance-audit`, and reusing
> it would silently redefine what an already-cited DOI points at.

### 3. Backfill

```bash
python3 scripts/set_doi.py \
    --concept 10.5281/zenodo.<digits> \
    --version 10.5281/zenodo.<digits> \
    --record  https://zenodo.org/records/<digits> \
    --release-date YYYY-MM-DD

python3 scripts/set_doi.py --check     # must print: every carrier resolves to a real DOI
```

That one command rewrites **README.md** (badge and prose), **CITATION.cff**, **CHANGELOG.md**,
this file and `docs/predecessors/README.md`, and updates `metadata/zenodo_release.json`.

It deliberately does **not** rewrite `docs/audit_notes/` — those notes quote the placeholder
because that is what was true on the date they were written, and this repository does not rewrite
historical records.

### 4. Re-close the loop

```bash
git add -A && python3 scripts/collect_provenance.py
bash scripts/verify_from_clone.sh
```

### 5. Then, and only then, update the manuscript

The Data availability statement and reference [39] should cite the DOI produced in step 2 — the
one that resolves to *this* repository — alongside the GitHub URL. That edit lives in the
submitted `.docx` and is **not** made by anything in this repository.

---

## What is already done, so that only the DOI is missing

| Item | State |
|---|---|
| `.zenodo.json` metadata | present; it owns the release version, and `cut_release.sh` checks it against `CITATION.cff` and `CHANGELOG.md` |
| `CITATION.cff` | present, with a concept-DOI slot that resolves to a placeholder until step 3, and a commented version-DOI slot that step 3 activates |
| Predecessor archives | recorded read-only in [`README.md`](README.md#archived-predecessors), and their contents materialised in [`docs/predecessors/`](docs/predecessors/README.md) |
| Reproducibility gates | `scripts/verify_from_clone.sh` (**10** gates) and `scripts/cut_release.sh` — section 6 surfaces the pending DOI; section 7 checks the container base image is pinned by digest (it is, as of 2026-10-03) |
| DOI backfill tooling | [`scripts/set_doi.py`](scripts/set_doi.py) — `--show`, `--check`, and the backfill |

*Written 2026-10-03. Nothing in this file asserts a DOI that does not exist.*

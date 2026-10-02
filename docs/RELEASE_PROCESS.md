# RELEASE_PROCESS — how a version is cut and archived

Audience: the maintainer, six months from now, who has forgotten everything.
Follow the steps in order. Do not skip step 1.

---

## 0. One-time setup (do this once per repository)

1. Make the repository **Public** (Settings → General → Danger Zone → Change visibility).
   Zenodo will happily archive a private repository, but the resulting record is **public by default** — that leaks code and data. Public first, always.
2. Log in at <https://zenodo.org> **with your GitHub account** (same account that owns the repository).
3. Avatar → **Settings** → **GitHub** (Linked accounts) → authorise the GitHub App, then **Sync now**.
4. Find `eqtl-source-discordance` in the **Repositories** list and flip its switch **ON**.
   Default for every repository is OFF; nothing is archived until you flip it.
5. Copy the badge from the Zenodo record into `README.md`.

> **Timing rule.** Only GitHub *Releases* created **after** the switch is turned on are archived. Releases that already exist are not back-filled. Turn the switch on **before** cutting the first release.
>
> **Do not toggle the switch off and on.** It has historically caused earlier releases to be re-archived, producing duplicate versions.

---

## 1. Pre-flight (mandatory)

```bash
bash scripts/cut_release.sh          # runs every check below and prints a report
bash scripts/verify_from_clone.sh    # and then the same checks where a reader sits
```

**Run both.** `cut_release.sh` runs where the author works, and four defects have shipped
from a green pre-flight here: a path bootstrap one directory short (compiles, dies at run
time), a hash table recording CRLF values for files a clone checks out as LF, a manifest
hashing the working tree, and a rebuild that wrote a shipped input with the platform's line
ending. Each passed locally and failed for every reader. `verify_from_clone.sh` makes a
fresh `git clone --no-hardlinks` and re-runs the checks there, which is the only place the
claim "a third party can reproduce this" can be tested.

Manual equivalent:

| Check | Command | Must be |
|---|---|---|
| Working tree clean | `git status --porcelain` | empty |
| On the default branch | `git rev-parse --abbrev-ref HEAD` | `main` |
| Up to date with remote | `git fetch && git status -sb` | not behind |
| `.zenodo.json` is valid JSON | `python -m json.tool .zenodo.json > /dev/null` | exit 0 |
| `.zenodo.json` version matches tag | compare `version` with `vX.Y.Z` | identical |
| `CITATION.cff` version matches | compare `version:` | identical |
| `CHANGELOG.md` has a section for the version | `grep -n "^## \[X.Y.Z\]" CHANGELOG.md` | found |
| Pre-specification anchors reachable | `git cat-file -t 58da15b && git cat-file -t e70806b` | both `commit` |
| No file over 100 MB | `git ls-files -z \| xargs -0 du -h \| sort -rh \| head` | none |
| No stray runtime output tracked | `git ls-files \| grep -E '^(figs\|results\|outputs\|logs\|tmp)/'` | empty |
| `metadata/provenance.json` regenerated | `python scripts/collect_provenance.py` | no diff, or committed diff |
| `provenance.json` covers the tracked tree | `len(files) + len(excluded) == git ls-files` — checked by `scripts/cut_release.sh` | equal |
| **`provenance.json` hashes still match** | `python scripts/verify_provenance.py` | exit 0 |
| Every reproduction script can import its path module | `python code/analyses/reproduction_20261002/check_wiring.py` — also run by `cut_release.sh` | exit 0 |
| **That wiring gate can fail** | `python ... check_wiring.py --self-test` | exit 0 |
| **Shipped inputs byte-exact** | `python code/analyses/reproduction_20261002/paths_config.py` | exit 0 |
| **`ARCHIVE_MAP.md` is self-consistent** | `python scripts/check_archive_map.py` | exit 0 |
| **The headline numbers reproduce** | `python code/analyses/reproduction_min/reproduce_headline.py` | exit 0, 0 mismatches |
| **Table S9's pools re-derive from a clone** | `python code/analyses/reproduction_20261002/00_build_added_derived.py`'s `build_pools()` with every `REPRO_*` unset, then `git status --porcelain data/derived` | prints 11,820 / 818; empty status |

The last row runs inside `verify_from_clone.sh` and not in `cut_release.sh`, deliberately:
it writes to `data/derived/`, and a pre-flight check on the author's own tree must be
read-only. In a throwaway clone, writing to it is the point — the check is that the files
come back **byte-identical**.

The four rows in bold were added on **2026-10-02**, each because a check that existed could
not fail the build: a check that only prints its verdict (the `paths_config` self-check), a
check that is never run against a tree other than the author's, a check that was vacuous
because its own directory was on `sys.path`, and a document nothing parsed at all. A check
that cannot fail a release is not a gate.

**Freeze rule.** Every script that produces a reported number must already be merged. Nothing that can change a number may be touched after this point.

---

## 2. Choose the version number

Semantic versioning, adapted to research artefacts:

| Bump | When | Test |
|---|---|---|
| **MAJOR** | Any reported number or conclusion changes | Would a published value in the manuscript change? |
| **MINOR** | New analyses, figures, tables or scripts added; **no** existing number changes | |
| **PATCH** | Documentation, comments, environment pinning only | |

Record the justification in `CHANGELOG.md` **and state explicitly whether any number changed.**

---

## 3. Cut the release

```bash
# 3.1 Update metadata (all three must agree)
#     .zenodo.json  -> "version": "X.Y.Z"
#     CHANGELOG.md  -> new "## [X.Y.Z] - YYYY-MM-DD" section at the top
#     CITATION.cff  -> version: X.Y.Z  (and date-released)

# 3.2 Regenerate provenance
#     Note: collect_provenance.py walks `git ls-files`, so stage new files FIRST,
#     or they will not be hashed. `git add -A` before this step is fine.
git add -A
python scripts/collect_provenance.py
git diff --stat metadata/provenance.json

# 3.3 Commit
git add -A
git commit -m "release: vX.Y.Z"

# 3.4 Annotated tag
git tag -a vX.Y.Z -m "vX.Y.Z - <one-line summary>"

# 3.5 Push branch and tag
git push origin main --follow-tags
```

Then, on GitHub: **Releases → Draft a new release**

- *Choose a tag*: `vX.Y.Z`
- *Release title*: `vX.Y.Z — <one-line summary>`
- *Describe this release*: paste the `CHANGELOG.md` section verbatim
- Leave "Set as the latest release" checked
- → **Publish release**

Zenodo picks it up within seconds to minutes and creates a new record: a new **version DOI**, under the existing **concept DOI**.

---

## 4. After publication

1. Copy the new version DOI and the concept DOI into `README.md` (if the badge is present, it already carries the concept DOI).
2. Add the version DOI to the manuscript's data-availability statement as *the version analyzed* — **but only if it genuinely is** (see §6).
3. If the associated article now has a DOI, add it to the Zenodo record:
   **record page → Edit → Related works → `is supplement to` → article DOI**, then **Publish**.
   Metadata edits do **not** create a new version and do **not** change any DOI.
4. Add the same relation to `CITATION.cff` as `preferred-citation`.

---

## 5. Absolute rules

| Rule | Why |
|---|---|
| A published tag is **never** force-pushed, rebased, moved or deleted | A DOI must never point at content that no longer exists |
| A published release is **never** deleted | Same reason. Supersede it instead |
| Tags are annotated (`git tag -a`) | Carries author, date and message; lightweight tags are indistinguishable from branch pointers |
| `.zenodo.json` changes are committed **before** the release | Zenodo reads the file from the tagged tree, not from `main` |
| The repository is never renamed | Renaming breaks every hard-coded URL in `.zenodo.json`, `CITATION.cff` and published DOI metadata |
| `metadata/ARCHIVE_MAP.md` never over-claims | A map that admits a gap is useful; one that asserts a false mapping is a liability |

---

## 6. "The version analyzed" is a claim you must be able to defend

The predecessor archive stated in the manuscript that the archived snapshot was *the version analyzed*, while three simulation scripts and the final figure scripts were written **after** that snapshot was deposited. The claim was therefore false on its face, and a reviewer noticed.

Two legitimate ways to make the claim:

| Path | How | Requirement |
|---|---|---|
| **Release last** (preferred) | Finish all analysis, simulation and figure scripts → then cut the release → cite that version DOI | The freeze rule in §1 must actually hold |
| **Release early, cite honestly** | Deposited snapshot predates later script changes → write instead: *"pre-specification is recorded in the version-controlled repository; commit identifiers are given in `metadata/PRE_REGISTRATION.md`"* | Do not call an earlier deposit "the version analyzed" |

---

## 7. If a release is wrong

| Situation | Action |
|---|---|
| Metadata wrong (title, description, keywords, licence, related works) | Edit it on the Zenodo record page and **Publish**. DOI unchanged, no new version. |
| Wrong files deposited, or a number changed | **Do not delete.** Fix in the repository, cut the next version, and say so in `CHANGELOG.md`. The superseded version stays online and citable. |
| Release accidentally made public with sensitive content | Zenodo record → Edit → **Restricted**/**Closed** access, and contact Zenodo support. Removing files from an archived DOI is not possible; assume anything published is permanent. |

---

## 8. Location of the DOIs

| DOI | Where it appears |
|---|---|
| **concept DOI** | `README.md` badge, `CITATION.cff` `identifiers`, manuscript data-availability statement, cover letter, project page |
| **version DOI** | Manuscript data-availability statement (*the version analyzed*), `CHANGELOG.md` release links |

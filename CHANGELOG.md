# Changelog

All notable changes to this archive are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/) adapted to research artefacts (see `docs/RELEASE_PROCESS.md` §2).

**Every entry must state explicitly whether any reported number changed.** That sentence is the first thing a reviewer will look for.

---

## Version lineage — read this before comparing version numbers

This project has been re-archived three times. Version numbers **do not restart** with each repository; they continue across the lineage so that no two releases of this study ever share a number. Releases below this repository's first entry belong to predecessor repositories, which are archived and read-only.

| Version | Repository | Zenodo record | Note |
|---|---|---|---|
| v1.0.0 – v3.0.0 | `wu-yijing/twas-eqtl-source-discordance` (formerly `TWAS-eQTL-source-confounding`) | concept `10.5281/zenodo.21238202` | Full pre-2026-09-24 development history. **GitHub tags and Zenodo version labels for this period are not identical — see "Open item" below.** |
| v1.0.0 – v1.0.1 | `wu-yijing/eqtl-source-discordance-audit` | concept `10.5281/zenodo.22910500` | Release-only snapshot; **its v1.0.0 tag sits two commits behind that repository's final state** |
| **v4.0.0** → | **this repository** | new concept DOI `<CONCEPT>` | Canonical from here on |

> **Open item — do not close this by assumption.** The predecessor README declares Zenodo version **v2.7.0** as current, while its GitHub tags stop at **v3.0.0**. GitHub tags and Zenodo version labels for the predecessor repository are therefore out of step. Record the true mapping here once verified, because a reader comparing the two will otherwise conclude that a release is missing.

---

## [Unreleased]

### 2026-10-02 (sixth pass) — the documents audited against the archive; one row does not reproduce

**No reported number changes.** New check, and one status that was wrong.

`scripts/audit_documents_vs_repo.py` answers the question a reviewer actually asks — are the
numbers in the manuscript and the Supporting Information in here — in two strengths, and says
which is which. Run against `Supporting_Information_GenetEpidemiol_20260930.docx` (31 tables)
and `Manuscript_GenetEpidemiol_20260930.docx` (4 tables):

* **Class A, structural equality** — 8 tables that are a straight projection of a shipped
  table, compared **cell by cell** after aligning rows on their key columns:
  **4,398 cells, 0 mismatches.** S2 728/728, S3 1,554/1,554, S4 420/420, S13 288/288,
  S15 243/243 (+9 declared placeholders), S18 1,035/1,035, S23 122/122, main-text
  Table 2(A) 4/4.
* **Class B, value presence** — every other table's numbers looked up in the archive at the
  precision the document prints them: **2,850 of 2,851.** Class B is a necessary condition,
  not a sufficient one, and the script says so.
* **Class C** — 8 items the archive map already declares as gaps or as needing a submission
  document, listed so the report accounts for every table instead of the easy ones.

**The single absent value is a real finding, and it changes a status.** SI Table S5a has four
data rows; `data/derived/crosscohort.csv` carries rows 1, 2 and 4 (under different labels) but
**not row 3, the √N_e direct-weighting sensitivity (pooled Z +2.09; Q 76.6; I² 98.7)**. The map
marked S5a ✅ on the strength of row 1 alone. It is now **🟡**, with the three reproducible rows
named and the fourth identified. Distribution: **19 ✅ / 13 🟡 / 5 🔴 / 9 ➖**.

Three classes of apparent mismatch turned out to be conventions, not data, and the comparator
now encodes them — each was worth 30–84 phantom cells: the documents print `—` where the CSVs
leave a field empty (Table S3); they print `Non-candidate` where the CSV holds `NonCandidate`
(Table S4); and Table S23 prints the **denominator** of a `matched/total` field, not the
numerator — which is easy to miss because for ACTB the two coincide (`23/23`) while CKAP4 prints
659 against `633/659`.

Also fixed: `paths_config.si_tables()` documented `object i = Table S(i+1)`, which is **false**.
The submitted SI splits Table S5 into two table objects (S5a, S5b), so the rule holds only up to
the fourth object — `si_labels()[6]` is `'S6'`, not `'S7'`. Nothing depended on it, but a caller
trusting it would have read the wrong table. `si_labels()` and `si_table_by_label('S5a')` now
address tables by caption, which is what the existing diagnostics were really doing.

### 2026-10-02 (fifth pass) — the last two caveats, one closed and one made specific

**No reported number changes.** S9's published values, and every other value in the Supporting
Information, are untouched. What changes is that one of the two remaining "you cannot re-run
this" statements is now false, and the other is now measured.

**S9 — closed, not merely declared.** The row said `clone (outcome)`: the published numbers
reproduce from a clone, but re-deriving the pools needs the mashr model databases, which this
archive does not distribute. That framed the wrong thing as the obstacle. The pool filters read
**one column** out of those 10.5 MB of SQLite — `n.snps.in.model`, per gene, for two tissues —
so the dependency was reduced to what is actually used and shipped as
`data/derived/mashr_nsnps.csv.gz` (61 kB; 16,812 symbols × 2 tissues). `build_pools()` now
reads the projection, and it was run with **every** source variable unset:

```
POOL_A chain: WB model genes 12,622 -> minus 104-panel 12,555 -> minus panel families 11,885
              -> minus disease blacklist = POOL_A 11,820 -> of which have BOTH-tissue models 10,450
POOL_818 = 818 (published 818), both-tissue 767 (published 767), WB-only 51 (published 51)
```

Every published figure of the chain, and the four pool files it writes came out
**byte-identical** (`git status` clean afterwards). `REPRO_MASHR_DB_DIR` is no longer needed to
re-derive anything: set it and `load_model_snps()` reads both databases *as well* and refuses to
continue unless every gene and count agrees — verified by changing one count in the projection
and confirming it reports `1 value(s) differ`. S9's locality label is therefore `clone`, and the
`clone (outcome)` label was retired: it existed for that single row and an unused category
invites the reader to hunt for the row it belongs to.

Two false dependencies were removed on the way. `build_pools()` and `copy_small()` still
demanded the *external* originals for `covariate_matrix.csv`, `Human_Mouse_Common.csv`,
`groups.json` and the three random-control files even though those ship — so the derivation
refused to run from a clone after the data layer had landed. They now prefer the shipped copy.
`copy_small()` also used raw `shutil.copyfile` on files `.gitattributes` declares `eol=lf`, which
is the same defect as the CRLF hash table: a plain copy of a CRLF source produces a shipped input
whose MD5 can never match. It uses `copy_lf`.

**S17 — the caveat is now measured rather than inherited.** The row said the gene-cluster half
needs "the housekeeping layers carried in SI Tables S6/S15". Checked, and it is
narrower and more interesting than that. The five `repo_crosscheck/verify_cluster*.py` scripts
read only `data/derived/primary_arm_96pairs.csv` and **do reproduce from a clone**. The
gene-cluster rows are one script, `bmc_ref/verify_s17_cluster.py`, and it reads four SI tables
from the `.docx`: t02 = S3, t06 = S6, t15 = S15, t18 = S18. Three of those four are redundant in
principle — S3 is `data/derived/gtex_Z.csv`, S15 and S18 are the `Group` column of
`data/derived/eqtlgen_Z.csv`. **Only t06 = S6 is genuinely absent**, and it cannot be recovered
from `gtex_Z.csv` because the housekeeping genes are excluded from the 74-gene panel by that
panel's own pre-specified rules — measured overlap **0 of 30**. The z-scores are *not* the
obstacle: the shipped wide table carries 29 of the 30 (TUT1 absent). The obstacle is the
combination rule into an ACAT-O p-value, and it is **not recovered**: recombining those
z-scores by the textbook Cauchy/ACAT-O recipe misses the published values on the *candidate*
genes, where ground truth exists (ACTB/DR: published 0.2085, recomputed 0.2116). That route is
closed until the rule is established, and saying so is more useful to a reader than "needs the
SI". The row keeps `clone + SI`, now for a reason someone can check.

**S20 is unchanged and still `clone + SI`** — its generator `m15_pc.py` reads three tables out
of Additional file 1 by position, and shipping those values is a decision about redistributing
submission content, not a reduction like the one above. It is left as it stands.

Distribution is unchanged: **20 ✅ / 12 🟡 / 5 🔴 / 9 ➖**. The locality vocabulary is now four
labels — `` `clone` `` (28 rows, was 27), `` `clone + SI` `` (2), `` `none` `` (7), `` `—` `` (9).

### 2026-10-02 (fourth pass) — checks that can fail, and a map that checks itself

**No reported number changes.** The data layer, the estimators and every value in the
Supporting Information are untouched. What changes is whether the repository can tell when
something *has* changed.

Three questions drove this pass. Each produced a defect that had been passing review.

**1. Can the archive prove a reader gets what we claim?** Not from here. Four defects have
shipped from a green pre-flight: a path bootstrap one directory level short (it compiles,
then dies at run time), a hash table recording CRLF values for files a clone checks out as
LF, a manifest hashing the working tree, and a rebuild writing a shipped input with the
platform's line ending. Every one of them passed on the machine that produced it. The checks
now run where the reader is:

- **`scripts/verify_from_clone.sh`** — makes a `git clone --no-hardlinks` into a temp
  directory and runs every check inside it, including a CRLF sweep of the checked-out tree.
  It is the definition of "it passes". `docs/RELEASE_PROCESS.md` §1 now requires it
  alongside `cut_release.sh`, and `cut_release.sh` says in its own header why it is not
  sufficient on its own.
- **`scripts/verify_provenance.py`** — recomputes every SHA-256 and byte count in
  `metadata/provenance.json` from the index, and compares. Until now nothing re-checked the
  manifest: `cut_release.sh` confirmed only that it was valid JSON and free of placeholders.

**2. Can a check fail?** Four could not.

- `paths_config.py`'s shipped-input self-check printed its verdict and **exited 0 either
  way**, so no gate could rely on it. It now exits non-zero, and `cut_release.sh` calls it.
- `check_wiring.py` gained **`--self-test`**: it runs itself against two probes of its own —
  one wired correctly, one stopped a directory short — and fails unless the first passes and
  the second is caught. That checker was vacuous once (its own directory was on `sys.path`,
  so every script "passed"), and a gate nobody has watched fail is not a gate. The
  demonstration is now part of every release.
- `check_wiring.py` also grew into a round trip: the wiring-package rebuild now writes
  `s9_pools/disease_blacklist.txt` through `write_lf()`. It was written with the default text
  mode, which translates `\n` to `os.linesep` — so **rebuilding the package on Windows broke
  the package's own integrity check**, producing a CRLF file whose MD5 did not match the LF
  value recorded in `paths_config.SHIPPED`. Reproduced, fixed, and re-verified by writing the
  file both ways.

**3. Is `metadata/ARCHIVE_MAP.md` checked at all?** It was checked by eye, and eyes stop
checking. Three defects were sitting in it:

- The `Input locality` column — added exactly to separate "verified" from "checkable by
  you" — had been written into the rows but **not into the table headers**. Markdown
  renderers drop cells beyond the header, so the column that protects the manuscript's
  conclusions was invisible in the rendered file while looking present in the source.
- An unescaped `|` inside a cell (`(\|Z\| density)`) split one row into extra cells, shifting
  every value in it one column to the right.
- The summary line is hand-maintained and had already drifted once (it read 16 ✅ / 13 🟡 /
  9 🔴 / 8 ➖ against a table holding 12 ✅ and 12 🔴).

  **`scripts/check_archive_map.py`** now enforces the column declaration, every row's cell
  count against its header, the summary counts against the status column, and a controlled
  vocabulary for the locality labels. `cut_release.sh` runs it. It was verified by
  re-introducing all three defects and confirming each is reported.

**The map now states the two axes explicitly.** The tables previously answered "is the value
right?" and "can I re-run it?" with a single mark, which is how both went wrong. `Status`
now answers only the first; `Input locality` answers only the second, from a defined
vocabulary — `` `clone` ``, `` `clone (outcome)` ``, `` `clone + SI` ``, `` `none` ``,
`` `—` `` — and the Status key says plainly that **a locality label is not a doubt about the
value**. S9 stays ✅ (the published numbers reproduce from a clone without either the mashr
databases or the original GTEx × FinnGen tables) with `clone (outcome)` recording that
*re-deriving the pools* is not possible from this archive. S16 is ✅ `clone`. S17 and S20 are
✅ `clone + SI`. Distribution is unchanged at **20 ✅ / 12 🟡 / 5 🔴 / 9 ➖**.

### 2026-10-02 (third pass) — guard rails, a self-contained check, and one convention still owed

The second pass made the package runnable and shipped the data layer. This pass adds the checks
that keep it that way, and records the two things a reader is still owed.

#### Added
- **`code/analyses/reproduction_min/`** — a single ~180-line script needing only `data/derived/`
  and numpy: no argument, no `.docx`, no network. It reproduces the headline 66/96 = 68.75 % and
  ρ = 0.38964, the per-phenotype split, the tissue-only arm (138 · 91 · 65.9 % · +0.4138) and the
  three SCZ arms (5,584 · 5,551 · 5,506 at +0.4690 · +0.4199 · +0.4465), with **15 assertions and
  0 mismatches**. It is the only 100 %-self-contained reproduction in the archive: before it, a
  reader with a bare clone could not verify a single reported number.
- **`code/analyses/reproduction_20261002/check_wiring.py`** — executes every script's import
  preamble and fails if `paths_config` is not importable. Each script carries its own
  bootstrap, and a bootstrap with the wrong depth compiles cleanly and dies at run time; 24
  scripts shipped that way in the first portable revision. The check stubs third-party modules
  it lacks, so it runs under a bare Python, and it strips this file's own directory from
  `sys.path` so it cannot pass vacuously. Called by `scripts/cut_release.sh`, which now also
  fails the release if `reproduction_min` stops reproducing under an interpreter that has numpy.
- **Table-note text for SI Table S24** in `docs/audit_notes/R2残余差异消除方案_20261002.md` §五
  item 7, with the measurement behind it: `multiZ` carries **77 exact zeros** among the 8,315
  complete-case genes; scoring a zero as positive moves the dual arm from 5,506 to **5,544**
  (+38 pairs, **+0.46 pp**), and the other two arms by +1 and +5.

#### Changed
- **The whole tree is normalised to LF.** `.gitattributes` already declared `eol=lf` for source,
  Markdown and JSON; `*.csv`, `*.tsv` and `*.txt` are now listed too. Without this a Windows
  working copy differs byte-wise from a Linux one, and `metadata/provenance.json`, which records a
  SHA-256 per file, would verify on one platform and fail on the other. The committed blobs change
  once; nothing else does.
- **`paths_config.SHIPPED_SPEC` recorded the wrong hashes — 11 of the 20 shipped inputs failed their
  own check in a clone.** The table mixed two conventions: the older entries carried the LF hashes of
  the checked-out files, the newly added ones carried the CRLF hashes of the author's originals. The
  two differ by exactly one byte per line. Consequence: `python paths_config.py` reported *all
  shipped inputs present and byte-exact* on the machine that built the package and reported
  **11 `MD5 MISMATCH` for anyone who cloned it** — i.e. the package's integrity mechanism, added to
  make the archive verifiable, failed precisely for the people it was meant to protect. Found on
  2026-10-02 by cloning `--no-hardlinks` and running the self-check inside the clone; all values are
  now the checked-out ones and the table carries a note saying to re-record them only from a clone.
- `scripts/collect_provenance.py` hashes **every tracked file** (previously three hand-picked
  directories, 36 files against a tree of 281) and records the non-redistributed reproduction
  inputs separately, with their SHA-256. `scripts/cut_release.sh` asserts
  `len(files) + len(excluded) == git ls-files`.
- `metadata/ARCHIVE_MAP.md` §8 records the re-audit that produced all of the above, including the
  one row where the mark and the reality can differ: read the **Input locality** column, not the
  mark, when you want to know whether *you* can check a row.

#### Verification
- **S16 reproduces from a clone**: all nine framework-layer rows re-run and match.
- **Table S9 reproduces from a clone without the mashr databases** — verified with
  `REPRO_MASHR_DB_DIR` unset. The pool membership ships as `data/derived/s9_pools/*.txt`, and the
  official GTEx × FinnGen layer ships flattened, so the exclusion chain 12,622 → 11,820, POOL_818
  = 818/767/51, coverage 568/768, the 16 random-control rates, the 8 null-distribution values and
  the 4 percentiles all reproduce. Re-*deriving* the pools still needs the mashr models; that is
  `00_build_added_derived.py`, not the reproduction, and it is stated on the row.
- **The BMC↔GE cross-check was re-run rather than asserted**: 83 statistics cross-checked, 63
  present in both documents, 20 in the predecessor only, **0 unique to the GE submission**. The
  predecessor *Additional file 1* carries 27 tables against the GE *Supporting Information*'s 31 —
  the `S`*n* → `S`*n+1* renumbering.
- The predecessor repository was cloned to check the `processed_officialZ/` → `derived/` mapping:
  **6 of 6 files identical line for line** (the predecessor stores them with CRLF, so its recorded
  MD5s differ from this archive's LF ones by exactly one byte per line). `code/analyses/reproduction_20261002/INPUTS.md` §A.1 records it
  as a measurement rather than an inference.
- All 18 diagnostic scripts exit 0.

#### Numbers
- **No reported number changes.** This pass adds checks, documentation and a self-contained
  reproduction script; it normalises line endings, which changes file bytes but no value.

### 2026-10-02 (second pass) — make the reproduction package runnable, and its inputs explicit

A review of the first-pass package found that it could not actually be run by anyone
else: its 35 scripts carried 26 distinct absolute paths from the author's machine, none
of them pointing at this repository, and the files they read were not committed. This
entry is the repair.

#### Fixed
- **No absolute paths remain.** Every script in `code/analyses/reproduction_20261002/`
  now resolves its inputs through `code/analyses/reproduction_20261002/paths_config.py`,
  which walks up to the repository root (sentinel `.zenodo.json`), honours `TWAS_REPO`
  and `TWAS_DATA_Z` — the same variables `code/figures/paths_config.py` uses — and
  accepts `--repo-root` / `--ms-docx` / `--si-docx` / `--af1-docx` / `--mashr-db-dir` /
  `--gtex-official-dir`. `code/README.md` rule 3 requires this and the first pass broke it.
- **Scripts no longer claim to accept a path argument without accepting one.**
  `recompute.py` and `recompute_scz.py` previously hard-coded the two documents while the
  package README said they "take a path argument".
- `scripts/recompute_scz.py` reads the gzipped Z layers through
  `paths_config.open_text()`, and records the MD5 of the **decompressed** bytes for those
  inputs so an input's recorded hash no longer depends on the compressor.
- `metadata/provenance_source.json` pointed `superseded_by` at
  `data/processed_officialZ/`, a directory that does not exist in this repository. Now
  `data/derived/`.
- The Supporting Information is read directly from the `.docx` by
  `paths_config.si_tables()`. The `tNN.tsv` files the diagnostic scripts used to read had
  never been committed.
- Three diagnostic scripts could not run at all, independently of the path problem, and
  are fixed here: `repo_crosscheck/verify_cluster3.py` built a 0-d array from a generator
  inside `np.where`; `repo_crosscheck/verify_cluster4.py` indexed a position-list with gene
  names; `r3/diag_s9_s20b.py` exec'd a preamble whose `__file__` pointed at the working
  directory rather than at the sibling script. Every script in the package now exits 0.

#### Added
- `code/analyses/reproduction_20261002/paths_config.py` — the single path entry point
  (repository-root discovery, an input registry with per-file MD5s, `si_tables()`
  extraction, and an actionable message instead of a traceback when a document is absent).
- `code/analyses/reproduction_20261002/INPUTS.md` — every input: logical name, path, MD5,
  byte count, which script reads it, whether it ships here, and where to get it if not.
- `code/analyses/reproduction_20261002/00_build_added_derived.py` — rebuilds each derived
  table added below from the upstream source that produced it.
- **3.7 MB of derived data under `data/derived/`**, so that the two largest gaps are
  closable from a clone:
  - `derived/genomewide/` — the five genome-wide weight-source Z layers, gzipped
    (2.8 MB). These define every analysis universe and the framework-layer contrast
    (S16); before this addition the framework layer was not reproducible from this
    archive at all.
  - `derived/gtex_official_finngen/gtex_official_zscores_wide.csv.gz` — the official
    MetaXcan GTEx × FinnGen layer flattened to one row per gene (0.7 MB), which feeds the
    Table S9 ACAT-O chain without its 12.3 MB of originals. Z-scores are stored as the
    original strings, not reformatted, so the median-|Z| statistics keep their digits.
  - `derived/s9_pools/`, `derived/hrt/`, `derived/hrt_random_control/`,
    `derived/groups.json`, `derived/covariate_matrix.csv` — 12 small files (0.2 MB)
    carrying the Table S9 pools, strata and random controls.
- `data/processed_officialZ/README.md` — a pointer, so the ~40 remaining references to the
  retired path (mostly under `code/deprecated/`) read as *retired* rather than *dangling*.
- `results/README.md` — separates the files a script writes from the transcripts of the
  diagnostic scripts, and says which is which.
- `results/recompute_r3_s9_s20_log.txt` — the run log the S9/S20 script declares but which
  the first pass did not commit.

#### Removed
- `scripts/r3/_patch_r3.py`, `scripts/r3/m15/_patch.py`, `scripts/r3/m15/_patch_r3.py` —
  one-off local patchers that rewrote sibling source files in place by string replacement
  and carried machine paths. Build artefacts, not deliverables.

#### Changed
- `metadata/ARCHIVE_MAP.md` — the six reproduced rows now state **where each input lives
  and whether it ships**, so ✅ is a claim a reader can check. A new section records the
  added data layer.
- `data/README.md` — the new derived tables are listed with their row counts, and the
  directory table now explains `derived/genomewide/` and the retired `processed_officialZ/`
  name.
- `code/analyses/reproduction_20261002/README.md` — the three inaccurate claims removed,
  the run instructions rewritten around `paths_config.py`, and a "what reproduces from a
  clone alone" table added.

#### Verification
- A clean copy of the tree at a different path, with no `.git` and no author directories,
  was run end to end with only the repository contents plus the two journal documents.
  `recompute.py`, `recompute_scz.py`, `recompute_r3_s9_s20.py`, `simulation_validation.py`
  and `m15_pc.py` all completed, and their machine-readable outputs match the committed
  ones key for key. The Table S9 numbers reproduce **without** either the mashr databases
  or the six original GTEx × FinnGen tables.

#### Numbers
- **No reported number changes.** This entry changes where inputs live and how they are
  named; it adds derived tables that were previously absent; and it removes three build
  artefacts. Every value the manuscript and its Supporting Information report is
  unchanged, and the re-run outputs are byte-for-byte equal to the committed results apart
  from input-file hashes.
- One incidental finding, recorded because it explains a count rather than a value:
  `data/derived/s9_pools/disease_blacklist.txt` is stored **without case normalisation**,
  faithfully to the published pipeline. The gene sets it is subtracted from are upper-cased,
  so the single token that is not already all-caps — `C5orf67` — excludes nothing. That is
  why POOL_A holds **11,820** genes and not 11,819, and `both_A` 10,450 and not 10,449.
  The published numbers are correct as printed; the exclusion step simply does not act on
  that one gene. Recorded in `code/analyses/reproduction_20261002/INPUTS.md` section F and
  in `data/README.md`.


### 2026-10-02 — third-party reproduction of both submitted documents

#### Added
- `code/analyses/reproduction_20261002/` — a self-contained reproduction package (61 files, ~3,450 lines of Python) that recomputes every value readable out of `Manuscript_GenetEpidemiol_20260930.docx` and `Supporting_Information_GenetEpidemiol_20260930.docx` from `data/derived/` and the two documents. Layout and run order in that directory's `README.md`; every script prints the MD5 of its inputs on its first line.
- `docs/audit_notes/复现核验_GE投稿两份文档_20261002.md` — the full account. Grade: **R1 ≈ 200 items identical at the reported precision, R2 = 3, R3 = 0**. No reported value failed to reproduce and none was found to differ in its point estimate.
- `docs/audit_notes/BMC定稿与GE投稿值域交叉核对_20261002.md` — the two documents against the predecessor 2026-09-28 final manuscript: 63 comparable headline statistics all identical, none unique to the new documents. Also establishes that the predecessor's *Additional file 1* and the current Supporting Information are the **same document under two numberings** (Table S*n* → S*(n+1)* for n = 1–25, plus the new S27–S30).
- `docs/audit_notes/R2残余差异消除方案_20261002.md` — remediation for the three residual items, with paste-ready SI note text.
- `code/analyses/reproduction_20261002/scripts/r3/m15/m15_pc.py` — **the missing generator for SI Table S20** (`code/figures/m15_positive_control.json` lineage), recovered verbatim.

#### Changed
- `metadata/ARCHIVE_MAP.md` — eight items moved to ✅: SI Tables **S9, S16, S17, S27, S28, S29** and **Note S5** (🔴 → ✅), and main-text **Table 2(B)** (🟡 → ✅); **S20**'s evidence row now names the recovered generator. GAP-3, GAP-5, GAP-7, GAP-9 and GAP-10 are closed. Distribution is now **20 ✅, 12 🟡, 5 🔴, 9 ➖**.
  - The status counts are now produced by a machine count of the status column. **The line previously read "16 ✅, 13 🟡, 9 🔴, 8 ➖", which did not match the table beneath it** — that table in fact held 12 ✅ and 12 🔴. Corrected here rather than carried forward.
  - Two internal cross-reference errors fixed: the Note S5 row cited "GAP-4", which the register reserves for Figs. S1 and S2 (it is GAP-5); and the S20 row described the JSON as its own carrier, which is what allowed the missing generator to go unnoticed.
- `docs/audit_notes/INDEX.md` — three rows added.

#### Numbers
- **No reported number changes.** This commit adds a reproduction package, three audit notes and the recovered S20 generator, and moves archive-map statuses to reflect what has now been reproduced. Every value the manuscript and its Supporting Information report is unchanged. The three residual R2 items are rounding-chain or undisclosed-parameter differences, not value differences; the largest is 0.04 percentage points.

### Added
- Repository consolidated as the single canonical archive for this study; full development history carried over from the predecessor repository, so the pre-specification anchors `58da15b` (2026-07-24) and `e70806b` (2026-09-10) remain reachable in this tree.
- `metadata/ARCHIVE_MAP.md`, `metadata/PRE_REGISTRATION.md`, `metadata/provenance.json`.
- `docs/RELEASE_PROCESS.md` and `scripts/cut_release.sh`.

### Changed
- Archive map re-keyed to the current Supporting Information numbering (Tables S1–S30). The predecessor `ARCHIVE_NOTE.md` used an older Additional-file numbering and is **not** carried over.
- Archive map verified item by item against `Supporting_Information_GenetEpidemiol_20260930.docx` (2026-10-02): every one of the 46 items now carries a status backed by a table title, header, column/row count or an actual cell value. The status key gained a fourth state — 🟡 **DERIVABLE** (inputs present and verified, producing step not shipped) — so that "we hold the inputs" is no longer conflated with "we can reproduce the table".

### Fixed
- `data/derived/s1_anchor_102pairs.csv` and `data/derived/s1_primary_arm_96pairs.csv` were **mis-filed in the authoritative layer**. Their ANXA1/DR values are 1.2913 / 2.1391; the authoritative table has 0.4283 / 0.9302. Their row counts (102, 96) happen to look right, which is how the error survived. Both are v2.5.0-generation output and now sit in `data/superseded/s1_cluster_robustness/`.
- The archive map no longer claims that `figures/` holds the figure files. **The repository contains no figure files** — `figures/` holds only its README; what is shipped is the *scripts* that produce some of the panels.

### Added
- `code/analyses/recovered/` — three scripts recovered from unarchived session working directories, copied verbatim. `tost_ci_calculator.py` and `tost_and_newcombe.py` were **run and reproduce the published values** (Newcombe 90% CI −9.7 to +15.4 for GTEx and −13.3 to +12.6 for eQTLGen; TOST p = 0.181/0.060/0.014 and 0.116/0.034/0.007). `scz_arm_recount_si_fix.py` recomputes from the archived four-arm SCZ table.
- `code/deprecated/si_editors/` — seven `.docx`-patching scripts, also recovered verbatim, with a README explaining the pattern they expose.
- `scripts/collect_provenance.py` — regenerates `metadata/provenance.json`; hashes the 36 files that back a reported number and records the external-input manifest.
- `metadata/provenance.json` rewritten: **36 files hashed**, 8 external inputs with identifiers, versions and the retrieval date from Supporting Information Note S4, and **no placeholders**.
- `data/README.md` external-input manifest filled from Note S4 — every resource **retrieved 2026-09-08**; software versions (official MetaXcan v0.8.1, Python 3.13.0, R 4.5.2 + MatchIt); and the GCST90043640 citation (Jiang et al. *Nat Genet* 2021;53:1616–1621, doi:10.1038/s41588-021-00954-4). External hashes are recorded as `not-held` rather than invented — nothing here claims hash verification that did not happen.

### The finding that matters more than the recovery

Several of the surviving scripts are **not computations at all**. `apply_d2_fixed_threshold.py`, `apply_d3_genomewide_control.py` and `apply_s11_hrt_restricted.py` carry their SI values as **hard-coded English prose literals** and read no data — e.g. `"...reached an FDR enrichment of 69.1% (56/8..."`. The workflow was: compute elsewhere (uncaptured) → paste the numbers into a `.docx`-patching script → write them into the Supporting Information.

So several gaps are **not** "the script got lost". The number was pasted in from something never captured. Searching for a missing script will not close them; the value has to be re-derived. Recorded in `metadata/ARCHIVE_MAP.md` §5.

### Known gaps (declared, not hidden)
- **5 items are marked 🔴** in `metadata/ARCHIVE_MAP.md` as of 2026-10-02: SI Table **S6**, SI Table **S10**, **Figs. S1 and S2**, and the value row of main-text **Table 1**. (This line previously read "9 items" and listed S9, S11, S16, S17, S27, S28 and S29 among them; S9, S16, S17, S27, S28 and S29 are now ✅ — see the 2026-10-02 entry above.) **S7 has moved from 🔴 to 🟡** — its TOST/Newcombe half is now recovered and verified; its "Smallest margin attained" column is not.
- **GAP-1 (SI Table S6) is now diagnosed, and the fault is the repository's, not the Supporting Information's.** The housekeeping Z layer here was computed on **2026-08-30**; the σᵢ correction landed **2026-09-17**. Reading the Table S6 block out of all 93 archived copies of the supplementary file and ordering them by mtime shows the published values changed between 2026-09-16 22:24 and 2026-09-17 19:15 — inside that window. Corroborating: every changed value shrinks |Z| and moves the ACAT-O P toward 0.5; 22 of 30 genes change by a constant per-gene ratio (a per-gene multiplicative correction); the model-SNP column is unchanged for all 30.
  → **`data/derived/hk_reselect/` was moved to `data/superseded/hk_reselect_20260830/`** with a full notice. The housekeeping arm of main-text Table 1 is therefore **not reproducible from this archive**.
- **Still open on GAP-1, and deliberately not closed by assumption:** 8 of 30 genes (`DNAJC4`, `E2F4`, `GOLGA3`, `SDF4`, `SRM`, `TOMM20`, `SPRYD3`, `TUT1`) do **not** follow a constant ratio, and `GOLGA3` flips sign at DPN — a pure σᵢ rescale cannot do that. The corrected computation is not archived anywhere on disk. Because it differs from the archived one by more than the σᵢ factor, SI Tables S7, S19 and S26 — which aggregate the housekeeping arm — should be re-checked against the corrected layer before submission.
- The generating scripts for the missing tables exist on the local disk only inside unarchived session directories (`2026-09-22-14-24-45/work/si_fix.py`, `2026-09-11-19-30-45/apply_d2.py`, `2026-09-11-18-13-13/_apply_edits.py`, …). They are recoverable, but nothing has been copied in yet.

### Numbers
- **No reported number changes.** This commit moves two mis-filed files out of the authoritative layer, corrects documentation, and declares gaps. Every value the manuscript reports is unaffected.

---

## [4.0.0] — 2026-10-02

### Added
- First release of the consolidated archive: analysis scripts, processed derived data, containerised environment, and archived figures.

### Numbers
- **No reported number changes in this release.** This release re-hosts the same analysed content under the canonical repository and updates metadata and repository layout only.

### Migration notes
- History imported from `wu-yijing/twas-eqtl-source-discordance`; predecessor tags were **not** imported, so `v1.0.0`–`v3.0.0` remain only in the archived repositories.
- Cite this study as concept DOI `<CONCEPT>`; for the analysed snapshot cite `10.5281/zenodo.<VER>`.

---

[Unreleased]: https://github.com/wu-yijing/eqtl-source-discordance/compare/v4.0.0...HEAD
[4.0.0]: https://github.com/wu-yijing/eqtl-source-discordance/releases/tag/v4.0.0

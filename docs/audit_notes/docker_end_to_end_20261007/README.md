# The recommended Docker path, run end to end

**Date:** 2026-10-07 · **Repository HEAD:** `47a0935` + this note, packaged as the commit
`logs/24-…` documents (§0.6)
**Question this note answers:** `env/Dockerfile` is the environment this archive recommends.
Does it actually build, run, and reproduce every reported value and figure — and what can it
not do?

**Short answer:** it builds (EXIT=0), it runs (EXIT=0), and the values and figures reproduce.
Getting there exposed **eight defects, six of which are invisible unless the thing is
executed** — including one that had never been built at all and one whose failure was
reported as a success. The list is in §3; the limits that remain are in §4. Assembling this
record then found **two more of exactly the same shape in the note's own tooling** — a step
that ran clean and was reported as a skip, and an image identity replaced by a template error
(§0.3).

---

## 0. Packaging record — 2026-10-07

The note, the logs and the evidence under `results/` were assembled into the repository in
two passes on 2026-10-07: the first with **no Docker daemon on the packaging host**, the
second after the daemon was restored. This section records the packaging step itself, because
it produced two defects in this note's own tooling (§0.3) and one correction to what the
first pass wrote down (§0.4).

### 0.1 What ships

| Item | Provenance |
|---|---|
| `logs/01…23` | the run, verbatim: six build attempts and the probe that identified defect 3, the pipeline runs (default, full, the entrypoint trap and its correction), the main-figure runs, the final-image runs, the two host references and the clone gates |
| `logs/25…28` | added at packaging time — the rebuild, its run, the rebuild after the defect-9 fix, and its run (§0.3, §0.5) |
| `logs/24-…` | the gate suite re-run at packaging time (§0.6) |
| `COMMANDS.md` | every command, in order, each with the log it produced |
| all five files under `results/` | written by `bash scripts/make_evidence.sh` against the image of §0.2 — derived, not copied |

### 0.2 The image every number here was measured on

`eqtl-discordance:latest` · `image_id sha256:a8b0ae74e0c1…` · built `2026-10-07T07:03:43Z` ·
`3,826,567,401` bytes · `ENTRYPOINT ["/bin/bash", "/app/code/run_all.sh"]` · `working_dir /app`.
`results/image-fingerprint.txt` records this in full, together with the base-image digest
`env/Dockerfile` pins, resolved against the registry rather than taken on trust, and
`results/inside-image-verification.txt` records the same image from the inside: Python 3.13.12
and R 4.5.2, all eleven declared Python dependencies importable, `MatchIt 4.5.5 + optmatch
0.10.6 + cobalt 4.5.2` loading, gate 13 and the three other validators passing, and step 4's
format precheck exiting 0 with `有问题的图： NONE`.

### 0.3 Two defects the packaging step found — in this note's own tooling

Both were found by **executing** the packaging code, not by reading it, and both are the same
shape as the eight in §3: a check that reports the wrong verdict.

| # | Defect | How it announced itself | Fix |
|---|---|---|---|
| 9 | **`code/run_all.sh` reported a clean step 4 as a skip.** The §3.7 fix tested `grep -q '有问题的图：NONE'`, but `11_figure_precheck.py` prints the verdict with `print('有问题的图：', problems or 'NONE')` — one space more. The match never fired, so a clean precheck fell through to `[skip] … ran and reported figure(s) outside the format limits`, which is the opposite of its result | `logs/26-…`: step 4 runs for the first time, prints its table with `有问题的图： NONE`, and is reported as a skip | compare with whitespace stripped (`tr -d '[:space:]'`) instead of guessing the separator; the same run then reports `[ ok ]` — `logs/28-…` |
| 10 | **PART 1 of `scripts/make_evidence.sh` shipped an empty image identity.** Its `docker image inspect --format` referenced `{{.Config.Cmd}}`, and this image sets no `CMD`. Docker renders these templates with `missingkey=error`, so the absent key aborted the whole inspect — id, size, created time and entrypoint were all replaced by a template error | the first `results/image-fingerprint.txt` had a `template parsing error` where the identity table belongs | read every `Config` field through `index .Config "…"`, which yields the zero value for an absent key instead of erroring |

Neither changes a reported number; both are recorded because a fix without the failure it
fixes is only an assertion, which is this note's own standard.

### 0.4 A correction to the first pass

The first pass recorded that the post-`pymupdf` rebuild "was not taken". **That was wrong**,
and the packaging step found it by measuring: the image already on the host carries
`pymupdf 1.27.2.3` — `docker run … python3 -c "import fitz"` succeeds on it — so the rebuild
had in fact run earlier on 2026-10-07, and only its log failed to survive. The first pass
inferred "not run" from an absent log while the daemon was down and could not check. With the
daemon up, the rebuild was re-run against the whole current tree (`logs/25-…`), the image
identity captured (`results/image-fingerprint.txt`), and the tree rebuilt once more after the
defect-9 fix (`logs/27-…`). `COMMANDS.md` §2's row 8 is restored accordingly.

### 0.5 The figure evidence was re-derived on the rebuilt image, and did not move

The three font conditions were re-run against the rebuilt image. Every output is
**byte-identical** to what the earlier image produced — `Figure_1.png` `010a174514cdec30…`
with Arial, `a2320405442606e1…` with nothing supplied, `edd3d94978a76d55…` with
`fonts-liberation` — so §4.3's table and `results/figure-verification.txt` describe the
rebuilt image exactly as they described the previous one. That is the answer to "does adding a
dependency change the figures": it does not.

### 0.6 The gate suite re-run at packaging time

`logs/24-clone-gates-at-the-packaged-commit.log` is the 14 gates run against a fresh clone at
the packaging commit: **0 failures, 0 skipped**, "Safe to publish". Gate 13 there reports
**16** audit-note directories where `logs/23-…` (taken at `47a0935`) reported 15, gate 3
`576 / 577` where it reported `545 / 546`, and gate 11 577 files — the three gates whose
numbers the packaging step itself moves. The commit that *carries* this log is one later than
the commit it describes, because the gate script clones `HEAD` and a log cannot be inside the
commit it documents; `COMMANDS.md` §5 already states that off-by-one. Gates 3 and 13 were
therefore also re-run **directly against the final staged tree**, not only inside the clone.

**What this does not change.** No reported number. Headline values (C4), the figure
comparisons including the §4.3 font table (C6) and the 14 clone gates (C8) were all
re-derived at packaging time rather than copied, and the two packaging defects (§0.3) were in
the checks, not in the pipeline they check.

---

## 1. What "跑通" means here — the exit criteria

The word is only useful if it is checkable, so it is defined as nine conditions. A run counts
as 跑通 when **all of C1–C8 hold and C9 is honoured**.

| # | Criterion | Why it is in the list |
|---|---|---|
| **C1** | `docker build -f env/Dockerfile .` exits 0 from a clean checkout, and the build asserts the pinned R stack (`MatchIt 4.5.5` + `optmatch 0.10.6` load) | a build that is only *asserted* to work is the state this archive was in until 2026-10-06 |
| **C2** | Every invocation documented in `env/README.md` and `README.md` completes exit 0 | a documented command that does not work is worse than an undocumented one |
| **C3** | Every step of `code/run_all.sh` **executes**. A step may be reported skipped only when the reason is printed and it is a declared external dependency | §3.7 is what happens when a step's non-execution is reported as a benign skip |
| **C4** | The headline values are recomputed **inside the container** and agree with the submitted documents at the reported precision | the container must not be a different pipeline from the one that made the paper |
| **C5** | Steps 3b and 3c pass in the container (SI Table S5a row 3; SI Table S4 candidate order) | the two checks added on 2026-10-06 are part of the pipeline now |
| **C6** | Figures regenerate: SI figures pixel-identical to the committed files; the four main figures pixel-identical **when the font they are typeset in is supplied** | "reproduces the figures" has to survive a platform change; see §5 |
| **C7** | The archive's own validators pass inside the container (`check_audit_manifests`, `check_archive_map`, `check_s4_order`, `check_fig4_hk_source`) | the container should not be a place where the archive's checks are inapplicable |
| **C8** | The 14 clone gates pass against a fresh clone of the pushed commit | the container is one reader of the archive; the gates are the archive's own check |
| **C9** | **Everything the container cannot do is named, with its reason, and none of it is counted as a pass.** | the honesty clause, and the one that carries the most weight: every defect below was a claim that read as satisfied |

---

## 2. Verdict

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Build | ✅ **EXIT=0**, 3.83 GB, `R stack OK: MatchIt 4.5.5 + optmatch 0.10.6` | `logs/06-…`, `logs/07-…`, `logs/25-…` (re-run at packaging time), `logs/27-…`; `results/image-fingerprint.txt` — `image_id sha256:a8b0ae74e0c1…`, `3,826,567,401` bytes |
| C2 | Documented invocations | ✅ both forms EXIT=0 | `logs/18-…` (form 1), `logs/11-…` (form 2) |
| C3 | Every pipeline step executes | ✅ after the fixes in §3.7 and §0.3 — step 4 runs and states its verdict | `logs/26-…` (step 4 runs for the first time; its verdict was mis-reported as a skip — defect 9) and `logs/28-…` (`[ ok ] 11_figure_precheck.py: page size, font type, min point size and dpi all within limits`). Every pre-fix log shows the `ModuleNotFoundError` this fixed: `logs/08-…`, `09-…`, `10-…`, `11-…`, `18-…` |
| C4 | Headline values | ✅ `96 pairs / 68.8 % / rho = 0.3898` — identical to the host and to the manuscript | `results/headline-values.txt` |
| C5 | Steps 3b / 3c | ✅ `[ ok ]` in the container | `logs/18-…`, `results/headline-values.txt` |
| C6 | Figures | ✅ SI 8/8 pixel-identical; main 4/4 pixel-identical **with Arial**, 4.3–9.9 % different without it (quantified) | `results/figure-verification.txt` |
| C7 | In-container validators | ✅ all four pass; step 4's format precheck exits 0 and reports `有问题的图： NONE` | `results/inside-image-verification.txt` — produced inside the image: `MatchIt 4.5.5 + optmatch 0.10.6 + cobalt 4.5.2`, gate 13, `check_archive_map`, `check_s4_order` and `check_fig4_hk_source` all pass. The same four validators also pass in the clone (C8) |
| C8 | 14 clone gates | ✅ 0 failures / 0 skipped | `logs/23-…` (at `47a0935`), `results/clone-gate-summary.txt`, and `logs/24-…` — re-run at packaging time on `5c4defc`, the commit that stages this note |
| C9 | Limits named | ✅ §4 — three things, each with its reason | §4 |

---

## 3. What running it found — eight defects

Ordered by how they announce themselves. Each row was found by executing the path, not by
reading it.

| # | Defect | How it announced itself | Cause | Where it was fixed |
|---|---|---|---|---|
| 1 | **The image had never been built.** | `dockerfile parse error on line 47: FROM requires either one or three arguments` — the build never reached the pull | the pinned tag was recorded as a *trailing comment on the `FROM` line*; BuildKit reads a trailing `#` as further arguments | `env/Dockerfile` (tag on its own comment line) |
| 2 | **No C/C++ toolchain.** | would have failed at the R layer | `renv` compiles Rcpp / RcppArmadillo / cobalt / MatchIt / optmatch from source; the image installed headers but no compiler | `env/Dockerfile` (`build-essential`, `patch`) |
| 3 | **The two-step R remedy collapsed into one step.** | `ERROR: dependencies 'Rcpp', 'dplyr', 'tibble', 'rlemon' are not available for package 'optmatch'` — *after* the patched build was supposed to fix exactly that | `renv`'s default transactional install **rolled back** the twenty packages that had already built when `restore()` stopped at optmatch | `env/Dockerfile` (`renv.config.install.transactional = FALSE`, a dependency safety net, then restore the remainder) |
| 4 | **`renv`'s worker timed out** on the first long run, at 59 minutes, and rolled the layer back | `worker process timed out` | slow first-time compilation of the R dependency chain in the VM | resolved by the layer caching the earlier stages; recorded because it is what made the first 3 hours look like a hang |
| 5 | **`.dockerignore` excluded `*.log`.** | broke `scripts/check_audit_manifests.py` inside the image | 18 tracked `.log` files under `docs/audit_notes/` are hashed by `metadata/provenance.json`; dropping them made gate 13 unable to pass in the container, and nothing in the image said so | `.dockerignore` |
| 6 | **The documented `docker run` command reported success while doing none of what it asked.** | `Figures written to: /app/figures/` — and under `--rm` every figure discarded, exit 0 | the image sets `ENTRYPOINT ["/bin/bash", "/app/code/run_all.sh"]`, so `… eqtl-discordance bash code/run_all.sh` passes the trailing words *as arguments*; nothing executed them | `env/README.md` (two working forms, and why the third is not one) |
| 7 | **Step 4 of the pipeline had never run in the image, and said nothing was wrong.** | `ModuleNotFoundError: No module named 'fitz'` reported as `[skip] precheck reported non-blocking findings` | `PyMuPDF` was declared in **neither** `env/environment.yml` **nor** `env/requirements.txt`, although `code/figures/11_figure_precheck.py` imports it. `run_all.sh` mapped *any* non-zero exit onto the "ran and found advisories" message, and on success printed no verdict line at all | `env/environment.yml`, `env/requirements.txt` (+`pymupdf==1.27.2.3`); `code/run_all.sh` now separates *ran-with-findings* / *could-not-run* / *crashed* |
| 8 | **Manuscript Figure 4 could only be built on one machine.** | `FileNotFoundError: 'E:\workbuddy\GE投稿资料\_修订_20260930\Supporting_Information_…docx'` | `unified_fig4.py` read its housekeeping panel out of the submitted SI, and resolved it through a hardcoded absolute path; `reproduce.sh` never passed `SI_DOCX` | `unified_fig4.py` now reads `data/derived/hk_official_Z.csv` — which **is** SI Table S6, shipped since 2026-10-03 — so the SI is no longer an input at all |

Defects 1, 6 and 7 share a shape worth naming, because it is why they survived: **each one
failed while reporting success.** The parse error at least refused to proceed. The other two
printed a success line and discarded the work (§3.6), or printed a skip that reads as a
completed check (§3.7). `|| true`, a trailing comment, and a catch-all error message are the
three mechanisms; all three are now gone from this path.

Defect 7 was found while assembling this note — by reading the log this note publishes. The
relevant line was in `logs/18-…` the whole time:

```
== 4. Figure format precheck ==
ModuleNotFoundError: No module named 'fitz'
  [skip] precheck reported non-blocking findings
```

---

## 4. What the container reproduces, and what it cannot

Three things cannot be done inside it. None changes a reported number, and none is a defect
in the archive — but each is a limit a reader will hit, so each is stated with its reason and
its remedy.

**4.1 Gate 3 (`scripts/verify_provenance.py`) does not run in a container.**
It compares `metadata/provenance.json` against `git ls-files`, and `.git/` is excluded from
the image by design — shipping a git object store in a reproduction image would be an odd
choice. This is an *applicability* limit, not a defect. Gate 3 runs in the clone (§2, C8).

**4.2 The upstream S-PrediXcan chain cannot run here.**
The image is Python 3.13.12 + numpy 2.4.4; official MetaXcan v0.8.1 predates numpy 2, and
`code/run_upstream.sh` asserts `numpy.__version__[0] == "1"` and stops. The source tree is
fetched so the pinned version is inspectable, and `env/Dockerfile`'s header says in as many
words that S-PrediXcan does not run here. Its environment is
`env/environment-upstream.yml`; the chain's own execution record is
`docs/audit_notes/upstream_chain_closure_20261004/`.

**4.3 The four manuscript main figures need Arial, which cannot ship.**
`code/figures/ge_main/figstyle_ge.py` typesets them in Arial (with `mathtext.rm = 'Arial'`,
so one family is used throughout, which is the journal's requirement). Arial is proprietary
and is deliberately not in the image, so matplotlib falls through to DejaVu Sans. Measured
consequences, and the measured answer to "would a metric-compatible substitute do instead":

| Font resolved | Fig. 1 | Fig. 2 | Fig. 3 | Fig. 4 | Matches? |
|---|---|---|---|---|---|
| **Arial** (mount it) | 0 | 0 | 0 | 0 | ✅ pixel-identical |
| Liberation Sans (`fonts-liberation`) | 1.61 % | 8.03 % | 6.44 % | 3.63 % | ❌ no figure matches |
| DejaVu Sans (nothing supplied) | 4.46 % | 9.86 % | 7.26 % | 4.29 % | ❌ no figure matches |

Percentages are differing pixels against the host reference. `fonts-liberation` improves
Figure 1 markedly and the others barely, and makes none of them match — which is why it is
**not** added to the image: it would buy a better-looking failure for a full image rebuild.
`reproduce.sh` reports which font it resolved *before* it compares anything, so a font
substitution can no longer be read as a data or code difference. Mount recipe:
`code/figures/ge_main/README.md`.

> The SI figures (`code/run_all.sh`) are unaffected: they are typeset in DejaVu Sans, which
> the image has. That is why 8/8 of them are pixel-identical with no extra step.

---

## 5. Why a byte comparison is the wrong check off the producing machine

This is the one thing that looks like a failure and is not, so it is measured rather than
argued. Running the same pipeline on two platforms:

```
run_all.sh on the Windows host  ->  figures/*.png byte-identical to the committed files
run_all.sh inside the image     ->  every .png DIFFERENT, sizes off by ~2 %
```

Every image is **pixel-identical** — 0 differing pixels, maximum channel delta 0 — with
`IHDR`, `pHYs`, `IEND` and the *decompressed* IDAT stream identical byte for byte
(`Fig3.png`: 22,266,060 bytes on both sides). Only the *compressed* IDAT differs:

```
host       zlib 1.3.1
container  zlib 1.3.2   (compiled against 1.3.1)
```

zlib 1.3.2 emits a different, slightly larger deflate stream for the same input. The PDFs
differ by exactly 6 bytes in `startxref`, from the embedded date strings.

So `sha256sum figures/*.png` — which is how `figures/README.md` closes its release procedure,
and is correct *on the producing machine* — reports "the archive did not reproduce" when it
reproduced perfectly. `scripts/compare_figures_pixels.py` is the check to use instead: it
fails only on a missing file, a shape change or a real pixel difference.

---

## 6. Regenerating this note's evidence

```bash
# inside-image checks, image fingerprint, headline extraction, figure comparison
PYTHON=<python with numpy + Pillow> bash scripts/make_evidence.sh

# the figure comparisons additionally need the produced figure sets; the script's header
# names the five environment variables that point at them
```

The script's header states, for each part, what it needs and what it does when a part cannot
run: a part that could not run is **printed as such** and does not turn the exit status green.
That is the same rule as C9. PART 1 and PART 2 need a running daemon (`docker image inspect`
and `docker run`); the figure comparisons additionally need the produced figure sets, named by
five environment variables in the header. The two font-substitution comparisons are declared
`expect-diff`, so their difference — which is their result — does not fail the run; a missing
file or a shape change in them still does. The full invocation is `COMMANDS.md` §7.

---

## 7. Contents of this directory

```
README.md                                  this note (§0 is the packaging record)
COMMANDS.md                                every command run, in order, with its log
MANIFEST.sha256                            hashes of everything below (gate 13 checks it)
scripts/make_evidence.sh                   regenerates results/ (§6)
results/image-fingerprint.txt              docker client/server, image id, created, size,
                                           entrypoint, ENV; the base digest re-checked
results/inside-image-verification.txt      produced inside the image: interpreter versions,
                                           every declared Python dependency imported, the
                                           pinned R stack loaded, gate 13 and three other
                                           validators, and step 4's format precheck
results/headline-values.txt                headline values from the container's log and the
                                           host's log, quoted with line numbers
results/figure-verification.txt            pixel comparisons: SI figures, main figures with
                                           Arial / with Liberation Sans / with DejaVu Sans
results/clone-gate-summary.txt             the gates, quoted from the clone log
logs/01..07-build-*.log                    six build attempts; each failure and the fix
logs/05-probe-…                            the probe that identified defect 3
logs/08..11-run-*.log                      the pipeline, and the entrypoint trap (§3.6)
logs/12..17-ge_main-*.log                  the main figures: the path failure, the four
                                           scripts after the fix, Arial, the font preflight,
                                           the no-SI run, the Liberation measurement
logs/18..20-final-image-*.log              the runs that exposed defect 7
logs/21..22-host-reference-*.log           the same two pipelines on the host — the reference
                                           side of every comparison above
logs/23-clone-gates-at-HEAD.log            the gates against a fresh clone of 47a0935
logs/24-clone-gates-at-the-packaged-       the gates re-run at packaging time, against a
commit.log                                 fresh clone of the packaging commit (§0.6)
logs/25-build-7-rebuild-after-pymupdf.log  the rebuild at packaging time: the pinned tag on
                                           its own comment line, the three-step R layer, the
                                           C toolchain, `R stack OK` (defects 1-4's fixes all
                                           in one build)
logs/26-run-step-4-runs-and-misreports-    the pipeline in the rebuilt image: step 4 executes
clean-as-skip.log                          for the first time and its clean verdict is
                                           reported as a skip — defect 9, the negative
logs/27-build-8-rebuild-after-the-         the rebuild that carries the defect-9 fix
defect-9-fix.log
logs/28-run-step-4-reports-ok.log          the same pipeline after the fix: step 4 reports
                                           `[ ok ] … all within limits` — C3's evidence
```

## 8. What this note does not claim

* It does not claim the reported numbers are correct — it claims the container recomputes them
  and gets the same values. What the numbers mean is the manuscript's business.
* It does not claim reproducibility *by a third party*: the host here is the producing machine,
  so where the container and the host differ, the host is the reference. A third-party
  reproduction of these values was already recorded in
  `docs/audit_notes/复现核验_GE投稿两份文档_20261002.md`.
* It does not claim the image is hermetic. It fetches from the base registry, from
  `cloud.r-project.org` and from CRAN's archive at build time; those are recorded in
  `env/renv.lock` and in the Dockerfile's pinned base digest, but the network is a build-time
  dependency and is not pinned away.

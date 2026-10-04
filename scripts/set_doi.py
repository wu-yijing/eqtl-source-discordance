#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
set_doi.py — fill, or check, this repository's Zenodo DOIs.

WHY THIS SCRIPT EXISTS
----------------------
Four carriers have to agree on the DOI: `README.md` (badge and status block), `CITATION.cff`,
`CHANGELOG.md` and `DOI_PENDING.md`. Editing them by hand is how they drift apart, and a
drifted DOI is worse than an obvious placeholder: it looks resolved and is not.

`metadata/zenodo_release.json` is the single source of truth. This script writes it and
propagates from it. Three regions are *managed whole* rather than token-replaced, because a
half-updated status sentence is a lie:

  * `README.md`, between `<!-- DOI_STATUS_BEGIN ...` and `<!-- DOI_STATUS_END -->`
  * `CITATION.cff`, between `#DOI_VERSION_IDENTIFIER_BEGIN` and `#DOI_VERSION_IDENTIFIER_END`
  * the comment lines that introduce `CITATION.cff`'s identifiers list, which sit outside both
    managed blocks and so are swapped by literal match

Everything else is a straight token substitution of `10.5281/zenodo.<CONCEPT>` and
`10.5281/zenodo.<VER>` (and their bare, backticked forms in `CHANGELOG.md`).

Both managed blocks keep their BEGIN/END markers *after* substitution, so a later release can run
this script a second time and move the version DOI forward — the markers are the contract that makes
the backfill repeatable. A block that lost its markers would silently stop being updated, which is
how the first backfill left `CITATION.cff` frozen while `README.md` moved on.

USAGE
-----
    python3 scripts/set_doi.py --show          # current state
    python3 scripts/set_doi.py --check         # exit non-zero while any carrier is unresolved

    # after the Zenodo record is published (see DOI_PENDING.md)
    python3 scripts/set_doi.py \
        --concept 10.5281/zenodo.12345678 \
        --version 10.5281/zenodo.12345679 \
        --record  https://zenodo.org/records/12345679 \
        --release-date 2026-10-10

WHAT IS DELIBERATELY NOT REWRITTEN
----------------------------------
Historical records under `docs/audit_notes/` quote the placeholder because that is what was
true on the date they were written, and this repository does not rewrite historical records
(see `docs/audit_notes/INDEX.md`). `--check` therefore inspects the carriers only.

Prose *outside* the managed regions is not rewritten either — including `DOI_PENDING.md`, which
records how the release was produced. That file is dated evidence rather than a status flag; its
status line was closed by hand when the deposit went out, and only its DOI tokens are substituted.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

PLACEHOLDER_CONCEPT = "10.5281/zenodo.<CONCEPT>"
PLACEHOLDER_VERSION = "10.5281/zenodo.<VER>"

README_BLOCK_RE = re.compile(
    r"<!-- DOI_STATUS_BEGIN.*?<!-- DOI_STATUS_END -->", re.DOTALL)
CFF_BLOCK_RE = re.compile(
    r"#DOI_VERSION_IDENTIFIER_BEGIN.*?#DOI_VERSION_IDENTIFIER_END", re.DOTALL)

# ---------------------------------------------------------------------------
# The two managed blocks. Keep the pending variant identical to what is in the
# tree today; keep the published variant free of placeholders. If you change one,
# change the other in the same commit — this is the pair the `--check` step
# depends on.
# ---------------------------------------------------------------------------

README_BLOCK_PENDING = """<!-- DOI_STATUS_BEGIN — managed by scripts/set_doi.py; the pending and published variants live together in that file. Do not edit this block by hand. -->
> ⚠️ **No published DOI yet.** This repository has not been deposited to Zenodo, so it has no citable
> identifier and the placeholders below are unresolved. Everything needed for the deposit is in the
> tree ([`.zenodo.json`](.zenodo.json), [`CITATION.cff`](CITATION.cff)); what was missing was a place
> to record the result. That is [`DOI_PENDING.md`](DOI_PENDING.md), and the backfill is one command:
> `python3 scripts/set_doi.py --concept … --version …`.
>
> Concept DOI `10.5281/zenodo.<CONCEPT>` · version DOI `10.5281/zenodo.<VER>` — **placeholders, not
> registered identifiers. Do not cite them.** See [`DOI_PENDING.md`](DOI_PENDING.md) for why the DOI
> already quoted by the associated manuscript (an earlier repository's `10.5281/zenodo.22910500`) is
> *not* a substitute: it resolves to a September 2026 snapshot that predates this repository's
> reproductions.
<!-- DOI_STATUS_END -->"""

README_BLOCK_PUBLISHED = """<!-- DOI_STATUS_BEGIN — managed by scripts/set_doi.py; the pending and published variants live together in that file. Do not edit this block by hand. -->
> **Archived, citable snapshot.** Cite the concept DOI `{concept}` for the software and dataset —
> it always resolves to the latest archived version — or the version DOI `{version}` to refer to
> this exact analysed snapshot. Machine-readable form: [`CITATION.cff`](CITATION.cff). The registry
> of record is [`metadata/zenodo_release.json`](metadata/zenodo_release.json); the steps that
> produced it are in [`DOI_PENDING.md`](DOI_PENDING.md).
>
> *If you are reading this inside a Zenodo archive* of the repository, the two values above are the
> ones known when the tag was cut. The concept DOI is permanent; the version DOI may name the
> **previous** release, because a version DOI only comes into existence once its own deposit has been
> published — a tag cannot contain the DOI that its own publication mints. For the version DOI of the
> release you are reading, resolve the concept DOI, or read the registry on the current `main`.
<!-- DOI_STATUS_END -->"""

CFF_BLOCK_PENDING = """#DOI_VERSION_IDENTIFIER_BEGIN
  # - type: doi
  #   value: 10.5281/zenodo.<VER>
  #   description: "Version DOI — pins this exact archived snapshot"
#DOI_VERSION_IDENTIFIER_END"""

CFF_BLOCK_PUBLISHED = """#DOI_VERSION_IDENTIFIER_BEGIN
  - type: doi
    value: {version}
    description: "Version DOI — pins this exact archived snapshot"
#DOI_VERSION_IDENTIFIER_END"""

# The two comment lines that introduce the identifiers list. They are not inside
# either managed block, so they have to be swapped explicitly — otherwise a later
# release leaves a "status pending, must not be cited" note sitting directly above
# two live DOIs, which is exactly the half-updated sentence this script exists to
# prevent.
CFF_NOTE_PENDING = """  # Managed by scripts/set_doi.py from metadata/zenodo_release.json.
  # While that registry reports status "pending", the values below are unregistered
  # placeholders and must not be cited — see DOI_PENDING.md."""

CFF_NOTE_PUBLISHED = """  # Managed by scripts/set_doi.py from metadata/zenodo_release.json.
  # Both values below were minted by Zenodo when this release was published, and
  # metadata/zenodo_release.json remains their single source of truth."""


def repo_root() -> str:
    """Walk up to the sentinel, the same convention as paths_config.py."""
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(8):
        if os.path.exists(os.path.join(root, ".zenodo.json")):
            return root
        parent = os.path.dirname(root)
        if parent == root:
            break
        root = parent
    raise SystemExit("set_doi.py: could not locate the repository root (no .zenodo.json found)")


ROOT = repo_root()
REGISTRY = os.path.join(ROOT, "metadata", "zenodo_release.json")


def load_registry() -> dict:
    with open(REGISTRY, encoding="utf-8") as fh:
        return json.load(fh)


def save_registry(reg: dict) -> None:
    with open(REGISTRY, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(reg, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def read(rel: str) -> str:
    with open(os.path.join(ROOT, rel), encoding="utf-8", newline="") as fh:
        return fh.read()


def write(rel: str, text: str) -> None:
    with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def occurrences(body: str) -> int:
    return (body.count(PLACEHOLDER_CONCEPT) + body.count(PLACEHOLDER_VERSION)
            + len(re.findall(r"`<CONCEPT>`|`<VER>`", body)))


def release_version() -> str:
    """.zenodo.json owns the version; this file must not duplicate it."""
    try:
        with open(os.path.join(ROOT, ".zenodo.json"), encoding="utf-8") as fh:
            return json.load(fh).get("version", "<unresolved>")
    except Exception:
        return "<unresolved>"


def show(reg: dict) -> None:
    print("metadata/zenodo_release.json")
    print("  status        : %s" % reg.get("status"))
    print("  version       : %s   (from .zenodo.json)" % release_version())
    print("  release_date  : %s" % reg.get("release_date"))
    print("  concept_doi   : %s" % reg.get("concept_doi"))
    print("  version_doi   : %s" % reg.get("version_doi"))
    print("  record        : %s" % reg.get("zenodo_record_url"))
    print("  carriers      :")
    for rel in reg["carriers"]:
        if not os.path.exists(os.path.join(ROOT, rel)):
            print("      [MISSING] %s" % rel)
            continue
        print("      %-32s placeholder occurrences: %d" % (rel, occurrences(read(rel))))
    if reg.get("status") != "published":
        print()
        print("  DOI is PENDING. See DOI_PENDING.md for the publication steps.")


def check(reg: dict) -> int:
    """Return the number of carriers that still hold a placeholder token."""
    bad = []
    for rel in reg["carriers"]:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            bad.append((rel, "file missing"))
            continue
        n = occurrences(read(rel))
        if n:
            bad.append((rel, "%d placeholder token(s)" % n))
    if bad:
        print("[FAIL] unresolved DOI placeholders in %d carrier(s):" % len(bad))
        for rel, why in bad:
            print("         %-32s %s" % (rel, why))
        print()
        print("       Either publish the Zenodo record and run set_doi.py with the real DOIs,")
        print("       or leave the placeholders in place and do not claim the archive is")
        print("       citable. See DOI_PENDING.md.")
        return len(bad)
    if reg.get("status") != "published":
        print("[FAIL] every carrier is resolved but metadata/zenodo_release.json still says")
        print("       status=%r. Re-run set_doi.py with --concept and --version." % reg.get("status"))
        return 1
    print("[ ok ] every carrier resolves to a real DOI (no placeholder tokens)")
    return 0


def apply_doi(reg: dict, concept: str, version: str, record: str | None,
              release_date: str | None) -> int:
    if not re.fullmatch(r"10\.5281/zenodo\.\d{4,}", concept or ""):
        raise SystemExit("set_doi.py: --concept must look like 10.5281/zenodo.<digits>")
    if not re.fullmatch(r"10\.5281/zenodo\.\d{4,}", version or ""):
        raise SystemExit("set_doi.py: --version must look like 10.5281/zenodo.<digits>")
    if concept == version:
        raise SystemExit("set_doi.py: --concept and --version must differ "
                         "(Zenodo issues a concept DOI and a version DOI)")

    changed = []

    # 1. Whole-region replacements first, so their placeholder tokens never reach the
    #    token pass (and cannot be half-substituted).
    body = read("README.md")
    if README_BLOCK_RE.search(body):
        new = README_BLOCK_RE.sub(
            lambda _m: README_BLOCK_PUBLISHED.format(concept=concept, version=version), body, count=1)
        if new != body:
            write("README.md", new)
            changed.append("README.md")
            body = new
    else:
        print("  [warn] README.md has no DOI_STATUS_BEGIN/END block — badge handled, prose not.")

    cff = read("CITATION.cff")
    cff_new = cff.replace(CFF_NOTE_PENDING, CFF_NOTE_PUBLISHED)
    if CFF_BLOCK_RE.search(cff_new):
        cff_new = CFF_BLOCK_RE.sub(
            lambda _m: CFF_BLOCK_PUBLISHED.format(version=version), cff_new, count=1)
    else:
        print("  [warn] CITATION.cff has no DOI_VERSION_IDENTIFIER block — version DOI not added.")
    if cff_new != cff:
        write("CITATION.cff", cff_new)
        changed.append("CITATION.cff (version DOI identifier activated)")

    # 2. Token substitution across the remaining carriers.
    for rel in reg["carriers"]:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        before = read(rel)
        after = before.replace(PLACEHOLDER_CONCEPT, concept).replace(PLACEHOLDER_VERSION, version)
        after = after.replace("`<CONCEPT>`", "`%s`" % concept).replace("`<VER>`", "`%s`" % version)
        if after != before:
            write(rel, after)
            if rel not in [c.split(" ")[0] for c in changed]:
                changed.append(rel)

    # 3. The README badge: swap the "pending" shield for the real Zenodo badge.
    body = read("README.md")
    fallback = reg.get("fallback_readme_badge")
    if fallback and fallback in body:
        body = body.replace(fallback, reg["published_readme_badge_template"].format(concept=concept))
        write("README.md", body)
        if "README.md" not in [c.split(" ")[0] for c in changed]:
            changed.append("README.md")

    # 4. The registry itself.
    reg["status"] = "published"
    reg["concept_doi"] = concept
    reg["version_doi"] = version
    reg["zenodo_record_url"] = record
    if release_date:
        reg["release_date"] = release_date
    save_registry(reg)
    changed.append("metadata/zenodo_release.json")

    print("[ ok ] DOI recorded: concept %s  version %s" % (concept, version))
    for rel in changed:
        print("       rewritten: %s" % rel)
    print()
    print("       Next: `git add -A` then scripts/collect_provenance.py (it hashes the index),")
    print("       then scripts/verify_from_clone.sh.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", action="store_true", help="print the current DOI state")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if any carrier still holds a placeholder token")
    ap.add_argument("--concept", help="concept DOI, e.g. 10.5281/zenodo.12345678")
    ap.add_argument("--version", dest="version_doi",
                    help="version DOI, e.g. 10.5281/zenodo.12345679")
    ap.add_argument("--record", help="Zenodo record URL")
    ap.add_argument("--release-date", help="release date, YYYY-MM-DD")
    args = ap.parse_args()

    reg = load_registry()

    if args.concept or args.version_doi:
        if not (args.concept and args.version_doi):
            raise SystemExit("set_doi.py: pass --concept and --version together")
        return apply_doi(reg, args.concept, args.version_doi, args.record, args.release_date)

    if args.check:
        return check(reg)

    show(reg)
    return 0


if __name__ == "__main__":
    sys.exit(main())

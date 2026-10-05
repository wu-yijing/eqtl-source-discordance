#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check every `docs/audit_notes/*/MANIFEST.sha256` against the checked-out tree.

WHY THIS EXISTS
---------------
Every audit note ships a `MANIFEST.sha256` listing the hashes of its own files. Until
2026-10-05 **no gate looked at any of them**. That is not a hypothetical hole: three of
them had silently drifted (READMEs edited after the manifest was generated; `.log` files
hashed as CRLF before `.gitattributes` normalised them to LF) and the drift was found by
hand, during an unrelated audit, not by a check. A digest nobody verifies records intent,
not state.

This script is that check. For each `docs/audit_notes/*/`:

* the directory **must have** a `MANIFEST.sha256` — an audit note whose contents are
  unregistered is not a checkable record;
* every entry in it must name a file that exists, with the recorded SHA-256.

Both `"<hash>  <path>"` (text mode) and `"<hash> *<path>"` (GNU binary mode) are accepted,
because both occur in this tree — the binary marker is stripped, since a checkout is a
checkout and the marker records how the line was written, not what to hash.

    python3 scripts/check_audit_manifests.py
    python3 scripts/check_audit_manifests.py --self-test   # proves it can also fail

Exit status: 0 if every manifest is present and every entry matches; 1 otherwise.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import os
import shutil
import sys
import tempfile

REL_GLOB = os.path.join("docs", "audit_notes", "*")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(path):
    """Yield (recorded_hash, relative_path). Tolerates text and GNU-binary lines."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                yield lineno, None, None
                continue
            digest, rel = parts[0], parts[1].strip()
            if rel.startswith("*"):
                rel = rel[1:]
            yield lineno, digest.lower(), rel


def check(root, quiet=False):
    """Return a list of failure strings. Empty list == every manifest agrees."""
    failures = []
    dirs = sorted(d for d in glob.glob(os.path.join(root, REL_GLOB)) if os.path.isdir(d))
    if not dirs:
        return ["no docs/audit_notes/*/ directories under %s" % root]

    for d in dirs:
        name = os.path.relpath(d, root).replace(os.sep, "/") + "/"
        manifest = os.path.join(d, "MANIFEST.sha256")
        if not os.path.exists(manifest):
            failures.append("%s: no MANIFEST.sha256" % name)
            if not quiet:
                print("  [FAIL] %-46s no MANIFEST.sha256" % name)
            continue
        ok = bad = 0
        for lineno, digest, rel in parse_manifest(manifest):
            if digest is None:
                failures.append("%s/MANIFEST.sha256:%d: unparsable line" % (name, lineno))
                bad += 1
                continue
            target = os.path.join(d, rel.replace("/", os.sep))
            if not os.path.exists(target):
                failures.append("%s/MANIFEST.sha256:%d: %s is missing" % (name, lineno, rel))
                bad += 1
                if not quiet:
                    print("  [FAIL] %-46s %s missing" % (name, rel))
                continue
            got = sha256_of(target)
            if got != digest:
                failures.append("%s/MANIFEST.sha256:%d: %s recorded %s, is %s"
                                % (name, lineno, rel, digest[:16], got[:16]))
                bad += 1
                if not quiet:
                    print("  [FAIL] %-46s %s recorded %s… is %s…"
                          % (name, rel, digest[:12], got[:12]))
            else:
                ok += 1
        if not quiet and not bad:
            print("  [ ok ] %-46s %d entr%s" % (name, ok, "y" if ok == 1 else "ies"))
    return failures


def self_test():
    """A checker that cannot fail is not a check. Build both outcomes and require both."""
    tmp = tempfile.mkdtemp(prefix="manifest-selftest-")
    try:
        root = os.path.join(tmp, "docs", "audit_notes")
        good = os.path.join(root, "good_note")
        broken = os.path.join(root, "broken_note")
        unregistered = os.path.join(root, "unregistered_note")
        for d in (good, broken, unregistered):
            os.makedirs(d)
        for d in (good, broken):
            with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as f:
                f.write("x\n")
            with open(os.path.join(d, "script.py"), "w", encoding="utf-8") as f:
                f.write("print(1)\n")
            rels = ("README.md", "script.py")
            lines = []
            for r in rels:
                actual = sha256_of(os.path.join(d, r))
                # the broken one records a plausible-looking but wrong digest, and uses the
                # GNU binary marker so the parser's tolerance is exercised too
                if d is broken and r == "README.md":
                    lines.append("%s *%s" % ("0" * 64, r))
                else:
                    lines.append("%s  %s" % (actual, r))
            with open(os.path.join(d, "MANIFEST.sha256"), "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        with open(os.path.join(unregistered, "README.md"), "w", encoding="utf-8") as f:
            f.write("no manifest here\n")

        fails_good = check(tmp, quiet=True)
        print("  self-test: a correct manifest alone          -> %s"
              % ("PASS" if not fails_good else "FAIL (%d)" % len(fails_good)))
        expect = {
            "a wrong digest is caught": any("broken_note" in f for f in fails_good),
            "a missing manifest is caught": any("unregistered_note" in f for f in fails_good),
            "a wrong digest does not sink the good note":
                not any("good_note" in f for f in fails_good),
        }
        for k, v in expect.items():
            print("  self-test: %-46s -> %s" % (k, "PASS" if v else "FAIL"))
        # the fixture is deliberately mixed, so a correct checker MUST report failures
        passed = all(expect.values()) and bool(fails_good)
        if not bool(fails_good):
            print("  self-test: the fixture was reported clean — the checker is vacuous")
        return passed
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    help="repository root (default: the parent of this script's directory)")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="prove the checker both passes and fails, then exit")
    args = ap.parse_args()

    if args.self_test:
        print("== self-test ==")
        return 0 if self_test() else 1

    failures = check(args.root, quiet=args.quiet)
    dirs = len([d for d in glob.glob(os.path.join(args.root, REL_GLOB)) if os.path.isdir(d)])
    print()
    if failures:
        print("checked %d audit-note director%s: %d problem(s)"
              % (dirs, "y" if dirs == 1 else "ies", len(failures)))
        print("RESULT: a shipped audit manifest does not match the tree it describes.")
        return 1
    print("checked %d audit-note director%s: every manifest is present and matches"
          % (dirs, "y" if dirs == 1 else "ies"))
    print("RESULT: every audit note's MANIFEST.sha256 describes the tree that ships.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

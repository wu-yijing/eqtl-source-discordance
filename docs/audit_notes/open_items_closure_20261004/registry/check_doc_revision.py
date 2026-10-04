#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_doc_revision.py — ask the reproduction package which revision you hold.

`code/analyses/reproduction_20261002/paths_config.py` identifies a supplied
submission document by MD5 against a list of recorded revisions. This is a thin,
read-only wrapper so that a reader — author, editor or reviewer — can point it at
their own copy and get a verdict without setting up the whole package:

    [ok]              the file matches a recorded revision, which is named
    [UNRECOGNISED]    the file matches none of them; its MD5 and byte count are printed
    [missing]         no file at that path

Before 2026-10-04 the list stopped at manuscript rev4 / SI rev2, so every later
revision — including the ones actually submitted — came back `[UNRECOGNISED]`.
This script is how that was found and how the fix is checked.

Usage
-----
    python check_doc_revision.py --manuscript /path/Manuscript.docx
    python check_doc_revision.py --si /path/Supporting_Information.docx
    python check_doc_revision.py --manuscript M.docx --si S.docx --repo /path/to/clone

`--repo` defaults to the first ancestor of this file that contains
`code/analyses/reproduction_20261002/paths_config.py`, so in a clone no argument
is needed. The script never writes anything.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def find_repo(explicit=None):
    if explicit:
        return os.path.abspath(explicit)
    d = HERE
    while True:
        if os.path.exists(os.path.join(d, "code", "analyses", "reproduction_20261002",
                                       "paths_config.py")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def main():
    ap = argparse.ArgumentParser(description="identify a submission document's revision")
    ap.add_argument("--manuscript")
    ap.add_argument("--si")
    ap.add_argument("--repo")
    a = ap.parse_args()

    repo = find_repo(a.repo)
    if repo is None:
        print("could not locate paths_config.py — pass --repo")
        return 2
    sys.path.insert(0, os.path.join(repo, "code", "analyses", "reproduction_20261002"))
    import paths_config as P  # noqa: E402

    print("repo: %s" % repo)
    print("recorded revisions: manuscript %d, si %d"
          % (len(P.DOCS["manuscript"]["revisions"]), len(P.DOCS["si"]["revisions"])))
    print("-" * 92)

    rc = 0
    for logical, path in (("manuscript", a.manuscript), ("si", a.si)):
        if not path:
            continue
        # `doc_status` only hashes when it is given a *logical* name — a raw path
        # falls through to 'unchecked' without hashing anything. So point the
        # package's environment variable at the file and ask by name.
        os.environ[P.DOCS[logical]['env']] = os.path.abspath(path)
        p, status, detail = P.doc_status(logical)
        tag = {"exact": "[ok]", "unrecognised": "[UNRECOGNISED]",
               "missing": "[missing]", "unchecked": "[unchecked]"}[status]
        print("%-16s %s" % (tag, os.path.basename(path)))
        print("%-16s %s" % ("", detail))
        if status == "unrecognised":
            rc = 1
    if rc:
        print("\nA revision this archive has not seen is not an error by itself — it just "
              "means the copy you hold is not one of the ones it can vouch for.")
    return rc


if __name__ == "__main__":
    sys.exit(main())

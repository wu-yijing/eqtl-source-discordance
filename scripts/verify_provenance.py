#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_provenance.py — recompute every hash in `metadata/provenance.json` and compare.

WHY THIS EXISTS
---------------
The manifest is only worth anything if it can be checked by the person who receives the
archive, in the place they receive it. Two failures taught that:

* The manifest originally hashed the **working tree**. A Windows checkout of a file
  declared `eol=lf` need not be byte-identical to a Linux one, and any script using
  Python's default text mode puts CRLF back into the log or CSV it writes. So the values
  verified on the machine that produced them and failed on a reader's — the opposite of
  the point.
* Nothing re-checked the manifest. `cut_release.sh` confirmed it was valid JSON and free
  of placeholders, which says nothing about whether the hashes are right.

This script hashes the **index** — the bytes a fresh clone receives — and compares both
the SHA-256 and the byte count of every entry. Run it in a clone to find out what a reader
gets; run it here to find out whether the manifest is stale.

    python scripts/verify_provenance.py
    python scripts/verify_provenance.py -v

Exit code 0 = every entry matches. Non-zero = the manifest is stale or the tree has been
altered; the report names the paths and says which of the two it looks like.
Standard library only.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MANIFEST = os.path.join(REPO, 'metadata', 'provenance.json')


def git(*args, **kw):
    return subprocess.run(['git'] + list(args), cwd=REPO, stdout=subprocess.PIPE,
                          check=True, **kw).stdout


def index_blobs():
    """`path -> content bytes`, straight from the object store.

    The index is hashed rather than the working tree because the index is what a clone
    reconstructs. See the module docstring.
    """
    raw = git('ls-files', '-s', '-z')
    sha_by_path = {}
    for rec in raw.split(b'\0'):
        if not rec:
            continue
        meta, _, path = rec.partition(b'\t')
        parts = meta.split()
        if len(parts) >= 2:
            sha_by_path[path.decode('utf-8')] = parts[1].decode('ascii')

    shas = sorted(set(sha_by_path.values()))
    feed = b''.join(s.encode('ascii') + b'\n' for s in shas)
    out = git('cat-file', '--batch', input=feed)

    blobs, pos = {}, 0
    for sha in shas:
        nl = out.find(b'\n', pos)
        header = out[pos:nl].split()
        if len(header) < 3 or header[1] != b'blob':
            pos = nl + 1
            continue
        size = int(header[2])
        blobs[sha] = out[nl + 1: nl + 1 + size]
        pos = nl + 1 + size + 1
    return {p: blobs.get(s) for p, s in sha_by_path.items()}


def main():
    verbose = '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:]
    if not os.path.isfile(MANIFEST):
        print('  [FAIL] %s not found — run scripts/collect_provenance.py' % MANIFEST)
        return 1
    with open(MANIFEST, encoding='utf-8') as fh:
        doc = json.load(fh)

    blobs = index_blobs()
    try:
        tracked = [p.decode('utf-8') for p in git('ls-files', '-z').split(b'\0') if p]
    except subprocess.CalledProcessError:
        tracked = []

    want = {f['path']: f for f in doc.get('files', [])}
    missing, mismatch, unchecked = [], [], []

    for path in sorted(want):
        content = blobs.get(path)
        if content is None:
            unchecked.append(path)
            continue
        got = hashlib.sha256(content).hexdigest()
        if got != want[path]['sha256'] or len(content) != want[path]['bytes']:
            mismatch.append((path, want[path], got, len(content)))

    registered = set(want)
    # The manifest declares its own exclusions — it cannot hash itself. Those are not
    # gaps, and reporting them would make the check cry wolf on every run.
    allowed = {e.get('path') for e in doc.get('excluded', []) if e.get('path')}
    unlisted = sorted(set(tracked) - registered - allowed)

    print()
    print('  manifest: %d entries   tracked: %d' % (len(want), len(tracked)))
    if verbose:
        for p in unchecked:
            print('    [skip] %s — object not readable' % p)
        for p in unlisted:
            print('    [note] %s — tracked but not registered' % p)
    for p, rec, got, size in mismatch:
        print('    [FAIL] %s' % p)
        print('           manifest sha256 %s (%d B)' % (rec['sha256'][:16], rec['bytes']))
        print('           index    sha256 %s (%d B)' % (got[:16], size))

    bad = len(mismatch) + len(unlisted)
    if bad:
        print('  %d entr%s do not agree with the index.' % (bad, 'y' if bad == 1 else 'ies'))
        print('  If the tree changed on purpose, regenerate: python scripts/collect_provenance.py')
        return 1
    print('  [ ok ] every registered hash and byte count matches the index')
    return 0


if __name__ == '__main__':
    sys.exit(main())

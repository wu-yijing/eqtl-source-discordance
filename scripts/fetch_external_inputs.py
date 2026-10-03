#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 scripts/fetch_external_inputs.py — download the third-party inputs, and check
=============================================================================

The archive stores no third-party data. `data/external/SOURCES.tsv` says where
each input comes from; `data/external/SHA256SUMS` says which bytes are the ones
the reported numbers came from. This script is what joins them up: it downloads
each input from the recorded link and refuses to leave a file behind that does
not match the recorded SHA-256.

Nothing calls this automatically. `code/run_all.sh` needs none of these files —
it reads `data/derived/`. They are needed only to rebuild the upstream chain
(`code/run_upstream.sh`) from raw inputs, which is why they are links here and
not copies.

    python3 scripts/fetch_external_inputs.py --list
    python3 scripts/fetch_external_inputs.py --only finngen_R13_DM_NEPHROPATHY.gz
    python3 scripts/fetch_external_inputs.py --only gtex,mashr        # substring match
    python3 scripts/fetch_external_inputs.py --dir /data/eqtl_inputs
    python3 scripts/fetch_external_inputs.py --check-manifests        # no network

Total is about 4.7 GB, so fetch one arm at a time unless you mean it.

Files with `-` in the `url` column have no direct link — PGC3 is behind an
application, and one GTEx covariance has no source this archive could confirm.
They are reported as NO-URL with the reason, not silently skipped.

Exit status: 0 if every file that has a URL ends up present and byte-correct;
1 if any download mismatched, failed, or if the two manifests disagree; 2 on a
malformed manifest.
"""

import argparse
import hashlib
import os
import shutil
import sys
import tarfile
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
EXT = os.path.join(REPO, 'data', 'external')
SOURCES = os.path.join(EXT, 'SOURCES.tsv')
SUMS = os.path.join(EXT, 'SHA256SUMS')

USER_AGENT = 'eqtl-source-discordance/1.0 (reproducibility fetch; python-urllib)'
CHUNK = 1 << 20


def read_sources(path):
    """SOURCES.tsv -> OrderedDict(name -> dict(url, bytes, licence, redistribute, note))."""
    if not os.path.exists(path):
        raise SystemExit('sources manifest not found: %s' % path)
    rows = {}
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line or line.startswith('#') or line.startswith('file\t'):
                continue
            parts = line.split('\t')
            if len(parts) != 6:
                raise SystemExit('SOURCES.tsv: expected 6 tab-separated fields, got %d in:\n  %s'
                                 % (len(parts), line[:120]))
            name, url, nbytes, licence, redistribute, note = parts
            rows[name] = dict(url=url, bytes=int(nbytes), licence=licence,
                              redistribute=redistribute, note=note)
    if not rows:
        raise SystemExit('SOURCES.tsv contained no usable rows: %s' % path)
    return rows


def read_sums(path):
    """SHA256SUMS -> {name: sha256}."""
    if not os.path.exists(path):
        raise SystemExit('hash manifest not found: %s' % path)
    out = {}
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                continue
            out[parts[1].strip().lstrip('*')] = parts[0].lower()
    return out


def check_manifests(sources, sums, quiet=False):
    """The two manifests must describe exactly the same file set. Returns problem list."""
    problems = []
    only_sources = sorted(set(sources) - set(sums))
    only_sums = sorted(set(sums) - set(sources))
    if only_sources:
        problems.append('in SOURCES.tsv but not SHA256SUMS: %s' % ', '.join(only_sources))
    if only_sums:
        problems.append('in SHA256SUMS but not SOURCES.tsv: %s' % ', '.join(only_sums))
    if not quiet:
        print('manifests : %d file(s) in SOURCES.tsv, %d in SHA256SUMS' % (len(sources), len(sums)))
        if problems:
            for p in problems:
                print('  [FAIL] %s' % p)
        else:
            print('  [ ok ] the two manifests describe the same file set')
    return problems


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(CHUNK), b''):
            h.update(block)
    return h.hexdigest()


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return '%.1f %s' % (n, unit) if unit != 'B' else '%d B' % n
        n /= 1024.0


def _progress(done, total):
    if total:
        pct = 100.0 * done / total
        sys.stderr.write('\r    %s / %s  (%.1f%%)   ' % (human(done), human(total), pct))
    else:
        sys.stderr.write('\r    %s   ' % human(done))
    sys.stderr.flush()


def download_to(url, dest, expect_bytes=None):
    """Resume-capable download. Returns (ok, message)."""
    part = dest + '.part'
    have = os.path.getsize(part) if os.path.exists(part) else 0
    headers = {'User-Agent': USER_AGENT}
    if have:
        headers['Range'] = 'bytes=%d-' % have
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        return False, 'request failed: %s' % e

    with resp:
        if have and resp.status == 200:
            have = 0                      # server ignored the range; start over
        total = expect_bytes or 0
        cl = resp.headers.get('Content-Length')
        if cl and total:
            total = max(total, have + int(cl))
        mode = 'ab' if have else 'wb'
        done = have
        with open(part, mode) as out:
            while True:
                block = resp.read(CHUNK)
                if not block:
                    break
                out.write(block)
                done += len(block)
                _progress(done, total)
    sys.stderr.write('\n')
    if expect_bytes and os.path.getsize(part) != expect_bytes:
        return False, 'size %s, expected %s' % (human(os.path.getsize(part)), human(expect_bytes))
    os.replace(part, dest)
    return True, 'downloaded %s' % human(os.path.getsize(dest))


def fetch_tar_member(url, member_basename, dest):
    """Stream a .tar over HTTP and extract the first member whose basename matches."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        return False, 'request failed: %s' % e
    with resp:
        try:
            tf = tarfile.open(fileobj=resp, mode='r|')   # streaming: no seeking
        except tarfile.TarError as e:
            return False, 'not a readable tar: %s' % e
        with tf:
            for member in tf:
                if os.path.basename(member.name.rstrip('/')) == member_basename:
                    if not member.isfile():
                        continue
                    part = dest + '.part'
                    with open(part, 'wb') as out:
                        shutil.copyfileobj(tf.extractfile(member), out, CHUNK)
                    os.replace(part, dest)
                    return True, 'extracted %s from the tar' % member.name
    return False, 'member %s not found inside the tar' % member_basename


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument('--dir', default=EXT, help='where to put the downloads')
    ap.add_argument('--sources', default=SOURCES)
    ap.add_argument('--manifest', default=SUMS)
    ap.add_argument('--only', action='append', default=[],
                    help='fetch only names containing this substring; repeatable')
    ap.add_argument('--list', action='store_true', help='show the plan and exit')
    ap.add_argument('--dry-run', action='store_true', help='say what would happen, fetch nothing')
    ap.add_argument('--check-manifests', action='store_true',
                    help='only check that SOURCES.tsv and SHA256SUMS agree; no network')
    args = ap.parse_args()

    sources = read_sources(args.sources)
    sums = read_sums(args.manifest)

    print('sources   : %s' % args.sources)
    print('hashes    : %s' % args.manifest)
    problems = check_manifests(sources, sums)
    if args.check_manifests:
        return 1 if problems else 0
    if problems:
        print()
        print('Refusing to fetch from manifests that disagree: a file present in one and')
        print('absent from the other is exactly how an unhashed download slips through.')
        return 1

    names = sorted(sources)
    if args.only:
        names = [n for n in names if any(s.lower() in n.lower() for s in args.only)]
        if not names:
            raise SystemExit('--only matched no file')

    if not os.path.isdir(args.dir):
        if args.dry_run:
            print('\ntarget %s does not exist (dry run, not creating it)' % args.dir)
        else:
            os.makedirs(args.dir, exist_ok=True)

    print('target    : %s' % args.dir)
    print('%-62s %14s %s' % ('file', 'bytes', 'url host'))
    print('-' * 100)
    for n in names:
        host = sources[n]['url'].split('/')[2] if sources[n]['url'].startswith('http') else '-'
        print('%-62s %14s %s' % (n[:62], format(sources[n]['bytes'], ','), host))
    if args.list:
        print()
        print('total: %s across %d file(s)' % (human(sum(sources[n]['bytes'] for n in names)), len(names)))
        return 0

    if args.dry_run:
        print()
        print('dry run: nothing fetched')
        return 0

    print()
    ok = skipped = nourl = failed = 0
    failures = []
    for n in names:
        dest = os.path.join(args.dir, n)
        url = sources[n]['url']
        want = sums[n]

        if os.path.exists(dest):
            got = sha256_of(dest)
            if got == want:
                skipped += 1
                print('  [ ok ] %-58s already correct, not re-fetched' % n[:58])
                continue

        if url == '-':
            nourl += 1
            print('  [ -- ] %-58s NO URL — %s' % (n[:58], sources[n]['note'][:70]))
            failures.append((n, 'no URL'))
            continue

        print('  [ .. ] %-58s fetching %s' % (n[:58], url[:70]))
        if url.endswith('.tar') and not n.endswith('.tar'):
            good, msg = fetch_tar_member(url, n, dest)
        else:
            good, msg = download_to(url, dest, sources[n]['bytes'])

        if not good:
            failed += 1
            print('  [FAIL] %s  (%s)' % (n, msg))
            failures.append((n, msg))
            continue
        got = sha256_of(dest)
        if got != want:
            failed += 1
            print('  [FAIL] %s  hash mismatch' % n)
            print('         expected %s' % want)
            print('         found    %s' % got)
            print('         %s was left on disk: do NOT use it. Re-download from the source,')
            print('         or check whether you picked a different release.')
            failures.append((n, 'hash mismatch'))
            continue
        ok += 1
        print('  [ ok ] %-58s %s, sha256 verified' % (n[:58], msg))

    print('-' * 100)
    print('verified %d   already present %d   no URL %d   failed %d   (of %d)'
          % (ok, skipped, nourl, failed, len(names)))

    if nourl:
        print()
        print('%d file(s) have no direct link; SOURCES.tsv says why for each.' % nourl)
        print('PGC3 is behind a data-access application and its terms forbid redistribution;')
        print('the other is a GTEx covariance whose source this archive could not confirm.')
    if failures:
        print()
        print('Failed: %s' % ', '.join(n for n, _ in failures))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

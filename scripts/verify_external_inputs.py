#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 scripts/verify_external_inputs.py — check third-party inputs against hashes
=============================================================================

`data/README.md` lists every external input the reported numbers depend on, and
`data/external/SHA256SUMS` now carries the SHA-256 of the copy that produced them.
This script is what makes that list usable: point it at the directory holding your
downloads and it says, per file, whether you hold the same bytes.

It tolerates a partial set on purpose — an input that is simply absent is reported
`MISSING`, not `MISMATCH`, because most readers will need only one arm.

**A hash match is not proof of a complete file.** An interrupted download hashes
happily and reports `ok` — it is "the right bytes so far". This archive hit exactly
that on 2026-10-03: `gtex_v8_mashr_snp_covariance.txt.gz` was a `.gz` whose stream
stopped after 6.8 % of the source file, and the recorded SHA-256 was the hash of the
fragment. So, for a `.gz` input that is present, this script also checks that the gzip
stream actually *ends* — trailer present, CRC32 and ISIZE correct. Use
`--no-integrity` to skip that pass (it decompresses, so it is the slow part).

    python3 scripts/verify_external_inputs.py --dir /path/to/downloads
    python3 scripts/verify_external_inputs.py --dir data/external --strict
    python3 scripts/verify_external_inputs.py --list          # names and sizes only

Exit status: 0 if nothing mismatched (absent files are reported but do not fail
unless --strict), 1 if any file present on disk has the wrong hash, 2 on a bad
manifest.

Renaming note: two inputs are distributed under a different name from the
canonical one this manifest uses. `data/external/README.md` records the mapping;
this script also accepts the download names.
"""

import argparse
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MANIFEST = os.path.join(REPO, 'data', 'external', 'SHA256SUMS')

# Files whose distribution name differs from the canonical name in SHA256SUMS.
ALIASES = {
    'GCST90043640.h.tsv.gz': [
        '34737426-GCST90043640-EFO_0003770.h (1).tsv.gz',
        '34737426-GCST90043640-EFO_0003770.h.tsv.gz',
    ],
    'RNApull_down_MS_results.zip': [
        'RNApull down MS实验结果.zip',
    ],
    # The PredictDB release names this file after its consumer, not its content. The gzip
    # header inside it still says `gtex_v8_expression_mashr_snp_covariance.txt`.
    'gtex_v8_mashr_snp_covariance.txt.gz': [
        'gtex_v8_expression_mashr_snp_smultixcan_covariance.txt.gz',
    ],
}


def parse_manifest(path):
    """Returns [(sha256, filename)]; skips comments and blanks."""
    if not os.path.exists(path):
        raise SystemExit('manifest not found: %s' % path)
    out = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            m = re.match(r'^([0-9a-fA-F]{64})\s+\*?(.+)$', line)
            if m:
                out.append((m.group(1).lower(), m.group(2).strip()))
    if not out:
        raise SystemExit('manifest contained no usable entries: %s' % path)
    return out


def sha256_of(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(chunk), b''):
            h.update(block)
    return h.hexdigest()


def gzip_status(path, chunk=1 << 22):
    """('ok', decompressed_bytes) | ('truncated', n) | ('corrupt', msg) | ('not-gzip', None).

    A gzip member is only complete if it ends with its trailer, and only valid if that
    trailer's CRC32 and ISIZE match the decompressed stream. An interrupted download
    fails this while still matching whatever hash was computed over the fragment.
    """
    import struct
    import zlib
    try:
        with open(path, 'rb') as fh:
            if fh.read(2) != b'\x1f\x8b':
                return 'not-gzip', None
    except OSError as e:
        return 'corrupt', str(e)
    total = 0
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        with open(path, 'rb') as fh:
            for block in iter(lambda: fh.read(chunk), b''):
                total += len(d.decompress(block))
        d.flush()
    except zlib.error as e:
        return 'corrupt', str(e)
    if not d.eof:
        return 'truncated', total
    return 'ok', total


def locate(name, directory):
    """Canonical name first, then the recorded download aliases."""
    for candidate in [name] + ALIASES.get(name, []):
        p = os.path.join(directory, candidate)
        if os.path.exists(p):
            return p
    return None


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return '%.1f %s' % (n, unit) if unit != 'B' else '%d B' % n
        n /= 1024.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument('--dir', default=os.path.join(REPO, 'data', 'external'),
                    help='directory holding the downloaded inputs')
    ap.add_argument('--manifest', default=MANIFEST)
    ap.add_argument('--strict', action='store_true',
                    help='exit non-zero if any input is absent')
    ap.add_argument('--list', action='store_true',
                    help='list the manifest and exit')
    ap.add_argument('--no-integrity', action='store_true',
                    help='skip the gzip-completeness pass (a hash match alone is not '
                         'proof of a complete file)')
    args = ap.parse_args()

    entries = parse_manifest(args.manifest)

    if args.list:
        print('%-62s %s' % ('file', 'sha256'))
        for sha, name in entries:
            print('%-62s %s' % (name, sha))
        return 0

    if not os.path.isdir(args.dir):
        raise SystemExit('not a directory: %s' % args.dir)

    print('manifest : %s (%d entries)' % (args.manifest, len(entries)))
    print('directory: %s' % args.dir)
    print('-' * 78)

    ok = miss = bad = 0
    broken = 0
    failures = []
    incomplete = []
    for sha, name in entries:
        p = locate(name, args.dir)
        if p is None:
            miss += 1
            print('  [ -- ] MISSING   %-58s' % name[:58])
            continue
        got = sha256_of(p)
        if got == sha:
            ok += 1
            print('  [ ok ] %-58s %s' % (name[:58], human(os.path.getsize(p))))
            if not args.no_integrity and name.endswith('.gz'):
                state, n = gzip_status(p)
                if state == 'truncated':
                    broken += 1
                    incomplete.append((name, 'gzip stream ends after %s — the file is a '
                                       'prefix of its source, not the recorded artefact'
                                       % human(n)))
                    print('         [FAIL] the hash matches but the gzip stream never ends:')
                    print('                it decompresses %s and stops. An interrupted' % human(n))
                    print('                download hashes exactly like the real file.')
                elif state == 'corrupt':
                    broken += 1
                    incomplete.append((name, 'not a readable gzip stream: %s' % n))
                    print('         [FAIL] not a readable gzip stream: %s' % n)
        else:
            bad += 1
            failures.append((name, sha, got))
            print('  [FAIL] MISMATCH  %-58s' % name[:58])
            print('         expected %s' % sha)
            print('         found    %s  (%s)' % (got, p))

    print('-' * 78)
    print('ok %d   mismatched %d   incomplete %d   missing %d   (of %d)'
          % (ok, bad, broken, miss, len(entries)))
    for name, why in incomplete:
        print('  incomplete: %-46s %s' % (name[:46], why))

    if broken:
        print()
        print('An INCOMPLETE file matches its recorded hash and is still unusable: the')
        print('download stopped early and the hash was taken over the fragment. Re-fetch')
        print('it from the link in data/external/SOURCES.tsv and check the byte count.')
    if bad:
        print()
        print('A hash that differs means you do NOT hold the file these numbers came from.')
        print('Re-download it from the source recorded in data/external/README.md, or check')
        print('whether you picked a different release (e.g. FinnGen R12 vs R13).')
    if miss:
        print()
        print('%d input(s) absent. That is expected unless you intend to re-run the whole' % miss)
        print('upstream chain: the downstream reproduction (code/run_all.sh) needs none of them.')

    if bad or broken:
        return 1
    if miss and args.strict:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

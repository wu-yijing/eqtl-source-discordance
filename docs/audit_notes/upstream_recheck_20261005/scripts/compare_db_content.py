#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compare_db_content.py — compare two SQLite databases by CONTENT, not by bytes.

WHY THIS EXISTS
---------------
`code/upstream/verify_middleware.py` pins the four eQTLGen `*.db` artefacts by
`file-sha256`. A SQLite file's byte image depends on the writer's library version, so a
rebuild under a different `sqlite3.sqlite_version` can return a *different* file with the
*same* schema, the *same* rows in the *same order*, and even the *same byte count* — and
the byte comparison then reports DIFFERS with nothing actually different.

This script settles that case: it hashes the schema and then every row of every table, in
a deterministic order, for both files, and reports MATCH/DIFFER plus the per-table row
counts. It is the `.db` analogue of the content comparison the archive already applies to
the `.txt.gz` covariances.

    python compare_db_content.py <db-a> <db-b> [<db-a> <db-b> ...]

Exit code 0 = every pair is content-identical. Non-zero = at least one pair differs, or a
file is missing (the report names it).

Standard library only.
"""
import hashlib
import os
import sqlite3
import sys


def content_hash(path):
    con = sqlite3.connect('file:%s?mode=ro' % path.replace('\\', '/'), uri=True)
    cur = con.cursor()
    h = hashlib.sha256()
    schema = cur.execute(
        "SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' "
        "ORDER BY type, name").fetchall()
    for t, n, s in schema:
        h.update(('%s|%s|%s\n' % (t, n, s)).encode('utf-8'))
    rows = {}
    for t, n, s in schema:
        if t != 'table':
            continue
        rows[n] = cur.execute('SELECT COUNT(*) FROM "%s"' % n).fetchone()[0]
        cols = [c[1] for c in cur.execute('PRAGMA table_info("%s")' % n).fetchall()]
        order = ','.join('"%s"' % c for c in cols)
        for r in cur.execute('SELECT * FROM "%s" ORDER BY %s' % (n, order)):
            h.update(('%s|%s\n' % (n, '|'.join('' if v is None else str(v)
                                               for v in r))).encode('utf-8'))
    con.close()
    return h.hexdigest(), rows


def main(argv):
    args = argv[1:]
    if not args or len(args) % 2:
        print(__doc__.strip().split('\n\n')[0])
        print('\nusage: compare_db_content.py <db-a> <db-b> [<db-a> <db-b> ...]')
        return 2
    bad = 0
    for i in range(0, len(args), 2):
        a, b = args[i], args[i + 1]
        print('=' * 78)
        print('%s  vs  %s' % (a, b))
        if not os.path.exists(a):
            print('  [MISSING] %s' % a)
            bad += 1
            continue
        if not os.path.exists(b):
            print('  [MISSING] %s' % b)
            bad += 1
            continue
        ha, ra = content_hash(a)
        hb, rb = content_hash(b)
        print('  bytes      : %d  vs  %d  %s' % (os.path.getsize(a), os.path.getsize(b),
                                                 'equal' if os.path.getsize(a) == os.path.getsize(b)
                                                 else 'DIFFER'))
        print('  tables     : %s' % ra)
        if ha == hb:
            print('  content    : MATCH   sha256 %s' % ha)
        else:
            print('  content    : DIFFER')
            print('    a %s  %s' % (ha, ra))
            print('    b %s  %s' % (hb, rb))
            bad += 1
    print('=' * 78)
    print('RESULT: %s' % ('all pairs are content-identical' if bad == 0
                          else '%d pair(s) differ or are missing' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

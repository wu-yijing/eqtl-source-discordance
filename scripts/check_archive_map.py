#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_archive_map.py — make `metadata/ARCHIVE_MAP.md` check itself.

WHY THIS EXISTS
---------------
`ARCHIVE_MAP.md` is the only place that says, item by item, whether the reported
value can be re-derived and whether a reader can re-run the chain. It is therefore
the document a reviewer will read to decide what to trust. It was wrong before, in
ways nobody noticed:

* The summary line said **16 ✅ / 13 🟡 / 9 🔴 / 8 ➖** while the table beneath it held
  12 ✅ and 12 🔴. A hand-maintained count drifts.
* When the repair added an `Input locality` column it edited the rows but not the
  table headers. Markdown renderers drop cells beyond the header, so the column —
  the one thing that distinguishes "verified" from "checkable by you" — was invisible
  in the rendered file while looking present in the source.
* An unescaped `|` inside a cell (`(|Z| density)`) split one row into two extra cells,
  silently shifting every value in it one column to the right.

All three are the same class of defect: a document that cannot be checked by machine
is checked by eye, and eyes stop checking. This script checks the structure and the
counts, so the prose is the only part left to judgement.

    python scripts/check_archive_map.py
    python scripts/check_archive_map.py -v

Exit code 0 = the map is structurally sound and self-consistent. Non-zero = it is not;
the report names the line. `scripts/cut_release.sh` runs this before a release.

Standard library only, so it runs under any interpreter the release happens to have.
"""
import io
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MAP = os.path.join(REPO, 'metadata', 'ARCHIVE_MAP.md')

STATUS_MARKS = ('✅', '🟡', '🔴', '➖')

#: The vocabulary of the `Input locality` column. Every data row of the three item
#: tables must begin its last cell with one of these, in bold backticks, followed by
#: an em dash and a reason. Keep in step with the Status key in the map itself.
LOCALITY = {
    'clone': 'every input ships; a fresh clone re-runs it end to end',
    'clone + SI': 're-runs once you supply a document published with the paper',
    'none': 'nothing in this archive produces it',
    '—': 'no data artefact',
}

#: The three tables whose rows are the items of the manuscript and its SI. Identified
#: by their title cell so a re-ordering or a re-titling is caught rather than assumed.
ITEM_TABLES = {
    'Manuscript item': 'main text',
    'Item': 'SI notes, figures and tables',
}


def cells(line):
    """Split a table row on unescaped pipes only."""
    parts = re.split(r'(?<!\\)\|', line)
    if parts and parts[0].strip() == '':
        parts = parts[1:]
    if parts and parts[-1].strip() == '':
        parts = parts[:-1]
    return [c.strip() for c in parts]


def is_separator(line):
    """`|---|:--:|` and friends: every character except the pipes is a dash or a colon."""
    if not line.startswith('|'):
        return False
    body = line.replace('|', '').replace(' ', '')
    return bool(body) and set(body) <= set('-:')


def status_of(cs):
    for c in cs:
        if c in STATUS_MARKS:
            return c
    return None


def locality_of(cs):
    m = re.match(r'\*\*`([^`]+)`\*\*\s*—', cs[-1]) if cs else None
    return m.group(1) if m else None


def main():
    argv = sys.argv[1:]
    verbose = '-v' in argv or '--verbose' in argv
    counts_only = '--counts' in argv
    if not os.path.isfile(MAP):
        print('  [FAIL] %s not found' % MAP)
        return 1

    text = io.open(MAP, encoding='utf-8').read()
    lines = text.split('\n')

    problems = []
    item_rows = []          # (line_no, first_cell, status, locality)
    n_tables = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.startswith('|'):
            i += 1
            continue
        head = cells(line)
        is_header = i + 1 < len(lines) and is_separator(lines[i + 1])
        if is_header:
            n_tables += 1
            ncol = len(head)
            title = head[0]
            if verbose:
                print('  table at line %-4d cols=%d  first header cell: %s'
                      % (i + 1, ncol, title))
            j = i + 2
            while j < len(lines) and lines[j].startswith('|'):
                if is_separator(lines[j]):
                    j += 1
                    continue
                cs = cells(lines[j])
                if len(cs) != ncol:
                    problems.append(
                        'line %d: %d cells in a %d-column table — a pipe inside a cell '
                        'is probably unescaped, or a column was added to the rows but '
                        'not to the header. First cell: %r'
                        % (j + 1, len(cs), ncol, cs[0][:40] if cs else ''))
                if title in ITEM_TABLES:
                    st = status_of(cs)
                    if st:
                        item_rows.append((j + 1, cs[0], st, locality_of(cs)))
                j += 1
            i = j
            continue
        i += 1

    # ---- 2. the declared column must exist in all three item tables
    for tbl in ITEM_TABLES:
        pat = re.compile(r'^\| ' + re.escape(tbl) + r' \|.*\| Input locality \|$', re.M)
        if not pat.search(text):
            problems.append("no table header declares an 'Input locality' column "
                            "(looked for one starting with '%s')" % tbl)

    # ---- 3. the summary counts must equal the machine count
    counts = Counter(r[2] for r in item_rows)

    if counts_only:
        # Consumed by cut_release.sh, which needs the number of GAP rows. Counting the
        # emoji in the whole file — the obvious way, and what that script used to do —
        # also counts the status key that defines the mark and the summary line that
        # reports it, so it over-reports. Only the item tables are a count of items.
        print('%d %d %d %d %d' % (len(item_rows), counts['✅'], counts['🟡'],
                                  counts['🔴'], counts['➖']))
        return 0

    m = re.search(r'Of (\d+) items checked[^:]*:\s*\*\*(\d+) ✅, (\d+) 🟡, (\d+) 🔴, '
                  r'(\d+) ➖\*\*', text)
    if not m:
        problems.append('the summary line ("Of N items checked ... **a ✅, b 🟡, ...") '
                        'is missing or no longer matches the pattern this check expects')
    else:
        declared = dict(total=int(m.group(1)), ok=int(m.group(2)), deriv=int(m.group(3)),
                        gap=int(m.group(4)), na=int(m.group(5)))
        actual = dict(total=len(item_rows), ok=counts['✅'], deriv=counts['🟡'],
                      gap=counts['🔴'], na=counts['➖'])
        if declared != actual:
            problems.append('the summary counts disagree with the table: line says %s, '
                            'the status column holds %s' % (declared, actual))
        elif verbose:
            print('  counts: %s (matches the table)' % actual)

    # ---- 4. every item row must carry a locality label from the vocabulary
    for lineno, first, st, loc in item_rows:
        if loc is None:
            problems.append('line %d (%s): no `locality` label in the last cell'
                            % (lineno, first[:40]))
        elif loc not in LOCALITY:
            problems.append('line %d (%s): locality %r is not in the vocabulary %s'
                            % (lineno, first[:40], loc, sorted(LOCALITY)))

    # ---- 5. the vocabulary must be documented in the map itself, not only here
    for label in LOCALITY:
        if '`%s`' % label not in text:
            problems.append('locality label %r is used but never defined in the map'
                            % label)

    print()
    print('  archive map: %d tables, %d item rows, %d locality labels'
          % (n_tables, len(item_rows), len(LOCALITY)))
    if problems:
        print('  %d problem(s):' % len(problems))
        for p in problems:
            print('    - %s' % p)
        return 1
    print('  [ ok ] structure, column declaration, counts and locality labels agree')
    return 0


if __name__ == '__main__':
    sys.exit(main())

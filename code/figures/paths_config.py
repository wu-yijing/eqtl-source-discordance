# -*- coding: utf-8 -*-
"""Figure pipeline — the single path entry point.

Every script in this directory reads its input/output paths from here; none of
them hard-codes an absolute path. Paths are resolved by walking up from this
file until the repository root is found, so the pipeline runs on a fresh clone
without editing anything.

Repository root = the first ancestor directory containing `.zenodo.json`.
Override any path with an environment variable:

| environment variable | meaning | default |
|---|---|---|
| `TWAS_REPO`    | repository root (contains `data/`, `figures/`) | first ancestor with `.zenodo.json` |
| `TWAS_DATA_Z`  | **authoritative** Z data layer                 | `<TWAS_REPO>/data/derived` |
| `FIG_OUT_MAIN` | main-figure output directory                   | `<TWAS_REPO>/figures` |
| `FIG_OUT_SUPP` | supplementary-figure output directory           | same as `FIG_OUT_MAIN` |
| `AF1_DOCX`     | Supporting Information `.docx`                 | `<TWAS_REPO>/manuscript/Supporting_Information.docx` |
| `FIG_RESULTS`  | bundled inputs/products (json)                 | this directory |

⚠️ **2026-10-02 — the path contract changed with the repository reorganisation.**
This file used to sit one level below the repository root
(`figure_scripts_officialZ_20260917/`) and derived `REPO` as the parent of its
own directory. It now lives at `code/figures/`, and the authoritative data layer
moved from `data/processed_officialZ/` to `data/derived/`. Both changes are
handled below; the old behaviour survives only as a last-resort fallback.

⚠️ **The Supporting Information is not distributed with this repository.** Point
`AF1_DOCX` at the copy you downloaded from the journal:

```bash
AF1_DOCX="/path/to/Supporting_Information.docx" python 00_build_officialZ_data_layer.py
```
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_SENTINEL = '.zenodo.json'


def _find_repo(start):
    """Walk up from `start` looking for the repository sentinel."""
    d = start
    for _ in range(8):
        if os.path.exists(os.path.join(d, _SENTINEL)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    # Fallback for the historical layout: <repo>/code/figures/paths_config.py
    return os.path.dirname(os.path.dirname(start))


REPO = os.environ.get('TWAS_REPO') or _find_repo(HERE)
DATA_Z = os.environ.get('TWAS_DATA_Z') or os.path.join(REPO, 'data', 'derived')
OUT_MAIN = os.environ.get('FIG_OUT_MAIN') or os.path.join(REPO, 'figures')
OUT_SUPP = os.environ.get('FIG_OUT_SUPP') or OUT_MAIN
AF1 = os.environ.get('AF1_DOCX') or os.path.join(REPO, 'manuscript', 'Supporting_Information.docx')
RES = os.environ.get('FIG_RESULTS') or HERE

#: The pre-correction layer. Named here only so scripts can assert they are NOT
#: reading it — it is never an input path.
FORBIDDEN = os.path.join(REPO, 'data', 'superseded')


def need(path, what='input'):
    """Existence assertion that prints an actionable message instead of a traceback."""
    if not os.path.exists(path):
        sys.exit(
            '[missing path] %s does not exist:\n  %s\n'
            '  Override (any one of):\n'
            '    - TWAS_REPO    : point at your clone (default: first ancestor with %s)\n'
            '    - TWAS_DATA_Z  : point at the authoritative data layer\n'
            '    - AF1_DOCX     : point at the Supporting Information .docx\n'
            '    - FIG_OUT_MAIN / FIG_OUT_SUPP : point at your figure output directory' %
            (what, path, _SENTINEL))
    return path


def report():
    for k in ('REPO', 'DATA_Z', 'OUT_MAIN', 'OUT_SUPP', 'AF1', 'RES', 'FORBIDDEN'):
        print('  %-9s = %s' % (k, globals()[k]))


if __name__ == '__main__':
    report()

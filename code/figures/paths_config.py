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

#: ⚠️ **2026-10-03 — legacy filenames.** The scripts in this directory were written
#: against the predecessor's data layer, which lived at `data/processed_officialZ/`
#: and used a `_official` suffix. That directory has never existed in this repository
#: (see `code/analyses/reproduction_20261002/INPUTS.md` §A.1): the same six files were
#: renamed into `data/derived/` on 2026-10-02. The figure scripts were not updated, so
#: every one of them raised FileNotFoundError from a fresh clone and `code/run_all.sh`
#: failed its own preflight. `rz()` resolves the old name onto the shipped file, which
#: is the same mapping `code/analyses/reproduction_20261002/paths_config.py` already
#: carries as `OFFICIAL_Z_RENAME`.
OFFICIAL_Z_RENAME = {
    'scz_z_4arm_official.csv': 'scz_z_4arm.csv',
    'gtex_official_Z.csv': 'gtex_Z.csv',
    'eqtlgen_official_Z.csv': 'eqtlgen_Z.csv',
    'gene_groups_TableS1_official.csv': 'gene_groups.csv',
    'primary_arm_96pairs_official.csv': 'primary_arm_96pairs.csv',
    'crosscohort_TableS4_official.csv': 'crosscohort.csv',
}


def rz(name):
    """Resolve a legacy `processed_officialZ` filename to its `data/derived/` path.

    Names that are already current (or are not data-layer files at all) are passed
    through unchanged, so a call site may use this unconditionally.
    """
    return os.path.join(DATA_Z, OFFICIAL_Z_RENAME.get(name, name))


#: Tokens the Supporting Information uses for "no value". `—` (em dash) is the one
#: the GE revision uses; the figure scripts' original one-line lamdas only knew
#: `None`/''/'NA' and raised `ValueError: could not convert string to float: '—'`
#: on the first cell that carried it.
_NA_TOKENS = frozenset(['', 'NA', 'N/A', 'n/a', 'NaN', 'nan', '-', '–', '−', '—', '.', '..'])


def num(x):
    """Parse one cell of a Supporting-Information table into a float, or NaN.

    Robust on purpose: returns NaN instead of raising for placeholders, thousands
    separators, percentages and free text, so a single unexpected cell cannot abort
    a figure build.
    """
    if x is None:
        return float('nan')
    try:
        s = str(x).strip()
    except Exception:
        return float('nan')
    if s in _NA_TOKENS:
        return float('nan')
    s = s.replace(',', '').replace('%', '').replace('\u00a0', ' ').strip()
    try:
        return float(s)
    except ValueError:
        return float('nan')


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

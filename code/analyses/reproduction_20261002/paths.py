# -*- coding: utf-8 -*-
"""
================================================================================
 paths.py — the single place where this reproduction package resolves an input
================================================================================

WHY THIS MODULE EXISTS
----------------------
As first committed (91afa33) the 35 scripts in this package carried the author's
own absolute paths — 27 of them, 26 distinct, not one of which pointed into this
repository. A third party cloning the archive could therefore run *nothing*: the
paths led to an unarchived session directory or to a second local clone of a
different repository.

Every input now resolves through this file, and every resolvable one defaults to
a path **inside this tree**.

TWO CLASSES OF INPUT
--------------------
1. DISTRIBUTED — the file ships in this repository. `derived()`, `superseded()`
   and `fig()` return it directly, relative to the repository root. Nothing else
   is needed. This is the normal case: it covers everything the manuscript's
   headline numbers rest on.

2. NOT DISTRIBUTED — a resource this archive deliberately does not redistribute
   (the two submitted `.docx`, the mashr model databases, the full-universe
   eQTLGen/GTEx gene-level Z files, the SI table extract, the predecessor BMC
   manuscript). `external()` resolves one of these from, in order:

     a. a path given on the command line (`--input NAME=PATH`, or a dedicated
        flag such as `--manuscript`);
     b. the environment variable named in `EXTERNAL[name].env`;
     c. a path relative to `--repo-root`, if someone drops the file in;
     d. otherwise it raises `NotDistributed`, whose message states what the file
        is and where it comes from.

   `INPUTS.md` lists all of them, with the MD5 recorded in `results/` so a reader
   can tell whether the copy they supply is the one that produced the numbers.

USAGE
-----
    import paths
    ap = argparse.ArgumentParser()
    paths.add_common_args(ap)                  # --repo-root, --input NAME=PATH
    args = ap.parse_args()
    paths.apply_args(args)

    p = paths.derived('gtex_Z')                # ships here — always works
    z = paths.external('t1_full_dir')          # raises NotDistributed unless supplied

Nothing in this module writes to disk.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

__all__ = [
    'REPO_ROOT', 'NotDistributed', 'set_repo_root', 'add_common_args', 'apply_args',
    'derived', 'superseded', 'fig', 'external', 'get', 'path', 'DISTRIBUTED',
    'EXTERNAL', 'legacy_alias',
]


class NotDistributed(FileNotFoundError):
    """Raised when an input that this archive does not redistribute is missing."""


# ---------------------------------------------------------------- repository root
def _find_repo_root(start: Path) -> Path:
    """Walk up from `start` to the first directory that looks like this repo."""
    for cand in (start, *start.parents):
        if (cand / 'data' / 'derived').is_dir() and (cand / 'metadata').is_dir():
            return cand
    raise NotDistributed(
        'could not locate the repository root above %s: expected an ancestor '
        'containing data/derived/ and metadata/. Pass --repo-root explicitly.'
        % start)


_env_root = os.environ.get('EQTL_REPO_ROOT')
REPO_ROOT: Path = Path(_env_root).expanduser().resolve() if _env_root else _find_repo_root(
    Path(__file__).resolve().parent)


def set_repo_root(root) -> Path:
    """Point the package at another checkout (used by `--repo-root`)."""
    global REPO_ROOT
    if root:
        REPO_ROOT = Path(root).expanduser().resolve()
    return REPO_ROOT


# ------------------------------------------------------------ distributed inputs
# logical name -> path relative to the repository root.
# Data-layer equivalence (established 2026-10-02, see metadata/ARCHIVE_MAP.md):
# every value here is byte- or cell-identical to the `processed_officialZ/` layer
# the analysis scripts originally read from a second local clone.
DISTRIBUTED = {
    # --- data/derived/ : the authoritative layer, and the only one distributed ---
    'gtex_Z':            'data/derived/gtex_Z.csv',
    'eqtlgen_Z':         'data/derived/eqtlgen_Z.csv',
    'gene_groups':       'data/derived/gene_groups.csv',
    'primary_arm_96pairs': 'data/derived/primary_arm_96pairs.csv',
    'crosscohort':       'data/derived/crosscohort.csv',
    'scz_z_4arm':        'data/derived/scz_z_4arm.csv',
    'hk_genes':          'data/derived/hk_genes.txt',
    'ukb_dr_dir':        'data/derived/ukb_dr',

    # --- code/figures/ ---
    'm15_json':          'code/figures/m15_positive_control.json',

    # --- data/superseded/ : declared exemption, see the note below ---
    'covariate_matrix':  'data/superseded/covariate_matrix.csv',
    'hk_reselect_dir':   'data/superseded/hk_reselect_20260830/data',
    'human_mouse_common': 'data/superseded/hk_reselect_20260830/data/Human_Mouse_Common.csv',
}

# `covariate_matrix.csv` is the ONE distributed input that lives outside
# `data/derived/`. It exists only in the superseded layer, and `data/README.md`
# says values in `superseded/` must never be quoted. It is *not* quoted here: the
# 104-gene panel roster is all S9's pool construction takes from it, and the panel
# roster is a fixed input, not an affected value. Recorded as an explicit
# exemption in `data/README.md` and in `INPUTS.md` (audit P2-7).
EXEMPT_FROM_SUPERSEDED = ['covariate_matrix']

# Legacy directory names that used to be hard-coded in the scripts, mapped onto
# their in-repository equivalent. Kept so that a stale copy of a script still
# lands on the right file instead of a missing directory.
_LEGACY = {
    'data/processed_officialZ': 'data/derived',
    'data/processed/ukb_dr_official': 'data/derived/ukb_dr',
    'data/hk_reselect_20260830/data': 'data/superseded/hk_reselect_20260830/data',
}


def legacy_alias(rel: str) -> str:
    """Rewrite a pre-2026-10-02 repository-relative path to its current one."""
    rel = rel.replace('\\', '/').lstrip('./')
    for old, new in sorted(_LEGACY.items(), key=lambda kv: -len(kv[0])):
        if rel == old or rel.startswith(old + '/'):
            return new + rel[len(old):]
    return rel


def path(name_or_rel: str) -> Path:
    """Resolve a logical name from DISTRIBUTED, or a repository-relative path."""
    rel = DISTRIBUTED.get(name_or_rel, name_or_rel)
    rel = legacy_alias(rel)
    return (REPO_ROOT / rel).resolve()


def derived(name: str) -> Path:
    """A file under data/derived/. Raises if the name is not in that layer."""
    rel = DISTRIBUTED.get(name, name)
    if not legacy_alias(rel).startswith('data/derived/'):
        raise KeyError('%r is not a data/derived/ input (got %r)' % (name, rel))
    return path(rel)


def superseded(name: str) -> Path:
    return path(name)


def fig(name: str) -> Path:
    return path(DISTRIBUTED.get(name, name))


# --------------------------------------------------------- not-distributed inputs
# logical name -> (env var, what it is, where it comes from)
EXTERNAL = {
    'manuscript_docx': (
        'EQTL_MANUSCRIPT_DOCX',
        'the submitted main text, Manuscript_GenetEpidemiol_20260930.docx',
        'Accompanies the submission; not redistributed with this archive.'),
    'si_docx': (
        'EQTL_SI_DOCX',
        'the submitted Supporting Information, Supporting_Information_GenetEpidemiol_20260930.docx',
        'Accompanies the submission; not redistributed with this archive. All 31 tables S1–S30.'),
    't1_full_dir': (
        'EQTL_T1_FULL_DIR',
        'the six gene-level Z files of the full universe: eqz_full.csv, '
        'gtex/official_Whole_Blood.csv, gtex/official_Nerve_Tibial.csv, '
        'en/official_en_Whole_Blood.csv, en/official_en_Nerve_Tibial.csv',
        'Derived from the GTEx v8 MASHR / elastic-net weight models and the eQTLGen '
        'phase I summary statistics (Note S4). Size is the reason it is not redistributed. '
        'The elastic-net pair (en/) cannot be re-derived from anything in this archive.'),
    'mashr_dir': (
        'EQTL_MASHR_DIR',
        'mashr_Whole_Blood.db (4.6 MB) and mashr_Nerve_Tibial.db (5.9 MB)',
        'The GTEx v8 mashr model databases used to enumerate the model universe in S9.'),
    'groups_json': (
        'EQTL_GROUPS_JSON',
        'groups.json — the stratification definition behind the S9 control layers',
        'The 3,956-byte lay2/lay3 gene lists. Reproduces POOL_818 = 818/767/51.'),
    't1_s8rand_dir': (
        'EQTL_T1_S8RAND_DIR',
        'the eQTLGen random-control run: official_rand_{DR,DN,DPN}.csv',
        'The random-control arm of S9. Not redistributed.'),
    'metaxcan_run_dir': (
        'EQTL_METAXCAN_RUN_DIR',
        'the GTEx official MetaXcan run: official_{tissue}_{trait}.csv',
        'Six files = 2 tissues × 3 phenotypes. Supplies the ACAT-O P of S9.'),
    'additional_file1_docx': (
        'EQTL_ADDITIONAL_FILE1',
        'Additional file 1_审稿意见修订_20260917.docx',
        'The predecessor submission\'s Additional file; the only carrier of the S20 input tables.'),
    'si_tables_dir': (
        'EQTL_SI_TABLES_DIR',
        'the 31 SI tables extracted from the Supporting Information as .tsv',
        'A derived extract of `si_docx`; regenerate by extracting each table to tNN.tsv.'),
    'bmc_manuscript_docx': (
        'EQTL_BMC_MANUSCRIPT_DOCX',
        'the predecessor BMC Genomics final manuscript (投稿前定稿/Manuscript.docx)',
        'Used only by bmc_ref/, for the BMC↔GE cross-check.'),
    'bmc_additional_file1_docx': (
        'EQTL_BMC_ADDITIONAL_FILE1',
        'the predecessor BMC Genomics Additional_file_1.docx',
        'Used only by bmc_ref/, for the BMC↔GE cross-check.'),
}

_overrides = {}


def add_common_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add `--repo-root` and `--input NAME=PATH` to a script's parser."""
    parser.add_argument(
        '--repo-root', default=None, metavar='DIR',
        help='repository root; default: the ancestor of this package that holds '
             'data/derived/ and metadata/ (env EQTL_REPO_ROOT)')
    parser.add_argument(
        '--input', action='append', default=[], metavar='NAME=PATH',
        help='bind a logical input to a path; repeatable. Run the script with '
             '--list-inputs to see the names. e.g. --input manuscript_docx=C:/m.docx')
    parser.add_argument(
        '--list-inputs', action='store_true',
        help='print the input manifest and exit')
    return parser


def apply_args(args) -> Path:
    """Apply parsed `--repo-root` / `--input` to the module's resolver."""
    set_repo_root(getattr(args, 'repo_root', None))
    for item in getattr(args, 'input', None) or []:
        if '=' not in item:
            raise SystemExit('--input expects NAME=PATH, got %r' % item)
        name, value = item.split('=', 1)
        _overrides[name.strip()] = value.strip()
    return REPO_ROOT


def bootstrap_args(argv=None) -> Path:
    """Consume `--repo-root` / `--input` in a script that has no parser of its own.

    The diagnostic scripts under `repo_crosscheck/`, `bmc_ref/` and `r2_fix/` take no
    options, so they cannot use `add_common_args()` + `apply_args()`. Without this they
    would ignore `--input` entirely and only respond to environment variables — which is
    exactly how they behaved when first rewired. Call it once, right after
    `import paths`, and `--input NAME=PATH` works everywhere in the package.

    `parse_known_args` + `add_help=False` mean the script's own behaviour is untouched:
    anything this does not recognise is left for the script.
    """
    ap = add_common_args(argparse.ArgumentParser(add_help=False))
    args, _ = ap.parse_known_args(argv)
    if getattr(args, 'list_inputs', False):
        print(list_inputs())
        raise SystemExit(0)
    return apply_args(args)


def list_inputs() -> str:
    out = ['distributed (ships in this repository):']
    for k in sorted(DISTRIBUTED):
        p = (REPO_ROOT / DISTRIBUTED[k])
        out.append('  %-22s %-52s %s' % (k, DISTRIBUTED[k], 'ok' if p.exists() else 'MISSING'))
    out.append('')
    out.append('not distributed (supply with --input NAME=PATH or the env var):')
    for k in sorted(EXTERNAL):
        env, what, _ = EXTERNAL[k]
        out.append('  %-22s %s' % (k, env))
        out.append('      %s' % what)
    return '\n'.join(out)


def external(name: str) -> Path:
    """Resolve an input this archive does not redistribute. Raises if it cannot."""
    if name not in EXTERNAL:
        raise KeyError('unknown input %r; known: %s'
                       % (name, ', '.join(sorted(EXTERNAL))))
    env, what, origin = EXTERNAL[name]

    for cand, src in ((_overrides.get(name), '--input %s' % name),
                      (os.environ.get(env), 'env %s' % env),
                      (str((REPO_ROOT / name)) if (REPO_ROOT / name).exists() else None,
                       'a file named %s/ at the repository root' % name)):
        if cand:
            p = Path(cand).expanduser()
            if p.exists():
                return p.resolve()
            raise NotDistributed(
                '%s was supplied via %s but does not exist: %s' % (name, src, p))

    raise NotDistributed(
        '\n'
        '  Input %r is not distributed with this archive.\n'
        '    what it is : %s\n'
        '    where from : %s\n'
        '    supply it  : --input %s=/path/to/it   (or set %s)\n'
        '  See code/analyses/reproduction_20261002/INPUTS.md for the recorded MD5,\n'
        '  so you can confirm the copy you supply is the one that produced the numbers.\n'
        % (name, what, origin, name, env))


def get(name: str) -> Path:
    """`derived()`/`fig()` if the name is distributed, else `external()`."""
    if name in DISTRIBUTED:
        return path(name)
    return external(name)


if __name__ == '__main__':
    ap = add_common_args(argparse.ArgumentParser(description=__doc__.splitlines()[1]))
    print('repository root: %s' % REPO_ROOT)
    print()
    print(list_inputs())

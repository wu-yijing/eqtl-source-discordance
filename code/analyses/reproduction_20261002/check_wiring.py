#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_wiring.py — prove that every script in this package can import `paths_config`.

WHY THIS EXISTS
---------------
Each script carries its own bootstrap to locate `paths_config.py`, because a script in
`scripts/r3/m15/` sits four directories below it. A bootstrap with the wrong depth is
silently fatal: the script compiles, and then dies with
`ModuleNotFoundError: No module named 'paths_config'` the moment it runs. That is exactly
what shipped in the first attempt at making this package portable — 24 scripts wired one
directory level short. Neither `compileall` nor any existing release check noticed, because
both only look at syntax and file contents.

This check executes, for every script, the module-level code that precedes its
`import paths_config` line — with `__file__` set to the real script path, and with this
checker's own directory removed from `sys.path` — and fails if `paths_config` does not
become importable.

    python code/analyses/reproduction_20261002/check_wiring.py
    python code/analyses/reproduction_20261002/check_wiring.py -v
    python code/analyses/reproduction_20261002/check_wiring.py --self-test

Exit code 0 = every script wired. Non-zero = at least one is broken; the report names the
file and the error. `scripts/cut_release.sh` runs this before a release.

`--self-test` runs the checker against two probes of its own — one wired correctly and one
the same but stopped one directory short — and fails unless the first passes and the second
is caught. A gate that has never been observed to fail is not a gate; this one was vacuous
once, so the demonstration is now part of every release rather than a memory.

Two properties this check must have, both learned the hard way:

* It must not be **vacuous.** The first version left this file's own directory on
  `sys.path`; since `paths_config.py` lives there, every script "passed". It now removes
  this directory, the script's directory and the working directory before executing the
  preamble, so only the script's own bootstrap can make the import succeed.
* It must not depend on the **analysis environment.** Third-party modules that this
  interpreter lacks (numpy, scipy, pandas, python-docx) are replaced by stubs that answer
  any attribute lookup, so the check still reaches `import paths_config` when run under a
  bare Python.
"""
import argparse
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
SENTINEL = 'paths_config.py'
MODULE = 'paths_config'

# Third-party modules the preambles import. If one is missing from the running
# interpreter, it is replaced by a stub that answers any attribute access, so the check
# still reaches `import paths_config`.
THIRD_PARTY = [
    'numpy', 'pandas', 'scipy', 'scipy.stats', 'scipy.optimize',
    'docx', 'docx.table', 'docx.oxml', 'docx.oxml.ns',
    'matplotlib', 'matplotlib.pyplot', 'seaborn', 'openpyxl',
]

GUIDANCE = """\
A script is wired with the wrong number of os.path.dirname(...) levels, or not at all.
Use the depth-independent form:

    import os as _os
    import sys as _sys


    def _repro_pkg():
        d = _os.path.dirname(_os.path.abspath(__file__))
        for _ in range(8):
            if _os.path.exists(_os.path.join(d, 'paths_config.py')):
                return d
            d = _os.path.dirname(d)
        raise RuntimeError('paths_config.py not found above %s' % __file__)


    _sys.path.insert(0, _repro_pkg())
    import paths_config as P
"""


class _Stub(types.ModuleType):
    """Answers any attribute lookup, so `from x import y` on a stub succeeds."""

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        return _Stub('%s.%s' % (self.__name__, name))

    def __call__(self, *a, **k):
        return _Stub(self.__name__ + '()')


# --------------------------------------------------------------------------------------
# Self-test: a gate that has never been observed to fail is not a gate
# --------------------------------------------------------------------------------------
#: Directory used for the probes below. Excluded from the scan, in case a previous run
#: died before its cleanup.
SELFTEST_DIR = '_wiring_selftest'

#: Two probes with the same code and different bootstrap reach. Written as source text so
#: that `preamble()` reads them exactly the way it reads the real scripts.
PROBE = '''import os as _os
import sys as _sys


def _repro_pkg():
    d = _os.path.dirname(_os.path.abspath(__file__))
    for _ in range(%(depth)d):
        if _os.path.exists(_os.path.join(d, 'paths_config.py')):
            return d
        d = _os.path.dirname(d)
    raise RuntimeError('paths_config.py not found above %%s' %% __file__)


_sys.path.insert(0, _repro_pkg())
import paths_config as P
'''


def self_test():
    """Prove this checker can fail.

    Places two probes three directories below `paths_config.py`: one whose bootstrap walks
    up far enough, and one that stops short — the exact defect class this file exists for.
    The first must pass and the second must fail. If both pass, the checker is vacuous and
    the release gate is decorative; that has happened here once already, so it is now a
    test rather than a memory.

    Returns (ok, report_lines).
    """
    import shutil
    import tempfile

    report = []
    sandbox = os.path.join(HERE, SELFTEST_DIR)
    if os.path.isdir(sandbox):
        shutil.rmtree(sandbox, ignore_errors=True)
    probe_dir = os.path.join(sandbox, 'scripts', 'sub')
    os.makedirs(probe_dir)
    try:
        good = os.path.join(probe_dir, 'good.py')
        bad = os.path.join(probe_dir, 'bad.py')
        with open(good, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(PROBE % {'depth': 8})
        with open(bad, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(PROBE % {'depth': 1})

        ok_good, detail_good = check_one(good)
        ok_bad, detail_bad = check_one(bad)

        report.append('  [%s] a correct bootstrap passes            %s'
                      % (' ok ' if ok_good else 'FAIL', detail_good or ''))
        report.append('  [%s] a one-level-short bootstrap is caught %s'
                      % (' ok ' if ok_bad is False else 'FAIL', detail_bad or ''))
        if ok_good is not True:
            report.append('      -> the checker rejects a script that is wired correctly; '
                          'its verdicts cannot be trusted')
        if ok_bad is not False:
            report.append('      -> the checker ACCEPTS the defect it exists to catch; '
                          'the release gate is vacuous')
        return (ok_good is True and ok_bad is False), report
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def install_stubs():
    """Stub only the third-party modules that genuinely fail to import."""
    missing = []
    for name in THIRD_PARTY:
        try:
            __import__(name)
        except Exception:                          # noqa: BLE001
            missing.append(name)
    for name in missing:
        sys.modules[name] = _Stub(name)
    return missing


def scripts():
    for dirpath, dirnames, filenames in os.walk(HERE):
        dirnames[:] = [d for d in dirnames
                       if d not in ('__pycache__', SELFTEST_DIR)]
        for fn in sorted(filenames):
            if fn.endswith('.py'):
                yield os.path.join(dirpath, fn)


def preamble(path):
    """Module-level lines up to and including the first `import paths_config`."""
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('import %s' % MODULE) or s.startswith('from %s ' % MODULE):
            return '\n'.join(lines[:i + 1]), i + 1
    return None, 0


def check_one(path):
    """Execute the preamble with the real __file__; report (ok, detail).

    Two things this deliberately does NOT punish:

    * The preamble runs with `sys.argv` replaced by just the script name, so a script that
      parses arguments at module level can never see this checker's own flags. (Without
      that, `check_wiring.py -v` was swallowed by whichever preamble called `parse_args()`.)
    * A preamble that raises *after* `paths_config` became importable is a pass: the
      bootstrap worked, and what failed is a downstream requirement such as a document or
      bulk layer this archive does not distribute. Not a wiring defect.
    """
    code, upto = preamble(path)
    if code is None:
        return None, 'does not import %s' % MODULE
    saved_path, saved_argv = list(sys.path), list(sys.argv)
    sys.modules.pop(MODULE, None)
    sys.argv = [path]
    # CRITICAL: strip the directories that would let `import paths_config` succeed on its
    # own — this checker's own directory (it lives beside paths_config.py), the script's
    # directory, and the working directory. Without this the check is vacuous.
    blocked = {os.path.abspath(HERE), os.path.abspath(os.path.dirname(path)),
               os.path.abspath(os.getcwd())}
    sys.path[:] = [p for p in saved_path if os.path.abspath(p or os.getcwd()) not in blocked]
    try:
        g = {'__file__': path, '__name__': '_wiring_check_%d' % id(path)}
        exec(compile(code, path, 'exec'), g)
        if MODULE not in sys.modules:
            return False, 'preamble ran but `%s` was not imported' % MODULE
        return True, '%s -> %s' % (MODULE, sys.modules[MODULE].REPO)
    except SystemExit as exc:
        # MissingInput / paths_config.doc() exits with an actionable message. That is a
        # downstream requirement, not a wiring fault — but only if the import worked.
        return (MODULE in sys.modules), 'bootstrap ok; a later line exited (%s)' % (exc.code,)
    except Exception as exc:                       # noqa: BLE001 - report anything
        if MODULE in sys.modules:
            return True, ('bootstrap ok; a later module-level line raised %s: %s'
                          % (type(exc).__name__, str(exc).splitlines()[0][:60]))
        return False, '%s: %s' % (type(exc).__name__, str(exc).splitlines()[0][:80])
    finally:
        # Remove only this package's module. Never clear sys.modules: numpy, scipy and
        # other C extensions raise "cannot load module more than once per process" if
        # they are dropped and re-imported within one interpreter.
        sys.modules.pop(MODULE, None)
        sys.path[:] = saved_path
        sys.argv = saved_argv


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument('-v', '--verbose', action='store_true')
    ap.add_argument('--strict', action='store_true',
                    help='do not stub missing third-party modules (use the real ones)')
    ap.add_argument('--self-test', action='store_true',
                    help='prove the checker can fail, then exit without scanning')
    args = ap.parse_args()

    stubbed = [] if args.strict else install_stubs()

    ok_selftest = True
    if args.self_test:
        ok_selftest, report = self_test()
        print('self-test:')
        for line in report:
            print(line)
        print('  self-test: %s' % ('the checker both passes and fails as it should'
                                   if ok_selftest else 'THE CHECKER IS UNRELIABLE'))
        return 0 if ok_selftest else 1

    wired = broken = skipped = 0
    for path in scripts():
        rel = os.path.relpath(path, HERE).replace(os.sep, '/')
        # This file quotes the bootstrap it enforces — in its docstring and in GUIDANCE —
        # so a line-oriented scan finds `import paths_config` inside a string literal and
        # would truncate the preamble. It is not a consumer of the module; skip it.
        if rel in (SENTINEL, os.path.basename(__file__)):
            skipped += 1
            continue
        ok, detail = check_one(path)
        if ok is None:
            skipped += 1
            if args.verbose:
                print('  [skip] %-52s %s' % (rel, detail))
        elif ok:
            wired += 1
            if args.verbose:
                print('  [ ok ] %-52s %s' % (rel, detail))
        else:
            broken += 1
            print('  [FAIL] %-52s %s' % (rel, detail))

    print()
    if stubbed:
        print('(stubbed, not importable here: %s)' % ', '.join(stubbed))
    print('wired: %d   broken: %d   without a %s import: %d'
          % (wired, broken, MODULE, skipped))
    if broken:
        print()
        print(GUIDANCE)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

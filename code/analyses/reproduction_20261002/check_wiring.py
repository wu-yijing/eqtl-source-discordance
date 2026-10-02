#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_wiring.py — prove that every script in this package can import `paths`.

WHY THIS EXISTS
---------------
The bootstrap that lets a script find `paths.py` is duplicated in every script. A
wrong number of `os.path.dirname(...)` levels is silently fatal — the script
compiles, and then dies with `ModuleNotFoundError: No module named 'paths'` the
moment it runs. That is exactly what shipped in the first attempt at making this
package portable: 24 scripts wired one directory level short, and neither
`compileall` nor any existing release check noticed, because both only look at
syntax and file contents.

This check executes, for every script, the module-level code that precedes its
`import paths` line — with `__file__` set to the real script path — and fails if
`paths` does not become importable. It is the check that would have caught it.

    python code/analyses/reproduction_20261002/check_wiring.py
    python code/analyses/reproduction_20261002/check_wiring.py -v

Exit code 0 = every script wired. Non-zero = at least one is broken; the report
names the file and the bootstrap that was executed. `scripts/cut_release.sh` runs
this before a release.
"""
import argparse
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))

# Third-party modules the preambles import. If one is missing from the running
# interpreter, it is replaced by a stub that answers any attribute access, so the
# check still reaches `import paths`. Without this the check would report a wiring
# failure merely because the release script happens to run under a bare Python —
# and a wiring check must not depend on the analysis environment.
THIRD_PARTY = [
    'numpy', 'pandas', 'scipy', 'scipy.stats', 'scipy.optimize',
    'docx', 'docx.table', 'docx.oxml', 'docx.oxml.ns',
    'matplotlib', 'matplotlib.pyplot', 'seaborn', 'openpyxl',
]


class _Stub(types.ModuleType):
    """Answers any attribute lookup, so `from x import y` on a stub succeeds."""

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)
        return _Stub('%s.%s' % (self.__name__, name))

    def __call__(self, *a, **k):
        return _Stub(self.__name__ + '()')


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
        dirnames[:] = [d for d in dirnames if d != '__pycache__']
        for fn in sorted(filenames):
            if fn.endswith('.py'):
                yield os.path.join(dirpath, fn)


def preamble(path):
    """Module-level lines up to and including the first `import paths` statement."""
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('import paths') or s.startswith('from paths '):
            return '\n'.join(lines[:i + 1]), i + 1
    return None, 0


def check_one(path):
    """Execute the preamble with the real __file__; report (ok, detail).

    Two things this deliberately does NOT punish:

    * The preamble is run with `sys.argv` replaced by just the script name, so a
      script that parses arguments at module level can never see this checker's
      own flags. (Without that, `check_wiring.py -v` was swallowed by whichever
      preamble called `parse_args()` — an error that looked like a wiring bug and
      was not one.)
    * A preamble that raises *after* `paths` became importable is a pass: the
      bootstrap worked, and what failed is a downstream requirement such as an
      input that this archive does not distribute. That is not a wiring defect.
    """
    code, upto = preamble(path)
    if code is None:
        return None, 'does not import paths'
    saved_path, saved_argv = list(sys.path), list(sys.argv)
    sys.modules.pop('paths', None)
    sys.argv = [path]
    # CRITICAL: strip the directories that would let `import paths` succeed on its
    # own — this checker's own directory (it lives beside paths.py) and the script's
    # directory (which Python puts on sys.path when running a script). Without this
    # the check is vacuous: every script "passes" because the checker's sys.path
    # already contains paths.py. Verified by re-introducing the fixed-depth bug and
    # confirming it is then reported.
    blocked = {os.path.abspath(HERE), os.path.abspath(os.path.dirname(path)),
               os.path.abspath(os.getcwd())}
    sys.path[:] = [p for p in saved_path if os.path.abspath(p or os.getcwd()) not in blocked]
    try:
        g = {'__file__': path, '__name__': '_wiring_check_%d' % id(path)}
        exec(compile(code, path, 'exec'), g)
        if 'paths' not in sys.modules:
            return False, 'preamble ran but `paths` was not imported'
        return True, 'paths -> %s' % sys.modules['paths'].REPO_ROOT
    except Exception as exc:                       # noqa: BLE001 - report anything
        if 'paths' in sys.modules:
            return True, ('bootstrap ok; a later module-level line raised '
                          '%s: %s' % (type(exc).__name__, str(exc).splitlines()[0][:60]))
        return False, '%s: %s' % (type(exc).__name__, exc)
    finally:
        # Remove only this package's module. Never clear sys.modules: numpy, scipy
        # and other C extensions raise "cannot load module more than once per
        # process" if they are dropped and re-imported within one interpreter.
        sys.modules.pop('paths', None)
        sys.path[:] = saved_path
        sys.argv = saved_argv


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument('-v', '--verbose', action='store_true')
    ap.add_argument('--strict', action='store_true',
                    help='do not stub missing third-party modules (use the real ones)')
    args = ap.parse_args()

    stubbed = [] if args.strict else install_stubs()

    wired = broken = skipped = 0
    failures = []
    for path in scripts():
        rel = os.path.relpath(path, HERE).replace(os.sep, '/')
        if rel == 'paths.py':
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
            failures.append((rel, detail))
            print('  [FAIL] %-52s %s' % (rel, detail))

    print()
    if stubbed:
        print('(stubbed, not importable here: %s)' % ', '.join(stubbed))
    print('wired: %d   broken: %d   without a paths import: %d' % (wired, broken, skipped))
    if broken:
        print()
        print('A script is wired with the wrong number of os.path.dirname(...) levels, or')
        print('not at all. Use the depth-independent form:')
        print()
        print('    import sys as _sys, os as _os')
        print('    _p = _os.path.dirname(_os.path.abspath(__file__))')
        print("    while _p != _os.path.dirname(_p) and not _os.path.isfile(_os.path.join(_p, 'paths.py')):")
        print('        _p = _os.path.dirname(_p)')
        print('    _sys.path.insert(0, _p)')
        print('    import paths as _paths')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

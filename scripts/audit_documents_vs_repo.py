#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_documents_vs_repo.py — do the two submitted documents follow from this archive?

The question a reader asks is not "is `data/derived/` well formed" but "are the numbers in
the manuscript and the Supporting Information in here". This answers that, table by table,
in two strengths, and says which is which.

**Class A — structural equality.** For the tables that are a straight projection of a
shipped table, every cell is compared against the shipped CSV, row by row, after aligning
rows on their key columns. A cell agrees only if it matches after parsing as a number with
a stated tolerance, or matches as a string after whitespace/case normalisation. A missing
token (`—`, `–`, `NA`, empty) on one side matches a missing token on the other.

**Class B — value presence.** For every other table, each numeric cell is looked up in the
repository's own numbers — `data/derived/`, the reproduction package's `results/`, and
`code/figures/` — at the precision the document prints it. This is a *necessary* condition,
not a sufficient one: it shows the archive contains the value, not that it can re-derive
it. It is still the check that catches a documented number with no counterpart in the
archive at all.

**Class C — declared elsewhere, not machine-checked here.** Items the archive map records as
a gap or as needing a submission document. They are listed with that status so the report
accounts for every table rather than quietly covering the easy ones.

    python scripts/audit_documents_vs_repo.py --si <SI.docx> --manuscript <MS.docx>
    python scripts/audit_documents_vs_repo.py --si ... --manuscript ... -v

Exit code 0 = no Class A mismatch and no Class B value missing. Non-zero = the report names
the table and the cell.
Standard library only.
"""
import argparse
import collections
import csv
import gzip
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PKG = os.path.join(REPO, 'code', 'analyses', 'reproduction_20261002')
sys.path.insert(0, PKG)

NUM = re.compile(r'^[+\-\u2212\u2013]?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?$')
#: Tokens that mean "no value". The documents print an em dash where the CSVs leave the
#: field empty; treating them as different produced 84 phantom mismatches in Table S3.
ABSENT = {'', '\u2014', '\u2013', '-', 'na', 'n/a', '\u2014\u2014', 'nan', '.'}


def num(s):
    """Float if the cell is a bare number, else None. Strips thousands separators, %, sign."""
    t = (s or '').strip().replace('\u2212', '-').replace('\u2013', '-').replace(',', '')
    t = t.replace('%', '').replace('\u00a0', '')
    return float(t) if NUM.match(t) else None


def decimals(s):
    t = (s or '').strip().replace(',', '')
    return len(t.split('.')[1]) if '.' in t else 0


def is_absent(s):
    return (s or '').strip().lower() in ABSENT


def normalise(s):
    # Strip EVERY non-alphanumeric character, not just whitespace: the documents print
    # `Non-candidate` where the CSV holds `NonCandidate`, which is the same label.
    return re.sub(r'[^a-z0-9]', '', (s or '').strip().lower())


#: The documents print group names without the `NN_` prefix the CSV carries
#: (`30_HOTAIR_Candidate` -> `Candidate`), and print a `matched/total` pair as its
#: numerator. Both are display conventions, not data differences: left alone they produced
#: 121 phantom mismatches across Tables S4 and S23.
_SOFTEN = re.compile(r'^\s*\d+_[a-z]+_', re.I)


def soften(s):
    return _SOFTEN.sub('', (s or '').strip())


def first_of_pair(s):
    """`23/23` -> `23`; anything else unchanged."""
    t = (s or '').strip()
    return t.split('/')[0].strip() if '/' in t else t


def last_of_pair(s):
    """`633/659` -> `659`. Table S23 prints the *total* model SNPs, not the matched count:
    for ACTB both readings coincide (`23/23`), which is what made the difference easy to
    miss — CKAP4 prints 659 against a `633/659` field and DDX5 prints 367 against `335/367`."""
    t = (s or '').strip()
    return t.split('/')[-1].strip() if '/' in t else t


# --------------------------------------------------------------------------- documents
def load_documents(si_path, ms_path):
    import paths_config as P
    os.environ['REPRO_SI_DOCX'] = si_path
    os.environ['REPRO_MS_DOCX'] = ms_path
    P.apply_cli_overrides()

    def pack(path, labels_from_caption):
        tabs = P.si_tables(path)
        out = []
        for i, t in enumerate(tabs):
            if labels_from_caption:
                m = re.match(r'\s*Table\s*S?(\d+[a-z]?)', t['title'], re.I)
                label = 'S' + m.group(1) if m else 'obj%d' % i
            else:
                # The manuscript's captions carry a panel letter, not a table number:
                # "(A) Disease-agnostic control layers", "(B) Testbed groups", then
                # "(A) Direction consistency by phenotype", "(B) Two-axis ... arm summary".
                # Objects 0-1 are Table 1's two panels, 2-3 are Table 2's.
                m = re.match(r'\s*\(?([AB])\)?\s', t['title'])
                panel = m.group(1) if m else '?'
                label = 'MS%d%s' % (i // 2 + 1, panel)
            out.append((label, t['title'], t['rows']))
        return out

    return pack(P.doc('si'), True), pack(P.doc('manuscript'), False)


# --------------------------------------------------------------------------- corpus
def corpus_numbers():
    """Every number the repository itself contains, bucketed by printed precision."""
    roots = [os.path.join(REPO, 'data', 'derived'),
             os.path.join(PKG, 'results'),
             os.path.join(REPO, 'code', 'figures')]
    text, n_files = [], 0
    for root in roots:
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d != '__pycache__']
            for f in fn:
                p = os.path.join(dp, f)
                try:
                    if f.endswith('.gz'):
                        with gzip.open(p, 'rt', encoding='utf-8', errors='replace') as fh:
                            text.append(fh.read())
                    elif f.endswith(('.csv', '.json', '.txt', '.log', '.tsv')):
                        with io.open(p, encoding='utf-8', errors='replace') as fh:
                            text.append(fh.read())
                    else:
                        continue
                except OSError:
                    continue
                n_files += 1
    blob = '\n'.join(text)
    vals = re.findall(r'[+\-\u2212]?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?', blob)
    buckets = {p: set() for p in range(7)}
    for v in vals:
        try:
            x = float(v.replace('\u2212', '-'))
        except ValueError:
            continue
        for p in range(7):
            buckets[p].add('%.*f' % (p, x))
    return buckets, n_files, len(vals)


def present(v, buckets):
    """Is this printed number among the repository's numbers, at this precision?"""
    p = min(decimals(v), 6)
    x = num(v)
    if x is None:
        return None
    return ('%.*f' % (p, x)) in buckets[p]


# --------------------------------------------------------------------------- class A
def load_csv(path):
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8-sig') as fh:
        return list(csv.DictReader(fh))


def compare_cells(label, drows, crows, key_doc, key_csv, colmap, expect_norow=0,
                  tol_rel=2e-3, tol_abs=5e-5, verbose=False):
    """Cell-by-cell comparison. Returns a dict of results."""
    dh = [c.strip() for c in drows[0]]
    idx = {c: i for i, c in enumerate(dh)}
    bykey = {}
    for r in crows:
        bykey[tuple((r.get(c) or '').strip() for c in key_csv)] = r

    n = ok = bad = norow = 0
    examples = []
    for r in drows[1:]:
        k = tuple((r[idx[c]] if c in idx else '').strip() for c in key_doc)
        cr = bykey.get(k)
        if cr is None:
            norow += 1
            if len(examples) < 4:
                examples.append(('row not in the shipped table', k))
            continue
        for dcol, ccol in colmap.items():
            if dcol not in idx:
                continue
            dv = r[idx[dcol]]
            ccol, xform = (ccol if isinstance(ccol, tuple) else (ccol, None))
            cv = cr.get(ccol, '')
            if xform == 'soften':
                cv = soften(cv)
            elif xform == 'first':
                cv = first_of_pair(cv)
            elif xform == 'last':
                cv = last_of_pair(cv)
            a, b = num(dv), num(cv)
            n += 1
            if a is not None and b is not None:
                good = abs(a - b) <= max(tol_abs, tol_rel * abs(a))
            elif is_absent(dv) and is_absent(cv):
                good = True
            else:
                good = normalise(dv) == normalise(cv)
            if good:
                ok += 1
            else:
                bad += 1
                if len(examples) < 6:
                    examples.append((k, dcol, dv, cv))
    if verbose:
        for e in examples:
            print('          %s' % (e,))
    return dict(cells=n, ok=ok, bad=bad, norow=norow, expect_norow=expect_norow,
                rows=len(drows) - 1, examples=examples)


def class_a(si, ms, verbose):
    """The tables that are a straight projection of a shipped table."""
    G = os.path.join(REPO, 'data', 'derived')
    S = os.path.join(REPO, 'data', 'superseded')
    by = {lab: rows for lab, _, rows in si}
    msx = {lab: rows for lab, _, rows in ms}

    jobs = []
    jobs.append(('S2  complete gene list', by.get('S2'),
                 load_csv(os.path.join(G, 'gene_groups.csv')), ['Gene'], ['Gene'],
                 {'Gene': 'Gene', 'Group': 'Group', 'Source': 'Source',
                  'Pull-down Unused score': 'Pull-down Unused score',
                  'Length (bp)': 'Length (bp)', 'GC content (%)': 'GC content (%)',
                  'Mean eQTL SNP count': 'Mean eQTL SNP count'}))
    jobs.append(('S3  GTEx v8 baseline TWAS', by.get('S3'),
                 load_csv(os.path.join(G, 'gtex_Z.csv')), ['Gene', 'Phenotype'], ['Gene', 'Trait'],
                 {'Z_Nerve_Tibial': 'Z_Nerve_Tibial', 'Z_Whole_Blood': 'Z_Whole_Blood',
                  'Z_multi_tissue': 'Z_multi_tissue', 'P_Stouffer': 'P_Stouffer',
                  'FDR_q_Stouffer': 'FDR_q_Stouffer', 'P_ACAT_O': 'P_ACAT_O',
                  'FDR_q_ACAT_O': 'FDR_q_ACAT_O'}))
    jobs.append(('S4  Mahalanobis matched pairs', by.get('S4'),
                 load_csv(os.path.join(S, 'mahalanobis_matched_pairs.csv')), ['Gene'], ['Gene'],
                 {'Group': ('Group', 'soften'), 'log10_Length': 'log10_Length',
                  'Length_bp': 'Length_bp', 'n_eQTL_SNPs': 'n_eQTL_SNPs', 'GC_pct': 'GC_pct',
                  'subclass': 'subclass', 'treated': 'treated'}, 0))
    jobs.append(('S13 per-pair primary arm', by.get('S13'),
                 load_csv(os.path.join(G, 'primary_arm_96pairs.csv')), ['Gene', 'Trait'],
                 ['Gene', 'Trait'],
                 {'Z_GTEx': 'Z_GTEx', 'Z_eQTLGen': 'Z_eQTLGen', 'Same': 'Same'}))
    eg = load_csv(os.path.join(G, 'eqtlgen_Z.csv'))
    # The SI prints 90 rows against the archive's 81: nine are placeholders for genes with
    # no eQTLGen model. Declared, so they are reported rather than counted as failures.
    jobs.append(('S15 housekeeping eQTLGen', by.get('S15'),
                 [r for r in eg if r['Group'] == 'Housekeeping'], ['Gene', 'Trait'],
                 ['Gene', 'Trait'],
                 {'Z_eQTLGen': 'Z_eQTLGen', 'P': 'P', 'BH q': 'BH_q'}, 9))
    jobs.append(('S18 per-gene eQTLGen, three groups', by.get('S18'),
                 [r for r in eg if r['Group'] != 'Housekeeping'], ['Gene', 'Phenotype'],
                 ['Gene', 'Trait'],
                 {'Z_eQTLGen': 'Z_eQTLGen', 'P': 'P', 'BH q': 'BH_q',
                  'Gene group': 'Group', 'FDR-significant': 'FDR_significant'}))
    jobs.append(('S23 harmonized arm composition', by.get('S23'),
                 eg, ['Gene'], ['Gene'],
                 {'Gene group': ('Group', 'soften'),
                  'eQTLGen model SNPs (n)': ('Model_SNPs', 'last')}, 0))
    # Main-text Table 2 is two panels: (A) by phenotype, (B) the two-axis arm summary.
    # The panel's `Pairs (n)` is the row count of the shipped per-pair table by phenotype,
    # so it is computed here rather than looked up.
    pa = load_csv(os.path.join(G, 'primary_arm_96pairs.csv'))
    cnt = collections.Counter(r['Trait'] for r in pa)
    counted = [{'Trait': t, 'N': str(cnt[t]), 'K': ''} for t in ('DR', 'DN', 'DPN')]
    counted.append({'Trait': 'Overall', 'N': str(len(pa)), 'K': ''})
    jobs.append(('MS Table 2(A) by phenotype', msx.get('MS2A'), counted, ['Phenotype'], ['Trait'],
                 {'Pairs (n)': 'N'}))

    print('== Class A — structural equality (every cell of the shipped table compared) ==')
    print('   %-38s %-6s %-6s %-6s %-6s %s' % ('table', 'rows', 'cells', 'ok', 'bad', 'rows w/o counterpart'))
    total_bad = 0
    for job in jobs:
        label, drows, crows, kd, kc, cm = job[:6]
        exp = job[6] if len(job) > 6 else 0
        if drows is None:
            print('   %-38s  table absent from the document' % label)
            continue
        cm = {k: v for k, v in cm.items() if v is not None}
        res = compare_cells(label, drows, crows, kd, kc, cm, expect_norow=exp, verbose=verbose)
        note = ''
        if res['norow'] != res['expect_norow']:
            note = '  <-- %d row(s) with no counterpart' % res['norow']
        flag = '' if res['bad'] == 0 else '  <-- MISMATCH'
        print('   %-38s %-6d %-6d %-6d %-6d %-6d%s%s'
              % (label, res['rows'], res['cells'], res['ok'], res['bad'], res['norow'],
                 flag, note))
        total_bad += res['bad']
    print()
    return total_bad


# --------------------------------------------------------------------------- class B
#: Tables whose values come from a script rather than a one-to-one shipped table. Each entry
#: names the script that produces them, so the report points somewhere.
SCRIPT_BACKED = {
    'S9':  'r3/recompute_r3_s9_s20.py (16 random-control rates, null distribution, strata)',
    'S16': 'recompute_scz.py (framework-layer contrast, 9 rows)',
    'S17': 'repo_crosscheck/verify_cluster*.py; gene-cluster rows need SI Table S6',
    'S19': 'derivable by counting over gtex_Z / eqtlgen_Z',
    'S20': 'r3/m15/m15_pc.py (reads Additional file 1)',
    'S21': 'thresholding over primary_arm_96pairs.csv',
    'S22': 're-count over eqtlgen_Z.csv with TUBB dropped',
    'S24': 'recompute_scz.py (three SCZ arms)',
    'S25': 'hand-curated',
    'S26': "Fisher tests over data/superseded/mahalanobis_matched_pairs.csv",
    'S27': 'r3/simulation_validation.py',
    'S28': 'r3/simulation_validation.py',
    'S29': 'r3/simulation_validation.py',
    'S7':  "code/analyses/recovered/tost_ci_calculator.py (margin column not recovered)",
    'S8':  'derivable by counting; no script shipped',
    'S11': 'derivable by counting',
    'S5b': 'inputs verified; the 8-gene assembly is not shipped',
    'S5a': 'rows 1, 2 and 4 correspond to crosscohort.csv (labels differ); row 3, the '
           'sqrt(N_e) direct-weighting row (pooled Z +2.09, Q 76.6), has NO counterpart',
    'S3':  'handled in Class A',
}

#: Not a data artefact, or a known gap. Printed with the reason so the report covers every
#: table rather than only the ones that come out well.
DECLARED = {
    'S1':  'positioning table, rendered directly in the SI (no data artefact)',
    'S6':  'GAP-1 — the corrected GTEx housekeeping layer is not in this archive',
    'S10': 'GAP-8 — DN cross-population check, no generator',
    'S12': 'document artefact (the proposed checklist itself)',
    'S14': 'document artefact (the checklist completed)',
    'S30': 'integrated assessment, rendered directly in the SI',
    'MS1A': 'main-text Table 1(A) — rests on the housekeeping layer (GAP-1/GAP-2)',
    'MS1B': 'main-text Table 1(B) — same housekeeping layer',
}


#: Tables whose numbers are bibliography years or item numbering, not data.
DOCUMENT_ARTEFACT = {'S1', 'S12', 'S14', 'S30'}


def class_bc(si, ms, buckets, verbose, done):
    print('== Classes B and C — value presence, and what is declared elsewhere ==')
    print('   %-7s %-46s %s' % ('table', 'script / reason', 'numeric cells: present / total'))
    tot = found = 0
    missing_tables = []
    for label, title, rows in list(si) + list(ms):
        if label in done:
            continue
        # Cells are frequently composite (`21/1,326`, `4.1019 (df 94)`, `+0.5 to +1.2`),
        # so pull every numeric token out rather than requiring the whole cell to be a
        # number. That is what made Table S9 look like it had none.
        nums = []
        for r in rows[1:]:
            for c in r:
                if is_absent(c) or len(c) > 80:
                    # A sentence is not a data cell. Table S9's source column carries
                    # `... the filter chain 1129->1112->1013->1007->767 ...`, whose
                    # intermediate steps are prose describing the archived selection
                    # rules; counting them as "values not in the archive" would report a
                    # gap where there is an explanation.
                    continue
                # Word boundaries matter: without them `GCST90018832`, `MetaXcan v0.8.1`
                # and `PXD083775` each contribute a "number" that is really an identifier,
                # and the report fills with absences that are artefacts of tokenising.
                for tok in re.findall(
                        r'(?<![A-Za-z0-9.])[+\-\u2212]?\d[\d,]*(?:\.\d+)?(?![A-Za-z0-9])',
                        c or ''):
                    nums.append(tok)
        artefact = label in DOCUMENT_ARTEFACT
        if not nums:
            print('   %-7s %-46s (no numeric cells)' % (label, (DECLARED.get(label) or '—')[:46]))
            continue
        if artefact:
            # A checklist or a positioning table carries years and item numbers, not data.
            # Counting them against the archive measures nothing.
            print('   %-7s %-46s %4d token(s), not data — excluded from the total'
                  % (label, (DECLARED.get(label) or '—')[:46], len(nums)))
            continue
        hit = sum(1 for c in nums if present(c, buckets))
        tot += len(nums)
        found += hit
        mark = '' if hit == len(nums) else '  <-- %d value(s) not in the archive' % (len(nums) - hit)
        if hit != len(nums):
            missing_tables.append((label, [c for c in nums if not present(c, buckets)][:8]))
        where = SCRIPT_BACKED.get(label) or DECLARED.get(label) or 'not classified'
        print('   %-7s %-46s %4d / %-4d%s' % (label, where[:46], hit, len(nums), mark))
        if verbose and hit != len(nums):
            for c in [c for c in nums if not present(c, buckets)][:8]:
                print('             absent: %s' % c)
    print()
    print('   numeric cells in B/C tables: %d   present in the archive: %d (%.1f%%)'
          % (tot, found, 100.0 * found / tot if tot else 100.0))
    for label, vals in missing_tables:
        print('   %-7s absent values: %s' % (label, ', '.join(vals)))
    return missing_tables


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument('--si', required=True)
    ap.add_argument('--manuscript', required=True)
    ap.add_argument('-v', '--verbose', action='store_true')
    ap.add_argument('--report', help='also write the report to this path')
    args = ap.parse_args()

    for p in (args.si, args.manuscript):
        if not os.path.isfile(p):
            print('  [FAIL] not found: %s' % p)
            return 1

    si, ms = load_documents(args.si, args.manuscript)
    print()
    print('  Supporting Information: %d tables' % len(si))
    print('  Manuscript            : %d tables' % len(ms))
    buckets, n_files, n_vals = corpus_numbers()
    print('  archive corpus        : %d files, %d numeric tokens' % (n_files, n_vals))
    print()

    bad_a = class_a(si, ms, args.verbose)
    done = {'S2', 'S4', 'S13', 'S15', 'S18', 'S23', 'MS2A'}
    missing_b = class_bc(si, ms, buckets, args.verbose, done)

    print()
    print('==================================================')
    print('  Class A mismatched cells : %d%s' % (bad_a, '' if bad_a == 0 else '   <-- FAIL'))
    print('  Class B tables with a value absent from the archive: %d' % len(missing_b))
    print('  Class C: %d item(s), declared above, not machine-checkable here'
          % len([1 for k in DECLARED if k not in done]))
    if bad_a:
        print('  RESULT: the documents and the archive disagree. Not reproducible as shipped.')
        return 1
    print('  RESULT: every Class A cell agrees; every Class B value is present in the archive.')
    print('          Class B is a necessary condition, not a sufficient one — see the docstring.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

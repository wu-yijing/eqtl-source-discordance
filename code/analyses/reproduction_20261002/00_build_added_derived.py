# -*- coding: utf-8 -*-
"""00 — build the derived tables added on 2026-10-02.

Run this only if you hold the upstream sources; the outputs are already tracked in
`data/derived/`, so a reader who just wants to reproduce a reported value does not
need it. It exists so that every added table has a stated, re-runnable origin.

Sources (all environment variables; `code/analyses/reproduction_20261002/INPUTS.md`
section B says where each one comes from):

    REPRO_T1_DIR             the five genome-wide Z layers (eqz_full.csv,
                             gtex/official_{Whole_Blood,Nerve_Tibial}.csv,
                             en/official_en_{Whole_Blood,Nerve_Tibial}.csv)
    REPRO_HRT_SOURCE         HRT Atlas v1.0 human-mouse common set (semicolon TSV)
    REPRO_RAND_DIR           official MetaXcan output for the random-control genes
    REPRO_COVARIATE          the 104-gene panel covariance table
    REPRO_GROUPS_JSON        POOL_818 / arm group definitions
    REPRO_MASHR_DB_DIR       mashr_Whole_Blood.db, mashr_Nerve_Tibial.db
    REPRO_GTEX_OFFICIAL_DIR  the six official MetaXcan GTEx x FinnGen tables

    python 00_build_added_derived.py

Writes, all under `data/derived/`:

| output | built from | why it is here |
|---|---|---|
| `genomewide/eqz_full.csv.gz` | eQTLGen whole-blood S-PrediXcan output | defines the 10,357-gene model pool and the universe counts |
| `genomewide/gtex_official_Whole_Blood.csv.gz` | GTEx v8 MASHR Whole_Blood | weight-source A arm |
| `genomewide/gtex_official_Nerve_Tibial.csv.gz` | GTEx v8 MASHR Nerve_Tibial | weight-source A arm |
| `genomewide/en_official_en_Whole_Blood.csv.gz` | GTEx v8 elastic-net Whole_Blood | the framework-layer cross-weight arm (Table S16) |
| `genomewide/en_official_en_Nerve_Tibial.csv.gz` | GTEx v8 elastic-net Nerve_Tibial | as above |
| `gtex_official_finngen/gtex_official_zscores_wide.csv.gz` | the six official MetaXcan GTEx x FinnGen tables | one row per gene; feeds the Table S9 ACAT-O chain |
| `covariate_matrix.csv` | the 104-gene panel table | defines the panel, hence the exclusion chain |
| `hrt/Human_Mouse_Common.csv` | HRT Atlas v1.0 | POOL_818 source |
| `hrt_random_control/official_rand_{DR,DN,DPN}.csv` | official MetaXcan on the random-control genes | Table S9 random-control rates |
| `groups.json` | group definitions | Table S9 stratification |
| `s9_pools/*.txt` | mashr databases + the files above | Table S9 pool membership |
"""
import csv
import gzip
import io
import os
import re
import shutil
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths_config as P  # noqa: E402

P.apply_cli_overrides()

TRAITS = ['DR', 'DN', 'DPN']
TISSUES = ['Nerve_Tibial', 'Whole_Blood']
EXTRA_FAMILY = re.compile(r'^(MRPS|MRPL|MT-|MTRNR|MTND|MTATP|MTCO|MTCYB)')
HERE = P.HERE


def write_lf(path, text):
    """Write UTF-8 with LF, whatever the platform.

    `paths_config` records each shipped file's byte size and asserts it, so a CRLF
    working copy would make that check fail on a fresh LF clone.
    """
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def copy_lf(src, dst):
    """Copy a text file, normalising CRLF to LF."""
    with open(src, 'rb') as f:
        data = f.read()
    with open(dst, 'wb') as f:
        f.write(data.replace(b'\r\n', b'\n').replace(b'\r', b'\n'))

SOURCES = {
    't1': ('REPRO_T1_DIR', 'the five genome-wide Z layers'),
    'hrt': ('REPRO_HRT_SOURCE', 'HRT Atlas v1.0 human-mouse common set'),
    'rand': ('REPRO_RAND_DIR', 'official MetaXcan output for the random-control genes'),
    'covariate': ('REPRO_COVARIATE', 'the 104-gene panel covariance table'),
    'groups': ('REPRO_GROUPS_JSON', 'POOL_818 / arm group definitions'),
    'mashr': ('REPRO_MASHR_DB_DIR', 'mashr_Whole_Blood.db, mashr_Nerve_Tibial.db'),
    'gtexm': ('REPRO_GTEX_OFFICIAL_DIR', 'the six official MetaXcan GTEx x FinnGen tables'),
}


def src(key):
    env, what = SOURCES[key]
    v = os.environ.get(env)
    if not v or not os.path.exists(v):
        raise SystemExit('[missing source] %s is unset or does not exist: %r\n'
                         '  needed for: %s\n  see INPUTS.md section B' % (env, v, what))
    return v


def shipped_or(key, rel):
    """Prefer the copy that already ships here; fall back to the external source.

    Once a layer is in `data/derived/`, requiring its original again is a false
    dependency: it made the Table S9 pool derivation unrunnable from a clone even after
    the data layer had landed, which is the whole distinction ARCHIVE_MAP's `Input
    locality` column draws.
    """
    p = os.path.join(P.DERIVED, *rel.split('/'))
    if os.path.exists(p):
        return p
    return src(key)


def log(*a):
    print('  ' + ' '.join(str(x) for x in a))


def disease_blacklist():
    """The T2DM / complication / metabolic gene list, taken from the committed script.

    Written **verbatim**, without upper-casing. The gene sets it is subtracted from
    are upper-cased (`meta[...]` keys come from `genename.upper()`), and the
    published chain subtracts a case-sensitive set, so a token whose spelling is
    not already all-caps does not in fact exclude anything. Exactly one token in
    the list is affected — `C5orf67` — which is why the published POOL_A is 11,820
    rather than 11,819. Reproduced as-is; flagged in `INPUTS.md`.
    """
    p = os.path.join(HERE, 'scripts', 'r3', 'recompute_r3_s9_s20.py')
    m = re.search(r'else """(.*?)"""\.split\(\)\)', open(p, encoding='utf-8').read(), re.S)
    if not m:
        raise RuntimeError('could not locate the inline disease blacklist in %s' % p)
    tokens = m.group(1).split()
    genes = sorted(set(tokens))
    out = os.path.join(P.DERIVED, 's9_pools')
    os.makedirs(out, exist_ok=True)
    # write_lf, not open(..., 'w'): the default text mode translates '\n' to os.linesep,
    # so on Windows this rebuild produced a CRLF file whose MD5 did not match the LF
    # value recorded in paths_config.SHIPPED — rebuilding the package broke the
    # package's own integrity check.
    write_lf(os.path.join(out, 'disease_blacklist.txt'), '\n'.join(genes) + '\n')
    mixed = [g for g in genes if g != g.upper()]
    log('s9_pools/disease_blacklist.txt   %3d tokens%s'
        % (len(genes), ('  (not all-caps, so inert: %s)' % ', '.join(mixed)) if mixed else ''))
    return set(genes)


def build_genomewide():
    t1 = src('t1')
    os.makedirs(P.GENOMEWIDE, exist_ok=True)
    jobs = [('eqz_full.csv', 'eqz_full.csv.gz', 'eQTLGen whole blood'),
            ('gtex/official_Whole_Blood.csv', 'gtex_official_Whole_Blood.csv.gz', 'GTEx v8 MASHR Whole_Blood'),
            ('gtex/official_Nerve_Tibial.csv', 'gtex_official_Nerve_Tibial.csv.gz', 'GTEx v8 MASHR Nerve_Tibial'),
            ('en/official_en_Whole_Blood.csv', 'en_official_en_Whole_Blood.csv.gz', 'GTEx v8 elastic-net Whole_Blood'),
            ('en/official_en_Nerve_Tibial.csv', 'en_official_en_Nerve_Tibial.csv.gz', 'GTEx v8 elastic-net Nerve_Tibial')]
    for rel, dst, what in jobs:
        s = os.path.join(t1, *rel.split('/'))
        if not os.path.exists(s):
            raise SystemExit('[missing source] %s' % s)
        with open(s, 'rb') as fi, gzip.GzipFile(os.path.join(P.GENOMEWIDE, dst), 'wb', mtime=0) as fo:
            shutil.copyfileobj(fi, fo)
        os.utime(os.path.join(P.GENOMEWIDE, dst), (315532800, 315532800))
        log('genomewide/%-38s <- %-44s %s' % (dst, rel, what))


def build_gtex_official_wide():
    """Flatten the six official MetaXcan tables to one row per gene (max |z| wins).

    The z-score is stored as the **original string**, not a reformatted float: the
    source tables carry more precision than `%g` would preserve, and two of the
    Table S9 statistics (the median |Z| columns) are reported to seven significant
    digits, so a lossy round-trip would be visible.
    """
    d = src('gtexm')
    wide = {}
    for tis in TISSUES:
        for tr in TRAITS:
            fp = os.path.join(d, 'official_%s_%s.csv' % (tis, tr))
            if not os.path.exists(fp):
                raise SystemExit('[missing source] %s' % fp)
            for r in csv.DictReader(open(fp, encoding='utf-8')):
                sym = r.get('gene_name')
                if not sym:
                    continue
                raw = (r.get('zscore') or '').strip()
                try:
                    z = float(raw)
                except (TypeError, ValueError):
                    continue
                k = (sym, tis, tr)
                if k not in wide or abs(z) > abs(float(wide[k])):
                    wide[k] = raw
    genes = sorted({k[0] for k in wide})
    out = os.path.join(P.DERIVED, 'gtex_official_finngen')
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, 'gtex_official_zscores_wide.csv.gz')
    cols = ['%s_%s' % (t, tr) for t in TISSUES for tr in TRAITS]
    with gzip.GzipFile(path, 'wb', mtime=0) as f:
        w = io.TextIOWrapper(f, encoding='utf-8', newline='')
        cw = csv.writer(w)
        cw.writerow(['gene'] + cols)
        for g in genes:
            cw.writerow([g] + [wide.get((g, t, tr), '') for t in TISSUES for tr in TRAITS])
        w.flush()
    os.utime(path, (315532800, 315532800))
    log('gtex_official_finngen/gtex_official_zscores_wide.csv.gz  %d genes x %d columns'
        % (len(genes), len(cols)))


def read_mashr_dbs():
    """{tissue: {SYMBOL: n_snps_in_model}}, straight out of the mashr model databases."""
    mash = src('mashr')
    meta = {}
    for t in TISSUES:
        fp = os.path.join(mash, 'mashr_%s.db' % t)
        if not os.path.exists(fp):
            raise SystemExit('[missing source] %s' % fp)
        conn = sqlite3.connect(fp)
        meta[t] = {gn.upper(): n for _, gn, n in
                   conn.execute('SELECT gene, genename, "n.snps.in.model" FROM extra') if gn}
        conn.close()
    return meta


def build_mashr_nsnps():
    """Export the single column the Table S9 pool filters actually read.

    The mashr model databases are 10.5 MB of SQLite that only an R toolchain opens, and
    the pool construction reads exactly one thing from them: `n.snps.in.model`, per gene,
    for two tissues. Exporting that as a projection makes the pool re-derivation — as
    opposed to the reproduction of its outcome — possible from a clone, which is what
    ARCHIVE_MAP's `Input locality` column distinguishes. About 60 kB gzipped.
    """
    db = read_mashr_dbs()
    genes = sorted(set(db[TISSUES[0]]) | set(db[TISSUES[1]]))
    path = os.path.join(P.DERIVED, 'mashr_nsnps.csv.gz')
    with gzip.GzipFile(path, 'wb', mtime=0) as f:
        w = io.TextIOWrapper(f, encoding='utf-8', newline='')
        cw = csv.writer(w)
        cw.writerow(['gene'] + list(TISSUES))
        for g in genes:
            cw.writerow([g] + [db[t].get(g, '') for t in TISSUES])
        w.flush()
    os.utime(path, (315532800, 315532800))
    log('mashr_nsnps.csv.gz  %d genes x %d tissues  (%d / %d with a model)'
        % (len(genes), len(TISSUES),
           len(db[TISSUES[0]]), len(db[TISSUES[1]])))


def load_model_snps():
    """The model-SNP counts, from the shipped projection rather than the databases.

    If `REPRO_MASHR_DB_DIR` is set the databases are read as well and the two must agree
    exactly. That is the point of the cross-check: a projection that has silently drifted
    from the models it summarises would keep reproducing the published chain while no
    longer standing for anything.
    """
    path = os.path.join(P.DERIVED, 'mashr_nsnps.csv.gz')
    if not os.path.exists(path):
        raise SystemExit('[missing input] %s\n  run 00_build_mashr_nsnps (see INPUTS.md A)'
                         % path)
    meta = {t: {} for t in TISSUES}
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            for t in TISSUES:
                v = (row.get(t) or '').strip()
                if v:
                    meta[t][row['gene'].upper()] = int(v)

    if os.environ.get('REPRO_MASHR_DB_DIR'):
        db = read_mashr_dbs()
        for t in TISSUES:
            if db[t] != meta[t]:
                shared = set(db[t]) & set(meta[t])
                raise SystemExit(
                    '[projection mismatch] %s: %d gene(s) only in the databases, %d only in '
                    'the projection, %d value(s) differ — regenerate it'
                    % (t, len(set(db[t]) - set(meta[t])), len(set(meta[t]) - set(db[t])),
                       sum(1 for g in shared if db[t][g] != meta[t][g])))
        log('mashr_nsnps.csv.gz cross-checked against both databases: identical')
    return meta


def build_pools():
    panel = {r['Gene'].upper() for r in
             csv.DictReader(open(shipped_or('covariate', 'covariate_matrix.csv'),
                                 encoding='utf-8'))}
    fams = set()
    for g in panel:
        m = re.match(r'^([A-Za-z]+)', g)
        if m and len(m.group(1)) >= 3:
            fams.add(m.group(1).upper())
    disease = disease_blacklist()

    meta = load_model_snps()

    def strip(gs):
        gs = {g for g in gs if g not in panel}
        gs = {g for g in gs if not (any(g.startswith(p) for p in fams) or EXTRA_FAMILY.match(g))}
        return {g for g in gs if g not in disease}

    wb_ok = {g: n for g, n in meta['Whole_Blood'].items() if n and n >= 1}
    flow = [('WB model genes', len(wb_ok))]
    after_panel = {g for g in wb_ok if g not in panel}
    flow.append(('minus 104-panel', len(after_panel)))
    after_fam = {g for g in after_panel
                 if not (any(g.startswith(p) for p in fams) or EXTRA_FAMILY.match(g))}
    flow.append(('minus panel families', len(after_fam)))
    pool_a = {g for g in after_fam if g not in disease}
    flow.append(('minus disease blacklist = POOL_A', len(pool_a)))
    both_a = {g for g in pool_a if meta['Nerve_Tibial'].get(g, 0) and meta['Nerve_Tibial'][g] >= 1}
    flow.append(('of which have BOTH-tissue models', len(both_a)))
    log('POOL_A chain: ' + '  ->  '.join('%s %s' % (k, format(v, ',')) for k, v in flow))
    log('  (published: 12,622 -> 12,555 -> 11,885 -> POOL_A 11,820, of which 10,450 both-tissue)')

    hrt = set()
    with open(shipped_or('hrt', 'hrt/Human_Mouse_Common.csv'),
              encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.lower().startswith('mouse'):
                continue
            p = line.split(';')
            if len(p) >= 2 and p[1].strip():
                hrt.add(p[1].strip().upper())
    c2 = strip(hrt)
    pool_818 = {g for g in c2 if meta['Whole_Blood'].get(g, 0) and meta['Whole_Blood'][g] >= 1}
    both_818 = {g for g in pool_818 if meta['Nerve_Tibial'].get(g, 0) and meta['Nerve_Tibial'][g] >= 1}
    log('POOL_818 = %d (published 818), both-tissue %d (published 767), WB-only %d (published 51)'
        % (len(pool_818), len(both_818), len(pool_818 - both_818)))

    out = os.path.join(P.DERIVED, 's9_pools')
    os.makedirs(out, exist_ok=True)
    for name, gs in [('POOL_A', pool_a), ('both_A', both_a),
                     ('POOL_818', pool_818), ('both_818', both_818)]:
        write_lf(os.path.join(out, name + '.txt'), '\n'.join(sorted(gs)) + '\n')
        log('s9_pools/%-24s %6d genes' % (name + '.txt', len(gs)))


def copy_small():
    """Place the small shipped inputs. Skip any whose source is absent but whose copy
    already ships — the aim is that a clone can rebuild the derivations, not that it can
    obtain third-party originals it was never given.

    `copy_lf`, not `shutil.copyfile`: the sources are CRLF on the author's disk while
    `.gitattributes` declares `eol=lf` for these files, so a plain copy produced a shipped
    input whose MD5 could never match the recorded one.
    """
    jobs = [('hrt', 'hrt/Human_Mouse_Common.csv', 'hrt/Human_Mouse_Common.csv'),
            ('covariate', 'covariate_matrix.csv', 'covariate_matrix.csv'),
            ('groups', 'groups.json', 'groups.json')]
    for key, rel, dst_rel in jobs:
        dst = os.path.join(P.DERIVED, *dst_rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        s = shipped_or(key, dst_rel)
        if s == dst:
            log('%-34s already shipped, left as is' % dst_rel)
            continue
        copy_lf(s, dst)
        log(dst_rel)
    os.makedirs(os.path.join(P.DERIVED, 'hrt_random_control'), exist_ok=True)
    for tr in TRAITS:
        dst = os.path.join(P.DERIVED, 'hrt_random_control', 'official_rand_%s.csv' % tr)
        if os.path.exists(dst) and not os.environ.get('REPRO_RAND_DIR'):
            log('hrt_random_control/official_rand_%s.csv  already shipped' % tr)
            continue
        s = os.path.join(src('rand'), 'official_rand_%s.csv' % tr)
        if not os.path.exists(s):
            raise SystemExit('[missing source] %s' % s)
        copy_lf(s, dst)
        log('hrt_random_control/official_rand_%s.csv' % tr)


if __name__ == '__main__':
    print('=== sources ===')
    for k, (env, what) in SOURCES.items():
        v = os.environ.get(env)
        print('  %-28s %s  %s' % (env, ('ok   ' if v and os.path.exists(v) else 'ABSENT'), what))
    print()
    print('=== building ===')
    build_genomewide()
    build_gtex_official_wide()
    build_mashr_nsnps()
    build_pools()
    copy_small()
    print()
    print('done. Now run:  python paths_config.py   to verify.')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate metadata/provenance.json.

Hashes every file the reported numbers depend on, and records the external-input
manifest. Run before each release; `scripts/cut_release.sh` warns if the file
still contains placeholders.

    python scripts/collect_provenance.py

The external-input half is documentation, not discovery: those resources are not
redistributed here, so their hashes are recorded as `not-held` until someone with
the file on disk records them. Identifiers, versions and the retrieval date come
from Supporting Information Note S4.
"""
import hashlib
import json
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, 'metadata', 'provenance.json')

# Directories whose contents back a reported number.
HASH_DIRS = ['data/derived', 'code/analyses/recovered', 'code/figures']

# Supporting Information Note S4 — identifiers, versions, retrieval date.
EXTERNAL = [
    ("FinnGen", "primary GWAS input: DR / DN / DPN", "Data Freeze 13 (R13)",
     "https://www.finngen.fi/en/access_results"),
    ("GCST90043640", "UK Biobank diabetic retinopathy GWAS (PheCode 250.7); cross-cohort arm",
     "as distributed by GWAS Catalog", "https://www.ebi.ac.uk/gwas/studies/GCST90043640",
     "Publication recorded by GWAS Catalog: Jiang L, Zheng Z, Fang H, Yang J. Nat Genet 2021;53:1616-1621. doi:10.1038/s41588-021-00954-4"),
    ("GCST90018832", "cross-population diabetic nephropathy meta-analysis (DN check)",
     "as distributed by GWAS Catalog", "https://www.ebi.ac.uk/gwas/studies/GCST90018832"),
    ("PGC3_SCZ_wave3", "independent-trait genome-wide benchmark", "schizophrenia wave 3 (scz2022)",
     "https://pgc.unc.edu/for-researchers/download-results/"),
    ("GTEx_v8_MASHR", "eQTL weight source A: Nerve_Tibial and Whole_Blood",
     "GTEx v8 MASHR models", "https://predictdb.org/post/2021/07/21/gtex-v8-models-on-eqtl-and-sqtl"),
    ("eQTLGen_phaseI", "eQTL weight source B", "phase I cis-eQTL, N = 31,684",
     "https://www.eqtlgen.org/"),
    ("1000G_phase3_EUR", "linkage-disequilibrium reference panel", "Phase 3 European panel",
     "https://www.internationalgenome.org/"),
    ("ProteomeXchange_iProX", "RNA pull-down LC-MS/MS",
     "PXD083775 (iProX IPX0019439000, subproject IPX0019439001)",
     "https://proteomecentral.proteomexchange.org/"),
]

ANCESTRY_NOTE = (
    "For every GWAS resource, record the COMPLETE population composition of the source and "
    "state separately which subset was used. GCST90018832, for example, is a cross-population "
    "diabetic-nephropathy resource that includes East Asian participants alongside European "
    "participants; a table note listing only the European component is incomplete, and a "
    "Limitations statement that says 'all GWAS analyzed here comprise participants of European "
    "ancestry' contradicts the Methods. Both defects existed in an earlier revision."
)


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(chunk), b''):
            h.update(block)
    return h.hexdigest()


def main():
    files = []
    for d in HASH_DIRS:
        root = os.path.join(REPO, d)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [x for x in dirnames if x != '__pycache__']
            for fn in sorted(filenames):
                if fn.startswith('.'):
                    continue
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, REPO).replace(os.sep, '/')
                files.append({"path": rel, "bytes": os.path.getsize(p), "sha256": sha256(p)})
    files.sort(key=lambda x: x['path'])

    external = []
    for row in EXTERNAL:
        rid, role, version, url = row[0], row[1], row[2], row[3]
        entry = {
            "id": rid, "role": role, "version": version, "source_url": url,
            "retrieved": "2026-09-08",
            "retrieval_note": "Supporting Information Note S4 states: 'Every resource was retrieved on 8 September 2026.'",
            "sha256": "not-held",
            "sha256_note": "Not redistributed with this archive. Record the hash the first time someone runs this against the downloaded file.",
        }
        if len(row) > 4:
            entry["citation"] = row[4]
        external.append(entry)

    doc = {
        "_note": ("Provenance manifest. Regenerate with scripts/collect_provenance.py before each "
                  "release. 'external_inputs' is documentation; 'files' are hashed from this tree."),
        "schema_version": "2.0",
        "generated_by": {
            "script": "scripts/collect_provenance.py",
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "metaxcan": "MetaXcan v0.8.1 (official binary)",
            "analysis_env": "Python 3.13.0 / R 4.5.2 with MatchIt, pinned as env/environment.yml and env/renv.lock",
        },
        "external_inputs": external,
        "external_input_caveat": ANCESTRY_NOTE,
        "files": files,
        "file_count": len(files),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write('\n')
    print('wrote %s  (%d files hashed, %d external inputs)' % (OUT, len(files), len(external)))


if __name__ == '__main__':
    main()

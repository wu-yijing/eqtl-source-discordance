#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_SI_structure.py — check the SI package structure, and that a rebuilt
revision carries the intended text.

WHY
===
A Supporting Information revision was saved through the editor channel this
project had already decided against. The damage is measurable and this script is
what measures it: package part count, and three `word/document.xml` markers that
the editor channel drops —

    w:tblPrEx     table-property exceptions (cell-level borders / margins)
    w:tblCellMar  table cell margins
    w:tblBorders  table borders

`styles.xml` is reported too, so that "the definitions were dropped" can be told
apart from "the definitions were moved into a table style".

It also compares the visible text of the inputs, so a rebuild can be shown to
carry the later revision's text while keeping the earlier revision's package.

Usage
-----
    python verify_SI_structure.py --base BASE.docx --target TARGET.docx [--rebuilt OUT.docx]
    python verify_SI_structure.py --base ... --target ... --rebuilt ... --json out.json

Exit status 0 always; the verdict is in the report (`checks` in the JSON).
"""
import argparse
import json
import os
import sys
import zipfile

import docx

MARKERS = ("tblPrEx", "tblCellMar", "tblBorders", "insideH")


def probe(path):
    z = zipfile.ZipFile(path)
    names = [i.filename for i in z.infolist()]
    doc = z.read("word/document.xml").decode("utf-8", "replace")
    sty = z.read("word/styles.xml").decode("utf-8", "replace") if "word/styles.xml" in names else ""
    d = docx.Document(path)
    text = [p.text for p in d.paragraphs]
    for t in d.tables:
        for r in t.rows:
            text.append(" | ".join(c.text for c in r.cells))
    return {
        "path": path,
        "bytes": os.path.getsize(path),
        "parts": len(names),
        "part_names": sorted(names),
        "document_xml_bytes": len(doc.encode("utf-8")),
        "markers": {m: doc.count(m) for m in MARKERS},
        "styles_xml_bytes": len(sty.encode("utf-8")),
        "styles_markers": {m: sty.count(m) for m in MARKERS},
        "text_units": len(text),
        "text": text,
        "text_join": "\n".join(text),
    }


def main():
    ap = argparse.ArgumentParser(description="check an SI package's structure")
    ap.add_argument("--base", required=True, help="the revision with the good package")
    ap.add_argument("--target", required=True, help="the revision whose text is wanted")
    ap.add_argument("--rebuilt", help="the rebuilt file, if there is one")
    ap.add_argument("--json")
    a = ap.parse_args()

    b = probe(a.base)
    t = probe(a.target)
    out = {"base": a.base, "target": a.target, "rebuilt": a.rebuilt, "checks": {}}

    def show(tag, p):
        print("%-10s parts %2d  document.xml %8d B  %s  styles %6d B  text %5d"
              % (tag, p["parts"], p["document_xml_bytes"],
                 "  ".join("%s=%d" % (m, p["markers"][m]) for m in MARKERS),
                 p["styles_xml_bytes"], p["text_units"]))

    print("file            package / markers")
    print("-" * 96)
    show("base", b)
    show("target", t)

    # 1. the regression, described
    reg = {m: (b["markers"][m], t["markers"][m]) for m in MARKERS
           if b["markers"][m] != t["markers"][m]}
    out["regression"] = {"marker_from_to": reg, "parts_from_to": [b["parts"], t["parts"]]}
    out["styles_unchanged"] = b["styles_markers"] == t["styles_markers"]
    print("\nregression   parts %d -> %d" % (b["parts"], t["parts"]))
    for m, (x, y) in reg.items():
        print("             %-12s %d -> %d" % (m, x, y))
    print("             styles.xml markers unchanged: %s" % out["styles_unchanged"])

    r = None
    if a.rebuilt:
        r = probe(a.rebuilt)
        show("rebuilt", r)
        out["checks"]["package_restored"] = r["parts"] == b["parts"]
        out["checks"]["markers_restored"] = all(r["markers"][m] == b["markers"][m] for m in MARKERS)
        out["checks"]["text_is_target"] = r["text"] == t["text"]
        out["checks"]["styles_unchanged"] = r["styles_markers"] == b["styles_markers"]
        out["rebuilt_record"] = {k: r[k] for k in
                                 ("bytes", "parts", "document_xml_bytes", "markers",
                                  "styles_xml_bytes", "text_units")}
        print("\nrebuilt vs base    parts %d == %d : %s"
              % (r["parts"], b["parts"], out["checks"]["package_restored"]))
        print("rebuilt vs base    all markers equal : %s" % out["checks"]["markers_restored"])
        print("rebuilt vs target  text identical    : %s" % out["checks"]["text_is_target"])
        if not out["checks"]["text_is_target"]:
            for i, (x, y) in enumerate(zip(t["text"], r["text"])):
                if x != y:
                    print("  first difference at unit %d:\n    target  %r\n    rebuilt %r"
                          % (i, x[:110], y[:110]))
                    break

    if a.json:
        slim = dict(out)
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(slim, fh, indent=1, sort_keys=True)
            fh.write("\n")
        print("\nwrote %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())

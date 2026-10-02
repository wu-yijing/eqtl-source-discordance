# -*- coding: utf-8 -*-
"""格式无关比对：分数 k/N、百分数、ρ 值的集合差异（BMC 定稿 vs GE 投稿稿）。"""
# ---------------------------------------------------------------------------
# Path resolution (added 2026-10-02). Satisfies code/README.md rule 3:
# "No absolute paths, no personal directories."
# ---------------------------------------------------------------------------
import os as _os
import sys as _sys


def _repro_pkg():
    d = _os.path.dirname(_os.path.abspath(__file__))
    for _ in range(6):
        if _os.path.exists(_os.path.join(d, 'paths_config.py')):
            return d
        d = _os.path.dirname(d)
    raise RuntimeError('paths_config.py not found above %s' % __file__)


_sys.path.insert(0, _repro_pkg())
import paths_config as PC        # noqa: E402
PC.apply_cli_overrides()
# ---------------------------------------------------------------------------

import re, zipfile, collections
from xml.etree import ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def pt(p):
    o=[]
    for n in p.iter():
        if n.tag==W+'t': o.append(n.text or '')
        elif n.tag==W+'tab': o.append(' ')
    return ''.join(o)
def full(path):
    z=zipfile.ZipFile(path); root=ET.fromstring(z.read('word/document.xml'))
    parts=[pt(p) for p in root.iter(W+'p')]
    for tbl in root.iter(W+'tbl'):
        for tr in tbl.findall(W+'tr'):
            parts.append(' | '.join(' '.join(pt(p) for p in tc.findall(W+'p')).strip() for tc in tr.findall(W+'tc')))
    return ' \u241F '.join(x for x in parts if x.strip())
BMC=full(PC.doc('pred_manuscript'))
GE =full(PC.doc('manuscript'))

def ctx(t,s,w=80):
    m=re.search(re.escape(s),t); return '—' if not m else t[max(0,m.start()-w):m.end()+w].replace('\u241F',' | ')

FRAC=re.compile(r'(?<![\d.])(\d{1,3})/(\d{1,3})(?![\d.])')
def fracs(t):
    c=collections.Counter()
    for a,b in FRAC.findall(t): c[f'{a}/{b}']+=1
    return c
PCT=re.compile(r'(?<![\d.])(\d{1,3}\.\d)%')
def pcts(t): return collections.Counter(PCT.findall(t))
RHO=re.compile(r'ρ\s*[=≈]\s*[+\-−]?(0\.\d{2,4})')
def rhos(t): return collections.Counter(x.replace('−','-') for x in RHO.findall(t))

for name,fn,lab in [('分数 k/N',fracs,'分数'),('百分数 %',pcts,'百分数'),('ρ 值',rhos,'ρ')]:
    b=fn(BMC); g=fn(GE)
    onlyB=sorted(set(b)-set(g)); onlyG=sorted(set(g)-set(b))
    print('='*104); print(f'{name}：BMC {len(b)} 种 / GE {len(g)} 种 ｜ 仅 BMC {len(onlyB)} 种，仅 GE {len(onlyG)} 种')
    print('='*104)
    if onlyB:
        print('  仅 BMC 有：')
        for s in onlyB[:26]:
            print(f'    {s:10s} BMC×{b[s]:<2d} | ' + ctx(BMC,s)[:150])
        if len(onlyB)>26: print(f'    ...（省略 {len(onlyB)-26} 项）')
    if onlyG:
        print('  仅 GE 有：')
        for s in onlyG:
            print(f'    {s:10s} GE×{g[s]:<2d} | ' + ctx(GE,s)[:150])
    print()

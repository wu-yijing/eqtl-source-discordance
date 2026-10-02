# -*- coding: utf-8 -*-
import re, zipfile
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
import sys as _sys, os as _os
_p = _os.path.dirname(_os.path.abspath(__file__))
while _p != _os.path.dirname(_p) and not _os.path.isfile(_os.path.join(_p, 'paths.py')):
    _p = _os.path.dirname(_p)
_sys.path.insert(0, _p)
import paths as _paths          # noqa: E402  集中路径解析：向上找到 paths.py
_paths.bootstrap_args()   # 消费 --repo-root / --input（本脚本无自有 parser）
GE=full(str(_paths.external('manuscript_docx')))
BMC=full(str(_paths.external('bmc_manuscript_docx')))
PROBES=['df','permutation','67.6','0.373','102','5,584','5,551','5,506','9,048','0.784','0.638','0.525','0.647',
        '0.14','2.38','3.70','-0.05','−0.05','2.97','3.69','3,910','6,310','6,014','70.4','65.2','67.4','0.32','0.36']
for p in PROBES:
    mg=re.findall(r'.{55}'+re.escape(p)+r'.{55}', GE)
    mb=re.findall(r'.{55}'+re.escape(p)+r'.{55}', BMC)
    print(f'── {p:12s} GE×{len(mg)}  BMC×{len(mb)}')
    for x in mg[:2]: print('     GE :', x.replace('\u241F','|'))
    if not mg:
        for x in mb[:1]: print('     BMC:', x.replace('\u241F','|'))
        print('     GE : —— 无')

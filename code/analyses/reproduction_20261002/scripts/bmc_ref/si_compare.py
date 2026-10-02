# -*- coding: utf-8 -*-
import re, zipfile, hashlib
from xml.etree import ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def pt(p):
    o=[]
    for n in p.iter():
        if n.tag==W+'t': o.append(n.text or '')
        elif n.tag==W+'tab': o.append(' ')
    return ''.join(o)
def load(path):
    z=zipfile.ZipFile(path); root=ET.fromstring(z.read('word/document.xml'))
    body=root.find(W+'body'); ch=list(body)
    titles=[]; notes=[]; lastps=[]
    for k,c in enumerate(ch):
        if c.tag==W+'p':
            t=pt(c).strip()
            if t: lastps.append(t); lastps=lastps[-2:]
        elif c.tag==W+'tbl':
            rows=[]
            for tr in c.findall(W+'tr'):
                rows.append([' '.join(pt(p) for p in tc.findall(W+'p')).strip() for tc in tr.findall(W+'tc')])
            titles.append((len(rows), len(rows[0]) if rows else 0, lastps[-1] if lastps else ''))
    return titles
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import paths as _paths          # noqa: E402  集中路径解析，见 ../paths.py
B=load(str(_paths.external('bmc_additional_file1_docx')))
G=load(str(_paths.external('si_docx')))
print(f'BMC AF1 表数 {len(B)}  |  GE SI 表数 {len(G)}')
print()
print('=== BMC AF1 表目录（行×列 | 表题前 100 字）===')
for i,(r,c,t) in enumerate(B): print(f'  {i:02d} {r:>3}r×{c:<2}c | {t[:100]}')
print()
print('=== 表题集合差异 ===')
def norm(t): return re.sub(r'[\s\u00a0]+','',t)[:60]
sb={norm(t):i for i,(r,c,t) in enumerate(B)}
sg={norm(t):i for i,(r,c,t) in enumerate(G)}
ob=[k for k in sb if k not in sg]; og=[k for k in sg if k not in sb]
print(f'  仅 BMC 有 {len(ob)} 条：')
for k in ob[:20]: print(f'     [{sb[k]:02d}] {k[:90]}')
print(f'  仅 GE 有 {len(og)} 条：')
for k in og[:20]: print(f'     [{sg[k]:02d}] {k[:90]}')

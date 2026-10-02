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
def load(path):
    z=zipfile.ZipFile(path); root=ET.fromstring(z.read('word/document.xml'))
    ch=list(root.find(W+'body')); out=[]; last=[]
    for c in ch:
        if c.tag==W+'p':
            t=pt(c).strip()
            if t: last.append(t); last=last[-1:]
        elif c.tag==W+'tbl':
            rows=[[ ' '.join(pt(p) for p in tc.findall(W+'p')).strip() for tc in tr.findall(W+'tc')] for tr in c.findall(W+'tr')]
            out.append((len(rows), len(rows[0]) if rows else 0, (last[-1] if last else ''), rows))
    return out
B=load(r'E:/workbuddy/BMC Genomics投稿资料\投稿前定稿\Additional_file_1.docx')
G=load(r'E:/workbuddy/GE投稿资料/_修订_20260930/Supporting_Information_GenetEpidemiol_20260930.docx')
def tabno(t):
    m=re.match(r'Table\s*S(\d+[a-z]?)', t.strip()); return m.group(1) if m else '?'
def sig(r):  # 内容指纹：行数 + 列数 + 首行拼接的哈希
    import hashlib
    h=hashlib.md5(('|'.join(r[3][0])).encode('utf-8')).hexdigest()[:10] if r[3] else 'NA'
    return f'{r[0]}r×{r[1]}c#{h}'
print(f'BMC AF1 {len(B)} 表  |  GE SI {len(G)} 表')
print()
print('  BMC#   GE#   行×列 | 表题（前 78 字）')
print('  ' + '-'*100)
bsig={sig(r):i for i,r in enumerate(B)}; gsig={sig(r):i for i,r in enumerate(G)}
for i,r in enumerate(B):
    j=gsig.get(sig(r))
    t=r[2]
    tn=tabno(t); gn=tabno(G[j][2]) if j is not None else '—'
    flag='' if j is not None else '   ← GE 无对应'
    print(f'  S{tn:<5} S{gn:<5} {r[0]:>4}r×{r[1]:<2}c | {t[:78]}{flag}')
print()
print('=== GE SI 中 BMC 没有的表 ===')
for j,r in enumerate(G):
    if sig(r) not in bsig:
        print(f'  S{tabno(r[2]):<5} {r[0]:>4}r×{r[1]:<2}c | {r[2][:95]}')

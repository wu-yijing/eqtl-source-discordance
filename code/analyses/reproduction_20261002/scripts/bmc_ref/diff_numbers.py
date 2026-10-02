# -*- coding: utf-8 -*-
"""对比 BMC 投稿前定稿 与 GE 投稿稿 的数值token，定位差异。"""
import re, collections, zipfile
from xml.etree import ElementTree as ET
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
def pt(p):
    o=[]
    for n in p.iter():
        if n.tag==W+'t': o.append(n.text or '')
        elif n.tag==W+'tab': o.append(' ')
    return ''.join(o)
def text_of(path):
    z=zipfile.ZipFile(path); root=ET.fromstring(z.read('word/document.xml'))
    paras=[pt(p) for p in root.iter(W+'p')]
    tabs=[]
    for tbl in root.iter(W+'tbl'):
        for tr in tbl.findall(W+'tr'):
            tabs.append(' | '.join(' '.join(pt(p) for p in tc.findall(W+'p')).strip() for tc in tr.findall(W+'tc')))
    return paras, tabs

BMC=r'E:/workbuddy/BMC Genomics投稿资料\投稿前定稿\Manuscript.docx'
GE =r'E:/workbuddy/GE投稿资料/_修订_20260930/Manuscript_GenetEpidemiol_20260930.docx'

TOK=re.compile(r'(?<![\w.])(?:[+\-−]?\d+(?:\.\d+)?)(?:\s?(?:%|percentage points|points))?')
def tokens(lines):
    c=collections.Counter(); loc={}
    for i,l in enumerate(lines):
        for m in TOK.finditer(l):
            s=m.group(0).strip().replace('−','-').replace(' ','')
            c[s]+=1
            loc.setdefault(s,[]).append((i,l[max(0,m.start()-70):m.end()+70]))
    return c,loc

bp,bt=text_of(BMC); gp,gt=text_of(GE)
bc,bloc=tokens(bp+bt); gc,gloc=tokens(gp+gt)
print(f'BMC 段落 {len(bp)} 表格行 {len(bt)}  |  GE 段落 {len(gp)} 表格行 {len(gt)}')
print(f'BMC 数值token种类 {len(bc)}（合计 {sum(bc.values())}）| GE 数值token种类 {len(gc)}（合计 {sum(gc.values())}）')
print()
print('='*104)
print('A. GE 有、BMC 无 的数值 token（<12 字符以内易误配，已过滤纯小数）')
print('='*104)
only_ge=sorted(set(gc)-set(bc))
for s in only_ge:
    if len(s)>26: continue
    print(f'  {s:22s} GE×{gc[s]:<3d}  |  ' + gloc[s][0][1].replace('\n',' ')[:96])
print()
print('='*104)
print('B. BMC 有、GE 无 的数值 token（限定为"suspect"：出现≥2次或带百分号，减少噪声）')
print('='*104)
only_bmc=sorted(set(bc)-set(gc))
shown=0
for s in only_bmc:
    if len(s)>26: continue
    if bc[s]<2 and not s.endswith('%'): continue
    print(f'  {s:22s} BMC×{bc[s]:<3d}  |  ' + bloc[s][0][1].replace('\n',' ')[:96])
    shown+=1
print(f'  （共 {shown} 条满足筛选条件 / {len(only_bmc)} 条仅 BMC 有）')

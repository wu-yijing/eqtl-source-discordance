# -*- coding: utf-8 -*-
"""以「特征值」为锚，比对 BMC 投稿前定稿 与 GE 投稿稿。
只输出「一方缺失或出现次数不同」的锚点，并展开两侧上下文。"""
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
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
import paths as _paths          # noqa: E402  集中路径解析，见 ../paths.py
BMC=full(str(_paths.external('bmc_manuscript_docx')))
GE =full(str(_paths.external('manuscript_docx')))
print(f'BMC 字符 {len(BMC):,}  |  GE 字符 {len(GE):,}')

ANCHORS=[
 ('头条率','68\\.8'),('头条对','66/96'),('头条ρ','0\\.39(?!\\d)'),('ρ三位','0\\.390'),
 ('DR','23/32'),('DN','21/32'),('DPN','22/32'),('DR%','71\\.9'),('DN%','65\\.6'),
 ('夹层SE','0\\.125'),('刀切SE','0\\.137'),('自助下','58\\.3'),('自助上','79\\.2'),
 ('反转二项P','0\\.362'),('全集零分布','54\\.9'),('臂内零分布','63\\.6'),('源内参照','96\\.7'),
 ('缺口','27\\.9'),('缺口区间','17\\.5.{0,3}38\\.4'),('≥0.5','75\\.6'),('≥1.0','88\\.2'),
 ('top10','0\\.053'),('top20','0\\.176'),('top30','0\\.304'),('单源9对','4\\.5%'),
 ('共同宙panel','0\\.463'),('共同宙tissue','0\\.410'),('共同宙dual','0\\.443'),
 ('共同宙%panel','70\\.4'),('共同宙%tissue','65\\.2'),('共同宙%dual','67\\.4'),
 ('Δρ双-组','-0\\.020'),('Δρ双-组CI','0\\.089'),('Δρ双-织','\\+0\\.033'),('Δρ双-织CI','0\\.274'),
 ('SCZΔρ织','0\\.0265'),('SCZΔρ织CI上','0\\.0524'),('SCZΔρ组','-0\\.0226'),('SCZΔρ组CI','0\\.0094'),
 ('框架ρ','0\\.797'),('框架CI下','0\\.781'),('框架CI上','0\\.812'),('框架%','82\\.4'),
 ('织轴框架','0\\.499'),('资源轴','0\\.582'),('弹性网','0\\.647'),('WB全集','0\\.784'),
 ('定向校验','0\\.638'),('织轴EN','0\\.525'),
 ('合并差','2\\.66'),('合并CI上','5\\.55'),('合并Q','0\\.14'),('GTEx臂差','2\\.38'),('eQTLGen臂差','3\\.70'),
 ('90%上界','6\\.4'),('90%下界','0\\.7'),
 ('FinnGen Z','2\\.31'),('UKB Z','0\\.72'),('合并Z','1\\.51'),('合并P','0\\.056'),
 ('I2','20\\.6'),('PI上','3\\.36'),
 ('BH功效GTEx','8\\.0'),('BH功效eQ','13\\.0'),('名义功效GTEx','14\\.5'),('名义功效eQ','17\\.5'),
 ('TUBB剔除','2\\.6%'),('配对P','1\\.00'),('匹配P','0\\.077'),('匹配名义','9\\.9'),
 ('SCZ panel k','5,584'),('SCZ tissue k','5,551'),('SCZ dual k','5,506'),
 ('SCZ CC','8,315'),('SCZ 双组织','8,890'),('SCZ eqZ&wbZ','9,048'),('零分布对','3,617'),('零分布k','1,987'),
 ('可用例ρ','0\\.4665'),('完例ρ','0\\.4690'),('管家织轴','0\\.64'),('管家CI上','0\\.76'),
 ('分半DR','93\\.8'),('分半DPN','97\\.2'),('分半DN','99\\.1'),
 ('TUBB SNP','1,848'),('TUBB保留','359'),('RNH1 NT Z','2\\.67'),('RNH1 q DR','0\\.28'),
 ('19对排除ρ','0\\.336'),('主臂Fisher下','0\\.21'),('主臂Fisher上','0\\.55'),
 ('反转率主臂','31\\.2'),('反转率dual','32\\.8'),('反转率SCZ','33\\.8'),
 ('三分位低','27\\.3'),('三分位中','39\\.4'),('三分位高','31\\.8'),
 ('TUBB |Z|','11\\.89'),('模拟覆盖下','94\\.0'),('模拟覆盖上','96\\.2'),
 ('模拟192对','7\\.2'),('模拟t3','5\\.46'),('恒等式超额','6\\.05'),
]
def ctx(t,pat,w=78):
    m=re.search(pat,t);  return None if not m else t[max(0,m.start()-w):m.end()+w].replace('\u241F',' | ')
miss=[]; diff=[]
for lab,pat in ANCHORS:
    nb=len(re.findall(pat,BMC)); ng=len(re.findall(pat,GE))
    if nb and ng:
        if nb!=ng: diff.append((lab,pat,nb,ng))
    else:
        miss.append((lab,pat,nb,ng))
print()
print('='*104); print(f'A. 一方完全缺失的锚点（{len(miss)} 项）'); print('='*104)
for lab,pat,nb,ng in miss:
    print(f'  ▸ {lab:16s} BMC×{nb}  GE×{ng}')
    print(f'      BMC: {ctx(BMC,pat) if nb else "—"}')
    print(f'      GE : {ctx(GE ,pat) if ng else "—"}')
print()
print('='*104); print(f'B. 两侧都有但出现次数不同（{len(diff)} 项）'); print('='*104)
for lab,pat,nb,ng in diff:
    print(f'  ▸ {lab:16s} BMC×{nb}  GE×{ng}')

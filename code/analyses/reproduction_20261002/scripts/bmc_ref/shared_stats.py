# -*- coding: utf-8 -*-
"""逐项核对 BMC 定稿 与 GE 投稿稿 的共享统计量（容错模式，容忍排版差异）。"""
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
BMC=full(str(_paths.external('bmc_manuscript_docx')))
GE =full(str(_paths.external('manuscript_docx')))
def has(t,*pats): return any(re.search(p,t) for p in pats)

ITEMS=[
 ('头条方向一致率 68.8%',       r'68\.8\s*%', r'66\s*\(68\.8\)'),
 ('主臂 96 对',                 r'\b96\b'),
 ('头条 ρ = 0.39',              r'0\.39\b', r'0\.390'),
 ('per-phenotype 23/21/22',     r'23\s*\(71\.9', r'71\.9'),
 ('DN 21 (65.6%)',              r'21\s*\(65\.6', r'65\.6'),
 ('DPN 22 (68.8%)',             r'22\s*\(68\.8', r'68\.8'),
 ('naive P 8.7×10⁻⁵',           r'8\.7\s*×\s*10', r'8\.7e-?0?5', r'8\.7\s*×'),
 ('sandwich SE 0.125',          r'0\.125'),
 ('jackknife SE 0.137',         r'0\.137'),
 ('df 31',                      r'df\s*=?\s*31'),
 ('permutation P<0.001',        r'P\s*<\s*0\.001'),
 ('自助法 ρ 区间 0.12–0.62',      r'0\.12\s*[–\-]\s*0\.62'),
 ('自助法率区间 58.3–79.2',       r'58\.3\s*[–\-]\s*79\.2'),
 ('经验零分布 54.9% (1,987/3,617)',r'54\.9', r'1,?987\s*/\s*3,?617'),
 ('臂内零分布 63.6% (35/55)',     r'63\.6', r'35\s*/\s*55'),
 ('源内参照 96.7% (93.8–99.0)',   r'96\.7', r'93\.8\s*[–\-]\s*99\.0'),
 ('缺口 27.9 pp (17.5–38.4)',     r'27\.9', r'17\.5\s*[–\-]\s*38\.4'),
 ('≥0.5 层 75.6%',              r'75\.6'),
 ('≥1.0 层 88.2%',              r'88\.2'),
 ('反转 12 / 18',                r'\b12\b[^.]{0,40}\b18\b'),
 ('反转二项 P = 0.362',           r'0\.362'),
 ('三臂 n 96/159/138/198',      r'\b159\b', r'\b138\b', r'\b198\b'),
 ('三臂 ρ 0.390/0.490/0.414/0.442', r'0\.490', r'0\.414', r'0\.442'),
 ('三臂率 71.1/65.9/67.2',       r'71\.1', r'65\.9', r'67\.2'),
 ('锚集 34/102, 69 (67.6%)',     r'67\.6'),
 ('锚集 ρ 0.373',               r'0\.373'),
 ('候选 panel 47/63 (74.6%) ρ 0.583', r'74\.6', r'0\.583'),
 ('候选 dual 58/78 (74.4%) ρ 0.561',  r'74\.4', r'0\.561'),
 ('top10 交集 1/10 (Jaccard 0.053)', r'0\.053'),
 ('198 对中 9 对单源显著',          r'9\s*(pairs|对)', r'4\.5'),
 ('198 对中 0 对双源显著',          r'none of\s*(the\s*)?nine', r'9\b[^.]{0,60}both'),
 ('共同宇宙 135 对',               r'\b135\b'),
 ('共同宇宙 ρ 0.463/0.410/0.443',  r'0\.463', r'0\.410', r'0\.443'),
 ('共同宇宙率 70.4/65.2/67.4',      r'70\.4', r'65\.2', r'67\.4'),
 ('Δρ −0.020 (−0.125,+0.089)',    r'0\.125 to \+0\.089', r'0\.125\s*[–\-]\s*\+?0\.089'),
 ('Δρ +0.033 (−0.217,+0.274)',    r'0\.217', r'0\.274'),
 ('Fisher-z 主臂 0.21–0.55',       r'0\.21', r'0\.55'),
 ('Fisher-z panel 0.36–0.60',     r'0\.36', r'0\.60'),
 ('Fisher-z tissue 0.27–0.54',    r'0\.27', r'0\.54'),
 ('Fisher-z dual 0.32–0.55',      r'0\.32'),
 ('SCZ 完例 8,315',               r'8,?315'),
 ('SCZ panel k 5,584',            r'5,?584'),
 ('SCZ tissue k 5,551',           r'5,?551'),
 ('SCZ dual k 5,506',             r'5,?506'),
 ('SCZ ρ +0.469/+0.420/+0.447',   r'0\.469', r'0\.420', r'0\.447'),
 ('SCZ Δρ +0.0265 (+0.0002,+0.0524)', r'0\.0265', r'0\.0524'),
 ('SCZ Δρ −0.0226 (−0.0355,−0.0094)', r'0\.0226', r'0\.0355', r'0\.0094'),
 ('SCZ 双组织 8,890',             r'8,?890'),
 ('SCZ eqZ&WB 9,048',             r'9,?048'),
 ('框架 ρ 0.797 (0.781–0.812; 82.4%)', r'0\.797', r'0\.781', r'0\.812', r'82\.4'),
 ('框架宇宙 4,098',               r'4,?098'),
 ('织轴 0.499 (0.469–0.528; 69.8%)', r'0\.499', r'0\.528', r'69\.8'),
 ('资源轴 0.582 (n=3,910)',        r'0\.582', r'3,?910'),
 ('WB 全集 0.784 (6,310)',         r'0\.784', r'6,?310'),
 ('定向校验 0.638 (6,014)',        r'0\.638', r'6,?014'),
 ('未定向 0.001',                  r'0\.001'),
 ('织轴弹性网 0.525',              r'0\.525'),
 ('弹性网资源轴 0.647',            r'0\.647'),
 ('合并差 +2.66 (−0.22,+5.55)',    r'2\.66', r'5\.55'),
 ('合并 Q = 0.14',                r'Q\s*=\s*0\.14'),
 ('臂差 +2.38 / +3.70',            r'2\.38', r'3\.70'),
 ('90% 区间 (−0.7,+6.4)',          r'6\.4', r'−0\.7', r'-0\.7'),
 ('臂间 r = −0.05',                r'−0\.05', r'-0\.05'),
 ('SE 1.5 → 2.2',                 r'1\.5', r'2\.2'),
 ('RNH1 FinnGen +2.31 / UKB +0.72', r'2\.31', r'0\.72'),
 ('RNH1 合并 +1.51 (SE 0.79; P=0.056)', r'1\.51', r'0\.79', r'0\.056'),
 ('RNH1 Q 1.26; I² 20.6%; PI −0.33~+3.36', r'1\.26', r'20\.6', r'3\.36', r'0\.33'),
 ('RNH1 GTEx NT +2.67',            r'2\.67'),
 ('端点 11 个 FDR 显著对',           r'\b11\b'),
 ('检出边界 2.97–3.69',             r'2\.97', r'3\.69'),
 ('零标定 4.9–5.3%',               r'4\.9', r'5\.3'),
 ('功效 8.0 / 13.0 pp',             r'8\.0', r'13\.0'),
 ('名义功效 14.5 / 17.5 pp',         r'14\.5', r'17\.5'),
 ('剔 TUBB 后 2/78 (2.6%)',          r'2\.6', r'78'),
 ('Fisher P = 1.00',               r'1\.00'),
 ('匹配 eQTLGen 6.2% vs 0.0% P=0.077', r'0\.077'),
 ('匹配名义 9.9% vs 7.0% P=0.76',    r'9\.9', r'0\.76'),
 ('匹配 GTEx 2.4% vs 1.7%',          r'1\.7'),
 ('19 对排除后 ρ 0.336 (0.17–0.49)',  r'0\.336', r'0\.17', r'0\.49'),
 ('反转率 31.2 / 32.8 / 33.8',       r'31\.2', r'32\.8', r'33\.8'),
 ('TUBB 1,848 模型 SNP',            r'1,?848'),
 ('TUBB 保留 359 SNP',              r'\b359\b'),
 ('45 基因共同宇宙',                 r'\b45\b'),
]
both=[]; only_b=[]; only_g=[]
for lab,*pats in ITEMS:
    hb=has(BMC,*pats); hg=has(GE,*pats)
    (both if hb and hg else (only_b if hb else (only_g if hg else []))).append(lab)
    if not hb and not hg: both.append(lab+' [两侧均未检出!]')
print(f'共核对 {len(ITEMS)} 项')
print(f'  ✓ 两稿均有 : {len(both)}')
print(f'  ○ 仅 BMC  : {len(only_b)}')
print(f'  ● 仅 GE   : {len(only_g)}')
print()
if only_b:
    print('仅 BMC 有（GE 压缩时略去，非分歧）：');  [print('   ○',x) for x in only_b]
if only_g:
    print('仅 GE 有（BMC 无对应值 —— 需注意）：');  [print('   ●',x) for x in only_g]
print()
print('两稿均有：');  [print('   ✓',x) for x in both]

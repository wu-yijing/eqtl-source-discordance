import os, re, zipfile, hashlib
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
D = r'E:\workbuddy\BMC Genomics投稿资料\定稿资料'
ROOT = r'E:\workbuddy\BMC Genomics投稿资料'
MS = os.path.join(D, 'manuscript修订版_审稿意见修订_20260917.docx')
SI = os.path.join(D, 'Additional file 1_审稿意见修订_20260917.docx')
CL = os.path.join(D, 'CoverLetter_20260914.docx')


def blocks(p):
    r = ET.fromstring(zipfile.ZipFile(p).read('word/document.xml'))
    out = []
    for c in r.find(W + 'body'):
        if c.tag == W + 'p':
            pr = c.find(W + 'pPr')
            st = None
            if pr is not None:
                s = pr.find(W + 'pStyle')
                st = s.get(W + 'val') if s is not None else None
            ln = pr is not None and pr.find(W + 'lnNumType') is not None
            out.append(('p', ''.join(t.text or '' for t in c.iter(W + 't')), st))
        elif c.tag == W + 'tbl':
            rows = [[' '.join(''.join(t.text or '' for t in pp.iter(W + 't')) for pp in tc.findall(W + 'p'))
                     for tc in tr.findall(W + 'tc')] for tr in c.findall(W + 'tr')]
            out.append(('tbl', rows, None))
    return out


R = []
P = R.append

# ============ A. 独立复核：Fig S2 的 pull-down / literature 拆分 ============
sb = blocks(SI)
s1 = next(b[1] for b in sb if b[0] == 'tbl' and b[1] and b[1][0][:2] == ['Gene', 'Group'])
s17 = next(b[1] for b in sb if b[0] == 'tbl' and b[1] and b[1][0][:3] == ['Gene', 'Phenotype', 'Gene group'])
s7 = next(b[1] for b in sb if b[0] == 'tbl' and b[1] and 'Equivalent |Z|' in ' '.join(b[1][0]))
s10 = next(b[1] for b in sb if b[0] == 'tbl' and b[1] and 'Gene-set composition' in ' '.join(b[1][0]))
P('== A. Fig. S2 candidate denominator: pull-down vs literature ==')
P('Table S1 header: %s' % s1[0])
gi, grp, src = s1[0].index('Gene'), s1[0].index('Group'), s1[0].index('Source')
cand = [(r[gi].strip(), r[src].strip()) for r in s1[1:] if len(r) > src and r[grp].strip() == 'Candidate']
P('  candidates in Table S1 = %d' % len(cand))
from collections import Counter
P('  by Source (all candidates): %s' % dict(Counter(s for _, s in cand)))
eq_genes = {r[0].strip() for r in s17[1:] if len(r) > 3 and r[0].strip()}
P('  genes with eQTLGen per-gene rows (Table S17) = %d' % len(eq_genes))
withmod = [(g, s) for g, s in cand if g in eq_genes]
P('  candidates WITH an eQTLGen model = %d' % len(withmod))
P('  their Source split = %s' % dict(Counter(s for _, s in withmod)))
P('  caption claims: 27 candidates with an eQTLGen model (13 pull-down, 14 literature)')

# ============ B. Fig S3 分母 81 / 75 / 51 ============
P('\n== B. Fig. S3 denominators 81/75/51 ==')
for row in s7:
    if row and row[0].strip().startswith('eQTLGen'):
        P('  Table S7 (eQTLGen): %s' % ' | '.join(x[:22] for x in row))
P('  Table S10 eQTLGen row: %s' % ' | '.join(x[:40] for x in
                                              next(r for r in s10 if r and 'eQTLGen whole-blood (harmonized' in r[0])))
P('  caption claims: three groups contribute 81, 75 and 51 gene-phenotype pairs')

# ============ C. SI 结构（修复回归检查） ============
P('\n== C. SI regression check after the Fig S1 image fix ==')
z = zipfile.ZipFile(SI)
xml = z.read('word/document.xml').decode('utf-8')
media = [n for n in z.namelist() if n.startswith('word/media/') and not n.endswith('/')]
rels = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', z.read('word/_rels/document.xml.rels').decode('utf-8')))
emb = set(re.findall(r'embed="(rId\d+)"', xml))
P('  media=%d  blip=%d  orphan=%s' % (len(media), xml.count('<a:blip'),
                                      [r for r, t in rels.items() if 'media/' in t and r not in emb]))
P('  lnNumType in styles? sections: %s' % ('yes' if '<w:lnNumType' in xml else 'no'))
i = 0
for kind, val, st in sb:
    if kind == 'p':
        if 'blip' in ET.tostring(list(ET.fromstring(zipfile.ZipFile(SI).read('word/document.xml')).find(W + 'body'))[i],
                                 encoding='unicode') or val.startswith(('Figure S', 'Supporting')):
            P('  block%03d style=%-14s | %s' % (i, st, (val[:70] if val.strip() else '[IMAGE/EMPTY]')))
        i += 1
P('  (order check) figure/paragraph sequence above: S1 image must precede the "Figure S1." caption')

# ============ D. 投稿信：S11 提及次数 + 数值 ============
P('\n== D. Cover letter ==')
cl = blocks(CL)
ct = '\n'.join(v for k, v, s in cl if k == 'p')
P('  "Table S11" mentions = %d ; "Table S13" mentions = %d ; "STREGA" mentions = %d'
  % (ct.count('Table S11'), ct.count('Table S13'), ct.count('STREGA')))
for v in ['68.8%', '0.39', '31.2%', '32.8%', '63.6%', '96.7%', '27.9', '33.3%', '33.8%',
          '8,315', '2.7 percentage', '0.077', '1.00', '+2.7', '0.463']:
    P('  %-16s %d' % (v, ct.count(v)))
P('  placeholders: %s' % {k: ct.count(k) for k in ('[[', 'TODO', 'TBD', 'TO BE COMPLETED')})

open(r'E:\workbuddy\2026-09-18-07-04-15\.tmp\round4_checks.txt', 'w', encoding='utf-8').write('\n'.join(R))
print('\n'.join(R))

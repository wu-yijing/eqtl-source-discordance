# -*- coding: utf-8 -*-
"""Apply the M1 (resource-axis confound: alternative tests) and M2 (SESOI for the
0.10 equivalence margin) additions to the EN and CN manuscripts.

Lossless: every part of the .docx other than word/document.xml is copied VERBATIM
(so word/footer1.xml, rels, content-types, styles are untouched byte-for-byte).
"""
import os, re, shutil, time, zipfile, hashlib
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WQ = '{%s}' % W
S = r'E:\workbuddy\BMC Genomics投稿资料'
DST = os.path.join(S, '定稿资料')
BKROOT = os.path.join(S, '定稿备份')
TS = time.strftime('%Y%m%d_%H%M%S')

EN = os.path.join(DST, 'manuscript修订版_题目摘要术语修订_20260913.docx')
CN = os.path.join(DST, 'manuscript修订版_中文_题目摘要术语修订_20260913.docx')

# --------------------------------------------------------------------------- EN
EN_47 = (u" Two consequences are recorded here. First, the margin is anchored on the "
         u"smallest difference this metric can express at a decision-relevant scale: by the "
         u"sign-agreement identity of Methods 2.5, a difference of 0.10 in \u03c1 corresponds to "
         u"\u22483.3\u20133.9 percentage points of direction consistency across the correlations observed "
         u"here, which is smaller than every difference that separates the graded conclusions of "
         u"this study (the \u00b115-percentage-point confirmatory margin; the 7.2-percentage-point "
         u"spread across predefined gene-subset definitions; and the up to \u224822-percentage-point "
         u"shifts that source change induces in group-stratified enrichment). Second, because the "
         u"panel axis is a compound of reference panel, training-sample size and statistical "
         u"framework, its components were interrogated separately wherever the data allow, and the "
         u"one that cannot be isolated is named in Results 3.3 rather than left implicit.")

EN_84 = (u" The components of the panel axis were interrogated separately wherever the data "
         u"permit. Holding the reference panel and its training samples fixed and varying only the "
         u"statistical framework \u2014 recomputing every group-stratified FDR decision under "
         u"Stouffer-weighted Z rather than ACAT-O \u2014 left the enrichment conclusions unchanged "
         u"(Section 3.4; Additional file 1: Table S2), so the between-source contrast is not an "
         u"artefact of the integration framework. The training-sample-size component cannot be "
         u"isolated with currently public resources: no two eQTL reference panels differ in sample "
         u"size while sharing panel construction, modelling framework and tissue, and the "
         u"within-GTEx tissue contrast (Whole_Blood N = 670 versus Nerve_Tibial N = 532) varies "
         u"tissue and sample size together. Because the denser and larger resource also yields the "
         u"more precise estimates, the panel axis is reported as a joint contrast whose attribution "
         u"among the three components is bounded rather than resolved.")

EN_112 = (u" Equivalently, on the scale of the metric the margin of 0.10 in \u03c1 corresponds to "
          u"\u22483.3\u20133.9 percentage points of direction consistency (Methods 2.6), smaller than every "
          u"difference that separates the graded conclusions of this study; a difference within the "
          u"margin therefore cannot change any of them.")

EN_129 = (u" Two of the three confounded components are, however, already bounded by the present "
          u"data: fixing the reference panel and its training samples and varying only the "
          u"integration framework left the group-stratified enrichment conclusions unchanged "
          u"(Results 3.4; Additional file 1: Table S2), and the tissue contrast likewise holds panel "
          u"and framework fixed while varying tissue alone. Only the training-sample-size component "
          u"remains untestable, because no public resource pair differs in sample size alone. The "
          u"decisive test is a within-panel sample-size ladder \u2014 subsampling or accumulating "
          u"samples inside one reference panel while holding tissue and modelling framework fixed "
          u"\u2014 which would convert the present joint contrast into an attributable one; we therefore "
          u"report the panel axis as a bounded joint contrast and identify that ladder as the "
          u"required next step.")

EN_134 = (u" Two standards for such a margin are available and both are reported here. An "
          u"external standard would require an independent, decision-relevant scale for \u03c1 in this "
          u"setting, which does not exist; we therefore use an internal but explicit one. Through "
          u"the sign-agreement identity \u00bd + arcsin(\u03c1)/\u03c0 (Methods 2.5), a difference of 0.10 in \u03c1 "
          u"corresponds to \u22483.3\u20133.9 percentage points of direction consistency. That is smaller "
          u"than each difference that separates the graded conclusions of this study \u2014 the "
          u"\u00b115-percentage-point confirmatory equivalence margin, the 7.2-percentage-point spread "
          u"across predefined gene-subset definitions, and the up to \u224822-percentage-point shifts "
          u"that source change induces in group-stratified enrichment \u2014 so the margin is a smallest "
          u"effect size of interest at the resolution of the endpoints actually used here, rather "
          u"than a round number chosen for convenience. Its limits are stated: at 0.05 the result is "
          u"marginal and at 0.02 equivalence is not established, so differences below \u22480.05 in \u03c1 "
          u"remain compatible with the data.")

EN_155_MARK = u"so the partition should be read as a diagnostic heuristic rather than a causal decomposition."
EN_155_INS = (u" The framework component of that confound is excluded as the driver by an "
              u"alternative test that holds the reference panel and its training samples fixed "
              u"(Results 3.3), but the sample-size component cannot be isolated with currently "
              u"public resources, so the attribution is bounded rather than resolved.")

# --------------------------------------------------------------------------- CN
CN_47 = (u"\u6b64\u5904\u8bb0\u5f55\u4e24\u70b9\u540e\u679c\u3002\u7b2c\u4e00\uff0c"
         u"\u8be5\u8fb9\u754c\u951a\u5b9a\u4e8e\u672c\u6307\u6807\u5728\u51b3\u7b56\u76f8\u5173\u5c3a\u5ea6\u4e0a"
         u"\u6240\u80fd\u8868\u8fbe\u7684\u6700\u5c0f\u5dee\u5f02\uff1a\u4f9d\u65b9\u6cd5 2.5 \u7684\u7b26\u53f7"
         u"\u4e00\u81f4\u7387\u6052\u7b49\u5f0f\uff0c\u03c1 \u4e0a\u7684 0.10 \u76f8\u5f53\u4e8e\u7ea6 "
         u"3.3\u20133.9 \u4e2a\u767e\u5206\u70b9\u7684\u65b9\u5411\u4e00\u81f4\u7387\uff08\u53d6\u672c\u6587"
         u"\u6240\u89c2\u6d4b\u5230\u7684\u76f8\u5173\u503c\u8303\u56f4\uff09\uff0c\u4f4e\u4e8e\u672c\u7814\u7a76"
         u"\u4efb\u4e00\u5206\u7ea7\u7ed3\u8bba\u6240\u4f9d\u8d56\u7684\u6700\u5c0f\u95f4\u9694\uff08\u00b115 "
         u"\u4e2a\u767e\u5206\u70b9\u7684\u9a8c\u8bc1\u6027\u8fb9\u9645\uff1b\u9884\u8bbe\u57fa\u56e0\u5b50\u96c6"
         u"\u5b9a\u4e49\u95f4 7.2 \u4e2a\u767e\u5206\u70b9\u7684\u8de8\u5ea6\uff1b\u4ee5\u53ca\u6765\u6e90\u66f4"
         u"\u6362\u5728\u7ec4\u5206\u5c42\u5bcc\u96c6\u4e2d\u5f15\u8d77\u7684\u6700\u9ad8\u7ea6 22 \u4e2a"
         u"\u767e\u5206\u70b9\u7684\u4f4d\u79fb\uff09\u3002\u7b2c\u4e8c\uff0c\u7531\u4e8e\u9762\u677f\u8f74\u662f"
         u"\u53c2\u8003\u9762\u677f\u3001\u8bad\u7ec3\u6837\u672c\u91cf\u4e0e\u7edf\u8ba1\u6846\u67b6\u4e09\u8005"
         u"\u7684\u590d\u5408\uff0c\u51e1\u6570\u636e\u5141\u8bb8\u5904\u6211\u4eec\u5df2\u5bf9\u5176\u7ec4\u5206"
         u"\u5206\u522b\u68c0\u9a8c\uff0c\u800c\u65e0\u6cd5\u5206\u79bb\u7684\u90a3\u4e00\u4e2a\u5728\u7ed3\u679c "
         u"3.3 \u4e2d\u660e\u786e\u70b9\u540d\uff0c\u800c\u975e\u7559\u4f5c\u9ed8\u793a\u3002")

CN_84 = (u"\u51e1\u6570\u636e\u5141\u8bb8\u5904\uff0c\u6211\u4eec\u5bf9\u9762\u677f\u8f74\u7684\u4e09\u4e2a"
         u"\u7ec4\u5206\u5206\u522b\u4f5c\u4e86\u68c0\u9a8c\u3002\u56fa\u5b9a\u53c2\u8003\u9762\u677f\u53ca"
         u"\u5176\u8bad\u7ec3\u6837\u672c\u3001\u4ec5\u53d8\u52a8\u7edf\u8ba1\u6846\u67b6\u2014\u2014"
         u"\u5373\u6539\u7528 Stouffer \u52a0\u6743 Z \u800c\u975e ACAT-O \u91cd\u7b97\u6bcf\u4e00\u4e2a"
         u"\u7ec4\u5206\u5c42 FDR \u5224\u5b9a\u2014\u2014\u672a\u6539\u53d8\u5bcc\u96c6\u7ed3\u8bba"
         u"\uff083.4 \u8282\uff1b\u9644\u52a0\u6587\u4ef6 1\uff1a\u8868 S2\uff09\uff0c\u6545\u8be5\u8de8"
         u"\u6765\u6e90\u5bf9\u6bd4\u5e76\u975e\u6574\u5408\u6846\u67b6\u6240\u81f4\u7684\u5047\u8c61\u3002"
         u"\u8bad\u7ec3\u6837\u672c\u91cf\u8fd9\u4e00\u7ec4\u5206\u5728\u5f53\u524d\u516c\u5f00\u8d44\u6e90\u4e0b"
         u"\u65e0\u6cd5\u88ab\u5206\u79bb\uff1a\u6ca1\u6709\u4efb\u4f55\u4e24\u5957 eQTL \u53c2\u8003\u9762\u677f"
         u"\u5728\u4fdd\u6301\u9762\u677f\u6784\u5efa\u3001\u5efa\u6a21\u6846\u67b6\u4e0e\u7ec4\u7ec7\u4e00\u81f4"
         u"\u7684\u524d\u63d0\u4e0b\u4ec5\u6837\u672c\u91cf\u4e0d\u540c\uff1b\u800c GTEx \u5185\u90e8\u7684"
         u"\u7ec4\u7ec7\u5bf9\u6bd4\uff08Whole_Blood N = 670 \u5bf9 Nerve_Tibial N = 532\uff09"
         u"\u540c\u65f6\u53d8\u52a8\u4e86\u7ec4\u7ec7\u4e0e\u6837\u672c\u91cf\u3002\u7531\u4e8e\u66f4\u81f4"
         u"\u5bc6\u3001\u6837\u672c\u91cf\u66f4\u5927\u7684\u8d44\u6e90\u540c\u65f6\u7ed9\u51fa\u66f4"
         u"\u7cbe\u786e\u7684\u4f30\u8ba1\uff0c\u9762\u677f\u8f74\u4f5c\u4e3a\u8054\u5408\u5bf9\u6bd4\u62a5"
         u"\u544a\uff0c\u5176\u4e09\u4e2a\u7ec4\u5206\u95f4\u7684\u5f52\u56e0\u662f\u6709\u754c\u7684\uff0c"
         u"\u800c\u975e\u5df2\u88ab\u89e3\u6790\u3002")

CN_112 = (u"\u7b49\u4ef7\u5730\uff0c\u5c31\u672c\u6307\u6807\u7684\u5c3a\u5ea6\u800c\u8a00\uff0c\u03c1 "
          u"\u4e0a\u7684 0.10 \u8fb9\u9645\u76f8\u5f53\u4e8e\u7ea6 3.3\u20133.9 \u4e2a\u767e\u5206\u70b9"
          u"\u7684\u65b9\u5411\u4e00\u81f4\u7387\uff08\u65b9\u6cd5 2.6\uff09\uff0c\u5c0f\u4e8e\u672c\u7814"
          u"\u7a76\u4efb\u4e00\u5206\u7ea7\u7ed3\u8bba\u4e4b\u95f4\u7684\u95f4\u9694\u3002")

CN_129 = (u"\u4e0d\u8fc7\uff0c\u4e09\u4e2a\u6df7\u6742\u7ec4\u5206\u4e2d\u6709\u4e24\u4e2a\u5df2\u88ab"
          u"\u73b0\u6709\u6570\u636e\u754c\u5b9a\uff1a\u56fa\u5b9a\u53c2\u8003\u9762\u677f\u53ca\u5176\u8bad"
          u"\u7ec3\u6837\u672c\u3001\u4ec5\u53d8\u52a8\u6574\u5408\u6846\u67b6\uff0c\u672a\u6539\u53d8\u7ec4"
          u"\u5206\u5c42\u5bcc\u96c6\u7ed3\u8bba\uff08\u7ed3\u679c 3.4\uff1b\u9644\u52a0\u6587\u4ef6 1\uff1a"
          u"\u8868 S2\uff09\uff1b\u7ec4\u7ec7\u5bf9\u6bd4\u5219\u5728\u56fa\u5b9a\u9762\u677f\u4e0e"
          u"\u6846\u67b6\u7684\u524d\u63d0\u4e0b\u4ec5\u53d8\u52a8\u7ec4\u7ec7\u3002\u53ea\u6709\u8bad\u7ec3"
          u"\u6837\u672c\u91cf\u8fd9\u4e00\u7ec4\u5206\u4ecd\u4e0d\u53ef\u68c0\u9a8c\uff0c\u56e0\u4e3a"
          u"\u6ca1\u6709\u4efb\u4f55\u516c\u5f00\u8d44\u6e90\u5bf9\u4ec5\u5728\u6837\u672c\u91cf\u4e0a"
          u"\u5b58\u5728\u5dee\u5f02\u3002\u51b3\u5b9a\u6027\u7684\u68c0\u9a8c\u662f\u9762\u677f\u5185"
          u"\u6837\u672c\u91cf\u9636\u68af\u2014\u2014\u5728\u540c\u4e00\u53c2\u8003\u9762\u677f\u5185"
          u"\u90e8\u901a\u8fc7\u5b50\u91c7\u6837\u6216\u6837\u672c\u7d2f\u79ef\u6539\u53d8\u6837\u672c"
          u"\u91cf\uff0c\u540c\u65f6\u56fa\u5b9a\u7ec4\u7ec7\u4e0e\u5efa\u6a21\u6846\u67b6\u2014\u2014"
          u"\u5b83\u80fd\u5c06\u5f53\u524d\u7684\u8054\u5408\u5bf9\u6bd4\u8f6c\u5316\u4e3a\u53ef\u5f52"
          u"\u56e0\u7684\u5bf9\u6bd4\uff1b\u56e0\u6b64\u6211\u4eec\u6309\u6709\u754c\u7684\u8054\u5408"
          u"\u5bf9\u6bd4\u62a5\u544a\u9762\u677f\u8f74\uff0c\u5e76\u628a\u8be5\u9636\u68af\u5217\u4e3a"
          u"\u5fc5\u9700\u7684\u4e0b\u4e00\u6b65\u3002")

CN_134 = (u"\u6b64\u7c7b\u8fb9\u9645\u6709\u4e24\u5957\u6807\u51c6\uff0c\u6b64\u5904\u4e00\u5e76"
          u"\u62a5\u544a\u3002\u5916\u90e8\u6807\u51c6\u8981\u6c42\u8be5\u60c5\u5883\u4e0b \u03c1 \u6709"
          u"\u4e00\u4e2a\u72ec\u7acb\u4e14\u4e0e\u51b3\u7b56\u76f8\u5173\u7684\u5c3a\u5ea6\uff0c\u800c\u8fd9"
          u"\u5e76\u4e0d\u5b58\u5728\uff1b\u56e0\u6b64\u6211\u4eec\u91c7\u7528\u5185\u751f\u7684\u3001\u4f46"
          u"\u88ab\u660e\u786e\u5199\u51fa\u7684\u6807\u51c6\u3002\u4f9d\u7b26\u53f7\u4e00\u81f4\u7387"
          u"\u6052\u7b49\u5f0f \u00bd + arcsin(\u03c1)/\u03c0\uff08\u65b9\u6cd5 2.5\uff09\uff0c\u03c1 \u4e0a "
          u"0.10 \u7684\u5dee\u5f02\u76f8\u5f53\u4e8e\u7ea6 3.3\u20133.9 \u4e2a\u767e\u5206\u70b9\u7684"
          u"\u65b9\u5411\u4e00\u81f4\u7387\u3002\u8be5\u91cf\u5c0f\u4e8e\u672c\u7814\u7a76\u5404\u5206"
          u"\u7ea7\u7ed3\u8bba\u4e4b\u95f4\u7684\u6bcf\u4e00\u5904\u95f4\u9694\u2014\u2014\u00b115 \u4e2a"
          u"\u767e\u5206\u70b9\u7684\u9a8c\u8bc1\u6027\u7b49\u4ef7\u8fb9\u9645\u3001\u9884\u8bbe\u57fa"
          u"\u56e0\u5b50\u96c6\u5b9a\u4e49\u95f4 7.2 \u4e2a\u767e\u5206\u70b9\u7684\u8de8\u5ea6\uff0c"
          u"\u4ee5\u53ca\u6765\u6e90\u66f4\u6362\u5728\u7ec4\u5206\u5c42\u5bcc\u96c6\u4e2d\u5f15\u8d77"
          u"\u7684\u6700\u9ad8\u7ea6 22 \u4e2a\u767e\u5206\u70b9\u7684\u4f4d\u79fb\u2014\u2014\u6545"
          u"\u8be5\u8fb9\u9645\u662f\u5728\u6b64\u5904\u5b9e\u9645\u4f7f\u7528\u7684\u7aef\u70b9\u5206"
          u"\u8fa8\u7387\u4e0a\u7684\u6700\u5c0f\u611f\u5174\u8da3\u6548\u5e94\u91cf\uff0c\u800c\u975e"
          u"\u51fa\u4e8e\u4fbf\u5229\u9009\u53d6\u7684\u6574\u6570\u3002\u5176\u9650\u5ea6\u4ea6\u5df2"
          u"\u58f0\u660e\uff1a\u5728 0.05 \u4e0b\u7ed3\u679c\u4e3a\u8fb9\u7f18\uff0c\u5728 0.02 \u4e0b"
          u"\u7b49\u4ef7\u6027\u4e0d\u6210\u7acb\uff0c\u6545 \u03c1 \u4e0a\u5c0f\u4e8e\u7ea6 0.05 \u7684"
          u"\u5dee\u5f02\u4ecd\u4e0e\u6570\u636e\u76f8\u5bb9\u3002")

CN_155_MARK = u"\u6545\u8be5\u5212\u5206\u5e94\u8bfb\u4f5c\u8bca\u65ad\u6027\u542f\u53d1\u800c\u975e\u56e0\u679c\u5206\u89e3\u3002"
CN_155_INS = (u"\u8be5\u6df7\u6742\u4e2d\u7684\u6846\u67b6\u7ec4\u5206\u5df2\u88ab\u4e00\u9879\u66ff\u4ee3"
              u"\u68c0\u9a8c\u6392\u9664\u4e3a\u9a71\u52a8\u56e0\u7d20\u2014\u2014\u8be5\u68c0\u9a8c\u56fa\u5b9a"
              u"\u53c2\u8003\u9762\u677f\u53ca\u5176\u8bad\u7ec3\u6837\u672c\uff08\u7ed3\u679c 3.3\uff09"
              u"\u2014\u2014\u4f46\u6837\u672c\u91cf\u7ec4\u5206\u5728\u5f53\u524d\u516c\u5f00\u8d44\u6e90\u4e0b"
              u"\u65e0\u6cd5\u88ab\u5206\u79bb\uff0c\u6545\u5f52\u56e0\u662f\u6709\u754c\u7684\uff0c\u800c"
              u"\u975e\u5df2\u88ab\u89e3\u6790\u3002")

SPEC = {
    EN: [dict(para=47, mode='append', text=EN_47),
         dict(para=84, mode='append', text=EN_84),
         dict(para=112, mode='append', text=EN_112),
         dict(para=129, mode='append', text=EN_129),
         dict(para=134, mode='append', text=EN_134),
         dict(para=155, mode='insert_after', marker=EN_155_MARK, text=EN_155_INS)],
    CN: [dict(para=47, mode='append', text=CN_47),
         dict(para=84, mode='append', text=CN_84),
         dict(para=112, mode='append', text=CN_112),
         dict(para=129, mode='append', text=CN_129),
         dict(para=134, mode='append', text=CN_134),
         dict(para=155, mode='insert_after', marker=CN_155_MARK, text=CN_155_INS)],
}


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def make_run(template_r, text):
    """Clone a run element and give it exactly one w:t carrying `text`."""
    r = etree.fromstring(etree.tostring(template_r))
    for t in r.findall(WQ + 't'):
        r.remove(t)
    for extra in ('br', 'tab', 'drawing', 'noBreakHyphen'):
        for e in r.findall(WQ + extra):
            r.remove(e)
    t = etree.SubElement(r, WQ + 't')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return r


def process(path):
    edits = SPEC[path]
    zin = zipfile.ZipFile(path)
    infos = zin.infolist()
    parts = {i.filename: zin.read(i.filename) for i in infos}
    zin.close()

    root = etree.fromstring(parts['word/document.xml'])
    body = root.find(WQ + 'body')
    paras = [c for c in body if c.tag == WQ + 'p']
    print('  paragraphs in body: %d' % len(paras))

    log = []
    for e in edits:
        p = paras[e['para']]
        runs = p.findall(WQ + 'r')
        full = ''.join(t.text or '' for t in p.iter(WQ + 't'))
        assert e['text'].strip()[:40] not in full, 'already applied? P%04d' % e['para']

        if e['mode'] == 'append':
            tmpl = runs[0]
            for r in reversed(runs):
                if ''.join(t.text or '' for t in r.findall(WQ + 't')).strip():
                    tmpl = r
                    break
            p.append(make_run(tmpl, e['text']))
            log.append('P%04d append  +%d chars' % (e['para'], len(e['text'])))
        else:
            hit = None
            for t in p.iter(WQ + 't'):
                if t.text and e['marker'] in t.text:
                    hit = t
                    break
            assert hit is not None, 'marker not found in P%04d' % e['para']
            hits = sum(1 for t in p.iter(WQ + 't') if t.text and e['marker'] in t.text)
            assert hits == 1, 'marker ambiguous (%d) in P%04d' % (hits, e['para'])
            before, after = hit.text.split(e['marker'], 1)
            run = hit.getparent()
            rA = etree.fromstring(etree.tostring(run))
            rB = etree.fromstring(etree.tostring(run))
            for r, txt in ((rA, before + e['marker'] + e['text']), (rB, after)):
                ts = r.findall(WQ + 't')
                ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                ts[0].text = txt
                for extra in ts[1:]:
                    r.remove(extra)
            parent = run.getparent()
            idx = list(parent).index(run)
            parent.remove(run)
            parent.insert(idx, rA)
            parent.insert(idx + 1, rB)
            log.append('P%04d insert  +%d chars (mid-paragraph)' % (e['para'], len(e['text'])))

    newxml = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

    out = path + '.new'
    zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for i in infos:
        if i.filename == 'word/document.xml':
            zi = zipfile.ZipInfo('word/document.xml', date_time=i.date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, newxml)
        else:
            zi = zipfile.ZipInfo(i.filename, date_time=i.date_time)
            zi.compress_type = i.compress_type
            zi.external_attr = i.external_attr
            zout.writestr(zi, parts[i.filename])
    zout.close()
    print('  wrote %s' % os.path.basename(out))
    for l in log:
        print('   ', l)
    return out


def verify(newp, orig, edits):
    z = zipfile.ZipFile(newp)
    names = z.namelist()
    zo = zipfile.ZipFile(orig)
    assert sorted(names) == sorted(zo.namelist()), 'part list changed'
    assert 'word/footer1.xml' in names, 'footer part lost'
    root = etree.fromstring(z.read('word/document.xml'))
    body = root.find(WQ + 'body')
    paras = [c for c in body if c.tag == WQ + 'p']
    txt = '\n'.join(''.join(t.text or '' for t in p.iter(WQ + 't')) for p in paras)
    ok = []
    for e in edits:
        probe = e['text'].strip().replace('\u2014', '\u2014')[:30]
        ok.append(probe in txt)
    # every part other than document.xml must be byte-identical
    same = 0
    for n in names:
        if n == 'word/document.xml':
            continue
        if z.read(n) == zo.read(n):
            same += 1
    print('   verify: parts=%d identical_non_docx=%d/%d  new_text_present=%s'
          % (len(names), same, len(names) - 1, all(ok)))
    assert all(ok), 'some new text missing'
    assert same == len(names) - 1, 'a non-document part was modified'


if __name__ == '__main__':
    bk = os.path.join(BKROOT, 'before_M1M2_' + TS)
    os.makedirs(bk, exist_ok=True)
    print('backup ->', bk)
    for p in (EN, CN):
        print('before md5', os.path.basename(p), md5(p))
        shutil.copy2(p, os.path.join(bk, os.path.basename(p)))

    news = {}
    for p in (EN, CN):
        print('== processing', os.path.basename(p))
        news[p] = process(p)

    for p in (EN, CN):
        print('== verify', os.path.basename(p))
        verify(news[p], p, SPEC[p])

    for p in (EN, CN):
        os.replace(news[p], p)
        print('   replaced; after md5', os.path.basename(p), md5(p))

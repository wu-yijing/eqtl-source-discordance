#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_r2_notes.py — 把 R2 方案的 P1/P2 注记施加到稿件，**只改 word/document.xml**。

背景
----
`docs/audit_notes/R2残余差异消除方案_20261002.md` 把 R2 的三项残差逐条诊断完毕，
并给出了可直接粘贴的英文文本。该文件结尾写着：

    做完 P1+P2 后，R2 = 0，R1 覆盖两文档的全部报告值。

本脚本就是执行那一步，并且**不是把文字抄一遍**——它每次运行都从那份方案里**重新抽取**
待插入的段落，抽取不到就报错退出。所以：若方案被改动，本脚本会失败而不是悄悄分叉。

插入位置（两支都靠唯一锚点定位，锚点不唯一即断言失败）
------------------------------------------------------
SI   Table S17 表注段（"…archived with the code."）之后，新增两段：
       · 段 1 = Resampling details 句（方案 §三(2)）+ 置换单元句（方案 §四）
       · 段 2 = sandwich / jackknife 估计量（方案 §二）
     新段落按原表注段的 `<w:pPr>` 克隆，因此版式与相邻表注一致。
稿件 §一 方案 A 的括号：就地替换 `exceeds that by 6.1 points` →
     `exceeds that by 6.1 points (6.01 points when evaluated at the unrounded ρ = 0.3896
     and rate = 68.75%)`。纯增补，不改任何数字。

字形
----
SI 正文已出现的非 ASCII 字符共 30 种。方案 §二 的公式里有一个字符是 **Times New Roman
不含**的：`∈`（U+2208，实测 times.ttf / timesbd.ttf / timesi.ttf 均缺）。其余 14 个
（Σ φ ỹ ̃ ̄ ² · − √ ρ 等）字体均有覆盖。故本脚本只做**一处**替换：

    Σ_{i∈g}   →   Σ_{i in g}

并在输出里明写这一处替换，避免读者以为原文如此。方案 §三(2)（Δ ρ）、§四（—）用到的
字符 SI 本来就已使用。

用法
----
    python apply_r2_notes.py --si <in.docx> --si-out <out.docx>
    python apply_r2_notes.py --ms <in.docx> --ms-out <out.docx>
    python apply_r2_notes.py --si ... --si-out ... --ms ... --ms-out ...   # 两支同时
"""
import argparse
import os
import random
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
R2_NOTE = os.path.normpath(os.path.join(HERE, '..', 'R2残余差异消除方案_20261002.md'))

#: SI 表 S17 表注段的段末锚点。该句在 rev6 中唯一。
SI_NOTE_TAIL = ('Machine-readable output and the analysis script are archived '
                'with the code.')

#: 稿件 §一 的替换锚点。在 rev7 中唯一。
MS_ANCHOR = 'exceeds that by 6.1 points'

#: 字体缺 `∈`，唯一一处替换。替换前后都要能在方案原文里找到，见 check_substitution()。
GLYPH_SUBSTITUTION = ('Σ_{i∈g}', 'Σ_{i in g}')


# --------------------------------------------------------------------------
# 1. 从方案中抽取待插入文本（不缓存、不硬编码）
# --------------------------------------------------------------------------
def _norm(t):
    """去掉 markdown 引用符，把换行折成空格。"""
    return ' '.join(t.replace('>', '').split())


def extract_blocks(note_path=R2_NOTE):
    """从 R2 方案抽取 A / C / D / E 四块。抽不到即抛错。"""
    s = open(note_path, encoding='utf-8').read()
    pats = {
        # §三(2) Resampling details 整段
        'A': r'\*\*Resampling details\.\*\*.*?bootstrap\)\.',
        # §二 估计量整段
        'C': r'\*\*Cluster-robust \(sandwich\).*?df = K − 1 = 31\.',
        # §四 置换单元（反引号内的整句）
        'D': r'`(Gene labels are permuted as whole genes.*?)`',
        # §一 方案 A 的目标整句（用于确认括号里的内容与方案一致）
        'E': r'改为：`…(.*?)…`',
    }
    out = {}
    for k, p in pats.items():
        m = re.search(p, s, re.S)
        if not m:
            raise SystemExit('R2 方案中抽不到第 %s 块（pattern %r）——方案被改动过？'
                             % (k, p))
        out[k] = _norm(m.group(1) if k in ('D', 'E') else m.group(0))
    # 括号句：只取其中的括号部分
    m = re.search(r'(\(6\.01 points[^)]*\))', out['E'])
    if not m:
        raise SystemExit('§一 的括号文本抽不到')
    out['E_paren'] = m.group(1)
    # 唯一一处字形替换必须在方案原文里成立：源形在、目标形不在
    src_form, dst_form = GLYPH_SUBSTITUTION
    if src_form not in out['C']:
        raise SystemExit('字形替换的源形 %r 不在 §二 文本里' % src_form)
    if dst_form in out['C']:
        raise SystemExit('§二 文本里已经出现了目标形 %r —— 替换假设不再成立' % dst_form)
    return out


# --------------------------------------------------------------------------
# 2. 行内 markdown → docx run 列表
# --------------------------------------------------------------------------
def runs_of(text, rpr):
    """把 `**bold**` 变成粗体 run，去掉反引号，其余为普通 run。"""
    text = text.replace('`', '')
    parts = re.split(r'\*\*(.+?)\*\*', text)
    out = []
    for i, seg in enumerate(parts):
        if not seg:
            continue
        out.append((i % 2 == 1, seg))          # 奇数下标 = 原本被 ** 包住的
    return [(bold, seg, rpr) for bold, seg in out]


def _esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def run_xml(text, rpr, bold=False):
    r = rpr if not bold else _insert_bold(rpr)
    return ('<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>'
            % (r, _esc(text)))


def _insert_bold(rpr):
    """rpr 是 <w:rPr> 与 </w:rPr> 之间的内容，尾部追加 <w:b/><w:bCs/>。"""
    return rpr + '<w:b/><w:bCs/>'


# --------------------------------------------------------------------------
# 3. 结构保真的最小化重建
# --------------------------------------------------------------------------
def rewrite(src_path, out_path, new_doc_xml):
    with zipfile.ZipFile(src_path) as src, \
         zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == 'word/document.xml':
                data = new_doc_xml.encode('utf-8')
            info = zipfile.ZipInfo(item.filename, date_time=item.date_time)
            info.compress_type = item.compress_type
            info.external_attr = item.external_attr
            info.internal_attr = item.internal_attr
            info.create_system = item.create_system
            dst.writestr(info, data)
    return [i.filename for i in zipfile.ZipFile(src_path).infolist()], \
           [i.filename for i in zipfile.ZipFile(out_path).infolist()]


def _para_ids(x):
    return set(re.findall(r'w14:paraId="([0-9A-Fa-f]{8})"', x))


def _fresh_id(x):
    have = _para_ids(x)
    while True:
        cand = '%08X' % random.getrandbits(32)
        if cand not in have:
            return cand


def _ppr_and_rpr_of_para_ending_at(x, tail_anchor):
    """取出以 tail_anchor 结尾的那一段的 <w:pPr>…</w:pPr> 与一个 run 的 rPr。"""
    i = x.find(tail_anchor)
    assert i >= 0, '段末锚点找不到'
    end = x.index('</w:p>', i) + len('</w:p>')
    start = x.rfind('<w:p ', 0, i)
    para = x[start:end]
    m = re.search(r'<w:pPr>.*?</w:pPr>', para, re.S)
    ppr = m.group(0) if m else '<w:pPr/>'
    m2 = re.search(r'<w:r><w:rPr>(.*?)</w:rPr>', para, re.S)
    rpr = m2.group(1) if m2 else ''
    return ppr, rpr, start, end


# --------------------------------------------------------------------------
# 4. 两支
# --------------------------------------------------------------------------
def apply_si(si_in, si_out, blocks):
    x = zipfile.ZipFile(si_in).read('word/document.xml').decode('utf-8')

    if x.count(SI_NOTE_TAIL) != 1:
        raise SystemExit('SI 锚点不唯一：%d 次' % x.count(SI_NOTE_TAIL))
    ppr, rpr, _s, end = _ppr_and_rpr_of_para_ending_at(x, SI_NOTE_TAIL)

    disclosure = blocks['A'] + ' ' + blocks['D']
    estimator = blocks['C'].replace(*GLYPH_SUBSTITUTION)

    def para(text, pid):
        body = ''.join(run_xml(seg, rpr, bold=b) for b, seg, _ in runs_of(text, rpr))
        return '<w:p w14:paraId="%s">%s%s</w:p>' % (pid, ppr, body)

    ins = (para(disclosure, _fresh_id(x)) +
           para(estimator, _fresh_id(x)))
    x2 = x[:end] + ins + x[end:]

    a, b = rewrite(si_in, si_out, x2)
    return dict(anchor=SI_NOTE_TAIL, inserted=ins, parts_in=len(a), parts_out=len(b),
                disclosure=disclosure, estimator=estimator,
                estimator_as_written_in_note=blocks['C'])


def apply_ms(ms_in, ms_out, blocks):
    x = zipfile.ZipFile(ms_in).read('word/document.xml').decode('utf-8')
    if x.count(MS_ANCHOR) != 1:
        raise SystemExit('稿件锚点不唯一：%d 次' % x.count(MS_ANCHOR))
    old = MS_ANCHOR
    new = MS_ANCHOR + ' ' + blocks['E_paren']
    x2 = x.replace(old, new)
    a, b = rewrite(ms_in, ms_out, x2)
    return dict(anchor=old, replacement=new, parts_in=len(a), parts_out=len(b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--si'); ap.add_argument('--si-out')
    ap.add_argument('--ms'); ap.add_argument('--ms-out')
    ap.add_argument('--note', default=R2_NOTE)
    a = ap.parse_args()
    if not (a.si and a.si_out) and not (a.ms and a.ms_out):
        ap.error('至少要给 --si/--si-out 或 --ms/--ms-out 一组')

    blocks = extract_blocks(a.note)
    print('从 %s 抽到 A/C/D/E 四块 ✓' % os.path.basename(a.note))
    print('  字形替换（唯一一处）：%r → %r' % GLYPH_SUBSTITUTION)
    print('  （依据：Times New Roman 实测覆盖 14/15，唯缺 ∈ U+2208）')
    print()

    if a.si and a.si_out:
        r = apply_si(a.si, a.si_out, blocks)
        print('[SI] 锚点：%r' % r['anchor'])
        print('     部件 %d → %d（应相等）' % (r['parts_in'], r['parts_out']))
        print('     新增 2 段：')
        print('       · %s' % r['disclosure'][:120])
        print('       · %s' % r['estimator'][:120])
        print('     写出 %s (%d B)' % (a.si_out, os.path.getsize(a.si_out)))
        print()

    if a.ms and a.ms_out:
        r = apply_ms(a.ms, a.ms_out, blocks)
        print('[MS] 替换：%r' % r['anchor'])
        print('         → %r' % r['replacement'])
        print('     部件 %d → %d（应相等）' % (r['parts_in'], r['parts_out']))
        print('     写出 %s (%d B)' % (a.ms_out, os.path.getsize(a.ms_out)))

    return 0


if __name__ == '__main__':
    sys.exit(main())

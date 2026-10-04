#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_r2_notes.py — 独立核验 `apply_r2_notes.py` 的两份产物。

不读施加脚本的任何中间产物，只读三样东西：**输入 docx、输出 docx、R2 方案**。
七项检查：

  1 部件表完全相同（名字与顺序）；除 word/document.xml 外逐部件逐字节相同
  2 document.xml 与输入**只有一处连续差异**（b = a[:i] + ins + a[j:]，且 j == i）
  3 ins 的 run 序列 = 从 R2 方案现抽文本编成的 run 序列（逐字符相等，含唯一一处字形替换）
    且新增段的 <w:pPr> 与 S17 表注段相同（版式继承，非新造样式）
  4 文本层：SI 段数 = 输入 + 2，两段新文本紧随 S17 表注且与方案逐字相等；
    正文恰好 1 段变化，且改动仅为括号插入
  5 SI 四个表格标记计数不变（tblPrEx / tblCellMar / tblBorders / insideH）
  6 字形审计：插入文本的每个非 ASCII 字符都在 Times New Roman 有覆盖
  7 数字审计：输入里出现过的数值 token 一个不少（新增 token 逐项列出）

用法：
    python verify_r2_notes.py --si-in A.docx --si-out B.docx --ms-in C.docx --ms-out D.docx
退出码 0 = 七项全过。
"""
import argparse
import collections
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_r2_notes as A                                        # noqa: E402

#: 实测（fontTools，times.ttf / timesbd.ttf / timesi.ttf）：Times New Roman 缺此码位
FONT_MISSING = {0x2208}


def parts(path):
    with zipfile.ZipFile(path) as z:
        return [(i.filename, z.read(i.filename)) for i in z.infolist()]


def docxml(path):
    return zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')


def contiguous_span(a, b):
    """a 与 b 是否只在单处连续区间不同。返回 (i, j, ins) 或 None。"""
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    j = 0
    while j < (n - i) and a[len(a) - 1 - j] == b[len(b) - 1 - j]:
        j += 1
    if len(a) - j != i:
        return None
    return i, len(a) - j, b[i:len(b) - j]


def runs_only(s):
    return re.findall(r'<w:r>.*?</w:r>', s, re.S)


def paras(path):
    import docx
    return [p.text for p in docx.Document(path).paragraphs]


def plain(text):
    """方案文本 → 文档里实际呈现的纯文本（去掉 ** 与反引号）。"""
    return text.replace('**', '').replace('`', '')


def expect_runs(blocks, rpr):
    """按施加脚本同样的规则，把两段预期文本编成 run 序列。"""
    out = []
    for text in (blocks['A'] + ' ' + blocks['D'],
                 blocks['C'].replace(*A.GLYPH_SUBSTITUTION)):
        out += [A.run_xml(seg, rpr, bold=b) for b, seg, _ in A.runs_of(text, rpr)]
    return out


def numeric_tokens(texts):
    return collections.Counter(t for s in texts for t in re.findall(r'\d+(?:[.,]\d+)*', s))


def si_note_rpr(si_in):
    """从输入里取出 S17 表注段第一个 run 的 rPr 内容，供预期串构造。"""
    x = docxml(si_in)
    _ppr, rpr, _s, _e = A._ppr_and_rpr_of_para_ending_at(x, A.SI_NOTE_TAIL)
    return rpr


def check_si(si_in, si_out, blocks, problems):
    print('  [1] 部件表')
    pi, po = parts(si_in), parts(si_out)
    if [k for k, _ in pi] != [k for k, _ in po]:
        problems.append('SI 部件表不同')
        print('      ✗ 部件表不同')
    else:
        diff = [k for (k, v), (_, w) in zip(pi, po) if v != w]
        if diff == ['word/document.xml']:
            print('      ✓ %d 个部件；仅 word/document.xml 被重写' % len(pi))
        else:
            problems.append('SI 被重写的部件为 %s' % diff)
            print('      ✗ 被重写的部件为 %s' % diff)

    xi, xo = docxml(si_in), docxml(si_out)
    print('  [2] document.xml：单处连续差异')
    span = contiguous_span(xi, xo)
    if not span:
        problems.append('SI 的 document.xml 差异不是单处连续区间')
        print('      ✗ 差异不连续')
        return
    i, j, ins = span
    if j != i:
        problems.append('SI 的差异不是纯插入（j=%d ≠ i=%d）' % (j, i))
    print('      ✓ 纯插入，区间 [%d, %d)，插入 %d 字符' % (i, j, len(ins)))

    print('  [3] 插入串 = 方案现抽文本；新增段继承表注段版式')
    rpr = si_note_rpr(si_in)
    got = runs_only(ins)
    exp = expect_runs(blocks, rpr)
    if got == exp:
        print('      ✓ run 序列逐字符相等（%d 个 run），含 %r → %r 一处字形替换'
              % ((len(got),) + A.GLYPH_SUBSTITUTION))
    else:
        problems.append('SI 插入 run 序列与方案不符')
        print('      ✗ run 序列不符（got %d / exp %d）' % (len(got), len(exp)))
        for k, (g, e) in enumerate(zip(got, exp)):
            if g != e:
                print('         第 %d 个 run 不同:\n           got %r\n           exp %r'
                      % (k + 1, g[:180], e[:180]))
                break
    ppr_note, _r, _s, _e = A._ppr_and_rpr_of_para_ending_at(xi, A.SI_NOTE_TAIL)
    pprs = re.findall(r'<w:pPr>.*?</w:pPr>', ins, re.S)
    if pprs and all(p == ppr_note for p in pprs):
        print('      ✓ 新增 %d 段的 <w:pPr> 与 S17 表注段相同（未新造版式）' % len(pprs))
    else:
        problems.append('SI 新增段的 pPr 与表注段不同')
        print('      ✗ pPr 与表注段不同：%r vs %r' % (pprs, ppr_note))

    print('  [4] 文本层：段数与位置')
    ti, to = paras(si_in), paras(si_out)
    pos = [k for k, t in enumerate(ti) if A.SI_NOTE_TAIL in t]
    plain_new = [plain(blocks['A'] + ' ' + blocks['D']),
                 plain(blocks['C'].replace(*A.GLYPH_SUBSTITUTION))]
    if len(to) == len(ti) + 2 and len(pos) == 1 and to[pos[0]] == ti[pos[0]] \
            and to[pos[0] + 1:pos[0] + 3] == plain_new:
        print('      ✓ 段数 %d → %d；两段新文本紧随 S17 表注（第 %d 段后），逐字相等'
              % (len(ti), len(to), pos[0]))
    else:
        problems.append('SI 段数或插入位置不符')
        print('      ✗ 段数 %d → %d；表注在 %s；新段 = %r'
              % (len(ti), len(to), pos, to[pos[0] + 1:pos[0] + 3] if pos else None))
    n_ok = sum(1 for a, b in zip(ti, [t for k, t in enumerate(to)
                                      if k not in (pos[0] + 1, pos[0] + 2)]) if a == b)
    if n_ok == len(ti):
        print('      ✓ 原有 %d 段文本逐段未变' % len(ti))
    else:
        problems.append('SI 原有段文本被改动（仅 %d/%d 相同）' % (n_ok, len(ti)))
        print('      ✗ 原有段文本被改动（仅 %d/%d 相同）' % (n_ok, len(ti)))

    print('  [5] 表格标记计数')
    marks = ('tblPrEx', 'tblCellMar', 'tblBorders', 'insideH')
    bad = [m for m in marks if xi.count(m) != xo.count(m)]
    if bad:
        problems.append('SI 表格标记变化：%s' % bad)
        print('      ✗ 变化：%s' % bad)
    else:
        print('      ✓ %s 四项均不变' % ' / '.join(marks))

    print('  [6] 字形审计')
    old_chars = {c for c in ''.join(ti) if ord(c) > 127}
    used = sorted({c for c in ''.join(plain_new) if ord(c) > 127})
    added = [c for c in used if c not in old_chars]
    miss = [c for c in used if ord(c) in FONT_MISSING]
    if miss:
        problems.append('插入文本含字体缺字形：%s' % miss)
        print('      ✗ 含字体缺字形：%s' % miss)
    else:
        print('      ✓ 用到 %d 种非 ASCII 字符（%d 种为本文档新引入），字形均有覆盖'
              % (len(used), len(added)))
        print('        新引入：%s' % (' '.join('%s(U+%04X)' % (c, ord(c)) for c in added)
                                    or '无'))

    print('  [7] 数字审计')
    ni, no = numeric_tokens(ti), numeric_tokens(to)
    missing = {k: v for k, v in ni.items() if no.get(k, 0) < v}
    if missing:
        problems.append('SI 原有数值 token 减少：%s' % missing)
        print('      ✗ 原有 token 减少：%s' % missing)
    else:
        added_tok = sorted(set(no) - set(ni))
        print('      ✓ 原有数值 token 一个不少；新增 %d 个'
              % len(added_tok))
        print('        新增：%s%s' % (' '.join(added_tok[:26]),
                                     ' …' if len(added_tok) > 26 else ''))


def check_ms(ms_in, ms_out, blocks, problems):
    print('  [1] 部件表')
    pi, po = parts(ms_in), parts(ms_out)
    if [k for k, _ in pi] != [k for k, _ in po]:
        problems.append('正文部件表不同')
        print('      ✗ 部件表不同')
    else:
        diff = [k for (k, v), (_, w) in zip(pi, po) if v != w]
        if diff == ['word/document.xml']:
            print('      ✓ %d 个部件；仅 word/document.xml 被重写' % len(pi))
        else:
            problems.append('正文被重写的部件为 %s' % diff)
            print('      ✗ 被重写的部件为 %s' % diff)

    xi, xo = docxml(ms_in), docxml(ms_out)
    print('  [2] document.xml：单处连续差异')
    span = contiguous_span(xi, xo)
    if not span:
        problems.append('正文差异不是单处连续区间')
        print('      ✗ 差异不连续')
        return
    i, j, ins = span
    print('      ✓ 纯插入' if j == i else '      ! 非纯插入（j=%d ≠ i=%d）' % (j, i))
    print('        区间 [%d, %d)，插入 %d 字符' % (i, j, len(ins)))

    print('  [3] 插入串 = 方案 §一 的括号')
    exp = ' ' + blocks['E_paren']
    if ins == exp:
        print('      ✓ 逐字符相等：%r' % exp)
    else:
        problems.append('正文插入串与方案不符')
        print('      ✗ got %r\n         exp %r' % (ins, exp))

    print('  [4] 文本层：恰好 1 段变化')
    ti, to = paras(ms_in), paras(ms_out)
    changed = [k for k, (a, b) in enumerate(zip(ti, to)) if a != b]
    if len(ti) == len(to) and len(changed) == 1:
        k = changed[0]
        cut = ti[k].find(A.MS_ANCHOR)
        print('      ✓ 段数 %d 不变；第 %d 段变化' % (len(to), k))
        print('        改前：…%s…' % ti[k][max(0, cut - 50):cut + 160])
        print('        改后：…%s…' % to[k][max(0, cut - 50):cut + 160])
        if to[k] == ti[k].replace(A.MS_ANCHOR, A.MS_ANCHOR + ' ' + blocks['E_paren']):
            print('      ✓ 该段变化恰是括号插入，其余字符不变')
        else:
            problems.append('正文该段的变化不止括号插入')
            print('      ✗ 该段的变化不止括号插入')
    else:
        problems.append('正文并非恰好 1 段变化（changed=%d）' % len(changed))
        print('      ✗ 段数 %d → %d，变化 %d 段' % (len(ti), len(to), len(changed)))

    print('  [7] 数字审计')
    ni, no = numeric_tokens(ti), numeric_tokens(to)
    missing = {k: v for k, v in ni.items() if no.get(k, 0) < v}
    if missing:
        problems.append('正文原有数值 token 减少：%s' % missing)
        print('      ✗ 原有 token 减少：%s' % missing)
    else:
        print('      ✓ 原有数值 token 一个不少；新增：%s'
              % (' '.join(sorted(set(no) - set(ni))) or '无'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--si-in'); ap.add_argument('--si-out')
    ap.add_argument('--ms-in'); ap.add_argument('--ms-out')
    a = ap.parse_args()
    blocks = A.extract_blocks()
    problems = []
    print('=' * 78)
    print('R2 注记施加 —— 独立核验')
    print('=' * 78)
    if a.si_in and a.si_out:
        print('\n【SI】')
        check_si(a.si_in, a.si_out, blocks, problems)
    if a.ms_in and a.ms_out:
        print('\n【正文】')
        check_ms(a.ms_in, a.ms_out, blocks, problems)
    print()
    print('=' * 78)
    if problems:
        print('%d 项未通过：' % len(problems))
        for p in problems:
            print('  - %s' % p)
        return 1
    print('七项检查全部通过 ✓')
    return 0


if __name__ == '__main__':
    sys.exit(main())

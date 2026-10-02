# -*- coding: utf-8 -*-
"""把归档脚本 m15_pc.py 的两处路径改到本机当前可用位置（仅路径，逻辑不动）。"""
p = 'm15_pc.py'
L = open(p, encoding='utf-8').read().split('\n')
assert L[10].startswith('AF = '), L[10]
assert L[11].startswith('OUT_DIR = '), L[11]
new_af = 'AF = r"E:\\workbuddy\\BMC Genomics投稿资料\\定稿资料\\Additional file 1_审稿意见修订_20260917.docx"'
new_out = 'OUT_DIR = r"E:\\workbuddy\\GE投稿资料\\_重算_20261002\\r3\\m15"'
L[10] = new_af
L[11] = new_out
open(p, 'w', encoding='utf-8').write('\n'.join(L))
print('patched:')
print(' ', L[10])
print(' ', L[11])

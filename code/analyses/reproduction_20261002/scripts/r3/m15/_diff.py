# -*- coding: utf-8 -*-
"""把 m15_pc.py 的重跑输出与两份归档 JSON 逐键比对。"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
new = json.load(open(os.path.join(HERE, 'm15_positive_control.json'), encoding='utf-8'))
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))
import paths as _paths          # noqa: E402  集中路径解析，见 ../../../paths.py
cands = {
    '本仓库 code/figures/m15_positive_control.json': str(_paths.fig('m15_json')),
    # 归档副本是可选的：分别用 EQTL_M15_ARCHIVE_1 / _2 指向即可，缺则跳过
    '归档副本 1 (EQTL_M15_ARCHIVE_1)':
        os.environ.get('EQTL_M15_ARCHIVE_1', os.path.join(HERE, 'm15_archive_1.json')),
    '归档副本 2 (EQTL_M15_ARCHIVE_2)':
        os.environ.get('EQTL_M15_ARCHIVE_2', os.path.join(HERE, 'm15_archive_2.json')),
}

def walk(a, b, path=''):
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: diffs.append((path + '/' + k, '<缺少>', '有'))
            elif k not in b: diffs.append((path + '/' + k, '有', '<缺少>'))
            else: diffs += walk(a[k], b[k], path + '/' + k)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): diffs.append((path, f'len={len(a)}', f'len={len(b)}'))
        else:
            for i, (x, y) in enumerate(zip(a, b)): diffs += walk(x, y, f'{path}[{i}]')
    elif isinstance(a, float) and isinstance(b, float):
        if abs(a - b) > 1e-12: diffs.append((path, a, b))
    elif a != b:
        diffs.append((path, a, b))
    return diffs

print('重跑输出的顶层键:', sorted(new.keys()))
print()
for lab, p in cands.items():
    if not os.path.exists(p):
        print(f'--- {lab}: 文件不存在，跳过'); continue
    old = json.load(open(p, encoding='utf-8'))
    d = walk(new, old)
    print(f'--- {lab}: 差异项 {len(d)}')
    for path, a, b in d[:25]:
        print(f'    {path}: 重跑={a}  归档={b}')
    print()

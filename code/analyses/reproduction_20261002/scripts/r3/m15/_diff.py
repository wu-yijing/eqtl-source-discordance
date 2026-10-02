# -*- coding: utf-8 -*-
"""把 m15_pc.py 的重跑输出与两份归档 JSON 逐键比对。"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
new = json.load(open(os.path.join(HERE, 'm15_positive_control.json'), encoding='utf-8'))
cands = {
    '本地归档 2026-09-17-20-59-12/_review': r'E:\workbuddy\2026-09-17-20-59-12\_review\m15_positive_control.json',
    '仓库 code/figures (eqtl-source-discordance)': r'E:\workbuddy\eqtl-source-discordance\code\figures\m15_positive_control.json',
    '仓库 figure_scripts_officialZ_20260917 (audit)': r'E:\workbuddy\eqtl-source-discordance-audit\figure_scripts_officialZ_20260917\m15_positive_control.json',
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

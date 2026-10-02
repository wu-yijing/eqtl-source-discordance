# -*- coding: utf-8 -*-
"""把 m15_pc.py 的重跑输出与两份归档 JSON 逐键比对。"""
# ---------------------------------------------------------------------------
# Path resolution (added 2026-10-02). Satisfies code/README.md rule 3:
# "No absolute paths, no personal directories."
# ---------------------------------------------------------------------------
import os as _os
import sys as _sys


def _repro_pkg():
    d = _os.path.dirname(_os.path.abspath(__file__))
    for _ in range(6):
        if _os.path.exists(_os.path.join(d, 'paths_config.py')):
            return d
        d = _os.path.dirname(d)
    raise RuntimeError('paths_config.py not found above %s' % __file__)


_sys.path.insert(0, _repro_pkg())
import paths_config as PC        # noqa: E402
PC.apply_cli_overrides()
# ---------------------------------------------------------------------------

import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
# 生成脚本把产物写到包的 results/（2026-10-02 起），不再写在自己旁边。
new = json.load(open(os.path.join(PC.RESULTS, 'm15_positive_control.json'), encoding='utf-8'))
cands = {
    'repo code/figures/m15_positive_control.json (tracked)':
        os.path.join(PC.REPO, 'code', 'figures', 'm15_positive_control.json'),
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

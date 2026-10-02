# -*- coding: utf-8 -*-
"""修正 recompute_r3_s9_s20.py 中 Table S20 组间功效的 Δ 定义。

归档脚本 m15_pc.py 的定义（2026-09-17-20-59-12/_review/m15_pc.py:118-151）：
    p2 = r1 + d/100        # Δ 加在 **HK（参照组）率** 上，不是加在观测候选率上
    power(n1, r1, n2, p2) = Σ_a Σ_b pmf1(a)·pmf2(b)·1[Fisher双侧(a,b) < 0.05]
本脚本原先误用 base2（观测候选率）+ Δ，导致 Δmin 系统性偏小。
"""
p = 'recompute_r3_s9_s20.py'
s = open(p, encoding='utf-8').read()

old = """def exact_mde(n1, p1, n2, base2, target=0.80, alpha=0.05):
    \"\"\"枚举 (a,b) 全空间；返回达到 80% 功效的最小绝对百分点差（0.5 pp 网格）。\"\"\"
    best = None
    for dpp in np.arange(0.5, 30.01, 0.5):
        p2 = min(0.99, base2 / 100 + dpp / 100)"""
new = """def exact_mde(n1, p1, n2, base2, target=0.80, alpha=0.05):
    \"\"\"枚举 (a,b) 全空间；返回达到 80% 功效的最小绝对百分点差（0.5 pp 网格）。
    口径（照 2026-09-17-20-59-12/_review/m15_pc.py）：Δ 加在**参照组(组 1)率**上，
    即 p2 = r1 + Δ；观测候选率 r2 只作行标签，不参与计算。\"\"\"
    best = None
    for dpp in np.arange(0.5, 30.01, 0.5):
        p2 = min(0.99, p1 / 100 + dpp / 100)"""
assert old in s, 'exact_mde 段未找到'
s = s.replace(old, new)

old2 = "log('\\n  (7c) 组间最小可检差：在观测分母与率下对 2×2 结果空间做精确枚举（Fisher 双侧, α=0.05, 80% 功效）')"
new2 = ("log('\\n  (7c) 组间最小可检差：对 2×2 结果空间做精确枚举（Fisher 双侧, α=0.05, 80% 功效）')\n"
        "log('       口径：Δ 加在参照组(组 1 = 管家/HRT 随机对照)率上 → p2 = r1 + Δ；'\n"
        "    '与归档脚本 2026-09-17-20-59-12/_review/m15_pc.py:118-151 逐字一致')")
assert old2 in s, '7c 标题未找到'
s = s.replace(old2, new2)
open(p, 'w', encoding='utf-8').write(s)
print('patched OK')

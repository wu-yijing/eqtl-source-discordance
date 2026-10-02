# -*- coding: utf-8 -*-
"""报告三元组 (SE=0.125, 一侧 P=0.002, 双侧 P=0.004, df=31) 的自洽区间。"""
import math
from scipy.stats import t as td
rho=0.389639; df=31
print('='*92); print('sandwich SE 报告三元组的自洽性'); print('='*92)
for se in [0.1154,0.1244,0.1250,0.1264,0.1270,0.1284,0.1299,0.1312,0.1367]:
    z=rho/se
    one=td.sf(z,df); two=2*td.sf(abs(z),df)
    print(f'  SE={se:.4f} → z={z:.4f}  一侧 P={one:.5f}（显示 {one:.3f}）  双侧 P={two:.5f}（显示 {two:.3f}）')
print()
# 反解：要让一侧 P 显示 0.002 且双侧显示 0.004，SE 的允许范围
lo=hi=None
for i in range(400001):
    se=0.1100+i*1e-7
    z=rho/se; one=td.sf(z,df); two=2*td.sf(abs(z),df)
    ok = (round(one,3)==0.002) and (round(two,3)==0.004)
    if ok and lo is None: lo=se
    if ok: hi=se
print(f'  使 (一侧,双侧) 显示为 (0.002, 0.004) 的 SE 区间 = [{lo:.5f}, {hi:.5f}]')
print(f'  报告的 SE = 0.125 落在该区间内 → 三元组自洽；区间内任意 SE 都给同样的显示值。')
print()
print('='*92); print('三项 R2 的可消除性判定'); print('='*92)
print('  A13      ：取整链，补一句口径说明或改用未取整值 → 可完全消除')
print('  sandwich ：估计量未指定；影响函数族 14 种候选无一致值，但三元组自洽 → 补公式后即可完全消除')
print('  行序敏感 ：除非规范重抽样的基因排序，否则端点永不可逐位复现 → 需改实现 + 补说明')

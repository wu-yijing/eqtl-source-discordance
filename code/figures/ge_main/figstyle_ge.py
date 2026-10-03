# -*- coding: utf-8 -*-
"""GE 投稿版四张主图的**统一绘图样式**（2026-10-01 建立）。

设计依据（Wiley 官方 figure preparation 指南，逐字）：
  · "To add lettering, it is best to use Helvetica or Arial (sans serif fonts).
     Keep lettering consistently sized throughout your final-sized artwork,
     usually about 2–3 mm (8–12 pt)."        → 字体 Arial；字号向 8 pt 收敛
  · "Do not include titles or captions within your illustrations."
                                             → 移除描述性面板标题，仅保留 (a)/(b) 部件标识
  · "Figure parts should be denoted by lowercase letters (a, b, c, etc.)."
  · "Figures are created at a size between 80mm and 180mm in width"
                                             → 四图统一 160 mm（本稿版心 165.1 mm 以内）
  · "Color illustrations should be submitted as RGB (8 bits per channel)."
  · "All lines should be at least 0.1 mm (0.3 pt) wide."

统一口径：
  宽度      WIDTH_IN = 160.0 mm = 6.2992 in（四图一律）
  字体      Arial（回退 Helvetica → DejaVu Sans）
  字号      面板标签 8.5 / 轴标签 8.5 / 刻度 8.0 / 数据标注 7.5 / 模块标题 9.0 / 说明文字 7.5
  dpi       600
  颜色      RGB，色盲友好（沿用原稿配色，未改）
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

# ---------- 统一尺寸 ----------
MM = 25.4
WIDTH_IN = 160.0 / MM          # 6.2992 in —— 四图公用
DPI = 600

# ---------- 统一字体与字号 ----------
FONT_STACK = ['Arial', 'Helvetica', 'Liberation Sans', 'DejaVu Sans']
FS_PANEL = 8.5      # (a) / (b) 部件标识（粗体）
FS_AXLABEL = 8.5    # xlabel / ylabel
FS_TICK = 8.0       # 刻度数字
FS_ANNOT = 7.5      # 图内数据标注（ρ、n、P、consistency）
FS_MODTITLE = 9.0   # Fig.1 模块标题
FS_BODY = 7.5       # Fig.1 模块说明文字


def apply_rcparams():
    """四图共用的 rcParams（axes 细节仍由各图脚本自行设定）。"""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': FONT_STACK,
        'font.size': FS_TICK,
        'axes.labelsize': FS_AXLABEL,
        'axes.titlesize': FS_PANEL,
        'xtick.labelsize': FS_TICK,
        'ytick.labelsize': FS_TICK,
        'legend.fontsize': FS_ANNOT,
        'axes.linewidth': 0.7,
        'axes.edgecolor': '#333333',
        'xtick.major.width': 0.7,
        'ytick.major.width': 0.7,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'none',
        # mathtext（$\\rho$、$\\Delta$ 等）必须一并走 Arial，否则 matplotlib 默认
        # 回退到 DejaVu Sans 数学字体，导致同一张图内出现两族字体（Wiley 要求字体一致）
        'mathtext.fontset': 'custom',
        'mathtext.rm': 'Arial',
        'mathtext.it': 'Arial:italic',
        'mathtext.bf': 'Arial:bold',
        'mathtext.default': 'it',
    })


def despine(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)


def panel_tag(ax, letter, fontsize=FS_PANEL, pad=4):
    """Wiley 的部件标识：小写字母，置于面板正上方居中。
    仅 (a)/(b)，不带任何描述性文字（Wiley: 图内不得有标题）。"""
    ax.set_title('(%s)' % letter, fontsize=fontsize, fontweight='bold', pad=pad)


def save(fig, path_base, dpi=DPI):
    """PDF（矢量，投稿首选）+ PNG（RGB 8-bit @600 dpi）。不用 bbox_inches='tight'，
    以保证输出物理尺寸 == figsize，便于四图宽度精确对齐。"""
    for ext in ('png', 'pdf'):
        fig.savefig(path_base + '.' + ext, dpi=dpi, transparent=False, facecolor='white')
    p = path_base + '.png'
    im = Image.open(p)
    if im.mode != 'RGB':
        im.convert('RGB').save(p, dpi=(dpi, dpi))
    plt.close(fig)


def report(path_base):
    """打印输出文件的尺寸核验信息。"""
    import os, struct
    png = path_base + '.png'
    d = open(png, 'rb').read()
    i, w, h, dpi_x = 8, None, None, None
    while i < len(d):
        ln = struct.unpack('>I', d[i:i + 4])[0]
        t = d[i + 4:i + 8]
        da = d[i + 8:i + 8 + ln]
        if t == b'IHDR':
            w, h = struct.unpack('>II', da[:8])
        elif t == b'pHYs':
            dpi_x = struct.unpack('>IIB', da)[0] * 0.0254
        elif t == b'IEND':
            break
        i += 12 + ln
    print('  %s : %dx%d px @%.0f dpi = %.2f x %.2f in = %.1f x %.1f mm'
          % (os.path.basename(png), w, h, dpi_x, w / dpi_x, h / dpi_x,
             w / dpi_x * MM, h / dpi_x * MM))

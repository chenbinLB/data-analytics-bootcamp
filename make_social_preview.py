# -*- coding: utf-8 -*-
"""
make_social_preview.py — 生成 GitHub Social Preview (1280x640)
=============================================================
用途:上传到 GitHub 仓库的 "Social preview" 设置
     分享仓库链接时,自动显示这张图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent / "promo" / "social-preview.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

# 中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ===== 画布 =====
fig, ax = plt.subplots(figsize=(12.8, 6.4), dpi=100)
ax.set_xlim(0, 1280)
ax.set_ylim(0, 640)
ax.set_aspect('equal')
ax.axis('off')

# 背景:深蓝渐变
gradient = np.linspace(0, 1, 256).reshape(-1, 1)
gradient = np.hstack([gradient] * 1280)
ax.imshow(gradient, extent=[0, 1280, 0, 640], aspect='auto',
          cmap='Blues_r', alpha=0.4, zorder=0)

# 顶部深色条
ax.add_patch(FancyBboxPatch((0, 540), 1280, 100, boxstyle="square,pad=0",
                              facecolor='#0d1b2a', edgecolor='none', zorder=1))
# 底部装饰条
ax.add_patch(FancyBboxPatch((0, 0), 1280, 60, boxstyle="square,pad=0",
                              facecolor='#0d1b2a', edgecolor='none', zorder=1))

# 装饰:散点(代码感)
np.random.seed(42)
for _ in range(60):
    x, y = np.random.uniform(0, 1280), np.random.uniform(60, 540)
    s = np.random.uniform(20, 80)
    ax.scatter([x], [y], s=s, c='#3da9fc', alpha=0.15, zorder=1)

# ===== 主标题 =====
ax.text(640, 460, '大厂数据分析师', fontsize=72, color='white',
        weight='bold', ha='center', va='center', zorder=3,
        family='Microsoft YaHei')

ax.text(640, 380, '4 周突击课', fontsize=60, color='#3da9fc',
        weight='bold', ha='center', va='center', zorder=3,
        family='Microsoft YaHei')

# 副标题
ax.text(640, 310, '15 个跑通的 Jupyter Notebook  |  真实数据集  |  零环境门槛',
        fontsize=22, color='#e0e1dd', ha='center', va='center', zorder=3,
        family='Microsoft YaHei', style='italic')

# ===== 4 周路径 =====
weeks = [
    ('W0', '预备周'),
    ('W1', 'SQL'),
    ('W2', 'Python'),
    ('W3', '统计/A/B'),
    ('W4', '求职'),
]
start_x = 200
gap = 220
y_week = 200

for i, (wk, name) in enumerate(weeks):
    x = start_x + i * gap
    # 圆圈
    circle = patches.Circle((x, y_week), 45, facecolor='#3da9fc',
                             edgecolor='white', linewidth=3, zorder=4)
    ax.add_patch(circle)
    ax.text(x, y_week, wk, fontsize=28, color='white',
            weight='bold', ha='center', va='center', zorder=5,
            family='Microsoft YaHei')
    # 名字
    ax.text(x, y_week - 80, name, fontsize=20, color='white',
            ha='center', va='center', zorder=5,
            family='Microsoft YaHei')
    # 箭头
    if i < len(weeks) - 1:
        ax.annotate('', xy=(x + gap - 45, y_week), xytext=(x + 45, y_week),
                    arrowprops=dict(arrowstyle='->', color='white', lw=2.5, alpha=0.6),
                    zorder=3)

# ===== 底部信息 =====
ax.text(40, 30, 'github.com/chenbinLB/data-analytics-bootcamp',
        fontsize=16, color='#a8dadc', va='center', family='Consolas')

ax.text(1240, 30, '49.9 元  |  MIT License  |  v1.0',
        fontsize=16, color='#a8dadc', ha='right', va='center', family='Microsoft YaHei')

# 右上角徽章
ax.add_patch(FancyBboxPatch((1080, 560), 180, 60,
                              boxstyle="round,pad=0,rounding_size=10",
                              facecolor='#06d6a0', edgecolor='white', linewidth=2, zorder=4))
ax.text(1170, 590, '180+ cells OK', fontsize=18, color='white',
        weight='bold', ha='center', va='center', zorder=5, family='Consolas')

plt.tight_layout()
plt.savefig(OUT, dpi=100, bbox_inches='tight', facecolor='#0d1b2a')
print(f"已生成: {OUT}")
print(f"尺寸: 1280x640 | 大小: {OUT.stat().st_size / 1024:.1f} KB")

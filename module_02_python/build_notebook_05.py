# -*- coding: utf-8 -*-
"""
build_notebook_05.py — module_02_python/05_visualization.ipynb
================================================================
可视化 - 优化版:所有 cell 自包含
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "05_visualization.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text if isinstance(text, list) else [text]}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text if isinstance(text, list) else [text]}


def py_run(stmt):
    setup_lines = [
        "# 自包含 setup",
        "if 'pd' not in globals():",
        "    import numpy as np",
        "    import pandas as pd",
        "    import matplotlib.pyplot as plt",
        "    import seaborn as sns",
        "    import sqlite3",
        "    from pathlib import Path",
        "    pd.set_option('display.max_columns', 30)",
        "    pd.set_option('display.width', 200)",
        "    sns.set_style('whitegrid')",
        "    plt.rcParams['figure.figsize'] = (10, 5)",
        "    plt.rcParams['font.size'] = 11",
        "    print('Setup OK')",
        "if 'conn' not in globals():",
        "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))",
        "",
    ]
    if isinstance(stmt, list):
        body = "\n".join(setup_lines) + "\n".join(stmt)
    else:
        body = "\n".join(setup_lines) + stmt
    return code(body)


# 准备 orders / users / merged 的自包含代码(头部加 if not in globals)
DATA_SETUP = [
    "if 'orders' not in globals():",
    "    orders = pd.read_sql('SELECT order_date, amount, user_id FROM orders WHERE status = \"completed\"', conn)",
    "    orders['order_date'] = pd.to_datetime(orders['order_date'])",
    "    orders = orders.set_index('order_date')",
    "if 'users' not in globals():",
    "    users = pd.read_sql('SELECT * FROM users', conn)",
]


cells = []

cells.append(md("""# W2.5 — 可视化(数据分析师的"翻译官")

> 分析师 80% 时间在分析,20% 在做图。但**会做图和做对图是两码事**。
> 本节按 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试

## 本节大纲
- **0. 原理总览**:绘图四问 + 库选型
- **1. Matplotlib 基础**(oop 风格,自包含 demo)
- **2. 8 大常用图**(合并 mega cell,自包含)
- **3. Seaborn 高级**(合并 mega cell,自包含)
- **4. Plotly 交互式**(mega cell,自包含)
- **5. 实战:电商运营仪表盘**

> 所有 cell 自包含,跳着跑任何一个都不会报错。
"""))

cells.append(py_run([
    "import numpy as np",
    "import pandas as pd",
    "import matplotlib.pyplot as plt",
    "import seaborn as sns",
    "sns.set_style('whitegrid')",
    "plt.rcParams['figure.figsize'] = (10, 5)",
    "plt.rcParams['font.size'] = 11",
    "print('OK')",
]))

# 0. 原理
cells.append(md("""## 0. 原理总览:绘图四问

### 0.1 绘图前必须回答的 4 个问题

| 问题 | 含义 |
|------|------|
| 1. 给谁看? | 受众决定复杂度(老板简单 / 数据团队细节) |
| 2. 回答什么问题? | 类型决定图(趋势→折线 / 比较→柱状) |
| 3. 用什么图? | 数据 + 问题决定图(见下表) |
| 4. 怎么配色? | 可读性 |

### 0.2 图表选择速查

| 想看... | 用图 |
|--------|------|
| 随时间变化 | **折线图** |
| 类目比较 | **柱状图** / **条形图** |
| 部分占整体 | **饼图**(< 7 类) / **堆叠柱状图** |
| 分布形状 | **直方图** / **箱线图** / **密度图** |
| 两个变量关系 | **散点图** |
| 相关性矩阵 | **热力图** |

### 0.3 Matplotlib vs Seaborn vs Plotly 选型

| 库 | 优势 | 适用 |
|----|------|------|
| **Matplotlib** | 底层、灵活、可定制 100% | 出版级图表、定制化 |
| **Seaborn** | 高级 API、美观、统计友好 | 探索性分析、快速出图 |
| **Plotly** | 交互式、网页化 | 仪表盘、给老板的演示 |

**生产铁律**:**探索用 Seaborn,展示用 Matplotlib 调细节,看板用 Plotly**。
"""))

# 1. Matplotlib 基础
cells.append(md("""## 1. Matplotlib 基础(oop 风格)

### 1.1 原理

- **pyplot 风格**(`plt.plot()`):简单但耦合
- **OOP 风格**(`fig, ax = plt.subplots()`):生产推荐,易组合子图

### 1.2 基础案例(自包含,不依赖真实数据)"""))

cells.append(py_run([
    "# 1.2.1 OOP 风格:折线 + 柱状 + 子图",
    "fig, axes = plt.subplots(2, 2, figsize=(12, 8))",
    "",
    "# 子图 1:折线",
    "axes[0, 0].plot([1, 2, 3, 4], [10, 20, 15, 30], 'o-', color='steelblue', linewidth=2, label='销售额')",
    "axes[0, 0].set_xlabel('月份')",
    "axes[0, 0].set_ylabel('销售额(万)')",
    "axes[0, 0].set_title('折线图')",
    "axes[0, 0].legend()",
    "axes[0, 0].grid(True, alpha=0.3)",
    "",
    "# 子图 2:柱状",
    "categories = ['北京', '上海', '广州', '深圳']",
    "values = [120, 95, 80, 105]",
    "bars = axes[0, 1].bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])",
    "axes[0, 1].bar_label(bars, fmt='%d')",
    "axes[0, 1].set_title('柱状图')",
    "",
    "# 子图 3:散点",
    "np.random.seed(42)",
    "axes[1, 0].scatter(np.random.randn(100), np.random.randn(100), alpha=0.6, color='green')",
    "axes[1, 0].set_title('散点图')",
    "",
    "# 子图 4:直方图",
    "axes[1, 1].hist(np.random.randn(1000), bins=30, color='purple', alpha=0.7)",
    "axes[1, 1].set_title('直方图')",
    "",
    "fig.suptitle('2x2 子图组合', fontsize=14, fontweight='bold')",
    "plt.tight_layout()",
    "plt.show()",
]))

cells.append(md("""### 1.3 面试题

- Q1: pyplot vs OOP 风格?
  A: 生产用 OOP(`fig, ax = plt.subplots()`),易组合子图。
- Q2: 怎么避免中文乱码?
  A: `plt.rcParams['font.sans-serif'] = ['SimHei']`(Win)/ `['PingFang SC']`(Mac),`plt.rcParams['axes.unicode_minus'] = False`。
"""))

# 2. 8 大常用图 (mega cell)
cells.append(md("""## 2. 8 大常用图(mega cell,自包含)

所有 8 个图都基于真实订单数据,在同一个 cell 内完成。"""))

cells.append(py_run(DATA_SETUP + [
    "print('=' * 60)",
    "print('8 大常用图(自包含)')",
    "print('=' * 60)",
    "",
    "fig = plt.figure(figsize=(18, 12))",
    "",
    "# 2.1 折线图(趋势)",
    "ax1 = plt.subplot(3, 3, 1)",
    "daily = orders.resample('D').sum()",
    "ax1.plot(daily.index, daily['amount'], color='steelblue', linewidth=1)",
    "ax1.plot(daily.index, daily['amount'].rolling('7D').mean(), color='red', linewidth=2, label='7日 MA')",
    "ax1.set_title('2.1 折线图(GMV 趋势)')",
    "ax1.legend(fontsize=8)",
    "ax1.grid(True, alpha=0.3)",
    "",
    "# 2.2 柱状图(类目比较)",
    "ax2 = plt.subplot(3, 3, 2)",
    "merged_ch = orders.merge(users[['user_id', 'channel']], on='user_id', how='left')",
    "channel_gmv = merged_ch.groupby('channel')['amount'].sum().sort_values(ascending=False)",
    "bars = ax2.bar(channel_gmv.index, channel_gmv.values, color='#4ECDC4')",
    "ax2.bar_label(bars, fmt='%.0f', fontsize=8)",
    "ax2.set_title('2.2 柱状图(各渠道 GMV)')",
    "ax2.tick_params(axis='x', rotation=30)",
    "",
    "# 2.3 直方图(分布)",
    "ax3 = plt.subplot(3, 3, 3)",
    "ax3.hist(orders['amount'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)",
    "ax3.axvline(orders['amount'].mean(), color='red', linestyle='--', label=f'均值 {orders[\"amount\"].mean():.0f}')",
    "ax3.set_title('2.3 直方图(订单金额分布)')",
    "ax3.legend(fontsize=8)",
    "",
    "# 2.4 散点图(关系)",
    "ax4 = plt.subplot(3, 3, 4)",
    "np.random.seed(42)",
    "ad_spend = np.random.uniform(0, 100, 200)",
    "sales = 2 * ad_spend + np.random.normal(0, 30, 200) + 50",
    "ax4.scatter(ad_spend, sales, alpha=0.5, color='coral')",
    "ax4.set_xlabel('广告费(千)')",
    "ax4.set_title('2.4 散点图(广告费 vs 销售)')",
    "",
    "# 2.5 箱线图(分布对比)",
    "ax5 = plt.subplot(3, 3, 5)",
    "channels = merged_ch['channel'].unique()[:4]",
    "data_by_ch = [merged_ch[merged_ch['channel'] == c]['amount'].values for c in channels]",
    "bp = ax5.boxplot(data_by_ch, labels=channels, patch_artist=True)",
    "for patch, color in zip(bp['boxes'], ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']):",
    "    patch.set_facecolor(color)",
    "ax5.set_title('2.5 箱线图(各渠道订单金额)')",
    "ax5.tick_params(axis='x', rotation=30)",
    "",
    "# 2.6 饼图(占比)",
    "ax6 = plt.subplot(3, 3, 6)",
    "city_dist = users['city'].value_counts().head(5)",
    "colors = plt.cm.Set3(np.arange(len(city_dist)))",
    "ax6.pie(city_dist, labels=city_dist.index, autopct='%1.1f%%', colors=colors, startangle=90)",
    "ax6.set_title('2.6 饼图(城市分布)')",
    "",
    "# 2.7 热力图(交叉表)",
    "ax7 = plt.subplot(3, 3, 7)",
    "merged_full = orders.merge(users[['user_id', 'channel', 'age_group']], on='user_id', how='left')",
    "ct = pd.crosstab(merged_full['channel'], merged_full['age_group'])",
    "sns.heatmap(ct, annot=True, fmt='d', cmap='YlOrRd', ax=ax7, cbar=False)",
    "ax7.set_title('2.7 热力图(渠道 × 年龄)')",
    "",
    "# 2.8 漏斗图(转化)",
    "ax8 = plt.subplot(3, 3, 8)",
    "events = pd.read_sql('SELECT * FROM user_events', conn)",
    "funnel = events.groupby('event_type')['user_id'].nunique().sort_values(ascending=False)",
    "y_pos = np.arange(len(funnel))",
    "bars = ax8.barh(y_pos, funnel.values, color='#4ECDC4')",
    "ax8.set_yticks(y_pos)",
    "ax8.set_yticklabels(funnel.index)",
    "ax8.invert_yaxis()",
    "ax8.bar_label(bars, fmt='%d', padding=5, fontsize=8)",
    "ax8.set_title('2.8 漏斗图(行为转化)')",
    "",
    "fig.delaxes(plt.subplot(3, 3, 9))  # 删除第 9 个空子图",
    "fig.suptitle('8 大常用图', fontsize=16, fontweight='bold')",
    "plt.tight_layout()",
    "plt.show()",
]))

# 3. Seaborn
cells.append(md("""## 3. Seaborn 高级(mega cell,自包含)"""))

cells.append(py_run(DATA_SETUP + [
    "print('=' * 60)",
    "print('Seaborn 高级图')",
    "print('=' * 60)",
    "",
    "merged = orders.merge(users[['user_id', 'channel', 'age_group']], on='user_id', how='left')",
    "",
    "fig, axes = plt.subplots(2, 2, figsize=(14, 10))",
    "",
    "# 3.1 histplot(直方图 + KDE)",
    "sns.histplot(data=orders, x='amount', bins=50, kde=True, ax=axes[0, 0], color='steelblue')",
    "axes[0, 0].set_title('3.1 订单金额分布(直方图 + KDE)')",
    "axes[0, 0].set_xlim(0, 3000)",
    "",
    "# 3.2 kdeplot(密度图对比)",
    "sns.kdeplot(data=merged, x='amount', hue='channel', ax=axes[0, 1], fill=True, alpha=0.5)",
    "axes[0, 1].set_title('3.2 各渠道订单金额密度图')",
    "axes[0, 1].set_xlim(0, 3000)",
    "",
    "# 3.3 boxplot(箱线图对比)",
    "sns.boxplot(data=merged, y='channel', x='amount', ax=axes[1, 0], palette='Set2')",
    "axes[1, 0].set_title('3.3 各渠道订单金额箱线图')",
    "axes[1, 0].set_xlim(0, 3000)",
    "",
    "# 3.4 violinplot(小提琴图 - 展示分布密度)",
    "sns.violinplot(data=merged, y='channel', x='amount', ax=axes[1, 1], palette='Set2')",
    "axes[1, 1].set_title('3.4 各渠道订单金额小提琴图')",
    "axes[1, 1].set_xlim(0, 3000)",
    "",
    "fig.suptitle('Seaborn 高级图', fontsize=16, fontweight='bold')",
    "plt.tight_layout()",
    "plt.show()",
]))

# 4. Plotly
cells.append(md("""## 4. Plotly 交互式(mega cell,自包含)"""))

cells.append(py_run(DATA_SETUP + [
    "print('=' * 60)",
    "print('Plotly 交互式')",
    "print('=' * 60)",
    "",
    "import plotly.express as px",
    "",
    "# 4.1 折线图(交互式)",
    "daily = orders.resample('D').sum()",
    "fig = px.line(",
    "    daily.reset_index(),",
    "    x='order_date',",
    "    y='amount',",
    "    title='4.1 每日 GMV(交互式折线)',",
    "    labels={'order_date': '日期', 'amount': 'GMV'}",
    ")",
    "fig.show()",
    "",
    "print('\\n(注意:Plotly 图在 Jupyter / PyCharm 会弹出交互窗口或嵌入显示)')",
]))

# 5. 实战仪表盘
cells.append(md("""## 5. 实战:电商运营仪表盘(4 张图,mega cell)"""))

cells.append(py_run(DATA_SETUP + [
    "print('=' * 60)",
    "print('电商运营仪表盘')",
    "print('=' * 60)",
    "",
    "fig, axes = plt.subplots(2, 2, figsize=(14, 10))",
    "",
    "# 图 1:GMV 趋势",
    "daily = orders.resample('D').sum()",
    "axes[0, 0].plot(daily.index, daily['amount'], alpha=0.5, label='每日')",
    "axes[0, 0].plot(daily.index, daily['amount'].rolling('7D').mean(), color='red', linewidth=2, label='7日 MA')",
    "axes[0, 0].set_title('每日 GMV 趋势')",
    "axes[0, 0].legend()",
    "axes[0, 0].grid(True, alpha=0.3)",
    "",
    "# 图 2:各渠道 GMV",
    "merged = orders.merge(users[['user_id', 'channel']], on='user_id', how='left')",
    "channel_gmv = merged.groupby('channel')['amount'].sum().sort_values(ascending=False)",
    "axes[0, 1].bar(channel_gmv.index, channel_gmv.values, color='#4ECDC4')",
    "axes[0, 1].set_title('各渠道 GMV')",
    "axes[0, 1].tick_params(axis='x', rotation=30)",
    "",
    "# 图 3:订单金额分布",
    "axes[1, 0].hist(orders['amount'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')",
    "axes[1, 0].axvline(orders['amount'].mean(), color='red', linestyle='--', label=f'均值 {orders[\"amount\"].mean():.0f}')",
    "axes[1, 0].axvline(orders['amount'].median(), color='green', linestyle='--', label=f'中位数 {orders[\"amount\"].median():.0f}')",
    "axes[1, 0].set_title('订单金额分布')",
    "axes[1, 0].legend()",
    "",
    "# 图 4:周内效应(用 orders 自己的 datetime 索引)",
    "orders['weekday'] = orders.index.dayofweek",
    "data_by_day = [orders[orders['weekday'] == d]['amount'].values for d in range(7)]",
    "labels = ['一', '二', '三', '四', '五', '六', '日']",
    "bp = axes[1, 1].boxplot(data_by_day, labels=labels, patch_artist=True)",
    "for patch in bp['boxes']:",
    "    patch.set_facecolor('#45B7D1')",
    "axes[1, 1].set_title('订单金额周内分布')",
    "axes[1, 1].set_xlabel('星期')",
    "axes[1, 1].set_ylabel('金额')",
    "",
    "fig.suptitle('电商运营仪表盘', fontsize=16, fontweight='bold')",
    "plt.tight_layout()",
    "plt.show()",
]))

cells.append(md("""## 6. 小结

### 速查表

| 需求 | 库 + 图 |
|------|---------|
| 趋势 | Matplotlib `plot` / Seaborn `lineplot` / Plotly `line` |
| 比较 | `bar` / `barh` / `barplot` |
| 分布 | `hist` / `histplot` / `boxplot` / `violinplot` |
| 关系 | `scatter` / `pairplot` / `heatmap` |
| 占比 | `pie`(< 7 类) / `barh` |
| 子图 | `plt.subplots(2, 2)` |
| 交互式 | Plotly Express |

### 自测清单

- [ ] 能用 Matplotlib OOP 风格出折线/柱状/散点
- [ ] 能用 Seaborn 出分布图、分类图
- [ ] 能选对图表回答业务问题
- [ ] 能做 2x2 子图组合
- [ ] 能调配色 + 标签 + 图例

**全部 ✅ 之后推进 W2.6(综合实战)或 W3(统计 + A/B 测试)。**
"""))


nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"已生成: {OUT}")
print(f"Cell 总数: {len(cells)}")
print(f"文件大小: {OUT.stat().st_size / 1024:.1f} KB")

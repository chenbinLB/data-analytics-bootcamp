# -*- coding: utf-8 -*-
"""
build_notebook_01.py — module_03_stats/01_stats_basics.ipynb (v2 精简版)
================================================================
统计基础:全部塞到 mega cell 里,避免跨依赖
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "01_stats_basics.ipynb"


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
        "    from scipy import stats",
        "    import sqlite3",
        "    from pathlib import Path",
        "    pd.set_option('display.max_columns', 30)",
        "    pd.set_option('display.width', 200)",
        "    sns.set_style('whitegrid')",
        "    plt.rcParams['figure.figsize'] = (10, 5)",
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


def data_setup():
    """订单和用户的自包含 setup"""
    return [
        "if 'orders' not in globals():",
        "    orders = pd.read_sql('SELECT amount, order_date, user_id, status FROM orders', conn)",
        "    orders_completed = orders[orders['status'] == 'completed'].copy()",
        "    orders_completed['order_date'] = pd.to_datetime(orders_completed['order_date'])",
        "    orders = orders_completed.set_index('order_date')",
        "if 'users' not in globals():",
        "    users = pd.read_sql('SELECT * FROM users', conn)",
    ]


cells = []

cells.append(md("""# W3.1 — 统计学基础(数据分析师的"内功心法")

> 大厂面试必问:统计基础 + 假设检验。业务再花哨,统计不扎实就漏。
> 本节按 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试

## 本节大纲
- **0. 原理总览**:为什么数据分析师必须懂统计
- **1. 描述统计**(均值 / 中位数 / 方差 / 分位数)
- **2. 概率分布**(正态 / 泊松 / 伯努利)
- **3. 假设检验**(t 检验 / 卡方 / p 值 / 置信区间)
- **4. 实战:用统计找异常值 + 对比差异**

> 所有 cell 都自包含,跳着跑任何一个都不会报错。
"""))

cells.append(py_run([
    "import numpy as np",
    "import pandas as pd",
    "import matplotlib.pyplot as plt",
    "import seaborn as sns",
    "from scipy import stats",
    "print('OK')",
]))

# 0. 原理
cells.append(md("""## 0. 原理总览

### 0.1 统计在数据分析师的 5 大应用

1. A/B 测试:判断"新版本比旧版本好"是真实差异还是偶然
2. 异动归因:DAU 突然下降 20%,是产品 bug 还是正常波动
3. 异常检测:哪些订单是异常(基于统计分布)
4. 预测建模:回归、分类、聚类(底层都是统计)
5. 报告呈现:用置信区间 / p 值让结论更严谨

### 0.2 核心统计概念速查

| 概念 | 含义 |
|------|------|
| 均值 μ | 数据中心 |
| 方差 σ² / 标准差 σ | 数据离散度 |
| p 值 | 原假设成立时,看到当前/更极端数据的概率 |
| 置信区间 | 真实值的可信范围(95% 置信) |
| Type I 错误 | 假阳性(误报) |
| Type II 错误 | 假阴性(漏报) |

### 0.3 大厂铁律

- p < 0.05 是门槛,不是真理
- 样本量越大,统计越显著
- 业务效果大小更重要
- 先看分布,再选检验
"""))

# 1 + 2 + 3 + 4 全部合并到 mega cell
cells.append(md("""## 1-4. 完整流程(mega cell)

把所有内容合并到一个 cell,内部按章节分块。"""))

cells.append(py_run(data_setup() + [
    "print('=' * 60)",
    "print('1. 描述统计')",
    "print('=' * 60)",
    "amounts = orders['amount']",
    "print('订单金额描述统计:')",
    "print(amounts.describe().round(2))",
    "print(f'\\n偏度: {amounts.skew():.2f}(> 0 右偏)')",
    "print(f'峰度: {amounts.kurtosis():.2f}')",
    "print(f'5% 截尾均值: {stats.trim_mean(amounts, 0.05):.2f}')",
    "",
    "print('\\n' + '=' * 60)",
    "print('2. 异常值检测(IQR / Z-score / MAD 三种方法)')",
    "print('=' * 60)",
    "Q1, Q3 = amounts.quantile(0.25), amounts.quantile(0.75)",
    "IQR = Q3 - Q1",
    "outliers_iqr = amounts[(amounts < Q1 - 1.5*IQR) | (amounts > Q3 + 1.5*IQR)]",
    "z_scores = np.abs((amounts - amounts.mean()) / amounts.std())",
    "outliers_z = amounts[z_scores > 3]",
    "mad = np.abs(amounts - amounts.median()).median()",
    "modified_z = 0.6745 * (amounts - amounts.median()) / mad",
    "outliers_mad = amounts[np.abs(modified_z) > 3.5]",
    "print(f'IQR 异常值: {len(outliers_iqr)}({len(outliers_iqr)/len(amounts)*100:.1f}%)')",
    "print(f'Z-score 异常值: {len(outliers_z)}({len(outliers_z)/len(amounts)*100:.2f}%)')",
    "print(f'MAD 异常值: {len(outliers_mad)}({len(outliers_mad)/len(amounts)*100:.2f}%)')",
    "",
    "print('\\n' + '=' * 60)",
    "print('3. 概率分布 + 95% 置信区间')",
    "print('=' * 60)",
    "n = len(amounts)",
    "mean = amounts.mean()",
    "se = amounts.std() / np.sqrt(n)",
    "ci_low, ci_high = stats.norm.interval(0.95, loc=mean, scale=se)",
    "print(f'样本量: {n}')",
    "print(f'均值: {mean:.2f}')",
    "print(f'95% 置信区间: [{ci_low:.2f}, {ci_high:.2f}]')",
    "",
    "print('\\n' + '=' * 60)",
    "print('4. 假设检验(A/B 两组对比)')",
    "print('=' * 60)",
    "merged = orders.merge(users[['user_id', 'channel']], on='user_id', how='left')",
    "organic = merged[merged['channel'] == 'organic']['amount']",
    "paid = merged[merged['channel'] == 'paid']['amount']",
    "print(f'Organic: n={len(organic)}, 均值={organic.mean():.2f}')",
    "print(f'Paid: n={len(paid)}, 均值={paid.mean():.2f}')",
    "t_stat, p_value = stats.ttest_ind(organic, paid, equal_var=False)",
    "print(f'\\nt 检验(Welch\\'s): t={t_stat:.3f}, p={p_value:.4f}')",
    "print(f'结论(α=0.05): {\"显著差异\" if p_value < 0.05 else \"无显著差异\"}')",
    "",
    "# 非参数检验(数据不服从正态时)",
    "u_stat, p_mw = stats.mannwhitneyu(organic, paid, alternative='two-sided')",
    "print(f'Mann-Whitney U: U={u_stat:.2f}, p={p_mw:.4f}')",
    "",
    "print('\\n' + '=' * 60)",
    "print('5. ANOVA(多组对比) + 卡方(类别独立性)')",
    "print('=' * 60)",
    "groups = [merged[merged['channel'] == ch]['amount'].values for ch in merged['channel'].unique()]",
    "f_stat, p_anova = stats.f_oneway(*groups)",
    "print(f'ANOVA: F={f_stat:.2f}, p={p_anova:.4f}')",
    "print(f'结论: {\"各渠道均值有显著差异\" if p_anova < 0.05 else \"无显著差异\"}')",
    "",
    "buyers = orders.reset_index()['user_id'].unique()  # 简化",
    "users['is_buyer'] = users['user_id'].isin(buyers).astype(int)",
    "ct = pd.crosstab(users['channel'], users['is_buyer'])",
    "chi2, p_chi, dof, _ = stats.chi2_contingency(ct)",
    "print(f'\\n卡方检验: chi2={chi2:.2f}, p={p_chi:.4f}')",
    "print(f'结论: {\"渠道与购买独立\" if p_chi >= 0.05 else \"渠道与购买不独立\"}')",
]))

cells.append(md("""## 5. 小结

### 速查表

| 场景 | 检验方法 | 函数 |
|------|---------|------|
| 1 组均值 vs 常数 | 单样本 t | `stats.ttest_1samp` |
| 2 组均值 | 独立 t | `stats.ttest_ind` |
| 2 组非正态 | Mann-Whitney | `stats.mannwhitneyu` |
| 3+ 组均值 | ANOVA | `stats.f_oneway` |
| 类别独立性 | 卡方 | `stats.chi2_contingency` |
| 正态性 | D'Agostino | `stats.normaltest` |
| 95% 置信区间 | Norm.interval | `stats.norm.interval(0.95)` |

### 自测清单

- [ ] 能区分均值/中位数/众数
- [ ] 能用 IQR / Z-score / MAD 检测异常
- [ ] 能说出正态/泊松/伯努利分布的业务场景
- [ ] 能用 t 检验 / 卡方 / ANOVA
- [ ] 知道 p 值的真实含义
- [ ] 知道什么时候用非参数检验

**全部 ✅ 之后推进 W3.2(A/B 测试设计 + 实现)。**
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

# -*- coding: utf-8 -*-
"""
build_notebook_04.py — module_02_python/04_timeseries.ipynb
================================================================
时间序列:to_datetime / 索引 / resample / rolling / shift / diff
已优化:所有 cell 自包含,跳着跑也不会 NameError
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "04_timeseries.ipynb"


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
        "    import sqlite3",
        "    from pathlib import Path",
        "    pd.set_option('display.max_columns', 30)",
        "    pd.set_option('display.width', 200)",
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


def ensure_orders():
    """返回 orders 的自包含准备代码(每个 cell 头部都加)"""
    return [
        "# 自包含:准备 orders 时间序列数据",
        "if 'orders' not in globals():",
        "    orders = pd.read_sql('SELECT order_date, amount, user_id FROM orders WHERE status = \"completed\"', conn)",
        "    orders['order_date'] = pd.to_datetime(orders['order_date'])",
        "    orders = orders.set_index('order_date')",
    ]


cells = []

cells.append(md("""# W2.4 — 时间序列(电商 / 金融 / 运营的核心技能)

> 80% 的业务数据都有时间维度,时间序列分析是数据分析师必会。
> 本节按 5 段结构讲透:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试

## 本节大纲
- **0. 原理总览**:时间序列跟普通数据的区别
- **1. to_datetime + 时间索引**(基础)
- **2. resample + rolling + shift**(mega cell,综合)
- **3. 实战:GMV 时间序列分析**(mega cell)

> **重要**:所有 cell 都自包含,跳着跑任何一个都不会报错。
"""))

cells.append(py_run([
    "import numpy as np",
    "import pandas as pd",
    "print('Pandas version:', pd.__version__)",
]))

# 0. 原理
cells.append(md("""## 0. 原理总览:时间序列的核心

### 0.1 跟普通数据的区别

| 维度 | 普通数据 | 时间序列 |
|------|---------|---------|
| 索引 | 默认 0..N-1 | **时间戳**(DatetimeIndex) |
| 查询 | 按位置/标签 | 按时间区间(`.loc['2025-02']`) |
| 聚合 | 按列 | 按时间粒度(天/周/月) |
| 计算 | 简单加减 | 累计/同比/环比/滚动 |
| 可视化 | 直方图/散点 | **折线图**(核心) |

### 0.2 大厂时间序列分析的 5 大操作

1. **重采样**(`resample`):按天/周/月汇总(降采样)或插值(升采样)
2. **滚动计算**(`rolling`):滑动窗口(7 日移动平均、30 日 GMV)
3. **差分**(`diff` / `pct_change`):算环比 / 同比
4. **平移**(`shift`):看上一期 / 下一期
5. **时区**(`tz_localize` / `tz_convert`):跨时区业务(美东 / 港股)

### 0.3 实战铁律

- 时间列必须用 `pd.to_datetime` 转,不要用字符串
- 设置时间索引:`df.set_index('date')` 之后才能用 resample / rolling
- 时区一致:统一用 UTC 存储,展示时转本地时区
- 补齐缺失日:业务上"今天"如果没数据,要用 `reindex` 补 0
"""))

# 1. to_datetime + 索引
cells.append(md("""## 1. to_datetime + 时间索引(自包含基础)

### 1.1 原理

- `pd.to_datetime(s)`:字符串/数值/混合 → datetime64
- `df.set_index('col')`:把列设为索引(时间序列必备)
- `df.index` 类型变成 `DatetimeIndex`,支持 `.year` / `.month` / `.day` / `.weekday` 等访问器

### 1.2 基础案例:各种格式转换 + 时间索引 + 访问器 + 时间切片"""))

cells.append(py_run([
    "# 1.2.1 字符串 -> datetime(Pandas 2.x 严格模式,需要 format='mixed')",
    "s = pd.Series(['2025-01-15', '2025/02/20', '15-Mar-2025', '20250325'])",
    "print('原:')",
    "print(s.tolist())",
    "print('\\n转 datetime(format=mixed 混合格式):')",
    "print(pd.to_datetime(s, format='mixed').tolist())",
    "",
    "# 1.2.2 Unix 时间戳",
    "timestamps = pd.Series([1700000000, 1700100000, 1700200000])",
    "print('\\nUnix 时间戳转 datetime:')",
    "print(pd.to_datetime(timestamps, unit='s').tolist())",
    "",
    "# 1.2.3 自定义格式(更快更准)",
    "s2 = pd.Series(['15/01/2025', '20/02/2025'])",
    "print('\\n自定义格式(DD/MM/YYYY):')",
    "print(pd.to_datetime(s2, format='%d/%m/%Y').tolist())",
]))

cells.append(py_run([
    "# 1.2.4 设时间索引 + 访问器 + 时间切片",
    "df = pd.DataFrame({",
    "    'date': pd.date_range('2025-01-01', periods=10, freq='D'),",
    "    'value': range(10)",
    "})",
    "df = df.set_index('date')",
    "print('设置时间索引后:')",
    "print(df.head(3))",
    "print('\\n索引 dtype:', df.index.dtype)",
    "",
    "# 时间访问器",
    "df['year'] = df.index.year",
    "df['month'] = df.index.month",
    "df['weekday'] = df.index.day_name()",
    "df['is_weekend'] = df.index.dayofweek >= 5",
    "print('\\n加时间特征:')",
    "print(df.head(3))",
    "",
    "# 时间切片",
    "print('\\n2025-01-03 之后:')",
    "print(df.loc['2025-01-03':].head(2))",
    "print('\\n1 月份数据:')",
    "print(df.loc['2025-01'].head(2))",
]))

cells.append(md("""### 1.3 陷阱 + 面试

**陷阱 1**:时间格式不一致导致推断失败
```python
pd.to_datetime(['01/15/2025', '02/20/2025'])  # 推断成 MM/DD/YYYY(美国格式)
# 解决:显式 format='%d/%m/%Y'
```

**陷阱 2**:DatetimeIndex 不能直接用 `==` 比较字符串
```python
df.loc[df.index == '2025-01-15']  # 可能错
df.loc[df.index == pd.Timestamp('2025-01-15')]  # 对
```

**面试**:
- Q1: 时间序列为啥要设索引?
  A: 设了才能用 resample / rolling / 时间切片,代码更简洁且性能更好。
- Q2: 怎么处理跨时区数据?
  A: 存储用 UTC,展示用本地时区(`tz_localize('UTC').tz_convert('Asia/Shanghai')`)。
"""))

# 2-3. mega cell: resample + rolling + shift
cells.append(md("""## 2-3. resample + rolling + shift(diffs)(mega cell)

本节合并到一个 mega cell,避免跨 cell 依赖(每个函数一个 demo,内部自包含)。"""))

cells.append(py_run(ensure_orders() + [
    "# ===== 2.1 resample(重采样) =====",
    "print('=' * 60)",
    "print('2.1 resample')",
    "print('=' * 60)",
    "daily = orders.resample('D').sum()",
    "weekly = orders.resample('W').sum()",
    "monthly = orders.resample('M').sum()",
    "print('按日 / 周 / 月 GMV:')",
    "print(f'  日均: {daily[\"amount\"].mean():.0f}')",
    "print(f'  周均: {weekly[\"amount\"].mean():.0f}')",
    "print(f'  月均: {monthly[\"amount\"].mean():.0f}')",
    "",
    "# 多聚合函数",
    "result = orders.resample('D').agg(",
    "    gmv=('amount', 'sum'),",
    "    order_cnt=('amount', 'count'),",
    "    avg_order=('amount', 'mean')",
    ").round(2)",
    "print('\\n每日多指标(前 5 天):')",
    "print(result.head())",
    "",
    "# 补齐缺失日",
    "daily_full = orders.resample('D').sum().asfreq('D', fill_value=0)",
    "print(f'\\n补齐缺失日后: {len(daily_full)} 天(原 {len(daily)} 天)')",
    "",
    "# ===== 2.2 rolling(滚动计算) =====",
    "print('\\n' + '=' * 60)",
    "print('2.2 rolling')",
    "print('=' * 60)",
    "daily['ma3'] = daily['amount'].rolling(3).mean()",
    "daily['ma7'] = daily['amount'].rolling(7, min_periods=1).mean()",
    "daily['ma30'] = daily['amount'].rolling(30, min_periods=1).mean()",
    "print('移动平均(前 5 天):')",
    "print(daily[['amount', 'ma3', 'ma7', 'ma30']].head().round(0))",
    "",
    "# 时间窗口(更准)",
    "daily['ma7d'] = daily['amount'].rolling('7D').mean()",
    "daily['gmv_30d'] = daily['amount'].rolling('30D').sum()",
    "print('\\n时间窗口(后 5 天):')",
    "print(daily[['amount', 'ma7d', 'gmv_30d']].tail().round(0))",
    "",
    "# 滚动波动率",
    "daily['vol_7d'] = daily['amount'].rolling(7).std()",
    "print('\\n波动率(后 5 天):')",
    "print(daily[['amount', 'ma7', 'vol_7d']].tail().round(0))",
    "",
    "# 异常点检测",
    "threshold = 2",
    "anomalies = daily[daily['amount'] > daily['ma7'] + threshold * daily['vol_7d']]",
    "print(f'\\n异常点(>{threshold}σ,共 {len(anomalies)} 天):')",
    "if len(anomalies) > 0:",
    "    print(anomalies[['amount', 'ma7']].head())",
    "",
    "# ===== 2.3 shift + diff + pct_change =====",
    "print('\\n' + '=' * 60)",
    "print('2.3 shift + diff + pct_change')",
    "print('=' * 60)",
    "daily['prev'] = daily['amount'].shift(1)",
    "daily['diff_1d'] = daily['amount'].diff(1)",
    "daily['pct_1d'] = daily['amount'].pct_change(1) * 100",
    "daily['wow_pct'] = daily['amount'].pct_change(7) * 100",
    "print('差分 / 同比(后 5 天):')",
    "print(daily[['amount', 'prev', 'diff_1d', 'pct_1d', 'wow_pct']].tail().round(2))",
]))

cells.append(md("""### 2-3 节陷阱 + 面试

**陷阱 1**:resample 后的索引是右闭合
```python
orders.resample('W', label='left', closed='left').sum()  # 改用左闭合
```

**陷阱 2**:rolling 后的前 N-1 个是 NaN
```python
df['col'].rolling(7, min_periods=1).mean()  # min_periods 解决
```

**陷阱 3**:固定窗口 vs 时间窗口
- `rolling(7)`:7 个数据(可能跨 7 天或 2 天)
- `rolling('7D')`:7 天的数据(精确时间窗口,业务更准)

**面试**:
- Q1: 7 日 MA vs 30 日 MA?
  A: 日活级别选 7 日,周级别选 30 日。看业务粒度。
- Q2: 同比 / 环比 区别?
  A: 环比 = 上一期;同比 = 去年同期。
- Q3: 异常点检测用什么方法?
  A: 滚动 MA + 2σ / 3σ,或季节性分解(STL) + 残差分析。
"""))

# 4. 综合实战
cells.append(md("""## 4. 综合实战:GMV 时间序列完整分析

把上面所有方法组合,做一份完整的"运营周报"分析。"""))

cells.append(py_run(ensure_orders() + [
    "print('=' * 60)",
    "print('GMV 时间序列完整分析')",
    "print('=' * 60)",
    "",
    "# Step 1:补齐缺失日 + 基础汇总",
    "daily = orders.resample('D').sum().asfreq('D', fill_value=0)",
    "print(f'时间范围: {daily.index.min().date()} ~ {daily.index.max().date()}({len(daily)} 天)')",
    "print(f'总 GMV: {daily[\"amount\"].sum():.0f}')",
    "print(f'日均 GMV: {daily[\"amount\"].mean():.0f}')",
    "print(f'最高单日: {daily[\"amount\"].max():.0f}({daily[\"amount\"].idxmax().date()})')",
    "",
    "# Step 2:加各种时间序列特征",
    "daily['day_of_week'] = daily.index.dayofweek",
    "daily['is_weekend'] = daily['day_of_week'] >= 5",
    "daily['ma7'] = daily['amount'].rolling('7D', min_periods=1).mean()",
    "daily['ma30'] = daily['amount'].rolling('30D', min_periods=1).mean()",
    "daily['cumsum'] = daily['amount'].cumsum()",
    "daily['mom_pct'] = daily['amount'].pct_change(1) * 100",
    "daily['wow_pct'] = daily['amount'].pct_change(7) * 100",
    "daily['vol_7d'] = daily['amount'].rolling(7).std()",
    "",
    "print('\\n汇总指标:')",
    "print(daily[['amount', 'ma7', 'ma30', 'cumsum']].iloc[[0, 30, 60, -1]].round(0))",
    "",
    "# Step 3:周内效应(看工作日 vs 周末)",
    "weekday_stats = daily.groupby('day_of_week').agg(",
    "    gmv=('amount', 'sum'),",
    "    avg_gmv=('amount', 'mean'),",
    "    days=('amount', 'count')",
    ").round(0)",
    "weekday_stats.index = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']",
    "print('\\n周内效应:')",
    "print(weekday_stats)",
    "",
    "# Step 4:异常点",
    "daily['upper'] = daily['ma7'] + 2 * daily['vol_7d']",
    "anomalies = daily[daily['amount'] > daily['upper']]",
    "print(f'\\n异常点(>2σ): {len(anomalies)} 天')",
    "if len(anomalies) > 0:",
    "    print(anomalies[['amount', 'ma7', 'upper']].head())",
    "",
    "# Step 5:最近趋势(后 14 天)",
    "print('\\n最近 14 天趋势:')",
    "print(daily[['amount', 'ma7', 'mom_pct', 'wow_pct']].tail(14).round(0))",
]))

cells.append(md("""## 5. 小结

### 速查表

| 需求 | 写法 |
|------|------|
| 转 datetime | `pd.to_datetime(s, format=..., errors='coerce')` |
| 设时间索引 | `df.set_index('date')` |
| 选时间区间 | `df.loc['2025-02']` / `df.loc['2025-01':'2025-03']` |
| 重采样 | `df.resample('W'/'M'/'D').sum()` |
| 多聚合 | `df.resample('D').agg(gmv=('col', 'sum'), ...)` |
| 补齐缺失日 | `.asfreq('D', fill_value=0)` |
| 移动平均 | `df['col'].rolling('7D').mean()` |
| 移动标准差 | `df['col'].rolling('7D').std()` |
| 上一期 | `df['col'].shift(1)` |
| 差分 | `df['col'].diff(1)` |
| 百分比变化 | `df['col'].pct_change(1)` |
| 时区 | `df.tz_localize('UTC').tz_convert('Asia/Shanghai')` |

### 自测清单

- [ ] 能用 to_datetime 处理各种格式字符串
- [ ] 能用 resample 按天/周/月汇总
- [ ] 能用 rolling 算 7 日 / 30 日移动平均
- [ ] 能用 pct_change 算环比 / 同比
- [ ] 能用 asfreq 补齐缺失日
- [ ] 能用滚动 MA + σ 检测异常

**全部 ✅ 之后推进 W2.5(可视化)。**
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

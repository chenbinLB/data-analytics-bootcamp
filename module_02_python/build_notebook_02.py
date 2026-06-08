# -*- coding: utf-8 -*-
"""
build_notebook_02.py — module_02_python/02_pandas_basics.ipynb
================================================================
Pandas 基础:Series / DataFrame / 索引 / 选择 / 增删改查
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "02_pandas_basics.ipynb"


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
        "    print('Connected ->', conn)",
        "",
    ]
    if isinstance(stmt, list):
        body = "\n".join(setup_lines) + "\n".join(stmt)
    else:
        body = "\n".join(setup_lines) + stmt
    return code(body)


cells = []

# 标题
cells.append(md("""# W2.2 — Pandas 基础(数据分析主力)

> Pandas 是 Python 数据分析的**核心工具**。本节按 5 段结构讲透基础。

## 本节大纲
- **0. 原理总览**:Pandas 为什么快?跟 NumPy / Excel 的关系
- **1. Series + DataFrame**:两种核心数据结构
- **2. 索引(.loc / .iloc)**:两种核心选择方式
- **3. 增删改查 + 排序 + 描述统计**
- **4. 实战**:加载电商数据 + 5 个基本分析

## 学习建议
- 把每个 .loc / .iloc 例子都跑一下,看输出
- 重点掌握"链式操作"和"向量化函数"
"""))

cells.append(py_run([
    "import numpy as np",
    "import pandas as pd",
    "print('Pandas version:', pd.__version__)",
]))

# 0. 原理
cells.append(md("""## 0. 原理总览:Pandas 为什么快?

### 0.1 三层架构

```
DataFrame     (表,行+列+索引,业务视角)
    |
    ↓ 用列存
Series        (一列带索引,类似 dict)
    |
    ↓ 用 ndarray 存
NumPy ndarray (C 数组,快)
```

### 0.2 关键设计

- **行/列都有索引**:像 SQL 表的 primary key,但更灵活
- **向量化运算**:`df['col'] * 2` 跟 SQL `SELECT col * 2 FROM t` 一样
- **缺失值友好**:内置 NaN,跟 R 一致
- **I/O 强**:CSV / Excel / SQL / Parquet / JSON 全支持

### 0.3 跟 NumPy / Excel 的对比

| 场景 | Excel | NumPy | Pandas |
|------|-------|-------|--------|
| 表格数据 | ✅ 但慢 | ❌ 不便 | ✅ 完美 |
| 同构矩阵 | ✅ | ✅ 完美 | ✅ 但冗余 |
| 缺失值 | 部分支持 | 不支持 | ✅ 完善 |
| 异构列(每列不同类型) | ✅ | ❌ | ✅ 完美 |
| 大数据(GB+) | ❌ 卡 | ✅ | ✅(chunks) |

**一句话总结**:Pandas = 表格 + NumPy 的性能 + SQL 的易用。
"""))

# 1. Series + DataFrame
cells.append(md("""## 1. Series + DataFrame

### 1.1 原理

**Series**:一列带索引的一维数组(像 dict + ndarray)。
**DataFrame**:多个 Series 组成的二维表(每列是一个 Series,共享行索引)。

### 1.2 基础案例:Series"""))

cells.append(py_run([
    "s = pd.Series([10, 20, 30, 40], index=['a', 'b', 'c', 'd'])",
    "print('Series:\\n', s)",
    "print('值:', s.values)",
    "print('索引:', s.index)",
    "print('元素类型:', s.dtype)",
    "print('按标签取值:', s['b'])",
    "",
    "# 跟 dict 转换",
    "print('转 dict:', dict(s))",
    "print('从 dict 创建:', pd.Series({'x': 1, 'y': 2, 'z': 3}))",
]))

cells.append(md("""### 1.3 进阶案例 1:DataFrame 创建(4 种方式)"""))

cells.append(py_run([
    "# 方式 1:从 dict 创建",
    "df1 = pd.DataFrame({",
    "    'name': ['Alice', 'Bob', 'Charlie'],",
    "    'age': [25, 30, 35],",
    "    'city': ['北京', '上海', '深圳']",
    "})",
    "print('从 dict:\\n', df1)",
    "",
    "# 方式 2:从 list 创建(指定列名)",
    "df2 = pd.DataFrame(",
    "    [[1, 2], [3, 4], [5, 6]],",
    "    columns=['A', 'B']",
    ")",
    "print('\\n从 list:\\n', df2)",
    "",
    "# 方式 3:从 NumPy 数组",
    "df3 = pd.DataFrame(np.random.randn(4, 3), columns=['X', 'Y', 'Z'])",
    "print('\\n从 ndarray:\\n', df3)",
    "",
    "# 方式 4:从 SQL(本项目主要场景)",
    "import sqlite3",
    "from pathlib import Path",
    "if 'conn' not in globals():",
    "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))",
    "df4 = pd.read_sql('SELECT * FROM users LIMIT 3', conn)",
    "print('\\n从 SQL:\\n', df4)",
]))

cells.append(md("""### 1.4 进阶案例 2:DataFrame 核心属性"""))

cells.append(py_run([
    "df = pd.read_sql('SELECT * FROM orders LIMIT 100', conn)",
    "print('形状 (行,列):', df.shape)",
    "print('列名:', df.columns.tolist())",
    "print('行索引(默认 0..N-1):', df.index[:5].tolist())",
    "print('每列 dtype:\\n', df.dtypes)",
    "print('前 3 行:\\n', df.head(3))",
    "print('后 3 行:\\n', df.tail(3))",
    "print('随机 3 行:\\n', df.sample(3, random_state=42))",
]))

cells.append(md("""### 1.5 陷阱案例

**陷阱 1**:DataFrame 切片**返回视图还是副本**?
- `.loc[]` / `.iloc[]` 默认返回视图(修改会影响原 df)
- `.copy()` 显式副本

**陷阱 2**:列访问 `df.col` vs `df['col']`
- `df.col` 简洁,但**列名不能有空格/特殊字符**
- `df['col']` 通用,推荐

**陷阱 3**:布尔索引要用 `()` 包起来
```python
# 错
df[df['age'] > 25 and df['city'] == '北京']  # Python and,不是向量化
# 对
df[(df['age'] > 25) & (df['city'] == '北京')]  # & | ~ 是向量化运算符
```

### 1.6 面试 Q&A

**Q1: Series 和 DataFrame 关系?**
A: DataFrame 是多个 Series 组成的二维表,每列是一个 Series,共享行索引。

**Q2: 为什么 Pandas 用混合 Python/C 实现?**
A: Python 易用 + C 性能。Series/DataFrame 的 metadata(索引、列名)是 Python 对象,数据本身是 NumPy ndarray(连续内存)。

**Q3: DataFrame 适合多大数据?**
A: 一般 < 几 GB(内存)。超过 1GB 用 chunked / Dask / Polars / Spark。
"""))

# 2. 索引
cells.append(md("""## 2. 索引(.loc / .iloc) — Pandas 最重要的两个属性

### 2.1 原理

- **`.loc[]`**:基于**标签**(label)的索引(行/列名)
- **.iloc[]**:基于**位置**(integer position)的索引(0-based)
- 这两个一定搞清楚,混用会出错

### 2.2 基础案例:.loc vs .iloc"""))

cells.append(py_run([
    "df = pd.DataFrame({",
    "    'name': ['Alice', 'Bob', 'Charlie'],",
    "    'age': [25, 30, 35],",
    "    'city': ['北京', '上海', '深圳']",
    "}, index=['a', 'b', 'c'])",
    "print(df)",
    "",
    "# .loc(标签)",
    "print('\\n.loc[\"a\"]:\\n', df.loc['a'])",
    "print('\\n.loc[\"a\", \"name\"]:', df.loc['a', 'name'])",
    "print('\\n.loc[[\"a\", \"c\"]]:\\n', df.loc[['a', 'c']])",
    "",
    "# .iloc(位置)",
    "print('\\n.iloc[0]:\\n', df.iloc[0])",
    "print('\\n.iloc[0, 1]:', df.iloc[0, 1])",
    "print('\\n.iloc[0:2]:\\n', df.iloc[0:2])",
]))

cells.append(md("""### 2.3 进阶案例 1:布尔索引(数据筛选核心)"""))

cells.append(py_run([
    "df = pd.read_sql('SELECT * FROM users', conn)",
    "",
    "# 单条件",
    "print('北京用户数:', (df['city'] == '北京').sum())",
    "",
    "# 多条件(注意:& | ~ 不用 and or not)",
    "young_beijing = df[(df['city'] == '北京') & (df['age_group'] == '18-24')]",
    "print('北京 18-24 用户数:', len(young_beijing))",
    "",
    "# 包含列表",
    "tier1 = df[df['city'].isin(['北京', '上海', '广州', '深圳'])]",
    "print('一线城市用户数:', len(tier1))",
    "",
    "# 字符串包含",
    "social_users = df[df['channel'].str.contains('social', na=False)]",
    "print('social 渠道用户数:', len(social_users))",
    "",
    "# 数值范围",
    "print('\\n每渠道用户数:')",
    "print(df.groupby('channel').size())",
]))

cells.append(py_run([
    "# 实战:复杂筛选(订单数据)",
    "if 'df' not in globals():",
    "    df = pd.read_sql('SELECT * FROM users', conn)",
    "orders = pd.read_sql('SELECT * FROM orders WHERE status = \"completed\"', conn)",
    "",
    "# 大单 + 最近 30 天 + 北京用户",
    "cutoff = pd.Timestamp('2025-03-01')",
    "orders['order_date'] = pd.to_datetime(orders['order_date'])",
    "",
    "big_recent = orders[",
    "    (orders['amount'] >= 1000) &",
    "    (orders['order_date'] >= cutoff)",
    "    & orders['user_id'].isin(df[df['city'] == '北京']['user_id'])",
    "]",
    "print(f'北京用户近 30 天大单(>=1000): {len(big_recent)} 单')",
    "print(f'总金额: {big_recent[\"amount\"].sum():.2f}')",
]))

cells.append(md("""### 2.4 进阶案例 2:query()(类 SQL 写法)"""))

cells.append(py_run([
    "df = pd.read_sql('SELECT * FROM users', conn)",
    "",
    "# query() 用 SQL 语法筛选,可读性高",
    "result = df.query('city == \"北京\" and age_group == \"18-24\"')",
    "print(f'query 结果: {len(result)} 行')",
    "",
    "# 支持变量引用(用 @)",
    "target_cities = ['北京', '上海']",
    "result = df.query('city in @target_cities and channel == \"organic\"')",
    "print(f'北京/上海 organic 渠道用户: {len(result)} 行')",
    "",
    "# 复杂表达式",
    "result = df.query('channel.str.startswith(\"paid\")', engine='python')",
    "print(f'paid* 渠道: {len(result)} 行')",
]))

cells.append(md("""### 2.5 陷阱案例

**陷阱 1**:`.loc` 切片**包含**右边界,`.iloc` 切片**不包含**
```python
df.loc['a':'c']  # a, b, c(包含 c)
df.iloc[0:2]     # 0, 1(不含 2)
```

**陷阱 2**:`df['col'] = value` 不会触发 SettingWithCopyWarning
```python
# 警告:SettingWithCopyWarning
df_sub = df[df['x'] > 0]
df_sub['y'] = 1  # 可能不生效

# 解决:.loc + 显式条件
df.loc[df['x'] > 0, 'y'] = 1
```

**陷阱 3**:字符串访问用 `.str`,不是直接调方法
```python
df['col'].str.lower()  # 对
df['col'].lower()  # 错:AttributeError
```

### 2.6 面试 Q&A

**Q1: .loc 和 .iloc 区别?**
A: .loc 按标签(行/列名),.iloc 按位置(0-based)。切片时 .loc 含右边界,.iloc 不含。

**Q2: 布尔索引 vs query()?**
A: 布尔索引更快(query 有解析开销),query 可读性更高(类 SQL)。数据大用布尔,数据小 / 复杂条件用 query。

**Q3: SettingWithCopyWarning 怎么避免?**
A: 1) 用 .loc 显式条件赋值;2) 用 .copy() 显式副本;3) 链式操作用 .pipe()。
"""))

# 3. 增删改查
cells.append(md("""## 3. 增删改查 + 排序 + 描述统计

### 3.1 原理

数据分析师 80% 的时间在:**读 + 改 + 聚合**。Pandas 这块 API 极丰富,但**不查文档记不住**。重点是掌握套路。

### 3.2 基础案例:CRUD 操作"""))

cells.append(py_run([
    "df = pd.DataFrame({",
    "    'name': ['Alice', 'Bob', 'Charlie'],",
    "    'age': [25, 30, 35],",
    "})",
    "print('原:\\n', df)",
    "",
    "# 新增列",
    "df['salary'] = [50000, 60000, 70000]",
    "df['age_in_5y'] = df['age'] + 5",
    "df['senior'] = df['age'] > 30",
    "print('\\n加列后:\\n', df)",
    "",
    "# 修改值",
    "df.loc[df['name'] == 'Bob', 'salary'] = 65000  # 单值",
    "df['salary'] = df['salary'] * 1.1  # 整列",
    "print('\\n改值后:\\n', df)",
    "",
    "# 删除列",
    "df = df.drop(columns=['senior'])",
    "print('\\n删列后:\\n', df)",
]))

cells.append(md("""### 3.3 进阶案例 1:排序 + 排名"""))

cells.append(py_run([
    "df = pd.read_sql('SELECT * FROM users LIMIT 10', conn)",
    "",
    "# 按注册日升序",
    "print('按注册日升序:\\n', df.sort_values('register_date').head(3))",
    "",
    "# 多列排序",
    "print('\\n按 city 升序 + 注册日 降序:\\n', df.sort_values(['city', 'register_date'], ascending=[True, False]).head(3))",
    "",
    "# 排名",
    "df_sorted = df.sort_values('register_date')",
    "df_sorted['reg_rank'] = range(1, len(df_sorted) + 1)",
    "print('\\n加排名:\\n', df_sorted[['user_id', 'register_date', 'reg_rank']].head(3))",
]))

cells.append(py_run([
    "# 实战:用户消费排名",
    "orders = pd.read_sql('SELECT user_id, SUM(amount) AS gmv FROM orders WHERE status = \"completed\" GROUP BY user_id', conn)",
    "orders['rank'] = orders['gmv'].rank(ascending=False, method='min')",
    "orders['percentile'] = orders['gmv'].rank(pct=True)",
    "print('GMV Top 5:')",
    "print(orders.sort_values('gmv', ascending=False).head(5))",
]))

cells.append(md("""### 3.4 进阶案例 2:描述统计 + 聚合分组"""))

cells.append(py_run([
    "orders = pd.read_sql('SELECT * FROM orders WHERE status = \"completed\"', conn)",
    "",
    "# 描述统计(数值列)",
    "print('订单金额描述统计:\\n', orders['amount'].describe())",
    "",
    "# 单独统计",
    "print(f'\\n总和: {orders[\"amount\"].sum():.0f}')",
    "print(f'均值: {orders[\"amount\"].mean():.2f}')",
    "print(f'中位数: {orders[\"amount\"].median():.0f}')",
    "print(f'标准差: {orders[\"amount\"].std():.2f}')",
    "print(f'分位数: {orders[\"amount\"].quantile([0.25, 0.5, 0.75]).to_dict()}')",
    "",
    "# value_counts(频次统计)",
    "print('\\n订单状态分布:')",
    "print(orders['status'].value_counts())",
]))

cells.append(py_run([
    "# groupby(最常用)",
    "if 'orders' not in globals():",
    "    orders = pd.read_sql('SELECT * FROM orders WHERE status = \"completed\"', conn)",
    "print('各渠道 GMV 汇总:')",
    "users = pd.read_sql('SELECT * FROM users', conn)",
    "merged = orders.merge(users[['user_id', 'channel']], on='user_id', how='left')",
    "print(merged.groupby('channel')['amount'].agg(['sum', 'mean', 'count']).round(2))",
    "",
    "# 多聚合函数",
    "print('\\n多聚合:')",
    "print(merged.groupby('channel').agg(",
    "    gmv=('amount', 'sum'),",
    "    avg_order=('amount', 'mean'),",
    "    order_cnt=('order_id', 'count'),",
    "    user_cnt=('user_id', 'nunique')",
    ").round(2))",
]))

cells.append(md("""### 3.5 陷阱案例

**陷阱 1**:`inplace=True` 慎用
```python
# 错:inplace 操作难调试
df.drop('col', axis=1, inplace=True)  # 改 df 自身,其他引用它的变量也会变

# 对:链式赋值
df = df.drop('col', axis=1)
```

**陷阱 2**:`mean()` 默认**跳过 NaN**
```python
pd.Series([1, 2, np.nan]).mean()  # 1.5(跳过 NaN)
# 想算 NaN 为 0:fillna(0) 先
```

**陷阱 3**:`groupby` 后取多列要 `[['a', 'b']]`,不是 `['a', 'b']`
```python
df.groupby('g')['a', 'b'].mean()  # 错(在某些版本)
df.groupby('g')[['a', 'b']].mean()  # 对
```

### 3.6 面试 Q&A

**Q1: Pandas 怎么处理大数据?**
A: 1) chunked 读(`chunksize`);2) 只读需要的列(`usecols`);3) 优化 dtype(把 int64 改 int32,把 object 改 category);4) 用 Polars / Dask 替代。

**Q2: 怎么优化 DataFrame 内存?**
A: 1) `df.info(memory_usage='deep')` 看内存;2) `astype` 转更小类型;3) object 列用 `pd.Categorical`;4) 重复值多的列用 SparseArray。

**Q3: 合并多个 DataFrame 怎么选方法?**
A: `merge`(类似 SQL JOIN) / `concat`(纵向/横向拼接) / `join`(基于索引合并)。生产中 80% 用 `merge`。
"""))

# 4. 实战
cells.append(md("""## 4. 实战:5 个基础分析

### 4.1 数据加载(常用 I/O)"""))

cells.append(py_run([
    "import sqlite3",
    "from pathlib import Path",
    "",
    "if 'conn' not in globals():",
    "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))",
    "",
    "# 4 种常用加载方式",
    "df_sql = pd.read_sql('SELECT * FROM orders', conn)  # 从 SQL",
    "df_csv = pd.read_csv('../data/orders.csv') if False else None  # 从 CSV(本项目没这文件)",
    "# df_excel = pd.read_excel('data.xlsx')  # 从 Excel",
    "# df_parquet = pd.read_parquet('data.parquet')  # 从 Parquet",
    "",
    "print(f'订单数据: {df_sql.shape}')",
    "print(df_sql.head())",
]))

cells.append(py_run([
    "# 实战 1:每用户消费总览(一次跑完整流程)",
    "print('=' * 50)",
    "print('实战 1:每用户消费总览')",
    "print('=' * 50)",
    "",
    "orders = pd.read_sql('SELECT * FROM orders WHERE status = \"completed\"', conn)",
    "user_summary = orders.groupby('user_id').agg(",
    "    order_cnt=('order_id', 'count'),",
    "    gmv=('amount', 'sum'),",
    "    avg_order=('amount', 'mean'),",
    "    last_order=('order_date', 'max'),",
    "    first_order=('order_date', 'min'),",
    ").reset_index()",
    "",
    "user_summary['active_days'] = (",
    "    pd.to_datetime(user_summary['last_order']) -",
    "    pd.to_datetime(user_summary['first_order'])",
    ").dt.days",
    "",
    "print('用户消费总览:')",
    "print(user_summary.describe().round(2))",
    "",
    "print('\\n' + '=' * 50)",
    "print('实战 2:RFM 简版分层')",
    "print('=' * 50)",
    "snapshot_date = pd.Timestamp('2025-04-01')",
    "user_summary['recency_days'] = (snapshot_date - pd.to_datetime(user_summary['last_order'])).dt.days",
    "user_summary['r_score'] = pd.qcut(user_summary['recency_days'], 4, labels=[4, 3, 2, 1])",
    "user_summary['f_score'] = pd.qcut(user_summary['order_cnt'].rank(method='first'), 4, labels=[1, 2, 3, 4])",
    "user_summary['m_score'] = pd.qcut(user_summary['gmv'].rank(method='first'), 4, labels=[1, 2, 3, 4])",
    "user_summary['rfm_avg'] = (user_summary['r_score'].astype(int) + user_summary['f_score'].astype(int) + user_summary['m_score'].astype(int)) / 3",
    "print('RFM 分层:')",
    "print(user_summary['rfm_avg'].value_counts().sort_index(ascending=False))",
    "",
    "print('\\n' + '=' * 50)",
    "print('实战 3:每日 GMV + 滚动平均')",
    "print('=' * 50)",
    "orders['order_date'] = pd.to_datetime(orders['order_date'])",
    "daily_gmv = orders.groupby(orders['order_date'].dt.date)['amount'].sum().reset_index()",
    "daily_gmv.columns = ['dt', 'daily_gmv']",
    "daily_gmv['ma7'] = daily_gmv['daily_gmv'].rolling(7).mean()",
    "daily_gmv['cum'] = daily_gmv['daily_gmv'].cumsum()",
    "print('每日 GMV 趋势(前 10 天):')",
    "print(daily_gmv.head(10))",
    "",
    "print('\\n' + '=' * 50)",
    "print('实战 4:用户行为漏斗')",
    "print('=' * 50)",
    "events = pd.read_sql('SELECT * FROM user_events', conn)",
    "funnel = events.groupby('event_type')['user_id'].nunique().reset_index()",
    "funnel.columns = ['event', 'user_cnt']",
    "funnel = funnel.sort_values('user_cnt', ascending=False)",
    "print('行为漏斗:')",
    "print(funnel)",
    "if len(funnel) > 1:",
    "    funnel['conversion'] = (funnel['user_cnt'] / funnel['user_cnt'].shift(1) * 100).round(2)",
    "    print('\\n各步转化率:')",
    "    print(funnel[['event', 'user_cnt', 'conversion']])",
    "",
    "print('\\n' + '=' * 50)",
    "print('实战 5:用户首末单 + 复购率')",
    "print('=' * 50)",
    "first_last = orders.sort_values(['user_id', 'order_date']).groupby('user_id').agg(",
    "    first=('amount', 'first'),",
    "    last=('amount', 'last'),",
    "    order_cnt=('order_id', 'count'),",
    ").reset_index()",
    "first_last['repurchase'] = (first_last['order_cnt'] >= 2).astype(int)",
    "repurchase_rate = first_last['repurchase'].mean()",
    "print(f'复购率(>=2 单): {repurchase_rate:.2%}')",
    "first_last['first_last_diff'] = first_last['last'] - first_last['first']",
    "print(f'首末单差平均: {first_last[\"first_last_diff\"].mean():.2f}')",
    "print(f'消费升级占比(末单>首单): {(first_last[\"first_last_diff\"] > 0).mean():.2%}')",
]))

cells.append(md("""## 5. 小结

### 速查表

| 需求 | 写法 |
|------|------|
| 创建 | `pd.Series / DataFrame / read_sql / read_csv` |
| 选行 | `df.loc[label] / df.iloc[pos] / df[mask]` |
| 选列 | `df['col'] / df[['a', 'b']]` |
| 加列 | `df['new'] = ...` |
| 改值 | `df.loc[mask, 'col'] = value` |
| 删 | `df.drop(columns=['col'])` |
| 排序 | `df.sort_values('col')` |
| 描述 | `df.describe() / .mean() / .sum()` |
| 分组 | `df.groupby('g').agg(...)` |
| 合并 | `df.merge(df2, on='key')` |

### 自测清单

- [ ] 能解释 .loc vs .iloc 区别
- [ ] 能用布尔索引做复杂筛选
- [ ] 能用 query() 写类 SQL 查询
- [ ] 能用 groupby + agg 做多维度分析
- [ ] 能避开 SettingWithCopyWarning

**全部 ✅ 之后推进 W2.3(数据清洗)。**
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

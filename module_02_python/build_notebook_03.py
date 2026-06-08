# -*- coding: utf-8 -*-
"""
build_notebook_03.py — module_02_python/03_data_cleaning.ipynb
================================================================
数据清洗:缺失值/重复/类型/字符串 + 实战脏数据
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "03_data_cleaning.ipynb"


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


cells = []

cells.append(md("""# W2.3 — 数据清洗(数据分析 80% 的时间)

> 数据分析师名言:"80% 的时间在清洗数据,20% 在分析"。
> 本节按 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试

## 本节大纲
- **0. 原理总览**:数据为什么会脏?清洗的 4 步流程
- **1. 缺失值处理**(7 种策略)
- **2. 重复值处理**
- **3. 数据类型转换**(astype / to_numeric / to_datetime)
- **4. 字符串处理**(.str 访问器)
- **5. 实战:造一份脏数据并清洗**

## 学习建议
- 脏数据样本自己造(可控)
- 每个清洗策略跑一下,看效果
- 重点是判断"什么时候用什么策略"
"""))

cells.append(py_run([
    "import numpy as np",
    "import pandas as pd",
    "print('Pandas version:', pd.__version__)",
]))

# 0. 原理
cells.append(md("""## 0. 原理总览:数据为什么会脏?

### 0.1 脏数据来源(大厂常见)

| 来源 | 例子 |
|------|------|
| 用户输入 | 手机号格式不一、地址乱填 |
| 系统 bug | 时间戳错乱、数值溢出 |
| 跨系统同步 | 字段类型不一致、字段缺失 |
| 业务变化 | 新增字段没兼容旧数据 |
| ETL 漏数据 | 抽数脚本没覆盖某些情况 |

### 0.2 数据清洗 4 步流程

```
1. 概览   ->  df.info() / df.describe() / df.isnull().sum()
2. 缺失   ->  dropna() / fillna()
3. 重复   ->  drop_duplicates()
4. 转换   ->  astype() / to_datetime() / .str 方法
```

### 0.3 大厂铁律

- 不删原始数据:用 `df_clean = df.copy()` 在副本上操作
- 清洗操作可复现:函数化 / 写脚本,不要手动改 Excel
- 记录清洗规则:有 100 个 NULL,删了 50 个,留 50 个——why?要写清楚
- 检测异常值:不只是清洗,还要识别"数据本身的问题"(如不可能为负的金额出现 -1)
"""))

# 1. 缺失值
cells.append(md("""## 1. 缺失值处理(NaN / None)

### 1.1 原理

Pandas 用 `NaN`(Not a Number)表示缺失值,在数值列里;字符串列里用 `None` 或 `NaN`。两者在大多数操作里等同。

**检测缺失**:
- `df.isnull()` / `df.isna()`(同义):返回 bool DataFrame
- `df.notnull()` / `df.notna()`:反向
- `df.isnull().sum()`:每列缺失数
- `df.isnull().mean()`:每列缺失比例(更直观)

**填充策略**(7 种):

| 策略 | 场景 |
|------|------|
| 删除行(`dropna`) | 缺失 < 5% 且不关键 |
| 删除列 | 缺失 > 50% 且不重要 |
| 固定值填充 | 业务上"默认值" |
| 前向/后向填充(`ffill`/`bfill`) | 时间序列 |
| 统计值填充(均值/中位数/众数) | 数值列 |
| 模型预测填充 | 重要列 |
| 标记填充(-1 / 9999) | 明确"未知"语义 |

### 1.2 基础案例:检测 + 简单填充"""))

cells.append(py_run([
    "# 造一份含缺失的数据",
    "df = pd.DataFrame({",
    "    'name': ['Alice', 'Bob', None, 'David'],",
    "    'age': [25, None, 35, 40],",
    "    'salary': [50000, 60000, None, 80000],",
    "    'city': ['北京', '上海', '深圳', None]",
    "})",
    "print('原数据:')",
    "print(df)",
    "",
    "# 检测缺失",
    "print('每列缺失数:')",
    "print(df.isnull().sum())",
    "print('每列缺失比例(%):')",
    "print((df.isnull().mean() * 100).round(2))",
    "",
    "# 删除有缺失的行(任何列缺失都删)",
    "print('删除有缺失的行后:')",
    "print(df.dropna())",
    "",
    "# 删除全是缺失的列",
    "df2 = df.copy()",
    "df2['all_null'] = None",
    "print('删除全缺失列后:')",
    "print(df2.dropna(axis=1, how='all'))",
]))

cells.append(md("""### 1.3 进阶案例 1:7 种填充策略"""))

cells.append(py_run([
    "df = pd.DataFrame({",
    "    'A': [1, 2, None, 4, 5],",
    "    'B': [10, None, 30, None, 50],",
    "    'C': ['x', None, 'z', None, 'w'],",
    "    'D': pd.to_datetime(['2025-01-01', None, '2025-01-03', None, '2025-01-05'])",
    "})",
    "print('原数据:')",
    "print(df)",
    "",
    "# 策略 1:固定值填充",
    "print('策略 1 - 固定值填充(A 填 0):')",
    "print(df.fillna({'A': 0}))",
    "",
    "# 策略 2:均值/中位数填充",
    "print('策略 2 - 均值填充(A):')",
    "print(df.fillna({'A': df['A'].mean()}))",
    "",
    "# 策略 3:前向/后向填充(时间序列友好)",
    "print('策略 3 - 前向填充(D 列):')",
    "print(df.fillna(method='ffill'))",
    "",
    "# 策略 4:线性插值(时间序列)",
    "print('策略 4 - 线性插值(A):')",
    "print(df.interpolate())",
    "",
    "# 策略 5:每列不同填充",
    "print('策略 5 - 多列分别填充:')",
    "print(df.fillna({'A': 0, 'B': 999, 'C': 'unknown', 'D': pd.Timestamp('2025-01-10')}))",
]))

cells.append(md("""### 1.4 进阶案例 2:删除策略详解"""))

cells.append(py_run([
    "df = pd.DataFrame({",
    "    'A': [1, 2, None, 4, 5],",
    "    'B': [10, None, 30, None, 50],",
    "    'C': [None, None, None, 4, 5]",
    "})",
    "print('原数据:')",
    "print(df)",
    "",
    "# how='any' 默认 - 任何缺失就删",
    "print('删除任何缺失的行:')",
    "print(df.dropna(how='any'))",
    "",
    "# how='all' - 全部缺失才删",
    "print('删除全部缺失的行:')",
    "print(df.dropna(how='all'))",
    "",
    "# subset - 只看某些列",
    "print('只对 A 列缺失就删:')",
    "print(df.dropna(subset=['A']))",
    "",
    "# thresh - 至少 N 个非缺失值",
    "print('每行至少 2 个非缺失值:')",
    "print(df.dropna(thresh=2))",
]))

cells.append(md("""### 1.5 陷阱案例

**陷阱 1**:`== None` 不能用
```python
df[df['col'] == None]  # 错!Pandas NaN 不等于 None
df[df['col'].isnull()]  # 对
```

**陷阱 2**:`fillna(inplace=True)` 慎用(链式失效)
```python
df.fillna(0, inplace=True)  # 修改 df
df.fillna(0)  # 返回新 df,df 本身不变
```

**陷阱 3**:字符串列的 NaN
```python
pd.Series(['a', None, 'c']).isnull()  # True 在 None 位置(正确)
pd.Series(['a', '', 'c']).isnull()  # False(空字符串不是 NaN!)
```

### 1.6 面试 Q&A

**Q1: 缺失值用均值还是中位数?**
A: 看分布。对称分布用均值(更快);偏态分布用中位数(对异常值鲁棒)。

**Q2: 时间序列的缺失值怎么填?**
A: 用前向/后向填充(`ffill`/`bfill`)或线性插值(`interpolate()`)。不能用均值(破坏时间趋势)。

**Q3: 缺失率 > 50% 的列怎么处理?**
A: 通常**删除**(信号太少),但要看业务。如果该列是关键(如身份证号),尝试单独建模预测填充。
"""))

# 2. 重复值
cells.append(md("""## 2. 重复值处理

### 2.1 原理

**重复值的 2 种**:
- **完全重复**:所有列都一样(数据录入错误)
- **部分重复**:某几列一样(如同一用户重复注册)

**检测**:`duplicated()` 返回 bool Series
**删除**:`drop_duplicates()`

### 2.2 基础案例"""))

cells.append(py_run([
    "df = pd.DataFrame({",
    "    'user_id': [1, 2, 2, 3, 4, 4, 4],",
    "    'name': ['A', 'B', 'B', 'C', 'D', 'D', 'E'],",
    "    'email': ['a@x', 'b@x', 'b@x', 'c@x', 'd@x', 'd@x', 'e@x'],",
    "})",
    "print('原数据:')",
    "print(df)",
    "",
    "# 检测完全重复(默认所有列比对)",
    "print('\\n哪些是完全重复:')",
    "print(df.duplicated())",
    "print('重复行数:', df.duplicated().sum())",
    "",
    "# 删除完全重复(保留第一个)",
    "print('\\n删除完全重复(保留第一个):')",
    "print(df.drop_duplicates())",
    "",
    "# 按某列去重(只考虑 user_id)",
    "print('\\n按 user_id 去重(保留第一个):')",
    "print(df.drop_duplicates(subset=['user_id']))",
    "",
    "# 保留最后一个",
    "print('\\n按 user_id 去重(保留最后一个):')",
    "print(df.drop_duplicates(subset=['user_id'], keep='last'))",
    "",
    "# 全部删除(只要出现过就都删)",
    "print('\\n按 user_id 去重(重复的全部删):')",
    "print(df.drop_duplicates(subset=['user_id'], keep=False))",
]))

cells.append(md("""### 2.3 陷阱 + 面试

**陷阱**:列对比时,字符串和数字类型不一致
```python
df = pd.DataFrame({'A': ['1', '1.0', 1, 1.0]})
df.duplicated()  # '1' != 1.0,但 '1' == 1,NaN 比较是 NaN
```

**面试**:
- Q1: 部分重复(用户重复注册)怎么保留有效那条?
  A: 加时间列 + `sort_values('time')` + `drop_duplicates(subset=['user_id'], keep='last')`
- Q2: 删重复时 inplace=True 风险?
  A: 难回滚,推荐链式 `df = df.drop_duplicates(...)`
"""))

# 3. 类型转换
cells.append(md("""## 3. 数据类型转换

### 3.1 原理

Pandas 常见 dtype:
- `int64` / `int32` / `int8`
- `float64` / `float32`
- `object`(字符串 / Python 对象)
- `bool`
- `datetime64`
- `category`(分类,枚举型,省内存)

**类型转换三剑客**:
- `astype()`:通用转换
- `to_numeric()`:数值专用,带错误处理
- `to_datetime()`:日期专用,带格式推断

### 3.2 基础案例"""))

cells.append(py_run([
    "# 字符串 -> 数值(to_numeric + errors='coerce')",
    "s = pd.Series(['1', '2', 'three', '4', None])",
    "print('原:')",
    "print(s)",
    "print('\\n转数值(错误变 NaN):')",
    "print(pd.to_numeric(s, errors='coerce'))",
    "",
    "# 字符串 -> 日期",
    "s = pd.Series(['2025-01-01', '2025/02/15', 'not a date', '2025-03-20'])",
    "print('\\n转日期:')",
    "print(pd.to_datetime(s, errors='coerce'))",
    "",
    "# 自定义日期格式",
    "s = pd.Series(['01-2025-15', '02-2025-20'])",  # 假装是 MM-YYYY-DD",
    "print('\\n自定义格式:')",
    "print(pd.to_datetime(s, format='%m-%Y-%d', errors='coerce'))",
]))

cells.append(md("""### 3.3 进阶案例:astype + 内存优化"""))

cells.append(py_run([
    "df = pd.DataFrame({",
    "    'user_id': pd.array([1, 2, 3, 4], dtype='int32'),",
    "    'channel': ['organic', 'paid', 'social', 'organic'],",
    "    'is_active': [True, False, True, True],",
    "    'score': [0.5, 0.8, 0.3, 0.9],",
    "})",
    "print('原:')",
    "print(df)",
    "print('\\ndtypes:')",
    "print(df.dtypes)",
    "print('\\n内存(bytes):', df.memory_usage(deep=True).sum())",
    "",
    "# 优化:channel 用 category(重复值多)",
    "df['channel'] = df['channel'].astype('category')",
    "print('\\n优化后:')",
    "print(df.dtypes)",
    "print('内存(bytes):', df.memory_usage(deep=True).sum())",
    "",
    "# downcast 数值类型",
    "df['user_id'] = pd.to_numeric(df['user_id'], downcast='integer')",
    "print('\\nDowncast 后:')",
    "print(df.dtypes)",
]))

cells.append(md("""### 3.4 陷阱 + 面试

**陷阱 1**:astype('int') 对 NaN 报错
```python
pd.Series([1, 2, None]).astype('int')  # ValueError
# 对:先 fillna 或用 'Int64'(大写,允许 NaN)
pd.Series([1, 2, None]).astype('Int64')  # OK
```

**陷阱 2**:astype 改变原数据 vs 返回新
```python
df['col'].astype('int')  # 返回新 Series
df['col'] = df['col'].astype('int')  # 重新赋值给 df
```

**面试**:
- Q1: 怎么把 object 列转 category 省内存?
  A: `df['col'].astype('category')`。重复值越多省得越多。
- Q2: 字符串日期转 datetime 失败怎么办?
  A: `errors='coerce'` 转 NaT,然后 `fillna` 或 `dropna` 处理。
"""))

# 4. 字符串
cells.append(md("""## 4. 字符串处理(.str 访问器)

### 4.1 原理

`Series.str` 访问器提供**向量化**字符串操作,类似 Python str 方法但对整个 Series 同时生效。

**常用方法**:
- 大小写:`lower` / `upper` / `title` / `capitalize`
- 去空白:`strip` / `lstrip` / `rstrip`
- 包含/匹配:`contains` / `startswith` / `endswith` / `match`
- 替换:`replace`
- 拆分:`split` / `partition`
- 切片:`[start:end]`
- 长度:`len`
- 正则:很多方法接受 `regex=True`

### 4.2 基础案例"""))

cells.append(py_run([
    "s = pd.Series(['  Alice  ', 'BOB', 'charlie', '  David  '])",
    "print('原:')",
    "print(s)",
    "",
    "print('\\n去空白 + 转小写:')",
    "print(s.str.strip().str.lower())",
    "",
    "print('\\n是否包含特定字符:')",
    "print(s.str.contains('a', case=False))",
    "",
    "print('\\n以 A 开头:')",
    "print(s.str.strip().str.startswith('A'))",
]))

cells.append(md("""### 4.3 进阶案例 1:正则提取 + 替换"""))

cells.append(py_run([
    "# 真实业务:手机号格式化",
    "phones = pd.Series([",
    "    '13800138000',",
    "    '138-0013-8000',",
    "    '+86 138 0013 8000',",
    "    '1380013800',  # 少一位",
    "    '1380013800a',  # 带字母",
    "])",
    "print('原:')",
    "print(phones)",
    "",
    "# 提取纯数字(用正则)",
    "digits = phones.str.replace(r'\\D', '', regex=True)",
    "print('\\n提取纯数字:')",
    "print(digits)",
    "",
    "# 判断是否合法(11 位数字)",
    "valid = (digits.str.len() == 11) & (digits.str.match(r'^1\\d{10}$'))",
    "print('\\n是否合法手机号:')",
    "print(valid)",
    "",
    "# 格式化输出 +86-xxx-xxxx-xxxx",
    "formatted = '86-' + digits.str[0:3] + '-' + digits.str[3:7] + '-' + digits.str[7:11]",
    "print('\\n格式化:')",
    "print(formatted)",
]))

cells.append(md("""### 4.4 进阶案例 2:split + 拆分字段"""))

cells.append(py_run([
    "# 真实业务:地址拆分为省市区",
    "addresses = pd.Series([",
    "    '广东省 深圳市 南山区',",
    "    '北京市 海淀区 中关村',",
    "    '上海市 浦东新区 张江',",
    "])",
    "print('原:')",
    "print(addresses)",
    "",
    "# 拆分",
    "split = addresses.str.split(' ', expand=True)",
    "split.columns = ['省', '市', '区']",
    "print('\\n拆分后:')",
    "print(split)",
]))

cells.append(md("""### 4.5 陷阱 + 面试

**陷阱 1**:`str` 访问器对 NaN 友好(返回 NaN,不报错)
```python
pd.Series(['a', None, 'b']).str.upper()  # ['A', NaN, 'B']
```

**陷阱 2**:字符串列里混了数字会出错
```python
s = pd.Series(['1', '2', 'three'])
s.str.upper()  # OK
s.astype(int)  # ValueError
```

**面试**:
- Q1: 怎么从混合日期字符串里提取日期?
  A: `pd.to_datetime(s, errors='coerce', format='mixed')` 或正则提取
- Q2: .str 访问器 vs apply(lambda) 哪个好?
  A: 几乎都是 .str 快(向量化 C 实现)。只有逻辑复杂时才用 apply。
"""))

# 5. 综合实战
cells.append(md("""## 5. 综合实战:造一份脏数据并清洗

### 5.1 造数据 + 概览"""))

cells.append(py_run([
    "# 造一份贴近业务的脏数据",
    "np.random.seed(42)",
    "n = 1000",
    "df = pd.DataFrame({",
    "    'user_id': np.random.randint(1, 500, n),  # 故意有重复",
    "    'name': np.random.choice(['Alice', 'Bob', None, ''], n, p=[0.4, 0.4, 0.1, 0.1]),",
    "    'phone': [f'+86 138 {np.random.randint(1000, 9999)} {np.random.randint(1000, 9999)}' if i % 10 != 0 else None for i in range(n)],",
    "    'register_date': pd.to_datetime('2025-01-01') + pd.to_timedelta(np.random.randint(0, 90, n), unit='D'),",
    "    'amount': np.random.choice([10, 50, 100, 500, 1000, None, -1], n, p=[0.2, 0.2, 0.2, 0.2, 0.1, 0.05, 0.05]),",
    "    'channel': np.random.choice(['organic', 'paid', 'SOCIAL', ' Direct ', None], n),",
    "    'is_active': np.random.choice([True, False, 'yes', 'no', None], n),",
    "})",
    "print('原数据形状:', df.shape)",
    "print('\\n概览:')",
    "print(df.info())",
    "print('\\n每列缺失:')",
    "print(df.isnull().sum())",
]))

cells.append(md("""### 5.2-5.5 综合实战:4 步清洗 pipeline

把 4 个清洗步骤合并到一个 mega cell(避免跨 cell 依赖)。"""))

cells.append(py_run([
    "# 一次性跑完整个清洗流程",
    "print('=' * 60)",
    "print('清洗步骤 1:去重 + 缺失处理')",
    "print('=' * 60)",
    "if 'df' not in globals():",
    "    # 自包含:自己造一份脏数据(如果前面 cell 没跑过)",
    "    np.random.seed(42)",
    "    n = 1000",
    "    df = pd.DataFrame({",
    "        'user_id': np.random.randint(1, 500, n),",
    "        'name': np.random.choice(['Alice', 'Bob', None, ''], n, p=[0.4, 0.4, 0.1, 0.1]),",
    "        'phone': [f'+86 138 {np.random.randint(1000, 9999)} {np.random.randint(1000, 9999)}' if i % 10 != 0 else None for i in range(n)],",
    "        'register_date': pd.to_datetime('2025-01-01') + pd.to_timedelta(np.random.randint(0, 90, n), unit='D'),",
    "        'amount': np.random.choice([10, 50, 100, 500, 1000, None, -1], n, p=[0.2, 0.2, 0.2, 0.2, 0.1, 0.05, 0.05]),",
    "        'channel': np.random.choice(['organic', 'paid', 'SOCIAL', ' Direct ', None], n),",
    "        'is_active': np.random.choice([True, False, 'yes', 'no', None], n),",
    "    })",
    "    print('(自包含:已自动造数据)')",
    "df_clean = df.copy()",
    "print('清洗前:', df_clean.shape)",
    "df_clean = df_clean.drop_duplicates(subset=['user_id', 'register_date'])",
    "print('去重后:', df_clean.shape)",
    "df_clean['name'] = df_clean['name'].replace('', None)",
    "df_clean = df_clean.dropna(subset=['name'])",
    "df_clean['phone'] = df_clean['phone'].fillna('unknown')",
    "mode_channel = df_clean['channel'].mode()[0]",
    "df_clean['channel'] = df_clean['channel'].fillna(mode_channel)",
    "print('清洗后缺失:')",
    "print(df_clean.isnull().sum())",
    "",
    "print('\\n' + '=' * 60)",
    "print('清洗步骤 2:异常值 + 类型转换')",
    "print('=' * 60)",
    "print('amount 负数:', (df_clean['amount'] < 0).sum())",
    "df_clean = df_clean[df_clean['amount'] >= 0]",
    "df_clean['is_active'] = df_clean['is_active'].map({'yes': True, 'no': False, True: True, False: False})",
    "df_clean['channel'] = df_clean['channel'].str.strip().str.lower()",
    "print('channel 分布:')",
    "print(df_clean['channel'].value_counts())",
    "",
    "print('\\n' + '=' * 60)",
    "print('清洗步骤 3:字符串处理')",
    "print('=' * 60)",
    "df_clean['phone_digits'] = df_clean['phone'].str.replace(r'\\D', '', regex=True)",
    "valid_mask = (df_clean['phone_digits'].str.len() == 11)",
    "print(f'有效手机号: {valid_mask.sum()} / {len(df_clean)}')",
    "df_clean['phone_formatted'] = df_clean['phone_digits'].where(",
    "    valid_mask,",
    "    'invalid'",
    ").where(",
    "    ~valid_mask | (df_clean['phone_digits'].str.len() == 11),",
    "    df_clean['phone_digits'].str[0:3] + '-' + df_clean['phone_digits'].str[3:7] + '-' + df_clean['phone_digits'].str[7:11]",
    ")",
    "print('格式化样本:')",
    "print(df_clean[['phone', 'phone_formatted']].head(10))",
    "",
    "print('\\n' + '=' * 60)",
    "print('清洗步骤 4:数据质量报告')",
    "print('=' * 60)",
    "",
    "def quality_report(df_, name='清洗后'):",
    "    print(f'\\n----- {name} 质量报告 -----')",
    "    print(f'形状: {df_.shape}')",
    "    print(f'每列缺失率(%):')",
    "    print((df_.isnull().mean() * 100).round(2))",
    "    print(f'每列 dtype:')",
    "    print(df_.dtypes)",
    "    print(f'重复行数: {df_.duplicated().sum()}')",
    "    print(f'内存: {df_.memory_usage(deep=True).sum() / 1024:.1f} KB')",
    "",
    "quality_report(df_clean, '清洗后')",
    "print()",
    "quality_report(df, '原数据')",
]))

cells.append(md("""## 6. 小结

### 速查表

| 场景 | 写法 |
|------|------|
| 检测缺失 | `df.isnull() / isnull().sum() / isnull().mean()` |
| 删除缺失 | `df.dropna(how='any'/'all', subset=[...], thresh=N)` |
| 填充缺失 | `df.fillna(value / dict / method='ffill' / method='bfill')` |
| 检测重复 | `df.duplicated()` |
| 删除重复 | `df.drop_duplicates(subset=[...], keep='first'/'last'/False)` |
| 转数值 | `pd.to_numeric(s, errors='coerce')` |
| 转日期 | `pd.to_datetime(s, errors='coerce', format=...)` |
| 转类型 | `df['col'].astype('int' / 'category' / 'Int64')` |
| 字符串操作 | `df['col'].str.lower() / strip() / contains() / replace(regex=True)` |
| 拆分 | `df['col'].str.split(' ', expand=True)` |

### 自测清单

- [ ] 能区分 NaN 和 None
- [ ] 能选对填充策略(均值/中位数/前向)
- [ ] 能用 to_numeric / to_datetime 处理脏数据
- [ ] 能用 .str 访问器做向量化字符串处理
- [ ] 能写出完整清洗 pipeline

**全部 ✅ 之后推进 W2.4(时间序列)。**
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

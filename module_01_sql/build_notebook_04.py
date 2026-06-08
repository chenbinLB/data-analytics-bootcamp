# -*- coding: utf-8 -*-
"""
build_notebook_04_v2.py — 04_hive_and_optimization.ipynb v2(加深版)
====================================================================
模块 1.4 收官:Hive SQL + 性能 + 真题 + 面试模板
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "04_hive_and_optimization.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text if isinstance(text, list) else [text]}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text if isinstance(text, list) else [text]}


def py_run(stmt):
    return code(stmt)


def sql_run(comment, sql):
    setup = (
        "# 自包含 setup\n"
        "if 'pd' not in globals() or 'conn' not in globals():\n"
        "    import pandas as pd\n"
        "    import sqlite3\n"
        "    from pathlib import Path\n"
        "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))\n"
        "    print('Setup OK')\n"
        "\n"
    )
    body = comment.rstrip() + "\n\n" + setup + 'pd.read_sql("""\n' + sql.strip() + '\n""", conn)'
    return code(body)


cells = []

# ============== 标题 ==============

cells.append(md("""# 模块 1.4 — Hive SQL + 性能优化 + 真题(收官版)

> **本节是模块 1 收官**。补全生产环境差异和性能意识。
> 学完这节,你可以投递 SQL 笔试要求的任何数分岗位。

## 本节大纲
- **0. 原理总览**:为什么生产用 Hive/Spark SQL,跟 SQLite 差什么
- **1. SQLite vs Hive SQL 差异速查**(带案例)
- **2. 常用 Hive 特有函数**(带案例)
- **3. 性能优化 10 条铁律**(每条带原理 + 反例)
- **4. EXPLAIN 解读**(带案例)
- **5. 大厂真题分类索引**(带刷题节奏)
- **6. 模块 1 速查表**(贴墙)
- **7. 简历 / 面试怎么用模块 1**
"""))

cells.append(py_run("""# 数据库连接
import sqlite3
import pandas as pd
from pathlib import Path

DB = Path('../data/ecommerce.db').resolve()
conn = sqlite3.connect(DB)
print('Connected to', DB)"""))

# ============== 0. 原理总览 ==============

cells.append(md("""## 0. 原理总览:为什么生产用 Hive/Spark SQL?

### 0.1 数据规模的演进

```
单机 SQLite        < 1 GB         本地分析
单机 PostgreSQL    < 100 GB       部门级
Hive / Spark SQL   100 GB - PB    互联网大厂
MaxCompute / BigQuery  PB+         云数仓
```

我们这个项目用 SQLite 练,但**生产 99% 用 Hive/Spark SQL**。好消息:**90% 语法通用**。

### 0.2 三种主流 SQL 引擎对比

| 引擎 | 部署 | 计算模型 | 典型场景 |
|------|------|---------|---------|
| **SQLite** | 嵌入式 | 单机 | 本地开发、原型验证、小数据 |
| **Hive** | 集群 | MapReduce / Tez / Spark | 大厂数仓、离线 T+1 报表 |
| **Spark SQL** | 集群 | DAG(内存计算) | 大厂实时数仓、机器学习 |

### 0.3 关键差异总览

| 维度 | SQLite | Hive / Spark SQL |
|------|--------|------------------|
| 数据存储 | 单文件(.db) | HDFS / OSS / S3(分布式文件) |
| 表类型 | 普通表 | 内部表 / 外部表 / 分区表 / 分桶表 |
| 数据格式 | 二进制 | ORC / Parquet / TextFile |
| 计算方式 | 单机全内存 | 分布式 Map / Reduce |
| 函数丰富度 | 基础 | 极丰富(几百个内置函数) |
| 优化器 | 简单 | CBO(基于成本)+ 规则优化器 |

### 0.4 大厂面试会问的"生产差异"

- "SQLite 和 Hive 写 SQL 有啥不一样?" — 主要在日期/字符串/复杂类型函数
- "生产 SQL 怎么优化?" — 看下面 10 条铁律
- "数据倾斜怎么解决?" — 倾斜 key 加随机前缀打散
- "大表 JOIN 怎么搞?" — Map Join(小表广播)/ Bucket Join / 过滤下推

### 0.5 我们的练法

本项目用 SQLite 练,**重点是 SQL 思维和业务能力**。生产环境的差异(主要是函数名 + 性能调优)单独讲。
"""))

# ============== 1. SQLite vs Hive 差异 ==============

cells.append(md("""## 1. SQLite vs Hive SQL 差异(快对照表)

### 1.1 原理

SQLite 是 ANSI SQL 的"子集实现",Hive SQL 是"超集 + 自己的方言"。大部分查询 100% 通用,差异集中在**函数**和**类型**。

### 1.2 函数差异速查(完整)

**日期函数**(最常考):

| 用途 | SQLite | Hive / Spark SQL |
|------|--------|------------------|
| 字符串转 date | `DATE(str)` | `TO_DATE(str, 'yyyy-MM-dd')` |
| 截断到日 | `DATE(col)` | `TO_DATE(col)` |
| 加 N 天 | `DATE(col, '+N day')` | `DATE_ADD(col, N)` |
| 减 N 天 | `DATE(col, '-N day')` | `DATE_SUB(col, N)` |
| 算天数差 | `julianday(a) - julianday(b)` | `DATEDIFF(a, b)` |
| 提取年 | `CAST(strftime('%Y', col) AS INT)` | `YEAR(col)` |
| 提取月 | `strftime('%m', col)` | `MONTH(col)` |
| 当月最后一天 | (需算) | `LAST_DAY(col)` |
| 字符串转时间戳 | (难) | `UNIX_TIMESTAMP(str)` |
| 时间戳转字符串 | (难) | `FROM_UNIXTIME(ts, 'yyyy-MM-dd')` |

**字符串函数**:

| 用途 | SQLite | Hive |
|------|--------|------|
| 拼接 | `a || b` | `CONCAT(a, b, c)` / `CONCAT_WS(',', a, b)` |
| 截取 | `SUBSTR(s, start, len)` | 同(SQL 标准) |
| 正则提取 | (无) | `REGEXP_EXTRACT(s, regex, idx)` |
| 正则替换 | (无) | `REGEXP_REPLACE(s, regex, rep)` |
| 拆分 | (无) | `SPLIT(s, ',')`(返回 array) |
| 长度 | `LENGTH(s)` | 同 |
| 大小写 | `LOWER/UPPER` | 同 |

**空值函数**:

| 用途 | SQLite | Hive |
|------|--------|------|
| 第一个非空 | `COALESCE(a, b, c)` | 同 |
| NULL 替换 | `IFNULL(a, b)` | `NVL(a, b)` / `COALESCE(a, b)` |
| NULLIF | 同 | 同 |

**聚合函数**(Hive 特有):

| 函数 | 用途 | 风险 |
|------|------|------|
| `COLLECT_LIST(col)` | 把分组内值聚成数组 | 数据倾斜(单 key 太多) |
| `COLLECT_SET(col)` | 同上 + 去重 | 同 |
| `PERCENTILE_APPROX(col, 0.5)` | 近似中位数(快) | 误差 < 1% |
| `APPROX_COUNT_DISTINCT(col)` | 近似去重数(快) | 误差 < 2% |
| `VARIANCE / STDDEV` | 方差/标准差 | 同 |

**复杂类型**(Hive 特有):

```sql
-- array
SELECT col[0] FROM t;  -- 取第一个元素
SELECT size(col) FROM t;  -- 数组长度
SELECT explode(col) FROM t;  -- 行转列(配合 LATERAL VIEW)

-- struct
SELECT col.field FROM t;  -- 访问字段

-- map
SELECT col['key'] FROM t;  -- 取 key 对应值
```

### 1.3 实战案例:从 SQLite 改写到 Hive

**SQLite 写法**:
```sql
SELECT
    strftime('%Y-%m', order_date) AS ym,
    COUNT(*) AS cnt
FROM orders
WHERE julianday('2025-04-01') - julianday(order_date) <= 30
GROUP BY ym
```

**Hive 写法**:
```sql
SELECT
    SUBSTR(order_date, 1, 7) AS ym,
    COUNT(*) AS cnt
FROM orders
WHERE DATEDIFF('2025-04-01', order_date) <= 30
GROUP BY SUBSTR(order_date, 1, 7)
```

**核心差异**:`strftime` 换成 `SUBSTR`(Hive 不一定有 `strftime`),`julianday` 换成 `DATEDIFF`。
"""))

# ============== 2. 常用 Hive 函数案例 ==============

cells.append(md("""## 2. 常用 Hive 特有函数(实战案例)

### 2.1 原理

这些函数在 SQLite 中**不可用**或**行为不同**,但生产用得非常多。理解原理 + 记住场景,面试能过。

### 2.2 `COLLECT_LIST / COLLECT_SET`

**作用**:把分组内的值聚成数组。

**业务场景**:看每个用户买过的所有商品 ID。"""))

cells.append(sql_run("""# 演示:用 group_concat 模拟 collect_list(SQLite 替代)
# Hive 写法:SELECT user_id, COLLECT_LIST(product_id) FROM ... GROUP BY user_id""",
"""SELECT
    user_id,
    GROUP_CONCAT(DISTINCT product_id) AS product_list  -- SQLite 等价
FROM orders
WHERE status = 'completed'
GROUP BY user_id
ORDER BY user_id
LIMIT 5"""))

cells.append(md("""### 2.3 `LATERAL VIEW EXPLODE`(行转列)

**业务**:用户买了多个商品,展开成多行(便于后续 JOIN / 分析)"""))

cells.append(sql_run("""# SQLite 模拟:用递归 CTE 把 1,2,3 拆成 3 行
# Hive 写法:LATERAL VIEW EXPLODE(SPLIT(products, ',')) tbl AS product
# (用 RECURSIVE CTE 模拟 explode 行为)""",
"""WITH RECURSIVE
nums(n) AS (
    SELECT 1 UNION ALL SELECT n + 1 FROM nums WHERE n < 3
),
sample AS (
    SELECT '1,2,3' AS products
)
SELECT s.products, n AS idx,
    SUBSTR(s.products,
        (n - 1) * 2 + 1,
        CASE WHEN n = 3 THEN 1 ELSE 2 END
    ) AS product_id
FROM sample s, nums
-- 实际 Hive:LATERAL VIEW EXPLODE(SPLIT(products, ',')) tbl AS product_id"""))

cells.append(md("""### 2.4 `APPROX_COUNT_DISTINCT`(近似去重)

**原理**:HyperLogLog 算法,用固定内存估算去重数,误差 < 2%。

**业务场景**:算全平台 UV(千万级以上)"""))

cells.append(sql_run("""# SQLite 没有近似去重,用真实 COUNT(DISTINCT) 演示
# Hive:SELECT APPROX_COUNT_DISTINCT(user_id) FROM ... (快 10-100 倍)""",
"""-- SQLite 等价
SELECT COUNT(DISTINCT user_id) AS uv
FROM user_events
WHERE event_type = 'pv'"""))

cells.append(md("""### 2.5 `PERCENTILE_APPROX`(近似分位数)

**业务**:算用户消费金额的 P50/P90/P99(中位数 / 长尾头部)"""))

cells.append(sql_run("""# SQLite 等价:用 OFFSET 算分位数
# Hive:SELECT PERCENTILE_APPROX(amount, 0.5) FROM ... """,
"""WITH sorted AS (
    SELECT amount,
        ROW_NUMBER() OVER (ORDER BY amount) AS rn,
        COUNT(*) OVER () AS total
    FROM orders WHERE status = 'completed'
)
SELECT
    MAX(CASE WHEN rn = CAST(total * 0.5 AS INT) THEN amount END) AS p50,
    MAX(CASE WHEN rn = CAST(total * 0.9 AS INT) THEN amount END) AS p90,
    MAX(CASE WHEN rn = CAST(total * 0.99 AS INT) THEN amount END) AS p99
FROM sorted"""))

# ============== 3. 性能优化 10 条 ==============

cells.append(md("""## 3. 性能优化 10 条铁律(大厂笔试加分)

每条铁律 = 原理 + 反例 + 正例。

### 3.1 铁律 1:避免 `SELECT *`

**原理**:`SELECT *` 让引擎查所有列,数据量大时 IO / 网络传输浪费严重。生产环境大表(100+ 列)只查需要 2-3 列时,`SELECT *` 可能慢 50 倍。

**反例**:
```sql
SELECT * FROM orders WHERE order_date >= '2025-02-01'
```

**正例**:
```sql
SELECT order_id, user_id, amount FROM orders WHERE order_date >= '2025-02-01'
```

### 3.2 铁律 2:先过滤,后 JOIN

**原理**:JOIN 是 O(N*M) 或 O(N+M),过滤行越少,JOIN 越快。**过滤下推**是优化器的基本策略。

**反例**:
```sql
SELECT * FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE o.status = 'completed' AND u.channel = 'paid_search'
```

**正例**:
```sql
SELECT * FROM (
    SELECT * FROM orders WHERE status = 'completed'
) o
JOIN (
    SELECT * FROM users WHERE channel = 'paid_search'
) u ON o.user_id = u.user_id
```

### 3.3 铁律 3:小表驱动大表

**原理**:Hash Join 时,小表建 hash 表(内存),大表探测。小表越大,内存占用越大;大表越大,探测越慢。所以**小表放右边**(`LEFT JOIN` 主表在左)。

**反例**:
```sql
-- 不推荐:大表 LEFT JOIN 小表(小表是维表)
SELECT * FROM orders o LEFT JOIN dim_city c ON o.city_code = c.code
```

**正例**:
```sql
-- 推荐:大表 LEFT JOIN 小表(顺序 OK,关键是过滤下推)
SELECT * FROM orders o
LEFT JOIN dim_city c ON o.city_code = c.code
WHERE o.status = 'completed'
```

**进阶**:大表 JOIN 大表,用 `MAPJOIN` 提示小表广播:
```sql
SELECT /*+ MAPJOIN(small_tbl) */ *
FROM big_tbl JOIN small_tbl ON ...
```

### 3.4 铁律 4:避免 `COUNT(DISTINCT)大字段`

**原理**:千万级 `COUNT(DISTINCT)` 走 shuffle + 去重,极慢。生产上有 3 个替代方案:
- `APPROX_COUNT_DISTINCT`(误差 2%)
- `GROUP BY + COUNT` 二次聚合
- 预计算到宽表

**反例**:
```sql
SELECT COUNT(DISTINCT user_id) FROM events  -- 千万级慢
```

**正例**:
```sql
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events  -- 1-2 秒
-- 或
SELECT COUNT(*) FROM (SELECT user_id FROM events GROUP BY user_id) t  -- 二次聚合
```

### 3.5 铁律 5:分区表 + 分桶表

**原理**:
- **分区**(PARTITIONED BY):按时间/类别切文件夹,查询时只扫相关分区
- **分桶**(CLUSTERED BY):按 hash 切文件,JOIN 时相同 bucket 配对

**反例**:
```sql
-- 全表扫 1TB 数据
SELECT * FROM orders WHERE user_id = 12345
```

**正例**(分区表):
```sql
-- 只扫 user_id=12345 的分区文件
SELECT * FROM orders PARTITION (dt='2025-02-15')
WHERE user_id = 12345
```

**正例**(分桶表):
```sql
CREATE TABLE orders_bucketed (
    ...
) CLUSTERED BY (user_id) INTO 32 BUCKETS;
```

### 3.6 铁律 6:避免数据倾斜

**原理**:数据倾斜 = 某个 key 数据量远超其他 key,Reducer 处理时间 = max(slowest_reducer)。常见场景:
- JOIN key 是常量(如 `user_id = 0` 的"未登录用户")
- GROUP BY 维度过少
- COUNT(DISTINCT)单 key 多

**反例**:
```sql
-- 100 万条 user_id=0 的"未登录订单",让单个 Reducer 处理
SELECT user_id, COUNT(*) FROM orders GROUP BY user_id
```

**正例**:
```sql
-- 倾斜 key 加随机前缀
SELECT
    CASE WHEN user_id = 0
         THEN CONCAT('skew_', CAST(RAND() * 100 AS INT))
         ELSE CAST(user_id AS STRING)
    END AS user_id_skewed,
    COUNT(*)
FROM orders
GROUP BY 1
-- 跑完后再聚合
```

### 3.7 铁律 7:窗口函数前先排序

**原理**:`ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` 性能优于 `RANK()`(后者并列需要回退)。

实际上,三者在 Hive / Spark 里性能差异很小(都是 sort + window operator),主要看业务语义。

**铁律 8:避免在 WHERE 里用函数**

**原理**:`WHERE YEAR(order_date) = 2025` 会让分区/索引失效(每行都要算 YEAR)。

**反例**:
```sql
WHERE YEAR(order_date) = 2025
```

**正例**:
```sql
WHERE order_date >= '2025-01-01' AND order_date < '2026-01-01'
```

### 3.9 铁律 9:`UNION ALL` 替代 `UNION`(允许重复时)

**原理**:`UNION` 去重,慢;`UNION ALL` 保留,快。如果业务允许重复,优先 `UNION ALL`。

### 3.10 铁律 10:复杂查询拆 CTE

**原理**:可读性 + 可调试 + 优化器可能并行执行 CTE(PostgreSQL 12+,MySQL 8.0+)。

**反例**(3 层嵌套):
```sql
SELECT * FROM (
    SELECT user_id FROM (
        SELECT user_id, SUM(amount) AS gmv FROM orders GROUP BY user_id
    ) WHERE gmv > 1000
) t1 JOIN users u ON t1.user_id = u.user_id
```

**正例**(CTE 链式):
```sql
WITH
user_gmv AS (SELECT user_id, SUM(amount) AS gmv FROM orders GROUP BY user_id),
high_value AS (SELECT user_id FROM user_gmv WHERE gmv > 1000)
SELECT u.* FROM high_value h JOIN users u ON h.user_id = u.user_id
```
"""))

# ============== 4. EXPLAIN 解读 ==============

cells.append(md("""## 4. EXPLAIN 解读(看 SQL 慢在哪)

### 4.1 原理

**EXPLAIN** 命令让你看到 SQL 的**执行计划**:
- 数据怎么扫(全表 / 索引 / 范围)
- JOIN 用什么算法(Nested Loop / Hash / Sort-Merge)
- 各阶段的数据量估算
- 是否有排序 / 落盘

### 4.2 SQLite 的 EXPLAIN QUERY PLAN(本项目)"""))

cells.append(sql_run("""# 简单查询的执行计划""",
"""EXPLAIN QUERY PLAN
SELECT user_id, COUNT(*) AS cnt
FROM orders
WHERE status = 'completed'
GROUP BY user_id"""))

cells.append(sql_run("""# 带 JOIN 的执行计划""",
"""EXPLAIN QUERY PLAN
SELECT u.city, COUNT(*) AS cnt
FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE o.status = 'completed'
GROUP BY u.city"""))

cells.append(md("""**看 SQLite EXPLAIN 关注 3 件事**:
1. `SCAN TABLE`:全表扫(慢,大表要避免)
2. `SEARCH TABLE ... USING INDEX`:走索引(快)
3. `USE TEMP B-TREE FOR ORDER BY`:内存排序(数据量大时会落盘)

### 4.3 Hive 的 EXPLAIN(更详细)

```sql
EXPLAIN
SELECT ... FROM ...;
```

输出包含:
- **Stage 拆分**(Map / Reduce 阶段)
- **每个 Stage 的算子**(Filter / Project / Join)
- **数据量估算**(rows, bytes)
- **是否走分区 / 桶**

### 4.4 实战:用 EXPLAIN 诊断慢查询

**场景**:某查询跑 30 秒,先 EXPLAIN 看看。

**步骤**:
1. `EXPLAIN` 找出最耗时的 stage
2. 看是否走索引 / 分区
3. 看数据倾斜(某个 stage 数据量特别大)
4. 对症下药(改 SQL / 加分区 / 加索引)
"""))

# ============== 5. 真题分类索引 ==============

cells.append(md("""## 5. 大厂 SQL 真题分类索引(50 道 + 刷题节奏)

### 5.1 入门必刷(⭐,1-2 天)

| # | 题目 | 核心考点 | 来源 |
|---|------|---------|------|
| 1 | 各部门工资最高的员工 | 子查询 | LeetCode 184 |
| 2 | 查找重复的电子邮箱 | GROUP BY + HAVING | LeetCode 182 |
| 3 | 从不订购的客户 | LEFT JOIN + IS NULL | LeetCode 183 |
| 4 | 上升的温度 | DATEDIFF / LEAD LAG | LeetCode 197 |
| 5 | 第 N 高的薪水 | LIMIT OFFSET / 窗口函数 | LeetCode 177 |

### 5.2 中等必备(⭐⭐,2-3 天)

| # | 题目 | 核心考点 |
|---|------|---------|
| 6 | 连续出现的数字 | 窗口函数 + 段编号 |
| 7 | 部门工资前三高的员工 | DENSE_RANK TopN |
| 8 | 分数排名 | RANK / DENSE_RANK |
| 9 | 行程和用户 | LEFT JOIN 条件过滤 |
| 10 | 体育馆人流量 | Gaps and Islands |
| 11 | 列出指定时间段内所有的下单产品 | LEFT JOIN + DISTINCT |
| 12 | 即时订单配送率 | 业务转化漏斗 |
| 13 | 每月交易额 + 累计交易额 | 窗口函数累计 |
| 14 | 银行账户概要 | 多表 JOIN |
| 15 | 销售分析 III | BETWEEN + 聚合 |

### 5.3 高频大厂真题(⭐⭐⭐,3-5 天)

| # | 题目 | 核心考点 |
|---|------|---------|
| 16 | 连续登录用户(Gaps and Islands) | LAG + 段编号 |
| 17 | 用户留存率(D1/D7) | 日期函数 + LEFT JOIN |
| 18 | 漏斗分析(浏览→加购→购买) | 条件聚合 |
| 19 | RFM 8 群 | NTILE + 组合判断 |
| 20 | TopN 分组 | PARTITION + ROW_NUMBER |
| 21 | 月度复购率 | LAG + 月份对比 |
| 22 | 沉默用户召回 | 复杂条件 |
| 23 | 品类迁移 | 多窗口 + 集合差 |
| 24 | 用户行为路径 | LATERAL VIEW + EXPLODE |
| 25 | AB 测试结果查询 | 多表 JOIN + 统计 |

### 5.4 笔试压轴(⭐⭐⭐⭐,可选)

| # | 题目 | 核心考点 |
|---|------|---------|
| 26 | 最近 7 天每天的活跃用户数 | 窗口 + 日期运算 |
| 27 | 用户连续购买天数 | Gaps and Islands |
| 28 | 累计 GMV 排名 | 累计 + 排名 |
| 29 | 用户分群 + 占比 + GMV 贡献 | RFM 完整版 |
| 30 | 异动归因(DAU 突然下降) | 同比/环比 + 多维拆解 |

### 5.5 刷题节奏

- 入门 1-5 + 中等 6-15:每天 5 道,2-3 天
- 高频 16-25:每天 3-4 道,3 天
- 压轴 26-30:看思路,不卡死
- **重点是模块 1.1-1.3 的内容能脱口而出,刷题只是巩固**
"""))

# ============== 6. 模块 1 速查表 ==============

cells.append(md("""## 6. 模块 1 速查表(贴墙用)

### 6.1 基础(模块 1.1)

| 需求 | 写法 |
|------|------|
| 过滤 | `WHERE col = ...` |
| 排序 | `ORDER BY col ASC/DESC LIMIT n` |
| 去重 | `DISTINCT` / `COUNT(DISTINCT col)` |
| 分组 | `GROUP BY col1, col2` |
| 过滤组 | `HAVING agg() > ...` |
| 左连 | `LEFT JOIN ... ON ...` |
| 存在性 | `WHERE EXISTS (SELECT 1 ...)` |
| 空值 | `IS NULL`(不用 = NULL) |

### 6.2 窗口函数(模块 1.2)

| 需求 | 写法 |
|------|------|
| 取每组 TopN | `ROW_NUMBER() OVER (PARTITION BY g ORDER BY m DESC) <= N` |
| 累计求和 | `SUM(col) OVER (ORDER BY dt)` |
| 移动平均 | `AVG(col) OVER (ORDER BY dt ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` |
| 上行值 | `LAG(col, 1) OVER (PARTITION BY g ORDER BY t)` |
| 占比 | `col * 1.0 / SUM(col) OVER (PARTITION BY g)` |
| 排名 | `RANK() / DENSE_RANK() OVER (PARTITION BY g ORDER BY m DESC)` |
| 分桶 | `NTILE(n) OVER (ORDER BY m)` |
| 命名窗口 | `WINDOW w AS (...)`,多个函数复用 |

### 6.3 CTE + 业务(模块 1.3)

| 业务 | 核心 CTE 结构 | 关键函数 |
|------|-------------|---------|
| 留存率 | new_users + LEFT JOIN events | MAX(CASE WHEN date diff = N) |
| 漏斗 | user_funnel + 条件聚合 | MAX(CASE WHEN event = X) |
| 连续登录 | user_days + LAG + 段编号 | Gaps and Islands |
| RFM | 三个 NTILE + CASE WHEN | 8 群映射 |
| 行为路径 | ROW_NUMBER OVER (PARTITION BY user) | 时序判断 |

### 6.4 性能(模块 1.4)

- 避免 SELECT *
- 先过滤后 JOIN
- 小表驱动大表
- 分区 + 分桶
- 避免数据倾斜(随机前缀打散)
- 复杂查询拆 CTE
- 近似函数(APPROX_*)替代精确
- WHERE 不用函数(保护索引)
"""))

# ============== 7. 简历/面试 ==============

cells.append(md("""## 7. 简历 / 面试怎么用模块 1

### 7.1 简历项目模板(直接用)

> **数分项目经验**:
> 1. 电商用户行为分析(基于 50 万条用户行为日志)
>    - 用 SQL 窗口函数 + Gaps and Islands 思路计算 N 日留存
>    - 用 RFM 模型 8 群划分识别高价值客户 8000+,贡献 60% GMV
>    - 漏斗分析定位"加购 -> 购买"转化率瓶颈,推动运营优化

**关键词命中**:SQL、窗口函数、Gaps and Islands、留存、RFM、漏斗、转化率

### 7.2 面试模板(直接背)

**Q: 讲讲你用 SQL 做过最复杂的事?**

答:用 Gaps and Islands 思路算每个用户最长连续活跃天数,核心是 LAG 算日期差 + 段编号 + 段内聚合。整个查询 30 行内可读,生产环境跑 1000 万行数据 1.5 秒。

**Q: 窗口函数和聚合函数的区别?**

答:聚合函数 + GROUP BY 把 N 行变 1 行;窗口函数 + OVER 把 N 行变 N 行,加额外列。窗口函数能保留每行上下文,做排名、累计、同比。

**Q: 数据倾斜遇到过吗?怎么解决?**

答:遇到过。某次 JOIN 时 user_id = 0 的用户有几百万行,导致单 Reducer 跑 20 分钟。解决:把倾斜 key 加随机前缀打散,JOIN 后再合并。

**Q: Hive 和 MySQL 的 SQL 区别?**

答:90% 通用,主要是 Hive 特有:窗口函数(更丰富)、LATERAL VIEW explode 数组炸开、PERCENTILE_APPROX 近似分位数。日期函数 Hive 用 TO_DATE / DATE_ADD,MySQL 用 DATE_FORMAT / DATE_ADD。

**Q: 留存率怎么算?**

答:核心是 D0 新用户表 + 后续活跃日 LEFT JOIN。用 MAX(CASE WHEN DATE 差 = N THEN 1 END) 判断 D+N 是否有行为。`SUM(D+N 留存标记) / COUNT(总新用户) = D+N 留存率`。

**Q: 大表 JOIN 怎么优化?**

答:三板斧:1) 过滤下推(先 WHERE 再 JOIN);2) 小表驱动大表(Hash Join 内存友好);3) 数据倾斜时用 MAPJOIN 广播小表,或者加随机前缀打散倾斜 key。

### 7.3 简历加分项

除了 SQL,这些**大厂数据分析师必会**的相关能力(后续模块会覆盖):
- Python 数据处理(Pandas)
- 可视化(Matplotlib / Seaborn)
- A/B 测试设计 + 统计推断
- 指标体系搭建
- 异动归因分析
- LLM 工具使用(加分项)

模块 1 把 SQL 这块打扎实,后续模块一一攻破。
"""))

# ============== 8. 模块 1 收官 ==============

cells.append(md("""## 8. 模块 1 SQL 收官

**你已具备**:
- 基础语法速过 + JOIN + 子查询(原理 + 4-5 案例/知识点)
- **8 大窗口函数**(排名 / 累计 / 上下行 / 命名窗口)
- **5 大业务案例**(留存 / 漏斗 / 连续登录 / RFM / 行为路径)
- Hive SQL 差异 + 性能优化意识
- 50 道大厂真题分类索引

**自测标准**(都过关才算 W1 完成):
- [ ] 看业务题 5 分钟内能写出 SQL 框架
- [ ] 留存 / 漏斗 / RFM 任意一道题不看答案写出来
- [ ] 解释清楚 ROW_NUMBER / RANK / DENSE_RANK 差异
- [ ] 能说出 3 条 SQL 性能优化铁律
- [ ] 简历上能写出"用 SQL 窗口函数 / RFM / 漏斗"的项目描述

如果都 ✓,可以推进到 W2 了。

**下一步**:
- W2:Python 数据处理 + 可视化(打开 `module_02_python/`)
- 继续刷题:按模块 1.4 第 5 节刷题节奏
- 简历更新:用模块 1.4 第 7 节模板,把项目经历写上去
"""))


# ============== 写出 .ipynb ==============

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

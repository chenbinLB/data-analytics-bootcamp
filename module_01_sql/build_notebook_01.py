# -*- coding: utf-8 -*-
"""
build_notebook_01_v2.py — 01_basics_review.ipynb v2(加深版)
=============================================================

跟 1.2 同样的 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "01_basics_review.ipynb"


def md(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text if isinstance(text, list) else [text],
    }


def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text if isinstance(text, list) else [text],
    }


def py_run(stmt):
    return code(stmt)


def sql_run(comment, sql):
    setup = (
        "# 自包含 setup(如果已经跑过其他 cell,这里会跳过)\n"
        "if 'pd' not in globals() or 'conn' not in globals():\n"
        "    import pandas as pd\n"
        "    import sqlite3\n"
        "    from pathlib import Path\n"
        "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))\n"
        "    print('Setup OK ->', conn)\n"
        "\n"
    )
    body = comment.rstrip() + "\n\n" + setup + 'pd.read_sql("""\n' + sql.strip() + '\n""", conn)'
    return code(body)


cells = []

# ============== 标题 ==============

cells.append(md("""# 模块 1.1 — SQL 基础速过(加深版)

> Python 语法你已经会,这部分只梳理 SQL 重点和**大厂常见坑**。
> 这版我加了**详细原理**和**多案例**,确保你不仅会用,还懂为什么。

## 本节大纲
- **0. 原理总览**:SQL 执行顺序(关键!)
- **1. SELECT / WHERE / ORDER BY**:原理 + 4 案例
- **2. DISTINCT**:原理 + 3 案例
- **3. GROUP BY / HAVING / 聚合**:原理 + 4 案例
- **4. JOIN 全家福**:原理 + 5 案例
- **5. 子查询**:原理 + 4 案例
- **6. 练习题 + 答案**
- **7. 速查表 + 面试模板**

## 学习建议
- 每个知识点按"原理 -> 基础 -> 进阶 -> 陷阱 -> 面试"5 段读
- **不要跳原理段**,面试官最喜欢问"为什么"
- 跑 cell,看输出,确认跟预期一致
- 练习题先自己想 5 分钟再看答案
"""))

cells.append(py_run("""# 数据库连接
import sqlite3
import pandas as pd
from pathlib import Path

DB = Path('../data/ecommerce.db').resolve()
conn = sqlite3.connect(DB)
print('Connected to', DB)

# 验证数据
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
print('\\n数据表:')
print(tables)"""))

# ============== 0. 原理总览 ==============

cells.append(md("""## 0. 原理总览:SQL 执行顺序(必须背下来)

### 0.1 SQL 书写顺序 vs 执行顺序

很多人写 SQL 是按"我想看什么"写,但**数据库执行是按另一个顺序**。理解这个,很多谜团解开。

**书写顺序**(你写的顺序):
```
SELECT ...
FROM ...
WHERE ...
GROUP BY ...
HAVING ...
ORDER BY ...
LIMIT ...
```

**执行顺序**(数据库实际跑的顺序):
```
1. FROM        -- 1. 先确定数据源(JOIN 在这里完成)
2. WHERE       -- 2. 过滤行
3. GROUP BY    -- 3. 分组
4. HAVING      -- 4. 过滤组
5. SELECT      -- 5. 选列 + 聚合
6. ORDER BY    -- 6. 排序
7. LIMIT       -- 7. 限制行数
```

### 0.2 为什么这个顺序重要?

- **WHERE 不能用聚合函数**(聚合在 SELECT 阶段才计算)
- **SELECT 里的别名在 WHERE 里不能用**(WHERE 还没投影)
- **ORDER BY 引用 SELECT 别名可以**(ORDER BY 在 SELECT 之后)
- **HAVING 是"过滤组"**,"WHERE 是"过滤行""

### 0.3 思考:为什么 LIMIT 在最后?

因为 LIMIT 是"截取结果"——必须先有完整结果集,才能截取。如果 LIMIT 在中间,JOIN 后过滤的优化器就乱了。

### 0.4 大厂面试题:"WHERE 和 HAVING 区别?"

**标准答案**:
- `WHERE`:过滤**行**,在 GROUP BY 之前,**不能**用聚合函数
- `HAVING`:过滤**组**,在 GROUP BY 之后,**能用**聚合函数
- `WHERE` 过滤掉的行不参与聚合,`HAVING` 是聚合后才过滤

**反例**:
```sql
-- 错:WHERE 用了聚合
SELECT channel, SUM(amount)
FROM orders
WHERE SUM(amount) > 1000
GROUP BY channel

-- 对:HAVING 过滤聚合
SELECT channel, SUM(amount)
FROM orders
GROUP BY channel
HAVING SUM(amount) > 1000
```
"""))

# ============== 1. SELECT / WHERE / ORDER BY ==============

cells.append(md("""## 1. SELECT / WHERE / ORDER BY / LIMIT

### 1.1 原理

**SELECT**:**投影**——从表中"切出"需要的列。投影时可以做:
- 简单列: `SELECT col1, col2`
- 表达式: `SELECT amount * 1.1 AS with_tax`
- 函数: `SELECT UPPER(name)`, `SELECT DATE(t)`
- 别名: `SELECT col AS new_name`

**WHERE**:**过滤行**——一行一行判断 WHERE 条件,留下满足的。WHERE 能用:
- 比较: `=`, `<>`, `>`, `<`, `>=`, `<=`
- 逻辑: `AND`, `OR`, `NOT`
- 范围: `BETWEEN x AND y`(包含两端), `IN (a, b, c)`, `NOT IN`
- 模式: `LIKE 'abc%'`(模糊匹配)
- 空值: `IS NULL`, `IS NOT NULL`

**ORDER BY**:**排序**——按指定列排序,默认 ASC(升序),可指定 DESC(降序)。可以多列排序,前一个相同时才用第二个。

**LIMIT**:**截取**——只取前 N 行。MySQL 风格: `LIMIT n OFFSET m`(跳过 m 行取 n 行);PostgreSQL 风格: `LIMIT n OFFSET m`;SQLite 跟 PostgreSQL 一样。

### 1.2 基础案例:多条件过滤 + 排序"""))

cells.append(sql_run("""# 基础:查 2025-02 后注册、来自 paid_search 的 Top10 用户""",
"""SELECT user_id, register_date, channel, city
FROM users
WHERE register_date >= '2025-02-01'
  AND channel = 'paid_search'
ORDER BY register_date DESC
LIMIT 10"""))

cells.append(md("""### 1.3 进阶案例 1:范围与集合(BETWEEN / IN / LIKE)"""))

cells.append(sql_run("""# 进阶 1:BETWEEN + IN + LIKE 综合用法""",
"""SELECT user_id, order_date, amount, status
FROM orders
WHERE order_date BETWEEN '2025-02-01' AND '2025-02-28'
  AND status IN ('completed', 'refunded')
  AND amount BETWEEN 100 AND 1000
  AND user_id LIKE '1%'  -- 用户 ID 以 1 开头(SQLite 的 LIKE 模式)
ORDER BY amount DESC
LIMIT 10"""))

cells.append(md("""### 1.4 进阶案例 2:NULL 处理(大厂易错)

NULL 是 SQL 里的"特殊公民",跟 0/空字符串都不一样。"""))

cells.append(sql_run("""# 进阶 2:NULL 处理(找"有注册渠道"vs"无注册渠道"的用户)""",
"""SELECT
    COUNT(*) AS total_users,
    SUM(CASE WHEN channel IS NOT NULL THEN 1 ELSE 0 END) AS has_channel,
    SUM(CASE WHEN channel IS NULL THEN 1 ELSE 0 END) AS no_channel
FROM users

-- 错误写法:WHERE channel = NULL 永远为 NULL(没结果)
-- 正确:WHERE channel IS NULL"""))

cells.append(md("""### 1.5 陷阱案例

**陷阱 1**:`WHERE col = NULL` 永远没结果
```sql
-- 错:NULL = NULL 在 SQL 里是 NULL(不是 TRUE)
SELECT * FROM users WHERE channel = NULL

-- 对:用 IS NULL
SELECT * FROM users WHERE channel IS NULL
```

**陷阱 2**:字符串比较的大小写问题
```sql
-- SQLite 默认区分大小写:'paid_search' != 'Paid_Search'
-- MySQL 默认不区分(取决于 collation)
-- 生产上注意:用 LOWER() 包一下,或者在 schema 层定 collation
WHERE LOWER(channel) = 'paid_search'
```

**陷阱 3**:日期字符串比较
```sql
-- 如果 order_date 是 '2025-02-01 10:23:45',以下比较会出错
WHERE order_date >= '2025-02-01'  -- 真,但 '2025-02-01' 被当 '2025-02-01 00:00:00'
-- 如果要"2 月 1 日整天":
WHERE order_date >= '2025-02-01' AND order_date < '2025-02-02'
-- 或者用 DATE() 截断
WHERE DATE(order_date) = '2025-02-01'  -- 但这函数会导致全表扫,慎用
```

### 1.6 面试 Q&A

**Q1: WHERE 后面能用列别名吗?**
A: 不能。WHERE 在 SELECT 之前执行,别名还没生成。ORDER BY 可以(在 SELECT 之后)。

**Q2: 1000 万行用 WHERE 过滤,要建索引吗?**
A: 看 WHERE 列的选择性。如果过滤后剩 1%,建索引能 100 倍提速;过滤后剩 50%,索引效果差。

**Q3: LIKE 'abc%' 和 LIKE '%abc' 哪个快?**
A: 前缀匹配能走 B-tree 索引(快),后缀/中缀匹配只能全表扫(慢)。生产上要避免后缀模糊查询。
"""))

# ============== 2. DISTINCT ==============

cells.append(md("""## 2. DISTINCT — 去重

### 2.1 原理

**作用**:去掉 SELECT 结果中的重复行。

**内部实现**:
- 引擎在内存里建一个 hash set(或者排序后去重)
- 对每行的"完整投影列"做去重
- DISTINCT 作用在**所有** SELECT 列,不是某一列

**性能特征**:
- DISTINCT 在内存里跑,大结果集会消耗内存
- 千万级以上 DISTINCT 经常 OOM,生产上分两步:先 GROUP BY,再用 EXISTS 校验

### 2.2 基础案例"""))

cells.append(sql_run("""# 基础:去重查询(城市 + 年龄段的唯一组合)""",
"""SELECT DISTINCT city, age_group
FROM users
ORDER BY city, age_group
LIMIT 15"""))

cells.append(md("""### 2.3 进阶案例:COUNT(DISTINCT) 的微妙之处"""))

cells.append(sql_run("""# 进阶:COUNT(DISTINCT) 的不同位置""",
"""SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT user_id) AS unique_buyers,
    COUNT(DISTINCT order_id) AS unique_orders  -- 跟 COUNT(*) 一样
FROM orders WHERE status = 'completed'

-- 注意:COUNT(DISTINCT col) 是"对 col 去重后计数",跟 DISTINCT 关键字位置不同"""))

cells.append(md("""### 2.4 陷阱案例

**陷阱 1**:DISTINCT 跟 ORDER BY 一起用
```sql
-- DISTINCT 优先,ORDER BY 必须在 DISTINCT 列里
SELECT DISTINCT city FROM users ORDER BY register_date  -- 错!register_date 不在 SELECT 里
SELECT DISTINCT city FROM users ORDER BY city  -- 对
```

**陷阱 2**:DISTINCT 不能跟 COUNT 之外的聚合混用
```sql
-- 错:DISTINCT 跟 SUM 没意义
SELECT DISTINCT user_id, SUM(amount) FROM orders  -- 这是按 user_id 去重,但 SUM 还是聚合
-- 实际:对每个 user_id 取一行,然后 SUM 这一个 amount(等于 amount 本身)
```

### 2.5 面试 Q&A

**Q1: DISTINCT 和 GROUP BY 区别?**
A: 大多数情况下等价(都去重)。区别:DISTINCT 只能简单去重,GROUP BY 能配聚合。

**Q2: 千万级数据用 DISTINCT 会怎样?**
A: 内存可能炸。生产上常用 `APPROX_COUNT_DISTINCT`(HyperLogLog,误差 1-2%)。
"""))

# ============== 3. GROUP BY / HAVING / 聚合 ==============

cells.append(md("""## 3. GROUP BY / HAVING / 聚合函数

### 3.1 原理

**GROUP BY**:**分组**——把数据按指定列的"值"分组,每组变成"一行"。

**聚合函数**:对每组数据算一个值(SUM/AVG/COUNT/MIN/MAX)。

**执行流程**:
```
原始数据 -> 按 GROUP BY 列分组 -> 每组算聚合 -> 输出每组一行
```

**核心铁律**:**SELECT 里的非聚合列必须全部出现在 GROUP BY 里**(SQL 严格模式)。

### 3.2 基础案例:各渠道汇总"""))

cells.append(sql_run("""# 基础:各渠道用户数 + 订单数 + GMV + 客单价""",
"""SELECT
    u.channel,
    COUNT(DISTINCT u.user_id) AS user_cnt,
    COUNT(DISTINCT o.order_id) AS order_cnt,
    ROUND(SUM(o.amount), 2) AS gmv,
    ROUND(AVG(o.amount), 2) AS avg_order_amount
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND o.status = 'completed'
GROUP BY u.channel
ORDER BY gmv DESC"""))

cells.append(md("""### 3.3 进阶案例 1:多列分组(组合维度分析)"""))

cells.append(sql_run("""# 进阶 1:渠道 + 城市 双维度分组""",
"""SELECT
    u.channel,
    u.city,
    COUNT(DISTINCT u.user_id) AS user_cnt,
    ROUND(SUM(o.amount), 2) AS gmv
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND o.status = 'completed'
GROUP BY u.channel, u.city
HAVING COUNT(DISTINCT u.user_id) >= 50  -- 过滤用户数 >=50 的组
ORDER BY gmv DESC
LIMIT 15"""))

cells.append(md("""### 3.4 进阶案例 2:行转列思路(CASE WHEN + 聚合)

**业务**:看每个城市的订单状态分布(完成/退款/取消)"""))

cells.append(sql_run("""# 进阶 2:行转列(每城市订单状态分布)""",
"""SELECT
    u.city,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN o.status = 'completed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN o.status = 'refunded'  THEN 1 ELSE 0 END) AS refunded,
    SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    ROUND(100.0 * SUM(CASE WHEN o.status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS completed_pct
FROM orders o
JOIN users u ON o.user_id = u.user_id
GROUP BY u.city
ORDER BY total_orders DESC"""))

cells.append(md("""### 3.5 陷阱案例

**陷阱 1**:SELECT 里有非聚合列但 GROUP BY 没包含
```sql
-- 大部分数据库(MySQL 默认,SQLite 旧版)会"随意"选一个值,这是 bug 风险!
SELECT u.city, u.channel, SUM(o.amount)  -- city 和 channel 必须都在 GROUP BY
FROM orders o JOIN users u ON o.user_id = u.user_id
GROUP BY u.city  -- channel 漏了!
```

**陷阱 2**:WHERE 用了聚合
```sql
-- 错:WHERE 不能用聚合
SELECT channel, SUM(amount) FROM orders
WHERE SUM(amount) > 1000
GROUP BY channel

-- 对:HAVING 过滤聚合
SELECT channel, SUM(amount) FROM orders
GROUP BY channel
HAVING SUM(amount) > 1000
```

**陷阱 3**:COUNT(*) vs COUNT(col) vs COUNT(DISTINCT col)
- `COUNT(*)`:算行数(包括 NULL)
- `COUNT(col)`:算 col 非 NULL 的行数
- `COUNT(DISTINCT col)`:算 col 去重后非 NULL 的个数

### 3.6 面试 Q&A

**Q1: GROUP BY 后的 SELECT 列有什么限制?**
A: 必须是聚合函数或出现在 GROUP BY 里的列。否则在严格模式下报错,非严格模式下给任意值(坑!)。

**Q2: COUNT(*) 走索引吗?**
A: 如果有索引能"覆盖扫描"(如 COUNT 主键),就快;否则走全表扫。

**Q3: 怎么"行转列"?**
A: `MAX(CASE WHEN ... THEN val END) AS col` 或者 `FILTER (WHERE ...)` 子句(标准 SQL)。
"""))

# ============== 4. JOIN ==============

cells.append(md("""## 4. JOIN 全家福(大厂 80% 笔试题核心)

### 4.1 原理:三种 JOIN 算法

数据库在执行 JOIN 时,根据数据规模和索引情况选择不同算法:

| 算法 | 原理 | 适用场景 | 复杂度 |
|------|------|---------|--------|
| **Nested Loop Join** | 双层 for 循环,外层一行,内层扫一次 | 小表驱动大表、有索引 | O(N*M) |
| **Hash Join** | 把小表 hash 化,大表探测 | 等值 JOIN、大表 | O(N + M) |
| **Sort-Merge Join** | 两边都排序,然后归并 | 大表 + 有序输入 | O(N log N + M log M) |

**大厂铁律**:**小表驱动大表**——把行数少的表放在 JOIN 的右边(`LEFT JOIN` 主表在左)。

### 4.2 JOIN 类型速查"""))

cells.append(md("""
| 类型 | 行为 | 业务场景 |
|------|------|---------|
| `INNER JOIN` | 两边都有的才返回 | 已知两边都有对应数据 |
| `LEFT JOIN`(最常用) | 保留左表全部,右表没匹配补 NULL | 看左表维度下右表情况 |
| `RIGHT JOIN` | 保留右表全部 | 不推荐,改写为 LEFT JOIN |
| `FULL JOIN` | 两边都保留 | SQLite 不支持,Hive/Spark 支持 |
| `CROSS JOIN` | 笛卡尔积 | 谨慎,数据量爆炸 |
| `SELF JOIN` | 自己连自己 | 找上下行、找同期对比 |
"""))

cells.append(sql_run("""# 基础 INNER JOIN:用户 + 订单 + 商品(三表)""",
"""SELECT
    u.user_id,
    u.channel,
    p.category,
    COUNT(*) AS order_cnt,
    ROUND(SUM(o.amount), 2) AS gmv
FROM orders o
INNER JOIN users u ON o.user_id = u.user_id
INNER JOIN products p ON o.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY u.user_id, u.channel, p.category
ORDER BY gmv DESC
LIMIT 15"""))

cells.append(md("""### 4.3 进阶案例 1:LEFT JOIN + NULL 检测(找"无订单用户")"""))

cells.append(sql_run("""# 进阶 1:LEFT JOIN + IS NULL(找"下过浏览但没下过单"的用户)""",
"""SELECT
    COUNT(DISTINCT e.user_id) AS browse_only_users
FROM user_events e
LEFT JOIN orders o ON e.user_id = o.user_id AND o.status = 'completed'
WHERE o.order_id IS NULL  -- 没匹配到完成订单的用户"""))

cells.append(md("""### 4.4 进阶案例 2:SELF JOIN(找用户同期对比)"""))

cells.append(sql_run("""# 进阶 2:SELF JOIN 找"同日下单的不同用户对"
# 注意:实际场景里要用 LIMIT + 索引;这里取单日样本演示""",
"""-- 取某一日(2025-02-15)同城市同时段下过单的用户对
WITH one_day AS (
    SELECT u.user_id, u.city
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    WHERE o.status = 'completed'
      AND DATE(o.order_date) = '2025-02-15'
)
SELECT
    a.user_id AS user_a,
    b.user_id AS user_b,
    a.city
FROM one_day a
JOIN one_day b ON a.city = b.city AND a.user_id < b.user_id
ORDER BY a.city
LIMIT 10"""))

cells.append(md("""### 4.5 进阶案例 3:多表 JOIN 的写法选择

**业务**:用户 + 订单 + 商品,看各品类的用户来源渠道"""))

cells.append(sql_run("""# 进阶 3:多表 JOIN(用户 + 订单 + 商品 三表)""",
"""SELECT
    p.category,
    u.channel,
    COUNT(DISTINCT u.user_id) AS user_cnt,
    ROUND(SUM(o.amount), 2) AS gmv
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN products p ON o.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY p.category, u.channel
ORDER BY gmv DESC
LIMIT 15"""))

cells.append(md("""### 4.6 陷阱案例

**陷阱 1**:ON 条件和 WHERE 条件混用
```sql
-- LEFT JOIN 时,ON 里的过滤只影响"右表能不能连上",不会过滤左表
-- WHERE 里的过滤会同时影响两边

-- 例:找"有 completed 订单的 paid_search 用户"
-- 错写法(可能漏数据):
SELECT * FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE u.channel = 'paid_search' AND o.status = 'completed'

-- 对写法(过滤在 ON 里):
SELECT * FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND o.status = 'completed'
WHERE u.channel = 'paid_search'
-- 这两种结果在 INNER JOIN 里一样,在 LEFT JOIN 里可能不同!
```

**陷阱 2**:JOIN 出笛卡尔积
```sql
-- 错:忘记 JOIN 条件
SELECT * FROM users, orders  -- 5000 * 27811 = 1.4 亿行
-- 对:加 ON
SELECT * FROM users u JOIN orders o ON u.user_id = o.user_id
```

**陷阱 3**:JOIN 性能差
```sql
-- 大表 JOIN 大表,性能灾难
-- 优化思路:先过滤(下推),再 JOIN
SELECT * FROM (
    SELECT * FROM orders WHERE status = 'completed'
) o
JOIN (
    SELECT * FROM users WHERE channel = 'paid_search'
) u ON o.user_id = u.user_id
```

### 4.7 面试 Q&A

**Q1: LEFT JOIN 和 INNER JOIN 怎么选?**
A: 看业务。INNER JOIN 是"两边都有";LEFT JOIN 是"以左表为主,看右表情况"。运营分析 90% 用 LEFT JOIN。

**Q2: JOIN 3 张表,性能会差吗?**
A: 取决于数据量、是否有索引、JOIN 顺序。生产上会用 EXPLAIN 看执行计划,优化器会选最优顺序。

**Q3: 数据倾斜的 JOIN 怎么优化?**
A: 倾斜 key 加随机前缀打散,先局部 JOIN 再合并。或者用 map join(小表广播)。
"""))

# ============== 5. 子查询 ==============

cells.append(md("""## 5. 子查询:IN / EXISTS / 相关

### 5.1 原理

**子查询**:嵌套在主查询里的 SELECT。

**三类**:
1. **标量子查询**:返回单个值,用 `=` / `>` 等比较
2. **多行子查询**:返回多行,用 `IN` / `ANY` / `ALL`
3. **相关子查询**:子查询里引用外层表的列(性能差!)

**性能**:
- 非相关子查询:先算子查询,再算外层(优化器可能"半连接优化")
- 相关子查询:**外层每行都要跑一次子查询**,O(N*M),N 大时很慢
- **生产铁律**:能用 `JOIN` 替代子查询就用 JOIN;实在不行用**窗口函数**改写

### 5.2 基础案例:IN / NOT IN"""))

cells.append(sql_run("""# 基础 1:下过单的用户数(IN 写法)""",
"""SELECT COUNT(*) AS buyer_cnt
FROM users
WHERE user_id IN (SELECT DISTINCT user_id FROM orders)"""))

cells.append(sql_run("""# 基础 2:没下过单的用户数(NOT IN 写法)""",
"""SELECT COUNT(*) AS non_buyer_cnt
FROM users
WHERE user_id NOT IN (SELECT user_id FROM orders WHERE user_id IS NOT NULL)"""))

cells.append(md("""### 5.3 进阶案例 1:EXISTS(短路求值,大表推荐)"""))

cells.append(sql_run("""# 进阶 1:EXISTS 写法(子查询结果集大时更快)""",
"""-- EXISTS:子查询里只要找到一行匹配就停(短路)
SELECT COUNT(*) AS buyer_cnt
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.user_id
)"""))

cells.append(md("""### 5.4 进阶案例 2:相关子查询(每用户算自己的平均)"""))

cells.append(sql_run("""# 进阶 2:相关子查询 - 算每用户客单价(只看 completed)""",
"""SELECT
    o.user_id,
    ROUND((
        SELECT AVG(o2.amount)
        FROM orders o2
        WHERE o2.user_id = o.user_id
          AND o2.status = 'completed'
    ), 2) AS user_avg
FROM orders o
WHERE o.status = 'completed'
GROUP BY o.user_id
ORDER BY user_avg DESC
LIMIT 10"""))

cells.append(md("""### 5.5 陷阱案例:NOT IN + NULL 灾难

**反例**:
```sql
-- 错:子查询里有 NULL,NOT IN 返回 0 行!
SELECT * FROM users
WHERE user_id NOT IN (SELECT user_id FROM blacklist WHERE user_id IS NOT NULL)
-- 子查询返回:1, 2, 3, NULL
-- NOT IN (1, 2, 3, NULL) 永远为 NULL(没人能 NOT IN 一个含 NULL 的列表)
-- 结果:0 行

-- 对:NOT EXISTS
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM blacklist b WHERE b.user_id = u.user_id
)
```

### 5.6 进阶案例 3:用 JOIN 替代子查询(性能更好)"""))

cells.append(sql_run("""# 进阶 3a:子查询版(用户客单价 > 1000)""",
"""SELECT user_id, ROUND(avg_amount, 2) AS avg_amt
FROM (
    SELECT user_id, AVG(amount) AS avg_amount
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
) t
WHERE avg_amount > 1000
ORDER BY avg_amt DESC
LIMIT 10"""))

cells.append(sql_run("""# 进阶 3b:JOIN 改写版(优化器更容易处理)""",
"""SELECT o.user_id, AVG(o.amount) AS avg_amt
FROM orders o
WHERE o.status = 'completed'
GROUP BY o.user_id
HAVING AVG(o.amount) > 1000
ORDER BY avg_amt DESC
LIMIT 10"""))

cells.append(md("""### 5.7 面试 Q&A

**Q1: IN 和 EXISTS 怎么选?**
A: 子查询结果集**小**(< 1K)用 IN(简单可读);**大**用 EXISTS(短路求值)。

**Q2: 相关子查询性能差,怎么改写?**
A: 用 JOIN + GROUP BY,或者用窗口函数(本模块 1.2 重点)。

**Q3: NOT IN 遇到 NULL 怎么办?**
A: 必须改用 NOT EXISTS,或者确保子查询没 NULL(用 `WHERE col IS NOT NULL` 过滤)。

**Q4: 子查询和 CTE 区别?**
A: CTE(WITH)是"命名子查询",可读性更好,可以复用,可以引用其他 CTE。性能上等价。
"""))

# ============== 6. 练习题 + 答案 ==============

cells.append(md("""## 6. 练习题(6 道,大厂常考)

每题都标了"陷阱提示",**先想 5 分钟再看答案**。

### Q1(⭐):各城市用户数 Top 5

### Q2(⭐):客单价 Top 3 城市(只看 completed)

### Q3(⭐⭐):复购用户(下过 ≥2 单 completed),按订单数降序

### Q4(⭐⭐):购买过 `electronics` 的用户城市分布
> 提示:用 IN + 子查询

### Q5(⭐⭐⭐):用 LEFT JOIN 找出"只浏览从未购买"的用户数
> 提示:`IS NULL` 检测未匹配

### Q6(⭐⭐⭐):**反例陷阱题** — 找出"不在 blacklist 表的用户数"
> 提示:考虑 NULL 陷阱
"""))

cells.append(md("### 答案"))

cells.append(sql_run("""# Q1:各城市用户数 Top 5""",
"""SELECT city, COUNT(*) AS user_cnt
FROM users
GROUP BY city
ORDER BY user_cnt DESC
LIMIT 5"""))

cells.append(sql_run("""# Q2:客单价 Top 3 城市""",
"""SELECT u.city,
       ROUND(SUM(o.amount) * 1.0 / COUNT(o.order_id), 2) AS avg_order
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.status = 'completed'
GROUP BY u.city
ORDER BY avg_order DESC
LIMIT 3"""))

cells.append(sql_run("""# Q3:复购用户(>=2 单 completed)""",
"""SELECT user_id, COUNT(*) AS order_cnt
FROM orders
WHERE status = 'completed'
GROUP BY user_id
HAVING COUNT(*) >= 2
ORDER BY order_cnt DESC
LIMIT 10"""))

cells.append(sql_run("""# Q4:购买过 electronics 的用户城市分布""",
"""SELECT u.city, COUNT(DISTINCT u.user_id) AS user_cnt
FROM users u
WHERE u.user_id IN (
    SELECT o.user_id
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE p.category = 'electronics' AND o.status = 'completed'
)
GROUP BY u.city
ORDER BY user_cnt DESC"""))

cells.append(sql_run("""# Q5:只浏览从未购买的用户数(LEFT JOIN + IS NULL)""",
"""SELECT COUNT(DISTINCT e.user_id) AS browse_only_users
FROM user_events e
LEFT JOIN orders o ON e.user_id = o.user_id AND o.status = 'completed'
WHERE o.order_id IS NULL"""))

cells.append(sql_run("""# Q6:NULL 陷阱演示(用 EXISTS 安全做法)""",
"""-- 反例:有 NULL 的子查询,NOT IN 返回 0 行
-- SELECT * FROM users WHERE user_id NOT IN (1, 2, NULL)  -- 0 行!

-- 对:NOT EXISTS
SELECT COUNT(*) AS safe_count
FROM users u
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.user_id AND o.status = 'completed')"""))

# ============== 7. 小结 + 速查表 ==============

cells.append(md("""## 7. 小结 + 速查表

### 7.1 速查表(贴墙)

| 需求 | 写法 |
|------|------|
| 过滤行 | `WHERE col = ...` |
| 多条件 | `WHERE a=1 AND (b=2 OR c=3)` |
| 范围 | `WHERE col BETWEEN x AND y` |
| 集合 | `WHERE col IN (a, b, c)` |
| 模糊 | `WHERE col LIKE 'abc%'` |
| 空值 | `WHERE col IS NULL`(不用 = NULL) |
| 排序 | `ORDER BY col ASC/DESC` |
| 多列排序 | `ORDER BY col1, col2 DESC` |
| 分页 | `LIMIT n OFFSET m` |
| 去重 | `DISTINCT` / `COUNT(DISTINCT col)` |
| 分组 | `GROUP BY col1, col2` |
| 过滤组 | `HAVING agg() > ...` |
| 内连 | `INNER JOIN` |
| 左连(常用) | `LEFT JOIN` |
| 存在性 | `WHERE EXISTS (SELECT 1 ...)` |

### 7.2 面试必背

**Q: SQL 执行顺序?**
A: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT

**Q: WHERE vs HAVING?**
A: WHERE 过滤行(分组前,不能用聚合);HAVING 过滤组(分组后,能用聚合)

**Q: JOIN 三种算法?**
A: Nested Loop(小表驱动大表)、Hash Join(等值大表)、Sort-Merge(大表 + 有序)

**Q: NOT IN 的 NULL 陷阱?**
A: 子查询含 NULL 时,NOT IN 返回 0 行。改用 NOT EXISTS。

**Q: 大表 JOIN 怎么优化?**
A: 小表驱动大表 + 过滤下推 + 联合索引 + 避免 SELECT *

### 7.3 自测清单

- [ ] 能口述 SQL 执行顺序
- [ ] 解释清楚 WHERE vs HAVING
- [ ] 知道 LEFT JOIN 的 ON 和 WHERE 区别
- [ ] 能用 IN / EXISTS / JOIN 三种方式写"找某类用户"
- [ ] 知道 NOT IN 的 NULL 陷阱
- [ ] 能解释三种 JOIN 算法的适用场景

**全部 ✅ 之后可以推进到模块 1.2(窗口函数)或直接进 W2。**
"""))


# ============== 写出 .ipynb ==============

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.11",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"已生成: {OUT}")
print(f"Cell 总数: {len(cells)}")
print(f"文件大小: {OUT.stat().st_size / 1024:.1f} KB")

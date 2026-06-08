# -*- coding: utf-8 -*-
"""
build_notebook_03_v2.py — 03_cte_and_business.ipynb v2(加深版)
================================================================

CTE(WITH 子句)+ 5 大业务案例(留存/漏斗/连续登录/RFM/行为路径)
按 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "03_cte_and_business.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text if isinstance(text, list) else [text]}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text if isinstance(text, list) else [text]}


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

cells.append(md("""# 模块 1.3 — CTE + 业务案例(加深版)

> CTE(WITH 子句)是**大厂 SQL 笔试/工作的核心可读性工具**。
> 本节把模块 1.1/1.2 的能力组合起来,做 5 个真实业务案例,每个都按 5 段结构。

## 本节大纲
- **0. 原理总览**:CTE 是什么 + 跟子查询对比
- **1. CTE 基础**:原理 + 4 案例(单/多/链式/命名)
- **2. 递归 CTE**:原理 + 3 案例(日期序列/连续登录/树形)
- **3. 业务案例 1:留存率** - 原理 + 4 案例
- **4. 业务案例 2:漏斗分析** - 原理 + 3 案例
- **5. 业务案例 3:连续登录** - 原理 + 3 案例
- **6. 业务案例 4:RFM 客户分群** - 原理 + 3 案例
- **7. 业务案例 5:行为路径** - 原理 + 2 案例
- **8. 综合练习题 + 答案**
- **9. 小结 + 速查表**

## 学习建议
- 业务案例是大厂面试核心(留存/漏斗/RFM 必问),多花时间
- 每个案例先自己想思路,再看代码
- 跑通 cell 后,**试着改 SQL 套到自己的业务上**
"""))

cells.append(py_run("""# 数据库连接
import sqlite3
import pandas as pd
from pathlib import Path

DB = Path('../data/ecommerce.db').resolve()
conn = sqlite3.connect(DB)
print('Connected to', DB)"""))

# ============== 0. 原理总览 ==============

cells.append(md("""## 0. 原理总览:CTE 是什么,跟子查询比有什么不同

### 0.1 CTE 的定义

**CTE(Common Table Expression)**:用 `WITH` 把子查询抽出来,起个名字,像临时表一样在主查询里用。

**语法**:
```sql
WITH cte_name AS (
    SELECT ... FROM ...
)
SELECT * FROM cte_name;
```

### 0.2 CTE vs 子查询 vs 临时表

| 维度 | 子查询 | CTE(WITH) | 临时表 |
|------|--------|-----------|--------|
| 可读性 | 3 层嵌套就晕 | **高**(像命名函数) | 高 |
| 复用 | 不能 | 同一查询内可多次引用 | 多查询都能用 |
| 调试 | 难(每层要重跑) | 简单(每步单独跑) | 简单 |
| 跨查询 | 不能 | 不能(每次查询都要重写) | 能 |
| 性能 | 优化器可能重写 | 等价(优化器可能"内联") | 物化,可能更慢(老版本) |
| 跨数据库 | ✅ | PostgreSQL 12+/MySQL 8.0+/Hive/Spark | ✅ |

**大厂铁律**:**3 层嵌套以上**必须改写成 CTE,否则维护灾难。

### 0.3 CTE 的内部执行

- **PostgreSQL 12+ / MySQL 8.0+**:CTE 默认会**物化**(先算 CTE 一次,再多次引用)
- **SQLite / 旧版 MySQL**:CTE 可能被**内联**(优化器把 CTE 展开成子查询)
- **大表上**:物化更快(只算一次);小表上内联差不多

### 0.4 实战口诀

- "**先分步,再组合**" — 每个 CTE 是一个"加工步骤"
- "**命名要有业务意义**" — `user_gmv` 比 `t1` 好
- "**超过 5 个 CTE 就该拆成多个查询**" — 太多反而难读
"""))

# ============== 1. CTE 基础 ==============

cells.append(md("""## 1. CTE 基础 + 多 CTE 链式

### 1.1 原理

**单 CTE** = 一个命名子查询。

**多 CTE 链式** = 数据"流水线"加工:原始 -> 步骤1 -> 步骤2 -> ... -> 最终输出。

**CTE 之间的引用关系**:
- 后面的 CTE 可以引用前面的 CTE
- 同一层 CTE 名字不重复
- CTE 内部**不能**直接用 ORDER BY(部分数据库允许,但标准不支持)

### 1.2 基础案例:单 CTE

**业务**:把"完成订单用户"先抽出来,再算他们的总 GMV"""))

cells.append(sql_run("""# 基础:单 CTE""",
"""WITH buyers AS (
    SELECT DISTINCT user_id
    FROM orders WHERE status = 'completed'
)
SELECT COUNT(*) AS buyer_cnt FROM buyers"""))

cells.append(md("""### 1.3 进阶案例 1:多 CTE 链式(从原始到结论)

**业务**:找"头部 20% 用户"的渠道分布"""))

cells.append(sql_run("""# 进阶 1:多 CTE 链式(原始 -> 用户 GMV -> 头部用户 -> 渠道分布)""",
"""WITH
-- Step 1:每个用户 GMV
user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
-- Step 2:第 80 百分位的 GMV 阈值
gmv_threshold AS (
    SELECT gmv AS p80
    FROM user_gmv
    ORDER BY gmv
    LIMIT 1 OFFSET (SELECT CAST(COUNT(*) * 0.2 AS INTEGER) FROM user_gmv)
),
-- Step 3:头部用户(GMV >= 阈值)
top_users AS (
    SELECT user_id, gmv
    FROM user_gmv, gmv_threshold
    WHERE user_gmv.gmv >= gmv_threshold.p80
)
-- Step 4:头部用户的渠道分布
SELECT u.channel, COUNT(*) AS user_cnt
FROM top_users t
JOIN users u ON t.user_id = u.user_id
GROUP BY u.channel
ORDER BY user_cnt DESC"""))

cells.append(md("""### 1.4 进阶案例 2:CTE 复用(同一查询内多次引用)

**业务**:算"用户贡献"占该渠道总 GMV 的比例"""))

cells.append(sql_run("""# 进阶 2:CTE 复用(同一查询内多次引用同一 CTE)""",
"""WITH
user_gmv AS (
    SELECT u.user_id, u.channel, SUM(o.amount) AS gmv
    FROM orders o JOIN users u ON o.user_id = u.user_id
    WHERE o.status = 'completed'
    GROUP BY u.user_id, u.channel
),
channel_total AS (
    SELECT channel, SUM(gmv) AS channel_gmv
    FROM user_gmv
    GROUP BY channel
)
-- 每用户贡献 / 渠道总 GMV
SELECT u.user_id, u.channel, u.gmv, ct.channel_gmv,
    ROUND(100.0 * u.gmv / ct.channel_gmv, 2) AS pct_of_channel
FROM user_gmv u
JOIN channel_total ct ON u.channel = ct.channel
ORDER BY u.channel, pct_of_channel DESC
LIMIT 15"""))

cells.append(md("""### 1.5 陷阱案例

**陷阱 1**:CTE 名字不能跨层重复
```sql
-- 错
WITH a AS (SELECT 1), a AS (SELECT 2)  -- SQL 错
```

**陷阱 2**:CTE 里用 ORDER BY(部分数据库报错)
```sql
-- 错:CTE 内部不能直接 ORDER BY
WITH top_users AS (
    SELECT * FROM users ORDER BY register_date  -- 报错
)
```

**陷阱 3**:CTE 里的 NULL 处理要小心
```sql
-- 如果 CTE 里有 NULL 过滤,后续引用会丢失这些行
WITH active AS (SELECT user_id FROM orders WHERE amount > 0)
SELECT COUNT(*) FROM users WHERE user_id NOT IN (SELECT user_id FROM active)
-- 如果 active 有 NULL,NOT IN 返回 0 行
```

### 1.6 面试 Q&A

**Q1: CTE 和视图(View)区别?**
A: 视图是持久化的命名查询,跨查询可用;CTE 是查询内的临时命名,只在该查询内可用。

**Q2: CTE 会让查询变慢吗?**
A: 不会。PostgreSQL 12+ / MySQL 8.0+ 的 CTE 会物化(只算一次),所以**多次引用时比子查询快**。

**Q3: 大表上 CTE 会爆内存吗?**
A: 会,如果 CTE 本身产生几十亿行,物化会占内存。生产上对大 CTE 用 `WITH ... MATERIALIZED` 显式控制。
"""))

# ============== 2. 递归 CTE ==============

cells.append(md("""## 2. 递归 CTE(高级特性)

### 2.1 原理

**递归 CTE** 用 `WITH RECURSIVE`,由两部分组成:
1. **锚点查询**(Anchor):初始行集
2. **递归部分**:基于上一轮的结果,迭代生成新行
3. 直到递归部分返回空集,**终止**

**语法**:
```sql
WITH RECURSIVE cte AS (
    -- 锚点
    SELECT ...
    UNION ALL
    -- 递归
    SELECT ... FROM cte WHERE ...
)
SELECT * FROM cte;
```

**适用场景**:
- 日期序列生成
- 树形结构(组织架构、评论树)
- 图遍历(找 N 度好友)
- 连续登录天数
- BOM(物料清单)展开

### 2.2 基础案例:生成连续日期序列"""))

cells.append(sql_run("""# 基础:用递归 CTE 生成 2025-01-01 到 2025-01-31 的日期序列
# 业务场景:补齐缺失日期,算日活连续曲线""",
"""WITH RECURSIVE date_range AS (
    SELECT DATE('2025-01-01') AS dt
    UNION ALL
    SELECT DATE(dt, '+1 day') FROM date_range WHERE dt < '2025-01-31'
)
SELECT dt FROM date_range"""))

cells.append(md("""### 2.3 进阶案例 1:连续登录天数(简化版)

**业务**:用递归找每个用户的最长连续活跃段"""))

cells.append(sql_run("""# 进阶 1:用递归找某用户的最长连续活跃段""",
"""WITH RECURSIVE
user_days AS (
    SELECT DISTINCT user_id, DATE(event_time) AS dt
    FROM user_events WHERE event_type = 'pv'
),
-- 递归:从最早一天开始,找下一天
walk AS (
    SELECT user_id, dt, dt AS chain_start, 1 AS chain_len
    FROM user_days WHERE user_id = 1
    UNION ALL
    SELECT w.user_id, d.dt, w.chain_start, w.chain_len + 1
    FROM walk w
    JOIN user_days d ON d.user_id = w.user_id
    WHERE d.dt = DATE(w.dt, '+1 day')
)
SELECT chain_start, MAX(chain_len) AS max_len
FROM walk
GROUP BY chain_start
ORDER BY max_len DESC
LIMIT 5"""))

cells.append(md("""### 2.4 进阶案例 2:树形结构(组织架构遍历)

**业务**:找某员工的所有下属(模拟)"""))

cells.append(sql_run("""# 进阶 2:递归遍历树(模拟组织架构)""",
"""WITH RECURSIVE
-- 锚点:某员工
org(node, parent) AS (
    VALUES
        (1, NULL), (2, 1), (3, 1), (4, 2), (5, 2), (6, 3), (7, 6)
),
-- 递归:从某节点往下找所有下属
subtree AS (
    SELECT node, parent, 1 AS depth FROM org WHERE node = 1
    UNION ALL
    SELECT o.node, o.parent, s.depth + 1
    FROM org o JOIN subtree s ON o.parent = s.node
)
SELECT node, parent, depth FROM subtree
ORDER BY depth, node"""))

cells.append(md("""### 2.5 陷阱案例:递归必须有终止条件!

**反例**(没终止条件,死循环):
```sql
WITH RECURSIVE bad AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM bad  -- 没有 WHERE 终止!
)
SELECT * FROM bad  -- 死循环
```

**必须**:
```sql
WITH RECURSIVE good AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM good WHERE n < 100  -- 明确终止
)
SELECT * FROM good
```

### 2.6 面试 Q&A

**Q1: 递归 CTE 在生产中用得多吗?**
A: 不少!日期序列、连续段、组织架构、评论树都是常见场景。

**Q2: 递归 CTE 性能?**
A: 每轮迭代扫一次,O(深度)。深度 10 以内基本秒级,深度 100+ 就要考虑优化(加索引、限制最大深度)。

**Q3: 递归 vs 循环表 + JOIN?**
A: 递归简单直观,适合"找 N 步以内";大深度用循环表 + 自关联更稳定。
"""))

# ============== 3. 业务案例 1:留存率 ==============

cells.append(md("""## 3. 业务案例 1:N 日留存率(大厂面试必问)

### 3.1 原理

**留存率定义**:在某日新注册/新活跃的用户中,第 N 天还活跃的比例。

**核心思路**:
1. 确定"新用户"集合 + 起始日 D0
2. 找这些用户在 D0 之后 N 天的活跃情况
3. **留存数 / 总新用户数 = 留存率**

**SQL 实现套路**(两个流派):
- **流派 A**:D0 + 后续活跃日 JOIN,数 distinct
- **流派 B**:用窗口函数 `LAG/LEAD` 找下次访问,判断差值

### 3.2 基础案例:1 日留存"""))

cells.append(sql_run("""# 基础:D1 留存(简化版)""",
"""WITH
-- 新用户及注册日
new_users AS (
    SELECT user_id, DATE(register_date) AS d0
    FROM users
    WHERE register_date >= '2025-01-01'
),
-- 每个新用户是否在 D0+1 活跃
d1_check AS (
    SELECT n.user_id, n.d0,
           MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+1 day') THEN 1 ELSE 0 END) AS d1_active
    FROM new_users n
    LEFT JOIN user_events e ON e.user_id = n.user_id
    GROUP BY n.user_id, n.d0
)
SELECT
    COUNT(*) AS new_user_cnt,
    SUM(d1_active) AS d1_retained,
    ROUND(100.0 * SUM(d1_active) / COUNT(*), 2) AS d1_retention_pct
FROM d1_check"""))

cells.append(md("""### 3.3 进阶案例 1:N 日留存(D1 + D3 + D7 + D30)"""))

cells.append(sql_run("""# 进阶 1:N 日留存(D1/D3/D7/D30 同时算)""",
"""WITH
new_users AS (
    SELECT user_id, DATE(register_date) AS d0
    FROM users WHERE register_date >= '2025-01-01'
),
retention AS (
    SELECT n.user_id, n.d0,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+1 day')  THEN 1 ELSE 0 END) AS d1,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+3 day')  THEN 1 ELSE 0 END) AS d3,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+7 day')  THEN 1 ELSE 0 END) AS d7,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+30 day') THEN 1 ELSE 0 END) AS d30
    FROM new_users n
    LEFT JOIN user_events e ON e.user_id = n.user_id
    GROUP BY n.user_id, n.d0
)
SELECT
    COUNT(*) AS new_user_cnt,
    ROUND(100.0 * SUM(d1)  / COUNT(*), 2) AS d1_pct,
    ROUND(100.0 * SUM(d3)  / COUNT(*), 2) AS d3_pct,
    ROUND(100.0 * SUM(d7)  / COUNT(*), 2) AS d7_pct,
    ROUND(100.0 * SUM(d30) / COUNT(*), 2) AS d30_pct
FROM retention"""))

cells.append(md("""### 3.4 进阶案例 2:按渠道拆留存(精细化运营)"""))

cells.append(sql_run("""# 进阶 2:按渠道拆 D7 留存(看哪个渠道拉来的用户更优质)""",
"""WITH
new_users AS (
    SELECT u.user_id, u.channel, DATE(u.register_date) AS d0
    FROM users u WHERE u.register_date >= '2025-01-01'
),
d7_check AS (
    SELECT n.user_id, n.channel, n.d0,
           MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+7 day') THEN 1 ELSE 0 END) AS d7_active
    FROM new_users n
    LEFT JOIN user_events e ON e.user_id = n.user_id
    GROUP BY n.user_id, n.channel, n.d0
)
SELECT channel,
    COUNT(*) AS new_users,
    SUM(d7_active) AS d7_retained,
    ROUND(100.0 * SUM(d7_active) / COUNT(*), 2) AS d7_retention_pct
FROM d7_check
GROUP BY channel
ORDER BY d7_retention_pct DESC"""))

cells.append(md("""### 3.5 进阶案例 3:周留存曲线(D1/D3/D7/D14/D28)"""))

cells.append(sql_run("""# 进阶 3:周留存曲线(看新用户 4 周内的衰减)""",
"""WITH
new_users AS (
    SELECT user_id, DATE(register_date) AS d0
    FROM users WHERE register_date >= '2025-01-01'
),
retention AS (
    SELECT n.user_id, n.d0,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+1 day')  THEN 1 ELSE 0 END) AS d1,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+7 day')  THEN 1 ELSE 0 END) AS d7,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+14 day') THEN 1 ELSE 0 END) AS d14,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+28 day') THEN 1 ELSE 0 END) AS d28
    FROM new_users n
    LEFT JOIN user_events e ON e.user_id = n.user_id
    GROUP BY n.user_id, n.d0
)
SELECT
    ROUND(100.0 * SUM(d1)  / COUNT(*), 2) AS d1,
    ROUND(100.0 * SUM(d7)  / COUNT(*), 2) AS d7,
    ROUND(100.0 * SUM(d14) / COUNT(*), 2) AS d14,
    ROUND(100.0 * SUM(d28) / COUNT(*), 2) AS d28,
    -- 衰减率(D7 流失 / D1 留存)
    ROUND(100.0 * (SUM(d1) - SUM(d7)) / NULLIF(SUM(d1), 0), 2) AS d1_to_d7_churn
FROM retention"""))

cells.append(md("""### 3.6 陷阱案例

**陷阱 1**:D0 那天"新用户"口径不清
```sql
-- 错:把"当天下过单"当新用户(会重复计数)
SELECT user_id FROM orders WHERE DATE(order_date) = '2025-02-15'

-- 对:用注册日(D0)定义新用户
SELECT user_id FROM users WHERE DATE(register_date) = '2025-02-15'
```

**陷阱 2**:活跃口径不一致
- D1 留存 = 第 1+1=2 天的活跃?还是 D0+1 那天活跃?
- **生产中要明确口径**:通常是 D0+1 那天(注册次日)

**陷阱 3**:留存率的分母
- 是"D0 新用户数",还是"截至今天还有效的用户数"(扣流失)
- 一般用前者(包含已流失),更直观

### 3.7 面试 Q&A

**Q1: D7 留存怎么算?**
A: 找 D0 注册的用户,看 D0+7 那天是否活跃(浏览/加购/购买都算)。`SUM(d7_active) / COUNT(总新用户)`。

**Q2: 留存率突然下降,怎么排查?**
A: 1. 按渠道拆(某个渠道质量问题);2. 按时间拆(某天注册集中低);3. 看产品改版(可能是注册流程变了);4. 看数据完整性(埋点丢失)。

**Q3: LAG/LEAD 算留存和 JOIN 算留存哪个好?**
A: 千万级用 LAG/LEAD(性能好);中小数据用 JOIN 简单直观。生产看团队习惯。
"""))

# ============== 4. 业务案例 2:漏斗分析 ==============

cells.append(md("""## 4. 业务案例 2:漏斗分析(电商核心)

### 4.1 原理

**漏斗**:用户在多步操作中的转化情况。常见:浏览 -> 加购 -> 收藏 -> 购买。

**两种漏斗**:
- **独立漏斗**:用户只要做过这步就算转化(不管顺序)
- **严格漏斗**:用户必须按顺序做(浏览 -> 加购才算)

**转化率公式**:
- 步骤转化率 = 步骤 N 人数 / 步骤 N-1 人数
- 总体转化率 = 末步人数 / 首步人数

### 4.2 基础案例:独立漏斗(快速版)"""))

cells.append(sql_run("""# 基础:4 步独立漏斗(浏览/加购/收藏/购买)""",
"""WITH
user_funnel AS (
    SELECT user_id,
        MAX(CASE WHEN event_type = 'pv'       THEN 1 ELSE 0 END) AS did_pv,
        MAX(CASE WHEN event_type = 'cart'     THEN 1 ELSE 0 END) AS did_cart,
        MAX(CASE WHEN event_type = 'favorite' THEN 1 ELSE 0 END) AS did_fav,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS did_purchase
    FROM user_events
    GROUP BY user_id
)
SELECT
    SUM(did_pv)       AS step1_pv,
    SUM(did_cart)     AS step2_cart,
    SUM(did_fav)      AS step3_fav,
    SUM(did_purchase) AS step4_purchase,
    ROUND(100.0 * SUM(did_cart)     / SUM(did_pv), 2)       AS pv_to_cart,
    ROUND(100.0 * SUM(did_fav)      / SUM(did_cart), 2)    AS cart_to_fav,
    ROUND(100.0 * SUM(did_purchase) / SUM(did_fav), 2)     AS fav_to_purchase,
    ROUND(100.0 * SUM(did_purchase) / SUM(did_pv), 2)       AS overall_pct
FROM user_funnel"""))

cells.append(md("""### 4.3 进阶案例 1:每日漏斗趋势

**业务**:看漏斗每天的转化情况(找异常天)"""))

cells.append(sql_run("""# 进阶 1:每日漏斗趋势""",
"""WITH
daily_funnel AS (
    SELECT
        DATE(event_time) AS dt,
        MAX(CASE WHEN event_type = 'pv'       THEN 1 ELSE 0 END) AS did_pv,
        MAX(CASE WHEN event_type = 'cart'     THEN 1 ELSE 0 END) AS did_cart,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS did_purchase
    FROM user_events
    GROUP BY DATE(event_time), user_id
)
SELECT dt,
    SUM(did_pv) AS pv_users,
    SUM(did_cart) AS cart_users,
    SUM(did_purchase) AS purchase_users,
    ROUND(100.0 * SUM(did_cart) / NULLIF(SUM(did_pv), 0), 2) AS pv_to_cart_pct
FROM daily_funnel
GROUP BY dt
ORDER BY dt
LIMIT 10"""))

cells.append(md("""### 4.4 进阶案例 2:严格漏斗(按时序)

**业务**:严格"先 pv 后 cart"的转化率(排除掉"看完直接购买"的情况)"""))

cells.append(sql_run("""# 进阶 2:严格漏斗(用户必须有 pv 之后才 cart 的事件)""",
"""WITH
events_with_seq AS (
    SELECT user_id, event_type, event_time,
        ROW_NUMBER() OVER (PARTITION BY user_id, event_type ORDER BY event_time) AS seq
    FROM user_events
    WHERE event_type IN ('pv', 'cart', 'purchase')
),
pv_then_cart AS (
    SELECT a.user_id
    FROM events_with_seq a
    JOIN events_with_seq b ON a.user_id = b.user_id AND a.seq = b.seq
    WHERE a.event_type = 'pv' AND b.event_type = 'cart'
      AND b.event_time > a.event_time
),
cart_then_purchase AS (
    SELECT a.user_id
    FROM events_with_seq a
    JOIN events_with_seq b ON a.user_id = b.user_id AND a.seq = b.seq
    WHERE a.event_type = 'cart' AND b.event_type = 'purchase'
      AND b.event_time > a.event_time
)
SELECT
    (SELECT COUNT(DISTINCT user_id) FROM events_with_seq WHERE event_type = 'pv') AS step1_pv,
    (SELECT COUNT(*) FROM pv_then_cart) AS step2_pv_to_cart,
    (SELECT COUNT(*) FROM cart_then_purchase) AS step3_cart_to_purchase,
    (SELECT COUNT(DISTINCT user_id) FROM events_with_seq WHERE event_type = 'purchase') AS step3_purchase"""))

cells.append(md("""### 4.5 陷阱案例

**陷阱 1**:分子分母搞反
```sql
-- 错:把"末步"当分母
pv_to_cart_pct = cart_users / purchase_users  -- 错!
-- 对:上一步 / 当前步
pv_to_cart_pct = cart_users / pv_users  -- 对
```

**陷阱 2**:时间窗口不明确
- "30 天转化漏斗"是"30 天内完成所有步骤"还是"每步都在 30 天内"?
- **生产中要明确口径**

### 4.6 面试 Q&A

**Q1: 独立漏斗 vs 严格漏斗用哪个?**
A: 业务早期用独立(看大盘);精细化运营用严格(看路径)。

**Q2: 漏斗哪一步流失最大,怎么改进?**
A: 看"步骤转化率",最低的那步是瓶颈。改进方向:UX 优化、促销引导、推荐算法。

**Q3: 大表漏斗怎么算?**
A: 1) 用宽表预计算;2) 用 Spark SQL 跑;3) 漏斗步数大时用 DAG 拆解。
"""))

# ============== 5. 业务案例 3:连续登录 ==============

cells.append(md("""## 5. 业务案例 3:连续登录(Gaps and Islands)

### 5.1 原理

**问题**:给定用户的活跃日期,找最长连续段。

**经典解法 Gaps and Islands**:
1. 提每个用户的不重复活跃日
2. 用 `LAG` 算与前一日的差
3. 差 = 1 连续,差 > 1 开新段
4. 用 `SUM(CASE WHEN gap > 1 THEN 1 END) OVER` 给段编号
5. 按段分组算每段长度

### 5.2 基础案例:每用户最长连续活跃"""))

cells.append(sql_run("""# 基础:每用户最长连续活跃天数(Gaps and Islands)""",
"""WITH
user_days AS (
    SELECT DISTINCT user_id, DATE(event_time) AS dt
    FROM user_events WHERE event_type = 'pv'
),
with_gap AS (
    SELECT user_id, dt,
        LAG(dt) OVER (PARTITION BY user_id ORDER BY dt) AS prev_dt,
        julianday(dt) - julianday(LAG(dt) OVER (PARTITION BY user_id ORDER BY dt)) AS gap
    FROM user_days
),
with_streak AS (
    SELECT user_id, dt,
        SUM(CASE WHEN gap IS NULL OR gap > 1 THEN 1 ELSE 0 END)
            OVER (PARTITION BY user_id ORDER BY dt) AS streak_id
    FROM with_gap
)
SELECT user_id, MAX(streak_len) AS max_consecutive
FROM (
    SELECT user_id, streak_id, COUNT(*) AS streak_len
    FROM with_streak
    GROUP BY user_id, streak_id
)
GROUP BY user_id
HAVING max_consecutive >= 5
ORDER BY max_consecutive DESC
LIMIT 15"""))

cells.append(md("""### 5.3 进阶案例 1:连续登录用户数(每日)"""))

cells.append(sql_run("""# 进阶 1:每天"连续登录 >= 7 天"的用户数""",
"""WITH
user_days AS (
    SELECT DISTINCT user_id, DATE(event_time) AS dt
    FROM user_events WHERE event_type = 'pv'
),
with_gap AS (
    SELECT user_id, dt,
        LAG(dt) OVER (PARTITION BY user_id ORDER BY dt) AS prev_dt,
        julianday(dt) - julianday(LAG(dt) OVER (PARTITION BY user_id ORDER BY dt)) AS gap
    FROM user_days
),
with_streak AS (
    SELECT user_id, dt,
        SUM(CASE WHEN gap IS NULL OR gap > 1 THEN 1 ELSE 0 END)
            OVER (PARTITION BY user_id ORDER BY dt) AS streak_id
    FROM with_gap
),
streak_len AS (
    SELECT user_id, dt, streak_id,
        COUNT(*) OVER (PARTITION BY user_id, streak_id) AS streak_len
    FROM with_streak
)
SELECT dt, COUNT(*) AS active_7d_plus_users
FROM streak_len
WHERE streak_len >= 7
GROUP BY dt
ORDER BY dt
LIMIT 10"""))

cells.append(md("""### 5.4 进阶案例 2:沉默用户识别

**业务**:90 天未活跃、但历史 GMV Top 20% 的用户(高价值待召回)"""))

cells.append(sql_run("""# 进阶 2:沉默用户召回名单(90+ 天无单 + GMV Top 20%)""",
"""WITH
user_gmv AS (
    SELECT user_id, MAX(order_date) AS last_order, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
gmv_threshold AS (
    SELECT gmv AS p80 FROM user_gmv
    ORDER BY gmv
    LIMIT 1 OFFSET (SELECT CAST(COUNT(*) * 0.2 AS INTEGER) FROM user_gmv)
)
SELECT
    COUNT(*) AS recall_candidates,
    ROUND(AVG(gmv), 2) AS avg_gmv
FROM user_gmv, gmv_threshold
WHERE julianday('2025-04-01') - julianday(last_order) > 90
  AND gmv >= gmv_threshold.p80"""))

cells.append(md("""### 5.5 陷阱案例

**陷阱 1**:`LAG` 默认 NULL(第一行没前一行)
```sql
-- 用 CASE WHEN prev_dt IS NULL OR gap > 1 才是"新段开始"
SUM(CASE WHEN gap IS NULL OR gap > 1 THEN 1 ELSE 0 END) OVER (...)
```

**陷阱 2**:日期不是连续序列时,LAG 算的 gap > 1
- 数据有缺失日:gap = 1 还是不连续?看业务定义
- 严格意义:有 gap = 1 就是连续,有 > 1 就开新段

### 5.6 面试 Q&A

**Q1: Gaps and Islands 的核心思路?**
A: LAG 算 gap + 段编号 + 分组聚合。

**Q2: 连续登录 7 天,这个"7"怎么定义?**
A: 严格定义:中间 6 天不间断("7" = 7 个不同日);松定义:7 天内至少 5 天活跃。看业务。

**Q3: 大表上 Gaps and Islands 慢?**
A: 用递归 CTE 替代窗口函数,或者预计算到宽表。
"""))

# ============== 6. 业务案例 4:RFM 客户分群 ==============

cells.append(md("""## 6. 业务案例 4:RFM 客户分群(经典模型)

### 6.1 原理

**RFM** = Recency(最近消费) + Frequency(频次) + Monetary(金额)

**打分方式**:
- R:越近越好,小天数高分(用 NTILE DESC)
- F:越多越好
- M:越多越好
- 各维度打 1-5 分(可用 NTILE 5)

**8 群划分**:
| R | F | M | 群名 |
|---|---|---|------|
| 高 | 高 | 高 | 重要价值(黄金客户) |
| 高 | 高 | 低 | 重要发展 |
| 高 | 低 | 高 | 重要发展_低频 |
| 高 | 低 | 低 | 新客户 |
| 低 | 高 | 高 | 重要保持 |
| 低 | 高 | 低 | 一般保持 |
| 低 | 低 | 高 | 重要挽留 |
| 低 | 低 | 低 | 流失客户 |

### 6.2 基础案例:完整 RFM 8 群 + 占比 + GMV 贡献"""))

cells.append(sql_run("""# 基础:完整 RFM 8 群(打分 + 群名 + 占比 + GMV 贡献)""",
"""WITH
rfm AS (
    SELECT
        user_id,
        CAST(julianday('2025-04-01') - julianday(MAX(order_date)) AS INTEGER) AS r,
        COUNT(*) AS f,
        ROUND(SUM(amount), 2) AS m
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
scored AS (
    SELECT *,
        NTILE(2) OVER (ORDER BY r DESC) AS r_high,  -- 1=近, 2=远
        NTILE(2) OVER (ORDER BY f) AS f_high,
        NTILE(2) OVER (ORDER BY m) AS m_high
    FROM rfm
),
grouped AS (
    SELECT
        CASE
            WHEN r_high=1 AND f_high=1 AND m_high=1 THEN 'A_重要价值'
            WHEN r_high=1 AND f_high=1 AND m_high=2 THEN 'B_重要发展'
            WHEN r_high=2 AND f_high=1 AND m_high=1 THEN 'C_重要保持'
            WHEN r_high=1 AND f_high=2 AND m_high=1 THEN 'D_发展_高客单'
            WHEN r_high=2 AND f_high=2 AND m_high=1 THEN 'E_挽留'
            WHEN r_high=1 AND f_high=2 AND m_high=2 THEN 'F_新客'
            WHEN r_high=2 AND f_high=1 AND m_high=2 THEN 'G_一般保持'
            ELSE 'H_流失'
        END AS segment,
        m
    FROM scored
)
SELECT
    segment,
    COUNT(*) AS user_cnt,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS user_pct,
    ROUND(SUM(m), 2) AS total_gmv,
    ROUND(100.0 * SUM(m) / SUM(SUM(m)) OVER (), 2) AS gmv_pct
FROM grouped
GROUP BY segment
ORDER BY gmv_pct DESC"""))

cells.append(md("""### 6.3 进阶案例 1:5 分制(更精细)"""))

cells.append(sql_run("""# 进阶 1:5 分制 RFM(NTILE 5)""",
"""WITH
rfm AS (
    SELECT
        user_id,
        CAST(julianday('2025-04-01') - julianday(MAX(order_date)) AS INTEGER) AS r,
        COUNT(*) AS f,
        SUM(amount) AS m
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY r DESC) AS r_score,  -- 5=最近
        NTILE(5) OVER (ORDER BY f) AS f_score,         -- 5=高频
        NTILE(5) OVER (ORDER BY m) AS m_score          -- 5=高额
    FROM rfm
)
SELECT
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN '1_重要价值'
        WHEN r_score >= 4 AND f_score < 4  THEN '2_重要发展'
        WHEN r_score <  4 AND f_score >= 4 THEN '3_重要保持'
        WHEN r_score <  4 AND f_score <  4 AND m_score >= 4 THEN '4_重要挽留'
        ELSE '5_其他'
    END AS segment,
    COUNT(*) AS user_cnt
FROM scored
GROUP BY 1
ORDER BY 1"""))

cells.append(md("""### 6.4 进阶案例 2:群运营策略表(可放进 PPT)"""))

cells.append(sql_run("""# 进阶 2:群运营策略 + 累计 GMV 占比""",
"""WITH
rfm AS (
    SELECT user_id,
        CAST(julianday('2025-04-01') - julianday(MAX(order_date)) AS INTEGER) AS r,
        COUNT(*) AS f,
        SUM(amount) AS m
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
scored AS (
    SELECT *, NTILE(2) OVER (ORDER BY r DESC) AS r_high,
              NTILE(2) OVER (ORDER BY f) AS f_high,
              NTILE(2) OVER (ORDER BY m) AS m_high
    FROM rfm
),
grouped AS (
    SELECT CASE
        WHEN r_high=1 AND f_high=1 AND m_high=1 THEN 'A_重要价值'
        WHEN r_high=1 AND f_high=1 AND m_high=2 THEN 'B_重要发展'
        WHEN r_high=2 AND f_high=1 AND m_high=1 THEN 'C_重要保持'
        WHEN r_high=2 AND f_high=2 AND m_high=1 THEN 'D_重要挽留'
        WHEN r_high=1 AND f_high=2 AND m_high=2 THEN 'E_新客'
        ELSE 'F_其他'
    END AS segment, m FROM scored
)
SELECT
    segment,
    COUNT(*) AS user_cnt,
    ROUND(SUM(m), 2) AS total_gmv,
    -- 累计贡献(按 GMV 降序累计)
    ROUND(100.0 * SUM(SUM(m)) OVER (ORDER BY SUM(m) DESC) / SUM(SUM(m)) OVER (), 2) AS cum_gmv_pct
FROM grouped
GROUP BY segment
ORDER BY total_gmv DESC"""))

cells.append(md("""### 6.5 陷阱 + 面试

**陷阱 1**:R/F/M 三个 NTILE 顺序搞反
- R(Recency)越**近**越好 → ORDER BY r **DESC**
- F(频次)越多越好 → ORDER BY f ASC(NTILE 1 是最少)
- M(金额)越多越好 → ORDER BY m ASC

**陷阱 2**:NTILE(2) 不一定 50/50
- 奇数行 NTILE(2) 会 51/49,差一行不影响业务

**面试 Q&A**:
- Q1: RFM 模型的局限? A: 不考虑品类偏好、行为路径、生命周期
- Q2: 为什么 NTILE 不用业务阈值? A: 数据探索阶段快,生产环境会用业务规则(高净值用户 GMV > 10000)
- Q3: 8 群 vs 5 群? A: 数据量大用 5 群(更粗),小数据用 8 群(更细)
"""))

# ============== 7. 业务案例 5:行为路径 ==============

cells.append(md("""## 7. 业务案例 5:用户行为转化路径

### 7.1 原理

**行为路径**:用户在产品中的行为序列(浏览 -> 加购 -> ...)。

**关键**:
- **顺序**:必须按时序判断(用窗口函数 `ROW_NUMBER` 给事件编号)
- **窗口**:用户在一段时间内的行为(一般 7/30 天)
- **转化**:用户在路径上完成目标动作(如最终购买)

### 7.2 基础案例:行为路径(按时序)"""))

cells.append(sql_run("""# 基础:看每用户在指定时段内的"事件序列"(前 5 步)""",
"""WITH
user_path AS (
    SELECT
        user_id,
        event_type,
        event_time,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time) AS step
    FROM user_events
    WHERE DATE(event_time) >= '2025-02-01'
)
SELECT user_id, step, event_type, event_time
FROM user_path
WHERE step <= 3
ORDER BY user_id, step
LIMIT 15"""))

cells.append(md("""### 7.3 进阶案例:用户完成购买的路径模式"""))

cells.append(sql_run("""# 进阶:成功购买用户的"路径模式"(前 3 步)""",
"""WITH
purchasers AS (
    SELECT DISTINCT user_id FROM user_events WHERE event_type = 'purchase'
),
user_path AS (
    SELECT
        e.user_id,
        e.event_type,
        ROW_NUMBER() OVER (PARTITION BY e.user_id ORDER BY e.event_time) AS step
    FROM user_events e
    JOIN purchasers p ON e.user_id = p.user_id
    WHERE DATE(e.event_time) >= '2025-02-01'
)
SELECT step, event_type, COUNT(*) AS user_cnt
FROM user_path
WHERE step <= 3
GROUP BY step, event_type
ORDER BY step, user_cnt DESC"""))

cells.append(md("""### 7.4 陷阱 + 面试

**陷阱**:路径太长(> 5 步)分析会稀释
- 限制 max step = 3 或 4,看最关键的前几步
- 用"模式挖掘"工具(Markov Chain / 序列模式)更专业

**面试 Q&A**:
- Q1: 行为路径有什么用? A: 产品优化(看哪步卡住)、个性化推荐
- Q2: 怎么找"流失节点"? A: 算每步的转化率,断崖式下降的就是流失节点
"""))

# ============== 8. 综合练习题 ==============

cells.append(md("""## 8. 综合练习题(6 道,大厂常考)

**难度梯度**:⭐⭐ × 2, ⭐⭐⭐ × 3, ⭐⭐⭐⭐ × 1

### Q1(⭐⭐):D7 留存(每个注册日的新用户在第 7 天是否回访)

### Q2(⭐⭐):每月复购率(本月下过单 + 上月也下过单)
> 提示:用 LAG 找上月 + 跨月判断

### Q3(⭐⭐⭐):品类迁移(用户前 30 天 vs 后 30 天最常买的品类是否有变化)

### Q4(⭐⭐⭐):沉默用户召回名单(90+ 天没下单 + GMV Top 20%)

### Q5(⭐⭐⭐):完整 RFM 8 群 + 占比 + GMV 贡献

### Q6(⭐⭐⭐⭐):**D7-D1 留存衰减率**(看新用户从 D1 到 D7 流失多少)
> 提示:留存曲线斜率

写完后看参考答案。先自己想 15 分钟。
"""))

cells.append(md("### 答案"))

cells.append(sql_run("""# Q1:D7 留存(每个注册日)""",
"""WITH
new_users AS (
    SELECT user_id, DATE(register_date) AS d0
    FROM users WHERE register_date >= '2025-01-01'
),
d7_check AS (
    SELECT n.user_id, n.d0,
           MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+7 day') THEN 1 ELSE 0 END) AS d7_active
    FROM new_users n
    LEFT JOIN user_events e ON e.user_id = n.user_id
    GROUP BY n.user_id, n.d0
)
SELECT d0, COUNT(*) AS new_users, SUM(d7_active) AS d7_retained,
       ROUND(100.0 * SUM(d7_active) / COUNT(*), 2) AS d7_retention_pct
FROM d7_check
GROUP BY d0
ORDER BY d0
LIMIT 10"""))

cells.append(sql_run("""# Q2:每月复购率""",
"""WITH
monthly AS (
    SELECT user_id, strftime('%Y-%m', order_date) AS ym
    FROM orders WHERE status = 'completed'
    GROUP BY user_id, ym
),
with_prev AS (
    SELECT user_id, ym,
           LAG(ym) OVER (PARTITION BY user_id ORDER BY ym) AS prev_ym
    FROM monthly
)
SELECT ym,
    COUNT(*) AS active_users,
    SUM(CASE WHEN prev_ym IS NOT NULL THEN 1 ELSE 0 END) AS repeat_users,
    ROUND(100.0 * SUM(CASE WHEN prev_ym IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_pct
FROM with_prev
GROUP BY ym
ORDER BY ym"""))

cells.append(sql_run("""# Q3:品类迁移(简化版,统计变化的用户数)""",
"""WITH
user_category_period AS (
    SELECT
        o.user_id,
        p.category,
        CASE WHEN DATE(o.order_date) < '2025-02-15' THEN 'first_half' ELSE 'second_half' END AS period
    FROM orders o JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'completed'
),
user_period_top AS (
    SELECT user_id, period, category,
           ROW_NUMBER() OVER (PARTITION BY user_id, period ORDER BY COUNT(*) DESC) AS rk
    FROM user_category_period
    GROUP BY user_id, period, category
)
SELECT
    (SELECT COUNT(DISTINCT user_id) FROM user_period_top WHERE period = 'first_half')  AS h1_users,
    (SELECT COUNT(DISTINCT user_id) FROM user_period_top WHERE period = 'second_half') AS h2_users,
    (SELECT COUNT(DISTINCT a.user_id)
     FROM (SELECT * FROM user_period_top WHERE period = 'first_half'  AND rk = 1) a
     JOIN (SELECT * FROM user_period_top WHERE period = 'second_half' AND rk = 1) b
       ON a.user_id = b.user_id
     WHERE a.category != b.category
    ) AS category_changed"""))

cells.append(sql_run("""# Q4:沉默用户召回名单(简化版:只算人数 + 平均 GMV)""",
"""WITH
user_gmv AS (
    SELECT user_id, MAX(order_date) AS last_order, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
gmv_threshold AS (
    SELECT gmv AS p80 FROM user_gmv
    ORDER BY gmv
    LIMIT 1 OFFSET (SELECT CAST(COUNT(*) * 0.2 AS INTEGER) FROM user_gmv)
)
SELECT
    COUNT(*) AS recall_candidates,
    ROUND(AVG(gmv), 2) AS avg_gmv
FROM user_gmv, gmv_threshold
WHERE julianday('2025-04-01') - julianday(last_order) > 90
  AND gmv >= gmv_threshold.p80"""))

cells.append(sql_run("""# Q5:完整 RFM 8 群 + 占比 + GMV 贡献""",
"""WITH
rfm AS (
    SELECT user_id,
        CAST(julianday('2025-04-01') - julianday(MAX(order_date)) AS INTEGER) AS r,
        COUNT(*) AS f,
        ROUND(SUM(amount), 2) AS m
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
scored AS (
    SELECT *,
        NTILE(2) OVER (ORDER BY r DESC) AS r_high,
        NTILE(2) OVER (ORDER BY f) AS f_high,
        NTILE(2) OVER (ORDER BY m) AS m_high
    FROM rfm
),
grouped AS (
    SELECT
        CASE
            WHEN r_high=1 AND f_high=1 AND m_high=1 THEN 'A_重要价值'
            WHEN r_high=1 AND f_high=1 AND m_high=2 THEN 'B_重要发展'
            WHEN r_high=2 AND f_high=1 AND m_high=1 THEN 'C_重要保持'
            WHEN r_high=2 AND f_high=1 AND m_high=2 THEN 'D_一般保持'
            WHEN r_high=1 AND f_high=2 AND m_high=1 THEN 'E_发展_高客单'
            WHEN r_high=1 AND f_high=2 AND m_high=2 THEN 'F_新客'
            WHEN r_high=2 AND f_high=2 AND m_high=1 THEN 'G_重要挽留'
            ELSE 'H_流失'
        END AS segment,
        m
    FROM scored
)
SELECT
    segment,
    COUNT(*) AS user_cnt,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS user_pct,
    ROUND(SUM(m), 2) AS total_gmv,
    ROUND(100.0 * SUM(m) / SUM(SUM(m)) OVER (), 2) AS gmv_pct
FROM grouped
GROUP BY segment
ORDER BY gmv_pct DESC"""))

cells.append(sql_run("""# Q6:D7-D1 留存衰减率
# 注意:SQLite 严格别名规则,不要让外层别名跟 CTE 列名重复""",
"""WITH
new_users AS (
    SELECT user_id, DATE(register_date) AS d0
    FROM users WHERE register_date >= '2025-01-01'
),
retention AS (
    SELECT n.user_id, n.d0,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+1 day') THEN 1 ELSE 0 END) AS d1_retained,
        MAX(CASE WHEN DATE(e.event_time) = DATE(n.d0, '+7 day') THEN 1 ELSE 0 END) AS d7_retained
    FROM new_users n
    LEFT JOIN user_events e ON e.user_id = n.user_id
    GROUP BY n.user_id, n.d0
)
SELECT
    SUM(d1_retained) AS total_d1,
    SUM(d7_retained) AS total_d7,
    ROUND(100.0 * (SUM(d1_retained) - SUM(d7_retained)) / NULLIF(SUM(d1_retained), 0), 2) AS d1_to_d7_churn_pct,
    ROUND(100.0 * SUM(d7_retained) / NULLIF(SUM(d1_retained), 0), 2) AS d7_retention_of_d1
FROM retention"""))

# ============== 9. 小结 ==============

cells.append(md("""## 9. 小结 + 速查表

### 9.1 速查表

| 业务 | 核心 CTE 结构 | 关键函数 |
|------|-------------|---------|
| 留存率 | new_users + LEFT JOIN events | MAX(CASE WHEN date diff = N) |
| 漏斗 | user_funnel + 条件聚合 | MAX(CASE WHEN event = X) |
| 连续登录 | user_days + LAG + 段编号 | Gaps and Islands |
| RFM | 三个 NTILE + CASE WHEN | 8 群映射 |
| 行为路径 | ROW_NUMBER OVER (PARTITION BY user) | 时序判断 |

### 9.2 面试必背

**Q: 留存率怎么算?**
A: 新用户 + LEFT JOIN 活跃日 + MAX(CASE WHEN date = d0+N)。分母是新用户数,分子是有 D+N 行为的用户数。

**Q: 漏斗哪步流失大怎么定位?**
A: 算每步转化率(cart/pv, purchase/cart, ...),最低的就是瓶颈。

**Q: Gaps and Islands 怎么解连续登录?**
A: LAG 算 gap + SUM(CASE WHEN gap>1) 分段 + 分组聚合。

**Q: RFM 模型的核心逻辑?**
A: R(最近)F(频次)M(金额)各打 1-5 分,组合出 8 群,给不同群不同运营策略。

### 9.3 自测清单

- [ ] 能用 CTE 写多步链式查询
- [ ] 能用递归 CTE 生成日期序列
- [ ] 能写 D1/D7 留存
- [ ] 能写漏斗(独立 + 严格)
- [ ] 能用 Gaps and Islands 算连续登录
- [ ] 能写完整 RFM 8 群

**全部 ✅ 之后可以推进到模块 1.4(收官)或直接 W2。**
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

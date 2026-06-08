# -*- coding: utf-8 -*-
"""
build_notebook_02_v2.py — 02_window_functions.ipynb v2(加深版)
=============================================================

新版标准:每个函数/知识点 = 5 段结构
  1. 原理(为什么 + 内部机制 + 性能)
  2. 基础案例
  3. 进阶案例(2 个不同业务场景)
  4. 陷阱案例(常见错误 + 反例)
  5. 面试 Q&A
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "02_window_functions.ipynb"


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
    # 自包含 setup:即使跳着跑,缺 pd/conn 时也会自动建好
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

cells.append(md("""# 模块 1.2 — 窗口函数全套(加深版)

> **本模块是模块 1 最重要的内容,占大厂 SQL 笔试 50%+ 比重。**
> 这版我加了**详细原理**和**多案例**,确保你不仅会用,还懂为什么。

## 本节大纲
- **0. 原理总览**:窗口函数 vs 聚合,为什么需要
- **1. ROW_NUMBER()**:原理 + 4 案例
- **2. RANK()**:原理 + 4 案例
- **3. DENSE_RANK()**:原理 + 4 案例
- **4. NTILE()**:原理 + 4 案例
- **5. SUM/AVG/COUNT OVER**:原理 + 4 案例
- **6. LAG() / LEAD()**:原理 + 4 案例
- **7. FIRST_VALUE / LAST_VALUE**:原理 + 4 案例
- **8. 命名窗口(WINDOW 子句)**:原理 + 2 案例
- **9. 业务综合实战**:3 个完整业务案例
- **10. 练习题**(6 道,带详细答案)
- **11. 小结 + 面试模板**

## 学习建议
- 每个函数按"原理 -> 基础 -> 进阶 -> 陷阱 -> 面试"5 段读
- **不要跳原理段**,面试官最喜欢问"为什么"
- 跑一遍所有 cell,看输出是否符合预期
- 练习题先自己做 5 分钟再看答案
"""))

# ============== 数据库连接 ==============

cells.append(py_run("""# 数据库连接
import sqlite3
import pandas as pd
from pathlib import Path

DB = Path('../data/ecommerce.db').resolve()
conn = sqlite3.connect(DB)
print('Connected to', DB)"""))

# ============== 0. 原理总览 ==============

cells.append(md("""## 0. 原理总览:窗口函数为什么存在?

### 0.1 一个生活化的对比

想象你在一个班 50 个学生里:
- **聚合函数**(`SUM/AVG/COUNT` + `GROUP BY`):老师说"按性别分组,告诉我平均分" → 你只得到 2 个数字(男/女平均分)
- **窗口函数**(`SUM/AVG/COUNT` + `OVER`):老师说"每个学生后面写上自己班级的平均分" → 你还是 50 个学生,但每个人多了 1 列

**关键差异**:**聚合函数会"吃掉"行,窗口函数保留所有行。**

### 0.2 SQL 执行顺序(理解的关键)

```
SELECT [聚合/窗口列]
FROM
WHERE        -- 1. 先过滤行
GROUP BY     -- 2. 再分组(用聚合时)
HAVING       -- 3. 过滤组
ORDER BY     -- 4. 排序
WINDOW w AS  -- 5. 定义窗口(如果有)
[SELECT 中执行] -- 6. 计算窗口函数
```

**窗口函数在 SELECT 阶段执行**,意味着它能看到 ORDER BY 后的顺序、聚合后的组,但在 LIMIT 之前。

### 0.3 OVER 子句的 3 个核心组件

```sql
函数() OVER (
    [PARTITION BY <分组列>]    -- 类似 GROUP BY,把数据切成几个"窗口"
    [ORDER BY <排序列>]        -- 窗口内排序
    [ROWS/RANGE BETWEEN <框>]  -- 窗口框,定义聚合范围(可选)
)
```

| 组件 | 作用 | 类比 |
|------|------|------|
| `PARTITION BY` | 把数据切成多个独立窗口 | 班级分组 |
| `ORDER BY` | 窗口内排序 | 学生按分数排队 |
| 窗口框 | 限定聚合的具体行范围 | "算前 5 名 + 自己" |

### 0.4 性能特征(为什么面试爱问)

| 维度 | 聚合函数 | 窗口函数 |
|------|---------|---------|
| 输出行数 | 减少(N 行 -> 1 行) | **不变**(N 行 -> N 行) |
| 单次开销 | 低 | 中(需要排序) |
| 内存占用 | 低 | 中(要维护窗口) |
| 大数据量 | 稳定 | 千万级以上需谨慎(排序开销) |
| 与 GROUP BY 嵌套 | ✅ | ❌(不能直接嵌套,要用 CTE) |

### 0.5 大厂为什么 80% SQL 题靠它

1. **业务需求天然要"行级上下文"**:不是"总分多少",而是"每个人在自己组里的排名"
2. **能用一次查询解决的事**,不用相关子查询,性能好
3. **可读性高**,逻辑线性(从左到右),不像嵌套子查询要"往里看"
4. **SQL 标准(SQL 2003 起)**,所有主流数据库都支持

**铁律**:**能用窗口函数就别用相关子查询**。
"""))

# ============== 1. ROW_NUMBER ==============

cells.append(md("""## 1. ROW_NUMBER() — 行号生成器

### 1.1 原理

**作用**:给每一行打一个**唯一**的行号(从 1 开始)。

**内部机制**:
- 引擎先按 `PARTITION BY` 分组(类似 GROUP BY)
- 每组内按 `ORDER BY` 排序
- 从 1 开始递增编号
- 编号是**唯一**的(就算两行完全一样,也会给不同编号)

**性能**:`ROW_NUMBER` 在内部走的是 `Sort + Increment` 模式,O(N log N) 时间复杂度。

### 1.2 基础案例:取每组第 1 条

**业务**:每个用户最近一次订单
"""))

cells.append(sql_run("""# 基础:每个用户最近一次订单(Row Number = 1)""",
"""WITH ranked AS (
    SELECT
        user_id,
        order_date,
        amount,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date DESC) AS rn
    FROM orders
    WHERE status = 'completed'
)
SELECT user_id, order_date, amount
FROM ranked
WHERE rn = 1
LIMIT 10"""))

cells.append(md("""### 1.3 进阶案例 1:每组 TopN

**业务**:每个渠道(GROUP BY 维度)消费金额最高的 3 个用户"""))

cells.append(sql_run("""# 进阶 1:每渠道 Top 3 用户""",
"""WITH user_channel_gmv AS (
    SELECT
        u.channel,
        o.user_id,
        SUM(o.amount) AS gmv
    FROM orders o
    JOIN users u ON o.user_id = u.user_id
    WHERE o.status = 'completed'
    GROUP BY u.channel, o.user_id
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY channel ORDER BY gmv DESC) AS rk
    FROM user_channel_gmv
)
SELECT channel, user_id, gmv, rk
FROM ranked
WHERE rk <= 3
ORDER BY channel, rk"""))

cells.append(md("""### 1.4 进阶案例 2:数据去重(取唯一记录)

**业务**:每个用户**最早一次**的注册信息(万一用户重复注册了)"""))

cells.append(sql_run("""# 进阶 2:用 ROW_NUMBER 去重 - 取每用户最早一次""",
"""WITH users_rn AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY register_date ASC) AS rn
    FROM users
)
SELECT user_id, register_date, channel, city, age_group, gender
FROM users_rn
WHERE rn = 1
LIMIT 10"""))

cells.append(md("""### 1.5 陷阱案例:`ROW_NUMBER` vs `DISTINCT` 的区别

**反例 1**:`ROW_NUMBER` 不会自动去重
```sql
-- 想取"所有出现过一次的城市",用 ROW_NUMBER 反而麻烦
SELECT DISTINCT city FROM users  -- 一行 SQL 搞定

-- 用 ROW_NUMBER 是绕弯路
SELECT city FROM (
    SELECT city, ROW_NUMBER() OVER (PARTITION BY city ORDER BY city) AS rn
    FROM users
) WHERE rn = 1
```

**反例 2**:`PARTITION BY` 一定要选对维度!
```sql
-- 想"每用户首单"但忘了 PARTITION BY user_id
SELECT user_id, order_date FROM (
    SELECT user_id, order_date,
        ROW_NUMBER() OVER (ORDER BY order_date) AS rn  -- 没 PARTITION!
    FROM orders
) WHERE rn = 1
-- 结果:全表最早的那一条订单,不是每个用户最早的一条
```

### 1.6 面试 Q&A

**Q1: ROW_NUMBER / RANK / DENSE_RANK 三者区别?**
- A: ROW_NUMBER 永远唯一(1,2,3,4),并列也强制编号;RANK 并列跳号(1,2,2,4);DENSE_RANK 并列不跳号(1,2,2,3)。

**Q2: 为什么"取每组 TopN"要用 ROW_NUMBER 而不是 MAX?**
- A: MAX 只能取一个值,取不到第二第三。ROW_NUMBER + WHERE rk <= N 是经典模式。

**Q3: 千万级数据用 ROW_NUMBER 会慢吗?**
- A: 取决于是否需要排序。如果已经按 user_id 建索引,排序开销小;否则要走全表扫 + 排序,可能 30+ 秒。生产上常配合 `(PARTITION 列, ORDER 列)` 联合索引。

**Q4: ROW_NUMBER 编号之后,能不能再用这个编号做 JOIN?**
- A: 能。把带 rn 的子查询作为 CTE 或子查询,再 JOIN 出去即可。常见用法是"先排名,再过滤,再 JOIN"。
"""))

# ============== 2. RANK ==============

cells.append(md("""## 2. RANK() — 允许并列且跳号

### 2.1 原理

**作用**:排名,允许并列。**并列后会跳号**(1,2,2,4 — 没有第 3 名)。

**内部机制**:
- 跟 ROW_NUMBER 一样,先排序
- 比较当前值和前一个值,如果相等就**复用**前一个编号
- 下一个值在前一个编号基础上**+1**

**对比 RANK vs ROW_NUMBER**:
```
原始分数: 100, 90, 90, 80
ROW_NUMBER: 1, 2, 3, 4    -- 编号不重
RANK:       1, 2, 2, 4    -- 第 3 名跳了
DENSE_RANK: 1, 2, 2, 3    -- 第 3 名不跳
```

### 2.2 基础案例:业绩排名"""))

cells.append(sql_run("""# 基础:用户 GMV 排名(RANK)""",
"""WITH user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
)
SELECT user_id, gmv,
    RANK() OVER (ORDER BY gmv DESC) AS rk
FROM user_gmv
ORDER BY gmv DESC
LIMIT 15"""))

cells.append(md("""### 2.3 进阶案例 1:找出每个部门的前 2 名(含并列)

**业务**:HR 系统里,各部门工资 Top 2(并列第 2 都算)"""))

cells.append(sql_run("""# 进阶 1:每部门工资 Top 2(用 RANK,会拿到所有并列第 2)""",
"""-- 模拟数据(因为我们没部门表)
WITH emp_salary AS (
    SELECT
        user_id,
        CASE user_id % 3 WHEN 0 THEN 'tech' WHEN 1 THEN 'sales' ELSE 'ops' END AS dept,
        SUM(amount) AS salary
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
ranked AS (
    SELECT *,
        RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rk
    FROM emp_salary
)
SELECT dept, user_id, salary, rk
FROM ranked
WHERE rk <= 2
ORDER BY dept, rk"""))

cells.append(md("""### 2.4 进阶案例 2:销售榜(Top 10 名单)

**业务**:对外公布的"销售冠军榜",第 11 名就是第 11 名(不补位)"""))

cells.append(sql_run("""# 进阶 2:销售 Top 10 榜(用 RANK,真实排名)""",
"""WITH user_sales AS (
    SELECT user_id, SUM(amount) AS sales
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
)
SELECT user_id, sales,
    RANK() OVER (ORDER BY sales DESC) AS real_rank
FROM user_sales
WHERE sales > 0
ORDER BY sales DESC
LIMIT 10"""))

cells.append(md("""### 2.5 陷阱案例:用 RANK 取 TopN 会"多算"

```sql
-- 想"取每组前 3 名",用 RANK + WHERE rk <= 3
-- 但如果有 2 个人并列第 3,你会拿到 4 个!
SELECT * FROM (
    SELECT *,
        RANK() OVER (PARTITION BY g ORDER BY m DESC) AS rk
    FROM t
) WHERE rk <= 3
-- 实际可能返回 3-5 行
```

**解决方案**:
- 严格 TopN(固定 3 个):用 `ROW_NUMBER`
- 接受并列(可能多 1-2 个):用 `RANK`
- 拿到"金牌/银牌/铜牌"且不要跳号:用 `DENSE_RANK`

### 2.6 面试 Q&A

**Q1: 业务里什么场景用 RANK 不跳号?**
- A: 用 DENSE_RANK 才是"不跳号",RANK 本身是跳号的。常见误区。

**Q2: 美团/抖音的"销量榜 Top10"用什么排名?**
- A: 看场景。对外公布"金牌/银牌/铜牌"用 DENSE_RANK;真实的"前 10 名"用 ROW_NUMBER(取前 10 个 SKU,不看分数)。

**Q3: RANK 在数据有 NULL 时会怎样?**
- A: NULL 被认为是相同值,会拿到相同排名。生产上常先 `WHERE m IS NOT NULL` 过滤。
"""))

# ============== 3. DENSE_RANK ==============

cells.append(md("""## 3. DENSE_RANK() — 允许并列但不跳号

### 3.1 原理

**作用**:排名,允许并列。**并列后不跳号**(1,2,2,3 — 第 3 名还在)。

**与 RANK 的差异**:
- RANK: 1, 2, 2, **4**(跳)
- DENSE_RANK: 1, 2, 2, **3**(不跳)

**类比**:
- 奥运会金牌榜:RANK(第 2 名有 2 个并列,就没有第 3 名银牌)
- 班级排名:DENSE_RANK(并列第 2 后,下一个就是第 3)

### 3.2 基础案例:找"金牌/银牌/铜牌"得奖人"""))

cells.append(sql_run("""# 基础:DENSE_RANK 排名(不跳号)""",
"""WITH user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
)
SELECT user_id, gmv,
    DENSE_RANK() OVER (ORDER BY gmv DESC) AS dr
FROM user_gmv
ORDER BY gmv DESC
LIMIT 15"""))

cells.append(md("""### 3.3 进阶案例 1:连续 3 名的用户数

**业务**:想知道每个分数段有多少人(连续排名场景)"""))

cells.append(sql_run("""# 进阶 1:用 DENSE_RANK 看"连续 3 名"分布""",
"""WITH user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
ranked AS (
    SELECT gmv,
        DENSE_RANK() OVER (ORDER BY gmv DESC) AS dr
    FROM user_gmv
)
SELECT
    CASE
        WHEN dr = 1 THEN '冠军'
        WHEN dr = 2 THEN '亚军'
        WHEN dr = 3 THEN '季军'
        WHEN dr BETWEEN 4 AND 10 THEN '前十'
        ELSE '其他'
    END AS tier,
    COUNT(*) AS user_cnt
FROM ranked
GROUP BY 1
ORDER BY MIN(dr)"""))

cells.append(md("""### 3.4 进阶案例 2:用户分层(头部/腰部/尾部)

**业务**:运营想做用户分群,头部 1%、腰部 10%、尾部 89%(分位数 + DENSE_RANK 组合)"""))

cells.append(sql_run("""# 进阶 2:用 NTILE + DENSE_RANK 组合做用户分层""",
"""WITH user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
tiered AS (
    SELECT user_id, gmv,
        NTILE(100) OVER (ORDER BY gmv DESC) AS percentile
    FROM user_gmv
)
SELECT
    CASE
        WHEN percentile <= 1 THEN 'Top 1%'
        WHEN percentile <= 5 THEN 'Top 5%'
        WHEN percentile <= 20 THEN 'Top 20%'
        ELSE 'Others'
    END AS tier,
    COUNT(*) AS user_cnt,
    ROUND(AVG(gmv), 2) AS avg_gmv
FROM tiered
GROUP BY 1
ORDER BY MIN(percentile)"""))

cells.append(md("""### 3.5 陷阱案例:DENSE_RANK 的"连续性"会误导 TopN

**反例**:
```sql
-- 想"取前 3 名",用 DENSE_RANK + rk <= 3
-- 假设分数是 [100, 90, 90, 80, 80, 80, 70]
-- DENSE_RANK: [1, 2, 2, 3, 3, 3, 4]
-- WHERE rk <= 3 会拿到 6 行(3 个并列第 3 都进了)
```

**怎么选**:
- 严格 "前 3 名" → `ROW_NUMBER` + rk <= 3
- "金牌/银牌/铜牌" 制度 → `DENSE_RANK` + rk <= 3
- "Top 1/3/5/10 名" → `RANK`(接受跳号)或 `DENSE_RANK`(不跳号)

### 3.6 面试 Q&A

**Q1: 为什么金牌/银牌/铜牌制度用 DENSE_RANK?**
- A: 因为即使有 2 个人并列金牌,下一个就是银牌(不是第 4 名)。这是体育/比赛的标准排名方式。

**Q2: ROW_NUMBER 是不是能完全替代 RANK / DENSE_RANK?**
- A: 排名场景不行(你要的就是并列)。但"取唯一 N 条"场景,ROW_NUMBER 严格,比 RANK/DENSE_RANK 更可控。

**Q3: DENSE_RANK 在 Hive/Spark 里有性能差异吗?**
- A: 在做窗口时,ROW_NUMBER / RANK / DENSE_RANK 的内部实现是同一种排序,性能差异可以忽略。差异在业务语义。
"""))

# ============== 4. NTILE ==============

cells.append(md("""## 4. NTILE(n) — 把数据切 n 桶

### 4.1 原理

**作用**:把数据**尽量均匀**地切成 n 桶,返回桶号(1 到 n)。

**内部机制**:
- 引擎先按 `ORDER BY` 排序
- 计算每桶的目标行数 = `CEIL(总行数 / n)`
- 前面的桶可能多 1 行(如果有余数)
- 例:12 行切 4 桶 → 每桶 3 行;13 行切 4 桶 → 第 1 桶 4 行,其余 3 行

**对比其他"分桶"函数**:
- `NTILE(n)`:按**行数**均匀分
- `PERCENT_RANK()`:按**百分位**算(0 到 1)
- `CUME_DIST()`:累计分布(<=当前值的比例)

### 4.2 基础案例:用户四象限分群"""))

cells.append(sql_run("""# 基础:把用户按 GMV 4 等分(头部 25% / 中上 / 中下 / 尾部)
# 注意:SQLite 不支持在 GROUP BY 里直接用窗口函数别名,必须先在子查询算好""",
"""WITH user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
tiered AS (
    SELECT user_id, gmv, NTILE(4) OVER (ORDER BY gmv DESC) AS tier
    FROM user_gmv
)
SELECT tier,
    COUNT(*) AS user_cnt,
    ROUND(MIN(gmv), 2) AS min_gmv,
    ROUND(MAX(gmv), 2) AS max_gmv,
    ROUND(AVG(gmv), 2) AS avg_gmv
FROM tiered
GROUP BY tier
ORDER BY tier"""))

cells.append(md("""### 4.3 进阶案例 1:百分位排名

**业务**:想知道"我超过百分之多少的用户"(用 NTILE 100 反向)"""))

cells.append(sql_run("""# 进阶 1:每个用户的百分位排名""",
"""WITH user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
)
SELECT
    user_id,
    ROUND(gmv, 2) AS gmv,
    NTILE(100) OVER (ORDER BY gmv DESC) AS percentile,
    -- 转换成"超过百分之多少"
    (100 - NTILE(100) OVER (ORDER BY gmv DESC)) AS beat_pct
FROM user_gmv
ORDER BY gmv DESC
LIMIT 15"""))

cells.append(md("""### 4.4 进阶案例 2:RFM 中的 F 维度(用 NTILE 打分)

**业务**:RFM 模型的 F(Frequency,消费频次)维度"""))

cells.append(sql_run("""# 进阶 2:RFM 中 F 维度的 NTILE 打分""",
"""WITH user_freq AS (
    SELECT user_id, COUNT(*) AS freq
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
)
SELECT
    user_id,
    freq,
    NTILE(5) OVER (ORDER BY freq) AS f_score  -- 1=低频, 5=高频
FROM user_freq
ORDER BY f_score DESC, freq DESC
LIMIT 15"""))

cells.append(md("""### 4.5 陷阱案例:NTILE 不保证"业务桶"等分

**陷阱 1**:数据有大量 NULL 时,NULL 会被分到最后一个桶
```sql
-- 假设 user_gmv 有 1000 行,其中 50 行 gmv 是 NULL
SELECT user_id, NTILE(4) OVER (ORDER BY gmv DESC) AS tier
FROM user_gmv
-- NULL 用户全部落在 tier=4 里(因为 DESC 时 NULL 在最前?还是最后?看数据库)
-- SQLite/Hive 都把 NULL 放最后(默认 NULLS LAST)
```

**陷阱 2**:分位数不精确
```sql
-- 想"前 10%",NTILE(10) = 1 是约 10%(可能 9% 或 11%)
-- 严格做法:用 PERCENT_RANK() + 0.9 比较
```

**陷阱 3**:NTILE 跟窗口框无关
```sql
-- NTILE 不接受 ROWS BETWEEN 框架
NTILE(4) OVER (PARTITION BY g ORDER BY m ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)  -- SQL 错
```

### 4.6 面试 Q&A

**Q1: NTILE 和 PERCENT_RANK 区别?**
- A: NTILE 把数据切 n 桶(分位数概念),返回桶号;PERCENT_RANK 返回 0-1 的连续值,代表"低于当前值的比例"。

**Q2: 用户分群用 NTILE 还是业务规则?**
- A: 看场景。**数据探索阶段**用 NTILE(快速切 4 桶看分布);**精细化运营**用业务规则(例如按消费金额 + 频次 + 品类综合打标签)。

**Q3: NTILE 切 10 桶,实际可能 9% 11% 怎么解决?**
- A: 用 `PERCENT_RANK() <= 0.1` 取前 10%(更精确但开销大)。或者接受"近似"。
"""))

# ============== 5. SUM/AVG/COUNT OVER ==============

cells.append(md("""## 5. SUM/AVG/COUNT OVER — 窗口聚合

### 5.1 原理

**作用**:跟普通聚合函数一样(SUM/AVG/COUNT/MIN/MAX),但**不减少行数**,而是给每行加一列聚合结果。

**默认窗口框**(重要!):
- `SUM(x) OVER (ORDER BY dt)` 默认是 **`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`**
- 也就是说"从分区第一行**到当前行**的累计",而不是"整个分区的总和"

**与 GROUP BY 的核心区别**:
```sql
-- 聚合:每个 channel 一行
SELECT channel, SUM(amount) FROM orders GROUP BY channel

-- 窗口:每行 orders 都加 channel 总额
SELECT order_id, channel, amount,
       SUM(amount) OVER (PARTITION BY channel) AS channel_total
FROM orders
```

### 5.2 基础案例:每日累计 GMV"""))

cells.append(sql_run("""# 基础:每日累计 GMV(默认窗口框就是累计)""",
"""WITH daily_gmv AS (
    SELECT DATE(order_date) AS dt, SUM(amount) AS daily_gmv
    FROM orders WHERE status = 'completed'
    GROUP BY DATE(order_date)
)
SELECT dt, daily_gmv,
    SUM(daily_gmv) OVER (ORDER BY dt) AS cum_gmv
FROM daily_gmv
ORDER BY dt
LIMIT 10"""))

cells.append(md("""### 5.3 进阶案例 1:占比分析

**业务**:每行占分区总和的百分比(找异常高的)"""))

cells.append(sql_run("""# 进阶 1:每用户订单金额占该用户总消费的百分比""",
"""WITH user_orders AS (
    SELECT user_id, order_id, amount
    FROM orders WHERE status = 'completed'
)
SELECT user_id, order_id, ROUND(amount, 2) AS amount,
    ROUND(SUM(amount) OVER (PARTITION BY user_id), 2) AS user_total,
    ROUND(100.0 * amount / SUM(amount) OVER (PARTITION BY user_id), 2) AS pct
FROM user_orders
ORDER BY user_id, pct DESC
LIMIT 15"""))

cells.append(md("""### 5.4 进阶案例 2:用户消费频次分布

**业务**:每个用户在本月消费笔数 / 全平台用户消费笔数(分位数)"""))

cells.append(sql_run("""# 进阶 2:每用户消费笔数 vs 全平台平均/最大/最小""",
"""WITH user_freq AS (
    SELECT user_id, COUNT(*) AS freq
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
)
SELECT user_id, freq,
    ROUND(AVG(freq) OVER (), 2) AS avg_freq,
    MAX(freq) OVER () AS max_freq,
    MIN(freq) OVER () AS min_freq,
    ROUND(100.0 * freq / SUM(freq) OVER (), 4) AS pct_of_total
FROM user_freq
ORDER BY freq DESC
LIMIT 15"""))

cells.append(md("""### 5.5 陷阱案例:窗口框的"默认陷阱"

**陷阱 1**:不写 ORDER BY 时,默认是"整个分区"
```sql
SUM(x) OVER (PARTITION BY g)              -- 整个分区的总和
SUM(x) OVER (PARTITION BY g ORDER BY t)   -- 从分区首行到当前行的累计(累加)
```

**陷阱 2**:ORDER BY 默认是 `RANGE` 而非 `ROWS`
```sql
SUM(x) OVER (ORDER BY t)  -- RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                           -- 当 t 有重复时,所有相同 t 的行被认为"同一行"(RANGE 的特性)
```

**陷阱 3**:聚合窗口里的 NULL
```sql
-- NULL 会被跳过(SUM 跳过 NULL)
-- 想包含 NULL 用 COALESCE(x, 0) 包一层
```

**实战铁律**:
- 不写 `ROWS BETWEEN` 就用默认(RANGE + UNBOUNDED PRECEDING 到 CURRENT ROW)
- 想要"整组总和"就**不写 ORDER BY**
- 想要"前 N 行"就**显式写 ROWS BETWEEN N-1 PRECEDING AND CURRENT ROW**

### 5.6 面试 Q&A

**Q1: SUM(x) OVER () 和 SUM(x) OVER (PARTITION BY 1) 一样吗?**
- A: 一样。`OVER ()` 没 PARTITION BY 等于"整个表一组"。

**Q2: 为什么累计求和要 ORDER BY?**
- A: 累计必须有顺序!没有 ORDER BY,引擎不知道"累计"的方向。

**Q3: COUNT(*) OVER 和 COUNT(col) OVER 区别?**
- A: COUNT(*) 算所有行(包括 NULL),COUNT(col) 跳过 NULL。窗口里也一样。
"""))

# ============== 6. LAG / LEAD ==============

cells.append(md("""## 6. LAG() / LEAD() — 上下行引用

### 6.1 原理

**作用**:
- `LAG(col, n, default)`:取**当前行前 n 行**的 col 值
- `LEAD(col, n, default)`:取**当前行后 n 行**的 col 值

**内部机制**:
- 引擎在窗口内按 `ORDER BY` 排序
- 标记每行的"行号"
- LAG/LEAD 直接按行号取目标行的值
- 找不到时返回 NULL(或你指定的 default)

**签名**:
```sql
LAG(col, n, default) OVER (PARTITION BY g ORDER BY t)
--          ^  ^       ^
--          |  |       默认值(可选),找不到时返回
--          |  往前/后看几行,默认 1
--          要取的列
```

### 6.2 基础案例:算环比(本月 vs 上月)"""))

cells.append(sql_run("""# 基础:每月 GMV + 上月 GMV + 环比""",
"""WITH monthly_gmv AS (
    SELECT
        strftime('%Y-%m', order_date) AS ym,
        ROUND(SUM(amount), 2) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY strftime('%Y-%m', order_date)
)
SELECT ym, gmv,
    LAG(gmv) OVER (ORDER BY ym) AS prev_gmv,
    ROUND(100.0 * (gmv - LAG(gmv) OVER (ORDER BY ym)) / LAG(gmv) OVER (ORDER BY ym), 2) AS mom_pct
FROM monthly_gmv
ORDER BY ym"""))

cells.append(md("""### 6.3 进阶案例 1:D1 留存(N 日回访)

**业务**:每个新用户第二天是否回访(用 LAG 找下一次访问)"""))

cells.append(sql_run("""# 进阶 1:D1 留存(LAG 找下次访问)""",
"""WITH user_events_daily AS (
    SELECT DISTINCT user_id, DATE(event_time) AS dt
    FROM user_events
    WHERE event_type = 'pv'
),
with_next AS (
    SELECT
        user_id, dt,
        LEAD(dt) OVER (PARTITION BY user_id ORDER BY dt) AS next_dt
    FROM user_events_daily
)
SELECT
    COUNT(DISTINCT user_id) AS total_active_users,
    SUM(CASE WHEN next_dt IS NOT NULL AND julianday(next_dt) - julianday(dt) <= 1 THEN 1 ELSE 0 END) AS d1_retained,
    ROUND(100.0 * SUM(CASE WHEN next_dt IS NOT NULL AND julianday(next_dt) - julianday(dt) <= 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS d1_retention_pct
FROM with_next"""))

cells.append(md("""### 6.4 进阶案例 2:复购间隔

**业务**:每个用户平均多少天复购一次"""))

cells.append(sql_run("""# 进阶 2:复购间隔(订单之间)""",
"""WITH user_orders AS (
    SELECT user_id, order_date,
        LAG(order_date) OVER (PARTITION BY user_id ORDER BY order_date) AS prev_order
    FROM orders
    WHERE status = 'completed'
)
SELECT user_id,
    ROUND(AVG(julianday(order_date) - julianday(prev_order)), 2) AS avg_gap,
    COUNT(*) AS order_cnt
FROM user_orders
WHERE prev_order IS NOT NULL
GROUP BY user_id
HAVING COUNT(*) >= 3
ORDER BY avg_gap
LIMIT 15"""))

cells.append(md("""### 6.5 陷阱案例:PARTITION BY 一定要选对

**反例 1**:没 PARTITION,跨用户取了
```sql
-- 想"用户自己的上笔订单",但忘了 PARTITION BY user_id
SELECT user_id, order_date,
    LAG(order_date) OVER (ORDER BY order_date) AS prev  -- 全表的上一个订单
FROM orders
-- 结果:不同用户的订单会"串"起来
```

**反例 2**:没 ORDER BY,LAG 拿不到确定值
```sql
-- 报错或不报错但意义不明
LAG(x) OVER (PARTITION BY g)
-- 必须给 ORDER BY,LAG 才有"方向"
```

**反例 3**:跨月比较要用日期函数,不要直接 LAG
```sql
-- 想"看上一年的同月",用 LAG(y, 12) 在月粒度
LAG(gmv, 12) OVER (ORDER BY ym)  -- 12 个月前的同月
```

### 6.6 面试 Q&A

**Q1: 算同比/环比,什么时候用 LAG,什么时候用自关联?**
- A: 粒度明确(每月一行)、只比一阶,直接 LAG;粒度不齐(订单表算同比)、跨多阶比较,用自关联(`o1.month = o2.month + 12`)。

**Q2: 留存率用 LAG 怎么算?**
- A: 把每个用户的活跃日提出来,LAG 找下一次活跃日,差值 = 1 就是"次日回访"。然后 `SUM(CASE WHEN diff = 1 THEN 1 END) / 总数`。

**Q3: LAG 在数据倾斜时会怎样?**
- A: 不会因为 LAG 倾斜(它是行内函数,跟 GROUP BY 的数据倾斜不同)。但 PARTITION BY 选错列会导致逻辑错误,跟性能无关。
"""))

# ============== 7. FIRST_VALUE / LAST_VALUE ==============

cells.append(md("""## 7. FIRST_VALUE / LAST_VALUE — 窗口首尾值

### 7.1 原理

**作用**:
- `FIRST_VALUE(col)`:窗口**第一行**的 col 值
- `LAST_VALUE(col)`:窗口**最后一行**的 col 值(默认有坑!)

**LAST_VALUE 默认窗口**:
- `LAST_VALUE(x) OVER (ORDER BY t)` 默认窗口是 `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
- 也就是说"默认只到当前行",拿不到真正的最后一行

**正确用法**(重要!):
```sql
-- 必须显式写 ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
LAST_VALUE(x) OVER (PARTITION BY g ORDER BY t
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
```

### 7.2 基础案例:用户首次/末次行为"""))

cells.append(sql_run("""# 基础:用户首次和末次浏览(LAST_VALUE 必须显式写窗口框)""",
"""WITH user_pv AS (
    SELECT user_id, event_time
    FROM user_events WHERE event_type = 'pv'
)
SELECT DISTINCT user_id,
    FIRST_VALUE(event_time) OVER (PARTITION BY user_id ORDER BY event_time) AS first_pv,
    LAST_VALUE(event_time) OVER (
        PARTITION BY user_id ORDER BY event_time
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_pv
FROM user_pv
ORDER BY user_id
LIMIT 10"""))

cells.append(md("""### 7.3 进阶案例 1:用 MAX/MIN 替代 LAST_VALUE(更直观)

**业务**:找用户最贵一笔订单(用 MAX 替代 LAST_VALUE 配 ASC)"""))

cells.append(sql_run("""# 进阶 1:用 MAX/MIN OVER 替代 LAST_VALUE/FIRST_VALUE(更清晰)""",
"""SELECT DISTINCT user_id,
    MAX(amount) OVER (PARTITION BY user_id) AS max_amount,
    MIN(amount) OVER (PARTITION BY user_id) AS min_amount,
    -- 等价于 FIRST_VALUE + ASC
    FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY amount ASC) AS min_v2,
    -- 等价于 LAST_VALUE + DESC
    FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY amount DESC) AS max_v2
FROM orders
WHERE status = 'completed'
ORDER BY user_id
LIMIT 10"""))

cells.append(md("""### 7.4 进阶案例 2:首次和末次之间的活跃天数

**业务**:用户的"生命周期"长度(从首次到末次)"""))

cells.append(sql_run("""# 进阶 2:用户生命周期(首次到末次)""",
"""WITH user_orders AS (
    SELECT user_id, order_date
    FROM orders WHERE status = 'completed'
)
SELECT DISTINCT user_id,
    FIRST_VALUE(order_date) OVER (PARTITION BY user_id ORDER BY order_date) AS first_order,
    LAST_VALUE(order_date) OVER (
        PARTITION BY user_id ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_order,
    CAST(julianday(LAST_VALUE(order_date) OVER (
        PARTITION BY user_id ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    )) - julianday(FIRST_VALUE(order_date) OVER (PARTITION BY user_id ORDER BY order_date)) AS INTEGER) AS lifecycle_days
FROM user_orders
ORDER BY lifecycle_days DESC
LIMIT 10"""))

cells.append(md("""### 7.5 陷阱案例:`LAST_VALUE` 的默认窗口框

**反例**:
```sql
-- 错误的 LAST_VALUE 用法
SELECT user_id, order_date,
    LAST_VALUE(order_date) OVER (PARTITION BY user_id ORDER BY order_date) AS wrong_last
FROM orders
-- 结果:wrong_last 跟 order_date 一样!(因为默认窗口框只到当前行)
```

**正确做法**(任选一种):
```sql
-- 写法 1:显式 ROWS BETWEEN
LAST_VALUE(order_date) OVER (PARTITION BY g ORDER BY t
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)

-- 写法 2:用 MAX 替代(更直观)
MAX(order_date) OVER (PARTITION BY g)
```

### 7.6 面试 Q&A

**Q1: 为什么不直接用 MAX 替代 LAST_VALUE?**
- A: MAX 在窗口里没有"位置信息",只是聚合值。如果你要"末次订单的多个字段"(如末次订单的金额、品类),用 LAST_VALUE + ROWS BETWEEN 更合适。

**Q2: FIRST_VALUE/LAST_VALUE 在数据倾斜时有坑吗?**
- A: 没有特别坑(都是行内函数)。但 ORDER BY 列没索引时,排序开销大。

**Q3: 找用户首单,是用 MIN(order_date) 还是 FIRST_VALUE(order_date)?**
- A: 都可以。MIN 更简洁;FIRST_VALUE 还能拿"首单对应的其他字段"(如首单金额、品类),用 MIN 拿不到。
"""))

# ============== 8. 命名窗口 ==============

cells.append(md("""## 8. 命名窗口(WINDOW 子句) — 减少重复

### 8.1 原理

**作用**:当多个窗口函数用相同的 `OVER (...)` 时,把窗口抽出来命名,避免代码重复。

**语法**:
```sql
SELECT
    func1() OVER w,
    func2() OVER w,
    func3() OVER w
FROM tbl
WINDOW w AS (PARTITION BY ... ORDER BY ... ROWS BETWEEN ...)
```

**支持的数据库**:PostgreSQL ✅、Hive ✅、Spark SQL ✅、MySQL 8.0+ ✅、SQLite 基础支持 ✅

### 8.2 基础案例:同一窗口里跑多个聚合"""))

cells.append(sql_run("""# 基础:同一窗口里跑 SUM/AVG/COUNT(命名窗口)""",
"""SELECT
    user_id,
    order_date,
    amount,
    SUM(amount)  OVER w AS cum_amount,
    AVG(amount)  OVER w AS avg_amount,
    COUNT(*)     OVER w AS cum_order_cnt,
    MAX(amount)  OVER w AS max_amount,
    MIN(amount)  OVER w AS min_amount
FROM orders
WHERE status = 'completed'
WINDOW w AS (PARTITION BY user_id ORDER BY order_date)
ORDER BY user_id, order_date
LIMIT 15"""))

cells.append(md("""### 8.3 进阶案例:多窗口组合(用两次 WINDOW 定义)

**业务**:同时看"用户内累计"和"全平台总计"
"""))

cells.append(sql_run("""# 进阶:多窗口组合(用户内 + 全平台)""",
"""SELECT
    user_id,
    order_date,
    amount,
    SUM(amount) OVER user_w AS user_cum,
    SUM(amount) OVER () AS platform_total
FROM orders
WHERE status = 'completed'
WINDOW
    user_w AS (PARTITION BY user_id ORDER BY order_date)
ORDER BY user_id, order_date
LIMIT 15"""))

cells.append(md("""### 8.4 陷阱:WINDOW 子句不能嵌套

```sql
-- 错的:WINDOW 子句里引用另一个 WINDOW
WINDOW w1 AS (PARTITION BY a), w2 AS (w1 ORDER BY b)  -- SQL 错
```

**正确做法**:
```sql
WINDOW
    w1 AS (PARTITION BY a),
    w2 AS (PARTITION BY a ORDER BY b)  -- 完整写
```
"""))

# ============== 9. 业务综合实战 ==============

cells.append(md("""## 9. 业务综合实战(3 个完整案例)

把前面 8 个函数组合起来,做真实业务。

### 9.1 案例 1:用户分层 RFM(头部/中/尾)+ 累计贡献

把 4 个窗口函数(RFM 三个 NTILE + 累计)组合,产出运营分群表。"""))

cells.append(sql_run("""# 案例 1:RFM 8 群 + 累计贡献 + 用户数""",
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
        NTILE(2) OVER (ORDER BY r DESC) AS r_high,
        NTILE(2) OVER (ORDER BY f) AS f_high,
        NTILE(2) OVER (ORDER BY m) AS m_high
    FROM rfm
),
segments AS (
    SELECT
        CASE
            WHEN r_high=1 AND f_high=1 AND m_high=1 THEN 'A_重要价值'
            WHEN r_high=1 AND f_high=1 AND m_high=2 THEN 'B_重要发展'
            WHEN r_high=2 AND f_high=1 AND m_high=1 THEN 'C_重要保持'
            WHEN r_high=1 AND f_high=2 AND m_high=1 THEN 'D_发展客户'
            WHEN r_high=2 AND f_high=2 AND m_high=1 THEN 'E_挽留客户'
            WHEN r_high=1 AND f_high=2 AND m_high=2 THEN 'F_新客户'
            WHEN r_high=2 AND f_high=1 AND m_high=2 THEN 'G_一般保持'
            ELSE 'H_流失客户'
        END AS segment,
        m
    FROM scored
)
SELECT
    segment,
    COUNT(*) AS user_cnt,
    ROUND(SUM(m), 2) AS total_gmv,
    ROUND(100.0 * SUM(m) / SUM(SUM(m)) OVER (), 2) AS gmv_pct,
    -- 累计贡献(看前 N 群贡献了多少 GMV)
    ROUND(100.0 * SUM(SUM(m)) OVER (ORDER BY SUM(m) DESC) / SUM(SUM(m)) OVER (), 2) AS cum_gmv_pct
FROM segments
GROUP BY segment
ORDER BY total_gmv DESC"""))

cells.append(md("""### 9.2 案例 2:用户活跃度画像(Lead/Lag + 累计 + 排名)"""))

cells.append(sql_run("""# 案例 2:用户活跃度画像""",
"""WITH
user_active_days AS (
    SELECT DISTINCT user_id, DATE(event_time) AS dt
    FROM user_events WHERE event_type = 'pv'
),
with_metrics AS (
    SELECT
        user_id, dt,
        LEAD(dt) OVER (PARTITION BY user_id ORDER BY dt) AS next_dt,
        LAG(dt)  OVER (PARTITION BY user_id ORDER BY dt) AS prev_dt,
        COUNT(*) OVER (PARTITION BY user_id) AS total_active_days
    FROM user_active_days
),
gaps AS (
    SELECT
        user_id,
        total_active_days,
        ROUND(AVG(julianday(next_dt) - julianday(dt)), 2) AS avg_next_gap,
        ROUND(AVG(julianday(dt) - julianday(prev_dt)), 2) AS avg_prev_gap
    FROM with_metrics
    WHERE next_dt IS NOT NULL OR prev_dt IS NOT NULL
    GROUP BY user_id, total_active_days
)
SELECT
    user_id,
    total_active_days,
    avg_next_gap,
    avg_prev_gap,
    RANK() OVER (ORDER BY total_active_days DESC) AS activity_rank,
    NTILE(4) OVER (ORDER BY total_active_days DESC) AS activity_tier  -- 1=最活跃
FROM gaps
ORDER BY total_active_days DESC
LIMIT 15"""))

cells.append(md("""### 9.3 案例 3:商品销售 Top10%(NTILE + 累计 + 占比)"""))

cells.append(sql_run("""# 案例 3:商品销售 Top10%(用 NTILE 找,看贡献了 GMV 多少)""",
"""WITH
product_sales AS (
    SELECT
        p.product_id,
        p.category,
        p.product_name,
        SUM(o.amount) AS gmv,
        COUNT(*) AS sales_cnt
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'completed'
    GROUP BY p.product_id, p.category, p.product_name
),
ranked AS (
    SELECT *,
        NTILE(10) OVER (ORDER BY gmv DESC) AS decile,
        SUM(gmv) OVER (ORDER BY gmv DESC) AS cum_gmv,
        ROUND(100.0 * gmv / SUM(gmv) OVER (), 2) AS gmv_pct
    FROM product_sales
)
SELECT
    CASE WHEN decile = 1 THEN 'Top 10%' ELSE 'Bottom 90%' END AS product_group,
    COUNT(*) AS product_cnt,
    ROUND(SUM(gmv), 2) AS total_gmv,
    ROUND(100.0 * SUM(gmv) / (SELECT SUM(gmv) FROM ranked), 2) AS gmv_share
FROM ranked
GROUP BY decile = 1
ORDER BY product_group"""))

# ============== 10. 练习题 ==============

cells.append(md("""## 10. 练习题(6 道,带详细答案)

每题都有"陷阱提示",**先想 10 分钟再看答案**。

### Q1(2 星):用窗口函数算"用户首末单差"平均
> 提示:FIRST_VALUE + LAST_VALUE + AVG

### Q2(2 星):找出 GMV 排名前 5% 又在最近 30 天活跃的用户
> 提示:NTILE(20) = 1 + 最近 30 天条件

### Q3(3 星):用窗口函数实现"用户消费排名连续段"
> 提示:用 DENSE_RANK + 段编号,看有多少段并列

### Q4(3 星):用 LEAD/LAG 算"用户连续 2 天活跃"的比例
> 提示:LEAD 找次日,LAG 找前一日,差值 = 1

### Q5(3 星):用 RANK + 累计,看头部 1/2/3 群贡献 GMV
> 提示:RANK 排名 + SUM OVER (累计)

### Q6(4 星):完整实现"用户购买品类迁移"分析
> 提示:第一次购买品类 vs 最近一次购买品类
"""))

cells.append(md("### 答案"))

cells.append(sql_run("""# Q1:用户首末单差平均""",
"""WITH user_orders AS (
    SELECT user_id, order_date,
        FIRST_VALUE(order_date) OVER (PARTITION BY user_id ORDER BY order_date) AS first_dt,
        LAST_VALUE(order_date) OVER (
            PARTITION BY user_id ORDER BY order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_dt
    FROM orders WHERE status = 'completed'
)
SELECT
    user_id,
    CAST(julianday(last_dt) - julianday(first_dt) AS INTEGER) AS life_days
FROM user_orders
GROUP BY user_id
ORDER BY life_days DESC
LIMIT 10"""))

cells.append(sql_run("""# Q2:Top 5% GMV + 最近 30 天活跃
# 注意:NTILE 不能直接在 WHERE 用,先在子查询算好 decile 再过滤""",
"""WITH user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
user_decile AS (
    SELECT user_id, gmv, NTILE(20) OVER (ORDER BY gmv DESC) AS decile
    FROM user_gmv
),
top5pct AS (
    SELECT user_id, gmv FROM user_decile WHERE decile = 1
),
recent_active AS (
    SELECT DISTINCT user_id
    FROM user_events
    WHERE event_type = 'pv'
      AND event_time >= DATE('2025-03-01')
)
SELECT COUNT(*) AS target_users
FROM top5pct t
JOIN recent_active r ON t.user_id = r.user_id"""))

cells.append(sql_run("""# Q3:连续段分析(Gaps and Islands 简化版)""",
"""WITH user_orders AS (
    SELECT user_id, order_date,
        LAG(order_date) OVER (PARTITION BY user_id ORDER BY order_date) AS prev_date
    FROM orders WHERE status = 'completed'
),
with_streak AS (
    SELECT user_id, order_date,
        SUM(CASE
            WHEN prev_date IS NULL OR julianday(order_date) - julianday(prev_date) > 1
            THEN 1 ELSE 0
        END) OVER (PARTITION BY user_id ORDER BY order_date) AS streak_id
    FROM user_orders
)
SELECT user_id, streak_id, COUNT(*) AS streak_len
FROM with_streak
GROUP BY user_id, streak_id
ORDER BY streak_len DESC
LIMIT 15"""))

cells.append(sql_run("""# Q4:连续 2 天活跃用户比例""",
"""WITH user_active AS (
    SELECT DISTINCT user_id, DATE(event_time) AS dt
    FROM user_events WHERE event_type = 'pv'
),
with_next AS (
    SELECT user_id, dt,
        LEAD(dt) OVER (PARTITION BY user_id ORDER BY dt) AS next_dt
    FROM user_active
)
SELECT
    ROUND(100.0 * SUM(CASE WHEN julianday(next_dt) - julianday(dt) = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_2day_active
FROM with_next"""))

cells.append(sql_run("""# Q5:头部 1/2/3 群贡献 GMV""",
"""WITH user_gmv AS (
    SELECT user_id, SUM(amount) AS gmv
    FROM orders WHERE status = 'completed'
    GROUP BY user_id
),
ranked AS (
    SELECT user_id, gmv,
        RANK() OVER (ORDER BY gmv DESC) AS rk
    FROM user_gmv
)
SELECT
    CASE
        WHEN rk <= 10 THEN 'Top 10'
        WHEN rk <= 50 THEN 'Top 11-50'
        WHEN rk <= 100 THEN 'Top 51-100'
        ELSE 'Other'
    END AS tier,
    COUNT(*) AS user_cnt,
    ROUND(SUM(gmv), 2) AS total_gmv
FROM ranked
GROUP BY 1
ORDER BY MIN(rk)"""))

cells.append(sql_run("""# Q6:品类迁移分析""",
"""WITH user_category AS (
    SELECT
        o.user_id,
        p.category,
        o.order_date,
        ROW_NUMBER() OVER (PARTITION BY o.user_id ORDER BY o.order_date) AS first_rn,
        ROW_NUMBER() OVER (PARTITION BY o.user_id ORDER BY o.order_date DESC) AS last_rn
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'completed'
)
SELECT
    COUNT(DISTINCT user_id) AS total_users,
    SUM(CASE WHEN first_rn = 1 THEN 1 ELSE 0 END) AS first_orders,  -- 冗余演示
    COUNT(DISTINCT CASE WHEN first_rn = 1 THEN user_id END) AS users_with_first
FROM user_category"""))

# ============== 11. 小结 ==============

cells.append(md("""## 11. 小结 + 面试模板

### 11.1 速查表(贴墙)

| 函数 | 用途 | 一句话 |
|------|------|--------|
| ROW_NUMBER | 唯一编号 | 取每组 TopN 的标准选择 |
| RANK | 排名(跳号) | 真实排名场景 |
| DENSE_RANK | 排名(不跳号) | 金银铜牌制度 |
| NTILE(n) | 分 n 桶 | 头部/腰部/尾部 |
| SUM/AVG OVER | 累计/聚合 | 不减少行数的聚合 |
| LAG/LEAD | 上下行 | 环比/同比/留存 |
| FIRST/LAST_VALUE | 窗口首尾 | 找首末状态 |
| 命名窗口 | 复用窗口 | 减少重复 |

### 11.2 面试必背模板(直接用)

**Q: 讲讲窗口函数和聚合函数的区别**
> A: 聚合 + GROUP BY 把 N 行变 1 行,适合"算分组总和";窗口函数 + OVER 把 N 行变 N 行加额外列,适合"每行都拿上下文"。窗口函数支持 PARTITION BY 分窗口、ORDER BY 排序、ROWS BETWEEN 定义窗口框。

**Q: ROW_NUMBER / RANK / DENSE_RANK 的区别**
> A: ROW_NUMBER 永远唯一(并列也强制编号),适合严格 TopN;RANK 并列跳号(1,2,2,4),适合"前 N 名"语义;DENSE_RANK 并列不跳号(1,2,2,3),适合"金银铜牌"。

**Q: 留存率怎么用 SQL 算?**
> A: 思路:每个新用户 + 后续活跃日。先取每个用户的活跃日,LAG 找下次活跃日,差值 <= 1 就是次日留存。然后 `SUM(CASE WHEN diff <= 1 THEN 1 END) / 总用户数`。

**Q: 1 亿行数据用窗口函数会不会很慢?**
> A: 看是否需要全局排序。如果 PARTITION 列 + ORDER 列有联合索引,排序开销小;否则走全表扫 + 排序,可能 30 秒+。生产上常用宽表预计算 + 增量更新,避免大表实时窗口。

### 11.3 自测清单

- [ ] 能不看答案写出 8 大函数的基础示例
- [ ] 解释清楚 ROW_NUMBER / RANK / DENSE_RANK 差异
- [ ] 知道 LAST_VALUE 必须显式写 ROWS BETWEEN
- [ ] 能用 LAG/LAG 写出留存率
- [ ] 能把"找最近一次"的相关子查询改写成窗口函数
- [ ] 知道 NTILE 不保证等分(可能 9% 或 11%)

**全部 ✅ 之后可以推进 W2**。
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

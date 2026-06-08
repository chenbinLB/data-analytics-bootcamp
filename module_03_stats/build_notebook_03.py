# -*- coding: utf-8 -*-
"""
build_notebook_03.py — module_03_stats/03_business_skills.ipynb
================================================================
业务能力:指标体系 / 异动归因 / 数据叙事
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "03_business_skills.ipynb"


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
        "    np.random.seed(42)",
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


cells = []

cells.append(md("""# W3.3 — 业务能力(数据分析师的"软实力")

> 技术再强,业务不懂也是白搭。本节讲 3 个核心业务能力。
> 本节按 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试

## 本节大纲
- **0. 原理总览**:为什么业务能力比技术重要
- **1. 指标体系搭建**(OSM / AARRR / 虚荣指标陷阱)
- **2. 异动归因分析**(DAU 突然下降怎么办)
- **3. 数据叙事**(把分析变成业务故事)

## 学习建议
- 这部分"软实力"大厂面试高频
- 重点是"模板化"思维(拿到问题有套路)
"""))

cells.append(py_run([
    "import numpy as np",
    "import pandas as pd",
    "print('OK')",
]))

# 0. 原理
cells.append(md("""## 0. 原理总览

### 0.1 大厂面试为什么问业务题?

| 问题 | 考察 |
|------|------|
| "DAU 下降 20% 怎么排查?" | 异动归因能力 |
| "设计北极星指标" | 指标体系思维 |
| "怎么用数据说服老板?" | 数据叙事能力 |
| "GMV 提升 5%,但毛利下降 3%,你怎么看?" | 业务洞察能力 |

### 0.2 数据分析师 5 大软实力

1. **指标体系设计**:从 0 搭建一套指标
2. **异动归因**:指标异常时快速定位原因
3. **数据叙事**:把分析变成业务能听懂的故事
4. **业务理解**:懂行业(电商/金融/广告)的关键指标
5. **跨部门沟通**:和 PM / 运营 / 老板对话

### 0.3 大厂铁律

- **没有"对的"指标,只有"合适的"指标**——因公司阶段而异
- **虚荣指标 vs 可执行指标**:DAU 涨了但用户次日留存下降,可能是注册送钱
- **永远问 "so what"**:数据变化了,业务该怎么办?
"""))

# 1. 指标体系
cells.append(md("""## 1. 指标体系搭建

### 1.1 原理

**指标体系的 3 个层次**:
- **战略层**:北极星指标(North Star Metric, 1 个)
- **战术层**:业务模块指标(几个, 衡量方向)
- **执行层**:日常报表(几十个,日常监控)

**常见框架**:
- **OSM** (Objective / Strategy / Measure):目标 → 策略 → 指标
- **AARRR** (海盗指标):Acquisition / Activation / Retention / Revenue / Referral
- **HEART**:Happiness / Engagement / Adoption / Retention / Task success
- **AARRR + 细分**:每个阶段再分维度(渠道/城市/品类)

### 1.2 基础案例:OSM 拆解(从目标到指标)"""))

cells.append(py_run([
    "# 业务目标:提升 GMV",
    "# OSM 拆解:",
    "",
    "O = '提升电商平台 GMV'  # Objective 目标",
    "S = [  # Strategy 策略",
    "    '拉新(更多新用户)',",
    "    '促活(提升复购率)',",
    "    '提价(提高客单价)',",
    "]",
    "M = {  # Measure 指标",
    "    '拉新': ['日新用户数', 'CAC(获客成本)', '新用户转化率'],",
    "    '促活': ['复购率', '30 日留存', 'MAU/DAU'],",
    "    '提价': ['ARPU(每用户收入)', '客单价', '高客单用户占比'],",
    "}",
    "",
    "for s, ms in zip(S, M.values() if isinstance(M, dict) else []):",
    "    print(f'{s}: {ms}')",
    "",
    "# 北极星指标:综合体现商业价值的单一指标",
    "print('\\n北极星指标: 总 GMV(简单直接,代表商业价值)')",
]))

cells.append(md("""### 1.3 进阶案例 1:用户生命周期价值(LTV) 拆解"""))

cells.append(py_run([
    "# LTV = 生命周期价值(用户整个生命周期贡献的总收入)",
    "# LTV = 留存率 × 单用户 ARPU / 流失率",
    "",
    "# 简化计算:用我们手头的真实数据",
    "if 'orders' not in globals():",
    "    orders = pd.read_sql('SELECT user_id, order_date, amount FROM orders WHERE status = \"completed\"', conn)",
    "    orders['order_date'] = pd.to_datetime(orders['order_date'])",
    "",
    "# 每个用户的总消费",
    "user_gmv = orders.groupby('user_id')['amount'].sum()",
    "print('用户 LTV 统计:')",
    "print(user_gmv.describe().round(2))",
    "",
    "# LTV 分桶(头部 10% 价值)",
    "p90 = user_gmv.quantile(0.9)",
    "print(f'\\n头部 10% 用户的 LTV 阈值: {p90:.0f}')",
    "print(f'头部 10% 用户数: {(user_gmv >= p90).sum()}')",
    "print(f'头部 10% 贡献 GMV: {user_gmv[user_gmv >= p90].sum():.0f}(占 {user_gmv[user_gmv >= p90].sum()/user_gmv.sum()*100:.1f}%)')",
]))

cells.append(md("""### 1.4 进阶案例 2:虚荣指标 vs 可执行指标"""))

cells.append(py_run([
    "# 虚荣指标:涨了但不能 action 的指标",
    "vanity_metrics = [",
    "    ('总注册用户数', '涨了说明产品有拉新,但不说明活跃度'),",
    "    ('总 GMV', '涨了说明规模扩大,但可能毛利率下降'),",
    "    ('页面 PV', '涨了说明访问多,但可能跳出率也涨了'),",
    "]",
    "",
    "actionable_metrics = [",
    "    ('DAU/MAU(粘性)', '高说明用户天天用,低说明流失风险'),",
    "    ('净推荐值 NPS', '高说明用户愿意推荐'),",
    "    ('每用户月均订单数', '涨说明复购强'),",
    "    ('单订单履约时长', '降说明体验好'),",
    "]",
    "",
    "print('=' * 50)",
    "print('虚荣指标(涨了不告诉你怎么办)')",
    "print('=' * 50)",
    "for m, why in vanity_metrics:",
    "    print(f'  {m}: {why}')",
    "",
    "print('\\n' + '=' * 50)",
    "print('可执行指标(涨了告诉你该做什么)')",
    "print('=' * 50)",
    "for m, why in actionable_metrics:",
    "    print(f'  {m}: {why}')",
]))

cells.append(md("""### 1.5 面试题

- Q1: 怎么选北极星指标?
  A: 看商业本质:电商 → GMV;内容 → DAU/时长;社交 → 互动量。要"既体现商业价值,又能驱动团队行动"。
- Q2: GMV 涨了 10% 但利润没涨,怎么解释?
  A: 拆解:GMV = 订单量 × 客单价。可能 1) 订单量涨但客单价降(促销);2) 退货率涨(抵消了 GMV);3) 成本涨(补贴)。
- Q3: 业务要"提升用户活跃度",你怎么拆?
  A: 定义"活跃"(DAU/MAU/访问频次/功能使用深度),拆维度(新/老/不同渠道),设提升目标,找抓手(推送/签到/活动)。
"""))

# 2. 异动归因
cells.append(md("""## 2. 异动归因分析(大厂面试高频)

### 2.1 原理

**异动归因 5 步法**:
1. **确认异常**:不是数据问题(ETL 漏数、统计口径变化)
2. **量化异常**:今天比平时低/高多少?绝对值和相对值
3. **拆分维度**:看是哪个维度异常(渠道/城市/品类/用户群)
4. **找外部原因**:节假日、竞品、舆情、政策
5. **定位根因**:对比实验,看哪个是 trigger

### 2.2 基础案例:DAU 下降 20% 排查(mega cell)"""))

cells.append(py_run([
    "print('=' * 60)",
    "print('实战:DAU 异动归因(模拟场景)')",
    "print('=' * 60)",
    "",
    "if 'orders' not in globals():",
    "    orders = pd.read_sql('SELECT order_date, user_id, amount FROM orders WHERE status = \"completed\"', conn)",
    "    orders['order_date'] = pd.to_datetime(orders['order_date'])",
    "    orders = orders.set_index('order_date')",
    "if 'users' not in globals():",
    "    users = pd.read_sql('SELECT * FROM users', conn)",
    "",
    "# Step 1:DAU 日活(用有下单的用户作为活跃用户代理)",
    "dau = orders.resample('D')['user_id'].nunique()",
    "print('最近 14 天 DAU:')",
    "print(dau.tail(14).round(0))",
    "",
    "# Step 2:计算 7 日均值 + 检测异常",
    "dau_ma7 = dau.rolling('7D').mean()",
    "dau_std = dau.rolling('7D').std()",
    "today = dau.iloc[-1]",
    "expected = dau_ma7.iloc[-2]  # 昨天 7 日均值",
    "expected_std = dau_std.iloc[-2]",
    "z_score = (today - expected) / expected_std if expected_std > 0 else 0",
    "",
    "print(f'\\n今日 DAU: {today}')",
    "print(f'7 日均值: {expected:.0f}')",
    "print(f'Z-score: {z_score:.2f}(> 2 算异常)')",
    "is_anomaly = abs(z_score) > 2",
    "print(f'\\n是否异常: {is_anomaly}')",
    "",
    "if is_anomaly:",
    "    print('\\n--- Step 3:维度拆解 ---')",
    "    # 按渠道拆",
    "    today_orders = orders[orders.index.date == dau.index[-1].date()]",
    "    today_with_channel = today_orders.merge(users[['user_id', 'channel']], on='user_id', how='left')",
    "    channel_dau = today_with_channel.groupby('channel')['user_id'].nunique()",
    "    baseline_dau = orders.merge(users[['user_id', 'channel']], on='user_id', how='left').set_index('order_date').resample('D').apply(lambda x: x.groupby('channel')['user_id'].nunique())",
    "    baseline_avg = baseline_dau.unstack().rolling('7D').mean().iloc[-2].fillna(0)",
    "    ",
    "    print('\\n各渠道 DAU(今日 vs 7 日均值):')",
    "    for ch in channel_dau.index:",
    "        today_cnt = channel_dau.get(ch, 0)",
    "        baseline_cnt = baseline_avg.get(ch, 0)",
    "        pct = (today_cnt - baseline_cnt) / baseline_cnt * 100 if baseline_cnt > 0 else 0",
    "        print(f'  {ch}: 今日 {today_cnt} vs 均值 {baseline_cnt:.0f}({pct:+.1f}%)')",
]))

cells.append(md("""### 2.3 进阶案例 1:异动归因检查清单(模板)"""))

cells.append(py_run([
    "# 异动归因 5 步检查清单",
    "checklist = [",
    "    '1. 【数据本身】数据是否完整?ETL 跑通了吗?有没有缺日?',",
    "    '2. 【统计口径】统计口径最近改了吗?是否新老数据混用?',",
    "    '3. 【外部环境】今天/昨天是节假日/双 11 / 春节/疫情/竞品活动?',",
    "    '4. 【产品改动】产品最近发版了吗?有没有上线 BUG?',",
    "    '5. 【渠道异常】某个投放渠道暂停了?某个广告主跑完了?',",
    "    '6. 【分维度拆】哪个城市/渠道/品类/用户群异常?',",
    "    '7. 【对照组】同期行业大盘是否也有类似波动?',",
    "    '8. 【A/B 实验】是不是某个 A/B 实验分流出了错?',",
    "]",
    "for item in checklist:",
    "    print(item)",
]))

cells.append(md("""### 2.4 进阶案例 2:同环比 + 周环比(归因常用)"""))

cells.append(py_run([
    "if 'orders' not in globals():",
    "    orders = pd.read_sql('SELECT order_date, user_id, amount FROM orders WHERE status = \"completed\"', conn)",
    "    orders['order_date'] = pd.to_datetime(orders['order_date'])",
    "    orders = orders.set_index('order_date')",
    "",
    "dau = orders.resample('D')['user_id'].nunique()",
    "",
    "# 同比 = 7 天前同一天",
    "dau_7d_ago = dau.shift(7)",
    "# 环比 = 昨天",
    "dau_1d_ago = dau.shift(1)",
    "",
    "compare = pd.DataFrame({",
    "    'today': dau,",
    "    'yesterday': dau_1d_ago,",
    "    '7d_ago': dau_7d_ago,",
    "    'mom_pct': (dau - dau_1d_ago) / dau_1d_ago * 100,",
    "    'wow_pct': (dau - dau_7d_ago) / dau_7d_ago * 100,",
    "})",
    "",
    "print('最近 7 天(今天 vs 昨天 vs 7 天前):')",
    "print(compare.tail(7).round(2))",
    "",
    "# 自动化归因(简易版)",
    "today_dau = dau.iloc[-1]",
    "if compare['wow_pct'].iloc[-1] < -20:",
    "    print(f'\\n同比下降 {abs(compare[\"wow_pct\"].iloc[-1]):.0f}%,可能是:')",
    "    print('  1. 7 天前基数太高(节假日/活动后)')",
    "    print('  2. 持续问题(对比昨天也下降 → 真异常)')",
    "elif compare['wow_pct'].iloc[-1] > 20:",
    "    print(f'\\n同比上涨 {compare[\"wow_pct\"].iloc[-1]:.0f}%,可能:')",
    "    print('  1. 7 天前基数太低(基数效应)')",
    "    print('  2. 真增长(对比昨天也涨 → 真增长)')",
    "else:",
    "    print('\\n同比无显著变化(±20%)')",
]))

cells.append(md("""### 2.5 面试题

- Q1: DAU 下降 20% 怎么排查?
  A: 5 步:1) 确认数据;2) 量化异常;3) 分维度拆;4) 查外部;5) 定位根因。
- Q2: GMV 涨了但 DAU 降了,怎么看?
  A: GMV = DAU × 客单价,可能 1) 客单价大幅提升(高净值用户买贵的);2) 退货减少(净 GMV 涨);3) 渠道引流不精准但转化率高。
- Q3: 指标异动但找不到原因怎么办?
  A: 1) 看同期行业大盘;2) 跟业务方对一下(他们可能知道);3) 延长窗口观察 7-14 天再下结论。
"""))

# 3. 数据叙事
cells.append(md("""## 3. 数据叙事(把分析变成故事)

### 3.1 原理

**数据叙事 5 段式**(结构化表达):
1. **背景**:什么问题 / 为什么要做
2. **发现**:数据告诉了我们什么(关键发现)
3. **归因**:为什么会这样(原因)
4. **建议**:业务应该怎么办(可执行)
5. **预期**:做了之后会怎样(效果预测)

**大厂铁律**:
- 数字本身不说谎,但"叙事框架"决定听众怎么理解
- 5W1H:Who / What / When / Where / Why / How
- 故事要有"主角"(用户 / GMV / 转化率)和"冲突"(为什么跌了)+ "解决"(怎么办)

### 3.2 基础案例:5 段式分析报告模板"""))

cells.append(py_run([
    "# 5 段式报告模板",
    "template = '''",
    "===== [报告标题:一句话说结论] =====",
    "",
    "1. 背景(Why):",
    "   - 业务问题:...",
    "   - 重要性:...",
    "",
    "2. 发现(What):",
    "   - 关键数据:... vs 预期/历史",
    "   - 量化影响:...(影响多大)",
    "",
    "3. 归因(Why):",
    "   - 主因 1:... (数据支撑)",
    "   - 主因 2:... (数据支撑)",
    "   - 主因 3:... (数据支撑)",
    "",
    "4. 建议(How):",
    "   - 短期(本周):... (可执行)",
    "   - 中期(本月):...",
    "   - 长期(本季):...",
    "",
    "5. 预期(So What):",
    "   - 如果做:预计 GMV 提升 X%",
    "   - 如果不做:预计继续下滑 Y%",
    "   - 需要资源:...",
    "====='''",
    "print(template)",
]))

cells.append(md("""### 3.3 进阶案例 1:把"数据发现"变成"业务故事" """))

cells.append(py_run([
    "# 场景:头部 10% 用户贡献 60% GMV",
    "# 这是个数据发现,怎么变成业务故事?",
    "",
    "# 数据层面:",
    "data_finding = '头部 10% 用户贡献 60% GMV'",
    "",
    "# 业务故事框架(5 段式):",
    "story = '''",
    "===== 用户结构呈典型二八分布 =====",
    "",
    "1. 背景:",
    "   - 用户结构是否合理,决定资源投入方向",
    "",
    "2. 发现:",
    "   - 头部 10% 用户贡献 60% GMV(Pareto 分布)",
    "   - 中间 30% 用户贡献 30% GMV",
    "   - 尾部 60% 用户仅贡献 10% GMV",
    "",
    "3. 归因:",
    "   - 头部用户:高客单价 + 高复购(每月 2-3 单)",
    "   - 中部用户:正常消费(每月 1 单)",
    "   - 尾部用户:偶尔尝试(数月 1 单)",
    "",
    "4. 建议:",
    "   - 短期:对头部用户做 VIP 服务(专属客服/优先发货)",
    "   - 中期:推出会员体系(头部享折扣/积分翻倍)",
    "   - 长期:提升中部 → 头部(精准营销 + 复购激励)",
    "",
    "5. 预期:",
    "   - 做 VIP 服务:头部 10% 留存提升 5%,GMV 提升 3%",
    "   - 推会员体系:中部 30% 转化为头部 5%,GMV 提升 2%",
    "   - 不做:用户结构固化,GMV 增长见顶",
    "====='''",
    "print(story)",
]))

cells.append(md("""### 3.4 进阶案例 2:可视化叙事(数据故事图)"""))

cells.append(py_run([
    "# 实战:画一个「GMV 增长拆解瀑布图」",
    "# 解释:Growth = 新用户贡献 + 老用户复购 + 客单价提升",
    "",
    "fig, ax = plt.subplots()",
    "",
    "# 拆解数据",
    "labels = ['Q1 GMV', '新用户贡献', '老用户复购', '客单价提升', 'Q2 GMV']",
    "values = [100, 30, 15, 10, 155]  # 假设值",
    "delta = [values[1], values[2], values[3], values[4] - values[3]]",
    "",
    "# 画柱状图(从下往上累加)",
    "ax.bar(labels[0], values[0], color='steelblue', label='Q1 基线')",
    "bottom = values[0]",
    "colors = ['#90EE90', '#FFB6C1', '#FFD700']",
    "for i, (lbl, v, c) in enumerate(zip(labels[1:-1], values[1:-1], colors)):",
    "    ax.bar(lbl, v, bottom=bottom, color=c, label=lbl)",
    "    bottom += v",
    "ax.bar(labels[-1], bottom, color='coral', label='Q2 合计')",
    "",
    "ax.set_title('Q2 GMV 增长拆解(瀑布图)', fontsize=14)",
    "ax.set_ylabel('GMV')",
    "ax.legend(loc='upper left', fontsize=9)",
    "plt.tight_layout()",
    "plt.show()",
]))

cells.append(md("""### 3.5 面试题

- Q1: 怎么向老板汇报"DAU 涨了但收入没涨"?
  A: 用 5 段式:背景(收入要看 GMV 不是 DAU)→ 发现(DAU 涨 X%,但客单价跌 Y%)→ 归因(新用户低客单价用户多)→ 建议(做新用户引导转化)→ 预期。
- Q2: 怎么让数据故事更有说服力?
  A: 1) 数字 + 业务含义("涨 10% GMV" 不如 "多挣 500 万");2) 对比("比竞品高 3%");3) 趋势(连续 3 月增长)。
- Q3: 数据发现怎么分级(哪些值得报告)?
  A: 业务影响大 + 数据可信 + 业务可执行 = P0(立即报告);只一两个条件满足 = P1(下个迭代);都弱 = 不报告。
"""))

# 4. 综合实战
cells.append(md("""## 4. 综合实战:周报生成(自动 5 段式)"""))

cells.append(py_run([
    "print('=' * 60)",
    "print('周报自动生成')",
    "print('=' * 60)",
    "",
    "if 'orders' not in globals():",
    "    orders = pd.read_sql('SELECT order_date, user_id, amount FROM orders WHERE status = \"completed\"', conn)",
    "    orders['order_date'] = pd.to_datetime(orders['order_date'])",
    "    orders = orders.set_index('order_date')",
    "if 'users' not in globals():",
    "    users = pd.read_sql('SELECT * FROM users', conn)",
    "",
    "# 本周 / 上周",
    "this_week = orders[orders.index >= orders.index.max() - pd.Timedelta(days=7)]",
    "last_week = orders[(orders.index < orders.index.max() - pd.Timedelta(days=7)) &",
    "                  (orders.index >= orders.index.max() - pd.Timedelta(days=14))]",
    "",
    "tw_gmv = this_week['amount'].sum()",
    "lw_gmv = last_week['amount'].sum()",
    "tw_dau = this_week['user_id'].nunique()",
    "lw_dau = last_week['user_id'].nunique()",
    "tw_aov = this_week['amount'].mean()",
    "lw_aov = last_week['amount'].mean()",
    "",
    "report = f'''",
    "===== 本周电商运营周报 =====",
    "",
    "1. 背景:本周(过去 7 天)运营数据,对比上周",
    "",
    "2. 发现:",
    "   - GMV: {tw_gmv:,.0f} 元(上周 {lw_gmv:,.0f},环比 {(tw_gmv-lw_gmv)/lw_gmv*100:+.1f}%)",
    "   - 活跃用户: {tw_dau}(上周 {lw_dau},环比 {(tw_dau-lw_dau)/lw_dau*100:+.1f}%)",
    "   - 客单价: {tw_aov:.0f} 元(上周 {lw_aov:.0f},环比 {(tw_aov-lw_aov)/lw_aov*100:+.1f}%)",
    "",
    "3. 归因:",
    "'''",
    "if tw_gmv > lw_gmv * 1.1:",
    "    report += '   - GMV 大幅上涨,可能来自促销活动或新增渠道\\n'",
    "elif tw_gmv < lw_gmv * 0.9:",
    "    report += '   - GMV 大幅下滑,需要排查(活动结束?竞品?产品问题?)\\n'",
    "else:",
    "    report += '   - GMV 平稳,在正常波动范围内\\n'",
    "",
    "if tw_dau > lw_dau * 1.1:",
    "    report += '   - 活跃用户大涨,可能来自新增渠道或拉新活动\\n'",
    "elif tw_dau < lw_dau * 0.9:",
    "    report += '   - 活跃用户下降,需要关注留存(可能流失加剧)\\n'",
    "",
    "report += f'''",
    "4. 建议:",
    "   - 继续监控下周数据,确认本周表现是否持续",
    "   - 如有异动,按'5 步法'归因(数据/口径/外部/产品/维度)",
    "",
    "5. 预期:下周数据应保持稳定,如有活动需提前对齐",
    "====='''",
    "print(report)",
]))

cells.append(md("""## 5. 小结

### 速查表

| 业务能力 | 核心 |
|---------|------|
| 指标体系 | 北极星 + 战术 + 执行 3 层;OSM/AARRR/HEART 框架 |
| 异动归因 | 5 步法:数据 / 口径 / 外部 / 维度 / 根因 |
| 数据叙事 | 5 段式:背景 / 发现 / 归因 / 建议 / 预期 |
| 虚荣指标 | 涨了不告诉你怎么办的指标 |
| 可执行指标 | 涨了能驱动行动的指标 |

### 自测清单

- [ ] 能从 0 设计一套指标体系
- [ ] 能用 OSM 拆解业务目标
- [ ] 能按 5 步法排查异动
- [ ] 能用 5 段式写分析报告
- [ ] 能区分虚荣指标 vs 可执行指标
- [ ] 能用数据故事说服业务方

**全部 ✅ 之后推进 W4(实战项目 + AI 协同 + 求职准备)。**
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

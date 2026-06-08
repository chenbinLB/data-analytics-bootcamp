# -*- coding: utf-8 -*-
"""
build_notebook_02.py — module_03_stats/02_ab_testing.ipynb
================================================================
A/B 测试设计 + 完整 pipeline(按 5 段结构)
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "02_ab_testing.ipynb"


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
        "    from math import ceil",
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

cells.append(md("""# W3.2 — A/B 测试设计 + 完整 pipeline(大厂数分必考)

> A/B 测试是数据分析师的"杀手锏"——把"我觉得这样更好"变成"统计上有 95% 把握更好"。
> 本节按 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试

## 本节大纲
- **0. 原理总览**:A/B 测试的核心逻辑
- **1. 实验设计**(假设、分组、指标、时长)
- **2. 样本量计算**(用公式 + Python 工具)
- **3. 完整 pipeline**(造数据 -> 分组 -> 检验 -> 决策)
- **4. 实战:用真实数据改造一个 A/B 测试场景**

## 学习建议
- A/B 测试是大厂面试 100% 考
- 重点掌握"样本量计算 + 假设检验 + 决策"完整流程
- 业务经验:什么时候不能做 A/B 测试?
"""))

cells.append(py_run([
    "import numpy as np",
    "import pandas as pd",
    "print('OK')",
]))

# 0. 原理
cells.append(md("""## 0. 原理总览:A/B 测试核心逻辑

### 0.1 流程总览

```
业务问题:  新功能 / 新策略 真的更好吗?
    ↓
实验设计:  H0(无差异) / H1(有差异) / 指标 / 时长
    ↓
样本量:  需要多少样本? MDE / α / β
    ↓
随机分组:  A 组(旧) vs B 组(新)
    ↓
收集数据:  跑 X 天
    ↓
假设检验:  t 检验 / 卡方 / 显著性
    ↓
决策:     上线 / 调整 / 放弃
```

### 0.2 大厂 A/B 测试 5 大要素

| 要素 | 含义 | 业务 |
|------|------|------|
| 假设 | H0 / H1 | "新版本转化率 = 旧版本" |
| 指标 | OEC(Overall Evaluation Criterion) | GMV / 转化率 / 留存 |
| 分组 | 随机、对照、互斥 | 用户 ID hash % 2 |
| 时长 | 至少覆盖 1 个完整业务周期 | 1 个周末 / 1 个发薪日 |
| 样本量 | 算出来,不是拍脑袋 | 1000 vs 1000(取决于效应大小) |

### 0.3 大厂铁律

- **AA 测试**:上线前先跑 7 天 A vs A(确保分组无偏)
- **互斥用户**:同一用户只能在 A 或 B 组(避免污染)
- **SRM 检查**(Sample Ratio Mismatch):实际分组比例跟预期差 > 1% 要警惕
- **辛普森悖论**:整体结论和分层结论相反
- **过早停止**:"看 100 个用户就显著就停了"——多次检验需校正
"""))

# 1. 实验设计
cells.append(md("""## 1. 实验设计(5 大要素)

### 1.1 原理

**好的实验设计 = 明确假设 + 选对指标 + 算够样本 + 跑够时间**

### 1.2 基础案例:把业务问题翻译成假设"""))

cells.append(py_run([
    "# 业务问题:把结账按钮从橙色换成绿色,能提高转化率吗?",
    "",
    "# 翻译成假设:",
    "H0 = '绿色按钮的转化率 = 橙色按钮的转化率(无差异)'",
    "H1 = '绿色按钮的转化率 > 橙色按钮的转化率(有差异)'",
    "",
    "# 关键指标(OEC):结账转化率(最重要的北极星指标)",
    "# 护栏指标:退款率(不能因为转化率上升导致退款也上升)",
    "print('主指标: 结账转化率(转化 / 访问)')",
    "print('护栏指标: 退款率(退款单 / 总单) / 客单价(单笔金额)')",
    "",
    "# 最小可检测效应(MDE):业务上值得追求的最小提升",
    "baseline_rate = 0.10  # 当前转化率 10%",
    "mde = 0.01  # 想检测 1% 绝对提升(从 10% 到 11%)",
    "print(f'\\n基线转化率: {baseline_rate:.1%}')",
    "print(f'最小可检测效应(MDE): {mde:.1%}(相对提升 {(mde/baseline_rate)*100:.0f}%)')",
]))

cells.append(md("""### 1.3 进阶案例:SRM 检查(分组是否平衡)"""))

cells.append(py_run([
    "# 模拟 SRM 检查",
    "np.random.seed(42)",
    "n_total = 10000",
    "",
    "# 情况 1:分组正常(各 5000)",
    "group_a = np.random.choice([0, 1], n_total)",
    "cnt_a = group_a.sum()",
    "cnt_b = len(group_a) - cnt_a",
    "print(f'正常分组: A={cnt_a}, B={cnt_b}, 比例 {cnt_a/n_total:.4f}')",
    "",
    "# SRM 卡方检验",
    "from scipy.stats import chisquare",
    "expected = [n_total / 2, n_total / 2]",
    "actual = [cnt_a, cnt_b]",
    "chi2, p_srm = chisquare(actual, f_exp=expected)",
    "print(f'SRM 卡方: chi2={chi2:.3f}, p={p_srm:.4f}')",
    "print(f'结论: {\"分组无偏(无 SRM)\" if p_srm > 0.01 else \"分组有偏(有 SRM,需要排查)\"}')",
    "",
    "# 情况 2:分组失衡(SRM 触发)",
    "group_a_biased = np.random.choice([0, 1], n_total, p=[0.55, 0.45])",
    "cnt_a2 = group_a_biased.sum()",
    "cnt_b2 = len(group_a_biased) - cnt_a2",
    "chi2_2, p_srm_2 = chisquare([cnt_a2, cnt_b2], f_exp=expected)",
    "print(f'\\n失衡分组: A={cnt_a2}, B={cnt_b2}, 比例 {cnt_a2/n_total:.4f}')",
    "print(f'SRM 卡方: chi2={chi2_2:.3f}, p={p_srm_2:.4f}')",
    "print(f'结论: {\"分组无偏\" if p_srm_2 > 0.01 else \"分组有偏(SRM!)\"}')",
]))

cells.append(md("""### 1.4 面试题

- Q1: 什么时候不适合做 A/B 测试?
  A: 1) 改动太大风险高;2) 流量太小跑不出统计显著性;3) 周期不够(覆盖不到完整业务周期);4) 已有其他实验在跑(互相干扰)。
- Q2: 怎么解决"分组污染"?
  A: 1) 互斥(用户只能进 A 或 B);2) hash 取模稳定分组;3) cookie/device ID 作分组依据。
"""))

# 2. 样本量计算
cells.append(md("""## 2. 样本量计算(科学实验的核心)

### 2.1 原理

样本量由 4 个因素决定:
- **基线转化率** p0(现状)
- **最小可检测效应** MDE(想检测到的最小变化)
- **α**(显著性水平,常用 0.05)
- **β**(1 - 统计功效,常用 0.2,即 80% 功效)

**公式**(双样本比例):
```
n = (Z_{1-α/2} + Z_{1-β})² × (p1(1-p1) + p0(1-p0)) / (p1 - p0)²
```

简化近似(常用):
```
n ≈ 16 × p × (1-p) / MDE²  (p 和 MDE 用小数)
```

### 2.2 基础案例:用公式算样本量"""))

cells.append(py_run([
    "from math import ceil",
    "from scipy.stats import norm",
    "",
    "def sample_size_proportion(p0, mde, alpha=0.05, power=0.8):",
    "    \"\"\"双样本比例检验的样本量(每组)\"\"\"",
    "    p1 = p0 + mde",
    "    z_alpha = norm.ppf(1 - alpha / 2)  # 双尾",
    "    z_beta = norm.ppf(power)",
    "    p_avg = (p0 + p1) / 2",
    "    # 标准公式",
    "    p1_var = p0 * (1 - p0) + p1 * (1 - p1)",
    "    numerator = (z_alpha * (2 * p_avg * (1 - p_avg)) ** 0.5 + z_beta * (p1_var ** 0.5)) ** 2",
    "    n = numerator / (mde ** 2)",
    "    return ceil(n)",
    "",
    "# 自包含:函数定义",
    "from scipy.stats import norm",
    "from math import ceil",
    "def sample_size_proportion(p0, mde, alpha=0.05, power=0.8):",
    "    p1 = p0 + mde",
    "    z_alpha = norm.ppf(1 - alpha / 2)",
    "    z_beta = norm.ppf(power)",
    "    p_avg = (p0 + p1) / 2",
    "    p1_var = p0 * (1 - p0) + p1 * (1 - p1)",
    "    numerator = (z_alpha * (2 * p_avg * (1 - p_avg)) ** 0.5 + z_beta * (p1_var ** 0.5)) ** 2",
    "    n = numerator / (mde ** 2)",
    "    return ceil(n)",
    "",
    "# 场景 1:基线 10%,想检测 +1% 绝对提升",
    "p0 = 0.10",
    "mde = 0.01",
    "n1 = sample_size_proportion(p0, mde)",
    "print(f'基线 {p0:.0%}, MDE {mde:.0%}: 每组需要 {n1} 样本,共 {n1*2}')",
    "",
    "# 场景 2:基线 10%,想检测 +2% 绝对提升",
    "n2 = sample_size_proportion(p0, 0.02)",
    "print(f'基线 {p0:.0%}, MDE +2%: 每组 {n2},共 {n2*2}')",
    "",
    "# 场景 3:基线 10%,想检测 +0.5% 绝对提升(更难,需要更多样本)",
    "n3 = sample_size_proportion(p0, 0.005)",
    "print(f'基线 {p0:.0%}, MDE +0.5%: 每组 {n3},共 {n3*2}')",
    "",
    "# 场景 4:基线 5%(更小),MDE +0.5%",
    "n4 = sample_size_proportion(0.05, 0.005)",
    "print(f'基线 5%, MDE +0.5%: 每组 {n4},共 {n4*2}')",
]))

cells.append(md("""### 2.3 进阶案例:样本量表(常用场景)"""))

cells.append(py_run([
    "# 自包含:函数定义",
    "from scipy.stats import norm",
    "from math import ceil",
    "if 'sample_size_proportion' not in globals():",
    "    def sample_size_proportion(p0, mde, alpha=0.05, power=0.8):",
    "        p1 = p0 + mde",
    "        z_alpha = norm.ppf(1 - alpha / 2)",
    "        z_beta = norm.ppf(power)",
    "        p_avg = (p0 + p1) / 2",
    "        p1_var = p0 * (1 - p0) + p1 * (1 - p1)",
    "        numerator = (z_alpha * (2 * p_avg * (1 - p_avg)) ** 0.5 + z_beta * (p1_var ** 0.5)) ** 2",
    "        n = numerator / (mde ** 2)",
    "        return ceil(n)",
    "",
    "# 样本量表:不同 (基线, MDE) 组合",
    "print('样本量表(α=0.05, power=0.8, 双尾):')",
    "print(f'{\"基线\":<10}{\"MDE\":<15}{\"每组样本\":<15}{\"总样本\":<15}')",
    "for p0 in [0.05, 0.10, 0.20, 0.30]:",
    "    for mde in [0.005, 0.01, 0.02, 0.05]:",
    "        if p0 + mde <= 1:",
    "            n = sample_size_proportion(p0, mde)",
    "            print(f'{p0:<10}{mde:<15.3f}{n:<15,}{n*2:<15,}')",
    "    print()",
]))

cells.append(md("""### 2.4 面试题

- Q1: MDE 怎么定?
  A: 业务判断——"这个效应小到不值得做,就当没效果"。常用 1% 绝对或 10% 相对。
- Q2: 样本量越大越好吗?
  A: 不是。样本量越大,小效应也"显著",但 1% 提升可能不 care。要平衡"统计显著"和"业务重要"。
- Q3: 怎么加快实验?
  A: 1) 增大 MDE(检测大效应);2) 提高基线(找高转化场景);3) 调低 power(到 0.7);4) 用 CUPED(用历史数据降方差)。
"""))

# 3. 完整 pipeline
cells.append(md("""## 3. 完整 A/B 测试 pipeline(mega cell)

从造数据 -> 分组 -> 检验 -> 决策,完整跑一遍。"""))

cells.append(py_run([
    "print('=' * 60)",
    "print('完整 A/B 测试 pipeline')",
    "print('=' * 60)",
    "",
    "np.random.seed(42)",
    "",
    "# ===== Step 1:实验设计 =====",
    "print('\\n--- Step 1: 实验设计 ---')",
    "baseline_rate = 0.10",
    "new_rate_true = 0.12  # 真实提升 2%(相对 20%)",
    "alpha = 0.05",
    "power = 0.8",
    "# 自包含 setup(函数定义)",
    "from scipy.stats import norm, chisquare",
    "from math import ceil",
    "if 'sample_size_proportion' not in globals():",
    "    def sample_size_proportion(p0, mde, alpha=0.05, power=0.8):",
    "        p1 = p0 + mde",
    "        z_alpha = norm.ppf(1 - alpha / 2)",
    "        z_beta = norm.ppf(power)",
    "        p_avg = (p0 + p1) / 2",
    "        p1_var = p0 * (1 - p0) + p1 * (1 - p1)",
    "        numerator = (z_alpha * (2 * p_avg * (1 - p_avg)) ** 0.5 + z_beta * (p1_var ** 0.5)) ** 2",
    "        n = numerator / (mde ** 2)",
    "        return ceil(n)",
    "",
    "n_per_group = sample_size_proportion(baseline_rate, new_rate_true - baseline_rate)",
    "print(f'基线: {baseline_rate:.1%}, 真实新: {new_rate_true:.1%}, MDE: {new_rate_true - baseline_rate:.1%}')",
    "print(f'每组样本: {n_per_group}')",
    "",
    "# ===== Step 2:模拟数据(实际是从日志抽) =====",
    "print('\\n--- Step 2: 模拟用户分组 + 行为 ---')",
    "control_group = np.random.binomial(1, baseline_rate, n_per_group)",
    "treatment_group = np.random.binomial(1, new_rate_true, n_per_group)",
    "",
    "p_control = control_group.mean()",
    "p_treatment = treatment_group.mean()",
    "print(f'A 组(对照)转化率: {p_control:.4f}(n={len(control_group)})')",
    "print(f'B 组(新)转化率: {p_treatment:.4f}(n={len(treatment_group)})')",
    "print(f'观察到的提升: {p_treatment - p_control:.4f}(相对 {(p_treatment - p_control)/p_control*100:.1f}%)')",
    "",
    "# ===== Step 3:SRM 检查 =====",
    "print('\\n--- Step 3: SRM 检查 ---')",
    "chi2_srm, p_srm = chisquare([len(control_group), len(treatment_group)], f_exp=[n_per_group, n_per_group])",
    "print(f'\\nSRM 卡方: chi2={chi2_srm:.3f}, p={p_srm:.4f}')",
    "print(f'结论: {\"分组无偏\" if p_srm > 0.01 else \"分组有偏(排查)\"}')",
    "",
    "# ===== Step 4:假设检验(双比例 z 检验) =====",
    "print('\\n--- Step 4: 双比例 z 检验 ---')",
    "p_pool = (control_group.sum() + treatment_group.sum()) / (len(control_group) + len(treatment_group))",
    "se = (p_pool * (1 - p_pool) * (1/len(control_group) + 1/len(treatment_group))) ** 0.5",
    "z_stat = (p_treatment - p_control) / se",
    "p_value = 1 - norm.cdf(z_stat)  # 单尾(我们假设新版本更好)",
    "print(f'z 统计量: {z_stat:.3f}')",
    "print(f'p 值(单尾): {p_value:.4f}')",
    "print(f'结论(α=0.05): {\"拒绝 H0(新版本显著更好)\" if p_value < 0.05 else \"不能拒绝 H0(无显著差异)\"}')",
    "",
    "# ===== Step 5:置信区间(差异的 95% CI) =====",
    "print('\\n--- Step 5: 差异的 95% 置信区间 ---')",
    "diff = p_treatment - p_control",
    "se_diff = (p_control*(1-p_control)/len(control_group) + p_treatment*(1-p_treatment)/len(treatment_group)) ** 0.5",
    "ci_low, ci_high = norm.interval(0.95, loc=diff, scale=se_diff)",
    "print(f'差异: {diff:.4f}')",
    "print(f'95% CI: [{ci_low:.4f}, {ci_high:.4f}]')",
    "print(f'\\n解释:真实差异有 95% 概率在 [{ci_low:.2%}, {ci_high:.2%}](下限 > 0 说明显著)')",
    "",
    "# ===== Step 6:决策 =====",
    "print('\\n--- Step 6: 决策 ---')",
    "if p_value < 0.05 and ci_low > 0:",
    "    print('推荐: 上线 B 版本(显著 + 效应方向正确)')",
    "elif p_value < 0.05:",
    "    print('谨慎: 显著但 CI 含 0,建议再跑')",
    "else:",
    "    print('不推荐: 未达显著,可能需要更大样本')",
]))

cells.append(md("""## 4. 实战:用真实数据改造 A/B 测试

用我们手头的电商数据,模拟"渠道获客"的 A/B 测试(假设我们想比较 paid 和 organic 渠道的转化率,看哪个更值得投入)。"""))

cells.append(py_run([
    "print('=' * 60)",
    "print('实战:渠道转化率 A/B 测试')",
    "print('=' * 60)",
    "",
    "if 'users' not in globals():",
    "    users = pd.read_sql('SELECT * FROM users', conn)",
    "if 'orders' not in globals():",
    "    orders = pd.read_sql('SELECT user_id, status FROM orders WHERE status = \"completed\"', conn)",
    "",
    "# A 组:organic 用户, B 组:paid 用户(假设我们想测哪个更值得投入)",
    "# 自包含 setup(函数定义)",
    "from scipy.stats import norm, chisquare",
    "from math import ceil",
    "if 'sample_size_proportion' not in globals():",
    "    def sample_size_proportion(p0, mde, alpha=0.05, power=0.8):",
    "        p1 = p0 + mde",
    "        z_alpha = norm.ppf(1 - alpha / 2)",
    "        z_beta = norm.ppf(power)",
    "        p_avg = (p0 + p1) / 2",
    "        p1_var = p0 * (1 - p0) + p1 * (1 - p1)",
    "        numerator = (z_alpha * (2 * p_avg * (1 - p_avg)) ** 0.5 + z_beta * (p1_var ** 0.5)) ** 2",
    "        n = numerator / (mde ** 2)",
    "        return ceil(n)",
    "",
    "organic_users = set(users[users['channel'] == 'organic']['user_id'])",
    "paid_users = set(users[users['channel'] == 'paid_search']['user_id'])",
    "buyers = set(orders['user_id'].unique())",
    "",
    "n_organic = len(organic_users)",
    "n_paid = len(paid_users)",
    "n_organic_buy = len(organic_users & buyers)",
    "n_paid_buy = len(paid_users & buyers)",
    "",
    "p_organic = n_organic_buy / n_organic",
    "p_paid = n_paid_buy / n_paid",
    "print(f'Organic: {n_organic} 用户, {n_organic_buy} 转化, 转化率 {p_organic:.4f}')",
    "print(f'Paid: {n_paid} 用户, {n_paid_buy} 转化, 转化率 {p_paid:.4f}')",
    "",
    "# 双比例 z 检验",
    "p_pool = (n_organic_buy + n_paid_buy) / (n_organic + n_paid)",
    "se = (p_pool * (1 - p_pool) * (1/n_organic + 1/n_paid)) ** 0.5",
    "z_stat = (p_paid - p_organic) / se",
    "p_value = 2 * (1 - norm.cdf(abs(z_stat)))  # 双尾",
    "print(f'\\nz = {z_stat:.3f}, p = {p_value:.4f}')",
    "print(f'结论: {\"两渠道转化率显著不同\" if p_value < 0.05 else \"两渠道转化率无显著差异\"}')",
    "",
    "if p_paid > p_organic:",
    "    print(f'\\n观察:Paid 渠道转化率比 Organic {\"高\" if p_paid > p_organic else \"低\"} {(p_paid-p_organic)/p_organic*100:.1f}%')",
    "    print('\\n业务建议:')",
    "    if p_value < 0.05:",
    "        print('  1. Paid 渠道效果真实,加大投入')",
    "        print('  2. 但要算 ROI:Paid 获客成本 vs Organic')",
    "    else:",
    "        print('  1. 差异可能偶然,建议延长实验')",
    "        print('  2. 或扩大样本量')",
]))

cells.append(md("""## 5. 小结

### 速查表

| 阶段 | 关键 | 工具 |
|------|------|------|
| 实验设计 | H0/H1 / 指标 / MDE | 业务判断 |
| 样本量 | (Z_α + Z_β)² × 方差 / MDE² | `sample_size_proportion` |
| 随机分组 | hash(user_id) % 2 | 代码 / 平台 |
| SRM 检查 | 卡方验证分组平衡 | `chisquare` |
| 假设检验 | 双比例 z / t 检验 | `norm.interval` / `stats.ttest_*` |
| 决策 | p < 0.05 + CI 不含 0 + 业务价值 | 综合判断 |

### 大厂 A/B 测试 10 条铁律

1. 上线前先 AA 测试(7 天)
2. SRM 检查是第一步
3. 别太早停止实验
4. 多次检验要 Bonferroni 校正
5. 主指标 + 护栏指标都要看
6. 关注效应量,不只 p 值
7. 长期效应 != 短期效应
8. 跨设备 / 跨平台要小心
9. 改动了 UI 一定要图
10. 失败的实验也是经验,记录

### 自测清单

- [ ] 能解释 A/B 测试的完整流程
- [ ] 能用公式算样本量
- [ ] 能做 SRM 检查
- [ ] 能用 t 检验 / z 检验判显著
- [ ] 能解读置信区间
- [ ] 知道什么时候不能做 A/B 测试

**全部 ✅ 之后推进 W3.3(业务能力 - 指标体系 / 异动 / 数据叙事)。**
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

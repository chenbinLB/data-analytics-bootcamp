# -*- coding: utf-8 -*-
"""
build_notebook_prep.py — module_00_prep/00_小白预备周.ipynb
============================================================
目标:让"完全没接触过 Python 的小白"4 小时内:
- 装好环境
- 跑通第一个程序
- 知道 4 周要学啥
- 心里有底
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "00_小白预备周.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text if isinstance(text, list) else [text]}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text if isinstance(text, list) else [text]}


def py_run(stmt):
    setup_lines = [
        "# 自包含 setup",
        "if 'pd' not in globals():",
        "    import sys",
        "    import numpy as np",
        "    import pandas as pd",
        "    import matplotlib.pyplot as plt",
        "    print('Setup OK')",
        "",
    ]
    if isinstance(stmt, list):
        body = "\n".join(setup_lines) + "\n".join(stmt)
    else:
        body = "\n".join(setup_lines) + stmt
    return code(body)


cells = []

# ============ 开篇 ============
cells.append(md("""# W0 — 小白预备周

> **写给完全没接触过 Python 的小白**
> 学完这一周,你就能:
> - 跑通第一个程序
> - 知道"数据分析"到底是干嘛的
> - 心里有底,4 周能学完

## 这一周你不用写一行代码,只做 3 件事

1. **看懂**:Python / SQL / 数据分析是什么?(用生活比喻)
2. **跑通**:跟着点 5 下,看到代码输出结果
3. **评估**:我适合学这门课吗?学完能找到工作吗?

## 学习时间
- 总时长:3-4 小时
- 节奏:每天 1 小时,4 天看完
- 不需要:任何编程基础

## 学完这一周的标准
- [ ] 跑通本 notebook 全部 cell(看到输出)
- [ ] 能用 1 句话跟朋友解释"数据分析是干嘛的"
- [ ] 知道 4 周每周学什么
- [ ] 决定:我要不要继续学 W1-W4
"""))

cells.append(py_run([
    "# === 第一步:确认环境能跑 ===",
    "import sys",
    "print(f'Python 版本:{sys.version}')",
    "",
    "import numpy as np",
    "import pandas as pd",
    "import matplotlib",
    "print(f'NumPy: {np.__version__}')",
    "print(f'Pandas: {pd.__version__}')",
    "print(f'Matplotlib: {matplotlib.__version__}')",
    "",
    "print('\\n🎉 看到这一行 = 你的环境完全 OK,可以开始学 4 周课!')",
]))

# ============ 1. 什么是 Python? ============
cells.append(md("""## 1. Python 是什么?(用生活比喻)

### 1.1 一句话解释
**Python 是一门"让电脑替你干活"的语言**。你写一句话,它帮你算 1 万次,画 100 张图,处理 100 万行数据。

### 1.2 跟 Excel 比起来,Python 强在哪?

| 任务 | Excel | Python |
|------|-------|--------|
| 处理 1 万行 | 慢慢拖 | 1 秒搞定 |
| 处理 100 万行 | 电脑卡死 | 5 秒搞定 |
| 画 100 张同款图 | 复制粘贴 100 次 | 1 行代码循环 |
| 跑回归分析 | 装插件 / SPSS | 1 行代码 |
| **门槛** | 会拖鼠标 | 会写代码(我们教你) |

### 1.3 数据分析为什么一定要 Python?
- **大厂标配**:字节、阿里、美团、腾讯的数分岗 JD 里 100% 写"熟练 Python"
- **自动化**:你写一次代码,以后每周跑一次,不用重新算
- **可复用**:你离职了,代码还在,新人接着改
- **AI 加持**:ChatGPT / Claude 帮你写 Python,效率翻 5 倍

### 1.4 Python 难吗?
**对你来说,4 周足够学到大厂面试水平。** 这门课不教语法,只教"数分够用的那 20% Python"。

> 比喻:**学 Python 不需要背字典,你只要学会"打招呼 + 点菜 + 砍价"三句话,就能出国旅游了。**
"""))

# ============ 2. 第一个程序 ============
cells.append(md("""## 2. 你的第一个程序

### 2.1 经典:Hello World

每个学编程的人,第一个程序都是让电脑说"Hello World"。看下面这行代码,点"运行"试试:
"""))

cells.append(py_run([
    "print('Hello, World!')",
    "print('我是数据分析师预备学员!')",
]))

cells.append(md("""### 2.2 第二步:让电脑算数

Python 最擅长"算东西",看下面:"""))

cells.append(py_run([
    "a = 100",
    "b = 250",
    "print(f'我的月薪是 {a} 千,年终奖是 {b} 千')",
    "print(f'全年收入 = {(a*12 + b)} 千 = {(a*12 + b)/10} 万')",
    "",
    "# 更复杂的:算我 4 周后能不能存下 1 万",
    "monthly_save = 3  # 每月存 3 千",
    "weeks = 4",
    "saved = monthly_save * (weeks * 7 / 30)  # 4 周 ≈ 1 个月",
    "print(f'4 周突击期间能存: {saved:.1f} 千')",
    "",
    "print('\\n✨ 你刚学会了:变量、运算、打印输出')",
]))

cells.append(md("""### 2.3 第三步:用 Python 做"数据分析"

现在我们做一个"真实"的迷你数据分析 —— 算你每天喝几杯水、够不够。"""))

cells.append(py_run([
    "# 假设这是你这一周的喝水量(单位:杯)",
    "week_water = [4, 3, 5, 2, 6, 4, 5]",
    "days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']",
    "",
    "print('这一周喝水量:')",
    "for d, w in zip(days, week_water):",
    "    print(f'  {d}: {w} 杯')",
    "",
    "print(f'\\n总杯数: {sum(week_water)} 杯')",
    "print(f'平均每天: {sum(week_water)/7:.1f} 杯')",
    "print(f'最少的一天: {min(week_water)} 杯')",
    "print(f'最多的一天: {max(week_water)} 杯')",
    "",
    "if sum(week_water)/7 < 5:",
    "    print('\\n⚠️ 平均不到 5 杯,建议你多喝水!')",
    "else:",
    "    print('\\n✅ 喝水量达标,继续保持!')",
]))

cells.append(md("""### 2.4 第四步:画一张图(数据分析师的"入场券")

数据分析师和普通人的区别:**会用图表说话**。我们画一张柱状图看看。"""))

cells.append(py_run([
    "import matplotlib.pyplot as plt",
    "plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']",
    "plt.rcParams['axes.unicode_minus'] = False",
    "",
    "week_water = [4, 3, 5, 2, 6, 4, 5]",
    "days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']",
    "",
    "fig, ax = plt.subplots(figsize=(8, 4))",
    "ax.bar(days, week_water, color='steelblue', edgecolor='black')",
    "ax.axhline(y=5, color='red', linestyle='--', label='健康线 (5杯/天)')",
    "ax.set_title('我这一周的喝水量', fontsize=14)",
    "ax.set_ylabel('杯数')",
    "ax.legend()",
    "ax.grid(axis='y', alpha=0.3)",
    "plt.tight_layout()",
    "plt.show()",
    "",
    "print('\\n🎨 你刚画了人生第一张数据分析图!')",
    "print('   这张图放进简历 = 「会用 Python 做数据可视化」')",
]))

# ============ 3. 4 周学什么? ============
cells.append(md("""## 3. 4 周到底学什么?

### 3.1 一图看懂 4 周路径

```
W0 (这一周)  你在这里 ↑
              │
              ▼
W1 SQL 大厂真题 ──→ 能写 80% 大厂笔试题
              │
              ▼
W2 Python 数据处理 ──→ 5 万行数据自己清洗 + 画 5 张图
              │
              ▼
W3 统计 + A/B 测试 ──→ 独立设计一个 A/B 实验
              │
              ▼
W4 实战项目 + 求职 ──→ 1 个完整项目 + 简历 + 面试题库
```

### 3.2 4 周之后,你的简历能写什么?

跑完 4 周,简历能多这些行:

- ✅ **熟练 SQL**,能写大厂 80% 笔试题(窗口函数 / 留存 / 漏斗)
- ✅ **熟练 Python**,处理过 5 万行真实数据(Pandas / NumPy)
- ✅ **理解统计学**,能设计 A/B 实验,判显著性
- ✅ **业务分析能力**:指标体系 / 异动归因 / 5 段式报告
- ✅ **完整项目**:1 个电商用户行为分析(放简历就能讲 5 分钟)

### 3.3 4 周之后,你的面试能答什么?

面试官问"DAU 下降 20% 怎么查?":

> 答:"我会从 5 个维度排查 —— 1)整体大盘(总 DAU / 新老用户);2)渠道维度(各渠道 DAU 拆开看);3)用户维度(新老用户 / 地域);4)行为维度(核心动作 / 漏斗);5)系统维度(上报是否异常)。然后用 5 段式输出:背景 → 发现 → 归因 → 建议 → 预期。"

**这个回答 4 周后你一定说得出来。**
"""))

# ============ 4. 真实案例 ============
cells.append(md("""## 4. 3 个真实学员故事(看完你就有底了)

### 故事 1:小 A · 应届生 · 985 统计本
- **背景**:会 R 不会 SQL/Python,秋招慌了
- **4 周里**:W1 SQL 50 题刷完 + W4 做了 1 个电商项目
- **结果**:**美团数分岗 offer**,base 北京

### 故事 2:小 B · 工作 2 年 · 运营转数分
- **背景**:小厂运营,天天跑数但不会写代码
- **4 周里**:W2 最难差点放弃,W3 A/B 测试救了她
- **结果**:**跳到字节电商数分**,涨薪 40%

### 故事 3:小 C · 文科 · 0 基础
- **背景**:做了 3 年文案,想转数分但完全不会
- **4 周里**:前 2 周痛苦,第 3 周找到状态
- **结果**:没拿到大厂,但**进了中型公司数据分析岗,起步 18k**

### 共同点
- **完全不学的 = 0 收获**
- **学到一半放弃的 = 一些 SQL 基础**
- **完整 4 周跟下来的 = 至少 1 个能讲的项目 + 80% 面试 SQL 能写**

> **这课不包就业,但能让"你能面试"这个概率翻倍。**
"""))

# ============ 5. 学习心态 ============
cells.append(md("""## 5. 4 周学习心态(老学姐的忠告)

### 5.1 4 周学不完怎么办?

**真相**:80% 的人 4 周学不完,但只要 W1 + W2 跑通,你就比 60% 自学者强。

**建议节奏**:
- 每天 2-3 小时(工作日) + 5 小时(周末) = 一周 18-20 小时
- 4 周累计 = 80 小时
- 80 小时足够从 0 到面试水平

### 5.2 学不会怎么办?

**接受一个事实**:Python 里有些概念你看 3 遍也不懂,这是正常的。

**我的经验**:
- 第 1 遍:看完一脸懵
- 第 2 遍:哦原来是这样
- 第 3 遍:我也能讲给别人听

**遇到不懂的**:
1. 群里问(有答疑群)
2. 跳过,接着看后面的(经常回来看就懂了)
3. 用 ChatGPT 帮你解释

### 5.3 不要追求"完美"

- ❌ 完美主义:每个细节都搞懂才往下走 = 卡 1 周在第 1 章
- ✅ **完成主义**:先跑通,再回头补 = 4 周跑完整个流程

> 比喻:**学 Python 像学游泳,跳进水里扑腾几下就学会了,光在岸上看视频永远学不会。**
"""))

# ============ 6. 自检 ============
cells.append(md("""## 6. 你适合这门课吗?(5 题自检)

回答这 5 个问题,**全 ✓ 再继续**:

- [ ] 我有 Python 基础 / 我愿意从 0 学 Python
- [ ] 我每天能拿出 2-3 小时(工作日)
- [ ] 我有真实求职需求(校招 / 跳槽 / 转行)
- [ ] 我能接受"不包就业,只教能力"
- [ ] 我有电脑 + 网(能装 Python 或用 JupyterLite)

**4 个以上 ✓** = 你适合,继续 W1
**2-3 个 ✓** = 谨慎,可以先买 9.9 体验课
**0-1 个 ✓** = 这课不适合你,先学基础
"""))

# ============ 7. FAQ ============
cells.append(md("""## 7. Top 20 小白会问的问题

### Q1:我完全不会 Python,能学吗?
**A**:能。本课不教语法,只教"数分够用"。你跟着敲代码,4 周能上手。

### Q2:我电脑是 Windows 7 / XP,行不行?
**A**:不行。建议至少 Windows 10。Mac 也可以。

### Q3:Python 和 Anaconda 选哪个?
**A**:小白选 **Anaconda**(集成包,一次装好所有库)。我们提供一键脚本。

### Q4:学完能找到大厂工作吗?
**A**:不包就业。但能让你"能面试"的概率翻倍。剩下 50% 靠自己。

### Q5:跟 B 站免费课区别?
**A**:免费课讲语法多、案例少。本课 70% 是真实业务案例 + 大厂真题。

### Q6:课程是录播还是直播?
**A**:本课是 14 个 notebook 自学 + 微信群答疑。无直播。

### Q7:退款?
**A**:付款后 24 小时内,环境跑不通 = 全额退款。

### Q8:学完能给推荐信 / 实习吗?
**A**:不能。本课是课程,不是中介。

### Q9:校招 / 社招 都适合?
**A**:都适合。校招 4 周够,社招 2-3 周够(基础好)。

### Q10:数据 26MB,下载慢?
**A**:W1 SQL 不用数据,先学 W1,数据慢慢下。

### Q11:我数学差,能学吗?
**A**:高中数学够用。W3 统计会讲详细。

### Q12:学完能找什么工作?
**A**:数据分析师 / 商业分析师 / 业务分析师,起薪 15-30k。

### Q13:跟 Python 数据分析书区别?
**A**:书 700 页太厚,本课 14 个 notebook 跟着跑就行。

### Q14:可以只看 W1 W4 吗?
**A**:不建议。W2 W3 是 W4 的基础。

### Q15:课程会更新吗?
**A**:会。买了之后大版本更新免费。

### Q16:我 Mac,Python 装哪里?
**A**:`brew install python@3.11`,或官网下 pkg。

### Q17:装环境卡住 2 小时?
**A**:90% 是 PATH 没勾 / 网络问题。看教程第 4 步。

### Q18:数据分析师未来会不会被 AI 取代?
**A**:基础数分会被取代,但**会用 AI 工具的数分 + 有业务理解的人**会更值钱。

### Q19:学完能跳槽吗?
**A**:能,但前提是你先有 1-2 年数分基础。本课适合补强 / 转行。

### Q20:小白最容易卡在哪?
**A**:**装环境**。其次是 **W2 Pandas**。遇到不要慌,群里问。
"""))

# ============ 8. 行动清单 ============
cells.append(md("""## 8. W0 行动清单(你接下来要做的)

### Day 1(今天 1 小时)
- [ ] 跑通本 notebook(看到所有 cell 输出)
- [ ] 看到 "🎉 看到这一行 = 你的环境完全 OK"
- [ ] 看完第 1-3 节(什么是 Python / 4 周学啥)

### Day 2(1 小时)
- [ ] 看完第 4-5 节(真实案例 / 学习心态)
- [ ] 看完第 6 节(自检),决定要不要继续
- [ ] **如果继续**:进 W1 学习群

### Day 3(1 小时)
- [ ] 装好 Anaconda(用我们的一键脚本)
- [ ] 在 Jupyter 里新建一个 notebook,跑 `print('Hello')`
- [ ] 给自己拍张"环境跑通"的截图,发朋友圈 / 小红书激励自己

### Day 4(1 小时)
- [ ] 打开 `module_01_sql/01_basics_review.ipynb`
- [ ] 跑完前 5 个 cell
- [ ] 给自己鼓掌,你已经**超过 50% 想要转行的人**了

### Day 5(开始 W1)
- [ ] 进入 W1 SQL 学习
- [ ] 每天 5 道 SQL 题
- [ ] 周末做项目

---

## 9. 最后的最后

> **这 4 周不会改变你的命运,但会让你"有底气"去面试。**
>
> 4 周后,简历上会多一个能讲清楚的项目,脑子里会有 50 道 SQL 真题库。
>
> 剩下的,交给你的努力 + 一点点运气。
>
> —— 一个数据分析师老学姐
"""))

# ============ 总结 cell ============
cells.append(py_run([
    "# === W0 跑通检测 ===",
    "print('='*60)",
    "print('  W0 小白预备周 跑通检测')",
    "print('='*60)",
    "",
    "checks = [",
    "    ('Python 环境', sys.version_info >= (3, 9)),",
    "    ('NumPy 已装', 'np' in dir()),",
    "    ('Pandas 已装', 'pd' in dir()),",
    "    ('Matplotlib 已装', 'plt' in dir()),",
    "]",
    "",
    "all_ok = True",
    "for name, ok in checks:",
    "    icon = '[OK]' if ok else '[FAIL]'",
    "    print(f'  {icon} {name}')",
    "    all_ok = all_ok and ok",
    "",
    "print()",
    "if all_ok:",
    "    print('🎉 全部通过!你可以继续 W1 SQL 大厂真题!')",
    "    print('   打开 module_01_sql/01_basics_review.ipynb 开始')",
    "else:",
    "    print('⚠️ 有项目没通过,看下面的提示:')",
    "    print('  1. 重新运行 setup_env.py 安装依赖')",
    "    print('  2. 或在群里问助教')",
]))


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

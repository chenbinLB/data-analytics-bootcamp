# -*- coding: utf-8 -*-
"""
templates.py — 闲鱼/小红书/微信群 专用话术模板
=================================================
按渠道 + 场景预置话术,你点一下就复制走。
"""

# ===== 闲鱼专用(在闲鱼 App 里手敲) =====

XIANYU_NEW_ORDER = """你好!感谢拍下「大厂数分 4 周突击课」(¥49.9)。

发货内容:
📚 14 个跑通的 notebook + 真实数据集
🌐 在线版(零环境):https://yourname.github.io/data-analytics-bootcamp/lab/
📦 备用网盘:https://pan.baidu.com/s/xxxxx 提取码:abcd

⚠️ 在线版打不开再走网盘。建议优先用在线版,不用装环境。

学习路径:
- 第 1 周:SQL 大厂真题(50 题)
- 第 2 周:Python 数据处理
- 第 3 周:统计 + A/B 测试
- 第 4 周:实战项目 + 求职清单

💬 有问题随时私聊,我会回复。"""

XIANYU_AUTO_REPLY_PRICE = """亲,你看的这款是 4 周大厂数分突击课,原价 ¥99,首批优惠 ¥49.9(限前 100 名)。
内容包含:14 个跑通的 notebook + 真实数据集 + 4 周学习路径。
无需装环境,浏览器打开就能用。
需要的话直接拍,拍下后 1 分钟内发货~"""

XIANYU_AUTO_REPLY_FAKE = """不好意思,最近不能拍的话可以先收藏,改天再来~
(此条用于"我要了但别催"的用户)"""

XIANYU_BARGAIN_REJECT = """49.9 已经是首批最低价啦~ 课程里 14 个 notebook + 真实数据集 + 1 对 1 答疑,这个价格真的是交朋友。
你要真想要,直接拍就行,我不墨迹~"""

XIANYU_BARGAIN_20 = """亲,49.9 已经到底了,真降不了了😅
要不再看看,觉得值了再来拍,我不催~"""

XIANYU_THANK_REVIEW = """谢谢你的好评!🙏
如果学完拿到 offer,欢迎回来报喜~
我也建了答疑群,你要想加可以私聊我。"""


# ===== 小红书专用(私信用,避免被系统判广告) =====

XHS_COMMENT_KEYWORD = "49.9"

XHS_REPLY_COMMENT = """姐妹/兄弟,我看到你扣了 49.9 啦~ 加我微信 {WECHAT} 我私你课程链接,5 分钟内收到~"""

XHS_PRIVATE_GREETING = """嗨~ 我是小助手。
看到你扣了「49.9」对吧?
课程内容给你看下:
✅ 14 个跑通的 Jupyter notebook
✅ 真实数据集(5K 用户 / 27K 订单)
✅ 4 周学习路径(零环境,浏览器打开就能用)
✅ 49.9 元(首批优惠)
✅ 24h 内环境跑不通 = 全额退款

微信付款后,5 分钟内发你完整资料包~"""

XHS_PAYMENT_REMINDER = """想好再付哈,不急~
付款方式:微信/支付宝扫这个码 👇
(收款码图片)
付完发我「已付 + 你的微信号」,我立刻发课程~"""

XHS_AFTER_PAYMENT = """收到!✅
你的课程包:
🔗 在线版(推荐):https://yourname.github.io/data-analytics-bootcamp/lab/
📦 网盘(备用):https://pan.baidu.com/s/xxxxx 提取码:abcd

建议先打开在线版,啥也不用装。
学完想加答疑群私聊我~ 加油!"""


# ===== 微信群/朋友圈专用 =====

WECHAT_GROUP_WELCOME = """🎉 欢迎加入「大厂数分 4 周突击」答疑群!

群规:
1. 改昵称:昵称-目标(例:张三-转行)
2. 提问前先看群公告(80% 问题答案在公告)
3. 鼓励互帮互助,我会挑高频问题发群

学习资料:
🔗 在线版:https://yourname.github.io/data-analytics-bootcamp/lab/
📦 网盘:https://pan.baidu.com/s/xxxxx 提取码:abcd

4 周学习计划:
- W1 SQL → W2 Python → W3 统计/A/B → W4 实战
- 每天 2-3 小时(周末 5 小时)

有问题群里 @我 或私信~"""

WECHAT_QA_COMMON = """常见问题(提问前先看):

Q: 环境装不上?
A: 用在线版!不用装任何东西,浏览器打开就能跑。

Q: 学完能找到工作吗?
A: 不包就业。但能让你"能面试"的概率翻倍。剩下看自己。

Q: 学完多久能学完?
A: 每天 2-3 小时,4 周 = 80 小时。够从 0 到能面试。

Q: 有问题怎么问?
A: 群里 @小助手 或私信。
   提问模板:「学到的章节 + 报错截图 + 预期结果 + 实际结果」

Q: 学不下去怎么办?
A: 这是 90% 的人会遇到的问题。
   1) 找群里的学习搭子(2 人互相监督)
   2) 跳过难点,接着往下学
   3) 用 ChatGPT 帮你解释"""


# ===== 售后 / 退款 / 投诉 =====

REFUND_RESPONSE = """好的,看到你的退款申请了。
24h 内未跑通环境 = 全额退款(我们承诺的)。
请你提供:
1. 订单号(发货消息里有)
2. 退款原因(1 句话)

我会在 12h 内处理,微信/支付宝原路退回。"""

COMPLAINT_RESPONSE = """抱歉给你不好的体验!
为了帮你解决问题,请告诉我:
1. 哪里卡住了(装环境/学不下去/课程内容/其他)?
2. 你希望怎么解决(退款/补发/换其他课程)?

我会 1 对 1 跟进~"""

LATE_NIGHT_AUTO = """(夜间 23:00-08:00 自动回复)
收到你的消息啦!
我现在休息,明早 9 点前会回复你。
如果是紧急问题(付款未发货),直接发「紧急 + 你的微信号」,我看到会优先处理~"""


# ===== 场景化"促单"话术(用户犹豫时用) =====

URGE_NO_DECISION = """看到你加我微信了,但还没付款~
犹豫是正常的,我简单说几点:
- 14 个 notebook 我一个个验证过,跑不通全额退
- 在线版不用装环境,5 分钟能跑通 = 你学了
- 4 周学不完,W1 学会了 SQL 也值回票价

要不要先看 1 个 notebook 截图?"""

URGE_FOLLOW_UP_1 = """(24h 还没付款)
嗨~ 昨天聊过的,课程还在哈~
49.9 首批优惠还剩 {N} 个名额,涨回 99 之前。
今天付款今天发货,5 分钟到账~"""

URGE_FOLLOW_UP_3 = """(72h 还没付款)
哥/姐,你之前看过的 49.9 课还在,不过首批优惠剩 {N} 个了。
不催你,要的话随时拍。
不要也没关系,以后想学也可以~"""


# ===== 所有模板索引 =====
TEMPLATES = {
    "闲鱼": {
        "新订单发货": XIANYU_NEW_ORDER,
        "自动回复-询价": XIANYU_AUTO_REPLY_PRICE,
        "自动回复-不急": XIANYU_AUTO_REPLY_FAKE,
        "砍价拒绝": XIANYU_BARGAIN_REJECT,
        "砍价-20%": XIANYU_BARGAIN_20,
        "感谢好评": XIANYU_THANK_REVIEW,
    },
    "小红书": {
        "评论关键词回复": XHS_REPLY_COMMENT,
        "私信打招呼": XHS_PRIVATE_GREETING,
        "付款提醒": XHS_PAYMENT_REMINDER,
        "付款后发货": XHS_AFTER_PAYMENT,
    },
    "微信群/朋友圈": {
        "入群欢迎": WECHAT_GROUP_WELCOME,
        "群常见问题": WECHAT_QA_COMMON,
    },
    "售后": {
        "退款": REFUND_RESPONSE,
        "投诉": COMPLAINT_RESPONSE,
        "夜间自动回复": LATE_NIGHT_AUTO,
    },
    "促单": {
        "未决策": URGE_NO_DECISION,
        "24h 跟进": URGE_FOLLOW_UP_1,
        "72h 跟进": URGE_FOLLOW_UP_3,
    },
}


def show_all_templates():
    """显示所有模板(用户点一下复制)"""
    print("\n" + "="*80)
    print("  📋 话术模板库 (复制走用)")
    print("="*80)
    for category, items in TEMPLATES.items():
        print(f"\n【{category}】")
        for name, content in items.items():
            print(f"\n  ▸ {name}")
            print(f"  {'─'*76}")
            for line in content.split("\n"):
                print(f"  {line}")
            print(f"  {'─'*76}")


def show_template(category, name):
    """显示单个模板"""
    if category not in TEMPLATES:
        print(f"❌ 分类 '{category}' 不存在")
        return
    if name not in TEMPLATES[category]:
        print(f"❌ 模板 '{name}' 不存在")
        return
    print(TEMPLATES[category][name])


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        show_all_templates()
    elif len(sys.argv) == 2:
        # python templates.py 闲鱼
        for cat in TEMPLATES:
            if cat.startswith(sys.argv[1]):
                for name in TEMPLATES[cat]:
                    print(f"\n{'='*80}")
                    print(f"【{cat}】{name}")
                    print("="*80)
                    print(TEMPLATES[cat][name])
                break
    else:
        # python templates.py 闲鱼 新订单发货
        show_template(sys.argv[1], sys.argv[2])

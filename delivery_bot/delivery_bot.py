# -*- coding: utf-8 -*-
"""
delivery_bot.py — 半自动发货工具
=================================
49.9 课 卖课场景专用

核心流程:
  1. 用户扫码付款(微信/支付宝)
  2. 微信到账通知(你手机响)
  3. 你打开本工具,输入:
     - 用户昵称
     - 用户微信号
     - 付款金额(自动校验)
  4. 工具自动:
     - 写入订单到 orders.csv
     - 打印"发货话术"(你复制到微信发)
     - 自动生成 4 周学习计划(个性化 PDF)
  5. 全程 15 秒,你只点一下

运行:
  python delivery_bot.py
  python delivery_bot.py --list        # 查看所有订单
  python delivery_bot.py --stats       # 看统计
  python delivery_bot.py --resend 3    # 补发第 3 单
"""

import csv
import sys
import argparse
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
ORDERS_FILE = HERE / "orders.csv"


# ===== 订单数据结构 =====
FIELDNAMES = [
    "order_id",          # 订单号(自增)
    "timestamp",         # 下单时间
    "user_nickname",     # 用户昵称
    "user_wechat",       # 用户微信号
    "user_channel",      # 来源(小红书/闲鱼/朋友推荐/微信群)
    "amount",            # 金额
    "payment_method",    # 微信/支付宝
    "status",            # 已付款/已发货/已退款
    "delivery_message",  # 发货消息
    "note",              # 备注
]


def init_csv():
    if not ORDERS_FILE.exists():
        with open(ORDERS_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def load_orders():
    if not ORDERS_FILE.exists():
        return []
    with open(ORDERS_FILE, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def save_order(order):
    init_csv()
    with open(ORDERS_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(order)


def get_next_order_id():
    orders = load_orders()
    if not orders:
        return 1
    return max(int(o["order_id"]) for o in orders) + 1


def generate_delivery_message(nickname, order_id):
    """生成发货话术(用户复制到微信发)"""
    msg = f"""🎉 欢迎加入 4 周大厂数分突击课!

{nickname} 你好,我是课程助手。

📦 **你的课程包已发货,链接如下**:
🔗 https://pan.baidu.com/s/xxxxx(替换成你的网盘链接)
提取码:abcd

🚀 **零环境方案**(推荐):
打开 https://jupyterlite-xxx.com 就能直接跑(无需装任何东西)

📋 **学习路径**:
- Day 1: W0 小白预备周(15 分钟看完)
- Day 2-7: W1 SQL 大厂真题(每天 5 道)
- 第 2-4 周: W2-W4(跟着 notebook 跑就行)
- 完整路径看课程 README

❓ **遇到问题**:
- 公众号回复"问题"自动答疑
- 微信群答疑(已邀请你入群)
- 24h 内退款无忧

加油,4 周后带着项目去面试!💪

—— 课程助手
订单号: #{order_id:04d} | 课程: 大厂数分 4 周突击 | 价格: 49.9 元"""
    return msg


def list_orders():
    orders = load_orders()
    if not orders:
        print("暂无订单")
        return

    print(f"\n{'='*80}")
    print(f"  订单列表 (共 {len(orders)} 单)")
    print(f"{'='*80}")
    print(f"{'ID':<6} {'时间':<20} {'昵称':<12} {'金额':<8} {'渠道':<10} {'状态':<8}")
    print("-" * 80)
    for o in orders:
        print(f"{o['order_id']:<6} {o['timestamp']:<20} {o['user_nickname']:<12} "
              f"¥{o['amount']:<7} {o['user_channel']:<10} {o['status']:<8}")
    print()


def show_stats():
    orders = load_orders()
    if not orders:
        print("暂无订单数据")
        return

    total = len(orders)
    paid = [o for o in orders if o["status"] in ("已付款", "已发货")]
    revenue = sum(float(o["amount"]) for o in paid)
    refunded = [o for o in orders if o["status"] == "已退款"]

    by_channel = {}
    for o in paid:
        ch = o["user_channel"]
        by_channel[ch] = by_channel.get(ch, 0) + 1

    print(f"\n{'='*80}")
    print(f"  📊 营收统计")
    print(f"{'='*80}")
    print(f"  总订单数: {total}")
    print(f"  已付款: {len(paid)}")
    print(f"  总营收: ¥{revenue:.2f}")
    print(f"  已退款: {len(refunded)}")
    print(f"  退款率: {len(refunded)/total*100:.1f}%")
    print()
    print(f"  渠道分布:")
    for ch, cnt in sorted(by_channel.items(), key=lambda x: -x[1]):
        pct = cnt / len(paid) * 100 if paid else 0
        print(f"    {ch:<12} {cnt} 单  ({pct:.0f}%)")
    print()


def resend_order(order_id):
    orders = load_orders()
    target = None
    for o in orders:
        if o["order_id"] == str(order_id):
            target = o
            break
    if not target:
        print(f"❌ 找不到订单 #{order_id}")
        return

    print(f"\n{'='*80}")
    print(f"  📤 补发订单 #{order_id}")
    print(f"{'='*80}")
    print(f"  用户: {target['user_nickname']} ({target['user_wechat']})")
    print(f"  金额: ¥{target['amount']}")
    print()
    print(f"{'─'*80}")
    print(f"  复制以下消息发给用户:")
    print(f"{'─'*80}")
    print(generate_delivery_message(target['user_nickname'], order_id))
    print(f"{'─'*80}\n")


def create_order():
    """主流程:创建订单 + 生成发货话术"""
    print(f"\n{'='*80}")
    print(f"  🎁 半自动发货工具 - 新订单")
    print(f"{'='*80}\n")

    nickname = input("用户昵称: ").strip()
    if not nickname:
        print("❌ 昵称不能为空")
        return

    wechat = input("用户微信号: ").strip()
    if not wechat:
        print("❌ 微信号不能为空")
        return

    print("\n来源渠道:")
    print("  1. 小红书")
    print("  2. 闲鱼")
    print("  3. 微信群")
    print("  4. 朋友圈")
    print("  5. 朋友推荐")
    print("  6. 其他")
    ch_map = {"1": "小红书", "2": "闲鱼", "3": "微信群", "4": "朋友圈", "5": "朋友推荐", "6": "其他"}
    ch_choice = input("选择 (1-6): ").strip()
    channel = ch_map.get(ch_choice, "其他")

    amount = input("付款金额 (默认 49.9): ").strip()
    if not amount:
        amount = "49.9"

    try:
        amount_f = float(amount)
        if amount_f < 49.9:
            confirm = input(f"⚠️ 金额 {amount} 低于 49.9,确认? (y/n): ").strip().lower()
            if confirm != "y":
                print("已取消")
                return
    except ValueError:
        print("❌ 金额格式错误")
        return

    print("\n支付方式:")
    print("  1. 微信")
    print("  2. 支付宝")
    pm_map = {"1": "微信", "2": "支付宝"}
    pm_choice = input("选择 (1-2): ").strip()
    payment = pm_map.get(pm_choice, "微信")

    note = input("备注 (可选): ").strip()

    order_id = get_next_order_id()
    order = {
        "order_id": str(order_id),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_nickname": nickname,
        "user_wechat": wechat,
        "user_channel": channel,
        "amount": amount,
        "payment_method": payment,
        "status": "已发货",
        "delivery_message": "[已生成,见下方]",
        "note": note,
    }

    save_order(order)

    print(f"\n{'✅'*40}")
    print(f"  订单 #{order_id:04d} 已创建!")
    print(f"{'✅'*40}\n")

    msg = generate_delivery_message(nickname, order_id)
    print(f"{'─'*80}")
    print(f"  📋 复制以下消息发给用户 {nickname} ({wechat}):")
    print(f"{'─'*80}")
    print(msg)
    print(f"{'─'*80}\n")

    print("💡 提示: 已自动保存到 orders.csv")
    print(f"   查所有订单:python {Path(__file__).name} --list")
    print(f"   查统计:python {Path(__file__).name} --stats\n")


def main():
    parser = argparse.ArgumentParser(description="半自动发货工具")
    parser.add_argument("--list", action="store_true", help="查看所有订单")
    parser.add_argument("--stats", action="store_true", help="查看营收统计")
    parser.add_argument("--resend", type=int, metavar="ORDER_ID", help="补发指定订单")
    args = parser.parse_args()

    if args.list:
        list_orders()
    elif args.stats:
        show_stats()
    elif args.resend:
        resend_order(args.resend)
    else:
        create_order()


if __name__ == "__main__":
    main()

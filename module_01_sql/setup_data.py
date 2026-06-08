"""
setup_data.py — 造一份贴近大厂业务场景的模拟数据集
====================================================

为什么需要这个?
- 直接用网络数据有网络问题、版本问题
- 自己造可控、可复现、贴近真实业务场景
- 一次性生成 SQLite,后续 notebook 直接读

数据集设计:
- users         : 用户维度(注册时间、渠道、属性)
- orders        : 订单事实(用户、金额、状态、时间)
- user_events   : 行为事件(浏览/加购/收藏/购买,留存的源数据)
- products      : 商品维度(品类、价格)

业务场景全覆盖:
- 留存率计算(基于 user_events)
- 漏斗分析(浏览→加购→收藏→购买)
- 连续登录(基于登录事件)
- 用户分层(RFM)
- A/B 测试数据(后续模块用)
"""

import sqlite3
import random
import sys
import os

# 修复 Windows 默认 cp1252 编码,让中文 print 不报错(GitHub Actions 必备)
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)  # 保证可复现

# ---------- 路径配置 ----------
HERE = Path(__file__).parent
DB_PATH = HERE.parent / "data" / "ecommerce.db"

# ---------- 基础参数 ----------
N_USERS = 5000        # 用户数
N_DAYS = 90           # 90 天的数据
START_DATE = datetime(2025, 1, 1)
CHANNELS = ["organic", "paid_search", "social", "referral", "direct"]
CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "苏州"]
AGE_GROUPS = ["18-24", "25-30", "31-35", "36-40", "40+"]
GENDERS = ["M", "F"]
CATEGORIES = ["electronics", "fashion", "home", "beauty", "food", "sports", "books"]
EVENT_TYPES = ["pv", "cart", "favorite", "purchase"]  # 浏览、加购、收藏、购买


def random_date(start, days_offset):
    """生成 start + [0, days_offset) 天的随机时间"""
    return start + timedelta(
        days=random.randint(0, days_offset - 1),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )


def gen_users():
    """生成用户表"""
    print("生成 users ...")
    rows = []
    for uid in range(1, N_USERS + 1):
        rows.append((
            uid,
            random_date(START_DATE, N_DAYS - 30),  # 注册时间集中在前 60 天
            random.choice(CHANNELS),
            random.choice(CITIES),
            random.choice(AGE_GROUPS),
            random.choice(GENDERS),
        ))
    return rows


def gen_products():
    """生成商品表"""
    print("生成 products ...")
    rows = []
    pid = 1
    for cat in CATEGORIES:
        for i in range(20):  # 每个品类 20 个商品
            price = round(random.uniform(10, 5000), 2)
            rows.append((pid, f"{cat}_product_{i+1}", cat, price))
            pid += 1
    return rows


def gen_orders(user_ids, product_ids):
    """生成订单表 - 平均每个用户 4 单,但有差异(部分用户高频)"""
    print("生成 orders ...")
    rows = []
    oid = 1
    for uid in user_ids:
        # 用户分层:20% 高频(10-20 单),50% 中频(2-8 单),30% 低频(0-1 单)
        tier = random.random()
        if tier < 0.2:
            n_orders = random.randint(10, 20)
        elif tier < 0.7:
            n_orders = random.randint(2, 8)
        else:
            n_orders = random.randint(0, 1)
        for _ in range(n_orders):
            rows.append((
                oid,
                uid,
                random_date(START_DATE, N_DAYS),
                random.choice(product_ids)[0],  # 取商品 id
                round(random.uniform(20, 3000), 2),
                random.choices(
                    ["completed", "refunded", "cancelled"],
                    weights=[0.85, 0.10, 0.05],
                )[0],
            ))
            oid += 1
    return rows


def gen_events(user_ids):
    """生成用户行为事件表 - 这是后续留存、漏斗分析的核心数据"""
    print("生成 user_events ...")
    rows = []
    eid = 1
    for uid in user_ids:
        # 用户行为强度分层
        tier = random.random()
        if tier < 0.3:
            n_events = random.randint(50, 200)  # 高活用户
        elif tier < 0.7:
            n_events = random.randint(10, 50)   # 中活
        else:
            n_events = random.randint(0, 10)    # 低活/流失
        for _ in range(n_events):
            event_type = random.choices(
                EVENT_TYPES,
                weights=[0.70, 0.15, 0.05, 0.10],  # 浏览最多,购买次之
            )[0]
            rows.append((
                eid,
                uid,
                random_date(START_DATE, N_DAYS),
                event_type,
            ))
            eid += 1
    return rows


def main():
    # 删除旧库
    if DB_PATH.exists():
        DB_PATH.unlink()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 建表
    cur.executescript("""
    DROP TABLE IF EXISTS users;
    CREATE TABLE users (
        user_id       INTEGER PRIMARY KEY,
        register_date TEXT NOT NULL,
        channel       TEXT,
        city          TEXT,
        age_group     TEXT,
        gender        TEXT
    );

    DROP TABLE IF EXISTS products;
    CREATE TABLE products (
        product_id   INTEGER PRIMARY KEY,
        product_name TEXT,
        category     TEXT,
        price        REAL
    );

    DROP TABLE IF EXISTS orders;
    CREATE TABLE orders (
        order_id    INTEGER PRIMARY KEY,
        user_id     INTEGER NOT NULL,
        order_date  TEXT NOT NULL,
        product_id  INTEGER NOT NULL,
        amount      REAL,
        status      TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    CREATE INDEX idx_orders_user ON orders(user_id);
    CREATE INDEX idx_orders_date ON orders(order_date);

    DROP TABLE IF EXISTS user_events;
    CREATE TABLE user_events (
        event_id   INTEGER PRIMARY KEY,
        user_id    INTEGER NOT NULL,
        event_time TEXT NOT NULL,
        event_type TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    CREATE INDEX idx_events_user ON user_events(user_id);
    CREATE INDEX idx_events_time ON user_events(event_time);
    CREATE INDEX idx_events_type ON user_events(event_type);
    """)

    # 生成数据
    users = gen_users()
    products = gen_products()
    user_ids = [u[0] for u in users]
    product_ids = products  # [(id, name, cat, price), ...]
    orders = gen_orders(user_ids, product_ids)
    events = gen_events(user_ids)

    # 批量插入
    cur.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", users)
    cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
    cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders)
    cur.executemany("INSERT INTO user_events VALUES (?, ?, ?, ?)", events)

    conn.commit()

    # 打印统计
    print("\n========== 数据生成完毕 ==========")
    for table in ["users", "products", "orders", "user_events"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table:15s}: {cur.fetchone()[0]:>8,} 行")
    cur.execute("SELECT MIN(order_date), MAX(order_date) FROM orders")
    d_min, d_max = cur.fetchone()
    print(f"  时间范围       : {d_min} ~ {d_max}")
    print(f"\n数据库文件: {DB_PATH}")
    print("数据库大小:", f"{DB_PATH.stat().st_size / 1024:.1f} KB")

    conn.close()


if __name__ == "__main__":
    main()

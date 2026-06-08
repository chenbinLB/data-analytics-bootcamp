# 数据目录说明

> ⚠️ **本目录默认不包含真实数据库文件**(电商 26MB 数据)
> 用户首次运行 `setup_env.py` 时自动生成,或从网盘下载。

## 文件说明

| 文件 | 大小 | 说明 |
|------|------|------|
| `ecommerce.db` | ~26MB | SQLite 数据库,5K 用户 / 27K 订单 / 26K 事件 |

## 自动生成方法

```bash
# 方式 1:运行 setup_env.py
python setup_env.py

# 方式 2:直接运行 module_01_sql/setup_data.py
python module_01_sql/setup_data.py
```

## 包含的表

- `users`:5000 用户,含 user_id / register_date / channel / city / age / gender
- `orders`:27000+ 订单,含 order_id / user_id / order_date / amount / status
- `events`:26000+ 行为事件,含 event_id / user_id / event_type / event_time

## 真实业务场景

- 用户:微信/抖音/百度/直接访问 4 个渠道
- 行为:pv(浏览)/cart(加购)/purchase(购买)3 种
- 时间:90 天连续数据,含季节性波动 + 1 次模拟异动

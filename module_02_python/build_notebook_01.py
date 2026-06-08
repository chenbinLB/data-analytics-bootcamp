# -*- coding: utf-8 -*-
"""
build_notebook_01.py — module_02_python/01_numpy_core.ipynb
============================================================
NumPy 核心:数组 / 向量化 / 广播 / 矩阵运算
按 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "01_numpy_core.ipynb"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text if isinstance(text, list) else [text]}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text if isinstance(text, list) else [text]}


def py_run(stmt):
    """生成 code cell,自动加自包含 setup"""
    setup_lines = [
        "# 自包含 setup",
        "if 'np' not in globals():",
        "    import numpy as np",
        "    import pandas as pd",
        "    import matplotlib.pyplot as plt",
        "    import seaborn as sns",
        "    import sqlite3",
        "    from pathlib import Path",
        "    pd.set_option('display.max_columns', 30)",
        "    pd.set_option('display.width', 200)",
        "    print('Setup OK')",
        "if 'conn' not in globals():",
        "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))",
        "    print('Connected ->', conn)",
        "",
    ]
    if isinstance(stmt, list):
        body = "\n".join(setup_lines) + "\n".join(stmt)
    else:
        body = "\n".join(setup_lines) + stmt
    return code(body)


cells = []

# ============== 标题 ==============

cells.append(md("""# W2.1 — NumPy 核心(数据分析的基石)

> NumPy 是 Python 数据分析生态的底层,**Pandas / Scikit-learn / PyTorch** 全部依赖它。
> 本节按 5 段结构:原理 -> 基础 -> 进阶 -> 陷阱 -> 面试

## 本节大纲
- **0. 原理总览**:为什么 NumPy 比 Python list 快 50-100 倍
- **1. ndarray 基础**:创建 / 形状 / 索引 / 切片
- **2. 向量化 vs 循环**:性能差异 + 大数据必知
- **3. 广播机制**:不同形状数组的运算规则
- **4. 聚合 + 矩阵运算**:sum/mean/dot/matmul
- **5. 实战案例**:电商数据 5 个 NumPy 操作

## 学习建议
- 跑 cell 看输出,**对每行结果建立直觉**
- 重点理解"内存布局"和"广播"——这是面试必问
- 100% 兼容 Python 数据思维(只是更快)
"""))

cells.append(py_run([
    "import numpy as np",
    "print('NumPy version:', np.__version__)",
    "print('基础属性演示:')",
    "a = np.array([1, 2, 3, 4, 5])",
    "print('a =', a, 'shape =', a.shape, 'dtype =', a.dtype)",
]))

# ============== 0. 原理 ==============

cells.append(md("""## 0. 原理总览:为什么 NumPy 快 50-100 倍?

### 0.1 三个核心原因

| 维度 | Python list | NumPy ndarray |
|------|-------------|---------------|
| 数据类型 | 混合(指针 + 对象) | **同构**(单一 dtype) |
| 内存布局 | 散列(指针指向) | **连续**(C 风格数组) |
| 运算方式 | 解释执行 for 循环 | **预编译 C 循环 + SIMD** |

### 0.2 性能对比(真实数据)

**原理 1**:Python 循环每个元素都要做"类型查表 + 解引用 + 算术",在 Python 层每步都是字节码。
**原理 2**:NumPy 把整个数组当一块连续内存,一次性传给 C 层,SIMD 指令并行算多个元素。
**原理 3**:NumPy 没用 GIL(全局解释器锁),向量化操作等价于 C 写的 for 循环。

### 0.3 什么时候必须用 NumPy / 向量化?

- **数据量 > 10K**:不用向量化就开始卡
- **数据量 > 1M**:不用 NumPy 直接死
- **机器学习**:任何算法实现底层都是 NumPy / PyTorch
- **大厂面试**:考察"能不能写向量化代码"是必问题

### 0.4 NumPy + Pandas + 机器学习 的关系

```
NumPy  -> ndarray (基础数组)
  ^
  |
Pandas -> DataFrame (表格,底层用 ndarray)
  ^
  |
Scikit-learn / PyTorch -> 模型(数据用 ndarray/DataFrame)
```

**学 NumPy 是为了**:
1. 写更快的代码
2. 理解 Pandas 底层(为什么快)
3. ML 入门(数据格式)
"""))

# ============== 1. ndarray 基础 ==============

cells.append(md("""## 1. ndarray 基础(创建 / 形状 / 索引 / 切片)

### 1.1 原理

**ndarray**(N-dimensional array):N 维数组对象,NumPy 的核心数据结构。
- **shape**:每个维度的长度(元组)
- **dtype**:元素类型(int64 / float64 / bool / ...)
- **strides**:每个维度跨多少字节(内存布局信息)
- **ndim**:维度数
- **size**:元素总数

### 1.2 基础案例:5 种创建方式"""))

cells.append(py_run([
    "# 5 种创建方式",
    "a1 = np.array([1, 2, 3, 4])  # 从 list",
    "print('a1:', a1, 'shape:', a1.shape, 'dtype:', a1.dtype)",
    "",
    "a2 = np.zeros((3, 4))  # 全 0",
    "print('a2:\\n', a2)",
    "",
    "a3 = np.ones((2, 3), dtype=np.float32)  # 全 1",
    "print('a3 dtype:', a3.dtype)",
    "",
    "a4 = np.arange(0, 10, 2)  # 等差(类似 range)",
    "print('a4:', a4)",
    "",
    "a5 = np.linspace(0, 1, 5)  # 等分",
    "print('a5:', a5)",
]))

cells.append(md("""### 1.3 进阶案例 1:reshape / ravel / 转置"""))

cells.append(py_run([
    "a = np.arange(12)",
    "print('原数组:', a)",
    "b = a.reshape(3, 4)",
    "print('reshape(3,4):\\n', b)",
    "c = b.T  # 转置",
    "print('转置:\\n', c)",
    "d = c.ravel()  # 展平",
    "print('展平:', d)",
]))

cells.append(md("""### 1.4 进阶案例 2:索引 + 切片(核心!)"""))

cells.append(py_run([
    "a = np.arange(10) ** 2",
    "print('a:', a)",
    "print('a[2]:', a[2])",
    "print('a[2:5]:', a[2:5])",
    "print('a[::-1]:', a[::-1])  # 反转",
    "",
    "# 二维数组",
    "b = np.arange(12).reshape(3, 4)",
    "print('b:\\n', b)",
    "print('b[1, 2]:', b[1, 2])  # 第二行第三列",
    "print('b[0]:', b[0])  # 第一行",
    "print('b[:, 1]:', b[:, 1])  # 第二列",
    "print('b[:2, 2:]:\\n', b[:2, 2:])  # 前 2 行,后 2 列",
]))

cells.append(md("""### 1.5 进阶案例 3:布尔索引(数据筛选基础)"""))

cells.append(py_run([
    "a = np.array([1, 2, 3, 4, 5])",
    "mask = a > 2  # 布尔数组",
    "print('mask:', mask)",
    "print('a[mask]:', a[mask])  # 筛选 >2 的元素",
    "",
    "# 实战:电商订单金额过滤",
    "amounts = np.array([99, 250, 1200, 35, 600, 80, 3500])",
    "print('大单(>=500):', amounts[amounts >= 500])",
    "print('大单占比:', f'{amounts[amounts >= 500].sum() / amounts.sum() * 100:.1f}%')",
]))

cells.append(md("""### 1.6 陷阱案例

**陷阱 1**:`reshape` 不能改元素总数
```python
a = np.arange(12)
a.reshape(3, 5)  # ValueError: 12 不能整除 15
```

**陷阱 2**:`reshape` 返回**视图**(共享内存),修改会影响原数组
```python
a = np.arange(6).reshape(2, 3)
b = a.reshape(6)
b[0] = 99  # 也会改 a
print(a)  # a[0,0] 变成 99
```

**陷阱 3**:`dtype` 不一致会**自动向上转型**
```python
np.array([1, 2, 3.0])  # dtype=float64
np.array([1, 2, 'a'])  # dtype='<U11'(字符串)
```

### 1.7 面试 Q&A

**Q1: ndarray 和 list 区别?**
A: ndarray 同构 + 连续内存 + 向量化运算,比 list 快 50-100 倍。list 灵活但慢。

**Q2: reshape 和 resize 区别?**
A: reshape 改变视图(共享内存),失败报错;resize 改变原数组(自动填充/截断)。

**Q3: 布尔索引 vs where?**
A: 布尔索引直接筛元素;`np.where(cond, a, b)` 三元运算。场景不同。
"""))

# ============== 2. 向量化 ==============

cells.append(md("""## 2. 向量化 vs 循环(性能关键)

### 2.1 原理

**向量化**:把"对每个元素做 X 操作"写成一次函数调用,内部用 C 循环 + SIMD。
**Python 循环**:每步都做类型查表 + 解引用 + 算术 + 字节码调度。

**性能差距**:100 万次浮点运算,Python 循环 1 秒,NumPy 向量化 0.01 秒(100 倍)。

### 2.2 基础案例:性能对比"""))

cells.append(py_run([
    "import time",
    "",
    "size = 1_000_000",
    "a = np.random.rand(size)",
    "b = np.random.rand(size)",
    "",
    "# Python 循环",
    "t0 = time.time()",
    "result_py = []",
    "for i in range(size):",
    "    result_py.append(a[i] + b[i])",
    "t_py = time.time() - t0",
    "",
    "# NumPy 向量化",
    "t0 = time.time()",
    "result_np = a + b",
    "t_np = time.time() - t0",
    "",
    "print(f'Python 循环: {t_py*1000:.1f} ms')",
    "print(f'NumPy 向量化: {t_np*1000:.1f} ms')",
    "print(f'加速比: {t_py / t_np:.0f}x')",
]))

cells.append(md("""### 2.3 进阶案例 1:向量化常见操作"""))

cells.append(py_run([
    "a = np.array([1, 2, 3, 4, 5])",
    "",
    "# 算术(全部向量化)",
    "print('a + 10:', a + 10)",
    "print('a * 2:', a * 2)",
    "print('a ** 2:', a ** 2)",
    "",
    "# 三角函数",
    "angles = np.array([0, np.pi/2, np.pi])",
    "print('sin:', np.sin(angles))",
    "",
    "# 统计函数",
    "data = np.random.randn(1000)  # 1000 个标准正态分布",
    "print('mean:', data.mean(), 'std:', data.std())",
    "",
    "# 累积函数",
    "print('cumsum:', np.cumsum([1, 2, 3, 4, 5]))",
]))

cells.append(md("""### 2.4 进阶案例 2:用向量化实现"分组聚合" """))

cells.append(py_run([
    "# 模拟订单数据",
    "np.random.seed(42)",
    "amounts = np.random.randint(10, 5000, size=1000)",
    "channels = np.random.choice(['organic', 'paid', 'social'], size=1000)",
    "",
    "# 不用 for 循环,算每个渠道的总 GMV(向量化)",
    "for ch in ['organic', 'paid', 'social']:",
    "    mask = (channels == ch)",
    "    print(f'{ch}: 订单数 {mask.sum()}, GMV {amounts[mask].sum()}, 客单价 {amounts[mask].mean():.0f}')",
    "",
    "# 进阶:用 np.unique + 索引加速(对超大数组更快)",
    "ch_codes = np.searchsorted(['organic', 'paid', 'social'], channels)",
    "gmv_by_ch = np.bincount(ch_codes, weights=amounts)",
    "cnt_by_ch = np.bincount(ch_codes)",
    "print('\\n用 bincount 算:')",
    "for i, ch in enumerate(['organic', 'paid', 'social']):",
    "    print(f'{ch}: GMV {gmv_by_ch[i]:.0f}, 客单价 {gmv_by_ch[i]/cnt_by_ch[i]:.0f}')",
]))

cells.append(md("""### 2.5 陷阱案例

**陷阱 1**:小数组(< 1000)用向量化反而慢(初始化开销)
```python
# 不推荐:对 10 个元素做向量化
np.sum(np.array([1, 2, 3]))  # 内部开销 > 计算
```

**陷阱 2**:循环里调 NumPy 函数(没向量化)
```python
# 错:Python 循环调 sum
for i in range(N):
    total += np.sum(arr[i])  # 每步都创建新数组

# 对:整体向量化
total = np.sum(arr)  # 一次 C 调用
```

**陷阱 3**:append / insert 在大数组上极慢
```python
# 错:O(N) per append
result = np.array([])
for i in range(N):
    result = np.append(result, i)  # 慢!

# 对:先收集 list,再转 ndarray
result = np.array(list_of_values)  # O(N)
```

### 2.6 面试 Q&A

**Q1: 为什么 NumPy 快?**
A: 三个原因:1) 同构数据 + 连续内存(SIMD 友好);2) C 层循环,绕过 Python 字节码;3) 无 GIL 锁。

**Q2: 什么时候用循环?什么时候向量化?**
A: 数据 < 1000 用循环(初始化开销大);> 1000 必须向量化;亿级以上考虑 chunked / Polars / Dask。

**Q3: 向量化代码怎么调试?**
A: 1) 小数据测试 + 打印中间结果;2) 用 `np.vectorize` 把标量函数向量化(慢但能跑);3) 用 numba `@jit` 装饰 Python 函数。
"""))

# ============== 3. 广播 ==============

cells.append(md("""## 3. 广播机制(不同形状数组的运算)

### 3.1 原理

**广播**(Broadcasting):NumPy 自动把不同形状的数组"对齐",让算术运算成为可能。规则:
1. **维度对齐**:从尾部开始,每个维度要么相等,要么其中一个是 1
2. **维度缺失**视为 1
3. **复制扩展**:维度为 1 的会被"复制"到匹配

**不兼容**就报错:`ValueError: operands could not be broadcast together`

### 3.2 基础案例:广播的 3 个层次"""))

cells.append(py_run([
    "# 标量 + 数组(最简单)",
    "a = np.array([1, 2, 3])",
    "print('a + 10:', a + 10)  # 10 被广播到 [10, 10, 10]",
    "",
    "# 一维 + 一维(同形状)",
    "a = np.array([1, 2, 3])",
    "b = np.array([10, 20, 30])",
    "print('a + b:', a + b)",
    "",
    "# 二维 + 一维(广播!)",
    "a = np.array([[1, 2, 3], [4, 5, 6]])  # shape (2, 3)",
    "b = np.array([10, 20, 30])  # shape (3,)",
    "print('a + b:\\n', a + b)  # b 被广播到 [[10,20,30],[10,20,30]]",
]))

cells.append(md("""### 3.3 进阶案例:列向量 + 行向量"""))

cells.append(py_run([
    "# 列向量(2,1) + 行向量(1,3)",
    "col = np.array([[1], [2]])  # shape (2, 1)",
    "row = np.array([[10, 20, 30]])  # shape (1, 3)",
    "print('col:\\n', col)",
    "print('row:\\n', row)",
    "print('col + row:\\n', col + row)  # 广播到 (2, 3)",
    "",
    "# 实战:每行加不同的偏移",
    "# 场景:不同商品类别的销售数据,加不同的'促销系数'",
    "sales = np.array([[100, 200, 300], [400, 500, 600]])  # 2 个商店,3 个商品",
    "promotion = np.array([[1.0, 1.1, 1.2]])  # 1 行 3 列(每个商品一个系数)",
    "print('促销后:\\n', sales * promotion)",
]))

cells.append(md("""### 3.4 陷阱案例:广播不兼容

**反例 1**:
```python
a = np.array([1, 2, 3])  # shape (3,)
b = np.array([1, 2])  # shape (2,)
a + b  # ValueError: 不能广播
```

**反例 2**:列向量的方向搞错
```python
a = np.array([[1, 2, 3], [4, 5, 6]])  # (2, 3)
b = np.array([[1], [2]])  # (2, 1) - 列向量
a + b  # OK:广播到 (2, 3)

b = np.array([[1, 2]])  # (1, 2) - 行向量,维度对不上
a + b  # ValueError
```

**反例 3**:`(N, 1)` vs `(N,)` 的差别
```python
a = np.array([1, 2, 3])  # (3,)
b = np.array([[1], [2], [3]])  # (3, 1)
a + b  # 广播到 (3, 3)
# 跟 a * b 维度不同!
```

### 3.5 面试 Q&A

**Q1: 广播规则?**
A: 从尾部维度对齐,每个维度要么相等,要么其中一个是 1。维度 1 会被"复制"扩展。

**Q2: 广播的实际应用?**
A: 1) 标准化(每行减均值);2) 距离矩阵(N 维 vs M 维);3) 批量加偏移(每列不同系数)。

**Q3: 怎么避免广播错误?**
A: 显式 reshape:`a.reshape(-1, 1)` 或 `a[None, :]` 加维度。
"""))

# ============== 4. 聚合 + 矩阵 ==============

cells.append(md("""## 4. 聚合 + 矩阵运算

### 4.1 原理

**聚合**:沿某个维度"折叠"数组(求和、求平均、最大值等)。
- `axis=0`:沿**行**折叠(结果少一行)
- `axis=1`:沿**列**折叠(结果少一列)
- 不指定:全部折叠(标量)

**矩阵运算**:
- `*` 是元素乘(Hadamard 积)
- `@` 或 `np.dot` 或 `np.matmul` 是矩阵乘

### 4.2 基础案例:聚合函数"""))

cells.append(py_run([
    "a = np.arange(12).reshape(3, 4)",
    "print('a:\\n', a)",
    "",
    "print('总和:', a.sum())",
    "print('按列求和(axis=0):', a.sum(axis=0))  # 每列的总和",
    "print('按行求和(axis=1):', a.sum(axis=1))  # 每行的总和",
    "",
    "print('每列均值:', a.mean(axis=0))",
    "print('每行最大值:', a.max(axis=1))",
    "",
    "print('argmax(展平后的索引):', a.argmax())",
    "print('最大值:', a.max())",
]))

cells.append(py_run([
    "# 实战:电商用户消费统计",
    "np.random.seed(42)",
    "n_users, n_categories = 100, 5",
    "purchase = np.random.randint(0, 100, size=(n_users, n_categories))",
    "",
    "print('每个品类的总销量:', purchase.sum(axis=0))  # shape (5,)",
    "print('每个用户的总消费:', purchase.sum(axis=1))  # shape (100,)",
    "print('最受欢迎品类(总销量最高):', purchase.sum(axis=0).argmax())",
    "",
    "# 累计:每个用户的消费累计",
    "print('\\n前 3 个用户的消费累计:')",
    "print(np.cumsum(purchase[:3], axis=1))",
]))

cells.append(md("""### 4.3 进阶案例 1:矩阵乘法(ML 核心)"""))

cells.append(py_run([
    "A = np.array([[1, 2], [3, 4]])  # 2x2",
    "B = np.array([[5, 6], [7, 8]])  # 2x2",
    "",
    "print('A * B (元素乘):\\n', A * B)",
    "print('A @ B (矩阵乘):\\n', A @ B)",
    "print('np.dot(A, B):\\n', np.dot(A, B))",
    "",
    "# 实战:用户-品类矩阵 × 品类-价格向量 = 用户总消费",
    "user_category_qty = np.array([",
    "    [3, 0, 1, 2, 0],  # 用户 1:买了 3 个品类 0,1 个品类 2 ...",
    "    [0, 2, 1, 0, 1],  # 用户 2",
    "])  # shape (2, 5)",
    "category_price = np.array([100, 200, 50, 300, 80])  # shape (5,)",
    "",
    "user_total = user_category_qty @ category_price  # shape (2,)",
    "print('每用户总消费:', user_total)",
]))

cells.append(md("""### 4.4 进阶案例 2:线性代数(PCA / 距离矩阵基础)"""))

cells.append(py_run([
    "from numpy.linalg import inv, eig, norm",
    "",
    "A = np.array([[4, 2], [2, 3]])",
    "print('A:\\n', A)",
    "print('逆矩阵:\\n', inv(A))",
    "print('特征值:', eig(A)[0])  # 特征值",
    "print('特征向量:\\n', eig(A)[1])  # 特征向量(列)",
    "",
    "# 实战:欧氏距离矩阵(N 个样本两两距离)",
    "points = np.array([[0, 0], [1, 0], [0, 2], [3, 4]])  # 4 个点",
    "# 两两距离:diff[i,j] = |points[i] - points[j]|",
    "diff = points[:, None, :] - points[None, :, :]  # (4, 4, 2)",
    "dist_matrix = np.sqrt((diff ** 2).sum(axis=2))",
    "print('距离矩阵:\\n', dist_matrix)",
]))

cells.append(md("""### 4.5 陷阱案例

**陷阱 1**:`*` vs `@` 搞混
```python
A = np.array([[1, 2]])  # (1, 2)
B = np.array([[3], [4]])  # (2, 1)
A * B  # (1, 2) * (2, 1) 广播,结果 (2, 2)
A @ B  # (1, 1)
```

**陷阱 2**:`axis` 方向搞反
```python
a = np.array([[1, 2, 3], [4, 5, 6]])
a.sum(axis=0)  # [5, 7, 9] - 按列求和(结果一行)
a.sum(axis=1)  # [6, 15] - 按行求和(结果一列)
```

**陷阱 3**:`np.dot` 对 1-D 数组行为不一致
```python
np.dot([1, 2, 3], [4, 5, 6])  # 32(标量积)
np.dot([[1, 2]], [[3], [4]])  # 11(矩阵乘)
# 推荐用 @ 或 np.matmul,语义更清晰
```

### 4.6 面试 Q&A

**Q1: `*` 和 `@` 区别?**
A: `*` 是元素乘(Hadamard 积,同形状);`@` 是矩阵乘(行 × 列求和)。形状不同时 `*` 用广播,`@` 要求内维度匹配。

**Q2: PCA 怎么用 NumPy 实现?**
A: 1) 中心化(减均值);2) 协方差矩阵(X.T @ X / n);3) 特征值分解(eig);4) 取最大 k 个特征值对应的特征向量。

**Q3: 大矩阵乘法的内存问题?**
A: 1000x1000 矩阵乘 = 8MB(单精度),一般无问题。10000x10000 = 8GB,需要分块或换稀疏矩阵。
"""))

# ============== 5. 实战案例 ==============

cells.append(md("""## 5. 实战案例:用 NumPy 算 5 个电商指标

### 5.1 数据准备(用 SQL 拉数据)"""))

cells.append(py_run([
    "import sqlite3",
    "from pathlib import Path",
    "",
    "if 'conn' not in globals():",
    "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))",
    "",
    "# 用 SQL 拉数据,直接得 DataFrame",
    "orders_df = pd.read_sql('SELECT user_id, order_date, amount, status FROM orders', conn)",
    "print('订单数据:', orders_df.shape)",
    "print(orders_df.head())",
]))

cells.append(py_run([
    "import sqlite3",
    "from pathlib import Path",
    "",
    "if 'conn' not in globals():",
    "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))",
    "if 'orders_df' not in globals():",
    "    orders_df = pd.read_sql('SELECT user_id, order_date, amount, status FROM orders', conn)",
    "",
    "# 把订单数据转 NumPy 数组(加快后续计算)",
    "completed = orders_df[orders_df['status'] == 'completed']",
    "amounts = completed['amount'].values  # 1D ndarray",
    "user_ids = completed['user_id'].values",
    "",
    "print('完成订单数:', len(amounts))",
    "print('总 GMV:', amounts.sum())",
    "print('平均订单金额:', amounts.mean())",
    "print('最大订单金额:', amounts.max())",
    "print('订单金额中位数:', np.median(amounts))",
    "print('订单金额标准差:', amounts.std())",
]))

cells.append(py_run([
    "import sqlite3",
    "from pathlib import Path",
    "",
    "if 'conn' not in globals():",
    "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))",
    "if 'orders_df' not in globals():",
    "    orders_df = pd.read_sql('SELECT user_id, order_date, amount, status FROM orders', conn)",
    "completed = orders_df[orders_df['status'] == 'completed']",
    "amounts = completed['amount'].values",
    "user_ids = completed['user_id'].values",
    "",
    "# 实战 1:消费分层(用分位数)",
    "p25, p50, p75, p90, p99 = np.percentile(amounts, [25, 50, 75, 90, 99])",
    "print(f'P25: {p25}, P50: {p50}, P75: {p75}, P90: {p90}, P99: {p99}')",
    "",
    "# 实战 2:头尾 10% 用户贡献多少 GMV(帕累托分析)",
    "user_total = np.bincount(user_ids, weights=amounts)  # 每个用户的总 GMV",
    "user_total_sorted = np.sort(user_total)[::-1]  # 降序",
    "",
    "top_10pct = int(len(user_total_sorted) * 0.1)",
    "top_gmv = user_total_sorted[:top_10pct].sum()",
    "all_gmv = user_total_sorted.sum()",
    "print(f'头部 10% 用户({top_10pct} 人)贡献 GMV: {top_gmv/all_gmv*100:.1f}%')",
    "",
    "# 实战 3:用户消费分箱",
    "bins = [0, 100, 500, 1000, 5000, float('inf')]",
    "labels = ['小单', '中单', '大单', '超大单', '超超大单']",
    "bin_idx = np.digitize(amounts, bins) - 1",
    "print('订单分布(按金额):')",
    "for i, label in enumerate(labels):",
    "    cnt = (bin_idx == i).sum()",
    "    pct = cnt / len(amounts) * 100",
    "    gmv_pct = amounts[bin_idx == i].sum() / amounts.sum() * 100",
    "    print(f'  {label}: {cnt} 单 ({pct:.1f}%), 贡献 GMV {gmv_pct:.1f}%')",
]))

cells.append(py_run([
    "import sqlite3",
    "from pathlib import Path",
    "",
    "if 'conn' not in globals():",
    "    conn = sqlite3.connect(str(Path('../data/ecommerce.db').resolve()))",
    "if 'orders_df' not in globals():",
    "    orders_df = pd.read_sql('SELECT user_id, order_date, amount, status FROM orders', conn)",
    "completed = orders_df[orders_df['status'] == 'completed']",
    "amounts = completed['amount'].values",
    "",
    "# 实战 4:用户消费跨度分析(用布尔索引)",
    "user_orders = pd.read_sql('''",
    "    SELECT user_id, COUNT(*) AS cnt, SUM(amount) AS gmv, MAX(order_date) AS last_order",
    "    FROM orders WHERE status = 'completed'",
    "    GROUP BY user_id",
    "''', conn)",
    "",
    "cnt_arr = user_orders['cnt'].values",
    "print('每用户订单数统计:')",
    "print(f'  均值: {cnt_arr.mean():.1f}, 中位数: {np.median(cnt_arr):.0f}')",
    "print(f'  1 单用户: {(cnt_arr == 1).sum()} ({(cnt_arr==1).sum()/len(cnt_arr)*100:.1f}%)')",
    "print(f'  2-5 单用户: {((cnt_arr >= 2) & (cnt_arr <= 5)).sum()}')",
    "print(f'  >=10 单用户: {(cnt_arr >= 10).sum()} ({(cnt_arr>=10).sum()/len(cnt_arr)*100:.1f}%)')",
    "",
    "# 实战 5:金额异常检测(3σ 原则)",
    "mean = amounts.mean()",
    "std = amounts.std()",
    "outliers = amounts[(amounts > mean + 3*std) | (amounts < mean - 3*std)]",
    "print(f'\\n3σ 异常值数量: {len(outliers)}, 占比 {len(outliers)/len(amounts)*100:.2f}%')",
    "print(f'异常值范围: {outliers.min() if len(outliers) else 0} ~ {outliers.max() if len(outliers) else 0}')",
]))

cells.append(md("""## 6. 小结

### 速查表

| 需求 | NumPy 写法 |
|------|----------|
| 创建数组 | `np.array / zeros / ones / arange / linspace` |
| 形状 | `.shape / .reshape / .ravel / .T` |
| 索引 | `a[i] / a[i, j] / a[start:end] / a[mask]` |
| 算术 | `a + b / a * b / a ** 2`(全部向量化) |
| 广播 | 维度对齐 + 维度 1 扩展 |
| 聚合 | `a.sum / mean / max / std / percentile(axis=...)` |
| 矩阵乘 | `a @ b` 或 `np.dot / np.matmul` |
| 距离 | `np.linalg.norm` 或广播相减 |

### 自测清单

- [ ] 能解释 ndarray 比 list 快 50-100 倍的 3 个原因
- [ ] 能用向量化代码替换 for 循环
- [ ] 能解释广播规则
- [ ] 能用 `np.bincount` 做分组聚合
- [ ] 能用 `*` vs `@` 的区别
- [ ] 能用 NumPy 算 5 个电商指标

**全部 ✅ 之后可以推进 W2.2(Pandas 基础)。**
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

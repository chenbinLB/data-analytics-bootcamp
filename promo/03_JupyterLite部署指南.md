# JupyterLite 零环境在线版 —— 部署指南

> 目标:让用户**不用装任何东西**,浏览器打开链接就能跑 14 个 notebook

---

## 方案对比

| 平台 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| **JupyterLite** | 真零环境、永久免费、可绑定自己域名 | 数据 26MB 上传慢一点 | ⭐⭐⭐ |
| **Google Colab** | 免费 GPU、白嫖 Google | 网速依赖 Google、需要 Google 账号 | ⭐⭐ |
| **阿里天池** | 国内快、中文支持 | 需要注册、可能收费 | ⭐⭐ |
| **腾讯 Cloud Studio** | 国内、有免费额度 | 配置复杂、有时间限制 | ⭐ |

**推荐方案**:**JupyterLite(主力) + 百度网盘 + Colab(备选)**

---

## 方案 A:JupyterLite 部署(主力)

### 原理
JupyterLite 把 Jupyter 直接跑在浏览器里(Python 是 Pyodide,WebAssembly 版),
**用户打开链接就是 Jupyter 界面**。

### 步骤 1:本地构建 JupyterLite(一次性)

```bash
# 安装 JupyterLite
pip install jupyterlite

# 在项目根目录创建 jupyter-lite 目录
cd data-analytics-bootcamp
jupyter lite init

# 复制你的 notebook + data
cp module_*/*.ipynb jupyter-lite/files/
cp data/ecommerce.db jupyter-lite/files/
```

### 步骤 2:构建静态站点

```bash
# 构建出可在浏览器跑的版本
jupyter lite build

# 构建产物在 ./jupyter-lite/_output/
```

### 步骤 3:部署(3 种免费方式任选)

#### 方式 1:GitHub Pages(推荐,免费 + 永久)

```bash
# 1. 把 jupyter-lite/_output/ 的内容推到你 GitHub 仓库的 gh-pages 分支
# 2. 仓库设置 -> Pages -> 选 gh-pages 分支
# 3. 访问 https://<用户名>.github.io/<仓库名>/lab/index.html
```

#### 方式 2:Vercel(免费 + 国内访问快)

```bash
# 1. 注册 Vercel(可用 GitHub 登录)
# 2. 导入你的 GitHub 仓库
# 3. 框架选 "Other",构建命令留空
# 4. 部署完成后会给一个 <项目名>.vercel.app 域名
```

#### 方式 3:Netlify(免费 + 拖拽即用)

```bash
# 1. 注册 Netlify
# 2. 把 jupyter-lite/_output/ 文件夹拖到 Netlify 部署区
# 3. 自动生成 <随机名>.netlify.app 域名
```

### 步骤 4:用户使用流程

```
1. 打开链接 https://your-domain.com/lab/index.html
2. 看到 Jupyter 界面(全在浏览器跑)
3. 左侧文件树点开 02_window_functions.ipynb
4. 点运行,代码立刻出结果
5. 完全不需要装环境
```

---

## 方案 B:百度网盘 + 本地 notebook(备选)

### 打包结构

```
data-analytics-bootcamp-49.zip (约 30MB)
├── README.md                  # 1 页 PDF 卖点(可选)
├── 14 个 notebook 文件
├── data/ecommerce.db
├── setup_env.py               # 本地环境脚本
└── 一键启动.bat / .sh         # 双击启动
```

### 一键启动脚本

**Windows: `一键启动.bat`**
```bat
@echo off
chcp 65001
echo ========================================
echo  大厂数分 4 周突击 - 一键启动
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    echo 请先安装 Python 3.10+:https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖(首次需要 2-3 分钟)...
pip install -r requirements.txt

REM 启动 Jupyter
echo.
echo 启动 Jupyter,浏览器会自动打开...
echo 关闭此窗口 = 停止 Jupyter
echo.
jupyter lab
pause
```

**Mac/Linux: `一键启动.sh`**
```bash
#!/bin/bash
echo "========================================"
echo " 大厂数分 4 周突击 - 一键启动"
echo "========================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3"
    echo "请先安装:brew install python3(Mac)或 apt install python3(Linux)"
    exit 1
fi

# 安装依赖
echo "正在安装依赖(首次需要 2-3 分钟)..."
pip3 install -r requirements.txt

# 启动 Jupyter
echo ""
echo "启动 Jupyter,浏览器会自动打开..."
echo "关闭此窗口 = 停止 Jupyter"
echo ""
jupyter lab
```

---

## 方案 C:Google Colab 一键打开(最省事)

### 原理
每个 notebook 顶部加一行代码,自动从 GitHub 拉数据

### 顶部代码模板(每个 notebook 第一格)

```python
# === Colab 一键运行环境 ===
# 1. 克隆仓库
!git clone https://github.com/你的用户名/data-analytics-bootcamp.git /content/bc
%cd /content/bc

# 2. 安装依赖
!pip install -q -r requirements.txt

# 3. 复制数据
import shutil
shutil.copy('data/ecommerce.db', '/content/')

# 4. 切换工作目录
import os
os.chdir('/content')
print("环境就绪!")
```

### 分享链接格式

```
https://colab.research.google.com/github/你的用户名/data-analytics-bootcamp/blob/main/module_01_sql/02_window_functions.ipynb
```

**用户点开就自动进 Colab,代码运行 = 环境就绪**

---

## 我的执行顺序(接下来的步骤)

1. **本目录创建 jupyter-lite**(用 14 个 notebook)
2. **构建 jupyter-lite**(输出 _output 文件夹)
3. **写百度网盘打包脚本**(一键启动)
4. **写 Colab 顶部代码**(每个 notebook 复制)
5. **给你 3 个使用链接 + 上传网盘操作步骤**

### 实际工作量
- 创建 + 构建 jupyterlite:1-2 小时(取决于 14 个 notebook 总大小)
- 写打包脚本:30 分钟
- 写 Colab 模板:30 分钟
- 测试:30 分钟

**总计 3-4 小时**

---

## 风险与应对

| 风险 | 应对 |
|------|------|
| 26MB 数据库在 JupyterLite 里加载慢 | 测试后告诉你实际速度,慢就改用"按需生成" |
| Pyodide 不支持某些库(duckdb 等) | 不用 duckdb / polars,只用 pandas / numpy / matplotlib |
| GitHub Pages 加载 30+ MB 慢 | 拆分上传 / 用 Vercel / 用 Netlify |
| 用户不会进 Colab(需要梯子) | 主推 JupyterLite,Colab 做备选 |

---

## 你需要准备的(我先做,你再补)

1. **GitHub 账号**(用来放仓库 + Pages 部署)
2. **百度网盘账号**(卖课时放网盘链接)
3. **微信号 + 二维码**(放 PDF 卖点)

这三个有的话,告诉我,我立刻开始 jupyterlite 构建。

---

**最后更新**:2026-06-09
**建议方案**:JupyterLite(主力)+ 百度网盘(备选)+ Colab(进阶备选)

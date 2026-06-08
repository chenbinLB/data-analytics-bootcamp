# -*- coding: utf-8 -*-
"""
setup_env.py — 大厂数分 4 周突击课 一键环境配置
================================================
用途:用户运行本脚本,自动检查并安装所有依赖,生成 14 个 notebook 所需环境。

用法:
    Windows: python setup_env.py
    Mac/Linux: python3 setup_env.py
"""

import sys
import subprocess
import platform
import os
from pathlib import Path


# ===== 配色(终端友好)=====
class C:
    H = "\033[95m"  # 标题
    B = "\033[94m"  # 蓝
    G = "\033[92m"  # 绿
    Y = "\033[93m"  # 黄
    R = "\033[91m"  # 红
    E = "\033[0m"   # 结束
    BOLD = "\033[1m"


def log(msg, color=C.B):
    print(f"{color}{msg}{C.E}")


def step(n, title):
    print()
    log(f"{'='*60}", C.H)
    log(f"  [{n}/5] {title}", C.H + C.BOLD)
    log(f"{'='*60}", C.H)


# ===== Step 1: 检查 Python =====
def check_python():
    step(1, "检查 Python 环境")

    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        log(f"  [OK] Python {version.major}.{version.minor}.{version.micro}", C.G)
        return True
    elif version.major == 3 and version.minor >= 9:
        log(f"  [WARN] Python {version.major}.{version.minor} 兼容但建议升级到 3.10+", C.Y)
        return True
    else:
        log(f"  [FAIL] Python {version.major}.{version.minor} 不支持,需 3.9+", C.R)
        log(f"  请到 https://www.python.org/downloads/ 下载 3.11", C.Y)
        return False


# ===== Step 2: 检查 pip =====
def check_pip():
    step(2, "检查 pip")
    try:
        out = subprocess.run([sys.executable, "-m", "pip", "--version"],
                             capture_output=True, text=True, check=True)
        log(f"  [OK] {out.stdout.strip()}", C.G)
        return True
    except Exception as e:
        log(f"  [FAIL] pip 不可用: {e}", C.R)
        return False


# ===== Step 3: 安装依赖 =====
def install_deps():
    step(3, "安装依赖包(首次 2-3 分钟)")

    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        log(f"  [FAIL] 找不到 requirements.txt", C.R)
        return False

    log(f"  依赖列表: {req_file}", C.B)
    log(f"  正在使用国内镜像源加速(清华源)...", C.B)

    mirrors = [
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "https://mirrors.aliyun.com/pypi/simple",
        "https://pypi.org/simple",  # 兜底
    ]

    for mirror in mirrors:
        log(f"  尝试镜像: {mirror}", C.B)
        cmd = [
            sys.executable, "-m", "pip", "install",
            "-r", str(req_file),
            "-i", mirror,
            "--trusted-host", "pypi.tuna.tsinghua.edu.cn",
            "--trusted-host", "mirrors.aliyun.com",
            "--trusted-host", "pypi.org",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                log(f"  [OK] 依赖安装完成", C.G)
                return True
            else:
                log(f"  [WARN] 镜像失败,尝试下一个", C.Y)
        except Exception as e:
            log(f"  [WARN] {e}", C.Y)

    log(f"  [FAIL] 所有镜像都失败,请检查网络", C.R)
    return False


# ===== Step 4: 检查数据 =====
def check_data():
    step(4, "检查数据文件")
    data_dir = Path(__file__).parent / "data"
    db_file = data_dir / "ecommerce.db"

    if db_file.exists():
        size_mb = db_file.stat().st_size / 1024 / 1024
        log(f"  [OK] 数据文件就绪 ({size_mb:.1f} MB): {db_file}", C.G)
        return True
    else:
        log(f"  [WARN] 数据文件不存在,尝试生成...", C.Y)
        setup_data = Path(__file__).parent / "module_01_sql" / "setup_data.py"
        if setup_data.exists():
            log(f"  运行: {setup_data}", C.B)
            result = subprocess.run([sys.executable, str(setup_data)],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                log(f"  [OK] 数据生成成功", C.G)
                return True
        log(f"  [FAIL] 数据文件缺失,请确认 data/ecommerce.db 存在", C.R)
        return False


# ===== Step 5: 启动 Jupyter =====
def launch_jupyter():
    step(5, "启动 Jupyter(关闭此窗口 = 停止)")

    log(f"  准备打开浏览器,请稍等...", C.B)

    # 检查 jupyter
    try:
        subprocess.run([sys.executable, "-m", "jupyter", "--version"],
                       capture_output=True, check=True)
    except Exception:
        log(f"  [INFO] 安装 jupyter...", C.B)
        subprocess.run([sys.executable, "-m", "pip", "install",
                        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
                        "jupyter", "ipykernel"], check=False)

    log(f"  启动后,请按以下顺序学习:", C.G)
    log(f"    1. module_01_sql/01_basics_review.ipynb", C.B)
    log(f"    2. module_01_sql/02_window_functions.ipynb", C.B)
    log(f"    3. ... 一直到 module_04_projects/02_ai_and_job_prep.ipynb", C.B)

    log(f"  按 Ctrl+C 停止", C.Y)
    print()

    try:
        subprocess.run([sys.executable, "-m", "jupyter", "lab"], check=False)
    except KeyboardInterrupt:
        log(f"\n  已停止", C.G)


# ===== Main =====
def main():
    os.system("cls" if platform.system() == "Windows" else "clear")

    log(f"""
    ============================================================
       大厂数分 4 周突击 - 一键环境配置
       Big Tech Data Analyst 4-Week Bootcamp - Setup
    ============================================================
       课程价格: 49.9 元
       14 个 notebook + 真实数据集
       让小白 4 周从 0 到能面试
    ============================================================
    """, C.H + C.BOLD)

    if not check_python():
        input("按回车键退出...")
        return 1

    if not check_pip():
        input("按回车键退出...")
        return 1

    if not install_deps():
        log(f"\n  依赖安装失败,你可以:", C.R)
        log(f"  1. 重新运行本脚本(网络问题),或", C.Y)
        log(f"  2. 手动运行: pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple", C.Y)
        input("按回车键退出...")
        return 1

    if not check_data():
        log(f"\n  数据文件缺失,不影响其他功能,你可以:", C.Y)
        log(f"  1. 跳过数据相关 notebook,或", C.Y)
        log(f"  2. 联系作者获取完整 data/ 文件夹", C.Y)

    launch_jupyter()
    return 0


if __name__ == "__main__":
    sys.exit(main())

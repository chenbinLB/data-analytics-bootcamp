# -*- coding: utf-8 -*-
"""verify.py — 验证单个 notebook 全部 cell 能跑通(跨平台版本)"""
import json, os, subprocess, sys
from pathlib import Path

# 强制 UTF-8 输出,Windows 必备
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

NB_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if NB_PATH is None:
    print("Usage: python verify.py <notebook.ipynb>")
    sys.exit(1)

NB_PATH = Path(NB_PATH)
print(f"\n===== {NB_PATH.name} =====")

nb = json.loads(NB_PATH.read_text(encoding='utf-8'))
code_cells = [(i, ''.join(c['source'])) for i, c in enumerate(nb['cells'])
              if c['cell_type'] == 'code' and ''.join(c['source']).strip()]
print(f"Total code cells: {len(code_cells)}")

failed = 0
for idx, (cell_idx, src) in enumerate(code_cells, 1):
    first_line = src.split('\n')[0][:50]
    tmp = Path("_tmp_run.py").resolve()
    tmp.write_text(src, encoding='utf-8')
    try:
        result = subprocess.run(
            [sys.executable, str(tmp)],
            capture_output=True, text=True, timeout=60, cwd=str(NB_PATH.parent.resolve()),
            env={**os.environ, 'MPLBACKEND': 'Agg'}
        )
        if result.returncode == 0:
            status = 'OK'
        else:
            status = f'FAIL: {result.stderr[:200]}'
            failed += 1
    except subprocess.TimeoutExpired:
        status = 'TIMEOUT'
        failed += 1
    print(f"  #{idx:2d} {status}  | {first_line}")
    tmp.unlink(missing_ok=True)

print(f"\n  ---> {len(code_cells) - failed}/{len(code_cells)} passed")
sys.exit(0 if failed == 0 else 1)

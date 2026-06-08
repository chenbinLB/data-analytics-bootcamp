# -*- coding: utf-8 -*-
import json, os, subprocess
from pathlib import Path
import sys
import io

# 修复 Windows 默认 cp1252 编码,让中文 print 不报错(GitHub Actions 必备)
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

NB_PATH = sys.argv[1] if len(sys.argv) > 1 else None
if NB_PATH is None:
    # 默认验证所有 notebook
    nb_paths = []
    for sub in ['module_01_sql', 'module_02_python', 'module_03_stats']:
        d = Path(rf'C:\Users\23596\.mavis\sessions\mvs_2cb7c6ea190c461eb815fb861c22ed5d\workspace\data-analytics-bootcamp\{sub}')
        if d.exists():
            nb_paths += sorted(d.glob('*.ipynb'))
else:
    nb_paths = [Path(NB_PATH)]

for NB in nb_paths:
    print(f'\n===== {NB.name} =====')
    os.chdir(NB.parent)

    with open(NB, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    code_cells = [(i, ''.join(c['source'])) for i, c in enumerate(nb['cells']) if c['cell_type'] == 'code' and ''.join(c['source']).strip()]
    print(f'Total code cells: {len(code_cells)}')

    failed = 0
    for idx, (cell_idx, src) in enumerate(code_cells, 1):
        first_line = src.split('\n')[0][:50]
        tmp = NB.parent / "_tmp_run.py"
        tmp.write_text(src, encoding='utf-8')
        try:
            result = subprocess.run(
                ['py', str(tmp)],
                capture_output=True, text=True, timeout=30, cwd=NB.parent,
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
        print(f'  #{idx:2d} {status}  | {first_line}')
        tmp.unlink(missing_ok=True)
    print(f'\n  ---> {len(code_cells) - failed}/{len(code_cells)} passed')

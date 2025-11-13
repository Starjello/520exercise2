#!/usr/bin/env python3
"""
Delete all files and subfolders inside tests/problem_102 but keep the folder itself.
Use this to reset before a new convergence run.
"""

import shutil
from pathlib import Path

PROBLEM_ID = 102  # change if needed
ROOT = Path(__file__).resolve().parent
TESTS_DIR = ROOT / "tests" / f"problem_{PROBLEM_ID}"

if TESTS_DIR.exists():
    for item in TESTS_DIR.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
    print(f"✅ Cleared contents of {TESTS_DIR}")
else:
    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created empty folder {TESTS_DIR}")

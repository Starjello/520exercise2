#!/usr/bin/env python3
"""
Clear all generated test and result files for problem 106.
Removes tests/problem_106/ and the corresponding results file if present.
"""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
TEST_DIR = ROOT / "tests" / "problem_106"
RESULT_FILE = ROOT / "results" / "problem_106_coverage.txt"

# Delete the tests folder
if TEST_DIR.exists():
    try:
        shutil.rmtree(TEST_DIR)
        print(f"🧹 Deleted folder: {TEST_DIR}")
    except Exception as e:
        print(f"⚠️ Could not delete {TEST_DIR}: {e}")
else:
    print(f"✅ No folder found for {TEST_DIR}")

# Delete the results file
if RESULT_FILE.exists():
    try:
        RESULT_FILE.unlink()
        print(f"🧹 Deleted file: {RESULT_FILE}")
    except Exception as e:
        print(f"⚠️ Could not delete {RESULT_FILE}: {e}")
else:
    print(f"✅ No results file found for {RESULT_FILE}")

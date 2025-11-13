# conftest.py
import os
import sys
import pathlib

# ──────────────────────────────────────────────
# Choose which implementation to test:
#   IMPL: openai | gemini
#   QUALITY: correct | incorrect
# You set these in the terminal before running pytest:
#   $env:IMPL="openai"; $env:QUALITY="correct"
# ──────────────────────────────────────────────

IMPL = os.environ.get("IMPL", "openai").lower()
QUALITY = os.environ.get("QUALITY", "correct").lower()

# Get the directory where this file lives (project root)
root = pathlib.Path(__file__).resolve().parent

# Build path to the selected solution folder
if QUALITY == "correct":
    base = root / "solutions_correct" / IMPL
else:
    base = root / "generated_solutions" / IMPL

# Safety check
if not base.exists():
    raise RuntimeError(f"Selected path does not exist: {base}")

# Add the selected folder to Python’s import path
sys.path.insert(0, str(base))

print(f"[conftest] Using implementation path: {base}")

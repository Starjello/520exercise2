# -------------------------------
# run_humaneval.ps1
# Double-click script for:
# 1. Activating venv
# 2. Running pytest with coverage
# 3. Running HumanEval combined summary
# -------------------------------

Write-Host "=== Activating virtual environment ==="

# Adjust path if your venv folder is not named '.venv'
$venvPath = ".\.venv\Scripts\Activate.ps1"

if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "Virtual environment activated."
} else {
    Write-Host "ERROR: Could not find virtual environment at $venvPath"
    Write-Host "Make sure this file is in the same folder as your venv."
    Pause
    exit 1
}

Write-Host "`n=== Running pytest with coverage ==="
pytest -v `
  --cov=openai_solutions `
  --cov-branch `
  --cov-report=term-missing `
  --cov-report=json:coverage.json

Write-Host "`n=== Running HumanEval Coverage Summary ==="
python humaneval_coverage_summary.py

Write-Host "`n=== Done! Summary written to humaneval_coverage_summary.txt ==="

# Keep window open
Pause

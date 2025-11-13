# LLM Evaluation Project (Minimal Instructions)

## Requirements
Install these packages inside your virtual environment:
pip install openai google-genai human-eval pytest pytest-cov

## Setting API Keys (inside your venv)
Windows PowerShell:
setx OPENAI_API_KEY "your_key_here"
setx GOOGLE_API_KEY "your_key_here"
Restart terminal afterwards.

---

## Files to Use / Look At

### OpenAI HumanEval runner
- run_humaneval_openai.py  
  Runs models on HumanEval tasks and saves solutions.

### HumanEval test suite (Pytest)
- test_humaneval_baseline.py  
  The pytest file that executes HumanEval tests on your solutions.

### Pytest config
- conftest.py  
  Configuration for loading solution files.

### Coverage summary generator (Part 1)
- humaneval_coverage_summary.py  
  Produces the combined HumanEval + coverage table.

### Bug testing framework (Part 2)
convergence.py for the test suite generation and coverage check
- run_bug_test.py  
  Tests 102_bug.py and 106_bug.py against:
  - HumanEval tests  
  - All iteration tests (iter_01, iter_02, iter_03)  
  Each assert is treated independently.

### Solutions + Debug Files
Inside:
openai_solutions/
Contains all generated solutions, debug logs, corrected solutions, and bug files used by the scripts.

---

## How to Run

### 1. Activate virtual environment
.\.venv\Scripts\activate

### 2. Run HumanEval + coverage (Part 1)
pytest -v --cov=openai_solutions --cov-branch --cov-report=term-missing --cov-report=json:coverage.json
python humaneval_coverage_summary.py

### 3. Run bug tests (Part 2)
python run_bug_test.py

---

## Notes
- Only the listed files are needed for the assignment.
- All other files/folders are just storage for solutions and intermediate outputs.


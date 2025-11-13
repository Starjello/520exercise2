#!/usr/bin/env python3
"""
LLM test generation loop for HumanEval (no CLI args) with prior-test memory.
- Run from repo ROOT.
- Edit SOLUTION_FILE and ENTRY_POINT below.
- Solution is loaded from ROOT/openai_solutions/SOLUTION_FILE via importlib (no package path).
- Cumulative tests in ROOT/tests/problem_<ID>/
- Coverage collected via 'coverage run' (not pytest-cov) and written per-iteration XML.
- Results appended to ROOT/results/problem_<ID>_coverage.txt
- Each iteration shows ChatGPT the tests from previous iterations to reduce duplicates.
"""

import os
import re
import sys
import time
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

from human_eval.data import read_problems
PROBLEM_ID = 106
# ===================== EDIT THESE TWO =====================
SOLUTION_FILE = f"humaneval_{PROBLEM_ID}_openai_attempt_001_base.py"   # file in openai_solutions/
ENTRY_POINT   = "f"                                  # function defined in that file
# ==========================================================


ITERATIONS = 3
MODEL = "gpt-4o-mini"
# Limit of how many prior-test characters to show (to keep prompt size sane)
PRIOR_TESTS_CHAR_BUDGET = 6000

ROOT = Path(__file__).resolve().parent
SOL_PATH = ROOT / "openai_solutions" / SOLUTION_FILE
SOL_PATH_POSIX = SOL_PATH.resolve().as_posix()   # single canonical path for import + coverage
SRC_DIR = SOL_PATH.parent                         # directory containing the solution file
TESTS_DIR = ROOT / "tests" / f"problem_{PROBLEM_ID}"
RESULTS_FILE = ROOT / "results" / f"problem_{PROBLEM_ID}_coverage.txt"

# OpenAI client (modern SDK)
try:
    from openai import OpenAI
except Exception as e:
    raise SystemExit("Please `pip install openai` before running this script.") from e

PROMPT_TEMPLATE = """You are a senior test engineer improving test coverage for a single function.

Context:
- HumanEval problem: {task_id}
- Function name (entry point): {entry_point}
- Function spec/docstring:

\"\"\"{prompt}\"\"\"

Goal:
Maximize **branch coverage** — not just input variety.  
Design tests that cause both True and False outcomes for every condition in the code.
Keep in mind that your last answer with a high probability missed a lot of branches.

Guidelines:
- For each `if` or `while` condition, include at least one test that makes it True and one that makes it False.
- Include tests that:
  * trigger early returns or skipped paths (e.g., when x>y),
  * hit end-of-loop cases where no condition is satisfied,
  * explore boundaries (equal numbers, smallest/largest valid inputs),
  * and exercise exception or empty-range behavior if possible.
- Do NOT repeat or trivially vary existing tests.
- Use only valid integers unless floats are explicitly supported.
- Each test must contain an assert with an expected value — no print statements.
- Output: **ONLY Python test code**, no prose or markdown fences.

Coverage feedback from previous run:
{coverage_hint}

Existing tests (to avoid duplication):
{prior_tests}
"""



def get_humaneval_spec(problem_id: int):
    data = read_problems()
    if isinstance(data, dict):
        problems = data
    else:
        problems = {p["task_id"]: p for p in data}
    task_id = f"HumanEval/{problem_id}"
    if task_id not in problems:
        raise RuntimeError(f"Problem {problem_id} not found in HumanEval")
    p = problems[task_id]
    return task_id, p["entry_point"], p["prompt"]

def call_chatgpt(model: str, system_msg: str, user_msg: str) -> str:
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )
    content = (resp.choices[0].message.content or "").strip()
    m = re.match(r"^```(?:python)?\s*([\s\S]*?)\s*```$", content, re.IGNORECASE)
    if m:
        content = m.group(1).strip()
    return content

def build_test_preamble(entry_point: str) -> str:
    """Import the solution module from a fixed POSIX path and expose ENTRY_POINT."""
    return f"""# Auto-import solution module from file path
import importlib.util, pathlib
_SOL_FILE = pathlib.Path(r\"\"\"{SOL_PATH_POSIX}\"\"\")
_spec = importlib.util.spec_from_file_location("solution_mod", _SOL_FILE)
solution_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(solution_mod)
{entry_point} = getattr(solution_mod, "{entry_point}")
"""

def write_test_file(iter_idx: int, preamble: str, llm_tests: str) -> Path:
    TESTS_DIR.mkdir(parents=True, exist_ok=True)
    fname = TESTS_DIR / f"test_humaneval_{PROBLEM_ID}_llm_iter_{iter_idx:02d}.py"
    fname.write_text(preamble.rstrip() + "\n\n" + llm_tests.strip() + "\n", encoding="utf-8")
    return fname

def run_pytest_with_coverage(xml_out: Path, cov_data_file: Path):
    """
    Run tests under coverage, then write xml to xml_out.
    We avoid pytest-cov: use `coverage run --branch --source=<dir> -m pytest`.
    """
    env = os.environ.copy()
    env["COVERAGE_FILE"] = str(cov_data_file)  # per-iteration .coverage file

    # 1) Run pytest under coverage
    cmd_run = [
    sys.executable, "-m", "coverage", "run",
    "--branch",
    f"--source={SRC_DIR.resolve().as_posix()}",
    "-m", "pytest", "-q", str(TESTS_DIR),
]

    proc1 = subprocess.run(cmd_run, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), env=env)

    # 2) Generate XML
    cmd_xml = [
    sys.executable, "-m", "coverage", "xml",
    "-o", str(xml_out),
    str(SOL_PATH.resolve())
]

    proc2 = subprocess.run(cmd_xml, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), env=env)

    stdout_all = (proc1.stdout or "") + "\n" + (proc2.stdout or "")
    return stdout_all, max(proc1.returncode, proc2.returncode)

def wait_for_file(path: Path, timeout_s: float = 3.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if path.exists() and path.stat().st_size > 0:
            return True
        time.sleep(0.1)
    return path.exists() and path.stat().st_size > 0

def parse_coverage_xml(xml_path: Path):
    """Parse coverage.xml root attrs, then fallback to totals if missing."""
    if not xml_path.exists() or xml_path.stat().st_size == 0:
        return None, None
    root = ET.parse(xml_path).getroot()
    def to_pct(attr_name):
        val = root.attrib.get(attr_name)
        try:
            return None if val is None else float(val) * 100.0
        except Exception:
            return None
    line_pct = to_pct("line-rate")
    branch_pct = to_pct("branch-rate")
    if line_pct is None:
        try:
            lines_valid = float(root.attrib.get("lines-valid", "0"))
            lines_covered = float(root.attrib.get("lines-covered", "0"))
            if lines_valid > 0:
                line_pct = 100.0 * (lines_covered / lines_valid)
        except Exception:
            pass
    if branch_pct is None:
        try:
            branches_valid = float(root.attrib.get("branches-valid", "0"))
            branches_covered = float(root.attrib.get("branches-covered", "0"))
            if branches_valid > 0:
                branch_pct = 100.0 * (branches_covered / branches_valid)
        except Exception:
            pass
    return line_pct, branch_pct

def append_results_line(results_file: Path, iter_idx: int, line_pct, branch_pct, note: str):
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with results_file.open("a", encoding="utf-8") as f:
        lp = float('nan') if line_pct is None else line_pct
        bp = float('nan') if branch_pct is None else branch_pct
        f.write(f"iter={iter_idx:02d}\tline%={lp:.2f}\tbranch%={bp:.2f}\t{note}\n")

def collect_prior_tests_text(current_iter_idx: int) -> str:
    """Read all earlier test files and return trimmed concatenation within a char budget."""
    files = sorted(TESTS_DIR.glob(f"test_humaneval_{PROBLEM_ID}_llm_iter_*.py"))
    texts = []
    total = 0
    for f in files:
        # ignore file that would be created this iteration
        if f.name.endswith(f"{current_iter_idx:02d}.py"):
            continue
        t = f"# {f.name}\n" + f.read_text(encoding='utf-8')
        if total + len(t) > PRIOR_TESTS_CHAR_BUDGET:
            remaining = PRIOR_TESTS_CHAR_BUDGET - total
            if remaining > 200:  # keep a little headroom so we don't cut mid-line too aggressively
                t = t[:remaining] + "\n# ... (truncated)\n"
                texts.append(t)
            break
        texts.append(t)
        total += len(t)
    if not texts:
        return "None"
    return "\n\n".join(texts)

def main():
    # Pre-flight checks
    if not SOL_PATH.exists():
        raise SystemExit(f"Solution not found: {SOL_PATH}")
    if not ENTRY_POINT or not isinstance(ENTRY_POINT, str):
        raise SystemExit("Please set ENTRY_POINT (function name) at top of script.")
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY not set in environment.")

    try:
        import coverage  # noqa: F401
    except Exception:
        raise SystemExit("Please `pip install coverage pytest` before running this script.")

    task_id, _pkg_entry_point, prompt = get_humaneval_spec(PROBLEM_ID)
    system_msg = (
        "You are a senior test engineer. Read prior tests and avoid duplicates. "
        "Target missing branches, exception paths, short-circuit logic, and boundary cases."
    )
    prior_hint = "None"

    # Build static preamble once
    preamble = build_test_preamble(ENTRY_POINT)

    for i in range(1, ITERATIONS + 1):
        # Gather prior tests text (memory for the LLM)
        prior_tests = collect_prior_tests_text(i)

        # Ask LLM for tests
        user_msg = PROMPT_TEMPLATE.format(
            task_id=task_id,
            entry_point=ENTRY_POINT,
            prompt=prompt,
            coverage_hint=prior_hint,
            prior_tests=prior_tests
        )
        print(f"[iter {i:02d}] Requesting tests from {MODEL} ...", flush=True)
        llm_tests = call_chatgpt(MODEL, system_msg, user_msg)

        # Write test file
        test_path = write_test_file(i, preamble, llm_tests)
        print(f"[iter {i:02d}] Wrote {test_path}", flush=True)

        # Run coverage -> xml
        xml_out = TESTS_DIR / f"coverage_iter_{i:02d}.xml"
        cov_data = TESTS_DIR / f".coverage_iter_{i:02d}"
        print(f"[iter {i:02d}] Running pytest under coverage ...", flush=True)
        stdout, rc = run_pytest_with_coverage(xml_out, cov_data)
        (TESTS_DIR / f"pytest_output_iter_{i:02d}.log").write_text(stdout, encoding="utf-8")

        # Wait for coverage file (handles slow FS / OneDrive)
        if not wait_for_file(xml_out, timeout_s=3.0):
            raise RuntimeError(f"[iter {i:02d}] coverage XML not written: {xml_out}\nSee log: {TESTS_DIR / f'pytest_output_iter_{i:02d}.log'}")

        # Parse coverage
        line_pct, branch_pct = parse_coverage_xml(xml_out)
        if line_pct is None and branch_pct is None:
            excerpt = "\n".join(stdout.splitlines()[-60:])
            (TESTS_DIR / f"coverage_parse_error_iter_{i:02d}.txt").write_text(excerpt, encoding="utf-8")
            append_results_line(RESULTS_FILE, i, None, None, note=f"{test_path.name} (parse failed)")
            print(f"[iter {i:02d}] WARNING: Could not parse coverage; see {xml_out} and coverage_parse_error_iter_{i:02d}.txt", flush=True)
        else:
            append_results_line(RESULTS_FILE, i, line_pct, branch_pct, note=test_path.name)
            print(f"[iter {i:02d}] Coverage  line%={(line_pct if line_pct is not None else float('nan')):.2f}  branch%={(branch_pct if branch_pct is not None else float('nan')):.2f}", flush=True)

        # Build quick hint for next round (text report) to tell the LLM what's still missing
        env = os.environ.copy()
        env["COVERAGE_FILE"] = str(cov_data)
        rep = subprocess.run(
            [sys.executable, "-m", "coverage", "report", "-m"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT), env=env
        ).stdout

        missing_lines = []
        for line in rep.splitlines():
            if SOL_PATH.name in line and "Missing" in rep:
                missing_lines.append(line)
        prior_hint = "None"
        if missing_lines:
            snippet = "\n".join(missing_lines[:10])
            prior_hint = f"From previous coverage report, Missing lines (subset):\n{snippet}"

    print(f"\nDone. Appended {ITERATIONS} lines to: {RESULTS_FILE}")
    print(f"Tests written to: {TESTS_DIR}")
    print(f"Solution file: {SOL_PATH}")
    print(f"Entry point: {ENTRY_POINT}")

if __name__ == "__main__":
    main()

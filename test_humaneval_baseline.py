#COMMAND LINE PROMPT
# pytest --cov --cov-report=term-missing


from pathlib import Path
import importlib.util

import pytest
from human_eval.data import read_problems


# ----------------------------
# CONFIG — EDIT THIS LIST ONLY
# ----------------------------

# HumanEval problem numbers that you *might* have solutions for.
# Missing files will be silently ignored.
PROBLEM_NUMBERS = [
    0, 1, 10, 11, 12,13,14,15, 101, 102, 103, 104, 105, 106, 107, 108, 109,
    110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 12, 120, 121,
    122, 123, 124, 125, 126, 127, 128, 129, 13, 130, 131
]

# Filenames are assumed to be:
#   humaneval_<PROBLEM>_attempt_001_base.py
# in either of these directories:
#   solutions_correct/openai/
#   generated_solutions/openai/


# ----------------------------
# PATHS + DATA
# ----------------------------

ROOT = Path(__file__).resolve().parent

SEARCH_DIRS = [
    ROOT / "openai_solutions",

]

PROBLEMS = read_problems()


# ----------------------------
# HELPERS
# ----------------------------

def load_module(path: Path):
    """Dynamically import a .py file from an arbitrary path."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore
    return module


def collect_solution_files():
    """
    Build a list of existing base solution files of the form:
      humaneval_<PROBLEM>_attempt_001_base.py
    Only files that actually exist are included.
    """
    found = []

    for problem_id in PROBLEM_NUMBERS:
        fname = f"humaneval_{problem_id}_openai_attempt_001_base.py"
        for d in SEARCH_DIRS:
            fpath = d / fname
            if fpath.exists():
                found.append(fpath)

    return found


SOLUTION_FILES = collect_solution_files()

# Optional: tiny hint in the output if nothing was found
if not SOLUTION_FILES:
    print("[test_humaneval_openai] No matching _base solution files found.")


# ----------------------------
# TEST
# ----------------------------

@pytest.mark.parametrize("solution_path", SOLUTION_FILES, ids=lambda p: p.name)
def test_humaneval_base(solution_path: Path):
    """
    For each ChatGPT _base solution file, run the official HumanEval tests
    for that problem.
    """
    # Extract problem number from filename: humaneval_<N>_attempt_001_base.py
    try:
        problem_id = int(solution_path.name.split("_")[1])
    except (IndexError, ValueError):
        pytest.fail(f"Unexpected filename format: {solution_path.name}")

    key = f"HumanEval/{problem_id}"

    if key not in PROBLEMS:
        pytest.skip(f"HumanEval dataset has no problem {key}")

    problem = PROBLEMS[key]
    entry_name = problem["entry_point"]  # required function name
    test_code = problem["test"]          # Python tests as a string

    module = load_module(solution_path)

    if not hasattr(module, entry_name):
        pytest.fail(f"{solution_path.name} does not define `{entry_name}`")

    func = getattr(module, entry_name)

    # The tests expect to call a function named `entry_name`.
    # Put your function into the globals under that name.
    exec_globals = {entry_name: func}

    # Running the HumanEval tests. Assertion errors inside this code
    # will be caught by pytest as test failures.
    exec(test_code, exec_globals)

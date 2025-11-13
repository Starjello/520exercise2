#!/usr/bin/env python3
"""
Run HumanEval tests against solutions in ./openai_solutions,
count per-assert results, and combine with pytest-cov coverage
information (from coverage.json) into a single summary file.

Workflow:

1) Run pytest with coverage:

   pytest -v ^
     --cov=openai_solutions ^
     --cov-branch ^
     --cov-report=term-missing ^
     --cov-report=json:coverage.json

2) Run this script:

   python humaneval_coverage_summary.py [--dir openai_solutions]

It will:
- Run HumanEval checks directly (not via pytest), counting asserts.
- Load coverage.json.
- Produce humaneval_coverage_summary.txt with columns:

  Name | Stmts | Miss | Branch | BrPart | Br% | Line% | Missing | Tests | Note
"""

from __future__ import annotations
import argparse
import ast
import importlib.util
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from types import FunctionType
from typing import Any, Dict, List, Optional, Tuple

from human_eval.data import read_problems

DEFAULT_DIR = "openai_solutions"

ROOT = Path(__file__).resolve().parent
COVERAGE_JSON_PATH = ROOT / "coverage.json"
OUT_PATH = ROOT / "humaneval_coverage_summary.txt"


# ---------- silence helper ----------
@contextmanager
def quiet_io():
    old_out, old_err = sys.stdout, sys.stderr
    devnull = open(os.devnull, "w")
    try:
        sys.stdout = sys.stderr = devnull
        yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err
        devnull.close()


# ---------- loading ----------
def load_module(path: Path):
    """Load a module in a way coverage.py can trace."""
    import runpy
    globals_dict = runpy.run_path(str(path))
    class Simple:
        pass
    mod = Simple()
    for k, v in globals_dict.items():
        setattr(mod, k, v)
    return mod

def discover_solution_files(root: Path) -> List[Path]:
    return sorted(
        p for p in root.glob("humaneval_*_openai_attempt_001_base.py") if p.is_file()
    )


# ---------- instrument asserts in check(candidate) ----------
class _AssertRecorder(ast.NodeTransformer):
    def visit_Assert(self, node: ast.Assert):
        test_expr = node.test
        msg_expr = node.msg if node.msg is not None else ast.Constant(value=None)
        call = ast.Call(
            func=ast.Name(id="__rec", ctx=ast.Load()),
            args=[test_expr, msg_expr, ast.Constant(value=node.lineno)],
            keywords=[],
        )
        return ast.Expr(value=call)


class _CheckOnly(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        is_check = node.name == "check" and any(
            arg.arg == "candidate" for arg in node.args.args
        )
        if is_check:
            node = _AssertRecorder().visit(node)
            ast.fix_missing_locations(node)
        return node


def _instrument_test_code(test_code: str) -> ast.AST:
    tree = ast.parse(test_code, mode="exec")
    tree = _CheckOnly().visit(tree)
    ast.fix_missing_locations(tree)
    return tree


def run_check_and_count_asserts(candidate_func, test_code: str):
    """
    Returns: total, passed, failed, failures_detail
    failures_detail: list[(lineno, ok, msg)]
    """
    records: List[Tuple[int, bool, Optional[str]]] = []

    def __rec(test_value, msg, lineno):
        ok = bool(test_value)
        records.append((lineno, ok, str(msg) if msg is not None else None))

    env: Dict[str, object] = {"__rec": __rec}

    # silence while compiling/executing the instrumented test module
    try:
        compiled = compile(
            _instrument_test_code(test_code),
            filename="<humaneval_test>",
            mode="exec",
        )
        with quiet_io():
            exec(compiled, env, env)
    except Exception as e:
        return 0, 0, 1, [(0, False, f"Test import error: {type(e).__name__}: {e}")]

    if "check" not in env or not isinstance(env["check"], FunctionType):
        return 0, 0, 1, [(0, False, "Missing check(candidate) in test")]

    # silence while running check(candidate)
    try:
        with quiet_io():
            env["check"](candidate_func)
    except Exception as e:
        records.append((0, False, f"Runtime error: {type(e).__name__}: {e}"))

    total = sum(1 for _, ok, _ in records if isinstance(ok, bool))
    passed = sum(1 for _, ok, _ in records if ok)
    failed = sum(1 for _, ok, _ in records if ok is False)
    failures_detail = [(ln, ok, msg) for (ln, ok, msg) in records if ok is False]
    return total, passed, failed, failures_detail


# ---------- coverage helpers ----------
def load_coverage() -> Dict[str, Any]:
    if not COVERAGE_JSON_PATH.exists():
        raise FileNotFoundError(
            f"{COVERAGE_JSON_PATH} not found. "
            "Did you run pytest with `--cov-report=json:coverage.json`?"
        )
    import json

    with COVERAGE_JSON_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_file_entry(
    cov_data: Dict[str, Any], solution_path: Path
) -> Tuple[str, Dict[str, Any]]:
    """
    Find the coverage entry corresponding to a given solution file.

    We match by suffix (filename or 'openai_solutions/<filename>') to be
    robust to absolute/relative paths in coverage.json.
    """
    files = cov_data.get("files", {})
    norm_target1 = solution_path.name.replace("\\", "/")
    norm_target2 = f"{DEFAULT_DIR}/{solution_path.name}".replace("\\", "/")

    best_path = ""
    best_entry: Dict[str, Any] = {}

    for path, entry in files.items():
        norm_path = path.replace("\\", "/")
        if norm_path.endswith(norm_target2) or norm_path.endswith(norm_target1):
            best_path = path
            best_entry = entry
            break

    return best_path, best_entry


def summarize_pytest_cov_style(
    entry: Dict[str, Any],
) -> Tuple[int, int, int, int, float, float, List[int]]:
    """
    Given a coverage.json 'file' entry, return:

        (stmts, miss, branch, brpart, line_percent, branch_percent, missing_lines)
    """
    if not entry:
        return 0, 0, 0, 0, 0.0, 0.0, []

    summary = entry.get("summary", {})
    stmts = int(summary.get("num_statements", 0))
    covered_lines = int(summary.get("covered_lines", 0))
    miss = max(stmts - covered_lines, 0)

    missing_lines = sorted(entry.get("missing_lines", []))

    num_branches = int(summary.get("num_branches", 0))
    covered_branches = int(summary.get("covered_branches", 0))
    missing_branches = entry.get("missing_branches", [])
    brpart = len(missing_branches) if missing_branches is not None else 0

    line_percent = (covered_lines / stmts * 100.0) if stmts > 0 else 0.0
    branch_percent = (
        covered_branches / num_branches * 100.0 if num_branches > 0 else 0.0
    )

    return stmts, miss, num_branches, brpart, line_percent, branch_percent, missing_lines


def compress_line_ranges(lines: List[int]) -> str:
    """
    Given a sorted list of line numbers, compress into pytest-cov-like
    range string, e.g.:

        [2, 3, 4, 7, 8, 10] -> "2-4, 7-8, 10"
    """
    if not lines:
        return ""

    ranges = []
    start = prev = lines[0]

    for ln in lines[1:]:
        if ln == prev + 1:
            prev = ln
        else:
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            start = prev = ln

    if start == prev:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{prev}")

    return ", ".join(ranges)


def interpret_result(
    tests_passed: int,
    tests_total: int,
    line_pct: float,
    branch_count: int,
    brpart: int,
) -> str:
    """
    Heuristic one-liner explaining the situation for a problem.
    """

    if tests_total == 0:
        return "No HumanEval test cases executed."

    if tests_passed < tests_total:
        if line_pct < 50:
            return (
                "Many HumanEval cases failing with low line coverage – "
                "implementation likely incomplete."
            )
        else:
            return (
                "Some HumanEval cases failing despite decent coverage – "
                "check edge cases and logic."
            )

    # All test cases passed
    if branch_count == 0:
        if line_pct >= 90:
            return "All HumanEval cases passed with high line coverage (no branch data)."
        else:
            return "All HumanEval cases passed but some lines remain untested (no branch data)."

    # We have branch info
    if brpart > 0 and line_pct >= 90:
        return (
            "All HumanEval cases passed with high line coverage, "
            "but some branches are only partially tested."
        )
    elif brpart > 0:
        return "All HumanEval cases passed; consider more tests to improve branch coverage."
    else:
        return "All HumanEval cases passed with strong line and branch coverage."


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(
        description="Run HumanEval tests on local solution files and combine with coverage.json."
    )
    ap.add_argument(
        "--dir",
        default=DEFAULT_DIR,
        help="Directory containing humaneval_* solution files (default: openai_solutions)",
    )
    args = ap.parse_args()

    sol_dir = Path(args.dir).resolve()
    files = discover_solution_files(sol_dir)

    if not files:
        print(f"[runner] No solution files found in {sol_dir}")
        print("         Expected filenames like: humaneval_0_openai_attempt_001_base.py")
        return

    problems = read_problems()

    # Load coverage once
    try:
        cov_data = load_coverage()
    except FileNotFoundError as e:
        print(e)
        print("Continuing WITHOUT coverage data (coverage columns will be zeroed).")
        cov_data = {"files": {}}

    print(f"Found {len(files)} solution files in: {sol_dir}\n")
    grand_total = grand_pass = grand_fail = 0

    # For printing quick per-problem HumanEval summary
    print(f"{'Problem':>7}  {'File':<50}  {'Asserts (P/T)':>15}  {'Status':>8}")
    print("-" * 88)

    # For final combined coverage summary table
    rows: List[Dict[str, Any]] = []

    for sol in files:
        try:
            problem_id = int(sol.name.split("_")[1])
        except Exception:
            print(
                f"{'???????':>7}  {sol.name:<50}  {'-':>15}  {'SKIP':>8}  (bad filename)"
            )
            continue

        key = f"HumanEval/{problem_id}"
        if key not in problems:
            print(
                f"{problem_id:>7}  {sol.name:<50}  {'-':>15}  {'SKIP':>8}  (not in dataset)"
            )
            continue

        entry_name = problems[key]["entry_point"]
        test_code = problems[key]["test"]

        # Try to import module
        try:
            mod = load_module(sol)
        except Exception as e:
            print(
                f"{problem_id:>7}  {sol.name:<50}  {'-':>15}  {'ERROR':>8}  (load: {type(e).__name__})"
            )
            grand_fail += 1
            # Still include in rows with zero tests and zero coverage
            rows.append(
                {
                    "name": str(sol),
                    "stmts": 0,
                    "miss": 0,
                    "branch": 0,
                    "brpart": 0,
                    "cover_pct": 0.0,
                    "branch_pct": 0.0,
                    "missing": "",
                    "tests": "0/0",
                    "note": f"Module import error: {type(e).__name__}",
                }
            )
            continue

        if not hasattr(mod, entry_name):
            print(
                f"{problem_id:>7}  {sol.name:<50}  {'0/0':>15}  {'FAIL':>8}  (missing `{entry_name}`)"
            )
            grand_fail += 1
            cov_path, cov_entry = find_file_entry(cov_data, sol)
            (
                stmts,
                miss,
                branch,
                brpart,
                cover_pct,
                branch_pct,
                missing_lines,
            ) = summarize_pytest_cov_style(cov_entry)
            missing_str = compress_line_ranges(missing_lines)
            note = "Missing required entry_point function in solution."
            rows.append(
                {
                    "name": cov_path if cov_path else str(sol),
                    "stmts": stmts,
                    "miss": miss,
                    "branch": branch,
                    "brpart": brpart,
                    "cover_pct": cover_pct,
                    "branch_pct": branch_pct,
                    "missing": missing_str,
                    "tests": "0/0",
                    "note": note,
                }
            )
            continue

        candidate = getattr(mod, entry_name)
        total, passed, failed, _ = run_check_and_count_asserts(candidate, test_code)
        status = "PASS" if failed == 0 and total > 0 else "FAIL"

        print(
            f"{problem_id:>7}  {sol.name:<50}  {f'{passed}/{total}':>15}  {status:>8}"
        )

        grand_total += 1
        grand_pass += int(status == "PASS")
        grand_fail += int(status == "FAIL")

        cov_path, cov_entry = find_file_entry(cov_data, sol)
        (
            stmts,
            miss,
            branch,
            brpart,
            cover_pct,
            branch_pct,
            missing_lines,
        ) = summarize_pytest_cov_style(cov_entry)
        missing_str = compress_line_ranges(missing_lines)
        note = interpret_result(
            tests_passed=passed,
            tests_total=total,
            line_pct=cover_pct,
            branch_count=branch,
            brpart=brpart,
        )

        rows.append(
            {
                "name": cov_path if cov_path else str(sol),
                "stmts": stmts,
                "miss": miss,
                "branch": branch,
                "brpart": brpart,
                "cover_pct": cover_pct,
                "branch_pct": branch_pct,
                "missing": missing_str,
                "tests": f"{passed}/{total}",
                "note": note,
            }
        )

    print("\n=== HUMAN-EVAL SUMMARY ===")
    print(f"Problems tested : {grand_total}")
    print(f"Problem PASS    : {grand_pass}")
    print(f"Problem FAIL    : {grand_fail}")
    if grand_total:
        print(f"Success rate    : {grand_pass / grand_total * 100:.1f}%")

    # ---------- build combined coverage summary table ----------
    if not rows:
        print("\nNo rows to summarize (no solutions or tests?).")
        return

    # Column widths (pytest-cov style + extra columns)
    name_w = max(len("Name"), max(len(r["name"]) for r in rows))
    stmts_w = max(len("Stmts"), max(len(str(r["stmts"])) for r in rows))
    miss_w = max(len("Miss"), max(len(str(r["miss"])) for r in rows))
    branch_w = max(len("Branch"), max(len(str(r["branch"])) for r in rows))
    brpart_w = max(len("BrPart"), max(len(str(r["brpart"])) for r in rows))
    brpct_w = max(len("Br%"), max(len(f"{r['branch_pct']:.1f}%") for r in rows))
    cover_w = max(len("Line%"), max(len(f"{r['cover_pct']:.1f}%") for r in rows))
    missing_w = max(len("Missing"), max(len(r["missing"]) for r in rows))
    tests_w = max(len("Tests"), max(len(r["tests"]) for r in rows))

    header = (
        f"{'Name'.ljust(name_w)}  "
        f"{'Stmts'.rjust(stmts_w)}  "
        f"{'Miss'.rjust(miss_w)}  "
        f"{'Branch'.rjust(branch_w)}  "
        f"{'BrPart'.rjust(brpart_w)}  "
        f"{'Br%'.rjust(brpct_w)}  "
        f"{'Line%'.rjust(cover_w)}  "
        f"{'Missing'.ljust(missing_w)}  "
        f"{'Tests'.rjust(tests_w)}  "
        f"Note"
    )
    sep = "-" * len(header)

    lines = [header, sep]
    for r in rows:
        branch_pct_str = f"{r['branch_pct']:.1f}%" if r["branch"] > 0 else "N/A"
        line_pct_str = f"{r['cover_pct']:.1f}%" if r["stmts"] > 0 else "0%"
        line = (
            f"{r['name'].ljust(name_w)}  "
            f"{str(r['stmts']).rjust(stmts_w)}  "
            f"{str(r['miss']).rjust(miss_w)}  "
            f"{str(r['branch']).rjust(branch_w)}  "
            f"{str(r['brpart']).rjust(brpart_w)}  "
            f"{branch_pct_str.rjust(brpct_w)}  "
            f"{line_pct_str.rjust(cover_w)}  "
            f"{r['missing'].ljust(missing_w)}  "
            f"{r['tests'].rjust(tests_w)}  "
            f"{r['note']}"
        )
        lines.append(line)

    table_text = "\n".join(lines)

    print("\n=== COMBINED COVERAGE + TEST SUMMARY ===")
    print(table_text)

    with OUT_PATH.open("w", encoding="utf-8") as f:
        f.write(table_text)
        f.write("\n")

    print(f"\n[summary] Wrote combined summary to {OUT_PATH}")


if __name__ == "__main__":
    main()

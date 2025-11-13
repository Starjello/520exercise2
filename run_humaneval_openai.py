#!/usr/bin/env python3
"""
Run HumanEval tests against solutions in ./openai_solutions,
with per-assert counts and fully silenced stdout/stderr from:
- solution import
- test code execution
- check(candidate) execution
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
from typing import Dict, List, Optional, Tuple

from human_eval.data import read_problems

DEFAULT_DIR = "openai_solutions"

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
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # silence prints during module import (top-level code in solution files)
    with quiet_io():
        spec.loader.exec_module(module)  # type: ignore
    return module

def discover_solution_files(root: Path) -> List[Path]:
    return sorted(p for p in root.glob("humaneval_*_openai_attempt_001_base.py") if p.is_file())

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
        is_check = node.name == "check" and any(arg.arg == "candidate" for arg in node.args.args)
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
    records: List[Tuple[int, bool, Optional[str]]] = []

    def __rec(test_value, msg, lineno):
        ok = bool(test_value)
        records.append((lineno, ok, str(msg) if msg is not None else None))

    env: Dict[str, object] = {"__rec": __rec}

    # silence while compiling/executing the instrumented test module
    try:
        compiled = compile(_instrument_test_code(test_code), filename="<humaneval_test>", mode="exec")
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

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description="Run HumanEval tests on local solution files.")
    ap.add_argument("--dir", default=DEFAULT_DIR, help="Directory containing humaneval_* solution files (default: openai_solutions)")
    args = ap.parse_args()

    sol_dir = Path(args.dir).resolve()
    files = discover_solution_files(sol_dir)

    if not files:
        print(f"[runner] No solution files found in {sol_dir}")
        print("         Expected filenames like: humaneval_0_openai_attempt_001_base.py")
        return

    problems = read_problems()

    print(f"Found {len(files)} solution files in: {sol_dir}\n")
    grand_total = grand_pass = grand_fail = 0
    print(f"{'Problem':>7}  {'File':<50}  {'Asserts (P/T)':>15}  {'Status':>8}")
    print("-" * 88)

    for sol in files:
        try:
            problem_id = int(sol.name.split("_")[1])
        except Exception:
            print(f"{'???????':>7}  {sol.name:<50}  {'-':>15}  {'SKIP':>8}  (bad filename)")
            continue

        key = f"HumanEval/{problem_id}"
        if key not in problems:
            print(f"{problem_id:>7}  {sol.name:<50}  {'-':>15}  {'SKIP':>8}  (not in dataset)")
            continue

        entry = problems[key]["entry_point"]
        test_code = problems[key]["test"]

        try:
            mod = load_module(sol)
        except Exception as e:
            print(f"{problem_id:>7}  {sol.name:<50}  {'-':>15}  {'ERROR':>8}  (load: {type(e).__name__})")
            grand_fail += 1
            continue

        if not hasattr(mod, entry):
            print(f"{problem_id:>7}  {sol.name:<50}  {'0/0':>15}  {'FAIL':>8}  (missing `{entry}`)")
            grand_fail += 1
            continue

        candidate = getattr(mod, entry)
        total, passed, failed, _ = run_check_and_count_asserts(candidate, test_code)
        status = "PASS" if failed == 0 and total > 0 else "FAIL"

        print(f"{problem_id:>7}  {sol.name:<50}  {f'{passed}/{total}':>15}  {status:>8}")
        grand_total += 1
        grand_pass += int(status == "PASS")
        grand_fail += int(status == "FAIL")

    print("\n=== SUMMARY ===")
    print(f"Problems tested : {grand_total}")
    print(f"Problem PASS    : {grand_pass}")
    print(f"Problem FAIL    : {grand_fail}")
    if grand_total:
        print(f"Success rate    : {grand_pass / grand_total * 100:.1f}%")

if __name__ == "__main__":
    main()

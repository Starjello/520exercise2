#!/usr/bin/env python3
"""
Generate a per-problem summary table for HumanEval runs based on:

- humaneval_test_stats.json (from pytest hook)
- coverage.json (from pytest-cov)

Columns:
  Name | Stmts | Miss | Branch | BrPart | Br% | Line% | Missing | Tests | Note
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "humaneval_coverage_summary.txt"

TEST_STATS_PATH = ROOT / "humaneval_test_stats.json"
COVERAGE_JSON_PATH = ROOT / "coverage.json"


def load_test_stats() -> Dict[int, Dict[str, int]]:
    if not TEST_STATS_PATH.exists():
        raise FileNotFoundError(
            f"{TEST_STATS_PATH} not found. "
            "Did you run pytest first so test_humaneval_baseline.py could produce it?"
        )
    with TEST_STATS_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    parsed: Dict[int, Dict[str, int]] = {}
    for pid_str, stats in raw.items():
        try:
            pid = int(pid_str)
        except ValueError:
            continue
        parsed[pid] = {
            "total": int(stats.get("total", 0)),
            "passed": int(stats.get("passed", 0)),
            "failed": int(stats.get("failed", 0)),
        }
    return parsed


def load_coverage() -> Dict[str, Any]:
    if not COVERAGE_JSON_PATH.exists():
        raise FileNotFoundError(
            f"{COVERAGE_JSON_PATH} not found. "
            "Did you run pytest with `--cov-report=json:coverage.json`?"
        )
    with COVERAGE_JSON_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_file_entry(cov_data: Dict[str, Any], filename_suffix: str) -> Tuple[str, Dict[str, Any]]:
    files = cov_data.get("files", {})
    norm_suffix = filename_suffix.replace("\\", "/")
    for path, entry in files.items():
        if path.replace("\\", "/").endswith(norm_suffix):
            return path, entry
    return "", {}


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

    # Missing line numbers
    missing_lines = sorted(entry.get("missing_lines", []))

    # Branch data
    num_branches = int(summary.get("num_branches", 0))
    missing_branches = entry.get("missing_branches", []) or []
    brpart = len(missing_branches)

    # Line coverage %
    line_percent = (covered_lines / stmts * 100.0) if stmts > 0 else 0.0

    # Branch coverage %: covered = total - missing
    covered_branches = num_branches - brpart
    branch_percent = (
        covered_branches / num_branches * 100.0 if num_branches > 0 else 0.0
    )

    return stmts, miss, num_branches, brpart, line_percent, branch_percent, missing_lines


def compress_line_ranges(lines: List[int]) -> str:
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
    if tests_total == 0:
        return "No HumanEval test cases executed."

    if tests_passed < tests_total:
        if line_pct < 50:
            return "Many HumanEval cases failing with low line coverage – implementation likely incomplete."
        else:
            return "Some HumanEval cases failing despite decent coverage – check edge cases and logic."

    if branch_count == 0:
        if line_pct >= 90:
            return "All HumanEval cases passed with high line coverage (no branch data)."
        else:
            return "All HumanEval cases passed but some lines remain untested (no branch data)."

    if brpart > 0 and line_pct >= 90:
        return "All HumanEval cases passed with high line coverage, but some branches are only partially tested."
    elif brpart > 0:
        return "All HumanEval cases passed; consider more tests to improve branch coverage."
    else:
        return "All HumanEval cases passed with strong line and branch coverage."


def main():
    test_stats = load_test_stats()
    cov_data = load_coverage()

    problem_ids = sorted(test_stats.keys())
    rows: List[Dict[str, Any]] = []

    for pid in problem_ids:
        stats = test_stats[pid]
        total = stats["total"]
        passed = stats["passed"]

        fname = f"humaneval_{pid}_openai_attempt_001_base.py"
        path, entry = find_file_entry(cov_data, fname)

        (
            stmts,
            miss,
            branch,
            brpart,
            line_pct,
            branch_pct,
            missing_lines,
        ) = summarize_pytest_cov_style(entry)
        missing_str = compress_line_ranges(missing_lines)
        note = interpret_result(
            tests_passed=passed,
            tests_total=total,
            line_pct=line_pct,
            branch_count=branch,
            brpart=brpart,
        )

        rows.append(
            {
                "name": path if path else fname,
                "stmts": stmts,
                "miss": miss,
                "branch": branch,
                "brpart": brpart,
                "line_pct": line_pct,
                "branch_pct": branch_pct,
                "missing": missing_str,
                "tests": f"{passed}/{total}",
                "note": note,
            }
        )

    if not rows:
        print("No problems found in stats.")
        return

    # Column widths
    name_w = max(len("Name"), max(len(r["name"]) for r in rows))
    stmts_w = max(len("Stmts"), max(len(str(r["stmts"])) for r in rows))
    miss_w = max(len("Miss"), max(len(str(r["miss"])) for r in rows))
    branch_w = max(len("Branch"), max(len(str(r["branch"])) for r in rows))
    brpart_w = max(len("BrPart"), max(len(str(r["brpart"])) for r in rows))
    brpct_w = max(len("Br%"), max(len(f"{r['branch_pct']:.1f}%") for r in rows))
    cover_w = max(len("Line%"), max(len(f"{r['line_pct']:.1f}%") for r in rows))
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
        br_str = f"{r['branch_pct']:.1f}%" if r["branch"] > 0 else "0%"
        ln_str = f"{r['line_pct']:.1f}%" if r["stmts"] > 0 else "0%"
        line = (
            f"{r['name'].ljust(name_w)}  "
            f"{str(r['stmts']).rjust(stmts_w)}  "
            f"{str(r['miss']).rjust(miss_w)}  "
            f"{str(r['branch']).rjust(branch_w)}  "
            f"{str(r['brpart']).rjust(brpart_w)}  "
            f"{br_str.rjust(brpct_w)}  "
            f"{ln_str.rjust(cover_w)}  "
            f"{r['missing'].ljust(missing_w)}  "
            f"{r['tests'].rjust(tests_w)}  "
            f"{r['note']}"
        )
        lines.append(line)

    table_text = "\n".join(lines)
    print(table_text)

    with OUT_PATH.open("w", encoding="utf-8") as f:
        f.write(table_text)
        f.write("\n")

    print(f"\n[generate_summary] Wrote combined summary to {OUT_PATH}")


if __name__ == "__main__":
    main()

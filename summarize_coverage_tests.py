#!/usr/bin/env python3
"""
Summarize all coverage_iter_XX.xml files into a simple text table.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

PROBLEM_ID = 106
ROOT = Path(__file__).resolve().parent
TESTS_DIR = ROOT / "tests" / f"problem_{PROBLEM_ID}"

rows = []

for xml_file in sorted(TESTS_DIR.glob("coverage_iter_*.xml")):
    try:
        root = ET.parse(xml_file).getroot()
        line_rate = float(root.attrib.get("line-rate", 0)) * 100
        branch_rate = float(root.attrib.get("branch-rate", 0)) * 100
        iter_num = xml_file.stem.split("_")[-1]
        rows.append((iter_num, line_rate, branch_rate))
    except Exception as e:
        print(f"⚠️  Could not read {xml_file.name}: {e}")

# Print header
print(f"{'Iter':<5} {'Line %':>8} {'Branch %':>10}")
print("-" * 26)
for iter_num, line_rate, branch_rate in rows:
    print(f"{iter_num:<5} {line_rate:8.2f} {branch_rate:10.2f}")

import csv

csv_path = ROOT / "results" / f"problem_{PROBLEM_ID}_coverage_summary.csv"
csv_path.parent.mkdir(parents=True, exist_ok=True)
with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Iteration", "Line %", "Branch %"])
    writer.writerows(rows)

print(f"\n✅ Saved summary to {csv_path}")

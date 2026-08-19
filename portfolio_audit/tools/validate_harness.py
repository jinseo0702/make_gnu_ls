#!/usr/bin/env python3
"""Mutation checks proving that semantic comparators reject bad outputs."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("run_baseline", HERE / "run_baseline.py")
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def process(stdout: bytes, stderr: bytes = b"", returncode: int = 0) -> dict:
    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
        "timed_out": False,
    }


def main() -> int:
    checks = []

    oracle_names = process(b"alpha\nbeta\ngamma\n")
    for check_id, mutated, defect in (
        ("H01", b"alpha  gamma  \n", "missing entry"),
        ("H02", b"alpha  beta  extra  gamma  \n", "extra entry"),
        ("H03", b"beta  alpha  gamma  \n", "wrong order"),
    ):
        result = runner.evaluate_names(process(mutated), oracle_names, {})
        checks.append({"id": check_id, "defect": defect, "classification": result["classification"], "detected": result["classification"] != "PASS"})

    target_long = b"total 4\n-rw-r--r-- 1 user group 99 Aug 19 12:00 item \n"
    oracle_long = b"total 4\n-rw-r--r-- 1 user group 10 Aug 19 12:00 item\n"
    result = runner.evaluate_long(process(target_long), process(oracle_long), {})
    checks.append({"id": "H04", "defect": "wrong size metadata", "classification": result["classification"], "detected": result["classification"] != "PASS"})

    result = runner.evaluate_error(process(b"", b"diagnostic\n", 0), process(b"", b"diagnostic\n", 2), {})
    checks.append({"id": "H05", "defect": "wrong success exit status on error", "classification": result["classification"], "detected": result["classification"] != "PASS"})

    report = {
        "check_count": len(checks),
        "detected_count": sum(item["detected"] for item in checks),
        "checks": checks,
    }
    output = HERE.parent / "harness_validation.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["detected_count"] == report["check_count"] else 1


if __name__ == "__main__":
    sys.exit(main())

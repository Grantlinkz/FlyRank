#!/usr/bin/env python
"""
FlyRank LLM Triage Evaluation Benchmark Runner
Milestone W6: Put an LLM behind your API

Executes test cases in evals/cases.json against the triage system,
evaluates responses against expected labels/constraints,
and prints a comprehensive performance and accuracy report.
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Fix Windows console encoding for UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.llm.schema import TaskTriageRequest, TaskTriageResponse
from src.llm.service import triage_task

CASES_FILE = Path(__file__).resolve().parent / "cases.json"


def load_test_cases() -> List[Dict[str, Any]]:
    if not CASES_FILE.exists():
        print(f"❌ Cases file not found: {CASES_FILE}")
        sys.exit(1)
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_case(case: Dict[str, Any], result: TaskTriageResponse) -> Tuple[bool, List[str]]:
    expected = case.get("expected", {})
    failures = []

    # 1. Category check
    if "category" in expected:
        if result.category.value != expected["category"]:
            failures.append(f"Category mismatch: expected '{expected['category']}', got '{result.category.value}'")
    elif "category_options" in expected:
        if result.category.value not in expected["category_options"]:
            failures.append(f"Category mismatch: expected one of {expected['category_options']}, got '{result.category.value}'")

    # 2. Urgency check
    if "urgency" in expected:
        if result.urgency.value != expected["urgency"]:
            failures.append(f"Urgency mismatch: expected '{expected['urgency']}', got '{result.urgency.value}'")
    elif "urgency_options" in expected:
        if result.urgency.value not in expected["urgency_options"]:
            failures.append(f"Urgency mismatch: expected one of {expected['urgency_options']}, got '{result.urgency.value}'")

    # 3. Confidence bounds
    if "min_confidence" in expected:
        if result.confidence < expected["min_confidence"]:
            failures.append(f"Confidence too low: expected >= {expected['min_confidence']}, got {result.confidence}")
    if "max_confidence" in expected:
        if result.confidence > expected["max_confidence"]:
            failures.append(f"Confidence too high: expected <= {expected['max_confidence']}, got {result.confidence}")

    passed = len(failures) == 0
    return passed, failures


def run_benchmark(stub_mode: bool = False, verbose: bool = True) -> int:
    cases = load_test_cases()
    total_cases = len(cases)
    passed_cases = 0
    total_duration_ms = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    repaired_count = 0

    print("=" * 90)
    print(f"🚀 FlyRank LLM Task Triage Benchmark Suite ({total_cases} test cases)")
    print(f"⚙️  Mode: {'STUB FIXTURE' if stub_mode else 'LIVE MODEL (OpenRouter / Provider)'}")
    print("=" * 90)

    results_table = []

    for case in cases:
        case_id = case["id"]
        name = case["name"]
        inp = case["input"]

        req = TaskTriageRequest(title=inp["title"], context=inp.get("context"))
        start_time = time.perf_counter()

        try:
            res, telemetry = triage_task(req, stub=stub_mode)
            passed, failure_reasons = evaluate_case(case, res)
            status_symbol = "✅ PASS" if passed else "❌ FAIL"
            if passed:
                passed_cases += 1

            total_duration_ms += telemetry.duration_ms
            total_input_tokens += telemetry.input_tokens or 0
            total_output_tokens += telemetry.output_tokens or 0
            if telemetry.repaired:
                repaired_count += 1

            results_table.append({
                "id": case_id,
                "name": name,
                "status": status_symbol,
                "category": res.category.value,
                "urgency": res.urgency.value,
                "effort": res.estimated_effort.value,
                "confidence": round(res.confidence, 2),
                "duration_ms": telemetry.duration_ms,
                "tokens": f"{telemetry.input_tokens}/{telemetry.output_tokens}",
                "repaired": "YES" if telemetry.repaired else "no",
                "failures": failure_reasons,
                "reason": res.reason,
            })

        except Exception as e:
            results_table.append({
                "id": case_id,
                "name": name,
                "status": "💥 ERROR",
                "category": "-",
                "urgency": "-",
                "effort": "-",
                "confidence": 0.0,
                "duration_ms": 0.0,
                "tokens": "0/0",
                "repaired": "no",
                "failures": [f"Execution exception: {str(e)}"],
                "reason": str(e),
            })

    # Display Report
    print(f"\n{'ID':<4} {'Status':<8} {'Name':<35} {'Category':<15} {'Urgency':<10} {'Conf':<6} {'Tokens':<10} {'Latency'}")
    print("-" * 105)

    for row in results_table:
        print(f"{row['id']:<4} {row['status']:<8} {row['name']:<35} {row['category']:<15} {row['urgency']:<10} {row['confidence']:<6.2f} {row['tokens']:<10} {row['duration_ms']}ms")
        if row["failures"] and verbose:
            for f in row["failures"]:
                print(f"     ↳ ⚠️  {f}")
        if verbose:
            print(f"     ↳ 💬 Reason: {row['reason']}")

    print("=" * 90)
    score_pct = (passed_cases / total_cases) * 100
    print(f"📊 Final Results: {passed_cases}/{total_cases} Passed ({score_pct:.1f}%)")
    print(f"⏱️  Total Duration: {total_duration_ms:.1f}ms | Avg Latency: {(total_duration_ms / total_cases):.1f}ms")
    print(f"🪙  Total Tokens: {total_input_tokens} In / {total_output_tokens} Out (Sum: {total_input_tokens + total_output_tokens})")
    print(f"🛠️  Repair Retries: {repaired_count}/{total_cases} cases required repair")
    print("=" * 90)

    return 0 if score_pct >= 75.0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LLM task triage benchmark suite")
    parser.add_argument("--stub", action="store_true", help="Run in zero-cost stub mode")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed explanations")
    args = parser.parse_args()

    sys.exit(run_benchmark(stub_mode=args.stub, verbose=not args.quiet))

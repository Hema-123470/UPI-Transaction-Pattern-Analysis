"""
phase4_testing_docs/run_phase4.py
------------------------------------
Master runner for Phase 4 – Testing, Integration & Documentation.

Steps:
  A – Run Phase 1 tests
  B – Run Phase 2 tests
  C – Run Phase 3 tests
  D – Generate final project report
  E – Print integration summary

Usage:
    python phase4_testing_docs/run_phase4.py
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phase4_testing_docs.final_report import run_final_report


def run_test_suite(module_name: str) -> tuple:
    """Import and run a test module. Returns (total, passed, failed)."""
    import importlib, io
    mod    = importlib.import_module(module_name)
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromModule(mod)
    stream = io.StringIO()          # in-memory stream avoids codec issues
    buf    = unittest.TextTestRunner(verbosity=2, stream=stream).run(suite)
    total  = buf.testsRun
    failed = len(buf.failures) + len(buf.errors)
    passed = total - failed
    return total, passed, failed


def main():
    t0 = time.time()

    print("\n" + "█" * 66)
    print("  UPI TRANSACTION PATTERN ANALYSIS")
    print("  ▶  Phase 4: Testing, Integration & Documentation")
    print("█" * 66)

    results = {}

    # ── Step A: Phase 1 Tests ─────────────────────────────────────────────────
    print("\n" + "─" * 66)
    print("  STEP A – Phase 1 Tests")
    print("─" * 66)
    t, p, f = run_test_suite("phase4_testing_docs.test_phase1")
    results["Phase 1"] = (t, p, f)
    status = "✅ PASS" if f == 0 else f"❌ FAIL ({f} failures)"
    print(f"  Result: {status}  |  {p}/{t} tests passed")

    # ── Step B: Phase 2 Tests ─────────────────────────────────────────────────
    print("\n" + "─" * 66)
    print("  STEP B – Phase 2 Tests")
    print("─" * 66)
    t, p, f = run_test_suite("phase4_testing_docs.test_phase2")
    results["Phase 2"] = (t, p, f)
    status = "✅ PASS" if f == 0 else f"❌ FAIL ({f} failures)"
    print(f"  Result: {status}  |  {p}/{t} tests passed")

    # ── Step C: Phase 3 Tests ─────────────────────────────────────────────────
    print("\n" + "─" * 66)
    print("  STEP C – Phase 3 Tests")
    print("─" * 66)
    t, p, f = run_test_suite("phase4_testing_docs.test_phase3")
    results["Phase 3"] = (t, p, f)
    status = "✅ PASS" if f == 0 else f"❌ FAIL ({f} failures)"
    print(f"  Result: {status}  |  {p}/{t} tests passed")

    # ── Step D: Final Report ──────────────────────────────────────────────────
    print("\n" + "─" * 66)
    print("  STEP D – Generating Final Report")
    print("─" * 66)
    run_final_report()

    # ── Summary ───────────────────────────────────────────────────────────────
    total_tests  = sum(r[0] for r in results.values())
    total_passed = sum(r[1] for r in results.values())
    total_failed = sum(r[2] for r in results.values())
    elapsed = time.time() - t0

    print("\n" + "█" * 66)
    print("  Phase 4 COMPLETE – INTEGRATION SUMMARY")
    print("─" * 66)
    print(f"  {'Suite':<12} {'Tests':>6}  {'Passed':>7}  {'Failed':>7}  {'Status'}")
    print("  " + "─" * 50)
    for suite, (t, p, f) in results.items():
        s = "✅" if f == 0 else "❌"
        print(f"  {suite:<12} {t:>6}  {p:>7}  {f:>7}  {s}")
    print("  " + "─" * 50)
    print(f"  {'TOTAL':<12} {total_tests:>6}  {total_passed:>7}  {total_failed:>7}  "
          f"{'✅ ALL PASS' if total_failed==0 else '❌ FAILURES'}")
    print()
    print(f"  Time elapsed: {elapsed:.1f}s")
    print()
    print("  ALL PROJECT OUTPUTS:")
    print("  ┌─ Phase 1 ────────────────────────────────────────┐")
    print("  │  data/raw/upi_transactions_raw.csv               │")
    print("  │  data/processed/upi_transactions_clean.csv       │")
    print("  │  reports/preprocessing_report.txt                │")
    print("  │  reports/figures/*.png                 (8 charts)│")
    print("  ├─ Phase 2 ────────────────────────────────────────┤")
    print("  │  reports/eda_summary_stats.txt                   │")
    print("  │  reports/eda_category_bank.csv                   │")
    print("  │  reports/eda_bank_summary.csv                    │")
    print("  │  reports/eda_status_analysis.csv                 │")
    print("  │  reports/eda_business_insights.txt               │")
    print("  │  reports/figures/eda/*.png            (14 charts)│")
    print("  ├─ Phase 3 ────────────────────────────────────────┤")
    print("  │  phase3_sql_powerbi/schema.sql                   │")
    print("  │  phase3_sql_powerbi/sql_queries.sql              │")
    print("  │  phase3_sql_powerbi/powerbi_guide.md             │")
    print("  │  reports/sql_results/*.csv            (18 files) │")
    print("  │  data/powerbi/*.csv                   (11 files) │")
    print("  ├─ Phase 4 ────────────────────────────────────────┤")
    print("  │  reports/FINAL_PROJECT_REPORT.txt                │")
    print("  │  README.md                                       │")
    print("  └──────────────────────────────────────────────────┘")
    print("█" * 66 + "\n")

    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    main()

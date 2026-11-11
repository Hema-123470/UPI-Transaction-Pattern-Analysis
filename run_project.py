"""
run_project.py
--------------
ONE COMMAND to run the entire UPI Transaction Pattern Analysis project.

Executes all 4 phases in order:
  Phase 1 → Data Collection & Preprocessing
  Phase 2 → Exploratory Data Analysis
  Phase 3 → SQL Analysis & Power BI Export
  Phase 4 → Testing & Final Report

Usage:
    python run_project.py
"""

import os
import sys
import time

# ── Make sure project root is on the path ────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def banner(title: str) -> None:
    print("\n" + "█" * 66)
    print(f"  {title}")
    print("█" * 66)


def section(title: str) -> None:
    print("\n" + "=" * 66)
    print(f"  {title}")
    print("=" * 66)


def check_dependencies() -> None:
    """Check all required libraries are installed."""
    section("CHECKING DEPENDENCIES")
    required = {
        "pandas"    : "pandas",
        "numpy"     : "numpy",
        "matplotlib": "matplotlib",
        "seaborn"   : "seaborn",
    }
    missing = []
    for display, pkg in required.items():
        try:
            __import__(pkg)
            print(f"  [OK]  {display}")
        except ImportError:
            print(f"  [MISSING]  {display}")
            missing.append(display)

    if missing:
        print(f"\n  Install missing packages with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

    print("\n  All dependencies satisfied.")


# ── Phase 1 ───────────────────────────────────────────────────────────────────
def run_phase1() -> None:
    section("PHASE 1 — Data Collection & Preprocessing")

    from config.settings import DATA_RAW_DIR, RAW_FILE
    from phase1_preprocessing.generate_dataset import generate_dataset
    from phase1_preprocessing.preprocess       import run_pipeline
    from phase1_preprocessing.data_profiler    import run_profiler

    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    # Step A: Generate raw dataset (skip if already exists)
    if os.path.exists(RAW_FILE):
        print(f"\n  [SKIP] Raw dataset already exists: {RAW_FILE}")
    else:
        print("\n  Generating 10,000 UPI transaction records ...")
        import pandas as pd
        df_raw = generate_dataset()
        df_raw.to_csv(RAW_FILE, index=False)
        print(f"  Raw dataset saved -> {RAW_FILE}")

    # Step B: Preprocess
    print("\n  Running preprocessing pipeline ...")
    run_pipeline()

    # Step C: Profile and chart
    print("\n  Generating data profile charts ...")
    run_profiler()

    print("\n  [DONE] Phase 1 complete.")


# ── Phase 2 ───────────────────────────────────────────────────────────────────
def run_phase2() -> None:
    section("PHASE 2 — Exploratory Data Analysis")

    from phase2_eda.eda_loader             import load_clean_data
    from phase2_eda.summary_stats          import run_summary
    from phase2_eda.trend_analysis         import run_trend_analysis
    from phase2_eda.category_bank_analysis import run_category_bank_analysis
    from phase2_eda.status_analysis        import run_status_analysis
    from phase2_eda.insights               import run_insights

    print("\n  Loading cleaned dataset ...")
    df = load_clean_data()
    print(f"  {len(df):,} records loaded.")

    print("\n  Module 1: Summary Statistics ...")
    run_summary(df)

    print("\n  Module 2: Trend Analysis ...")
    run_trend_analysis(df)

    print("\n  Module 3: Category & Bank Analysis ...")
    run_category_bank_analysis(df)

    print("\n  Module 4: Status Analysis ...")
    run_status_analysis(df)

    print("\n  Module 5: Business Insights ...")
    run_insights(df)

    print("\n  [DONE] Phase 2 complete.")


# ── Phase 3 ───────────────────────────────────────────────────────────────────
def run_phase3() -> None:
    section("PHASE 3 — SQL Analysis & Power BI Export")

    from phase3_sql_powerbi.sql_analysis       import run_sql_analysis
    from phase3_sql_powerbi.export_for_powerbi import run_export

    print("\n  Running SQL business analysis ...")
    run_sql_analysis()

    print("\n  Exporting Power BI datasets ...")
    run_export()

    print("\n  [DONE] Phase 3 complete.")


# ── Phase 4 ───────────────────────────────────────────────────────────────────
def run_phase4() -> None:
    section("PHASE 4 — Testing & Documentation")

    import io
    import unittest
    import importlib

    def run_tests(module_name: str, label: str) -> tuple:
        mod    = importlib.import_module(module_name)
        loader = unittest.TestLoader()
        suite  = loader.loadTestsFromModule(mod)
        stream = io.StringIO()
        result = unittest.TextTestRunner(verbosity=0, stream=stream).run(suite)
        total  = result.testsRun
        failed = len(result.failures) + len(result.errors)
        passed = total - failed
        status = "PASS" if failed == 0 else f"FAIL ({failed} failures)"
        print(f"  {label:<20} {passed:>3}/{total:>3} tests  [{status}]")
        return total, passed, failed

    print()
    t1, p1, f1 = run_tests("phase4_testing_docs.test_phase1", "Phase 1 Tests")
    t2, p2, f2 = run_tests("phase4_testing_docs.test_phase2", "Phase 2 Tests")
    t3, p3, f3 = run_tests("phase4_testing_docs.test_phase3", "Phase 3 Tests")

    total_t = t1 + t2 + t3
    total_p = p1 + p2 + p3
    total_f = f1 + f2 + f3

    print(f"  {'─'*40}")
    print(f"  {'TOTAL':<20} {total_p:>3}/{total_t:>3} tests  "
          f"[{'ALL PASS' if total_f == 0 else str(total_f)+' FAILURES'}]")

    print("\n  Generating final project report ...")
    from phase4_testing_docs.final_report import run_final_report
    run_final_report()

    print("\n  [DONE] Phase 4 complete.")
    return total_f


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    t_start = time.time()

    banner("UPI TRANSACTION PATTERN ANALYSIS  —  FULL PROJECT RUN")
    print("  Running all 4 phases automatically ...")

    check_dependencies()

    # ── Run all phases ────────────────────────────────────────────────────────
    t1 = time.time(); run_phase1(); e1 = round(time.time()-t1, 1)
    t2 = time.time(); run_phase2(); e2 = round(time.time()-t2, 1)
    t3 = time.time(); run_phase3(); e3 = round(time.time()-t3, 1)
    t4 = time.time(); test_failures = run_phase4(); e4 = round(time.time()-t4, 1)

    total_time = round(time.time() - t_start, 1)

    # ── Final summary ─────────────────────────────────────────────────────────
    banner("PROJECT COMPLETE — FINAL SUMMARY")
    print(f"""
  Phase 1  Data Collection & Preprocessing    {e1:>5}s
  Phase 2  Exploratory Data Analysis          {e2:>5}s
  Phase 3  SQL Analysis & Power BI Export     {e3:>5}s
  Phase 4  Testing & Documentation            {e4:>5}s
  {'─'*50}
  Total Time                                  {total_time:>5}s

  OUTPUT FILES
  ┌────────────────────────────────────────────────────┐
  │ data/raw/upi_transactions_raw.csv   10,000 records │
  │ data/processed/upi_transactions_clean.csv  25 cols │
  │ data/powerbi/pb_*.csv          11 Power BI files   │
  │ reports/figures/*.png               8 Phase 1 charts│
  │ reports/figures/eda/*.png          14 EDA charts   │
  │ reports/sql_results/*.csv          18 SQL results  │
  │ reports/eda_summary_stats.txt                      │
  │ reports/eda_business_insights.txt                  │
  │ reports/FINAL_PROJECT_REPORT.txt                   │
  │ README.md                                          │
  └────────────────────────────────────────────────────┘

  POWER BI DASHBOARD
  Open Power BI Desktop and load:
  -> data/powerbi/pb_transactions.csv
  Follow: phase3_sql_powerbi/powerbi_guide.md

  MYSQL DATABASE (optional)
  Edit credentials in phase3_sql_powerbi/db_setup.py
  Then run: python phase3_sql_powerbi/db_setup.py
    """)

    if test_failures > 0:
        print(f"  WARNING: {test_failures} test(s) failed. Check output above.")
        sys.exit(1)
    else:
        print("  All tests passed. Project is ready.")
        banner("SUCCESS")


if __name__ == "__main__":
    main()

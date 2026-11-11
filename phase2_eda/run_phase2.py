"""
phase2_eda/run_phase2.py
--------------------------
Master runner for Phase 2 – Exploratory Data Analysis.

Executes all EDA modules in order:
  Module 1 – Summary Statistics & KPIs
  Module 2 – Trend Analysis (daily/weekly/monthly/hourly)
  Module 3 – Category & Bank Analysis
  Module 4 – Status Analysis
  Module 5 – Business Insights

Usage:
    python phase2_eda/run_phase2.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase2_eda.eda_loader             import load_clean_data
from phase2_eda.summary_stats          import run_summary
from phase2_eda.trend_analysis         import run_trend_analysis
from phase2_eda.category_bank_analysis import run_category_bank_analysis
from phase2_eda.status_analysis        import run_status_analysis
from phase2_eda.insights               import run_insights


def main():
    t0 = time.time()

    print("\n" + "█" * 62)
    print("  UPI TRANSACTION PATTERN ANALYSIS")
    print("  ▶  Phase 2: Exploratory Data Analysis")
    print("█" * 62)

    # Load once — pass to each module to avoid re-reads
    print("\n[LOAD] Loading cleaned dataset …")
    df = load_clean_data()
    print(f"       {len(df):,} records loaded. Columns: {df.shape[1]}")

    # ── Module 1 ──────────────────────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  MODULE 1 – Summary Statistics & KPIs")
    print("─" * 62)
    run_summary(df)

    # ── Module 2 ──────────────────────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  MODULE 2 – Trend Analysis")
    print("─" * 62)
    run_trend_analysis(df)

    # ── Module 3 ──────────────────────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  MODULE 3 – Category & Bank Analysis")
    print("─" * 62)
    run_category_bank_analysis(df)

    # ── Module 4 ──────────────────────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  MODULE 4 – Transaction Status Analysis")
    print("─" * 62)
    run_status_analysis(df)

    # ── Module 5 ──────────────────────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  MODULE 5 – Business Insights")
    print("─" * 62)
    run_insights(df)

    elapsed = time.time() - t0
    print("\n" + "█" * 62)
    print("  Phase 2 COMPLETE")
    print(f"  Time elapsed: {elapsed:.1f}s")
    print("  Outputs:")
    print("    reports/eda_summary_stats.txt")
    print("    reports/eda_category_bank.csv")
    print("    reports/eda_bank_summary.csv")
    print("    reports/eda_status_analysis.csv")
    print("    reports/eda_business_insights.txt")
    print("    reports/figures/eda/*.png  (14 charts)")
    print("█" * 62 + "\n")


if __name__ == "__main__":
    main()

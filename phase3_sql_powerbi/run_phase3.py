"""
phase3_sql_powerbi/run_phase3.py
-----------------------------------
Master runner for Phase 3.

Steps:
  A – SQL analysis (pandas engine; MySQL optional)
  B – Export Power BI datasets
  C – MySQL DB setup (optional; prompts user)

Usage:
    python phase3_sql_powerbi/run_phase3.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phase3_sql_powerbi.sql_analysis       import run_sql_analysis
from phase3_sql_powerbi.export_for_powerbi import run_export


def main():
    t0 = time.time()

    print("\n" + "█" * 62)
    print("  UPI TRANSACTION PATTERN ANALYSIS")
    print("  ▶  Phase 3: SQL Database & Power BI Dashboard")
    print("█" * 62)

    # ── Step A: SQL Analysis ──────────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  STEP A – SQL Business Analysis")
    print("─" * 62)
    run_sql_analysis()

    # ── Step B: Power BI Export ───────────────────────────────────────────────
    print("\n" + "─" * 62)
    print("  STEP B – Power BI Dataset Export")
    print("─" * 62)
    run_export()

    elapsed = time.time() - t0
    print("\n" + "█" * 62)
    print("  Phase 3 COMPLETE")
    print(f"  Time elapsed: {elapsed:.1f}s")
    print("  Outputs:")
    print("    reports/sql_results/*.csv         (23 query result files)")
    print("    data/powerbi/*.csv                (11 Power BI-ready files)")
    print("    phase3_sql_powerbi/schema.sql     (MySQL schema)")
    print("    phase3_sql_powerbi/sql_queries.sql(24 business queries + 5 views)")
    print("    phase3_sql_powerbi/powerbi_guide.md")
    print("\n  NEXT STEPS:")
    print("  ① To load MySQL: python phase3_sql_powerbi/db_setup.py")
    print("     (Ensure MySQL is running and edit DB_CONFIG credentials)")
    print("  ② Open Power BI Desktop → Get Data → CSV →")
    print("     data/powerbi/pb_transactions.csv")
    print("  ③ Follow: phase3_sql_powerbi/powerbi_guide.md")
    print("█" * 62 + "\n")


if __name__ == "__main__":
    main()

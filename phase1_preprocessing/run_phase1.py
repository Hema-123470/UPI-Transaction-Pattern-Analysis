"""
phase1_preprocessing/run_phase1.py
------------------------------------
Master runner for Phase 1.
Executes all three steps in sequence:
  1. Dataset generation
  2. Preprocessing pipeline
  3. Data profiling & chart generation

Usage:
    python phase1_preprocessing/run_phase1.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phase1_preprocessing.generate_dataset import generate_dataset
from phase1_preprocessing.preprocess       import run_pipeline
from phase1_preprocessing.data_profiler    import run_profiler
from config.settings import DATA_RAW_DIR, RAW_FILE

import os

def main():
    print("\n" + "█" * 60)
    print("  UPI TRANSACTION PATTERN ANALYSIS")
    print("  ▶  Phase 1: Data Collection & Preprocessing")
    print("█" * 60)

    # ── Step A: Generate raw dataset ──────────────────────────────────────────
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    if os.path.exists(RAW_FILE):
        print(f"\n[SKIP] Raw file already exists: {RAW_FILE}")
        print("       Delete it to regenerate.")
    else:
        print("\n[STEP A] Generating raw dataset …")
        import pandas as pd
        df_raw = generate_dataset()
        df_raw.to_csv(RAW_FILE, index=False)
        print(f"[STEP A] Raw dataset saved → {RAW_FILE}")

    # ── Step B: Preprocessing ─────────────────────────────────────────────────
    print("\n[STEP B] Running preprocessing pipeline …")
    df_clean = run_pipeline()

    # ── Step C: Profiling ─────────────────────────────────────────────────────
    print("\n[STEP C] Running data profiler …")
    run_profiler()

    print("\n" + "█" * 60)
    print("  Phase 1 COMPLETE")
    print("  Outputs:")
    print("    data/raw/upi_transactions_raw.csv")
    print("    data/processed/upi_transactions_clean.csv")
    print("    reports/preprocessing_report.txt")
    print("    reports/figures/*.png  (8 charts)")
    print("█" * 60 + "\n")


if __name__ == "__main__":
    main()

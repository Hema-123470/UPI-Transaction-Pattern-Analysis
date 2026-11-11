"""
phase2_eda/eda_loader.py
--------------------------
Shared data-loading utility for all Phase 2 EDA modules.
Loads the cleaned CSV and applies consistent type-casting
so every module works with the same DataFrame structure.
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CLEAN_FILE


def load_clean_data() -> pd.DataFrame:
    """
    Load the Phase-1 cleaned dataset with correct dtypes.

    Returns
    -------
    pd.DataFrame
        Ready-to-analyse DataFrame with parsed dates and typed columns.
    """
    if not os.path.exists(CLEAN_FILE):
        raise FileNotFoundError(
            f"Cleaned dataset not found at:\n  {CLEAN_FILE}\n"
            "Run Phase 1 first: python phase1_preprocessing/run_phase1.py"
        )

    df = pd.read_csv(CLEAN_FILE)

    # ── Type casting ──────────────────────────────────────────────────────────
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], format="%Y-%m-%d")
    df["Amount"]          = pd.to_numeric(df["Amount"],   errors="coerce")
    df["Hour"]            = pd.to_numeric(df["Hour"],     errors="coerce").astype(int)
    df["MonthNum"]        = pd.to_numeric(df["MonthNum"], errors="coerce").astype(int)
    df["IsWeekend"]       = pd.to_numeric(df["IsWeekend"],errors="coerce").astype(int)
    df["WeekOfYear"]      = pd.to_numeric(df["WeekOfYear"],errors="coerce").astype(int)

    # ── Ordered categoricals (for correct chart sorting) ──────────────────────
    month_order   = ["January","February","March","April","May","June",
                     "July","August","September","October","November","December"]
    dow_order     = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    tod_order     = ["Morning","Afternoon","Evening","Night"]
    bucket_order  = ["Small (≤500)","Medium (501–2000)","Large (2001–10000)","Very Large (>10000)"]

    df["Month"]        = pd.Categorical(df["Month"],       categories=month_order,  ordered=True)
    df["DayOfWeek"]    = pd.Categorical(df["DayOfWeek"],   categories=dow_order,    ordered=True)
    df["TimeOfDay"]    = pd.Categorical(df["TimeOfDay"],   categories=tod_order,    ordered=True)
    df["AmountBucket"] = pd.Categorical(df["AmountBucket"],categories=bucket_order, ordered=True)

    return df

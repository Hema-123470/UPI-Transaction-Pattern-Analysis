"""
phase1_preprocessing/preprocess.py
-------------------------------------
Loads the raw UPI dataset and performs all cleaning and
feature-engineering steps required before EDA and SQL loading.

Steps performed:
  1. Load raw CSV and display basic info
  2. Check and report missing values
  3. Check and remove duplicate records
  4. Data-type corrections (dates, numerics)
  5. Outlier detection & capping on Amount
  6. Standardise categorical text columns
  7. Feature engineering
       – Hour, TimeOfDay (Morning/Afternoon/Evening/Night)
       – IsWeekend flag
       – AmountBucket (Small / Medium / Large / Very Large)
       – TransactionMonth (numeric)
  8. Validate referential integrity (Status values, known categories)
  9. Save cleaned dataset
 10. Print preprocessing summary report

Usage:
    python phase1_preprocessing/preprocess.py
"""

import os
import sys
import numpy  as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    RAW_FILE, CLEAN_FILE, REPORT_FILE,
    DATA_PROC_DIR, REPORTS_DIR,
    CATEGORIES, STATUSES, BANKS, UPI_APPS, STATES_CITIES, DEVICES
)

os.makedirs(DATA_PROC_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR,   exist_ok=True)


# ── Utility ───────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ── Step 1 : Load ─────────────────────────────────────────────────────────────

def load_data(path: str) -> pd.DataFrame:
    section("STEP 1 – Load Raw Dataset")
    df = pd.read_csv(path)
    print(f"  Shape          : {df.shape}")
    print(f"  Columns        : {list(df.columns)}")
    print(f"\n  dtypes:\n{df.dtypes.to_string()}")
    print(f"\n  Memory usage   : {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    return df


# ── Step 2 : Missing values ───────────────────────────────────────────────────

def check_missing(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 2 – Missing Value Analysis")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    report = pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct})
    print(report[report["Missing Count"] > 0].to_string() or "  No missing values found.")

    # Drop rows where critical columns are null
    critical = ["TransactionID", "TransactionDate", "Amount", "Status"]
    before = len(df)
    df.dropna(subset=critical, inplace=True)
    dropped = before - len(df)
    print(f"\n  Rows dropped (null in critical cols): {dropped}")

    # Fill remaining non-critical nulls
    df["Remarks"] = df["Remarks"].fillna("N/A")
    return df


# ── Step 3 : Duplicates ───────────────────────────────────────────────────────

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 3 – Duplicate Check")
    dup_count = df.duplicated(subset="TransactionID").sum()
    print(f"  Duplicate TransactionIDs : {dup_count}")
    df.drop_duplicates(subset="TransactionID", keep="first", inplace=True)
    print(f"  Records after dedup      : {len(df):,}")
    return df


# ── Step 4 : Data-type corrections ────────────────────────────────────────────

def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 4 – Data-Type Corrections")

    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], format="%Y-%m-%d")
    df["TransactionTime"] = pd.to_datetime(df["TransactionTime"], format="%H:%M:%S").dt.time
    df["Amount"]          = pd.to_numeric(df["Amount"], errors="coerce")
    df["ReferenceNo"]     = df["ReferenceNo"].astype(str)

    print("  TransactionDate → datetime64")
    print("  TransactionTime → time")
    print("  Amount          → float64")
    print("  ReferenceNo     → str")
    return df


# ── Step 5 : Outlier detection & capping ──────────────────────────────────────

def handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 5 – Outlier Detection & Capping (Amount)")

    q1  = df["Amount"].quantile(0.25)
    q3  = df["Amount"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers_low  = (df["Amount"] < lower).sum()
    outliers_high = (df["Amount"] > upper).sum()
    print(f"  IQR lower fence : ₹{lower:,.2f}")
    print(f"  IQR upper fence : ₹{upper:,.2f}")
    print(f"  Outliers below  : {outliers_low}")
    print(f"  Outliers above  : {outliers_high}")

    # Cap instead of drop (winsorisation)
    df["Amount"] = df["Amount"].clip(lower=max(0, lower), upper=upper)
    print(f"  Amount capped to [₹{max(0, lower):,.2f}, ₹{upper:,.2f}]")
    return df


# ── Step 6 : Standardise categoricals ────────────────────────────────────────

def standardise_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 6 – Standardise Categorical Columns")
    text_cols = ["DayOfWeek", "Month", "SenderBank", "ReceiverBank",
                 "UPIApp", "PaymentType", "Category", "State", "City",
                 "Device", "Status", "Remarks"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Status back to uppercase
    df["Status"] = df["Status"].str.upper()

    # Validate against known values
    unknown_status = df[~df["Status"].isin([s.upper() for s in STATUSES])]["Status"].unique()
    if len(unknown_status):
        print(f"  [WARN] Unknown Status values: {unknown_status}")

    unknown_cat = df[~df["Category"].isin([c.title() for c in CATEGORIES])]["Category"].unique()
    if len(unknown_cat):
        print(f"  [WARN] Unknown Category values: {unknown_cat}")

    print("  Categorical columns standardised ✓")
    return df


# ── Step 7 : Feature Engineering ─────────────────────────────────────────────

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    section("STEP 7 – Feature Engineering")

    # Hour
    df["Hour"] = df["TransactionTime"].apply(lambda t: t.hour)

    # Time of Day
    def time_of_day(h):
        if  6 <= h < 12: return "Morning"
        if 12 <= h < 17: return "Afternoon"
        if 17 <= h < 21: return "Evening"
        return "Night"
    df["TimeOfDay"] = df["Hour"].apply(time_of_day)

    # Weekend flag
    df["IsWeekend"] = df["TransactionDate"].dt.dayofweek.isin([5, 6]).astype(int)

    # Month number (for ordering)
    df["MonthNum"] = df["TransactionDate"].dt.month

    # Week of year
    df["WeekOfYear"] = df["TransactionDate"].dt.isocalendar().week.astype(int)

    # Amount bucket
    def amount_bucket(amt):
        if amt <= 500:    return "Small (≤500)"
        if amt <= 2_000:  return "Medium (501–2000)"
        if amt <= 10_000: return "Large (2001–10000)"
        return "Very Large (>10000)"
    df["AmountBucket"] = df["Amount"].apply(amount_bucket)

    new_cols = ["Hour", "TimeOfDay", "IsWeekend", "MonthNum", "WeekOfYear", "AmountBucket"]
    print(f"  New features added: {new_cols}")
    for c in new_cols:
        print(f"    {c}: {df[c].unique()[:6]} …")
    return df


# ── Step 8 : Integrity validation ────────────────────────────────────────────

def validate_integrity(df: pd.DataFrame) -> None:
    section("STEP 8 – Integrity Validation")
    print(f"  Total records             : {len(df):,}")
    print(f"  Unique TransactionIDs     : {df['TransactionID'].nunique():,}")
    print(f"  Amount nulls              : {df['Amount'].isnull().sum()}")
    print(f"  Amount negatives          : {(df['Amount'] < 0).sum()}")
    print(f"  Status distribution       :\n{df['Status'].value_counts().to_string()}")
    print(f"  PaymentType distribution  :\n{df['PaymentType'].value_counts().to_string()}")
    print(f"  Category count            : {df['Category'].nunique()}")
    print(f"  State count               : {df['State'].nunique()}")
    print(f"  Date range                : {df['TransactionDate'].min().date()}  →  {df['TransactionDate'].max().date()}")


# ── Step 9 : Save ─────────────────────────────────────────────────────────────

def save_clean(df: pd.DataFrame) -> None:
    section("STEP 9 – Save Cleaned Dataset")
    # Convert date & time back to string for CSV portability
    df_out = df.copy()
    df_out["TransactionDate"] = df_out["TransactionDate"].dt.strftime("%Y-%m-%d")
    df_out["TransactionTime"] = df_out["TransactionTime"].astype(str)
    df_out.to_csv(CLEAN_FILE, index=False)
    print(f"  Cleaned dataset saved → {CLEAN_FILE}")
    print(f"  Rows: {len(df_out):,}  |  Columns: {df_out.shape[1]}")


# ── Step 10 : Report ──────────────────────────────────────────────────────────

def write_report(df: pd.DataFrame) -> None:
    section("STEP 10 – Preprocessing Report")
    lines = [
        "=" * 60,
        " UPI Transaction Pattern Analysis",
        " Phase 1 – Preprocessing Report",
        "=" * 60,
        "",
        f"Raw records             : 10,000",
        f"Records after cleaning  : {len(df):,}",
        f"Columns (final)         : {df.shape[1]}",
        f"Date range              : {df['TransactionDate'].min().date()}  →  {df['TransactionDate'].max().date()}",
        f"Amount (post-cap) range : ₹{df['Amount'].min():,.2f}  –  ₹{df['Amount'].max():,.2f}",
        f"Total transaction value : ₹{df['Amount'].sum():,.2f}",
        "",
        "STATUS DISTRIBUTION",
        df["Status"].value_counts().to_string(),
        "",
        "PAYMENT TYPE",
        df["PaymentType"].value_counts().to_string(),
        "",
        "TOP 5 CATEGORIES BY VOLUME",
        df.groupby("Category")["Amount"].sum().sort_values(ascending=False).head(5).to_string(),
        "",
        "TOP 5 STATES BY TRANSACTION COUNT",
        df["State"].value_counts().head(5).to_string(),
        "",
        "TOP 5 BANKS (SENDER) BY TRANSACTION COUNT",
        df["SenderBank"].value_counts().head(5).to_string(),
        "",
        "UPI APP USAGE",
        df["UPIApp"].value_counts().to_string(),
        "",
        "TIME OF DAY DISTRIBUTION",
        df["TimeOfDay"].value_counts().to_string(),
        "",
        "AMOUNT BUCKET DISTRIBUTION",
        df["AmountBucket"].value_counts().to_string(),
    ]
    report_text = "\n".join(lines)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"  Report saved → {REPORT_FILE}")
    print("\n" + report_text)


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline() -> pd.DataFrame:
    print("=" * 60)
    print("  UPI Transaction Pattern Analysis")
    print("  Phase 1 – Data Preprocessing Pipeline")
    print("=" * 60)

    df = load_data(RAW_FILE)
    df = check_missing(df)
    df = remove_duplicates(df)
    df = fix_dtypes(df)
    df = handle_outliers(df)
    df = standardise_categoricals(df)
    df = feature_engineering(df)
    validate_integrity(df)
    save_clean(df)
    write_report(df)

    print("\n[DONE] Phase 1 preprocessing pipeline complete.\n")
    return df


if __name__ == "__main__":
    run_pipeline()

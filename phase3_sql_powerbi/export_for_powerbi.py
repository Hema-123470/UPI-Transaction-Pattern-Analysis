"""
phase3_sql_powerbi/export_for_powerbi.py
------------------------------------------
Exports pre-aggregated CSVs optimised for direct import into
Power BI Desktop — one CSV per dashboard page.

Files created in data/powerbi/:
  pb_page1_overview.csv     – Monthly KPIs
  pb_page2_time.csv         – Hourly & day-of-week patterns
  pb_page3_merchant_bank.csv– Category + bank summary
  pb_page4_status.csv       – Status analysis
  pb_transactions.csv       – Full cleaned dataset (master)

Usage:
    python phase3_sql_powerbi/export_for_powerbi.py
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CLEAN_FILE, BASE_DIR

PBI_DIR = os.path.join(BASE_DIR, "data", "powerbi")
os.makedirs(PBI_DIR, exist_ok=True)


def load() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_FILE)
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])
    df["Amount"] = pd.to_numeric(df["Amount"])
    return df


def export_page1_overview(df: pd.DataFrame) -> None:
    """Monthly KPI summary for Page 1."""
    month_order = ["January","February","March","April","May","June",
                   "July","August","September"]
    monthly = (
        df.groupby(["MonthNum","Month"], observed=True)
          .agg(
              total_transactions  = ("TransactionID","count"),
              total_value         = ("Amount","sum"),
              avg_amount          = ("Amount","mean"),
              success_count       = ("Status", lambda x: (x=="SUCCESS").sum()),
              failed_count        = ("Status", lambda x: (x=="FAILED").sum()),
              pending_count       = ("Status", lambda x: (x=="PENDING").sum()),
              p2p_count           = ("PaymentType", lambda x: (x=="P2P").sum()),
              p2m_count           = ("PaymentType", lambda x: (x=="P2M").sum()),
          )
          .round(2)
          .reset_index()
          .rename(columns={"MonthNum":"month_num","Month":"month_name"})
          .sort_values("month_num")
    )
    monthly["failure_rate_pct"]  = (monthly["failed_count"]  / monthly["total_transactions"] * 100).round(2)
    monthly["success_rate_pct"]  = (monthly["success_count"] / monthly["total_transactions"] * 100).round(2)

    out = os.path.join(PBI_DIR, "pb_page1_overview.csv")
    monthly.to_csv(out, index=False)
    print(f"  Page 1 Overview         → {out}  ({len(monthly)} rows)")


def export_page2_time(df: pd.DataFrame) -> None:
    """Hourly + day-of-week patterns for Page 2."""
    hourly = (
        df.groupby("Hour")
          .agg(
              txn_count    = ("TransactionID","count"),
              total_value  = ("Amount","sum"),
              avg_amount   = ("Amount","mean"),
              failed_count = ("Status", lambda x: (x=="FAILED").sum()),
          )
          .round(2)
          .reset_index()
          .rename(columns={"Hour":"hour"})
    )
    hourly["failure_rate_pct"] = (hourly["failed_count"] / hourly["txn_count"] * 100).round(2)

    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = (
        df.groupby(["DayOfWeek","IsWeekend"], observed=True)
          .agg(
              txn_count    = ("TransactionID","count"),
              total_value  = ("Amount","sum"),
              avg_amount   = ("Amount","mean"),
              failed_count = ("Status", lambda x: (x=="FAILED").sum()),
          )
          .round(2)
          .reindex(dow_order, level=0)
          .reset_index()
          .rename(columns={"DayOfWeek":"day_of_week","IsWeekend":"is_weekend"})
    )
    dow["failure_rate_pct"] = (dow["failed_count"] / dow["txn_count"] * 100).round(2)

    tod_order = ["Morning","Afternoon","Evening","Night"]
    tod = (
        df.groupby("TimeOfDay", observed=True)
          .agg(txn_count=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .reindex(tod_order)
          .reset_index()
          .rename(columns={"TimeOfDay":"time_of_day"})
    )

    h_out = os.path.join(PBI_DIR, "pb_page2_hourly.csv")
    d_out = os.path.join(PBI_DIR, "pb_page2_dow.csv")
    t_out = os.path.join(PBI_DIR, "pb_page2_timeofday.csv")
    hourly.to_csv(h_out, index=False)
    dow.to_csv(d_out, index=False)
    tod.to_csv(t_out, index=False)
    print(f"  Page 2 Hourly           → {h_out}")
    print(f"  Page 2 Day-of-Week      → {d_out}")
    print(f"  Page 2 Time of Day      → {t_out}")


def export_page3_merchant_bank(df: pd.DataFrame) -> None:
    """Category + bank + UPI app data for Page 3."""
    cat = (
        df.groupby("Category")
          .agg(
              txn_count     = ("TransactionID","count"),
              total_value   = ("Amount","sum"),
              avg_amount    = ("Amount","mean"),
              failed_count  = ("Status", lambda x: (x=="FAILED").sum()),
              p2p_count     = ("PaymentType", lambda x: (x=="P2P").sum()),
              p2m_count     = ("PaymentType", lambda x: (x=="P2M").sum()),
          )
          .round(2)
          .assign(failure_rate_pct=lambda x: (x["failed_count"]/x["txn_count"]*100).round(2),
                  value_share_pct =lambda x: (x["total_value"]/x["total_value"].sum()*100).round(2))
          .sort_values("total_value", ascending=False)
          .reset_index()
    )

    bank = (
        df.groupby("SenderBank")
          .agg(
              txn_count     = ("TransactionID","count"),
              total_value   = ("Amount","sum"),
              avg_amount    = ("Amount","mean"),
              failed_count  = ("Status", lambda x: (x=="FAILED").sum()),
              success_count = ("Status", lambda x: (x=="SUCCESS").sum()),
          )
          .round(2)
          .assign(failure_rate_pct= lambda x: (x["failed_count"]/x["txn_count"]*100).round(2),
                  success_rate_pct= lambda x: (x["success_count"]/x["txn_count"]*100).round(2))
          .sort_values("txn_count", ascending=False)
          .reset_index()
          .rename(columns={"SenderBank":"sender_bank"})
    )

    app = (
        df.groupby("UPIApp")
          .agg(
              txn_count     = ("TransactionID","count"),
              total_value   = ("Amount","sum"),
              avg_amount    = ("Amount","mean"),
              success_count = ("Status", lambda x: (x=="SUCCESS").sum()),
              failed_count  = ("Status", lambda x: (x=="FAILED").sum()),
          )
          .round(2)
          .assign(success_rate_pct=lambda x: (x["success_count"]/x["txn_count"]*100).round(2),
                  failure_rate_pct=lambda x: (x["failed_count"]/x["txn_count"]*100).round(2),
                  market_share_pct=lambda x: (x["txn_count"]/x["txn_count"].sum()*100).round(2))
          .sort_values("txn_count", ascending=False)
          .reset_index()
          .rename(columns={"UPIApp":"upi_app"})
    )

    cat.to_csv(os.path.join(PBI_DIR, "pb_page3_category.csv"), index=False)
    bank.to_csv(os.path.join(PBI_DIR, "pb_page3_bank.csv"), index=False)
    app.to_csv(os.path.join(PBI_DIR, "pb_page3_upi_app.csv"), index=False)
    print(f"  Page 3 Category         → {os.path.join(PBI_DIR,'pb_page3_category.csv')}")
    print(f"  Page 3 Bank             → {os.path.join(PBI_DIR,'pb_page3_bank.csv')}")
    print(f"  Page 3 UPI App          → {os.path.join(PBI_DIR,'pb_page3_upi_app.csv')}")


def export_page4_status(df: pd.DataFrame) -> None:
    """Status analysis data for Page 4."""
    # Status × category
    status_cat = (
        df.groupby(["Status","Category"])
          .agg(txn_count=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .reset_index()
    )

    # Status × bank
    status_bank = (
        df.groupby(["Status","SenderBank"])
          .agg(txn_count=("TransactionID","count"))
          .reset_index()
          .rename(columns={"SenderBank":"sender_bank"})
    )

    # Status × hour
    status_hour = (
        df.groupby(["Status","Hour"])
          .agg(txn_count=("TransactionID","count"))
          .reset_index()
          .rename(columns={"Hour":"hour"})
    )

    # Failure rate by bank
    fail_bank = (
        df.groupby("SenderBank")
          .apply(lambda x: round((x["Status"]=="FAILED").mean()*100, 2),
                 include_groups=False)
          .reset_index(name="failure_rate_pct")
          .rename(columns={"SenderBank":"sender_bank"})
          .sort_values("failure_rate_pct", ascending=False)
    )

    # Amount bucket × status
    bucket_status = (
        df.groupby(["AmountBucket","Status"], observed=True)
          .agg(txn_count=("TransactionID","count"),
               total_value=("Amount","sum"))
          .round(2)
          .reset_index()
          .rename(columns={"AmountBucket":"amount_bucket"})
    )

    for name, data in [
        ("pb_page4_status_category.csv", status_cat),
        ("pb_page4_status_bank.csv",     status_bank),
        ("pb_page4_status_hour.csv",     status_hour),
        ("pb_page4_failure_by_bank.csv", fail_bank),
        ("pb_page4_bucket_status.csv",   bucket_status),
    ]:
        out = os.path.join(PBI_DIR, name)
        data.to_csv(out, index=False)
        print(f"  Page 4 → {name:<35} ({len(data)} rows)")


def export_master(df: pd.DataFrame) -> None:
    """Full cleaned dataset for Power BI master import."""
    out = os.path.join(PBI_DIR, "pb_transactions.csv")
    df.to_csv(out, index=False)
    print(f"  Master dataset          → {out}  ({len(df):,} rows)")


def run_export() -> None:
    print("=" * 62)
    print("  UPI Transaction Pattern Analysis")
    print("  Phase 3 – Power BI Data Export")
    print("=" * 62)

    df = load()
    print(f"\n  Loaded {len(df):,} records. Exporting …\n")

    export_page1_overview(df)
    export_page2_time(df)
    export_page3_merchant_bank(df)
    export_page4_status(df)
    export_master(df)

    print(f"\n[DONE] All Power BI data files saved to: {PBI_DIR}")
    print("       Open Power BI Desktop and follow powerbi_guide.md\n")


if __name__ == "__main__":
    run_export()

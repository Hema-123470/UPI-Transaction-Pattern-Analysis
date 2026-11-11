"""
phase2_eda/summary_stats.py
------------------------------
Module 1 of Phase 2 EDA.

Computes and prints high-level KPIs:
  - Total transactions & total value
  - Average, median, min, max transaction amounts
  - Success / Failure / Pending breakdown
  - P2P vs P2M split
  - Most active month, day, hour
  - Top category and top state by volume

All results are also saved to reports/eda_summary_stats.txt
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import REPORTS_DIR
from phase2_eda.eda_loader import load_clean_data

os.makedirs(REPORTS_DIR, exist_ok=True)
STATS_FILE = os.path.join(REPORTS_DIR, "eda_summary_stats.txt")


def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a dict of all key performance indicators."""
    success = df[df["Status"] == "SUCCESS"]

    kpis = {
        # ── Volume ────────────────────────────────────────────────────────────
        "total_transactions"    : len(df),
        "total_value_inr"       : df["Amount"].sum(),
        "successful_txns"       : (df["Status"] == "SUCCESS").sum(),
        "failed_txns"           : (df["Status"] == "FAILED").sum(),
        "pending_txns"          : (df["Status"] == "PENDING").sum(),
        "success_rate_pct"      : round((df["Status"] == "SUCCESS").mean() * 100, 2),
        "failure_rate_pct"      : round((df["Status"] == "FAILED").mean()  * 100, 2),

        # ── Amount stats (all transactions) ───────────────────────────────────
        "avg_amount"            : round(df["Amount"].mean(),   2),
        "median_amount"         : round(df["Amount"].median(), 2),
        "min_amount"            : round(df["Amount"].min(),    2),
        "max_amount"            : round(df["Amount"].max(),    2),
        "std_amount"            : round(df["Amount"].std(),    2),

        # ── Amount stats (successful only) ────────────────────────────────────
        "avg_amount_success"    : round(success["Amount"].mean(),   2),
        "total_value_success"   : round(success["Amount"].sum(),    2),

        # ── P2P / P2M ─────────────────────────────────────────────────────────
        "p2p_count"             : (df["PaymentType"] == "P2P").sum(),
        "p2m_count"             : (df["PaymentType"] == "P2M").sum(),
        "p2p_total_value"       : round(df[df["PaymentType"]=="P2P"]["Amount"].sum(), 2),
        "p2m_total_value"       : round(df[df["PaymentType"]=="P2M"]["Amount"].sum(), 2),

        # ── Time ──────────────────────────────────────────────────────────────
        "date_min"              : str(df["TransactionDate"].min().date()),
        "date_max"              : str(df["TransactionDate"].max().date()),
        "peak_month"            : df["Month"].value_counts().idxmax(),
        "peak_day_of_week"      : df["DayOfWeek"].value_counts().idxmax(),
        "peak_hour"             : int(df["Hour"].value_counts().idxmax()),
        "peak_time_of_day"      : df["TimeOfDay"].value_counts().idxmax(),

        # ── Top performers ────────────────────────────────────────────────────
        "top_category_by_count" : df["Category"].value_counts().idxmax(),
        "top_category_by_value" : df.groupby("Category")["Amount"].sum().idxmax(),
        "top_state_by_count"    : df["State"].value_counts().idxmax(),
        "top_state_by_value"    : df.groupby("State")["Amount"].sum().idxmax(),
        "top_bank_sender"       : df["SenderBank"].value_counts().idxmax(),
        "top_upi_app"           : df["UPIApp"].value_counts().idxmax(),

        # ── Weekend vs Weekday ────────────────────────────────────────────────
        "weekend_txns"          : (df["IsWeekend"] == 1).sum(),
        "weekday_txns"          : (df["IsWeekend"] == 0).sum(),
        "weekend_avg_amount"    : round(df[df["IsWeekend"]==1]["Amount"].mean(), 2),
        "weekday_avg_amount"    : round(df[df["IsWeekend"]==0]["Amount"].mean(), 2),
    }
    return kpis


def format_report(kpis: dict, df: pd.DataFrame) -> str:
    """Build a formatted text report from the KPI dict."""
    sep = "=" * 62
    lines = [
        sep,
        "  UPI TRANSACTION PATTERN ANALYSIS",
        "  Phase 2 – EDA Summary Statistics",
        sep,
        "",
        "── OVERVIEW ─────────────────────────────────────────────",
        f"  Date Range              : {kpis['date_min']}  →  {kpis['date_max']}",
        f"  Total Transactions      : {kpis['total_transactions']:>10,}",
        f"  Total Value             : ₹{kpis['total_value_inr']:>15,.2f}",
        f"  Total Value (SUCCESS)   : ₹{kpis['total_value_success']:>15,.2f}",
        "",
        "── TRANSACTION AMOUNT ───────────────────────────────────",
        f"  Average Amount          : ₹{kpis['avg_amount']:>12,.2f}",
        f"  Median Amount           : ₹{kpis['median_amount']:>12,.2f}",
        f"  Std Deviation           : ₹{kpis['std_amount']:>12,.2f}",
        f"  Minimum Amount          : ₹{kpis['min_amount']:>12,.2f}",
        f"  Maximum Amount          : ₹{kpis['max_amount']:>12,.2f}",
        f"  Avg Amount (SUCCESS)    : ₹{kpis['avg_amount_success']:>12,.2f}",
        "",
        "── TRANSACTION STATUS ───────────────────────────────────",
        f"  Successful              : {kpis['successful_txns']:>7,}  ({kpis['success_rate_pct']}%)",
        f"  Failed                  : {kpis['failed_txns']:>7,}  ({kpis['failure_rate_pct']}%)",
        f"  Pending                 : {kpis['pending_txns']:>7,}",
        "",
        "── PAYMENT TYPE ─────────────────────────────────────────",
        f"  P2P (Person-to-Person)  : {kpis['p2p_count']:>7,}  |  ₹{kpis['p2p_total_value']:>14,.2f}",
        f"  P2M (Person-to-Merchant): {kpis['p2m_count']:>7,}  |  ₹{kpis['p2m_total_value']:>14,.2f}",
        "",
        "── PEAK TIME ANALYSIS ───────────────────────────────────",
        f"  Peak Month              : {kpis['peak_month']}",
        f"  Peak Day of Week        : {kpis['peak_day_of_week']}",
        f"  Peak Hour               : {kpis['peak_hour']:02d}:00",
        f"  Peak Time of Day        : {kpis['peak_time_of_day']}",
        "",
        "── WEEKEND VS WEEKDAY ───────────────────────────────────",
        f"  Weekday Transactions    : {kpis['weekday_txns']:>7,}  |  Avg ₹{kpis['weekday_avg_amount']:>10,.2f}",
        f"  Weekend Transactions    : {kpis['weekend_txns']:>7,}  |  Avg ₹{kpis['weekend_avg_amount']:>10,.2f}",
        "",
        "── TOP PERFORMERS ───────────────────────────────────────",
        f"  Top Category (Count)    : {kpis['top_category_by_count']}",
        f"  Top Category (Value)    : {kpis['top_category_by_value']}",
        f"  Top State (Count)       : {kpis['top_state_by_count']}",
        f"  Top State (Value)       : {kpis['top_state_by_value']}",
        f"  Top Sender Bank         : {kpis['top_bank_sender']}",
        f"  Top UPI App             : {kpis['top_upi_app']}",
        "",
        "── CATEGORY BREAKDOWN ───────────────────────────────────",
        df.groupby("Category").agg(
            Count=("TransactionID","count"),
            TotalValue=("Amount","sum"),
            AvgValue=("Amount","mean")
        ).sort_values("Count",ascending=False)
        .assign(
            TotalValue=lambda x: x["TotalValue"].map("₹{:,.2f}".format),
            AvgValue  =lambda x: x["AvgValue"].map("₹{:,.2f}".format)
        ).to_string(),
        "",
        "── STATE-WISE TRANSACTION COUNT ─────────────────────────",
        df["State"].value_counts().to_string(),
        "",
        sep,
    ]
    return "\n".join(lines)


def run_summary(df: pd.DataFrame = None) -> dict:
    """Compute KPIs, print report and save to file. Returns kpi dict."""
    if df is None:
        df = load_clean_data()

    kpis   = compute_kpis(df)
    report = format_report(kpis, df)

    print(report)

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n[INFO] Summary stats saved → {STATS_FILE}")
    return kpis


if __name__ == "__main__":
    run_summary()

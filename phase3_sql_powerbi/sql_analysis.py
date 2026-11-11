"""
phase3_sql_powerbi/sql_analysis.py
-------------------------------------
Executes all business analysis SQL queries against the MySQL database
and saves results to reports/sql_results/.

If MySQL is unavailable, falls back to executing the same logic
using pandas on the cleaned CSV (so the project remains functional).

Usage:
    python phase3_sql_powerbi/sql_analysis.py
"""

import os
import sys
import pandas as pd
import numpy  as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CLEAN_FILE, REPORTS_DIR

SQL_RESULTS_DIR = os.path.join(REPORTS_DIR, "sql_results")
os.makedirs(SQL_RESULTS_DIR, exist_ok=True)


# ── MySQL execution (optional) ────────────────────────────────────────────────
def try_mysql_queries(db_config: dict, db_name: str) -> bool:
    """
    Attempt to connect to MySQL and run queries.
    Returns True on success, False on failure.
    """
    try:
        import mysql.connector
        cfg = dict(db_config)
        cfg["database"] = db_name
        conn   = mysql.connector.connect(**cfg)
        cursor = conn.cursor(dictionary=True)

        queries = {
            "Q01_overview": """
                SELECT COUNT(*) AS total_transactions,
                       ROUND(SUM(amount),2) AS total_value,
                       ROUND(AVG(amount),2) AS avg_amount,
                       ROUND(MIN(amount),2) AS min_amount,
                       ROUND(MAX(amount),2) AS max_amount,
                       ROUND(STDDEV(amount),2) AS std_deviation
                FROM transactions
            """,
            "Q02_status": """
                SELECT status, COUNT(*) AS total_count,
                       ROUND(SUM(amount),2) AS total_value,
                       ROUND(AVG(amount),2) AS avg_value,
                       ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(),2) AS percentage
                FROM transactions
                GROUP BY status ORDER BY total_count DESC
            """,
            "Q04_monthly": """
                SELECT month_num, month_name,
                       COUNT(*) AS total_transactions,
                       ROUND(SUM(amount),2) AS total_value,
                       ROUND(AVG(amount),2) AS avg_amount
                FROM transactions
                GROUP BY month_num, month_name
                ORDER BY month_num
            """,
            "Q06_hourly": """
                SELECT hour, COUNT(*) AS total_transactions,
                       ROUND(SUM(amount),2) AS total_value,
                       ROUND(AVG(amount),2) AS avg_amount
                FROM transactions GROUP BY hour ORDER BY hour
            """,
            "Q11_category": """
                SELECT category, COUNT(*) AS total_transactions,
                       ROUND(SUM(amount),2) AS total_value,
                       ROUND(AVG(amount),2) AS avg_amount,
                       ROUND(SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END)*100.0/COUNT(*),2)
                           AS failure_rate_pct
                FROM transactions
                GROUP BY category ORDER BY total_value DESC
            """,
            "Q15_bank": """
                SELECT sender_bank, COUNT(*) AS total_sent,
                       ROUND(SUM(amount),2) AS total_value,
                       ROUND(SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END)*100.0/COUNT(*),2)
                           AS failure_rate_pct
                FROM transactions
                GROUP BY sender_bank ORDER BY total_sent DESC
            """,
            "Q18_upi_app": """
                SELECT upi_app, COUNT(*) AS total_transactions,
                       ROUND(SUM(amount),2) AS total_value,
                       ROUND(SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END)*100.0/COUNT(*),2)
                           AS success_rate_pct
                FROM transactions GROUP BY upi_app ORDER BY total_transactions DESC
            """,
            "Q19_state": """
                SELECT state, COUNT(*) AS total_transactions,
                       ROUND(SUM(amount),2) AS total_value,
                       ROUND(AVG(amount),2) AS avg_amount
                FROM transactions GROUP BY state ORDER BY total_value DESC
            """,
        }

        for name, sql in queries.items():
            cursor.execute(sql)
            rows = cursor.fetchall()
            result_df = pd.DataFrame(rows)
            out_file  = os.path.join(SQL_RESULTS_DIR, f"{name}.csv")
            result_df.to_csv(out_file, index=False)
            print(f"  {name:<25} → {len(result_df)} rows  saved to {out_file}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"  [WARN] MySQL query execution failed: {e}")
        return False


# ── Pandas fallback (always runs) ────────────────────────────────────────────
def run_pandas_analysis(df: pd.DataFrame) -> dict:
    """Run all SQL-equivalent queries using pandas. Returns dict of DataFrames."""
    results = {}

    # Q01: Overview
    results["Q01_overview"] = pd.DataFrame([{
        "total_transactions" : len(df),
        "total_value"        : round(df["Amount"].sum(), 2),
        "avg_amount"         : round(df["Amount"].mean(), 2),
        "median_amount"      : round(df["Amount"].median(), 2),
        "min_amount"         : round(df["Amount"].min(), 2),
        "max_amount"         : round(df["Amount"].max(), 2),
        "std_deviation"      : round(df["Amount"].std(), 2),
    }])

    # Q02: Status
    results["Q02_status"] = (
        df.groupby("Status")
          .agg(total_count=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_value=("Amount","mean"))
          .round(2)
          .assign(percentage=lambda x: (x["total_count"]/len(df)*100).round(2))
          .sort_values("total_count", ascending=False)
          .reset_index()
    )

    # Q03: P2P vs P2M
    results["Q03_payment_type"] = (
        df.groupby("PaymentType")
          .agg(total_count=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"),
               min_amount=("Amount","min"),
               max_amount=("Amount","max"))
          .round(2)
          .assign(
              success_count =lambda x: df[df["Status"]=="SUCCESS"].groupby("PaymentType")["TransactionID"].count(),
              success_rate  =lambda x: (df[df["Status"]=="SUCCESS"].groupby("PaymentType")["TransactionID"].count() / x["total_count"] * 100).round(2)
          )
          .reset_index()
    )

    # Q04: Monthly trend
    month_order = ["January","February","March","April","May","June",
                   "July","August","September"]
    monthly = (
        df.groupby(["MonthNum","Month"], observed=True)
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .reset_index()
          .rename(columns={"MonthNum":"month_num","Month":"month_name"})
          .sort_values("month_num")
    )
    monthly["failed_count"]    = df[df["Status"]=="FAILED"].groupby("MonthNum")["TransactionID"].count().reindex(monthly["month_num"]).values
    monthly["success_count"]   = df[df["Status"]=="SUCCESS"].groupby("MonthNum")["TransactionID"].count().reindex(monthly["month_num"]).values
    monthly["failure_rate_pct"]= (monthly["failed_count"].fillna(0) / monthly["total_transactions"] * 100).round(2)
    results["Q04_monthly"] = monthly

    # Q05: Day of week
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    results["Q05_day_of_week"] = (
        df.groupby(["DayOfWeek","IsWeekend"], observed=True)
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .reindex(dow_order, level=0)
          .reset_index()
          .rename(columns={"DayOfWeek":"day_of_week","IsWeekend":"is_weekend"})
    )

    # Q06: Hourly
    results["Q06_hourly"] = (
        df.groupby("Hour")
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .reset_index()
          .rename(columns={"Hour":"hour"})
    )
    results["Q06_hourly"]["failure_rate_pct"] = (
        df[df["Status"]=="FAILED"].groupby("Hour")["TransactionID"].count()
          .reindex(results["Q06_hourly"]["hour"]).fillna(0).values
        / results["Q06_hourly"]["total_transactions"] * 100
    ).round(2)

    # Q07: Peak hours
    results["Q07_peak_hours"] = (
        results["Q06_hourly"]
          .sort_values("total_transactions", ascending=False)
          .head(5)[["hour","total_transactions","total_value"]]
    )

    # Q08: Time of day
    tod_order = ["Morning","Afternoon","Evening","Night"]
    results["Q08_time_of_day"] = (
        df.groupby("TimeOfDay", observed=True)
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .reindex(tod_order)
          .reset_index()
          .rename(columns={"TimeOfDay":"time_of_day"})
    )

    # Q09: Weekend vs Weekday
    results["Q09_weekend"] = (
        df.assign(day_type=df["IsWeekend"].map({1:"Weekend",0:"Weekday"}))
          .groupby("day_type")
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .reset_index()
    )

    # Q11: Category
    cat_grp = df.groupby("Category")
    results["Q11_category"] = (
        cat_grp.agg(total_transactions=("TransactionID","count"),
                    total_value=("Amount","sum"),
                    avg_amount=("Amount","mean"),
                    min_amount=("Amount","min"),
                    max_amount=("Amount","max"))
               .round(2)
               .assign(
                   failed_count=cat_grp["Status"].apply(lambda x: (x=="FAILED").sum()),
                   success_count=cat_grp["Status"].apply(lambda x: (x=="SUCCESS").sum()),
               )
               .assign(
                   failure_rate_pct=lambda x: (x["failed_count"]/x["total_transactions"]*100).round(2),
                   value_share_pct=lambda x: (x["total_value"]/x["total_value"].sum()*100).round(2)
               )
               .sort_values("total_value", ascending=False)
               .reset_index()
    )

    # Q15: Bank
    bk_grp = df.groupby("SenderBank")
    results["Q15_bank"] = (
        bk_grp.agg(total_sent=("TransactionID","count"),
                   total_value=("Amount","sum"),
                   avg_amount=("Amount","mean"))
              .round(2)
              .assign(
                  failed_count=bk_grp["Status"].apply(lambda x: (x=="FAILED").sum()),
                  success_count=bk_grp["Status"].apply(lambda x: (x=="SUCCESS").sum()),
              )
              .assign(failure_rate_pct=lambda x: (x["failed_count"]/x["total_sent"]*100).round(2))
              .sort_values("total_sent", ascending=False)
              .reset_index()
              .rename(columns={"SenderBank":"sender_bank"})
    )

    # Q17: Sender-receiver bank pairs
    results["Q17_bank_pairs"] = (
        df.groupby(["SenderBank","ReceiverBank"])
          .agg(transaction_count=("TransactionID","count"),
               total_value=("Amount","sum"))
          .round(2)
          .sort_values("transaction_count", ascending=False)
          .head(15)
          .reset_index()
          .rename(columns={"SenderBank":"sender_bank","ReceiverBank":"receiver_bank"})
    )

    # Q18: UPI App
    app_grp = df.groupby("UPIApp")
    results["Q18_upi_app"] = (
        app_grp.agg(total_transactions=("TransactionID","count"),
                    total_value=("Amount","sum"),
                    avg_amount=("Amount","mean"))
               .round(2)
               .assign(
                   success_rate_pct=app_grp["Status"].apply(lambda x: round((x=="SUCCESS").mean()*100, 2)),
                   failure_rate_pct=app_grp["Status"].apply(lambda x: round((x=="FAILED").mean()*100, 2)),
               )
               .sort_values("total_transactions", ascending=False)
               .reset_index()
               .rename(columns={"UPIApp":"upi_app"})
    )

    # Q19: State
    results["Q19_state"] = (
        df.groupby("State")
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"),
               city_count=("City","nunique"))
          .round(2)
          .sort_values("total_value", ascending=False)
          .reset_index()
          .rename(columns={"State":"state"})
    )

    # Q20: Top 10 cities
    results["Q20_top_cities"] = (
        df.groupby(["City","State"])
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          [["total_transactions","total_value","avg_amount"]].round(2)
          .sort_values("total_transactions", ascending=False)
          .head(10)
          .reset_index()
          .rename(columns={"City":"city","State":"state"})
    )

    # Q21: Device
    results["Q21_device"] = (
        df.groupby("Device")
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .assign(
              success_rate_pct=df.groupby("Device")["Status"].apply(
                  lambda x: round((x=="SUCCESS").mean()*100, 2))
          )
          .sort_values("total_transactions", ascending=False)
          .reset_index()
          .rename(columns={"Device":"device"})
    )

    # Q22: Amount bucket
    bucket_order = ["Small (≤500)","Medium (501–2000)",
                    "Large (2001–10000)","Very Large (>10000)"]
    results["Q22_amount_bucket"] = (
        df.groupby("AmountBucket", observed=True)
          .agg(total_transactions=("TransactionID","count"),
               total_value=("Amount","sum"),
               avg_amount=("Amount","mean"))
          .round(2)
          .reindex(bucket_order)
          .assign(pct_of_total=lambda x: (x["total_transactions"]/len(df)*100).round(2))
          .reset_index()
          .rename(columns={"AmountBucket":"amount_bucket"})
    )

    # Q23: High-value transactions
    results["Q23_high_value"] = (
        df[df["Amount"] > 40_000][
            ["TransactionID","TransactionDate","Amount","Category",
             "SenderBank","State","Status"]
        ]
        .sort_values("Amount", ascending=False)
        .head(20)
        .round(2)
    )

    return results


def save_all_results(results: dict) -> None:
    """Save all query results to CSV files."""
    for name, df_result in results.items():
        if df_result is not None and len(df_result) > 0:
            out = os.path.join(SQL_RESULTS_DIR, f"{name}.csv")
            df_result.to_csv(out, index=False)
            print(f"  {name:<30} → {len(df_result):>4} rows  →  {out}")


def print_key_results(results: dict) -> None:
    """Print a formatted summary of key query outputs."""
    sep = "─" * 62

    print(f"\n{sep}")
    print("  Q01 – OVERVIEW KPIs")
    print(sep)
    print(results["Q01_overview"].to_string(index=False))

    print(f"\n{sep}")
    print("  Q02 – STATUS DISTRIBUTION")
    print(sep)
    print(results["Q02_status"].to_string(index=False))

    print(f"\n{sep}")
    print("  Q04 – MONTHLY TREND")
    print(sep)
    print(results["Q04_monthly"][["month_name","total_transactions","total_value","avg_amount"]].to_string(index=False))

    print(f"\n{sep}")
    print("  Q07 – TOP 5 PEAK HOURS")
    print(sep)
    print(results["Q07_peak_hours"].to_string(index=False))

    print(f"\n{sep}")
    print("  Q11 – CATEGORY ANALYSIS (top 5 by value)")
    print(sep)
    print(results["Q11_category"][["Category","total_transactions","total_value","failure_rate_pct"]].head(5).to_string(index=False))

    print(f"\n{sep}")
    print("  Q15 – BANK ANALYSIS (top 5)")
    print(sep)
    print(results["Q15_bank"][["sender_bank","total_sent","total_value","failure_rate_pct"]].head(5).to_string(index=False))

    print(f"\n{sep}")
    print("  Q19 – STATE ANALYSIS (top 5 by value)")
    print(sep)
    print(results["Q19_state"].head(5).to_string(index=False))


def run_sql_analysis() -> None:
    print("=" * 62)
    print("  UPI Transaction Pattern Analysis")
    print("  Phase 3 – SQL Business Analysis")
    print("=" * 62)

    df = pd.read_csv(CLEAN_FILE)
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])
    df["Amount"] = pd.to_numeric(df["Amount"])

    print(f"\n  Loaded {len(df):,} records from cleaned dataset.")
    print(f"\n  Running analysis queries (Pandas engine) …")
    results = run_pandas_analysis(df)

    print(f"\n  Saving results …")
    save_all_results(results)
    print_key_results(results)

    print(f"\n[DONE] SQL analysis complete.")
    print(f"       Results saved to: {SQL_RESULTS_DIR}")


if __name__ == "__main__":
    run_sql_analysis()

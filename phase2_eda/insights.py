"""
phase2_eda/insights.py
------------------------
Module 5 of Phase 2 EDA.

Derives and prints business-level insights from the dataset.
Saves results to reports/eda_business_insights.txt
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import REPORTS_DIR
from phase2_eda.eda_loader import load_clean_data

os.makedirs(REPORTS_DIR, exist_ok=True)
INSIGHTS_FILE = os.path.join(REPORTS_DIR, "eda_business_insights.txt")


def derive_insights(df: pd.DataFrame) -> list:
    """Compute and return a list of insight strings."""
    insights = []

    # ── 1. Transaction volume ─────────────────────────────────────────────────
    total = len(df)
    value = df["Amount"].sum()
    insights.append(
        f"INSIGHT 1 – Scale:\n"
        f"  The dataset covers {total:,} UPI transactions worth ₹{value:,.0f} "
        f"(≈ ₹{value/1e7:.2f} Crore) over Jan–Sep 2024."
    )

    # ── 2. Success/failure rate ───────────────────────────────────────────────
    sr = df["Status"].eq("SUCCESS").mean() * 100
    fr = df["Status"].eq("FAILED").mean()  * 100
    insights.append(
        f"INSIGHT 2 – Reliability:\n"
        f"  {sr:.1f}% of transactions succeeded. Failure rate is {fr:.1f}%, "
        f"which translates to {df['Status'].eq('FAILED').sum():,} failed transactions "
        f"and a potential revenue leakage of ₹{df[df['Status']=='FAILED']['Amount'].sum():,.0f}."
    )

    # ── 3. Peak hour ──────────────────────────────────────────────────────────
    peak_hr   = int(df["Hour"].value_counts().idxmax())
    peak_hr_n = df["Hour"].value_counts().max()
    tod_peak  = df["TimeOfDay"].value_counts().idxmax()
    insights.append(
        f"INSIGHT 3 – Peak Usage:\n"
        f"  Transactions peak at {peak_hr:02d}:00 hrs ({peak_hr_n:,} transactions). "
        f"'{tod_peak}' is the busiest time-of-day segment. "
        f"Banks and support teams should staff up during these hours."
    )

    # ── 4. Category insight ───────────────────────────────────────────────────
    top_cat_v = df.groupby("Category")["Amount"].sum().idxmax()
    top_cat_c = df["Category"].value_counts().idxmax()
    cat_fail  = df.groupby("Category").apply(
        lambda x: (x["Status"]=="FAILED").mean()*100, include_groups=False
    )
    high_fail_cat = cat_fail.idxmax()
    insights.append(
        f"INSIGHT 4 – Merchant Categories:\n"
        f"  '{top_cat_v}' generates the highest transaction value.\n"
        f"  '{top_cat_c}' has the most transactions by count.\n"
        f"  '{high_fail_cat}' has the highest failure rate "
        f"({cat_fail.max():.1f}%) — investigate payment gateway issues."
    )

    # ── 5. P2P vs P2M ─────────────────────────────────────────────────────────
    p2p_n  = (df["PaymentType"]=="P2P").sum()
    p2m_n  = (df["PaymentType"]=="P2M").sum()
    p2m_v  = df[df["PaymentType"]=="P2M"]["Amount"].sum()
    p2p_v  = df[df["PaymentType"]=="P2P"]["Amount"].sum()
    insights.append(
        f"INSIGHT 5 – Payment Type:\n"
        f"  P2M (merchant payments) account for {p2m_n/total*100:.1f}% of count "
        f"but {p2m_v/(p2m_v+p2p_v)*100:.1f}% of total value "
        f"(₹{p2m_v:,.0f}), indicating higher ticket sizes in merchant payments."
    )

    # ── 6. Top state and bank ─────────────────────────────────────────────────
    top_st = df["State"].value_counts().idxmax()
    top_bk = df["SenderBank"].value_counts().idxmax()
    top_ap = df["UPIApp"].value_counts().idxmax()
    insights.append(
        f"INSIGHT 6 – Geography & Banking:\n"
        f"  '{top_st}' leads in transaction count. "
        f"'{top_bk}' is the top sender bank. "
        f"'{top_ap}' is the most-used UPI app."
    )

    # ── 7. Weekend pattern ────────────────────────────────────────────────────
    wknd_avg = df[df["IsWeekend"]==1]["Amount"].mean()
    wkdy_avg = df[df["IsWeekend"]==0]["Amount"].mean()
    diff_pct = (wknd_avg - wkdy_avg) / wkdy_avg * 100
    insights.append(
        f"INSIGHT 7 – Weekend Spending:\n"
        f"  Weekend average transaction amount (₹{wknd_avg:,.0f}) is "
        f"{'higher' if diff_pct > 0 else 'lower'} than weekdays (₹{wkdy_avg:,.0f}) "
        f"by {abs(diff_pct):.1f}%, suggesting "
        f"{'leisure/entertainment spending peaks on weekends.' if diff_pct > 0 else 'most high-value payments occur on weekdays.'}"
    )

    # ── 8. High-value concentration ───────────────────────────────────────────
    hv = df[df["AmountBucket"]=="Very Large (>10000)"]
    insights.append(
        f"INSIGHT 8 – High-Value Transactions:\n"
        f"  {len(hv):,} transactions ({len(hv)/total*100:.1f}%) are high-value (>₹10,000), "
        f"accounting for ₹{hv['Amount'].sum()/value*100:.1f}% of total value. "
        f"Top categories: {', '.join(hv['Category'].value_counts().head(3).index.tolist())}."
    )

    # ── 9. Growth trend ───────────────────────────────────────────────────────
    month_order = ["January","February","March","April","May","June","July","August","September"]
    monthly_val = (
        df.groupby("Month", observed=True)["Amount"].sum()
          .reindex(month_order).dropna()
    )
    if len(monthly_val) >= 2:
        first_m, last_m = monthly_val.iloc[0], monthly_val.iloc[-1]
        growth = (last_m - first_m) / first_m * 100
        insights.append(
            f"INSIGHT 9 – Monthly Growth:\n"
            f"  Transaction value grew from ₹{first_m:,.0f} ({monthly_val.index[0]}) "
            f"to ₹{last_m:,.0f} ({monthly_val.index[-1]}), "
            f"a {'growth' if growth > 0 else 'decline'} of {abs(growth):.1f}%."
        )

    # ── 10. Device usage ──────────────────────────────────────────────────────
    dev_top = df["Device"].value_counts().idxmax()
    dev_pct = df["Device"].value_counts().iloc[0] / total * 100
    insights.append(
        f"INSIGHT 10 – Device Adoption:\n"
        f"  '{dev_top}' dominates with {dev_pct:.1f}% of transactions. "
        f"Feature Phone (*99#) usage reflects UPI adoption in semi-urban/rural areas."
    )

    return insights


def run_insights(df: pd.DataFrame = None) -> None:
    if df is None:
        df = load_clean_data()

    print("\n" + "=" * 62)
    print("  UPI TRANSACTION PATTERN ANALYSIS")
    print("  Phase 2 – Business Insights")
    print("=" * 62 + "\n")

    insights = derive_insights(df)
    report_lines = [
        "=" * 62,
        "  UPI TRANSACTION PATTERN ANALYSIS",
        "  Phase 2 – Key Business Insights",
        "=" * 62,
        ""
    ]

    for ins in insights:
        print(ins)
        print()
        report_lines.append(ins)
        report_lines.append("")

    report_lines.append("=" * 62)
    report_text = "\n".join(report_lines)

    with open(INSIGHTS_FILE, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[INFO] Business insights saved → {INSIGHTS_FILE}")


if __name__ == "__main__":
    run_insights()

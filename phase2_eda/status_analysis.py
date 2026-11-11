"""
phase2_eda/status_analysis.py
--------------------------------
Module 4 of Phase 2 EDA.

Analyses transaction success / failure patterns:
  - Overall success/fail/pending rates
  - Failure rate by category
  - Failure rate by bank
  - Failure rate by hour (peak failure times)
  - Failure rate by day of week
  - Failure rate by UPI app
  - Failure rate by payment type
  - Failure rate by amount bucket
  - Monthly failure trend

Charts: reports/figures/eda/  (S01–S07 prefix)
Data  : reports/eda_status_analysis.csv
"""

import os
import sys
import pandas as pd
import numpy  as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FIGURES_DIR, REPORTS_DIR
from phase2_eda.eda_loader import load_clean_data

EDA_FIGURES = os.path.join(FIGURES_DIR, "eda")
os.makedirs(EDA_FIGURES, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)
FIG_DPI = 130
STATUS_COLORS = {"SUCCESS":"#4CAF50","FAILED":"#F44336","PENDING":"#FF9800"}


def _save(name: str) -> None:
    path = os.path.join(EDA_FIGURES, name)
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")


# ── Chart S01: Overall status donut ──────────────────────────────────────────
def plot_overall_status(df: pd.DataFrame) -> None:
    status = df["Status"].value_counts()
    colors = [STATUS_COLORS.get(s,"#90A4AE") for s in status.index]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Overall Transaction Status Distribution", fontsize=13, fontweight="bold")

    # Donut
    wedges, texts, autotexts = axes[0].pie(
        status.values, labels=status.index,
        colors=colors, autopct="%1.1f%%",
        startangle=90, pctdistance=0.82,
        wedgeprops={"edgecolor":"white","linewidth":2}
    )
    # Draw centre hole
    centre = plt.Circle((0,0), 0.60, fc="white")
    axes[0].add_patch(centre)
    axes[0].text(0, 0, f"{len(df):,}\nTotal", ha="center", va="center",
                 fontsize=12, fontweight="bold", color="#333")
    axes[0].set_title("Status Distribution (Donut)")

    # Stacked bar per month
    month_order = ["January","February","March","April","May","June",
                   "July","August","September"]
    monthly = (
        df.groupby(["Month","Status"], observed=True)["TransactionID"]
          .count()
          .reset_index()
          .pivot(index="Month", columns="Status", values="TransactionID")
          .reindex(month_order)
          .fillna(0)
    )
    bottom = pd.Series([0]*len(monthly), index=monthly.index)
    for st in ["SUCCESS","FAILED","PENDING"]:
        if st in monthly.columns:
            axes[1].bar(monthly.index, monthly[st],
                        bottom=bottom, color=STATUS_COLORS[st],
                        label=st, edgecolor="white", alpha=0.85)
            bottom += monthly[st]
    axes[1].set_title("Monthly Transaction Count by Status")
    axes[1].set_ylabel("Transaction Count")
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].legend()

    _save("S01_overall_status.png")


# ── Chart S02: Failure rate by category ──────────────────────────────────────
def plot_failure_by_category(df: pd.DataFrame) -> None:
    cat_fail = (
        df.groupby("Category")
          .apply(lambda x: pd.Series({
              "FailureRate" : (x["Status"]=="FAILED").mean()*100,
              "Count"       : len(x),
              "FailedCount" : (x["Status"]=="FAILED").sum()
          }), include_groups=False)
          .sort_values("FailureRate", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(13, 6))
    colors = ["#E53935" if r > 12 else "#FFA726" if r > 8 else "#66BB6A"
              for r in cat_fail["FailureRate"]]
    bars = ax.bar(cat_fail.index, cat_fail["FailureRate"],
                  color=colors, edgecolor="white")
    ax.set_title("Transaction Failure Rate by Category (%)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Failure Rate (%)")
    ax.tick_params(axis="x", rotation=35)
    ax.axhline(df["Status"].eq("FAILED").mean()*100, color="#333",
               linestyle="--", linewidth=1.5, label="Overall Avg")
    ax.legend()
    for bar in bars:
        v = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, v+0.1,
                f"{v:.1f}%", ha="center", fontsize=9)
    _save("S02_failure_by_category.png")


# ── Chart S03: Failure rate by hour ──────────────────────────────────────────
def plot_failure_by_hour(df: pd.DataFrame) -> None:
    hourly_fail = (
        df.groupby("Hour")
          .apply(lambda x: (x["Status"]=="FAILED").mean()*100,
                 include_groups=False)
          .reset_index(name="FailureRate")
    )

    fig, ax = plt.subplots(figsize=(14, 5))
    avg_fail = df["Status"].eq("FAILED").mean()*100
    ax.bar(hourly_fail["Hour"], hourly_fail["FailureRate"],
           color="#EF9A9A", edgecolor="white", alpha=0.85)
    ax.plot(hourly_fail["Hour"], hourly_fail["FailureRate"],
            color="#B71C1C", marker="o", linewidth=1.5, markersize=4)
    ax.axhline(avg_fail, color="#1565C0", linestyle="--",
               linewidth=1.5, label=f"Overall Avg ({avg_fail:.1f}%)")
    ax.set_title("Transaction Failure Rate by Hour of Day", fontsize=13, fontweight="bold")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Failure Rate (%)")
    ax.set_xticks(range(0, 24))
    ax.legend()
    _save("S03_failure_by_hour.png")


# ── Chart S04: Failure rate by bank ──────────────────────────────────────────
def plot_failure_by_bank(df: pd.DataFrame) -> None:
    bank_fail = (
        df.groupby("SenderBank")
          .apply(lambda x: pd.Series({
              "FailureRate": (x["Status"]=="FAILED").mean()*100,
              "Count": len(x)
          }), include_groups=False)
          .sort_values("FailureRate", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    palette = sns.color_palette("RdYlGn_r", len(bank_fail))
    bars = ax.bar(bank_fail.index, bank_fail["FailureRate"],
                  color=palette, edgecolor="white")
    avg = df["Status"].eq("FAILED").mean()*100
    ax.axhline(avg, color="#1565C0", linestyle="--",
               linewidth=1.5, label=f"Overall Avg ({avg:.1f}%)")
    ax.set_title("Sender Bank Failure Rate (%)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Failure Rate (%)")
    ax.tick_params(axis="x", rotation=35)
    ax.legend()
    for bar in bars:
        v = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, v+0.05,
                f"{v:.1f}%", ha="center", fontsize=8)
    _save("S04_failure_by_bank.png")


# ── Chart S05: Amount bucket & status ────────────────────────────────────────
def plot_status_by_amount_bucket(df: pd.DataFrame) -> None:
    bucket_order = ["Small (≤500)","Medium (501–2000)",
                    "Large (2001–10000)","Very Large (>10000)"]
    pivot = (
        df.groupby(["AmountBucket","Status"], observed=True)["TransactionID"]
          .count()
          .reset_index()
          .pivot(index="AmountBucket", columns="Status", values="TransactionID")
          .reindex(bucket_order)
          .fillna(0)
    )
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle("Transaction Status by Amount Bucket", fontsize=13, fontweight="bold")

    bottom = pd.Series([0.0]*len(pivot_pct), index=pivot_pct.index)
    for st in ["SUCCESS","FAILED","PENDING"]:
        if st in pivot_pct.columns:
            axes[0].bar(pivot_pct.index, pivot_pct[st],
                        bottom=bottom, color=STATUS_COLORS[st],
                        label=st, edgecolor="white", alpha=0.85)
            bottom += pivot_pct[st]
    axes[0].set_title("Status % by Amount Bucket")
    axes[0].set_ylabel("Percentage (%)")
    axes[0].tick_params(axis="x", rotation=20)
    axes[0].legend()

    # Failure rate trend
    fail_rate = (pivot["FAILED"] / pivot.sum(axis=1) * 100).fillna(0)
    axes[1].plot(range(len(bucket_order)), fail_rate.reindex(bucket_order),
                 color="#E53935", marker="o", linewidth=2, markersize=8)
    axes[1].fill_between(range(len(bucket_order)),
                         fail_rate.reindex(bucket_order),
                         alpha=0.15, color="#E53935")
    axes[1].set_xticks(range(len(bucket_order)))
    axes[1].set_xticklabels(bucket_order, rotation=20)
    axes[1].set_title("Failure Rate by Amount Bucket")
    axes[1].set_ylabel("Failure Rate (%)")
    for i, v in enumerate(fail_rate.reindex(bucket_order)):
        axes[1].text(i, v+0.1, f"{v:.1f}%", ha="center", fontsize=10)
    _save("S05_status_amount_bucket.png")


# ── Save tabular output ───────────────────────────────────────────────────────
def save_status_report(df: pd.DataFrame) -> None:
    status_by_cat = (
        df.groupby(["Category","Status"])["TransactionID"]
          .count()
          .reset_index()
          .pivot(index="Category", columns="Status", values="TransactionID")
          .fillna(0)
    )
    status_by_cat["FailureRate%"] = (
        status_by_cat.get("FAILED",0) /
        status_by_cat.sum(axis=1) * 100
    ).round(2)
    out = os.path.join(REPORTS_DIR, "eda_status_analysis.csv")
    status_by_cat.to_csv(out)
    print(f"  Status analysis saved → {out}")


# ── Runner ────────────────────────────────────────────────────────────────────
def run_status_analysis(df: pd.DataFrame = None) -> None:
    if df is None:
        df = load_clean_data()

    print("\n  [Status Analysis] Generating charts …")
    plot_overall_status(df)
    plot_failure_by_category(df)
    plot_failure_by_hour(df)
    plot_failure_by_bank(df)
    plot_status_by_amount_bucket(df)
    save_status_report(df)
    print("  [Status Analysis] Done.\n")


if __name__ == "__main__":
    run_status_analysis()

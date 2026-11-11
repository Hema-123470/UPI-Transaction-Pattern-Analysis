"""
phase2_eda/trend_analysis.py
------------------------------
Module 2 of Phase 2 EDA.

Analyses and plots:
  - Daily transaction count and volume trend
  - Weekly transaction trend (week-of-year)
  - Monthly transaction count and volume (bar + line)
  - Day-of-week pattern (weekday vs weekend highlight)
  - Hourly distribution (peak hour identification)
  - Time-of-day distribution (Morning/Afternoon/Evening/Night)
  - Rolling 7-day average transaction value

Charts saved to reports/figures/eda/
"""

import os
import sys
import pandas as pd
import numpy  as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates  as mdates
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FIGURES_DIR
from phase2_eda.eda_loader import load_clean_data

EDA_FIGURES = os.path.join(FIGURES_DIR, "eda")
os.makedirs(EDA_FIGURES, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)
FIG_DPI = 130


def _save(name: str) -> None:
    path = os.path.join(EDA_FIGURES, name)
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")


# ── Chart 1: Daily trend ──────────────────────────────────────────────────────
def plot_daily_trend(df: pd.DataFrame) -> None:
    daily = df.groupby("TransactionDate").agg(
        Count=("TransactionID","count"),
        TotalAmount=("Amount","sum")
    ).reset_index()
    daily["Roll7"] = daily["TotalAmount"].rolling(7, min_periods=1).mean()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8), sharex=True)
    fig.suptitle("Daily UPI Transaction Trend (Jan–Sep 2024)", fontsize=14, fontweight="bold")

    ax1.plot(daily["TransactionDate"], daily["Count"],
             color="#1565C0", linewidth=1.2, alpha=0.8)
    ax1.fill_between(daily["TransactionDate"], daily["Count"],
                     alpha=0.15, color="#1565C0")
    ax1.set_ylabel("Transaction Count")
    ax1.set_title("Daily Transaction Count")

    ax2.bar(daily["TransactionDate"], daily["TotalAmount"] / 1e3,
            color="#4CAF50", alpha=0.6, width=0.8, label="Daily Volume")
    ax2.plot(daily["TransactionDate"], daily["Roll7"] / 1e3,
             color="#E64A19", linewidth=2, label="7-Day Rolling Avg")
    ax2.set_ylabel("Amount (₹ Thousands)")
    ax2.set_title("Daily Transaction Volume with 7-Day Rolling Average")
    ax2.legend()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)

    _save("T01_daily_trend.png")


# ── Chart 2: Weekly trend ─────────────────────────────────────────────────────
def plot_weekly_trend(df: pd.DataFrame) -> None:
    weekly = df.groupby("WeekOfYear").agg(
        Count=("TransactionID","count"),
        TotalAmount=("Amount","sum")
    ).reset_index()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(weekly["WeekOfYear"], weekly["Count"],
           color="#7B1FA2", alpha=0.75, edgecolor="white")
    ax2 = ax.twinx()
    ax2.plot(weekly["WeekOfYear"], weekly["TotalAmount"] / 1e6,
             color="#FF6F00", marker="s", linewidth=2, markersize=5)

    ax.set_xlabel("Week of Year")
    ax.set_ylabel("Transaction Count", color="#7B1FA2")
    ax2.set_ylabel("Total Amount (₹ Millions)", color="#FF6F00")
    ax.set_title("Weekly UPI Transaction Count & Volume (2024)", fontsize=13, fontweight="bold")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x:.1f}M"))

    _save("T02_weekly_trend.png")


# ── Chart 3: Monthly trend ────────────────────────────────────────────────────
def plot_monthly_trend(df: pd.DataFrame) -> None:
    month_order = ["January","February","March","April","May","June",
                   "July","August","September"]
    monthly = (
        df.groupby("Month", observed=True)
          .agg(Count=("TransactionID","count"), TotalAmount=("Amount","sum"))
          .reindex(month_order)
          .reset_index()
    )

    fig, ax1 = plt.subplots(figsize=(13, 6))
    x = range(len(monthly))

    bars = ax1.bar(x, monthly["Count"], color="#1976D2", alpha=0.8,
                   edgecolor="white", label="Transaction Count")
    for bar, v in zip(bars, monthly["Count"]):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5,
                 str(v), ha="center", fontsize=9, color="#1976D2")

    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly["Month"], rotation=30, ha="right")
    ax1.set_ylabel("Transaction Count", color="#1976D2")
    ax1.tick_params(axis="y", labelcolor="#1976D2")
    ax1.set_title("Monthly UPI Transaction Count & Volume", fontsize=13, fontweight="bold")

    ax2 = ax1.twinx()
    ax2.plot(x, monthly["TotalAmount"] / 1e6, color="#E53935",
             marker="o", linewidth=2.2, markersize=7, label="Total Value (₹M)")
    for xi, val in zip(x, monthly["TotalAmount"]):
        ax2.text(xi, val/1e6 + 0.3, f"₹{val/1e6:.1f}M",
                 ha="center", fontsize=8, color="#E53935")
    ax2.set_ylabel("Total Value (₹ Millions)", color="#E53935")
    ax2.tick_params(axis="y", labelcolor="#E53935")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x:.1f}M"))

    lines1, lbl1 = ax1.get_legend_handles_labels()
    lines2, lbl2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, lbl1+lbl2, loc="upper left")

    _save("T03_monthly_trend.png")


# ── Chart 4: Day-of-week ──────────────────────────────────────────────────────
def plot_day_of_week(df: pd.DataFrame) -> None:
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = (
        df.groupby("DayOfWeek", observed=True)
          .agg(Count=("TransactionID","count"), AvgAmt=("Amount","mean"))
          .reindex(dow_order)
    )

    colors = ["#FF7043" if d in ["Saturday","Sunday"] else "#1E88E5" for d in dow_order]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("UPI Transactions by Day of Week", fontsize=13, fontweight="bold")

    ax1.bar(dow.index, dow["Count"], color=colors, edgecolor="white")
    ax1.set_title("Transaction Count")
    ax1.set_ylabel("Count")
    ax1.tick_params(axis="x", rotation=30)
    for bar in ax1.patches:
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5,
                 f"{int(bar.get_height()):,}", ha="center", fontsize=9)

    ax2.bar(dow.index, dow["AvgAmt"], color=colors, edgecolor="white")
    ax2.set_title("Average Transaction Amount")
    ax2.set_ylabel("Amount (₹)")
    ax2.tick_params(axis="x", rotation=30)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x:,.0f}"))

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor="#1E88E5", label="Weekday"),
                       Patch(facecolor="#FF7043", label="Weekend")]
    ax1.legend(handles=legend_elements)

    _save("T04_day_of_week.png")


# ── Chart 5: Hourly heatmap + bar ────────────────────────────────────────────
def plot_hourly_analysis(df: pd.DataFrame) -> None:
    hourly = df.groupby("Hour").agg(
        Count=("TransactionID","count"),
        AvgAmt=("Amount","mean"),
        TotalAmt=("Amount","sum")
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle("Hourly UPI Transaction Pattern", fontsize=13, fontweight="bold")

    # Bar chart
    peak_hour = hourly.loc[hourly["Count"].idxmax(), "Hour"]
    bar_colors = ["#E53935" if h == peak_hour else "#42A5F5" for h in hourly["Hour"]]
    axes[0].bar(hourly["Hour"], hourly["Count"], color=bar_colors, edgecolor="white")
    axes[0].set_title(f"Transaction Count by Hour  (Peak: {int(peak_hour):02d}:00)")
    axes[0].set_xlabel("Hour of Day")
    axes[0].set_ylabel("Transaction Count")
    axes[0].set_xticks(range(0, 24))

    # Avg amount line
    axes[1].plot(hourly["Hour"], hourly["AvgAmt"],
                 color="#7B1FA2", marker="o", linewidth=2, markersize=5)
    axes[1].fill_between(hourly["Hour"], hourly["AvgAmt"], alpha=0.15, color="#7B1FA2")
    axes[1].set_title("Average Transaction Amount by Hour")
    axes[1].set_xlabel("Hour of Day")
    axes[1].set_ylabel("Average Amount (₹)")
    axes[1].set_xticks(range(0, 24))
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x:,.0f}"))

    _save("T05_hourly_analysis.png")


# ── Chart 6: Time of day ──────────────────────────────────────────────────────
def plot_time_of_day(df: pd.DataFrame) -> None:
    tod_order = ["Morning","Afternoon","Evening","Night"]
    tod = (
        df.groupby("TimeOfDay", observed=True)
          .agg(Count=("TransactionID","count"),
               TotalAmt=("Amount","sum"),
               AvgAmt=("Amount","mean"))
          .reindex(tod_order)
    )

    palette = {"Morning":"#FFB300","Afternoon":"#FB8C00","Evening":"#E53935","Night":"#283593"}
    colors  = [palette[t] for t in tod_order]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("UPI Transactions by Time of Day", fontsize=13, fontweight="bold")

    for ax, col, title, fmt in zip(
        axes,
        ["Count","TotalAmt","AvgAmt"],
        ["Transaction Count","Total Volume","Average Amount"],
        ["{:,.0f}","₹{:,.0f}","₹{:,.0f}"]
    ):
        bars = ax.bar(tod.index, tod[col], color=colors, edgecolor="white")
        ax.set_title(title)
        ax.set_ylabel(title)
        ax.tick_params(axis="x", rotation=20)
        for bar in bars:
            v = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, v + v*0.01,
                    fmt.format(v), ha="center", fontsize=8)

    _save("T06_time_of_day.png")


# ── Runner ────────────────────────────────────────────────────────────────────
def run_trend_analysis(df: pd.DataFrame = None) -> None:
    if df is None:
        df = load_clean_data()

    print("\n  [Trend Analysis] Generating charts …")
    plot_daily_trend(df)
    plot_weekly_trend(df)
    plot_monthly_trend(df)
    plot_day_of_week(df)
    plot_hourly_analysis(df)
    plot_time_of_day(df)
    print("  [Trend Analysis] Done.\n")


if __name__ == "__main__":
    run_trend_analysis()

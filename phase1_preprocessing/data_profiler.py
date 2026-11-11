"""
phase1_preprocessing/data_profiler.py
---------------------------------------
Generates a detailed statistical profile of the cleaned dataset
and saves summary visualisations to reports/figures/.

Charts produced:
  1. Amount distribution (histogram + KDE)
  2. Transaction count by Month
  3. Transaction count by Day of Week
  4. Transaction count by Status
  5. Top 10 Categories by transaction count
  6. Transaction count by UPI App
  7. Amount by PaymentType (boxplot)
  8. Heatmap – Hour vs DayOfWeek transaction density

Usage:
    python phase1_preprocessing/data_profiler.py
"""

import os
import sys
import pandas as pd
import numpy  as np
import matplotlib
matplotlib.use("Agg")                          # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CLEAN_FILE, FIGURES_DIR

os.makedirs(FIGURES_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
PALETTE = "Blues_d"
FIG_DPI = 120


def load_clean() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_FILE)
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])
    return df


# ── Chart helpers ─────────────────────────────────────────────────────────────

def save_fig(name: str) -> None:
    path = os.path.join(FIGURES_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI)
    plt.close()
    print(f"  Saved → {path}")


# ── Individual chart functions ────────────────────────────────────────────────

def plot_amount_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("UPI Transaction Amount Distribution", fontsize=14, fontweight="bold")

    axes[0].hist(df["Amount"], bins=50, color="#2196F3", edgecolor="white", alpha=0.85)
    axes[0].set_title("Histogram (all amounts)")
    axes[0].set_xlabel("Amount (₹)")
    axes[0].set_ylabel("Frequency")
    axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    # Log-scale for right-skewed view
    axes[1].hist(df["Amount"], bins=50, color="#FF5722", edgecolor="white", alpha=0.85, log=True)
    axes[1].set_title("Histogram (log Y-scale)")
    axes[1].set_xlabel("Amount (₹)")
    axes[1].set_ylabel("Frequency (log)")
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    save_fig("01_amount_distribution.png")


def plot_monthly_trend(df: pd.DataFrame) -> None:
    month_order = ["January","February","March","April","May","June",
                   "July","August","September"]
    monthly = df.groupby("Month").agg(
        TxnCount=("TransactionID", "count"),
        TotalAmount=("Amount", "sum")
    ).reindex(month_order).reset_index()

    fig, ax1 = plt.subplots(figsize=(12, 5))
    bars = ax1.bar(monthly["Month"], monthly["TxnCount"],
                   color="#1976D2", alpha=0.8, label="Transaction Count")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Transaction Count", color="#1976D2")
    ax1.tick_params(axis="y", labelcolor="#1976D2")
    ax1.set_title("Monthly UPI Transaction Count & Volume (2024)", fontsize=13, fontweight="bold")
    plt.xticks(rotation=30)

    ax2 = ax1.twinx()
    ax2.plot(monthly["Month"], monthly["TotalAmount"] / 1e6,
             color="#E64A19", marker="o", linewidth=2, label="Total Amount (₹ M)")
    ax2.set_ylabel("Total Amount (₹ Millions)", color="#E64A19")
    ax2.tick_params(axis="y", labelcolor="#E64A19")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.1f}M"))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    save_fig("02_monthly_trend.png")


def plot_day_of_week(df: pd.DataFrame) -> None:
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow = df["DayOfWeek"].value_counts().reindex(dow_order)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#1565C0" if d not in ["Saturday","Sunday"] else "#E53935" for d in dow_order]
    ax.bar(dow.index, dow.values, color=colors, edgecolor="white", alpha=0.85)
    ax.set_title("Transaction Count by Day of Week", fontsize=13, fontweight="bold")
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Transaction Count")

    save_fig("03_day_of_week.png")


def plot_status_distribution(df: pd.DataFrame) -> None:
    status_counts = df["Status"].value_counts()
    colors = {"SUCCESS": "#4CAF50", "FAILED": "#F44336", "PENDING": "#FF9800"}

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("UPI Transaction Status Distribution", fontsize=13, fontweight="bold")

    # Bar chart
    bar_colors = [colors.get(s, "#90A4AE") for s in status_counts.index]
    axes[0].bar(status_counts.index, status_counts.values, color=bar_colors, edgecolor="white")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Count by Status")
    for rect, v in zip(axes[0].patches, status_counts.values):
        axes[0].text(rect.get_x() + rect.get_width()/2, rect.get_height() + 20,
                     f"{v:,}", ha="center", fontsize=10)

    # Pie chart
    axes[1].pie(status_counts.values, labels=status_counts.index,
                colors=[colors.get(s, "#90A4AE") for s in status_counts.index],
                autopct="%1.1f%%", startangle=90,
                wedgeprops={"edgecolor": "white"})
    axes[1].set_title("Percentage by Status")

    save_fig("04_status_distribution.png")


def plot_category_analysis(df: pd.DataFrame) -> None:
    cat_data = (
        df.groupby("Category")
          .agg(Count=("TransactionID","count"), TotalAmt=("Amount","sum"))
          .sort_values("Count", ascending=False)
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("UPI Transactions by Category", fontsize=13, fontweight="bold")

    # Transaction count
    axes[0].barh(cat_data.index, cat_data["Count"],
                 color=sns.color_palette("Blues_r", len(cat_data)))
    axes[0].set_title("Transaction Count")
    axes[0].set_xlabel("Count")
    axes[0].invert_yaxis()

    # Total amount
    axes[1].barh(cat_data.index, cat_data["TotalAmt"] / 1e6,
                 color=sns.color_palette("Oranges_r", len(cat_data)))
    axes[1].set_title("Total Amount (₹ Millions)")
    axes[1].set_xlabel("Amount (₹ M)")
    axes[1].invert_yaxis()
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.1f}M"))

    save_fig("05_category_analysis.png")


def plot_upi_app_usage(df: pd.DataFrame) -> None:
    app_data = df["UPIApp"].value_counts()

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(app_data.index, app_data.values,
                  color=sns.color_palette("Set2", len(app_data)),
                  edgecolor="white")
    ax.set_title("Transaction Count by UPI App", fontsize=13, fontweight="bold")
    ax.set_xlabel("UPI App")
    ax.set_ylabel("Transaction Count")
    plt.xticks(rotation=30, ha="right")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{int(bar.get_height()):,}", ha="center", fontsize=8)

    save_fig("06_upi_app_usage.png")


def plot_amount_by_payment_type(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Amount Distribution by Payment Type", fontsize=13, fontweight="bold")

    sns.boxplot(data=df, x="PaymentType", y="Amount", hue="PaymentType",
                palette={"P2P":"#2196F3","P2M":"#FF5722"}, ax=axes[0], legend=False)
    axes[0].set_title("Boxplot")
    axes[0].set_ylabel("Amount (₹)")
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    sns.violinplot(data=df, x="PaymentType", y="Amount", hue="PaymentType",
                   palette={"P2P":"#2196F3","P2M":"#FF5722"}, ax=axes[1], cut=0, legend=False)
    axes[1].set_title("Violin Plot")
    axes[1].set_ylabel("")
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    save_fig("07_amount_payment_type.png")


def plot_hourly_heatmap(df: pd.DataFrame) -> None:
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = (
        df.groupby(["DayOfWeek", "Hour"])["TransactionID"]
          .count()
          .reset_index()
          .pivot(index="DayOfWeek", columns="Hour", values="TransactionID")
          .reindex(dow_order)
          .fillna(0)
    )

    fig, ax = plt.subplots(figsize=(16, 6))
    sns.heatmap(pivot, cmap="YlOrRd", linewidths=0.4, linecolor="white",
                annot=False, fmt=".0f", ax=ax,
                cbar_kws={"label": "Transaction Count"})
    ax.set_title("Transaction Density: Hour of Day vs Day of Week",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Hour of Day (0–23)")
    ax.set_ylabel("Day of Week")

    save_fig("08_hourly_heatmap.png")


# ── Statistical summary ───────────────────────────────────────────────────────

def print_statistical_summary(df: pd.DataFrame) -> None:
    print("\n" + "=" * 60)
    print("  STATISTICAL SUMMARY – Amount (₹)")
    print("=" * 60)
    desc = df["Amount"].describe()
    for stat, val in desc.items():
        print(f"  {stat:10s} : ₹{val:>12,.2f}")

    print("\n  Skewness  :", round(df["Amount"].skew(), 4))
    print("  Kurtosis  :", round(df["Amount"].kurt(), 4))

    print("\n" + "=" * 60)
    print("  TOP 5 CITIES BY TRANSACTION COUNT")
    print("=" * 60)
    print(df["City"].value_counts().head(5).to_string())


# ── Main ──────────────────────────────────────────────────────────────────────

def run_profiler() -> None:
    print("=" * 60)
    print("  UPI Transaction Pattern Analysis")
    print("  Phase 1 – Data Profiling & Visualisation")
    print("=" * 60)

    df = load_clean()
    print(f"\n  Loaded {len(df):,} records from cleaned dataset.\n")

    print("  Generating charts …")
    plot_amount_distribution(df)
    plot_monthly_trend(df)
    plot_day_of_week(df)
    plot_status_distribution(df)
    plot_category_analysis(df)
    plot_upi_app_usage(df)
    plot_amount_by_payment_type(df)
    plot_hourly_heatmap(df)
    print_statistical_summary(df)

    print("\n[DONE] Data profiling complete. All charts saved to reports/figures/\n")


if __name__ == "__main__":
    run_profiler()

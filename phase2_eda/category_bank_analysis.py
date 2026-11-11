"""
phase2_eda/category_bank_analysis.py
---------------------------------------
Module 3 of Phase 2 EDA.

Analyses:
  - Merchant category breakdown (count, value, avg, failure rate)
  - Bank-wise sender analysis (count, value, avg amount)
  - Bank-wise receiver analysis
  - Top sender-receiver bank pairs
  - UPI app usage comparison
  - Device type analysis
  - P2P vs P2M deep comparison
  - State-wise transaction patterns

Charts: reports/figures/eda/  (C01–C10 prefix)
Data  : reports/eda_category_bank.csv
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


def _save(name: str) -> None:
    path = os.path.join(EDA_FIGURES, name)
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")


# ── Category analysis ─────────────────────────────────────────────────────────
def plot_category_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Category × Status heatmap + category summary bar charts."""
    cat_summary = (
        df.groupby("Category")
          .agg(
              Count    =("TransactionID","count"),
              TotalAmt =("Amount","sum"),
              AvgAmt   =("Amount","mean"),
              SuccessN =("Status", lambda x: (x=="SUCCESS").sum()),
              FailedN  =("Status", lambda x: (x=="FAILED").sum()),
          )
          .assign(FailureRate=lambda x: (x["FailedN"]/x["Count"]*100).round(2))
          .sort_values("TotalAmt", ascending=False)
    )

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle("Merchant Category Analysis", fontsize=14, fontweight="bold")

    palette = sns.color_palette("Blues_r", len(cat_summary))

    # Total value
    axes[0].barh(cat_summary.index, cat_summary["TotalAmt"]/1e6,
                 color=palette, edgecolor="white")
    axes[0].set_title("Total Transaction Value (₹ Millions)")
    axes[0].set_xlabel("Value (₹ M)")
    axes[0].invert_yaxis()
    axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x:.1f}M"))
    for i, (idx, row) in enumerate(cat_summary.iterrows()):
        axes[0].text(row["TotalAmt"]/1e6 + 0.05, i,
                     f"₹{row['TotalAmt']/1e6:.1f}M", va="center", fontsize=8)

    # Failure rate
    fr_colors = ["#E53935" if r > 12 else "#FFA726" if r > 8 else "#66BB6A"
                 for r in cat_summary["FailureRate"]]
    axes[1].barh(cat_summary.index, cat_summary["FailureRate"],
                 color=fr_colors, edgecolor="white")
    axes[1].set_title("Failure Rate by Category (%)")
    axes[1].set_xlabel("Failure Rate (%)")
    axes[1].invert_yaxis()
    for i, r in enumerate(cat_summary["FailureRate"]):
        axes[1].text(r + 0.1, i, f"{r:.1f}%", va="center", fontsize=8)

    _save("C01_category_analysis.png")
    return cat_summary


def plot_category_scatter(df: pd.DataFrame) -> None:
    """Scatter: transaction count vs avg amount per category."""
    cat = df.groupby("Category").agg(
        Count=("TransactionID","count"),
        AvgAmt=("Amount","mean")
    ).reset_index()

    fig, ax = plt.subplots(figsize=(12, 7))
    scatter = ax.scatter(cat["Count"], cat["AvgAmt"],
                         s=cat["Count"]/5, alpha=0.7,
                         c=range(len(cat)), cmap="tab20")
    for _, row in cat.iterrows():
        ax.annotate(row["Category"],
                    (row["Count"], row["AvgAmt"]),
                    fontsize=8, ha="left", va="bottom",
                    xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("Transaction Count")
    ax.set_ylabel("Average Amount (₹)")
    ax.set_title("Category: Transaction Count vs Average Amount",
                 fontsize=13, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x:,.0f}"))
    _save("C02_category_scatter.png")


# ── Bank analysis ─────────────────────────────────────────────────────────────
def plot_bank_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Sender bank breakdown: count, total value, avg amount."""
    bank_summary = (
        df.groupby("SenderBank")
          .agg(Count=("TransactionID","count"),
               TotalAmt=("Amount","sum"),
               AvgAmt=("Amount","mean"))
          .sort_values("TotalAmt", ascending=False)
    )

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle("Bank-Wise Sender Analysis", fontsize=14, fontweight="bold")

    palette = sns.color_palette("Set2", len(bank_summary))

    for ax, col, title, fmt_fn in zip(
        axes,
        ["Count","TotalAmt","AvgAmt"],
        ["Transaction Count","Total Value (₹)","Avg Transaction Amount (₹)"],
        [lambda x: f"{x:,.0f}",
         lambda x: f"₹{x/1e6:.1f}M",
         lambda x: f"₹{x:,.0f}"]
    ):
        bars = ax.bar(range(len(bank_summary)), bank_summary[col],
                      color=palette, edgecolor="white")
        ax.set_xticks(range(len(bank_summary)))
        ax.set_xticklabels(bank_summary.index, rotation=40, ha="right", fontsize=8)
        ax.set_title(title)
        ax.set_ylabel(title)
        for bar in bars:
            v = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, v*1.01,
                    fmt_fn(v), ha="center", fontsize=7, rotation=90)

    _save("C03_bank_sender_analysis.png")
    return bank_summary


def plot_bank_heatmap(df: pd.DataFrame) -> None:
    """Heatmap of top sender-bank × receiver-bank transaction counts."""
    top_banks = df["SenderBank"].value_counts().head(8).index.tolist()
    sub = df[df["SenderBank"].isin(top_banks) & df["ReceiverBank"].isin(top_banks)]
    pivot = sub.pivot_table(
        index="SenderBank", columns="ReceiverBank",
        values="TransactionID", aggfunc="count", fill_value=0
    )

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="YlOrRd",
                linewidths=0.4, linecolor="white",
                cbar_kws={"label": "Transaction Count"}, ax=ax)
    ax.set_title("Sender Bank × Receiver Bank Transaction Count",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Receiver Bank")
    ax.set_ylabel("Sender Bank")
    _save("C04_bank_heatmap.png")


# ── UPI app analysis ──────────────────────────────────────────────────────────
def plot_upi_app_deep(df: pd.DataFrame) -> None:
    app_data = (
        df.groupby("UPIApp")
          .agg(Count=("TransactionID","count"),
               TotalAmt=("Amount","sum"),
               SuccessRate=("Status", lambda x: (x=="SUCCESS").mean()*100))
          .sort_values("Count", ascending=False)
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("UPI App Analysis", fontsize=13, fontweight="bold")

    palette = sns.color_palette("Paired", len(app_data))

    # Pie for count
    axes[0].pie(app_data["Count"], labels=app_data.index,
                colors=palette, autopct="%1.1f%%", startangle=90,
                wedgeprops={"edgecolor":"white","linewidth":1.5})
    axes[0].set_title("Transaction Count Share")

    # Bar for success rate
    sr_colors = ["#2E7D32" if r > 90 else "#F57F17" if r > 85 else "#C62828"
                 for r in app_data["SuccessRate"]]
    bars = axes[1].bar(app_data.index, app_data["SuccessRate"],
                       color=sr_colors, edgecolor="white")
    axes[1].set_title("Success Rate by UPI App (%)")
    axes[1].set_ylabel("Success Rate (%)")
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].set_ylim(75, 100)
    for bar in bars:
        v = bar.get_height()
        axes[1].text(bar.get_x()+bar.get_width()/2, v+0.1,
                     f"{v:.1f}%", ha="center", fontsize=9)

    _save("C05_upi_app_analysis.png")


# ── P2P vs P2M ────────────────────────────────────────────────────────────────
def plot_p2p_p2m(df: pd.DataFrame) -> None:
    ptype = (
        df.groupby("PaymentType")
          .agg(Count=("TransactionID","count"),
               TotalAmt=("Amount","sum"),
               AvgAmt=("Amount","mean"),
               SuccessRate=("Status", lambda x: (x=="SUCCESS").mean()*100))
    )

    # Monthly P2P vs P2M trend
    month_order = ["January","February","March","April","May","June",
                   "July","August","September"]
    monthly_pt = (
        df.groupby(["Month","PaymentType"], observed=True)["TransactionID"]
          .count()
          .reset_index()
          .pivot(index="Month", columns="PaymentType", values="TransactionID")
          .reindex(month_order)
          .fillna(0)
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("P2P vs P2M Transaction Analysis", fontsize=13, fontweight="bold")

    # Grouped bar
    x      = range(len(monthly_pt))
    width  = 0.35
    axes[0].bar([i-width/2 for i in x], monthly_pt.get("P2P", 0),
                width, color="#1976D2", alpha=0.85, label="P2P", edgecolor="white")
    axes[0].bar([i+width/2 for i in x], monthly_pt.get("P2M", 0),
                width, color="#E64A19", alpha=0.85, label="P2M", edgecolor="white")
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(monthly_pt.index, rotation=30, ha="right")
    axes[0].set_title("Monthly P2P vs P2M Count")
    axes[0].set_ylabel("Transaction Count")
    axes[0].legend()

    # Comparison table as grouped bars
    metrics  = ["Count","TotalAmt","AvgAmt"]
    labels   = ["Count","Total Value (₹)","Avg Amount (₹)"]
    norm_p2p = [ptype.loc["P2P", m] if "P2P" in ptype.index else 0 for m in metrics]
    norm_p2m = [ptype.loc["P2M", m] if "P2M" in ptype.index else 0 for m in metrics]

    # Normalize each metric to 100 for comparison
    totals   = [a+b if a+b > 0 else 1 for a, b in zip(norm_p2p, norm_p2m)]
    share_p2p = [a/t*100 for a, t in zip(norm_p2p, totals)]
    share_p2m = [b/t*100 for b, t in zip(norm_p2m, totals)]

    xb = range(len(metrics))
    axes[1].bar([i-0.2 for i in xb], share_p2p, 0.35,
                color="#1976D2", alpha=0.85, label="P2P", edgecolor="white")
    axes[1].bar([i+0.2 for i in xb], share_p2m, 0.35,
                color="#E64A19", alpha=0.85, label="P2M", edgecolor="white")
    axes[1].set_xticks(list(xb))
    axes[1].set_xticklabels(labels)
    axes[1].set_title("P2P vs P2M Share (%) by Metric")
    axes[1].set_ylabel("Share (%)")
    axes[1].legend()
    for ax in axes[1:]:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:.0f}%"))

    _save("C06_p2p_p2m_analysis.png")


# ── Device analysis ───────────────────────────────────────────────────────────
def plot_device_analysis(df: pd.DataFrame) -> None:
    dev = (
        df.groupby("Device")
          .agg(Count=("TransactionID","count"),
               AvgAmt=("Amount","mean"),
               SuccessRate=("Status", lambda x: (x=="SUCCESS").mean()*100))
          .sort_values("Count", ascending=False)
    )

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Device Type Analysis", fontsize=13, fontweight="bold")

    colors = ["#0288D1","#7CB342","#E64A19"][:len(dev)]
    axes[0].pie(dev["Count"], labels=dev.index,
                colors=colors, autopct="%1.1f%%",
                startangle=90, wedgeprops={"edgecolor":"white","linewidth":1.5})
    axes[0].set_title("Transaction Count by Device")

    axes[1].bar(dev.index, dev["SuccessRate"], color=colors, edgecolor="white")
    axes[1].set_title("Success Rate by Device (%)")
    axes[1].set_ylabel("Success Rate (%)")
    axes[1].set_ylim(75, 100)
    for bar in axes[1].patches:
        v = bar.get_height()
        axes[1].text(bar.get_x()+bar.get_width()/2, v+0.1,
                     f"{v:.1f}%", ha="center", fontsize=10)

    _save("C07_device_analysis.png")


# ── State analysis ────────────────────────────────────────────────────────────
def plot_state_analysis(df: pd.DataFrame) -> None:
    state_data = (
        df.groupby("State")
          .agg(Count=("TransactionID","count"),
               TotalAmt=("Amount","sum"),
               AvgAmt=("Amount","mean"))
          .sort_values("TotalAmt", ascending=False)
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("State-Wise Transaction Analysis", fontsize=13, fontweight="bold")

    palette = sns.color_palette("tab20", len(state_data))
    axes[0].barh(state_data.index, state_data["Count"], color=palette, edgecolor="white")
    axes[0].set_title("Transaction Count by State")
    axes[0].set_xlabel("Count")
    axes[0].invert_yaxis()

    axes[1].barh(state_data.index, state_data["TotalAmt"]/1e6,
                 color=palette, edgecolor="white")
    axes[1].set_title("Total Value by State (₹ Millions)")
    axes[1].set_xlabel("Value (₹ M)")
    axes[1].invert_yaxis()
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x:.1f}M"))

    _save("C08_state_analysis.png")


# ── Save tabular results ──────────────────────────────────────────────────────
def save_tabular_results(cat_summary: pd.DataFrame, bank_summary: pd.DataFrame) -> None:
    out_file = os.path.join(REPORTS_DIR, "eda_category_bank.csv")
    cat_summary.to_csv(out_file)
    print(f"  Category summary saved → {out_file}")

    bank_file = os.path.join(REPORTS_DIR, "eda_bank_summary.csv")
    bank_summary.to_csv(bank_file)
    print(f"  Bank summary saved     → {bank_file}")


# ── Runner ────────────────────────────────────────────────────────────────────
def run_category_bank_analysis(df: pd.DataFrame = None) -> None:
    if df is None:
        df = load_clean_data()

    print("\n  [Category & Bank Analysis] Generating charts …")
    cat_summary  = plot_category_heatmap(df)
    plot_category_scatter(df)
    bank_summary = plot_bank_analysis(df)
    plot_bank_heatmap(df)
    plot_upi_app_deep(df)
    plot_p2p_p2m(df)
    plot_device_analysis(df)
    plot_state_analysis(df)
    save_tabular_results(cat_summary, bank_summary)
    print("  [Category & Bank Analysis] Done.\n")


if __name__ == "__main__":
    run_category_bank_analysis()

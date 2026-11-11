"""
phase3_sql_powerbi/html_dashboard.py
--------------------------------------
Interactive 4-page HTML dashboard — NO Power BI needed.
Opens in Chrome, Edge, Firefox — any browser.

Pages:
  Page 1 – Overall Transaction Overview
  Page 2 – Time-Based Analysis
  Page 3 – Merchant & Bank Analysis
  Page 4 – Transaction Status Analysis

Output : reports/UPI_Dashboard.html
Usage  : python phase3_sql_powerbi/html_dashboard.py
"""

import os, sys
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CLEAN_FILE, REPORTS_DIR

os.makedirs(REPORTS_DIR, exist_ok=True)
OUT_FILE = os.path.join(REPORTS_DIR, "UPI_Dashboard.html")

# ── Theme colours ─────────────────────────────────────────────────────────────
BG     = "#0D1B2A"
CARD   = "#1B2A40"
GOLD   = "#F5A623"
BLUE   = "#1976D2"
GREEN  = "#4CAF50"
RED    = "#F44336"
AMBER  = "#FF9800"
ORANGE = "#E64A19"
TEXT   = "#E0E0E0"
GRID   = "#2A3A50"

BASE = dict(paper_bgcolor=BG, plot_bgcolor=CARD,
            font=dict(color=TEXT, family="Segoe UI,Arial"),
            title_font=dict(color=GOLD, size=14),
            margin=dict(l=50, r=30, t=50, b=50))


def _ax(fig):
    fig.update_xaxes(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID)
    return fig


def load_data():
    df = pd.read_csv(CLEAN_FILE)
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])
    df["Amount"]          = pd.to_numeric(df["Amount"])
    return df


# ──────────────────────────────────────────────────────────────────────────────
# Helper: render figure to HTML fragment
# ──────────────────────────────────────────────────────────────────────────────
def _fh(fig):
    return fig.to_html(full_html=False, include_plotlyjs=False,
                       config={"displayModeBar": True,
                               "modeBarButtonsToRemove": ["lasso2d", "select2d"]})


def _row(pairs):
    """pairs = [(fig, pct_width), ...]  pct_width values should sum ~100."""
    cells = "".join(
        f'<div style="flex:{p}%;min-width:0;padding:5px">{_fh(f)}</div>'
        for f, p in pairs
    )
    return f'<div style="display:flex">{cells}</div>'


def _kpi(items):
    """items = [(value_html, label), ...]"""
    cards = "".join(
        f'<div class="kc"><div class="kv">{v}</div><div class="kl">{l}</div></div>'
        for v, l in items
    )
    return f'<div class="krow">{cards}</div>'


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Overall Transaction Overview
# ══════════════════════════════════════════════════════════════════════════════
def page1(df):
    MO = ["January","February","March","April","May","June",
          "July","August","September"]

    mon = (df.groupby("Month", observed=True)
             .agg(n=("Amount","count"), v=("Amount","sum"))
             .reindex(MO).reset_index())

    sc  = df["Status"].value_counts()
    pc  = df["PaymentType"].value_counts()
    cv  = df.groupby("Category")["Amount"].sum().sort_values().tail(10)
    sv  = df["State"].value_counts().head(10)

    total = len(df)
    tval  = df["Amount"].sum()
    avg   = df["Amount"].mean()
    sr    = (df["Status"]=="SUCCESS").mean()*100
    leak  = df[df["Status"]=="FAILED"]["Amount"].sum()

    # Monthly dual-axis
    f1 = make_subplots(specs=[[{"secondary_y": True}]])
    f1.add_trace(go.Bar(x=mon["Month"], y=mon["n"],
                        name="Count", marker_color=BLUE, opacity=0.85),
                 secondary_y=False)
    f1.add_trace(go.Scatter(x=mon["Month"], y=mon["v"]/1e6,
                            name="Value ₹M", mode="lines+markers",
                            line=dict(color=GOLD, width=2.5), marker_size=7),
                 secondary_y=True)
    f1.update_layout(**BASE, title="Monthly Transaction Count & Value",
                     legend=dict(bgcolor=CARD), height=320)
    f1.update_yaxes(title_text="Count",    secondary_y=False,
                    gridcolor=GRID, color=BLUE)
    f1.update_yaxes(title_text="Value ₹M", secondary_y=True,
                    gridcolor=GRID, color=GOLD)
    f1.update_xaxes(gridcolor=GRID)

    # Status donut
    f2 = go.Figure(go.Pie(labels=sc.index, values=sc.values, hole=0.55,
                           marker=dict(colors=[GREEN,RED,AMBER],
                                       line=dict(color=BG,width=2)),
                           textinfo="label+percent",
                           textfont=dict(color=TEXT)))
    f2.add_annotation(text=f"{total:,}<br>Total", x=0.5, y=0.5,
                      font=dict(size=13, color=GOLD), showarrow=False)
    f2.update_layout(**BASE, title="Transaction Status",
                     showlegend=False, height=280)

    # P2P/P2M donut
    f3 = go.Figure(go.Pie(labels=pc.index, values=pc.values, hole=0.55,
                           marker=dict(colors=[BLUE,ORANGE],
                                       line=dict(color=BG,width=2)),
                           textinfo="label+percent",
                           textfont=dict(color=TEXT)))
    f3.update_layout(**BASE, title="P2P vs P2M Split",
                     showlegend=False, height=280)

    # Top categories
    f4 = go.Figure(go.Bar(x=cv.values/1e6, y=cv.index, orientation="h",
                           marker=dict(color=list(range(len(cv))),
                                       colorscale=[[0,BLUE],[1,GOLD]]),
                           text=[f"₹{v/1e6:.1f}M" for v in cv.values],
                           textposition="outside",
                           textfont=dict(color=TEXT, size=10)))
    f4.update_layout(**BASE, title="Top Categories by Transaction Value",
                     xaxis_title="Value (₹M)", height=360)
    f4.update_yaxes(autorange="reversed", gridcolor=GRID)
    f4.update_xaxes(gridcolor=GRID)

    # State bar
    f5 = go.Figure(go.Bar(x=sv.index, y=sv.values,
                           marker_color=BLUE, opacity=0.85,
                           text=sv.values, textposition="outside",
                           textfont=dict(color=TEXT, size=9)))
    f5.update_layout(**BASE, title="Transactions by State",
                     yaxis_title="Count", height=300)
    _ax(f5)

    k = _kpi([
        (f"{total:,}", "Total Transactions"),
        (f"₹{tval/1e7:.2f} Cr", "Total Value"),
        (f"₹{avg:,.0f}", "Avg Amount"),
        (f'<span style="color:{GREEN}">{sr:.1f}%</span>', "Success Rate"),
        (f'<span style="color:{RED}">{100-sr:.1f}%</span>', "Failure Rate"),
        (f'<span style="color:{AMBER}">₹{leak/1e7:.2f} Cr</span>', "Revenue Leakage"),
    ])
    return k + _row([(f1,100)]) + _row([(f2,33),(f3,33),(f5,34)]) + _row([(f4,100)])


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Time-Based Analysis
# ══════════════════════════════════════════════════════════════════════════════
def page2(df):
    MO  = ["January","February","March","April","May","June",
           "July","August","September"]
    DOW = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    TOD = ["Morning","Afternoon","Evening","Night"]

    hr  = df.groupby("Hour").agg(n=("Amount","count"), a=("Amount","mean")).reset_index()
    ph  = int(hr.loc[hr["n"].idxmax(), "Hour"])

    dw  = (df.groupby("DayOfWeek", observed=True)
             .agg(n=("Amount","count"), a=("Amount","mean"))
             .reindex(DOW).reset_index())

    tod = (df.groupby("TimeOfDay", observed=True)
             .agg(n=("Amount","count"))
             .reindex(TOD).reset_index())

    ms  = (df.groupby(["Month","Status"], observed=True)["TransactionID"]
             .count().reset_index()
             .pivot(index="Month", columns="Status", values="TransactionID")
             .reindex(MO).fillna(0))

    hm  = (df.groupby(["DayOfWeek","Hour"], observed=True)["TransactionID"]
             .count().reset_index()
             .pivot(index="DayOfWeek", columns="Hour", values="TransactionID")
             .reindex(DOW).fillna(0))

    pm  = str(df.groupby("Month", observed=True).size().idxmax())
    pd_ = str(df.groupby("DayOfWeek", observed=True).size().idxmax())

    # Hourly count bar
    hcols = [RED if h==ph else BLUE for h in hr["Hour"]]
    f1 = go.Figure(go.Bar(x=hr["Hour"], y=hr["n"], marker_color=hcols,
                           hovertemplate="Hour %{x}:00  Count:%{y}<extra></extra>"))
    f1.update_layout(**BASE, title=f"Count by Hour  (Peak: {ph:02d}:00)",
                     yaxis_title="Count", height=300)
    f1.update_xaxes(tickvals=list(range(0,24)), gridcolor=GRID)
    f1.update_yaxes(gridcolor=GRID)

    # Hourly avg amount
    f2 = go.Figure(go.Scatter(x=hr["Hour"], y=hr["a"], mode="lines+markers",
                               line=dict(color=GOLD,width=2.5), marker_size=6,
                               fill="tozeroy", fillcolor="rgba(245,166,35,0.1)"))
    f2.update_layout(**BASE, title="Avg Amount by Hour",
                     yaxis_title="Avg Amount (₹)", height=300)
    f2.update_xaxes(tickvals=list(range(0,24)), gridcolor=GRID)
    f2.update_yaxes(gridcolor=GRID)

    # Day of week
    dcols = [ORANGE if d in ["Saturday","Sunday"] else BLUE for d in DOW]
    f3 = go.Figure(go.Bar(x=dw["DayOfWeek"], y=dw["n"], marker_color=dcols,
                           text=dw["n"], textposition="outside",
                           textfont=dict(color=TEXT, size=9)))
    f3.update_layout(**BASE, title="Count by Day of Week",
                     yaxis_title="Count", height=300)
    _ax(f3)

    # Time of day
    f4 = go.Figure(go.Bar(x=tod["TimeOfDay"], y=tod["n"],
                           marker_color=[GOLD,ORANGE,RED,"#283593"],
                           text=tod["n"], textposition="outside",
                           textfont=dict(color=TEXT, size=11)))
    f4.update_layout(**BASE, title="Transactions by Time of Day",
                     yaxis_title="Count", height=300)
    _ax(f4)

    # Monthly by status stacked
    f5 = go.Figure()
    for st, c in [("SUCCESS",GREEN),("FAILED",RED),("PENDING",AMBER)]:
        if st in ms.columns:
            f5.add_trace(go.Bar(x=ms.index, y=ms[st],
                                name=st, marker_color=c, opacity=0.85))
    f5.update_layout(**BASE, barmode="stack",
                     title="Monthly Count by Status",
                     yaxis_title="Count",
                     legend=dict(bgcolor=CARD), height=300)
    _ax(f5)

    # Heatmap
    f6 = go.Figure(go.Heatmap(z=hm.values, x=list(range(24)), y=hm.index.tolist(),
                               colorscale="YlOrRd",
                               hovertemplate="Day:%{y}  Hr:%{x}  Count:%{z}<extra></extra>"))
    f6.update_layout(**BASE, title="Transaction Density  Hour × Day",
                     height=330)
    f6.update_xaxes(title_text="Hour", tickvals=list(range(0,24,2)), gridcolor=GRID)
    f6.update_yaxes(title_text="", gridcolor=GRID)

    we = df[df["IsWeekend"]==1]["Amount"].mean()
    wd = df[df["IsWeekend"]==0]["Amount"].mean()

    k = _kpi([
        (f'<span style="color:{GOLD}">{ph:02d}:00</span>', "Peak Hour"),
        (f'<span style="color:{GOLD}">{pd_}</span>',        "Peak Day"),
        (f'<span style="color:{GOLD}">{pm}</span>',          "Peak Month"),
        (f"{tod['n'].max():,}",                              "Night Transactions"),
        (f"₹{we:,.0f}",                                      "Weekend Avg"),
        (f"₹{wd:,.0f}",                                      "Weekday Avg"),
    ])
    return k + _row([(f1,50),(f2,50)]) + _row([(f3,50),(f4,50)]) + \
               _row([(f5,45),(f6,55)])


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Merchant & Bank Analysis
# ══════════════════════════════════════════════════════════════════════════════
def page3(df):
    MO = ["January","February","March","April","May","June",
          "July","August","September"]

    cat = (df.groupby("Category")
             .agg(n=("Amount","count"), v=("Amount","sum"), a=("Amount","mean"),
                  fr=("Status", lambda x: round((x=="FAILED").mean()*100,2)))
             .sort_values("v", ascending=False))

    bk = (df.groupby("SenderBank")
            .agg(n=("Amount","count"), v=("Amount","sum"),
                 fr=("Status", lambda x: round((x=="FAILED").mean()*100,2)))
            .sort_values("n", ascending=False))

    ap = (df.groupby("UPIApp")
            .agg(n=("Amount","count"),
                 sr=("Status", lambda x: round((x=="SUCCESS").mean()*100,2)))
            .sort_values("n", ascending=False))

    pt = (df.groupby(["Month","PaymentType"], observed=True)["TransactionID"]
            .count().reset_index()
            .pivot(index="Month", columns="PaymentType", values="TransactionID")
            .reindex(MO).fillna(0))

    # Category value (horizontal)
    f1 = go.Figure(go.Bar(x=cat["v"].values/1e6, y=cat.index, orientation="h",
                           marker=dict(color=list(range(len(cat))),
                                       colorscale=[[0,BLUE],[1,GOLD]]),
                           text=[f"₹{v/1e6:.1f}M" for v in cat["v"].values],
                           textposition="outside",
                           textfont=dict(color=TEXT, size=9)))
    f1.update_layout(**BASE, title="Category by Total Value",
                     xaxis_title="Value (₹M)", height=380)
    f1.update_yaxes(autorange="reversed", gridcolor=GRID)
    f1.update_xaxes(gridcolor=GRID)

    # Category scatter
    f2 = go.Figure(go.Scatter(
        x=cat["n"].values, y=cat["a"].values, mode="markers+text",
        marker=dict(size=cat["v"].values/cat["v"].max()*60+10,
                    color=cat["v"].values, colorscale=[[0,BLUE],[1,GOLD]],
                    opacity=0.8, line=dict(color=BG,width=1)),
        text=cat.index, textposition="top center",
        textfont=dict(size=9, color=TEXT),
        hovertemplate="<b>%{text}</b><br>Count:%{x}  Avg:₹%{y:,.0f}<extra></extra>"))
    f2.update_layout(**BASE, title="Category: Count vs Avg Amount",
                     xaxis_title="Count", yaxis_title="Avg Amount (₹)", height=380)
    _ax(f2)

    # Bank count
    f3 = go.Figure(go.Bar(x=bk.index, y=bk["n"].values,
                           marker_color=BLUE, opacity=0.85,
                           text=bk["n"].values, textposition="outside",
                           textfont=dict(color=TEXT, size=8)))
    f3.update_layout(**BASE, title="Sender Bank Transaction Count",
                     yaxis_title="Count", height=300)
    f3.update_xaxes(tickangle=30, gridcolor=GRID)
    f3.update_yaxes(gridcolor=GRID)

    # UPI app pie
    f4 = go.Figure(go.Pie(labels=ap.index, values=ap["n"].values, hole=0.4,
                           textinfo="label+percent",
                           marker=dict(line=dict(color=BG,width=1.5))))
    f4.update_layout(**BASE, title="UPI App Market Share",
                     height=300, showlegend=False)

    # Category failure rate
    fc = [RED if r>10 else AMBER if r>8 else GREEN for r in cat["fr"].values]
    f5 = go.Figure(go.Bar(x=cat.index, y=cat["fr"].values,
                           marker_color=fc,
                           text=[f"{r:.1f}%" for r in cat["fr"].values],
                           textposition="outside",
                           textfont=dict(color=TEXT, size=9)))
    f5.update_layout(**BASE, title="Failure Rate by Category (%)",
                     yaxis_title="Failure Rate (%)", height=300)
    f5.update_xaxes(tickangle=30, gridcolor=GRID)
    f5.update_yaxes(gridcolor=GRID)

    # Bank failure rate
    fb = [RED if r>10 else AMBER if r>9 else GREEN for r in bk["fr"].values]
    f6 = go.Figure(go.Bar(x=bk.index, y=bk["fr"].values,
                           marker_color=fb,
                           text=[f"{r:.1f}%" for r in bk["fr"].values],
                           textposition="outside",
                           textfont=dict(color=TEXT, size=9)))
    f6.update_layout(**BASE, title="Bank Failure Rate (%)",
                     yaxis_title="Failure Rate (%)", height=300)
    f6.update_xaxes(tickangle=30, gridcolor=GRID)
    f6.update_yaxes(gridcolor=GRID)

    # P2P vs P2M monthly
    f7 = go.Figure()
    for col, c in [("P2P",BLUE),("P2M",ORANGE)]:
        if col in pt.columns:
            f7.add_trace(go.Bar(x=pt.index, y=pt[col],
                                name=col, marker_color=c, opacity=0.85))
    f7.update_layout(**BASE, barmode="group",
                     title="P2P vs P2M by Month",
                     yaxis_title="Count",
                     legend=dict(bgcolor=CARD), height=300)
    _ax(f7)

    k = _kpi([
        (f'<span style="color:{GOLD}">{cat.index[0]}</span>', "Top Category (Value)"),
        (f'<span style="color:{GOLD}">{bk.index[0]}</span>',  "Top Sender Bank"),
        (f'<span style="color:{GOLD}">{ap.index[0]}</span>',  "Top UPI App"),
        (f"{len(cat)}", "Categories"),
        (f"{len(bk)}",  "Banks"),
        (f"{len(ap)}",  "UPI Apps"),
    ])
    return k + _row([(f1,42),(f2,58)]) + _row([(f3,58),(f4,42)]) + \
               _row([(f5,50),(f6,50)]) + _row([(f7,100)])


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Transaction Status Analysis
# ══════════════════════════════════════════════════════════════════════════════
def page4(df):
    MO  = ["January","February","March","April","May","June",
           "July","August","September"]
    BO  = ["Small (≤500)","Medium (501–2000)",
           "Large (2001–10000)","Very Large (>10000)"]

    sc   = df["Status"].value_counts()
    fd   = df[df["Status"]=="FAILED"]
    leak = fd["Amount"].sum()
    avf  = fd["Amount"].mean()
    ovf  = round((df["Status"]=="FAILED").mean()*100, 2)

    cf = (df.groupby("Category")["Status"]
            .apply(lambda x: round((x=="FAILED").mean()*100,2), include_groups=False)
            .sort_values(ascending=False))

    bf = (df.groupby("SenderBank")["Status"]
            .apply(lambda x: round((x=="FAILED").mean()*100,2), include_groups=False)
            .sort_values(ascending=False))

    hf = (df.groupby("Hour")["Status"]
            .apply(lambda x: round((x=="FAILED").mean()*100,2), include_groups=False)
            .reset_index(name="fr"))

    af = (df.groupby("UPIApp")["Status"]
            .apply(lambda x: round((x=="FAILED").mean()*100,2), include_groups=False)
            .sort_values(ascending=False))

    bkf = (df.groupby("AmountBucket", observed=True)["Status"]
             .apply(lambda x: round((x=="FAILED").mean()*100,2), include_groups=False)
             .reindex(BO))

    ms = (df.groupby(["Month","Status"], observed=True)["TransactionID"]
            .count().reset_index()
            .pivot(index="Month", columns="Status", values="TransactionID")
            .reindex(MO).fillna(0))

    # Status donut
    f1 = go.Figure(go.Pie(labels=sc.index, values=sc.values, hole=0.58,
                           marker=dict(colors=[GREEN,RED,AMBER],
                                       line=dict(color=BG,width=2)),
                           textinfo="label+value+percent",
                           textfont=dict(color=TEXT)))
    f1.add_annotation(text=f"{ovf}%<br>Failure", x=0.5, y=0.5,
                      font=dict(size=14, color=RED), showarrow=False)
    f1.update_layout(**BASE, title="Status Distribution",
                     showlegend=True, legend=dict(bgcolor=CARD), height=320)

    # Hourly failure
    f2 = go.Figure()
    f2.add_trace(go.Bar(x=hf["Hour"], y=hf["fr"],
                        marker_color=RED, opacity=0.55, name="Failure %"))
    f2.add_trace(go.Scatter(x=hf["Hour"], y=hf["fr"],
                            mode="lines+markers",
                            line=dict(color=RED,width=2), marker_size=4))
    f2.add_hline(y=ovf, line_dash="dash", line_color=GOLD,
                 annotation_text=f"Avg {ovf}%",
                 annotation_font=dict(color=GOLD, size=10))
    f2.update_layout(**BASE, title="Failure Rate by Hour",
                     yaxis_title="Failure Rate (%)", showlegend=False, height=320)
    f2.update_xaxes(tickvals=list(range(0,24)), gridcolor=GRID)
    f2.update_yaxes(gridcolor=GRID)

    # Category failure (horizontal)
    cc = [RED if r>10 else AMBER if r>8 else GREEN for r in cf.values]
    f3 = go.Figure(go.Bar(x=cf.values, y=cf.index, orientation="h",
                           marker_color=cc,
                           text=[f"{r:.1f}%" for r in cf.values],
                           textposition="outside",
                           textfont=dict(color=TEXT, size=9)))
    f3.add_vline(x=ovf, line_dash="dash", line_color=GOLD,
                 annotation_text=f"Avg {ovf}%",
                 annotation_font=dict(color=GOLD, size=10))
    f3.update_layout(**BASE, title="Failure Rate by Category",
                     xaxis_title="Failure Rate (%)", height=360)
    f3.update_yaxes(autorange="reversed", gridcolor=GRID)
    f3.update_xaxes(gridcolor=GRID)

    # Bank failure
    bc = [RED if r>10 else AMBER if r>9 else GREEN for r in bf.values]
    f4 = go.Figure(go.Bar(x=bf.index, y=bf.values, marker_color=bc,
                           text=[f"{r:.1f}%" for r in bf.values],
                           textposition="outside",
                           textfont=dict(color=TEXT, size=9)))
    f4.add_hline(y=ovf, line_dash="dash", line_color=GOLD,
                 annotation_text=f"Avg {ovf}%",
                 annotation_font=dict(color=GOLD, size=10))
    f4.update_layout(**BASE, title="Sender Bank Failure Rate (%)",
                     yaxis_title="Failure Rate (%)", height=320)
    f4.update_xaxes(tickangle=30, gridcolor=GRID)
    f4.update_yaxes(gridcolor=GRID)

    # UPI app failure
    ac = [RED if r>10 else AMBER if r>9 else GREEN for r in af.values]
    f5 = go.Figure(go.Bar(x=af.index, y=af.values, marker_color=ac,
                           text=[f"{r:.1f}%" for r in af.values],
                           textposition="outside",
                           textfont=dict(color=TEXT, size=9)))
    f5.add_hline(y=ovf, line_dash="dash", line_color=GOLD)
    f5.update_layout(**BASE, title="UPI App Failure Rate (%)",
                     yaxis_title="Failure Rate (%)", height=300)
    f5.update_xaxes(tickangle=25, gridcolor=GRID)
    f5.update_yaxes(gridcolor=GRID)

    # Amount bucket failure
    f6 = go.Figure(go.Scatter(x=BO, y=bkf.values,
                               mode="lines+markers+text",
                               line=dict(color=RED,width=2.5), marker_size=10,
                               text=[f"{r:.1f}%" for r in bkf.values],
                               textposition="top center",
                               textfont=dict(color=TEXT, size=11),
                               fill="tozeroy",
                               fillcolor="rgba(244,67,54,0.1)"))
    f6.update_layout(**BASE, title="Failure Rate by Amount Bucket",
                     yaxis_title="Failure Rate (%)", height=300)
    _ax(f6)

    # Monthly stacked
    f7 = go.Figure()
    for st, c in [("SUCCESS",GREEN),("FAILED",RED),("PENDING",AMBER)]:
        if st in ms.columns:
            f7.add_trace(go.Bar(x=ms.index, y=ms[st],
                                name=st, marker_color=c, opacity=0.85))
    f7.update_layout(**BASE, barmode="stack",
                     title="Monthly Transactions by Status",
                     yaxis_title="Count",
                     legend=dict(bgcolor=CARD), height=300)
    _ax(f7)

    k = _kpi([
        (f'<span style="color:{GREEN}">{sc.get("SUCCESS",0):,}</span>', "Successful"),
        (f'<span style="color:{RED}">{sc.get("FAILED",0):,}</span>',    "Failed"),
        (f'<span style="color:{AMBER}">{sc.get("PENDING",0):,}</span>', "Pending"),
        (f'<span style="color:{RED}">₹{leak/1e7:.2f} Cr</span>',        "Revenue Leakage"),
        (f'<span style="color:{RED}">₹{avf:,.0f}</span>',               "Avg Failed Amount"),
        (f'<span style="color:{RED}">{ovf}%</span>',                    "Overall Failure Rate"),
    ])
    return k + _row([(f1,35),(f2,65)]) + _row([(f3,50),(f4,50)]) + \
               _row([(f5,50),(f6,50)]) + _row([(f7,100)])


# ══════════════════════════════════════════════════════════════════════════════
# CSS + JS
# ══════════════════════════════════════════════════════════════════════════════
CSS = f"""<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{BG};color:{TEXT};font-family:'Segoe UI',Arial,sans-serif}}
.topbar{{background:#0A1520;padding:14px 24px;display:flex;align-items:center;
         justify-content:space-between;border-bottom:2px solid {GOLD};
         position:sticky;top:0;z-index:100}}
.logo{{font-size:18px;font-weight:700;color:{GOLD};letter-spacing:1px}}
.sub{{font-size:11px;color:#888;margin-top:3px}}
.tab-nav{{display:flex;gap:4px;padding:12px 18px 0;background:#0A1520;
          border-bottom:1px solid #1B2A40}}
.tab{{padding:10px 20px;cursor:pointer;border:none;border-radius:6px 6px 0 0;
      background:{CARD};color:{TEXT};font-size:13px;font-weight:600;transition:all .2s}}
.tab:hover{{background:#243550}}
.tab.on{{background:{GOLD};color:#000}}
.page{{display:none;padding:14px 18px}}
.page.on{{display:block}}
.krow{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:14px}}
.kc{{background:{CARD};border:1px solid #243550;border-radius:8px;
     padding:14px 18px;flex:1;min-width:130px;text-align:center}}
.kv{{font-size:21px;font-weight:700;color:{GOLD}}}
.kl{{font-size:10px;color:#888;margin-top:4px;text-transform:uppercase;letter-spacing:.5px}}
.footer{{text-align:center;padding:14px;font-size:11px;color:#555;
         border-top:1px solid #1B2A40;margin-top:16px}}
</style>"""

JS = """<script>
function show(n){
  document.querySelectorAll('.tab').forEach((b,i)=>b.classList.toggle('on',i===n));
  document.querySelectorAll('.page').forEach((p,i)=>p.classList.toggle('on',i===n));
}
document.addEventListener('DOMContentLoaded',()=>show(0));
</script>"""


# ══════════════════════════════════════════════════════════════════════════════
# Main builder
# ══════════════════════════════════════════════════════════════════════════════
def build():
    print("  Loading data …")
    df = load_data()
    print(f"  {len(df):,} records  |  Building pages …")

    tabs  = ["📊 Page 1: Overview","🕐 Page 2: Time Analysis",
             "🏦 Page 3: Merchant & Bank","✅ Page 4: Status Analysis"]
    funcs = [page1, page2, page3, page4]

    tab_html  = "".join(f'<button class="tab" onclick="show({i})">{t}</button>'
                        for i, t in enumerate(tabs))
    page_html = ""
    for i, fn in enumerate(funcs):
        print(f"  Building {tabs[i]} …")
        page_html += f'<div class="page" id="p{i}">{fn(df)}</div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UPI Transaction Pattern Analysis</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
{CSS}
</head>
<body>
<div class="topbar">
  <div>
    <div class="logo">📱 UPI Transaction Pattern Analysis</div>
    <div class="sub">Banking &amp; Finance Dashboard &nbsp;|&nbsp; Jan–Sep 2024 &nbsp;|&nbsp; 10,000 Transactions</div>
  </div>
  <div style="font-size:11px;color:#888">Python + Plotly &nbsp;|&nbsp; No Power BI Required</div>
</div>
<div class="tab-nav">{tab_html}</div>
{page_html}
<div class="footer">UPI Transaction Pattern Analysis &nbsp;|&nbsp; Built with Python &amp; Plotly &nbsp;|&nbsp; Opens in any browser</div>
{JS}
</body>
</html>"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size = os.path.getsize(OUT_FILE) / 1024
    print(f"\n  Dashboard saved  →  {OUT_FILE}")
    print(f"  File size        :  {size:.0f} KB")


if __name__ == "__main__":
    print("="*62)
    print("  UPI Transaction Pattern Analysis")
    print("  Building Interactive HTML Dashboard (No Power BI needed)")
    print("="*62 + "\n")
    build()
    print("\n[DONE] — Double-click the file to open in your browser:\n")
    print(f"  {OUT_FILE}\n")

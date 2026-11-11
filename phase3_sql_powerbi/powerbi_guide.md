# Power BI Dashboard Guide
## UPI Transaction Pattern Analysis

---

## Overview

This guide explains how to connect Power BI Desktop to the project data
and build the 4-page interactive dashboard.

---

## Step 1: Connect Data Source

### Option A — Connect via MySQL (Recommended)
1. Open **Power BI Desktop**
2. Click **Get Data → MySQL database**
3. Enter:
   - Server: `localhost`
   - Database: `upi_transaction_analysis`
4. Select the **`transactions`** table (and views if needed)
5. Click **Load**

### Option B — Connect via CSV (Always works)
1. Open **Power BI Desktop**
2. Click **Get Data → Text/CSV**
3. Browse to: `data/processed/upi_transactions_clean.csv`
4. Click **Load**

---

## Step 2: Data Model Setup

After loading, go to **Power Query Editor**:

| Column | Action |
|--------|--------|
| TransactionDate | Set type → **Date** |
| TransactionTime | Set type → **Time** |
| Amount          | Set type → **Decimal Number** |
| Hour, MonthNum  | Set type → **Whole Number** |
| IsWeekend       | Set type → **True/False** |

Create a **Date Table** for time intelligence:
```
DateTable = CALENDAR(DATE(2024,1,1), DATE(2024,9,30))
```

Add columns to DateTable:
```
Year       = YEAR([Date])
Month      = FORMAT([Date], "MMMM")
MonthNum   = MONTH([Date])
DayOfWeek  = FORMAT([Date], "dddd")
WeekNum    = WEEKNUM([Date])
Quarter    = "Q" & QUARTER([Date])
```

Mark DateTable as **Date Table** (Modeling tab).

---

## Step 3: DAX Measures

Create a **Measures** table and add:

```dax
-- Core KPIs
Total Transactions = COUNT(transactions[transaction_id])

Total Value = SUM(transactions[amount])

Avg Transaction Amount = AVERAGE(transactions[amount])

Success Count = CALCULATE([Total Transactions], transactions[status] = "SUCCESS")

Failed Count = CALCULATE([Total Transactions], transactions[status] = "FAILED")

Success Rate % = DIVIDE([Success Count], [Total Transactions], 0) * 100

Failure Rate % = DIVIDE([Failed Count], [Total Transactions], 0) * 100

P2P Transactions = CALCULATE([Total Transactions], transactions[payment_type] = "P2P")

P2M Transactions = CALCULATE([Total Transactions], transactions[payment_type] = "P2M")

P2P Value = CALCULATE([Total Value], transactions[payment_type] = "P2P")

P2M Value = CALCULATE([Total Value], transactions[payment_type] = "P2M")

Revenue Leakage = CALCULATE([Total Value], transactions[status] = "FAILED")

-- MoM Growth (requires DateTable relationship)
MoM Growth % =
VAR CurrentMonth = [Total Value]
VAR PreviousMonth = CALCULATE([Total Value], DATEADD(DateTable[Date], -1, MONTH))
RETURN DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, 0) * 100
```

---

## Step 4: Dashboard Pages

---

### PAGE 1 — Overall Transaction Overview

**Purpose:** Executive summary with high-level KPIs

**KPI Cards (top row):**
- Total Transactions: `10,000`
- Total Value: `₹14.98 Cr`
- Avg Transaction Amount: `₹14,982`
- Success Rate: `87.64%`
- Failure Rate: `9.29%`

**Visuals:**
1. **Clustered Bar Chart** — Monthly Transaction Count (Month on X-axis)
2. **Line Chart** — Monthly Total Value trend
3. **Donut Chart** — P2P vs P2M share
4. **Card** — Total P2P Value & Total P2M Value
5. **Bar Chart** — Top 5 Categories by Transaction Value
6. **Map Visual** — State-wise transaction count (bubble map)

**Slicers:**
- Month (list slicer)
- Payment Type (P2P / P2M)
- Status (SUCCESS / FAILED / PENDING)

**Design:**
- Background: Dark blue (#0D1B2A)
- Card background: #1B2A40
- Accent: Gold (#F5A623)
- Font: Segoe UI

---

### PAGE 2 — Time-Based Analysis

**Purpose:** Identify when UPI payments happen

**KPI Cards:**
- Peak Hour: `04:00 hrs`
- Peak Day: `Monday`
- Peak Month: `March`
- Weekend Avg: `₹15,167`

**Visuals:**
1. **Clustered Bar Chart** — Transaction Count by Hour (0–23)
   - Highlight peak hour bar in red
2. **Line Chart** — Average Amount by Hour
3. **Bar Chart** — Transaction Count by Day of Week
   - Weekend bars in orange, weekday in blue
4. **Stacked Bar** — Monthly count by Status
5. **Heatmap Matrix** — Hour (rows) × Day of Week (cols), value = count
   - Use conditional formatting for heat coloring
6. **Pie Chart** — Time of Day segments (Morning/Afternoon/Evening/Night)

**Slicers:**
- Month range (between slicer)
- Day of Week (checkbox)
- Time of Day (dropdown)

---

### PAGE 3 — Merchant & Bank Analysis

**Purpose:** Category and banking ecosystem analysis

**KPI Cards:**
- Top Category: `Salary/Transfer`
- Top Bank: `HDFC Bank`
- Top UPI App: `Paytm`
- No. of Categories: `15`

**Visuals:**
1. **Horizontal Bar Chart** — Category by Total Value (sorted desc)
2. **Clustered Bar Chart** — Category by Transaction Count
3. **Scatter Plot** — Category: Count (X) vs Avg Amount (Y), bubble = total value
4. **Bar Chart** — Sender Bank Transaction Count
5. **Bar Chart** — Bank Failure Rate % (sorted)
6. **Pie Chart** — UPI App market share (by count)
7. **Bar Chart** — UPI App Success Rate %
8. **Stacked Bar** — P2P vs P2M by Month

**Slicers:**
- Category (dropdown)
- Bank (multi-select)
- UPI App (multi-select)
- Payment Type

---

### PAGE 4 — Transaction Status Analysis

**Purpose:** Deep-dive into success and failure patterns

**KPI Cards:**
- Total Successful: `8,764`
- Total Failed: `929`
- Revenue Leakage (Failed Value): `₹1.40 Cr`
- Avg Failed Amount: `₹15,056`

**Visuals:**
1. **Donut Chart** — Overall Status distribution (green/red/orange)
2. **Bar Chart** — Failure Rate % by Category
3. **Bar Chart** — Failure Rate % by Sender Bank
4. **Line Chart** — Hourly Failure Rate %
5. **Stacked Bar** — Monthly transaction count by Status
6. **Bar Chart** — Failure Rate by UPI App
7. **Matrix** — Category × Status count (with conditional formatting)
8. **Bar Chart** — Failure Rate by Amount Bucket

**Slicers:**
- Month
- Category
- Sender Bank
- Device

---

## Step 5: Design Guidelines

### Colour Palette
| Element | Colour |
|---------|--------|
| Page background | #0D1B2A |
| Card background | #1B2A40 |
| Primary accent  | #F5A623 (gold) |
| Success (green) | #4CAF50 |
| Failure (red)   | #F44336 |
| Pending (amber) | #FF9800 |
| P2P (blue)      | #1976D2 |
| P2M (orange)    | #E64A19 |

### Layout Tips
- Use a consistent header bar on each page with the page title
- Place KPI cards in a top row across all pages
- Add page navigation buttons for easy switching
- Enable **cross-filter** so all visuals interact on click
- Add a **Reset Filters** button using a bookmark

---

## Step 6: Export & Publish

1. Save as: `phase3_sql_powerbi/UPI_Dashboard.pbix`
2. Export each page to PDF: File → Export → Export to PDF
3. Publish to Power BI Service (optional): Home → Publish

---

## SQL Views Available for Power BI

If connected to MySQL, use these views for optimised loads:

| View Name | Dashboard Page |
|-----------|---------------|
| `vw_monthly_kpi`     | Page 1 & Page 2 |
| `vw_hourly_pattern`  | Page 2 |
| `vw_category_summary`| Page 3 |
| `vw_bank_summary`    | Page 3 |
| `vw_status_analysis` | Page 4 |

---

*Generated by UPI Transaction Pattern Analysis – Phase 3*

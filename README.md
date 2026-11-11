# UPI Transaction Pattern Analysis

**Domain:** Banking & Finance | **Language:** Python 3.13 | **Tools:** Pandas · NumPy · Matplotlib · Seaborn · MySQL · Power BI

---

## Project Introduction

This end-to-end data analytics project analyses **when, where, and how people make UPI payments in India**. It covers 10,000 UPI transactions spanning January–September 2024 across 12 Indian states, 15 banks, and 10 UPI apps.

---

## Problem Statement

UPI processes billions of transactions monthly, making it the world's largest real-time payment system. However, stakeholders lack clear visibility into:
- Peak usage windows that stress payment gateways
- Categories with unusually high failure rates
- Geographic and banking ecosystem patterns
- P2P vs P2M spending behaviour

This project builds a full analytics pipeline to answer these questions.

---

## Project Structure

```
UPI/
├── config/
│   └── settings.py                ← Central config (paths, constants)
│
├── data/
│   ├── raw/
│   │   └── upi_transactions_raw.csv         (10,000 rows, 19 cols)
│   ├── processed/
│   │   └── upi_transactions_clean.csv       (10,000 rows, 25 cols)
│   └── powerbi/
│       └── pb_*.csv                          (11 Power BI-ready files)
│
├── phase1_preprocessing/
│   ├── generate_dataset.py        ← Dataset builder
│   ├── preprocess.py              ← 10-step cleaning pipeline
│   ├── data_profiler.py           ← Statistical profiling + 8 charts
│   └── run_phase1.py              ← Phase 1 master runner
│
├── phase2_eda/
│   ├── eda_loader.py              ← Shared data loader
│   ├── summary_stats.py           ← KPIs and summary statistics
│   ├── trend_analysis.py          ← Daily/weekly/monthly/hourly trends
│   ├── category_bank_analysis.py  ← Category, bank, UPI app, P2P/P2M
│   ├── status_analysis.py         ← Success/failure analysis
│   ├── insights.py                ← Business insights generator
│   └── run_phase2.py              ← Phase 2 master runner
│
├── phase3_sql_powerbi/
│   ├── schema.sql                 ← MySQL database schema
│   ├── sql_queries.sql            ← 24 business queries + 5 views
│   ├── db_setup.py                ← MySQL database loader
│   ├── sql_analysis.py            ← SQL-equivalent pandas analysis
│   ├── export_for_powerbi.py      ← Power BI CSV exporter
│   ├── powerbi_guide.md           ← Step-by-step dashboard guide
│   └── run_phase3.py              ← Phase 3 master runner
│
├── phase4_testing_docs/
│   ├── test_phase1.py             ← 28 Phase 1 unit tests
│   ├── test_phase2.py             ← 35 Phase 2 unit tests
│   ├── test_phase3.py             ← 22 Phase 3 integration tests
│   └── final_report.py            ← Final project report generator
│
├── reports/
│   ├── preprocessing_report.txt
│   ├── eda_summary_stats.txt
│   ├── eda_business_insights.txt
│   ├── FINAL_PROJECT_REPORT.txt
│   ├── figures/                   ← 8 Phase 1 charts
│   │   └── eda/                   ← 14 Phase 2 EDA charts
│   └── sql_results/               ← 18 SQL query result CSVs
│
└── README.md
```

---

## Dataset Description

| Column | Type | Description |
|--------|------|-------------|
| TransactionID | string | Unique UUID identifier |
| TransactionDate | date | Date of transaction (YYYY-MM-DD) |
| TransactionTime | time | Time of transaction (HH:MM:SS) |
| DayOfWeek | string | Monday–Sunday |
| Month | string | January–September |
| SenderUPI | string | Sender VPA (e.g., raj9812@oksbi) |
| ReceiverUPI | string | Receiver VPA |
| SenderBank | string | Sender's bank |
| ReceiverBank | string | Receiver's bank |
| UPIApp | string | UPI app used |
| Amount | float | Transaction amount in ₹ |
| PaymentType | string | P2P or P2M |
| Category | string | 15 spending categories |
| State | string | 12 Indian states |
| City | string | City within the state |
| Device | string | Android / iOS / Feature Phone |
| Status | string | SUCCESS / FAILED / PENDING |
| ReferenceNo | string | 12-digit reference number |
| Remarks | string | Free-text description |
| Hour | int | Hour extracted from time (0–23) |
| TimeOfDay | string | Morning / Afternoon / Evening / Night |
| IsWeekend | int | 1 = Weekend, 0 = Weekday |
| MonthNum | int | Month number (1–9) |
| WeekOfYear | int | ISO week number |
| AmountBucket | string | Small / Medium / Large / Very Large |

---

## Quick Start

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn mysql-connector-python
```

### Run All Phases
```bash
# Phase 1: Data Collection & Preprocessing
python phase1_preprocessing/run_phase1.py

# Phase 2: Exploratory Data Analysis
python phase2_eda/run_phase2.py

# Phase 3: SQL Analysis & Power BI Export
python phase3_sql_powerbi/run_phase3.py

# Phase 4: Testing & Final Report
python phase4_testing_docs/run_phase4.py

# Run all tests
python phase4_testing_docs/test_phase1.py
python phase4_testing_docs/test_phase2.py
python phase4_testing_docs/test_phase3.py
```

### Load MySQL Database (Optional)
1. Start MySQL server
2. Edit `DB_CONFIG` in `phase3_sql_powerbi/db_setup.py`
3. Run: `python phase3_sql_powerbi/db_setup.py`

### Open Power BI Dashboard
1. Open Power BI Desktop
2. Get Data → CSV → `data/powerbi/pb_transactions.csv`
3. Follow `phase3_sql_powerbi/powerbi_guide.md`

---

## Key Findings

| Metric | Value |
|--------|-------|
| Total Transactions | 10,000 |
| Total Value | ₹14.98 Crore |
| Average Amount | ₹14,982 |
| Success Rate | 87.64% |
| Failure Rate | 9.29% |
| Revenue Leakage (Failed) | ₹1.40 Crore |
| Peak Hour | 04:00 hrs |
| Peak Month | March |
| Top Category (Value) | Salary/Transfer |
| Top Category (Count) | Rent |
| Top State (Count) | Tamil Nadu |
| Top Bank | HDFC Bank |
| Top UPI App | Paytm |
| Android Share | 60.4% |

---

## Business Insights

1. **Scale** — ₹14.98 Crore transacted across 9 months
2. **Reliability** — 87.6% success; ₹1.40 Cr lost to failed transactions
3. **Peak Usage** — Night-time dominates; 04:00 hrs is the single peak hour (automated payments/EMIs)
4. **Category** — Salary/Transfer (#1 by value), Rent (#1 by count), EMI/Loan (highest failure rate 10.62%)
5. **P2P vs P2M** — P2M is 55.7% of count; P2P carries higher avg ticket size
6. **Geography** — Uttar Pradesh leads by value, Tamil Nadu by count
7. **Weekend Effect** — Weekend avg (₹15,167) is 1.7% higher than weekdays
8. **High-Value** — 45.1% of transactions exceed ₹10,000, accounting for 89% of total value
9. **Monthly Growth** — Peak in March (1,165 txns, ₹1.79 Cr)
10. **Device** — Android 60.4%, iOS 35%, Feature Phone 5% (rural UPI penetration)

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.13 |
| Data Processing | Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn |
| Database | MySQL 8.x |
| DB Connector | mysql-connector-python |
| BI Tool | Microsoft Power BI Desktop |
| IDE | VS Code / Kiro |

---

## Project Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Data Collection & Preprocessing | ✅ Complete |
| Phase 2 | Exploratory Data Analysis | ✅ Complete |
| Phase 3 | SQL Database & Power BI Dashboard | ✅ Complete |
| Phase 4 | Testing, Integration & Documentation | ✅ Complete |

---

## Test Coverage

| Test Suite | Tests | Status |
|------------|-------|--------|
| test_phase1.py | 28 tests | ✅ All Pass |
| test_phase2.py | 35 tests | ✅ All Pass |
| test_phase3.py | 22 tests | ✅ All Pass |

---

## Future Enhancements

- Real-time streaming ingestion (Kafka + Spark)
- Fraud detection model (Isolation Forest / XGBoost)
- Geo-spatial visualisation (Folium / GeoPandas)
- Predictive forecasting (ARIMA / Facebook Prophet)
- REST API layer (FastAPI)
- Automated scheduling (Apache Airflow)
- Power BI Service publish with scheduled refresh

---

## Author

**Domain:** Data Analytics — Banking & Finance  
**Project:** UPI Transaction Pattern Analysis  
**Dataset:** Jan–Sep 2024 | 10,000 Transactions | 12 States | 15 Banks

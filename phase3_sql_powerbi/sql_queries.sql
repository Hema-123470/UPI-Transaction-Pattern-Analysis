-- =============================================================
-- sql_queries.sql
-- UPI Transaction Pattern Analysis
-- Phase 3 – Business Analysis SQL Queries
-- Database: upi_transaction_analysis
-- =============================================================

USE upi_transaction_analysis;

-- =============================================================
-- SECTION 1: OVERVIEW KPIs
-- =============================================================

-- Q01: Total transactions, total value, average value
SELECT
    COUNT(*)                                AS total_transactions,
    ROUND(SUM(amount), 2)                   AS total_value_inr,
    ROUND(AVG(amount), 2)                   AS avg_amount_inr,
    ROUND(MEDIAN_AMOUNT, 2)                 AS median_approx,
    MIN(amount)                             AS min_amount,
    MAX(amount)                             AS max_amount
FROM transactions,
(SELECT AVG(amount) AS MEDIAN_AMOUNT
 FROM (
   SELECT amount FROM transactions
   ORDER BY amount
   LIMIT 2 - (SELECT COUNT(*) FROM transactions) % 2
   OFFSET (SELECT (COUNT(*) - 1) / 2 FROM transactions)
 ) AS sub) AS med;

-- Simplified version (without median subquery)
SELECT
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value_inr,
    ROUND(AVG(amount), 2)      AS avg_amount_inr,
    ROUND(MIN(amount), 2)      AS min_amount,
    ROUND(MAX(amount), 2)      AS max_amount,
    ROUND(STDDEV(amount), 2)   AS std_deviation
FROM transactions;

-- Q02: Transaction status summary
SELECT
    status,
    COUNT(*)                                        AS total_count,
    ROUND(SUM(amount), 2)                           AS total_value,
    ROUND(AVG(amount), 2)                           AS avg_value,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM transactions
GROUP BY status
ORDER BY total_count DESC;

-- Q03: P2P vs P2M comparison
SELECT
    payment_type,
    COUNT(*)                   AS total_count,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(MIN(amount), 2)      AS min_amount,
    ROUND(MAX(amount), 2)      AS max_amount,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
    ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)                         AS success_rate_pct
FROM transactions
GROUP BY payment_type
ORDER BY total_count DESC;


-- =============================================================
-- SECTION 2: TIME-BASED ANALYSIS
-- =============================================================

-- Q04: Monthly transaction trend
SELECT
    month_num,
    month_name,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN status = 'FAILED'  THEN 1 ELSE 0 END) AS failed_count,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)                         AS failure_rate_pct
FROM transactions
GROUP BY month_num, month_name
ORDER BY month_num;

-- Q05: Day-of-week analysis
SELECT
    day_of_week,
    is_weekend,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS failure_rate_pct
FROM transactions
GROUP BY day_of_week, is_weekend
ORDER BY
    FIELD(day_of_week,'Monday','Tuesday','Wednesday',
                      'Thursday','Friday','Saturday','Sunday');

-- Q06: Hourly transaction pattern
SELECT
    hour,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS failure_rate_pct
FROM transactions
GROUP BY hour
ORDER BY hour;

-- Q07: Peak hour (top 5)
SELECT
    hour,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_value
FROM transactions
GROUP BY hour
ORDER BY transaction_count DESC
LIMIT 5;

-- Q08: Time of day analysis
SELECT
    time_of_day,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS failure_rate_pct
FROM transactions
GROUP BY time_of_day
ORDER BY FIELD(time_of_day, 'Morning', 'Afternoon', 'Evening', 'Night');

-- Q09: Weekend vs Weekday
SELECT
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS failure_rate_pct
FROM transactions
GROUP BY is_weekend;

-- Q10: Daily transaction count (for trend line)
SELECT
    transaction_date,
    COUNT(*)                   AS daily_count,
    ROUND(SUM(amount), 2)      AS daily_value,
    ROUND(AVG(amount), 2)      AS daily_avg
FROM transactions
GROUP BY transaction_date
ORDER BY transaction_date;


-- =============================================================
-- SECTION 3: MERCHANT CATEGORY ANALYSIS
-- =============================================================

-- Q11: Full category breakdown
SELECT
    category,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(MIN(amount), 2)      AS min_amount,
    ROUND(MAX(amount), 2)      AS max_amount,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN status = 'FAILED'  THEN 1 ELSE 0 END) AS failed_count,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS failure_rate_pct,
    ROUND(SUM(amount) * 100.0 /
          (SELECT SUM(amount) FROM transactions), 2) AS value_share_pct
FROM transactions
GROUP BY category
ORDER BY total_value DESC;

-- Q12: Top 5 categories by transaction count
SELECT category, COUNT(*) AS txn_count
FROM transactions
GROUP BY category
ORDER BY txn_count DESC
LIMIT 5;

-- Q13: Top 5 categories by transaction value
SELECT category, ROUND(SUM(amount), 2) AS total_value
FROM transactions
GROUP BY category
ORDER BY total_value DESC
LIMIT 5;

-- Q14: Category trend by month (pivot-style)
SELECT
    month_name,
    month_num,
    category,
    COUNT(*)              AS txn_count,
    ROUND(SUM(amount), 2) AS total_value
FROM transactions
GROUP BY month_num, month_name, category
ORDER BY month_num, total_value DESC;


-- =============================================================
-- SECTION 4: BANK-WISE ANALYSIS
-- =============================================================

-- Q15: Sender bank performance
SELECT
    sender_bank,
    COUNT(*)                   AS total_sent,
    ROUND(SUM(amount), 2)      AS total_value_sent,
    ROUND(AVG(amount), 2)      AS avg_sent,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN status = 'FAILED'  THEN 1 ELSE 0 END) AS failed_count,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS failure_rate_pct
FROM transactions
GROUP BY sender_bank
ORDER BY total_sent DESC;

-- Q16: Receiver bank performance
SELECT
    receiver_bank,
    COUNT(*)                   AS total_received,
    ROUND(SUM(amount), 2)      AS total_value_received,
    ROUND(AVG(amount), 2)      AS avg_received
FROM transactions
GROUP BY receiver_bank
ORDER BY total_received DESC;

-- Q17: Top sender-receiver bank pairs
SELECT
    sender_bank,
    receiver_bank,
    COUNT(*)                   AS transaction_count,
    ROUND(SUM(amount), 2)      AS total_value
FROM transactions
GROUP BY sender_bank, receiver_bank
ORDER BY transaction_count DESC
LIMIT 15;

-- Q18: UPI App analysis
SELECT
    upi_app,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS success_rate_pct,
    ROUND(SUM(CASE WHEN status = 'FAILED'  THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS failure_rate_pct
FROM transactions
GROUP BY upi_app
ORDER BY total_transactions DESC;


-- =============================================================
-- SECTION 5: GEOGRAPHIC ANALYSIS
-- =============================================================

-- Q19: State-wise analysis
SELECT
    state,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    COUNT(DISTINCT city)       AS city_count,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS failure_rate_pct
FROM transactions
GROUP BY state
ORDER BY total_value DESC;

-- Q20: Top 10 cities
SELECT
    city,
    state,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount
FROM transactions
GROUP BY city, state
ORDER BY total_transactions DESC
LIMIT 10;

-- Q21: Device usage analysis
SELECT
    device,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)  AS success_rate_pct
FROM transactions
GROUP BY device
ORDER BY total_transactions DESC;


-- =============================================================
-- SECTION 6: AMOUNT ANALYSIS
-- =============================================================

-- Q22: Amount bucket distribution
SELECT
    amount_bucket,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct_of_total
FROM transactions
GROUP BY amount_bucket
ORDER BY FIELD(amount_bucket,
    'Small (≤500)', 'Medium (501–2000)',
    'Large (2001–10000)', 'Very Large (>10000)');

-- Q23: High-value transactions (>₹40,000)
SELECT
    transaction_id,
    transaction_date,
    amount,
    category,
    sender_bank,
    state,
    status
FROM transactions
WHERE amount > 40000
ORDER BY amount DESC
LIMIT 20;

-- Q24: Average transaction amount by category and payment type
SELECT
    category,
    payment_type,
    COUNT(*)                   AS transaction_count,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(amount), 2)      AS total_value
FROM transactions
GROUP BY category, payment_type
ORDER BY category, payment_type;


-- =============================================================
-- SECTION 7: POWER BI DASHBOARD VIEWS
-- (Optimised queries for direct dashboard connection)
-- =============================================================

-- View 1: Monthly KPI Summary (Page 1)
CREATE OR REPLACE VIEW vw_monthly_kpi AS
SELECT
    month_num,
    month_name,
    COUNT(*)                   AS total_transactions,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN status = 'FAILED'  THEN 1 ELSE 0 END) AS failed_count,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2) AS failure_rate_pct
FROM transactions
GROUP BY month_num, month_name;

-- View 2: Hourly Pattern (Page 2)
CREATE OR REPLACE VIEW vw_hourly_pattern AS
SELECT
    hour,
    time_of_day,
    COUNT(*)                   AS txn_count,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2) AS failure_rate_pct
FROM transactions
GROUP BY hour, time_of_day;

-- View 3: Category Summary (Page 3)
CREATE OR REPLACE VIEW vw_category_summary AS
SELECT
    category,
    payment_type,
    COUNT(*)                   AS txn_count,
    ROUND(SUM(amount), 2)      AS total_value,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2) AS failure_rate_pct
FROM transactions
GROUP BY category, payment_type;

-- View 4: Bank Summary (Page 3)
CREATE OR REPLACE VIEW vw_bank_summary AS
SELECT
    sender_bank,
    COUNT(*)                   AS txn_count,
    ROUND(SUM(amount), 2)      AS total_sent,
    ROUND(AVG(amount), 2)      AS avg_amount,
    ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2) AS success_rate_pct,
    ROUND(SUM(CASE WHEN status = 'FAILED'  THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2) AS failure_rate_pct
FROM transactions
GROUP BY sender_bank;

-- View 5: Status Analysis (Page 4)
CREATE OR REPLACE VIEW vw_status_analysis AS
SELECT
    status,
    category,
    sender_bank,
    upi_app,
    hour,
    day_of_week,
    amount_bucket,
    COUNT(*)                   AS txn_count,
    ROUND(SUM(amount), 2)      AS total_value
FROM transactions
GROUP BY status, category, sender_bank, upi_app, hour, day_of_week, amount_bucket;

-- =============================================================
-- END OF SQL QUERIES
-- =============================================================

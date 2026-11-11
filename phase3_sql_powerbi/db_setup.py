"""
phase3_sql_powerbi/db_setup.py
---------------------------------
Creates the MySQL database, tables, and imports the cleaned
UPI transaction dataset using mysql-connector-python.

Steps:
  1. Connect to MySQL (root / localhost)
  2. Create database upi_transaction_analysis
  3. Create fact table: transactions
  4. Bulk-insert 10,000 rows from cleaned CSV
  5. Verify row count and print summary

Usage:
    python phase3_sql_powerbi/db_setup.py

Configuration:
    Edit DB_CONFIG below to match your MySQL credentials.
"""

import os
import sys
import pandas as pd
import mysql.connector
from mysql.connector import Error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CLEAN_FILE

# ── MySQL connection config ──────────────────────────────────────────────────
DB_CONFIG = {
    "host"    : "localhost",
    "port"    : 3306,
    "user"    : "root",       # ← Change if needed
    "password": "",           # ← Change if needed
}
DB_NAME = "upi_transaction_analysis"


def get_connection(database: str = None):
    """Return a MySQL connection, optionally selecting a database."""
    cfg = dict(DB_CONFIG)
    if database:
        cfg["database"] = database
    return mysql.connector.connect(**cfg)


def create_database(cursor) -> None:
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    cursor.execute(f"USE `{DB_NAME}`;")
    print(f"  Database '{DB_NAME}' ready.")


def create_table(cursor) -> None:
    cursor.execute("DROP TABLE IF EXISTS transactions;")
    cursor.execute("""
        CREATE TABLE transactions (
            id                 INT           NOT NULL AUTO_INCREMENT,
            transaction_id     VARCHAR(40)   NOT NULL,
            transaction_date   DATE          NOT NULL,
            transaction_time   TIME          NOT NULL,
            day_of_week        VARCHAR(12)   NOT NULL,
            month_name         VARCHAR(12)   NOT NULL,
            month_num          TINYINT       NOT NULL,
            week_of_year       TINYINT       NOT NULL,
            hour               TINYINT       NOT NULL,
            time_of_day        VARCHAR(12)   NOT NULL,
            is_weekend         TINYINT(1)    NOT NULL DEFAULT 0,
            sender_upi         VARCHAR(60)   NOT NULL,
            receiver_upi       VARCHAR(60)   NOT NULL,
            sender_bank        VARCHAR(60)   NOT NULL,
            receiver_bank      VARCHAR(60)   NOT NULL,
            upi_app            VARCHAR(50)   NOT NULL,
            amount             DECIMAL(12,2) NOT NULL,
            payment_type       VARCHAR(5)    NOT NULL,
            category           VARCHAR(50)   NOT NULL,
            state              VARCHAR(60)   NOT NULL,
            city               VARCHAR(60)   NOT NULL,
            device             VARCHAR(30)   NOT NULL,
            status             VARCHAR(10)   NOT NULL,
            reference_no       VARCHAR(15)   NOT NULL,
            remarks            VARCHAR(120)  NOT NULL,
            amount_bucket      VARCHAR(25)   NOT NULL,
            PRIMARY KEY (id),
            UNIQUE KEY uq_txn (transaction_id),
            KEY idx_date      (transaction_date),
            KEY idx_status    (status),
            KEY idx_category  (category),
            KEY idx_bank      (sender_bank),
            KEY idx_state     (state),
            KEY idx_app       (upi_app),
            KEY idx_ptype     (payment_type),
            KEY idx_hour      (hour),
            KEY idx_month     (month_num)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    print("  Table 'transactions' created.")


def load_dataframe() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_FILE)
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"]).dt.strftime("%Y-%m-%d")
    df["Amount"]     = df["Amount"].round(2)
    df["ReferenceNo"]= df["ReferenceNo"].astype(str).str[:15]
    df["Remarks"]    = df["Remarks"].astype(str).str[:120]
    return df


def insert_data(cursor, conn, df: pd.DataFrame) -> None:
    sql = """
        INSERT INTO transactions (
            transaction_id, transaction_date, transaction_time,
            day_of_week, month_name, month_num, week_of_year,
            hour, time_of_day, is_weekend,
            sender_upi, receiver_upi, sender_bank, receiver_bank,
            upi_app, amount, payment_type, category,
            state, city, device, status, reference_no,
            remarks, amount_bucket
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
    """
    rows = [
        (
            row["TransactionID"],   row["TransactionDate"], row["TransactionTime"],
            row["DayOfWeek"],       row["Month"],           int(row["MonthNum"]),
            int(row["WeekOfYear"]), int(row["Hour"]),       row["TimeOfDay"],
            int(row["IsWeekend"]),  row["SenderUPI"],       row["ReceiverUPI"],
            row["SenderBank"],      row["ReceiverBank"],    row["UPIApp"],
            float(row["Amount"]),   row["PaymentType"],     row["Category"],
            row["State"],           row["City"],            row["Device"],
            row["Status"],          row["ReferenceNo"],     row["Remarks"],
            row["AmountBucket"]
        )
        for _, row in df.iterrows()
    ]

    # Batch insert in chunks of 500
    chunk_size = 500
    total = len(rows)
    for i in range(0, total, chunk_size):
        cursor.executemany(sql, rows[i:i+chunk_size])
        conn.commit()
        done = min(i + chunk_size, total)
        print(f"  Inserted {done:>6,} / {total:,} rows …", end="\r")
    print(f"\n  All {total:,} rows inserted successfully.")


def verify(cursor) -> None:
    cursor.execute("SELECT COUNT(*) FROM transactions;")
    count = cursor.fetchone()[0]
    print(f"\n  ✓ Verification — rows in transactions table: {count:,}")

    cursor.execute("""
        SELECT status, COUNT(*) AS cnt, SUM(amount) AS total
        FROM transactions GROUP BY status ORDER BY cnt DESC;
    """)
    print("\n  Status distribution:")
    for row in cursor.fetchall():
        print(f"    {row[0]:10s} : {row[1]:>5,} rows  | ₹{float(row[2]):>14,.2f}")


def run_db_setup() -> None:
    print("=" * 62)
    print("  UPI Transaction Pattern Analysis")
    print("  Phase 3 – MySQL Database Setup")
    print("=" * 62)

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        print("\n  Connected to MySQL server.")

        create_database(cursor)
        create_table(cursor)

        print("\n  Loading cleaned dataset …")
        df = load_dataframe()
        print(f"  {len(df):,} records ready for import.")

        print("\n  Inserting data …")
        insert_data(cursor, conn, df)
        verify(cursor)

        cursor.close()
        conn.close()
        print("\n[DONE] Database setup complete.\n")

    except Error as e:
        print(f"\n[ERROR] MySQL Error: {e}")
        print("\n  Possible causes:")
        print("  - MySQL server not running (start it via MySQL Workbench or services)")
        print("  - Wrong credentials in DB_CONFIG (edit phase3_sql_powerbi/db_setup.py)")
        print("  - mysql-connector-python not installed (pip install mysql-connector-python)")
        print("\n  The SQL analysis script will still work once MySQL is configured.")
        sys.exit(1)


if __name__ == "__main__":
    run_db_setup()

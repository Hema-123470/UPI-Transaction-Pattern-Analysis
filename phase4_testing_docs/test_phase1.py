"""
phase4_testing_docs/test_phase1.py
-------------------------------------
Unit and integration tests for Phase 1 modules.
Tests are self-contained and run without pytest (uses unittest).

Coverage:
  1. Dataset generation – schema, row count, value ranges
  2. Preprocessing – missing values, duplicates, dtypes, outlier capping
  3. Feature engineering – new columns, valid values
  4. Output files – existence and non-empty

Run:
    python phase4_testing_docs/test_phase1.py
"""

import os
import sys
import unittest
import pandas as pd
import numpy  as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    RAW_FILE, CLEAN_FILE, NUM_RECORDS, CATEGORIES,
    STATUSES, BANKS, UPI_APPS, STATES_CITIES, DEVICES
)


# ── Helper ────────────────────────────────────────────────────────────────────

def load(path):
    df = pd.read_csv(path)
    return df


# ══════════════════════════════════════════════════════════════════════════════
class TestRawDataset(unittest.TestCase):
    """Tests on the raw (generated) dataset."""

    @classmethod
    def setUpClass(cls):
        cls.df = load(RAW_FILE)

    # ── Schema ────────────────────────────────────────────────────────────────

    def test_row_count(self):
        self.assertEqual(len(self.df), NUM_RECORDS,
                         f"Expected {NUM_RECORDS} rows, got {len(self.df)}")

    def test_required_columns_present(self):
        required = [
            "TransactionID","TransactionDate","TransactionTime","DayOfWeek","Month",
            "SenderUPI","ReceiverUPI","SenderBank","ReceiverBank","UPIApp",
            "Amount","PaymentType","Category","State","City","Device",
            "Status","ReferenceNo","Remarks"
        ]
        for col in required:
            self.assertIn(col, self.df.columns, f"Missing column: {col}")

    def test_no_all_null_rows(self):
        null_rows = self.df.isnull().all(axis=1).sum()
        self.assertEqual(null_rows, 0, "There are rows where all values are null")

    # ── Values ────────────────────────────────────────────────────────────────

    def test_transaction_id_unique(self):
        self.assertEqual(self.df["TransactionID"].nunique(), NUM_RECORDS,
                         "TransactionID values are not unique")

    def test_amount_positive(self):
        self.assertTrue((self.df["Amount"] > 0).all(),
                        "Some Amount values are zero or negative")

    def test_status_valid_values(self):
        valid = {s.upper() for s in STATUSES}
        actual = set(self.df["Status"].str.upper().unique())
        self.assertTrue(actual.issubset(valid),
                        f"Invalid Status values: {actual - valid}")

    def test_payment_type_valid(self):
        valid = {"P2P", "P2M"}
        actual = set(self.df["PaymentType"].unique())
        self.assertTrue(actual.issubset(valid),
                        f"Invalid PaymentType values: {actual - valid}")

    def test_categories_valid(self):
        # Use lower-case comparison to avoid title-case quirks with "/" separator
        cat_set = set(c.lower() for c in CATEGORIES)
        actual  = set(c.lower() for c in self.df["Category"].unique())
        self.assertTrue(actual.issubset(cat_set),
                        f"Invalid categories: {actual - cat_set}")

    def test_date_range(self):
        dates = pd.to_datetime(self.df["TransactionDate"])
        self.assertGreaterEqual(dates.min(), pd.Timestamp("2024-01-01"),
                                "Date below 2024-01-01 found")
        self.assertLessEqual(dates.max(), pd.Timestamp("2024-09-30"),
                             "Date after 2024-09-30 found")

    def test_sender_bank_valid(self):
        valid  = set(BANKS)
        actual = set(self.df["SenderBank"].unique())
        self.assertTrue(actual.issubset(valid),
                        f"Invalid SenderBank values: {actual - valid}")

    def test_upi_app_valid(self):
        valid  = set(UPI_APPS)
        actual = set(self.df["UPIApp"].unique())
        self.assertTrue(actual.issubset(valid),
                        f"Invalid UPIApp values: {actual - valid}")

    def test_state_valid(self):
        valid  = set(STATES_CITIES.keys())
        actual = set(self.df["State"].unique())
        self.assertTrue(actual.issubset(valid),
                        f"Invalid State values: {actual - valid}")


# ══════════════════════════════════════════════════════════════════════════════
class TestCleanDataset(unittest.TestCase):
    """Tests on the cleaned / preprocessed dataset."""

    @classmethod
    def setUpClass(cls):
        cls.df = load(CLEAN_FILE)

    # ── Volume ────────────────────────────────────────────────────────────────

    def test_records_not_less_than_95_percent(self):
        """Preprocessing should retain ≥ 95 % of records."""
        self.assertGreaterEqual(len(self.df), int(NUM_RECORDS * 0.95),
                                "Too many rows dropped during cleaning")

    # ── No nulls in key columns ───────────────────────────────────────────────

    def test_no_null_in_critical_cols(self):
        for col in ["TransactionID","TransactionDate","Amount","Status"]:
            nulls = self.df[col].isnull().sum()
            self.assertEqual(nulls, 0, f"Null values found in {col}: {nulls}")

    # ── Uniqueness ────────────────────────────────────────────────────────────

    def test_no_duplicate_transaction_ids(self):
        dups = self.df.duplicated(subset="TransactionID").sum()
        self.assertEqual(dups, 0, f"Duplicate TransactionIDs: {dups}")

    # ── Outlier capping ───────────────────────────────────────────────────────

    def test_amount_non_negative(self):
        neg = (self.df["Amount"] < 0).sum()
        self.assertEqual(neg, 0, f"Negative Amount values after cleaning: {neg}")

    # ── Feature engineering columns exist ────────────────────────────────────

    def test_engineered_columns_present(self):
        for col in ["Hour","TimeOfDay","IsWeekend","MonthNum","WeekOfYear","AmountBucket"]:
            self.assertIn(col, self.df.columns, f"Engineered column missing: {col}")

    def test_hour_range(self):
        h = self.df["Hour"]
        self.assertTrue((h >= 0).all() and (h <= 23).all(),
                        "Hour values outside [0, 23]")

    def test_time_of_day_valid(self):
        valid = {"Morning","Afternoon","Evening","Night"}
        actual = set(self.df["TimeOfDay"].unique())
        self.assertTrue(actual.issubset(valid),
                        f"Invalid TimeOfDay values: {actual - valid}")

    def test_is_weekend_binary(self):
        vals = set(self.df["IsWeekend"].unique())
        self.assertTrue(vals.issubset({0, 1}),
                        f"IsWeekend has non-binary values: {vals}")

    def test_amount_bucket_valid(self):
        valid = {"Small (≤500)", "Medium (501–2000)",
                 "Large (2001–10000)", "Very Large (>10000)"}
        actual = set(self.df["AmountBucket"].unique())
        self.assertTrue(actual.issubset(valid),
                        f"Invalid AmountBucket values: {actual - valid}")

    def test_month_num_range(self):
        mn = self.df["MonthNum"]
        self.assertTrue((mn >= 1).all() and (mn <= 12).all(),
                        "MonthNum outside [1, 12]")


# ══════════════════════════════════════════════════════════════════════════════
class TestOutputFiles(unittest.TestCase):
    """Verify that all expected output files were created."""

    def test_raw_file_exists(self):
        self.assertTrue(os.path.exists(RAW_FILE), f"Raw file not found: {RAW_FILE}")

    def test_clean_file_exists(self):
        self.assertTrue(os.path.exists(CLEAN_FILE), f"Clean file not found: {CLEAN_FILE}")

    def test_report_file_exists(self):
        from config.settings import REPORT_FILE
        self.assertTrue(os.path.exists(REPORT_FILE), f"Report file not found: {REPORT_FILE}")

    def test_figures_generated(self):
        from config.settings import FIGURES_DIR
        figs = [f for f in os.listdir(FIGURES_DIR) if f.endswith(".png")]
        self.assertGreaterEqual(len(figs), 8,
                                f"Expected ≥8 chart files, found {len(figs)}: {figs}")

    def test_raw_file_non_empty(self):
        size = os.path.getsize(RAW_FILE)
        self.assertGreater(size, 1000, "Raw CSV file appears empty")

    def test_clean_file_non_empty(self):
        size = os.path.getsize(CLEAN_FILE)
        self.assertGreater(size, 1000, "Clean CSV file appears empty")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    loader  = unittest.TestLoader()
    suite   = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestRawDataset))
    suite.addTests(loader.loadTestsFromTestCase(TestCleanDataset))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFiles))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

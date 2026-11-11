"""
phase4_testing_docs/test_phase3.py
-------------------------------------
Unit and integration tests for Phase 3 SQL & Power BI modules.

Coverage:
  1. SQL result files existence and content
  2. KPI cross-validation (SQL results vs pandas calculations)
  3. Power BI export files existence and correctness
  4. SQL schema file existence
  5. Data integrity across aggregation levels

Run:
    python phase4_testing_docs/test_phase3.py
"""

import os
import sys
import unittest
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CLEAN_FILE, REPORTS_DIR, BASE_DIR

SQL_RESULTS = os.path.join(REPORTS_DIR, "sql_results")
PBI_DIR     = os.path.join(BASE_DIR, "data", "powerbi")


class TestSQLResultFiles(unittest.TestCase):
    """Verify all expected SQL result CSVs were created."""

    EXPECTED_FILES = [
        "Q01_overview.csv", "Q02_status.csv", "Q03_payment_type.csv",
        "Q04_monthly.csv",  "Q05_day_of_week.csv", "Q06_hourly.csv",
        "Q07_peak_hours.csv", "Q08_time_of_day.csv", "Q09_weekend.csv",
        "Q11_category.csv", "Q15_bank.csv", "Q17_bank_pairs.csv",
        "Q18_upi_app.csv",  "Q19_state.csv", "Q20_top_cities.csv",
        "Q21_device.csv",   "Q22_amount_bucket.csv", "Q23_high_value.csv",
    ]

    def test_sql_results_dir_exists(self):
        self.assertTrue(os.path.isdir(SQL_RESULTS))

    def test_all_result_files_exist(self):
        for fname in self.EXPECTED_FILES:
            path = os.path.join(SQL_RESULTS, fname)
            self.assertTrue(os.path.exists(path), f"Missing: {fname}")

    def test_all_files_non_empty(self):
        for fname in self.EXPECTED_FILES:
            path = os.path.join(SQL_RESULTS, fname)
            if os.path.exists(path):
                self.assertGreater(os.path.getsize(path), 50, f"Empty: {fname}")


class TestSQLResultContent(unittest.TestCase):
    """Validate the content of key SQL result files."""

    @classmethod
    def setUpClass(cls):
        cls.raw = pd.read_csv(CLEAN_FILE)
        cls.raw["Amount"] = pd.to_numeric(cls.raw["Amount"])

    def test_q01_total_transactions(self):
        q01 = pd.read_csv(os.path.join(SQL_RESULTS, "Q01_overview.csv"))
        self.assertEqual(q01["total_transactions"].iloc[0], len(self.raw))

    def test_q01_total_value(self):
        q01 = pd.read_csv(os.path.join(SQL_RESULTS, "Q01_overview.csv"))
        expected = round(self.raw["Amount"].sum(), 2)
        actual   = round(float(q01["total_value"].iloc[0]), 2)
        self.assertAlmostEqual(actual, expected, places=0)

    def test_q02_status_rows(self):
        q02 = pd.read_csv(os.path.join(SQL_RESULTS, "Q02_status.csv"))
        self.assertEqual(len(q02), 3, "Should have exactly 3 status values")

    def test_q02_status_sums_to_total(self):
        q02  = pd.read_csv(os.path.join(SQL_RESULTS, "Q02_status.csv"))
        total = q02["total_count"].sum()
        self.assertEqual(total, len(self.raw))

    def test_q04_monthly_9_rows(self):
        q04 = pd.read_csv(os.path.join(SQL_RESULTS, "Q04_monthly.csv"))
        self.assertEqual(len(q04), 9, "Should have data for 9 months")

    def test_q04_monthly_sum_equals_total(self):
        q04   = pd.read_csv(os.path.join(SQL_RESULTS, "Q04_monthly.csv"))
        total = q04["total_transactions"].sum()
        self.assertEqual(total, len(self.raw))

    def test_q06_hourly_24_rows(self):
        q06 = pd.read_csv(os.path.join(SQL_RESULTS, "Q06_hourly.csv"))
        self.assertEqual(len(q06), 24, "Should have 24 hourly rows")

    def test_q11_category_15_rows(self):
        q11 = pd.read_csv(os.path.join(SQL_RESULTS, "Q11_category.csv"))
        self.assertEqual(len(q11), 15, "Should have 15 categories")

    def test_q11_category_sum_equals_total(self):
        q11   = pd.read_csv(os.path.join(SQL_RESULTS, "Q11_category.csv"))
        total = q11["total_transactions"].sum()
        self.assertEqual(total, len(self.raw))

    def test_q15_bank_15_rows(self):
        q15 = pd.read_csv(os.path.join(SQL_RESULTS, "Q15_bank.csv"))
        self.assertEqual(len(q15), 15, "Should have 15 banks")

    def test_q19_state_12_rows(self):
        q19 = pd.read_csv(os.path.join(SQL_RESULTS, "Q19_state.csv"))
        self.assertEqual(len(q19), 12, "Should have 12 states")

    def test_q22_amount_bucket_4_rows(self):
        q22 = pd.read_csv(os.path.join(SQL_RESULTS, "Q22_amount_bucket.csv"))
        self.assertEqual(len(q22), 4, "Should have 4 amount buckets")

    def test_q23_high_value_amounts_above_40k(self):
        q23 = pd.read_csv(os.path.join(SQL_RESULTS, "Q23_high_value.csv"))
        if len(q23) > 0:
            self.assertTrue((q23["Amount"] > 40000).all(),
                            "All high-value records should be > ₹40,000")


class TestPowerBIExports(unittest.TestCase):
    """Verify Power BI export files are present and correct."""

    EXPECTED_FILES = [
        "pb_page1_overview.csv",
        "pb_page2_hourly.csv",
        "pb_page2_dow.csv",
        "pb_page2_timeofday.csv",
        "pb_page3_category.csv",
        "pb_page3_bank.csv",
        "pb_page3_upi_app.csv",
        "pb_page4_status_category.csv",
        "pb_page4_status_bank.csv",
        "pb_page4_failure_by_bank.csv",
        "pb_transactions.csv",
    ]

    def test_powerbi_dir_exists(self):
        self.assertTrue(os.path.isdir(PBI_DIR))

    def test_all_pbi_files_exist(self):
        for fname in self.EXPECTED_FILES:
            path = os.path.join(PBI_DIR, fname)
            self.assertTrue(os.path.exists(path), f"Missing: {fname}")

    def test_master_dataset_row_count(self):
        path = os.path.join(PBI_DIR, "pb_transactions.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            self.assertGreaterEqual(len(df), 9500)

    def test_page1_monthly_rows(self):
        path = os.path.join(PBI_DIR, "pb_page1_overview.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            self.assertEqual(len(df), 9)

    def test_page2_hourly_24_rows(self):
        path = os.path.join(PBI_DIR, "pb_page2_hourly.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            self.assertEqual(len(df), 24)

    def test_page3_category_15_rows(self):
        path = os.path.join(PBI_DIR, "pb_page3_category.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            self.assertEqual(len(df), 15)


class TestCrossValidation(unittest.TestCase):
    """Cross-validate SQL results against direct pandas calculations."""

    @classmethod
    def setUpClass(cls):
        cls.raw = pd.read_csv(CLEAN_FILE)
        cls.raw["Amount"] = pd.to_numeric(cls.raw["Amount"])

    def test_success_rate_matches(self):
        q02  = pd.read_csv(os.path.join(SQL_RESULTS, "Q02_status.csv"))
        sql_sr = float(q02[q02["Status"]=="SUCCESS"]["percentage"].iloc[0])
        pd_sr  = round((cls.raw["Status"]=="SUCCESS").mean()*100, 2) if False else \
                 round((self.raw["Status"]=="SUCCESS").mean()*100, 2)
        self.assertAlmostEqual(sql_sr, pd_sr, places=1)

    def test_top_category_by_value_matches(self):
        q11       = pd.read_csv(os.path.join(SQL_RESULTS, "Q11_category.csv"))
        sql_top   = q11.sort_values("total_value", ascending=False).iloc[0]["Category"]
        pandas_top= self.raw.groupby("Category")["Amount"].sum().idxmax()
        self.assertEqual(sql_top.strip(), pandas_top.strip())

    def test_top_bank_by_count_matches(self):
        q15       = pd.read_csv(os.path.join(SQL_RESULTS, "Q15_bank.csv"))
        sql_top   = q15.sort_values("total_sent", ascending=False).iloc[0]["sender_bank"]
        pandas_top= self.raw["SenderBank"].value_counts().idxmax()
        self.assertEqual(sql_top.strip(), pandas_top.strip())

    def test_total_value_q11_matches_raw(self):
        q11       = pd.read_csv(os.path.join(SQL_RESULTS, "Q11_category.csv"))
        sql_total = q11["total_value"].sum()
        pd_total  = self.raw["Amount"].sum()
        self.assertAlmostEqual(sql_total, pd_total, delta=100)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestSQLResultFiles, TestSQLResultContent,
                TestPowerBIExports, TestCrossValidation]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

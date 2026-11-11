"""
phase4_testing_docs/test_phase2.py
-------------------------------------
Unit and integration tests for Phase 2 EDA modules.

Coverage:
  1. KPI calculations correctness
  2. Trend analysis data completeness
  3. Category and bank analysis validity
  4. Status analysis accuracy
  5. Business insights consistency
  6. Output file existence

Run:
    python phase4_testing_docs/test_phase2.py
"""

import os
import sys
import unittest
import pandas as pd
import numpy  as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CLEAN_FILE, REPORTS_DIR, FIGURES_DIR
from phase2_eda.eda_loader    import load_clean_data
from phase2_eda.summary_stats import compute_kpis


EDA_FIGURES = os.path.join(FIGURES_DIR, "eda")


class TestEDALoader(unittest.TestCase):
    """Test that the EDA loader returns a correctly-typed DataFrame."""

    @classmethod
    def setUpClass(cls):
        cls.df = load_clean_data()

    def test_shape(self):
        self.assertGreaterEqual(self.df.shape[0], 9000)
        self.assertGreaterEqual(self.df.shape[1], 25)

    def test_transaction_date_dtype(self):
        # pandas 2.x may return datetime64[us] or datetime64[ns] — both valid
        dtype_str = str(self.df["TransactionDate"].dtype)
        self.assertTrue(dtype_str.startswith("datetime64"),
                        f"Expected datetime64 dtype, got {dtype_str}")

    def test_amount_dtype(self):
        self.assertTrue(pd.api.types.is_float_dtype(self.df["Amount"]))

    def test_month_ordered_categorical(self):
        self.assertTrue(hasattr(self.df["Month"], "cat"))
        self.assertTrue(self.df["Month"].cat.ordered)

    def test_day_of_week_ordered_categorical(self):
        self.assertTrue(self.df["DayOfWeek"].cat.ordered)


class TestKPIs(unittest.TestCase):
    """Test the correctness of KPI calculations."""

    @classmethod
    def setUpClass(cls):
        cls.df   = load_clean_data()
        cls.kpis = compute_kpis(cls.df)

    def test_total_transactions(self):
        self.assertEqual(self.kpis["total_transactions"], len(self.df))

    def test_total_value_positive(self):
        self.assertGreater(self.kpis["total_value_inr"], 0)

    def test_success_plus_failed_plus_pending_equals_total(self):
        total = (self.kpis["successful_txns"] +
                 self.kpis["failed_txns"] +
                 self.kpis["pending_txns"])
        self.assertEqual(total, self.kpis["total_transactions"])

    def test_success_rate_in_range(self):
        self.assertGreater(self.kpis["success_rate_pct"], 80)
        self.assertLess(self.kpis["success_rate_pct"], 100)

    def test_failure_rate_in_range(self):
        self.assertGreater(self.kpis["failure_rate_pct"], 0)
        self.assertLess(self.kpis["failure_rate_pct"], 20)

    def test_avg_amount_between_min_max(self):
        self.assertGreater(self.kpis["avg_amount"], self.kpis["min_amount"])
        self.assertLess(self.kpis["avg_amount"], self.kpis["max_amount"])

    def test_p2p_plus_p2m_equals_total(self):
        self.assertEqual(
            self.kpis["p2p_count"] + self.kpis["p2m_count"],
            self.kpis["total_transactions"]
        )

    def test_peak_hour_valid(self):
        self.assertGreaterEqual(self.kpis["peak_hour"], 0)
        self.assertLessEqual(self.kpis["peak_hour"], 23)

    def test_weekend_plus_weekday_equals_total(self):
        self.assertEqual(
            self.kpis["weekend_txns"] + self.kpis["weekday_txns"],
            self.kpis["total_transactions"]
        )

    def test_top_category_not_empty(self):
        self.assertIsNotNone(self.kpis["top_category_by_count"])
        self.assertGreater(len(self.kpis["top_category_by_count"]), 0)

    def test_total_value_success_less_than_total(self):
        self.assertLess(self.kpis["total_value_success"],
                        self.kpis["total_value_inr"])


class TestTrendAnalysis(unittest.TestCase):
    """Validate trend data computations."""

    @classmethod
    def setUpClass(cls):
        cls.df = load_clean_data()

    def test_monthly_records_count(self):
        monthly = self.df.groupby("Month", observed=True).size()
        self.assertEqual(len(monthly), 9, "Should have 9 months of data")

    def test_all_months_have_transactions(self):
        monthly = self.df.groupby("Month", observed=True).size()
        self.assertTrue((monthly > 0).all(), "Some months have 0 transactions")

    def test_hourly_covers_all_24_hours(self):
        hours = self.df["Hour"].unique()
        self.assertEqual(len(hours), 24, f"Expected 24 hours, got {len(hours)}")

    def test_dow_covers_all_7_days(self):
        days = self.df["DayOfWeek"].nunique()
        self.assertEqual(days, 7, f"Expected 7 days, got {days}")

    def test_daily_total_matches_grand_total(self):
        daily_sum = self.df.groupby("TransactionDate")["Amount"].sum().sum()
        self.assertAlmostEqual(daily_sum, self.df["Amount"].sum(), places=0)

    def test_no_negative_daily_amount(self):
        daily_amt = self.df.groupby("TransactionDate")["Amount"].sum()
        self.assertTrue((daily_amt >= 0).all())


class TestCategoryBankAnalysis(unittest.TestCase):
    """Validate category and bank analysis computations."""

    @classmethod
    def setUpClass(cls):
        cls.df = load_clean_data()

    def test_all_15_categories_present(self):
        self.assertEqual(self.df["Category"].nunique(), 15)

    def test_all_banks_present(self):
        self.assertEqual(self.df["SenderBank"].nunique(), 15)

    def test_all_upi_apps_present(self):
        self.assertEqual(self.df["UPIApp"].nunique(), 10)

    def test_category_value_shares_sum_to_100(self):
        shares = (self.df.groupby("Category")["Amount"].sum() /
                  self.df["Amount"].sum() * 100)
        self.assertAlmostEqual(shares.sum(), 100.0, places=1)

    def test_bank_count_sums_to_total(self):
        bank_total = self.df.groupby("SenderBank")["TransactionID"].count().sum()
        self.assertEqual(bank_total, len(self.df))

    def test_p2p_p2m_split(self):
        p2p = (self.df["PaymentType"] == "P2P").sum()
        p2m = (self.df["PaymentType"] == "P2M").sum()
        self.assertEqual(p2p + p2m, len(self.df))

    def test_device_types(self):
        # Standardisation title-cases "iOS" → "Ios"; check case-insensitively
        devices = set(d.lower() for d in self.df["Device"].unique())
        valid   = {"android", "ios", "feature phone (*99#)"}
        self.assertTrue(devices.issubset(valid),
                        f"Unexpected devices: {devices - valid}")


class TestStatusAnalysis(unittest.TestCase):
    """Validate status analysis computations."""

    @classmethod
    def setUpClass(cls):
        cls.df = load_clean_data()

    def test_three_statuses(self):
        statuses = set(self.df["Status"].unique())
        self.assertEqual(statuses, {"SUCCESS","FAILED","PENDING"})

    def test_success_is_majority(self):
        sr = (self.df["Status"] == "SUCCESS").mean()
        self.assertGreater(sr, 0.80, "Success rate should be > 80%")

    def test_failure_rate_by_category_not_zero(self):
        fail_rates = self.df.groupby("Category")["Status"].apply(
            lambda x: (x == "FAILED").mean()
        )
        self.assertTrue((fail_rates >= 0).all())
        self.assertTrue((fail_rates <= 1).all())

    def test_failed_value_positive(self):
        failed_val = self.df[self.df["Status"]=="FAILED"]["Amount"].sum()
        self.assertGreater(failed_val, 0)

    def test_hourly_failure_rate_valid(self):
        hourly_fr = self.df.groupby("Hour")["Status"].apply(
            lambda x: (x=="FAILED").mean() * 100
        )
        self.assertTrue((hourly_fr >= 0).all())
        self.assertTrue((hourly_fr <= 100).all())


class TestOutputFilesPhase2(unittest.TestCase):
    """Verify Phase 2 output files were created."""

    def test_eda_summary_stats_exists(self):
        path = os.path.join(REPORTS_DIR, "eda_summary_stats.txt")
        self.assertTrue(os.path.exists(path))

    def test_eda_category_bank_csv_exists(self):
        path = os.path.join(REPORTS_DIR, "eda_category_bank.csv")
        self.assertTrue(os.path.exists(path))

    def test_eda_status_csv_exists(self):
        path = os.path.join(REPORTS_DIR, "eda_status_analysis.csv")
        self.assertTrue(os.path.exists(path))

    def test_eda_insights_exists(self):
        path = os.path.join(REPORTS_DIR, "eda_business_insights.txt")
        self.assertTrue(os.path.exists(path))

    def test_eda_figures_count(self):
        if os.path.exists(EDA_FIGURES):
            figs = [f for f in os.listdir(EDA_FIGURES) if f.endswith(".png")]
            self.assertGreaterEqual(len(figs), 14,
                                    f"Expected ≥14 EDA charts, found {len(figs)}")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestEDALoader, TestKPIs, TestTrendAnalysis,
                TestCategoryBankAnalysis, TestStatusAnalysis,
                TestOutputFilesPhase2]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

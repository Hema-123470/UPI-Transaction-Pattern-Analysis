"""
config/settings.py
------------------
Central configuration for the UPI Transaction Pattern Analysis project.
All paths, constants and shared parameters live here so every module
imports from one place.
"""

import os

# ── Root directories ──────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
DATA_PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR     = os.path.join(BASE_DIR, "reports")
FIGURES_DIR     = os.path.join(BASE_DIR, "reports", "figures")

# ── File names ────────────────────────────────────────────────────────────────
RAW_FILE        = os.path.join(DATA_RAW_DIR,  "upi_transactions_raw.csv")
CLEAN_FILE      = os.path.join(DATA_PROC_DIR, "upi_transactions_clean.csv")
REPORT_FILE     = os.path.join(REPORTS_DIR,   "preprocessing_report.txt")

# ── Dataset generation parameters ────────────────────────────────────────────
NUM_RECORDS     = 10_000
RANDOM_SEED     = 42

# ── UPI domain constants ──────────────────────────────────────────────────────
BANKS = [
    "SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank",
    "Punjab National Bank", "Bank of Baroda", "Canara Bank",
    "IndusInd Bank", "Yes Bank", "IDFC First Bank", "Union Bank of India",
    "Federal Bank", "RBL Bank", "Paytm Payments Bank"
]

UPI_APPS = [
    "PhonePe", "Google Pay", "Paytm", "BHIM", "Amazon Pay",
    "WhatsApp Pay", "iMobile Pay", "MobiKwik", "Freecharge", "Airtel Payments Bank"
]

CATEGORIES = [
    "Food & Dining", "Groceries", "Shopping", "Utilities",
    "Transportation", "Education", "Healthcare", "Entertainment",
    "Travel", "Fuel", "Rent", "Salary/Transfer", "Insurance",
    "Investments", "EMI/Loan"
]

PAYMENT_TYPES = ["P2P", "P2M"]          # Person-to-Person / Person-to-Merchant

STATES_CITIES = {
    "Maharashtra":  ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Karnataka":    ["Bengaluru", "Mysuru", "Mangaluru", "Hubli", "Belagavi"],
    "Tamil Nadu":   ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Delhi":        ["New Delhi", "Dwarka", "Rohini", "Janakpuri", "Pitampura"],
    "Telangana":    ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    "Gujarat":      ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"],
    "West Bengal":  ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
    "Rajasthan":    ["Jaipur", "Jodhpur", "Kota", "Ajmer", "Bikaner"],
    "Uttar Pradesh":["Lucknow", "Kanpur", "Agra", "Varanasi", "Allahabad"],
    "Kerala":       ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam"],
    "Madhya Pradesh":["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain"],
    "Punjab":       ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala"],
}

DEVICES = ["Android", "iOS", "Feature Phone (*99#)"]

STATUSES = ["SUCCESS", "FAILED", "PENDING"]

# Amount ranges per category (min, max) in INR
AMOUNT_RANGES = {
    "Food & Dining":    (50,    2_500),
    "Groceries":        (100,   5_000),
    "Shopping":         (200,  25_000),
    "Utilities":        (200,   5_000),
    "Transportation":   (20,    2_000),
    "Education":        (500,  50_000),
    "Healthcare":       (200,  20_000),
    "Entertainment":    (100,   5_000),
    "Travel":           (500,  30_000),
    "Fuel":             (500,   5_000),
    "Rent":            (3_000, 50_000),
    "Salary/Transfer": (5_000,200_000),
    "Insurance":       (1_000, 25_000),
    "Investments":     (1_000,100_000),
    "EMI/Loan":        (2_000, 50_000),
}

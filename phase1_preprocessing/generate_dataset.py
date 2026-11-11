"""
phase1_preprocessing/generate_dataset.py
-----------------------------------------
Generates a realistic UPI transaction dataset with 10,000 records
covering Jan 2024 – Sep 2024.

Column schema (mirrors publicly available Kaggle UPI datasets):
  TransactionID       – unique UUID-based identifier
  TransactionDate     – date of transaction (YYYY-MM-DD)
  TransactionTime     – time of transaction (HH:MM:SS)
  DayOfWeek           – Monday … Sunday
  Month               – January … September
  SenderUPI           – sender VPA  (e.g., user1234@oksbi)
  ReceiverUPI         – receiver VPA
  SenderBank          – bank name of sender
  ReceiverBank        – bank name of receiver
  UPIApp              – app used (PhonePe, GPay, Paytm …)
  Amount              – transaction amount in INR
  PaymentType         – P2P or P2M
  Category            – Food & Dining, Travel, Rent …
  State               – Indian state
  City                – city within the state
  Device              – Android / iOS / Feature Phone (*99#)
  Status              – SUCCESS / FAILED / PENDING
  ReferenceNo         – 12-digit numeric reference
  Remarks             – short free-text description

Usage:
    python phase1_preprocessing/generate_dataset.py
"""

import os
import sys
import uuid
import random
import numpy  as np
import pandas as pd
from datetime import datetime, timedelta

# ── Make project root importable ──────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    DATA_RAW_DIR, RAW_FILE, NUM_RECORDS, RANDOM_SEED,
    BANKS, UPI_APPS, CATEGORIES, PAYMENT_TYPES,
    STATES_CITIES, DEVICES, STATUSES, AMOUNT_RANGES
)

# ── Seed for reproducibility ──────────────────────────────────────────────────
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ── Helper generators ─────────────────────────────────────────────────────────

def _upi_handle(bank: str) -> str:
    """Return a VPA like 'raj9812@oksbi'."""
    suffix_map = {
        "SBI":                    "oksbi",
        "HDFC Bank":              "okhdfc",
        "ICICI Bank":             "okicici",
        "Axis Bank":              "okaxis",
        "Kotak Mahindra Bank":    "kotak",
        "Punjab National Bank":   "pnb",
        "Bank of Baroda":         "barodampay",
        "Canara Bank":            "cnrb",
        "IndusInd Bank":          "indus",
        "Yes Bank":               "ybl",
        "IDFC First Bank":        "idfcbank",
        "Union Bank of India":    "unionbank",
        "Federal Bank":           "federal",
        "RBL Bank":               "rbl",
        "Paytm Payments Bank":    "paytm",
    }
    names = [
        "raj","priya","amit","sneha","rahul","divya","ankit","pooja",
        "vikram","kavya","rohan","neha","sanjay","meera","arjun","riya",
        "arun","nisha","kiran","suresh","deepa","mohan","geeta","venkat",
        "lakshmi","ganesh","usha","ramesh","sunita","anil","rekha","vijay"
    ]
    name = random.choice(names)
    num  = random.randint(1000, 9999)
    suffix = suffix_map.get(bank, "upi")
    return f"{name}{num}@{suffix}"


def _reference_no() -> str:
    return str(random.randint(100_000_000_000, 999_999_999_999))


def _remarks(category: str, payment_type: str) -> str:
    remarks_map = {
        "Food & Dining":    ["Zomato order", "Swiggy delivery", "Restaurant bill", "Café payment"],
        "Groceries":        ["BigBasket order", "Blinkit purchase", "Local kirana store", "DMart shopping"],
        "Shopping":         ["Flipkart purchase", "Amazon order", "Myntra order", "Meesho order"],
        "Utilities":        ["Electricity bill", "Water bill", "Gas cylinder payment", "DTH recharge"],
        "Transportation":   ["Ola ride", "Uber ride", "Metro card recharge", "Auto fare"],
        "Education":        ["School fees", "College fees", "Online course", "Coaching institute"],
        "Healthcare":       ["Pharmacy bill", "Doctor consultation", "Hospital payment", "Lab test"],
        "Entertainment":    ["PVR tickets", "BookMyShow", "OTT subscription", "Gaming top-up"],
        "Travel":           ["MakeMyTrip booking", "IRCTC ticket", "Hotel booking", "Bus ticket"],
        "Fuel":             ["Petrol station", "HP petrol pump", "BPCL fuel", "Indian Oil pump"],
        "Rent":             ["Monthly rent", "PG rent payment", "House rent"],
        "Salary/Transfer":  ["Monthly salary", "Freelance payment", "Money transfer", "Family transfer"],
        "Insurance":        ["LIC premium", "Health insurance", "Vehicle insurance", "Term plan"],
        "Investments":      ["SIP payment", "Mutual fund", "Stock purchase", "FD creation"],
        "EMI/Loan":         ["Home loan EMI", "Car loan EMI", "Personal loan EMI", "Credit card EMI"],
    }
    pool = remarks_map.get(category, ["UPI Payment"])
    remark = random.choice(pool)
    if payment_type == "P2P":
        names = ["Rahul","Priya","Amit","Sneha","Kavya","Vikram","Deepa","Ankit"]
        remark = f"Transfer to {random.choice(names)}"
    return remark


# ── Main dataset builder ──────────────────────────────────────────────────────

def generate_dataset(n: int = NUM_RECORDS) -> pd.DataFrame:
    """Generate n UPI transaction records and return a DataFrame."""

    # Date range: 01-Jan-2024 to 30-Sep-2024
    start_date = datetime(2024, 1, 1)
    end_date   = datetime(2024, 9, 30)
    date_range_days = (end_date - start_date).days

    rows = []
    for _ in range(n):
        # ── Temporal ──────────────────────────────────────────────────────────
        rand_days     = random.randint(0, date_range_days)
        rand_seconds  = random.randint(0, 86_399)
        txn_datetime  = start_date + timedelta(days=rand_days, seconds=rand_seconds)
        txn_date      = txn_datetime.strftime("%Y-%m-%d")
        txn_time      = txn_datetime.strftime("%H:%M:%S")
        day_of_week   = txn_datetime.strftime("%A")
        month         = txn_datetime.strftime("%B")

        # ── Banking ───────────────────────────────────────────────────────────
        sender_bank   = random.choice(BANKS)
        receiver_bank = random.choice(BANKS)
        sender_upi    = _upi_handle(sender_bank)
        receiver_upi  = _upi_handle(receiver_bank)
        upi_app       = random.choice(UPI_APPS)

        # ── Transaction ───────────────────────────────────────────────────────
        payment_type  = random.choices(PAYMENT_TYPES, weights=[40, 60])[0]
        category      = random.choice(CATEGORIES)

        # Salary/Transfer is always P2P
        if category == "Salary/Transfer":
            payment_type = "P2P"

        amt_min, amt_max = AMOUNT_RANGES[category]
        # Use log-normal so small amounts are more frequent
        amount = round(np.random.uniform(amt_min, amt_max), 2)

        # ── Geography ─────────────────────────────────────────────────────────
        state  = random.choice(list(STATES_CITIES.keys()))
        city   = random.choice(STATES_CITIES[state])

        # ── Device ────────────────────────────────────────────────────────────
        device = random.choices(DEVICES, weights=[60, 35, 5])[0]

        # ── Status (SUCCESS ~88 %, FAILED ~9 %, PENDING ~3 %) ─────────────────
        status = random.choices(STATUSES, weights=[88, 9, 3])[0]

        # ── Reference & Remarks ───────────────────────────────────────────────
        ref_no  = _reference_no()
        remark  = _remarks(category, payment_type)

        rows.append({
            "TransactionID":   str(uuid.UUID(int=random.getrandbits(128))),
            "TransactionDate": txn_date,
            "TransactionTime": txn_time,
            "DayOfWeek":       day_of_week,
            "Month":           month,
            "SenderUPI":       sender_upi,
            "ReceiverUPI":     receiver_upi,
            "SenderBank":      sender_bank,
            "ReceiverBank":    receiver_bank,
            "UPIApp":          upi_app,
            "Amount":          amount,
            "PaymentType":     payment_type,
            "Category":        category,
            "State":           state,
            "City":            city,
            "Device":          device,
            "Status":          status,
            "ReferenceNo":     ref_no,
            "Remarks":         remark,
        })

    df = pd.DataFrame(rows)
    df.sort_values("TransactionDate", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    print("=" * 60)
    print("  UPI Transaction Pattern Analysis")
    print("  Phase 1 – Dataset Generation")
    print("=" * 60)

    print(f"\n[INFO] Generating {NUM_RECORDS:,} UPI transaction records …")
    df = generate_dataset()

    df.to_csv(RAW_FILE, index=False)
    print(f"[INFO] Raw dataset saved → {RAW_FILE}")

    print(f"\n[PREVIEW] First 5 rows:")
    print(df.head().to_string(index=False))

    print(f"\n[SUMMARY]")
    print(f"  Total records  : {len(df):,}")
    print(f"  Columns        : {list(df.columns)}")
    print(f"  Date range     : {df['TransactionDate'].min()}  →  {df['TransactionDate'].max()}")
    print(f"  Amount range   : ₹{df['Amount'].min():,.2f}  –  ₹{df['Amount'].max():,.2f}")
    print(f"  Total volume   : ₹{df['Amount'].sum():,.2f}")
    print(f"  Status counts  :\n{df['Status'].value_counts().to_string()}")
    print("\n[DONE] Dataset generation complete.")

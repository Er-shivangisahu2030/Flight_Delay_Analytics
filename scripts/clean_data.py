"""
clean_data.py
--------------
Cleans the raw flight records CSV and writes a cleaned CSV ready for MySQL.

Responsibilities:
    1. Remove duplicate rows
    2. Handle null values
    3. Convert FL_DATE to proper date format
    4. Remove invalid delay values (impossible outliers, bad distances)
    5. Save cleaned CSV to data/flights_cleaned.csv

Run:
    python scripts/clean_data.py
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "flights_small.csv")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "flights_cleaned.csv")

# Any single delay beyond this many minutes is treated as a bad/corrupt
# record rather than a real flight (e.g. sensor or entry errors).
MAX_REASONABLE_DELAY_MIN = 1440  # 24 hours


def load_raw_data(path: str) -> pd.DataFrame:
    print(f"Loading raw data from: {path}")
    df = pd.read_csv(path)
    print(f"  -> {len(df):,} rows loaded")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    print(f"Removed {removed:,} duplicate rows")
    return df


def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Drop rows where we are missing the airline or the date - these are
    # not recoverable / not useful for analysis.
    df = df.dropna(subset=["AIRLINE", "FL_DATE", "ORIGIN", "DEST"])

    # For numeric delay columns, a missing value most often means the
    # field wasn't recorded. We fill with 0 rather than dropping the row,
    # since the flight still happened and other columns are still useful.
    for col in ["DEP_DELAY", "ARR_DELAY"]:
        missing = df[col].isnull().sum()
        if missing:
            df[col] = df[col].fillna(0)
            print(f"  Filled {missing:,} missing values in {col} with 0")

    # DISTANCE missing -> can't be inferred reliably, drop those rows.
    df = df.dropna(subset=["DISTANCE"])

    removed = before - len(df)
    print(f"Handled nulls (dropped {removed:,} unrecoverable rows)")
    return df


def convert_date_format(df: pd.DataFrame) -> pd.DataFrame:
    df["FL_DATE"] = pd.to_datetime(df["FL_DATE"], errors="coerce").dt.date
    before = len(df)
    df = df.dropna(subset=["FL_DATE"])
    removed = before - len(df)
    if removed:
        print(f"Dropped {removed:,} rows with unparseable dates")
    print("Converted FL_DATE to proper date format (YYYY-MM-DD)")
    return df


def remove_invalid_values(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Remove impossible/outlier delay values (data entry errors).
    df = df[df["DEP_DELAY"].abs() <= MAX_REASONABLE_DELAY_MIN]
    df = df[df["ARR_DELAY"].abs() <= MAX_REASONABLE_DELAY_MIN]

    # Distance must be a positive number.
    df = df[df["DISTANCE"] > 0]

    # Cancelled flag should only ever be 0 or 1.
    df = df[df["CANCELLED"].isin([0, 1])]

    removed = before - len(df)
    print(f"Removed {removed:,} rows with invalid delay/distance/cancelled values")
    return df


def finalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    keep_cols = [
        "FL_DATE", "AIRLINE", "ORIGIN", "DEST",
        "DEP_DELAY", "ARR_DELAY", "CANCELLED", "DISTANCE",
    ]
    df = df[keep_cols]
    df["CANCELLED"] = df["CANCELLED"].astype(int)
    df["DEP_DELAY"] = df["DEP_DELAY"].astype(float)
    df["ARR_DELAY"] = df["ARR_DELAY"].astype(float)
    df["DISTANCE"] = df["DISTANCE"].astype(float)
    return df


def main():
    df = load_raw_data(RAW_PATH)
    df = remove_duplicates(df)
    df = handle_nulls(df)
    df = convert_date_format(df)
    df = remove_invalid_values(df)
    df = finalize_columns(df)

    df.to_csv(CLEAN_PATH, index=False)
    print(f"\nCleaned dataset saved to: {CLEAN_PATH}")
    print(f"Final row count: {len(df):,}")


if __name__ == "__main__":
    main()

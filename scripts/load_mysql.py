"""
load_mysql.py
--------------
Loads the cleaned flight data into MySQL.

Responsibilities:
    1. Connect to MySQL
    2. Create the `flights` table (drops and recreates it for a clean run)
    3. Insert the cleaned CSV data in bulk

Run:
    python scripts/load_mysql.py
"""

import os
import sys
import pandas as pd
from sqlalchemy import text

# Allow running this file directly from the scripts/ folder or from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db_config import get_engine, DB_NAME  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "flights_cleaned.csv")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS flights (
    flight_date DATE,
    airline     VARCHAR(50),
    origin      VARCHAR(10),
    destination VARCHAR(10),
    dep_delay   FLOAT,
    arr_delay   FLOAT,
    cancelled   TINYINT,
    distance    FLOAT
);
"""


def create_table(engine):
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS flights;"))
        conn.execute(text(CREATE_TABLE_SQL))
        conn.commit()
    print("Table 'flights' created (or recreated).")


def load_data(engine):
    print(f"Reading cleaned data from: {CLEAN_PATH}")
    df = pd.read_csv(CLEAN_PATH)

    # Rename columns to match MySQL table schema
    df = df.rename(columns={
        "FL_DATE": "flight_date",
        "AIRLINE": "airline",
        "ORIGIN": "origin",
        "DEST": "destination",
        "DEP_DELAY": "dep_delay",
        "ARR_DELAY": "arr_delay",
        "CANCELLED": "cancelled",
        "DISTANCE": "distance",
    })

    print(f"Inserting {len(df):,} rows into MySQL...")
    df.to_sql("flights", con=engine, if_exists="append", index=False, chunksize=5000)
    print("Insert complete.")


def verify(engine):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM flights;"))
        count = result.scalar()
    print(f"Verification: 'flights' table now contains {count:,} rows.")


def main():
    print(f"Connecting to MySQL database: {DB_NAME}")
    engine = get_engine()

    create_table(engine)
    load_data(engine)
    verify(engine)


if __name__ == "__main__":
    main()

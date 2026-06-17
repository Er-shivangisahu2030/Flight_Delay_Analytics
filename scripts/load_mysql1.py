"""
load_mysql.py
--------------
Loads the cleaned flight data into MySQL.
"""

import os
import sys
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_config import get_engine, DB_NAME  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "flights_cleaned.csv")

CREATE_TABLE_SQL = """
CREATE TABLE flights (
    flight_date DATE,
    airline VARCHAR(50),
    origin VARCHAR(10),
    destination VARCHAR(10),
    dep_delay FLOAT,
    arr_delay FLOAT,
    cancelled TINYINT,
    distance FLOAT
);
"""


def create_table(engine):
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS flights"))
        conn.execute(text(CREATE_TABLE_SQL))

    print("✓ Table flights recreated")


def load_data(engine):
    if not os.path.exists(CLEAN_PATH):
        raise FileNotFoundError(f"Clean dataset not found: {CLEAN_PATH}")

    print(f"Reading: {CLEAN_PATH}")

    df = pd.read_csv(CLEAN_PATH)

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

    print(f"Loading {len(df):,} records...")

    df.to_sql(
        "flights",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

    print("✓ Data load complete")


def verify(engine):
    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM flights")
        ).scalar()

    print(f"✓ Verification successful: {count:,} rows")


def main():
    print(f"Connecting to database: {DB_NAME}")

    engine = get_engine()

    create_table(engine)
    load_data(engine)
    verify(engine)


if __name__ == "__main__":
    main()
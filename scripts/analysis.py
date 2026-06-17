"""
analysis.py
-----------
Analytics queries for Airline Delay & Operations Analytics Platform

Run:
    python scripts/analysis.py
"""

import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_config import get_engine

def query_avg_delay_by_airline(engine) -> pd.DataFrame:
    sql = """
    SELECT
        airline,
        ROUND(AVG(arr_delay), 2) AS avg_delay,
        COUNT(*) AS total_flights
    FROM flights
    GROUP BY airline
    ORDER BY avg_delay DESC;
    """
    return pd.read_sql(sql, engine)


def query_most_delayed_routes(engine, limit=20) -> pd.DataFrame:
    sql = f"""
    SELECT
        origin,
        destination,
        ROUND(AVG(arr_delay), 2) AS avg_delay,
        COUNT(*) AS total_flights
    FROM flights
    GROUP BY origin, destination
    ORDER BY avg_delay DESC
    LIMIT {limit};
    """
    return pd.read_sql(sql, engine)


def query_cancellation_rate(engine):
    sql = """
    SELECT ROUND(100 * AVG(cancelled), 2) AS cancellation_rate
    FROM flights;
    """
    df = pd.read_sql(sql, engine)

    value = df["cancellation_rate"].iloc[0]

    return 0.0 if pd.isna(value) else float(value)


def query_cancellation_rate_by_airline(engine) -> pd.DataFrame:
    sql = """
    SELECT
        airline,
        ROUND(100 * AVG(cancelled), 2) AS cancellation_rate,
        COUNT(*) AS total_flights
    FROM flights
    GROUP BY airline
    ORDER BY cancellation_rate DESC;
    """
    return pd.read_sql(sql, engine)


def query_top_airports(engine, limit=10) -> pd.DataFrame:
    sql = f"""
    SELECT
        origin AS airport,
        COUNT(*) AS total_flights
    FROM flights
    GROUP BY origin
    ORDER BY total_flights DESC
    LIMIT {limit};
    """
    return pd.read_sql(sql, engine)



def query_monthly_delay_trend(engine) -> pd.DataFrame:
    sql = """
    SELECT
        DATE_FORMAT(flight_date, '%%Y-%%m') AS month,
        ROUND(AVG(arr_delay), 2) AS avg_delay,
        COUNT(*) AS total_flights
    FROM flights
    GROUP BY month
    ORDER BY month;
    """
    return pd.read_sql(sql, engine)
def query_kpis(engine) -> dict:

    total_flights_df = pd.read_sql(
        "SELECT COUNT(*) AS total_flights FROM flights;",
        engine
    )

    avg_delay_df = pd.read_sql(
        "SELECT ROUND(AVG(arr_delay), 2) AS avg_delay FROM flights;",
        engine
    )

    num_airlines_df = pd.read_sql(
        "SELECT COUNT(DISTINCT airline) AS num_airlines FROM flights;",
        engine
    )

    total_flights = total_flights_df["total_flights"].iloc[0]
    avg_delay = avg_delay_df["avg_delay"].iloc[0]
    num_airlines = num_airlines_df["num_airlines"].iloc[0]

    if pd.isna(avg_delay):
        avg_delay = 0

    cancellation_rate = query_cancellation_rate(engine)

    return {
        "total_flights": int(total_flights or 0),
        "avg_delay": float(avg_delay),
        "cancellation_rate": float(cancellation_rate),
        "num_airlines": int(num_airlines or 0),
    }


def main():

    engine = get_engine()

    print("\n========== KPI SUMMARY ==========")

    try:
        kpis = query_kpis(engine)

        for key, value in kpis.items():
            print(f"{key}: {value}")

        print("\n========== AVG DELAY BY AIRLINE ==========")
        print(query_avg_delay_by_airline(engine).to_string(index=False))

        print("\n========== MOST DELAYED ROUTES ==========")
        print(query_most_delayed_routes(engine).to_string(index=False))

        print("\n========== CANCELLATION RATE BY AIRLINE ==========")
        print(query_cancellation_rate_by_airline(engine).to_string(index=False))

        print("\n========== TOP AIRPORTS ==========")
        print(query_top_airports(engine).to_string(index=False))

        print("\n========== MONTHLY DELAY TREND ==========")
        print(query_monthly_delay_trend(engine).to_string(index=False))

    except Exception as e:
        print("\nERROR:")
        print(e)


if __name__ == "__main__":
    main()
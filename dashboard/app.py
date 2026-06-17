"""
app.py
------
Streamlit Dashboard for Flight Delays Analytics Platform

Run:
    streamlit run dashboard/app.py
"""

import os
import sys

import streamlit as st
import plotly.express as px

# ------------------------------------------------------------------
# Make scripts folder importable
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

from db_config import get_engine
from analysis import (
    query_avg_delay_by_airline,
    query_most_delayed_routes,
    query_cancellation_rate_by_airline,
    query_top_airports,
    query_monthly_delay_trend,
    query_kpis,
)

# ------------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Flight Delays Analytics",
    page_icon="✈️",
    layout="wide",
)

# ------------------------------------------------------------------
# Database Connection
# ------------------------------------------------------------------
@st.cache_resource
def get_db():
    return get_engine()


@st.cache_data(ttl=300)
def load_dashboard_data():
    engine = get_db()

    return {
        "kpis": query_kpis(engine),
        "airlines": query_avg_delay_by_airline(engine),
        "routes": query_most_delayed_routes(engine, limit=15),
        "cancel": query_cancellation_rate_by_airline(engine),
        "airports": query_top_airports(engine, limit=10),
        "trend": query_monthly_delay_trend(engine),
    }


# ------------------------------------------------------------------
# Title
# ------------------------------------------------------------------
st.title("✈️ Flight Delay Analytics Dashboard")

st.markdown(
    """
    Analyze airline performance, delays, cancellations,
    route efficiency, and airport traffic using
    **Python + MySQL + SQL + Streamlit**.
    """
)

# ------------------------------------------------------------------
# Load Data
# ------------------------------------------------------------------
try:
    data = load_dashboard_data()

except Exception as e:
    st.error(f"""
Unable to connect to MySQL database.

Please verify:

1. MySQL service is running
2. Database 'airline_dw' exists
3. Flights table is loaded
4. Credentials in db_config.py are correct

Error:
{e}
""")
    st.stop()

# ------------------------------------------------------------------
# KPI Section
# ------------------------------------------------------------------
st.subheader("📊 Key Performance Indicators")

kpis = data["kpis"]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total Flights",
        f"{kpis['total_flights']:,}"
    )

with c2:
    st.metric(
        "Average Delay (Min)",
        f"{kpis['avg_delay']:.2f}"
    )

with c3:
    st.metric(
        "Cancellation Rate",
        f"{kpis['cancellation_rate']:.2f}%"
    )

with c4:
    st.metric(
        "Number of Airlines",
        f"{kpis['num_airlines']}"
    )

st.divider()

# ------------------------------------------------------------------
# Row 1
# ------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("🚨 Top Delayed Airlines")

    fig = px.bar(
        data["airlines"].head(10),
        x="avg_delay",
        y="airline",
        orientation="h",
        color="avg_delay",
        labels={
            "avg_delay": "Average Arrival Delay (Minutes)",
            "airline": "Airline"
        },
        color_continuous_scale="Reds",
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📈 Monthly Delay Trend")

    fig = px.line(
        data["trend"],
        x="month",
        y="avg_delay",
        markers=True,
        labels={
            "month": "Month",
            "avg_delay": "Average Delay"
        }
    )

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# Row 2
# ------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("🛫 Top Airports by Flight Volume")

    fig = px.bar(
        data["airports"],
        x="airport",
        y="total_flights",
        color="total_flights",
        color_continuous_scale="Blues",
        labels={
            "airport": "Airport",
            "total_flights": "Flights"
        }
    )

    fig.update_layout(
        showlegend=False,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("❌ Cancellation Rate by Airline")

    fig = px.bar(
        data["cancel"],
        x="cancellation_rate",
        y="airline",
        orientation="h",
        color="cancellation_rate",
        labels={
            "cancellation_rate": "Cancellation Rate (%)",
            "airline": "Airline"
        },
        color_continuous_scale="Oranges",
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# Delayed Routes Table
# ------------------------------------------------------------------
st.divider()

st.subheader("🛬 Top 15 Most Delayed Routes")

st.dataframe(
    data["routes"],
    use_container_width=True,
    hide_index=True
)

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.divider()

st.caption(
    "Airline Delay & Operations Analytics Platform | "
    "Built using Python, MySQL, SQLAlchemy, Plotly and Streamlit"
)
-- analytics_queries.sql
-- Standalone reference copy of every analytics query used by analysis.py
-- and the Streamlit dashboard. Run these directly in MySQL Workbench /
-- CLI if you want to explore the data without Python.
USE airlinedw_project;

-- 1. Average arrival delay by airline (highest delays first)
SELECT
    airline,
    ROUND(AVG(arr_delay), 2) AS avg_delay,
    COUNT(*) AS total_flights
FROM flights
GROUP BY airline
ORDER BY avg_delay DESC;

-- 2. Most delayed routes (origin -> destination)
SELECT
    origin,
    destination,
    ROUND(AVG(arr_delay), 2) AS avg_delay,
    COUNT(*) AS total_flights
FROM flights
GROUP BY origin, destination
ORDER BY avg_delay DESC
LIMIT 20;

-- 3. Overall cancellation rate (%)
SELECT
    ROUND(100 * AVG(cancelled), 2) AS cancellation_rate
FROM flights;

-- 4. Cancellation rate by airline
SELECT
    airline,
    ROUND(100 * AVG(cancelled), 2) AS cancellation_rate,
    COUNT(*) AS total_flights
FROM flights
GROUP BY airline
ORDER BY cancellation_rate DESC;

-- 5. Busiest airports (by total flights, origin + destination combined)
SELECT
    origin AS airport,
    COUNT(*) AS total_flights
FROM flights
GROUP BY origin
ORDER BY total_flights DESC
LIMIT 10;

-- 6. Monthly average delay trend
SELECT
    DATE_FORMAT(flight_date, '%Y-%m') AS month,
    ROUND(AVG(arr_delay), 2) AS avg_delay,
    COUNT(*) AS total_flights
FROM flights
GROUP BY month
ORDER BY month;

-- 7. KPI: total flights
SELECT COUNT(*) AS total_flights FROM flights;

-- 8. KPI: overall average arrival delay
SELECT ROUND(AVG(arr_delay), 2) AS avg_delay FROM flights;

-- 9. KPI: number of distinct airlines
SELECT COUNT(DISTINCT airline) AS num_airlines FROM flights;

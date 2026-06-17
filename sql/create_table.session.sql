-- create_table.sql
-- Creates the database (if needed) and the single flat `flights` table.
-- No foreign keys, no dimension/fact tables, no star schema by design.

CREATE DATABASE IF NOT EXISTS airlinedw_project;t;
USE airlinedw_project;


DROP TABLE IF EXISTS flights;

CREATE TABLE flights (
    flight_date DATE,
    airline     VARCHAR(50),
    origin      VARCHAR(10),
    destination VARCHAR(10),
    dep_delay   FLOAT,
    arr_delay   FLOAT,
    cancelled   TINYINT,
    distance    FLOAT
);

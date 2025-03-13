-- Show current user
SELECT CURRENT_USER();

-- Show current role
SELECT CURRENT_ROLE();

-- Show databases the current user has access to
SHOW DATABASES;

-- Show schemas in the current database
SHOW SCHEMAS;

-- Show available warehouses
SHOW WAREHOUSES;

-- Check if we can create a database
CREATE DATABASE IF NOT EXISTS MERCURIOS_DATA;

-- Try to use the database
USE DATABASE MERCURIOS_DATA;

-- Try to create a schema
CREATE SCHEMA IF NOT EXISTS MERCURIOS_DATA.ANALYTICS;

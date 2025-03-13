-- Script to create necessary database objects for Mercurios
-- Run this with appropriate privileges (ACCOUNTADMIN or similar)

-- 1. Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS MERCURIOS_DATA;

-- 2. Create schemas if they don't exist
USE DATABASE MERCURIOS_DATA;
CREATE SCHEMA IF NOT EXISTS RAW;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;
CREATE SCHEMA IF NOT EXISTS FIVETRAN_METADATA;

-- 3. Grant permissions to your user
GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA TO ROLE MERCURIOS_FIVETRAN_SERVICE;

GRANT CREATE TABLE, CREATE VIEW ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA TO ROLE MERCURIOS_FIVETRAN_SERVICE;

-- 4. Create sample tables for testing
USE SCHEMA MERCURIOS_DATA.ANALYTICS;

-- Sample inventory table
CREATE TABLE IF NOT EXISTS inventory (
    product_id VARCHAR(50),
    product_name VARCHAR(255),
    sku VARCHAR(50),
    quantity INTEGER,
    reorder_point INTEGER,
    days_of_inventory FLOAT,
    last_updated TIMESTAMP_NTZ
);

-- Sample shopify orders table
CREATE TABLE IF NOT EXISTS shopify_orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    order_date TIMESTAMP_NTZ,
    total_amount FLOAT,
    status VARCHAR(50)
);

-- Sample klaviyo metrics table
CREATE TABLE IF NOT EXISTS klaviyo_metrics (
    event_id VARCHAR(50),
    event_name VARCHAR(100),
    customer_id VARCHAR(50),
    timestamp TIMESTAMP_NTZ,
    properties VARIANT
);

-- Sample google analytics data
CREATE TABLE IF NOT EXISTS ga_sessions (
    session_id VARCHAR(50),
    user_id VARCHAR(50),
    start_time TIMESTAMP_NTZ,
    end_time TIMESTAMP_NTZ,
    device VARCHAR(50),
    channel VARCHAR(50),
    page_views INTEGER,
    events VARIANT
);

-- 5. Insert sample data
INSERT INTO inventory (product_id, product_name, sku, quantity, reorder_point, days_of_inventory, last_updated)
VALUES
    ('P001', 'T-Shirt Large', 'TSH-L-001', 120, 20, 15.5, CURRENT_TIMESTAMP()),
    ('P002', 'T-Shirt Medium', 'TSH-M-001', 85, 15, 12.2, CURRENT_TIMESTAMP()),
    ('P003', 'Jeans 32x30', 'JNS-32-30', 45, 10, 8.7, CURRENT_TIMESTAMP()),
    ('P004', 'Hoodie Black', 'HOD-BLK-L', 62, 12, 10.3, CURRENT_TIMESTAMP()),
    ('P005', 'Socks 3-Pack', 'SCK-3PK', 200, 30, 25.0, CURRENT_TIMESTAMP());

INSERT INTO shopify_orders (order_id, customer_id, order_date, total_amount, status)
VALUES
    ('ORD-001', 'CUST-001', CURRENT_TIMESTAMP() - INTERVAL '2 DAY', 125.99, 'completed'),
    ('ORD-002', 'CUST-002', CURRENT_TIMESTAMP() - INTERVAL '1 DAY', 79.50, 'processing'),
    ('ORD-003', 'CUST-001', CURRENT_TIMESTAMP() - INTERVAL '5 DAY', 45.25, 'completed'),
    ('ORD-004', 'CUST-003', CURRENT_TIMESTAMP() - INTERVAL '3 DAY', 199.99, 'completed'),
    ('ORD-005', 'CUST-004', CURRENT_TIMESTAMP(), 35.75, 'pending');

-- Verify setup
SELECT 'Database objects created successfully!' AS status;

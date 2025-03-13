-- Snowflake Troubleshooting Script
-- Run this script to diagnose permission issues and fix the cost optimization

-- 1. Check current context and permissions
SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();

-- 2. Use ACCOUNTADMIN role to ensure proper permissions
USE ROLE ACCOUNTADMIN;

-- 3. Set the correct database and schema context
USE DATABASE MERCURIOS_DATA;
USE SCHEMA PUBLIC;

-- 4. Verify warehouse existence and permissions
SHOW WAREHOUSES;

-- 5. Try optimizing warehouses with explicit database references
-- Reduce warehouse size when not in heavy ETL periods
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL';

-- Set aggressive auto-suspend to minimize idle time (60 seconds)
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET AUTO_SUSPEND = 60;

-- Configure auto-scaling to handle varying loads efficiently
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET MIN_CLUSTER_COUNT = 1, MAX_CLUSTER_COUNT = 2;

-- Also optimize other warehouses
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET AUTO_SUSPEND = 60;

-- 6. Create resource monitor with explicit database references
CREATE OR REPLACE RESOURCE MONITOR mercurios_cost_monitor
WITH 
    CREDIT_QUOTA = 100,
    FREQUENCY = MONTHLY,
    START_TIMESTAMP = CURRENT_TIMESTAMP,
    END_TIMESTAMP = NULL
;

-- 7. Apply resource monitor to warehouses
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;

-- 8. Create views with fully qualified names
CREATE OR REPLACE VIEW MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring AS
SELECT
    WAREHOUSE_NAME,
    DATE_TRUNC('day', START_TIME) AS usage_date,
    COUNT(*) AS query_count,
    SUM(EXECUTION_TIME) / 1000 / 60 / 60 AS execution_hours,
    SUM(CREDITS_USED) AS credits_used,
    AVG(EXECUTION_TIME) / 1000 AS avg_execution_seconds,
    MAX(EXECUTION_TIME) / 1000 AS max_execution_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY 1, 2
ORDER BY usage_date DESC, credits_used DESC;

-- 9. Verify changes
SELECT 
    WAREHOUSE_NAME, 
    WAREHOUSE_SIZE, 
    AUTO_SUSPEND, 
    MIN_CLUSTER_COUNT, 
    MAX_CLUSTER_COUNT,
    RESOURCE_MONITOR
FROM INFORMATION_SCHEMA.WAREHOUSES
WHERE WAREHOUSE_NAME IN ('MERCURIOS_LOADING_WH', 'MERCURIOS_ANALYTICS_WH', 'COMPUTE_WH', 'MERCURIOS_DEV_WH');

-- 10. Show resource monitors
SHOW RESOURCE MONITORS;

-- 11. Check if the view was created
SHOW VIEWS IN MERCURIOS_DATA.PUBLIC;

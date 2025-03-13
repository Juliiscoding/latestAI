-- Snowflake Cost Optimization Script - Direct Execution Version
-- Copy and paste this entire script into the Snowflake console to execute

-- 1. Optimize MERCURIOS_LOADING_WH Usage
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

-- 2. Set Up Cost Controls
-- Create a resource monitor with monthly quota
CREATE OR REPLACE RESOURCE MONITOR mercurios_cost_monitor
WITH 
    CREDIT_QUOTA = 100, -- Adjust based on your monthly budget
    FREQUENCY = MONTHLY,
    START_TIMESTAMP = CURRENT_TIMESTAMP,
    END_TIMESTAMP = NULL
;

-- Apply resource monitor to warehouses
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;

-- 3. Create views to monitor costs
-- Create a view to monitor warehouse usage and costs
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

-- Create a view to monitor query costs by type
CREATE OR REPLACE VIEW MERCURIOS_DATA.PUBLIC.query_cost_by_type AS
SELECT
    QUERY_TYPE,
    COUNT(*) AS query_count,
    SUM(CREDITS_USED) AS total_credits,
    AVG(CREDITS_USED) AS avg_credits_per_query,
    SUM(CREDITS_USED) / SUM(SUM(CREDITS_USED)) OVER () * 100 AS percentage_of_total
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(month, -1, CURRENT_TIMESTAMP())
AND CREDITS_USED > 0
GROUP BY QUERY_TYPE
ORDER BY total_credits DESC;

-- Create a view to identify expensive queries
CREATE OR REPLACE VIEW MERCURIOS_DATA.PUBLIC.expensive_queries AS
SELECT
    QUERY_ID,
    QUERY_TEXT,
    DATABASE_NAME,
    SCHEMA_NAME,
    QUERY_TYPE,
    USER_NAME,
    WAREHOUSE_NAME,
    EXECUTION_TIME / 1000 AS execution_seconds,
    CREDITS_USED,
    START_TIME
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
AND CREDITS_USED > 0.1
ORDER BY CREDITS_USED DESC
LIMIT 100;

-- 4. Grant access to the new views
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.query_cost_by_type TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.expensive_queries TO ROLE MERCURIOS_FIVETRAN_USER;

-- 5. Implement Time-Based Warehouse Scaling (if tasks are supported in your Snowflake edition)
-- Uncomment and run this section if you have Enterprise or higher edition

/*
-- Create a task to resize warehouses for off-hours (8PM Berlin time)
CREATE OR REPLACE TASK resize_warehouses_for_off_hours
    WAREHOUSE = MERCURIOS_DEV_WH
    SCHEDULE = 'USING CRON 0 20 * * * Europe/Berlin'
AS
BEGIN
    ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL';
    ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET WAREHOUSE_SIZE = 'XSMALL';
END;

-- Create a task to resize warehouses for business hours (8AM Berlin time)
CREATE OR REPLACE TASK resize_warehouses_for_business_hours
    WAREHOUSE = MERCURIOS_DEV_WH
    SCHEDULE = 'USING CRON 0 8 * * * Europe/Berlin'
AS
BEGIN
    -- Only scale up if needed for business hours
    ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'SMALL';
    ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET WAREHOUSE_SIZE = 'SMALL';
END;

-- Enable the tasks
ALTER TASK resize_warehouses_for_off_hours RESUME;
ALTER TASK resize_warehouses_for_business_hours RESUME;
*/

-- Verify changes
SELECT 
    WAREHOUSE_NAME, 
    WAREHOUSE_SIZE, 
    AUTO_SUSPEND, 
    MIN_CLUSTER_COUNT, 
    MAX_CLUSTER_COUNT,
    RESOURCE_MONITOR
FROM INFORMATION_SCHEMA.WAREHOUSES
WHERE WAREHOUSE_NAME IN ('MERCURIOS_LOADING_WH', 'MERCURIOS_ANALYTICS_WH', 'COMPUTE_WH', 'MERCURIOS_DEV_WH');

-- Show resource monitors
SHOW RESOURCE MONITORS;

-- Show new views
SHOW VIEWS IN MERCURIOS_DATA.PUBLIC;

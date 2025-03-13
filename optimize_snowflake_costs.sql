-- Snowflake Cost Optimization Script for Mercurios.ai
-- Run this script as ACCOUNTADMIN to implement cost-saving measures

-- 1. Configure warehouse auto-suspension and sizing
-- Development warehouse: Auto-suspend after 5 minutes of inactivity
ALTER WAREHOUSE MERCURIOS_DEV_WH SET 
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    COMMENT = 'Development warehouse with 5-minute auto-suspension';

-- Analytics warehouse: Auto-suspend after 10 minutes of inactivity
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET 
    AUTO_SUSPEND = 600
    AUTO_RESUME = TRUE
    COMMENT = 'Analytics warehouse with 10-minute auto-suspension';

-- Loading warehouse: Auto-suspend after 15 minutes of inactivity
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET 
    AUTO_SUSPEND = 900
    AUTO_RESUME = TRUE
    COMMENT = 'Loading warehouse with 15-minute auto-suspension';

-- 2. Implement resource monitors to prevent unexpected costs
-- Create resource monitor for development
CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_DEV_MONITOR
    WITH CREDIT_QUOTA = 10
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS ON 75 PERCENT DO NOTIFY
             ON 90 PERCENT DO NOTIFY
             ON 100 PERCENT DO SUSPEND;

-- Create resource monitor for analytics
CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_ANALYTICS_MONITOR
    WITH CREDIT_QUOTA = 20
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS ON 75 PERCENT DO NOTIFY
             ON 90 PERCENT DO NOTIFY
             ON 100 PERCENT DO SUSPEND;

-- Create resource monitor for loading
CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_LOADING_MONITOR
    WITH CREDIT_QUOTA = 15
    FREQUENCY = MONTHLY
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS ON 75 PERCENT DO NOTIFY
             ON 90 PERCENT DO NOTIFY
             ON 100 PERCENT DO SUSPEND;

-- Apply resource monitors to warehouses
ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = MERCURIOS_DEV_MONITOR;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = MERCURIOS_ANALYTICS_MONITOR;
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = MERCURIOS_LOADING_MONITOR;

-- 3. Apply clustering keys to large tables
-- This improves query performance and reduces compute costs
-- Identify large tables and apply clustering keys

-- Example for inventory table (adjust column names as needed)
ALTER TABLE MERCURIOS_DATA.STANDARD.INVENTORY CLUSTER BY (TENANT_ID, ARTICLE_ID);

-- Example for sales table (adjust column names as needed)
ALTER TABLE MERCURIOS_DATA.STANDARD.SALES CLUSTER BY (TENANT_ID, SALE_DATE);

-- 4. Set up automatic query optimization
-- Enable automatic clustering
ALTER ACCOUNT SET USE_AUTO_CLUSTERING = TRUE;

-- 5. Configure data retention policies
-- Set retention period for transient tables to 1 day
ALTER ACCOUNT SET DATA_RETENTION_TIME_IN_DAYS_FOR_TRANSIENT_TABLES = 1;

-- 6. Optimize warehouse sizes based on workload
-- Note: Adjust sizes based on actual usage patterns
-- Example: Scale down dev warehouse during non-business hours
CREATE OR REPLACE TASK scale_down_dev_warehouse
    WAREHOUSE = MERCURIOS_ADMIN_WH
    SCHEDULE = 'USING CRON 0 19 * * MON-FRI Europe/Berlin'
AS
    ALTER WAREHOUSE MERCURIOS_DEV_WH SET WAREHOUSE_SIZE = XSMALL;

CREATE OR REPLACE TASK scale_up_dev_warehouse
    WAREHOUSE = MERCURIOS_ADMIN_WH
    SCHEDULE = 'USING CRON 0 8 * * MON-FRI Europe/Berlin'
AS
    ALTER WAREHOUSE MERCURIOS_DEV_WH SET WAREHOUSE_SIZE = SMALL;

-- Enable the tasks
ALTER TASK scale_down_dev_warehouse RESUME;
ALTER TASK scale_up_dev_warehouse RESUME;

-- 7. Set up query result cache for 24 hours
ALTER ACCOUNT SET QUERY_RESULT_CACHE_RETENTION_TIME = 1440;

-- 8. Create usage monitoring views
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.WAREHOUSE_USAGE AS
SELECT
    WAREHOUSE_NAME,
    DATE_TRUNC('DAY', START_TIME) AS USAGE_DATE,
    COUNT(*) AS QUERY_COUNT,
    SUM(EXECUTION_TIME) / 1000 / 60 AS EXECUTION_MINUTES,
    SUM(CREDITS_USED) AS CREDITS_USED
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(MONTH, -1, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY 1, 2;

-- Create view for monitoring storage costs
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.STORAGE_USAGE AS
SELECT
    DATE_TRUNC('DAY', USAGE_DATE) AS USAGE_DATE,
    AVERAGE_STORAGE_BYTES / (1024 * 1024 * 1024) AS STORAGE_GB,
    AVERAGE_STAGE_BYTES / (1024 * 1024 * 1024) AS STAGE_GB
FROM SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE
WHERE USAGE_DATE >= DATEADD(MONTH, -1, CURRENT_DATE())
ORDER BY 1;

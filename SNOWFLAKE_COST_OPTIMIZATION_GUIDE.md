# Snowflake Cost Optimization Guide

This guide provides step-by-step instructions to optimize your Snowflake costs, focusing on reducing the usage of MERCURIOS_LOADING_WH which is consuming the majority of your credits.

## Step 1: Optimize Warehouse Settings

Log in to your Snowflake web console and execute the following SQL commands:

```sql
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
```

## Step 2: Set Up Cost Controls

```sql
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
```

## Step 3: Create Cost Monitoring Views

```sql
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

-- Grant access to the new views
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.expensive_queries TO ROLE MERCURIOS_FIVETRAN_USER;
```

## Step 4: Verify Your Changes

```sql
-- Verify warehouse settings
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
```

## Step 5: Optimize ETL Processes

To further reduce costs, consider these ETL optimization strategies:

1. **Batch your data loads** into smaller chunks to reduce memory usage
2. **Use incremental loading strategies** (which your Lambda connector supports)
3. **Schedule ETL jobs during off-peak hours** to avoid business-hour costs
4. **Implement proper clustering keys** for large tables to improve query performance

## Step 6: Monitor Your Costs

After implementing these changes, regularly monitor your costs using the new views:

```sql
-- Check warehouse costs
SELECT * FROM MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring;

-- Identify expensive queries
SELECT * FROM MERCURIOS_DATA.PUBLIC.expensive_queries;
```

## Additional Cost-Saving Recommendations

1. **Use Zero-Copy Cloning** for development environments instead of full copies
2. **Leverage Materialized Views** for frequently accessed data
3. **Implement data lifecycle management** to archive older data
4. **Review clustering keys** for optimal performance

By implementing these measures, you should see a significant reduction in your Snowflake costs, especially for the MERCURIOS_LOADING_WH which was consuming the majority of your credits.

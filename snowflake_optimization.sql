-- Snowflake Warehouse Optimization Script
-- This script helps optimize Snowflake warehouse usage to reduce costs

-- 1. Set auto-suspend to 60 seconds for all warehouses to minimize idle time
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET AUTO_SUSPEND = 60;

-- 2. Set appropriate warehouse sizes based on workload
-- For loading warehouse, use larger size during ETL windows, but scale down otherwise
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL';

-- For analytics warehouse, use medium size for better query performance
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET WAREHOUSE_SIZE = 'SMALL';

-- For development warehouse, use smallest size to save costs
ALTER WAREHOUSE MERCURIOS_DEV_WH SET WAREHOUSE_SIZE = 'XSMALL';

-- 3. Enable auto-scaling for the loading warehouse to handle varying loads efficiently
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET MIN_CLUSTER_COUNT = 1, MAX_CLUSTER_COUNT = 3, SCALING_POLICY = 'STANDARD';

-- 4. Create resource monitors to set spending limits and prevent unexpected costs
CREATE OR REPLACE RESOURCE MONITOR mercurios_monitor
WITH 
    CREDIT_QUOTA = 500, -- Adjust based on your monthly budget
    FREQUENCY = MONTHLY,
    START_TIMESTAMP = CURRENT_TIMESTAMP,
    END_TIMESTAMP = NULL
;

-- Apply resource monitor to warehouses
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = mercurios_monitor;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = mercurios_monitor;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = mercurios_monitor;
ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = mercurios_monitor;

-- 5. Create a scheduled task to automatically resize warehouses during off-hours
CREATE OR REPLACE TASK resize_warehouses_for_off_hours
    WAREHOUSE = MERCURIOS_DEV_WH
    SCHEDULE = 'USING CRON 0 20 * * * Europe/Berlin' -- 8PM Berlin time
AS
BEGIN
    ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL';
    ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET WAREHOUSE_SIZE = 'XSMALL';
END;

-- Create a task to resize warehouses for business hours
CREATE OR REPLACE TASK resize_warehouses_for_business_hours
    WAREHOUSE = MERCURIOS_DEV_WH
    SCHEDULE = 'USING CRON 0 8 * * * Europe/Berlin' -- 8AM Berlin time
AS
BEGIN
    ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'SMALL';
    ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET WAREHOUSE_SIZE = 'SMALL';
END;

-- Enable the tasks
ALTER TASK resize_warehouses_for_off_hours RESUME;
ALTER TASK resize_warehouses_for_business_hours RESUME;

-- 6. Create a query optimization policy to identify and optimize expensive queries
CREATE OR REPLACE PROCEDURE optimize_expensive_queries()
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
    // Query to find expensive queries
    var expensive_queries_sql = `
        SELECT QUERY_ID, QUERY_TEXT, EXECUTION_TIME, WAREHOUSE_NAME
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE EXECUTION_TIME > 60000 -- queries taking more than 1 minute
        AND START_TIME > DATEADD(day, -7, CURRENT_TIMESTAMP())
        ORDER BY EXECUTION_TIME DESC
        LIMIT 10
    `;
    
    // Execute the query
    var stmt = snowflake.createStatement({sqlText: expensive_queries_sql});
    var result = stmt.execute();
    
    // Process results
    var output = "Expensive queries identified:\n";
    while (result.next()) {
        output += "Query ID: " + result.getColumnValue(1) + "\n";
        output += "Execution Time (ms): " + result.getColumnValue(3) + "\n";
        output += "Warehouse: " + result.getColumnValue(4) + "\n";
        output += "Query Text: " + result.getColumnValue(2) + "\n\n";
    }
    
    return output;
$$;

-- 7. Create a view to monitor warehouse usage and costs
CREATE OR REPLACE VIEW warehouse_usage_monitoring AS
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

-- 8. Create a procedure to identify tables that could benefit from clustering
CREATE OR REPLACE PROCEDURE identify_clustering_candidates()
RETURNS TABLE()
LANGUAGE SQL
AS
$$
    SELECT 
        table_catalog,
        table_schema,
        table_name,
        row_count,
        bytes / (1024*1024*1024) AS size_gb
    FROM snowflake.account_usage.tables
    WHERE row_count > 10000000 -- tables with more than 10M rows
    AND bytes > 1073741824 -- tables larger than 1GB
    AND table_schema NOT LIKE '%INFORMATION_SCHEMA%'
    ORDER BY bytes DESC
    LIMIT 10;
$$;

-- 9. Create a procedure to optimize storage by removing redundant Time Travel data
CREATE OR REPLACE PROCEDURE optimize_storage()
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
    // Find tables with excessive Time Travel storage
    var time_travel_sql = `
        SELECT 
            TABLE_CATALOG,
            TABLE_SCHEMA,
            TABLE_NAME,
            ACTIVE_BYTES / (1024*1024*1024) AS ACTIVE_SIZE_GB,
            TIME_TRAVEL_BYTES / (1024*1024*1024) AS TIME_TRAVEL_SIZE_GB,
            (TIME_TRAVEL_BYTES / NULLIF(ACTIVE_BYTES, 0)) * 100 AS TIME_TRAVEL_RATIO
        FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
        WHERE TIME_TRAVEL_BYTES > 1073741824 -- more than 1GB
        AND (TIME_TRAVEL_BYTES / NULLIF(ACTIVE_BYTES, 0)) > 0.5 -- time travel > 50% of active
        ORDER BY TIME_TRAVEL_RATIO DESC
        LIMIT 10
    `;
    
    var stmt = snowflake.createStatement({sqlText: time_travel_sql});
    var result = stmt.execute();
    
    var output = "Tables with excessive Time Travel storage:\n";
    while (result.next()) {
        var catalog = result.getColumnValue(1);
        var schema = result.getColumnValue(2);
        var table = result.getColumnValue(3);
        var active_gb = result.getColumnValue(4);
        var tt_gb = result.getColumnValue(5);
        var ratio = result.getColumnValue(6);
        
        output += `${catalog}.${schema}.${table}: Active=${active_gb.toFixed(2)}GB, Time Travel=${tt_gb.toFixed(2)}GB (${ratio.toFixed(2)}%)\n`;
        
        // Generate ALTER TABLE statement to reduce retention period
        output += `-- Consider running: ALTER TABLE ${catalog}.${schema}.${table} SET DATA_RETENTION_TIME_IN_DAYS = 1;\n\n`;
    }
    
    return output;
$$;

-- 10. Create a dashboard query to monitor cost by query type
CREATE OR REPLACE VIEW query_cost_by_type AS
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

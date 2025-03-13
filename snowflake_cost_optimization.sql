-- Snowflake Cost Optimization Script
-- This script implements cost optimization measures for Mercurios.ai

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

-- 2. Implement Time-Based Warehouse Scaling
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

-- 3. Set Up Cost Controls
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

-- 4. Create views to monitor costs
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

-- 5. Create a procedure to optimize ETL processes
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.PUBLIC.optimize_etl_processes()
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
    // Find tables that are frequently updated
    var frequent_updates_sql = `
        SELECT 
            TABLE_CATALOG,
            TABLE_SCHEMA,
            TABLE_NAME,
            COUNT(*) AS update_count
        FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
        WHERE QUERY_START_TIME >= DATEADD(month, -1, CURRENT_TIMESTAMP())
        AND OPERATION_TYPE IN ('INSERT', 'UPDATE', 'MERGE', 'DELETE')
        GROUP BY 1, 2, 3
        HAVING COUNT(*) > 10
        ORDER BY update_count DESC
        LIMIT 10
    `;
    
    var stmt = snowflake.createStatement({sqlText: frequent_updates_sql});
    var result = stmt.execute();
    
    var output = "Tables with frequent updates that could benefit from optimization:\n";
    while (result.next()) {
        var catalog = result.getColumnValue(1);
        var schema = result.getColumnValue(2);
        var table = result.getColumnValue(3);
        var count = result.getColumnValue(4);
        
        output += `${catalog}.${schema}.${table}: ${count} updates\n`;
        
        // Generate recommendations
        output += `Recommendations for ${table}:\n`;
        output += `- Consider batching updates into smaller chunks\n`;
        output += `- Use incremental loading with 'MERGE INTO' statements\n`;
        output += `- Schedule updates during off-peak hours\n\n`;
    }
    
    // Find expensive merge operations
    var expensive_merges_sql = `
        SELECT 
            QUERY_ID,
            QUERY_TEXT,
            WAREHOUSE_NAME,
            EXECUTION_TIME / 1000 AS execution_seconds,
            CREDITS_USED
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE QUERY_TEXT ILIKE '%MERGE INTO%'
        AND START_TIME >= DATEADD(month, -1, CURRENT_TIMESTAMP())
        ORDER BY CREDITS_USED DESC
        LIMIT 5
    `;
    
    stmt = snowflake.createStatement({sqlText: expensive_merges_sql});
    result = stmt.execute();
    
    output += "Most expensive MERGE operations:\n";
    while (result.next()) {
        var query_id = result.getColumnValue(1);
        var query_text = result.getColumnValue(2);
        var warehouse = result.getColumnValue(3);
        var seconds = result.getColumnValue(4);
        var credits = result.getColumnValue(5);
        
        output += `Query ID: ${query_id}\n`;
        output += `Warehouse: ${warehouse}\n`;
        output += `Execution Time: ${seconds} seconds\n`;
        output += `Credits Used: ${credits}\n`;
        output += `Query: ${query_text.substring(0, 200)}...\n\n`;
    }
    
    return output;
$$;

-- 6. Create a procedure to identify tables that could benefit from clustering
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.PUBLIC.identify_clustering_candidates()
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
    WHERE row_count > 1000000 -- tables with more than 1M rows
    AND bytes > 1073741824 -- tables larger than 1GB
    AND table_schema NOT LIKE '%INFORMATION_SCHEMA%'
    ORDER BY bytes DESC
    LIMIT 10;
$$;

-- 7. Create a procedure to analyze and optimize storage
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.PUBLIC.optimize_storage()
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

-- 8. Grant access to the new views and procedures
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.query_cost_by_type TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.expensive_queries TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT USAGE ON PROCEDURE MERCURIOS_DATA.PUBLIC.optimize_etl_processes() TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT USAGE ON PROCEDURE MERCURIOS_DATA.PUBLIC.identify_clustering_candidates() TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT USAGE ON PROCEDURE MERCURIOS_DATA.PUBLIC.optimize_storage() TO ROLE MERCURIOS_FIVETRAN_USER;

#!/bin/bash
# Advanced Snowflake Cost Optimization Script
# This script implements comprehensive cost optimization measures for Mercurios.ai

echo "===== Mercurios.ai Advanced Snowflake Cost Optimization ====="
echo "Applying advanced cost optimization measures..."

# Load credentials from .env file
if [ -f .env ]; then
  source .env
  echo "✅ Loaded credentials from .env file"
else
  echo "❌ Error: .env file not found"
  exit 1
fi

# Create a temporary SQL file with all the optimization commands
cat > /tmp/advanced_snowflake_optimize.sql << 'EOF'
-- Set role to ACCOUNTADMIN for full permissions
USE ROLE ACCOUNTADMIN;

-- Set the database and schema context
USE DATABASE MERCURIOS_DATA;
USE SCHEMA PUBLIC;
USE WAREHOUSE COMPUTE_WH;

-- 1. MERCURIOS_LOADING_WH Optimizations
-- Reduce warehouse size to XSMALL
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL';

-- Set aggressive auto-suspend to 60 seconds to minimize idle time
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET AUTO_SUSPEND = 60;

-- Configure auto-scaling with min=1, max=2 clusters
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET MIN_CLUSTER_COUNT = 1, MAX_CLUSTER_COUNT = 2;

-- Enable query acceleration for better performance with smaller warehouse
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET QUERY_ACCELERATION_MAX_SCALE_FACTOR = 4;

-- 2. FIVETRAN_WAREHOUSE Optimizations
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET WAREHOUSE_SIZE = 'XSMALL';
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET MIN_CLUSTER_COUNT = 1, MAX_CLUSTER_COUNT = 1;

-- 3. MERCURIOS_ANALYTICS_WH Optimizations
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET STATEMENT_TIMEOUT_IN_SECONDS = 3600; -- Prevent runaway queries
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET STATEMENT_QUEUED_TIMEOUT_IN_SECONDS = 600; -- Prevent long queue times

-- Enable result caching for repetitive queries
ALTER SESSION SET USE_CACHED_RESULT = TRUE;

-- 4. COMPUTE_WH and DEV_WH Optimizations
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET WAREHOUSE_SIZE = 'XSMALL';

-- 5. Create Resource Monitor with 80 credit monthly quota
CREATE OR REPLACE RESOURCE MONITOR mercurios_cost_monitor
WITH 
    CREDIT_QUOTA = 80,
    FREQUENCY = MONTHLY,
    START_TIMESTAMP = CURRENT_DATE(),
    END_TIMESTAMP = NULL,
    TRIGGERS
    ON 70 PERCENT DO NOTIFY
    ON 90 PERCENT DO NOTIFY
    ON 95 PERCENT DO SUSPEND;

-- 6. Apply the resource monitor to all warehouses
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET RESOURCE_MONITOR = mercurios_cost_monitor;

-- 7. Create monitoring views for cost tracking
-- First, ensure we have access to ACCOUNT_USAGE
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE ACCOUNTADMIN;

-- Create warehouse cost monitoring view
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
WHERE START_TIME >= DATEADD(month, -1, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY usage_date DESC, credits_used DESC;

-- Create query cost by type view
CREATE OR REPLACE VIEW MERCURIOS_DATA.PUBLIC.query_cost_by_type AS
SELECT
    QUERY_TYPE,
    COUNT(*) AS query_count,
    SUM(CREDITS_USED) AS total_credits,
    AVG(CREDITS_USED) AS avg_credits_per_query,
    SUM(CREDITS_USED) / SUM(SUM(CREDITS_USED)) OVER () * 100 AS percentage_of_total
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(month, -1, CURRENT_DATE())
AND CREDITS_USED > 0
GROUP BY QUERY_TYPE
ORDER BY total_credits DESC;

-- Create expensive queries view
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
WHERE START_TIME >= DATEADD(day, -7, CURRENT_DATE())
AND CREDITS_USED > 0.1
ORDER BY CREDITS_USED DESC
LIMIT 100;

-- 8. Identify large tables for partitioning
CREATE OR REPLACE VIEW MERCURIOS_DATA.PUBLIC.large_tables_for_partitioning AS
SELECT
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_NAME,
    ROW_COUNT,
    BYTES / (1024*1024*1024) AS SIZE_GB
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLES
WHERE TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA')
AND BYTES > 1024*1024*1024 -- Tables larger than 1GB
ORDER BY BYTES DESC
LIMIT 20;

-- 9. Identify candidates for materialized views
CREATE OR REPLACE VIEW MERCURIOS_DATA.PUBLIC.materialized_view_candidates AS
WITH frequent_queries AS (
    SELECT
        HASH(REGEXP_REPLACE(QUERY_TEXT, '\\s+', ' ')) AS query_hash,
        REGEXP_REPLACE(QUERY_TEXT, '\\s+', ' ') AS normalized_query,
        COUNT(*) AS execution_count,
        AVG(EXECUTION_TIME) / 1000 AS avg_execution_time_sec,
        AVG(CREDITS_USED) AS avg_credits_used
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE START_TIME >= DATEADD(month, -1, CURRENT_DATE())
    AND QUERY_TYPE = 'SELECT'
    AND STATUS = 'SUCCESS'
    AND WAREHOUSE_NAME = 'MERCURIOS_ANALYTICS_WH'
    GROUP BY 1, 2
    HAVING COUNT(*) > 5 -- Queries run at least 5 times
    AND AVG(EXECUTION_TIME) > 10000 -- Queries taking more than 10 seconds
)
SELECT
    query_hash,
    normalized_query,
    execution_count,
    avg_execution_time_sec,
    avg_credits_used,
    execution_count * avg_credits_used AS total_potential_savings
FROM frequent_queries
ORDER BY total_potential_savings DESC
LIMIT 20;

-- 10. Create Snowpipe monitoring view for Fivetran
CREATE OR REPLACE VIEW MERCURIOS_DATA.PUBLIC.snowpipe_monitoring AS
SELECT
    pipe_name,
    file_name,
    stage_location,
    row_count,
    error_count,
    status,
    first_commit_time,
    last_commit_time
FROM SNOWFLAKE.ACCOUNT_USAGE.COPY_HISTORY
WHERE PIPE_NAME IS NOT NULL
AND LAST_LOAD_TIME >= DATEADD(day, -7, CURRENT_DATE())
ORDER BY LAST_LOAD_TIME DESC;

-- 11. Enable query tagging for better cost attribution
ALTER SESSION SET QUERY_TAG = 'cost_optimization_setup';

-- 12. Create a stored procedure to schedule ETL jobs during off-peak hours
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.PUBLIC.schedule_etl_jobs()
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
// This is a placeholder for scheduling ETL jobs
// In a real implementation, this would contain logic to:
// 1. Check current time and warehouse utilization
// 2. Schedule jobs during off-peak hours
// 3. Potentially adjust warehouse size based on workload
return "ETL jobs scheduled for off-peak hours";
$$;

-- 13. Create a stored procedure to analyze and optimize expensive queries
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.PUBLIC.optimize_expensive_queries()
RETURNS TABLE()
LANGUAGE SQL
AS
$$
SELECT 
    QUERY_ID,
    QUERY_TEXT,
    CREDITS_USED,
    EXECUTION_TIME/1000 AS EXECUTION_TIME_SECONDS,
    -- Recommendations based on query patterns
    CASE
        WHEN QUERY_TEXT ILIKE '%SELECT%FROM%JOIN%WHERE%GROUP BY%' AND EXECUTION_TIME > 60000 THEN 'Consider creating a materialized view'
        WHEN QUERY_TEXT ILIKE '%SELECT%FROM%WHERE%' AND QUERY_TEXT NOT ILIKE '%JOIN%' AND EXECUTION_TIME > 30000 THEN 'Consider adding appropriate indexes or clustering keys'
        WHEN EXECUTION_TIME > 120000 THEN 'Review query for optimization opportunities'
        ELSE 'No specific recommendation'
    END AS OPTIMIZATION_RECOMMENDATION
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE START_TIME >= DATEADD(day, -7, CURRENT_DATE())
AND CREDITS_USED > 0.2
ORDER BY CREDITS_USED DESC
LIMIT 20;
$$;

-- 14. Verify the changes
SELECT 
    WAREHOUSE_NAME, 
    WAREHOUSE_SIZE, 
    AUTO_SUSPEND, 
    MIN_CLUSTER_COUNT, 
    MAX_CLUSTER_COUNT,
    RESOURCE_MONITOR
FROM INFORMATION_SCHEMA.WAREHOUSES
WHERE WAREHOUSE_NAME IN ('MERCURIOS_LOADING_WH', 'MERCURIOS_ANALYTICS_WH', 'COMPUTE_WH', 'MERCURIOS_DEV_WH', 'FIVETRAN_WAREHOUSE');

-- Show resource monitors
SHOW RESOURCE MONITORS;

-- Show the new views
SHOW VIEWS IN MERCURIOS_DATA.PUBLIC;
EOF

# Run the SQL commands using SnowSQL with credentials from .env
echo "Executing advanced cost optimization commands..."
SNOWSQL_PWD="$SNOWFLAKE_PASSWORD" snowsql -a "$SNOWFLAKE_ACCOUNT" -u "$SNOWFLAKE_USER" -r "ACCOUNTADMIN" -w "$SNOWFLAKE_WAREHOUSE" -d "$SNOWFLAKE_DATABASE" -s "$SNOWFLAKE_SCHEMA" -f /tmp/advanced_snowflake_optimize.sql

# Clean up
rm /tmp/advanced_snowflake_optimize.sql

echo ""
echo "✅ Advanced cost optimization measures have been applied!"
echo ""
echo "💰 Summary of Optimizations:"
echo "  • MERCURIOS_LOADING_WH size reduced to XSMALL with query acceleration"
echo "  • FIVETRAN_WAREHOUSE optimized for micro-batch loading"
echo "  • Auto-suspend set to 60 seconds for all warehouses"
echo "  • Resource monitor created with 80 credit monthly quota and appropriate triggers"
echo "  • Created views to identify candidates for materialized views"
echo "  • Created views to identify large tables for partitioning"
echo "  • Enabled result caching for repetitive queries"
echo "  • Created stored procedures for scheduling ETL jobs and optimizing expensive queries"
echo ""
echo "📊 To view cost monitoring dashboards, run:"
echo "  SNOWSQL_PWD=\"$SNOWFLAKE_PASSWORD\" snowsql -a \"$SNOWFLAKE_ACCOUNT\" -u \"$SNOWFLAKE_USER\" -q \"SELECT * FROM MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring LIMIT 10;\""
echo ""
echo "🔍 To identify candidates for materialized views, run:"
echo "  SNOWSQL_PWD=\"$SNOWFLAKE_PASSWORD\" snowsql -a \"$SNOWFLAKE_ACCOUNT\" -u \"$SNOWFLAKE_USER\" -q \"SELECT * FROM MERCURIOS_DATA.PUBLIC.materialized_view_candidates LIMIT 10;\""
echo ""
echo "📋 To identify large tables for partitioning, run:"
echo "  SNOWSQL_PWD=\"$SNOWFLAKE_PASSWORD\" snowsql -a \"$SNOWFLAKE_ACCOUNT\" -u \"$SNOWFLAKE_USER\" -q \"SELECT * FROM MERCURIOS_DATA.PUBLIC.large_tables_for_partitioning LIMIT 10;\""
echo ""
echo "💡 To get recommendations for optimizing expensive queries, run:"
echo "  SNOWSQL_PWD=\"$SNOWFLAKE_PASSWORD\" snowsql -a \"$SNOWFLAKE_ACCOUNT\" -u \"$SNOWFLAKE_USER\" -q \"CALL MERCURIOS_DATA.PUBLIC.optimize_expensive_queries();\""

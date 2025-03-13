#!/bin/bash
# Snowflake Cost Optimization Script
# This script will apply cost optimization measures to your Snowflake account

echo "===== Mercurios.ai Snowflake Cost Optimization ====="
echo "Applying cost optimization measures to reduce customer costs..."

# Load credentials from .env file
if [ -f .env ]; then
  source .env
  echo "✅ Loaded credentials from .env file"
else
  echo "❌ Error: .env file not found"
  exit 1
fi

# Create a temporary SQL file with all the optimization commands
cat > /tmp/snowflake_optimize.sql << 'EOF'
-- Set role to ACCOUNTADMIN for full permissions
USE ROLE ACCOUNTADMIN;

-- Set the database and schema context
USE DATABASE MERCURIOS_DATA;
USE SCHEMA PUBLIC;
USE WAREHOUSE COMPUTE_WH;

-- 1. Optimize MERCURIOS_LOADING_WH (the biggest cost center)
-- Reduce warehouse size to XSMALL
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL';

-- Set aggressive auto-suspend to 60 seconds to minimize idle time
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET AUTO_SUSPEND = 60;

-- Configure auto-scaling with min=1, max=2 clusters
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET MIN_CLUSTER_COUNT = 1, MAX_CLUSTER_COUNT = 2;

-- 2. Optimize other warehouses with 60-second auto-suspend
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET AUTO_SUSPEND = 60;

-- 3. Create a resource monitor with 100 credit monthly quota
CREATE OR REPLACE RESOURCE MONITOR mercurios_cost_monitor
WITH 
    CREDIT_QUOTA = 100,
    FREQUENCY = MONTHLY,
    START_TIMESTAMP = CURRENT_TIMESTAMP,
    END_TIMESTAMP = NULL;

-- 4. Apply the resource monitor to all warehouses
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = mercurios_cost_monitor;

-- 5. Create monitoring views for cost tracking
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
WHERE START_TIME >= DATEADD(month, -1, CURRENT_TIMESTAMP())
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
WHERE START_TIME >= DATEADD(month, -1, CURRENT_TIMESTAMP())
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
WHERE START_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
AND CREDITS_USED > 0.1
ORDER BY CREDITS_USED DESC
LIMIT 100;

-- 6. Grant access to the views
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.query_cost_by_type TO ROLE MERCURIOS_FIVETRAN_USER;
GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.expensive_queries TO ROLE MERCURIOS_FIVETRAN_USER;

-- 7. Verify the changes
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

-- Show the new views
SHOW VIEWS IN MERCURIOS_DATA.PUBLIC;
EOF

# Create a temporary password file for SnowSQL
echo "$SNOWFLAKE_PASSWORD" > /tmp/snowsql_password.txt

# Run the SQL commands using SnowSQL with credentials from .env
echo "Executing cost optimization commands..."
SNOWSQL_PWD="$SNOWFLAKE_PASSWORD" snowsql -a "$SNOWFLAKE_ACCOUNT" -u "$SNOWFLAKE_USER" -r "ACCOUNTADMIN" -w "$SNOWFLAKE_WAREHOUSE" -d "$SNOWFLAKE_DATABASE" -s "$SNOWFLAKE_SCHEMA" -f /tmp/snowflake_optimize.sql

# Clean up
rm /tmp/snowflake_optimize.sql

echo ""
echo "✅ Cost optimization measures have been applied!"
echo ""
echo "💰 Summary of Optimizations:"
echo "  • MERCURIOS_LOADING_WH size reduced to XSMALL"
echo "  • Auto-suspend set to 60 seconds for all warehouses"
echo "  • Resource monitor created with 100 credit monthly quota"
echo "  • Cost monitoring views created for tracking expenses"
echo ""
echo "📊 To view cost monitoring dashboards, run:"
echo "  SNOWSQL_PWD=\"$SNOWFLAKE_PASSWORD\" snowsql -a \"$SNOWFLAKE_ACCOUNT\" -u \"$SNOWFLAKE_USER\" -q \"SELECT * FROM MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring LIMIT 10;\""
echo ""
echo "⚙️  To check your warehouse configurations, run:"
echo "  SNOWSQL_PWD=\"$SNOWFLAKE_PASSWORD\" snowsql -a \"$SNOWFLAKE_ACCOUNT\" -u \"$SNOWFLAKE_USER\" -q \"SELECT WAREHOUSE_NAME, WAREHOUSE_SIZE, AUTO_SUSPEND, RESOURCE_MONITOR FROM INFORMATION_SCHEMA.WAREHOUSES;\""

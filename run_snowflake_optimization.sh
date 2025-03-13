#!/bin/bash
# Script to apply Snowflake cost optimization measures using SnowSQL

echo "===== Mercurios.ai Snowflake Cost Optimization ====="
echo "This script will apply cost optimization measures to your Snowflake account."
echo ""

# Check if the SQL script exists
if [ ! -f "execute_cost_optimization.sql" ]; then
    echo "Error: execute_cost_optimization.sql not found."
    exit 1
fi

# Run the SnowSQL command with the optimization SQL file
echo "Executing cost optimization script with SnowSQL..."
snowsql -f execute_cost_optimization.sql

echo ""
echo "Cost optimization measures have been applied."
echo "To view the new cost monitoring dashboards, run:"
echo "snowsql -q \"SELECT * FROM MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring LIMIT 10;\""
echo ""
echo "To get information about your warehouse configuration, run:"
echo "snowsql -q \"SELECT WAREHOUSE_NAME, WAREHOUSE_SIZE, AUTO_SUSPEND, MIN_CLUSTER_COUNT, MAX_CLUSTER_COUNT, RESOURCE_MONITOR FROM INFORMATION_SCHEMA.WAREHOUSES WHERE WAREHOUSE_NAME IN ('MERCURIOS_LOADING_WH', 'MERCURIOS_ANALYTICS_WH', 'COMPUTE_WH', 'MERCURIOS_DEV_WH');\""

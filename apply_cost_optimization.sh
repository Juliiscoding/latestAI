#!/bin/bash
# Script to apply Snowflake cost optimization measures
# This will run the cost optimization SQL script using the persistent connection

echo "===== Mercurios.ai Snowflake Cost Optimization ====="
echo "This script will apply cost optimization measures to your Snowflake account."
echo "You will need to authenticate with Duo once to proceed."
echo ""

# Check if the SQL script exists
if [ ! -f "snowflake_cost_optimization.sql" ]; then
    echo "Error: snowflake_cost_optimization.sql not found."
    exit 1
fi

# Run the Python script with the optimization SQL file
python snowflake_persistent_connection.py --account "$SNOWFLAKE_ACCOUNT" --user "$SNOWFLAKE_USER" --warehouse "${SNOWFLAKE_WAREHOUSE:-MERCURIOS_DEV_WH}" --database "${SNOWFLAKE_DATABASE:-MERCURIOS_DATA}" --role "ACCOUNTADMIN" --file "snowflake_cost_optimization.sql" --verbose

echo ""
echo "Cost optimization measures have been applied."
echo "To view the new cost monitoring dashboards, run:"
echo "python snowflake_persistent_connection.py --query \"SELECT * FROM MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring LIMIT 10;\""
echo ""
echo "To get ETL optimization recommendations, run:"
echo "python snowflake_persistent_connection.py --query \"CALL MERCURIOS_DATA.PUBLIC.optimize_etl_processes();\""

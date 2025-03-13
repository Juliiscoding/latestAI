#!/usr/bin/env python
"""
Snowflake Cost Optimization Runner

This script connects to Snowflake and executes the cost optimization SQL commands.
"""

import os
import snowflake.connector
import getpass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Get connection parameters from environment variables or prompt
    account = os.getenv('SNOWFLAKE_ACCOUNT') or input("Snowflake Account: ")
    user = os.getenv('SNOWFLAKE_USER') or input("Snowflake Username: ")
    password = os.getenv('SNOWFLAKE_PASSWORD') or getpass.getpass("Snowflake Password: ")
    
    # Connect to Snowflake
    print(f"Connecting to Snowflake as {user}...")
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        role="ACCOUNTADMIN"  # Need admin role for warehouse modifications
    )
    
    try:
        cursor = conn.cursor()
        
        # Execute the optimization commands
        print("Optimizing MERCURIOS_LOADING_WH...")
        cursor.execute("ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL'")
        cursor.execute("ALTER WAREHOUSE MERCURIOS_LOADING_WH SET AUTO_SUSPEND = 60")
        cursor.execute("ALTER WAREHOUSE MERCURIOS_LOADING_WH SET MIN_CLUSTER_COUNT = 1, MAX_CLUSTER_COUNT = 2")
        
        # Optimize other warehouses
        print("Optimizing other warehouses...")
        cursor.execute("ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET AUTO_SUSPEND = 60")
        cursor.execute("ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60")
        cursor.execute("ALTER WAREHOUSE MERCURIOS_DEV_WH SET AUTO_SUSPEND = 60")
        
        # Set up cost controls
        print("Setting up cost controls...")
        cursor.execute("""
        CREATE OR REPLACE RESOURCE MONITOR mercurios_cost_monitor
        WITH 
            CREDIT_QUOTA = 100,
            FREQUENCY = MONTHLY,
            START_TIMESTAMP = CURRENT_TIMESTAMP,
            END_TIMESTAMP = NULL
        """)
        
        # Apply resource monitor to warehouses
        cursor.execute("ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = mercurios_cost_monitor")
        cursor.execute("ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = mercurios_cost_monitor")
        cursor.execute("ALTER WAREHOUSE COMPUTE_WH SET RESOURCE_MONITOR = mercurios_cost_monitor")
        cursor.execute("ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = mercurios_cost_monitor")
        
        # Create monitoring views
        print("Creating cost monitoring views...")
        cursor.execute("""
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
        ORDER BY usage_date DESC, credits_used DESC
        """)
        
        cursor.execute("""
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
        LIMIT 100
        """)
        
        # Grant access to the new views
        print("Granting access to monitoring views...")
        cursor.execute("GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring TO ROLE MERCURIOS_FIVETRAN_USER")
        cursor.execute("GRANT SELECT ON VIEW MERCURIOS_DATA.PUBLIC.expensive_queries TO ROLE MERCURIOS_FIVETRAN_USER")
        
        # Verify changes
        print("\nVerifying changes...")
        cursor.execute("""
        SELECT 
            WAREHOUSE_NAME, 
            WAREHOUSE_SIZE, 
            AUTO_SUSPEND, 
            MIN_CLUSTER_COUNT, 
            MAX_CLUSTER_COUNT,
            RESOURCE_MONITOR
        FROM INFORMATION_SCHEMA.WAREHOUSES
        WHERE WAREHOUSE_NAME IN ('MERCURIOS_LOADING_WH', 'MERCURIOS_ANALYTICS_WH', 'COMPUTE_WH', 'MERCURIOS_DEV_WH')
        """)
        
        results = cursor.fetchall()
        print("\nWarehouse Configuration:")
        print("------------------------")
        for row in results:
            print(f"Warehouse: {row[0]}")
            print(f"  Size: {row[1]}")
            print(f"  Auto-suspend: {row[2]} seconds")
            print(f"  Clusters: {row[3]}-{row[4]}")
            print(f"  Resource Monitor: {row[5] or 'None'}")
            print("")
        
        print("Cost optimization measures have been successfully applied!")
        print("\nYou can now monitor your costs using the following views:")
        print("  - MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring")
        print("  - MERCURIOS_DATA.PUBLIC.expensive_queries")
        
    finally:
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()

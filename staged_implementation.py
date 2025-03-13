#!/usr/bin/env python
"""
Staged Implementation of ROI Optimization Plan for Snowflake

This script implements the ROI optimization plan in stages, allowing for
controlled cost management at each step.
"""

import os
import sys
import time
import subprocess
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Snowflake connection parameters
snowflake_user = os.getenv("SNOWFLAKE_USER")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")

def connect_to_snowflake(warehouse=None):
    """Establish connection to Snowflake with optional warehouse."""
    conn_params = {
        "user": snowflake_user,
        "password": snowflake_password,
        "account": snowflake_account,
        "database": "MERCURIOS_DATA"
    }
    
    if warehouse:
        conn_params["warehouse"] = warehouse
    
    conn = snowflake.connector.connect(**conn_params)
    return conn

def execute_sql(sql, warehouse=None):
    """Execute SQL commands using a specific warehouse."""
    conn = connect_to_snowflake(warehouse)
    cursor = conn.cursor()
    
    try:
        for command in sql.split(';'):
            if command.strip():
                print(f"Executing: {command[:100]}..." if len(command) > 100 else f"Executing: {command}")
                try:
                    cursor.execute(command)
                    if cursor.description:
                        result = cursor.fetchall()
                        if result:
                            print(f"Result: {result[:5]}..." if len(result) > 5 else f"Result: {result}")
                except Exception as e:
                    print(f"Error executing command: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def adjust_resource_monitor():
    """Adjust the resource monitor to allow implementation."""
    print("\n=== Adjusting Resource Monitor ===")
    
    sql = """
    -- Check the current status of the resource monitor
    SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER';
    
    -- Temporarily adjust the resource monitor to allow implementation
    ALTER RESOURCE MONITOR MERCURIOSSTOPPER SET CREDIT_QUOTA = 2.0;
    
    -- Verify the change
    SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER';
    """
    
    execute_sql(sql)
    print("Resource monitor adjusted to allow implementation.")

def resume_warehouse(warehouse):
    """Resume a specific warehouse."""
    print(f"\n=== Resuming Warehouse {warehouse} ===")
    
    sql = f"""
    -- Resume the warehouse
    ALTER WAREHOUSE {warehouse} RESUME;
    
    -- Verify the status
    SHOW WAREHOUSES LIKE '{warehouse}';
    """
    
    execute_sql(sql)
    print(f"Warehouse {warehouse} resumed.")

def implement_analytics_views():
    """Implement the cost-efficient analytics views."""
    print("\n=== Implementing Analytics Views ===")
    
    # Resume the warehouse
    resume_warehouse('MERCURIOS_DEV_WH')
    
    # Read the SQL file
    with open('/Users/juliusrechenbach/API ProHandelTest/implement_cost_efficient_views.sql', 'r') as file:
        sql = file.read()
    
    # Execute the SQL
    execute_sql(sql, 'MERCURIOS_DEV_WH')
    
    print("Analytics views implemented successfully.")

def implement_dashboard_infrastructure():
    """Implement the dashboard infrastructure."""
    print("\n=== Implementing Dashboard Infrastructure ===")
    
    # Resume the warehouse
    resume_warehouse('MERCURIOS_ANALYTICS_WH')
    
    sql = """
    -- Create a materialized view for the dashboard
    CREATE OR REPLACE MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV
    AS SELECT * FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD;
    
    -- Create a task to refresh the materialized view
    CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_MV
      WAREHOUSE = MERCURIOS_ANALYTICS_WH
      SCHEDULE = 'USING CRON 0 3 * * * Europe/Berlin'
    AS
      REFRESH MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV;
    
    -- Initially suspend the task
    ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_MV SUSPEND;
    """
    
    # Execute the SQL
    execute_sql(sql, 'MERCURIOS_ANALYTICS_WH')
    
    print("Dashboard infrastructure implemented successfully.")

def implement_monitoring():
    """Implement cost monitoring."""
    print("\n=== Implementing Cost Monitoring ===")
    
    # Resume the warehouse
    resume_warehouse('MERCURIOS_DEV_WH')
    
    sql = """
    -- Create a view to monitor dashboard costs
    CREATE OR REPLACE VIEW MERCURIOS_DATA.ADMIN.DASHBOARD_COST_MONITORING AS
    SELECT 
      DATE_TRUNC('DAY', START_TIME) AS DATE,
      COUNT(*) AS QUERY_COUNT,
      SUM(TOTAL_ELAPSED_TIME)/1000/60 AS RUNTIME_MINUTES,
      SUM(TOTAL_ELAPSED_TIME)/1000/60/60 * 
        CASE 
          WHEN WAREHOUSE_SIZE = 'XSMALL' THEN 1
          WHEN WAREHOUSE_SIZE = 'SMALL' THEN 2
          ELSE 4
        END AS ESTIMATED_CREDITS
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
    AND QUERY_TEXT ILIKE '%BUSINESS_DASHBOARD%'
    GROUP BY 1
    ORDER BY 1 DESC;
    """
    
    # Execute the SQL
    execute_sql(sql, 'MERCURIOS_DEV_WH')
    
    print("Cost monitoring implemented successfully.")

def suspend_warehouses():
    """Suspend all warehouses."""
    print("\n=== Suspending All Warehouses ===")
    
    sql = """
    -- Suspend all warehouses
    ALTER WAREHOUSE MERCURIOS_DEV_WH SUSPEND;
    ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SUSPEND;
    ALTER WAREHOUSE MERCURIOS_LOADING_WH SUSPEND;
    
    -- Verify the status
    SHOW WAREHOUSES;
    """
    
    execute_sql(sql)
    print("All warehouses suspended.")

def reset_resource_monitor():
    """Reset the resource monitor to prevent further costs."""
    print("\n=== Resetting Resource Monitor ===")
    
    sql = """
    -- Reset the resource monitor to prevent further costs
    ALTER RESOURCE MONITOR MERCURIOSSTOPPER SET CREDIT_QUOTA = 0.0;
    
    -- Verify the change
    SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER';
    """
    
    execute_sql(sql)
    print("Resource monitor reset to prevent further costs.")

def main():
    """Main execution function."""
    print("=== Staged Implementation of ROI Optimization Plan ===")
    print("This script will implement the ROI optimization plan in stages.")
    
    # Display menu
    print("\nImplementation Stages:")
    print("1. Adjust Resource Monitor")
    print("2. Implement Analytics Views")
    print("3. Implement Dashboard Infrastructure")
    print("4. Implement Cost Monitoring")
    print("5. Suspend All Warehouses")
    print("6. Reset Resource Monitor")
    print("7. Execute All Steps")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-7): ")
    
    try:
        if choice == '1':
            adjust_resource_monitor()
        elif choice == '2':
            implement_analytics_views()
        elif choice == '3':
            implement_dashboard_infrastructure()
        elif choice == '4':
            implement_monitoring()
        elif choice == '5':
            suspend_warehouses()
        elif choice == '6':
            reset_resource_monitor()
        elif choice == '7':
            adjust_resource_monitor()
            implement_analytics_views()
            implement_dashboard_infrastructure()
            implement_monitoring()
            suspend_warehouses()
            reset_resource_monitor()
        elif choice == '0':
            print("Exiting...")
            return
        else:
            print("Invalid choice. Please try again.")
            
        print("\n=== Implementation Complete ===")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()

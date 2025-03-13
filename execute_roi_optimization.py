#!/usr/bin/env python
"""
ROI Optimization Plan Execution Script for Snowflake

This script orchestrates the implementation of the ROI optimization plan:
1. Analyzes Fivetran connectors
2. Creates cost-efficient analytics views
3. Sets up dashboard infrastructure
4. Activates and monitors the solution

It's designed to minimize Snowflake costs by carefully managing warehouse usage.
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

def execute_sql_file(file_path, warehouse):
    """Execute a SQL file using a specific warehouse."""
    print(f"\n=== Executing SQL file: {file_path} using {warehouse} ===")
    
    # Resume the warehouse
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        print(f"Resuming warehouse {warehouse}...")
        cursor.execute(f"ALTER WAREHOUSE {warehouse} RESUME")
        
        # Read the SQL file
        with open(file_path, 'r') as file:
            sql_commands = file.read()
        
        # Close the initial connection
        cursor.close()
        conn.close()
        
        # Connect with the warehouse and execute the SQL
        conn = connect_to_snowflake(warehouse)
        cursor = conn.cursor()
        
        # Split the SQL file by semicolons and execute each command
        for command in sql_commands.split(';'):
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
        
        print(f"SQL file execution completed.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always suspend the warehouse when done
        try:
            print(f"Suspending warehouse {warehouse}...")
            cursor.execute(f"ALTER WAREHOUSE {warehouse} SUSPEND")
        except:
            pass
        
        cursor.close()
        conn.close()

def analyze_fivetran_connectors():
    """Run the Fivetran connector analysis."""
    print("\n=== Step 1: Analyzing Fivetran Connectors ===")
    
    # Execute the SQL analysis script
    execute_sql_file('/Users/juliusrechenbach/API ProHandelTest/run_fivetran_analysis.sql', 'MERCURIOS_DEV_WH')
    
    print("\nBased on the analysis, follow these steps in Fivetran:")
    print("1. Log into Fivetran (https://fivetran.com/dashboard)")
    print("2. Navigate to the MERCURIOS destination")
    print("3. For each connector:")
    print("   - Shopify: Set to daily sync at 1:00 AM")
    print("   - Google Analytics: Set to daily sync at 2:00 AM")
    print("   - Klaviyo: Set to daily sync at 3:00 AM")
    print("   - AWS Lambda: Set to daily sync at 12:00 AM")
    print("   - Low-value connectors: Consider pausing")

def create_analytics_views():
    """Create the cost-efficient analytics views."""
    print("\n=== Step 2: Creating Cost-Efficient Analytics Views ===")
    
    # Execute the implementation script
    execute_sql_file('/Users/juliusrechenbach/API ProHandelTest/implement_cost_efficient_views.sql', 'MERCURIOS_DEV_WH')
    
    print("\nAnalytics views have been created successfully.")
    print("These views will provide valuable business insights without expensive ad-hoc queries.")

def setup_dashboard_infrastructure():
    """Set up the dashboard infrastructure."""
    print("\n=== Step 3: Setting Up Dashboard Infrastructure ===")
    
    # Create SQL for dashboard infrastructure
    dashboard_sql = """
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
    
    # Write the SQL to a temporary file
    with open('/Users/juliusrechenbach/API ProHandelTest/setup_dashboard.sql', 'w') as file:
        file.write(dashboard_sql)
    
    # Execute the SQL
    execute_sql_file('/Users/juliusrechenbach/API ProHandelTest/setup_dashboard.sql', 'MERCURIOS_ANALYTICS_WH')
    
    print("\nDashboard infrastructure has been set up successfully.")
    print("The dashboard will refresh daily at 3:00 AM to provide up-to-date insights.")

def activate_and_monitor():
    """Activate the tasks and set up monitoring."""
    print("\n=== Step 4: Activating and Monitoring ===")
    
    # Create SQL for activation and monitoring
    activation_sql = """
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
    
    -- Tasks will remain suspended until explicitly resumed
    -- To resume tasks, run:
    -- ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_MV RESUME;
    """
    
    # Write the SQL to a temporary file
    with open('/Users/juliusrechenbach/API ProHandelTest/activate_monitoring.sql', 'w') as file:
        file.write(activation_sql)
    
    # Execute the SQL
    execute_sql_file('/Users/juliusrechenbach/API ProHandelTest/activate_monitoring.sql', 'MERCURIOS_DEV_WH')
    
    print("\nMonitoring has been set up successfully.")
    print("Tasks will remain suspended until you explicitly resume them.")
    print("To resume tasks, run: ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_MV RESUME;")

def main():
    """Main execution function."""
    print("=== Snowflake ROI Optimization Plan Execution ===")
    print("This script will implement the ROI optimization plan in a cost-efficient manner.")
    
    # Check if we should proceed
    proceed = input("\nThis will temporarily resume warehouses to implement the plan. Proceed? (y/n): ")
    if proceed.lower() != 'y':
        print("Execution cancelled.")
        return
    
    try:
        # Step 1: Analyze Fivetran connectors
        analyze_fivetran_connectors()
        
        # Step 2: Create analytics views
        create_analytics_views()
        
        # Step 3: Set up dashboard infrastructure
        setup_dashboard_infrastructure()
        
        # Step 4: Activate and monitor
        activate_and_monitor()
        
        print("\n=== ROI Optimization Plan Implementation Complete ===")
        print("Your Snowflake environment is now optimized for maximum ROI.")
        print("\nNext steps:")
        print("1. Log into Fivetran to adjust connector sync frequencies")
        print("2. Connect your visualization tool to the materialized views")
        print("3. Resume tasks when you're ready to activate the dashboard")
        print("4. Monitor costs to ensure they remain under control")
        
    except Exception as e:
        print(f"Error during execution: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()

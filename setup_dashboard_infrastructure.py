#!/usr/bin/env python
"""
Dashboard Infrastructure Setup for Snowflake ROI Optimization

This script sets up materialized views and refresh tasks for dashboards
based on the successfully created analytics views.
"""

import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Snowflake connection parameters
snowflake_user = os.getenv("SNOWFLAKE_USER", "JULIUSRECHENBACH")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT", "VRXDFZX-ZZ95717")

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

def execute_sql(cursor, sql, description=None):
    """Execute SQL command and print result."""
    if description:
        print(f"\n=== {description} ===")
    
    print(f"Executing: \n{sql[:100]}...")
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        print(f"Success! Result: {result[:2] if result else 'No result returned'}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def setup_dashboard_infrastructure():
    """Set up dashboard infrastructure with materialized views and refresh tasks."""
    print("\n=== Setting Up Dashboard Infrastructure ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("COMPUTE_WH")
    cursor = conn.cursor()
    
    try:
        # 1. Create materialized view for Daily Sales Summary
        daily_sales_mv_sql = """
        CREATE OR REPLACE MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY_MV
        AS SELECT * FROM MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY;
        """
        execute_sql(cursor, daily_sales_mv_sql, "Daily Sales Summary Materialized View")
        
        # 2. Create materialized view for Customer Insights (if the view exists)
        customer_insights_mv_sql = """
        CREATE OR REPLACE MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.CUSTOMER_INSIGHTS_MV
        AS SELECT * FROM MERCURIOS_DATA.ANALYTICS.CUSTOMER_INSIGHTS;
        """
        execute_sql(cursor, customer_insights_mv_sql, "Customer Insights Materialized View")
        
        # 3. Create materialized view for Product Performance (if the view exists)
        product_performance_mv_sql = """
        CREATE OR REPLACE MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.PRODUCT_PERFORMANCE_MV
        AS SELECT * FROM MERCURIOS_DATA.ANALYTICS.PRODUCT_PERFORMANCE;
        """
        execute_sql(cursor, product_performance_mv_sql, "Product Performance Materialized View")
        
        # 4. Create a task to refresh the materialized views daily
        # First, ensure the task warehouse exists and is properly configured
        task_warehouse_sql = """
        CREATE WAREHOUSE IF NOT EXISTS MERCURIOS_TASK_WH
        WITH WAREHOUSE_SIZE = 'XSMALL'
        AUTO_SUSPEND = 60
        AUTO_RESUME = TRUE;
        """
        execute_sql(cursor, task_warehouse_sql, "Task Warehouse Setup")
        
        # Create a task to refresh the Daily Sales Summary materialized view
        refresh_daily_sales_task_sql = """
        CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.REFRESH_DAILY_SALES_MV
        WAREHOUSE = MERCURIOS_TASK_WH
        SCHEDULE = 'USING CRON 0 1 * * * America/Los_Angeles'
        AS
        CALL SYSTEM$REFRESH_MATERIALIZED_VIEW('MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY_MV');
        """
        execute_sql(cursor, refresh_daily_sales_task_sql, "Refresh Daily Sales Task")
        
        # Create a task to refresh the Customer Insights materialized view
        refresh_customer_insights_task_sql = """
        CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.REFRESH_CUSTOMER_INSIGHTS_MV
        WAREHOUSE = MERCURIOS_TASK_WH
        SCHEDULE = 'USING CRON 0 2 * * * America/Los_Angeles'
        AS
        CALL SYSTEM$REFRESH_MATERIALIZED_VIEW('MERCURIOS_DATA.ANALYTICS.CUSTOMER_INSIGHTS_MV');
        """
        execute_sql(cursor, refresh_customer_insights_task_sql, "Refresh Customer Insights Task")
        
        # Create a task to refresh the Product Performance materialized view
        refresh_product_performance_task_sql = """
        CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.REFRESH_PRODUCT_PERFORMANCE_MV
        WAREHOUSE = MERCURIOS_TASK_WH
        SCHEDULE = 'USING CRON 0 3 * * * America/Los_Angeles'
        AS
        CALL SYSTEM$REFRESH_MATERIALIZED_VIEW('MERCURIOS_DATA.ANALYTICS.PRODUCT_PERFORMANCE_MV');
        """
        execute_sql(cursor, refresh_product_performance_task_sql, "Refresh Product Performance Task")
        
        # 5. Resume the tasks if needed
        resume_tasks_sql = """
        ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_DAILY_SALES_MV RESUME;
        ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_CUSTOMER_INSIGHTS_MV RESUME;
        ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_PRODUCT_PERFORMANCE_MV RESUME;
        """
        execute_sql(cursor, resume_tasks_sql, "Resume Tasks")
        
        print("\nDashboard infrastructure setup complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_dashboard_infrastructure()

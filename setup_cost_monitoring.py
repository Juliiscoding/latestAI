#!/usr/bin/env python
"""
Cost Monitoring Setup for Snowflake ROI Optimization

This script sets up cost monitoring views and alerts to help optimize
Snowflake costs and ensure efficient resource usage.
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

def setup_cost_monitoring():
    """Set up cost monitoring views and alerts."""
    print("\n=== Setting Up Cost Monitoring ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("COMPUTE_WH")
    cursor = conn.cursor()
    
    try:
        # 1. Create warehouse usage monitoring view
        warehouse_usage_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ADMIN.WAREHOUSE_USAGE_MONITORING AS
        SELECT 
            WAREHOUSE_NAME,
            DATE_TRUNC('DAY', START_TIME) AS DATE,
            COUNT(*) AS QUERY_COUNT,
            SUM(EXECUTION_TIME)/1000/60 AS RUNTIME_MINUTES,
            SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_SERVICES_CREDITS,
            SUM(CREDITS_USED) AS COMPUTE_CREDITS,
            SUM(CREDITS_USED_CLOUD_SERVICES) + SUM(CREDITS_USED) AS TOTAL_CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
        GROUP BY 1, 2
        ORDER BY 1, 2 DESC;
        """
        execute_sql(cursor, warehouse_usage_sql, "Warehouse Usage Monitoring View")
        
        # 2. Create query performance monitoring view
        query_performance_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ADMIN.QUERY_PERFORMANCE_MONITORING AS
        SELECT 
            QUERY_ID,
            QUERY_TEXT,
            USER_NAME,
            WAREHOUSE_NAME,
            DATABASE_NAME,
            SCHEMA_NAME,
            EXECUTION_STATUS,
            ERROR_CODE,
            ERROR_MESSAGE,
            START_TIME,
            END_TIME,
            TOTAL_ELAPSED_TIME/1000 AS EXECUTION_TIME_SECONDS,
            BYTES_SCANNED/1024/1024 AS MB_SCANNED,
            ROWS_PRODUCED,
            COMPILATION_TIME/1000 AS COMPILATION_TIME_SECONDS,
            EXECUTION_TIME/1000 AS EXECUTION_TIME_SECONDS,
            QUEUED_PROVISIONING_TIME/1000 AS QUEUED_PROVISIONING_TIME_SECONDS,
            QUEUED_REPAIR_TIME/1000 AS QUEUED_REPAIR_TIME_SECONDS,
            QUEUED_OVERLOAD_TIME/1000 AS QUEUED_OVERLOAD_TIME_SECONDS
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE START_TIME >= DATEADD(DAY, -7, CURRENT_DATE())
        ORDER BY START_TIME DESC;
        """
        execute_sql(cursor, query_performance_sql, "Query Performance Monitoring View")
        
        # 3. Create daily cost summary view
        daily_cost_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ADMIN.DAILY_COST_SUMMARY AS
        SELECT 
            DATE_TRUNC('DAY', START_TIME) AS DATE,
            SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_SERVICES_CREDITS,
            SUM(CREDITS_USED) AS COMPUTE_CREDITS,
            SUM(CREDITS_USED_CLOUD_SERVICES) + SUM(CREDITS_USED) AS TOTAL_CREDITS
        FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
        GROUP BY 1
        ORDER BY 1 DESC;
        """
        execute_sql(cursor, daily_cost_sql, "Daily Cost Summary View")
        
        # 4. Create storage usage view
        storage_usage_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ADMIN.STORAGE_USAGE_MONITORING AS
        SELECT 
            DATE_TRUNC('DAY', USAGE_DATE) AS DATE,
            DATABASE_NAME,
            AVERAGE_STORAGE_BYTES/1024/1024/1024 AS AVERAGE_STORAGE_GB,
            AVERAGE_STAGE_BYTES/1024/1024/1024 AS AVERAGE_STAGE_GB,
            AVERAGE_FAILSAFE_BYTES/1024/1024/1024 AS AVERAGE_FAILSAFE_GB
        FROM SNOWFLAKE.ACCOUNT_USAGE.DATABASE_STORAGE_USAGE_HISTORY
        WHERE USAGE_DATE >= DATEADD(DAY, -30, CURRENT_DATE())
        ORDER BY 1 DESC, 2;
        """
        execute_sql(cursor, storage_usage_sql, "Storage Usage Monitoring View")
        
        # 5. Create materialized view for daily cost summary
        daily_cost_mv_sql = """
        CREATE OR REPLACE TABLE MERCURIOS_DATA.ADMIN.DAILY_COST_SUMMARY_TABLE AS
        SELECT * FROM MERCURIOS_DATA.ADMIN.DAILY_COST_SUMMARY;
        """
        execute_sql(cursor, daily_cost_mv_sql, "Daily Cost Summary Table")
        
        # 6. Create a task to refresh the daily cost summary table
        refresh_cost_task_sql = """
        CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.REFRESH_COST_SUMMARY
        WAREHOUSE = MERCURIOS_TASK_WH
        SCHEDULE = 'USING CRON 0 4 * * * America/Los_Angeles'
        AS
        TRUNCATE TABLE MERCURIOS_DATA.ADMIN.DAILY_COST_SUMMARY_TABLE;
        INSERT INTO MERCURIOS_DATA.ADMIN.DAILY_COST_SUMMARY_TABLE
        SELECT * FROM MERCURIOS_DATA.ADMIN.DAILY_COST_SUMMARY;
        """
        execute_sql(cursor, refresh_cost_task_sql, "Refresh Cost Summary Task")
        
        # 7. Create a resource monitor for each warehouse
        create_resource_monitors_sql = """
        -- Create resource monitor for MERCURIOS_ANALYTICS_WH
        CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_ANALYTICS_MONITOR
        WITH CREDIT_QUOTA = 10
        FREQUENCY = DAILY
        START_TIMESTAMP = CURRENT_TIMESTAMP
        TRIGGERS
          ON 75 PERCENT DO NOTIFY
          ON 90 PERCENT DO NOTIFY
          ON 100 PERCENT DO SUSPEND;
          
        -- Create resource monitor for MERCURIOS_DEV_WH
        CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_DEV_MONITOR
        WITH CREDIT_QUOTA = 5
        FREQUENCY = DAILY
        START_TIMESTAMP = CURRENT_TIMESTAMP
        TRIGGERS
          ON 75 PERCENT DO NOTIFY
          ON 90 PERCENT DO NOTIFY
          ON 100 PERCENT DO SUSPEND;
          
        -- Create resource monitor for MERCURIOS_LOADING_WH
        CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_LOADING_MONITOR
        WITH CREDIT_QUOTA = 8
        FREQUENCY = DAILY
        START_TIMESTAMP = CURRENT_TIMESTAMP
        TRIGGERS
          ON 75 PERCENT DO NOTIFY
          ON 90 PERCENT DO NOTIFY
          ON 100 PERCENT DO SUSPEND;
          
        -- Create resource monitor for MERCURIOS_TASK_WH
        CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_TASK_MONITOR
        WITH CREDIT_QUOTA = 2
        FREQUENCY = DAILY
        START_TIMESTAMP = CURRENT_TIMESTAMP
        TRIGGERS
          ON 75 PERCENT DO NOTIFY
          ON 90 PERCENT DO NOTIFY
          ON 100 PERCENT DO SUSPEND;
        """
        execute_sql(cursor, create_resource_monitors_sql, "Create Resource Monitors")
        
        # 8. Apply resource monitors to warehouses
        apply_monitors_sql = """
        -- Apply resource monitor to MERCURIOS_ANALYTICS_WH
        ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = MERCURIOS_ANALYTICS_MONITOR;
        
        -- Apply resource monitor to MERCURIOS_DEV_WH
        ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = MERCURIOS_DEV_MONITOR;
        
        -- Apply resource monitor to MERCURIOS_LOADING_WH
        ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = MERCURIOS_LOADING_MONITOR;
        
        -- Apply resource monitor to MERCURIOS_TASK_WH
        ALTER WAREHOUSE MERCURIOS_TASK_WH SET RESOURCE_MONITOR = MERCURIOS_TASK_MONITOR;
        """
        execute_sql(cursor, apply_monitors_sql, "Apply Resource Monitors")
        
        # 9. Resume the cost summary refresh task
        resume_cost_task_sql = """
        ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_COST_SUMMARY RESUME;
        """
        execute_sql(cursor, resume_cost_task_sql, "Resume Cost Summary Task")
        
        print("\nCost monitoring setup complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_cost_monitoring()

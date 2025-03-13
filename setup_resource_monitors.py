#!/usr/bin/env python
"""
Setup Resource Monitors for Snowflake ROI Optimization

This script creates and applies resource monitors to each warehouse
to control costs and prevent unexpected overages.
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
    
    print(f"Executing: {sql}")
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        print(f"Success! Result: {result[:2] if result else 'No result returned'}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def setup_resource_monitors():
    """Set up resource monitors for each warehouse."""
    print("\n=== Setting Up Resource Monitors ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("MERCURIOS_DEV_WH")
    cursor = conn.cursor()
    
    try:
        # Create resource monitor for MERCURIOS_ANALYTICS_WH
        analytics_monitor_sql = """
        CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_ANALYTICS_MONITOR
        WITH CREDIT_QUOTA = 10
        FREQUENCY = DAILY
        START_TIMESTAMP = CURRENT_TIMESTAMP
        TRIGGERS
          ON 75 PERCENT DO NOTIFY
          ON 90 PERCENT DO NOTIFY
          ON 100 PERCENT DO SUSPEND;
        """
        execute_sql(cursor, analytics_monitor_sql, "Create ANALYTICS Monitor")
        
        # Create resource monitor for MERCURIOS_DEV_WH
        dev_monitor_sql = """
        CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_DEV_MONITOR
        WITH CREDIT_QUOTA = 5
        FREQUENCY = DAILY
        START_TIMESTAMP = CURRENT_TIMESTAMP
        TRIGGERS
          ON 75 PERCENT DO NOTIFY
          ON 90 PERCENT DO NOTIFY
          ON 100 PERCENT DO SUSPEND;
        """
        execute_sql(cursor, dev_monitor_sql, "Create DEV Monitor")
        
        # Create resource monitor for MERCURIOS_LOADING_WH
        loading_monitor_sql = """
        CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_LOADING_MONITOR
        WITH CREDIT_QUOTA = 8
        FREQUENCY = DAILY
        START_TIMESTAMP = CURRENT_TIMESTAMP
        TRIGGERS
          ON 75 PERCENT DO NOTIFY
          ON 90 PERCENT DO NOTIFY
          ON 100 PERCENT DO SUSPEND;
        """
        execute_sql(cursor, loading_monitor_sql, "Create LOADING Monitor")
        
        # Create resource monitor for MERCURIOS_TASK_WH
        task_monitor_sql = """
        CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_TASK_MONITOR
        WITH CREDIT_QUOTA = 2
        FREQUENCY = DAILY
        START_TIMESTAMP = CURRENT_TIMESTAMP
        TRIGGERS
          ON 75 PERCENT DO NOTIFY
          ON 90 PERCENT DO NOTIFY
          ON 100 PERCENT DO SUSPEND;
        """
        execute_sql(cursor, task_monitor_sql, "Create TASK Monitor")
        
        # Apply resource monitor to MERCURIOS_ANALYTICS_WH
        apply_analytics_sql = """
        ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH 
        SET RESOURCE_MONITOR = MERCURIOS_ANALYTICS_MONITOR;
        """
        execute_sql(cursor, apply_analytics_sql, "Apply ANALYTICS Monitor")
        
        # Apply resource monitor to MERCURIOS_DEV_WH
        apply_dev_sql = """
        ALTER WAREHOUSE MERCURIOS_DEV_WH 
        SET RESOURCE_MONITOR = MERCURIOS_DEV_MONITOR;
        """
        execute_sql(cursor, apply_dev_sql, "Apply DEV Monitor")
        
        # Apply resource monitor to MERCURIOS_LOADING_WH
        apply_loading_sql = """
        ALTER WAREHOUSE MERCURIOS_LOADING_WH 
        SET RESOURCE_MONITOR = MERCURIOS_LOADING_MONITOR;
        """
        execute_sql(cursor, apply_loading_sql, "Apply LOADING Monitor")
        
        # Apply resource monitor to MERCURIOS_TASK_WH
        apply_task_sql = """
        ALTER WAREHOUSE MERCURIOS_TASK_WH 
        SET RESOURCE_MONITOR = MERCURIOS_TASK_MONITOR;
        """
        execute_sql(cursor, apply_task_sql, "Apply TASK Monitor")
        
        # Set auto-suspension for all warehouses
        auto_suspend_analytics_sql = """
        ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH 
        SET AUTO_SUSPEND = 60;
        """
        execute_sql(cursor, auto_suspend_analytics_sql, "Set ANALYTICS Auto-Suspend")
        
        auto_suspend_dev_sql = """
        ALTER WAREHOUSE MERCURIOS_DEV_WH 
        SET AUTO_SUSPEND = 60;
        """
        execute_sql(cursor, auto_suspend_dev_sql, "Set DEV Auto-Suspend")
        
        auto_suspend_loading_sql = """
        ALTER WAREHOUSE MERCURIOS_LOADING_WH 
        SET AUTO_SUSPEND = 60;
        """
        execute_sql(cursor, auto_suspend_loading_sql, "Set LOADING Auto-Suspend")
        
        auto_suspend_task_sql = """
        ALTER WAREHOUSE MERCURIOS_TASK_WH 
        SET AUTO_SUSPEND = 60;
        """
        execute_sql(cursor, auto_suspend_task_sql, "Set TASK Auto-Suspend")
        
        print("\nResource monitors setup complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_resource_monitors()

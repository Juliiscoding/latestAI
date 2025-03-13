#!/usr/bin/env python
"""
Targeted ROI Optimization Implementation for Snowflake

This script implements a targeted approach to ROI optimization based on
the actual state of your Snowflake environment.
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

def check_environment():
    """Check the current state of the Snowflake environment."""
    print("\n=== Checking Snowflake Environment ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        # Check warehouses
        print("\nChecking warehouses...")
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        print(f"Warehouses: {warehouses}")
        
        # Check databases
        print("\nChecking databases...")
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print(f"Databases: {databases}")
        
        # Check schemas in MERCURIOS_DATA
        print("\nChecking schemas in MERCURIOS_DATA...")
        cursor.execute("SHOW SCHEMAS IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        print(f"Schemas: {schemas}")
        
        # Check tables in RAW schema
        print("\nChecking tables in RAW schema...")
        cursor.execute("SHOW TABLES IN SCHEMA MERCURIOS_DATA.RAW")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        
        # Check user privileges
        print("\nChecking user privileges...")
        cursor.execute("SHOW GRANTS TO USER CURRENT_USER()")
        grants = cursor.fetchall()
        print(f"Grants: {grants}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def create_schemas():
    """Create necessary schemas if they don't exist."""
    print("\n=== Creating Necessary Schemas ===")
    
    sql = """
    -- Create ANALYTICS schema if it doesn't exist
    CREATE SCHEMA IF NOT EXISTS MERCURIOS_DATA.ANALYTICS;
    
    -- Create ADMIN schema if it doesn't exist
    CREATE SCHEMA IF NOT EXISTS MERCURIOS_DATA.ADMIN;
    """
    
    execute_sql(sql, "MERCURIOS_DEV_WH")
    print("Schemas created successfully.")

def create_sample_tables():
    """Create sample tables for demonstration purposes."""
    print("\n=== Creating Sample Tables ===")
    
    sql = """
    -- Create sample CUSTOMERS table if it doesn't exist
    CREATE TABLE IF NOT EXISTS MERCURIOS_DATA.RAW.CUSTOMERS (
        customer_id VARCHAR(50),
        name VARCHAR(100),
        email VARCHAR(100),
        signup_date DATE,
        last_order_date DATE,
        total_orders INT,
        total_spend FLOAT
    );
    
    -- Create sample ARTICLES table if it doesn't exist
    CREATE TABLE IF NOT EXISTS MERCURIOS_DATA.RAW.ARTICLES (
        article_id VARCHAR(50),
        name VARCHAR(100),
        category VARCHAR(50),
        price FLOAT,
        cost FLOAT,
        inventory_count INT
    );
    
    -- Create sample ORDERS table if it doesn't exist
    CREATE TABLE IF NOT EXISTS MERCURIOS_DATA.RAW.ORDERS (
        order_id VARCHAR(50),
        customer_id VARCHAR(50),
        order_date DATE,
        total_amount FLOAT,
        status VARCHAR(20)
    );
    
    -- Create sample ORDER_ITEMS table if it doesn't exist
    CREATE TABLE IF NOT EXISTS MERCURIOS_DATA.RAW.ORDER_ITEMS (
        order_id VARCHAR(50),
        article_id VARCHAR(50),
        quantity INT,
        price FLOAT
    );
    """
    
    execute_sql(sql, "MERCURIOS_DEV_WH")
    print("Sample tables created successfully.")

def create_analytics_views():
    """Create analytics views based on available tables."""
    print("\n=== Creating Analytics Views ===")
    
    sql = """
    -- 1. Daily Sales Summary View
    CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY AS
    SELECT
        DATE_TRUNC('DAY', o.order_date) AS day,
        COUNT(DISTINCT o.order_id) AS order_count,
        COUNT(DISTINCT o.customer_id) AS customer_count,
        SUM(o.total_amount) AS total_sales
    FROM MERCURIOS_DATA.RAW.ORDERS o
    GROUP BY 1
    ORDER BY 1 DESC;
    
    -- 2. Customer Insights View
    CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.CUSTOMER_INSIGHTS AS
    SELECT
        c.customer_id,
        c.name,
        c.email,
        c.signup_date,
        c.last_order_date,
        c.total_orders,
        c.total_spend,
        c.total_spend / NULLIF(c.total_orders, 0) AS avg_order_value,
        DATEDIFF('day', c.last_order_date, CURRENT_DATE()) AS days_since_last_order
    FROM MERCURIOS_DATA.RAW.CUSTOMERS c;
    
    -- 3. Product Performance View
    CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.PRODUCT_PERFORMANCE AS
    SELECT
        a.article_id,
        a.name,
        a.category,
        a.price,
        a.cost,
        a.inventory_count,
        COUNT(DISTINCT oi.order_id) AS order_count,
        SUM(oi.quantity) AS total_quantity_sold,
        SUM(oi.quantity * oi.price) AS total_revenue,
        SUM(oi.quantity * (oi.price - a.cost)) AS total_profit,
        (SUM(oi.quantity * (oi.price - a.cost)) / NULLIF(SUM(oi.quantity * oi.price), 0)) * 100 AS profit_margin
    FROM MERCURIOS_DATA.RAW.ARTICLES a
    LEFT JOIN MERCURIOS_DATA.RAW.ORDER_ITEMS oi ON a.article_id = oi.article_id
    GROUP BY 1, 2, 3, 4, 5, 6;
    
    -- 4. Consolidated Business Dashboard View
    CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD AS
    SELECT
        'Sales' AS metric_category,
        'Today''s Sales' AS metric_name,
        (SELECT COALESCE(SUM(total_amount), 0) FROM MERCURIOS_DATA.RAW.ORDERS WHERE order_date = CURRENT_DATE()) AS metric_value
    UNION ALL
    SELECT
        'Sales' AS metric_category,
        'Yesterday''s Sales' AS metric_name,
        (SELECT COALESCE(SUM(total_amount), 0) FROM MERCURIOS_DATA.RAW.ORDERS WHERE order_date = DATEADD('day', -1, CURRENT_DATE())) AS metric_value
    UNION ALL
    SELECT
        'Sales' AS metric_category,
        'This Month''s Sales' AS metric_name,
        (SELECT COALESCE(SUM(total_amount), 0) FROM MERCURIOS_DATA.RAW.ORDERS WHERE DATE_TRUNC('month', order_date) = DATE_TRUNC('month', CURRENT_DATE())) AS metric_value
    UNION ALL
    SELECT
        'Customers' AS metric_category,
        'Total Customers' AS metric_name,
        (SELECT COUNT(*) FROM MERCURIOS_DATA.RAW.CUSTOMERS) AS metric_value
    UNION ALL
    SELECT
        'Inventory' AS metric_category,
        'Low Stock Items' AS metric_name,
        (SELECT COUNT(*) FROM MERCURIOS_DATA.RAW.ARTICLES WHERE inventory_count < 10) AS metric_value;
    """
    
    execute_sql(sql, "MERCURIOS_DEV_WH")
    print("Analytics views created successfully.")

def setup_dashboard_infrastructure():
    """Set up dashboard infrastructure."""
    print("\n=== Setting Up Dashboard Infrastructure ===")
    
    sql = """
    -- Create a materialized view for the dashboard
    CREATE OR REPLACE MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV
    AS SELECT * FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD;
    """
    
    execute_sql(sql, "MERCURIOS_ANALYTICS_WH")
    print("Dashboard infrastructure set up successfully.")

def setup_monitoring():
    """Set up cost monitoring."""
    print("\n=== Setting Up Cost Monitoring ===")
    
    sql = """
    -- Create a view to monitor warehouse usage
    CREATE OR REPLACE VIEW MERCURIOS_DATA.ADMIN.WAREHOUSE_USAGE_MONITORING AS
    SELECT 
        WAREHOUSE_NAME,
        DATE_TRUNC('DAY', START_TIME) AS DATE,
        COUNT(*) AS QUERY_COUNT,
        SUM(EXECUTION_TIME)/1000/60 AS RUNTIME_MINUTES
    FROM TABLE(MERCURIOS_DATA.INFORMATION_SCHEMA.QUERY_HISTORY())
    WHERE START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
    GROUP BY 1, 2
    ORDER BY 1, 2 DESC;
    """
    
    execute_sql(sql, "MERCURIOS_DEV_WH")
    print("Cost monitoring set up successfully.")

def suspend_warehouses():
    """Suspend all warehouses."""
    print("\n=== Suspending All Warehouses ===")
    
    sql = """
    -- Suspend all warehouses
    ALTER WAREHOUSE IF EXISTS MERCURIOS_DEV_WH SUSPEND;
    ALTER WAREHOUSE IF EXISTS MERCURIOS_ANALYTICS_WH SUSPEND;
    ALTER WAREHOUSE IF EXISTS MERCURIOS_LOADING_WH SUSPEND;
    
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
    print("=== Targeted ROI Optimization Implementation ===")
    print("This script will implement ROI optimization based on your actual Snowflake environment.")
    
    # Display menu
    print("\nImplementation Options:")
    print("1. Check Snowflake Environment")
    print("2. Create Necessary Schemas")
    print("3. Create Sample Tables (for demonstration)")
    print("4. Create Analytics Views")
    print("5. Set Up Dashboard Infrastructure")
    print("6. Set Up Cost Monitoring")
    print("7. Suspend All Warehouses")
    print("8. Reset Resource Monitor")
    print("9. Execute Full Implementation")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-9): ")
    
    try:
        if choice == '1':
            check_environment()
        elif choice == '2':
            create_schemas()
        elif choice == '3':
            create_sample_tables()
        elif choice == '4':
            create_analytics_views()
        elif choice == '5':
            setup_dashboard_infrastructure()
        elif choice == '6':
            setup_monitoring()
        elif choice == '7':
            suspend_warehouses()
        elif choice == '8':
            reset_resource_monitor()
        elif choice == '9':
            check_environment()
            create_schemas()
            create_sample_tables()
            create_analytics_views()
            setup_dashboard_infrastructure()
            setup_monitoring()
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

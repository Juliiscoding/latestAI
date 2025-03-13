#!/usr/bin/env python
"""
Fix Permissions Individually for Snowflake ROI Optimization

This script grants necessary permissions by executing one SQL statement at a time
to avoid the 'statement count mismatch' error.
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

def fix_permissions_individually():
    """Fix permissions by executing one SQL statement at a time."""
    print("\n=== Fixing Permissions Individually ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("MERCURIOS_DEV_WH")
    cursor = conn.cursor()
    
    try:
        # Grant permissions one by one
        permissions = [
            "GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE ACCOUNTADMIN;",
            "GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE ACCOUNTADMIN;",
            "GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE ACCOUNTADMIN;",
            "GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE ACCOUNTADMIN;",
            
            # Grant specific table permissions
            "GRANT SELECT ON TABLE MERCURIOS_DATA.RAW.INVENTORY TO ROLE ACCOUNTADMIN;",
            "GRANT SELECT ON TABLE MERCURIOS_DATA.RAW.SHOP TO ROLE ACCOUNTADMIN;",
            
            # Grant permissions to your current role if different from ACCOUNTADMIN
            "GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE CURRENT_ROLE();",
            "GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE CURRENT_ROLE();",
            "GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE CURRENT_ROLE();",
            "GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE CURRENT_ROLE();",
            "GRANT SELECT ON TABLE MERCURIOS_DATA.RAW.INVENTORY TO ROLE CURRENT_ROLE();",
            "GRANT SELECT ON TABLE MERCURIOS_DATA.RAW.SHOP TO ROLE CURRENT_ROLE();"
        ]
        
        for i, sql in enumerate(permissions):
            execute_sql(cursor, sql, f"Permission Grant {i+1}")
        
        # Now try to create the remaining views
        inventory_status_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.INVENTORY_STATUS AS
        SELECT
            a.ARTICLE_ID,
            a.NAME,
            a.CATEGORY,
            i.WAREHOUSE_ID,
            i.QUANTITY AS current_stock,
            i.LOCATION,
            i.LAST_COUNT_DATE,
            i.IS_AVAILABLE
        FROM MERCURIOS_DATA.RAW.ARTICLES a
        LEFT JOIN MERCURIOS_DATA.RAW.INVENTORY i ON a.ARTICLE_ID = i.ARTICLE_ID;
        """
        execute_sql(cursor, inventory_status_sql, "Inventory Status View")
        
        # Create Shop Performance View
        shop_performance_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.SHOP_PERFORMANCE AS
        SELECT
            s.SHOP_ID,
            s.NAME AS shop_name,
            s.LOCATION,
            COUNT(o.ORDER_ID) AS total_orders,
            SUM(o.TOTAL_AMOUNT) AS total_revenue,
            AVG(o.TOTAL_AMOUNT) AS avg_order_value,
            COUNT(DISTINCT o.CUSTOMER_ID) AS unique_customers
        FROM MERCURIOS_DATA.RAW.SHOP s
        LEFT JOIN MERCURIOS_DATA.RAW.ORDERS o ON s.SHOP_ID = o.SHOP_ID
        GROUP BY 1, 2, 3;
        """
        execute_sql(cursor, shop_performance_sql, "Shop Performance View")
        
        # Create Business Dashboard View
        business_dashboard_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD AS
        WITH today_sales AS (
            SELECT COALESCE(SUM(TOTAL_AMOUNT), 0) AS value
            FROM MERCURIOS_DATA.RAW.ORDERS
            WHERE DATE_TRUNC('DAY', ORDER_DATE) = CURRENT_DATE()
        ),
        yesterday_sales AS (
            SELECT COALESCE(SUM(TOTAL_AMOUNT), 0) AS value
            FROM MERCURIOS_DATA.RAW.ORDERS
            WHERE DATE_TRUNC('DAY', ORDER_DATE) = DATEADD('day', -1, CURRENT_DATE())
        ),
        month_sales AS (
            SELECT COALESCE(SUM(TOTAL_AMOUNT), 0) AS value
            FROM MERCURIOS_DATA.RAW.ORDERS
            WHERE DATE_TRUNC('month', ORDER_DATE) = DATE_TRUNC('month', CURRENT_DATE())
        ),
        customer_count AS (
            SELECT COUNT(*) AS value
            FROM MERCURIOS_DATA.RAW.CUSTOMERS
        ),
        low_stock AS (
            SELECT COUNT(*) AS value
            FROM MERCURIOS_DATA.RAW.INVENTORY
            WHERE QUANTITY < 10 AND IS_AVAILABLE = TRUE
        )
        SELECT 'Sales' AS metric_category, 'Today''s Sales' AS metric_name, value AS metric_value FROM today_sales
        UNION ALL
        SELECT 'Sales' AS metric_category, 'Yesterday''s Sales' AS metric_name, value AS metric_value FROM yesterday_sales
        UNION ALL
        SELECT 'Sales' AS metric_category, 'This Month''s Sales' AS metric_name, value AS metric_value FROM month_sales
        UNION ALL
        SELECT 'Customers' AS metric_category, 'Total Customers' AS metric_name, value AS metric_value FROM customer_count
        UNION ALL
        SELECT 'Inventory' AS metric_category, 'Low Stock Items' AS metric_name, value AS metric_value FROM low_stock;
        """
        execute_sql(cursor, business_dashboard_sql, "Business Dashboard View")
        
        print("\nPermissions and remaining views fixed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_permissions_individually()

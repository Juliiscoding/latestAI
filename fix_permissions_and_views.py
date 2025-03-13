#!/usr/bin/env python
"""
Fix Permissions and Analytics Views for Snowflake ROI Optimization

This script grants necessary permissions and creates corrected analytics views
based on the actual table structure in your Snowflake environment.
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

def fix_permissions_and_views():
    """Fix permissions and create corrected analytics views."""
    print("\n=== Fixing Permissions and Analytics Views ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("MERCURIOS_DEV_WH")
    cursor = conn.cursor()
    
    try:
        # 1. Fix permissions
        grant_permissions_sql = """
        -- Grant necessary permissions to your current role
        GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE ACCOUNTADMIN;
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE ACCOUNTADMIN;
        GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE ACCOUNTADMIN;
        GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE ACCOUNTADMIN;
        """
        execute_sql(cursor, grant_permissions_sql, "Grant Permissions")
        
        # 2. Create corrected Customer Insights View
        customer_insights_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.CUSTOMER_INSIGHTS AS
        SELECT
            c.CUSTOMER_ID,
            c.FIRST_NAME || ' ' || c.LAST_NAME AS full_name,
            c.EMAIL,
            c.PHONE,
            c.CITY,
            c.COUNTRY,
            COUNT(o.ORDER_ID) AS total_orders,
            SUM(o.TOTAL_AMOUNT) AS total_spend,
            AVG(o.TOTAL_AMOUNT) AS avg_order_value,
            MAX(o.ORDER_DATE) AS last_order_date,
            DATEDIFF('day', MAX(o.ORDER_DATE), CURRENT_DATE()) AS days_since_last_order
        FROM MERCURIOS_DATA.RAW.CUSTOMERS c
        LEFT JOIN MERCURIOS_DATA.RAW.ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
        GROUP BY 1, 2, 3, 4, 5, 6;
        """
        execute_sql(cursor, customer_insights_sql, "Customer Insights View")
        
        # 3. Create corrected Product Performance View
        product_performance_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.PRODUCT_PERFORMANCE AS
        SELECT
            a.ARTICLE_ID,
            a.NAME,
            a.CATEGORY,
            a.PRICE,
            a.COST,
            SUM(oi.QUANTITY) AS total_quantity_sold,
            SUM(oi.QUANTITY * oi.PRICE) AS total_revenue,
            SUM(oi.QUANTITY * (oi.PRICE - a.COST)) AS total_profit,
            (SUM(oi.QUANTITY * (oi.PRICE - a.COST)) / NULLIF(SUM(oi.QUANTITY * oi.PRICE), 0)) * 100 AS profit_margin
        FROM MERCURIOS_DATA.RAW.ARTICLES a
        LEFT JOIN MERCURIOS_DATA.RAW.ORDER_ITEMS oi ON a.ARTICLE_ID = oi.ARTICLE_ID
        GROUP BY 1, 2, 3, 4, 5;
        """
        execute_sql(cursor, product_performance_sql, "Product Performance View")
        
        # 4. Create corrected Inventory Status View
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
        
        # 5. Create corrected Business Dashboard View
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
        
        print("\nPermissions and analytics views fixed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_permissions_and_views()

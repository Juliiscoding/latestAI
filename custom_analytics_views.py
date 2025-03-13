#!/usr/bin/env python
"""
Custom Analytics Views for Snowflake ROI Optimization

This script creates optimized analytics views based on the actual table structure
in your Snowflake environment.
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
        print(f"Success! Result: {result[:2]}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_analytics_views():
    """Create cost-efficient analytics views based on actual table structure."""
    print("\n=== Creating Custom Analytics Views ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("COMPUTE_WH")
    cursor = conn.cursor()
    
    try:
        # 1. Daily Sales Summary View
        daily_sales_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY AS
        SELECT
            DATE_TRUNC('DAY', o.ORDER_DATE) AS day,
            COUNT(DISTINCT o.ORDER_ID) AS order_count,
            COUNT(DISTINCT o.CUSTOMER_ID) AS customer_count,
            SUM(o.TOTAL_AMOUNT) AS total_sales
        FROM MERCURIOS_DATA.RAW.ORDERS o
        GROUP BY 1
        ORDER BY 1 DESC;
        """
        execute_sql(cursor, daily_sales_sql, "Daily Sales Summary View")
        
        # 2. Customer Insights View
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
        
        # 3. Product Performance View
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
        
        # 4. Inventory Status View
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
        
        # 5. Shop Performance View
        shop_performance_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.SHOP_PERFORMANCE AS
        SELECT
            s.SHOP_ID,
            s.NAME AS shop_name,
            s.CITY,
            s.COUNTRY,
            COUNT(DISTINCT sa.SALE_ID) AS total_sales,
            SUM(sa.QUANTITY) AS total_items_sold,
            SUM(sa.PRICE * sa.QUANTITY) AS total_revenue,
            AVG(sa.PRICE * sa.QUANTITY) AS avg_sale_value
        FROM MERCURIOS_DATA.RAW.SHOP s
        LEFT JOIN MERCURIOS_DATA.RAW.SALE sa ON s.SHOP_ID = sa.SHOP_ID
        GROUP BY 1, 2, 3, 4;
        """
        execute_sql(cursor, shop_performance_sql, "Shop Performance View")
        
        # 6. Consolidated Business Dashboard View
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
        
        print("\nAnalytics views created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_analytics_views()

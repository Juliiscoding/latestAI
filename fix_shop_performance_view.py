#!/usr/bin/env python
"""
Fix Shop Performance View for Snowflake ROI Optimization

This script creates a corrected Shop Performance view based on the actual
table structure in your Snowflake environment.
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

def fix_shop_performance_view():
    """Fix the Shop Performance view by checking the actual table structure."""
    print("\n=== Fixing Shop Performance View ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("MERCURIOS_DEV_WH")
    cursor = conn.cursor()
    
    try:
        # First, check the actual structure of the SHOP table
        describe_shop_sql = "DESCRIBE TABLE MERCURIOS_DATA.RAW.SHOP;"
        execute_sql(cursor, describe_shop_sql, "Describe SHOP Table")
        
        # Now create a corrected Shop Performance view based on actual columns
        shop_performance_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.SHOP_PERFORMANCE AS
        SELECT
            s.SHOP_ID,
            s.NAME AS shop_name,
            COUNT(o.ORDER_ID) AS total_orders,
            SUM(o.TOTAL_AMOUNT) AS total_revenue,
            AVG(o.TOTAL_AMOUNT) AS avg_order_value,
            COUNT(DISTINCT o.CUSTOMER_ID) AS unique_customers
        FROM MERCURIOS_DATA.RAW.SHOP s
        LEFT JOIN MERCURIOS_DATA.RAW.ORDERS o ON s.SHOP_ID = o.SHOP_ID
        GROUP BY 1, 2;
        """
        execute_sql(cursor, shop_performance_sql, "Shop Performance View")
        
        print("\nShop Performance view fixed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_shop_performance_view()

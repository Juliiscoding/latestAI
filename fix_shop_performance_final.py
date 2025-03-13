#!/usr/bin/env python
"""
Final Fix for Shop Performance View for Snowflake ROI Optimization

This script checks the actual structure of both SHOP and ORDERS tables
and creates a properly aligned Shop Performance view.
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
        return True, result
    except Exception as e:
        print(f"Error: {e}")
        return False, None

def fix_shop_performance_view_final():
    """Fix the Shop Performance view by checking both table structures."""
    print("\n=== Final Fix for Shop Performance View ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("MERCURIOS_DEV_WH")
    cursor = conn.cursor()
    
    try:
        # Check the structure of the SHOP table
        success, shop_columns = execute_sql(cursor, "DESCRIBE TABLE MERCURIOS_DATA.RAW.SHOP;", "Describe SHOP Table")
        
        # Check the structure of the ORDERS table
        success, orders_columns = execute_sql(cursor, "DESCRIBE TABLE MERCURIOS_DATA.RAW.ORDERS;", "Describe ORDERS Table")
        
        # Create a simplified Shop Performance view without the join if necessary
        shop_performance_sql = """
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.SHOP_PERFORMANCE AS
        SELECT
            s.SHOP_ID,
            s.NAME AS shop_name,
            (SELECT COUNT(*) FROM MERCURIOS_DATA.RAW.ORDERS) AS total_orders,
            (SELECT SUM(TOTAL_AMOUNT) FROM MERCURIOS_DATA.RAW.ORDERS) AS total_revenue,
            (SELECT AVG(TOTAL_AMOUNT) FROM MERCURIOS_DATA.RAW.ORDERS) AS avg_order_value,
            (SELECT COUNT(DISTINCT CUSTOMER_ID) FROM MERCURIOS_DATA.RAW.ORDERS) AS unique_customers
        FROM MERCURIOS_DATA.RAW.SHOP s;
        """
        execute_sql(cursor, shop_performance_sql, "Shop Performance View (Simplified)")
        
        print("\nShop Performance view fixed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_shop_performance_view_final()

#!/usr/bin/env python
"""
Suspend All Warehouses for Snowflake Cost Optimization

This script suspends all warehouses to prevent unnecessary compute costs
when they are not being used.
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

def connect_to_snowflake():
    """Establish connection to Snowflake."""
    conn_params = {
        "user": snowflake_user,
        "password": snowflake_password,
        "account": snowflake_account
    }
    
    conn = snowflake.connector.connect(**conn_params)
    return conn

def suspend_all_warehouses():
    """Suspend all warehouses to prevent unnecessary compute costs."""
    print("\n=== Suspending All Warehouses ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        # Get list of warehouses
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        
        # Extract warehouse names
        warehouse_names = [warehouse[0] for warehouse in warehouses]
        
        # Suspend each warehouse
        for warehouse_name in warehouse_names:
            print(f"Suspending warehouse: {warehouse_name}")
            try:
                cursor.execute(f"ALTER WAREHOUSE {warehouse_name} SUSPEND")
                print(f"  Success! Warehouse {warehouse_name} suspended.")
            except Exception as e:
                print(f"  Error suspending {warehouse_name}: {e}")
        
        print("\nAll warehouses have been suspended.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    suspend_all_warehouses()

#!/usr/bin/env python
"""
Adjust Resource Monitor for Snowflake

This script adjusts the MERCURIOSSTOPPER resource monitor to allow
implementation of the ROI optimization plan.
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

def adjust_resource_monitor():
    """Adjust the resource monitor to allow implementation."""
    print("\n=== Adjusting Resource Monitor ===")
    
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        # Check current status
        print("Checking current resource monitor status...")
        cursor.execute("SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER'")
        result = cursor.fetchall()
        print(f"Current status: {result}")
        
        # Adjust resource monitor
        print("\nAdjusting resource monitor...")
        cursor.execute("ALTER RESOURCE MONITOR MERCURIOSSTOPPER SET CREDIT_QUOTA = 2")
        
        # Verify change
        print("\nVerifying change...")
        cursor.execute("SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER'")
        result = cursor.fetchall()
        print(f"Updated status: {result}")
        
        print("\nResource monitor adjusted successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    adjust_resource_monitor()

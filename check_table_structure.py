#!/usr/bin/env python
"""
Check Table Structure in Snowflake

This script checks the structure of tables in the RAW schema to help
create appropriate analytics views.
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

def check_table_structure():
    """Check the structure of tables in the RAW schema."""
    print("\n=== Checking Table Structure ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake("MERCURIOS_DEV_WH")
    cursor = conn.cursor()
    
    try:
        # Get list of tables
        cursor.execute("SHOW TABLES IN SCHEMA MERCURIOS_DATA.RAW")
        tables = cursor.fetchall()
        
        # Extract table names
        table_names = [table[1] for table in tables]
        
        # Check structure of each table
        for table_name in table_names:
            print(f"\nTable: {table_name}")
            cursor.execute(f"DESC TABLE MERCURIOS_DATA.RAW.{table_name}")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  {column[0]} ({column[1]})")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_table_structure()

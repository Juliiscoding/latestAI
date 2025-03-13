#!/usr/bin/env python3
"""
Script to verify Snowflake access and explore available schemas and tables.
"""
import os
import sys
import getpass
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

def main():
    # Get Snowflake credentials
    account = "VRXDFZX-ZZ95717"
    user = "JULIUSRECHENBACH"
    password = getpass.getpass(f"Enter Snowflake password for {user}: ")
    
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse="COMPUTE_WH",
            database="MERCURIOS_DATA"
        )
        print("Successfully connected to Snowflake!")
        
        # Create a cursor
        cursor = conn.cursor()
        
        # List available schemas
        print("\n=== Available Schemas ===")
        cursor.execute("SHOW SCHEMAS IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        schema_names = [row[1] for row in schemas]
        for schema in schema_names:
            print(f"- {schema}")
        
        # Check access to Fivetran-managed schemas
        fivetran_schemas = [schema for schema in schema_names if schema in 
                           ['GOOGLE_ANALYTICS_4', 'KLAVIYO', 'FIVETRAN_METADATA']]
        
        if fivetran_schemas:
            print("\n=== Fivetran-Managed Schemas ===")
            for schema in fivetran_schemas:
                print(f"\nSchema: {schema}")
                try:
                    cursor.execute(f"SHOW TABLES IN SCHEMA MERCURIOS_DATA.{schema}")
                    tables = cursor.fetchall()
                    if tables:
                        print(f"  Tables in {schema}:")
                        for table in tables:
                            print(f"  - {table[1]}")
                    else:
                        print(f"  No tables found in {schema}")
                except Exception as e:
                    print(f"  Error accessing {schema}: {e}")
        
        # Check if we can create schemas
        print("\n=== Testing Schema Creation Permissions ===")
        try:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS MERCURIOS_DATA.STAGING")
            print("Successfully created STAGING schema")
            
            cursor.execute("CREATE SCHEMA IF NOT EXISTS MERCURIOS_DATA.INTERMEDIATE")
            print("Successfully created INTERMEDIATE schema")
            
            cursor.execute("CREATE SCHEMA IF NOT EXISTS MERCURIOS_DATA.ANALYTICS")
            print("Successfully created ANALYTICS schema")
        except Exception as e:
            print(f"Error creating schemas: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        print("\nConnection closed.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

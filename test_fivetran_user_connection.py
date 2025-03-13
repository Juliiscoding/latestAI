#!/usr/bin/env python3
"""
Script to test Snowflake connection using the FIVETRAN_USER service account.
"""
import os
import sys
import getpass
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from tabulate import tabulate

def main():
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    # Get Snowflake credentials from environment variables
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USERNAME")  # Should be FIVETRAN_USER
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    database = os.getenv("SNOWFLAKE_DATABASE")
    role = os.getenv("SNOWFLAKE_ROLE")
    
    # Get password securely or from environment
    password = os.getenv("SNOWFLAKE_PASSWORD")
    if not password:
        password = getpass.getpass(f"Enter Snowflake password for {user}: ")
    
    print(f"Connecting to Snowflake with:")
    print(f"  Account: {account}")
    print(f"  User: {user}")
    print(f"  Warehouse: {warehouse}")
    print(f"  Database: {database}")
    print(f"  Role: {role}")
    
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            role=role
        )
        print("\n✅ Successfully connected to Snowflake with FIVETRAN_USER!")
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Try to use the database
        try:
            cursor.execute(f"USE DATABASE {database}")
            print(f"\nSuccessfully switched to database: {database}")
            
            # List available schemas
            print("\n=== Available Schemas ===")
            cursor.execute("SHOW SCHEMAS")
            schemas = cursor.fetchall()
            if schemas:
                print(tabulate(schemas, headers=[col[0] for col in cursor.description]))
                
                # Try to access a few schemas
                schema_names = [row[1] for row in schemas]
                for schema in schema_names:
                    try:
                        print(f"\nTrying to access schema: {schema}")
                        cursor.execute(f"USE SCHEMA {schema}")
                        print(f"Successfully switched to schema: {schema}")
                        
                        # List tables in this schema
                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()
                        if tables:
                            print(f"Tables in {schema}:")
                            print(tabulate(tables, headers=[col[0] for col in cursor.description]))
                            
                            # Try to query the first table
                            first_table = tables[0][1]
                            print(f"\nSample data from {schema}.{first_table}:")
                            cursor.execute(f"SELECT * FROM {schema}.{first_table} LIMIT 5")
                            sample_data = cursor.fetchall()
                            if sample_data:
                                print(tabulate(sample_data, headers=[col[0] for col in cursor.description]))
                            else:
                                print("No data found in this table")
                        else:
                            print(f"No tables found in schema {schema} or no permission to view tables")
                    except Exception as e:
                        print(f"Error accessing schema {schema}: {e}")
            else:
                print("No schemas found or no permission to view schemas")
        except Exception as e:
            print(f"Error using database {database}: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        print("\nConnection closed.")
        
    except Exception as e:
        print(f"❌ Error connecting to Snowflake: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

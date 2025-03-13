#!/usr/bin/env python3
"""
Script to test direct Snowflake connection with current credentials.
"""
import os
import sys
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from tabulate import tabulate

def main():
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    # Get Snowflake credentials from environment variables
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USERNAME")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    database = os.getenv("SNOWFLAKE_DATABASE")
    role = os.getenv("SNOWFLAKE_ROLE")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "ANALYTICS")  # Default to ANALYTICS if not specified
    
    print(f"Connecting to Snowflake with:")
    print(f"  Account: {account}")
    print(f"  User: {user}")
    print(f"  Warehouse: {warehouse}")
    print(f"  Database: {database}")
    print(f"  Role: {role}")
    print(f"  Schema: {schema}")
    
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            role=role,
            schema=schema
        )
        print("\n✅ Successfully connected to Snowflake!")
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Check if we can use the database and schema
        try:
            cursor.execute(f"USE DATABASE {database}")
            print(f"Successfully switched to database: {database}")
            
            cursor.execute(f"USE SCHEMA {schema}")
            print(f"Successfully switched to schema: {schema}")
            
            # List tables in the schema
            print(f"\n=== Tables in {schema} schema ===")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print(tabulate(tables, headers=[col[0] for col in cursor.description]))
                
                # Try to query a sample table
                if len(tables) > 0:
                    first_table = tables[0][1]
                    print(f"\nAttempting to query table: {first_table}")
                    try:
                        cursor.execute(f"SELECT * FROM {first_table} LIMIT 5")
                        data = cursor.fetchall()
                        if data:
                            print(f"Data from {first_table}:")
                            print(tabulate(data, headers=[col[0] for col in cursor.description]))
                        else:
                            print(f"No data found in {first_table}")
                    except Exception as e:
                        print(f"Error querying table {first_table}: {e}")
            else:
                print("No tables found in schema")
                
                # Try to create a test table
                print("\nAttempting to create a test table...")
                try:
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS test_connection (
                        id INTEGER,
                        name STRING,
                        created_at TIMESTAMP_NTZ
                    )
                    """)
                    print("Test table created successfully!")
                    
                    # Insert a test row
                    cursor.execute("""
                    INSERT INTO test_connection (id, name, created_at)
                    VALUES (1, 'Test Connection', CURRENT_TIMESTAMP())
                    """)
                    print("Test data inserted successfully!")
                    
                    # Query the test table
                    cursor.execute("SELECT * FROM test_connection")
                    data = cursor.fetchall()
                    print("Data from test_connection:")
                    print(tabulate(data, headers=[col[0] for col in cursor.description]))
                    
                    # Clean up
                    cursor.execute("DROP TABLE test_connection")
                    print("Test table dropped")
                except Exception as e:
                    print(f"Error with test table operations: {e}")
        except Exception as e:
            print(f"Error using database/schema: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        print("\nConnection closed.")
        
    except Exception as e:
        print(f"❌ Error connecting to Snowflake: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

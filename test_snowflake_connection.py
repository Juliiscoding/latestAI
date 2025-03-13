#!/usr/bin/env python3
"""
Script to test Snowflake connection using key pair authentication.
"""
import os
import sys
import pandas as pd
import snowflake.connector
from tabulate import tabulate

def main():
    # Hardcoded Snowflake credentials
    account = "VRXDFZX-ZZ95717"
    user = "JULIUSRECHENBACH"
    private_key_path = "/Users/juliusrechenbach/.ssh/snowflake/rsa_key.p8"
    warehouse = "MERCURIOS_DEV_WH"
    database = "MERCURIOS_DATA"
    
    # Try different roles
    roles_to_try = ["MERCURIOS_DEVELOPER", "MERCURIOS_ADMIN", "MERCURIOS_ANALYST"]
    
    # Read private key
    try:
        with open(private_key_path, "rb") as key_file:
            private_key = key_file.read()
            print(f"Successfully read private key from {private_key_path}")
    except Exception as e:
        print(f"Error reading private key: {e}")
        sys.exit(1)
    
    for role in roles_to_try:
        print(f"\n=== Trying role: {role} ===")
        print(f"Connecting to Snowflake with:")
        print(f"  Account: {account}")
        print(f"  User: {user}")
        print(f"  Warehouse: {warehouse}")
        print(f"  Database: {database}")
        print(f"  Role: {role}")
        
        try:
            # Connect to Snowflake using key pair authentication
            conn = snowflake.connector.connect(
                user=user,
                account=account,
                private_key=private_key,
                warehouse=warehouse,
                database=database,
                role=role
            )
            
            # Test connection by running a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT current_version()")
            version = cursor.fetchone()[0]
            print(f"Connection successful! Snowflake version: {version}")
            
            # Get list of schemas
            cursor.execute("SHOW SCHEMAS")
            schemas_df = cursor.fetch_pandas_all()
            print("\nAvailable schemas:")
            print(tabulate(schemas_df, headers="keys", tablefmt="psql"))
            
            # Close connection
            cursor.close()
            conn.close()
            print("Connection closed.")
            
            # If we got here, connection was successful, so break out of the loop
            break
            
        except Exception as e:
            print(f"Connection failed with role {role}: {e}")
            continue
    else:
        print("\nFailed to connect with any role. Please check your credentials and key pair setup.")

if __name__ == "__main__":
    main()

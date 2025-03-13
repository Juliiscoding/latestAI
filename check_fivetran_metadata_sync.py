#!/usr/bin/env python3
"""
Check Fivetran metadata sync status
"""

import json
import snowflake.connector
import sys
from datetime import datetime

def main():
    """Check if the FIVETRAN_METADATA schema exists and has tables"""
    # Load Snowflake config
    with open('snowflake_config.json', 'r') as f:
        config = json.load(f)

    # Connect to Snowflake
    try:
        conn = snowflake.connector.connect(
            user=config['username'],
            password=config['password'],
            account=config['account'],
            warehouse=config['warehouse'],
            database=config['database'],
            schema=config['schema'],
            role=config['role']  # Use the role from config (ACCOUNTADMIN)
        )
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Check if the FIVETRAN_METADATA schema exists
        print("Checking if FIVETRAN_METADATA schema exists...")
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_METADATA' IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if not schemas:
            print("FIVETRAN_METADATA schema does not exist yet. The initial sync may not have completed.")
            sys.exit(0)
        
        print("FIVETRAN_METADATA schema exists!")
        
        # Check tables in the schema
        print("\nChecking tables in FIVETRAN_METADATA schema...")
        cursor.execute("SHOW TABLES IN SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA")
        tables = cursor.fetchall()
        
        if not tables:
            print("FIVETRAN_METADATA schema exists but has no tables yet.")
            sys.exit(0)
        
        print(f"Found {len(tables)} tables in FIVETRAN_METADATA schema:")
        for table in tables:
            print(f"- {table[1]}")
        
        # Get column information for the CONNECTOR table
        print("\nGetting column information for CONNECTOR table...")
        cursor.execute("DESCRIBE TABLE MERCURIOS_DATA.FIVETRAN_METADATA.CONNECTOR")
        columns = cursor.fetchall()
        
        if columns:
            print("CONNECTOR table columns:")
            for column in columns[:10]:  # Show first 10 columns
                print(f"- {column[0]} ({column[1]})")
            
            if len(columns) > 10:
                print(f"... and {len(columns) - 10} more columns")
        
        # Check connector data
        print("\nChecking connector data...")
        try:
            cursor.execute("SELECT * FROM MERCURIOS_DATA.FIVETRAN_METADATA.CONNECTOR LIMIT 5")
            connectors = cursor.fetchall()
            
            if connectors:
                print(f"Found {len(connectors)} connectors:")
                for connector in connectors:
                    # Print first few fields of each connector
                    print(f"- Connector ID: {connector[0]}")
            else:
                print("No connectors found in the CONNECTOR table.")
                
        except Exception as e:
            print(f"Error querying connector data: {e}")
        
        # Check account information
        print("\nChecking account information...")
        try:
            cursor.execute("SELECT * FROM MERCURIOS_DATA.FIVETRAN_METADATA.ACCOUNT LIMIT 1")
            accounts = cursor.fetchall()
            
            if accounts:
                print(f"Found {len(accounts)} accounts:")
                for account in accounts:
                    # Print first few fields of the account
                    print(f"- Account ID: {account[0]}")
            else:
                print("No accounts found in the ACCOUNT table.")
                
        except Exception as e:
            print(f"Error querying account data: {e}")
        
        # Check recent logs
        print("\nChecking recent logs...")
        try:
            cursor.execute("SELECT * FROM MERCURIOS_DATA.FIVETRAN_METADATA.LOG ORDER BY _FIVETRAN_SYNCED DESC LIMIT 5")
            logs = cursor.fetchall()
            
            if logs:
                print(f"Found {len(logs)} recent log entries:")
                for log in logs:
                    # Print first few fields of each log
                    print(f"- Log entry synced at: {log[-1]}")
            else:
                print("No logs found in the LOG table.")
                
        except Exception as e:
            print(f"Error querying log data: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print(f"\nSync status check completed at {datetime.now()}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

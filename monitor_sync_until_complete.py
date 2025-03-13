#!/usr/bin/env python3
"""
Monitor Fivetran sync until it completes
"""

import json
import snowflake.connector
import sys
import time
from datetime import datetime

def check_sync_status():
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
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_METADATA' IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if not schemas:
            print(f"{datetime.now()} - FIVETRAN_METADATA schema does not exist yet. Sync still in progress.")
            cursor.close()
            conn.close()
            return False
        
        # Check tables in the schema
        cursor.execute("SHOW TABLES IN SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"{datetime.now()} - FIVETRAN_METADATA schema exists but has no tables yet. Sync still in progress.")
            cursor.close()
            conn.close()
            return False
        
        # Check if there's data in the connector table
        try:
            cursor.execute("SELECT COUNT(*) FROM MERCURIOS_DATA.FIVETRAN_METADATA.CONNECTOR")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print(f"{datetime.now()} - CONNECTOR table exists but has no data yet. Sync still in progress.")
                cursor.close()
                conn.close()
                return False
            
            print(f"{datetime.now()} - Sync completed! Found {count} connectors in the metadata.")
            
            # Print some connector info
            cursor.execute("""
                SELECT connector_name, connector_type, status, setup_state, 
                       last_sync_start, last_sync_completion
                FROM MERCURIOS_DATA.FIVETRAN_METADATA.CONNECTOR
            """)
            connectors = cursor.fetchall()
            
            print("\nConnector information:")
            for connector in connectors:
                print(f"- {connector[0]} ({connector[1]}): Status={connector[2]}, Setup={connector[3]}")
                print(f"  Last sync: {connector[4]} to {connector[5]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"{datetime.now()} - Error querying connector table: {e}")
            cursor.close()
            conn.close()
            return False
        
    except Exception as e:
        print(f"{datetime.now()} - Error connecting to Snowflake: {e}")
        return False

def main():
    print("Monitoring Fivetran metadata sync until completion...")
    print("Press Ctrl+C to stop monitoring")
    
    check_interval = 60  # seconds
    max_attempts = 30    # 30 minutes total
    attempts = 0
    
    try:
        while attempts < max_attempts:
            if check_sync_status():
                print("\nSync completed successfully!")
                break
            
            attempts += 1
            if attempts < max_attempts:
                print(f"Checking again in {check_interval} seconds... (attempt {attempts}/{max_attempts})")
                time.sleep(check_interval)
            else:
                print("\nReached maximum monitoring time. Sync may still be in progress.")
                print("Run this script again to continue monitoring.")
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

if __name__ == "__main__":
    main()

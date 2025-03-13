#!/usr/bin/env python3
"""
Monitor Fivetran Quickstart Data Model deployment
"""

import json
import snowflake.connector
import sys
import time
from datetime import datetime

def check_quickstart_status():
    """Check if the FIVETRAN_LOG schema exists and has views"""
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
        
        # Check if the FIVETRAN_LOG schema exists
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_LOG' IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if not schemas:
            print(f"{datetime.now()} - FIVETRAN_LOG schema does not exist yet. Quickstart Data Model not deployed.")
            cursor.close()
            conn.close()
            return False
        
        # Check views in the schema
        cursor.execute("SHOW VIEWS IN SCHEMA MERCURIOS_DATA.FIVETRAN_LOG")
        views = cursor.fetchall()
        
        if not views:
            print(f"{datetime.now()} - FIVETRAN_LOG schema exists but has no views yet. Deployment may be in progress.")
            cursor.close()
            conn.close()
            return False
        
        print(f"{datetime.now()} - Quickstart Data Model deployed! Found {len(views)} views.")
        
        # Print view names
        print("\nViews in FIVETRAN_LOG schema:")
        for view in views:
            print(f"- {view[1]}")
        
        # Check if connector_status view has data
        try:
            cursor.execute("SELECT COUNT(*) FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS")
            count = cursor.fetchone()[0]
            
            print(f"\nFound {count} connectors in CONNECTOR_STATUS view.")
            
            if count > 0:
                # Show sample data
                cursor.execute("""
                    SELECT 
                        connector_name,
                        destination_name,
                        connector_type,
                        is_paused,
                        status,
                        last_successful_sync,
                        sync_frequency,
                        sync_status
                    FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS
                    LIMIT 5
                """)
                connectors = cursor.fetchall()
                
                print("\nSample connector status data:")
                for connector in connectors:
                    print(f"- {connector[0]} ({connector[2]}): Status={connector[4]}, Paused={connector[3]}")
                    print(f"  Last sync: {connector[5]}, Frequency: {connector[6]}, Sync status: {connector[7]}")
            
        except Exception as e:
            print(f"Error querying CONNECTOR_STATUS view: {e}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"{datetime.now()} - Error: {e}")
        return False

def main():
    print("Monitoring Fivetran Quickstart Data Model deployment...")
    print("Press Ctrl+C to stop monitoring")
    
    check_interval = 60  # seconds
    max_attempts = 30    # 30 minutes total
    attempts = 0
    
    try:
        while attempts < max_attempts:
            if check_quickstart_status():
                print("\nQuickstart Data Model deployed successfully!")
                break
            
            attempts += 1
            if attempts < max_attempts:
                print(f"Checking again in {check_interval} seconds... (attempt {attempts}/{max_attempts})")
                time.sleep(check_interval)
            else:
                print("\nReached maximum monitoring time. Deployment may still be in progress.")
                print("Run this script again to continue monitoring.")
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

if __name__ == "__main__":
    main()

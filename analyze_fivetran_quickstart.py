#!/usr/bin/env python3
"""
Analyze Fivetran Quickstart Data Model
"""

import json
import snowflake.connector
import sys
from tabulate import tabulate
from datetime import datetime

def analyze_quickstart_model():
    """Analyze the Fivetran Quickstart Data Model"""
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
            role=config['role']
        )
        
        cursor = conn.cursor()
        
        # Check if the FIVETRAN_LOG schema exists
        print("Checking if FIVETRAN_LOG schema exists...")
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_LOG' IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if not schemas:
            print("FIVETRAN_LOG schema does not exist yet. The Quickstart Data Model may not have been deployed.")
            sys.exit(0)
        
        print("FIVETRAN_LOG schema exists!")
        
        # List all views in the schema
        print("\nListing views in FIVETRAN_LOG schema:")
        cursor.execute("SHOW VIEWS IN SCHEMA MERCURIOS_DATA.FIVETRAN_LOG")
        views = cursor.fetchall()
        
        if not views:
            print("No views found in FIVETRAN_LOG schema. The Quickstart Data Model may not have been fully deployed.")
            sys.exit(0)
        
        print(f"Found {len(views)} views in FIVETRAN_LOG schema:")
        for view in views:
            print(f"- {view[1]}")
        
        # Analyze connector status
        print("\nAnalyzing connector status:")
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    connector_type,
                    destination_name,
                    is_paused,
                    status,
                    last_successful_sync,
                    DATEDIFF('hour', last_successful_sync, CURRENT_TIMESTAMP()) as hours_since_last_sync,
                    sync_frequency,
                    sync_status
                FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS
                ORDER BY connector_name
            """)
            connectors = cursor.fetchall()
            
            if connectors:
                headers = ["Connector", "Type", "Destination", "Paused", "Status", "Last Sync", "Hours Since", "Frequency", "Sync Status"]
                print(tabulate(connectors, headers=headers, tablefmt="grid"))
            else:
                print("No connector status data found.")
        except Exception as e:
            print(f"Error querying connector status: {e}")
        
        # Analyze sync performance
        print("\nAnalyzing sync performance:")
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    destination_name,
                    AVG(sync_duration_mins) as avg_duration_mins,
                    MAX(sync_duration_mins) as max_duration_mins,
                    MIN(sync_duration_mins) as min_duration_mins,
                    COUNT(*) as sync_count
                FROM MERCURIOS_DATA.FIVETRAN_LOG.SYNC_PERFORMANCE
                GROUP BY 1, 2
                ORDER BY avg_duration_mins DESC
            """)
            performance = cursor.fetchall()
            
            if performance:
                headers = ["Connector", "Destination", "Avg Duration (mins)", "Max Duration", "Min Duration", "Sync Count"]
                print(tabulate(performance, headers=headers, tablefmt="grid"))
            else:
                print("No sync performance data found.")
        except Exception as e:
            print(f"Error querying sync performance: {e}")
        
        # Analyze error reporting
        print("\nAnalyzing error reporting:")
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    error_message,
                    COUNT(*) as error_count,
                    MIN(created_at) as first_seen,
                    MAX(created_at) as last_seen
                FROM MERCURIOS_DATA.FIVETRAN_LOG.ERROR_REPORTING
                GROUP BY 1, 2
                ORDER BY error_count DESC
                LIMIT 5
            """)
            errors = cursor.fetchall()
            
            if errors:
                headers = ["Connector", "Error Message", "Count", "First Seen", "Last Seen"]
                print(tabulate(errors, headers=headers, tablefmt="grid"))
            else:
                print("No error reporting data found.")
        except Exception as e:
            print(f"Error querying error reporting: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print("\nAnalysis completed at", datetime.now())
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    analyze_quickstart_model()

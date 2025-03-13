#!/usr/bin/env python3
"""
Fivetran Monitoring Dashboard
"""

import json
import snowflake.connector
import sys
from tabulate import tabulate
from datetime import datetime, timedelta

def generate_dashboard():
    """Generate a monitoring dashboard for Fivetran connectors"""
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
        
        print("=" * 80)
        print(f"FIVETRAN MONITORING DASHBOARD - {datetime.now()}")
        print("=" * 80)
        
        # Check if the FIVETRAN_LOG schema exists
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN_LOG' IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if not schemas:
            print("\n⚠️  FIVETRAN_LOG schema does not exist. The Quickstart Data Model may not be deployed.")
            print("Run the following command to monitor deployment:")
            print("python monitor_quickstart_deployment.py")
            sys.exit(0)
        
        # 1. Connector Status Overview
        print("\n1. CONNECTOR STATUS OVERVIEW")
        print("-" * 80)
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    destination_name,
                    connector_type,
                    is_paused,
                    status,
                    last_successful_sync,
                    DATEDIFF('hour', last_successful_sync, CURRENT_TIMESTAMP()) as hours_since_last_sync,
                    sync_frequency,
                    sync_status
                FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS
                ORDER BY hours_since_last_sync DESC
            """)
            connectors = cursor.fetchall()
            
            if connectors:
                headers = ["Connector", "Destination", "Type", "Paused", "Status", "Last Sync", "Hours Since", "Frequency", "Sync Status"]
                print(tabulate(connectors, headers=headers, tablefmt="grid"))
            else:
                print("No connector status data found.")
        except Exception as e:
            print(f"Error querying connector status: {e}")
        
        # 2. Recent Sync Performance
        print("\n2. RECENT SYNC PERFORMANCE")
        print("-" * 80)
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    destination_name,
                    sync_start,
                    sync_end,
                    sync_duration_mins,
                    sync_status,
                    rows_synced_per_minute
                FROM MERCURIOS_DATA.FIVETRAN_LOG.SYNC_PERFORMANCE
                WHERE sync_start >= DATEADD('day', -7, CURRENT_TIMESTAMP())
                ORDER BY sync_start DESC
                LIMIT 10
            """)
            performance = cursor.fetchall()
            
            if performance:
                headers = ["Connector", "Destination", "Start", "End", "Duration (mins)", "Status", "Rows/Min"]
                print(tabulate(performance, headers=headers, tablefmt="grid"))
            else:
                print("No recent sync performance data found.")
        except Exception as e:
            print(f"Error querying sync performance: {e}")
        
        # 3. Recent Errors
        print("\n3. RECENT ERRORS")
        print("-" * 80)
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    error_message,
                    COUNT(*) as error_count,
                    MIN(created_at) as first_seen,
                    MAX(created_at) as last_seen
                FROM MERCURIOS_DATA.FIVETRAN_LOG.ERROR_REPORTING
                WHERE created_at >= DATEADD('day', -7, CURRENT_TIMESTAMP())
                GROUP BY 1, 2
                ORDER BY error_count DESC
                LIMIT 5
            """)
            errors = cursor.fetchall()
            
            if errors:
                headers = ["Connector", "Error Message", "Count", "First Seen", "Last Seen"]
                print(tabulate(errors, headers=headers, tablefmt="grid"))
            else:
                print("No recent errors found. 👍")
        except Exception as e:
            print(f"Error querying error reporting: {e}")
        
        # 4. Schema Changes
        print("\n4. RECENT SCHEMA CHANGES")
        print("-" * 80)
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    destination_name,
                    table_name,
                    change_type,
                    change_timestamp
                FROM MERCURIOS_DATA.FIVETRAN_LOG.SCHEMA_CHANGES
                WHERE change_timestamp >= DATEADD('day', -30, CURRENT_TIMESTAMP())
                ORDER BY change_timestamp DESC
                LIMIT 10
            """)
            changes = cursor.fetchall()
            
            if changes:
                headers = ["Connector", "Destination", "Table", "Change Type", "Timestamp"]
                print(tabulate(changes, headers=headers, tablefmt="grid"))
            else:
                print("No recent schema changes found.")
        except Exception as e:
            print(f"Error querying schema changes: {e}")
        
        # 5. Connector Health Alerts
        print("\n5. CONNECTOR HEALTH ALERTS")
        print("-" * 80)
        try:
            cursor.execute("""
                SELECT 
                    connector_name,
                    destination_name,
                    connector_type,
                    status,
                    last_successful_sync,
                    DATEDIFF('hour', last_successful_sync, CURRENT_TIMESTAMP()) as hours_since_last_sync,
                    sync_frequency
                FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS
                WHERE 
                    (DATEDIFF('hour', last_successful_sync, CURRENT_TIMESTAMP()) > sync_frequency * 2)
                    OR status != 'connected'
                ORDER BY hours_since_last_sync DESC
            """)
            alerts = cursor.fetchall()
            
            if alerts:
                headers = ["Connector", "Destination", "Type", "Status", "Last Sync", "Hours Since", "Frequency"]
                print("⚠️  The following connectors require attention:")
                print(tabulate(alerts, headers=headers, tablefmt="grid"))
            else:
                print("✅ All connectors are healthy!")
        except Exception as e:
            print(f"Error generating health alerts: {e}")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("Dashboard generated at", datetime.now())
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_dashboard()

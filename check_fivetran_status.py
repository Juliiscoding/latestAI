#!/usr/bin/env python3
"""
Check Fivetran connector status using the Fivetran metadata schema in Snowflake.
This script helps identify the status of Fivetran connectors and diagnose any issues
with data synchronization.
"""

import snowflake.connector
import getpass
from tabulate import tabulate
from datetime import datetime, timedelta
import sys

# Constants
ACCOUNT = 'VRXDFZX-ZZ95717'
USER = 'JULIUSRECHENBACH'
WAREHOUSE = 'COMPUTE_WH'
DATABASE = 'MERCURIOS_DATA'
SCHEMA = 'FIVETRAN_METADATA'

def connect_to_snowflake(role="ACCOUNTADMIN"):
    """Connect to Snowflake with the specified role."""
    try:
        # Get password securely
        password = getpass.getpass(f"Enter your Snowflake password: ")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            account=ACCOUNT,
            user=USER,
            password=password,
            warehouse=WAREHOUSE,
            database=DATABASE,
            role=role
        )
        
        print(f"✅ Successfully connected with role: {role}")
        
        # Get current role and user
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ROLE(), CURRENT_USER()")
        current_role, current_user = cursor.fetchone()
        print(f"Current role: {current_role}, Current user: {current_user}")
        
        return conn
    except Exception as e:
        print(f"❌ Failed to connect with role {role}: {str(e)}")
        return None

def check_fivetran_connectors(conn):
    """Check the status of Fivetran connectors."""
    if not conn:
        print("No connection available.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Try to use the Fivetran metadata schema
        cursor.execute(f"USE SCHEMA {DATABASE}.{SCHEMA}")
        print(f"✅ Successfully accessed schema: {SCHEMA}")
        
        # List all tables in the schema
        print("\nListing all tables in the Fivetran metadata schema...")
        cursor.execute(f"SHOW TABLES IN SCHEMA {DATABASE}.{SCHEMA}")
        tables = cursor.fetchall()
        if tables:
            print("Tables in Fivetran metadata schema:")
            for table in tables:
                print(f"- {table[1]}")
        
        # Get connector information
        print("\nFetching connector information...")
        cursor.execute(f"""
            SELECT 
                c.CONNECTOR_ID,
                c.CONNECTOR_NAME,
                c.CONNECTOR_TYPE_ID,
                c.DESTINATION_ID,
                c.SIGNED_UP,
                c.PAUSED,
                c.SYNC_FREQUENCY,
                c._FIVETRAN_SYNCED
            FROM {DATABASE}.{SCHEMA}.CONNECTOR c
            WHERE c._FIVETRAN_DELETED = FALSE
            ORDER BY c.SIGNED_UP DESC
        """)
        connectors = cursor.fetchall()
        
        if not connectors:
            print("No connectors found in the Fivetran metadata.")
            return
        
        # Display connector information
        connector_headers = [
            "Connector ID", "Name", "Type ID", "Destination ID", 
            "Signed Up", "Paused", "Sync Frequency", "Last Synced"
        ]
        print("\nConnector Information:")
        print(tabulate(connectors, headers=connector_headers, tablefmt="pretty"))
        
        # Get connector type information
        print("\nFetching connector type information...")
        cursor.execute(f"""
            SELECT 
                ct.CONNECTOR_TYPE_ID,
                ct.CONNECTOR_TYPE_NAME,
                ct.DATA_SOURCE_NAME
            FROM {DATABASE}.{SCHEMA}.CONNECTOR_TYPE ct
            ORDER BY ct.CONNECTOR_TYPE_NAME
        """)
        connector_types = cursor.fetchall()
        
        if connector_types:
            # Display connector type information
            connector_type_headers = [
                "Type ID", "Type Name", "Data Source Name"
            ]
            print("\nConnector Type Information:")
            print(tabulate(connector_types, headers=connector_type_headers, tablefmt="pretty"))
        
        # Check for logs
        print("\nChecking for connector logs...")
        cursor.execute(f"""
            SELECT 
                l.CONNECTOR_ID,
                c.CONNECTOR_NAME,
                l.CREATED_AT,
                l.MESSAGE,
                l.LEVEL
            FROM {DATABASE}.{SCHEMA}.LOG l
            JOIN {DATABASE}.{SCHEMA}.CONNECTOR c ON l.CONNECTOR_ID = c.CONNECTOR_ID
            WHERE l.LEVEL = 'ERROR'
            ORDER BY l.CREATED_AT DESC
            LIMIT 10
        """)
        logs = cursor.fetchall()
        
        if logs:
            # Display log information
            log_headers = [
                "Connector ID", "Connector Name", "Created At", "Message", "Level"
            ]
            print("\nRecent Error Logs:")
            print(tabulate(logs, headers=log_headers, tablefmt="pretty"))
        else:
            print("\nNo error logs found.")
    
    except Exception as e:
        print(f"❌ Error checking Fivetran connectors: {str(e)}")
    
    finally:
        cursor.close()

def check_fivetran_transformations(conn):
    """Check the status of Fivetran transformations."""
    if not conn:
        print("No connection available.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Try to use the Fivetran metadata schema
        cursor.execute(f"USE SCHEMA {DATABASE}.{SCHEMA}")
        
        # Check if transformation runs table exists
        cursor.execute(f"SHOW TABLES LIKE 'TRANSFORMATION_RUNS' IN SCHEMA {DATABASE}.{SCHEMA}")
        if not cursor.fetchone():
            print("❌ TRANSFORMATION_RUNS table not found in Fivetran metadata schema.")
            return
        
        # Get transformation run information
        print("\nFetching transformation run information...")
        cursor.execute(f"""
            SELECT 
                tr.ID,
                tr.TRANSFORMATION_ID,
                tr.STARTED_AT,
                tr.FINISHED_AT,
                tr.STATUS,
                tr.TRIGGER_ID,
                tr.TRIGGER_TYPE,
                tr.DESTINATION_ID,
                tr._FIVETRAN_SYNCED
            FROM {DATABASE}.{SCHEMA}.TRANSFORMATION_RUNS tr
            ORDER BY tr.STARTED_AT DESC
            LIMIT 10
        """)
        runs = cursor.fetchall()
        
        if not runs:
            print("No transformation runs found in the Fivetran metadata.")
            return
        
        # Display transformation run information
        run_headers = [
            "ID", "Transformation ID", "Started At", "Finished At", 
            "Status", "Trigger ID", "Trigger Type", "Destination ID", "Last Synced"
        ]
        print("\nTransformation Run Information:")
        print(tabulate(runs, headers=run_headers, tablefmt="pretty"))
    
    except Exception as e:
        print(f"❌ Error checking Fivetran transformations: {str(e)}")
    
    finally:
        cursor.close()

def main():
    """Main function to run the script."""
    print("Checking Fivetran connector status in Snowflake...")
    
    # Connect with ACCOUNTADMIN role
    conn = connect_to_snowflake("ACCOUNTADMIN")
    if conn:
        print("\n" + "=" * 80)
        print("CHECKING FIVETRAN CONNECTORS")
        print("=" * 80)
        check_fivetran_connectors(conn)
        
        print("\n" + "=" * 80)
        print("CHECKING FIVETRAN TRANSFORMATIONS")
        print("=" * 80)
        check_fivetran_transformations(conn)
        
        conn.close()
    else:
        print("Failed to connect to Snowflake. Exiting.")

if __name__ == "__main__":
    main()

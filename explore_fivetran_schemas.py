#!/usr/bin/env python3
"""
Explore Fivetran-managed schemas in Snowflake for Mercurios AI project.
This script attempts to access and explore Fivetran-managed schemas including
Google Analytics 4 and Klaviyo data.
"""

import snowflake.connector
import getpass
from tabulate import tabulate
import sys

# Constants
ACCOUNT = 'VRXDFZX-ZZ95717'
USER = 'JULIUSRECHENBACH'
WAREHOUSE = 'COMPUTE_WH'
DATABASE = 'MERCURIOS_DATA'

def connect_to_snowflake(role):
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

def explore_fivetran_schemas(conn, schemas_to_explore):
    """Explore Fivetran-managed schemas and their tables."""
    if not conn:
        print("No connection available.")
        return
    
    cursor = conn.cursor()
    
    # Try to access each schema and list tables
    for schema in schemas_to_explore:
        print(f"\n{'=' * 80}")
        print(f"EXPLORING SCHEMA: {schema}")
        print(f"{'=' * 80}")
        
        try:
            # Try to use the schema
            cursor.execute(f"USE SCHEMA {DATABASE}.{schema}")
            print(f"✅ Successfully accessed schema: {schema}")
            
            # List tables in the schema
            cursor.execute(f"SHOW TABLES IN SCHEMA {DATABASE}.{schema}")
            tables = cursor.fetchall()
            
            if tables:
                print(f"Tables in {schema}:")
                table_data = []
                for table in tables:
                    table_name = table[1]
                    # Get row count for the table
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {DATABASE}.{schema}.{table_name}")
                        row_count = cursor.fetchone()[0]
                    except Exception as e:
                        row_count = f"Error: {str(e)}"
                    
                    # Get column information
                    try:
                        cursor.execute(f"DESCRIBE TABLE {DATABASE}.{schema}.{table_name}")
                        columns = cursor.fetchall()
                        column_count = len(columns)
                        sample_columns = ", ".join([col[0] for col in columns[:5]])
                        if column_count > 5:
                            sample_columns += f", ... ({column_count-5} more)"
                    except Exception as e:
                        column_count = "Error"
                        sample_columns = str(e)
                    
                    table_data.append([table_name, row_count, column_count, sample_columns])
                
                print(tabulate(table_data, headers=["Table Name", "Row Count", "Column Count", "Sample Columns"], tablefmt="pretty"))
                
                # For GA4 schema, explore event data if available
                if schema == "GOOGLE_ANALYTICS_4" and any(t[0] == "EVENTS" for t in table_data):
                    try:
                        print("\nExploring GA4 event data:")
                        cursor.execute("""
                            SELECT event_name, COUNT(*) as event_count
                            FROM MERCURIOS_DATA.GOOGLE_ANALYTICS_4.EVENTS
                            GROUP BY event_name
                            ORDER BY event_count DESC
                            LIMIT 10
                        """)
                        events = cursor.fetchall()
                        if events:
                            print(tabulate(events, headers=["Event Name", "Count"], tablefmt="pretty"))
                    except Exception as e:
                        print(f"Could not explore GA4 events: {str(e)}")
                
                # For Klaviyo schema, explore metrics if available
                if schema == "KLAVIYO" and any(t[0] == "METRICS" for t in table_data):
                    try:
                        print("\nExploring Klaviyo metrics:")
                        cursor.execute("""
                            SELECT name, integration_name, COUNT(*) as metric_count
                            FROM MERCURIOS_DATA.KLAVIYO.METRICS
                            GROUP BY name, integration_name
                            ORDER BY metric_count DESC
                            LIMIT 10
                        """)
                        metrics = cursor.fetchall()
                        if metrics:
                            print(tabulate(metrics, headers=["Metric Name", "Integration", "Count"], tablefmt="pretty"))
                    except Exception as e:
                        print(f"Could not explore Klaviyo metrics: {str(e)}")
            else:
                print(f"No tables found in {schema}")
                
        except Exception as e:
            print(f"❌ Failed to access schema {schema}: {str(e)}")
    
    cursor.close()

def main():
    """Main function to run the script."""
    print("Exploring Fivetran-managed schemas in Snowflake...")
    
    # Try with different roles
    roles_to_try = ["ACCOUNTADMIN", "MERCURIOS_ADMIN"]
    schemas_to_explore = [
        "GOOGLE_ANALYTICS_4", 
        "KLAVIYO", 
        "FIVETRAN_ARMED_UNLEADED_STAGING",
        "FIVETRAN_METADATA"
    ]
    
    for role in roles_to_try:
        print(f"\n{'=' * 80}")
        print(f"ATTEMPTING WITH ROLE: {role}")
        print(f"{'=' * 80}")
        
        conn = connect_to_snowflake(role)
        if conn:
            explore_fivetran_schemas(conn, schemas_to_explore)
            conn.close()
            
            # Ask if user wants to continue with next role
            if role != roles_to_try[-1]:
                continue_prompt = input(f"\nContinue with next role ({roles_to_try[roles_to_try.index(role) + 1]})? (y/n): ")
                if continue_prompt.lower() != 'y':
                    break
        else:
            print(f"Skipping exploration with role {role} due to connection failure.")

if __name__ == "__main__":
    main()

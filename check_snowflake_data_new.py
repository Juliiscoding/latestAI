#!/usr/bin/env python3
"""
Script to check Snowflake data from the ProHandel API connector
"""

import os
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from tabulate import tabulate
import getpass
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Snowflake connection parameters
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USERNAME') or os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', 'MERCURIOS_LOADING_WH')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'MERCURIOS_DATA')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'ANALYTICS')

# ProHandel table names to look for
PROHANDEL_TABLES = [
    'ARTICLE', 'CUSTOMER', 'ORDER', 'SALE', 'INVENTORY', 'SHOP',
    'DAILY_SALES_AGG', 'ARTICLE_SALES_AGG', 'WAREHOUSE_INVENTORY_AGG'
]

# Fivetran schemas to check
FIVETRAN_SCHEMAS = [
    'FIVETRAN_ARMED_UNLEADED_STAGING',  # Default Fivetran staging schema
    'FIVETRAN_ARMED_UNLEADED',          # Default Fivetran schema
    'PROHANDEL',                        # Custom schema for ProHandel data
    'RAW_PROHANDEL'                     # Another possible schema name
]

def prompt_for_credentials():
    """Prompt for Snowflake credentials if not found in environment"""
    global SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE
    
    if not SNOWFLAKE_ACCOUNT:
        SNOWFLAKE_ACCOUNT = input("Enter Snowflake account (e.g., xy12345.us-east-1): ")
    
    if not SNOWFLAKE_USER:
        SNOWFLAKE_USER = input("Enter Snowflake username: ")
    
    if not SNOWFLAKE_PASSWORD:
        SNOWFLAKE_PASSWORD = getpass.getpass("Enter Snowflake password: ")
    
    if not SNOWFLAKE_WAREHOUSE:
        SNOWFLAKE_WAREHOUSE = input("Enter Snowflake warehouse (default: MERCURIOS_LOADING_WH): ") or "MERCURIOS_LOADING_WH"
    
    if not SNOWFLAKE_DATABASE:
        SNOWFLAKE_DATABASE = input("Enter Snowflake database (default: MERCURIOS_DATA): ") or "MERCURIOS_DATA"

def connect_to_snowflake():
    """Connect to Snowflake and return the connection"""
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )
        print(f"Connected to Snowflake: {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}")
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {str(e)}")
        return None

def list_schemas(conn):
    """List all schemas in the database"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SHOW SCHEMAS IN {SNOWFLAKE_DATABASE}")
        schemas = cursor.fetchall()
        
        if not schemas:
            print(f"No schemas found in {SNOWFLAKE_DATABASE}")
            return []
        
        # Extract schema names
        schema_names = [row[1] for row in schemas]
        print(f"Found {len(schema_names)} schemas in {SNOWFLAKE_DATABASE}:")
        for schema in schema_names:
            print(f"  - {schema}")
        
        return schema_names
    except Exception as e:
        print(f"Error listing schemas: {str(e)}")
        return []

def check_table_data(conn, schema, table_name, limit=5):
    """Check data in a specific table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {SNOWFLAKE_DATABASE}.{schema}.{table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No data found in {schema}.{table_name}")
            return
        
        # Get column names
        column_names = [desc[0] for desc in cursor.description]
        
        # Create a DataFrame for better display
        df = pd.DataFrame(rows, columns=column_names)
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        
    except Exception as e:
        print(f"Error checking table data: {str(e)}")

def check_table_structure(conn, schema, table_name):
    """Check the structure of a specific table"""
    try:
        print(f"\n=== Structure of {schema}.{table_name} ===")
        
        # Get column information
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE TABLE {SNOWFLAKE_DATABASE}.{schema}.{table_name}")
        columns = cursor.fetchall()
        
        if not columns:
            print(f"No column information available for {schema}.{table_name}")
            return
        
        # Create a DataFrame with column information
        column_df = pd.DataFrame(columns, columns=['name', 'type', 'kind', 'null', 'default', 'primary_key', 'unique_key', 'check', 'expression', 'comment'])
        print(tabulate(column_df[['name', 'type', 'null', 'default']], headers='keys', tablefmt='psql', showindex=False))
        
    except Exception as e:
        print(f"Error checking table structure: {str(e)}")

def check_fivetran_sync_status(conn):
    """Check Fivetran sync status from metadata tables"""
    print("\n=== Checking Fivetran Sync Status ===")
    
    # Schemas where Fivetran metadata might be stored
    metadata_schemas = ['FIVETRAN_LOG', 'INFORMATION_SCHEMA']
    connector_found = False
    
    for schema in metadata_schemas:
        try:
            # Check if the schema exists
            cursor = conn.cursor()
            cursor.execute(f"SHOW SCHEMAS LIKE '{schema}' IN {SNOWFLAKE_DATABASE}")
            schema_exists = cursor.fetchone()
            
            if not schema_exists:
                print(f"Schema {schema} does not exist in {SNOWFLAKE_DATABASE}")
                continue
            
            print(f"Checking Fivetran metadata in {schema}...")
            
            # Check for connector information
            try:
                cursor.execute(f"""
                    SELECT * FROM {SNOWFLAKE_DATABASE}.{schema}.CONNECTORS 
                    WHERE CONNECTOR_NAME LIKE '%PROHANDEL%' OR CONNECTOR_ID LIKE '%ARMED_UNLEADED%'
                """)
                connectors = cursor.fetchall()
                
                if connectors:
                    connector_found = True
                    print(f"Found {len(connectors)} ProHandel connectors:")
                    
                    # Get column names
                    column_names = [desc[0] for desc in cursor.description]
                    
                    # Create a DataFrame for better display
                    connector_df = pd.DataFrame(connectors, columns=column_names)
                    print(tabulate(connector_df, headers='keys', tablefmt='psql', showindex=False))
                    
                    # Check sync logs for each connector
                    for connector in connectors:
                        connector_id = connector[column_names.index('CONNECTOR_ID')]
                        print(f"\nChecking sync logs for connector: {connector_id}")
                        
                        try:
                            cursor.execute(f"""
                                SELECT * FROM {SNOWFLAKE_DATABASE}.{schema}.SYNC_LOGS 
                                WHERE CONNECTOR_ID = '{connector_id}'
                                ORDER BY CREATED DESC
                                LIMIT 5
                            """)
                            logs = cursor.fetchall()
                            
                            if logs:
                                # Get column names
                                log_column_names = [desc[0] for desc in cursor.description]
                                
                                # Create a DataFrame for better display
                                log_df = pd.DataFrame(logs, columns=log_column_names)
                                print(tabulate(log_df, headers='keys', tablefmt='psql', showindex=False))
                            else:
                                print("No recent sync logs found for this connector")
                        except Exception as e:
                            print(f"Error querying sync logs: {str(e)}")
                else:
                    print("No ProHandel connectors found in Fivetran metadata")
            except Exception as e:
                print(f"Error querying connectors: {str(e)}")
        except Exception as e:
            print(f"Error checking Fivetran metadata in {schema}: {str(e)}")
    
    if not connector_found:
        print("No ProHandel connectors found in Fivetran metadata tables.")
        print("This could mean the connector hasn't been fully set up yet or the metadata tables haven't been populated.")

def check_prohandel_lambda_data(conn):
    """Specifically check for ProHandel data loaded through the Lambda connector"""
    print("\n=== Checking for ProHandel Data from Lambda Connector ===")
    
    # Check each schema for ProHandel tables
    found_tables = []
    for schema in FIVETRAN_SCHEMAS:
        try:
            # First check if the schema exists
            cursor = conn.cursor()
            cursor.execute(f"SHOW SCHEMAS LIKE '{schema}' IN {SNOWFLAKE_DATABASE}")
            schema_exists = cursor.fetchone()
            
            if not schema_exists:
                print(f"❌ Schema {schema} does not exist in {SNOWFLAKE_DATABASE}")
                continue
                
            print(f"\n✅ Found schema: {schema}")
            
            # Check for each ProHandel table
            for table in PROHANDEL_TABLES:
                try:
                    cursor = conn.cursor()
                    query = f"SELECT COUNT(*) FROM {SNOWFLAKE_DATABASE}.{schema}.{table}"
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        found_tables.append((schema, table, count))
                        print(f"  ✅ Found {count} rows in {schema}.{table}")
                    else:
                        print(f"  ⚠️ Table {schema}.{table} exists but has no data")
                        
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        print(f"  ❌ Table {schema}.{table} does not exist")
                    else:
                        print(f"  ❌ Error checking {schema}.{table}: {str(e)}")
        except Exception as e:
            print(f"❌ Error checking schema {schema}: {str(e)}")
    
    return found_tables

def main():
    """Main function"""
    print("=== Checking Snowflake Data from ProHandel API ===")
    
    # Prompt for credentials if needed
    if not all([SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD]):
        prompt_for_credentials()
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    if not conn:
        return
    
    try:
        # List all schemas in the database
        print("\n=== Available Schemas ===")
        schemas = list_schemas(conn)
        if not schemas:
            print("No schemas found. Cannot proceed.")
            return
        
        # Check specifically for ProHandel data from Lambda
        found_tables = check_prohandel_lambda_data(conn)
        
        # If we found tables with data, offer to show samples
        if found_tables:
            print("\n=== ProHandel Tables with Data ===")
            for schema, table, count in found_tables:
                print(f"{schema}.{table}: {count} rows")
            
            # Check Fivetran sync status
            print("\n=== Checking Fivetran Sync Status ===")
            check_fivetran_sync_status(conn)
            
            # Ask if user wants to see sample data
            check_samples = input("\nDo you want to see sample data from these tables? (y/n): ").lower()
            if check_samples == 'y':
                for schema, table, _ in found_tables:
                    print(f"\n=== Sample Data from {schema}.{table} ===")
                    check_table_data(conn, schema, table, 5)
                    check_table_structure(conn, schema, table)
        else:
            print("\n⚠️ No ProHandel data found in Snowflake. The Lambda connector may not have run successfully.")
            
            # Check Fivetran sync status
            print("\n=== Checking Fivetran Sync Status ===")
            check_fivetran_sync_status(conn)
    finally:
        conn.close()
        print("\nSnowflake connection closed.")

if __name__ == "__main__":
    main()

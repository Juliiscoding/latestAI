#!/usr/bin/env python
"""
Check AWS Lambda Data - Mercurios.ai
This script specifically checks for data from the AWS Lambda connector
that brings in ProHandel API data.
"""

import os
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from tabulate import tabulate

# Load environment variables
load_dotenv()

# Snowflake connection parameters
snowflake_params = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'user': os.getenv('SNOWFLAKE_USERNAME'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
    'database': os.getenv('SNOWFLAKE_DATABASE'),
    'role': os.getenv('SNOWFLAKE_ROLE')
}

def connect_to_snowflake():
    """Establish connection to Snowflake."""
    print(f"Connecting to Snowflake with:")
    print(f"  Account: {snowflake_params['account']}")
    print(f"  User: {snowflake_params['user']}")
    print(f"  Warehouse: {snowflake_params['warehouse']}")
    print(f"  Database: {snowflake_params['database']}")
    print(f"  Role: {snowflake_params['role']}")
    
    try:
        conn = snowflake.connector.connect(
            **snowflake_params
        )
        print("Successfully connected to Snowflake!")
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        return None

def run_query(conn, query):
    """Execute a query and return results as a pandas DataFrame."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=columns)
        cursor.close()
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def find_aws_lambda_schemas(conn):
    """Find schemas that might contain AWS Lambda data."""
    query = """
    SELECT SCHEMA_NAME 
    FROM INFORMATION_SCHEMA.SCHEMATA
    WHERE SCHEMA_NAME LIKE '%AWS%' 
       OR SCHEMA_NAME LIKE '%LAMBDA%'
       OR SCHEMA_NAME LIKE '%PROHANDEL%'
       OR SCHEMA_NAME LIKE '%ARMED_UNLEADED%'
    ORDER BY SCHEMA_NAME
    """
    return run_query(conn, query)

def find_tables_in_schema(conn, schema):
    """Find tables in a specific schema."""
    query = f"""
    SELECT TABLE_NAME, ROW_COUNT
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = '{schema}'
    ORDER BY TABLE_NAME
    """
    return run_query(conn, query)

def find_all_tables(conn):
    """Find all tables in the database."""
    query = """
    SELECT TABLE_SCHEMA, TABLE_NAME, ROW_COUNT
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    return run_query(conn, query)

def check_fivetran_connections(conn):
    """Check Fivetran connection metadata."""
    query = """
    SELECT 
        c.CONNECTOR_NAME,
        c.CONNECTOR_TYPE,
        c.CREATED_AT,
        c.SUCCEEDED_AT,
        c.FAILED_AT,
        c.SYNC_FREQUENCY,
        c.STATUS
    FROM FIVETRAN_METADATA.CONNECTION c
    ORDER BY c.CONNECTOR_TYPE
    """
    try:
        return run_query(conn, query)
    except:
        print("Could not find Fivetran metadata tables. Trying alternative approach...")
        return None

def check_fivetran_schema_changes(conn):
    """Check schema changes for AWS Lambda connector."""
    query = """
    SELECT 
        s.CONNECTOR_ID,
        c.CONNECTOR_NAME,
        s.SCHEMA_NAME,
        s.CREATED_AT,
        s.SUCCEEDED_AT
    FROM FIVETRAN_METADATA.DESTINATION_SCHEMA_CHANGE_EVENT s
    JOIN FIVETRAN_METADATA.CONNECTION c ON s.CONNECTOR_ID = c.ID
    WHERE c.CONNECTOR_TYPE = 'aws_lambda'
    ORDER BY s.CREATED_AT DESC
    """
    try:
        return run_query(conn, query)
    except:
        print("Could not find Fivetran schema change events. Trying alternative approach...")
        return None

def search_for_prohandel_data(conn):
    """Search for any tables that might contain ProHandel data."""
    print("\n=== Searching for tables with ProHandel-related names ===")
    query = """
    SELECT TABLE_SCHEMA, TABLE_NAME, ROW_COUNT
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA LIKE '%ARMED_UNLEADED%'
       OR TABLE_NAME LIKE '%PROHANDEL%'
       OR TABLE_NAME LIKE '%PRO_HANDEL%'
       OR TABLE_NAME LIKE '%ARTICLE%'
       OR TABLE_NAME LIKE '%PRODUCT%'
       OR TABLE_NAME LIKE '%INVENTORY%'
       OR TABLE_NAME LIKE '%STOCK%'
    ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    return run_query(conn, query)

def check_fivetran_armed_unleaded_schema(conn):
    """Check the FIVETRAN_ARMED_UNLEADED_STAGING schema specifically."""
    print("\n=== Checking FIVETRAN_ARMED_UNLEADED_STAGING schema ===")
    query = """
    SELECT TABLE_NAME, ROW_COUNT
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'FIVETRAN_ARMED_UNLEADED_STAGING'
    ORDER BY TABLE_NAME
    """
    return run_query(conn, query)

def sample_table_data(conn, schema, table):
    """Sample data from a specific table."""
    print(f"\n=== Sample data from {schema}.{table} ===")
    query = f"""
    SELECT *
    FROM {schema}.{table}
    LIMIT 5
    """
    return run_query(conn, query)

def main():
    """Main function to run the script."""
    conn = connect_to_snowflake()
    if not conn:
        return
    
    try:
        # Find AWS Lambda related schemas
        print("\n=== AWS Lambda Related Schemas ===")
        schemas_df = find_aws_lambda_schemas(conn)
        print(tabulate(schemas_df, headers='keys', tablefmt='psql'))
        
        # Check Fivetran connections
        print("\n=== Fivetran Connections ===")
        connections_df = check_fivetran_connections(conn)
        if connections_df is not None:
            print(tabulate(connections_df, headers='keys', tablefmt='psql'))
        
        # Check Fivetran schema changes for AWS Lambda
        print("\n=== Fivetran Schema Changes for AWS Lambda ===")
        schema_changes_df = check_fivetran_schema_changes(conn)
        if schema_changes_df is not None:
            print(tabulate(schema_changes_df, headers='keys', tablefmt='psql'))
        
        # Search for ProHandel data
        prohandel_tables_df = search_for_prohandel_data(conn)
        if prohandel_tables_df is not None and not prohandel_tables_df.empty:
            print(tabulate(prohandel_tables_df, headers='keys', tablefmt='psql'))
        else:
            print("No tables found with ProHandel-related names.")
        
        # Check the FIVETRAN_ARMED_UNLEADED_STAGING schema
        armed_unleaded_df = check_fivetran_armed_unleaded_schema(conn)
        if armed_unleaded_df is not None and not armed_unleaded_df.empty:
            print(tabulate(armed_unleaded_df, headers='keys', tablefmt='psql'))
            
            # Sample data from the first table in this schema
            if len(armed_unleaded_df) > 0:
                first_table = armed_unleaded_df.iloc[0]['TABLE_NAME']
                sample_df = sample_table_data(conn, 'FIVETRAN_ARMED_UNLEADED_STAGING', first_table)
                if sample_df is not None:
                    print(tabulate(sample_df, headers='keys', tablefmt='psql'))
        
    finally:
        conn.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()

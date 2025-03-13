#!/usr/bin/env python3
"""
Script to check if ProHandel data has been successfully loaded into Snowflake
"""

import os
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from tabulate import tabulate

# Load environment variables
load_dotenv()

# Snowflake connection parameters
snowflake_params = {
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
    'database': os.getenv('SNOWFLAKE_DATABASE', 'MERCURIOS'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'AWS_LAMBDA')
}

def connect_to_snowflake():
    """Connect to Snowflake and return the connection"""
    try:
        conn = snowflake.connector.connect(
            user=snowflake_params['user'],
            password=snowflake_params['password'],
            account=snowflake_params['account'],
            warehouse=snowflake_params['warehouse'],
            database=snowflake_params['database']
            # Don't specify schema yet to check available schemas
        )
        print(f"Connected to Snowflake: {snowflake_params['account']} - {snowflake_params['database']}")
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {str(e)}")
        return None

def list_schemas(conn):
    """List all schemas in the database"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SHOW SCHEMAS IN {snowflake_params['database']}")
        schemas = cursor.fetchall()
        
        if not schemas:
            print(f"No schemas found in {snowflake_params['database']}")
            return []
        
        schema_names = [schema[1] for schema in schemas]
        print(f"\nFound {len(schema_names)} schemas in database {snowflake_params['database']}:")
        for schema in schema_names:
            print(f"  - {schema}")
        
        return schema_names
    except Exception as e:
        print(f"Error listing schemas: {str(e)}")
        return []

def check_tables(conn, schema=None):
    """Check which tables exist in a specific schema"""
    try:
        schema_to_use = schema or snowflake_params['schema']
        cursor = conn.cursor()
        cursor.execute(f"SHOW TABLES IN {snowflake_params['database']}.{schema_to_use}")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"No tables found in {snowflake_params['database']}.{schema_to_use}")
            return []
        
        table_names = [table[1] for table in tables]
        print(f"\nFound {len(table_names)} tables in schema {schema_to_use}:")
        for table in table_names:
            print(f"  - {table}")
        
        return table_names
    except Exception as e:
        print(f"Error checking tables in schema {schema_to_use}: {str(e)}")
        return []

def check_table_data(conn, table_name, schema=None):
    """Check data in a specific table"""
    try:
        schema_to_use = schema or snowflake_params['schema']
        cursor = conn.cursor()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {snowflake_params['database']}.{schema_to_use}.{table_name}")
        row_count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {snowflake_params['database']}.{schema_to_use}.{table_name} LIMIT 5")
        sample_data = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"DESCRIBE TABLE {snowflake_params['database']}.{schema_to_use}.{table_name}")
        columns = [col[0] for col in cursor.fetchall()]
        
        print(f"\nTable: {schema_to_use}.{table_name}")
        print(f"  - Row count: {row_count}")
        print(f"  - Columns: {len(columns)}")
        
        if sample_data:
            print("\nSample data:")
            df = pd.DataFrame(sample_data, columns=columns)
            print(tabulate(df.head(), headers='keys', tablefmt='psql'))
        
        # Check if tenant_id column exists
        if 'TENANT_ID' in [col.upper() for col in columns]:
            print("\n✅ Table includes tenant_id column for multi-tenant support")
        else:
            print("\n❌ Table does not include tenant_id column")
        
        return row_count
    except Exception as e:
        print(f"Error checking table data for {schema_to_use}.{table_name}: {str(e)}")
        return 0

def main():
    """Main function"""
    print("=== Checking ProHandel Data in Snowflake ===")
    
    conn = connect_to_snowflake()
    if not conn:
        return
    
    try:
        # List all schemas in the database
        schemas = list_schemas(conn)
        
        # Expected tables from ProHandel
        expected_tables = ['ARTICLES', 'CUSTOMERS', 'ORDERS', 'SALES', 'INVENTORY', 'SUPPLIERS']
        found_prohandel_tables = {}
        
        # Check each schema for ProHandel tables
        print("\n=== Searching for ProHandel tables across all schemas ===")
        for schema in schemas:
            tables = check_tables(conn, schema)
            
            # Check if any of the expected tables exist in this schema
            prohandel_tables = [table for table in tables if table.upper() in expected_tables]
            if prohandel_tables:
                print(f"\n✅ Found ProHandel tables in schema: {schema}")
                found_prohandel_tables[schema] = prohandel_tables
        
        if not found_prohandel_tables:
            print("\n❌ No ProHandel tables found in any schema. The Fivetran sync may not have completed yet.")
            print("\nPossible reasons:")
            print("  1. The Fivetran sync has not run yet - try clicking 'SYNC NOW' in the Fivetran UI")
            print("  2. The Lambda function is not returning data correctly")
            print("  3. There might be permission issues with the Fivetran service account")
            return
        
        # Check data in each found ProHandel table
        print("\n=== Checking ProHandel table data ===")
        total_rows = 0
        for schema, tables in found_prohandel_tables.items():
            print(f"\nExamining tables in schema: {schema}")
            for table in tables:
                rows = check_table_data(conn, table, schema)
                total_rows += rows
        
        print(f"\nTotal rows across all ProHandel tables: {total_rows}")
        
        if total_rows > 0:
            print("\n✅ ProHandel data has been successfully loaded into Snowflake!")
        else:
            print("\n❌ ProHandel tables exist but contain no data. Check Fivetran sync status.")
    
    finally:
        conn.close()
        print("\nSnowflake connection closed")

if __name__ == "__main__":
    main()

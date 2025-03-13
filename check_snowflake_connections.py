#!/usr/bin/env python3
"""
Script to check all available data and connections in Snowflake
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

def list_databases(conn):
    """List all databases"""
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        if not databases:
            print("No databases found")
            return []
        
        # Extract database names
        database_names = [row[1] for row in databases]
        print(f"Found {len(database_names)} databases:")
        for db in database_names:
            print(f"  - {db}")
        
        return database_names
    except Exception as e:
        print(f"Error listing databases: {str(e)}")
        return []

def list_schemas(conn, database=None):
    """List all schemas in the database"""
    try:
        cursor = conn.cursor()
        db_name = database or SNOWFLAKE_DATABASE
        cursor.execute(f"SHOW SCHEMAS IN {db_name}")
        schemas = cursor.fetchall()
        
        if not schemas:
            print(f"No schemas found in {db_name}")
            return []
        
        # Extract schema names
        schema_names = [row[1] for row in schemas]
        print(f"Found {len(schema_names)} schemas in {db_name}:")
        for schema in schema_names:
            print(f"  - {schema}")
        
        return schema_names
    except Exception as e:
        print(f"Error listing schemas: {str(e)}")
        return []

def list_tables_in_schema(conn, schema, database=None):
    """List all tables in a schema"""
    try:
        cursor = conn.cursor()
        db_name = database or SNOWFLAKE_DATABASE
        cursor.execute(f"SHOW TABLES IN {db_name}.{schema}")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"No tables found in {db_name}.{schema}")
            return []
        
        # Extract table names and other info
        table_info = []
        for row in tables:
            table_name = row[1]
            table_type = row[3]
            created_on = row[5]
            table_info.append((table_name, table_type, created_on))
        
        print(f"Found {len(table_info)} tables in {db_name}.{schema}:")
        
        # Create a DataFrame for better display
        table_df = pd.DataFrame(table_info, columns=['Table Name', 'Table Type', 'Created On'])
        print(tabulate(table_df, headers='keys', tablefmt='psql', showindex=False))
        
        return [t[0] for t in table_info]
    except Exception as e:
        print(f"Error listing tables in {schema}: {str(e)}")
        return []

def check_table_row_count(conn, schema, table, database=None):
    """Check the row count of a table"""
    try:
        cursor = conn.cursor()
        db_name = database or SNOWFLAKE_DATABASE
        
        # Use double quotes to handle case sensitivity
        query = f'SELECT COUNT(*) FROM "{db_name}"."{schema}"."{table}"'
        cursor.execute(query)
        count = cursor.fetchone()[0]
        
        return count
    except Exception as e:
        print(f"Error counting rows in {schema}.{table}: {str(e)}")
        return 0

def check_fivetran_metadata(conn):
    """Check for Fivetran metadata and connections"""
    print("\n=== Checking for Fivetran Metadata ===")
    
    # Known Fivetran metadata schemas
    metadata_schemas = ['FIVETRAN_LOG', 'FIVETRAN_METADATA', 'FIVETRAN_METADATA_FIVETRAN_PLATFORM']
    
    found_connectors = []
    
    for schema in metadata_schemas:
        try:
            # Check if schema exists
            cursor = conn.cursor()
            cursor.execute(f"SHOW SCHEMAS LIKE '{schema}' IN {SNOWFLAKE_DATABASE}")
            schema_exists = cursor.fetchone()
            
            if not schema_exists:
                print(f"Schema {schema} does not exist in {SNOWFLAKE_DATABASE}")
                continue
                
            print(f"\nChecking Fivetran metadata in {schema}...")
            
            # List tables in the schema
            tables = list_tables_in_schema(conn, schema)
            
            # Look for connector-related tables
            connector_tables = [t for t in tables if 'CONNECTOR' in t.upper()]
            
            for table in connector_tables:
                try:
                    cursor = conn.cursor()
                    cursor.execute(f'SELECT * FROM "{SNOWFLAKE_DATABASE}"."{schema}"."{table}" LIMIT 10')
                    rows = cursor.fetchall()
                    
                    if rows:
                        # Get column names
                        column_names = [desc[0] for desc in cursor.description]
                        
                        # Create a DataFrame for better display
                        df = pd.DataFrame(rows, columns=column_names)
                        print(f"\n=== Connector data from {schema}.{table} ===")
                        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                        
                        # Add to found connectors
                        for row in rows:
                            connector_info = {}
                            for i, col in enumerate(column_names):
                                connector_info[col] = row[i]
                            found_connectors.append(connector_info)
                except Exception as e:
                    print(f"Error querying {schema}.{table}: {str(e)}")
        except Exception as e:
            print(f"Error checking schema {schema}: {str(e)}")
    
    return found_connectors

def check_external_connections(conn):
    """Check for external data connections (Google Analytics, Shopify, Klaviyo, etc.)"""
    print("\n=== Checking for External Data Connections ===")
    
    # Known external data schemas
    external_schemas = [
        'GOOGLE_ANALYTICS_4', 
        'SHOPIFY', 'SHOPIFY_SHOPIFY', 'SHOPIFY_STG_SHOPIFY',
        'KLAVIYO', 'KLAVIYO_KLAVIYO', 'KLAVIYO_STG_KLAVIYO'
    ]
    
    for schema in external_schemas:
        try:
            # Check if schema exists
            cursor = conn.cursor()
            cursor.execute(f"SHOW SCHEMAS LIKE '{schema}' IN {SNOWFLAKE_DATABASE}")
            schema_exists = cursor.fetchone()
            
            if not schema_exists:
                print(f"Schema {schema} does not exist in {SNOWFLAKE_DATABASE}")
                continue
                
            print(f"\n=== Found external data schema: {schema} ===")
            
            # List tables in the schema
            tables = list_tables_in_schema(conn, schema)
            
            # Check row counts for up to 5 tables
            if tables:
                print("\nSample table row counts:")
                for table in tables[:5]:
                    count = check_table_row_count(conn, schema, table)
                    print(f"  - {schema}.{table}: {count} rows")
                
                # Show sample data from the first table
                if tables:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(f'SELECT * FROM "{SNOWFLAKE_DATABASE}"."{schema}"."{tables[0]}" LIMIT 5')
                        rows = cursor.fetchall()
                        
                        if rows:
                            # Get column names
                            column_names = [desc[0] for desc in cursor.description]
                            
                            # Create a DataFrame for better display
                            df = pd.DataFrame(rows, columns=column_names)
                            print(f"\n=== Sample data from {schema}.{tables[0]} ===")
                            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                    except Exception as e:
                        print(f"Error querying sample data: {str(e)}")
        except Exception as e:
            print(f"Error checking schema {schema}: {str(e)}")

def main():
    """Main function"""
    print("=== Checking Snowflake Data Connections ===")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Prompt for credentials if needed
    if not all([SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD]):
        prompt_for_credentials()
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    if not conn:
        return
    
    try:
        # List databases
        print("\n=== Available Databases ===")
        databases = list_databases(conn)
        
        # List schemas in the current database
        print(f"\n=== Schemas in {SNOWFLAKE_DATABASE} ===")
        schemas = list_schemas(conn)
        
        # Check for Fivetran metadata
        fivetran_connectors = check_fivetran_metadata(conn)
        
        # Check for external data connections
        check_external_connections(conn)
        
        # Summary
        print("\n=== Summary ===")
        print(f"Total databases: {len(databases)}")
        print(f"Total schemas in {SNOWFLAKE_DATABASE}: {len(schemas)}")
        print(f"Found {len(fivetran_connectors)} Fivetran connectors")
        
        # List all schemas and their table counts
        print("\n=== All Schemas and Table Counts ===")
        for schema in schemas:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.{schema}")
                tables = cursor.fetchall()
                print(f"  - {schema}: {len(tables)} tables")
            except Exception as e:
                print(f"  - {schema}: Error counting tables - {str(e)}")
    finally:
        conn.close()
        print("\nSnowflake connection closed.")

if __name__ == "__main__":
    main()

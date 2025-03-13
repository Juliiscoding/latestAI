#!/usr/bin/env python3
"""
Script to check Snowflake data from the ProHandel API connector
"""

import os
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from tabulate import tabulate

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
        import getpass
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

def search_for_prohandel_tables(conn, schemas):
    """Search for ProHandel tables across all schemas"""
    prohandel_tables = []
    prohandel_schemas = []
    
    # List of table names we're looking for (case insensitive)
    target_tables = [
        'ARTICLES', 'CUSTOMERS', 'ORDERS', 'ORDER_ITEMS', 'SALES', 'SALE_ITEMS', 
        'INVENTORY', 'SUPPLIERS', 'BRANCHES', 'CATEGORIES', 'COUNTRIES', 
        'CREDITS', 'CURRENCIES', 'INVOICES', 'LABELS', 'PAYMENTS', 'STAFF', 'VOUCHERS'
    ]
    target_tables_lower = [t.lower() for t in target_tables]
    
    print("\nSearching for ProHandel tables across all schemas...")
    
    for schema in schemas:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.{schema}")
            tables = cursor.fetchall()
            
            if not tables:
                continue
            
            # Check if any of the tables match our target tables
            for row in tables:
                table_name = row[1]
                if table_name.lower() in target_tables_lower or 'prohandel' in table_name.lower():
                    prohandel_tables.append((schema, table_name))
                    if schema not in prohandel_schemas:
                        prohandel_schemas.append(schema)
        except Exception as e:
            print(f"Error checking schema {schema}: {str(e)}")
    
    if prohandel_tables:
        print(f"\nFound {len(prohandel_tables)} ProHandel-related tables:")
        for schema, table in prohandel_tables:
            print(f"  - {schema}.{table}")
        
        print(f"\nProHandel data appears to be in these schemas: {', '.join(prohandel_schemas)}")
    else:
        print("\nNo ProHandel-related tables found in any schema.")
        print("This suggests that the Fivetran sync may not have completed yet or there might be an issue with the connector.")
    
    return prohandel_tables

def check_table_data(conn, schema, table_name, limit=5):
    """Check data in a specific table"""
    try:
        print(f"\n=== Data in {schema}.{table_name} (top {limit} rows) ===")
        
        # Get row count
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {SNOWFLAKE_DATABASE}.{schema}.{table_name}")
        count = cursor.fetchone()[0]
        print(f"Total rows: {count}")
        
        if count == 0:
            print(f"No data in table {schema}.{table_name}")
            return
        
        # Get sample data
        query = f"SELECT * FROM {SNOWFLAKE_DATABASE}.{schema}.{table_name} LIMIT {limit}"
        df = pd.read_sql(query, conn)
        
        # Display sample data
        print(tabulate(df, headers='keys', tablefmt='psql'))
        
    except Exception as e:
        print(f"Error checking table data: {str(e)}")

def check_fivetran_sync_status(conn):
    """Check Fivetran sync status from metadata tables"""
    print("\n=== Checking Fivetran Sync Status ===\n")
    
    # Try different possible locations for Fivetran metadata
    metadata_schemas = ['FIVETRAN_METADATA', 'FIVETRAN_METADATA_FIVETRAN_PLATFORM', 'FIVETRAN_METADATA_STG_FIVETRAN_PLATFORM']
    connector_found = False
    
    for schema in metadata_schemas:
        try:
            # Check if the schema exists
            cursor = conn.cursor()
            cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.{schema}")
            tables = cursor.fetchall()
            
            if not tables:
                continue
                
            # Look for the connectors table
            table_names = [row[1] for row in tables]
            connector_table = None
            
            # Check for various possible connector table names
            possible_tables = ['CONNECTORS', 'CONNECTOR', 'CONNECTIONS', 'CONNECTION']
            for table in possible_tables:
                if table in table_names:
                    connector_table = table
                    break
                    
            if connector_table:
                print(f"Found Fivetran metadata in {schema}.{connector_table}")
                
                # Query for ProHandel connector - specifically looking for 'bowed_protocol'
                query = f"""
                SELECT *
                FROM {SNOWFLAKE_DATABASE}.{schema}.{connector_table} 
                WHERE connector_id = 'bowed_protocol'
                """
                
                df = pd.read_sql(query, conn)
                if not df.empty:
                    connector_found = True
                    print("\nProHandel connector details (ID: bowed_protocol):")
                    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                    
                    # If we found the connector, check for schema changes table
                    schema_changes_table = None
                    possible_schema_tables = ['SCHEMA_CHANGES', 'SCHEMAS', 'SCHEMA_CHANGE_LOG']
                    for table in possible_schema_tables:
                        if table in table_names:
                            schema_changes_table = table
                            break
                            
                    if schema_changes_table:
                        print(f"\nSchema changes for connector 'bowed_protocol':")
                        schema_query = f"""
                        SELECT *
                        FROM {SNOWFLAKE_DATABASE}.{schema}.{schema_changes_table}
                        WHERE connector_id = 'bowed_protocol'
                        ORDER BY created_at DESC
                        LIMIT 10
                        """
                        try:
                            schema_df = pd.read_sql(schema_query, conn)
                            if not schema_df.empty:
                                print(tabulate(schema_df, headers='keys', tablefmt='psql', showindex=False))
                            else:
                                print("No schema changes found for ProHandel connector")
                        except Exception as e:
                            print(f"Error querying schema changes: {str(e)}")
                    
                    # Check sync logs if available
                    log_table = None
                    possible_log_tables = ['CONNECTOR_EXECUTION_LOG', 'SYNC_LOG', 'LOGS', 'CONNECTOR_LOGS']
                    for table in possible_log_tables:
                        if table in table_names:
                            log_table = table
                            break
                            
                    if log_table:
                        print(f"\nRecent sync logs for connector 'bowed_protocol':")
                        # Try different query formats based on common Fivetran metadata structures
                        log_queries = [
                            f"""
                            SELECT *
                            FROM {SNOWFLAKE_DATABASE}.{schema}.{log_table}
                            WHERE connector_id = 'bowed_protocol'
                            ORDER BY created_at DESC
                            LIMIT 10
                            """,
                            f"""
                            SELECT *
                            FROM {SNOWFLAKE_DATABASE}.{schema}.{log_table}
                            WHERE message_data->>'connector_id' = 'bowed_protocol'
                            ORDER BY created_at DESC
                            LIMIT 10
                            """
                        ]
                        
                        log_df = None
                        for query in log_queries:
                            try:
                                log_df = pd.read_sql(query, conn)
                                if not log_df.empty:
                                    break
                            except Exception:
                                continue
                                
                        if log_df is not None and not log_df.empty:
                            print(tabulate(log_df, headers='keys', tablefmt='psql', showindex=False))
                        else:
                            print("No recent sync logs found for ProHandel connector")
                except Exception as e:
                    print(f"Error querying sync logs: {str(e)}")
        except Exception as e:
            print(f"Error checking Fivetran metadata in {schema}: {str(e)}")
    
    if not connector_found:
        print("No connector with ID 'bowed_protocol' found in Fivetran metadata tables.")
        print("This could mean the connector hasn't been fully set up yet or the metadata tables haven't been populated.")
        print("If you just configured the connector, wait a few minutes for the first sync to complete.")

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

def check_fivetran_armed_unleaded_tables(conn):
    """Specifically check for tables in the FIVETRAN_ARMED_UNLEADED_STAGING schema"""
    schema = "FIVETRAN_ARMED_UNLEADED_STAGING"
    try:
        print(f"\n=== Checking tables in {schema} ===")
        
        cursor = conn.cursor()
        cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.{schema}")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"No tables found in {schema}")
            return []
        
        table_names = [row[1] for row in tables]
        print(f"Found {len(table_names)} tables in {schema}:")
        for table in table_names:
            print(f"  - {table}")
        
        return [(schema, table) for table in table_names]
    except Exception as e:
        print(f"Error checking {schema}: {str(e)}")
        return []

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
                print(f"\u274c Schema {schema} does not exist in {SNOWFLAKE_DATABASE}")
                continue
                
            print(f"\n\u2705 Found schema: {schema}")
            
            # Check for each ProHandel table
            for table in PROHANDEL_TABLES:
                try:
                    cursor = conn.cursor()
                    query = f"SELECT COUNT(*) FROM {SNOWFLAKE_DATABASE}.{schema}.{table}"
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        found_tables.append((schema, table, count))
                        print(f"  \u2705 Found {count} rows in {schema}.{table}")
                    else:
                        print(f"  \u26a0\ufe0f Table {schema}.{table} exists but has no data")
                        
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        print(f"  \u274c Table {schema}.{table} does not exist")
                    else:
                        print(f"  \u274c Error checking {schema}.{table}: {str(e)}")
        except Exception as e:
            print(f"\u274c Error checking schema {schema}: {str(e)}")
    
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
            print("\n\u26a0\ufe0f No ProHandel data found in Snowflake. The Lambda connector may not have run successfully.")
            
            # Check Fivetran sync status
            print("\n=== Checking Fivetran Sync Status ===")
            check_fivetran_sync_status(conn)
    finally:
        conn.close()
        print("\nSnowflake connection closed.")

if __name__ == "__main__":
    main()

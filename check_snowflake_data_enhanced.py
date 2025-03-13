#!/usr/bin/env python3
"""
Enhanced script to check Snowflake data from the ProHandel API connector
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
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USERNAME')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', 'MERCURIOS_LOADING_WH')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'MERCURIOS_DATA')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'ANALYTICS')

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
    
    # Try different possible locations for Fivetran metadata
    metadata_schemas = ['FIVETRAN_METADATA', 'FIVETRAN_METADATA_FIVETRAN_PLATFORM', 'FIVETRAN_METADATA_STG_FIVETRAN_PLATFORM']
    connector_found = False
    
    # Also check for the specific connector IDs we know about
    connector_ids = ['bowed_protocol', 'armed_unleaded', 'look_frescoes']
    
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
                
                # Query for ProHandel connector - try all known connector IDs
                for connector_id in connector_ids:
                    query = f"""
                    SELECT *
                    FROM {SNOWFLAKE_DATABASE}.{schema}.{connector_table} 
                    WHERE connector_id = '{connector_id}'
                    """
                    
                    try:
                        df = pd.read_sql(query, conn)
                        if not df.empty:
                            connector_found = True
                            print(f"\nProHandel connector details (ID: {connector_id}):")
                            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                            
                            # If we found the connector, check for schema changes table
                            schema_changes_table = None
                            possible_schema_tables = ['SCHEMA_CHANGES', 'SCHEMAS', 'SCHEMA_CHANGE_LOG']
                            for table in possible_schema_tables:
                                if table in table_names:
                                    schema_changes_table = table
                                    break
                                    
                            if schema_changes_table:
                                print(f"\nSchema changes for connector '{connector_id}':")
                                schema_query = f"""
                                SELECT *
                                FROM {SNOWFLAKE_DATABASE}.{schema}.{schema_changes_table}
                                WHERE connector_id = '{connector_id}'
                                ORDER BY created_at DESC
                                LIMIT 10
                                """
                                try:
                                    schema_df = pd.read_sql(schema_query, conn)
                                    if not schema_df.empty:
                                        print(tabulate(schema_df, headers='keys', tablefmt='psql', showindex=False))
                                    else:
                                        print(f"No schema changes found for connector '{connector_id}'")
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
                                print(f"\nRecent sync logs for connector '{connector_id}':")
                                # Try different query formats based on common Fivetran metadata structures
                                log_queries = [
                                    f"""
                                    SELECT *
                                    FROM {SNOWFLAKE_DATABASE}.{schema}.{log_table}
                                    WHERE connector_id = '{connector_id}'
                                    ORDER BY created_at DESC
                                    LIMIT 10
                                    """,
                                    f"""
                                    SELECT *
                                    FROM {SNOWFLAKE_DATABASE}.{schema}.{log_table}
                                    WHERE message_data->>'connector_id' = '{connector_id}'
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
                                    print(f"No recent sync logs found for connector '{connector_id}'")
                    except Exception as e:
                        print(f"Error querying connector '{connector_id}': {str(e)}")
        except Exception as e:
            print(f"Error checking Fivetran metadata in {schema}: {str(e)}")
    
    if not connector_found:
        print("\nNo ProHandel connector found in Fivetran metadata tables.")
        print("This could mean the connector hasn't been fully set up yet or the metadata tables haven't been populated.")
        print("If you just configured the connector, wait a few minutes for the first sync to complete.")

def check_fivetran_staging_tables(conn):
    """Specifically check for tables in the Fivetran staging schemas"""
    staging_schemas = [
        "FIVETRAN_ARMED_UNLEADED_STAGING", 
        "FIVETRAN_BOWED_PROTOCOL_STAGING",
        "FIVETRAN_LOOK_FRESCOES_STAGING"
    ]
    
    all_staging_tables = []
    
    for schema in staging_schemas:
        try:
            print(f"\n=== Checking tables in {schema} ===")
            
            cursor = conn.cursor()
            cursor.execute(f"SHOW SCHEMAS LIKE '{schema}' IN {SNOWFLAKE_DATABASE}")
            schemas_result = cursor.fetchall()
            
            if not schemas_result:
                print(f"Schema {schema} does not exist")
                continue
                
            cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.{schema}")
            tables = cursor.fetchall()
            
            if not tables:
                print(f"No tables found in {schema}")
                continue
            
            table_names = [row[1] for row in tables]
            print(f"Found {len(table_names)} tables in {schema}:")
            for table in table_names:
                print(f"  - {table}")
            
            all_staging_tables.extend([(schema, table) for table in table_names])
        except Exception as e:
            print(f"Error checking {schema}: {str(e)}")
    
    return all_staging_tables

def main():
    """Main function"""
    print("=== Checking Snowflake Data from ProHandel API ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    if not conn:
        return
    
    # List all schemas in the database
    schemas = list_schemas(conn)
    if not schemas:
        print("No schemas found. Cannot proceed.")
        conn.close()
        return
    
    # Check Fivetran sync status first
    check_fivetran_sync_status(conn)
    
    # Check for tables in the Fivetran staging schemas
    staging_tables = check_fivetran_staging_tables(conn)
    
    # Search for ProHandel tables across all schemas
    prohandel_tables = search_for_prohandel_tables(conn, schemas)
    
    # If we found any ProHandel tables, check their data
    if prohandel_tables:
        print("\nChecking data in ProHandel tables...")
        for schema, table in prohandel_tables:
            try:
                check_table_data(conn, schema, table)
                check_table_structure(conn, schema, table)
            except Exception as e:
                print(f"Error checking {schema}.{table}: {str(e)}")
    
    # Check data in staging tables
    if staging_tables:
        print("\nChecking data in Fivetran staging tables...")
        for schema, table in staging_tables:
            try:
                check_table_data(conn, schema, table)
                check_table_structure(conn, schema, table)
            except Exception as e:
                print(f"Error checking {schema}.{table}: {str(e)}")
    
    # If no tables found at all
    if not prohandel_tables and not staging_tables:
        print("\nNo ProHandel or staging tables found to check data.")
        print("Please verify that the Fivetran connector is properly configured and has completed at least one sync.")
    
    # Close connection
    conn.close()
    print("\nDone!")

if __name__ == "__main__":
    main()

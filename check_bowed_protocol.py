#!/usr/bin/env python3
"""
Script to specifically check for the bowed_protocol connector in Fivetran metadata
and any tables it might be creating in Snowflake
"""

import os
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from tabulate import tabulate
import time

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

def check_fivetran_metadata(conn):
    """Check Fivetran metadata for bowed_protocol connector"""
    print("\n=== Checking Fivetran Metadata for bowed_protocol connector ===")
    
    # Try different possible locations for Fivetran metadata
    metadata_schemas = [
        'FIVETRAN_METADATA', 
        'FIVETRAN_METADATA_FIVETRAN_PLATFORM', 
        'FIVETRAN_METADATA_STG_FIVETRAN_PLATFORM',
        'FIVETRAN_LOG',
        'INFORMATION_SCHEMA'
    ]
    
    connector_found = False
    
    for schema in metadata_schemas:
        try:
            # Check if the schema exists
            cursor = conn.cursor()
            cursor.execute(f"SHOW SCHEMAS LIKE '{schema}' IN {SNOWFLAKE_DATABASE}")
            schemas_result = cursor.fetchall()
            
            if not schemas_result:
                print(f"Schema {schema} does not exist")
                continue
                
            print(f"Checking schema: {schema}")
            cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.{schema}")
            tables = cursor.fetchall()
            
            if not tables:
                print(f"No tables found in {schema}")
                continue
                
            # Look for tables that might contain connector information
            table_names = [row[1] for row in tables]
            print(f"Tables in {schema}: {', '.join(table_names)}")
            
            # Check each table for 'bowed_protocol'
            for table in table_names:
                try:
                    query = f"""
                    SELECT COUNT(*) 
                    FROM {SNOWFLAKE_DATABASE}.{schema}.{table} 
                    WHERE LOWER(TO_VARCHAR(PARSE_JSON(VALUE:c))) LIKE '%bowed_protocol%'
                    """
                    
                    try:
                        cursor.execute(query)
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"Found references to 'bowed_protocol' in {schema}.{table}: {count} rows")
                            connector_found = True
                            
                            # Try to get more details
                            detail_query = f"""
                            SELECT * 
                            FROM {SNOWFLAKE_DATABASE}.{schema}.{table} 
                            WHERE LOWER(TO_VARCHAR(PARSE_JSON(VALUE:c))) LIKE '%bowed_protocol%'
                            LIMIT 5
                            """
                            
                            try:
                                df = pd.read_sql(detail_query, conn)
                                print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                            except Exception as e:
                                print(f"Error getting details from {schema}.{table}: {str(e)}")
                    except Exception:
                        # Try a simpler query if the JSON parsing fails
                        try:
                            query = f"""
                            SELECT COUNT(*) 
                            FROM {SNOWFLAKE_DATABASE}.{schema}.{table} 
                            WHERE TO_VARCHAR(TABLE_NAME) LIKE '%bowed_protocol%' 
                               OR TO_VARCHAR(CONNECTOR_ID) LIKE '%bowed_protocol%'
                            """
                            cursor.execute(query)
                            count = cursor.fetchone()[0]
                            if count > 0:
                                print(f"Found references to 'bowed_protocol' in {schema}.{table}: {count} rows")
                                connector_found = True
                                
                                # Try to get more details
                                detail_query = f"""
                                SELECT * 
                                FROM {SNOWFLAKE_DATABASE}.{schema}.{table} 
                                WHERE TO_VARCHAR(TABLE_NAME) LIKE '%bowed_protocol%' 
                                   OR TO_VARCHAR(CONNECTOR_ID) LIKE '%bowed_protocol%'
                                LIMIT 5
                                """
                                
                                try:
                                    df = pd.read_sql(detail_query, conn)
                                    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                                except Exception as e:
                                    print(f"Error getting details from {schema}.{table}: {str(e)}")
                        except Exception:
                            # If both queries fail, just continue to the next table
                            pass
                except Exception as e:
                    print(f"Error checking {schema}.{table}: {str(e)}")
        except Exception as e:
            print(f"Error checking schema {schema}: {str(e)}")
    
    if not connector_found:
        print("\nNo references to 'bowed_protocol' found in Fivetran metadata tables.")
        print("This could mean the connector hasn't been fully set up yet or the metadata tables haven't been populated.")
        print("If you just configured the connector, wait a few minutes for the first sync to complete.")

def check_bowed_protocol_schemas(conn):
    """Check for schemas related to bowed_protocol"""
    print("\n=== Checking for schemas related to bowed_protocol ===")
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"SHOW SCHEMAS LIKE '%BOWED_PROTOCOL%' IN {SNOWFLAKE_DATABASE}")
        schemas = cursor.fetchall()
        
        if not schemas:
            print("No schemas found with 'BOWED_PROTOCOL' in the name")
            return []
        
        schema_names = [row[1] for row in schemas]
        print(f"Found {len(schema_names)} schemas related to bowed_protocol:")
        for schema in schema_names:
            print(f"  - {schema}")
            
            # Check tables in this schema
            try:
                cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.{schema}")
                tables = cursor.fetchall()
                
                if not tables:
                    print(f"    No tables found in {schema}")
                    continue
                    
                table_names = [row[1] for row in tables]
                print(f"    Found {len(table_names)} tables in {schema}:")
                for table in table_names:
                    print(f"      - {table}")
                    
                    # Check row count
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {SNOWFLAKE_DATABASE}.{schema}.{table}")
                        count = cursor.fetchone()[0]
                        print(f"        Row count: {count}")
                        
                        # If there's data, show a sample
                        if count > 0:
                            try:
                                df = pd.read_sql(f"SELECT * FROM {SNOWFLAKE_DATABASE}.{schema}.{table} LIMIT 3", conn)
                                print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                            except Exception as e:
                                print(f"        Error getting sample data: {str(e)}")
                    except Exception as e:
                        print(f"        Error getting row count: {str(e)}")
            except Exception as e:
                print(f"    Error listing tables in {schema}: {str(e)}")
        
        return schema_names
    except Exception as e:
        print(f"Error checking for bowed_protocol schemas: {str(e)}")
        return []

def check_raw_tables(conn):
    """Check for ProHandel tables in the RAW schema"""
    print("\n=== Checking for ProHandel tables in RAW schema ===")
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"SHOW SCHEMAS LIKE 'RAW' IN {SNOWFLAKE_DATABASE}")
        schemas = cursor.fetchall()
        
        if not schemas:
            print("RAW schema does not exist")
            return
        
        # Check tables in RAW schema
        cursor.execute(f"SHOW TABLES IN {SNOWFLAKE_DATABASE}.RAW")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in RAW schema")
            return
            
        # Look for ProHandel-related tables
        prohandel_tables = []
        target_tables = [
            'ARTICLES', 'CUSTOMERS', 'ORDERS', 'ORDER_ITEMS', 'SALES', 'SALE_ITEMS', 
            'INVENTORY', 'SUPPLIERS', 'BRANCHES', 'CATEGORIES', 'COUNTRIES', 
            'CREDITS', 'CURRENCIES', 'INVOICES', 'LABELS', 'PAYMENTS', 'STAFF', 'VOUCHERS'
        ]
        target_tables_lower = [t.lower() for t in target_tables]
        
        for row in tables:
            table_name = row[1]
            if table_name.lower() in target_tables_lower or 'prohandel' in table_name.lower():
                prohandel_tables.append(table_name)
        
        if prohandel_tables:
            print(f"Found {len(prohandel_tables)} ProHandel-related tables in RAW schema:")
            for table in prohandel_tables:
                print(f"  - {table}")
                
                # Check row count
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {SNOWFLAKE_DATABASE}.RAW.{table}")
                    count = cursor.fetchone()[0]
                    print(f"    Row count: {count}")
                    
                    # If there's data, show a sample
                    if count > 0:
                        try:
                            df = pd.read_sql(f"SELECT * FROM {SNOWFLAKE_DATABASE}.RAW.{table} LIMIT 3", conn)
                            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
                        except Exception as e:
                            print(f"    Error getting sample data: {str(e)}")
                except Exception as e:
                    print(f"    Error getting row count: {str(e)}")
        else:
            print("No ProHandel-related tables found in RAW schema")
    except Exception as e:
        print(f"Error checking RAW schema: {str(e)}")

def main():
    """Main function"""
    print("=== Checking Snowflake Data for bowed_protocol connector ===")
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    if not conn:
        return
    
    # Check Fivetran metadata for bowed_protocol connector
    check_fivetran_metadata(conn)
    
    # Check for schemas related to bowed_protocol
    bowed_schemas = check_bowed_protocol_schemas(conn)
    
    # Check for ProHandel tables in RAW schema
    check_raw_tables(conn)
    
    # If no bowed_protocol schemas found, suggest waiting
    if not bowed_schemas:
        print("\nNo schemas related to bowed_protocol found yet.")
        print("This is normal if the connector was just set up or if the sync is still in progress.")
        print("Fivetran typically creates schemas like FIVETRAN_BOWED_PROTOCOL_STAGING when data starts flowing.")
        print("Please check back in a few minutes or hours after the sync has had time to complete.")
    
    # Close connection
    conn.close()
    print("\nDone!")

if __name__ == "__main__":
    main()

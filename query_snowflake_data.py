#!/usr/bin/env python
"""
Query Snowflake Data - Mercurios.ai
This script demonstrates how to query data from your Snowflake instance
using the credentials in your .env file.
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

def explore_schemas(conn):
    """List all schemas in the database."""
    query = f"""
    SELECT SCHEMA_NAME 
    FROM {snowflake_params['database']}.INFORMATION_SCHEMA.SCHEMATA
    ORDER BY SCHEMA_NAME
    """
    return run_query(conn, query)

def explore_tables(conn, schema):
    """List all tables in a schema."""
    query = f"""
    SELECT TABLE_NAME, ROW_COUNT
    FROM {snowflake_params['database']}.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = '{schema}'
    ORDER BY TABLE_NAME
    """
    return run_query(conn, query)

def sample_data(conn, schema, table, limit=10):
    """Get sample data from a table."""
    query = f"""
    SELECT * 
    FROM {snowflake_params['database']}.{schema}.{table}
    LIMIT {limit}
    """
    return run_query(conn, query)

def analyze_shopify_data(conn):
    """Analyze Shopify customer and order data."""
    print("\n=== Shopify Customer Analysis ===")
    query = """
    SELECT 
        COUNT(*) as total_customers,
        AVG(ORDERS_COUNT) as avg_orders_per_customer,
        MAX(ORDERS_COUNT) as max_orders_per_customer
    FROM MERCURIOS_DATA.SHOPIFY.CUSTOMER
    """
    df = run_query(conn, query)
    print(tabulate(df, headers='keys', tablefmt='psql'))
    
    print("\n=== Top Products by Orders ===")
    query = """
    SELECT 
        p.TITLE as product_name,
        COUNT(ol.ID) as order_count,
        SUM(ol.QUANTITY) as total_quantity
    FROM MERCURIOS_DATA.SHOPIFY.ORDER_LINE ol
    JOIN MERCURIOS_DATA.SHOPIFY.PRODUCT p ON ol.PRODUCT_ID = p.ID
    GROUP BY p.TITLE
    ORDER BY order_count DESC
    LIMIT 10
    """
    df = run_query(conn, query)
    print(tabulate(df, headers='keys', tablefmt='psql'))

def inventory_analysis(conn):
    """Analyze inventory data."""
    print("\n=== Inventory Analysis ===")
    query = """
    SELECT 
        *
    FROM MERCURIOS_DATA.ANALYTICS.INVENTORY
    """
    df = run_query(conn, query)
    print(tabulate(df, headers='keys', tablefmt='psql'))
    
    print("\n=== Reorder Recommendations ===")
    query = """
    SELECT 
        *
    FROM MERCURIOS_DATA.ANALYTICS.REORDER_RECOMMENDATIONS
    """
    df = run_query(conn, query)
    print(tabulate(df, headers='keys', tablefmt='psql'))

def main():
    """Main function to run the script."""
    conn = connect_to_snowflake()
    if not conn:
        return
    
    try:
        # List schemas
        print("\n=== Available Schemas ===")
        schemas_df = explore_schemas(conn)
        print(tabulate(schemas_df, headers='keys', tablefmt='psql'))
        
        # Choose a schema to explore
        schema_to_explore = input("\nEnter schema name to explore (e.g., SHOPIFY): ").strip().upper()
        
        # List tables in the schema
        print(f"\n=== Tables in {schema_to_explore} Schema ===")
        tables_df = explore_tables(conn, schema_to_explore)
        print(tabulate(tables_df, headers='keys', tablefmt='psql'))
        
        # Choose a table to sample
        table_to_sample = input("\nEnter table name to sample: ").strip().upper()
        
        # Show sample data
        print(f"\n=== Sample Data from {schema_to_explore}.{table_to_sample} ===")
        sample_df = sample_data(conn, schema_to_explore, table_to_sample)
        print(tabulate(sample_df, headers='keys', tablefmt='psql'))
        
        # Run predefined analyses
        run_analyses = input("\nRun predefined analyses? (y/n): ").strip().lower()
        if run_analyses == 'y':
            try:
                analyze_shopify_data(conn)
                inventory_analysis(conn)
            except Exception as e:
                print(f"Error running analyses: {e}")
        
    finally:
        conn.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()

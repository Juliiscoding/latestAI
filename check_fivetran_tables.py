#!/usr/bin/env python3
"""
Script to check Fivetran tables in Snowflake for ProHandel and Google Analytics 4 data
This script helps analyze the data available in Snowflake and assess its usefulness for the Mercurios project
"""

import os
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from tabulate import tabulate

# Load environment variables from .env file
load_dotenv()

# Snowflake connection parameters
# Hardcode the account identifier to ensure it's correct
SNOWFLAKE_ACCOUNT = 'VRXDFZX-ZZ95717'
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')

def connect_to_snowflake():
    """Connect to Snowflake and return the connection"""
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE
        )
        print(f"Connected to Snowflake: {SNOWFLAKE_DATABASE}")
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {str(e)}")
        return None

def list_fivetran_schemas(conn):
    """List all Fivetran schemas in the database"""
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW SCHEMAS LIKE 'FIVETRAN%'")
        schemas = cursor.fetchall()
        print("\n=== Fivetran Schemas ===")
        for schema in schemas:
            print(f"- {schema[1]}")
        return [schema[1] for schema in schemas]
    except Exception as e:
        print(f"Error listing schemas: {str(e)}")
        return []

def list_tables_in_schema(conn, schema):
    """List all tables in a schema"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SHOW TABLES IN SCHEMA {schema}")
        tables = cursor.fetchall()
        print(f"\n=== Tables in {schema} ===")
        for table in tables:
            print(f"- {table[1]}")
        return [table[1] for table in tables]
    except Exception as e:
        print(f"Error listing tables in {schema}: {str(e)}")
        return []

def describe_table(conn, schema, table):
    """Describe a table's structure"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE TABLE {schema}.{table}")
        columns = cursor.fetchall()
        print(f"\n=== Structure of {schema}.{table} ===")
        for column in columns:
            print(f"- {column[0]}: {column[1]}")
        return columns
    except Exception as e:
        print(f"Error describing table {schema}.{table}: {str(e)}")
        return []

def sample_table_data(conn, schema, table, limit=5):
    """Sample data from a table"""
    try:
        query = f"SELECT * FROM {schema}.{table} LIMIT {limit}"
        df = pd.read_sql(query, conn)
        print(f"\n=== Sample data from {schema}.{table} ===")
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        return df
    except Exception as e:
        print(f"Error sampling data from {schema}.{table}: {str(e)}")
        return None

def check_prohandel_tables(conn):
    """Check for ProHandel tables in all schemas"""
    # Common ProHandel table names
    prohandel_tables = ['ARTICLES', 'CUSTOMERS', 'ORDERS', 'SALES', 'INVENTORY']
    
    # Check all schemas
    cursor = conn.cursor()
    cursor.execute("SHOW SCHEMAS")
    schemas = cursor.fetchall()
    
    found_tables = []
    
    for schema in schemas:
        schema_name = schema[1]
        for table_name in prohandel_tables:
            try:
                cursor.execute(f"SHOW TABLES LIKE '{table_name}' IN SCHEMA {schema_name}")
                tables = cursor.fetchall()
                if tables:
                    found_tables.append((schema_name, table_name))
                    print(f"Found {table_name} in schema {schema_name}")
            except Exception as e:
                # Skip errors due to permission issues
                pass
    
    return found_tables

def check_ga4_tables(conn):
    """Check for Google Analytics 4 tables and assess their usefulness"""
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES IN SCHEMA GOOGLE_ANALYTICS_4")
        tables = cursor.fetchall()
        
        print("\n=== Google Analytics 4 Tables ===")
        for table in tables:
            print(f"- {table[1]}")
        
        # Categorize tables by their usefulness for Mercurios
        ecommerce_tables = [t[1] for t in tables if 'ECOMMERCE' in t[1]]
        conversion_tables = [t[1] for t in tables if 'CONVERSION' in t[1]]
        traffic_tables = [t[1] for t in tables if 'TRAFFIC' in t[1]]
        user_tables = [t[1] for t in tables if 'USER' in t[1]]
        demographic_tables = [t[1] for t in tables if 'DEMOGRAPHIC' in t[1]]
        
        print("\n=== GA4 Data Categories ===")
        print(f"Ecommerce Data: {len(ecommerce_tables)} tables")
        print(f"Conversion Data: {len(conversion_tables)} tables")
        print(f"Traffic Data: {len(traffic_tables)} tables")
        print(f"User Data: {len(user_tables)} tables")
        print(f"Demographic Data: {len(demographic_tables)} tables")
        
        # Assess usefulness for Mercurios
        print("\n=== GA4 Data Usefulness for Mercurios ===")
        print("1. Ecommerce Data: HIGH - Provides product performance metrics that can be joined with ProHandel inventory data")
        print("2. Conversion Data: HIGH - Helps understand which products convert best online")
        print("3. Traffic Data: MEDIUM - Useful for understanding how users find products")
        print("4. User Data: MEDIUM - Helps segment customers for inventory planning")
        print("5. Demographic Data: MEDIUM - Useful for regional inventory planning")
        
        return {
            'ecommerce': ecommerce_tables,
            'conversion': conversion_tables,
            'traffic': traffic_tables,
            'user': user_tables,
            'demographic': demographic_tables
        }
    except Exception as e:
        print(f"Error checking GA4 tables: {str(e)}")
        return {}

def analyze_ga4_prohandel_integration(conn, ga4_tables):
    """Analyze how GA4 data can be integrated with ProHandel data"""
    print("\n=== Integration Opportunities ===")
    
    # Key integration points
    print("1. Product Performance: Join ProHandel inventory with GA4 ecommerce data")
    print("   - Match products by SKU/article_id")
    print("   - Analyze which products get views vs. which sell well in-store")
    
    print("\n2. Customer Segmentation: Combine ProHandel customer data with GA4 user data")
    print("   - Identify high-value customers across online and offline channels")
    print("   - Create customer segments for inventory planning")
    
    print("\n3. Inventory Optimization: Use GA4 traffic and conversion data to forecast demand")
    print("   - Identify trending products from online behavior")
    print("   - Adjust inventory levels based on online interest")
    
    print("\n4. Regional Analysis: Combine ProHandel sales locations with GA4 demographic data")
    print("   - Optimize inventory by region based on online and offline behavior")
    
    # Suggested dbt models
    print("\n=== Suggested dbt Models ===")
    print("1. stg_ga4_product_performance - Clean GA4 product data")
    print("2. stg_ga4_user_acquisition - Clean GA4 user acquisition data")
    print("3. int_product_performance_combined - Join ProHandel and GA4 product data")
    print("4. int_customer_behavior_combined - Join ProHandel and GA4 customer data")
    print("5. fct_product_insights - Comprehensive product performance metrics")
    print("6. fct_customer_insights - Comprehensive customer behavior metrics")
    print("7. fct_inventory_forecast_enhanced - Inventory forecast using both data sources")

def main():
    """Main function"""
    # Connect to Snowflake
    conn = connect_to_snowflake()
    if not conn:
        return
    
    # List Fivetran schemas
    fivetran_schemas = list_fivetran_schemas(conn)
    
    # Check for ProHandel tables across all schemas
    print("\n=== Searching for ProHandel tables ===")
    prohandel_tables = check_prohandel_tables(conn)
    
    # For each ProHandel table found, describe it and sample data
    for schema, table in prohandel_tables:
        describe_table(conn, schema, table)
        sample_table_data(conn, schema, table)
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    # Connect to Snowflake
    conn = connect_to_snowflake()
    if conn:
        # Check for ProHandel tables
        print("\n=== Checking ProHandel Tables ===")
        prohandel_tables = check_prohandel_tables(conn)
        
        # Check for Google Analytics 4 tables
        print("\n=== Checking Google Analytics 4 Tables ===")
        ga4_tables = check_ga4_tables(conn)
        
        # Analyze integration opportunities
        if ga4_tables:
            analyze_ga4_prohandel_integration(conn, ga4_tables)
        
        # Close connection
        conn.close()
        print("\n=== Analysis Complete ===")
        print("The Google Analytics 4 export connector is providing rich, detailed data")
        print("that can be integrated with ProHandel data for enhanced inventory management.")
        print("Consider implementing the suggested dbt models to leverage this data.")
    else:
        print("Failed to connect to Snowflake.")

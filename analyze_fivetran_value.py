#!/usr/bin/env python
"""
Analyze Fivetran connector value to identify high-value vs. low-value data sources.
This helps optimize sync frequency and reduce costs while preserving business insights.
"""

import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Snowflake connection parameters
snowflake_user = os.getenv("SNOWFLAKE_USER")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")

def connect_to_snowflake():
    """Establish connection to Snowflake."""
    conn = snowflake.connector.connect(
        user=snowflake_user,
        password=snowflake_password,
        account=snowflake_account,
        warehouse="MERCURIOS_DEV_WH",  # Use smallest warehouse for analysis
        database="MERCURIOS_DATA"
    )
    return conn

def get_raw_tables(conn):
    """Get list of all tables in the RAW schema."""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES IN MERCURIOS_DATA.RAW")
    tables = cursor.fetchall()
    cursor.close()
    return tables

def analyze_table_usage(conn):
    """Analyze which tables are being queried most frequently."""
    cursor = conn.cursor()
    
    # Query to find which tables are most frequently accessed
    query = """
    SELECT 
        SPLIT_PART(SPLIT_PART(OBJECTS_ACCESSED, '.', -2), '"', 2) as schema_name,
        SPLIT_PART(SPLIT_PART(OBJECTS_ACCESSED, '.', -1), '"', 2) as table_name,
        COUNT(*) as query_count
    FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
    WHERE QUERY_START_TIME >= DATEADD(month, -1, CURRENT_TIMESTAMP())
    AND SPLIT_PART(SPLIT_PART(OBJECTS_ACCESSED, '.', -2), '"', 2) = 'RAW'
    GROUP BY 1, 2
    ORDER BY 3 DESC
    """
    
    try:
        cursor.execute(query)
        usage_data = cursor.fetchall()
        usage_df = pd.DataFrame(usage_data, columns=['schema', 'table', 'query_count'])
        return usage_df
    except Exception as e:
        print(f"Error analyzing table usage: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def analyze_table_size(conn):
    """Analyze the size of each table in the RAW schema."""
    cursor = conn.cursor()
    
    query = """
    SELECT 
        table_schema,
        table_name,
        row_count,
        bytes/1024/1024 as size_mb
    FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
    WHERE table_schema = 'RAW'
    ORDER BY size_mb DESC
    """
    
    try:
        cursor.execute(query)
        size_data = cursor.fetchall()
        size_df = pd.DataFrame(size_data, columns=['schema', 'table', 'row_count', 'size_mb'])
        return size_df
    except Exception as e:
        print(f"Error analyzing table size: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def identify_source_tables(conn):
    """Identify which tables come from which Fivetran connector."""
    cursor = conn.cursor()
    
    # This is a best guess based on table naming conventions
    # You may need to adjust this based on your actual naming patterns
    query = """
    SELECT 
        table_name,
        CASE
            WHEN table_name LIKE 'SHOPIFY%' THEN 'shopify'
            WHEN table_name LIKE 'GA%' OR table_name LIKE 'GOOGLE_ANALYTICS%' THEN 'google_analytics_4_export'
            WHEN table_name LIKE 'KLAVIYO%' THEN 'klaviyo'
            WHEN table_name LIKE 'AWS%' OR table_name LIKE 'LAMBDA%' THEN 'aws_lambda'
            ELSE 'unknown'
        END as likely_source
    FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
    WHERE table_schema = 'RAW'
    """
    
    try:
        cursor.execute(query)
        source_data = cursor.fetchall()
        source_df = pd.DataFrame(source_data, columns=['table', 'source'])
        return source_df
    except Exception as e:
        print(f"Error identifying source tables: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def generate_value_report():
    """Generate a comprehensive report on connector value."""
    conn = connect_to_snowflake()
    
    try:
        # Get all tables
        tables = get_raw_tables(conn)
        print(f"Found {len(tables)} tables in RAW schema")
        
        # Analyze table usage
        usage_df = analyze_table_usage(conn)
        
        # Analyze table size
        size_df = analyze_table_size(conn)
        
        # Identify source tables
        source_df = identify_source_tables(conn)
        
        # Merge the dataframes
        if not usage_df.empty and not size_df.empty and not source_df.empty:
            # Merge usage and size
            merged_df = pd.merge(size_df, usage_df, on=['schema', 'table'], how='left')
            
            # Merge with source
            merged_df = pd.merge(merged_df, source_df, on='table', how='left')
            
            # Fill NaN values
            merged_df['query_count'] = merged_df['query_count'].fillna(0)
            
            # Calculate value score (size efficiency)
            merged_df['value_score'] = merged_df['query_count'] / (merged_df['size_mb'] + 1)  # Add 1 to avoid division by zero
            
            # Aggregate by source
            source_summary = merged_df.groupby('source').agg({
                'size_mb': 'sum',
                'row_count': 'sum',
                'query_count': 'sum',
                'value_score': 'mean'
            }).reset_index()
            
            # Sort by value score
            source_summary = source_summary.sort_values('value_score', ascending=False)
            
            # Save to CSV
            merged_df.to_csv('fivetran_table_value_analysis.csv', index=False)
            source_summary.to_csv('fivetran_connector_value_summary.csv', index=False)
            
            print("\n=== Fivetran Connector Value Analysis ===")
            print(source_summary)
            
            print("\n=== Recommended Actions ===")
            for _, row in source_summary.iterrows():
                if row['value_score'] > 1.0:
                    print(f"HIGH VALUE - {row['source']}: Keep syncing regularly")
                elif row['value_score'] > 0.1:
                    print(f"MEDIUM VALUE - {row['source']}: Reduce sync frequency to daily")
                else:
                    print(f"LOW VALUE - {row['source']}: Consider pausing or weekly sync")
            
            return source_summary
        else:
            print("Unable to complete analysis due to missing data")
            return None
    finally:
        conn.close()

if __name__ == "__main__":
    generate_value_report()

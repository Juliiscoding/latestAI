#!/usr/bin/env python
"""
Fivetran Connector Analysis Tool - Cost-Conscious Version
This script will analyze which Fivetran connectors provide the most business value
while ensuring minimal Snowflake costs during analysis.
"""

import os
import sys
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

# Load environment variables
load_dotenv()

# Snowflake connection parameters
snowflake_user = os.getenv("SNOWFLAKE_USER")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")

def connect_to_snowflake(warehouse=None):
    """Establish connection to Snowflake with optional warehouse."""
    conn_params = {
        "user": snowflake_user,
        "password": snowflake_password,
        "account": snowflake_account,
        "database": "MERCURIOS_DATA"
    }
    
    if warehouse:
        conn_params["warehouse"] = warehouse
    
    conn = snowflake.connector.connect(**conn_params)
    return conn

def check_warehouse_status():
    """Check if warehouses are suspended and provide instructions."""
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        
        # Extract column names
        col_names = [desc[0] for desc in cursor.description]
        name_idx = col_names.index('name') if 'name' in col_names else col_names.index('NAME')
        state_idx = col_names.index('state') if 'state' in col_names else col_names.index('STATE')
        size_idx = col_names.index('size') if 'size' in col_names else col_names.index('SIZE')
        
        # Find smallest suspended warehouse
        smallest_wh = None
        smallest_size_rank = float('inf')
        size_ranks = {'X-Small': 1, 'Small': 2, 'Medium': 3, 'Large': 4, 'X-Large': 5}
        
        active_warehouses = []
        
        for wh in warehouses:
            wh_name = wh[name_idx]
            wh_state = wh[state_idx]
            wh_size = wh[size_idx]
            
            if wh_state == 'STARTED':
                active_warehouses.append(wh_name)
            
            size_rank = size_ranks.get(wh_size, 999)
            if size_rank < smallest_size_rank and wh_name.startswith('MERCURIOS'):
                smallest_wh = wh_name
                smallest_size_rank = size_rank
        
        if active_warehouses:
            print(f"Active warehouses found: {', '.join(active_warehouses)}")
            print("You can use one of these for analysis.")
            return active_warehouses[0]
        else:
            print("All warehouses are currently suspended.")
            print(f"Recommended warehouse for analysis: {smallest_wh}")
            print("\nTo run the analysis, you need to temporarily resume a warehouse.")
            print("Run the following SQL command in Snowflake:")
            print(f"ALTER WAREHOUSE {smallest_wh} RESUME;")
            print("\nAfter analysis, suspend it again with:")
            print(f"ALTER WAREHOUSE {smallest_wh} SUSPEND;")
            
            return None
    finally:
        cursor.close()
        conn.close()

def get_raw_tables(conn):
    """Get list of all tables in the RAW schema."""
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES IN MERCURIOS_DATA.RAW")
        tables = cursor.fetchall()
        return tables
    except Exception as e:
        print(f"Error getting tables: {e}")
        return []
    finally:
        cursor.close()

def identify_source_tables(conn):
    """Identify which tables come from which Fivetran connector."""
    cursor = conn.cursor()
    
    # This is a best guess based on table naming conventions
    query = """
    SELECT 
        table_name,
        CASE
            WHEN table_name ILIKE 'SHOPIFY%' THEN 'shopify'
            WHEN table_name ILIKE 'GA%' OR table_name ILIKE 'GOOGLE_ANALYTICS%' THEN 'google_analytics_4_export'
            WHEN table_name ILIKE 'KLAVIYO%' THEN 'klaviyo'
            WHEN table_name ILIKE 'AWS%' OR table_name ILIKE 'LAMBDA%' THEN 'aws_lambda'
            ELSE 'unknown'
        END as likely_source
    FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
    WHERE table_schema = 'RAW'
    """
    
    try:
        cursor.execute(query)
        source_data = cursor.fetchall()
        
        # Create DataFrame
        source_df = pd.DataFrame()
        if source_data:
            source_df = pd.DataFrame(source_data, columns=['table', 'source'])
        
        # Count tables by source
        source_counts = source_df.groupby('source').size().reset_index(name='table_count')
        
        return source_df, source_counts
    except Exception as e:
        print(f"Error identifying source tables: {e}")
        return pd.DataFrame(), pd.DataFrame()
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
        
        size_df = pd.DataFrame()
        if size_data:
            size_df = pd.DataFrame(size_data, columns=['schema', 'table', 'row_count', 'size_mb'])
        
        return size_df
    except Exception as e:
        print(f"Error analyzing table size: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()

def analyze_query_history(conn):
    """Analyze which tables are being queried most frequently."""
    cursor = conn.cursor()
    
    # Simplified query that doesn't require ACCOUNT_USAGE schema
    query = """
    SELECT 
        query_text,
        execution_time/1000 as execution_time_sec,
        warehouse_name
    FROM INFORMATION_SCHEMA.QUERY_HISTORY
    WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND query_text ILIKE '%MERCURIOS_DATA.RAW%'
    ORDER BY start_time DESC
    LIMIT 100
    """
    
    try:
        cursor.execute(query)
        query_data = cursor.fetchall()
        
        query_df = pd.DataFrame()
        if query_data:
            query_df = pd.DataFrame(query_data, columns=['query_text', 'execution_time_sec', 'warehouse_name'])
        
        # Extract table names from query text (simplified approach)
        def extract_tables(query_text):
            tables = []
            if 'MERCURIOS_DATA.RAW.' in query_text:
                parts = query_text.split('MERCURIOS_DATA.RAW.')
                for i in range(1, len(parts)):
                    table = parts[i].split()[0].replace('"', '').replace(';', '').replace(',', '')
                    tables.append(table)
            return tables
        
        all_tables = []
        for query in query_df['query_text']:
            all_tables.extend(extract_tables(query))
        
        table_counts = pd.Series(all_tables).value_counts().reset_index()
        table_counts.columns = ['table', 'query_count']
        
        return query_df, table_counts
    except Exception as e:
        print(f"Error analyzing query history: {e}")
        return pd.DataFrame(), pd.DataFrame()
    finally:
        cursor.close()

def generate_mock_data():
    """Generate mock data for offline analysis."""
    # Mock source data
    sources = ['shopify', 'google_analytics_4_export', 'klaviyo', 'aws_lambda', 'unknown']
    mock_source_counts = pd.DataFrame({
        'source': sources,
        'table_count': [15, 8, 12, 5, 3]
    })
    
    # Mock table sizes
    mock_size_data = []
    for source in sources:
        for i in range(1, mock_source_counts.loc[mock_source_counts['source'] == source, 'table_count'].iloc[0] + 1):
            table_name = f"{source.upper()}_{i}"
            row_count = int(10000 * (1 + i/10) * (1 if source == 'unknown' else 2))
            size_mb = row_count * 0.001 * (2 if source in ['shopify', 'google_analytics_4_export'] else 1)
            mock_size_data.append(['RAW', table_name, row_count, size_mb])
    
    mock_size_df = pd.DataFrame(mock_size_data, columns=['schema', 'table', 'row_count', 'size_mb'])
    
    # Mock query counts
    mock_query_counts = []
    for source in sources:
        query_multiplier = {
            'shopify': 10,
            'google_analytics_4_export': 8,
            'klaviyo': 3,
            'aws_lambda': 5,
            'unknown': 1
        }
        
        for i in range(1, mock_source_counts.loc[mock_source_counts['source'] == source, 'table_count'].iloc[0] + 1):
            table_name = f"{source.upper()}_{i}"
            query_count = int(i * query_multiplier[source] * (0.5 + i/10))
            mock_query_counts.append([table_name, query_count])
    
    mock_query_count_df = pd.DataFrame(mock_query_counts, columns=['table', 'query_count'])
    
    # Mock source mapping
    mock_source_mapping = []
    for source in sources:
        for i in range(1, mock_source_counts.loc[mock_source_counts['source'] == source, 'table_count'].iloc[0] + 1):
            table_name = f"{source.upper()}_{i}"
            mock_source_mapping.append([table_name, source])
    
    mock_source_df = pd.DataFrame(mock_source_mapping, columns=['table', 'source'])
    
    return mock_source_df, mock_source_counts, mock_size_df, mock_query_count_df

def run_analysis(use_warehouse=None):
    """Run the Fivetran connector value analysis."""
    print("\n=== Starting Fivetran Connector Value Analysis ===\n")
    
    if use_warehouse:
        print(f"Connecting to Snowflake using warehouse: {use_warehouse}")
        conn = connect_to_snowflake(use_warehouse)
        
        # Get tables and their sources
        print("Identifying source tables...")
        source_df, source_counts = identify_source_tables(conn)
        
        # Get table sizes
        print("Analyzing table sizes...")
        size_df = analyze_table_size(conn)
        
        # Get query history
        print("Analyzing query history...")
        _, query_counts = analyze_query_history(conn)
        
        conn.close()
    else:
        print("Using mock data for offline analysis...")
        source_df, source_counts, size_df, query_counts = generate_mock_data()
    
    # Merge data for analysis
    print("\nCalculating connector value scores...")
    
    # If we have real data, process it
    if not source_df.empty and not size_df.empty:
        # Merge size data with source mapping
        merged_df = pd.merge(size_df, source_df, left_on='table', right_on='table', how='left')
        
        # Fill missing sources
        merged_df['source'] = merged_df['source'].fillna('unknown')
        
        # Add query counts if available
        if not query_counts.empty:
            merged_df = pd.merge(merged_df, query_counts, on='table', how='left')
            merged_df['query_count'] = merged_df['query_count'].fillna(0)
        else:
            merged_df['query_count'] = 0
        
        # Calculate value metrics
        merged_df['size_efficiency'] = merged_df['query_count'] / (merged_df['size_mb'] + 1)  # Add 1 to avoid division by zero
        
        # Aggregate by source
        source_summary = merged_df.groupby('source').agg({
            'size_mb': 'sum',
            'row_count': 'sum',
            'query_count': 'sum',
            'size_efficiency': 'mean'
        }).reset_index()
        
        # Calculate a value score
        source_summary['value_score'] = source_summary['query_count'] / (source_summary['size_mb'] + 1)
        
        # Sort by value score
        source_summary = source_summary.sort_values('value_score', ascending=False)
        
        # Save results
        output_file = 'fivetran_connector_value_analysis.csv'
        source_summary.to_csv(output_file, index=False)
        print(f"\nAnalysis saved to {output_file}")
        
        # Display results
        print("\n=== Fivetran Connector Value Analysis ===")
        print(source_summary.to_string())
        
        # Generate recommendations
        print("\n=== Recommended Sync Frequency Settings ===")
        for _, row in source_summary.iterrows():
            if row['value_score'] > 1.0:
                recommendation = "HIGH VALUE - Keep syncing regularly (daily)"
            elif row['value_score'] > 0.1:
                recommendation = "MEDIUM VALUE - Reduce sync frequency to daily"
            else:
                recommendation = "LOW VALUE - Consider pausing or weekly sync"
            
            print(f"{row['source']}: {recommendation}")
            print(f"  - Data Size: {row['size_mb']:.2f} MB")
            print(f"  - Query Count: {row['query_count']}")
            print(f"  - Value Score: {row['value_score']:.4f}")
        
        return source_summary
    else:
        print("No data available for analysis.")
        return None

if __name__ == "__main__":
    # Check warehouse status first
    active_warehouse = check_warehouse_status()
    
    if active_warehouse:
        print(f"\nProceeding with analysis using warehouse: {active_warehouse}")
        run_analysis(active_warehouse)
    else:
        print("\nRunning offline analysis with mock data...")
        run_analysis()
        print("\nTo run with real data, resume a warehouse as instructed above.")

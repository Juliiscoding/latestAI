import snowflake.connector
import os
from tabulate import tabulate
import getpass

print("Connecting to Snowflake to explore Fivetran metadata...")

# Get password securely
password = getpass.getpass('Enter your Snowflake password: ')
if not password:
    print("Password cannot be empty. Please run the script again and enter your password.")
    exit(1)

try:
    # Connect to Snowflake with the working parameters
    conn = snowflake.connector.connect(
        user='JULIUSRECHENBACH',
        password=password,
        account='VRXDFZX-ZZ95717',
        role='ACCOUNTADMIN',
        warehouse='COMPUTE_WH'
    )

    # Create a cursor object
    cur = conn.cursor()

    # Use MERCURIOS_DATA database
    cur.execute("USE DATABASE MERCURIOS_DATA")
    
    # Explore Fivetran metadata
    print("\n=== Fivetran Connectors ===")
    cur.execute("""
    SELECT 
        c.id as connector_id,
        c.name as connector_name,
        ct.name as connector_type,
        c.created_at,
        c.connected_by,
        c.status,
        c.setup_state
    FROM FIVETRAN_METADATA.CONNECTOR c
    JOIN FIVETRAN_METADATA.CONNECTOR_TYPE ct ON c.connector_type_id = ct.id
    """)
    connectors = cur.fetchall()
    print(tabulate(connectors, headers=[col[0] for col in cur.description]))
    
    # Explore Fivetran logs
    print("\n=== Recent Fivetran Logs ===")
    cur.execute("""
    SELECT 
        timestamp,
        connector_id,
        level,
        message
    FROM FIVETRAN_METADATA.LOG
    ORDER BY timestamp DESC
    LIMIT 10
    """)
    logs = cur.fetchall()
    print(tabulate(logs, headers=[col[0] for col in cur.description]))
    
    # Explore transformation runs
    print("\n=== Fivetran Transformation Runs ===")
    cur.execute("""
    SELECT *
    FROM FIVETRAN_METADATA.TRANSFORMATION_RUNS
    """)
    transformations = cur.fetchall()
    print(tabulate(transformations, headers=[col[0] for col in cur.description]))
    
    # Explore RAW schema tables
    print("\n=== RAW Schema Tables ===")
    cur.execute("""
    SELECT 
        table_name,
        table_type,
        row_count,
        bytes,
        created
    FROM INFORMATION_SCHEMA.TABLES
    WHERE table_schema = 'RAW'
    """)
    raw_tables = cur.fetchall()
    print(tabulate(raw_tables, headers=[col[0] for col in cur.description]))
    
    # Get column information for RAW tables
    print("\n=== RAW Schema Table Columns ===")
    cur.execute("""
    SELECT 
        table_name,
        column_name,
        data_type,
        character_maximum_length,
        is_nullable
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_schema = 'RAW'
    ORDER BY table_name, ordinal_position
    """)
    raw_columns = cur.fetchall()
    print(tabulate(raw_columns, headers=[col[0] for col in cur.description]))
    
    # Close the connection
    cur.close()
    conn.close()
    
    print("\nExploration complete!")
    
except Exception as e:
    print(f"Error: {str(e)}")

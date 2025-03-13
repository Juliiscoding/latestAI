import snowflake.connector
import os
from tabulate import tabulate
import getpass

print("Connecting to Snowflake to explore information schema...")

# Get password securely (make sure to enter a password when prompted)
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

    # Explore MERCURIOS_DATA database
    print("\nExploring MERCURIOS_DATA database:")
    cur.execute("USE DATABASE MERCURIOS_DATA")
    
    # Query information schema for tables
    print("\nQuerying INFORMATION_SCHEMA for tables:")
    cur.execute("""
    SELECT 
        table_catalog as database_name,
        table_schema as schema_name,
        table_name,
        table_type,
        row_count,
        bytes
    FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
    ORDER BY table_schema, table_name
    """)
    tables_info = cur.fetchall()
    print(tabulate(tables_info, headers=[col[0] for col in cur.description]))
    
    # Query information schema for schemas
    print("\nQuerying INFORMATION_SCHEMA for schemas:")
    cur.execute("""
    SELECT 
        catalog_name as database_name,
        schema_name,
        schema_owner,
        created
    FROM MERCURIOS_DATA.INFORMATION_SCHEMA.SCHEMATA
    ORDER BY schema_name
    """)
    schemas_info = cur.fetchall()
    print(tabulate(schemas_info, headers=[col[0] for col in cur.description]))
    
    # Close the connection
    cur.close()
    conn.close()
    
    print("\nExploration complete!")
    
except Exception as e:
    print(f"Error: {str(e)}")

import snowflake.connector
import os
from tabulate import tabulate
import getpass

print("Connecting to Snowflake to explore MERCURIOS_DATA...")

# Get password securely
password = getpass.getpass('Enter your Snowflake password: ')

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
cur.execute("SHOW SCHEMAS")
schemas = cur.fetchall()
print("\nSchemas in MERCURIOS_DATA:")
print(tabulate(schemas, headers=[col[0] for col in cur.description]))

# Try to get a list of available roles
print("\nAvailable roles:")
try:
    cur.execute("SHOW ROLES")
    roles = cur.fetchall()
    print(tabulate(roles, headers=[col[0] for col in cur.description]))
except Exception as e:
    print(f"Error listing roles: {str(e)}")

# Check current grants
print("\nCurrent grants for ACCOUNTADMIN:")
try:
    cur.execute("SHOW GRANTS TO ROLE ACCOUNTADMIN")
    grants = cur.fetchall()
    print(tabulate(grants, headers=[col[0] for col in cur.description]))
except Exception as e:
    print(f"Error listing grants: {str(e)}")

# Try to grant access to Fivetran schemas
print("\nAttempting to grant access to Fivetran schemas...")
try:
    cur.execute("GRANT IMPORTED PRIVILEGES ON DATABASE MERCURIOS_DATA TO ROLE ACCOUNTADMIN")
    print("Successfully granted imported privileges.")
except Exception as e:
    print(f"Error granting privileges: {str(e)}")

# Try to access PUBLIC schema which we should have access to
print("\nExploring PUBLIC schema:")
try:
    cur.execute("USE SCHEMA MERCURIOS_DATA.PUBLIC")
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    print("Tables in PUBLIC schema:")
    print(tabulate(tables, headers=[col[0] for col in cur.description]))
except Exception as e:
    print(f"Error accessing PUBLIC schema: {str(e)}")

# Try to create a view that joins data across schemas (if we have permission)
print("\nAttempting to create a view that accesses Fivetran data...")
try:
    cur.execute("""
    CREATE OR REPLACE VIEW MERCURIOS_DATA.PUBLIC.FIVETRAN_SCHEMA_INFO AS
    SELECT 
        table_catalog as database_name,
        table_schema as schema_name,
        table_name,
        column_count,
        bytes,
        row_count
    FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
    WHERE table_schema LIKE 'FIVETRAN%' OR table_schema LIKE 'GOOGLE%' OR table_schema LIKE 'KLAVIYO%'
    """)
    print("Successfully created view.")
    
    # Query the view
    cur.execute("SELECT * FROM MERCURIOS_DATA.PUBLIC.FIVETRAN_SCHEMA_INFO")
    view_data = cur.fetchall()
    print("\nFivetran Schema Information:")
    print(tabulate(view_data, headers=[col[0] for col in cur.description]))
except Exception as e:
    print(f"Error creating or querying view: {str(e)}")

# Try to query information schema directly
print("\nQuerying INFORMATION_SCHEMA directly:")
try:
    cur.execute("""
    SELECT 
        table_catalog as database_name,
        table_schema as schema_name,
        table_name,
        column_count,
        bytes,
        row_count
    FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
    WHERE table_schema LIKE 'GOOGLE%' OR table_schema LIKE 'KLAVIYO%'
    """)
    info_schema_data = cur.fetchall()
    print(tabulate(info_schema_data, headers=[col[0] for col in cur.description]))
except Exception as e:
    print(f"Error querying INFORMATION_SCHEMA: {str(e)}")

# Look for Fivetran-related schemas
fivetran_schemas = []
for schema in schemas:
    schema_name = schema[1]  # Assuming name is in the second column
    if any(keyword in schema_name.upper() for keyword in ['FIVETRAN', 'GOOGLE', 'ANALYTICS', 'GA4', 'SHOPIFY', 'KLAVIYO', 'AWS']):
        fivetran_schemas.append(schema_name)

# Explore each Fivetran-related schema
for schema_name in fivetran_schemas:
    print(f"\nExploring schema: {schema_name}")
    try:
        cur.execute(f"USE SCHEMA {schema_name}")
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        print(f"Tables in {schema_name}:")
        print(tabulate(tables, headers=[col[0] for col in cur.description]))
        
        # Get sample data from each table (limit to first 5 tables to avoid too much output)
        for i, table in enumerate(tables[:5]):
            table_name = table[1]  # Assuming name is in the second column
            print(f"\nSample data from {schema_name}.{table_name}:")
            try:
                cur.execute(f"SELECT * FROM {schema_name}.{table_name} LIMIT 5")
                sample_data = cur.fetchall()
                if sample_data:
                    print(tabulate(sample_data, headers=[col[0] for col in cur.description]))
                else:
                    print("No data found in this table.")
            except Exception as e:
                print(f"Error querying table: {str(e)}")
    except Exception as e:
        print(f"Error accessing schema: {str(e)}")

# If no Fivetran schemas were found
if not fivetran_schemas:
    print("\nNo Fivetran-related schemas found. This is expected if data hasn't been synced yet.")
    print("Listing all schemas for reference:")
    for schema in schemas:
        schema_name = schema[1]
        print(f"\nExploring schema: {schema_name}")
        try:
            cur.execute(f"USE SCHEMA {schema_name}")
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            print(f"Tables in {schema_name}:")
            print(tabulate(tables, headers=[col[0] for col in cur.description]))
        except Exception as e:
            print(f"Error exploring schema: {str(e)}")

# Close the connection
cur.close()
conn.close()

print("\nExploration complete!")

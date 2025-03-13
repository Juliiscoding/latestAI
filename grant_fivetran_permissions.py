#!/usr/bin/env python3
"""
Grant necessary permissions to FIVETRAN_USER in Snowflake
"""

import json
import snowflake.connector
import sys

# Load Snowflake config
with open('snowflake_config.json', 'r') as f:
    config = json.load(f)

# Connect to Snowflake
try:
    conn = snowflake.connector.connect(
        user=config['username'],
        password=config['password'],
        account=config['account'],
        warehouse=config['warehouse'],
        database=config['database'],
        schema=config['schema'],
        role=config['role']  # Use the role from config (ACCOUNTADMIN)
    )
    
    # Create a cursor object
    cursor = conn.cursor()
    
    database = config['database']
    
    # Grant permissions to FIVETRAN_USER
    permissions = [
        f"GRANT USAGE ON DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT MODIFY ON DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT MONITOR ON DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE SCHEMA ON DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT USAGE ON WAREHOUSE {config['warehouse']} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT OPERATE ON WAREHOUSE {config['warehouse']} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        # Grant permissions on all existing schemas
        f"GRANT USAGE ON ALL SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE TABLE ON ALL SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE VIEW ON ALL SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE STAGE ON ALL SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE PIPE ON ALL SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        # Future grants for new schemas
        f"GRANT USAGE ON FUTURE SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE TABLE ON FUTURE SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE VIEW ON FUTURE SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE STAGE ON FUTURE SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
        f"GRANT CREATE PIPE ON FUTURE SCHEMAS IN DATABASE {database} TO ROLE MERCURIOS_FIVETRAN_SERVICE;",
    ]
    
    print("Granting permissions to FIVETRAN_USER via MERCURIOS_FIVETRAN_SERVICE role...")
    for sql in permissions:
        print(f"Executing: {sql}")
        cursor.execute(sql)
        print("Success!")
    
    # Verify the role has the necessary permissions
    print("\nVerifying permissions on database...")
    cursor.execute(f"SHOW GRANTS ON DATABASE {database}")
    for row in cursor:
        if "MERCURIOS_FIVETRAN_SERVICE" in str(row):
            print(row)
    
    print("\nVerifying permissions on warehouse...")
    cursor.execute(f"SHOW GRANTS ON WAREHOUSE {config['warehouse']}")
    for row in cursor:
        if "MERCURIOS_FIVETRAN_SERVICE" in str(row):
            print(row)
    
    # Close the connection
    cursor.close()
    conn.close()
    
    print("\nSuccessfully granted permissions to FIVETRAN_USER via MERCURIOS_FIVETRAN_SERVICE role")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

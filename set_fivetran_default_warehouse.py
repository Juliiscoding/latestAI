#!/usr/bin/env python3
"""
Set DEFAULT_WAREHOUSE for FIVETRAN_USER in Snowflake
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
    
    # Set the default warehouse for FIVETRAN_USER
    warehouse = config['warehouse']
    sql = f"ALTER USER FIVETRAN_USER SET DEFAULT_WAREHOUSE='{warehouse}';"
    cursor.execute(sql)
    
    # Verify the default warehouse was set
    cursor.execute("DESCRIBE USER FIVETRAN_USER;")
    user_properties = {}
    for row in cursor:
        property_name = row[0]
        property_value = row[1]
        user_properties[property_name] = property_value
        print(f"{property_name}: {property_value}")
    
    if user_properties.get('DEFAULT_WAREHOUSE') == warehouse:
        print(f"\nSuccessfully set DEFAULT_WAREHOUSE to {warehouse} for FIVETRAN_USER")
    else:
        print(f"\nWarning: DEFAULT_WAREHOUSE may not have been set correctly")
    
    # Close the connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

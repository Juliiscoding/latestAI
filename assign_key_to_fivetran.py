#!/usr/bin/env python3
"""
Assign RSA public key to FIVETRAN_USER in Snowflake
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
    
    # Read the public key
    with open('/Users/juliusrechenbach/.ssh/snowflake/fivetran_rsa_key.pub', 'r') as f:
        public_key = f.read()
    
    # Extract just the key part (remove header and footer)
    key_lines = public_key.strip().split('\n')
    if len(key_lines) >= 3:  # Has header and footer
        key_content = ''.join(key_lines[1:-1])
    else:
        key_content = public_key.strip()
    
    # Execute SQL to alter user
    sql = f"ALTER USER FIVETRAN_USER SET RSA_PUBLIC_KEY='{key_content}';"
    cursor.execute(sql)
    
    # Verify the key was set
    cursor.execute("DESCRIBE USER FIVETRAN_USER;")
    for row in cursor:
        print(row)
    
    # Close the connection
    cursor.close()
    conn.close()
    
    print("Successfully assigned public key to FIVETRAN_USER")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

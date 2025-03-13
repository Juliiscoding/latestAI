#!/usr/bin/env python3
"""
Grant permissions to access Fivetran metadata tables
"""

import json
import snowflake.connector
import sys

def main():
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
        
        cursor = conn.cursor()
        
        # Grant permissions to the current role
        print(f"Granting permissions to role {config['role']}...")
        
        # Grant usage on schema
        cursor.execute(f"GRANT USAGE ON SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA TO ROLE {config['role']}")
        print(f"Granted USAGE on schema FIVETRAN_METADATA to role {config['role']}")
        
        # Grant select on all tables
        cursor.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA TO ROLE {config['role']}")
        print(f"Granted SELECT on all tables in FIVETRAN_METADATA to role {config['role']}")
        
        # Grant select on future tables
        cursor.execute(f"GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA TO ROLE {config['role']}")
        print(f"Granted SELECT on future tables in FIVETRAN_METADATA to role {config['role']}")
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print("\nPermissions granted successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

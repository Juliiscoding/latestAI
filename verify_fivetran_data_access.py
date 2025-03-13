#!/usr/bin/env python3
"""
Verify access to Fivetran-managed schemas and tables in Snowflake.
"""

import snowflake.connector
import getpass
from tabulate import tabulate

# Constants
ACCOUNT = 'VRXDFZX-ZZ95717'
USER = 'JULIUSRECHENBACH'
WAREHOUSE = 'COMPUTE_WH'
DATABASE = 'MERCURIOS_DATA'

def connect_to_snowflake(role):
    """Connect to Snowflake with the specified role."""
    try:
        # Get password securely
        password = getpass.getpass(f"Enter your Snowflake password for role {role}: ")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            account=ACCOUNT,
            user=USER,
            password=password,
            warehouse=WAREHOUSE,
            role=role,
            database=DATABASE
        )
        
        print(f"✅ Successfully connected with role: {role}")
        
        # Get current role and user
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ROLE(), CURRENT_USER()")
        current_role, current_user = cursor.fetchone()
        print(f"Current role: {current_role}, Current user: {current_user}")
        
        return conn
    except Exception as e:
        print(f"❌ Failed to connect with role {role}: {str(e)}")
        return None

def check_schema_access(conn, schema_name):
    """Check access to a specific schema and its tables."""
    if not conn:
        print(f"No connection available for schema {schema_name}.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Try to use the schema
        cursor.execute(f"USE SCHEMA {schema_name}")
        print(f"✅ Successfully accessed schema {schema_name}")
        
        # List tables in the schema
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"Tables in {schema_name} schema:")
            table_data = []
            for table in tables:
                table_name = table[1]
                table_kind = table[3]
                table_data.append([table_name, table_kind])
            
            print(tabulate(table_data, headers=["Table Name", "Kind"], tablefmt="pretty"))
            
            # Sample data from first table
            if len(tables) > 0:
                first_table = tables[0][1]
                print(f"\nSample data from {first_table}:")
                try:
                    cursor.execute(f"SELECT * FROM {first_table} LIMIT 5")
                    rows = cursor.fetchall()
                    
                    if rows:
                        # Get column names
                        col_names = [desc[0] for desc in cursor.description]
                        
                        # Print data
                        print(tabulate(rows, headers=col_names, tablefmt="pretty"))
                    else:
                        print(f"No data found in {first_table}.")
                except Exception as e:
                    print(f"❌ Failed to query table {first_table}: {str(e)}")
        else:
            print(f"No tables found in {schema_name} schema.")
    
    except Exception as e:
        print(f"❌ Failed to access schema {schema_name}: {str(e)}")
    
    finally:
        cursor.close()

def main():
    """Main function to run the script."""
    # Schemas to check
    schemas = [
        "GOOGLE_ANALYTICS_4",
        "KLAVIYO",
        "KLAVIYO_KLAVIYO",
        "KLAVIYO_INT_KLAVIYO",
        "KLAVIYO_STG_KLAVIYO",
        "FIVETRAN_METADATA"
    ]
    
    # Roles to check
    roles = [
        "ACCOUNTADMIN",
        "MERCURIOS_ADMIN",
        "MERCURIOS_DEVELOPER",
        "MERCURIOS_FIVETRAN_SERVICE"
    ]
    
    for role in roles:
        print(f"\n{'=' * 80}")
        print(f"TESTING ROLE: {role}")
        print(f"{'=' * 80}")
        
        conn = connect_to_snowflake(role)
        if conn:
            for schema in schemas:
                print(f"\n--- Testing access to {schema} schema with role {role} ---")
                check_schema_access(conn, schema)
            
            conn.close()
        else:
            print(f"Skipping schema tests for role {role} due to connection failure.")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    main()

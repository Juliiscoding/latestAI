#!/usr/bin/env python3
"""
Query Fivetran-managed schemas directly using the MERCURIOS_FIVETRAN_SERVICE role.
"""

import snowflake.connector
import getpass
from tabulate import tabulate

# Constants
ACCOUNT = 'VRXDFZX-ZZ95717'
USER = 'JULIUSRECHENBACH'
WAREHOUSE = 'COMPUTE_WH'
DATABASE = 'MERCURIOS_DATA'

def connect_to_snowflake():
    """Connect to Snowflake with MERCURIOS_FIVETRAN_SERVICE role."""
    try:
        # Get password securely
        password = getpass.getpass(f"Enter your Snowflake password: ")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            account=ACCOUNT,
            user=USER,
            password=password,
            warehouse=WAREHOUSE,
            role="MERCURIOS_FIVETRAN_SERVICE",
            database=DATABASE
        )
        
        print(f"✅ Successfully connected with role: MERCURIOS_FIVETRAN_SERVICE")
        
        # Get current role and user
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ROLE(), CURRENT_USER()")
        current_role, current_user = cursor.fetchone()
        print(f"Current role: {current_role}, Current user: {current_user}")
        
        return conn
    except Exception as e:
        print(f"❌ Failed to connect: {str(e)}")
        return None

def query_schemas(conn):
    """Query Fivetran-managed schemas."""
    if not conn:
        print("No connection available.")
        return
    
    cursor = conn.cursor()
    
    try:
        # List all schemas
        print("\nListing all schemas...")
        cursor.execute("SHOW SCHEMAS")
        schemas = cursor.fetchall()
        
        if schemas:
            print("Schemas accessible to MERCURIOS_FIVETRAN_SERVICE:")
            schema_data = []
            for schema in schemas:
                schema_name = schema[1]
                schema_owner = schema[5]
                schema_data.append([schema_name, schema_owner])
            
            print(tabulate(schema_data, headers=["Schema Name", "Owner"], tablefmt="pretty"))
        else:
            print("No schemas found.")
        
        # Check Google Analytics 4 schema
        print("\nChecking Google Analytics 4 schema...")
        try:
            cursor.execute("USE SCHEMA GOOGLE_ANALYTICS_4")
            print("✅ Successfully accessed GOOGLE_ANALYTICS_4 schema")
            
            # List tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print("Tables in GOOGLE_ANALYTICS_4 schema:")
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
                    cursor.execute(f"SELECT * FROM {first_table} LIMIT 5")
                    rows = cursor.fetchall()
                    
                    if rows:
                        # Get column names
                        col_names = [desc[0] for desc in cursor.description]
                        
                        # Print data
                        print(tabulate(rows, headers=col_names, tablefmt="pretty"))
                    else:
                        print(f"No data found in {first_table}.")
            else:
                print("No tables found in GOOGLE_ANALYTICS_4 schema.")
        except Exception as e:
            print(f"❌ Failed to access GOOGLE_ANALYTICS_4 schema: {str(e)}")
        
        # Check Klaviyo schema
        print("\nChecking Klaviyo schema...")
        try:
            cursor.execute("USE SCHEMA KLAVIYO")
            print("✅ Successfully accessed KLAVIYO schema")
            
            # List tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print("Tables in KLAVIYO schema:")
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
                    cursor.execute(f"SELECT * FROM {first_table} LIMIT 5")
                    rows = cursor.fetchall()
                    
                    if rows:
                        # Get column names
                        col_names = [desc[0] for desc in cursor.description]
                        
                        # Print data
                        print(tabulate(rows, headers=col_names, tablefmt="pretty"))
                    else:
                        print(f"No data found in {first_table}.")
            else:
                print("No tables found in KLAVIYO schema.")
        except Exception as e:
            print(f"❌ Failed to access KLAVIYO schema: {str(e)}")
        
        # Check other Klaviyo schemas
        klaviyo_schemas = ["KLAVIYO_KLAVIYO", "KLAVIYO_INT_KLAVIYO", "KLAVIYO_STG_KLAVIYO"]
        for schema in klaviyo_schemas:
            print(f"\nChecking {schema} schema...")
            try:
                cursor.execute(f"USE SCHEMA {schema}")
                print(f"✅ Successfully accessed {schema} schema")
                
                # List tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"Tables in {schema} schema:")
                    table_data = []
                    for table in tables:
                        table_name = table[1]
                        table_kind = table[3]
                        table_data.append([table_name, table_kind])
                    
                    print(tabulate(table_data, headers=["Table Name", "Kind"], tablefmt="pretty"))
                else:
                    print(f"No tables found in {schema} schema.")
            except Exception as e:
                print(f"❌ Failed to access {schema} schema: {str(e)}")
    
    except Exception as e:
        print(f"❌ Error querying schemas: {str(e)}")
    
    finally:
        cursor.close()

def main():
    """Main function to run the script."""
    print("Querying Fivetran-managed schemas...")
    
    conn = connect_to_snowflake()
    if conn:
        query_schemas(conn)
        conn.close()
    else:
        print("Failed to connect to Snowflake. Exiting.")

if __name__ == "__main__":
    main()

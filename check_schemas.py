#!/usr/bin/env python3
"""
Check if schemas exist in Snowflake for Mercurios AI project.
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
    """Connect to Snowflake with ACCOUNTADMIN role."""
    try:
        # Get password securely
        password = getpass.getpass(f"Enter your Snowflake password: ")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            account=ACCOUNT,
            user=USER,
            password=password,
            warehouse=WAREHOUSE,
            role="ACCOUNTADMIN"
        )
        
        print(f"✅ Successfully connected with role: ACCOUNTADMIN")
        
        # Get current role and user
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ROLE(), CURRENT_USER()")
        current_role, current_user = cursor.fetchone()
        print(f"Current role: {current_role}, Current user: {current_user}")
        
        return conn
    except Exception as e:
        print(f"❌ Failed to connect: {str(e)}")
        return None

def check_schemas(conn):
    """Check if schemas exist in Snowflake."""
    if not conn:
        print("No connection available.")
        return
    
    cursor = conn.cursor()
    
    try:
        # List all databases
        print("\nListing all databases...")
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        if databases:
            print("Databases in Snowflake account:")
            for db in databases:
                print(f"- {db[1]}")
        
        # Use MERCURIOS_DATA database
        print(f"\nUsing MERCURIOS_DATA database...")
        cursor.execute(f"USE DATABASE MERCURIOS_DATA")
        print("✅ Successfully set MERCURIOS_DATA as current database")
        
        # List all schemas in MERCURIOS_DATA
        print(f"\nListing all schemas in MERCURIOS_DATA...")
        cursor.execute(f"SHOW SCHEMAS")
        schemas = cursor.fetchall()
        
        if schemas:
            print("Schemas in MERCURIOS_DATA:")
            schema_data = []
            for schema in schemas:
                schema_name = schema[1]
                schema_owner = schema[5]
                schema_data.append([schema_name, schema_owner])
            
            print(tabulate(schema_data, headers=["Schema Name", "Owner"], tablefmt="pretty"))
        else:
            print("No schemas found in MERCURIOS_DATA.")
        
        # Check for specific schemas
        schemas_to_check = [
            "GOOGLE_ANALYTICS_4",
            "KLAVIYO",
            "FIVETRAN_ARMED_UNLEADED_STAGING",
            "FIVETRAN_METADATA",
            "PUBLIC",
            "RAW"
        ]
        
        print("\nChecking for specific schemas...")
        for schema in schemas_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{schema}'")
            if cursor.fetchone()[0] > 0:
                print(f"✅ Schema {schema} exists in MERCURIOS_DATA")
            else:
                print(f"❌ Schema {schema} does not exist in MERCURIOS_DATA")
        
        # Check for Fivetran schemas with different naming patterns
        print("\nChecking for Fivetran schemas with different naming patterns...")
        cursor.execute(f"SHOW SCHEMAS LIKE 'FIVETRAN%'")
        fivetran_schemas = cursor.fetchall()
        
        if fivetran_schemas:
            print("Fivetran-related schemas found:")
            for schema in fivetran_schemas:
                print(f"- {schema[1]}")
        else:
            print("No Fivetran-related schemas found.")
        
        # Check for GA4 schemas with different naming patterns
        print("\nChecking for GA4 schemas with different naming patterns...")
        cursor.execute(f"SHOW SCHEMAS LIKE '%GA4%'")
        ga4_schemas = cursor.fetchall()
        
        if not ga4_schemas:
            cursor.execute(f"SHOW SCHEMAS LIKE '%GOOGLE%'")
            ga4_schemas = cursor.fetchall()
        
        if ga4_schemas:
            print("GA4-related schemas found:")
            for schema in ga4_schemas:
                print(f"- {schema[1]}")
        else:
            print("No GA4-related schemas found.")
        
        # Check for Klaviyo schemas with different naming patterns
        print("\nChecking for Klaviyo schemas with different naming patterns...")
        cursor.execute(f"SHOW SCHEMAS LIKE '%KLAVIYO%'")
        klaviyo_schemas = cursor.fetchall()
        
        if klaviyo_schemas:
            print("Klaviyo-related schemas found:")
            for schema in klaviyo_schemas:
                print(f"- {schema[1]}")
        else:
            print("No Klaviyo-related schemas found.")
    
    except Exception as e:
        print(f"❌ Error checking schemas: {str(e)}")
    
    finally:
        cursor.close()

def main():
    """Main function to run the script."""
    print("Checking schemas in Snowflake...")
    
    conn = connect_to_snowflake()
    if conn:
        check_schemas(conn)
        conn.close()
    else:
        print("Failed to connect to Snowflake. Exiting.")

if __name__ == "__main__":
    main()

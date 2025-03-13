#!/usr/bin/env python3
"""
Verify grants on schemas in Snowflake for Mercurios AI project.
"""

import snowflake.connector
import getpass
from tabulate import tabulate

# Constants
ACCOUNT = 'VRXDFZX-ZZ95717'
USER = 'JULIUSRECHENBACH'
WAREHOUSE = 'COMPUTE_WH'
DATABASE = 'MERCURIOS_DATA'

def connect_to_snowflake(role="ACCOUNTADMIN"):
    """Connect to Snowflake with specified role."""
    try:
        # Get password securely
        password = getpass.getpass(f"Enter your Snowflake password: ")
        
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            account=ACCOUNT,
            user=USER,
            password=password,
            warehouse=WAREHOUSE,
            role=role
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

def verify_grants(role):
    """Verify grants for a specific role."""
    print(f"\n{'='*80}")
    print(f"VERIFYING GRANTS FOR ROLE: {role}")
    print(f"{'='*80}")
    
    conn = connect_to_snowflake(role)
    if not conn:
        print(f"Could not verify grants for role {role}. Connection failed.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Use MERCURIOS_DATA database
        cursor.execute(f"USE DATABASE MERCURIOS_DATA")
        print("✅ Successfully accessed MERCURIOS_DATA database")
        
        # List all schemas in MERCURIOS_DATA
        print(f"\nListing accessible schemas for role {role}...")
        cursor.execute(f"SHOW SCHEMAS")
        schemas = cursor.fetchall()
        
        if schemas:
            print(f"Schemas accessible to {role}:")
            schema_data = []
            for schema in schemas:
                schema_name = schema[1]
                schema_owner = schema[5]
                schema_data.append([schema_name, schema_owner])
            
            print(tabulate(schema_data, headers=["Schema Name", "Owner"], tablefmt="pretty"))
        else:
            print(f"No schemas accessible to {role}.")
        
        # Try to access each schema and list tables
        schemas_to_check = [
            "GOOGLE_ANALYTICS_4",
            "KLAVIYO",
            "KLAVIYO_KLAVIYO",
            "KLAVIYO_INT_KLAVIYO",
            "KLAVIYO_STG_KLAVIYO",
            "FIVETRAN_ARMED_UNLEADED_STAGING",
            "FIVETRAN_METADATA",
            "FIVETRAN_METADATA_FIVETRAN_PLATFORM",
            "FIVETRAN_METADATA_STG_FIVETRAN_PLATFORM",
            "PUBLIC",
            "RAW"
        ]
        
        print("\nChecking access to specific schemas...")
        for schema in schemas_to_check:
            try:
                cursor.execute(f'USE SCHEMA "{schema}"')
                print(f"✅ Successfully accessed schema {schema}")
                
                # List tables in schema
                cursor.execute(f'SHOW TABLES')
                tables = cursor.fetchall()
                
                if tables:
                    print(f"   Tables in {schema}:")
                    for table in tables[:5]:  # Show only first 5 tables
                        print(f"   - {table[1]}")
                    
                    if len(tables) > 5:
                        print(f"   ... and {len(tables) - 5} more tables")
                else:
                    print(f"   No tables found in {schema}")
            except Exception as e:
                print(f"❌ Failed to access schema {schema}: {str(e)}")
    
    except Exception as e:
        print(f"❌ Error verifying grants: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function to run the script."""
    print("Verifying grants in Snowflake...")
    
    roles_to_check = [
        "ACCOUNTADMIN",
        "MERCURIOS_ADMIN",
        "MERCURIOS_ANALYST",
        "MERCURIOS_DEVELOPER"
    ]
    
    for role in roles_to_check:
        verify_grants(role)
    
    print("\nGrant verification complete!")

if __name__ == "__main__":
    main()

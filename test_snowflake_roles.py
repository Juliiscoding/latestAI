import snowflake.connector
import os
from tabulate import tabulate
import getpass

print("Testing Snowflake access with different roles...")

# Get password securely
password = getpass.getpass('Enter your Snowflake password: ')
if not password:
    print("Password cannot be empty. Please run the script again and enter your password.")
    exit(1)

# Roles to test
roles_to_test = ['ACCOUNTADMIN', 'MERCURIOS_ADMIN', 'MERCURIOS_ANALYST', 'MERCURIOS_DEVELOPER']

# Test each role
for role in roles_to_test:
    print(f"\n\n{'='*80}")
    print(f"TESTING ROLE: {role}")
    print(f"{'='*80}")
    
    try:
        # Connect to Snowflake with the role
        conn = snowflake.connector.connect(
            user='JULIUSRECHENBACH',
            password=password,
            account='VRXDFZX-ZZ95717',
            role=role,
            warehouse='MERCURIOS_DEV_WH'  # Using the warehouse shown in screenshots
        )
        
        # Create a cursor object
        cur = conn.cursor()
        
        print(f"✅ Successfully connected with role: {role}")
        
        # Get current role and user
        cur.execute("SELECT CURRENT_ROLE(), CURRENT_USER()")
        current = cur.fetchone()
        print(f"Current role: {current[0]}, Current user: {current[1]}")
        
        # Use MERCURIOS_DATA database
        cur.execute("USE DATABASE MERCURIOS_DATA")
        print("✅ Successfully accessed MERCURIOS_DATA database")
        
        # Test access to schemas
        schemas_to_test = [
            'GOOGLE_ANALYTICS_4',
            'KLAVIYO',
            'FIVETRAN_ARMED_UNLEADED_STAGING',
            'FIVETRAN_METADATA',
            'PUBLIC',
            'RAW'
        ]
        
        for schema in schemas_to_test:
            try:
                cur.execute(f"USE SCHEMA {schema}")
                print(f"✅ Access to schema {schema}: SUCCESS")
                
                # List tables in schema
                cur.execute("SHOW TABLES")
                tables = cur.fetchall()
                if tables:
                    print(f"   Tables in {schema}:")
                    for table in tables[:5]:  # Show first 5 tables
                        print(f"   - {table[1]}")
                    if len(tables) > 5:
                        print(f"   ... and {len(tables) - 5} more tables")
                else:
                    print(f"   No tables found in {schema}")
                    
            except Exception as e:
                print(f"❌ Access to schema {schema}: FAILED - {str(e)}")
        
        # Close the connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Failed to connect with role {role}: {str(e)}")

print("\nRole testing complete!")

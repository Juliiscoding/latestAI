import snowflake.connector
import os
from tabulate import tabulate
import getpass

print("Let's try connecting to Snowflake with username/password...")

# Get password securely
password = getpass.getpass('Enter your Snowflake password: ')

# Try different account formats
account_formats = [
    'VRXDFZX-ZZ95717',  # Original format
    'vrxdfzx-zz95717',  # Lowercase
    'vrxdfzx.zz95717',  # With dot instead of dash
    'zz95717',          # Just the account name
    'vrxdfzx',          # Just the org name
    'vrxdfzx.zz95717.snowflakecomputing.com'  # Full URL
]

# Try different warehouses
warehouses = ['COMPUTE_WH', 'MERCURIOS_WH', None]

# Try different connection parameters
for account in account_formats:
    for warehouse in warehouses:
        try:
            print(f"\nTrying account: {account}, warehouse: {warehouse}")
            
            conn_params = {
                'user': 'JULIUSRECHENBACH',
                'password': password,
                'account': account,
                'role': 'ACCOUNTADMIN'
            }
            
            if warehouse:
                conn_params['warehouse'] = warehouse
                
            # Connect to Snowflake
            conn = snowflake.connector.connect(**conn_params)
            
            # If we get here, connection was successful
            print("✅ Connection successful!")
            
            # Create a cursor object
            cur = conn.cursor()
            
            print("\nListing all databases:")
            cur.execute("SHOW DATABASES")
            databases = cur.fetchall()
            print(tabulate(databases, headers=[col[0] for col in cur.description]))
            
            # Close the connection
            cur.close()
            conn.close()
            
            # Exit the loop if successful
            print("\nConnection test completed successfully.")
            exit(0)
            
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            continue

print("\nAll connection attempts failed. Please check your Snowflake credentials and account information.")

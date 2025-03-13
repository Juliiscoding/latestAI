#!/usr/bin/env python3
"""
Test script for Snowflake password authentication to verify connection parameters.
"""

import os
import sys
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Snowflake credentials
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")

def main():
    print(f"Testing Snowflake password authentication...")
    print(f"Account: {SNOWFLAKE_ACCOUNT}")
    print(f"User: {SNOWFLAKE_USER}")
    
    try:
        # Connect to Snowflake
        print(f"\nConnecting to Snowflake with password authentication...")
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse="MERCURIOS_DEV_WH",
            database="MERCURIOS_DATA",
            role="MERCURIOS_DEVELOPER"
        )
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT current_version()")
        version = cursor.fetchone()[0]
        print(f"✅ Connection successful! Snowflake version: {version}")
        
        # Show current user and role
        cursor.execute("SELECT current_user(), current_role()")
        user_role = cursor.fetchone()
        print(f"Current user: {user_role[0]}")
        print(f"Current role: {user_role[1]}")
        
        # Get account details
        cursor.execute("SELECT current_account()")
        account = cursor.fetchone()[0]
        print(f"Current account: {account}")
        
        # Get region
        cursor.execute("SELECT current_region()")
        region = cursor.fetchone()[0]
        print(f"Current region: {region}")
        
        # Close the connection
        cursor.close()
        conn.close()
        print("Connection closed.")
        
        print("\n✅ Password authentication successful!")
        print("This confirms that your basic connection parameters are correct.")
        print("The issue is specifically with the key pair authentication.")
        
        # Suggest next steps
        print("\nNext steps for key pair authentication:")
        print("1. Verify the exact account identifier format from this test")
        print("2. Check if the public key was registered correctly in Snowflake")
        print("3. Ensure the private key is in the correct format (PKCS8 DER)")
        print("4. Try regenerating the key pair with the regenerate_snowflake_key.py script")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting steps:")
        print("1. Verify your Snowflake credentials in the .env file")
        print("2. Check if your Snowflake account is active")
        print("3. Verify network connectivity to Snowflake")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)

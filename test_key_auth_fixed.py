#!/usr/bin/env python3
"""
Test script for Snowflake key pair authentication with the correct account identifier.
"""

import os
import sys
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Snowflake credentials
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PRIVATE_KEY_PATH = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")

# Use the correct account identifier from the password authentication test
ACCOUNT = "ND80018"

def main():
    print(f"Testing Snowflake key pair authentication with corrected account...")
    print(f"Account: {ACCOUNT}")
    print(f"User: {SNOWFLAKE_USER}")
    print(f"Private Key Path: {SNOWFLAKE_PRIVATE_KEY_PATH}")
    
    try:
        # Read the private key
        with open(SNOWFLAKE_PRIVATE_KEY_PATH, "rb") as key_file:
            p_key = key_file.read()
            print(f"Successfully read private key file")
        
        # Try different account formats based on the correct account name
        account_formats = [
            ACCOUNT,                                # Just the account name
            f"{ACCOUNT}.snowflakecomputing.com",    # With domain
            f"AWS_EU_CENTRAL_1.{ACCOUNT}",          # With region
            f"eu-central-1.{ACCOUNT}"               # With region in different format
        ]
        
        for account_format in account_formats:
            print(f"\n=== Testing account format: {account_format} ===")
            
            try:
                # Connect to Snowflake
                conn = snowflake.connector.connect(
                    user=SNOWFLAKE_USER,
                    account=account_format,
                    private_key=p_key,
                    warehouse="MERCURIOS_DEV_WH",
                    database="MERCURIOS_DATA",
                    role="MERCURIOS_DEVELOPER",
                    login_timeout=10  # Shorter timeout for faster testing
                )
                
                # Test the connection
                cursor = conn.cursor()
                cursor.execute("SELECT current_version()")
                version = cursor.fetchone()[0]
                print(f"✅ SUCCESS! Connected with account format: {account_format}")
                print(f"Snowflake version: {version}")
                
                # Show current user and role
                cursor.execute("SELECT current_user(), current_role()")
                user_role = cursor.fetchone()
                print(f"Current user: {user_role[0]}")
                print(f"Current role: {user_role[1]}")
                
                # Close the connection
                cursor.close()
                conn.close()
                print("Connection closed.")
                
                # If we got here, we found a working format
                print(f"\n✅ WORKING ACCOUNT FORMAT: {account_format}")
                print("Update your scripts to use this account format.")
                return account_format
                
            except Exception as e:
                print(f"❌ Failed with format {account_format}: {str(e)[:150]}...")
                continue
        
        print("\n❌ All account formats failed.")
        print("Try the following troubleshooting steps:")
        print("1. Verify the public key was registered correctly in Snowflake")
        print("2. Check if the private key is in the correct format (PKCS8 DER)")
        print("3. Try regenerating the key pair and registering it again")
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    working_format = main()
    if working_format:
        print(f"\nSuccess! Use this account format in your scripts: {working_format}")
        sys.exit(0)
    else:
        sys.exit(1)

#!/usr/bin/env python3
"""
Test script for Snowflake key pair authentication following official documentation.
"""

import os
import sys
import pandas as pd
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

# Configuration
ACCOUNT = "VRXDFZX-ZZ95717"
USER = "JULIUSRECHENBACH"
PRIVATE_KEY_PATH = "/Users/juliusrechenbach/.ssh/snowflake/rsa_key.p8"

def main():
    print(f"Testing Snowflake key pair authentication...")
    print(f"Account: {ACCOUNT}")
    print(f"User: {USER}")
    print(f"Private Key Path: {PRIVATE_KEY_PATH}")
    
    try:
        # Read the private key
        with open(PRIVATE_KEY_PATH, "rb") as key_file:
            p_key = key_file.read()
            print(f"Successfully read private key file")
        
        # Try to connect with different roles
        roles = ["MERCURIOS_DEVELOPER", "MERCURIOS_ADMIN", "MERCURIOS_ANALYST"]
        
        for role in roles:
            print(f"\nTrying to connect with role: {role}")
            try:
                # Connect to Snowflake
                conn = snowflake.connector.connect(
                    user=USER,
                    account=ACCOUNT,
                    private_key=p_key,
                    warehouse="MERCURIOS_DEV_WH",
                    database="MERCURIOS_DATA",
                    role=role
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
                
                # Close the connection
                cursor.close()
                conn.close()
                print("Connection closed.")
                
                # If we got here, we're done
                return True
                
            except Exception as e:
                print(f"❌ Connection failed with role {role}: {e}")
                continue
        
        print("\nAll connection attempts failed.")
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nTroubleshooting steps:")
        print("1. Verify the public key was registered correctly in Snowflake")
        print("2. Check if the private key is in the correct format (PKCS8 DER)")
        print("3. Try regenerating the key pair with the generate_snowflake_key.py script")
        print("4. Ensure the account name is correct")
        sys.exit(1)
    else:
        print("\nKey pair authentication is working correctly!")
        sys.exit(0)

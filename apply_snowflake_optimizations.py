#!/usr/bin/env python3
"""
Script to apply Snowflake performance optimizations from the optimize_snowflake_costs.sql file.
This script reads the SQL commands from the file and executes them in Snowflake.
"""

import os
import sys
import snowflake.connector
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Snowflake credentials
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
    
    # Read private key
    try:
        with open(private_key_path, "rb") as key_file:
            private_key = key_file.read()
            print(f"Successfully read private key from {private_key_path}")
    except Exception as e:
        print(f"Error reading private key: {e}")
        sys.exit(1)
    
    # Read SQL file
    sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "optimize_snowflake_costs.sql")
    try:
        with open(sql_file_path, "r") as f:
            sql_content = f.read()
            print(f"Successfully read SQL file from {sql_file_path}")
    except Exception as e:
        print(f"Error reading SQL file: {e}")
        sys.exit(1)
    
    # Split SQL commands by semicolon
    sql_commands = [cmd.strip() for cmd in sql_content.split(";") if cmd.strip()]
    
    # Connect to Snowflake
    try:
        conn = snowflake.connector.connect(
            user=user,
            account=account,
            private_key=private_key,
            warehouse="MERCURIOS_ADMIN_WH",  # Use admin warehouse for these operations
            role="MERCURIOS_ADMIN"  # Use admin role for these operations
        )
        print("Successfully connected to Snowflake")
        
        # Execute SQL commands
        cursor = conn.cursor()
        for i, cmd in enumerate(sql_commands):
            if cmd.strip():
                print(f"\nExecuting command {i+1}/{len(sql_commands)}:")
                print(f"{cmd[:100]}..." if len(cmd) > 100 else cmd)
                try:
                    cursor.execute(cmd)
                    print("✅ Command executed successfully")
                except Exception as e:
                    print(f"❌ Error executing command: {e}")
        
        # Close connection
        cursor.close()
        conn.close()
        print("\nConnection closed")
        print("\n✅ Snowflake optimizations applied successfully")
        
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

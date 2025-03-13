#!/usr/bin/env python3
"""
Script to execute the Snowflake setup SQL script.
"""
import os
import sys
import getpass
from dotenv import load_dotenv
import snowflake.connector

# Load environment variables
load_dotenv(override=True)

# Get Snowflake credentials from environment variables
account = os.getenv("SNOWFLAKE_ACCOUNT")
user = os.getenv("SNOWFLAKE_USERNAME")
password = os.getenv("SNOWFLAKE_PASSWORD")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
role = os.getenv("SNOWFLAKE_ROLE")

if not all([account, user, password, warehouse]):
    print("Error: Missing required Snowflake credentials in .env file")
    sys.exit(1)

# Ask user which SQL file to execute
print("Which SQL file would you like to execute?")
print("1. create_database_objects.sql (Create database, schemas, and sample tables)")
print("2. setup_fivetran_permissions.sql (Set up Fivetran service account permissions)")
print("3. create_fivetran_user.sql (Create or reset FIVETRAN_USER)")
choice = input("Enter choice (1-3): ")

if choice == '1':
    sql_file = "create_database_objects.sql"
elif choice == '2':
    sql_file = "setup_fivetran_permissions.sql"
elif choice == '3':
    sql_file = "create_fivetran_user.sql"
else:
    print("Invalid choice")
    sys.exit(1)

# Read the SQL script
try:
    with open(sql_file, "r") as f:
        sql_script = f.read()
except FileNotFoundError:
    print(f"Error: SQL file '{sql_file}' not found")
    sys.exit(1)

# Split the script into individual statements
# This is a simple split by semicolon, which works for most SQL but might need refinement
sql_statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]

print(f"\nConnecting to Snowflake with:")
print(f"  Account: {account}")
print(f"  User: {user}")
print(f"  Warehouse: {warehouse}")
print(f"  Role: {role}")

# Connect to Snowflake
try:
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        role=role
    )
    print("Successfully connected to Snowflake!")
except Exception as e:
    print(f"Error connecting to Snowflake: {e}")
    sys.exit(1)

# Execute each statement
cursor = conn.cursor()
print(f"\nExecuting {len(sql_statements)} SQL statements from {sql_file}...")

for i, stmt in enumerate(sql_statements):
    if stmt and not stmt.isspace():
        try:
            print(f"\nExecuting statement {i+1}/{len(sql_statements)}...")
            print(f"SQL: {stmt[:100]}{'...' if len(stmt) > 100 else ''}")
            cursor.execute(stmt)
            if cursor.rowcount >= 0:
                print(f"  Success! Affected {cursor.rowcount} rows.")
            else:
                print("  Success! (No rowcount available)")
                
            # If there are results, display them
            try:
                results = cursor.fetchall()
                if results:
                    print("\nResults:")
                    for row in results[:5]:  # Show at most 5 rows
                        print(f"  {row}")
                    if len(results) > 5:
                        print(f"  ... and {len(results) - 5} more rows")
            except:
                pass  # Not all statements return results
                
        except Exception as e:
            print(f"  Error executing statement: {e}")
            print(f"  Statement was: {stmt[:100]}...")
            # Continue with the next statement

# Close the connection
cursor.close()
conn.close()
print("\nExecution complete. Connection closed.")

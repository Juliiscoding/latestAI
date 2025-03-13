#!/usr/bin/env python3
"""
Query Fivetran metadata to find out what schemas and tables actually exist.
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
            role="ACCOUNTADMIN",
            database=DATABASE
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

def query_fivetran_metadata(conn):
    """Query Fivetran metadata to find out what schemas and tables actually exist."""
    if not conn:
        print("No connection available.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Use Fivetran metadata schema
        print("\nAccessing FIVETRAN_METADATA schema...")
        cursor.execute("USE SCHEMA FIVETRAN_METADATA")
        print("✅ Successfully accessed FIVETRAN_METADATA schema")
        
        # List tables in the schema
        print("\nListing tables in FIVETRAN_METADATA schema...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print("Tables in FIVETRAN_METADATA schema:")
            table_data = []
            for table in tables:
                table_name = table[1]
                table_kind = table[3]
                table_data.append([table_name, table_kind])
            
            print(tabulate(table_data, headers=["Table Name", "Kind"], tablefmt="pretty"))
            
            # For each table, describe its columns
            for table in tables:
                table_name = table[1]
                print(f"\nDescribing columns in {table_name} table...")
                try:
                    cursor.execute(f"DESCRIBE TABLE {table_name}")
                    columns = cursor.fetchall()
                    
                    if columns:
                        print(f"Columns in {table_name} table:")
                        column_data = []
                        for column in columns:
                            column_name = column[0]
                            column_type = column[1]
                            column_data.append([column_name, column_type])
                        
                        print(tabulate(column_data, headers=["Column Name", "Type"], tablefmt="pretty"))
                        
                        # Sample data from each table
                        print(f"\nSample data from {table_name} table:")
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                        rows = cursor.fetchall()
                        
                        if rows:
                            # Get column names
                            col_names = [desc[0] for desc in cursor.description]
                            
                            # Print data
                            print(tabulate(rows, headers=col_names, tablefmt="pretty"))
                        else:
                            print(f"No data found in {table_name} table.")
                    else:
                        print(f"No columns found in {table_name} table.")
                except Exception as e:
                    print(f"❌ Failed to describe {table_name} table: {str(e)}")
        else:
            print("No tables found in FIVETRAN_METADATA schema.")
        
        # List all schemas in the database
        print("\nListing all schemas in MERCURIOS_DATA database...")
        cursor.execute("SHOW SCHEMAS IN DATABASE MERCURIOS_DATA")
        schemas = cursor.fetchall()
        
        if schemas:
            print("Schemas in MERCURIOS_DATA database:")
            schema_data = []
            for schema in schemas:
                schema_name = schema[1]
                schema_owner = schema[5]
                schema_data.append([schema_name, schema_owner])
            
            print(tabulate(schema_data, headers=["Schema Name", "Owner"], tablefmt="pretty"))
        else:
            print("No schemas found in MERCURIOS_DATA database.")
        
        # Get information about the Fivetran service role
        print("\nGetting information about the Fivetran service role...")
        cursor.execute("SHOW ROLES LIKE 'MERCURIOS_FIVETRAN_SERVICE'")
        fivetran_role = cursor.fetchall()
        
        if fivetran_role:
            print("Fivetran service role information:")
            role_data = []
            for role in fivetran_role:
                role_name = role[1]
                role_owner = role[5]
                role_data.append([role_name, role_owner])
            
            print(tabulate(role_data, headers=["Role Name", "Owner"], tablefmt="pretty"))
            
            # Check grants to this role
            print("\nChecking grants to Fivetran service role...")
            cursor.execute("SHOW GRANTS TO ROLE MERCURIOS_FIVETRAN_SERVICE")
            grants = cursor.fetchall()
            
            if grants:
                print("Grants to Fivetran service role:")
                grant_data = []
                for grant in grants:
                    privilege = grant[1]
                    granted_on = grant[2]
                    name = grant[3]
                    grant_data.append([privilege, granted_on, name])
                
                print(tabulate(grant_data, headers=["Privilege", "Granted On", "Name"], tablefmt="pretty"))
            else:
                print("No grants found for Fivetran service role.")
            
            # Check grants of this role
            print("\nChecking grants of Fivetran service role...")
            cursor.execute("SHOW GRANTS OF ROLE MERCURIOS_FIVETRAN_SERVICE")
            grants_of = cursor.fetchall()
            
            if grants_of:
                print("Grants of Fivetran service role:")
                grant_of_data = []
                for grant in grants_of:
                    grantee = grant[1]
                    granted_to = grant[2]
                    grant_of_data.append([grantee, granted_to])
                
                print(tabulate(grant_of_data, headers=["Grantee", "Granted To"], tablefmt="pretty"))
            else:
                print("No grants of Fivetran service role found.")
        else:
            print("Fivetran service role not found.")
    
    except Exception as e:
        print(f"❌ Error querying Fivetran metadata: {str(e)}")
    
    finally:
        cursor.close()

def main():
    """Main function to run the script."""
    print("Querying Fivetran metadata...")
    
    conn = connect_to_snowflake()
    if conn:
        query_fivetran_metadata(conn)
        conn.close()
    else:
        print("Failed to connect to Snowflake. Exiting.")

if __name__ == "__main__":
    main()

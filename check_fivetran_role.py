#!/usr/bin/env python3
"""
Check Fivetran service role in Snowflake for Mercurios AI project.
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

def check_fivetran_role(conn):
    """Check Fivetran service role in Snowflake."""
    if not conn:
        print("No connection available.")
        return
    
    cursor = conn.cursor()
    
    try:
        # List all roles
        print("\nListing all roles in Snowflake account...")
        cursor.execute("SHOW ROLES")
        roles = cursor.fetchall()
        
        if roles:
            print("Roles in Snowflake account:")
            role_data = []
            for role in roles:
                role_name = role[1]
                role_owner = role[5]
                role_data.append([role_name, role_owner])
            
            print(tabulate(role_data, headers=["Role Name", "Owner"], tablefmt="pretty"))
        else:
            print("No roles found.")
        
        # Check for Fivetran service role
        print("\nChecking for Fivetran service role...")
        cursor.execute("SHOW ROLES LIKE '%FIVETRAN%'")
        fivetran_roles = cursor.fetchall()
        
        if fivetran_roles:
            print("Fivetran-related roles found:")
            for role in fivetran_roles:
                print(f"- {role[1]}")
                
                # Check grants to this role
                print(f"\nChecking grants to role {role[1]}...")
                cursor.execute(f"SHOW GRANTS TO ROLE {role[1]}")
                grants = cursor.fetchall()
                
                if grants:
                    print(f"Grants to role {role[1]}:")
                    grant_data = []
                    for grant in grants:
                        privilege = grant[1]
                        granted_on = grant[2]
                        name = grant[3]
                        grant_data.append([privilege, granted_on, name])
                    
                    print(tabulate(grant_data, headers=["Privilege", "Granted On", "Name"], tablefmt="pretty"))
                else:
                    print(f"No grants found for role {role[1]}.")
                
                # Check grants of this role
                print(f"\nChecking grants of role {role[1]}...")
                cursor.execute(f"SHOW GRANTS OF ROLE {role[1]}")
                grants_of = cursor.fetchall()
                
                if grants_of:
                    print(f"Grants of role {role[1]}:")
                    grant_of_data = []
                    for grant in grants_of:
                        grantee = grant[1]
                        granted_to = grant[2]
                        grant_of_data.append([grantee, granted_to])
                    
                    print(tabulate(grant_of_data, headers=["Grantee", "Granted To"], tablefmt="pretty"))
                else:
                    print(f"No grants of role {role[1]} found.")
        else:
            print("No Fivetran-related roles found.")
        
        # Check for share databases
        print("\nChecking for share databases...")
        cursor.execute("SHOW SHARES")
        shares = cursor.fetchall()
        
        if shares:
            print("Shares in Snowflake account:")
            share_data = []
            for share in shares:
                share_name = share[1]
                share_kind = share[2]
                share_data.append([share_name, share_kind])
            
            print(tabulate(share_data, headers=["Share Name", "Kind"], tablefmt="pretty"))
        else:
            print("No shares found.")
        
        # Check for database grants
        print("\nChecking grants on MERCURIOS_DATA database...")
        cursor.execute("SHOW GRANTS ON DATABASE MERCURIOS_DATA")
        db_grants = cursor.fetchall()
        
        if db_grants:
            print("Grants on MERCURIOS_DATA database:")
            db_grant_data = []
            for grant in db_grants:
                privilege = grant[1]
                granted_on = grant[2]
                name = grant[3]
                grantee = grant[4]
                db_grant_data.append([privilege, granted_on, name, grantee])
            
            print(tabulate(db_grant_data, headers=["Privilege", "Granted On", "Name", "Grantee"], tablefmt="pretty"))
        else:
            print("No grants found on MERCURIOS_DATA database.")
        
        # Check for imported privileges
        print("\nChecking imported privileges...")
        try:
            cursor.execute("SHOW GRANTS OF SHARE FIVETRAN_SHARE")
            imported_grants = cursor.fetchall()
            
            if imported_grants:
                print("Imported privileges from FIVETRAN_SHARE:")
                imported_grant_data = []
                for grant in imported_grants:
                    privilege = grant[1]
                    granted_on = grant[2]
                    name = grant[3]
                    imported_grant_data.append([privilege, granted_on, name])
                
                print(tabulate(imported_grant_data, headers=["Privilege", "Granted On", "Name"], tablefmt="pretty"))
            else:
                print("No imported privileges found from FIVETRAN_SHARE.")
        except Exception as e:
            print(f"❌ Error checking imported privileges: {str(e)}")
    
    except Exception as e:
        print(f"❌ Error checking Fivetran role: {str(e)}")
    
    finally:
        cursor.close()

def main():
    """Main function to run the script."""
    print("Checking Fivetran service role in Snowflake...")
    
    conn = connect_to_snowflake()
    if conn:
        check_fivetran_role(conn)
        conn.close()
    else:
        print("Failed to connect to Snowflake. Exiting.")

if __name__ == "__main__":
    main()

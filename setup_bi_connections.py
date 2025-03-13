#!/usr/bin/env python3
"""
BI Connection Setup Script for Mercurios.ai

This script automates the process of setting up connections between Snowflake and BI tools
like Tableau, Power BI, or Looker. It creates the necessary roles, grants appropriate
permissions, and generates connection strings for the BI tools.
"""

import os
import sys
import argparse
import json
import uuid
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")

def connect_to_snowflake():
    """Establish connection to Snowflake using password authentication"""
    try:
        conn = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse="MERCURIOS_ADMIN_WH",
            role="MERCURIOS_ADMIN"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        sys.exit(1)

def setup_tableau_connection(tenant_name=None):
    """Set up connection for Tableau"""
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        # Create a role for Tableau
        role_name = f"MERCURIOS_TABLEAU_ROLE" if not tenant_name else f"MERCURIOS_{tenant_name.upper()}_TABLEAU_ROLE"
        user_name = f"TABLEAU_USER" if not tenant_name else f"TABLEAU_{tenant_name.upper()}_USER"
        password = str(uuid.uuid4())
        
        # Begin transaction
        cursor.execute("BEGIN")
        
        # Create role
        cursor.execute(f"CREATE ROLE IF NOT EXISTS {role_name}")
        
        # Grant privileges
        cursor.execute(f"""
        GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE {role_name};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH TO ROLE {role_name};
        """)
        
        # Create user
        cursor.execute(f"""
        CREATE USER IF NOT EXISTS {user_name}
        PASSWORD = '{password}'
        DEFAULT_ROLE = {role_name}
        DEFAULT_WAREHOUSE = MERCURIOS_ANALYTICS_WH;
        """)
        
        # Grant role to user
        cursor.execute(f"GRANT ROLE {role_name} TO USER {user_name}")
        
        # If tenant-specific, add row-level security
        if tenant_name:
            # Get tenant ID
            cursor.execute(f"""
            SELECT TENANT_ID FROM MERCURIOS_DATA.STANDARD.TENANTS
            WHERE TENANT_NAME = '{tenant_name}' AND STATUS = 'ACTIVE'
            """)
            result = cursor.fetchone()
            if not result:
                raise Exception(f"Tenant {tenant_name} not found or not active")
                
            tenant_id = result[0]
            
            # Create row access policies
            cursor.execute(f"""
            CREATE OR REPLACE ROW ACCESS POLICY tableau_tenant_isolation ON MERCURIOS_DATA.ANALYTICS.INVENTORY_ANALYTICS
            AS (tenant_id VARCHAR) TO ROLE {role_name}
            USING (tenant_id = '{tenant_id}');
            """)
        
        # Commit transaction
        cursor.execute("COMMIT")
        
        # Generate connection details
        connection_details = {
            "type": "Tableau",
            "server": f"{SNOWFLAKE_ACCOUNT}.snowflakecomputing.com",
            "username": user_name,
            "password": password,  # Note: In production, use a more secure way to handle passwords
            "role": role_name,
            "warehouse": "MERCURIOS_ANALYTICS_WH",
            "database": "MERCURIOS_DATA",
            "schema": "ANALYTICS"
        }
        
        # Save connection details to file
        output_file = f"tableau_connection{'_' + tenant_name if tenant_name else ''}.json"
        with open(output_file, "w") as f:
            json.dump(connection_details, f, indent=4)
            
        print(f"Tableau connection set up successfully. Details saved to {output_file}")
        print(f"User: {user_name}")
        print(f"Role: {role_name}")
        
    except Exception as e:
        # Rollback in case of error
        cursor.execute("ROLLBACK")
        print(f"Error setting up Tableau connection: {e}")
    finally:
        cursor.close()
        conn.close()

def setup_powerbi_connection(tenant_name=None):
    """Set up connection for Power BI"""
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        # Create a role for Power BI
        role_name = f"MERCURIOS_POWERBI_ROLE" if not tenant_name else f"MERCURIOS_{tenant_name.upper()}_POWERBI_ROLE"
        user_name = f"POWERBI_USER" if not tenant_name else f"POWERBI_{tenant_name.upper()}_USER"
        password = str(uuid.uuid4())
        
        # Begin transaction
        cursor.execute("BEGIN")
        
        # Create role
        cursor.execute(f"CREATE ROLE IF NOT EXISTS {role_name}")
        
        # Grant privileges
        cursor.execute(f"""
        GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE {role_name};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH TO ROLE {role_name};
        """)
        
        # Create user
        cursor.execute(f"""
        CREATE USER IF NOT EXISTS {user_name}
        PASSWORD = '{password}'
        DEFAULT_ROLE = {role_name}
        DEFAULT_WAREHOUSE = MERCURIOS_ANALYTICS_WH;
        """)
        
        # Grant role to user
        cursor.execute(f"GRANT ROLE {role_name} TO USER {user_name}")
        
        # If tenant-specific, add row-level security
        if tenant_name:
            # Get tenant ID
            cursor.execute(f"""
            SELECT TENANT_ID FROM MERCURIOS_DATA.STANDARD.TENANTS
            WHERE TENANT_NAME = '{tenant_name}' AND STATUS = 'ACTIVE'
            """)
            result = cursor.fetchone()
            if not result:
                raise Exception(f"Tenant {tenant_name} not found or not active")
                
            tenant_id = result[0]
            
            # Create row access policies
            cursor.execute(f"""
            CREATE OR REPLACE ROW ACCESS POLICY powerbi_tenant_isolation ON MERCURIOS_DATA.ANALYTICS.INVENTORY_ANALYTICS
            AS (tenant_id VARCHAR) TO ROLE {role_name}
            USING (tenant_id = '{tenant_id}');
            """)
        
        # Commit transaction
        cursor.execute("COMMIT")
        
        # Generate connection details
        connection_details = {
            "type": "Power BI",
            "server": f"{SNOWFLAKE_ACCOUNT}.snowflakecomputing.com",
            "username": user_name,
            "password": password,  # Note: In production, use a more secure way to handle passwords
            "role": role_name,
            "warehouse": "MERCURIOS_ANALYTICS_WH",
            "database": "MERCURIOS_DATA",
            "schema": "ANALYTICS"
        }
        
        # Save connection details to file
        output_file = f"powerbi_connection{'_' + tenant_name if tenant_name else ''}.json"
        with open(output_file, "w") as f:
            json.dump(connection_details, f, indent=4)
            
        print(f"Power BI connection set up successfully. Details saved to {output_file}")
        print(f"User: {user_name}")
        print(f"Role: {role_name}")
        
    except Exception as e:
        # Rollback in case of error
        cursor.execute("ROLLBACK")
        print(f"Error setting up Power BI connection: {e}")
    finally:
        cursor.close()
        conn.close()

def setup_looker_connection(tenant_name=None):
    """Set up connection for Looker"""
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        # Create a role for Looker
        role_name = f"MERCURIOS_LOOKER_ROLE" if not tenant_name else f"MERCURIOS_{tenant_name.upper()}_LOOKER_ROLE"
        user_name = f"LOOKER_USER" if not tenant_name else f"LOOKER_{tenant_name.upper()}_USER"
        password = str(uuid.uuid4())
        
        # Begin transaction
        cursor.execute("BEGIN")
        
        # Create role
        cursor.execute(f"CREATE ROLE IF NOT EXISTS {role_name}")
        
        # Grant privileges
        cursor.execute(f"""
        GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE {role_name};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {role_name};
        GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.MARTS TO ROLE {role_name};
        GRANT USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH TO ROLE {role_name};
        """)
        
        # Create user
        cursor.execute(f"""
        CREATE USER IF NOT EXISTS {user_name}
        PASSWORD = '{password}'
        DEFAULT_ROLE = {role_name}
        DEFAULT_WAREHOUSE = MERCURIOS_ANALYTICS_WH;
        """)
        
        # Grant role to user
        cursor.execute(f"GRANT ROLE {role_name} TO USER {user_name}")
        
        # If tenant-specific, add row-level security
        if tenant_name:
            # Get tenant ID
            cursor.execute(f"""
            SELECT TENANT_ID FROM MERCURIOS_DATA.STANDARD.TENANTS
            WHERE TENANT_NAME = '{tenant_name}' AND STATUS = 'ACTIVE'
            """)
            result = cursor.fetchone()
            if not result:
                raise Exception(f"Tenant {tenant_name} not found or not active")
                
            tenant_id = result[0]
            
            # Create row access policies
            cursor.execute(f"""
            CREATE OR REPLACE ROW ACCESS POLICY looker_tenant_isolation ON MERCURIOS_DATA.ANALYTICS.INVENTORY_ANALYTICS
            AS (tenant_id VARCHAR) TO ROLE {role_name}
            USING (tenant_id = '{tenant_id}');
            """)
        
        # Commit transaction
        cursor.execute("COMMIT")
        
        # Generate connection details
        connection_details = {
            "type": "Looker",
            "server": f"{SNOWFLAKE_ACCOUNT}.snowflakecomputing.com",
            "username": user_name,
            "password": password,  # Note: In production, use a more secure way to handle passwords
            "role": role_name,
            "warehouse": "MERCURIOS_ANALYTICS_WH",
            "database": "MERCURIOS_DATA",
            "schema": "ANALYTICS"
        }
        
        # Save connection details to file
        output_file = f"looker_connection{'_' + tenant_name if tenant_name else ''}.json"
        with open(output_file, "w") as f:
            json.dump(connection_details, f, indent=4)
            
        print(f"Looker connection set up successfully. Details saved to {output_file}")
        print(f"User: {user_name}")
        print(f"Role: {role_name}")
        
    except Exception as e:
        # Rollback in case of error
        cursor.execute("ROLLBACK")
        print(f"Error setting up Looker connection: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description="BI Connection Setup Tool for Mercurios.ai")
    parser.add_argument("--tool", required=True, choices=["tableau", "powerbi", "looker"], help="BI tool to set up")
    parser.add_argument("--tenant", help="Optional tenant name for tenant-specific connection")
    
    args = parser.parse_args()
    
    if args.tool == "tableau":
        setup_tableau_connection(args.tenant)
    elif args.tool == "powerbi":
        setup_powerbi_connection(args.tenant)
    elif args.tool == "looker":
        setup_looker_connection(args.tenant)

if __name__ == "__main__":
    main()

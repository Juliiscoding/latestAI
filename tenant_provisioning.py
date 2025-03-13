#!/usr/bin/env python3
"""
Tenant Provisioning Script for Mercurios.ai

This script automates the process of onboarding new tenants to the Mercurios.ai platform.
It creates the necessary database objects, sets up security, and configures monitoring.
"""

import os
import sys
import argparse
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

def provision_tenant(tenant_name, tenant_display_name, tenant_admin_email):
    """Provision a new tenant in the Mercurios.ai platform"""
    # Generate a unique tenant ID
    tenant_id = str(uuid.uuid4())
    
    # Connect to Snowflake
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute("BEGIN")
        
        # 1. Create tenant record in tenant management table
        cursor.execute(f"""
        INSERT INTO MERCURIOS_DATA.STANDARD.TENANTS (
            TENANT_ID, 
            TENANT_NAME, 
            TENANT_DISPLAY_NAME, 
            TENANT_ADMIN_EMAIL,
            CREATED_AT,
            STATUS
        ) VALUES (
            '{tenant_id}',
            '{tenant_name}',
            '{tenant_display_name}',
            '{tenant_admin_email}',
            CURRENT_TIMESTAMP(),
            'ACTIVE'
        )
        """)
        
        # 2. Set up row-level security for the tenant
        # Create a role for the tenant
        tenant_role = f"TENANT_{tenant_name.upper()}_ROLE"
        cursor.execute(f"CREATE ROLE IF NOT EXISTS {tenant_role}")
        
        # Grant necessary privileges to the tenant role
        cursor.execute(f"""
        GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE {tenant_role};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE {tenant_role};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.STANDARD TO ROLE {tenant_role};
        GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE {tenant_role};
        GRANT USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH TO ROLE {tenant_role};
        """)
        
        # 3. Create row access policies for tenant isolation
        cursor.execute(f"""
        CREATE OR REPLACE ROW ACCESS POLICY tenant_isolation_policy ON MERCURIOS_DATA.STANDARD.INVENTORY
        AS (tenant_id VARCHAR) TO ROLE {tenant_role}
        USING (tenant_id = '{tenant_id}');
        
        CREATE OR REPLACE ROW ACCESS POLICY tenant_isolation_policy ON MERCURIOS_DATA.STANDARD.SALES
        AS (tenant_id VARCHAR) TO ROLE {tenant_role}
        USING (tenant_id = '{tenant_id}');
        
        CREATE OR REPLACE ROW ACCESS POLICY tenant_isolation_policy ON MERCURIOS_DATA.STANDARD.ARTICLES
        AS (tenant_id VARCHAR) TO ROLE {tenant_role}
        USING (tenant_id = '{tenant_id}');
        """)
        
        # 4. Set up monitoring for the tenant
        cursor.execute(f"""
        CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.{tenant_name.upper()}_USAGE AS
        SELECT
            QUERY_ID,
            SESSION_ID,
            USER_NAME,
            ROLE_NAME,
            WAREHOUSE_NAME,
            DATABASE_NAME,
            SCHEMA_NAME,
            QUERY_TEXT,
            START_TIME,
            END_TIME,
            TOTAL_ELAPSED_TIME,
            BYTES_SCANNED,
            ROWS_PRODUCED,
            CREDITS_USED_CLOUD_SERVICES
        FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE ROLE_NAME = '{tenant_role}'
        AND START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
        ORDER BY START_TIME DESC;
        """)
        
        # 5. Commit the transaction
        cursor.execute("COMMIT")
        
        print(f"Successfully provisioned tenant: {tenant_display_name}")
        print(f"Tenant ID: {tenant_id}")
        print(f"Tenant Role: {tenant_role}")
        
        return {
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "tenant_role": tenant_role,
            "status": "ACTIVE"
        }
        
    except Exception as e:
        # Rollback in case of error
        cursor.execute("ROLLBACK")
        print(f"Error provisioning tenant: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def list_tenants():
    """List all tenants in the system"""
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        SELECT 
            TENANT_ID, 
            TENANT_NAME, 
            TENANT_DISPLAY_NAME, 
            TENANT_ADMIN_EMAIL,
            CREATED_AT,
            STATUS
        FROM MERCURIOS_DATA.STANDARD.TENANTS
        ORDER BY CREATED_AT DESC
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("No tenants found")
            return
            
        print("\nTenant List:")
        print("-" * 80)
        print(f"{'TENANT_ID':<36} | {'TENANT_NAME':<20} | {'STATUS':<10} | {'ADMIN_EMAIL':<30}")
        print("-" * 80)
        
        for row in results:
            tenant_id, tenant_name, _, admin_email, _, status = row
            print(f"{tenant_id:<36} | {tenant_name:<20} | {status:<10} | {admin_email:<30}")
            
    except Exception as e:
        print(f"Error listing tenants: {e}")
    finally:
        cursor.close()
        conn.close()

def deactivate_tenant(tenant_name):
    """Deactivate a tenant"""
    conn = connect_to_snowflake()
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute("BEGIN")
        
        # Update tenant status
        cursor.execute(f"""
        UPDATE MERCURIOS_DATA.STANDARD.TENANTS
        SET STATUS = 'INACTIVE', UPDATED_AT = CURRENT_TIMESTAMP()
        WHERE TENANT_NAME = '{tenant_name}'
        """)
        
        # Revoke privileges from tenant role
        tenant_role = f"TENANT_{tenant_name.upper()}_ROLE"
        cursor.execute(f"""
        REVOKE USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH FROM ROLE {tenant_role};
        """)
        
        # Commit the transaction
        cursor.execute("COMMIT")
        
        print(f"Successfully deactivated tenant: {tenant_name}")
        
    except Exception as e:
        # Rollback in case of error
        cursor.execute("ROLLBACK")
        print(f"Error deactivating tenant: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description="Tenant Provisioning Tool for Mercurios.ai")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Provision tenant command
    provision_parser = subparsers.add_parser("provision", help="Provision a new tenant")
    provision_parser.add_argument("--name", required=True, help="Tenant name (lowercase, no spaces)")
    provision_parser.add_argument("--display-name", required=True, help="Display name for the tenant")
    provision_parser.add_argument("--admin-email", required=True, help="Email address for tenant admin")
    
    # List tenants command
    list_parser = subparsers.add_parser("list", help="List all tenants")
    
    # Deactivate tenant command
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate a tenant")
    deactivate_parser.add_argument("--name", required=True, help="Tenant name to deactivate")
    
    args = parser.parse_args()
    
    if args.command == "provision":
        provision_tenant(args.name, args.display_name, args.admin_email)
    elif args.command == "list":
        list_tenants()
    elif args.command == "deactivate":
        deactivate_tenant(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

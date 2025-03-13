#!/usr/bin/env python
import json
import os
import snowflake.connector
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load Snowflake configuration from JSON file."""
    try:
        with open('snowflake_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise

def get_fivetran_config():
    """Generate Fivetran connection configuration for Snowflake."""
    config = load_config()
    
    # Connect to Snowflake
    logger.info("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        user=config['username'],
        password=config['password'],
        account=config['account'],
        role=config['role']
    )
    
    try:
        # Get account URL
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_ACCOUNT()")
        account_name = cursor.fetchone()[0]
        
        # Get region info
        cursor.execute("SELECT CURRENT_REGION()")
        region = cursor.fetchone()[0]
        
        # Check if Fivetran user exists
        cursor.execute("SHOW USERS LIKE 'FIVETRAN_USER'")
        fivetran_user_exists = cursor.fetchall()
        
        # Check if Fivetran role exists
        cursor.execute("SHOW ROLES LIKE 'MERCURIOS_FIVETRAN_SERVICE'")
        fivetran_role_exists = cursor.fetchall()
        
        # Format the Snowflake account URL
        account_url = f"{account_name.lower()}.snowflakecomputing.com"
        
        # Get database info
        cursor.execute("SHOW DATABASES LIKE 'MERCURIOS_DATA'")
        database_info = cursor.fetchall()
        
        # Print configuration information
        print("\n=== Fivetran-Snowflake Connection Configuration ===")
        print(f"Host: {account_url}")
        print(f"Port: 443")
        print(f"User: {'FIVETRAN_USER' if fivetran_user_exists else 'Not created yet'}")
        print(f"Database: {config['database']}")
        print(f"Role: {'MERCURIOS_FIVETRAN_SERVICE' if fivetran_role_exists else 'Not created yet'}")
        print(f"Warehouse: {config['warehouse']}")
        print(f"Schema: {config['schema']}")
        print("\nAuthentication Method: KEY_PAIR (recommended) or PASSWORD")
        
        print("\n=== Additional Configuration Parameters ===")
        print("Make sure these Snowflake parameters are set to FALSE:")
        print("- PREVENT_LOAD_FROM_INLINE_URL")
        print("- REQUIRE_STORAGE_INTEGRATION_FOR_STAGE_OPERATION")
        print("If preserving source naming, set QUOTED_IDENTIFIERS_IGNORE_CASE to FALSE")
        
        # Generate SQL to check/set these parameters
        print("\n=== SQL to verify parameter settings ===")
        print("SHOW PARAMETERS LIKE 'PREVENT_LOAD_FROM_INLINE_URL' IN ACCOUNT;")
        print("SHOW PARAMETERS LIKE 'REQUIRE_STORAGE_INTEGRATION_FOR_STAGE_OPERATION' IN ACCOUNT;")
        print("SHOW PARAMETERS LIKE 'QUOTED_IDENTIFIERS_IGNORE_CASE' IN ACCOUNT;")
        
        # Generate SQL to set these parameters if needed
        print("\n=== SQL to set required parameters ===")
        print("ALTER ACCOUNT SET PREVENT_LOAD_FROM_INLINE_URL = FALSE;")
        print("ALTER ACCOUNT SET REQUIRE_STORAGE_INTEGRATION_FOR_STAGE_OPERATION = FALSE;")
        print("ALTER ACCOUNT SET QUOTED_IDENTIFIERS_IGNORE_CASE = FALSE;")
        
        # If Fivetran user doesn't exist, provide SQL to create it
        if not fivetran_user_exists:
            print("\n=== SQL to create Fivetran user ===")
            print("CREATE USER FIVETRAN_USER PASSWORD='<strong_password>' DEFAULT_ROLE=MERCURIOS_FIVETRAN_SERVICE;")
            print("GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER FIVETRAN_USER;")
        
    finally:
        conn.close()
        logger.info("Connection closed")

if __name__ == "__main__":
    get_fivetran_config()

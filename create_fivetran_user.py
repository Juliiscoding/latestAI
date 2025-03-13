#!/usr/bin/env python
import json
import os
import snowflake.connector
import logging
import secrets
import string

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

def generate_strong_password(length=16):
    """Generate a strong random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_fivetran_user():
    """Create a Fivetran user in Snowflake with appropriate permissions."""
    config = load_config()
    
    # Generate a strong password
    password = generate_strong_password()
    
    # Connect to Snowflake
    logger.info("Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        user=config['username'],
        password=config['password'],
        account=config['account'],
        role=config['role']
    )
    
    try:
        cursor = conn.cursor()
        
        # Check if Fivetran user already exists
        cursor.execute("SHOW USERS LIKE 'FIVETRAN_USER'")
        user_exists = len(cursor.fetchall()) > 0
        
        if user_exists:
            logger.info("FIVETRAN_USER already exists. Resetting password...")
            cursor.execute(f"ALTER USER FIVETRAN_USER SET PASSWORD = '{password}'")
        else:
            logger.info("Creating FIVETRAN_USER...")
            cursor.execute(f"CREATE USER FIVETRAN_USER PASSWORD='{password}' DEFAULT_ROLE=MERCURIOS_FIVETRAN_SERVICE")
            cursor.execute("GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER FIVETRAN_USER")
        
        # Set required account parameters
        logger.info("Setting required account parameters...")
        cursor.execute("ALTER ACCOUNT SET PREVENT_LOAD_FROM_INLINE_URL = FALSE")
        cursor.execute("ALTER ACCOUNT SET REQUIRE_STORAGE_INTEGRATION_FOR_STAGE_OPERATION = FALSE")
        cursor.execute("ALTER ACCOUNT SET QUOTED_IDENTIFIERS_IGNORE_CASE = FALSE")
        
        # Save Fivetran configuration to a file
        fivetran_config = {
            "host": f"{conn.account.lower()}.snowflakecomputing.com",
            "port": 443,
            "user": "FIVETRAN_USER",
            "password": password,  # Note: In production, use a more secure method to handle this
            "database": config['database'],
            "schema": config['schema'],
            "warehouse": config['warehouse'],
            "role": "MERCURIOS_FIVETRAN_SERVICE"
        }
        
        with open('fivetran_config.json', 'w') as f:
            json.dump(fivetran_config, f, indent=4)
        
        logger.info("Fivetran configuration saved to fivetran_config.json")
        
        # Print configuration information (without password)
        print("\n=== Fivetran-Snowflake Connection Configuration ===")
        print(f"Host: {fivetran_config['host']}")
        print(f"Port: {fivetran_config['port']}")
        print(f"User: {fivetran_config['user']}")
        print(f"Database: {fivetran_config['database']}")
        print(f"Schema: {fivetran_config['schema']}")
        print(f"Warehouse: {fivetran_config['warehouse']}")
        print(f"Role: {fivetran_config['role']}")
        print(f"\nPassword has been saved to fivetran_config.json")
        print("\nUse these details to configure your Fivetran connection to Snowflake.")
        
    finally:
        conn.close()
        logger.info("Connection closed")

if __name__ == "__main__":
    create_fivetran_user()

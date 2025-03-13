#!/usr/bin/env python3
"""
Snowflake Setup Script for Mercurios.ai

This script sets up Snowflake as a scalable, multi-tenant data warehouse for Mercurios.ai.
It creates warehouses, databases, schemas, roles, and users according to the architecture.
"""

import json
import os
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path):
    """Load Snowflake configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        raise

def execute_query(conn, query, description=None):
    """Execute a SQL query on Snowflake and log the result."""
    cursor = conn.cursor()
    if description:
        logger.info(f"Executing: {description}")
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        if description:
            logger.info(f"Successfully executed: {description}")
        return result
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise
    finally:
        cursor.close()

def execute_script(conn, script_path):
    """Execute a SQL script file"""
    with open(script_path, 'r') as f:
        sql_commands = f.read()
    
    # Split the script into individual commands
    commands = sql_commands.split(';')
    
    cursor = conn.cursor()
    results = []
    
    for command in commands:
        # Skip empty commands
        if command.strip() == '':
            continue
            
        logger.info(f"Executing: {command.strip()[:100]}...")
        try:
            cursor.execute(command)
            result = cursor.fetchall() if cursor.description else None
            results.append(result)
            logger.info("Success!")
        except Exception as e:
            logger.error(f"Error executing command: {e}")
    
    cursor.close()
    return results

def setup_warehouses(conn):
    """Set up separate warehouses for different workloads."""
    warehouses = [
        {
            "name": "MERCURIOS_ADMIN_WH",
            "size": "XSMALL",
            "auto_suspend": 60,
            "description": "Administrative warehouse for setup and maintenance"
        },
        {
            "name": "MERCURIOS_LOADING_WH",
            "size": "MEDIUM",
            "auto_suspend": 300,
            "description": "ETL/Loading warehouse for data ingestion"
        },
        {
            "name": "MERCURIOS_ANALYTICS_WH",
            "size": "LARGE",
            "auto_suspend": 600,
            "description": "Analytics warehouse for reporting and dashboards"
        },
        {
            "name": "MERCURIOS_DEV_WH",
            "size": "SMALL",
            "auto_suspend": 120,
            "description": "Development warehouse for testing and development"
        }
    ]
    
    for wh in warehouses:
        query = f"""
        CREATE WAREHOUSE IF NOT EXISTS {wh['name']}
          WITH WAREHOUSE_SIZE = '{wh['size']}'
          AUTO_SUSPEND = {wh['auto_suspend']}
          AUTO_RESUME = TRUE
          INITIALLY_SUSPENDED = TRUE
          COMMENT = '{wh['description']}';
        """
        execute_query(conn, query, f"Creating warehouse: {wh['name']}")

def setup_database_and_schemas(conn):
    """Set up the database and schemas for multi-tenant architecture."""
    # Create main database
    execute_query(
        conn,
        "CREATE DATABASE IF NOT EXISTS MERCURIOS_DATA;",
        "Creating main database: MERCURIOS_DATA"
    )
    
    # Create schemas
    schemas = [
        {"name": "RAW", "description": "Landing zone for Fivetran data"},
        {"name": "STANDARD", "description": "Standardized and cleaned data"},
        {"name": "ANALYTICS", "description": "Analytics-ready data for reporting"},
        {"name": "TENANT_CUSTOMIZATIONS", "description": "Customer-specific customizations"}
    ]
    
    for schema in schemas:
        query = f"""
        USE DATABASE MERCURIOS_DATA;
        CREATE SCHEMA IF NOT EXISTS {schema['name']} COMMENT = '{schema['description']}';
        """
        execute_query(conn, query, f"Creating schema: {schema['name']}")

def setup_roles_and_access_control(conn):
    """Set up roles and access control for multi-tenant security."""
    # Create roles
    roles = [
        "MERCURIOS_ADMIN",
        "MERCURIOS_ANALYST",
        "MERCURIOS_DEVELOPER",
        "MERCURIOS_FIVETRAN_SERVICE",
        "MERCURIOS_APP_SERVICE"
    ]
    
    for role in roles:
        execute_query(
            conn,
            f"CREATE ROLE IF NOT EXISTS {role};",
            f"Creating role: {role}"
        )
    
    # Grant warehouse access
    warehouse_grants = [
        {"role": "MERCURIOS_FIVETRAN_SERVICE", "warehouse": "MERCURIOS_LOADING_WH"},
        {"role": "MERCURIOS_ANALYST", "warehouse": "MERCURIOS_ANALYTICS_WH"},
        {"role": "MERCURIOS_APP_SERVICE", "warehouse": "MERCURIOS_ANALYTICS_WH"},
        {"role": "MERCURIOS_DEVELOPER", "warehouse": "MERCURIOS_DEV_WH"},
        {"role": "MERCURIOS_ADMIN", "warehouse": "MERCURIOS_ADMIN_WH"},
        {"role": "MERCURIOS_ADMIN", "warehouse": "MERCURIOS_LOADING_WH"},
        {"role": "MERCURIOS_ADMIN", "warehouse": "MERCURIOS_ANALYTICS_WH"},
        {"role": "MERCURIOS_ADMIN", "warehouse": "MERCURIOS_DEV_WH"}
    ]
    
    for grant in warehouse_grants:
        execute_query(
            conn,
            f"GRANT USAGE ON WAREHOUSE {grant['warehouse']} TO ROLE {grant['role']};",
            f"Granting {grant['role']} usage on {grant['warehouse']}"
        )
    
    # Grant database access to all roles
    for role in roles:
        execute_query(
            conn,
            f"GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE {role};",
            f"Granting {role} usage on MERCURIOS_DATA database"
        )
    
    # Grant schema access
    schema_grants = [
        {"role": "MERCURIOS_FIVETRAN_SERVICE", "schema": "RAW", "privileges": "USAGE, CREATE TABLE, INSERT, UPDATE, DELETE"},
        {"role": "MERCURIOS_ADMIN", "schema": "RAW", "privileges": "ALL"},
        {"role": "MERCURIOS_ADMIN", "schema": "STANDARD", "privileges": "ALL"},
        {"role": "MERCURIOS_ADMIN", "schema": "ANALYTICS", "privileges": "ALL"},
        {"role": "MERCURIOS_ADMIN", "schema": "TENANT_CUSTOMIZATIONS", "privileges": "ALL"},
        {"role": "MERCURIOS_DEVELOPER", "schema": "RAW", "privileges": "USAGE, SELECT"},
        {"role": "MERCURIOS_DEVELOPER", "schema": "STANDARD", "privileges": "USAGE, CREATE TABLE, SELECT, INSERT, UPDATE, DELETE"},
        {"role": "MERCURIOS_DEVELOPER", "schema": "ANALYTICS", "privileges": "USAGE, CREATE TABLE, SELECT, INSERT, UPDATE, DELETE"},
        {"role": "MERCURIOS_DEVELOPER", "schema": "TENANT_CUSTOMIZATIONS", "privileges": "USAGE, CREATE TABLE, SELECT, INSERT, UPDATE, DELETE"},
        {"role": "MERCURIOS_ANALYST", "schema": "STANDARD", "privileges": "USAGE, SELECT"},
        {"role": "MERCURIOS_ANALYST", "schema": "ANALYTICS", "privileges": "USAGE, SELECT"},
        {"role": "MERCURIOS_APP_SERVICE", "schema": "STANDARD", "privileges": "USAGE, SELECT"},
        {"role": "MERCURIOS_APP_SERVICE", "schema": "ANALYTICS", "privileges": "USAGE, SELECT"}
    ]
    
    for grant in schema_grants:
        execute_query(
            conn,
            f"GRANT {grant['privileges']} ON SCHEMA MERCURIOS_DATA.{grant['schema']} TO ROLE {grant['role']};",
            f"Granting {grant['role']} {grant['privileges']} on {grant['schema']} schema"
        )
    
    # Grant future privileges
    future_grants = [
        {"role": "MERCURIOS_FIVETRAN_SERVICE", "schema": "RAW", "object_type": "TABLE", "privileges": "INSERT, UPDATE, DELETE"},
        {"role": "MERCURIOS_ADMIN", "schema": "RAW", "object_type": "TABLE", "privileges": "ALL"},
        {"role": "MERCURIOS_ADMIN", "schema": "STANDARD", "object_type": "TABLE", "privileges": "ALL"},
        {"role": "MERCURIOS_ADMIN", "schema": "ANALYTICS", "object_type": "TABLE", "privileges": "ALL"},
        {"role": "MERCURIOS_ADMIN", "schema": "TENANT_CUSTOMIZATIONS", "object_type": "TABLE", "privileges": "ALL"},
        {"role": "MERCURIOS_DEVELOPER", "schema": "RAW", "object_type": "TABLE", "privileges": "SELECT"},
        {"role": "MERCURIOS_DEVELOPER", "schema": "STANDARD", "object_type": "TABLE", "privileges": "SELECT, INSERT, UPDATE, DELETE"},
        {"role": "MERCURIOS_DEVELOPER", "schema": "ANALYTICS", "object_type": "TABLE", "privileges": "SELECT, INSERT, UPDATE, DELETE"},
        {"role": "MERCURIOS_ANALYST", "schema": "STANDARD", "object_type": "TABLE", "privileges": "SELECT"},
        {"role": "MERCURIOS_ANALYST", "schema": "ANALYTICS", "object_type": "TABLE", "privileges": "SELECT"},
        {"role": "MERCURIOS_APP_SERVICE", "schema": "STANDARD", "object_type": "TABLE", "privileges": "SELECT"},
        {"role": "MERCURIOS_APP_SERVICE", "schema": "ANALYTICS", "object_type": "TABLE", "privileges": "SELECT"}
    ]
    
    for grant in future_grants:
        execute_query(
            conn,
            f"GRANT {grant['privileges']} ON FUTURE {grant['object_type']}S IN SCHEMA MERCURIOS_DATA.{grant['schema']} TO ROLE {grant['role']};",
            f"Granting {grant['role']} {grant['privileges']} on future {grant['object_type']}s in {grant['schema']} schema"
        )

def create_service_users(conn, fivetran_password, app_password):
    """Create service users for Fivetran and the application."""
    # Create Fivetran service user
    execute_query(
        conn,
        f"""
        CREATE USER IF NOT EXISTS FIVETRAN_SERVICE
          PASSWORD = '{fivetran_password}'
          DEFAULT_ROLE = MERCURIOS_FIVETRAN_SERVICE
          DEFAULT_WAREHOUSE = MERCURIOS_LOADING_WH
          COMMENT = 'Service account for Fivetran data loading';
        
        GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER FIVETRAN_SERVICE;
        """,
        "Creating Fivetran service user"
    )
    
    # Create application service user
    execute_query(
        conn,
        f"""
        CREATE USER IF NOT EXISTS APP_SERVICE
          PASSWORD = '{app_password}'
          DEFAULT_ROLE = MERCURIOS_APP_SERVICE
          DEFAULT_WAREHOUSE = MERCURIOS_ANALYTICS_WH
          COMMENT = 'Service account for application access';
        
        GRANT ROLE MERCURIOS_APP_SERVICE TO USER APP_SERVICE;
        """,
        "Creating application service user"
    )

def setup_multi_tenant_tables(conn):
    """Create example multi-tenant tables with row-level security."""
    # Create tenant mapping table
    execute_query(
        conn,
        """
        USE DATABASE MERCURIOS_DATA;
        USE SCHEMA STANDARD;
        
        CREATE TABLE IF NOT EXISTS TENANT_USER_MAPPING (
            TENANT_ID VARCHAR NOT NULL,
            USER_ROLE VARCHAR NOT NULL,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (TENANT_ID, USER_ROLE)
        );
        """,
        "Creating tenant user mapping table"
    )
    
    # Create example multi-tenant tables
    tables = [
        {
            "name": "ARTICLES",
            "columns": """
                TENANT_ID VARCHAR NOT NULL,
                ARTICLE_ID VARCHAR NOT NULL,
                ARTICLE_NUMBER VARCHAR,
                NAME VARCHAR,
                DESCRIPTION VARCHAR,
                CATEGORY VARCHAR,
                BRAND VARCHAR,
                SUPPLIER VARCHAR,
                PURCHASE_PRICE FLOAT,
                SELLING_PRICE FLOAT,
                PROFIT_MARGIN FLOAT,
                STOCK_QUANTITY INTEGER,
                STOCK_STATUS VARCHAR,
                CREATED_AT TIMESTAMP_NTZ,
                UPDATED_AT TIMESTAMP_NTZ,
                PRIMARY KEY (TENANT_ID, ARTICLE_ID)
            """
        },
        {
            "name": "CUSTOMERS",
            "columns": """
                TENANT_ID VARCHAR NOT NULL,
                CUSTOMER_ID VARCHAR NOT NULL,
                CUSTOMER_NUMBER VARCHAR,
                FIRST_NAME VARCHAR,
                LAST_NAME VARCHAR,
                EMAIL VARCHAR,
                PHONE VARCHAR,
                ADDRESS VARCHAR,
                CITY VARCHAR,
                POSTAL_CODE VARCHAR,
                COUNTRY VARCHAR,
                CUSTOMER_SINCE TIMESTAMP_NTZ,
                LAST_ORDER_DATE TIMESTAMP_NTZ,
                TOTAL_ORDERS INTEGER,
                TOTAL_SPENT FLOAT,
                CREATED_AT TIMESTAMP_NTZ,
                UPDATED_AT TIMESTAMP_NTZ,
                PRIMARY KEY (TENANT_ID, CUSTOMER_ID)
            """
        },
        {
            "name": "ORDERS",
            "columns": """
                TENANT_ID VARCHAR NOT NULL,
                ORDER_ID VARCHAR NOT NULL,
                ORDER_NUMBER VARCHAR,
                CUSTOMER_ID VARCHAR,
                ORDER_DATE TIMESTAMP_NTZ,
                DELIVERY_DATE TIMESTAMP_NTZ,
                STATUS VARCHAR,
                TOTAL_AMOUNT FLOAT,
                DISCOUNT_AMOUNT FLOAT,
                TAX_AMOUNT FLOAT,
                SHIPPING_AMOUNT FLOAT,
                PAYMENT_METHOD VARCHAR,
                SHIPPING_METHOD VARCHAR,
                CREATED_AT TIMESTAMP_NTZ,
                UPDATED_AT TIMESTAMP_NTZ,
                PRIMARY KEY (TENANT_ID, ORDER_ID)
            """
        }
    ]
    
    for table in tables:
        execute_query(
            conn,
            f"""
            USE DATABASE MERCURIOS_DATA;
            USE SCHEMA STANDARD;
            
            CREATE TABLE IF NOT EXISTS {table['name']} (
                {table['columns']}
            );
            """,
            f"Creating {table['name']} table"
        )
    
    # Create row access policy for tenant isolation
    execute_query(
        conn,
        """
        USE DATABASE MERCURIOS_DATA;
        
        CREATE OR REPLACE ROW ACCESS POLICY tenant_isolation_policy
            AS (tenant_id VARCHAR) RETURNS BOOLEAN ->
            current_role() IN ('MERCURIOS_ADMIN', 'MERCURIOS_DEVELOPER') 
            OR EXISTS (
                SELECT 1 FROM MERCURIOS_DATA.STANDARD.TENANT_USER_MAPPING
                WHERE TENANT_USER_MAPPING.USER_ROLE = current_role()
                AND TENANT_USER_MAPPING.TENANT_ID = tenant_id
            );
        """,
        "Creating row access policy for tenant isolation"
    )
    
    # Apply row access policy to tables
    for table in tables:
        execute_query(
            conn,
            f"""
            USE DATABASE MERCURIOS_DATA;
            USE SCHEMA STANDARD;
            
            ALTER TABLE {table['name']} ADD ROW ACCESS POLICY tenant_isolation_policy ON (TENANT_ID);
            """,
            f"Applying row access policy to {table['name']} table"
        )

def setup_snowflake():
    """Set up the Snowflake environment"""
    logger.info("Connecting to Snowflake...")
    
    # Load configuration
    with open('snowflake_config.json', 'r') as f:
        config = json.load(f)
    
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=config['username'],
        password=config['password'],
        account=config['account'],
        role=config['role']
    )
    
    logger.info("Connected to Snowflake successfully!")
    
    # Create warehouses
    logger.info("\nCreating warehouses...")
    conn.cursor().execute("""
    CREATE WAREHOUSE IF NOT EXISTS MERCURIOS_LOADING_WH
      WITH WAREHOUSE_SIZE = 'MEDIUM'
      AUTO_SUSPEND = 300
      AUTO_RESUME = TRUE
      INITIALLY_SUSPENDED = TRUE;
    """)
    
    conn.cursor().execute("""
    CREATE WAREHOUSE IF NOT EXISTS MERCURIOS_ANALYTICS_WH
      WITH WAREHOUSE_SIZE = 'LARGE'
      AUTO_SUSPEND = 600
      AUTO_RESUME = TRUE
      INITIALLY_SUSPENDED = TRUE;
    """)
    
    conn.cursor().execute("""
    CREATE WAREHOUSE IF NOT EXISTS MERCURIOS_DEV_WH
      WITH WAREHOUSE_SIZE = 'SMALL'
      AUTO_SUSPEND = 120
      AUTO_RESUME = TRUE
      INITIALLY_SUSPENDED = TRUE;
    """)
    
    # Create database and schemas
    logger.info("\nCreating database and schemas...")
    conn.cursor().execute("CREATE DATABASE IF NOT EXISTS MERCURIOS_DATA;")
    conn.cursor().execute("USE DATABASE MERCURIOS_DATA;")
    conn.cursor().execute("CREATE SCHEMA IF NOT EXISTS RAW;")
    conn.cursor().execute("CREATE SCHEMA IF NOT EXISTS STANDARD;")
    conn.cursor().execute("CREATE SCHEMA IF NOT EXISTS ANALYTICS;")
    
    # Create roles
    logger.info("\nCreating roles...")
    conn.cursor().execute("CREATE ROLE IF NOT EXISTS MERCURIOS_ADMIN;")
    conn.cursor().execute("CREATE ROLE IF NOT EXISTS MERCURIOS_DEVELOPER;")
    conn.cursor().execute("CREATE ROLE IF NOT EXISTS MERCURIOS_ANALYST;")
    conn.cursor().execute("CREATE ROLE IF NOT EXISTS MERCURIOS_FIVETRAN_SERVICE;")
    
    # Grant privileges to roles
    logger.info("\nGranting privileges to roles...")
    conn.cursor().execute("GRANT USAGE ON WAREHOUSE MERCURIOS_LOADING_WH TO ROLE MERCURIOS_ADMIN;")
    conn.cursor().execute("GRANT USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH TO ROLE MERCURIOS_ADMIN;")
    conn.cursor().execute("GRANT USAGE ON WAREHOUSE MERCURIOS_DEV_WH TO ROLE MERCURIOS_ADMIN;")
    
    conn.cursor().execute("GRANT USAGE ON WAREHOUSE MERCURIOS_DEV_WH TO ROLE MERCURIOS_DEVELOPER;")
    conn.cursor().execute("GRANT USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH TO ROLE MERCURIOS_ANALYST;")
    conn.cursor().execute("GRANT USAGE ON WAREHOUSE MERCURIOS_LOADING_WH TO ROLE MERCURIOS_FIVETRAN_SERVICE;")
    
    conn.cursor().execute("GRANT ALL ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_ADMIN;")
    conn.cursor().execute("GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_DEVELOPER;")
    conn.cursor().execute("GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_ANALYST;")
    conn.cursor().execute("GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_FIVETRAN_SERVICE;")
    
    conn.cursor().execute("GRANT ALL ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_ADMIN;")
    conn.cursor().execute("GRANT ALL ON SCHEMA MERCURIOS_DATA.STANDARD TO ROLE MERCURIOS_ADMIN;")
    conn.cursor().execute("GRANT ALL ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_ADMIN;")
    
    conn.cursor().execute("GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;")
    conn.cursor().execute("GRANT CREATE TABLE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;")
    conn.cursor().execute("GRANT INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;")
    
    conn.cursor().execute("GRANT USAGE, CREATE TABLE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_DEVELOPER;")
    conn.cursor().execute("GRANT USAGE, CREATE TABLE ON SCHEMA MERCURIOS_DATA.STANDARD TO ROLE MERCURIOS_DEVELOPER;")
    conn.cursor().execute("GRANT USAGE, CREATE TABLE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_DEVELOPER;")
    
    conn.cursor().execute("GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_ANALYST;")
    conn.cursor().execute("GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_ANALYST;")
    
    # Create Fivetran service user
    logger.info("\nCreating Fivetran service user...")
    try:
        conn.cursor().execute("""
        CREATE USER IF NOT EXISTS FIVETRAN_SERVICE
          PASSWORD = 'ChangeThisToSecurePassword123!'
          DEFAULT_ROLE = MERCURIOS_FIVETRAN_SERVICE
          DEFAULT_WAREHOUSE = MERCURIOS_LOADING_WH;
        """)
        
        conn.cursor().execute("GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER FIVETRAN_SERVICE;")
    except Exception as e:
        logger.error(f"Error creating Fivetran service user: {e}")
    
    # Create sample tables for testing
    logger.info("\nCreating sample tables...")
    try:
        conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS MERCURIOS_DATA.RAW.ARTICLES (
            article_id VARCHAR(50) PRIMARY KEY,
            tenant_id VARCHAR(50) NOT NULL,
            name VARCHAR(255),
            description TEXT,
            price DECIMAL(10, 2),
            cost DECIMAL(10, 2),
            category VARCHAR(100),
            supplier_id VARCHAR(50),
            created_at TIMESTAMP_NTZ,
            updated_at TIMESTAMP_NTZ
        );
        """)
        
        conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS MERCURIOS_DATA.RAW.CUSTOMERS (
            customer_id VARCHAR(50) PRIMARY KEY,
            tenant_id VARCHAR(50) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(255),
            phone VARCHAR(50),
            address TEXT,
            city VARCHAR(100),
            postal_code VARCHAR(20),
            country VARCHAR(50),
            created_at TIMESTAMP_NTZ,
            updated_at TIMESTAMP_NTZ
        );
        """)
        
        conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS MERCURIOS_DATA.RAW.ORDERS (
            order_id VARCHAR(50) PRIMARY KEY,
            tenant_id VARCHAR(50) NOT NULL,
            customer_id VARCHAR(50),
            order_date TIMESTAMP_NTZ,
            status VARCHAR(50),
            total_amount DECIMAL(10, 2),
            shipping_address TEXT,
            shipping_city VARCHAR(100),
            shipping_postal_code VARCHAR(20),
            shipping_country VARCHAR(50),
            created_at TIMESTAMP_NTZ,
            updated_at TIMESTAMP_NTZ,
            FOREIGN KEY (customer_id) REFERENCES MERCURIOS_DATA.RAW.CUSTOMERS(customer_id)
        );
        """)
    except Exception as e:
        logger.error(f"Error creating sample tables: {e}")
    
    # Assign roles to account admin
    logger.info("\nAssigning roles to account admin...")
    try:
        conn.cursor().execute(f"GRANT ROLE MERCURIOS_ADMIN TO USER {config['username']};")
        conn.cursor().execute(f"GRANT ROLE MERCURIOS_DEVELOPER TO USER {config['username']};")
        conn.cursor().execute(f"GRANT ROLE MERCURIOS_ANALYST TO USER {config['username']};")
    except Exception as e:
        logger.warning(f"Error assigning roles to account admin: {e}")
    
    logger.info("\nSnowflake setup completed successfully!")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Set up Snowflake for Mercurios.ai')
    parser.add_argument('--config', default='snowflake_config.json', help='Path to Snowflake configuration file')
    parser.add_argument('--fivetran-password', required=True, help='Password for Fivetran service user')
    parser.add_argument('--app-password', required=True, help='Password for application service user')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Connect to Snowflake
    logger.info(f"Connecting to Snowflake account: {config['account']}")
    conn = snowflake.connector.connect(
        user=config['username'],
        password=config['password'],
        account=config['account'],
        role='ACCOUNTADMIN'  # Need ACCOUNTADMIN role for setup
    )
    
    try:
        # Setup steps
        setup_warehouses(conn)
        setup_database_and_schemas(conn)
        setup_roles_and_access_control(conn)
        create_service_users(conn, args.fivetran_password, args.app_password)
        setup_multi_tenant_tables(conn)
        
        logger.info("Snowflake setup completed successfully!")
    except Exception as e:
        logger.error(f"Error during Snowflake setup: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    setup_snowflake()

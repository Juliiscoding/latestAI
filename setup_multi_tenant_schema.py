#!/usr/bin/env python3
"""
Set up multi-tenant schema structure in Snowflake for Mercurios.ai
"""

import json
import snowflake.connector
import sys
import argparse

def setup_schema_per_tenant(cursor, database, tenant_id):
    """
    Implement the schema-per-tenant isolation pattern
    """
    print(f"Setting up schema-per-tenant structure for tenant {tenant_id}...")
    
    # Create tenant schema
    schema_name = f"TENANT_{tenant_id}"
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{schema_name}")
    print(f"Created schema {schema_name}")
    
    # Create core tables
    tables = {
        "PRODUCTS": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.PRODUCTS (
                product_id VARCHAR NOT NULL,
                product_name VARCHAR,
                product_sku VARCHAR,
                product_description VARCHAR,
                product_category VARCHAR,
                product_price FLOAT,
                product_cost FLOAT,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (product_id)
            )
        """,
        "INVENTORY": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.INVENTORY (
                inventory_id VARCHAR NOT NULL,
                product_id VARCHAR NOT NULL,
                warehouse_id VARCHAR,
                quantity INTEGER,
                reorder_level INTEGER,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (inventory_id),
                FOREIGN KEY (product_id) REFERENCES {database}.{schema}.PRODUCTS(product_id)
            )
        """,
        "CUSTOMERS": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.CUSTOMERS (
                customer_id VARCHAR NOT NULL,
                customer_name VARCHAR,
                customer_email VARCHAR,
                customer_phone VARCHAR,
                customer_address VARCHAR,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (customer_id)
            )
        """,
        "ORDERS": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.ORDERS (
                order_id VARCHAR NOT NULL,
                customer_id VARCHAR,
                order_date TIMESTAMP_NTZ,
                order_status VARCHAR,
                order_total FLOAT,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (order_id),
                FOREIGN KEY (customer_id) REFERENCES {database}.{schema}.CUSTOMERS(customer_id)
            )
        """,
        "ORDER_ITEMS": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.ORDER_ITEMS (
                order_item_id VARCHAR NOT NULL,
                order_id VARCHAR NOT NULL,
                product_id VARCHAR NOT NULL,
                quantity INTEGER,
                price FLOAT,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (order_item_id),
                FOREIGN KEY (order_id) REFERENCES {database}.{schema}.ORDERS(order_id),
                FOREIGN KEY (product_id) REFERENCES {database}.{schema}.PRODUCTS(product_id)
            )
        """
    }
    
    for table_name, create_sql in tables.items():
        sql = create_sql.format(database=database, schema=schema_name)
        print(f"Creating table {table_name}...")
        cursor.execute(sql)
        print(f"Created table {table_name}")
    
    # Grant permissions to roles
    cursor.execute(f"GRANT USAGE ON SCHEMA {database}.{schema_name} TO ROLE MERCURIOS_FIVETRAN_SERVICE")
    cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {database}.{schema_name} TO ROLE MERCURIOS_FIVETRAN_SERVICE")
    cursor.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA {database}.{schema_name} TO ROLE MERCURIOS_ANALYST")
    
    print(f"Granted permissions on schema {schema_name}")
    return schema_name

def setup_shared_schema_with_rls(cursor, database):
    """
    Implement the shared schema with row-level security pattern
    """
    print("Setting up shared schema with row-level security...")
    
    # Create shared schema
    schema_name = "SHARED"
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{schema_name}")
    print(f"Created schema {schema_name}")
    
    # Create core tables with tenant_id
    tables = {
        "PRODUCTS": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.PRODUCTS (
                tenant_id VARCHAR NOT NULL,
                product_id VARCHAR NOT NULL,
                product_name VARCHAR,
                product_sku VARCHAR,
                product_description VARCHAR,
                product_category VARCHAR,
                product_price FLOAT,
                product_cost FLOAT,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (tenant_id, product_id)
            )
        """,
        "INVENTORY": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.INVENTORY (
                tenant_id VARCHAR NOT NULL,
                inventory_id VARCHAR NOT NULL,
                product_id VARCHAR NOT NULL,
                warehouse_id VARCHAR,
                quantity INTEGER,
                reorder_level INTEGER,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (tenant_id, inventory_id),
                FOREIGN KEY (tenant_id, product_id) REFERENCES {database}.{schema}.PRODUCTS(tenant_id, product_id)
            )
        """,
        "CUSTOMERS": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.CUSTOMERS (
                tenant_id VARCHAR NOT NULL,
                customer_id VARCHAR NOT NULL,
                customer_name VARCHAR,
                customer_email VARCHAR,
                customer_phone VARCHAR,
                customer_address VARCHAR,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (tenant_id, customer_id)
            )
        """,
        "ORDERS": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.ORDERS (
                tenant_id VARCHAR NOT NULL,
                order_id VARCHAR NOT NULL,
                customer_id VARCHAR,
                order_date TIMESTAMP_NTZ,
                order_status VARCHAR,
                order_total FLOAT,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (tenant_id, order_id),
                FOREIGN KEY (tenant_id, customer_id) REFERENCES {database}.{schema}.CUSTOMERS(tenant_id, customer_id)
            )
        """,
        "ORDER_ITEMS": """
            CREATE TABLE IF NOT EXISTS {database}.{schema}.ORDER_ITEMS (
                tenant_id VARCHAR NOT NULL,
                order_item_id VARCHAR NOT NULL,
                order_id VARCHAR NOT NULL,
                product_id VARCHAR NOT NULL,
                quantity INTEGER,
                price FLOAT,
                created_at TIMESTAMP_NTZ,
                updated_at TIMESTAMP_NTZ,
                PRIMARY KEY (tenant_id, order_item_id),
                FOREIGN KEY (tenant_id, order_id) REFERENCES {database}.{schema}.ORDERS(tenant_id, order_id),
                FOREIGN KEY (tenant_id, product_id) REFERENCES {database}.{schema}.PRODUCTS(tenant_id, product_id)
            )
        """
    }
    
    for table_name, create_sql in tables.items():
        sql = create_sql.format(database=database, schema=schema_name)
        print(f"Creating table {table_name}...")
        cursor.execute(sql)
        print(f"Created table {table_name}")
    
    # Create secure view function for tenant isolation
    cursor.execute(f"""
    CREATE OR REPLACE FUNCTION {database}.{schema_name}.CURRENT_TENANT_ID()
    RETURNS VARCHAR
    AS
    $$
        SELECT CURRENT_SESSION_PROPERTY('app.current_tenant_id')
    $$
    """)
    
    # Create row access policies for each table
    for table_name in tables.keys():
        policy_name = f"tenant_isolation_policy_{table_name.lower()}"
        cursor.execute(f"""
        CREATE OR REPLACE ROW ACCESS POLICY {policy_name}
        ON {database}.{schema_name}.{table_name}
        FOR SELECT
        USING (tenant_id = {database}.{schema_name}.CURRENT_TENANT_ID())
        """)
        print(f"Created row access policy for {table_name}")
    
    # Grant permissions to roles
    cursor.execute(f"GRANT USAGE ON SCHEMA {database}.{schema_name} TO ROLE MERCURIOS_FIVETRAN_SERVICE")
    cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {database}.{schema_name} TO ROLE MERCURIOS_FIVETRAN_SERVICE")
    cursor.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA {database}.{schema_name} TO ROLE MERCURIOS_ANALYST")
    
    print(f"Granted permissions on schema {schema_name}")
    return schema_name

def main():
    parser = argparse.ArgumentParser(description='Set up multi-tenant schema structure in Snowflake')
    parser.add_argument('--isolation-pattern', choices=['schema-per-tenant', 'shared-schema-rls'], 
                        default='schema-per-tenant', help='Tenant isolation pattern to use')
    parser.add_argument('--tenant-id', help='Tenant ID for schema-per-tenant pattern')
    parser.add_argument('--config-file', default='snowflake_config.json', help='Path to Snowflake config file')
    
    args = parser.parse_args()
    
    if args.isolation_pattern == 'schema-per-tenant' and not args.tenant_id:
        print("Error: --tenant-id is required for schema-per-tenant pattern")
        sys.exit(1)
    
    # Load Snowflake config
    try:
        with open(args.config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)
    
    # Connect to Snowflake
    try:
        conn = snowflake.connector.connect(
            user=config['username'],
            password=config['password'],
            account=config['account'],
            warehouse=config['warehouse'],
            database=config['database'],
            schema=config['schema'],
            role=config['role']  # Use the role from config (ACCOUNTADMIN)
        )
        
        # Create a cursor object
        cursor = conn.cursor()
        
        database = config['database']
        
        # Create MERCURIOS_ANALYST role if it doesn't exist
        cursor.execute("SELECT 1 FROM INFORMATION_SCHEMA.ROLES WHERE ROLE_NAME = 'MERCURIOS_ANALYST'")
        if not cursor.fetchone():
            cursor.execute("CREATE ROLE MERCURIOS_ANALYST")
            print("Created MERCURIOS_ANALYST role")
        
        # Set up schema structure based on chosen pattern
        if args.isolation_pattern == 'schema-per-tenant':
            schema_name = setup_schema_per_tenant(cursor, database, args.tenant_id)
        else:
            schema_name = setup_shared_schema_with_rls(cursor, database)
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print(f"\nSuccessfully set up {args.isolation_pattern} structure in {database}")
        print(f"Schema name: {schema_name}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

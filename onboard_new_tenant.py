#!/usr/bin/env python3
"""
Onboard a new tenant to the Mercurios.ai platform
This script automates the process of setting up all necessary resources for a new tenant
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
import snowflake.connector
from datetime import datetime

def generate_tenant_id():
    """Generate a unique tenant ID"""
    return str(uuid.uuid4())[:8].upper()

def setup_snowflake_resources(config, tenant_id, tenant_name, isolation_pattern):
    """Set up Snowflake resources for the new tenant"""
    print(f"Setting up Snowflake resources for tenant {tenant_id} ({tenant_name})...")
    
    # Use the setup_multi_tenant_schema.py script
    if isolation_pattern == 'schema-per-tenant':
        cmd = [
            'python', 'setup_multi_tenant_schema.py',
            '--isolation-pattern', 'schema-per-tenant',
            '--tenant-id', tenant_id,
            '--config-file', 'snowflake_config.json'
        ]
    else:
        cmd = [
            'python', 'setup_multi_tenant_schema.py',
            '--isolation-pattern', 'shared-schema-rls',
            '--config-file', 'snowflake_config.json'
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error setting up Snowflake resources: {result.stderr}")
        return False
    
    print(result.stdout)
    
    # Connect to Snowflake to register tenant metadata
    try:
        conn = snowflake.connector.connect(
            user=config['username'],
            password=config['password'],
            account=config['account'],
            warehouse=config['warehouse'],
            database=config['database'],
            schema=config['schema'],
            role=config['role']
        )
        
        cursor = conn.cursor()
        
        # Create tenants metadata table if it doesn't exist
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {config['database']}.{config['schema']}.TENANTS (
            tenant_id VARCHAR NOT NULL,
            tenant_name VARCHAR NOT NULL,
            isolation_pattern VARCHAR NOT NULL,
            schema_name VARCHAR NOT NULL,
            pos_system VARCHAR,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (tenant_id)
        )
        """)
        
        # Determine schema name based on isolation pattern
        schema_name = f"TENANT_{tenant_id}" if isolation_pattern == 'schema-per-tenant' else 'SHARED'
        
        # Insert tenant metadata
        cursor.execute(f"""
        INSERT INTO {config['database']}.{config['schema']}.TENANTS (
            tenant_id, tenant_name, isolation_pattern, schema_name, pos_system, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
        )
        """, (tenant_id, tenant_name, isolation_pattern, schema_name, 'ProHandel'))
        
        cursor.close()
        conn.close()
        
        print(f"Registered tenant {tenant_id} in metadata table")
        return True
        
    except Exception as e:
        print(f"Error registering tenant metadata: {e}")
        return False

def setup_lambda_function(tenant_id, tenant_name, api_url, api_key, aws_region):
    """Set up AWS Lambda function for the new tenant"""
    print(f"Setting up AWS Lambda function for tenant {tenant_id}...")
    
    # Create a directory for the tenant's Lambda function
    tenant_dir = f"lambda_functions/tenant_{tenant_id.lower()}"
    os.makedirs(tenant_dir, exist_ok=True)
    
    # Create Lambda function configuration
    lambda_config = {
        "function_name": f"prohandel-fivetran-connector-{tenant_id.lower()}",
        "description": f"Fivetran connector for {tenant_name} (Tenant ID: {tenant_id})",
        "runtime": "python3.9",
        "handler": "lambda_function.lambda_handler",
        "timeout": 180,
        "memory_size": 256,
        "environment_variables": {
            "TENANT_ID": tenant_id,
            "API_BASE_URL": api_url,
            "API_KEY": api_key
        }
    }
    
    # Save Lambda configuration
    with open(f"{tenant_dir}/lambda_config.json", 'w') as f:
        json.dump(lambda_config, f, indent=2)
    
    # Create deployment script
    deploy_script = f"""#!/bin/bash
# Deployment script for tenant {tenant_id} Lambda function

# Create deployment package
echo "Creating deployment package..."
cd {tenant_dir}
pip install -r requirements.txt -t ./package
cp lambda_function.py ./package/
cd package
zip -r ../deployment-package.zip .
cd ..

# Deploy Lambda function
echo "Deploying Lambda function..."
aws lambda create-function \\
  --function-name {lambda_config['function_name']} \\
  --runtime {lambda_config['runtime']} \\
  --role arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole \\
  --handler {lambda_config['handler']} \\
  --timeout {lambda_config['timeout']} \\
  --memory-size {lambda_config['memory_size']} \\
  --zip-file fileb://deployment-package.zip \\
  --environment "Variables={{TENANT_ID={tenant_id},API_BASE_URL={api_url},API_KEY={api_key}}}" \\
  --region {aws_region}

echo "Lambda function deployed successfully!"
"""
    
    with open(f"{tenant_dir}/deploy.sh", 'w') as f:
        f.write(deploy_script)
    
    # Make the script executable
    os.chmod(f"{tenant_dir}/deploy.sh", 0o755)
    
    # Copy Lambda function code template
    # This assumes you have a template lambda_function.py file
    try:
        with open("lambda_function_template.py", 'r') as src:
            with open(f"{tenant_dir}/lambda_function.py", 'w') as dst:
                content = src.read()
                # Replace placeholders with tenant-specific values
                content = content.replace("{{TENANT_ID}}", tenant_id)
                content = content.replace("{{TENANT_NAME}}", tenant_name)
                dst.write(content)
    except FileNotFoundError:
        print("Warning: lambda_function_template.py not found. Creating a placeholder file.")
        with open(f"{tenant_dir}/lambda_function.py", 'w') as f:
            f.write(f"""
import json
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Tenant-specific configuration
TENANT_ID = os.environ.get('TENANT_ID', '{tenant_id}')
API_BASE_URL = os.environ.get('API_BASE_URL', '{api_url}')
API_KEY = os.environ.get('API_KEY', '')

def lambda_handler(event, context):
    """
    Fivetran connector handler for tenant {tenant_id} ({tenant_name})
    """
    logger.info(f"Received event: {{json.dumps(event)}}")
    
    # Extract request type from the event
    request_type = event.get('type', '')
    
    if request_type == 'test':
        # Handle test request
        return handle_test()
    elif request_type == 'schema':
        # Handle schema request
        return handle_schema()
    elif request_type == 'sync':
        # Handle sync request
        state = event.get('state', {})
        return handle_sync(state)
    else:
        # Handle unknown request type
        logger.error(f"Unknown request type: {{request_type}}")
        return {
            'error': f"Unknown request type: {{request_type}}"
        }

def handle_test():
    """Handle test request"""
    # TODO: Implement test connection logic
    return {
        'success': True,
        'message': 'Connection successful'
    }

def handle_schema():
    """Handle schema request"""
    # TODO: Implement schema definition logic
    return {
        'schema': {{
            'products': {{
                'primary_key': ['product_id'],
                'columns': {{
                    'product_id': 'string',
                    'product_name': 'string',
                    'product_sku': 'string',
                    'product_price': 'number',
                    'tenant_id': 'string'
                }}
            }},
            # Add more tables as needed
        }}
    }

def handle_sync(state):
    """Handle sync request"""
    # TODO: Implement sync logic
    return {{
        'state': state,
        'insert': {{
            'products': [
                # Sample data - replace with actual API call
                {{
                    'product_id': 'sample-1',
                    'product_name': 'Sample Product',
                    'product_sku': 'SKU-001',
                    'product_price': 99.99,
                    'tenant_id': TENANT_ID
                }}
            ]
        }},
        'delete': {{}}
    }}
""")
    
    # Create requirements.txt
    with open(f"{tenant_dir}/requirements.txt", 'w') as f:
        f.write("""requests==2.28.1
python-dateutil==2.8.2
""")
    
    print(f"Lambda function setup completed for tenant {tenant_id}")
    print(f"Lambda function code and deployment script created in {tenant_dir}")
    print(f"To deploy the Lambda function, run: cd {tenant_dir} && ./deploy.sh")
    
    return True

def register_tenant_in_fivetran(tenant_id, tenant_name, lambda_function_name, aws_region):
    """Register the tenant in Fivetran (this is a placeholder - actual implementation would use Fivetran API)"""
    print(f"Registering tenant {tenant_id} in Fivetran...")
    
    # Create Fivetran configuration guide
    fivetran_guide = f"""# Fivetran Configuration for Tenant {tenant_id}

## Overview
This guide provides instructions for setting up a Fivetran connector for tenant {tenant_name} (ID: {tenant_id}).

## Lambda Function Details
- **Function Name**: {lambda_function_name}
- **Region**: {aws_region}
- **ARN**: arn:aws:lambda:{aws_region}:689864027744:function:{lambda_function_name}

## Fivetran Setup Steps

1. Log in to the Fivetran dashboard
2. Click "Add Connector"
3. Search for and select "AWS Lambda"
4. Configure the connector with the following details:
   - **Connector Name**: {tenant_name} ProHandel
   - **Lambda Function ARN**: arn:aws:lambda:{aws_region}:689864027744:function:{lambda_function_name}
   - **AWS Region**: {aws_region}
   - **IAM Role**: arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole
5. Click "Save & Test" to verify the connection
6. Configure the schema mapping:
   - Ensure all tables include the tenant_id column
   - Map tables to the appropriate Snowflake destination
7. Set the sync frequency (recommended: every 6 hours)
8. Start the initial sync

## Snowflake Destination
The data will be loaded into the following location in Snowflake:
- **Database**: MERCURIOS_DATA
- **Schema**: {"TENANT_" + tenant_id if isolation_pattern == 'schema-per-tenant' else 'SHARED'}

## Monitoring
Monitor the connector's performance in the Fivetran dashboard and in Snowflake using the following query:

```sql
SELECT * FROM MERCURIOS_DATA.FIVETRAN_METADATA.CONNECTOR 
WHERE connector_name LIKE '%{tenant_name}%';
```

## Troubleshooting
If you encounter issues with the connector:
1. Check the Lambda function logs in AWS CloudWatch
2. Verify the IAM permissions
3. Check the Fivetran connector logs
4. Ensure the API credentials are valid
"""
    
    # Save the guide
    tenant_dir = f"lambda_functions/tenant_{tenant_id.lower()}"
    with open(f"{tenant_dir}/fivetran_setup.md", 'w') as f:
        f.write(fivetran_guide)
    
    print(f"Fivetran setup guide created in {tenant_dir}/fivetran_setup.md")
    return True

def main():
    parser = argparse.ArgumentParser(description='Onboard a new tenant to the Mercurios.ai platform')
    parser.add_argument('--tenant-name', required=True, help='Name of the tenant')
    parser.add_argument('--api-url', required=True, help='Base URL for the tenant\'s ProHandel API')
    parser.add_argument('--api-key', required=True, help='API key for the tenant\'s ProHandel API')
    parser.add_argument('--isolation-pattern', choices=['schema-per-tenant', 'shared-schema-rls'], 
                        default='schema-per-tenant', help='Tenant isolation pattern to use')
    parser.add_argument('--aws-region', default='eu-central-1', help='AWS region for Lambda function')
    parser.add_argument('--tenant-id', help='Optional: Specify a tenant ID (generated if not provided)')
    parser.add_argument('--config-file', default='snowflake_config.json', help='Path to Snowflake config file')
    
    args = parser.parse_args()
    
    # Generate tenant ID if not provided
    tenant_id = args.tenant_id if args.tenant_id else generate_tenant_id()
    
    print(f"Onboarding new tenant: {args.tenant_name} (ID: {tenant_id})")
    print(f"Isolation pattern: {args.isolation_pattern}")
    print(f"API URL: {args.api_url}")
    print(f"AWS Region: {args.aws_region}")
    print()
    
    # Load Snowflake config
    try:
        with open(args.config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)
    
    # Create lambda_functions directory if it doesn't exist
    os.makedirs("lambda_functions", exist_ok=True)
    
    # Setup process
    print("Starting tenant onboarding process...")
    print("Step 1: Setting up Snowflake resources")
    if not setup_snowflake_resources(config, tenant_id, args.tenant_name, args.isolation_pattern):
        print("Failed to set up Snowflake resources. Aborting.")
        sys.exit(1)
    
    print("\nStep 2: Setting up Lambda function")
    lambda_function_name = f"prohandel-fivetran-connector-{tenant_id.lower()}"
    if not setup_lambda_function(tenant_id, args.tenant_name, args.api_url, args.api_key, args.aws_region):
        print("Failed to set up Lambda function. Aborting.")
        sys.exit(1)
    
    print("\nStep 3: Registering tenant in Fivetran")
    if not register_tenant_in_fivetran(tenant_id, args.tenant_name, lambda_function_name, args.aws_region):
        print("Failed to register tenant in Fivetran. Aborting.")
        sys.exit(1)
    
    # Create tenant summary file
    summary = f"""# Tenant Onboarding Summary

## Tenant Information
- **Tenant ID**: {tenant_id}
- **Tenant Name**: {args.tenant_name}
- **Isolation Pattern**: {args.isolation_pattern}
- **ProHandel API URL**: {args.api_url}
- **Onboarding Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Resources Created
- **Snowflake Schema**: {"TENANT_" + tenant_id if args.isolation_pattern == 'schema-per-tenant' else 'SHARED'}
- **Lambda Function**: {lambda_function_name}
- **Lambda Region**: {args.aws_region}
- **Lambda ARN**: arn:aws:lambda:{args.aws_region}:689864027744:function:{lambda_function_name}

## Next Steps
1. Deploy the Lambda function: `cd lambda_functions/tenant_{tenant_id.lower()} && ./deploy.sh`
2. Configure the Fivetran connector using the guide: `lambda_functions/tenant_{tenant_id.lower()}/fivetran_setup.md`
3. Start the initial sync in Fivetran
4. Verify data is flowing into Snowflake

## Monitoring
- Monitor the Lambda function in AWS CloudWatch
- Monitor the Fivetran connector in the Fivetran dashboard
- Monitor data in Snowflake using the queries in the Fivetran setup guide
"""
    
    tenant_dir = f"lambda_functions/tenant_{tenant_id.lower()}"
    with open(f"{tenant_dir}/onboarding_summary.md", 'w') as f:
        f.write(summary)
    
    print("\nTenant onboarding completed successfully!")
    print(f"Tenant ID: {tenant_id}")
    print(f"Summary file: {tenant_dir}/onboarding_summary.md")
    print(f"Next steps: Follow the instructions in {tenant_dir}/onboarding_summary.md")

if __name__ == "__main__":
    main()

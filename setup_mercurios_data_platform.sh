#!/bin/bash

# Mercurios.ai Data Platform Setup Script
# This script sets up the entire data platform architecture:
# 1. Snowflake data warehouse
# 2. dbt configuration for transformations
# 3. Fivetran integration for data loading
# 4. AWS S3 data lake (optional)

set -e

echo "====================================================="
echo "Mercurios.ai Data Platform Setup"
echo "====================================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install -r snowflake_requirements.txt
pip install pyyaml boto3

# Step 1: Snowflake Setup
echo "====================================================="
echo "Step 1: Snowflake Setup"
echo "====================================================="

# Prompt for Snowflake configuration
read -p "Enter Snowflake account identifier (e.g., xy12345.eu-central-1): " ACCOUNT
read -p "Enter Snowflake username: " USERNAME
read -sp "Enter Snowflake password: " PASSWORD
echo
read -sp "Enter password for Fivetran service user: " FIVETRAN_PASSWORD
echo
read -sp "Enter password for application service user: " APP_PASSWORD
echo

# Update snowflake_config.json
echo "Updating Snowflake configuration..."
cat > snowflake_config.json << EOF
{
    "account": "$ACCOUNT", 
    "username": "$USERNAME",
    "password": "$PASSWORD",
    "region": "eu-central-1",
    "role": "ACCOUNTADMIN",
    "warehouse": "MERCURIOS_ADMIN_WH",
    "database": "MERCURIOS_DATA",
    "schema": "PUBLIC"
}
EOF

# Make setup scripts executable
chmod +x setup_snowflake.py
chmod +x update_dbt_profiles.py
chmod +x update_fivetran_config.py

# Run Snowflake setup
echo "Running Snowflake setup..."
python setup_snowflake.py --fivetran-password "$FIVETRAN_PASSWORD" --app-password "$APP_PASSWORD"

# Step 2: dbt Configuration
echo "====================================================="
echo "Step 2: dbt Configuration"
echo "====================================================="

# Update dbt profiles
echo "Updating dbt profiles to use Snowflake..."
python update_dbt_profiles.py

# Update dbt project configuration
echo "Updating dbt project configuration..."
cat > dbt_prohandel/dbt_project.yml << EOF
name: 'prohandel'
version: '1.0.0'
config-version: 2

profile: 'prohandel'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  prohandel:
    staging:
      +materialized: view
      +schema: RAW
    intermediate:
      +materialized: table
      +schema: STANDARD
    marts:
      +materialized: table
      +schema: ANALYTICS
      inventory:
        +schema: ANALYTICS
      sales:
        +schema: ANALYTICS
EOF

# Step 3: Fivetran Integration
echo "====================================================="
echo "Step 3: Fivetran Integration"
echo "====================================================="

# Prompt for Fivetran API credentials
read -p "Enter Fivetran API key (or press Enter to skip): " FIVETRAN_API_KEY
read -p "Enter Fivetran API secret (or press Enter to skip): " FIVETRAN_API_SECRET

# Update Fivetran configuration
if [ -n "$FIVETRAN_API_KEY" ] && [ -n "$FIVETRAN_API_SECRET" ]; then
    echo "Updating Fivetran configuration..."
    python update_fivetran_config.py --fivetran-api-key "$FIVETRAN_API_KEY" --fivetran-api-secret "$FIVETRAN_API_SECRET"
else
    echo "Skipping Fivetran API configuration..."
    python update_fivetran_config.py
fi

# Step 4: AWS S3 Data Lake (Optional)
echo "====================================================="
echo "Step 4: AWS S3 Data Lake Setup (Optional)"
echo "====================================================="

read -p "Do you want to set up an S3 data lake? (y/n): " SETUP_S3

if [ "$SETUP_S3" == "y" ] || [ "$SETUP_S3" == "Y" ]; then
    # Prompt for AWS credentials
    read -p "Enter AWS access key ID: " AWS_ACCESS_KEY_ID
    read -sp "Enter AWS secret access key: " AWS_SECRET_ACCESS_KEY
    echo
    read -p "Enter S3 bucket name prefix (e.g., mercurios-data-lake): " S3_BUCKET_PREFIX
    
    # Export AWS credentials
    export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
    export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
    
    # Create S3 buckets script
    cat > setup_s3_data_lake.py << EOF
#!/usr/bin/env python3
import boto3
import sys

def create_s3_buckets(bucket_prefix):
    """Create S3 buckets for the data lake."""
    s3 = boto3.client('s3')
    
    # Define buckets
    buckets = [
        {"name": f"{bucket_prefix}-raw", "description": "Raw data from various sources"},
        {"name": f"{bucket_prefix}-processed", "description": "Processed data ready for analytics"},
        {"name": f"{bucket_prefix}-archive", "description": "Archived historical data"}
    ]
    
    for bucket in buckets:
        try:
            # Create bucket
            s3.create_bucket(
                Bucket=bucket["name"],
                CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'}
            )
            
            # Add tags
            s3.put_bucket_tagging(
                Bucket=bucket["name"],
                Tagging={
                    'TagSet': [
                        {'Key': 'Project', 'Value': 'Mercurios.ai'},
                        {'Key': 'Description', 'Value': bucket["description"]}
                    ]
                }
            )
            
            # Enable versioning
            s3.put_bucket_versioning(
                Bucket=bucket["name"],
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            print(f"Created bucket: {bucket['name']}")
        except Exception as e:
            print(f"Error creating bucket {bucket['name']}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python setup_s3_data_lake.py <bucket_prefix>")
        sys.exit(1)
    
    bucket_prefix = sys.argv[1]
    create_s3_buckets(bucket_prefix)
EOF
    
    chmod +x setup_s3_data_lake.py
    
    # Create S3 buckets
    echo "Creating S3 buckets for data lake..."
    python setup_s3_data_lake.py "$S3_BUCKET_PREFIX"
    
    echo "S3 data lake setup completed!"
else
    echo "Skipping S3 data lake setup..."
fi

# Final steps
echo "====================================================="
echo "Setup Completed!"
echo "====================================================="
echo "The Mercurios.ai data platform has been set up with the following components:"
echo "1. Snowflake data warehouse"
echo "2. dbt configuration for transformations"
echo "3. Fivetran integration for data loading"
if [ "$SETUP_S3" == "y" ] || [ "$SETUP_S3" == "Y" ]; then
    echo "4. AWS S3 data lake"
fi

echo ""
echo "Next steps:"
echo "1. Configure Fivetran to connect to Snowflake using the FIVETRAN_SERVICE user"
echo "2. Set up the ProHandel connector in Fivetran"
echo "3. Run dbt models to transform the data"
echo "4. Set up the GraphQL API layer"
echo "5. Configure the Next.js frontend"

# Save configuration for future reference
echo "Saving configuration summary..."
cat > mercurios_platform_config.md << EOF
# Mercurios.ai Data Platform Configuration

## Snowflake Configuration
- Account: $ACCOUNT
- Database: MERCURIOS_DATA
- Warehouses:
  - MERCURIOS_ADMIN_WH (Admin tasks)
  - MERCURIOS_LOADING_WH (ETL/Loading)
  - MERCURIOS_ANALYTICS_WH (Analytics)
  - MERCURIOS_DEV_WH (Development)

## Service Users
- FIVETRAN_SERVICE: Used by Fivetran to load data
- APP_SERVICE: Used by the application to access data

## Schemas
- RAW: Landing zone for Fivetran data
- STANDARD: Standardized and cleaned data
- ANALYTICS: Analytics-ready data for reporting
- TENANT_CUSTOMIZATIONS: Customer-specific customizations

## Fivetran Configuration
- Destination: Snowflake
- Schema: RAW
- Warehouse: MERCURIOS_LOADING_WH
- Role: MERCURIOS_FIVETRAN_SERVICE

EOF

if [ "$SETUP_S3" == "y" ] || [ "$SETUP_S3" == "Y" ]; then
    cat >> mercurios_platform_config.md << EOF
## S3 Data Lake
- Raw Data Bucket: ${S3_BUCKET_PREFIX}-raw
- Processed Data Bucket: ${S3_BUCKET_PREFIX}-processed
- Archive Bucket: ${S3_BUCKET_PREFIX}-archive
EOF
fi

echo "Configuration summary saved to mercurios_platform_config.md"

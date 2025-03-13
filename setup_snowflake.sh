#!/bin/bash

# Setup script for Snowflake configuration
set -e

echo "Setting up Snowflake for Mercurios.ai..."

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

# Make setup_snowflake.py executable
chmod +x setup_snowflake.py

# Run Snowflake setup
echo "Running Snowflake setup..."
python setup_snowflake.py --fivetran-password "$FIVETRAN_PASSWORD" --app-password "$APP_PASSWORD"

echo "Snowflake setup completed!"
echo "Next steps:"
echo "1. Configure Fivetran to connect to Snowflake using the FIVETRAN_SERVICE user"
echo "2. Set up the ProHandel connector in Fivetran"
echo "3. Configure dbt to use Snowflake for transformations"

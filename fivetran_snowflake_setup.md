# Fivetran to Snowflake Setup Guide

This guide walks you through setting up Fivetran with Snowflake as your destination for the ProHandel connector.

## Prerequisites

1. A Fivetran account
2. A Snowflake account
3. ProHandel API credentials

## Step 1: Set Up Snowflake

Follow the instructions in `snowflake_setup_guide.md` to:
1. Create your Snowflake account
2. Set up warehouses, databases, and schemas
3. Configure roles and permissions
4. Create the service user for Fivetran

## Step 2: Connect Fivetran to Snowflake

1. Log in to your Fivetran account
2. Click "Add Destination" or "Connect your destination"
3. Select "Snowflake" from the list of destinations
4. Enter the following details:
   - **Account**: Your Snowflake account identifier (e.g., `xy12345.eu-central-1.snowflakecomputing.com`)
   - **Database**: `MERCURIOS_DATA` (or your chosen database name)
   - **Schema**: `RAW` (this is where Fivetran will load the data)
   - **Username**: `FIVETRAN_SERVICE` (the service user you created)
   - **Password**: The password you set for the service user
   - **Warehouse**: `MERCURIOS_LOADING_WH` (the warehouse for data loading)
   - **Role**: `MERCURIOS_FIVETRAN_SERVICE` (the role with appropriate permissions)

5. Click "Save" or "Test Connection" to verify the connection

## Key Pair Authentication Setup

As of March 2025, Snowflake is blocking single-factor password authentication. We have set up key pair authentication for the FIVETRAN_USER:

1. Generated RSA key pair:
   ```bash
   mkdir -p ~/.ssh/snowflake
   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out ~/.ssh/snowflake/fivetran_rsa_key.p8 -nocrypt
   openssl rsa -in ~/.ssh/snowflake/fivetran_rsa_key.p8 -pubout -out ~/.ssh/snowflake/fivetran_rsa_key.pub
   ```

2. Assigned public key to FIVETRAN_USER in Snowflake:
   ```python
   # Used assign_key_to_fivetran.py script to set the public key
   python assign_key_to_fivetran.py
   ```

3. Set default warehouse for FIVETRAN_USER:
   ```python
   # Used set_fivetran_default_warehouse.py script to set the default warehouse
   python set_fivetran_default_warehouse.py
   ```

4. Grant necessary permissions to FIVETRAN_USER:
   ```python
   # Used grant_fivetran_permissions.py script to grant database and warehouse permissions
   python grant_fivetran_permissions.py
   ```

5. Private key for Fivetran:
   - The private key is stored in `fivetran_private_key.txt` (multi-line format)
   - A single-line version (required by Fivetran) is in `fivetran_private_key_single_line.txt`
   - **IMPORTANT**: When pasting into Fivetran, use the single-line version as Fivetran requires the private key to have no line breaks
   - The key is not encrypted, so leave "Is Private Key Encrypted?" toggle OFF

### Troubleshooting Key Pair Authentication

If you encounter a "400 Bad Request" error when setting up the Fivetran connector:
1. Make sure you're using the single-line private key format (no line breaks)
2. Verify that the key has the correct prefix `-----BEGIN PRIVATE KEY-----` and postfix `-----END PRIVATE KEY-----`
3. Ensure there are no spaces in the key

If you encounter a "Default Warehouse Test" error:
1. Make sure the FIVETRAN_USER has a default warehouse set
2. Run the `set_fivetran_default_warehouse.py` script to set the default warehouse

If you encounter a "Permission Test" error:
1. Make sure the FIVETRAN_USER has the necessary permissions on the database and warehouse
2. Run the `grant_fivetran_permissions.py` script to grant the required permissions
3. The script grants the following permissions to the MERCURIOS_FIVETRAN_SERVICE role:
   - USAGE, MODIFY, MONITOR, and CREATE SCHEMA on the database
   - USAGE and OPERATE on the warehouse
   - USAGE, CREATE TABLE, CREATE VIEW, CREATE STAGE, and CREATE PIPE on all schemas

## Snowflake Connection Details

For the Fivetran-Snowflake integration, use the following connection details:

- **Host**: vrxdfzx-zz95717.snowflakecomputing.com
- **Port**: 443
- **User**: FIVETRAN_USER
- **Auth**: KEY_PAIR
- **Database**: MERCURIOS_DATA
- **Role**: MERCURIOS_FIVETRAN_SERVICE

## Snowflake Account Parameters

The following parameters have been set in the Snowflake account:

- PREVENT_LOAD_FROM_INLINE_URL = FALSE
- REQUIRE_STORAGE_INTEGRATION_FOR_STAGE_OPERATION = FALSE
- QUOTED_IDENTIFIERS_IGNORE_CASE = FALSE

## Fivetran Configuration

- **Deployment Model**: SaaS Deployment
- **Data Processing Location**: EU (to match AWS Lambda region)
- **Fivetran Processing Cloud Provider**: GCP
- **Time Zone**: Europe/Berlin

## Step 3: Set Up ProHandel Connector

1. In Fivetran, navigate to "Connectors" and click "Add Connector"
2. Search for or select "Function" or "AWS Lambda" connector type
3. Enter the following details:
   - **Connector Name**: `ProHandel - [Customer Name]`
   - **AWS Region**: `eu-central-1` (or your chosen region)
   - **Function ARN**: The ARN of your deployed Lambda function (e.g., `arn:aws:lambda:eu-central-1:689864027744:function:prohandel-fivetran-connector-[tenant_id]`)

4. Click "Save" or "Test Connection" to verify the connector works

## Step 4: Configure Sync Settings

1. In the connector settings, configure the sync frequency:
   - For initial testing: Hourly
   - For production: Every 6 hours or daily, depending on your needs

2. Enable "Historical Sync" for the initial load to get all historical data

3. Click "Save and Sync" to start the initial data load

## Step 5: Verify Data in Snowflake

After the initial sync completes, verify that data is correctly loaded into Snowflake:

```sql
-- Connect to Snowflake and run:
USE DATABASE MERCURIOS_DATA;
USE SCHEMA RAW;

-- Check that tables were created
SHOW TABLES;

-- Check row counts
SELECT COUNT(*) FROM ARTICLES;
SELECT COUNT(*) FROM CUSTOMERS;
SELECT COUNT(*) FROM ORDERS;
SELECT COUNT(*) FROM SALES;
SELECT COUNT(*) FROM INVENTORY;

-- Sample data
SELECT * FROM ARTICLES LIMIT 10;
```

## Step 6: Set Up dbt for Transformations

Once data is flowing into Snowflake, set up dbt to transform the raw data:

1. Install dbt locally or use dbt Cloud
2. Configure dbt to connect to Snowflake
3. Create models that transform data from the RAW schema to STANDARD and ANALYTICS schemas
4. Schedule dbt runs to keep transformed data up to date

## Troubleshooting

### Common Issues

1. **Connection Failures**:
   - Check that the Snowflake service user has the correct permissions
   - Verify that the warehouse is properly configured and has enough resources

2. **Missing Data**:
   - Check the Lambda function logs for errors
   - Verify that the ProHandel API credentials are correct
   - Check that the Lambda function has the correct permissions

3. **Sync Errors**:
   - Look at the Fivetran connector logs for specific error messages
   - Check that the Lambda function timeout is set high enough (at least 3 minutes)
   - Verify that the Lambda function has enough memory (at least 256MB)

### Getting Help

If you encounter issues:
1. Check the CloudWatch logs for the Lambda function
2. Review the Fivetran connector logs
3. Check the Snowflake query history for errors
4. Contact Mercurios.ai support at support@mercurios.ai

# Fivetran API Setup Guide

This guide explains how to use the `fivetran_api_setup.py` script to automate the Fivetran connector setup process directly from Windsurf.

## Prerequisites

Before running the script, you'll need:

1. **Fivetran API Credentials**:
   - API Key and API Secret from your Fivetran account
   - You can generate these in the Fivetran dashboard under Account Settings > API Config

2. **Fivetran Group and Destination**:
   - Group ID where the connector will be created
   - Destination ID where the data will be loaded

3. **AWS Lambda Function ARN**:
   - ARN of your deployed ProHandel Lambda function
   - You can find this using the AWS CLI or the AWS Console

4. **ProHandel API Credentials**:
   - Username and password for the ProHandel API

## Running the Script

You can run the script in two ways:

### 1. Interactive Mode

Simply run the script without arguments:

```bash
python fivetran_api_setup.py
```

The script will:
- Ask for your Fivetran API credentials
- List available groups and destinations
- Help find your Lambda ARN
- Guide you through the entire setup process

### 2. Config File Mode

Create a configuration file based on the provided template:

```bash
# Copy and edit the template
cp fivetran_config_template.json fivetran_config.json
# Edit the file with your credentials
nano fivetran_config.json
```

Then run the script with the config file:

```bash
python fivetran_api_setup.py --config fivetran_config.json
```

### 3. Command Line Arguments

You can also provide all parameters directly:

```bash
python fivetran_api_setup.py \
  --api-key YOUR_API_KEY \
  --api-secret YOUR_API_SECRET \
  --group-id YOUR_GROUP_ID \
  --destination-id YOUR_DESTINATION_ID \
  --lambda-arn YOUR_LAMBDA_ARN \
  --prohandel-username YOUR_USERNAME \
  --prohandel-password YOUR_PASSWORD
```

## What the Script Does

The script automates the following steps:

1. **Creates a new connector** in your Fivetran account
2. **Configures the connector** with your Lambda function ARN and ProHandel credentials
3. **Tests the connection** to ensure everything is working
4. **Configures the schema** to sync all tables and columns
5. **Sets the destination** where the data will be loaded
6. **Sets the sync schedule** to hourly (configurable)
7. **Starts the initial sync**

## Monitoring the Sync

After the script completes, you can monitor the sync process using:

1. The Fivetran dashboard
2. The `monitor_sync.py` script:

```bash
python monitor_sync.py --config data_quality_config.json
```

## Troubleshooting

If you encounter any issues:

1. **API Authentication Errors**:
   - Verify your API key and secret are correct
   - Check that your API key has the necessary permissions

2. **Connector Creation Errors**:
   - Make sure you have the right group ID
   - Check that you don't have too many connectors in your account

3. **Connection Test Failures**:
   - Verify your Lambda ARN is correct
   - Check that your ProHandel credentials are valid
   - Look at the AWS CloudWatch logs for the Lambda function

4. **Schema Configuration Errors**:
   - Make sure the Lambda function is returning the correct schema
   - Check that you have permissions to modify the schema

5. **Destination Errors**:
   - Verify your destination ID is correct
   - Make sure the destination is properly configured

## Next Steps

After the Fivetran connector is set up and syncing:

1. Run data quality checks:
   ```bash
   python data_quality_monitor.py --config data_quality_config.json
   ```

2. Set up and run dbt models:
   ```bash
   ./run_dbt_models.sh
   ```

3. Create dashboards based on the transformed data

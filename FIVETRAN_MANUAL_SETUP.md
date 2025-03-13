# Fivetran Manual Setup Guide

Since we're encountering some issues with the Fivetran API for creating a new connector, let's follow a hybrid approach:

1. Create the connector manually through the Fivetran UI
2. Use the API to configure and monitor the connector

## Step 1: Create the AWS Lambda Connector in Fivetran UI

1. Log in to your Fivetran account at [https://fivetran.com/dashboard](https://fivetran.com/dashboard)
2. Click "Add Connector" in the top right corner
3. In the search bar, type "AWS Lambda" and select it from the results
4. Configure the connector with the following details:
   - **Connector Name**: ProHandel Data
   - **Schema Name**: prohandel_data
   - **Group**: Warehouse (look_frescoes)

## Step 2: Configure AWS Lambda Details

Enter the following AWS details:

1. **AWS Region**: `eu-central-1`
2. **External ID**: `look_frescoes` (this should be pre-filled)
3. **Role ARN**: `arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole`
4. **Lambda Function ARN**: `arn:aws:lambda:eu-central-1:689864027744:function:prohandel-fivetran-connector`
5. **Execution Timeout**: `180` seconds (3 minutes)

## Step 3: Add Secrets

Add the following secrets that will be passed to your Lambda function:

1. Click "Add Secret"
2. Add the following key-value pairs:
   - Key: `PROHANDEL_API_KEY`, Value: `7e7c639358434c4fa215d4e3978739d0`
   - Key: `PROHANDEL_API_SECRET`, Value: `1cjnuux79d`
   - Key: `PROHANDEL_AUTH_URL`, Value: `https://auth.prohandel.cloud/api/v4`
   - Key: `PROHANDEL_API_URL`, Value: `https://api.prohandel.de/api/v2`

## Step 4: Test the Connection

1. Click "Save & Test"
2. Fivetran will test the connection to your Lambda function
3. If successful, you'll see a confirmation message
4. If unsuccessful, check the error message and troubleshoot accordingly

## Step 5: Configure Schema

1. After the test is successful, Fivetran will retrieve the schema from your Lambda function
2. Review the tables and columns that will be synced
3. Select all tables to sync

## Step 6: Set Sync Schedule

1. Set the sync frequency to hourly (60 minutes)
2. Click "Save" to start the initial sync

## Step 7: Monitor the Sync

After setting up the connector, you can monitor the sync process using:

1. The Fivetran dashboard
2. Our monitoring script:

```bash
python monitor_sync.py
```

## Step 8: Run Data Quality Checks

After the initial sync completes, run data quality checks:

```bash
python data_quality_monitor.py --config data_quality_config.json
```

## Step 9: Set Up dbt Models

Set up and run the dbt models:

```bash
./run_dbt_models.sh
```

## Step 10: Create Dashboards

Create dashboards based on the transformed data using the configuration in `dashboard_config.json`.

# ProHandel Fivetran Connector Configuration Guide

This guide provides step-by-step instructions for configuring the ProHandel AWS Lambda connector in Fivetran.

## Prerequisites

Before you begin, ensure you have:

1. AWS account with appropriate permissions
2. ProHandel API credentials (username and password)
3. Fivetran account with admin access
4. AWS Lambda function deployed (see SETUP_GUIDE.md)

## Step 1: Create a New Connector in Fivetran

1. Log in to your Fivetran account at [https://fivetran.com/dashboard](https://fivetran.com/dashboard)
2. Click "Add Connector" in the top right corner
3. In the search bar, type "AWS Lambda" and select it from the results
4. Configure the connector with a descriptive name (e.g., "ProHandel Data")

## Step 2: Configure AWS Lambda Details

Enter the following AWS details:

1. **AWS Region**: `eu-central-1` (or your deployed region)
2. **Lambda Function ARN**: The ARN of your deployed Lambda function (output from deploy.sh)
3. **Execution Timeout**: `180` seconds (3 minutes)

### Secrets Configuration

Add the following secrets that will be passed to your Lambda function:

1. Click "Add Secret"
2. Add the following key-value pairs:
   - Key: `PROHANDEL_USERNAME`, Value: Your ProHandel username
   - Key: `PROHANDEL_PASSWORD`, Value: Your ProHandel password
   - Key: `PROHANDEL_AUTH_URL`, Value: `https://auth.prohandel.cloud/api/v4`
   - Key: `PROHANDEL_API_URL`, Value: `https://api.prohandel.de/api/v2`

## Step 3: Test the Connection

1. Click "Save & Test"
2. Fivetran will test the connection to your Lambda function
3. If successful, you'll see a confirmation message
4. If unsuccessful, check the error message and troubleshoot accordingly

## Step 4: Configure Schema

1. After the test is successful, Fivetran will retrieve the schema from your Lambda function
2. Review the tables and columns that will be synced
3. Select the tables you want to sync:
   - `article`: Product information
   - `customer`: Customer data
   - `order`: Order information
   - `sale`: Sales transactions
   - `inventory`: Stock levels
   - `shop`: Store/branch information
   - `daily_sales_agg`: Daily sales aggregations
   - `article_sales_agg`: Sales aggregated by article
   - `warehouse_inventory_agg`: Inventory aggregated by warehouse

4. For each table, you can:
   - Enable/disable the table
   - Select which columns to sync
   - Set up transformations (if needed)

## Step 5: Configure Destination

1. Select your destination database (e.g., Snowflake, BigQuery, Redshift)
2. Configure the destination settings:
   - Schema name (e.g., `prohandel_data`)
   - Connection details (if not already configured)

## Step 6: Set Sync Schedule

1. Choose a sync frequency that meets your business needs:
   - For real-time analytics: Every 15 minutes or hourly
   - For daily reporting: Daily
   - For less frequent analysis: Weekly

2. Set the start time for the initial sync

## Step 7: Start Initial Sync

1. Review your configuration
2. Click "Save & Start" to begin the initial sync
3. Monitor the sync progress in the Fivetran dashboard

## Monitoring and Maintenance

### Monitoring Sync Status

1. Navigate to your connector in the Fivetran dashboard
2. View the sync history and status
3. Check for any errors or warnings

### Troubleshooting Common Issues

1. **Authentication Errors**:
   - Verify your ProHandel credentials
   - Check that the secrets are correctly configured in Fivetran

2. **Timeout Errors**:
   - Increase the execution timeout in the connector settings
   - Consider optimizing the Lambda function for performance

3. **Missing Data**:
   - Verify that the ProHandel API is returning the expected data
   - Check the Lambda function logs in AWS CloudWatch

### Updating the Connector

If you need to update the connector:

1. Deploy the updated Lambda function using the deploy.sh script
2. In Fivetran, navigate to your connector settings
3. Click "Re-test Connection" to verify the updated function works
4. Resume the sync

## Support Resources

- For issues with the ProHandel API: Contact ProHandel support
- For issues with the Lambda function: Check AWS CloudWatch logs
- For issues with Fivetran: Contact Fivetran support at [support@fivetran.com](mailto:support@fivetran.com)

## Data Schema Reference

For a detailed reference of the data schema and available tables, refer to the schema documentation in the repository.

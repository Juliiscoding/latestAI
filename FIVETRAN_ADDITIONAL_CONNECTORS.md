# Setting Up Additional Fivetran Connectors

This guide covers the setup of additional connectors for your Fivetran integration, specifically the AWS Lambda connector for your ProHandel API and the Shopify connector.

## 1. AWS Lambda Connector Setup

The AWS Lambda connector will connect to your existing `prohandel-fivetran-connector` Lambda function.

### Prerequisites
- Your Lambda function is already deployed to AWS (ARN: `arn:aws:lambda:eu-central-1:689864027744:function:prohandel-fivetran-connector`)
- The IAM role `ProHandelFivetranConnectorRole` has been created with appropriate permissions

### Setup Steps

1. In the Fivetran dashboard, click **Add connection**
2. Search for and select **AWS Lambda**
3. Configure the connector with the following settings:
   - **Connection Name**: `prohandel-api`
   - **AWS Region**: `eu-central-1`
   - **Function Name**: `prohandel-fivetran-connector`
   - **Authentication Method**: Select "AWS IAM User" 
   - **AWS Access Key ID**: Enter your AWS access key
   - **AWS Secret Access Key**: Enter your AWS secret key
   - **Sync Frequency**: Set to your preferred frequency (recommended: 6 hours)

4. Click **Save & Test** to verify the connection
5. Once the test is successful, click **Continue**
6. Review the schema and click **Save & Continue**
7. Start the initial sync

## 2. Shopify Connector Setup

The Shopify connector will sync your Shopify store data to Snowflake.

### Prerequisites
- Active Shopify store
- Admin access to your Shopify account
- Shopify API credentials

### Setup Steps

1. In the Fivetran dashboard, click **Add connection**
2. Search for and select **Shopify**
3. Configure the connector with the following settings:
   - **Connection Name**: `shopify-store`
   - **Shop Name**: Enter your Shopify store name (the part before `.myshopify.com`)
   - **API Version**: Select the latest available version
   - **Authentication Method**: Select "API Password"
   - **API Key**: Enter your Shopify API key
   - **API Password**: Enter your Shopify API password
   - **Shared Secret**: Enter your Shopify shared secret
   - **Sync Frequency**: Set to your preferred frequency (recommended: 6 hours)

4. Click **Save & Test** to verify the connection
5. Once the test is successful, click **Continue**
6. Review the schema and click **Save & Continue**
7. Start the initial sync

## 3. Integration with Existing Data

### Lambda to Snowflake Integration

The AWS Lambda connector will sync your ProHandel API data to the following tables in Snowflake:

- `ARTICLES`: Product information
- `CUSTOMERS`: Customer data
- `ORDERS`: Order information
- `SALES`: Sales data
- `INVENTORY`: Inventory levels

### Shopify to Snowflake Integration

The Shopify connector will sync your Shopify store data to tables including:

- `ORDERS`: Shopify orders
- `CUSTOMERS`: Shopify customers
- `PRODUCTS`: Shopify products
- `TRANSACTIONS`: Payment transactions
- `INVENTORY_ITEMS`: Inventory information

### Data Transformation

To create a unified view of your data across systems, you'll need to create transformations that:

1. Normalize identifiers between ProHandel and Shopify
2. Create unified customer views
3. Reconcile inventory across systems
4. Match orders between systems

These transformations can be implemented using:
- Fivetran transformations
- dbt models
- Snowflake views and stored procedures

## 4. Monitoring

Once set up, you can monitor these additional connectors using the same monitoring tools we've already created:

```bash
# Generate a monitoring dashboard including the new connectors
python fivetran_dashboard.py

# Check for alerts across all connectors
python fivetran_alerts.py
```

## 5. Troubleshooting

If you encounter issues with the connectors:

### AWS Lambda Connector Issues
- Verify the Lambda function is accessible with the provided credentials
- Check CloudWatch logs for any Lambda execution errors
- Ensure the Lambda function is implementing the Fivetran protocol correctly

### Shopify Connector Issues
- Verify API credentials are correct
- Check for any API rate limiting issues
- Ensure the Shopify store is accessible

For detailed troubleshooting, use:
```bash
python troubleshoot_transformations.py
```

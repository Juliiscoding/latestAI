# Testing Guide for ProHandel AWS Lambda Connector

This guide provides instructions for testing your ProHandel AWS Lambda connector both locally and in AWS.

## Local Testing

### Prerequisites

- Python 3.9 or higher
- Required Python packages installed (`pip install -r requirements.txt`)
- `.env` file with your ProHandel API credentials

### Test Operations

#### 1. Test Connection

To test the basic connection to the ProHandel API:

```bash
python test_lambda.py --operation test
```

Expected output:
```json
{
  "success": true
}
```

#### 2. Test Schema Retrieval

To test schema retrieval:

```bash
python test_lambda.py --operation schema
```

Expected output:
```json
{
  "schema": {
    "tables": {
      "article": {
        "primary_key": ["number"],
        "columns": {
          "number": {"type": "string"},
          "name": {"type": "string"},
          "price": {"type": "number"},
          ...
          "profit_margin": {"type": "number"},
          "price_tier": {"type": "string"}
        }
      },
      ...
      "daily_sales_agg": {
        "primary_key": ["sale_date"],
        "columns": {
          "sale_date": {"type": "string"},
          "sale_count": {"type": "integer"},
          "total_quantity": {"type": "number"},
          "total_amount": {"type": "number"},
          "aggregation_type": {"type": "string"}
        }
      }
    }
  }
}
```

#### 3. Test Data Sync

To test data synchronization with a specific state:

```bash
python test_lambda.py --operation sync --state-days 30
```

This will sync data from the last 30 days.

#### 4. Test Data Enhancement

To test data enhancement and aggregation:

```bash
python test_lambda.py --operation sync --state-days 30 --enhancement
```

This will sync data with enhanced fields and aggregations.

## AWS Lambda Testing

### Testing in AWS Console

1. Navigate to your Lambda function in the AWS Console
2. Click on the "Test" tab
3. Create test events for different operations:

#### Test Connection Event

```json
{
  "request": {
    "operation": "test",
    "secrets": {
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET",
      "api_url": "https://linde.prohandel.de/api/v2"
    }
  }
}
```

#### Schema Event

```json
{
  "request": {
    "operation": "schema",
    "secrets": {
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET",
      "api_url": "https://linde.prohandel.de/api/v2"
    }
  }
}
```

#### Sync Event

```json
{
  "request": {
    "operation": "sync",
    "state": {
      "last_sync": "2023-01-01T00:00:00"
    },
    "secrets": {
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET",
      "api_url": "https://linde.prohandel.de/api/v2"
    }
  }
}
```

### Monitoring Lambda Execution

1. Navigate to CloudWatch in the AWS Console
2. Go to "Log groups"
3. Find and check the log group named "/aws/lambda/ProHandelFivetranConnector"
4. Review the logs for any errors or issues

## Testing with Fivetran

### Initial Connection Test

1. In Fivetran, configure the connector as described in the Fivetran Configuration Guide
2. Click "Save & Test"
3. Fivetran will test the connection to your Lambda function
4. If successful, you'll see a green checkmark and a success message

### Schema Verification

1. After successful connection, Fivetran will retrieve the schema
2. Verify that all expected tables are present:
   - Core tables: article, customer, order, orderposition, sale, inventory
   - Aggregation tables: daily_sales_agg, article_sales_agg, warehouse_inventory_agg
3. Verify that enhanced fields are present in the core tables

### Initial Sync Test

1. Start the initial sync in Fivetran
2. Monitor the sync progress in the Fivetran dashboard
3. Once complete, check your data warehouse for the synced data
4. Verify that data has been properly loaded into all tables

### Data Enhancement Verification

To verify that data enhancement is working correctly:

1. Check the article table for profit_margin and price_tier fields
2. Check the customer table for full_address field
3. Check the order table for delivery_time_days and order_age_days fields
4. Check the sale table for sale_age_days field
5. Check the inventory table for stock_status field

### Aggregation Verification

To verify that data aggregation is working correctly:

1. Check the daily_sales_agg table for daily sales totals
2. Check the article_sales_agg table for sales totals by article
3. Check the warehouse_inventory_agg table for inventory totals by warehouse

## Troubleshooting Common Issues

### Connection Issues

- Verify that your API credentials are correct
- Check that the Lambda function has internet access (if in a VPC)
- Ensure the IAM role has the necessary permissions

### Schema Issues

- Check that the Lambda function can access the ProHandel API
- Verify that the schema definition in the Lambda function matches the expected structure

### Sync Issues

- Check CloudWatch Logs for detailed error messages
- Verify that the state management is working correctly
- Ensure that the Lambda function has enough memory and timeout configured

### Data Enhancement Issues

- Check that pandas and numpy are properly installed in the Lambda package
- Verify that the data structure from the API matches what the enhancer expects
- Check for any errors in the data transformation process

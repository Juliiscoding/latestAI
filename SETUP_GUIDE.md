# ProHandel Fivetran Connector Setup Guide

This guide provides instructions for setting up the ProHandel API connector with Fivetran using AWS Lambda.

## Prerequisites

1. AWS account with permissions to create Lambda functions and IAM roles
2. AWS CLI installed and configured with appropriate credentials
3. ProHandel API credentials (username and password)
4. Fivetran account with access to the AWS Lambda connector

## Setup Steps

### 1. Create IAM Role for Lambda

Create an IAM role that allows the Lambda function to execute and write logs to CloudWatch:

```bash
# Run the setup-iam.sh script
chmod +x setup-iam.sh
./setup-iam.sh
```

### 2. Configure Environment Variables

Before deploying, set your ProHandel API credentials as environment variables:

```bash
export PROHANDEL_USERNAME="your_username"
export PROHANDEL_PASSWORD="your_password"
```

### 3. Deploy the Lambda Function

Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Create a deployment package with all dependencies
- Create or update the Lambda function
- Configure environment variables
- Output the Lambda function ARN

### 4. Configure Fivetran

1. Log in to your Fivetran account
2. Create a new connector and select "AWS Lambda"
3. Enter the Lambda function ARN provided by the deployment script
4. Complete the Fivetran setup process

## Lambda Function Details

- **Runtime**: Python 3.9
- **Memory**: 256 MB
- **Timeout**: 3 minutes
- **Handler**: lambda_function.lambda_handler

## Data Schema

The connector provides the following tables:

| Table Name | Description |
|------------|-------------|
| article | Product information |
| customer | Customer data |
| order | Order information |
| sale | Sales transactions |
| inventory | Stock levels |
| shop | Store/branch information |
| daily_sales_agg | Daily sales aggregations |
| article_sales_agg | Sales aggregated by article |
| warehouse_inventory_agg | Inventory aggregated by warehouse |

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your ProHandel credentials are correctly set as environment variables.

2. **Timeout Errors**: If the Lambda function times out, consider:
   - Increasing the Lambda timeout setting
   - Implementing pagination for large data sets
   - Using incremental loading with state management

3. **Missing Data**: Ensure all required endpoints are accessible with your API credentials.

### Logs

Check CloudWatch Logs for detailed error information:

```bash
aws logs get-log-events --log-group-name /aws/lambda/prohandel-fivetran-connector --log-stream-name $(aws logs describe-log-streams --log-group-name /aws/lambda/prohandel-fivetran-connector --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text)
```

## Maintenance

### Updating the Connector

To update the connector code:

1. Make your changes to the Lambda function code
2. Run the deployment script again
3. Test the updated connector in Fivetran

### Monitoring

Set up CloudWatch Alarms to monitor:
- Lambda function errors
- Lambda function duration
- Lambda function throttling

## Support

For issues with:
- ProHandel API: Contact ProHandel support
- Lambda function: Check CloudWatch logs and update code as needed
- Fivetran integration: Contact Fivetran support

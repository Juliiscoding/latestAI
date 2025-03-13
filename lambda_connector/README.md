# ProHandel AWS Lambda Function for Fivetran

This AWS Lambda function integrates the ProHandel API with Fivetran using the AWS Lambda connector approach. It leverages the existing ProHandel connector code from the Mercurios.ai ETL pipeline.

## Features

- Extracts data from ProHandel API endpoints
- Supports incremental loading based on timestamp fields
- Validates data using existing schema validation
- Handles authentication with ProHandel API
- Compatible with Fivetran's AWS Lambda connector
- Adds calculated fields and derived data to enrich the raw API data
- Creates aggregated views of sales and inventory data for analytics

## Setup Instructions

### 1. Local Development and Testing

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Test the Lambda function locally:
   ```
   python lambda_function.py
   ```

### 2. AWS Lambda Deployment

1. Create a deployment package:
   ```
   pip install -r requirements.txt -t ./package
   cp lambda_function.py ./package/
   cd package
   zip -r ../lambda_deployment.zip .
   ```

2. Create an AWS Lambda function:
   - Runtime: Python 3.9
   - Handler: lambda_function.lambda_handler
   - Memory: 256 MB (increase if needed)
   - Timeout: 3 minutes
   - Environment variables:
     - PROHANDEL_API_KEY: Your ProHandel API key
     - PROHANDEL_API_SECRET: Your ProHandel API secret
     - PROHANDEL_API_URL: ProHandel API URL

3. Upload the deployment package:
   ```
   aws lambda update-function-code --function-name ProHandelFivetranConnector --zip-file fileb://lambda_deployment.zip
   ```

### 3. Fivetran Configuration

1. Create a new AWS Lambda connector in Fivetran
2. Configure the connector with your Lambda function ARN
3. Set up the required secrets:
   - api_key: Your ProHandel API key
   - api_secret: Your ProHandel API secret
   - api_url: ProHandel API URL

## Data Flow

1. Fivetran invokes the Lambda function with an operation request (test, schema, or sync)
2. The Lambda function processes the request using the ProHandel connector
3. For sync operations, the function extracts data incrementally based on the last sync timestamp
4. The function returns the data to Fivetran, which loads it into your destination

## Enhanced Data Features

The connector enhances the raw ProHandel data with additional calculated fields and aggregations:

### Enhanced Fields

- **Articles**:
  - `profit_margin`: Calculated profit margin percentage
  - `price_tier`: Categorization of articles by price range

- **Customers**:
  - `full_address`: Concatenated address fields

- **Orders**:
  - `delivery_time_days`: Days between order and delivery
  - `order_age_days`: Days since the order was placed

- **Sales**:
  - `sale_age_days`: Days since the sale occurred

- **Inventory**:
  - `stock_status`: Categorization of stock levels

### Aggregated Tables

- **Daily Sales Aggregation**:
  - Daily totals of sales, quantities, and amounts

- **Article Sales Aggregation**:
  - Total sales, quantities, and amounts by article

- **Warehouse Inventory Aggregation**:
  - Total article count and quantities by warehouse

## Troubleshooting

- Check CloudWatch Logs for detailed error messages
- Ensure your Lambda function has sufficient memory and timeout settings
- Verify that your API credentials are correct
- For schema issues, check the sample data returned by the API

## Advanced Configuration

You can modify the `lambda_function.py` file to:
- Add data transformations before sending to Fivetran
- Implement custom aggregations
- Add data quality checks
- Filter sensitive data
- Enhance data with additional fields

# Enhanced ProHandel Fivetran Connector

This is an enhanced AWS Lambda function for connecting the ProHandel API to Fivetran. It includes features for incremental loading, data transformation, and a comprehensive schema.

## Features

1. **Real ProHandel API Integration**:
   - Connects to the ProHandel API using authentication
   - Fetches data from multiple endpoints (articles, customers, orders, sales, inventory)
   - Handles pagination for large datasets

2. **Comprehensive Schema**:
   - Includes all major tables from the ProHandel API
   - Defines appropriate data types for all columns
   - Includes primary keys for proper data synchronization

3. **Incremental Loading**:
   - Tracks last sync timestamp for each entity type
   - Only fetches data that has changed since the last sync
   - Optimizes data transfer and reduces API load

4. **Data Transformation**:
   - Adds calculated fields (profit margins, stock status)
   - Creates full addresses from component fields
   - Calculates age metrics for orders and sales
   - Standardizes data formats

5. **Error Handling**:
   - Comprehensive error logging to `/tmp/logs`
   - Detailed error messages for troubleshooting
   - Graceful handling of API failures

## Files

- `lambda_function.py` - Main Lambda handler implementing the Fivetran connector protocol
- `prohandel_api.py` - ProHandel API client for data fetching
- `data_processor.py` - Data transformation and processing logic
- `schema.py` - Schema definitions for all tables
- `requirements.txt` - Python dependencies
- `deploy.py` - Deployment script for the Lambda function

## Deployment

To deploy the enhanced Lambda function:

1. Make sure you have AWS CLI configured with appropriate credentials
2. Run the deployment script:

```bash
python deploy.py
```

The script will:
- Install dependencies
- Package the Lambda function code
- Update the Lambda function in AWS
- Configure environment variables and Lambda settings

## Environment Variables

The Lambda function uses the following environment variables:

- `PROHANDEL_API_KEY` - ProHandel API key
- `PROHANDEL_API_SECRET` - ProHandel API secret

These are set automatically by the deployment script.

## Testing

After deployment, you can test the connector in Fivetran by clicking "Save & Test" in the Fivetran UI. The connector should:

1. Successfully connect to the ProHandel API
2. Return the schema for all tables
3. Begin syncing data incrementally

## Next Steps

Future enhancements could include:

1. Adding more data validation
2. Implementing more complex transformations
3. Adding support for deleting records
4. Optimizing performance for very large datasets

# ProHandel API Monitoring Guide

This guide provides instructions for monitoring the ProHandel API integration, setting up CloudWatch alarms, and addressing the shop endpoint issue.

## Monitoring the Shop Endpoint

### Current Status

During testing, we observed that the shop endpoint does not return any data. This could be due to:

1. No shop records exist in the system
2. The endpoint configuration is incorrect
3. The API credentials do not have permission to access shop data
4. The shop endpoint requires additional parameters

### Recommended Actions

1. **Verify with ProHandel Support**:
   - Contact ProHandel support to confirm if the shop endpoint should return data
   - Verify if additional parameters are required for this endpoint
   - Confirm that your API credentials have the necessary permissions

2. **Test with Different Parameters**:
   ```python
   from etl.connectors.prohandel_connector import ProHandelConnector
   
   connector = ProHandelConnector()
   
   # Try with different parameters
   shops = connector.get_entity_list('shop', params={'active': True})
   print(f"Number of shops: {len(shops)}")
   print(shops)
   ```

3. **Monitor API Responses**:
   - Add detailed logging for the shop endpoint
   - Check response headers and status codes
   - Look for any error messages in the response body

## Setting Up CloudWatch Alarms

### Lambda Function Metrics to Monitor

1. **Invocation Errors**:
   - Monitors failed Lambda function executions
   - Recommended threshold: > 0 errors in 5 minutes

2. **Duration**:
   - Monitors execution time
   - Recommended threshold: > 120 seconds (out of 180 second timeout)

3. **Throttles**:
   - Monitors when Lambda function is throttled
   - Recommended threshold: > 0 throttles in 5 minutes

4. **Memory Usage**:
   - Monitors memory utilization
   - Recommended threshold: > 200 MB (out of 256 MB allocated)

### Setting Up Alarms in AWS Console

1. **Navigate to CloudWatch**:
   - Log in to AWS Management Console
   - Go to CloudWatch service

2. **Create Alarms for Invocation Errors**:
   - Click "Alarms" in the left sidebar
   - Click "Create alarm"
   - Click "Select metric"
   - Choose "Lambda" > "By Function Name"
   - Find and select "Errors" for your function
   - Click "Select metric"
   - Set the period to 5 minutes
   - Set the threshold to "Greater than 0"
   - Click "Next"
   - Configure notification settings (SNS topic or email)
   - Add a name and description
   - Click "Create alarm"

3. **Repeat for Other Metrics**:
   - Follow the same process for Duration, Throttles, and Memory Usage
   - Adjust thresholds as recommended above

### Setting Up Log-Based Alarms

1. **Create Metric Filters**:
   - Go to CloudWatch > "Log groups"
   - Select your Lambda function's log group
   - Click "Metric filters"
   - Click "Create metric filter"
   - Define filter patterns for errors (e.g., "ERROR", "Exception", "Timeout")
   - Create a metric for each filter
   - Create alarms based on these metrics

## Documenting API Schema

The ProHandel API schema can be documented for future reference:

1. **Extract Schema Information**:
   ```python
   import json
   from lambda_function import lambda_handler
   
   # Simulate a Fivetran schema request
   event = {
       "request": {
           "operation": "schema"
       }
   }
   
   # Call the Lambda handler
   response = lambda_handler(event, None)
   
   # Save the schema to a file
   with open('prohandel_api_schema.json', 'w') as f:
       json.dump(response, f, indent=2)
   ```

2. **Generate HTML Documentation**:
   - Use a tool like [JSON Schema Viewer](https://github.com/jlblcc/json-schema-viewer)
   - Or convert to Markdown for easier reading

3. **Key Schema Components to Document**:
   - Entity types and their relationships
   - Required fields and data types
   - Field descriptions and constraints
   - Example values for each field

## Implementing Data Quality Monitoring

### Key Data Quality Metrics

1. **Completeness**:
   - Monitor percentage of null values in critical fields
   - Alert if completeness falls below thresholds

2. **Timeliness**:
   - Monitor data freshness (time since last update)
   - Alert if data is older than expected

3. **Consistency**:
   - Check for referential integrity between related entities
   - Verify that calculated fields match expected values

4. **Volume**:
   - Monitor record counts for each entity
   - Alert on unexpected changes in data volume

### Implementation Approach

1. **Add Data Quality Checks to Lambda Function**:
   ```python
   def check_data_quality(entity_name, data):
       """Check data quality for an entity."""
       quality_issues = []
       
       # Check completeness
       for record in data:
           for key_field in ['id', 'name']:
               if key_field not in record or record[key_field] is None:
                   quality_issues.append(f"Missing {key_field} in {entity_name} record {record.get('id', 'unknown')}")
       
       # Check volume
       if len(data) == 0:
           quality_issues.append(f"No records found for {entity_name}")
       
       # Log quality issues
       if quality_issues:
           logger.warning(f"Data quality issues found: {quality_issues}")
       
       return quality_issues
   ```

2. **Add to Sync Operation**:
   ```python
   # In the sync operation handler
   quality_issues = check_data_quality(entity_name, data)
   if quality_issues:
       # Add quality issues to metadata
       metadata = {
           "quality_issues": quality_issues
       }
   ```

3. **Set Up Monitoring Dashboard**:
   - Create a CloudWatch dashboard for data quality metrics
   - Include visualizations for completeness, timeliness, etc.
   - Set up alarms for critical data quality issues

## Next Steps

1. Contact ProHandel support about the shop endpoint
2. Implement CloudWatch alarms for the Lambda function
3. Document the API schema for all entities
4. Implement data quality monitoring
5. Set up regular testing of all API endpoints

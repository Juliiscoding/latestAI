import os
import json
import logging
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

import boto3
from prohandel_api import ProHandelAPI
from data_processor import DataProcessor
from schema import get_schema

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler for detailed logs
file_handler = logging.FileHandler('/tmp/lambda_logs.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class EnhancedLambdaHandler:
    """Enhanced Lambda handler for ProHandel API integration with Fivetran."""
    
    def __init__(self):
        """Initialize the Lambda handler with API credentials."""
        self.api_key = os.environ.get('PROHANDEL_API_KEY')
        self.api_secret = os.environ.get('PROHANDEL_API_SECRET')
        self.tenant_id = os.environ.get('TENANT_ID', 'default')  # Get tenant ID from environment variable
        
        if not self.api_key or not self.api_secret:
            logger.error("API credentials not found in environment variables")
            raise ValueError("API credentials not found in environment variables")
        
        self.api = ProHandelAPI(self.api_key, self.api_secret)
        self.processor = DataProcessor(self.api)
        self.schema = get_schema()
        
        logger.info(f"Initialized Lambda handler for tenant: {self.tenant_id}")
    
    def add_tenant_id_to_data(self, data: List[Dict]) -> List[Dict]:
        """Add tenant_id to all data records."""
        for record in data:
            record['tenant_id'] = self.tenant_id
        return data
    
    def handle_request(self, event: Dict) -> Dict:
        """Handle incoming Fivetran requests."""
        try:
            # Sanitize event for logging (hide secrets)
            event_log = {k: v for k, v in event.items() if k != 'secrets'}
            if 'secrets' in event:
                event_log['secrets'] = {k: '***' for k in event.get('secrets', {}).keys()}
            logger.info(f"Received event (sanitized): {json.dumps(event_log)}")
            
            # Log all keys in the event for debugging
            logger.info(f"Event keys: {list(event.keys())}")
            
            # Determine the request type based on the event structure
            # Fivetran sometimes doesn't include an explicit 'operation' field
            operation = event.get('operation', '')
            state = event.get('state', {})
            agent = event.get('agent', '')
            sync_id = event.get('sync_id', '')
            
            # If operation is not explicitly set, infer it from the event structure
            if not operation:
                if 'schema' in event:
                    # If event contains a schema field, it's likely a schema update
                    operation = 'schema'
                    logger.info("Inferred operation type: schema")
                elif state is not None and (agent or sync_id):
                    # If event contains state and agent/sync_id, it's likely a sync operation
                    operation = 'sync'
                    logger.info("Inferred operation type: sync")
                elif len(event) == 0 or (state is not None and len(event) <= 3):
                    # Empty event or minimal event with just state is likely a test
                    operation = 'test'
                    logger.info("Inferred operation type: test")
                else:
                    # Default to test operation if we can't determine
                    logger.warning(f"Could not clearly determine operation type from event structure: {list(event.keys())}")
                    operation = 'test'
                    logger.info("Defaulting to operation type: test")
                    
            logger.info(f"Processing {operation} operation for agent: {agent}")
            
            # Handle different operations
            if operation == 'test':
                return self.handle_test()
            elif operation == 'schema':
                return self.handle_schema()
            elif operation == 'sync':
                return self.handle_sync(state)
            else:
                logger.error(f"Unsupported operation: {operation}")
                return {
                    'error': f"Unsupported operation: {operation}",
                    'message': "This connector supports test, schema, and sync operations only."
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'error': str(e),
                'message': "An error occurred while processing the request. Check logs for details.",
                'stacktrace': traceback.format_exc()
            }
    
    def handle_test(self) -> Dict:
        """Handle test operation by validating API credentials."""
        try:
            logger.info("Testing connection to ProHandel API")
            
            # Attempt to authenticate with the API
            token = self.api.authenticate()
            if not token:
                logger.error("Failed to authenticate with ProHandel API")
                return {
                    'success': False,
                    'message': "Failed to authenticate with ProHandel API. Check credentials."
                }
            
            logger.info("Successfully authenticated with ProHandel API")
            return {
                'success': True,
                'message': f"Successfully connected to ProHandel API for tenant: {self.tenant_id}"
            }
            
        except Exception as e:
            logger.error(f"Test operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'message': f"Failed to connect to ProHandel API: {str(e)}"
            }
    
    def handle_schema(self) -> Dict:
        """Handle schema operation by returning the connector schema."""
        try:
            logger.info("Generating schema for Fivetran")
            
            # Add tenant_id to all table schemas
            schema = self.schema.copy()
            for table_name, table_info in schema['tables'].items():
                # Add tenant_id as the first column in primary key
                if 'primary_key' in table_info:
                    table_info['primary_key'] = ['tenant_id'] + table_info['primary_key']
                else:
                    table_info['primary_key'] = ['tenant_id']
                
                # Add tenant_id column to each table
                table_info['columns']['tenant_id'] = 'string'
            
            logger.info("Schema generation complete")
            return {
                'schema': schema
            }
            
        except Exception as e:
            logger.error(f"Schema operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'error': str(e),
                'message': "Failed to generate schema"
            }
    
    def handle_sync(self, state: Dict) -> Dict:
        """Handle sync operation by fetching and processing data."""
        try:
            logger.info(f"Starting sync operation with state: {json.dumps(state)}")
            
            # Initialize state if empty
            if not state:
                state = {
                    'articles': None,
                    'customers': None,
                    'orders': None,
                    'sales': None,
                    'inventory': None,
                    'last_sync_time': None
                }
            
            # Get last sync time for each entity
            articles_since = state.get('articles')
            customers_since = state.get('customers')
            orders_since = state.get('orders')
            sales_since = state.get('sales')
            inventory_since = state.get('inventory')
            
            # Process data with incremental loading
            logger.info("Processing articles data")
            articles_data = self.processor.process_articles(updated_since=articles_since)
            articles_data = self.add_tenant_id_to_data(articles_data)
            
            logger.info("Processing customers data")
            customers_data = self.processor.process_customers(updated_since=customers_since)
            customers_data = self.add_tenant_id_to_data(customers_data)
            
            logger.info("Processing orders data")
            orders_data = self.processor.process_orders(updated_since=orders_since)
            orders_data = self.add_tenant_id_to_data(orders_data)
            
            logger.info("Processing sales data")
            sales_data = self.processor.process_sales(updated_since=sales_since)
            sales_data = self.add_tenant_id_to_data(sales_data)
            
            logger.info("Processing inventory data")
            inventory_data = self.processor.process_inventory(updated_since=inventory_since)
            inventory_data = self.add_tenant_id_to_data(inventory_data)
            
            # Update state with current timestamp
            current_time = datetime.utcnow().isoformat()
            new_state = {
                'articles': current_time,
                'customers': current_time,
                'orders': current_time,
                'sales': current_time,
                'inventory': current_time,
                'last_sync_time': current_time
            }
            
            # Log data counts for monitoring
            logger.info(f"Processed {len(articles_data)} articles")
            logger.info(f"Processed {len(customers_data)} customers")
            logger.info(f"Processed {len(orders_data)} orders")
            logger.info(f"Processed {len(sales_data)} sales")
            logger.info(f"Processed {len(inventory_data)} inventory items")
            
            # Prepare response with data and updated state
            # Format the response according to Fivetran's requirements
            # Each table should have an array of records with proper column names
            response = {
                'state': new_state,
                'insert': {
                    'articles': articles_data if articles_data else [],
                    'customers': customers_data if customers_data else [],
                    'orders': orders_data if orders_data else [],
                    'sales': sales_data if sales_data else [],
                    'inventory': inventory_data if inventory_data else []
                },
                'delete': {},
                'schema': self.schema
            }
            
            logger.info("Sync operation completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Sync operation failed: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'error': str(e),
                'message': "Failed to sync data from ProHandel API",
                'stacktrace': traceback.format_exc()
            }

    def validate_data_quality(self, data: List[Dict], entity_type: str) -> Tuple[List[Dict], List[Dict]]:
        """Validate data quality and return valid and invalid records."""
        valid_records = []
        invalid_records = []
        
        schema_columns = self.schema['tables'].get(entity_type, {}).get('columns', {})
        required_fields = [field for field, type_info in schema_columns.items() 
                          if not field.startswith('_') and field != 'tenant_id']
        
        for record in data:
            is_valid = True
            validation_errors = []
            
            # Check for required fields
            for field in required_fields:
                if field not in record or record[field] is None:
                    is_valid = False
                    validation_errors.append(f"Missing required field: {field}")
            
            # Add validation result
            if is_valid:
                valid_records.append(record)
            else:
                record['_validation_errors'] = validation_errors
                invalid_records.append(record)
        
        # Log validation results
        if invalid_records:
            logger.warning(f"Found {len(invalid_records)} invalid {entity_type} records")
            
        return valid_records, invalid_records

# Lambda handler function
def lambda_handler(event, context):
    """AWS Lambda handler function."""
    try:
        # Log the incoming event with a truncated version for readability
        event_log = {k: v for k, v in event.items() if k != 'secrets'}
        if 'secrets' in event:
            event_log['secrets'] = {k: '***' for k in event.get('secrets', {}).keys()}
        
        logger.info(f"Lambda invoked with event (sanitized): {json.dumps(event_log)}")
        logger.info(f"Event keys: {list(event.keys()) if event else []}")
        
        # Check if event is None or empty
        if not event:
            logger.warning("Received empty event, treating as a test operation")
            event = {"operation": "test"}
        
        # Detect the request type based on event structure if not explicitly provided
        if 'type' in event and not 'operation' in event:
            # Convert Fivetran 'type' field to 'operation' for compatibility
            event['operation'] = event['type']
            logger.info(f"Converted 'type' to 'operation': {event['operation']}")
        
        # Infer operation type from event structure if not explicitly provided
        if not 'operation' in event:
            if 'schema' in event:
                event['operation'] = 'schema'
                logger.info("Inferred operation type: schema")
            elif 'state' in event and ('agent' in event or 'sync_id' in event):
                event['operation'] = 'sync'
                logger.info("Inferred operation type: sync")
            elif 'setup_test' in event and event.get('setup_test') is True:
                event['operation'] = 'test'
                logger.info("Inferred operation type: test (setup test)")
            else:
                event['operation'] = 'test'
                logger.info("Inferred operation type: test (default)")
        
        # Initialize handler and process the request
        handler = EnhancedLambdaHandler()
        response = handler.handle_request(event)
        
        # Create a separate log-friendly copy of the response (excluding large data payloads)
        # Important: This must not modify the original response object
        response_log = {}
        for key, value in response.items():
            if key == 'insert' and isinstance(value, dict):
                response_log[key] = {}
                for table, data in value.items():
                    if isinstance(data, list):
                        response_log[key][table] = f"[{len(data)} records]"
                    else:
                        response_log[key][table] = str(data)
            else:
                response_log[key] = value
        
        # Log the operation type that was used
        logger.info(f"Operation type used: {event.get('operation', 'inferred')}")
        
        logger.info(f"Lambda response: {json.dumps(response_log)}")
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Send error metric to CloudWatch
        try:
            cloudwatch = boto3.client('cloudwatch')
            cloudwatch.put_metric_data(
                Namespace='ProHandelConnector',
                MetricData=[
                    {
                        'MetricName': 'LambdaErrors',
                        'Value': 1,
                        'Unit': 'Count'
                    },
                ]
            )
        except Exception as metric_error:
            logger.error(f"Failed to send error metric: {str(metric_error)}")
        
        return {
            'error': str(e),
            'message': "An unexpected error occurred in the Lambda function",
            'stacktrace': traceback.format_exc()
        }

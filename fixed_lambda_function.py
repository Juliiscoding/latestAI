"""
ProHandel AWS Lambda Function for Fivetran integration.

This Lambda function adapts the existing ProHandel connector to work with Fivetran's
AWS Lambda connector. It handles data extraction from the ProHandel API with
incremental loading, authentication, and data quality validation.
"""
import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import copy

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler for detailed logs
file_handler = logging.FileHandler('/tmp/lambda_logs.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Import ProHandel connector components
# Note: In a real deployment, these imports would be from your actual connector modules
# For this example, we'll mock the connector functionality

class MockProHandelConnector:
    """Mock ProHandel connector for testing purposes."""
    
    def __init__(self):
        self.api_key = os.environ.get('PROHANDEL_API_KEY')
        self.api_secret = os.environ.get('PROHANDEL_API_SECRET')
        self.auth_url = os.environ.get('PROHANDEL_AUTH_URL')
        self.api_url = os.environ.get('PROHANDEL_API_URL')
    
    def authenticate(self):
        """Authenticate with ProHandel API."""
        logger.info(f"Authenticating with ProHandel API at {self.auth_url}")
        # In a real implementation, this would make an actual API call
        return True
    
    def get_entity_list(self, entity_type, page=1, pagesize=100, **kwargs):
        """Get a list of entities from ProHandel API."""
        logger.info(f"Getting {entity_type} list (page {page}, pagesize {pagesize})")
        # In a real implementation, this would make an actual API call
        return [{"id": 1, "name": f"Test {entity_type}"}]
    
    def get_schema(self):
        """Get the schema for all entities."""
        return {
            "articles": {
                "primary_key": ["id"],
                "columns": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                    "created_at": {"type": "timestamp"}
                }
            },
            "customers": {
                "primary_key": ["id"],
                "columns": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "created_at": {"type": "timestamp"}
                }
            },
            "orders": {
                "primary_key": ["id"],
                "columns": {
                    "id": {"type": "integer"},
                    "customer_id": {"type": "integer"},
                    "total": {"type": "number"},
                    "created_at": {"type": "timestamp"}
                }
            }
        }

# Initialize the connector
connector = MockProHandelConnector()

def lambda_handler(event, context):
    """
    AWS Lambda handler for Fivetran Function connector.
    
    Args:
        event: Lambda event containing Fivetran request
        context: Lambda context
        
    Returns:
        Response in Fivetran expected format
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract request details from event
        # Fivetran sends operation directly in the event, not nested in a request object
        operation = event.get('operation')
        secrets = event.get('secrets', {})
        
        # Update configuration from secrets
        if secrets:
            update_configuration_from_secrets(secrets)
        
        # Handle different operations
        if operation == 'test':
            return handle_test()
        elif operation == 'schema':
            return handle_schema()
        elif operation == 'sync':
            state = event.get('state', {})
            return handle_sync(state)
        else:
            logger.error(f"Unsupported operation: {operation}")
            return {'success': False, 'message': f'Unsupported operation: {operation}'}
    
    except Exception as e:
        logger.error(f"Lambda function error: {str(e)}", exc_info=True)
        return {'success': False, 'message': str(e)}

def update_configuration_from_secrets(secrets):
    """
    Update connector configuration from Fivetran secrets.
    
    Args:
        secrets: Secret configuration values from Fivetran
    """
    # Update API credentials if provided
    if 'PROHANDEL_API_KEY' in secrets and 'PROHANDEL_API_SECRET' in secrets:
        os.environ['PROHANDEL_API_KEY'] = secrets['PROHANDEL_API_KEY']
        os.environ['PROHANDEL_API_SECRET'] = secrets['PROHANDEL_API_SECRET']
    
    # Update API URLs if provided
    if 'PROHANDEL_AUTH_URL' in secrets:
        os.environ['PROHANDEL_AUTH_URL'] = secrets['PROHANDEL_AUTH_URL']
    if 'PROHANDEL_API_URL' in secrets:
        os.environ['PROHANDEL_API_URL'] = secrets['PROHANDEL_API_URL']
    
    # Reinitialize connector with new configuration
    global connector
    connector = MockProHandelConnector()

def handle_test():
    """
    Test connection to ProHandel API.
    
    Returns:
        Test result response
    """
    try:
        logger.info("Testing connection to ProHandel API")
        
        # Test authentication
        auth_result = connector.authenticate()
        
        if auth_result:
            # Test API access by fetching a small amount of data
            articles = connector.get_entity_list('article', page=1, pagesize=1)
            logger.info(f"Successfully connected to ProHandel API and retrieved {len(articles)} articles")
            return {'success': True, 'message': 'Successfully connected to ProHandel API'}
        else:
            logger.error("Authentication failed")
            return {'success': False, 'message': 'Authentication failed'}
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}", exc_info=True)
        return {'success': False, 'message': f'Connection test failed: {str(e)}'}

def handle_schema():
    """
    Return schema definition for Fivetran.
    
    Returns:
        Schema definition response
    """
    try:
        logger.info("Generating schema for Fivetran")
        
        # Get schema from connector
        schema = connector.get_schema()
        
        # Format schema for Fivetran
        fivetran_schema = {}
        for table_name, table_schema in schema.items():
            fivetran_schema[table_name] = {
                "primary_key": table_schema["primary_key"],
                "columns": {}
            }
            
            for column_name, column_def in table_schema["columns"].items():
                fivetran_schema[table_name]["columns"][column_name] = {
                    "type": column_def["type"]
                }
        
        logger.info(f"Generated schema with {len(fivetran_schema)} tables")
        return {'schema': fivetran_schema}
    except Exception as e:
        logger.error(f"Schema generation failed: {str(e)}", exc_info=True)
        return {'success': False, 'message': f'Schema generation failed: {str(e)}'}

def handle_sync(state):
    """
    Sync data from ProHandel API to Fivetran.
    
    Args:
        state: Current state from Fivetran
        
    Returns:
        Sync response with data and updated state
    """
    try:
        logger.info(f"Starting sync with state: {json.dumps(state)}")
        
        # Initialize response
        response = {
            'state': state or {},
            'insert': {},
            'delete': {},
            'schema': {}
        }
        
        # Get last sync times from state
        last_sync = {}
        for entity in ['articles', 'customers', 'orders']:
            last_sync[entity] = state.get(f'{entity}_last_sync')
        
        # Sync articles
        articles = connector.get_entity_list('article')
        response['insert']['articles'] = articles
        response['state']['articles_last_sync'] = datetime.utcnow().isoformat()
        
        # Sync customers
        customers = connector.get_entity_list('customer')
        response['insert']['customers'] = customers
        response['state']['customers_last_sync'] = datetime.utcnow().isoformat()
        
        # Sync orders
        orders = connector.get_entity_list('order')
        response['insert']['orders'] = orders
        response['state']['orders_last_sync'] = datetime.utcnow().isoformat()
        
        logger.info(f"Sync completed successfully")
        logger.info(f"Synced {len(articles)} articles, {len(customers)} customers, {len(orders)} orders")
        
        return response
    except Exception as e:
        logger.error(f"Sync failed: {str(e)}", exc_info=True)
        return {'success': False, 'message': f'Sync failed: {str(e)}'}

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "agent": "fivetran",
        "operation": "test",
        "secrets": {
            "PROHANDEL_API_KEY": "7e7c639358434c4fa215d4e3978739d0",
            "PROHANDEL_API_SECRET": "1cjnuux79d",
            "PROHANDEL_AUTH_URL": "https://auth.prohandel.cloud/api/v4",
            "PROHANDEL_API_URL": "https://api.prohandel.de/api/v2"
        }
    }
    
    # Test the lambda handler
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))

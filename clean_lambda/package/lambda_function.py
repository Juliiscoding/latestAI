"""
ProHandel AWS Lambda Function for Fivetran integration.

This Lambda function connects ProHandel API to Fivetran with enhanced reliability,
monitoring, and error handling. It follows a simplified approach focused on
successful data delivery with minimal processing in the Lambda layer.
"""
import json
import os
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import boto3
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
DEFAULT_PAGE_SIZE = 100
MAX_RETRIES = 3
RETRY_MULTIPLIER = 2
MAX_PAGES = 100  # Safety limit for pagination

class ProHandelAPI:
    """
    Handles authentication and data fetching from the ProHandel API.
    Simplified for reliability and focused on the core task of data extraction.
    """
    
    def __init__(self, api_key=None, api_secret=None, auth_url=None, api_url=None, tenant_id=None):
        """Initialize the ProHandel API client with credentials."""
        # Use provided credentials or get from environment
        self.api_key = api_key or os.environ.get('PROHANDEL_API_KEY')
        self.api_secret = api_secret or os.environ.get('PROHANDEL_API_SECRET')
        self.auth_url = auth_url or os.environ.get('PROHANDEL_AUTH_URL', 'https://api.prohandel.de/api/v2/auth')
        self.api_url = api_url or os.environ.get('PROHANDEL_API_URL', 'https://api.prohandel.de/api/v2')
        self.tenant_id = tenant_id or os.environ.get('TENANT_ID', 'default')
        
        # Validate required credentials
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret are required")
            
        self.token = None
        self.token_expiry = None
        
        logger.info(f"Initialized ProHandelAPI client for tenant: {self.tenant_id}")
        
        # Define API endpoints and their configurations
        self.endpoints = {
            'articles': {
                'path': '/article',
                'primary_key': ['number'],
                'timestamp_field': 'lastChangeDate'
            },
            'customers': {
                'path': '/customer',
                'primary_key': ['number'],
                'timestamp_field': 'lastChangeDate'
            },
            'orders': {
                'path': '/order',
                'primary_key': ['number'],
                'timestamp_field': 'lastChangeDate'
            },
            'sales': {
                'path': '/sale',
                'primary_key': ['number'],
                'timestamp_field': 'saleDate'
            },
            'inventory': {
                'path': '/inventory',
                'primary_key': ['articleNumber', 'warehouseCode'],
                'timestamp_field': 'lastChangeDate'
            },
            'suppliers': {
                'path': '/supplier',
                'primary_key': ['number'],
                'timestamp_field': 'lastChangeDate'
            }
        }
    
    def get_auth_token(self):
        """
        Get an authentication token from the ProHandel auth API.
        Includes retry logic for reliability.
        """
        # Check if we have a valid token
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token
            
        try:
            logger.info("Getting new auth token from ProHandel")
            
            # ProHandel uses a different authentication format
            auth_data = {
                "apiKey": self.api_key,
                "secret": self.api_secret
            }
            
            # Use the correct token endpoint
            token_url = self.auth_url if self.auth_url.endswith("/token") else f"{self.auth_url}/token"
            logger.info(f"Using token URL: {token_url}")
            
            response = requests.post(token_url, json=auth_data)
            response.raise_for_status()
            
            auth_response = response.json()
            logger.info(f"Authentication response received: {list(auth_response.keys())}")
            
            # Handle different token response formats
            if "token" in auth_response and isinstance(auth_response["token"], dict):
                if "token" in auth_response["token"] and "value" in auth_response["token"]["token"]:
                    self.token = auth_response["token"]["token"]["value"]
                    self.token_expiry = datetime.now() + timedelta(seconds=auth_response["token"]["token"]["expiresIn"])
                elif "value" in auth_response["token"]:
                    self.token = auth_response["token"]["value"]
                    self.token_expiry = datetime.now() + timedelta(seconds=auth_response["token"]["expiresIn"])
                
                # Update API URL if provided in the response
                if "serverUrl" in auth_response:
                    logger.info(f"Server URL from response: {auth_response['serverUrl']}")
                    self.api_url = auth_response['serverUrl']
                    logger.info(f"Updated API URL to: {self.api_url}")
            elif "accessToken" in auth_response:
                self.token = auth_response["accessToken"]
                self.token_expiry = datetime.now() + timedelta(minutes=60)  # Default to 1 hour
            else:
                logger.error(f"Unexpected authentication response format: {auth_response}")
                raise ValueError("Unexpected authentication response format")
                
            logger.info(f"Authentication successful. Token expires at {self.token_expiry}")
            return self.token
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                if e.response.content:
                    logger.error(f"Response content: {e.response.content.decode()}")
            raise
    
    @retry(
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=RETRY_MULTIPLIER)
    )
    def make_request(self, endpoint, params=None):
        """
        Make a request to the ProHandel API with automatic retries.
        """
        token = self.get_auth_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Ensure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = f"/{endpoint}"
            
        # Use the API URL, but check if it already includes the API path
        api_base_url = self.api_url
        
        # If we have a tenant-specific URL (like linde.prohandel.de), we need to make sure
        # we're not adding /api/v2 again if it's already in the URL
        if not api_base_url.endswith('/api/v2') and '/api/v2' not in api_base_url:
            # Add the API path if not present
            api_base_url = f"{api_base_url}/api/v2"
        
        # Construct the full URL
        url = f"{api_base_url}{endpoint}"
        
        try:
            logger.info(f"Making request to {url} with params {params}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Handle different response formats
            data = response.json()
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'items' in data:
                return data['items']
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                if e.response.content:
                    logger.error(f"Response content: {e.response.content.decode()}")
            raise
    
    def get_data(self, entity_type, updated_since=None, page=1, page_size=DEFAULT_PAGE_SIZE):
        """
        Get data for a specific entity type with pagination and incremental loading.
        """
        if entity_type not in self.endpoints:
            raise ValueError(f"Unknown entity type: {entity_type}")
            
        endpoint_config = self.endpoints[entity_type]
        endpoint_path = endpoint_config['path']
        
        # Prepare parameters for the request
        params = {
            'page': page,
            'pagesize': page_size
        }
        
        # Add timestamp filter for incremental loading if provided
        if updated_since and 'timestamp_field' in endpoint_config:
            timestamp_field = endpoint_config['timestamp_field']
            params[f"{timestamp_field}_gt"] = updated_since
            
        data = self.make_request(endpoint_path, params)
        
        # Add tenant_id to each record for multi-tenant support
        if isinstance(data, list):
            for record in data:
                if isinstance(record, dict):
                    record['tenant_id'] = self.tenant_id
        
        return data
        
    def get_all_data(self, entity_type, updated_since=None, page_size=DEFAULT_PAGE_SIZE):
        """
        Get all data for an entity type with pagination.
        """
        all_data = []
        page = 1
        
        while page <= MAX_PAGES:  # Safety limit to prevent infinite loops
            batch = self.get_data(entity_type, updated_since, page, page_size)
            
            if not batch:
                break
                
            all_data.extend(batch)
            
            # If we got fewer records than the page size, we're done
            if len(batch) < page_size:
                break
                
            page += 1
            
        return all_data


def lambda_handler(event, context):
    """
    AWS Lambda handler for Fivetran Function connector.
    
    Args:
        event: Lambda event containing Fivetran request
        context: Lambda context
        
    Returns:
        Response in Fivetran expected format
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract request details
        request_type = event.get('type')
        secrets = event.get('secrets', {})
        state = event.get('state', {})
        
        # Get tenant ID from secrets or use default
        tenant_id = secrets.get('TENANT_ID', os.environ.get('TENANT_ID', 'default'))
        logger.info(f"Using tenant ID: {tenant_id}")
        
        # Initialize API client with secrets if provided
        api = ProHandelAPI(
            api_key=secrets.get('PROHANDEL_API_KEY'),
            api_secret=secrets.get('PROHANDEL_API_SECRET'),
            auth_url=secrets.get('PROHANDEL_AUTH_URL'),
            api_url=secrets.get('PROHANDEL_API_URL'),
            tenant_id=tenant_id
        )
        
        # Handle different request types
        if request_type == 'test':
            return handle_test(api)
        elif request_type == 'schema':
            return handle_schema(api)
        elif request_type == 'sync':
            return handle_sync(api, state, event)
        else:
            raise ValueError(f"Unsupported request type: {request_type}")
            
    except Exception as e:
        # Capture full stack trace for better debugging
        stack_trace = traceback.format_exc()
        logger.error(f"Error in lambda_handler: {str(e)}\n{stack_trace}")
        
        # Send metrics to CloudWatch for monitoring
        try:
            cloudwatch = boto3.client('cloudwatch')
            cloudwatch.put_metric_data(
                Namespace='ProHandelFivetran',
                MetricData=[
                    {
                        'MetricName': 'LambdaErrors',
                        'Value': 1,
                        'Unit': 'Count'
                    }
                ]
            )
        except Exception as cw_error:
            logger.error(f"Failed to send error metric: {str(cw_error)}")
        
        return {
            'error': str(e),
            'stack_trace': stack_trace
        }
    finally:
        # Log execution time for performance monitoring
        execution_time = time.time() - start_time
        logger.info(f"Lambda execution completed in {execution_time:.2f} seconds")


def handle_test(api):
    """
    Test connection to ProHandel API.
    
    Args:
        api: ProHandel API client
        
    Returns:
        Test result response
    """
    try:
        # Try to authenticate and fetch a small amount of data
        api.get_data('articles', page=1, page_size=1)
        
        return {
            'success': True,
            'message': 'Successfully connected to ProHandel API'
        }
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def handle_schema(api):
    """
    Return schema definition for Fivetran.
    
    Args:
        api: ProHandel API client
        
    Returns:
        Schema definition response
    """
    try:
        tables = {}
        
        # Define schema for each entity type
        for entity_type, config in api.endpoints.items():
            primary_key = config.get('primary_key', [])
            
            # Get sample data to infer schema
            sample_data = api.get_data(entity_type, page=1, page_size=1)
            
            if sample_data:
                # Extract column names and types from sample data
                columns = {}
                for key, value in sample_data[0].items():
                    if isinstance(value, int):
                        columns[key] = 'integer'
                    elif isinstance(value, float):
                        columns[key] = 'number'
                    elif isinstance(value, bool):
                        columns[key] = 'boolean'
                    elif isinstance(value, (datetime, str)) and any(date_key in key.lower() for date_key in ['date', 'time', 'created', 'updated', 'change']):
                        columns[key] = 'timestamp'
                    else:
                        columns[key] = 'string'
                
                # Add tenant_id column to all tables for multi-tenant support
                columns['tenant_id'] = 'string'
                
                tables[entity_type] = {
                    'primary_key': primary_key,
                    'columns': columns
                }
        
        return {
            'tables': tables
        }
    except Exception as e:
        logger.error(f"Schema generation failed: {str(e)}")
        return {
            'error': str(e)
        }


def handle_sync(api, state, event):
    """
    Sync data from ProHandel API.
    
    Args:
        api: ProHandel API client
        state: Current state from Fivetran
        event: Original event from Fivetran
        
    Returns:
        Sync response with data and updated state
    """
    try:
        # Get last sync timestamp from state
        last_sync = state.get('last_sync')
        
        # Initialize response
        response = {
            'state': {},
            'insert': {},
            'delete': {}
        }
        
        # Current timestamp for this sync
        current_sync = datetime.now().isoformat()
        
        # Check if a specific table was requested
        requested_table = event.get('table')
        entity_types = [requested_table] if requested_table else api.endpoints.keys()
        
        # Sync each entity type
        for entity_type in entity_types:
            if entity_type not in api.endpoints:
                continue
                
            logger.info(f"Syncing entity: {entity_type}")
            
            # Get data with incremental loading
            entity_data = api.get_all_data(entity_type, updated_since=last_sync)
            
            # Add data to response
            if entity_data:
                logger.info(f"Found {len(entity_data)} records for {entity_type}")
                response['insert'][entity_type] = entity_data
            else:
                logger.info(f"No new data for {entity_type}")
        
        # Update state with current timestamp
        response['state']['last_sync'] = current_sync
        
        # Send metrics to CloudWatch for monitoring
        try:
            cloudwatch = boto3.client('cloudwatch')
            
            # Record total records synced
            total_records = sum(len(data) for data in response['insert'].values())
            
            cloudwatch.put_metric_data(
                Namespace='ProHandelFivetran',
                MetricData=[
                    {
                        'MetricName': 'RecordsSynced',
                        'Value': total_records,
                        'Unit': 'Count'
                    }
                ]
            )
        except Exception as cw_error:
            logger.error(f"Failed to send metrics: {str(cw_error)}")
        
        return response
    except Exception as e:
        logger.error(f"Sync failed: {str(e)}")
        return {
            'error': str(e)
        }


# For local testing
if __name__ == "__main__":
    # Configure logging for local testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test event
    test_event = {
        "type": "test",
        "secrets": {
            "PROHANDEL_API_KEY": os.environ.get("PROHANDEL_API_KEY"),
            "PROHANDEL_API_SECRET": os.environ.get("PROHANDEL_API_SECRET"),
            "PROHANDEL_AUTH_URL": os.environ.get("PROHANDEL_AUTH_URL"),
            "PROHANDEL_API_URL": os.environ.get("PROHANDEL_API_URL")
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))

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
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add the parent directory to sys.path to import from etl package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing connector components
from etl.connectors.prohandel_connector import ProHandelConnector
from etl.utils.logger import logger
from etl.validators.schema_validator import schema_validator

# Import data enhancement and aggregation components
from data_enhancer import data_enhancer, data_aggregator

# Initialize the connector
connector = ProHandelConnector()

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
        
        # Parse Fivetran request
        request = event.get('request', {})
        state = request.get('state', {})
        secrets = request.get('secrets', {})
        
        # Update configuration from secrets if provided
        if secrets:
            update_configuration_from_secrets(secrets)
        
        # Get the operation type
        operation = request.get('operation')
        
        if operation == 'test':
            # Test connection
            return handle_test()
        elif operation == 'schema':
            # Return schema
            return handle_schema()
        elif operation == 'sync':
            # Sync data
            return handle_sync(state)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
            
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}", exc_info=True)
        return {
            'error': str(e)
        }

def update_configuration_from_secrets(secrets):
    """
    Update connector configuration from Fivetran secrets.
    
    Args:
        secrets: Secret configuration values from Fivetran
    """
    if 'api_key' in secrets:
        os.environ['PROHANDEL_API_KEY'] = secrets['api_key']
    
    if 'api_secret' in secrets:
        os.environ['PROHANDEL_API_SECRET'] = secrets['api_secret']
    
    if 'api_url' in secrets:
        os.environ['PROHANDEL_API_URL'] = secrets['api_url']

def handle_test():
    """
    Test connection to ProHandel API.
    
    Returns:
        Test result response
    """
    try:
        # Try to authenticate and fetch a small amount of data
        connector.get_entity_list('article', page=1, pagesize=1)
        return {'success': True}
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}", exc_info=True)
        return {'success': False, 'error': str(e)}

def handle_schema():
    """
    Return schema definition for Fivetran.
    
    Returns:
        Schema definition response
    """
    try:
        # Define schema based on existing entities
        tables = {}
        
        # Core entity tables
        for entity_name in connector.API_ENDPOINTS:
            # Skip entities we don't want to include
            if entity_name in ['customercard', 'branch', 'voucher']:
                continue
                
            endpoint_config = connector.API_ENDPOINTS[entity_name]
            
            # Get sample data to infer schema
            sample_data = connector.get_entity_list(entity_name, page=1, pagesize=1)
            
            if sample_data:
                # Extract column names and types from sample data
                columns = {}
                for key, value in sample_data[0].items():
                    if isinstance(value, int):
                        columns[key] = {'type': 'integer'}
                    elif isinstance(value, float):
                        columns[key] = {'type': 'number'}
                    elif isinstance(value, bool):
                        columns[key] = {'type': 'boolean'}
                    elif isinstance(value, (datetime, str)) and any(date_key in key.lower() for date_key in ['date', 'time', 'created', 'updated', 'change']):
                        columns[key] = {'type': 'timestamp'}
                    else:
                        columns[key] = {'type': 'string'}
                
                # Set primary key if available
                primary_key = []
                if 'number' in columns:
                    primary_key.append('number')
                elif 'id' in columns:
                    primary_key.append('id')
                
                # For composite keys
                if entity_name == 'orderposition':
                    if 'orderNumber' in columns and 'position' in columns:
                        primary_key = ['orderNumber', 'position']
                elif entity_name == 'inventory':
                    if 'articleNumber' in columns and 'warehouseCode' in columns:
                        primary_key = ['articleNumber', 'warehouseCode']
                
                tables[entity_name] = {
                    'primary_key': primary_key,
                    'columns': columns
                }
                
                # Add enhanced fields based on entity type
                if entity_name == 'article':
                    # Add profit margin and price tier
                    tables[entity_name]['columns']['profit_margin'] = {'type': 'number'}
                    tables[entity_name]['columns']['price_tier'] = {'type': 'string'}
                elif entity_name == 'customer':
                    # Add full address
                    tables[entity_name]['columns']['full_address'] = {'type': 'string'}
                elif entity_name == 'order':
                    # Add delivery time and order age
                    tables[entity_name]['columns']['delivery_time_days'] = {'type': 'integer'}
                    tables[entity_name]['columns']['order_age_days'] = {'type': 'integer'}
                elif entity_name == 'sale':
                    # Add sale age
                    tables[entity_name]['columns']['sale_age_days'] = {'type': 'integer'}
                elif entity_name == 'inventory':
                    # Add stock status
                    tables[entity_name]['columns']['stock_status'] = {'type': 'string'}
        
        # Add aggregation tables
        tables['daily_sales_agg'] = {
            'primary_key': ['sale_date'],
            'columns': {
                'sale_date': {'type': 'string'},
                'sale_count': {'type': 'integer'},
                'total_quantity': {'type': 'number'},
                'total_amount': {'type': 'number'},
                'aggregation_type': {'type': 'string'}
            }
        }
        
        tables['article_sales_agg'] = {
            'primary_key': ['articleNumber'],
            'columns': {
                'articleNumber': {'type': 'string'},
                'sale_count': {'type': 'integer'},
                'total_quantity': {'type': 'number'},
                'total_amount': {'type': 'number'},
                'aggregation_type': {'type': 'string'}
            }
        }
        
        tables['warehouse_inventory_agg'] = {
            'primary_key': ['warehouseCode'],
            'columns': {
                'warehouseCode': {'type': 'string'},
                'article_count': {'type': 'integer'},
                'total_quantity': {'type': 'number'},
                'aggregation_type': {'type': 'string'}
            }
        }
        
        return {'schema': {'tables': tables}}
    except Exception as e:
        logger.error(f"Schema generation failed: {str(e)}", exc_info=True)
        return {'error': str(e)}

def handle_sync(state):
    """
    Sync data from ProHandel API.
    
    Args:
        state: Current state from Fivetran
        
    Returns:
        Sync response with data and updated state
    """
    try:
        # Get last sync timestamp from state
        last_sync = state.get('last_sync')
        last_sync_datetime = None
        
        if last_sync:
            try:
                last_sync_datetime = datetime.fromisoformat(last_sync)
            except ValueError:
                logger.warning(f"Could not parse last_sync timestamp: {last_sync}")
        
        # Initialize response
        response = {
            'state': {},
            'insert': {},
            'delete': {},
            'schema': {'tables': {}}
        }
        
        # Current timestamp for this sync
        current_sync = datetime.now().isoformat()
        
        # Track extracted data for aggregations
        extracted_data = {}
        
        # Sync each entity
        for entity_name in connector.API_ENDPOINTS:
            # Skip entities we don't want to include
            if entity_name in ['customercard', 'branch', 'voucher']:
                continue
                
            # Skip entities not in schema (if any)
            if 'schema' in state and 'tables' in state['schema'] and entity_name not in state['schema']['tables']:
                continue
                
            logger.info(f"Syncing entity: {entity_name}")
            
            # Prepare parameters for incremental loading
            params = {}
            if last_sync_datetime:
                timestamp_field = connector.API_ENDPOINTS[entity_name].get('timestamp_field')
                if timestamp_field:
                    # Format may need to be adjusted based on API requirements
                    params[f"{timestamp_field}_gt"] = last_sync_datetime.isoformat()
            
            # Get entity data with pagination
            entity_data = []
            page = 1
            while True:
                batch = connector.get_entity_list(entity_name, page=page, pagesize=100, params=params)
                if not batch:
                    break
                    
                # Validate data if needed
                validated_batch = schema_validator.validate_batch(entity_name, batch)
                entity_data.extend(validated_batch)
                
                page += 1
                
                # Limit the number of pages for testing
                if page > 10:
                    logger.warning(f"Reached maximum page limit for {entity_name}")
                    break
            
            # Store extracted data for aggregations
            extracted_data[entity_name] = entity_data
            
            # Enhance data based on entity type
            if entity_data:
                logger.info(f"Enhancing {len(entity_data)} records for {entity_name}")
                
                if entity_name == 'article':
                    entity_data = data_enhancer.enhance_article_data(entity_data)
                elif entity_name == 'customer':
                    entity_data = data_enhancer.enhance_customer_data(entity_data)
                elif entity_name == 'order':
                    entity_data = data_enhancer.enhance_order_data(entity_data)
                elif entity_name == 'sale':
                    entity_data = data_enhancer.enhance_sale_data(entity_data)
                elif entity_name == 'inventory':
                    entity_data = data_enhancer.enhance_inventory_data(entity_data)
            
            # Add data to response
            if entity_data:
                logger.info(f"Found {len(entity_data)} records for {entity_name}")
                response['insert'][entity_name] = entity_data
            else:
                logger.info(f"No new data for {entity_name}")
        
        # Create aggregations
        if 'sale' in extracted_data and extracted_data['sale']:
            # Daily sales aggregation
            daily_sales_agg = data_aggregator.aggregate_sales_by_date(extracted_data['sale'])
            if daily_sales_agg:
                response['insert']['daily_sales_agg'] = daily_sales_agg
                
            # Article sales aggregation
            article_sales_agg = data_aggregator.aggregate_sales_by_article(extracted_data['sale'])
            if article_sales_agg:
                response['insert']['article_sales_agg'] = article_sales_agg
        
        if 'inventory' in extracted_data and extracted_data['inventory']:
            # Warehouse inventory aggregation
            warehouse_inventory_agg = data_aggregator.aggregate_inventory_by_warehouse(extracted_data['inventory'])
            if warehouse_inventory_agg:
                response['insert']['warehouse_inventory_agg'] = warehouse_inventory_agg
        
        # Update state with current timestamp
        response['state']['last_sync'] = current_sync
        
        return response
    except Exception as e:
        logger.error(f"Sync failed: {str(e)}", exc_info=True)
        return {'error': str(e)}

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "request": {
            "operation": "test"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))

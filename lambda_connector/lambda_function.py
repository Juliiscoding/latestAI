"""
ProHandel AWS Lambda Function for Fivetran integration - Simplified Version.

This Lambda function provides a lightweight implementation for the Fivetran AWS Lambda connector.
It handles data extraction from the ProHandel API with minimal dependencies to ensure
compatibility with AWS Lambda environment.
"""
import json
import os
import sys
import time
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional

# Configure logging to use /tmp directory in Lambda
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/lambda_function.log', mode='a')
    ]
)
logger = logging.getLogger('prohandel_lambda')

# ProHandel API client
class ProHandelClient:
    def __init__(self):
        self.api_key = os.environ.get('PROHANDEL_API_KEY')
        self.api_secret = os.environ.get('PROHANDEL_API_SECRET')
        self.auth_url = os.environ.get('PROHANDEL_AUTH_URL', 'https://auth.prohandel.cloud/api/v4')
        self.api_url = os.environ.get('PROHANDEL_API_URL', 'https://api.prohandel.de/api/v2')
        self.token = None
        self.token_expiry = None
    
    def authenticate(self):
        """Authenticate with the ProHandel API and get an access token"""
        logger.info(f"Authenticating with {self.auth_url}...")
        
        try:
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.api_key,
                'client_secret': self.api_secret
            }
            
            response = requests.post(f"{self.auth_url}/token", data=auth_data)
            response.raise_for_status()
            
            auth_response = response.json()
            self.token = auth_response.get('access_token')
            expires_in = auth_response.get('expires_in', 3600)
            self.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)
            
            logger.info("Authentication successful")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise
    
    def get_headers(self):
        """Get headers for API requests with authentication token"""
        if not self.token or datetime.now(timezone.utc) >= self.token_expiry:
            self.authenticate()
        
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get_entity_list(self, entity_type, page=1, pagesize=100, modified_since=None):
        """Get a list of entities from the ProHandel API"""
        try:
            url = f"{self.api_url}/{entity_type}"
            params = {'page': page, 'pagesize': pagesize}
            
            if modified_since:
                # Format as ISO 8601 string
                if isinstance(modified_since, datetime):
                    modified_since = modified_since.isoformat()
                params['modified_since'] = modified_since
            
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting {entity_type} list: {str(e)}")
            raise

# Initialize the client
client = ProHandelClient()

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
        # Log the received event for debugging
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Check if this is a Fivetran direct format or our internal format
        if 'request' in event:
            # Internal format - used for local testing
            request = event.get('request', {})
            operation = request.get('operation')
            secrets = request.get('secrets', {})
            state = request.get('state', {})
        else:
            # Fivetran format - used when called from Fivetran
            secrets = event.get('secrets', {})
            state = event.get('state', {})
            
            # Determine operation type from Fivetran's request structure
            if 'setup_test' in event and event['setup_test'] == True:
                operation = 'test'
                logger.info("Request type: test (setup_test)")
            elif 'type' in event:
                operation = event['type']  # 'test', 'schema', or 'sync'
                logger.info(f"Request type: {operation}")
            elif 'schema' in event:
                operation = 'schema'
                logger.info("Request type: schema")
            elif 'sync_id' in event and not event.get('setup_test'):
                operation = 'sync'
                logger.info("Request type: sync")
            else:
                operation = None
                logger.info(f"Unknown request type: {list(event.keys())}")
        
        # Update configuration from secrets
        if secrets:
            update_configuration_from_secrets(secrets)
        
        # Handle different operations
        if operation == 'test':
            return handle_test()
        elif operation == 'schema':
            return handle_schema()
        elif operation == 'sync':
            return handle_sync(state)
        else:
            return {'error': f'Unsupported operation: {operation}'}
    
    except Exception as e:
        logger.error(f"Lambda function error: {str(e)}", exc_info=True)
        return {'error': str(e)}

def update_configuration_from_secrets(secrets):
    """
    Update client configuration from Fivetran secrets.
    
    Args:
        secrets: Secret configuration values from Fivetran
    """
    logger.info("Updating configuration from secrets...")
    
    # Handle both formats: our internal format and Fivetran's format
    # Internal format uses lowercase keys (api_key, api_secret)
    # Fivetran format uses uppercase keys (PROHANDEL_API_KEY, PROHANDEL_API_SECRET)
    
    # Check for API key
    if 'PROHANDEL_API_KEY' in secrets:
        os.environ['PROHANDEL_API_KEY'] = secrets['PROHANDEL_API_KEY']
    elif 'api_key' in secrets:
        os.environ['PROHANDEL_API_KEY'] = secrets['api_key']
    
    # Check for API secret
    if 'PROHANDEL_API_SECRET' in secrets:
        os.environ['PROHANDEL_API_SECRET'] = secrets['PROHANDEL_API_SECRET']
    elif 'api_secret' in secrets:
        os.environ['PROHANDEL_API_SECRET'] = secrets['api_secret']
    
    # Check for auth URL
    if 'PROHANDEL_AUTH_URL' in secrets:
        os.environ['PROHANDEL_AUTH_URL'] = secrets['PROHANDEL_AUTH_URL']
    elif 'auth_url' in secrets:
        os.environ['PROHANDEL_AUTH_URL'] = secrets['auth_url']
    
    # Check for API URL
    if 'PROHANDEL_API_URL' in secrets:
        os.environ['PROHANDEL_API_URL'] = secrets['PROHANDEL_API_URL']
    elif 'api_url' in secrets:
        os.environ['PROHANDEL_API_URL'] = secrets['api_url']
    
    # Log the configuration for debugging
    logger.info(f"API Key: {os.environ.get('PROHANDEL_API_KEY', 'Not set')[:5]}...")
    logger.info(f"Auth URL: {os.environ.get('PROHANDEL_AUTH_URL', 'Not set')}")
    logger.info(f"API URL: {os.environ.get('PROHANDEL_API_URL', 'Not set')}")
    
    # Reinitialize client with new configuration
    global client
    client = ProHandelClient()

def handle_test():
    """
    Test connection to ProHandel API.
    
    Returns:
        Test result response
    """
    try:
        # Test API access by fetching a small amount of data
        articles = client.get_entity_list('article', page=1, pagesize=1)
        
        return {'status': 'ok', 'message': 'Successfully connected to ProHandel API'}
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}", exc_info=True)
        return {'status': 'error', 'message': str(e)}

def handle_schema():
    """
    Return schema definition for Fivetran.
    
    Returns:
        Schema definition response
    """
    try:
        # Define schema based on hardcoded definitions for main entities
        tables = {}
        
        # Map of entity names to table names (for any renames)
        table_name_map = {
            'branch': 'shop'  # Map branch to shop for better semantic understanding
        }
        
        # Define hardcoded schemas for each entity type
        
        # Article schema
        article_columns = {
            'id': {'type': 'string'},
            'articleNumber': {'type': 'string'},
            'name': {'type': 'string'},
            'description': {'type': 'string'},
            'price': {'type': 'number'},
            'cost': {'type': 'number'},
            'categoryId': {'type': 'string'},
            'supplierId': {'type': 'string'},
            'ean': {'type': 'string'},
            'stockQuantity': {'type': 'number'},
            'isActive': {'type': 'boolean'},
            'createdAt': {'type': 'timestamp'},
            'updatedAt': {'type': 'timestamp'},
            'profit_margin': {'type': 'number'},  # Enhanced field
            'price_tier': {'type': 'string'}      # Enhanced field
        }
        tables['article'] = {
            'primary_key': ['id'],
            'columns': article_columns
        }
        
        # Customer schema
        customer_columns = {
            'id': {'type': 'string'},
            'customerNumber': {'type': 'string'},
            'name': {'type': 'string'},
            'email': {'type': 'string'},
            'phone': {'type': 'string'},
            'address': {'type': 'string'},
            'city': {'type': 'string'},
            'postalCode': {'type': 'string'},
            'country': {'type': 'string'},
            'isActive': {'type': 'boolean'},
            'createdAt': {'type': 'timestamp'},
            'updatedAt': {'type': 'timestamp'},
            'full_address': {'type': 'string'}    # Enhanced field
        }
        tables['customer'] = {
            'primary_key': ['id'],
            'columns': customer_columns
        }
        
        # Order schema
        order_columns = {
            'id': {'type': 'string'},
            'orderNumber': {'type': 'string'},
            'customerId': {'type': 'string'},
            'orderDate': {'type': 'timestamp'},
            'totalAmount': {'type': 'number'},
            'status': {'type': 'string'},
            'paymentMethod': {'type': 'string'},
            'shippingMethod': {'type': 'string'},
            'createdAt': {'type': 'timestamp'},
            'updatedAt': {'type': 'timestamp'},
            'delivery_time_days': {'type': 'integer'},  # Enhanced field
            'order_age_days': {'type': 'integer'}      # Enhanced field
        }
        tables['order'] = {
            'primary_key': ['id'],
            'columns': order_columns
        }
        
        # Sale schema
        sale_columns = {
            'id': {'type': 'string'},
            'saleNumber': {'type': 'string'},
            'customerId': {'type': 'string'},
            'saleDate': {'type': 'timestamp'},
            'totalAmount': {'type': 'number'},
            'paymentMethod': {'type': 'string'},
            'branchId': {'type': 'string'},
            'createdAt': {'type': 'timestamp'},
            'updatedAt': {'type': 'timestamp'},
            'sale_age_days': {'type': 'integer'}  # Enhanced field
        }
        tables['sale'] = {
            'primary_key': ['id'],
            'columns': sale_columns
        }
        
        # Inventory schema
        inventory_columns = {
            'id': {'type': 'string'},
            'articleId': {'type': 'string'},
            'branchNumber': {'type': 'string'},
            'articleNumber': {'type': 'string'},
            'quantity': {'type': 'number'},
            'updatedAt': {'type': 'timestamp'},
            'stock_status': {'type': 'string'}    # Enhanced field
        }
        tables['inventory'] = {
            'primary_key': ['id', 'branchNumber', 'articleNumber'],
            'columns': inventory_columns
        }
        
        # Branch/Shop schema
        branch_columns = {
            'id': {'type': 'string'},
            'branchNumber': {'type': 'string'},
            'name': {'type': 'string'},
            'address': {'type': 'string'},
            'city': {'type': 'string'},
            'postalCode': {'type': 'string'},
            'country': {'type': 'string'},
            'phone': {'type': 'string'},
            'email': {'type': 'string'},
            'createdAt': {'type': 'timestamp'},
            'updatedAt': {'type': 'timestamp'},
            'shop_type': {'type': 'string'},      # Enhanced field
            'is_online': {'type': 'boolean'}      # Enhanced field
        }
        tables['shop'] = {
            'primary_key': ['id'],
            'columns': branch_columns
        }
        
        # Category schema
        category_columns = {
            'id': {'type': 'string'},
            'name': {'type': 'string'},
            'parentId': {'type': 'string'},
            'description': {'type': 'string'},
            'createdAt': {'type': 'timestamp'},
            'updatedAt': {'type': 'timestamp'}
        }
        tables['category'] = {
            'primary_key': ['id'],
            'columns': category_columns
        }
        
        # Supplier schema
        supplier_columns = {
            'id': {'type': 'string'},
            'supplierNumber': {'type': 'string'},
            'name': {'type': 'string'},
            'contactPerson': {'type': 'string'},
            'email': {'type': 'string'},
            'phone': {'type': 'string'},
            'address': {'type': 'string'},
            'city': {'type': 'string'},
            'postalCode': {'type': 'string'},
            'country': {'type': 'string'},
            'createdAt': {'type': 'timestamp'},
            'updatedAt': {'type': 'timestamp'}
        }
        tables['supplier'] = {
            'primary_key': ['id'],
            'columns': supplier_columns
        }
        
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
            'primary_key': ['agg_id'],
            'columns': {
                'agg_id': {'type': 'string'},
                'articleNumber': {'type': 'string'},
                'total_quantity': {'type': 'number'},
                'total_amount': {'type': 'number'},
                'sale_count': {'type': 'integer'},
                'aggregation_type': {'type': 'string'},
                'description': {'type': 'string'},
                'name': {'type': 'string'},
                'category': {'type': 'string'},
                'supplier': {'type': 'string'}
            }
        }
        
        # Log the schema for debugging
        logger.info(f"Generated schema with {len(tables)} tables")
        for table_name, table_def in tables.items():
            logger.info(f"Table {table_name}: {len(table_def['columns'])} columns, primary key: {table_def['primary_key']}")
        
        return {'schema': {'tables': tables}}
    except Exception as e:
        logger.error(f"Schema generation failed: {str(e)}", exc_info=True)
        return {'error': str(e)}

def handle_sync(state=None):
    """
    Sync data from ProHandel API to Fivetran.
    
    Args:
        state: Current state from Fivetran
        
    Returns:
        Sync response with data and updated state
    """
    try:
        if state is None:
            state = {}
        
        # Get last sync timestamps for each entity
        last_sync_timestamps = state.get('bookmarks', {})
        
        # Initialize response
        response = {
            'state': {
                'bookmarks': {}
            },
            'insert': {},
            'delete': {},
            'schema': {'tables': {}}
        }
        
        # Define entities to sync
        entities_to_sync = [
            'article', 'customer', 'order', 
            'sale', 'inventory', 'branch'  # Use branch instead of shop
        ]
        
        # Process each entity
        for entity_name in entities_to_sync:
            try:
                # Get last sync timestamp for this entity
                last_sync = last_sync_timestamps.get(entity_name)
                
                # Map entity name to table name
                table_name = 'shop' if entity_name == 'branch' else entity_name
                
                # Fetch data with incremental loading if timestamp exists
                if last_sync:
                    # Convert string timestamp to datetime
                    last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                    
                    # Add a small buffer to avoid missing records
                    buffer_time = timedelta(minutes=5)
                    last_sync_dt -= buffer_time
                    
                    # Format for API query
                    last_sync_formatted = last_sync_dt.isoformat()
                    
                    logger.info(f"Fetching {entity_name} data modified since {last_sync_formatted}")
                    # Fetch data modified since last sync
                    data = client.get_entity_list(entity_name, modified_since=last_sync_formatted)
                else:
                    # First sync, get all data
                    logger.info(f"Fetching all {entity_name} data (first sync)")
                    data = client.get_entity_list(entity_name)
                
                # Skip if no data
                if not data:
                    logger.info(f"No data returned for entity: {entity_name}")
                    continue
                
                logger.info(f"Retrieved {len(data)} {entity_name} records")
                
                # Simple data enhancement without external dependencies
                enhanced_data = []
                for item in data:
                    try:
                        # Add basic calculated fields based on entity type
                        if entity_name == 'article' and 'price' in item and 'cost' in item:
                            # Calculate profit margin
                            price = float(item.get('price', 0))
                            cost = float(item.get('cost', 0))
                            if cost > 0:
                                item['profit_margin'] = round((price - cost) / cost * 100, 2)
                            else:
                                item['profit_margin'] = 0
                                
                            # Determine price tier
                            if price < 10:
                                item['price_tier'] = 'budget'
                            elif price < 50:
                                item['price_tier'] = 'standard'
                            else:
                                item['price_tier'] = 'premium'
                                
                        elif entity_name == 'customer':
                            # Create full address
                            address_parts = []
                            if item.get('address'):
                                address_parts.append(item['address'])
                            if item.get('city'):
                                address_parts.append(item['city'])
                            if item.get('postalCode'):
                                address_parts.append(item['postalCode'])
                            if item.get('country'):
                                address_parts.append(item['country'])
                            
                            item['full_address'] = ', '.join([p for p in address_parts if p])
                            
                        elif entity_name == 'order' and 'orderDate' in item:
                            # Calculate order age in days
                            try:
                                order_date = datetime.fromisoformat(item['orderDate'].replace('Z', '+00:00'))
                                current_date = datetime.now(timezone.utc)
                                item['order_age_days'] = (current_date - order_date).days
                                
                                # Estimate delivery time (simplified)
                                item['delivery_time_days'] = min(item['order_age_days'], 7)  # Cap at 7 days
                            except (ValueError, TypeError):
                                item['order_age_days'] = 0
                                item['delivery_time_days'] = 0
                                
                        elif entity_name == 'sale' and 'saleDate' in item:
                            # Calculate sale age in days
                            try:
                                sale_date = datetime.fromisoformat(item['saleDate'].replace('Z', '+00:00'))
                                current_date = datetime.now(timezone.utc)
                                item['sale_age_days'] = (current_date - sale_date).days
                            except (ValueError, TypeError):
                                item['sale_age_days'] = 0
                                
                        elif entity_name == 'inventory' and 'quantity' in item:
                            # Determine stock status
                            quantity = float(item.get('quantity', 0))
                            if quantity <= 0:
                                item['stock_status'] = 'out_of_stock'
                            elif quantity < 5:
                                item['stock_status'] = 'low_stock'
                            elif quantity < 20:
                                item['stock_status'] = 'medium_stock'
                            else:
                                item['stock_status'] = 'high_stock'
                                
                        elif entity_name == 'branch':
                            # Determine shop type and online status
                            name = item.get('name', '').lower()
                            if 'online' in name or 'web' in name:
                                item['is_online'] = True
                                item['shop_type'] = 'online'
                            else:
                                item['is_online'] = False
                                if 'warehouse' in name:
                                    item['shop_type'] = 'warehouse'
                                elif 'outlet' in name:
                                    item['shop_type'] = 'outlet'
                                else:
                                    item['shop_type'] = 'retail'
                        
                        # Ensure all values are of supported types for Fivetran
                        for key, value in list(item.items()):
                            if not isinstance(value, (str, int, float, bool, type(None))):
                                # Convert datetime objects to ISO format strings
                                if isinstance(value, datetime):
                                    item[key] = value.isoformat()
                                # Convert other objects to strings
                                else:
                                    item[key] = str(value)
                        
                        enhanced_data.append(item)
                    except Exception as item_error:
                        logger.warning(f"Error enhancing {entity_name} item: {str(item_error)}")
                        # Add the original item without enhancement
                        enhanced_data.append(item)
                
                logger.info(f"Enhanced {len(enhanced_data)} {entity_name} records")
                
                # Add data to response
                response['insert'][table_name] = enhanced_data
                logger.info(f"Added {len(enhanced_data)} {table_name} records to insert response")
                
                # Update bookmark with current timestamp
                current_time = datetime.now(timezone.utc).isoformat()
                response['state']['bookmarks'][entity_name] = current_time
                logger.info(f"Updated bookmark for {entity_name} to {current_time}")
                    
            except Exception as entity_error:
                logger.error(f"Error processing entity {entity_name}: {str(entity_error)}")
                # Continue with other entities instead of failing the entire sync
                continue
        
        # Add simple daily sales aggregation if we have sales data
        if 'sale' in response['insert'] and response['insert']['sale']:
            try:
                # Group sales by date
                sales_by_date = {}
                for sale in response['insert']['sale']:
                    sale_date = sale.get('saleDate', '').split('T')[0]  # Extract date part only
                    if not sale_date:
                        continue
                        
                    if sale_date not in sales_by_date:
                        sales_by_date[sale_date] = {
                            'sale_date': sale_date,
                            'sale_count': 0,
                            'total_quantity': 0,
                            'total_amount': 0,
                            'aggregation_type': 'daily'
                        }
                    
                    sales_by_date[sale_date]['sale_count'] += 1
                    sales_by_date[sale_date]['total_amount'] += float(sale.get('totalAmount', 0))
                    # Assuming each sale represents one item for simplicity
                    sales_by_date[sale_date]['total_quantity'] += 1
                
                # Convert to list for response
                daily_sales = list(sales_by_date.values())
                if daily_sales:
                    response['insert']['daily_sales_agg'] = daily_sales
                    logger.info(f"Added {len(daily_sales)} daily sales aggregation records")
            except Exception as agg_error:
                logger.error(f"Error during sales aggregation: {str(agg_error)}", exc_info=True)
                        logger.info(f"Added {len(article_sales)} article sales aggregation records")
                except Exception as article_agg_error:
                    logger.error(f"Error during article sales aggregation: {str(article_agg_error)}", exc_info=True)
            
            # Warehouse inventory aggregation
            if 'inventory' in response['insert'] and response['insert']['inventory']:
                try:
                    # Create a deep copy of the inventory data to avoid modifying the original
                    inventory_copy = copy.deepcopy(response['insert']['inventory'])
                    
                    logger.info(f"Generating warehouse inventory aggregations from {len(inventory_copy)} inventory records")
                    warehouse_inventory = enhancer.aggregate_warehouse_inventory(inventory_copy)
                    
                    if warehouse_inventory:
                        # Create a unique ID for each aggregation record
                        for i, record in enumerate(warehouse_inventory):
                            if 'agg_id' not in record:
                                record['agg_id'] = f"wh_agg_{record.get('warehouse', i)}"
                        
                        response['insert']['warehouse_inventory_agg'] = warehouse_inventory
                        logger.info(f"Added {len(warehouse_inventory)} warehouse inventory aggregation records")
                except Exception as warehouse_agg_error:
                    logger.error(f"Error during warehouse inventory aggregation: {str(warehouse_agg_error)}", exc_info=True)
            
            # Log summary of all data to be inserted
            logger.info("Sync summary:")
            for table, data in response['insert'].items():
                logger.info(f"  {table}: {len(data)} records")
                    
        except Exception as agg_error:
            logger.error(f"Error during data aggregation: {str(agg_error)}", exc_info=True)
            # Continue without aggregation if it fails
        
        return response
    
    except Exception as e:
        logger.error(f"Sync operation failed: {str(e)}", exc_info=True)
        return {'error': str(e)}

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "request": {
            "operation": "test",
            "secrets": {
                "api_key": os.environ.get("PROHANDEL_API_KEY"),
                "api_secret": os.environ.get("PROHANDEL_API_SECRET")
            }
        }
    }
    
    # Run test
    print(json.dumps(lambda_handler(test_event, None), indent=2))

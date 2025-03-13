"""
Fivetran connector Lambda function for ProHandel API
Tenant-specific implementation for {{TENANT_NAME}} (ID: {{TENANT_ID}})
"""

import json
import os
import logging
import requests
import time
from datetime import datetime, timedelta
import dateutil.parser

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Tenant-specific configuration
TENANT_ID = os.environ.get('TENANT_ID', '{{TENANT_ID}}')
API_BASE_URL = os.environ.get('API_BASE_URL', '')
API_KEY = os.environ.get('API_KEY', '')

# Constants
DEFAULT_PAGE_SIZE = 100
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Schema definition
SCHEMA = {
    'products': {
        'primary_key': ['product_id'],
        'columns': {
            'tenant_id': 'string',
            'product_id': 'string',
            'product_name': 'string',
            'product_sku': 'string',
            'product_description': 'string',
            'product_category': 'string',
            'product_price': 'number',
            'product_cost': 'number',
            'product_margin': 'number',  # Calculated field
            'stock_status': 'string',    # Calculated field
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    },
    'inventory': {
        'primary_key': ['inventory_id'],
        'columns': {
            'tenant_id': 'string',
            'inventory_id': 'string',
            'product_id': 'string',
            'warehouse_id': 'string',
            'warehouse_name': 'string',
            'quantity': 'number',
            'reorder_level': 'number',
            'days_of_supply': 'number',  # Calculated field
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    },
    'customers': {
        'primary_key': ['customer_id'],
        'columns': {
            'tenant_id': 'string',
            'customer_id': 'string',
            'customer_name': 'string',
            'customer_email': 'string',
            'customer_phone': 'string',
            'address_street': 'string',
            'address_city': 'string',
            'address_state': 'string',
            'address_zip': 'string',
            'address_country': 'string',
            'full_address': 'string',    # Calculated field
            'customer_since': 'timestamp',
            'customer_type': 'string',
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    },
    'orders': {
        'primary_key': ['order_id'],
        'columns': {
            'tenant_id': 'string',
            'order_id': 'string',
            'customer_id': 'string',
            'order_date': 'timestamp',
            'order_status': 'string',
            'order_total': 'number',
            'order_tax': 'number',
            'order_shipping': 'number',
            'order_discount': 'number',
            'order_age_days': 'number',  # Calculated field
            'payment_method': 'string',
            'shipping_method': 'string',
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    },
    'order_items': {
        'primary_key': ['order_item_id'],
        'columns': {
            'tenant_id': 'string',
            'order_item_id': 'string',
            'order_id': 'string',
            'product_id': 'string',
            'quantity': 'number',
            'price': 'number',
            'cost': 'number',
            'discount': 'number',
            'item_total': 'number',
            'item_profit': 'number',     # Calculated field
            'item_margin': 'number',     # Calculated field
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    }
}

def lambda_handler(event, context):
    """
    Main handler for Fivetran connector requests
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract request type from the event
    request_type = event.get('type', '')
    
    if request_type == 'test':
        # Handle test request
        return handle_test()
    elif request_type == 'schema':
        # Handle schema request
        return handle_schema()
    elif request_type == 'sync':
        # Handle sync request
        state = event.get('state', {})
        limit = event.get('limit', {})
        return handle_sync(state, limit)
    else:
        # Handle unknown request type
        logger.error(f"Unknown request type: {request_type}")
        return {
            'error': f"Unknown request type: {request_type}"
        }

def handle_test():
    """
    Handle test request by checking connection to the ProHandel API
    """
    try:
        # Test connection to the API
        response = make_api_request('/test-connection')
        
        if response.status_code == 200:
            logger.info("Connection test successful")
            return {
                'success': True,
                'message': 'Connection to ProHandel API successful'
            }
        else:
            logger.error(f"Connection test failed: {response.status_code} - {response.text}")
            return {
                'success': False,
                'message': f"Connection to ProHandel API failed: {response.status_code} - {response.text}"
            }
    except Exception as e:
        logger.error(f"Connection test failed with exception: {str(e)}")
        return {
            'success': False,
            'message': f"Connection to ProHandel API failed: {str(e)}"
        }

def handle_schema():
    """
    Handle schema request by returning the predefined schema
    """
    logger.info("Handling schema request")
    return {
        'schema': SCHEMA
    }

def handle_sync(state, limit):
    """
    Handle sync request by fetching data from the ProHandel API
    """
    logger.info(f"Handling sync request with state: {state}")
    
    # Initialize result
    result = {
        'state': state.copy(),
        'insert': {},
        'delete': {}
    }
    
    # Get the last sync timestamps for each entity
    last_sync = {
        'products': state.get('last_products_sync', '2000-01-01T00:00:00Z'),
        'inventory': state.get('last_inventory_sync', '2000-01-01T00:00:00Z'),
        'customers': state.get('last_customers_sync', '2000-01-01T00:00:00Z'),
        'orders': state.get('last_orders_sync', '2000-01-01T00:00:00Z'),
        'order_items': state.get('last_order_items_sync', '2000-01-01T00:00:00Z')
    }
    
    # Current timestamp for this sync
    current_timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Sync each entity
    try:
        # Sync products
        products = sync_products(last_sync['products'])
        if products:
            result['insert']['products'] = products
            result['state']['last_products_sync'] = current_timestamp
        
        # Sync inventory
        inventory = sync_inventory(last_sync['inventory'])
        if inventory:
            result['insert']['inventory'] = inventory
            result['state']['last_inventory_sync'] = current_timestamp
        
        # Sync customers
        customers = sync_customers(last_sync['customers'])
        if customers:
            result['insert']['customers'] = customers
            result['state']['last_customers_sync'] = current_timestamp
        
        # Sync orders
        orders = sync_orders(last_sync['orders'])
        if orders:
            result['insert']['orders'] = orders
            result['state']['last_orders_sync'] = current_timestamp
        
        # Sync order items
        order_items = sync_order_items(last_sync['order_items'])
        if order_items:
            result['insert']['order_items'] = order_items
            result['state']['last_order_items_sync'] = current_timestamp
        
    except Exception as e:
        logger.error(f"Sync failed with exception: {str(e)}")
        return {
            'error': f"Sync failed: {str(e)}"
        }
    
    logger.info(f"Sync completed successfully")
    return result

def sync_products(last_sync):
    """
    Sync products from the ProHandel API
    """
    logger.info(f"Syncing products updated since {last_sync}")
    
    products = []
    page = 1
    has_more = True
    
    while has_more:
        try:
            # Make API request to get products
            response = make_api_request(
                '/products',
                params={
                    'updated_since': last_sync,
                    'page': page,
                    'page_size': DEFAULT_PAGE_SIZE
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch products: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                has_more = False
                break
            
            # Process products
            for item in items:
                # Add tenant ID
                item['tenant_id'] = TENANT_ID
                
                # Calculate margin
                if 'product_price' in item and 'product_cost' in item and item['product_cost'] > 0:
                    item['product_margin'] = (item['product_price'] - item['product_cost']) / item['product_price']
                else:
                    item['product_margin'] = None
                
                # Determine stock status (this would normally be based on inventory data)
                item['stock_status'] = 'Unknown'  # Placeholder
                
                products.append(item)
            
            # Check if there are more pages
            has_more = data.get('has_more', False)
            page += 1
            
        except Exception as e:
            logger.error(f"Error syncing products: {str(e)}")
            break
    
    logger.info(f"Synced {len(products)} products")
    return products

def sync_inventory(last_sync):
    """
    Sync inventory from the ProHandel API
    """
    logger.info(f"Syncing inventory updated since {last_sync}")
    
    inventory = []
    page = 1
    has_more = True
    
    while has_more:
        try:
            # Make API request to get inventory
            response = make_api_request(
                '/inventory',
                params={
                    'updated_since': last_sync,
                    'page': page,
                    'page_size': DEFAULT_PAGE_SIZE
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch inventory: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                has_more = False
                break
            
            # Process inventory
            for item in items:
                # Add tenant ID
                item['tenant_id'] = TENANT_ID
                
                # Calculate days of supply (placeholder logic)
                if 'quantity' in item and 'reorder_level' in item and item['reorder_level'] > 0:
                    item['days_of_supply'] = item['quantity'] / item['reorder_level'] * 30
                else:
                    item['days_of_supply'] = None
                
                inventory.append(item)
            
            # Check if there are more pages
            has_more = data.get('has_more', False)
            page += 1
            
        except Exception as e:
            logger.error(f"Error syncing inventory: {str(e)}")
            break
    
    logger.info(f"Synced {len(inventory)} inventory records")
    return inventory

def sync_customers(last_sync):
    """
    Sync customers from the ProHandel API
    """
    logger.info(f"Syncing customers updated since {last_sync}")
    
    customers = []
    page = 1
    has_more = True
    
    while has_more:
        try:
            # Make API request to get customers
            response = make_api_request(
                '/customers',
                params={
                    'updated_since': last_sync,
                    'page': page,
                    'page_size': DEFAULT_PAGE_SIZE
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch customers: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                has_more = False
                break
            
            # Process customers
            for item in items:
                # Add tenant ID
                item['tenant_id'] = TENANT_ID
                
                # Create full address
                address_parts = []
                if item.get('address_street'):
                    address_parts.append(item['address_street'])
                if item.get('address_city'):
                    address_parts.append(item['address_city'])
                if item.get('address_state'):
                    address_parts.append(item['address_state'])
                if item.get('address_zip'):
                    address_parts.append(item['address_zip'])
                if item.get('address_country'):
                    address_parts.append(item['address_country'])
                
                item['full_address'] = ', '.join(address_parts) if address_parts else None
                
                customers.append(item)
            
            # Check if there are more pages
            has_more = data.get('has_more', False)
            page += 1
            
        except Exception as e:
            logger.error(f"Error syncing customers: {str(e)}")
            break
    
    logger.info(f"Synced {len(customers)} customers")
    return customers

def sync_orders(last_sync):
    """
    Sync orders from the ProHandel API
    """
    logger.info(f"Syncing orders updated since {last_sync}")
    
    orders = []
    page = 1
    has_more = True
    
    while has_more:
        try:
            # Make API request to get orders
            response = make_api_request(
                '/orders',
                params={
                    'updated_since': last_sync,
                    'page': page,
                    'page_size': DEFAULT_PAGE_SIZE
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch orders: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                has_more = False
                break
            
            # Process orders
            for item in items:
                # Add tenant ID
                item['tenant_id'] = TENANT_ID
                
                # Calculate order age in days
                if 'order_date' in item:
                    try:
                        order_date = dateutil.parser.parse(item['order_date'])
                        current_date = datetime.utcnow()
                        item['order_age_days'] = (current_date - order_date).days
                    except:
                        item['order_age_days'] = None
                else:
                    item['order_age_days'] = None
                
                orders.append(item)
            
            # Check if there are more pages
            has_more = data.get('has_more', False)
            page += 1
            
        except Exception as e:
            logger.error(f"Error syncing orders: {str(e)}")
            break
    
    logger.info(f"Synced {len(orders)} orders")
    return orders

def sync_order_items(last_sync):
    """
    Sync order items from the ProHandel API
    """
    logger.info(f"Syncing order items updated since {last_sync}")
    
    order_items = []
    page = 1
    has_more = True
    
    while has_more:
        try:
            # Make API request to get order items
            response = make_api_request(
                '/order_items',
                params={
                    'updated_since': last_sync,
                    'page': page,
                    'page_size': DEFAULT_PAGE_SIZE
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch order items: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                has_more = False
                break
            
            # Process order items
            for item in items:
                # Add tenant ID
                item['tenant_id'] = TENANT_ID
                
                # Calculate profit and margin
                if 'price' in item and 'cost' in item and 'quantity' in item:
                    item['item_total'] = item['price'] * item['quantity']
                    item['item_profit'] = (item['price'] - item['cost']) * item['quantity']
                    if item['price'] > 0:
                        item['item_margin'] = (item['price'] - item['cost']) / item['price']
                    else:
                        item['item_margin'] = None
                else:
                    item['item_total'] = None
                    item['item_profit'] = None
                    item['item_margin'] = None
                
                order_items.append(item)
            
            # Check if there are more pages
            has_more = data.get('has_more', False)
            page += 1
            
        except Exception as e:
            logger.error(f"Error syncing order items: {str(e)}")
            break
    
    logger.info(f"Synced {len(order_items)} order items")
    return order_items

def make_api_request(endpoint, params=None, method='GET', data=None, retries=0):
    """
    Make a request to the ProHandel API with retry logic
    """
    url = API_BASE_URL.rstrip('/') + '/' + endpoint.lstrip('/')
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, params=params, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Check if we need to retry
        if response.status_code >= 500 and retries < MAX_RETRIES:
            logger.warning(f"Request failed with status {response.status_code}, retrying ({retries+1}/{MAX_RETRIES})...")
            time.sleep(RETRY_DELAY * (2 ** retries))  # Exponential backoff
            return make_api_request(endpoint, params, method, data, retries + 1)
        
        return response
        
    except requests.exceptions.RequestException as e:
        if retries < MAX_RETRIES:
            logger.warning(f"Request failed with exception: {str(e)}, retrying ({retries+1}/{MAX_RETRIES})...")
            time.sleep(RETRY_DELAY * (2 ** retries))  # Exponential backoff
            return make_api_request(endpoint, params, method, data, retries + 1)
        else:
            raise

import json
import os
import boto3
from datetime import datetime
import traceback

# Import local modules
from prohandel_api import ProHandelAPI
from data_processor import DataProcessor
from schema import get_schema

# Create tmp logs directory
os.makedirs('/tmp/logs', exist_ok=True)

# Get API credentials from environment variables
API_KEY = os.environ.get('PROHANDEL_API_KEY', '7e7c639358434c4fa215d4e3978739d0')
API_SECRET = os.environ.get('PROHANDEL_API_SECRET', '1cjnuux79d')
AUTH_URL = os.environ.get('PROHANDEL_AUTH_URL', 'https://auth.prohandel.cloud/api/v4')
API_URL = os.environ.get('PROHANDEL_API_URL', 'https://linde.prohandel.de/api/v2')  # Updated to use verified working URL

# Initialize API client
api = ProHandelAPI(API_KEY, API_SECRET)

# Initialize data processor
data_processor = DataProcessor(API_KEY, API_SECRET)

def lambda_handler(event, context):
    """
    Lambda function handler for Fivetran connector
    """
    # Log the event for debugging
    try:
        print(f"Received event: {json.dumps(event)}")
        with open('/tmp/logs/event.log', 'w') as f:
            f.write(json.dumps(event, indent=2))
    except Exception as e:
        print(f"Error writing event log: {e}")
    
    # Process the Fivetran request
    try:
        # Extract credentials from secrets if provided
        secrets = event.get('secrets', {})
        if secrets:
            api_key = secrets.get('PROHANDEL_API_KEY', API_KEY)
            api_secret = secrets.get('PROHANDEL_API_SECRET', API_SECRET)
            auth_url = secrets.get('PROHANDEL_AUTH_URL', AUTH_URL)
            api_url = secrets.get('PROHANDEL_API_URL', API_URL)
            
            # Update API client with provided credentials
            api.api_key = api_key
            api.api_secret = api_secret
            api.auth_url = auth_url
            api.api_url = api_url
            api.access_token = None  # Force re-authentication
            
            # Update data processor
            data_processor.api = api
        
        # Determine request type
        request_type = ''
        if 'type' in event:
            request_type = event.get('type', '')
        elif 'schema' in event and event['schema'] is True:
            request_type = 'schema'
        elif 'table' in event:
            request_type = 'sync'
            
        print(f"Request type: {request_type}")
        
        if request_type == 'test':
            # Test connection to ProHandel API
            try:
                api.authenticate()
                return {"success": True, "message": "Connection to ProHandel API successful"}
            except Exception as e:
                error_msg = f"Connection to ProHandel API failed: {str(e)}"
                print(error_msg)
                return {"success": False, "message": error_msg}
        
        elif request_type == 'schema':
            # Return schema in Fivetran format
            schema = get_schema()
            # Ensure schema is formatted correctly for Fivetran
            print(f"Found {len(schema)} tables in schema:")
            for table_name in schema.keys():
                print(f"  - {table_name}")
            return schema
        
        elif request_type == 'sync':
            # Handle sync request with incremental loading
            state = event.get('state', {})
            limit = event.get('limit', 100)
            
            # Get the last sync timestamp for each entity
            articles_last_sync = state.get('articles_last_sync')
            customers_last_sync = state.get('customers_last_sync')
            orders_last_sync = state.get('orders_last_sync')
            sales_last_sync = state.get('sales_last_sync')
            inventory_last_sync = state.get('inventory_last_sync')
            
            # Get last sync timestamps for new endpoints
            suppliers_last_sync = state.get('suppliers_last_sync')
            branches_last_sync = state.get('branches_last_sync')
            categories_last_sync = state.get('categories_last_sync')
            countries_last_sync = state.get('countries_last_sync')
            credits_last_sync = state.get('credits_last_sync')
            currencies_last_sync = state.get('currencies_last_sync')
            invoices_last_sync = state.get('invoices_last_sync')
            labels_last_sync = state.get('labels_last_sync')
            payments_last_sync = state.get('payments_last_sync')
            staff_last_sync = state.get('staff_last_sync')
            vouchers_last_sync = state.get('vouchers_last_sync')
            
            print(f"Processing data with state: {state}")
            
            # Initialize response data
            insert_data = {}
            delete_data = {}
            
            try:
                # Process articles
                print("Processing articles...")
                articles = data_processor.process_articles(updated_since=articles_last_sync)
                if articles:
                    insert_data['articles'] = articles
                    # Update last sync timestamp
                    state['articles_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing articles: {str(e)}")
                traceback.print_exc()
            
            try:
                # Process customers
                print("Processing customers...")
                customers = data_processor.process_customers(updated_since=customers_last_sync)
                if customers:
                    insert_data['customers'] = customers
                    # Update last sync timestamp
                    state['customers_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing customers: {str(e)}")
                traceback.print_exc()
            
            try:
                # Process orders and order items
                print("Processing orders...")
                orders_data = data_processor.process_orders(updated_since=orders_last_sync)
                if orders_data.get('orders'):
                    insert_data['orders'] = orders_data['orders']
                    insert_data['order_items'] = orders_data.get('order_items', [])
                    # Update last sync timestamp
                    state['orders_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing orders: {str(e)}")
                traceback.print_exc()
            
            try:
                # Process sales and sale items
                print("Processing sales...")
                sales_data = data_processor.process_sales(updated_since=sales_last_sync)
                if sales_data.get('sales'):
                    insert_data['sales'] = sales_data['sales']
                    insert_data['sale_items'] = sales_data.get('sale_items', [])
                    # Update last sync timestamp
                    state['sales_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing sales: {str(e)}")
                traceback.print_exc()
            
            try:
                # Process inventory
                print("Processing inventory...")
                inventory = data_processor.process_inventory(updated_since=inventory_last_sync)
                if inventory:
                    insert_data['inventory'] = inventory
                    # Update last sync timestamp
                    state['inventory_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing inventory: {str(e)}")
                traceback.print_exc()
                
            # Process new endpoints
            try:
                # Process suppliers
                print("Processing suppliers...")
                suppliers = data_processor.process_suppliers(updated_since=suppliers_last_sync)
                if suppliers:
                    insert_data['suppliers'] = suppliers
                    # Update last sync timestamp
                    state['suppliers_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing suppliers: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process branches
                print("Processing branches...")
                branches = data_processor.process_branches(updated_since=branches_last_sync)
                if branches:
                    insert_data['branches'] = branches
                    # Update last sync timestamp
                    state['branches_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing branches: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process categories
                print("Processing categories...")
                categories = data_processor.process_categories(updated_since=categories_last_sync)
                if categories:
                    insert_data['categories'] = categories
                    # Update last sync timestamp
                    state['categories_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing categories: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process countries
                print("Processing countries...")
                countries = data_processor.process_countries(updated_since=countries_last_sync)
                if countries:
                    insert_data['countries'] = countries
                    # Update last sync timestamp
                    state['countries_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing countries: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process credits
                print("Processing credits...")
                credits = data_processor.process_credits(updated_since=credits_last_sync)
                if credits:
                    insert_data['credits'] = credits
                    # Update last sync timestamp
                    state['credits_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing credits: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process currencies
                print("Processing currencies...")
                currencies = data_processor.process_currencies(updated_since=currencies_last_sync)
                if currencies:
                    insert_data['currencies'] = currencies
                    # Update last sync timestamp
                    state['currencies_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing currencies: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process invoices
                print("Processing invoices...")
                invoices = data_processor.process_invoices(updated_since=invoices_last_sync)
                if invoices:
                    insert_data['invoices'] = invoices
                    # Update last sync timestamp
                    state['invoices_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing invoices: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process labels
                print("Processing labels...")
                labels = data_processor.process_labels(updated_since=labels_last_sync)
                if labels:
                    insert_data['labels'] = labels
                    # Update last sync timestamp
                    state['labels_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing labels: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process payments
                print("Processing payments...")
                payments = data_processor.process_payments(updated_since=payments_last_sync)
                if payments:
                    insert_data['payments'] = payments
                    # Update last sync timestamp
                    state['payments_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing payments: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process staff
                print("Processing staff...")
                staff = data_processor.process_staff(updated_since=staff_last_sync)
                if staff:
                    insert_data['staff'] = staff
                    # Update last sync timestamp
                    state['staff_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing staff: {str(e)}")
                traceback.print_exc()
                
            try:
                # Process vouchers
                print("Processing vouchers...")
                vouchers = data_processor.process_vouchers(updated_since=vouchers_last_sync)
                if vouchers:
                    insert_data['vouchers'] = vouchers
                    # Update last sync timestamp
                    state['vouchers_last_sync'] = datetime.now().isoformat()
            except Exception as e:
                print(f"Error processing vouchers: {str(e)}")
                traceback.print_exc()
            
            # Check if there's more data to sync
            has_more = False
            for entity in insert_data.values():
                if len(entity) >= limit:
                    has_more = True
                    break
            
            # Return sync response in Fivetran format
            # Ensure we're returning data even if empty to help Fivetran detect tables
            # If no data was processed, add empty arrays for all tables in the schema
            if not insert_data:
                schema_tables = get_schema().keys()
                for table in schema_tables:
                    insert_data[table] = []
            
            response = {
                "state": state,
                "insert": insert_data,
                "delete": delete_data,
                "hasMore": has_more
            }
            
            # Log detailed information about the data being returned
            print("\nReturning data for tables:")
            for table_name, rows in insert_data.items():
                print(f"  - {table_name}: {len(rows)} rows")
                if rows and len(rows) > 0:
                    # Print sample of first row with limited fields
                    sample = rows[0]
                    print(f"    Sample data (first row):")
                    count = 0
                    for key, value in sample.items():
                        if count < 5:
                            print(f"      {key}: {value}")
                            count += 1
                    if len(sample) > 5:
                        print(f"      ... and {len(sample) - 5} more fields")
            
            print(f"Returning response with {sum(len(v) for v in insert_data.values())} total rows")
            return response
        
        else:
            # Unknown request type
            error_msg = f"Unknown request type: {request_type}"
            print(error_msg)
            return {"success": False, "message": error_msg}
    
    except Exception as e:
        # Log the error
        error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        
        try:
            with open('/tmp/logs/error.log', 'w') as f:
                f.write(error_message)
        except Exception as log_error:
            print(f"Failed to write error log: {log_error}")
        
        # Return error response
        return {"success": False, "message": f"Error: {str(e)}"}

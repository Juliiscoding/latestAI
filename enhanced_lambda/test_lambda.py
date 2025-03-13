"""
Test script for the Lambda function and data processor
"""
import os
import json
from lambda_function import lambda_handler
from data_processor import DataProcessor
import traceback

# Set environment variables for testing
os.environ['PROHANDEL_API_KEY'] = '7e7c639358434c4fa215d4e3978739d0'
os.environ['PROHANDEL_API_SECRET'] = '1cjnuux79d'
os.environ['PROHANDEL_AUTH_URL'] = 'https://auth.prohandel.cloud/api/v4'
os.environ['PROHANDEL_API_URL'] = 'https://api.prohandel.de/api/v2'

def test_data_processor():
    """Test the data processor directly"""
    print("\n=== Testing Data Processor ===")
    try:
        # Initialize the data processor
        api_key = os.environ.get('PROHANDEL_API_KEY')
        api_secret = os.environ.get('PROHANDEL_API_SECRET')
        processor = DataProcessor(api_key, api_secret)
        
        # Test articles processing
        print("\nTesting articles processing...")
        articles = processor.process_articles()
        print(f"Processed {len(articles)} articles")
        if articles:
            print(f"Sample article: {json.dumps(articles[0], indent=2)}")
        
        # Test customers processing
        print("\nTesting customers processing...")
        customers = processor.process_customers()
        print(f"Processed {len(customers)} customers")
        if customers:
            print(f"Sample customer: {json.dumps(customers[0], indent=2)}")
        
        # Test orders processing
        print("\nTesting orders processing...")
        orders_data = processor.process_orders()
        print(f"Processed {len(orders_data['orders'])} orders and {len(orders_data['order_items'])} order items")
        if orders_data['orders']:
            print(f"Sample order: {json.dumps(orders_data['orders'][0], indent=2)}")
        
        # Test inventory processing
        print("\nTesting inventory processing...")
        inventory = processor.process_inventory()
        print(f"Processed {len(inventory)} inventory items")
        if inventory:
            print(f"Sample inventory item: {json.dumps(inventory[0], indent=2)}")
            
    except Exception as e:
        print(f"Error testing data processor: {str(e)}")
        traceback.print_exc()

def test_lambda_handler():
    """Test the Lambda handler with different event types"""
    print("\n=== Testing Lambda Handler ===")
    
    # Test schema event
    print("\nTesting schema event...")
    schema_event = {
        "schema": True
    }
    try:
        schema_response = lambda_handler(schema_event, None)
        print(f"Schema response status: {schema_response.get('state', {}).get('status')}")
        print(f"Tables: {', '.join(schema_response.get('schema', {}).keys())}")
    except Exception as e:
        print(f"Error testing schema event: {str(e)}")
        traceback.print_exc()
    
    # Test sync event for articles
    print("\nTesting sync event for articles...")
    sync_event = {
        "table": "articles",
        "state": {
            "last_sync": {
                "articles": None
            }
        },
        "secrets": {
            "PROHANDEL_API_KEY": os.environ.get('PROHANDEL_API_KEY'),
            "PROHANDEL_API_SECRET": os.environ.get('PROHANDEL_API_SECRET'),
            "PROHANDEL_AUTH_URL": os.environ.get('PROHANDEL_AUTH_URL'),
            "PROHANDEL_API_URL": os.environ.get('PROHANDEL_API_URL')
        }
    }
    try:
        sync_response = lambda_handler(sync_event, None)
        print(f"Sync response status: {sync_response.get('state', {}).get('status')}")
        print(f"Rows returned: {len(sync_response.get('insert', {}).get('articles', []))}")
        if sync_response.get('insert', {}).get('articles'):
            print(f"Sample row: {json.dumps(sync_response.get('insert', {}).get('articles')[0], indent=2)}")
    except Exception as e:
        print(f"Error testing sync event: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    test_data_processor()
    test_lambda_handler()

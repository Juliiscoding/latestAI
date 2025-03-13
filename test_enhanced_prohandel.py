"""
Test script for the enhanced ProHandel API implementation
"""
import os
import json
from enhanced_lambda.prohandel_api import ProHandelAPI
import traceback

# Get API credentials from environment variables or use defaults
API_KEY = os.environ.get('PROHANDEL_API_KEY', '7e7c639358434c4fa215d4e3978739d0')
API_SECRET = os.environ.get('PROHANDEL_API_SECRET', '1cjnuux79d')
AUTH_URL = os.environ.get('PROHANDEL_AUTH_URL', 'https://auth.prohandel.cloud/api/v4')
API_URL = os.environ.get('PROHANDEL_API_URL', 'https://linde.prohandel.de/api/v2')

def test_enhanced_prohandel_api():
    """Test the enhanced ProHandel API implementation"""
    print("\n=== Testing Enhanced ProHandel API Implementation ===")
    
    try:
        # Initialize the API client
        api = ProHandelAPI(API_KEY, API_SECRET)
        
        # Authenticate
        print("\nAuthenticating...")
        token = api.authenticate()
        print(f"Authentication successful! Token: {token[:10]}...")
        
        # Test endpoints
        endpoints = ["article", "customer", "order", "sale", "inventory"]
        
        for endpoint in endpoints:
            print(f"\n{'=' * 50}")
            print(f"Testing {endpoint.upper()} endpoint")
            print(f"{'=' * 50}")
            
            # Call the appropriate method based on endpoint
            try:
                if endpoint == "article":
                    response = api.get_articles(page=1, pagesize=5)
                elif endpoint == "customer":
                    response = api.get_customers(page=1, pagesize=5)
                elif endpoint == "order":
                    response = api.get_orders(page=1, pagesize=5)
                elif endpoint == "sale":
                    response = api.get_sales(page=1, pagesize=5)
                elif endpoint == "inventory":
                    response = api.get_inventory(page=1, pagesize=5)
                
                # Process response
                print(f"Response type: {type(response)}")
                
                # Check if response has data field
                if isinstance(response, dict) and 'data' in response:
                    data = response['data']
                    print(f"Received {len(data)} items in 'data' field")
                    
                    # Print first item if available
                    if data and len(data) > 0:
                        print(f"First item sample: {json.dumps(data[0], indent=2)[:500]}...")
                else:
                    print(f"Unexpected response format: {type(response)}")
                    print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
            
            except Exception as e:
                print(f"Error testing {endpoint} endpoint: {str(e)}")
                traceback.print_exc()
    
    except Exception as e:
        print(f"Error in test: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_prohandel_api()

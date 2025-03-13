#!/usr/bin/env python3
"""
Test script for the ProHandel Lambda function connector.
This script simulates Fivetran requests to test the Lambda function locally.
"""
import json
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

print(f"Current directory: {current_dir}")
print(f"Parent directory: {parent_dir}")
print(f"Python path: {sys.path}")

# Import the Lambda handler
try:
    print("Trying to import lambda_function...")
    from lambda_function import lambda_handler
    print("Successfully imported lambda_function")
except ImportError as e:
    print(f"Lambda function module not found: {e}")
    print("Checking if lambda_function.py exists...")
    if os.path.exists(os.path.join(current_dir, "lambda_function.py")):
        print("lambda_function.py exists in the current directory")
    else:
        print("lambda_function.py does not exist in the current directory")
    sys.exit(1)

def test_test_connection():
    """Test the test_connection operation of the Lambda function."""
    print("\n=== Testing TEST_CONNECTION operation ===")
    
    # Create a test event similar to what Fivetran would send
    test_event = {
        "request": {
            "operation": "test",
            "state": {},
            "secrets": {
                "api_key": os.environ.get("PROHANDEL_API_KEY"),
                "api_secret": os.environ.get("PROHANDEL_API_SECRET"),
                "auth_url": os.environ.get("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4"),
                "api_url": os.environ.get("PROHANDEL_API_URL", "https://api.prohandel.de/api/v2")
            }
        }
    }
    
    # Call the Lambda handler
    response = lambda_handler(test_event, {})
    
    # Print the response
    print(f"Response: {json.dumps(response, indent=2)}")
    
    return response

def test_get_schema():
    """Test the get_schema operation of the Lambda function."""
    print("\n=== Testing GET_SCHEMA operation ===")
    
    # Create a test event similar to what Fivetran would send
    test_event = {
        "request": {
            "operation": "schema",
            "state": {},
            "secrets": {
                "api_key": os.environ.get("PROHANDEL_API_KEY"),
                "api_secret": os.environ.get("PROHANDEL_API_SECRET"),
                "auth_url": os.environ.get("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4"),
                "api_url": os.environ.get("PROHANDEL_API_URL", "https://api.prohandel.de/api/v2")
            }
        }
    }
    
    # Call the Lambda handler
    response = lambda_handler(test_event, {})
    
    # Print the response
    print(f"Response: {json.dumps(response, indent=2)}")
    
    return response

def test_sync_data(entity_name="article", limit=5):
    """Test the sync_data operation of the Lambda function."""
    print(f"\n=== Testing SYNC_DATA operation for {entity_name} ===")
    
    # Create a test event similar to what Fivetran would send
    test_event = {
        "request": {
            "operation": "sync",
            "state": {},
            "secrets": {
                "api_key": os.environ.get("PROHANDEL_API_KEY"),
                "api_secret": os.environ.get("PROHANDEL_API_SECRET"),
                "auth_url": os.environ.get("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4"),
                "api_url": os.environ.get("PROHANDEL_API_URL", "https://api.prohandel.de/api/v2")
            },
            "tables": [
                {
                    "name": entity_name,
                    "columns": []  # Lambda should determine columns from schema
                }
            ],
            "limit": limit
        }
    }
    
    # Call the Lambda handler
    response = lambda_handler(test_event, {})
    
    # Print the response summary
    if "state" in response:
        print(f"Response state: {json.dumps(response['state'], indent=2)}")
    
    if "insert" in response and "tables" in response["insert"]:
        for table in response["insert"]["tables"]:
            print(f"Table: {table['name']}")
            print(f"Records synced: {len(table.get('rows', []))}")
            if table.get('rows'):
                print(f"First record sample: {json.dumps(list(table['rows'][0].keys()), indent=2)}")
    
    return response

if __name__ == "__main__":
    # Test all operations
    test_test_connection()
    test_get_schema()
    
    # Test sync for different entities
    entities = ["article", "customer", "order", "sale", "inventory", "branch", "supplier", "category"]
    for entity in entities:
        test_sync_data(entity)

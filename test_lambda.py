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
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Lambda handler
try:
    from lambda_connector.lambda_function import lambda_handler
except ImportError:
    print("Lambda function module not found. Make sure you're in the correct directory.")
    sys.exit(1)

def test_test_connection():
    """Test the test_connection operation of the Lambda function."""
    print("\n=== Testing TEST_CONNECTION operation ===")
    
    # Create a test event similar to what Fivetran would send
    test_event = {
        "agent": {
            "name": "fivetran-lambda-agent",
            "version": "1.0"
        },
        "operation": "TEST_CONNECTION",
        "state": {}
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
        "agent": {
            "name": "fivetran-lambda-agent",
            "version": "1.0"
        },
        "operation": "GET_SCHEMA",
        "state": {}
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
        "agent": {
            "name": "fivetran-lambda-agent",
            "version": "1.0"
        },
        "operation": "SYNC_DATA",
        "state": {},
        "schema": {
            "tables": [
                {
                    "name": entity_name,
                    "columns": []  # Lambda should determine columns from schema
                }
            ]
        },
        "limit": limit
    }
    
    # Call the Lambda handler
    response = lambda_handler(test_event, {})
    
    # Print the response
    print(f"Response status: {response.get('state', {}).get('hasMore', False)}")
    print(f"Records synced: {len(response.get('insert', {}).get('tables', [{}])[0].get('rows', []))}")
    
    # Print the first record if available
    if response.get('insert', {}).get('tables', [{}])[0].get('rows', []):
        print(f"First record: {json.dumps(response['insert']['tables'][0]['rows'][0], indent=2)}")
    
    return response

if __name__ == "__main__":
    # Test all operations
    test_test_connection()
    test_get_schema()
    
    # Test sync for different entities
    entities = ["article", "customer", "order", "sale", "inventory", "branch", "supplier", "category"]
    for entity in entities:
        test_sync_data(entity)

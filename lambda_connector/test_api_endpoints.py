#!/usr/bin/env python3
"""
Test script for the ProHandel API endpoints.
"""
import os
import sys
import json
import traceback
from pathlib import Path

# Add the parent directory to the path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import the necessary modules
from etl.connectors.prohandel_connector import prohandel_connector
from etl.config.config import API_CONFIG, API_ENDPOINTS
from etl.utils.auth import token_manager

def test_token():
    """Test the authentication token."""
    print("\n=== Testing Authentication Token ===")
    try:
        token = token_manager.get_token()
        print(f"Token: {token[:10]}...")
        print(f"Token expiry: {token_manager.token_expiry}")
        return True
    except Exception as e:
        print(f"Error getting token: {e}")
        traceback.print_exc()
        return False

def test_endpoint(endpoint_name, limit=5):
    """Test a specific API endpoint."""
    print(f"\n=== Testing endpoint: {endpoint_name} ===")
    
    try:
        # Get the endpoint configuration
        if endpoint_name not in API_ENDPOINTS:
            print(f"Endpoint {endpoint_name} not found in API_ENDPOINTS configuration")
            return False
        
        endpoint_config = API_ENDPOINTS[endpoint_name]
        print(f"Endpoint URL: {API_CONFIG['api_url']}/{endpoint_name}")
        print(f"Endpoint config: {endpoint_config}")
        
        # Ensure we have a valid token
        if not test_token():
            print("Authentication failed, cannot test endpoint")
            return False
        
        # Try making a direct request first
        try:
            print("Making direct request to endpoint...")
            response = prohandel_connector._make_request(f"/{endpoint_name}")
            print(f"Direct response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"Error making direct request: {e}")
            traceback.print_exc()
        
        # Fetch data from the endpoint using the get_entity_list method
        print("Fetching data using get_entity_list...")
        data = prohandel_connector.get_entity_list(endpoint_name, page=1, pagesize=limit)
        
        # Print the results
        if data:
            print(f"Successfully fetched {len(data)} records")
            if data:
                print(f"First record sample keys: {json.dumps(list(data[0].keys()), indent=2)}")
                print(f"First record sample (truncated): {json.dumps(data[0], indent=2)[:500]}...")
            return True
        else:
            print("No data returned")
            return False
    except Exception as e:
        print(f"Error testing endpoint {endpoint_name}: {e}")
        traceback.print_exc()
        return False

def test_all_endpoints(limit=5):
    """Test all API endpoints."""
    print("\n=== Testing all API endpoints ===")
    
    results = {}
    for endpoint_name in API_ENDPOINTS:
        results[endpoint_name] = test_endpoint(endpoint_name, limit)
    
    # Print summary
    print("\n=== Summary ===")
    successful = [name for name, result in results.items() if result]
    failed = [name for name, result in results.items() if not result]
    
    print(f"Successful endpoints ({len(successful)}): {', '.join(successful)}")
    print(f"Failed endpoints ({len(failed)}): {', '.join(failed)}")

if __name__ == "__main__":
    # Test specific endpoint if provided as argument
    if len(sys.argv) > 1:
        endpoint_name = sys.argv[1]
        test_endpoint(endpoint_name)
    else:
        # Test all endpoints
        test_all_endpoints()

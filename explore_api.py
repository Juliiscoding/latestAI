#!/usr/bin/env python3
"""
Script to explore the ProHandel API endpoints and structure.
This will authenticate and then try to discover available endpoints.
"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
api_key = os.environ.get("PROHANDEL_API_KEY")
api_secret = os.environ.get("PROHANDEL_API_SECRET")
auth_url = "https://auth.prohandel.cloud/api/v4"  # Hardcoded for testing

print(f"Auth URL: {auth_url}")

# Authenticate with the ProHandel API
def authenticate():
    """Authenticate with the ProHandel API and get access token."""
    auth_data = {
        "apiKey": api_key,
        "secret": api_secret
    }
    
    print(f"Authenticating with ProHandel API at {auth_url}/token...")
    try:
        response = requests.post(f"{auth_url}/token", json=auth_data)
        response.raise_for_status()
        
        auth_response = response.json()
        print(f"Authentication response status: {response.status_code}")
        
        # Handle different token response formats
        if "token" in auth_response and "token" in auth_response["token"] and "value" in auth_response["token"]["token"]:
            token = auth_response["token"]["token"]["value"]
            print("Token format: token.token.token.value")
            # Also print the server URL from the response
            if "serverUrl" in auth_response:
                print(f"Server URL from response: {auth_response['serverUrl']}")
                api_url = auth_response['serverUrl']
                print(f"Updated API URL to: {api_url}")
                return token, api_url
        elif "accessToken" in auth_response:
            token = auth_response["accessToken"]
            print("Token format: accessToken")
            return token, None
        else:
            print(f"Unexpected token format in response: {auth_response}")
            return None, None
        
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            if e.response.content:
                print(f"Response content: {e.response.content.decode()}")
        return None, None

# Test API endpoint with token
def test_endpoint(token, api_url, endpoint):
    """Test an API endpoint with the authentication token."""
    if not token:
        print("No token available. Cannot test endpoint.")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Ensure the API URL includes the version according to documentation
    if not api_url.endswith('/api/v2'):
        url = f"{api_url}/api/v2{endpoint}"
    else:
        url = f"{api_url}{endpoint}"
    
    print(f"Testing endpoint: {url}")
    
    try:
        # Add paging parameters as mentioned in the documentation
        params = {"pagesize": 5, "page": 1}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Endpoint response status: {response.status_code}")
        print(f"Received {len(data) if isinstance(data, list) else 'non-list'} records")
        
        # Print paging information from headers
        if 'x-page' in response.headers:
            print(f"Page: {response.headers['x-page']}")
        if 'x-pagesize' in response.headers:
            print(f"Page size: {response.headers['x-pagesize']}")
        if 'x-more-pages-available' in response.headers:
            print(f"More pages available: {response.headers['x-more-pages-available']}")
        
        # Print the first record if available
        if isinstance(data, list) and data:
            print(f"First record fields: {list(data[0].keys())}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Endpoint test failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            if e.response.content:
                print(f"Response content: {e.response.content.decode()}")
        return None

def discover_endpoints(token, api_url):
    """Try to discover available endpoints by testing common ones."""
    # Common endpoints to try
    common_endpoints = [
        "/article", "/customer", "/order", "/orderposition", "/sale", "/inventory",
        "/branch", "/supplier", "/category", "/brand", "/staff", "/shop",
        "/articlesize", "/cashregister", "/country", "/currency", "/discount",
        "/invoice", "/payment", "/pricechange", "/season", "/shape", "/size",
        "/stock", "/voucher", "/warehouse"
    ]
    
    # Test each endpoint
    successful_endpoints = []
    for endpoint in common_endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        data = test_endpoint(token, api_url, endpoint)
        if data is not None:
            successful_endpoints.append({
                "endpoint": endpoint,
                "record_count": len(data) if isinstance(data, list) else "non-list",
                "fields": list(data[0].keys()) if isinstance(data, list) and data else "unknown"
            })
    
    # Print summary of successful endpoints
    print("\n=== SUCCESSFUL ENDPOINTS ===")
    for endpoint_info in successful_endpoints:
        print(f"Endpoint: {endpoint_info['endpoint']}")
        print(f"Record count: {endpoint_info['record_count']}")
        if endpoint_info['fields'] != "unknown":
            print(f"Fields: {endpoint_info['fields']}")
        print("---")
    
    # Save the results to a file
    with open("api_endpoints.json", "w") as f:
        json.dump(successful_endpoints, f, indent=2)
    
    print(f"\nEndpoint information saved to api_endpoints.json")

if __name__ == "__main__":
    # Authenticate
    token, api_url = authenticate()
    
    if token and api_url:
        # Discover endpoints
        discover_endpoints(token, api_url)
    else:
        print("Authentication failed. Cannot discover endpoints.")

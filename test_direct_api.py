#!/usr/bin/env python3
"""
Direct API test for ProHandel API.
This script makes direct API calls to verify the ProHandel API is responding correctly.
"""
import os
import json
import requests
from datetime import datetime

# API credentials
API_KEY = "7e7c639358434c4fa215d4e3978739d0"
API_SECRET = "1cjnuux79d"
AUTH_URL = "https://auth.prohandel.cloud/api/v4"
API_URL = "https://api.prohandel.de/api/v2"

def authenticate():
    """Authenticate with the ProHandel API and get access token"""
    auth_data = {
        "apiKey": API_KEY,
        "secret": API_SECRET
    }
    
    print(f"Authenticating with {AUTH_URL}/token...")
    response = requests.post(f"{AUTH_URL}/token", json=auth_data)
    
    if response.status_code != 200:
        print(f"Authentication failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        return None, None
    
    auth_response = response.json()
    print("Authentication response structure:")
    print(json.dumps(auth_response, indent=2))
    
    # Extract server URL if available
    server_url = None
    if "serverUrl" in auth_response:
        server_url = auth_response["serverUrl"]
        print(f"Server URL from authentication: {server_url}")
    
    # Handle different response formats
    if "token" in auth_response and "value" in auth_response["token"]:
        token = auth_response["token"]["value"]
    elif "token" in auth_response and isinstance(auth_response["token"], dict) and "token" in auth_response["token"]:
        token = auth_response["token"]["token"]["value"]
    elif "access_token" in auth_response:
        token = auth_response["access_token"]
    else:
        print(f"Unexpected token format: {json.dumps(auth_response, indent=2)}")
        return None, None
    
    print(f"Successfully authenticated. Token: {token[:10]}...")
    return token, server_url

def test_endpoint(token, endpoint, params=None, server_url=None):
    """Test an API endpoint"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": "v2.29.1"
    }
    
    # Use server URL if provided, otherwise use default API URL
    base_url = server_url if server_url else API_URL
    
    # Add /api/v2 if not already in the URL
    if not base_url.endswith('/api/v2') and '/api/v2/' not in base_url:
        base_url = f"{base_url}/api/v2"
    
    # Ensure URL doesn't end with a slash
    if base_url.endswith('/'):
        base_url = base_url[:-1]
        
    url = f"{base_url}/{endpoint.lstrip('/')}"
    print(f"\nTesting endpoint: {url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        print(f"Status code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        # Handle empty response
        if not response.content:
            print("Empty response received")
            return None
        
        data = response.json()
        
        # Print summary of response
        if isinstance(data, list):
            print(f"Received list with {len(data)} items")
            if data:
                print("First item sample:")
                print(json.dumps(data[0], indent=2))
        elif isinstance(data, dict):
            if "data" in data:
                items = data["data"]
                print(f"Received {len(items)} items in 'data' field")
                if items:
                    print("First item sample:")
                    print(json.dumps(items[0], indent=2))
            else:
                print("Response structure:")
                print(json.dumps({k: "..." for k in data.keys()}, indent=2))
        
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        print(f"Raw response: {response.content}")
        return None

def main():
    """Main function to test the ProHandel API"""
    print("=== ProHandel Direct API Test ===")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Auth URL: {AUTH_URL}")
    print(f"Default API URL: {API_URL}")
    
    # Test authentication
    token, server_url = authenticate()
    if not token:
        print("Authentication failed. Cannot proceed with endpoint tests.")
        return
    
    # Use server URL from authentication if available
    api_url = server_url if server_url else API_URL
    print(f"Using API URL: {api_url}")
    
    # Test endpoints with a single record request
    endpoints = [
        ("article", {"page": 1, "pagesize": 5}),
        ("customer", {"page": 1, "pagesize": 5}),
        ("order", {"page": 1, "pagesize": 5}),
        ("sale", {"page": 1, "pagesize": 5}),
        ("inventory", {"page": 1, "pagesize": 5}),
        ("branch", {"page": 1, "pagesize": 5})
    ]
    
    results = {}
    
    for name, params in endpoints:
        print(f"\n{'='*50}")
        print(f"Testing {name} endpoint...")
        response = test_endpoint(token, name, params, server_url)
        
        if response:
            results[name] = "Success"
        else:
            results[name] = "Failed"
    
    # Print summary
    print("\n\n=== Test Summary ===")
    for name, status in results.items():
        print(f"{name}: {status}")

if __name__ == "__main__":
    main()

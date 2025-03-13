#!/usr/bin/env python3
"""
Simple test script to verify authentication with the ProHandel API.
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
api_key = os.environ.get("PROHANDEL_API_KEY")
api_secret = os.environ.get("PROHANDEL_API_SECRET")
auth_url = "https://auth.prohandel.cloud/api/v4"  # Hardcoded for testing
api_url = "https://api.prohandel.de/api/v2"  # Updated based on documentation

print(f"Auth URL: {auth_url}")
print(f"API URL: {api_url}")

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
                global api_url
                api_url = auth_response['serverUrl']
                print(f"Updated API URL to: {api_url}")
        elif "accessToken" in auth_response:
            token = auth_response["accessToken"]
            print("Token format: accessToken")
        else:
            print(f"Unexpected token format in response: {auth_response}")
            return None
        
        print(f"Authentication successful. Token: {token[:10]}...")
        return token
        
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            if e.response.content:
                print(f"Response content: {e.response.content.decode()}")
        return None

# Test API endpoint with token
def test_endpoint(token, endpoint="/customer"):
    """Test an API endpoint with the authentication token."""
    if not token:
        print("No token available. Cannot test endpoint.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
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
        print(f"Received {len(data)} records")
        
        # Print paging information from headers
        if 'x-page' in response.headers:
            print(f"Page: {response.headers['x-page']}")
        if 'x-pagesize' in response.headers:
            print(f"Page size: {response.headers['x-pagesize']}")
        if 'x-more-pages-available' in response.headers:
            print(f"More pages available: {response.headers['x-more-pages-available']}")
            
        print(f"First record: {data[0] if data else 'No data'}")
        
    except requests.exceptions.RequestException as e:
        print(f"Endpoint test failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            if e.response.content:
                print(f"Response content: {e.response.content.decode()}")

if __name__ == "__main__":
    # Test authentication
    token = authenticate()
    
    # Test API endpoint
    if token:
        # Try multiple endpoints based on the documentation
        endpoints = ["/customer", "/article", "/order", "/sale", "/inventory"]
        for endpoint in endpoints:
            print(f"\nTesting endpoint: {endpoint}")
            test_endpoint(token, endpoint)

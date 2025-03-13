"""
Test script to directly test the ProHandel API endpoints
"""
import os
import json
import requests
from requests.exceptions import RequestException
import traceback

# Load environment variables from .env file
def load_env_vars():
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
        return env_vars
    except Exception as e:
        print(f"Error loading .env file: {e}")
        return {}

# Get API credentials
env_vars = load_env_vars()
API_KEY = env_vars.get('PROHANDEL_API_KEY', '7e7c639358434c4fa215d4e3978739d0')
API_SECRET = env_vars.get('PROHANDEL_API_SECRET', '1cjnuux79d')
AUTH_URL = env_vars.get('PROHANDEL_AUTH_URL', 'https://auth.prohandel.cloud/api/v4')
API_URL = env_vars.get('PROHANDEL_API_URL', 'https://linde.prohandel.de/api/v2')

def authenticate():
    """Authenticate with the ProHandel API and get an access token"""
    print(f"Authenticating with {AUTH_URL}...")
    try:
        auth_data = {
            "apiKey": API_KEY,
            "secret": API_SECRET
        }
        
        response = requests.post(f"{AUTH_URL}/token", json=auth_data)
        response.raise_for_status()
        
        auth_response = response.json()
        access_token = auth_response["token"]["token"]["value"]
        print("Authentication successful!")
        return access_token
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        traceback.print_exc()
        return None

def test_endpoint(endpoint, access_token, params=None):
    """Test a specific API endpoint"""
    if params is None:
        params = {"page": 1, "pagesize": 10}
    
    # List of URL patterns to try, based on the working implementation
    url_patterns = [
        f"{API_URL}/{endpoint.lstrip('/')}",                  # Standard pattern
        f"{API_URL}/v2/{endpoint.lstrip('/')}",              # With v2 prefix
        f"{API_URL}/api/v2/{endpoint.lstrip('/')}",          # With api/v2 prefix
        f"{API_URL}/v2.29.1/{endpoint.lstrip('/')}",         # With version number
        f"https://linde.prohandel.de/api/v2/{endpoint.lstrip('/')}"  # Full URL with v2
    ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": "v2.29.1"
    }
    
    print(f"\nTesting endpoint: {endpoint}")
    print(f"Parameters: {params}")
    
    for url in url_patterns:
        print(f"\nTrying URL: {url}")
        try:
            response = requests.get(url, headers=headers, params=params)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response is a list or dictionary
                if isinstance(data, list):
                    print(f"Received list response with {len(data)} items")
                    if data:
                        print(f"First item sample: {json.dumps(data[0], indent=2)[:500]}...")
                elif isinstance(data, dict):
                    # Check if there's a data field
                    if 'data' in data:
                        items = data['data']
                        if isinstance(items, list):
                            print(f"Received {len(items)} items in 'data' field")
                            if items:
                                print(f"First item sample: {json.dumps(items[0], indent=2)[:500]}...")
                        else:
                            print(f"'data' field is not a list: {type(items)}")
                            print(f"Data sample: {json.dumps(data, indent=2)[:500]}...")
                    else:
                        print(f"No 'data' field in response")
                        print(f"Response keys: {list(data.keys())}")
                        print(f"Data sample: {json.dumps(data, indent=2)[:500]}...")
                else:
                    print(f"Unexpected response type: {type(data)}")
                
                # Return success status and data for the first successful URL
                return True, data
            else:
                print(f"Error response: {response.text}")
                # Continue to the next URL pattern
        except RequestException as e:
            print(f"Request error: {str(e)}")
            # Continue to the next URL pattern
        except Exception as e:
            print(f"Error: {str(e)}")
            # Continue to the next URL pattern
    
    # If all URL patterns failed, return failure
    print("All URL patterns failed for endpoint", endpoint)
    return False, None

def main():
    """Main function to test all endpoints"""
    # Authenticate
    access_token = authenticate()
    if not access_token:
        print("Authentication failed, cannot proceed with tests")
        return
    
    # List of endpoints to test
    endpoints = ["article", "customer", "order", "sale", "inventory"]
    
    # Test each endpoint
    results = {}
    for endpoint in endpoints:
        print(f"\n{'=' * 50}")
        print(f"Testing {endpoint.upper()} endpoint")
        print(f"{'=' * 50}")
        success, data = test_endpoint(endpoint, access_token)
        results[endpoint] = {
            "success": success,
            "has_data": bool(data and (isinstance(data, list) or 
                                      (isinstance(data, dict) and data.get('data'))))
        }
    
    # Print summary
    print("\n\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    for endpoint, result in results.items():
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        has_data = "✅ HAS DATA" if result["has_data"] else "❌ NO DATA"
        print(f"{endpoint.upper()}: {status} | {has_data}")

if __name__ == "__main__":
    main()

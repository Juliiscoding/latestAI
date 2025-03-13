#!/usr/bin/env python3
"""
Direct ProHandel API Test Script
This script tests direct connections to the ProHandel API without using Lambda
Focuses on core endpoints needed for CloudStock functionality:
- Authentication
- Inventory data (stock levels)
- Product data (details, pricing)
- Sales data (for historical analysis)
"""

import os
import json
import requests
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

class ProHandelDirectAPI:
    """Simple direct API client for ProHandel"""
    
    def __init__(self, api_key=None, api_secret=None):
        # Use provided credentials or load from environment
        self.api_key = api_key or os.getenv("PROHANDEL_API_KEY", "7e7c639358434c4fa215d4e3978739d0")
        self.api_secret = api_secret or os.getenv("PROHANDEL_API_SECRET", "1cjnuux79d")
        
        # Multiple possible URLs to try
        self.auth_urls = [
            "https://auth.prohandel.cloud/api/v4",
            "https://auth.prohandel.de/api/v4",
            "https://linde.prohandel.de/auth/api/v4"
        ]
        
        self.api_urls = [
            "https://linde.prohandel.de/api/v2",
            "https://api.prohandel.de/api/v2"
        ]
        
        self.access_token = None
        self.session = requests.Session()
        
        # Store successful URLs
        self.working_auth_url = None
        self.working_api_url = None
    
    def authenticate(self, verbose=True):
        """Try authentication with multiple possible URLs"""
        auth_data = {
            "apiKey": self.api_key,
            "secret": self.api_secret
        }
        
        if verbose:
            print(f"Attempting authentication with credentials:")
            print(f"  API Key: {self.api_key[:5]}...{self.api_key[-4:]}")
            print(f"  Secret: {self.api_secret[:3]}...{self.api_secret[-2:]}")
        
        # Try each auth URL
        for auth_url in self.auth_urls:
            try:
                if verbose:
                    print(f"\nTrying authentication URL: {auth_url}")
                
                response = self.session.post(f"{auth_url}/token", json=auth_data)
                
                if verbose:
                    print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    auth_response = response.json()
                    
                    # Handle different response formats
                    if "token" in auth_response and "value" in auth_response["token"]:
                        self.access_token = auth_response["token"]["value"]
                    elif "token" in auth_response and isinstance(auth_response["token"], dict) and "token" in auth_response["token"]:
                        self.access_token = auth_response["token"]["token"]["value"]
                    elif "access_token" in auth_response:
                        self.access_token = auth_response["access_token"]
                    else:
                        print(f"Unexpected token format: {json.dumps(auth_response, indent=2)}")
                        continue
                    
                    if verbose:
                        print(f"Authentication successful with {auth_url}")
                        print(f"Token: {self.access_token[:10]}...")
                    
                    self.working_auth_url = auth_url
                    return self.access_token
                else:
                    if verbose:
                        print(f"Authentication failed with status {response.status_code}")
                        print(f"Response: {response.text}")
            
            except Exception as e:
                if verbose:
                    print(f"Error with {auth_url}: {str(e)}")
                    traceback.print_exc()
        
        raise Exception("Authentication failed with all URLs")
    
    def make_api_request(self, endpoint, params=None, method="GET", verbose=True):
        """Make an API request with multiple URL patterns"""
        if not self.access_token:
            self.authenticate(verbose=verbose)
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Version": "v2.29.1"
        }
        
        # Try each API URL
        for api_url in self.api_urls:
            url = f"{api_url}/{endpoint.lstrip('/')}"
            
            try:
                if verbose:
                    print(f"\nTrying API URL: {url}")
                    print(f"Parameters: {params}")
                
                response = self.session.request(method, url, headers=headers, params=params)
                
                if verbose:
                    print(f"Response status: {response.status_code}")
                    print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    self.working_api_url = api_url
                    
                    # Try to parse as JSON
                    try:
                        data = response.json()
                        if verbose:
                            print(f"Response type: {type(data)}")
                            if isinstance(data, list):
                                print(f"Received {len(data)} items")
                            elif isinstance(data, dict) and "data" in data:
                                print(f"Received {len(data['data'])} items")
                        return data
                    except json.JSONDecodeError:
                        if verbose:
                            print(f"Could not parse response as JSON: {response.text[:100]}...")
                        return response.text
                
                elif response.status_code == 401:
                    # Try to refresh token and retry
                    if verbose:
                        print("Token expired, refreshing...")
                    self.authenticate(verbose=False)
                    return self.make_api_request(endpoint, params, method, verbose)
                
                else:
                    if verbose:
                        print(f"Request failed with status {response.status_code}")
                        print(f"Response: {response.text[:200]}...")
            
            except Exception as e:
                if verbose:
                    print(f"Error with {url}: {str(e)}")
                    traceback.print_exc()
        
        raise Exception(f"API request failed for all URLs: {endpoint}")
    
    def test_core_endpoints(self, verbose=True):
        """Test the core endpoints needed for CloudStock functionality"""
        results = {}
        
        # Core endpoints for CloudStock
        core_endpoints = [
            ("articles", "article"),
            ("inventory", "inventory"),
            ("sales", "sale")
        ]
        
        for name, endpoint in core_endpoints:
            try:
                if verbose:
                    print(f"\n=== Testing {name} endpoint ===")
                
                # Request just one item to test
                response = self.make_api_request(endpoint, params={"page": 1, "pagesize": 1}, verbose=verbose)
                
                # Process response
                if isinstance(response, list):
                    count = len(response)
                    sample = response[0] if count > 0 else None
                elif isinstance(response, dict) and "data" in response:
                    count = len(response["data"])
                    sample = response["data"][0] if count > 0 else None
                else:
                    count = 1
                    sample = response
                
                results[name] = {
                    "status": "Success",
                    "count": count,
                    "sample": sample
                }
                
                if verbose:
                    print(f"Successfully retrieved {count} {name}")
            
            except Exception as e:
                if verbose:
                    print(f"Error testing {name}: {str(e)}")
                
                results[name] = {
                    "status": "Error",
                    "error": str(e)
                }
        
        return results
    
    def get_working_config(self):
        """Return the working configuration for future use"""
        if not self.working_auth_url or not self.working_api_url:
            raise Exception("No working configuration found. Run test_core_endpoints first.")
        
        return {
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "auth_url": self.working_auth_url,
            "api_url": self.working_api_url
        }


def main():
    """Main function to test the ProHandel API"""
    print("=== ProHandel Direct API Test ===")
    print(f"Time: {datetime.now().isoformat()}")
    print("\nThis script tests direct connections to the ProHandel API")
    print("focusing on core endpoints needed for CloudStock functionality.")
    
    # Create API client
    api = ProHandelDirectAPI()
    
    try:
        # Test authentication
        print("\n=== Testing Authentication ===")
        token = api.authenticate()
        print("Authentication successful!")
        
        # Test core endpoints
        print("\n=== Testing Core Endpoints ===")
        results = api.test_core_endpoints()
        
        # Get working configuration
        config = api.get_working_config()
        
        # Save results to file
        output = {
            "timestamp": datetime.now().isoformat(),
            "working_config": config,
            "endpoint_results": results
        }
        
        with open("prohandel_direct_test_results.json", "w") as f:
            json.dump(output, f, indent=2)
        
        print("\n=== Test Results Summary ===")
        for endpoint, result in results.items():
            status = result["status"]
            if status == "Success":
                print(f"✅ {endpoint}: {result['count']} items")
            else:
                print(f"❌ {endpoint}: {result['error']}")
        
        print("\n=== Working Configuration ===")
        print(f"Auth URL: {config['auth_url']}")
        print(f"API URL: {config['api_url']}")
        print(f"API Key: {config['api_key'][:5]}...{config['api_key'][-4:]}")
        
        print("\nResults saved to prohandel_direct_test_results.json")
    
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

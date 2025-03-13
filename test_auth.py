#!/usr/bin/env python
"""
Test script to demonstrate the authentication with the ProHandel API.
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API credentials
API_KEY = os.getenv("PROHANDEL_API_KEY")
API_SECRET = os.getenv("PROHANDEL_API_SECRET")
AUTH_URL = os.getenv("PROHANDEL_AUTH_URL", "https://linde.prohandel.de/api/v2/auth")
API_URL = os.getenv("PROHANDEL_API_URL", "https://linde.prohandel.de/api/v2")

def authenticate():
    """Authenticate with the ProHandel API and get an access token."""
    print(f"Authenticating with {AUTH_URL}...")
    
    # Prepare authentication data
    auth_data = {
        "apiKey": API_KEY,
        "apiSecret": API_SECRET
    }
    
    try:
        # Make authentication request
        response = requests.post(f"{AUTH_URL}/token", json=auth_data)
        response.raise_for_status()
        
        # Parse response
        auth_response = response.json()
        
        if "accessToken" not in auth_response:
            print(f"Error: No access token in response: {auth_response}")
            return None
        
        # Get token and expiry
        token = auth_response["accessToken"]
        expires_in = auth_response.get("expiresIn", 3600)  # Default to 1 hour
        expiry = datetime.now() + timedelta(seconds=expires_in)
        
        print(f"Authentication successful! Token expires at {expiry}")
        
        return {
            "token": token,
            "expiry": expiry
        }
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def test_api_call(token):
    """Test an API call with the token."""
    print(f"Testing API call to {API_URL}/article...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make API request
        response = requests.get(f"{API_URL}/article", headers=headers, params={"page": 1, "pagesize": 5})
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        print(f"API call successful! Got {len(data)} articles")
        print(f"First article: {json.dumps(data[0], indent=2)}")
        
        return data
    except Exception as e:
        print(f"API call failed: {e}")
        return None

def main():
    """Main function."""
    print("Starting authentication test")
    
    # Authenticate
    auth_result = authenticate()
    
    if not auth_result:
        print("Authentication failed. Exiting.")
        return
    
    # Test API call
    test_api_call(auth_result["token"])
    
    print("Authentication test complete")

if __name__ == "__main__":
    main()

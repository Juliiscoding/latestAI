#!/usr/bin/env python3
"""
Simple test script for the ProHandel API authentication.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import the auth module
from etl.utils.auth import token_manager
from etl.config.config import API_CONFIG

def test_authentication():
    """Test authentication with the ProHandel API."""
    print("\n=== Testing Authentication ===")
    print(f"API Key: {API_CONFIG['api_key'][:5]}...")
    print(f"Auth URL: {API_CONFIG['auth_url']}")
    
    # Authenticate using the singleton token manager
    try:
        token_manager.authenticate()
        print(f"Authentication successful!")
        print(f"Access token: {token_manager.token[:10]}..." if token_manager.token else "No token received")
        print(f"Token expiry: {token_manager.token_expiry}")
        
        # Check if server_url is available in the token manager
        server_url = getattr(token_manager, 'server_url', None)
        if server_url:
            print(f"Server URL: {server_url}")
        else:
            print("Server URL not available in token manager")
        
        return True
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False

if __name__ == "__main__":
    test_authentication()

#!/usr/bin/env python3
"""
List Fivetran Services

This script lists available services in Fivetran.
"""

import requests
from base64 import b64encode

# Fivetran API credentials
API_KEY = "eWMMoSTR8ijWdw2u"
API_SECRET = "5hsGtNOxT5FkQYaTDZnzYmyAmhqmXBuR"

def get_auth_header():
    """Create Fivetran API authentication header."""
    auth_string = f"{API_KEY}:{API_SECRET}"
    encoded_auth = b64encode(auth_string.encode('utf-8')).decode('utf-8')
    return {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json'
    }

def list_services():
    """List available services."""
    url = "https://api.fivetran.com/v1/metadata/connectors"
    headers = get_auth_header()
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        services = response.json()['data']['items']
        print("\n=== Available Services ===")
        for service in services:
            print(f"Service: {service['id']}, Name: {service['name']}")
        return services
    else:
        print(f"Error listing services: {response.status_code}")
        print(response.text)
        return []

if __name__ == "__main__":
    list_services()

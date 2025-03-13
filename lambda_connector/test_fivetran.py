#!/usr/bin/env python
"""
Test script for the Fivetran connector
"""
import os
import json
import requests
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fivetran API credentials
FIVETRAN_API_KEY = os.getenv("FIVETRAN_API_KEY")
FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET")

# Fivetran API base URL
FIVETRAN_API_URL = "https://api.fivetran.com/v1"

def get_connector_details(connector_id):
    """Get details of a Fivetran connector."""
    url = f"{FIVETRAN_API_URL}/connectors/{connector_id}"
    response = requests.get(url, auth=(FIVETRAN_API_KEY, FIVETRAN_API_SECRET))
    return response.json()

def list_connectors():
    """List all connectors in the Fivetran account."""
    url = f"{FIVETRAN_API_URL}/connectors"
    response = requests.get(url, auth=(FIVETRAN_API_KEY, FIVETRAN_API_SECRET))
    return response.json()

def test_connector(connector_id):
    """Test a Fivetran connector."""
    url = f"{FIVETRAN_API_URL}/connectors/{connector_id}/test"
    response = requests.post(url, auth=(FIVETRAN_API_KEY, FIVETRAN_API_SECRET))
    return response.json()

def sync_connector(connector_id):
    """Sync a Fivetran connector."""
    url = f"{FIVETRAN_API_URL}/connectors/{connector_id}/sync"
    response = requests.post(url, auth=(FIVETRAN_API_KEY, FIVETRAN_API_SECRET))
    return response.json()

def main():
    """Main function to run the test script."""
    parser = argparse.ArgumentParser(description="Test Fivetran connector")
    parser.add_argument("--connector-id", default="ozone_lip", help="Fivetran connector ID")
    parser.add_argument("--list", action="store_true", help="List all connectors")
    parser.add_argument("--details", action="store_true", help="Get connector details")
    parser.add_argument("--test", action="store_true", help="Test connector")
    parser.add_argument("--sync", action="store_true", help="Sync connector")
    
    args = parser.parse_args()
    
    if args.list:
        print("Listing all connectors...")
        response = list_connectors()
        print(json.dumps(response, indent=2))
    
    if args.details:
        print(f"Getting details for connector {args.connector_id}...")
        response = get_connector_details(args.connector_id)
        print(json.dumps(response, indent=2))
    
    if args.test:
        print(f"Testing connector {args.connector_id}...")
        response = test_connector(args.connector_id)
        print(json.dumps(response, indent=2))
    
    if args.sync:
        print(f"Syncing connector {args.connector_id}...")
        response = sync_connector(args.connector_id)
        print(json.dumps(response, indent=2))
    
    if not (args.list or args.details or args.test or args.sync):
        print("No action specified. Use --list, --details, --test, or --sync.")

if __name__ == "__main__":
    main()

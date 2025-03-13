#!/usr/bin/env python3
"""
List Fivetran Resources

This script lists available groups and destinations in your Fivetran account.
"""

import requests
import json
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

def list_groups():
    """List available groups."""
    url = "https://api.fivetran.com/v1/groups"
    headers = get_auth_header()
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        groups = response.json()['data']['items']
        print("\n=== Available Groups ===")
        for i, group in enumerate(groups):
            print(f"{i}: ID: {group['id']}, Name: {group['name']}")
        return groups
    else:
        print(f"Error listing groups: {response.status_code}")
        print(response.text)
        return []

def list_destinations(group_id):
    """List available destinations in the group."""
    url = f"https://api.fivetran.com/v1/groups/{group_id}/destinations"
    headers = get_auth_header()
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        destinations = response.json()['data']['items']
        print(f"\n=== Available Destinations for Group {group_id} ===")
        for i, dest in enumerate(destinations):
            print(f"{i}: ID: {dest['id']}, Name: {dest['name']}, Service: {dest['service']}")
        return destinations
    else:
        print(f"Error listing destinations: {response.status_code}")
        print(response.text)
        return []

def list_connectors(group_id):
    """List available connectors in the group."""
    url = f"https://api.fivetran.com/v1/groups/{group_id}/connectors"
    headers = get_auth_header()
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        connectors = response.json()['data']['items']
        print(f"\n=== Available Connectors for Group {group_id} ===")
        for i, conn in enumerate(connectors):
            print(f"{i}: ID: {conn['id']}, Name: {conn['schema']}, Service: {conn['service']}, Status: {conn['status']['setup_state']}")
        return connectors
    else:
        print(f"Error listing connectors: {response.status_code}")
        print(response.text)
        return []

def save_config(group_id, destination_id):
    """Save the configuration to a file."""
    config = {
        "api_key": API_KEY,
        "api_secret": API_SECRET,
        "group_id": group_id,
        "destination_id": destination_id,
        "lambda_arn": "",
        "aws_region": "eu-central-1",
        "prohandel_username": "",
        "prohandel_password": "",
        "prohandel_auth_url": "https://auth.prohandel.cloud/api/v4",
        "prohandel_api_url": "https://api.prohandel.de/api/v2",
        "schema_name": "prohandel_data"
    }
    
    with open('fivetran_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\nConfiguration saved to fivetran_config.json")
    print("Please update the missing fields (lambda_arn, prohandel_username, prohandel_password)")

def main():
    """Main function."""
    print("Listing Fivetran resources...")
    
    # List groups
    groups = list_groups()
    if not groups:
        return
    
    # Select a group
    group_idx = int(input("\nEnter the number of the group to use (0-based index): "))
    group_id = groups[group_idx]['id']
    
    # List destinations for the selected group
    destinations = list_destinations(group_id)
    if not destinations:
        return
    
    # Select a destination
    dest_idx = int(input("\nEnter the number of the destination to use (0-based index): "))
    destination_id = destinations[dest_idx]['id']
    
    # List connectors for the selected group
    connectors = list_connectors(group_id)
    
    # Save the configuration
    save_config(group_id, destination_id)
    
    print("\nNext steps:")
    print("1. Update the fivetran_config.json file with your ProHandel credentials and Lambda ARN")
    print("2. Run the fivetran_api_setup.py script with the config file:")
    print("   python fivetran_api_setup.py --config fivetran_config.json")

if __name__ == "__main__":
    main()

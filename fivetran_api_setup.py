#!/usr/bin/env python3
"""
Fivetran API Setup Script

This script automates the setup of a Fivetran connector for ProHandel using the Fivetran API.
It handles creating the connector, configuring it, and starting the initial sync.
"""

import argparse
import json
import os
import requests
import subprocess
import sys
import time
from base64 import b64encode
from datetime import datetime

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Set up Fivetran connector via API')
    parser.add_argument('--api-key', type=str, help='Fivetran API key')
    parser.add_argument('--api-secret', type=str, help='Fivetran API secret')
    parser.add_argument('--group-id', type=str, help='Fivetran group ID')
    parser.add_argument('--lambda-arn', type=str, help='AWS Lambda function ARN')
    parser.add_argument('--aws-region', type=str, default='eu-central-1', help='AWS region')
    parser.add_argument('--prohandel-username', type=str, help='ProHandel username')
    parser.add_argument('--prohandel-password', type=str, help='ProHandel password')
    parser.add_argument('--prohandel-auth-url', type=str, 
                        default='https://auth.prohandel.cloud/api/v4', help='ProHandel auth URL')
    parser.add_argument('--prohandel-api-url', type=str, 
                        default='https://api.prohandel.de/api/v2', help='ProHandel API URL')
    parser.add_argument('--destination-id', type=str, help='Fivetran destination ID')
    parser.add_argument('--schema-name', type=str, default='prohandel_data', help='Schema name')
    parser.add_argument('--config', type=str, help='Path to config file with all parameters')
    return parser.parse_args()

def load_config(config_path):
    """Load configuration from file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)

def get_aws_lambda_arn():
    """Get AWS Lambda ARN using AWS CLI."""
    try:
        cmd = [
            'aws', 'lambda', 'list-functions',
            '--region', 'eu-central-1',
            '--query', 'Functions[?starts_with(FunctionName, `prohandel`)].FunctionArn',
            '--output', 'text'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        arn = result.stdout.strip()
        if arn:
            return arn
        else:
            print("No Lambda function with 'prohandel' in the name found.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error getting Lambda ARN: {e}")
        return None

def get_fivetran_auth_header(api_key, api_secret):
    """Create Fivetran API authentication header."""
    auth_string = f"{api_key}:{api_secret}"
    encoded_auth = b64encode(auth_string.encode('utf-8')).decode('utf-8')
    return {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json'
    }

def create_connector(api_key, api_secret, group_id, connector_name):
    """Create a new Fivetran connector."""
    url = f"https://api.fivetran.com/v1/connectors"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    payload = {
        "service": "lambda",
        "group_id": group_id,
        "paused": True,
        "trust_certificates": True,
        "trust_fingerprints": True,
        "run_setup_tests": False,
        "config": {
            "connector.name": connector_name
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Connector created successfully: {connector_name}")
        return response.json()['data']['id']
    else:
        print(f"Error creating connector: {response.status_code}")
        print(response.text)
        return None

def configure_connector(api_key, api_secret, connector_id, lambda_arn, aws_region, 
                        prohandel_username, prohandel_password, prohandel_auth_url, prohandel_api_url):
    """Configure the Fivetran connector with AWS Lambda details and secrets."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    payload = {
        "config": {
            "function_arn": lambda_arn,
            "region": aws_region,
            "execution_timeout": 180,
            "secrets": {
                "PROHANDEL_USERNAME": prohandel_username,
                "PROHANDEL_PASSWORD": prohandel_password,
                "PROHANDEL_AUTH_URL": prohandel_auth_url,
                "PROHANDEL_API_URL": prohandel_api_url
            }
        }
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Connector configured successfully")
        return True
    else:
        print(f"Error configuring connector: {response.status_code}")
        print(response.text)
        return False

def test_connector(api_key, api_secret, connector_id):
    """Test the Fivetran connector connection."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}/test"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"Connector test initiated")
        return True
    else:
        print(f"Error testing connector: {response.status_code}")
        print(response.text)
        return False

def check_test_status(api_key, api_secret, connector_id):
    """Check the status of the connector test."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    max_attempts = 10
    for attempt in range(max_attempts):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            status = response.json()['data']['status']['setup_state']
            if status == 'connected':
                print(f"Connector test successful")
                return True
            elif status in ['failed', 'error']:
                print(f"Connector test failed: {status}")
                return False
            else:
                print(f"Connector test in progress: {status}")
                time.sleep(5)
        else:
            print(f"Error checking connector status: {response.status_code}")
            print(response.text)
            return False
    
    print("Connector test timed out")
    return False

def configure_schema(api_key, api_secret, connector_id, schema_name):
    """Configure the schema for the connector."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}/schema"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    # First, get the current schema
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error getting schema: {response.status_code}")
        print(response.text)
        return False
    
    schema_data = response.json()['data']['schema']
    
    # Enable all tables and columns
    for table_name, table_data in schema_data.items():
        table_data['enabled'] = True
        for column_name, column_data in table_data['columns'].items():
            column_data['enabled'] = True
    
    # Update the schema
    payload = {
        "schema": schema_data,
        "schema_name": schema_name
    }
    
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Schema configured successfully")
        return True
    else:
        print(f"Error configuring schema: {response.status_code}")
        print(response.text)
        return False

def set_destination(api_key, api_secret, connector_id, destination_id):
    """Set the destination for the connector."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    payload = {
        "destination_id": destination_id
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Destination set successfully")
        return True
    else:
        print(f"Error setting destination: {response.status_code}")
        print(response.text)
        return False

def set_sync_schedule(api_key, api_secret, connector_id, sync_frequency='60'):
    """Set the sync schedule for the connector."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    payload = {
        "schedule_type": "auto",
        "paused": False,
        "sync_frequency": sync_frequency
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Sync schedule set successfully")
        return True
    else:
        print(f"Error setting sync schedule: {response.status_code}")
        print(response.text)
        return False

def list_destinations(api_key, api_secret, group_id):
    """List available destinations in the group."""
    url = f"https://api.fivetran.com/v1/groups/{group_id}/destinations"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        destinations = response.json()['data']['items']
        print("\nAvailable destinations:")
        for dest in destinations:
            print(f"ID: {dest['id']}, Name: {dest['name']}, Service: {dest['service']}")
        return destinations
    else:
        print(f"Error listing destinations: {response.status_code}")
        print(response.text)
        return []

def list_groups(api_key, api_secret):
    """List available groups."""
    url = "https://api.fivetran.com/v1/groups"
    headers = get_fivetran_auth_header(api_key, api_secret)
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        groups = response.json()['data']['items']
        print("\nAvailable groups:")
        for group in groups:
            print(f"ID: {group['id']}, Name: {group['name']}")
        return groups
    else:
        print(f"Error listing groups: {response.status_code}")
        print(response.text)
        return []

def interactive_setup():
    """Interactive setup process."""
    config = {}
    
    # Get API credentials
    config['api_key'] = input("Enter Fivetran API key: ")
    config['api_secret'] = input("Enter Fivetran API secret: ")
    
    # List groups and get group ID
    groups = list_groups(config['api_key'], config['api_secret'])
    if groups:
        group_idx = int(input("\nEnter the number of the group to use (0-based index): "))
        config['group_id'] = groups[group_idx]['id']
    else:
        config['group_id'] = input("Enter Fivetran group ID: ")
    
    # List destinations and get destination ID
    destinations = list_destinations(config['api_key'], config['api_secret'], config['group_id'])
    if destinations:
        dest_idx = int(input("\nEnter the number of the destination to use (0-based index): "))
        config['destination_id'] = destinations[dest_idx]['id']
    else:
        config['destination_id'] = input("Enter Fivetran destination ID: ")
    
    # Get Lambda ARN
    lambda_arn = get_aws_lambda_arn()
    if lambda_arn:
        print(f"Found Lambda ARN: {lambda_arn}")
        config['lambda_arn'] = lambda_arn
    else:
        config['lambda_arn'] = input("Enter AWS Lambda function ARN: ")
    
    # Get AWS region
    config['aws_region'] = input("Enter AWS region (default: eu-central-1): ") or "eu-central-1"
    
    # Get ProHandel credentials
    config['prohandel_username'] = input("Enter ProHandel username: ")
    config['prohandel_password'] = input("Enter ProHandel password: ")
    config['prohandel_auth_url'] = input("Enter ProHandel auth URL (default: https://auth.prohandel.cloud/api/v4): ") or "https://auth.prohandel.cloud/api/v4"
    config['prohandel_api_url'] = input("Enter ProHandel API URL (default: https://api.prohandel.de/api/v2): ") or "https://api.prohandel.de/api/v2"
    
    # Get schema name
    config['schema_name'] = input("Enter schema name (default: prohandel_data): ") or "prohandel_data"
    
    # Save config
    save_config = input("Save this configuration for future use? (y/n): ").lower()
    if save_config == 'y':
        config_path = input("Enter config file path (default: fivetran_config.json): ") or "fivetran_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_path}")
    
    return config

def main():
    """Main function."""
    args = parse_args()
    
    # Load config from file or interactive setup
    if args.config:
        config = load_config(args.config)
    elif all([args.api_key, args.api_secret, args.group_id, args.lambda_arn, 
              args.prohandel_username, args.prohandel_password, args.destination_id]):
        config = vars(args)
    else:
        print("Starting interactive setup...")
        config = interactive_setup()
    
    print("\n=== Fivetran Connector Setup ===\n")
    
    # Create connector
    connector_name = f"ProHandel Data {datetime.now().strftime('%Y-%m-%d')}"
    print(f"Creating connector: {connector_name}")
    connector_id = create_connector(config['api_key'], config['api_secret'], config['group_id'], connector_name)
    if not connector_id:
        sys.exit(1)
    
    # Configure connector
    print("\nConfiguring connector...")
    if not configure_connector(
        config['api_key'], config['api_secret'], connector_id, config['lambda_arn'],
        config['aws_region'], config['prohandel_username'], config['prohandel_password'],
        config['prohandel_auth_url'], config['prohandel_api_url']):
        sys.exit(1)
    
    # Test connector
    print("\nTesting connector...")
    if not test_connector(config['api_key'], config['api_secret'], connector_id):
        sys.exit(1)
    
    # Check test status
    print("\nChecking test status...")
    if not check_test_status(config['api_key'], config['api_secret'], connector_id):
        sys.exit(1)
    
    # Configure schema
    print("\nConfiguring schema...")
    if not configure_schema(config['api_key'], config['api_secret'], connector_id, config['schema_name']):
        sys.exit(1)
    
    # Set destination
    print("\nSetting destination...")
    if not set_destination(config['api_key'], config['api_secret'], connector_id, config['destination_id']):
        sys.exit(1)
    
    # Set sync schedule
    print("\nSetting sync schedule (hourly)...")
    if not set_sync_schedule(config['api_key'], config['api_secret'], connector_id, '60'):
        sys.exit(1)
    
    print("\n=== Fivetran Connector Setup Complete ===")
    print(f"Connector ID: {connector_id}")
    print("Initial sync has been started.")
    print("You can monitor the sync status in the Fivetran dashboard.")
    print("Or use the monitor_sync.py script to monitor the sync process.")

if __name__ == "__main__":
    main()

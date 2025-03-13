#!/usr/bin/env python3
"""
Setup Fivetran Connector

This script sets up a Fivetran connector for the ProHandel Lambda function.
"""

import requests
import json
import time
import subprocess
from base64 import b64encode
from datetime import datetime
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Fivetran API credentials
API_KEY = "eWMMoSTR8ijWdw2u"
API_SECRET = "5hsGtNOxT5FkQYaTDZnzYmyAmhqmXBuR"
GROUP_ID = "look_frescoes"  # From the previous script output

# ProHandel credentials from .env file
PROHANDEL_API_KEY = "7e7c639358434c4fa215d4e3978739d0"
PROHANDEL_API_SECRET = "1cjnuux79d"
PROHANDEL_AUTH_URL = "https://auth.prohandel.cloud/api/v4"
PROHANDEL_API_URL = "https://api.prohandel.de/api/v2"

# AWS Lambda details
AWS_REGION = "eu-central-1"
LAMBDA_ARN = "arn:aws:lambda:eu-central-1:689864027744:function:prohandel-connector"  # From memory

def get_auth_header():
    """Create Fivetran API authentication header."""
    auth_string = f"{API_KEY}:{API_SECRET}"
    encoded_auth = b64encode(auth_string.encode('utf-8')).decode('utf-8')
    return {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json'
    }

def get_aws_lambda_arn():
    """Get AWS Lambda ARN using AWS CLI."""
    try:
        cmd = [
            'aws', 'lambda', 'list-functions',
            '--region', AWS_REGION,
            '--query', 'Functions[?starts_with(FunctionName, `prohandel`)].FunctionArn',
            '--output', 'text'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        arn = result.stdout.strip()
        if arn:
            print(f"Found Lambda ARN: {arn}")
            return arn
        else:
            print("No Lambda function with 'prohandel' in the name found.")
            return None
    except Exception as e:
        print(f"Error getting Lambda ARN: {e}")
        return None

def create_connector(connector_name):
    """Create a new Fivetran connector."""
    url = "https://api.fivetran.com/v1/connectors"
    headers = get_auth_header()
    
    payload = {
        "service": "aws_lambda",
        "group_id": GROUP_ID,
        "paused": True,
        "trust_certificates": True,
        "trust_fingerprints": True,
        "run_setup_tests": False,
        "schema": "prohandel_data",
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

def configure_connector(connector_id, lambda_arn):
    """Configure the Fivetran connector with AWS Lambda details and secrets."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
    headers = get_auth_header()
    
    payload = {
        "config": {
            "function_arn": lambda_arn,
            "region": AWS_REGION,
            "execution_timeout": 180,
            "secrets": {
                "PROHANDEL_API_KEY": PROHANDEL_API_KEY,
                "PROHANDEL_API_SECRET": PROHANDEL_API_SECRET,
                "PROHANDEL_AUTH_URL": PROHANDEL_AUTH_URL,
                "PROHANDEL_API_URL": PROHANDEL_API_URL
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

def test_connector(connector_id):
    """Test the Fivetran connector connection."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}/test"
    headers = get_auth_header()
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"Connector test initiated")
        return True
    else:
        print(f"Error testing connector: {response.status_code}")
        print(response.text)
        return False

def check_test_status(connector_id):
    """Check the status of the connector test."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
    headers = get_auth_header()
    
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

def configure_schema(connector_id, schema_name="prohandel_data"):
    """Configure the schema for the connector."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}/schema"
    headers = get_auth_header()
    
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

def set_sync_schedule(connector_id, sync_frequency='60'):
    """Set the sync schedule for the connector."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
    headers = get_auth_header()
    
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

def main():
    """Main function."""
    print("\n=== Fivetran Connector Setup ===\n")
    
    # Check if we need to find the Lambda ARN
    global LAMBDA_ARN
    if not LAMBDA_ARN:
        LAMBDA_ARN = get_aws_lambda_arn()
        if not LAMBDA_ARN:
            LAMBDA_ARN = input("Enter your AWS Lambda function ARN: ")
    
    # Create connector
    connector_name = f"ProHandel Data {datetime.now().strftime('%Y-%m-%d')}"
    print(f"Creating connector: {connector_name}")
    connector_id = create_connector(connector_name)
    if not connector_id:
        print("Failed to create connector. Exiting.")
        return
    
    # Configure connector
    print("\nConfiguring connector...")
    if not configure_connector(connector_id, LAMBDA_ARN):
        print("Failed to configure connector. Exiting.")
        return
    
    # Test connector
    print("\nTesting connector...")
    if not test_connector(connector_id):
        print("Failed to test connector. Exiting.")
        return
    
    # Check test status
    print("\nChecking test status...")
    if not check_test_status(connector_id):
        print("Connector test failed. Exiting.")
        return
    
    # Configure schema
    print("\nConfiguring schema...")
    if not configure_schema(connector_id):
        print("Failed to configure schema. Exiting.")
        return
    
    # Set sync schedule
    print("\nSetting sync schedule (hourly)...")
    if not set_sync_schedule(connector_id):
        print("Failed to set sync schedule. Exiting.")
        return
    
    print("\n=== Fivetran Connector Setup Complete ===")
    print(f"Connector ID: {connector_id}")
    print("Initial sync has been started.")
    print("You can monitor the sync status in the Fivetran dashboard.")
    print("Or use the monitor_sync.py script to monitor the sync process.")

if __name__ == "__main__":
    main()

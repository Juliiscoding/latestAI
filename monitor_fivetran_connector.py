#!/usr/bin/env python3
"""
Monitor Fivetran Connector

This script monitors a Fivetran connector and runs data quality checks.
"""

import requests
import json
import time
import subprocess
from base64 import b64encode
from datetime import datetime

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

def monitor_connector(connector_id):
    """Monitor the Fivetran connector sync status."""
    url = f"https://api.fivetran.com/v1/connectors/{connector_id}"
    headers = get_auth_header()
    
    print(f"\n=== Monitoring Connector {connector_id} ===")
    
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            status = data['status']
            
            # Print connector status
            print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Setup State: {status['setup_state']}")
            print(f"Sync State: {status['sync_state']}")
            
            # If we have sync details, print them
            if 'sync_details' in data and data['sync_details']:
                sync_details = data['sync_details']
                print(f"Sync Start Time: {sync_details.get('start_time', 'N/A')}")
                print(f"Sync End Time: {sync_details.get('end_time', 'N/A')}")
                print(f"Sync Status: {sync_details.get('status', 'N/A')}")
                
                # If we have table details, print them
                if 'tables' in sync_details and sync_details['tables']:
                    print("\nTable Sync Status:")
                    for table, table_details in sync_details['tables'].items():
                        print(f"  {table}: {table_details.get('status', 'N/A')}")
                        if 'records_synced' in table_details:
                            print(f"    Records Synced: {table_details['records_synced']}")
            
            # If sync is complete, break the loop
            if status['sync_state'] == 'completed':
                print("\nSync completed successfully!")
                break
            elif status['sync_state'] in ['failed', 'error']:
                print("\nSync failed!")
                break
            
            # Wait for 30 seconds before checking again
            print("\nWaiting 30 seconds before checking again...")
            time.sleep(30)
        else:
            print(f"Error monitoring connector: {response.status_code}")
            print(response.text)
            break

def run_data_quality_checks():
    """Run data quality checks."""
    print("\n=== Running Data Quality Checks ===")
    try:
        cmd = ['python', 'data_quality_monitor.py', '--config', 'data_quality_config.json']
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running data quality checks: {e}")
        return False

def run_dbt_models():
    """Run dbt models."""
    print("\n=== Running dbt Models ===")
    try:
        cmd = ['./run_dbt_models.sh']
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running dbt models: {e}")
        return False

def main():
    """Main function."""
    print("=== Fivetran Connector Monitoring ===")
    
    # Get group ID
    group_id = input("Enter your Fivetran group ID (default: look_frescoes): ") or "look_frescoes"
    
    # List connectors
    connectors = list_connectors(group_id)
    if not connectors:
        print("No connectors found. Exiting.")
        return
    
    # Select connector
    connector_idx = int(input("\nEnter the number of the connector to monitor (0-based index): "))
    connector_id = connectors[connector_idx]['id']
    
    # Monitor connector
    monitor_connector(connector_id)
    
    # Run data quality checks
    run_data_quality_checks_input = input("\nDo you want to run data quality checks? (y/n): ")
    if run_data_quality_checks_input.lower() == 'y':
        run_data_quality_checks()
    
    # Run dbt models
    run_dbt_models_input = input("\nDo you want to run dbt models? (y/n): ")
    if run_dbt_models_input.lower() == 'y':
        run_dbt_models()
    
    print("\n=== Monitoring Complete ===")

if __name__ == "__main__":
    main()

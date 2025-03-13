#!/usr/bin/env python3
"""
Script to set up Fivetran integration with Snowflake.
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv(override=True)
    
    # Get Fivetran API credentials
    api_key = os.getenv("FIVETRAN_API_KEY")
    api_secret = os.getenv("FIVETRAN_API_SECRET")
    
    if not api_key or not api_secret:
        print("Error: Fivetran API credentials not found in .env file")
        sys.exit(1)
    
    # Get Snowflake credentials
    snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
    snowflake_user = os.getenv("SNOWFLAKE_USERNAME")
    snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
    snowflake_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    snowflake_database = os.getenv("SNOWFLAKE_DATABASE")
    snowflake_role = os.getenv("SNOWFLAKE_ROLE")
    snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA", "RAW")  # Default to RAW for Fivetran
    
    # Base URL for Fivetran API
    base_url = "https://api.fivetran.com/v1"
    
    # Authentication for API requests
    auth = (api_key, api_secret)
    
    # Step 1: List all connectors to check if PostgreSQL connector exists
    print("Checking existing connectors...")
    connectors_url = f"{base_url}/connectors"
    response = requests.get(connectors_url, auth=auth)
    
    if response.status_code != 200:
        print(f"Error fetching connectors: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    connectors = response.json()
    print(f"Found {len(connectors.get('data', {}).get('items', []))} connectors")
    
    # Step 2: List all destinations to check if Snowflake destination exists
    print("\nChecking existing destinations...")
    destinations_url = f"{base_url}/destinations"
    response = requests.get(destinations_url, auth=auth)
    
    if response.status_code != 200:
        print(f"Error fetching destinations: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    destinations = response.json()
    destination_items = destinations.get('data', {}).get('items', [])
    print(f"Found {len(destination_items)} destinations")
    
    # Check if Snowflake destination already exists
    snowflake_destination = None
    for dest in destination_items:
        if dest.get('service') == 'snowflake':
            snowflake_destination = dest
            print(f"Found existing Snowflake destination: {dest.get('id')} - {dest.get('name')}")
            break
    
    # Step 3: Create Snowflake destination if it doesn't exist
    if not snowflake_destination:
        print("\nCreating new Snowflake destination...")
        create_destination_url = f"{base_url}/destinations"
        destination_data = {
            "service": "snowflake",
            "name": "Mercurios Snowflake",
            "config": {
                "host": f"{snowflake_account}.snowflakecomputing.com",
                "port": "443",
                "user": snowflake_user,
                "password": snowflake_password,
                "database": snowflake_database,
                "schema": snowflake_schema,
                "warehouse": snowflake_warehouse,
                "role": snowflake_role
            },
            "run_setup_tests": True
        }
        
        response = requests.post(create_destination_url, auth=auth, json=destination_data)
        
        if response.status_code != 201:
            print(f"Error creating Snowflake destination: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        snowflake_destination = response.json().get('data')
        print(f"Successfully created Snowflake destination: {snowflake_destination.get('id')}")
    
    # Step 4: Create PostgreSQL connector if it doesn't exist
    print("\nWould you like to set up a PostgreSQL connector? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        print("Enter PostgreSQL connection details:")
        pg_host = input("Host: ")
        pg_port = input("Port (default 5432): ") or "5432"
        pg_database = input("Database: ")
        pg_user = input("Username: ")
        pg_password = input("Password: ")
        pg_schema = input("Schema (default public): ") or "public"
        connector_name = input("Connector name: ") or "PostgreSQL Connector"
        
        print("\nCreating new PostgreSQL connector...")
        create_connector_url = f"{base_url}/connectors"
        connector_data = {
            "service": "postgres",
            "name": connector_name,
            "destination_id": snowflake_destination.get('id'),
            "config": {
                "host": pg_host,
                "port": pg_port,
                "database": pg_database,
                "user": pg_user,
                "password": pg_password,
                "schema": pg_schema,
                "sync_mode": "COLUMNS"  # Based on your preference in MEMORY
            },
            "run_setup_tests": True
        }
        
        response = requests.post(create_connector_url, auth=auth, json=connector_data)
        
        if response.status_code != 201:
            print(f"Error creating PostgreSQL connector: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        connector = response.json().get('data')
        print(f"Successfully created PostgreSQL connector: {connector.get('id')}")
    
    print("\nSetup complete. Please check the Fivetran dashboard for connector status.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fivetran API Client
This script provides functions to interact with the Fivetran API
"""

import requests
import json
import base64
import time
from datetime import datetime

class FivetranClient:
    """Client for interacting with the Fivetran API"""
    
    def __init__(self, api_key, api_secret):
        """Initialize the client with API credentials"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.fivetran.com/v1"
        self.auth_header = self._get_auth_header()
    
    def _get_auth_header(self):
        """Get the authorization header for API requests"""
        auth_string = f"{self.api_key}:{self.api_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}
    
    def get_connectors(self):
        """Get all connectors"""
        url = f"{self.base_url}/connectors"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting connectors: {response.status_code}")
            print(response.text)
            return None
    
    def get_connector(self, connector_id):
        """Get a specific connector by ID"""
        url = f"{self.base_url}/connectors/{connector_id}"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting connector {connector_id}: {response.status_code}")
            print(response.text)
            return None
    
    def get_connector_sync_status(self, connector_id):
        """Get the sync status of a connector"""
        connector_data = self.get_connector(connector_id)
        
        if connector_data and "data" in connector_data:
            return connector_data["data"]["status"]["sync_state"]
        else:
            return None
    
    def get_groups(self):
        """Get all groups"""
        url = f"{self.base_url}/groups"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting groups: {response.status_code}")
            print(response.text)
            return None
    
    def get_group(self, group_id):
        """Get a specific group by ID"""
        url = f"{self.base_url}/groups/{group_id}"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting group {group_id}: {response.status_code}")
            print(response.text)
            return None
    
    def get_group_connectors(self, group_id):
        """Get all connectors in a group"""
        url = f"{self.base_url}/groups/{group_id}/connectors"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting connectors for group {group_id}: {response.status_code}")
            print(response.text)
            return None
    
    def get_destinations(self):
        """Get all destinations"""
        url = f"{self.base_url}/destinations"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting destinations: {response.status_code}")
            print(response.text)
            return None
    
    def get_destination(self, destination_id):
        """Get a specific destination by ID"""
        url = f"{self.base_url}/destinations/{destination_id}"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting destination {destination_id}: {response.status_code}")
            print(response.text)
            return None
    
    def get_transformations(self, destination_id):
        """Get all transformations for a destination"""
        url = f"{self.base_url}/destinations/{destination_id}/transformations"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting transformations for destination {destination_id}: {response.status_code}")
            print(response.text)
            return None
    
    def get_transformation(self, transformation_id):
        """Get a specific transformation by ID"""
        url = f"{self.base_url}/transformations/{transformation_id}"
        response = requests.get(url, headers=self.auth_header)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting transformation {transformation_id}: {response.status_code}")
            print(response.text)
            return None
    
    def get_transformation_status(self, transformation_id):
        """Get the status of a transformation"""
        transformation_data = self.get_transformation(transformation_id)
        
        if transformation_data and "data" in transformation_data:
            return transformation_data["data"]["status"]
        else:
            return None
    
    def monitor_transformation_until_complete(self, transformation_id, max_attempts=30, interval=60):
        """Monitor a transformation until it completes or fails"""
        print(f"Monitoring transformation {transformation_id}...")
        print("Press Ctrl+C to stop monitoring")
        
        attempt = 0
        
        try:
            while attempt < max_attempts:
                attempt += 1
                
                status = self.get_transformation_status(transformation_id)
                
                if status:
                    print(f"{datetime.now()} - Transformation status: {status}")
                    
                    if status == "SUCCEEDED":
                        print("Transformation completed successfully!")
                        return True
                    elif status == "FAILED":
                        print("Transformation failed!")
                        return False
                else:
                    print(f"{datetime.now()} - Could not get transformation status")
                
                print(f"Checking again in {interval} seconds... (attempt {attempt}/{max_attempts})")
                time.sleep(interval)
            
            print("Maximum monitoring time reached. Exiting.")
            return False
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            return False

def main():
    """Main function"""
    # Load Fivetran API config
    try:
        with open('fivetran_api_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("fivetran_api_config.json not found. Please create this file with your API key and secret.")
        print("Example:")
        print("""
        {
            "api_key": "your_api_key",
            "api_secret": "your_api_secret"
        }
        """)
        return
    
    client = FivetranClient(config['api_key'], config['api_secret'])
    
    # Get all connectors
    connectors = client.get_connectors()
    
    if connectors and "data" in connectors and "items" in connectors["data"]:
        print(f"Found {len(connectors['data']['items'])} connectors:")
        for connector in connectors["data"]["items"]:
            print(f"- {connector['name']} ({connector['id']}): {connector['status']['sync_state']}")
    else:
        print("No connectors found or error getting connectors.")
    
    # Get all destinations
    destinations = client.get_destinations()
    
    if destinations and "data" in destinations and "items" in destinations["data"]:
        print(f"\nFound {len(destinations['data']['items'])} destinations:")
        for destination in destinations["data"]["items"]:
            print(f"- {destination['name']} ({destination['id']})")
            
            # Get transformations for this destination
            transformations = client.get_transformations(destination['id'])
            
            if transformations and "data" in transformations and "items" in transformations["data"]:
                print(f"  Found {len(transformations['data']['items'])} transformations:")
                for transformation in transformations["data"]["items"]:
                    print(f"  - {transformation['name']} ({transformation['id']}): {transformation['status']}")
            else:
                print("  No transformations found for this destination.")
    else:
        print("No destinations found or error getting destinations.")

if __name__ == "__main__":
    main()

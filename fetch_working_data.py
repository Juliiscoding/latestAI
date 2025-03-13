import json
import os
import requests
from datetime import datetime, timedelta

def fetch_data_from_endpoint(endpoint, api_key="7e7c639358434c4fa215d4e3978739d0", api_secret="1cjnuux79d"):
    """Fetch data from a specific endpoint"""
    # Authenticate
    auth_url = "https://auth.prohandel.cloud/api/v4/token"
    auth_data = {
        "apiKey": api_key,
        "secret": api_secret
    }
    
    auth_response = requests.post(auth_url, json=auth_data)
    auth_response.raise_for_status()
    token = auth_response.json()["token"]["token"]["value"]
    
    # Make request to endpoint
    api_url = f"https://linde.prohandel.de/api/v2/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": "v2.29.1"
    }
    
    params = {"page": 1, "pagesize": 100}  # Limit to 100 items for analysis
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()

def fetch_and_save_all_data():
    """Fetch data from all working endpoints and save to JSON files"""
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # List of working endpoints
    endpoints = [
        "article",
        "customer",
        "order",
        "sale",
        "inventory",
        "customercard",
        "supplier",
        "branch",
        "category",
        "voucher",
        "invoice",
        "payment"
    ]
    
    # Fetch and save data from each endpoint
    for endpoint in endpoints:
        print(f"Fetching {endpoint} data...")
        try:
            data = fetch_data_from_endpoint(endpoint)
            with open(f"{data_dir}/{endpoint}.json", "w") as f:
                json.dump(data, f, indent=2)
            print(f"✓ Saved {len(data)} {endpoint} items")
        except Exception as e:
            print(f"✗ Error fetching {endpoint}: {str(e)}")
    
    print("\nData fetching complete!")

if __name__ == "__main__":
    fetch_and_save_all_data()

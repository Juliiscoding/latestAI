import json
import os
from pprint import pprint
import pandas as pd
from datetime import datetime

def analyze_data_structure():
    """Analyze the structure of data from each endpoint"""
    data_dir = "data"
    
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
    
    # Analyze each endpoint's data
    for endpoint in endpoints:
        file_path = f"{data_dir}/{endpoint}.json"
        if not os.path.exists(file_path):
            print(f"No data file found for {endpoint}")
            continue
            
        with open(file_path, "r") as f:
            data = json.load(f)
        
        if not data:
            print(f"\n{endpoint.upper()}: No data available")
            continue
            
        print(f"\n{endpoint.upper()} ({len(data)} items):")
        
        # Get a sample item
        sample = data[0] if data else {}
        
        # Print the keys and their types
        print("Fields:")
        for key, value in sample.items():
            value_type = type(value).__name__
            if isinstance(value, dict) and value:
                nested_keys = list(value.keys())
                print(f"  {key} ({value_type}): {nested_keys}")
            elif isinstance(value, list) and value:
                item_type = type(value[0]).__name__ if value else "unknown"
                print(f"  {key} ({value_type} of {item_type}): {len(value)} items")
            else:
                print(f"  {key} ({value_type}): {value}")

def create_data_summary():
    """Create a summary of the data from each endpoint"""
    data_dir = "data"
    
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
    
    summary = {}
    
    # Analyze each endpoint's data
    for endpoint in endpoints:
        file_path = f"{data_dir}/{endpoint}.json"
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, "r") as f:
            data = json.load(f)
        
        if not data:
            continue
            
        # Count items
        summary[endpoint] = {
            "count": len(data),
            "fields": list(data[0].keys()) if data else []
        }
    
    # Print summary
    print("\nDATA SUMMARY:")
    for endpoint, info in summary.items():
        print(f"{endpoint}: {info['count']} items with {len(info['fields'])} fields")

if __name__ == "__main__":
    analyze_data_structure()
    create_data_summary()

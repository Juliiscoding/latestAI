#!/usr/bin/env python3
"""
Script to directly test the ProHandel Lambda function locally
This will help verify if the Lambda function is returning data correctly
and simulate the Fivetran AWS Lambda connector integration
"""

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# Import the Lambda function directly from the current directory
sys.path.insert(0, os.path.dirname(__file__))
from lambda_function import lambda_handler

# Load environment variables
load_dotenv()

def test_connection():
    """Test the connection to the ProHandel API"""
    print("\n=== Testing Connection to ProHandel API ===")
    
    # Create a test event matching Fivetran's AWS Lambda connector format
    # Using the format from our CloudWatch logs
    event = {
        "secrets": {
            "PROHANDEL_API_KEY": os.getenv("PROHANDEL_API_KEY", "7e7c639358434c4fa215d4e3978739d0"),
            "PROHANDEL_API_SECRET": os.getenv("PROHANDEL_API_SECRET", "1cjnuux79d"),
            "PROHANDEL_AUTH_URL": os.getenv("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4"),
            "PROHANDEL_API_URL": os.getenv("PROHANDEL_API_URL", "https://linde.prohandel.de/api/v2")
        },
        "agent": "Fivetran AWS Lambda Connector/armed_unleaded/aws_lambda",
        "sync_id": "test-connection-" + datetime.now().strftime("%Y%m%d%H%M%S")
    }
    
    # Call the Lambda handler
    response = lambda_handler(event, None)
    print(f"Response: {json.dumps(response, indent=2)}")
    
    return response.get("success", False)

def get_schema():
    """Get the schema from the Lambda function"""
    print("\n=== Getting Schema from Lambda Function ===")
    
    # Create a schema event matching Fivetran's AWS Lambda connector format
    # Using the format from our CloudWatch logs but adding schema operation
    event = {
        "operation": "schema",  # Explicitly set operation
        "secrets": {
            "PROHANDEL_API_KEY": os.getenv("PROHANDEL_API_KEY", "7e7c639358434c4fa215d4e3978739d0"),
            "PROHANDEL_API_SECRET": os.getenv("PROHANDEL_API_SECRET", "1cjnuux79d"),
            "PROHANDEL_AUTH_URL": os.getenv("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4"),
            "PROHANDEL_API_URL": os.getenv("PROHANDEL_API_URL", "https://linde.prohandel.de/api/v2")
        },
        "agent": "Fivetran AWS Lambda Connector/armed_unleaded/aws_lambda",
        "sync_id": "schema-request-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "schema": {}
    }
    
    # Call the Lambda handler
    response = lambda_handler(event, None)
    
    # Print the full response for debugging
    print(f"Full schema response: {json.dumps(response, indent=2)}")
    
    # Print the tables in the schema
    if "tables" in response:
        print(f"Found {len(response['tables'])} tables in schema:")
        for table_name in response["tables"].keys():
            print(f"  - {table_name}")
            # Print column details
            columns = response["tables"][table_name].get("columns", {})
            print(f"    Columns: {len(columns)}")
            for col_name, col_type in list(columns.items())[:5]:  # Show first 5 columns
                print(f"      {col_name}: {col_type}")
            if len(columns) > 5:
                print(f"      ... and {len(columns) - 5} more columns")
    else:
        print("No tables found in schema response!")
        if "error" in response:
            print(f"Error: {response['error']}")
    
    return response

def test_sync(entity_type=None):
    """Test syncing data from the ProHandel API"""
    print(f"\n=== Testing Sync for {entity_type if entity_type else 'All Entities'} ===")
    
    # Create a sync event matching the format from CloudWatch logs
    event = {
        "operation": "sync",  # Explicitly set operation
        "secrets": {
            "PROHANDEL_API_KEY": os.getenv("PROHANDEL_API_KEY", "7e7c639358434c4fa215d4e3978739d0"),
            "PROHANDEL_API_SECRET": os.getenv("PROHANDEL_API_SECRET", "1cjnuux79d"),
            "PROHANDEL_AUTH_URL": os.getenv("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4"),
            "PROHANDEL_API_URL": os.getenv("PROHANDEL_API_URL", "https://linde.prohandel.de/api/v2")
        },
        "state": {},  # Start with empty state for full sync
        "agent": "Fivetran AWS Lambda Connector/armed_unleaded/aws_lambda",
        "sync_id": "sync-test-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "limit": 100
    }
    
    # If entity_type is specified, add it to the event
    if entity_type:
        event["table"] = entity_type
    
    # Call the Lambda handler
    response = lambda_handler(event, None)
    
    # Print summary of data returned
    if "insert" in response:
        print("\nData returned:")
        for table, data in response["insert"].items():
            print(f"  - {table}: {len(data)} rows")
            
            # Print sample data (first row) if available
            if data and len(data) > 0:
                print(f"    Sample data (first row):")
                sample = data[0]
                
                # Handle both string and dictionary formats
                if isinstance(sample, dict):
                    # Print at most 5 fields to avoid overwhelming output
                    sample_fields = list(sample.keys())[:5]
                    for field in sample_fields:
                        print(f"      {field}: {sample[field]}")
                    if len(sample.keys()) > 5:
                        print(f"      ... and {len(sample.keys()) - 5} more fields")
                elif isinstance(sample, str):
                    # If it's a string (possibly JSON), print it directly
                    print(f"      {sample[:100]}{'...' if len(sample) > 100 else ''}")
                    print("      (Data returned as string, not as dictionary)")
                else:
                    # For any other type
                    print(f"      Data type: {type(sample).__name__}")
                    print(f"      Value: {str(sample)[:100]}{'...' if len(str(sample)) > 100 else ''}")
    
    # Print state
    if "state" in response:
        print("\nUpdated state:")
        for key, value in response["state"].items():
            print(f"  - {key}: {value}")
    
    return response

def main():
    """Main function"""
    print("=== ProHandel Lambda Function Direct Test ===")
    
    # Test connection
    if not test_connection():
        print("Connection test failed. Exiting.")
        return
    
    # Get schema
    schema = get_schema()
    
    # Test sync for all entities
    print("\nTesting sync for all entities...")
    sync_response = test_sync()
    
    # If no data was returned, test individual entities
    if not sync_response.get("insert") or sum(len(data) for data in sync_response.get("insert", {}).values()) == 0:
        print("\nNo data returned for all entities. Testing individual entities...")
        
        # Test each entity type
        entity_types = [
            "articles", "customers", "orders", "sales", "inventory",
            "suppliers", "branches", "categories", "countries",
            "credits", "currencies", "invoices", "labels",
            "payments", "staff", "vouchers"
        ]
        
        for entity_type in entity_types:
            test_sync(entity_type)
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to test the schema response from the ProHandel Lambda function
This will help verify if the Lambda function is returning the schema correctly for Fivetran
"""

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the enhanced_lambda directory to the path
enhanced_lambda_path = os.path.join(os.path.dirname(__file__), 'enhanced_lambda')
sys.path.insert(0, enhanced_lambda_path)

# Import the Lambda function from enhanced_lambda directory
from enhanced_lambda.lambda_function import lambda_handler

# Load environment variables
load_dotenv()

def test_schema():
    """Test the schema response from the Lambda function"""
    print("\n=== Testing Schema Response from Lambda Function ===")
    
    # Create a schema event
    event = {
        "type": "schema",
        "secrets": {
            "PROHANDEL_API_KEY": os.getenv("PROHANDEL_API_KEY"),
            "PROHANDEL_API_SECRET": os.getenv("PROHANDEL_API_SECRET"),
            "PROHANDEL_AUTH_URL": os.getenv("PROHANDEL_AUTH_URL"),
            "PROHANDEL_API_URL": os.getenv("PROHANDEL_API_URL")
        }
    }
    
    # Call the Lambda handler
    schema = lambda_handler(event, None)
    
    # Check if schema is properly formatted
    if not isinstance(schema, dict):
        print(f"ERROR: Schema is not a dictionary. Type: {type(schema)}")
        return False
    
    print(f"Schema contains {len(schema)} tables:")
    for table_name, table_schema in schema.items():
        print(f"  - {table_name}")
        
        # Check if table schema has required fields
        if "primary_key" not in table_schema:
            print(f"    WARNING: Table {table_name} is missing 'primary_key'")
        
        if "columns" not in table_schema:
            print(f"    ERROR: Table {table_name} is missing 'columns'")
            continue
        
        # Print column information
        columns = table_schema["columns"]
        print(f"    Columns: {len(columns)}")
        
        # Print first 3 columns as examples
        for i, (column_name, column_type) in enumerate(columns.items()):
            if i < 3:
                print(f"      - {column_name}: {column_type}")
        
        if len(columns) > 3:
            print(f"      - ... and {len(columns) - 3} more columns")
    
    # Save schema to file for reference
    with open("schema_output.json", "w") as f:
        json.dump(schema, f, indent=2)
    print(f"\nSchema saved to schema_output.json")
    
    return True

def test_sync_empty():
    """Test the sync response with empty state to see if it returns empty tables"""
    print("\n=== Testing Sync Response with Empty State ===")
    
    # Create a sync event with empty state
    event = {
        "type": "sync",
        "secrets": {
            "PROHANDEL_API_KEY": os.getenv("PROHANDEL_API_KEY"),
            "PROHANDEL_API_SECRET": os.getenv("PROHANDEL_API_SECRET"),
            "PROHANDEL_AUTH_URL": os.getenv("PROHANDEL_AUTH_URL"),
            "PROHANDEL_API_URL": os.getenv("PROHANDEL_API_URL")
        },
        "state": {},
        "limit": 1  # Set limit to 1 to minimize data returned
    }
    
    # Call the Lambda handler
    response = lambda_handler(event, None)
    
    # Check if response is properly formatted
    if not isinstance(response, dict):
        print(f"ERROR: Response is not a dictionary. Type: {type(response)}")
        return False
    
    # Check if response has required fields
    required_fields = ["state", "insert", "delete", "hasMore"]
    for field in required_fields:
        if field not in response:
            print(f"ERROR: Response is missing required field '{field}'")
            return False
    
    # Check if insert data is properly formatted
    insert_data = response["insert"]
    if not isinstance(insert_data, dict):
        print(f"ERROR: Insert data is not a dictionary. Type: {type(insert_data)}")
        return False
    
    # Print insert data information
    print(f"Insert data contains {len(insert_data)} tables:")
    for table_name, rows in insert_data.items():
        print(f"  - {table_name}: {len(rows)} rows")
        
        # Print sample data for first row if available
        if rows and len(rows) > 0:
            print(f"    Sample data (first row):")
            sample = rows[0]
            count = 0
            for key, value in sample.items():
                if count < 5:
                    print(f"      {key}: {value}")
                    count += 1
            if len(sample) > 5:
                print(f"      ... and {len(sample) - 5} more fields")
    
    # Save response to file for reference
    with open("sync_output.json", "w") as f:
        json.dump(response, f, indent=2)
    print(f"\nSync response saved to sync_output.json")
    
    return True

def main():
    """Main function"""
    print("=== ProHandel Lambda Schema Test ===")
    
    # Test schema response
    schema_success = test_schema()
    
    # Test sync response with empty state
    sync_success = test_sync_empty()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Schema test: {'SUCCESS' if schema_success else 'FAILED'}")
    print(f"Sync test: {'SUCCESS' if sync_success else 'FAILED'}")
    
    if schema_success and sync_success:
        print("\nAll tests passed! The Lambda function is returning data in the correct format for Fivetran.")
        print("If Fivetran is still not detecting tables, check the Fivetran connector configuration.")
    else:
        print("\nSome tests failed. Please check the output above for details.")

if __name__ == "__main__":
    main()

"""
Test script for the Lambda function
This script simulates Fivetran requests to test the Lambda function's ability to connect to ProHandel API
"""
import json
import os
import sys
import importlib.util
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up the environment for the Lambda function
os.environ['PROHANDEL_API_KEY'] = os.getenv('PROHANDEL_API_KEY')
os.environ['PROHANDEL_API_SECRET'] = os.getenv('PROHANDEL_API_SECRET')
os.environ['PROHANDEL_AUTH_URL'] = os.getenv('PROHANDEL_AUTH_URL')
os.environ['PROHANDEL_API_URL'] = os.getenv('PROHANDEL_API_URL')

# Add the enhanced_lambda directory to the Python path
enhanced_lambda_dir = os.path.join(os.path.dirname(__file__), 'enhanced_lambda')
sys.path.insert(0, enhanced_lambda_dir)

# Import the lambda function using importlib to avoid import errors
spec = importlib.util.spec_from_file_location(
    "lambda_function", 
    os.path.join(enhanced_lambda_dir, "lambda_function.py")
)
lambda_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_module)
lambda_handler = lambda_module.lambda_handler

def test_connection():
    """Test connection to ProHandel API"""
    print("\n=== Testing Connection to ProHandel API ===")
    
    # Create a test event
    event = {
        "type": "test"
    }
    
    # Call the lambda handler
    response = lambda_handler(event, None)
    
    print(f"Response: {json.dumps(response, indent=2)}")
    return response["success"]

def test_schema():
    """Test schema retrieval"""
    print("\n=== Testing Schema Retrieval ===")
    
    # Create a schema event
    event = {
        "schema": True
    }
    
    # Call the lambda handler
    response = lambda_handler(event, None)
    
    # Print table names from schema
    if "tables" in response:
        print(f"Schema contains {len(response['tables'])} tables:")
        for table_name in response["tables"].keys():
            print(f"  - {table_name}")
    
    return "tables" in response

def test_sync(entity_type=None):
    """Test data synchronization for a specific entity type or all entities"""
    if entity_type:
        print(f"\n=== Testing Sync for {entity_type.upper()} ===")
    else:
        print("\n=== Testing Sync for ALL Entities ===")
    
    # Create a sync event
    event = {
        "table": entity_type if entity_type else "all",
        "state": {},
        "limit": 5
    }
    
    # Call the lambda handler
    response = lambda_handler(event, None)
    
    # Print summary of inserted data
    if "insert" in response:
        print("Inserted data summary:")
        for table, data in response["insert"].items():
            print(f"  - {table}: {len(data)} rows")
    
    # Print new state
    if "state" in response:
        print(f"Updated state: {json.dumps(response['state'], indent=2)}")
    
    return "insert" in response and len(response["insert"]) > 0

def main():
    """Main function to run all tests"""
    # Test connection
    connection_success = test_connection()
    if not connection_success:
        print("❌ Connection test failed. Stopping further tests.")
        return
    
    print("✅ Connection test successful!")
    
    # Test schema
    schema_success = test_schema()
    if not schema_success:
        print("❌ Schema test failed. Stopping further tests.")
        return
    
    print("✅ Schema test successful!")
    
    # Test sync for all entities
    sync_success = test_sync()
    if not sync_success:
        print("❌ Sync test failed.")
        return
    
    print("✅ Sync test successful!")
    
    print("\n=== All tests completed successfully! ===")
    print("The Lambda function is correctly configured to retrieve data from ProHandel API.")
    print("Fivetran should now be able to successfully sync data to Snowflake.")

if __name__ == "__main__":
    main()

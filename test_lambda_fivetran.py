#!/usr/bin/env python3
"""
Test Lambda Function with Fivetran Test Request
This script tests the Lambda function with a proper Fivetran test request
"""

import boto3
import json
import time

def test_lambda_fivetran():
    """Test the Lambda function with a Fivetran test request"""
    print("Testing Lambda function with Fivetran test request...")
    
    # Lambda function details
    region = "eu-central-1"
    function_name = "prohandel-fivetran-connector"
    
    try:
        # Create a Lambda client
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Create a test event that mimics a Fivetran test request
        test_event = {
            "agent": "fivetran",
            "state": {},
            "secrets": {
                "PROHANDEL_API_KEY": "7e7c639358434c4fa215d4e3978739d0",
                "PROHANDEL_API_SECRET": "1cjnuux79d",
                "PROHANDEL_AUTH_URL": "https://auth.prohandel.cloud/api/v4",
                "PROHANDEL_API_URL": "https://api.prohandel.de/api/v2"
            },
            "operation": "test"
        }
        
        print(f"Invoking Lambda function with test event...")
        print(f"Event: {json.dumps(test_event, indent=2)}")
        
        # Invoke the function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        # Parse the response
        payload = json.loads(response['Payload'].read().decode())
        
        print(f"\nResponse:")
        print(f"Status Code: {response['StatusCode']}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Check if the test was successful
        if response['StatusCode'] == 200:
            if payload.get('success') == True:
                print(f"\n✅ Lambda function test successful")
            else:
                print(f"\n❌ Lambda function test failed")
                print(f"Error: {payload.get('message', 'Unknown error')}")
        else:
            print(f"\n❌ Lambda function invocation failed with status code {response['StatusCode']}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error testing Lambda function: {e}")
        return False

def test_schema_request():
    """Test the Lambda function with a Fivetran schema request"""
    print("\nTesting Lambda function with Fivetran schema request...")
    
    # Lambda function details
    region = "eu-central-1"
    function_name = "prohandel-fivetran-connector"
    
    try:
        # Create a Lambda client
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Create a test event that mimics a Fivetran schema request
        test_event = {
            "agent": "fivetran",
            "state": {},
            "secrets": {
                "PROHANDEL_API_KEY": "7e7c639358434c4fa215d4e3978739d0",
                "PROHANDEL_API_SECRET": "1cjnuux79d",
                "PROHANDEL_AUTH_URL": "https://auth.prohandel.cloud/api/v4",
                "PROHANDEL_API_URL": "https://api.prohandel.de/api/v2"
            },
            "operation": "schema"
        }
        
        print(f"Invoking Lambda function with schema event...")
        print(f"Event: {json.dumps(test_event, indent=2)}")
        
        # Invoke the function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        # Parse the response
        payload = json.loads(response['Payload'].read().decode())
        
        print(f"\nResponse:")
        print(f"Status Code: {response['StatusCode']}")
        
        # Check if the schema request was successful
        if response['StatusCode'] == 200:
            if 'schema' in payload:
                print(f"\n✅ Lambda function schema request successful")
                print(f"Schema contains {len(payload['schema'])} tables")
                
                # Print table names
                print(f"\nTables:")
                for table_name in payload['schema']:
                    print(f"- {table_name}")
                    
                    # Print column count for each table
                    column_count = len(payload['schema'][table_name]['columns'])
                    print(f"  {column_count} columns")
            else:
                print(f"\n❌ Lambda function schema request failed")
                print(f"Error: {payload.get('message', 'Unknown error')}")
        else:
            print(f"\n❌ Lambda function invocation failed with status code {response['StatusCode']}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error testing Lambda function schema request: {e}")
        return False

if __name__ == "__main__":
    test_lambda_fivetran()
    time.sleep(1)  # Wait a second between requests
    test_schema_request()

#!/usr/bin/env python3
"""
Check if the Lambda function exists and is properly configured.
"""

import boto3
import json
import sys

# AWS Region
REGION = "eu-central-1"

def check_lambda_function(function_name):
    """Check if the Lambda function exists and print its configuration."""
    try:
        # Create a Lambda client
        lambda_client = boto3.client('lambda', region_name=REGION)
        
        # Get function details
        response = lambda_client.get_function(FunctionName=function_name)
        
        print(f"✅ Function {function_name} exists!")
        print("\nFunction Configuration:")
        config = response['Configuration']
        print(f"  Runtime: {config.get('Runtime')}")
        print(f"  Handler: {config.get('Handler')}")
        print(f"  Role: {config.get('Role')}")
        print(f"  Last Modified: {config.get('LastModified')}")
        print(f"  Timeout: {config.get('Timeout')} seconds")
        print(f"  Memory Size: {config.get('MemorySize')} MB")
        
        # Check environment variables
        if 'Environment' in config and 'Variables' in config['Environment']:
            env_vars = config['Environment']['Variables']
            print("\nEnvironment Variables:")
            for key, value in env_vars.items():
                # Mask sensitive values
                if 'key' in key.lower() or 'secret' in key.lower() or 'password' in key.lower():
                    print(f"  {key}: ********")
                else:
                    print(f"  {key}: {value}")
        
        # List function aliases
        aliases = lambda_client.list_aliases(FunctionName=function_name)
        if aliases['Aliases']:
            print("\nAliases:")
            for alias in aliases['Aliases']:
                print(f"  {alias['Name']}: points to version {alias['FunctionVersion']}")
        
        # List function versions
        versions = lambda_client.list_versions_by_function(FunctionName=function_name)
        if versions['Versions']:
            print("\nVersions:")
            for version in versions['Versions']:
                print(f"  Version: {version['Version']}, Last Modified: {version['LastModified']}")
        
        # Test invoke the function with a simple payload
        print("\nTesting function invocation...")
        test_payload = {
            "operation": "test"
        }
        try:
            invoke_response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(test_payload)
            )
            status_code = invoke_response['StatusCode']
            payload = json.loads(invoke_response['Payload'].read().decode('utf-8'))
            
            print(f"  Invocation Status Code: {status_code}")
            print(f"  Response Payload: {json.dumps(payload, indent=2)}")
            
            if status_code == 200:
                print("✅ Function invocation successful!")
            else:
                print("❌ Function invocation returned a non-200 status code.")
        except Exception as e:
            print(f"❌ Error invoking function: {e}")
        
        return True
    
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"❌ Function {function_name} does not exist in region {REGION}!")
        return False
    
    except Exception as e:
        print(f"❌ Error checking function: {e}")
        return False

def list_lambda_functions():
    """List all Lambda functions in the account."""
    try:
        # Create a Lambda client
        lambda_client = boto3.client('lambda', region_name=REGION)
        
        # List functions
        response = lambda_client.list_functions()
        
        print(f"Found {len(response['Functions'])} Lambda functions in region {REGION}:")
        for function in response['Functions']:
            print(f"  - {function['FunctionName']}")
        
        return response['Functions']
    
    except Exception as e:
        print(f"❌ Error listing functions: {e}")
        return []

def main():
    """Main function."""
    print("=== AWS Lambda Function Checker ===\n")
    
    # List all Lambda functions
    print("Listing all Lambda functions...")
    functions = list_lambda_functions()
    print()
    
    # Check the specific function
    function_name = "prohandel-connector"
    if len(sys.argv) > 1:
        function_name = sys.argv[1]
    
    print(f"Checking Lambda function: {function_name}...")
    check_lambda_function(function_name)

if __name__ == "__main__":
    main()

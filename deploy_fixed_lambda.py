#!/usr/bin/env python3
"""
Deploy Fixed Lambda Function
This script deploys the fixed Lambda function to AWS
"""

import boto3
import json
import os
import zipfile
import io
import time

def deploy_fixed_lambda():
    """Deploy the fixed Lambda function to AWS"""
    print("Deploying fixed Lambda function...")
    
    # Lambda function details
    region = "eu-central-1"
    function_name = "prohandel-fivetran-connector"
    role_arn = "arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole"
    
    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name=region)
    
    # Check if the function exists
    try:
        lambda_client.get_function(FunctionName=function_name)
        function_exists = True
        print(f"Lambda function '{function_name}' exists, updating...")
    except lambda_client.exceptions.ResourceNotFoundException:
        function_exists = False
        print(f"Lambda function '{function_name}' does not exist, creating...")
    
    # Create a zip file containing the Lambda function code
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write('fixed_lambda_function.py', 'lambda_function.py')
    
    zip_buffer.seek(0)
    zip_data = zip_buffer.read()
    
    # Deploy the Lambda function
    if function_exists:
        # Update the existing function
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_data,
            Publish=True
        )
        
        print(f"Lambda function updated successfully")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Version: {response['Version']}")
    else:
        # Create a new function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={
                'ZipFile': zip_data
            },
            Timeout=180,
            MemorySize=256,
            Publish=True,
            Environment={
                'Variables': {
                    'PROHANDEL_API_KEY': '7e7c639358434c4fa215d4e3978739d0',
                    'PROHANDEL_API_SECRET': '1cjnuux79d',
                    'PROHANDEL_AUTH_URL': 'https://auth.prohandel.cloud/api/v4',
                    'PROHANDEL_API_URL': 'https://api.prohandel.de/api/v2'
                }
            }
        )
        
        print(f"Lambda function created successfully")
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Version: {response['Version']}")
    
    # Wait for the function to be ready
    print("Waiting for the function to be ready...")
    time.sleep(5)
    
    # Test the function
    print("\nTesting the function...")
    test_event = {
        "agent": "fivetran",
        "operation": "test",
        "secrets": {
            "PROHANDEL_API_KEY": "7e7c639358434c4fa215d4e3978739d0",
            "PROHANDEL_API_SECRET": "1cjnuux79d",
            "PROHANDEL_AUTH_URL": "https://auth.prohandel.cloud/api/v4",
            "PROHANDEL_API_URL": "https://api.prohandel.de/api/v2"
        }
    }
    
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(test_event)
    )
    
    payload = json.loads(response['Payload'].read().decode())
    
    print(f"Test response: {json.dumps(payload, indent=2)}")
    
    if payload.get('success') == True:
        print("✅ Function test successful")
    else:
        print("❌ Function test failed")
        print(f"Error: {payload.get('message', 'Unknown error')}")
    
    return True

if __name__ == "__main__":
    deploy_fixed_lambda()

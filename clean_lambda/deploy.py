#!/usr/bin/env python3
"""
Deployment script for ProHandel Fivetran Lambda Connector.

This script packages the Lambda function and deploys it to AWS.
It handles dependencies, packaging, and Lambda function updates.
"""
import os
import sys
import shutil
import subprocess
import argparse
import json
import boto3
from datetime import datetime

# AWS Lambda configuration
LAMBDA_CONFIG = {
    'function_name': 'prohandel-fivetran-connector',
    'description': 'ProHandel API connector for Fivetran',
    'runtime': 'python3.9',
    'handler': 'lambda_function.lambda_handler',
    'timeout': 180,  # 3 minutes
    'memory_size': 256,
    'role_arn': 'arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole',
    'region': 'eu-central-1'
}

# Required packages
REQUIREMENTS = [
    'boto3',
    'requests',
    'tenacity'
]

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Deploy ProHandel Fivetran Lambda Connector')
    parser.add_argument('--update-function', action='store_true', help='Update the Lambda function code')
    parser.add_argument('--create-function', action='store_true', help='Create a new Lambda function')
    parser.add_argument('--package-only', action='store_true', help='Only create the deployment package without deploying')
    parser.add_argument('--test-local', action='store_true', help='Test the Lambda function locally')
    return parser.parse_args()

def create_deployment_package():
    """Create a deployment package for the Lambda function."""
    print("Creating deployment package...")
    
    # Create a temporary directory for the package
    package_dir = 'package'
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy the Lambda function code
    shutil.copy('lambda_function.py', package_dir)
    
    # Install dependencies
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install',
        '--target', package_dir,
        *REQUIREMENTS
    ])
    
    # Create a ZIP file
    shutil.make_archive('deployment_package', 'zip', package_dir)
    
    print(f"Deployment package created: {os.path.abspath('deployment_package.zip')}")
    return os.path.abspath('deployment_package.zip')

def update_lambda_function(package_path):
    """Update an existing Lambda function."""
    print(f"Updating Lambda function: {LAMBDA_CONFIG['function_name']}")
    
    lambda_client = boto3.client('lambda', region_name=LAMBDA_CONFIG['region'])
    
    with open(package_path, 'rb') as zip_file:
        lambda_client.update_function_code(
            FunctionName=LAMBDA_CONFIG['function_name'],
            ZipFile=zip_file.read(),
            Publish=True
        )
    
    print(f"Lambda function updated successfully")

def create_lambda_function(package_path):
    """Create a new Lambda function."""
    print(f"Creating Lambda function: {LAMBDA_CONFIG['function_name']}")
    
    lambda_client = boto3.client('lambda', region_name=LAMBDA_CONFIG['region'])
    
    with open(package_path, 'rb') as zip_file:
        response = lambda_client.create_function(
            FunctionName=LAMBDA_CONFIG['function_name'],
            Runtime=LAMBDA_CONFIG['runtime'],
            Role=LAMBDA_CONFIG['role_arn'],
            Handler=LAMBDA_CONFIG['handler'],
            Code={'ZipFile': zip_file.read()},
            Description=LAMBDA_CONFIG['description'],
            Timeout=LAMBDA_CONFIG['timeout'],
            MemorySize=LAMBDA_CONFIG['memory_size'],
            Publish=True,
            Environment={
                'Variables': {
                    'LOG_LEVEL': 'INFO'
                }
            }
        )
    
    print(f"Lambda function created successfully: {response['FunctionArn']}")

def test_lambda_locally():
    """Test the Lambda function locally."""
    print("Testing Lambda function locally...")
    
    # Create a test event
    test_event = {
        "type": "test",
        "secrets": {
            "PROHANDEL_API_KEY": os.environ.get("PROHANDEL_API_KEY"),
            "PROHANDEL_API_SECRET": os.environ.get("PROHANDEL_API_SECRET"),
            "PROHANDEL_AUTH_URL": os.environ.get("PROHANDEL_AUTH_URL", "https://auth.prohandel.cloud/api/v4"),
            "PROHANDEL_API_URL": os.environ.get("PROHANDEL_API_URL", "https://api.prohandel.de/api/v2")
        }
    }
    
    # Save the test event to a file
    with open('test_event.json', 'w') as f:
        json.dump(test_event, f, indent=2)
    
    # Import the Lambda handler
    sys.path.insert(0, os.getcwd())
    from lambda_function import lambda_handler
    
    # Run the Lambda handler
    result = lambda_handler(test_event, None)
    
    # Print the result
    print("\nTest Result:")
    print(json.dumps(result, indent=2))
    
    return result

def main():
    """Main function."""
    args = parse_args()
    
    # Test locally if requested
    if args.test_local:
        test_result = test_lambda_locally()
        if not test_result.get('success', False):
            print("Local test failed. Aborting deployment.")
            sys.exit(1)
    
    # Create the deployment package
    package_path = create_deployment_package()
    
    if args.package_only:
        print("Package created successfully. Skipping deployment.")
        return
    
    # Update or create the Lambda function
    if args.update_function:
        update_lambda_function(package_path)
    elif args.create_function:
        create_lambda_function(package_path)
    else:
        print("No deployment action specified. Use --update-function or --create-function.")

if __name__ == "__main__":
    main()

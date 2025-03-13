#!/usr/bin/env python3
"""
Script to deploy a simple Lambda function for Fivetran connector.
"""

import boto3
import json
import os
import zipfile
import tempfile
import shutil
import subprocess
import sys
import traceback

# AWS Region
REGION = "eu-central-1"
# Lambda function name
FUNCTION_NAME = "prohandel-fivetran-connector"
# Account ID
ACCOUNT_ID = "689864027744"

def create_deployment_package():
    """Create a deployment package for the Lambda function."""
    print("Creating deployment package...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    package_dir = os.path.join(temp_dir, 'package')
    os.makedirs(package_dir)
    zip_path = os.path.join(temp_dir, 'lambda_function.zip')
    
    # Create a requirements.txt file with the necessary dependencies
    requirements = [
        "requests",
        "tenacity",
        "boto3"
    ]
    
    requirements_path = os.path.join(temp_dir, 'requirements.txt')
    with open(requirements_path, 'w') as f:
        f.write('\n'.join(requirements))
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install',
        '-r', requirements_path,
        '--target', package_dir,
        '--upgrade'
    ])
    
    # Create the zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the lambda_function.py file from current directory
        lambda_file_path = 'lambda_function.py'
        if os.path.exists(lambda_file_path):
            print(f"Adding {lambda_file_path} to deployment package")
            zipf.write(lambda_file_path, 'lambda_function.py')
        else:
            raise FileNotFoundError(f"Lambda function file not found at {lambda_file_path}")
        
        # Add required dependencies from current directory
        dependency_files = [
            'prohandel_api.py',
            'schema.py',
            'data_processor.py'
        ]
        
        for file in dependency_files:
            if os.path.exists(file):
                print(f"Adding {file} to deployment package")
                zipf.write(file, file)
            else:
                print(f"Warning: {file} not found, skipping")
        
        # Add installed dependencies
        print("Adding installed dependencies to deployment package")
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    print(f"Deployment package created at {zip_path}")
    return temp_dir, zip_path

def update_lambda_function(lambda_client, function_name, zip_path):
    """Update the Lambda function with the new code."""
    print(f"Updating Lambda function {function_name}...")
    with open(zip_path, 'rb') as zip_file:
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_file.read(),
            Publish=True
        )
    
    # Wait for the update to complete
    print("Waiting for the update to complete...")
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName=function_name)
    
    print("Lambda function updated successfully!")

def main():
    """Main function."""
    print("=== Simple Lambda Function Deployer ===\n")
    
    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        # Create a deployment package
        temp_dir, zip_path = create_deployment_package()
        
        # Update the Lambda function
        update_lambda_function(lambda_client, FUNCTION_NAME, zip_path)
        
        # Get the function configuration to verify the update
        response = lambda_client.get_function(
            FunctionName=FUNCTION_NAME
        )
        
        # Print function details
        print("\nLambda Function Details:")
        print(f"  Name: {response['Configuration']['FunctionName']}")
        print(f"  ARN: {response['Configuration']['FunctionArn']}")
        print(f"  Runtime: {response['Configuration']['Runtime']}")
        print(f"  Handler: {response['Configuration']['Handler']}")
        print(f"  Last Modified: {response['Configuration']['LastModified']}")
        print(f"  Version: {response['Configuration']['Version']}")
        
        # Print Fivetran connector details
        print("\nFivetran Connector Configuration:")
        print(f"  AWS Region: {REGION}")
        print(f"  Account ID: {ACCOUNT_ID}")
        print(f"  Role ARN: arn:aws:iam::{ACCOUNT_ID}:role/ProHandelFivetranConnectorRole")
        print(f"  Lambda ARN: arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{FUNCTION_NAME}")
        
        # Clean up
        print("\nCleaning up temporary files...")
        shutil.rmtree(temp_dir)
        
        print("\nDone! The Lambda function has been updated successfully.")
        print("Now trigger a manual sync in Fivetran to test the updated function.")
    except Exception as e:
        print(f"Error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()

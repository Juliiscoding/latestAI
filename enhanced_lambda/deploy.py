#!/usr/bin/env python3
"""
Script to deploy the enhanced Lambda function for Fivetran connector.
"""

import boto3
import json
import os
import zipfile
import tempfile
import shutil
import subprocess

# AWS Region
REGION = "eu-central-1"
# Lambda function name
FUNCTION_NAME = "prohandel-fivetran-connector"

def create_deployment_package():
    """Create a deployment package for the Lambda function."""
    print("Creating deployment package...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    build_dir = os.path.join(temp_dir, 'build')
    os.makedirs(build_dir, exist_ok=True)
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([
        'pip', 'install', 
        '-r', 'requirements.txt', 
        '--target', build_dir
    ])
    
    # Copy Lambda function code
    print("Copying Lambda function code...")
    for file in ['lambda_function.py', 'prohandel_api.py', 'data_processor.py', 'schema.py']:
        shutil.copy(file, build_dir)
    
    # Create the zip file
    zip_path = os.path.join(temp_dir, 'lambda_function.zip')
    print(f"Creating zip file at {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(build_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, build_dir)
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
    
    # Update function configuration
    print("Updating function configuration...")
    lambda_client.update_function_configuration(
        FunctionName=function_name,
        Timeout=60,  # 60 seconds timeout
        MemorySize=256,  # 256 MB memory
        Environment={
            'Variables': {
                'PROHANDEL_API_KEY': os.environ.get('PROHANDEL_API_KEY', '7e7c639358434c4fa215d4e3978739d0'),
                'PROHANDEL_API_SECRET': os.environ.get('PROHANDEL_API_SECRET', '1cjnuux79d')
            }
        }
    )
    
    print("Lambda function updated successfully!")

def main():
    """Main function."""
    print("=== Enhanced Lambda Function Deployer ===\n")
    
    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        # Create a deployment package
        temp_dir, zip_path = create_deployment_package()
        
        # Update the Lambda function
        update_lambda_function(lambda_client, FUNCTION_NAME, zip_path)
        
        # Clean up
        print("Cleaning up temporary files...")
        shutil.rmtree(temp_dir)
        
        print("\nDone!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to deploy a Lambda function with all dependencies for Fivetran connector.
"""

import boto3
import json
import os
import zipfile
import tempfile
import shutil
import subprocess
import sys

# AWS Region
REGION = "eu-central-1"
# Lambda function name
FUNCTION_NAME = "prohandel-fivetran-connector"

def create_deployment_package():
    """Create a deployment package for the Lambda function with all dependencies."""
    print("Creating deployment package...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    package_dir = os.path.join(temp_dir, 'package')
    os.makedirs(package_dir)
    zip_path = os.path.join(temp_dir, 'lambda_function.zip')
    
    # Copy lambda_function.py to the package directory
    lambda_file_path = os.path.join('lambda_connector', 'lambda_function.py')
    if os.path.exists(lambda_file_path):
        print(f"Copying {lambda_file_path} to package directory")
        shutil.copy(lambda_file_path, os.path.join(package_dir, 'lambda_function.py'))
    else:
        raise FileNotFoundError(f"Lambda function file not found at {lambda_file_path}")
    
    # Copy data_enhancer.py if it exists
    data_enhancer_path = os.path.join('lambda_connector', 'data_enhancer.py')
    if os.path.exists(data_enhancer_path):
        print(f"Copying {data_enhancer_path} to package directory")
        shutil.copy(data_enhancer_path, os.path.join(package_dir, 'data_enhancer.py'))
    
    # Copy etl package
    etl_dir = 'etl'
    if os.path.exists(etl_dir) and os.path.isdir(etl_dir):
        print(f"Copying {etl_dir} package to package directory")
        etl_target_dir = os.path.join(package_dir, 'etl')
        shutil.copytree(etl_dir, etl_target_dir)
    
    # Install dependencies in the package directory
    requirements_path = os.path.join('lambda_connector', 'requirements.txt')
    if os.path.exists(requirements_path):
        print(f"Installing dependencies from {requirements_path} to package directory")
        
        # Try to install directly first (for local development and testing)
        try:
            print("Installing dependencies directly...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                '-r', requirements_path,
                '--target', package_dir,
                '--upgrade'
            ])
            
            # Explicitly install rpds-py wheel for Lambda compatibility
            print("Installing rpds-py wheel explicitly...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                'rpds-py==0.10.6',  # Use a specific version known to work with Lambda
                '--target', package_dir,
                '--no-deps',  # Don't reinstall dependencies
                '--platform', 'manylinux2014_x86_64',  # Lambda compatible platform
                '--only-binary=:all:',  # Only use binary wheels
                '--upgrade'
            ])
            
            # Also explicitly install jsonschema with its dependencies
            print("Installing jsonschema with dependencies...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                'jsonschema',
                '--target', package_dir,
                '--upgrade'
            ])
            
        except Exception as e:
            print(f"Warning: Error installing dependencies: {e}")
            print("Continuing with basic installation...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                '-r', requirements_path,
                '--target', package_dir,
                '--upgrade'
            ])
    
    # Create the zip file from the package directory
    print("Creating zip file from package directory")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                print(f"  Adding: {arcname}")
                zipf.write(file_path, arcname)
    
    print(f"Deployment package created at {zip_path}")
    return temp_dir, zip_path

def update_lambda_function(lambda_client, function_name, zip_path):
    """Update the Lambda function with the new code."""
    print(f"Updating Lambda function {function_name}...")
    
    # Get the zip file size
    zip_size = os.path.getsize(zip_path)
    print(f"Deployment package size: {zip_size / (1024 * 1024):.2f} MB")
    
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
    print("=== Lambda Function Deployer with Dependencies ===\n")
    
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

#!/usr/bin/env python3
"""
Script to deploy the ProHandel Lambda function to AWS
"""

import os
import json
import boto3
import zipfile
import tempfile
import shutil
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS configuration
AWS_REGION = os.getenv('AWS_REGION', 'eu-central-1')
LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME', 'prohandel-fivetran-connector')

def create_deployment_package():
    """Create a deployment package (ZIP file) for the Lambda function"""
    print("Creating deployment package...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a subdirectory for the package
        package_dir = os.path.join(temp_dir, 'package')
        os.makedirs(package_dir)
        
        # Copy the Lambda function code and dependencies
        files_to_include = [
            'lambda_function.py',
            'prohandel_api.py',
            'data_processor.py',
            'schema.py'
        ]
        
        for file in files_to_include:
            if os.path.exists(file):
                shutil.copy(file, package_dir)
                print(f"Added {file} to package")
            else:
                print(f"Warning: {file} not found, skipping")
        
        # Install dependencies into the package directory
        print("Installing dependencies...")
        subprocess.check_call([
            'pip', 'install',
            '--target', package_dir,
            'requests',
            'tenacity',
            'boto3'
        ])
        
        # Create a ZIP file
        zip_path = os.path.join(temp_dir, 'lambda_package.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, package_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Deployment package created at: {zip_path}")
        return zip_path
    
    except Exception as e:
        print(f"Error creating deployment package: {str(e)}")
        raise
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def update_lambda_function(zip_path):
    """Update the Lambda function code"""
    print(f"Updating Lambda function: {LAMBDA_FUNCTION_NAME}")
    
    try:
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        
        # Read the deployment package
        with open(zip_path, 'rb') as zip_file:
            zip_bytes = zip_file.read()
        
        # Update the Lambda function code
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_bytes,
            Publish=True
        )
        
        # Print the response
        print(f"Lambda function updated successfully. Version: {response['Version']}")
        print(f"Function ARN: {response['FunctionArn']}")
        
        return response
    
    except Exception as e:
        print(f"Error updating Lambda function: {str(e)}")
        raise

def main():
    """Main function"""
    print("=== Deploying ProHandel Lambda Function ===")
    
    # Create deployment package
    zip_path = create_deployment_package()
    
    # Update Lambda function
    update_lambda_function(zip_path)
    
    print("Deployment completed successfully")

if __name__ == "__main__":
    main()

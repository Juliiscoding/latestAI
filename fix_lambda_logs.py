#!/usr/bin/env python3
"""
Script to fix the Lambda function code to use /tmp for logs.
"""

import boto3
import json
import os
import zipfile
import tempfile
import shutil
import time

# AWS Region
REGION = "eu-central-1"
# Lambda function name
FUNCTION_NAME = "prohandel-fivetran-connector"

def download_lambda_code(lambda_client, function_name):
    """Download the Lambda function code."""
    print(f"Downloading Lambda function code for {function_name}...")
    response = lambda_client.get_function(FunctionName=function_name)
    location = response['Code']['Location']
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, 'lambda_function.zip')
    
    # Download the code
    import urllib.request
    urllib.request.urlretrieve(location, zip_path)
    
    # Extract the zip file
    extract_dir = os.path.join(temp_dir, 'extracted')
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    print(f"Lambda code downloaded and extracted to {extract_dir}")
    return temp_dir, extract_dir

def fix_log_paths(extract_dir):
    """Fix log paths in Python files to use /tmp."""
    print("Fixing log paths in Python files...")
    modified_files = []
    
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check if the file contains references to 'logs' directory
                if "open('logs/" in content or 'open("logs/' in content or "os.path.join('logs" in content or 'os.path.join("logs' in content:
                    print(f"Found log path references in {file}")
                    
                    # Replace direct references to 'logs' directory
                    new_content = content.replace("open('logs/", "open('/tmp/logs/")
                    new_content = new_content.replace('open("logs/', 'open("/tmp/logs/')
                    new_content = new_content.replace("os.path.join('logs", "os.path.join('/tmp', 'logs")
                    new_content = new_content.replace('os.path.join("logs', 'os.path.join("/tmp", "logs')
                    
                    # Add code to create the /tmp/logs directory if it doesn't exist
                    if "import os" not in new_content:
                        new_content = "import os\n" + new_content
                    
                    if "os.makedirs('/tmp/logs', exist_ok=True)" not in new_content:
                        # Find a good place to insert the makedirs line
                        lines = new_content.split('\n')
                        import_section_end = 0
                        for i, line in enumerate(lines):
                            if line.startswith('import ') or line.startswith('from '):
                                import_section_end = i
                        
                        # Insert after imports
                        lines.insert(import_section_end + 1, "# Create logs directory in /tmp")
                        lines.insert(import_section_end + 2, "os.makedirs('/tmp/logs', exist_ok=True)")
                        new_content = '\n'.join(lines)
                    
                    # Write the modified content back
                    with open(file_path, 'w') as f:
                        f.write(new_content)
                    
                    modified_files.append(file)
    
    return modified_files

def create_new_deployment_package(temp_dir, extract_dir):
    """Create a new deployment package with the fixed code."""
    print("Creating new deployment package...")
    new_zip_path = os.path.join(temp_dir, 'new_lambda_function.zip')
    
    with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, extract_dir)
                zipf.write(file_path, arcname)
    
    print(f"New deployment package created at {new_zip_path}")
    return new_zip_path

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
    print("=== Lambda Function Log Path Fixer ===\n")
    
    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        # Download the Lambda function code
        temp_dir, extract_dir = download_lambda_code(lambda_client, FUNCTION_NAME)
        
        # Fix log paths in Python files
        modified_files = fix_log_paths(extract_dir)
        
        if modified_files:
            print(f"Modified {len(modified_files)} files:")
            for file in modified_files:
                print(f"  - {file}")
            
            # Create a new deployment package
            new_zip_path = create_new_deployment_package(temp_dir, extract_dir)
            
            # Update the Lambda function
            update_lambda_function(lambda_client, FUNCTION_NAME, new_zip_path)
        else:
            print("No files needed modification.")
        
        # Clean up
        print("Cleaning up temporary files...")
        shutil.rmtree(temp_dir)
        
        print("\nDone!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

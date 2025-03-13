#!/usr/bin/env python3
"""
Script to add a tmp directory handler to the Lambda function.
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

def find_handler_file(extract_dir):
    """Find the Lambda handler file."""
    print("Finding Lambda handler file...")
    
    # Get the handler from the Lambda function
    lambda_client = boto3.client('lambda', region_name=REGION)
    response = lambda_client.get_function_configuration(FunctionName=FUNCTION_NAME)
    handler = response.get('Handler', 'lambda_function.lambda_handler')
    
    # The handler is in the format "file.function_name"
    handler_parts = handler.split('.')
    handler_file = handler_parts[0] + '.py'
    
    # Look for the handler file
    handler_path = None
    for root, _, files in os.walk(extract_dir):
        if handler_file in files:
            handler_path = os.path.join(root, handler_file)
            break
    
    if handler_path:
        print(f"Found handler file: {handler_path}")
        return handler_path
    else:
        print(f"Handler file {handler_file} not found!")
        return None

def add_tmp_directory_handler(handler_path):
    """Add code to handle tmp directory in the Lambda handler."""
    if not handler_path:
        return False
    
    print("Adding tmp directory handler code...")
    
    with open(handler_path, 'r') as f:
        content = f.read()
    
    # Check if we've already added the tmp directory handler
    if "# Ensure tmp directories exist" in content:
        print("Tmp directory handler already exists in the code.")
        return False
    
    # Find the handler function
    lambda_client = boto3.client('lambda', region_name=REGION)
    response = lambda_client.get_function_configuration(FunctionName=FUNCTION_NAME)
    handler = response.get('Handler', 'lambda_function.lambda_handler')
    handler_parts = handler.split('.')
    handler_function = handler_parts[1]
    
    # Find the handler function definition
    import re
    handler_pattern = re.compile(r'def\s+' + handler_function + r'\s*\(')
    match = handler_pattern.search(content)
    
    if not match:
        print(f"Could not find handler function '{handler_function}' in the code.")
        return False
    
    # Insert the tmp directory handler code after the function definition
    pos = match.end()
    # Find the end of the function signature (the closing parenthesis and colon)
    while pos < len(content) and content[pos] != ':':
        pos += 1
    
    if pos < len(content):
        pos += 1  # Move past the colon
    
    # Find the first non-whitespace character after the colon (beginning of function body)
    while pos < len(content) and content[pos].isspace():
        pos += 1
    
    # Insert our code at the beginning of the function body
    tmp_handler_code = """
    # Ensure tmp directories exist
    import os
    os.makedirs('/tmp/logs', exist_ok=True)
    
    # Monkey patch open function to redirect 'logs/' to '/tmp/logs/'
    original_open = open
    def patched_open(file, *args, **kwargs):
        if isinstance(file, str) and file.startswith('logs/'):
            file = '/tmp/' + file
        return original_open(file, *args, **kwargs)
    
    # Replace the built-in open function with our patched version
    import builtins
    builtins.open = patched_open
    
"""
    
    new_content = content[:pos] + tmp_handler_code + content[pos:]
    
    # Write the modified content back
    with open(handler_path, 'w') as f:
        f.write(new_content)
    
    print("Added tmp directory handler code to the Lambda function.")
    return True

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
    print("=== Lambda Function Tmp Directory Handler ===\n")
    
    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        # Download the Lambda function code
        temp_dir, extract_dir = download_lambda_code(lambda_client, FUNCTION_NAME)
        
        # Find the handler file
        handler_path = find_handler_file(extract_dir)
        
        # Add tmp directory handler
        modified = add_tmp_directory_handler(handler_path)
        
        if modified:
            # Create a new deployment package
            new_zip_path = create_new_deployment_package(temp_dir, extract_dir)
            
            # Update the Lambda function
            update_lambda_function(lambda_client, FUNCTION_NAME, new_zip_path)
        else:
            print("No modifications were made to the Lambda function.")
        
        # Clean up
        print("Cleaning up temporary files...")
        shutil.rmtree(temp_dir)
        
        print("\nDone!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

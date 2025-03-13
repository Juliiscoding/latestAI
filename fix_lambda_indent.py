#!/usr/bin/env python3
"""
Script to fix the indentation in the Lambda function.
"""

import boto3
import json
import os
import zipfile
import tempfile
import shutil
import time
import re

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

def fix_indentation(handler_path):
    """Fix the indentation in the Lambda handler."""
    if not handler_path:
        return False
    
    print("Fixing indentation in the Lambda handler...")
    
    with open(handler_path, 'r') as f:
        lines = f.readlines()
    
    # First, let's remove our previous patch if it exists
    patched_lines = []
    skip_until_line = -1
    for i, line in enumerate(lines):
        if "# Ensure tmp directories exist" in line:
            # Find the end of our patch
            for j in range(i, len(lines)):
                if "# Replace the built-in open function with our patched version" in lines[j]:
                    skip_until_line = j + 2  # Skip 2 more lines after this comment
                    break
        
        if i <= skip_until_line:
            continue
        
        patched_lines.append(line)
    
    if len(patched_lines) < len(lines):
        print("Removed previous patch.")
        lines = patched_lines
    
    # Get the handler function name
    lambda_client = boto3.client('lambda', region_name=REGION)
    response = lambda_client.get_function_configuration(FunctionName=FUNCTION_NAME)
    handler = response.get('Handler', 'lambda_function.lambda_handler')
    handler_parts = handler.split('.')
    handler_function = handler_parts[1]
    
    # Find the handler function and determine its indentation
    handler_line = -1
    handler_indent = ""
    for i, line in enumerate(lines):
        if re.match(r'^\s*def\s+' + handler_function + r'\s*\(', line):
            handler_line = i
            handler_indent = re.match(r'^\s*', line).group(0)
            break
    
    if handler_line == -1:
        print(f"Could not find handler function '{handler_function}' in the code.")
        return False
    
    # Determine the indentation of the first line of the function body
    body_indent = ""
    for i in range(handler_line + 1, len(lines)):
        if lines[i].strip() and not lines[i].strip().startswith('#'):
            body_indent = re.match(r'^\s*', lines[i]).group(0)
            break
    
    if not body_indent:
        print("Could not determine function body indentation.")
        return False
    
    # Create our patch with the correct indentation
    patch_lines = [
        f"{body_indent}# Ensure tmp directories exist\n",
        f"{body_indent}import os\n",
        f"{body_indent}os.makedirs('/tmp/logs', exist_ok=True)\n",
        f"\n",
        f"{handler_indent}# Function to redirect logs directory to /tmp\n",
        f"{handler_indent}def _write_to_tmp_logs(path):\n",
        f"{handler_indent}    if isinstance(path, str) and path.startswith('logs/'):\n",
        f"{handler_indent}        return '/tmp/' + path\n",
        f"{handler_indent}    return path\n",
        f"\n",
        f"{body_indent}# Redirect any logs directory access to /tmp\n",
        f"{body_indent}try:\n",
        f"{body_indent}    with open(_write_to_tmp_logs('logs/test.log'), 'a') as f:\n",
        f"{body_indent}        f.write('Lambda function started\\n')\n",
        f"{body_indent}except Exception as e:\n",
        f"{body_indent}    print(f'Log initialization error: {{e}}')\n",
        f"\n"
    ]
    
    # Insert our patch at the beginning of the function body
    new_lines = lines[:handler_line + 1]  # Include the function definition line
    
    # Find where to insert our patch (after the function signature)
    for i in range(handler_line + 1, len(lines)):
        line = lines[i]
        if ':' in line:  # Found the end of the function signature
            new_lines.append(line)  # Add the line with the colon
            new_lines.extend(patch_lines)  # Add our patch
            new_lines.extend(lines[i + 1:])  # Add the rest of the file
            break
        else:
            new_lines.append(line)  # Add lines that are part of the function signature
    
    # Write the fixed code back
    with open(handler_path, 'w') as f:
        f.writelines(new_lines)
    
    print("Fixed indentation in the Lambda handler.")
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
    print("=== Lambda Function Indentation Fixer ===\n")
    
    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    try:
        # Download the Lambda function code
        temp_dir, extract_dir = download_lambda_code(lambda_client, FUNCTION_NAME)
        
        # Find the handler file
        handler_path = find_handler_file(extract_dir)
        
        # Fix indentation
        modified = fix_indentation(handler_path)
        
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

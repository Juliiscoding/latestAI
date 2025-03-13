#!/usr/bin/env python
"""
Complete deployment script for ProHandel AWS Lambda Connector with Fivetran integration.
This script handles:
1. AWS IAM role and policy creation
2. Lambda function deployment
3. Fivetran connector configuration
"""
import os
import json
import time
import subprocess
import argparse
import zipfile
import tempfile
import shutil
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AWS_ACCOUNT_ID = "689864027744"
AWS_REGION = "eu-central-1"
LAMBDA_FUNCTION_NAME = "ProHandelFivetranConnector"
IAM_ROLE_NAME = "ProHandelFivetranConnectorRole"
FIVETRAN_API_KEY = os.getenv("FIVETRAN_API_KEY", "eWMMoSTR8ijWdw2u")
FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET", "hcH43fVni4oIPcmTFQZqmvbeZ0zmG9sp")
EXTERNAL_ID = "look_frescoes"

# Paths
BASE_DIR = Path(__file__).parent
PACKAGE_DIR = BASE_DIR / "package"
DEPLOYMENT_ZIP = BASE_DIR / "lambda_deployment.zip"

# AWS CLI commands wrapper
def run_aws_command(command, capture_output=True):
    """Run an AWS CLI command and return the result."""
    full_command = ["/usr/local/bin/aws"] + command
    print(f"Running: {' '.join(full_command)}")
    
    result = subprocess.run(
        full_command,
        capture_output=capture_output,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    if capture_output:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return result.stdout
    return None

# Fivetran API wrapper
class FivetranAPI:
    """Wrapper for Fivetran API calls."""
    
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.fivetran.com/v1"
        self.auth = (api_key, api_secret)
    
    def create_connector(self, group_id, service, config):
        """Create a new connector in Fivetran."""
        url = f"{self.base_url}/connectors"
        payload = {
            "service": service,
            "group_id": group_id,
            "config": config
        }
        response = requests.post(url, json=payload, auth=self.auth)
        return response.json()
    
    def get_groups(self):
        """Get all groups in the Fivetran account."""
        url = f"{self.base_url}/groups"
        response = requests.get(url, auth=self.auth)
        return response.json()

# Deployment steps
def configure_aws_credentials(access_key, secret_key):
    """Configure AWS CLI with credentials."""
    print("Configuring AWS credentials...")
    run_aws_command(["configure", "set", "aws_access_key_id", access_key], capture_output=False)
    run_aws_command(["configure", "set", "aws_secret_access_key", secret_key], capture_output=False)
    run_aws_command(["configure", "set", "region", AWS_REGION], capture_output=False)
    run_aws_command(["configure", "set", "output", "json"], capture_output=False)
    print("AWS credentials configured successfully.")

def create_iam_role():
    """Create the IAM role for the Lambda function."""
    print("Creating IAM role...")
    
    # Create trust policy file
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::834469178297:root"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "sts:ExternalId": EXTERNAL_ID
                    }
                }
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(trust_policy, temp_file)
        trust_policy_path = temp_file.name
    
    # Create the role
    try:
        response = run_aws_command([
            "iam", "create-role",
            "--role-name", IAM_ROLE_NAME,
            "--assume-role-policy-document", f"file://{trust_policy_path}"
        ])
        
        if not response:
            print("Role already exists, trying to update trust policy...")
            run_aws_command([
                "iam", "update-assume-role-policy",
                "--role-name", IAM_ROLE_NAME,
                "--policy-document", f"file://{trust_policy_path}"
            ])
    finally:
        os.unlink(trust_policy_path)
    
    # Attach policies
    policies = [
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
    ]
    
    for policy_arn in policies:
        run_aws_command([
            "iam", "attach-role-policy",
            "--role-name", IAM_ROLE_NAME,
            "--policy-arn", policy_arn
        ], capture_output=False)
    
    # Create Lambda invoke policy
    lambda_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": f"arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:{LAMBDA_FUNCTION_NAME}"
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(lambda_policy, temp_file)
        lambda_policy_path = temp_file.name
    
    try:
        policy_name = f"{LAMBDA_FUNCTION_NAME}InvokePolicy"
        try:
            response = run_aws_command([
                "iam", "create-policy",
                "--policy-name", policy_name,
                "--policy-document", f"file://{lambda_policy_path}"
            ])
            
            policy_arn = response["Policy"]["Arn"]
        except:
            print("Policy may already exist, getting ARN...")
            policy_arn = f"arn:aws:iam::{AWS_ACCOUNT_ID}:policy/{policy_name}"
        
        # Attach the policy to the role
        run_aws_command([
            "iam", "attach-role-policy",
            "--role-name", IAM_ROLE_NAME,
            "--policy-arn", policy_arn
        ], capture_output=False)
    finally:
        os.unlink(lambda_policy_path)
    
    print("IAM role created and configured successfully.")
    
    # Get the role ARN
    response = run_aws_command([
        "iam", "get-role",
        "--role-name", IAM_ROLE_NAME
    ])
    
    return response["Role"]["Arn"] if response else None

def create_deployment_package():
    """Create the Lambda deployment package."""
    print("Creating deployment package...")
    
    # Check if package directory exists
    if not PACKAGE_DIR.exists():
        print(f"Creating package directory: {PACKAGE_DIR}")
        PACKAGE_DIR.mkdir(exist_ok=True)
        
        # Install dependencies
        subprocess.run([
            "pip", "install", 
            "-r", str(BASE_DIR / "requirements.txt"),
            "-t", str(PACKAGE_DIR)
        ], check=True)
        
        # Copy Lambda function files
        shutil.copy(BASE_DIR / "lambda_function.py", PACKAGE_DIR)
        shutil.copy(BASE_DIR / "data_enhancer.py", PACKAGE_DIR)
    
    # Create zip file
    if DEPLOYMENT_ZIP.exists():
        DEPLOYMENT_ZIP.unlink()
    
    with zipfile.ZipFile(DEPLOYMENT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(PACKAGE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, PACKAGE_DIR)
                zipf.write(file_path, arcname)
    
    print(f"Deployment package created: {DEPLOYMENT_ZIP}")
    return DEPLOYMENT_ZIP

def deploy_lambda_function(role_arn):
    """Deploy the Lambda function to AWS."""
    print("Deploying Lambda function...")
    
    # Check if function exists
    function_exists = run_aws_command([
        "lambda", "get-function",
        "--function-name", LAMBDA_FUNCTION_NAME
    ])
    
    if function_exists:
        print("Function exists, updating code...")
        response = run_aws_command([
            "lambda", "update-function-code",
            "--function-name", LAMBDA_FUNCTION_NAME,
            "--zip-file", f"fileb://{DEPLOYMENT_ZIP}"
        ])
    else:
        print("Creating new function...")
        response = run_aws_command([
            "lambda", "create-function",
            "--function-name", LAMBDA_FUNCTION_NAME,
            "--runtime", "python3.9",
            "--role", role_arn,
            "--handler", "lambda_function.lambda_handler",
            "--timeout", "180",
            "--memory-size", "256",
            "--zip-file", f"fileb://{DEPLOYMENT_ZIP}"
        ])
    
    # Set environment variables
    run_aws_command([
        "lambda", "update-function-configuration",
        "--function-name", LAMBDA_FUNCTION_NAME,
        "--environment", json.dumps({
            "Variables": {
                "PROHANDEL_API_KEY": os.getenv("PROHANDEL_API_KEY", "your_api_key"),
                "PROHANDEL_API_SECRET": os.getenv("PROHANDEL_API_SECRET", "your_api_secret"),
                "PROHANDEL_API_URL": os.getenv("PROHANDEL_API_URL", "https://linde.prohandel.de/api/v2"),
                "PROHANDEL_AUTH_URL": os.getenv("PROHANDEL_AUTH_URL", "https://linde.prohandel.de/api/v2/auth")
            }
        })
    ])
    
    print("Lambda function deployed successfully.")
    
    # Get the function ARN
    response = run_aws_command([
        "lambda", "get-function",
        "--function-name", LAMBDA_FUNCTION_NAME
    ])
    
    return response["Configuration"]["FunctionArn"] if response else None

def configure_fivetran(lambda_arn, role_arn):
    """Configure the Fivetran connector."""
    print("Configuring Fivetran connector...")
    
    fivetran = FivetranAPI(FIVETRAN_API_KEY, FIVETRAN_API_SECRET)
    
    # Get the first group
    groups = fivetran.get_groups()
    if not groups.get("data", {}).get("items"):
        print("No Fivetran groups found. Please create a group in Fivetran first.")
        return False
    
    group_id = groups["data"]["items"][0]["id"]
    
    # Create the connector
    config = {
        "external_id": EXTERNAL_ID,
        "role_arn": role_arn,
        "function_arn": lambda_arn,
        "region": AWS_REGION,
        "sync_mode": "direct",
        "schema": "prohandel_data",
        "secrets": json.dumps({
            "api_key": os.getenv("PROHANDEL_API_KEY", "your_api_key"),
            "api_secret": os.getenv("PROHANDEL_API_SECRET", "your_api_secret"),
            "api_url": os.getenv("PROHANDEL_API_URL", "https://linde.prohandel.de/api/v2")
        })
    }
    
    response = fivetran.create_connector(group_id, "aws_lambda", config)
    
    if response.get("code") == "Success":
        print("Fivetran connector created successfully.")
        print(f"Connector ID: {response['data']['id']}")
        return True
    else:
        print(f"Error creating Fivetran connector: {response}")
        return False

def main():
    """Main function to run the deployment process."""
    parser = argparse.ArgumentParser(description="Deploy ProHandel AWS Lambda Connector")
    parser.add_argument("--aws-access-key", help="AWS Access Key ID")
    parser.add_argument("--aws-secret-key", help="AWS Secret Access Key")
    parser.add_argument("--skip-aws-config", action="store_true", help="Skip AWS credentials configuration")
    parser.add_argument("--skip-iam", action="store_true", help="Skip IAM role creation")
    parser.add_argument("--skip-lambda", action="store_true", help="Skip Lambda deployment")
    parser.add_argument("--skip-fivetran", action="store_true", help="Skip Fivetran configuration")
    
    args = parser.parse_args()
    
    # Configure AWS credentials if provided
    if not args.skip_aws_config:
        if args.aws_access_key and args.aws_secret_key:
            configure_aws_credentials(args.aws_access_key, args.aws_secret_key)
        else:
            print("AWS credentials not provided, skipping configuration.")
            print("Make sure your AWS credentials are configured correctly.")
    
    # Create IAM role
    role_arn = None
    if not args.skip_iam:
        role_arn = create_iam_role()
        if not role_arn:
            print("Failed to create or get IAM role.")
            return
    else:
        # Get existing role ARN
        response = run_aws_command([
            "iam", "get-role",
            "--role-name", IAM_ROLE_NAME
        ])
        role_arn = response["Role"]["Arn"] if response else None
    
    # Create deployment package and deploy Lambda function
    lambda_arn = None
    if not args.skip_lambda:
        deployment_package = create_deployment_package()
        lambda_arn = deploy_lambda_function(role_arn)
        if not lambda_arn:
            print("Failed to deploy Lambda function.")
            return
    else:
        # Get existing Lambda function ARN
        response = run_aws_command([
            "lambda", "get-function",
            "--function-name", LAMBDA_FUNCTION_NAME
        ])
        lambda_arn = response["Configuration"]["FunctionArn"] if response else None
    
    # Configure Fivetran
    if not args.skip_fivetran:
        if lambda_arn and role_arn:
            success = configure_fivetran(lambda_arn, role_arn)
            if success:
                print("Deployment completed successfully!")
            else:
                print("Deployment completed with errors in Fivetran configuration.")
        else:
            print("Missing Lambda or IAM role ARN, skipping Fivetran configuration.")
    else:
        print("Skipping Fivetran configuration.")
        print("Deployment completed successfully!")
    
    # Print summary
    print("\nDeployment Summary:")
    print(f"IAM Role ARN: {role_arn}")
    print(f"Lambda Function ARN: {lambda_arn}")
    print(f"External ID for Fivetran: {EXTERNAL_ID}")
    print(f"AWS Region: {AWS_REGION}")

if __name__ == "__main__":
    main()

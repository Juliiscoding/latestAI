#!/usr/bin/env python3
"""
Troubleshoot Lambda Connection
This script helps troubleshoot connection issues between Fivetran and AWS Lambda
"""

import boto3
import json
import sys
import subprocess
from datetime import datetime, timedelta

def check_lambda_function():
    """Check if the Lambda function exists and is accessible"""
    print("Checking Lambda function...")
    
    # Lambda function details
    region = "eu-central-1"
    function_name = "prohandel-fivetran-connector"
    
    try:
        # Create a Lambda client
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Get function details
        response = lambda_client.get_function(FunctionName=function_name)
        
        print(f"✅ Lambda function '{function_name}' exists in region '{region}'")
        print(f"Function ARN: {response['Configuration']['FunctionArn']}")
        print(f"Runtime: {response['Configuration']['Runtime']}")
        print(f"Handler: {response['Configuration']['Handler']}")
        print(f"Last Modified: {response['Configuration']['LastModified']}")
        print(f"Timeout: {response['Configuration']['Timeout']} seconds")
        print(f"Memory Size: {response['Configuration']['MemorySize']} MB")
        
        # Check if the function has been invoked recently
        metrics_client = boto3.client('cloudwatch', region_name=region)
        
        # Get invocation metrics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        invocation_metrics = metrics_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Invocations',
            Dimensions=[
                {
                    'Name': 'FunctionName',
                    'Value': function_name
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Sum']
        )
        
        if invocation_metrics['Datapoints']:
            total_invocations = sum(point['Sum'] for point in invocation_metrics['Datapoints'])
            print(f"Function has been invoked {total_invocations} times in the last 24 hours")
        else:
            print("Function has not been invoked in the last 24 hours")
        
        # Check for errors
        error_metrics = metrics_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Errors',
            Dimensions=[
                {
                    'Name': 'FunctionName',
                    'Value': function_name
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Sum']
        )
        
        if error_metrics['Datapoints']:
            total_errors = sum(point['Sum'] for point in error_metrics['Datapoints'])
            print(f"Function has had {total_errors} errors in the last 24 hours")
        else:
            print("No errors detected in the last 24 hours")
        
        return True
    
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"❌ Lambda function '{function_name}' does not exist in region '{region}'")
        print("Possible solutions:")
        print("1. Verify the function name is correct")
        print("2. Verify the region is correct")
        print("3. Deploy the function if it hasn't been deployed")
        return False
    
    except Exception as e:
        print(f"❌ Error checking Lambda function: {e}")
        return False

def check_iam_role():
    """Check if the IAM role exists and has the correct permissions"""
    print("\nChecking IAM role...")
    
    # IAM role details
    role_name = "ProHandelFivetranConnectorRole"
    
    try:
        # Create an IAM client
        iam_client = boto3.client('iam')
        
        # Get role details
        response = iam_client.get_role(RoleName=role_name)
        
        print(f"✅ IAM role '{role_name}' exists")
        print(f"Role ARN: {response['Role']['Arn']}")
        print(f"Created: {response['Role']['CreateDate']}")
        
        # Check attached policies
        policies = iam_client.list_attached_role_policies(RoleName=role_name)
        
        if policies['AttachedPolicies']:
            print(f"Role has {len(policies['AttachedPolicies'])} attached policies:")
            for policy in policies['AttachedPolicies']:
                print(f"- {policy['PolicyName']} ({policy['PolicyArn']})")
        else:
            print("❌ Role has no attached policies")
            print("Possible solutions:")
            print("1. Attach the necessary policies to the role")
            print("2. Create a new role with the correct policies")
        
        # Check trust relationship
        trust_policy = response['Role']['AssumeRolePolicyDocument']
        trust_policy_str = json.dumps(trust_policy)
        
        if '834469178297' in trust_policy_str:
            print("✅ Role has trust relationship with Fivetran")
        else:
            print("❌ Role does not have trust relationship with Fivetran")
            print("Possible solutions:")
            print("1. Update the trust relationship to allow Fivetran to assume the role")
            print("2. Create a new role with the correct trust relationship")
        
        return True
    
    except iam_client.exceptions.NoSuchEntityException:
        print(f"❌ IAM role '{role_name}' does not exist")
        print("Possible solutions:")
        print("1. Create the role using the setup-iam.sh script")
        print("2. Verify the role name is correct")
        return False
    
    except Exception as e:
        print(f"❌ Error checking IAM role: {e}")
        return False

def check_aws_credentials():
    """Check if the AWS credentials are valid"""
    print("\nChecking AWS credentials...")
    
    try:
        # Create an STS client
        sts_client = boto3.client('sts')
        
        # Get caller identity
        response = sts_client.get_caller_identity()
        
        print(f"✅ AWS credentials are valid")
        print(f"Account ID: {response['Account']}")
        print(f"User ID: {response['UserId']}")
        print(f"ARN: {response['Arn']}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error checking AWS credentials: {e}")
        print("Possible solutions:")
        print("1. Run 'aws configure' to set up your AWS credentials")
        print("2. Check if your AWS credentials have expired")
        print("3. Verify that your IAM user has the necessary permissions")
        return False

def check_fivetran_external_id():
    """Check if the external ID is correct"""
    print("\nChecking Fivetran external ID...")
    
    # External ID from the Fivetran UI
    external_id = "armed_unleaded"
    
    # Check if the external ID is in the IAM role trust relationship
    try:
        # Create an IAM client
        iam_client = boto3.client('iam')
        
        # Get role details
        response = iam_client.get_role(RoleName="ProHandelFivetranConnectorRole")
        
        # Check trust relationship
        trust_policy = response['Role']['AssumeRolePolicyDocument']
        
        if external_id in str(trust_policy):
            print(f"✅ External ID '{external_id}' is in the trust relationship")
        else:
            print(f"❌ External ID '{external_id}' is not in the trust relationship")
            print("Possible solutions:")
            print("1. Update the trust relationship to include the correct external ID")
            print("2. Use the external ID from the trust relationship in the Fivetran UI")
        
        return True
    
    except Exception as e:
        print(f"❌ Error checking external ID: {e}")
        return False

def test_lambda_invocation():
    """Test invoking the Lambda function"""
    print("\nTesting Lambda invocation...")
    
    # Lambda function details
    region = "eu-central-1"
    function_name = "prohandel-fivetran-connector"
    
    try:
        # Create a Lambda client
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Create a test event
        test_event = {
            "agent": "fivetran",
            "state": {},
            "secrets": {
                "PROHANDEL_API_KEY": "7e7c639358434c4fa215d4e3978739d0",
                "PROHANDEL_API_SECRET": "1cjnuux79d",
                "PROHANDEL_AUTH_URL": "https://auth.prohandel.cloud/api/v4",
                "PROHANDEL_API_URL": "https://api.prohandel.de/api/v2"
            },
            "setup_test": True
        }
        
        # Invoke the function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        # Parse the response
        payload = json.loads(response['Payload'].read().decode())
        
        if response['StatusCode'] == 200:
            print(f"✅ Lambda function invocation successful")
            print(f"Response: {json.dumps(payload, indent=2)}")
        else:
            print(f"❌ Lambda function invocation failed with status code {response['StatusCode']}")
            print(f"Response: {json.dumps(payload, indent=2)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error invoking Lambda function: {e}")
        return False

def check_aws_cli_installation():
    """Check if AWS CLI is installed and configured"""
    print("\nChecking AWS CLI installation...")
    
    try:
        # Run AWS CLI version command
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ AWS CLI is installed: {result.stdout.strip()}")
        else:
            print(f"❌ AWS CLI is not installed or not in PATH")
            print("Possible solutions:")
            print("1. Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html")
            print("2. Add AWS CLI to your PATH")
            return False
        
        # Check AWS CLI configuration
        result = subprocess.run(['aws', 'configure', 'list'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ AWS CLI is configured")
            print(result.stdout)
        else:
            print(f"❌ AWS CLI is not configured")
            print("Possible solutions:")
            print("1. Run 'aws configure' to set up your AWS credentials")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error checking AWS CLI installation: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("AWS Lambda Connection Troubleshooter")
    print("=" * 50)
    
    # Check AWS CLI installation
    aws_cli_ok = check_aws_cli_installation()
    
    if not aws_cli_ok:
        print("\n❌ AWS CLI issues must be resolved before continuing")
        sys.exit(1)
    
    # Check AWS credentials
    aws_creds_ok = check_aws_credentials()
    
    if not aws_creds_ok:
        print("\n❌ AWS credential issues must be resolved before continuing")
        sys.exit(1)
    
    # Check IAM role
    iam_role_ok = check_iam_role()
    
    # Check Lambda function
    lambda_function_ok = check_lambda_function()
    
    # Check external ID
    external_id_ok = check_fivetran_external_id()
    
    # Test Lambda invocation
    if lambda_function_ok:
        lambda_invocation_ok = test_lambda_invocation()
    else:
        lambda_invocation_ok = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("Troubleshooting Summary")
    print("=" * 50)
    
    print(f"AWS CLI Installation: {'✅ OK' if aws_cli_ok else '❌ Issues detected'}")
    print(f"AWS Credentials: {'✅ OK' if aws_creds_ok else '❌ Issues detected'}")
    print(f"IAM Role: {'✅ OK' if iam_role_ok else '❌ Issues detected'}")
    print(f"Lambda Function: {'✅ OK' if lambda_function_ok else '❌ Issues detected'}")
    print(f"External ID: {'✅ OK' if external_id_ok else '❌ Issues detected'}")
    print(f"Lambda Invocation: {'✅ OK' if lambda_invocation_ok else '❌ Issues detected'}")
    
    # Provide recommendations
    print("\nRecommendations:")
    
    if not aws_cli_ok or not aws_creds_ok:
        print("1. Fix AWS CLI and credential issues first")
    elif not iam_role_ok:
        print("1. Create or update the IAM role")
        print("2. Ensure the role has the correct trust relationship with Fivetran")
        print("3. Ensure the role has the necessary permissions")
    elif not lambda_function_ok:
        print("1. Deploy the Lambda function")
        print("2. Ensure the function is in the correct region")
    elif not external_id_ok:
        print("1. Update the trust relationship to include the correct external ID")
        print("2. Use the external ID from the trust relationship in the Fivetran UI")
    elif not lambda_invocation_ok:
        print("1. Check the Lambda function logs for errors")
        print("2. Ensure the function has the necessary permissions")
        print("3. Verify the function code is correct")
    else:
        print("All checks passed. If you're still experiencing issues:")
        print("1. Check the Fivetran UI for more specific error messages")
        print("2. Contact Fivetran support for assistance")
        print("3. Check CloudWatch Logs for any Lambda function errors")

if __name__ == "__main__":
    main()

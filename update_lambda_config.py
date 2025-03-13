#!/usr/bin/env python3
"""
Update Lambda Configuration
This script updates the Lambda function configuration to match Fivetran's expectations
"""

import boto3

def update_lambda_config():
    """Update the Lambda function configuration"""
    print("Updating Lambda function configuration...")
    
    # Lambda function details
    region = "eu-central-1"
    function_name = "prohandel-fivetran-connector"
    
    try:
        # Create a Lambda client
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Update the function configuration
        response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Timeout=180,  # 3 minutes
            MemorySize=256  # 256 MB
        )
        
        print(f"✅ Lambda function configuration updated successfully")
        print(f"Timeout: 180 seconds (3 minutes)")
        print(f"Memory Size: 256 MB")
        
        return True
    
    except Exception as e:
        print(f"❌ Error updating Lambda function configuration: {e}")
        return False

if __name__ == "__main__":
    update_lambda_config()

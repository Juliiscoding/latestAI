#!/usr/bin/env python3
"""
Update Trust Policy
This script updates the IAM role's trust policy to allow Fivetran to assume the role
"""

import boto3
import json

def update_trust_policy():
    """Update the trust policy for the ProHandelFivetranConnectorRole"""
    print("Updating trust policy for ProHandelFivetranConnectorRole...")
    
    # IAM role details
    role_name = "ProHandelFivetranConnectorRole"
    
    # External ID from the Fivetran UI
    external_id = "armed_unleaded"
    
    # Create an IAM client
    iam_client = boto3.client('iam')
    
    # Define the trust policy
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
                    "AWS": "arn:aws:iam::834469178297:root"  # Fivetran's AWS account
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "sts:ExternalId": external_id
                    }
                }
            }
        ]
    }
    
    try:
        # Update the trust policy
        response = iam_client.update_assume_role_policy(
            RoleName=role_name,
            PolicyDocument=json.dumps(trust_policy)
        )
        
        print(f"✅ Trust policy updated successfully")
        print(f"External ID '{external_id}' added to trust policy")
        print(f"Fivetran's AWS account added to trust policy")
        
        return True
    
    except Exception as e:
        print(f"❌ Error updating trust policy: {e}")
        return False

if __name__ == "__main__":
    update_trust_policy()

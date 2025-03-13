#!/bin/bash
# Script to set up IAM role for the ProHandel Lambda function

# Set variables
ROLE_NAME="ProHandelFivetranConnectorRole"
POLICY_NAME="ProHandelFivetranConnectorPolicy"
REGION="eu-central-1"  # Change to your AWS region
AWS_ACCOUNT_ID="689864027744"
AWS_CLI="python3 ./aws-cli.py"

# Create the IAM role with trust policy
echo "Creating IAM role..."
$AWS_CLI iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json

# Create the IAM policy
echo "Creating IAM policy..."
$AWS_CLI iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document file://lambda-policy.json

# Attach the policy to the role
echo "Attaching policy to role..."
$AWS_CLI iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${POLICY_NAME}"

# Wait for role to propagate
echo "Waiting for role to propagate..."
sleep 10

echo "IAM setup completed!"
echo "Role ARN: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"

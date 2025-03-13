#!/bin/bash

# Define variables
ROLE_NAME="ProHandelFivetranConnectorRole"
POLICY_NAME="ProHandelFivetranConnectorInvokePolicy"
ACCOUNT_ID="689864027744"
REGION="eu-central-1"
FUNCTION_NAME="ProHandelFivetranConnector"

echo "Creating policy to allow Lambda invocation..."
aws iam create-policy \
    --policy-name $POLICY_NAME \
    --policy-document file://fivetran-invoke-policy.json

echo "Attaching policy to role..."
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME

echo "Done! The Fivetran connector should now be able to invoke the Lambda function."

# Fixing IAM Permissions for Fivetran Lambda Connector

The error message you're seeing indicates that the IAM role `ProHandelFivetranConnectorRole` doesn't have the necessary permissions to invoke the Lambda function. Here's how to fix this issue:

## Option 1: Using the AWS CLI

If you have the AWS CLI configured, you can run the provided script:

```bash
./update-iam-permissions.sh
```

This script will create and attach the necessary policy to your IAM role.

## Option 2: Using the AWS Console

If you prefer to use the AWS Console, follow these steps:

1. Log in to the AWS Management Console
2. Navigate to the IAM service
3. Click on "Policies" in the left sidebar
4. Click "Create policy"
5. Select the JSON tab
6. Paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:eu-central-1:689864027744:function:ProHandelFivetranConnector"
        }
    ]
}
```

7. Click "Next"
8. Name the policy "ProHandelFivetranConnectorInvokePolicy"
9. Add a description: "Allows Fivetran to invoke the ProHandel Lambda connector"
10. Click "Create policy"
11. Navigate to "Roles" in the left sidebar
12. Find and click on "ProHandelFivetranConnectorRole"
13. Click on the "Permissions" tab
14. Click "Add permissions" and select "Attach policies"
15. Search for "ProHandelFivetranConnectorInvokePolicy"
16. Select the policy and click "Attach policies"

## Option 3: Update the Trust Relationship

Additionally, make sure the trust relationship for the role is correctly configured:

1. In the IAM console, navigate to the "ProHandelFivetranConnectorRole"
2. Click on the "Trust relationships" tab
3. Click "Edit trust relationship"
4. Ensure the policy includes both Lambda and Fivetran's account:

```json
{
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
                    "sts:ExternalId": "look_frescoes"
                }
            }
        }
    ]
}
```

5. Click "Update Trust Policy"

## After Making Changes

After making these changes, return to Fivetran and click "Save & Test" again to verify the connection works.

If you continue to experience issues, check the CloudWatch logs for your Lambda function to see if there are any other errors occurring.

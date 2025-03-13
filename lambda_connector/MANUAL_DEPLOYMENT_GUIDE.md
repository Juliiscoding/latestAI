# Manual Deployment Guide for ProHandel AWS Lambda Connector

Since we're having issues with the AWS CLI, this guide will walk you through manually deploying the Lambda function through the AWS Console.

## Step 1: Create the IAM Role

1. Log in to the AWS Management Console
2. Navigate to the IAM service
3. Click on "Roles" in the left sidebar
4. Click "Create role"
5. Select "AWS service" as the trusted entity type
6. Choose "Lambda" as the use case
7. Click "Next"
8. Search for and attach the following policies:
   - AWSLambdaBasicExecutionRole (for CloudWatch Logs)
   - AmazonS3ReadOnlyAccess (if you'll be using S3 for data transfer)
9. Click "Next"
10. Name the role "ProHandelFivetranConnectorRole"
11. Add a description: "Role for ProHandel Fivetran Lambda connector"
12. Click "Create role"

## Step 2: Update the Trust Relationship

1. Find and click on the newly created "ProHandelFivetranConnectorRole"
2. Go to the "Trust relationships" tab
3. Click "Edit trust relationship"
4. Replace the policy document with the contents of the `trust-policy.json` file:

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

## Step 3: Create the Lambda Function

1. Navigate to the Lambda service in the AWS Management Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Enter the following details:
   - Function name: "ProHandelFivetranConnector"
   - Runtime: Python 3.9
   - Architecture: x86_64
5. Under "Permissions", expand "Change default execution role"
6. Select "Use an existing role"
7. Choose "ProHandelFivetranConnectorRole" from the dropdown
8. Click "Create function"

## Step 4: Upload the Deployment Package

1. On the function page, scroll down to the "Code source" section
2. Click "Upload from" and select ".zip file"
3. Upload the `lambda_deployment.zip` file we created
4. Click "Save"

## Step 5: Configure the Lambda Function

1. Scroll down to the "Configuration" tab
2. Click on "General configuration" and click "Edit"
   - Set Memory to 256 MB
   - Set Timeout to 3 minutes (180 seconds)
   - Click "Save"
3. Click on "Environment variables" and click "Edit"
   - Add the following environment variables:
     - Key: PROHANDEL_API_KEY, Value: your_api_key
     - Key: PROHANDEL_API_SECRET, Value: your_api_secret
     - Key: PROHANDEL_AUTH_URL, Value: https://auth.prohandel.cloud/api/v4
     - Key: PROHANDEL_API_URL, Value: https://api.prohandel.de/api/v2
   - Click "Save"

## Step 6: Configure Fivetran

1. Log in to your Fivetran account
2. Create a new AWS Lambda connector
3. Configure the connector with:
   - External ID: "look_frescoes"
   - Role ARN: The ARN of the IAM role you created (format: arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole)
   - Lambda Function: The ARN of your Lambda function (format: arn:aws:lambda:eu-central-1:689864027744:function:ProHandelFivetranConnector)
   - Region: eu-central-1
   - Secrets:
     - api_key: Your ProHandel API key
     - api_secret: Your ProHandel API secret
     - api_url: The ProHandel API URL (https://linde.prohandel.de/api/v2)
   - Sync Method: "Sync directly" (or "Sync through S3 bucket" for larger datasets)

## Step 7: Test the Connection

1. In Fivetran, click "Save & Test"
2. Fivetran will test the connection to your Lambda function
3. If successful, you can proceed to set up the schema and start syncing data

## Troubleshooting

If you encounter issues:

1. Check CloudWatch Logs for Lambda function errors:
   - Navigate to CloudWatch in the AWS Console
   - Go to "Log groups"
   - Find and check the log group named "/aws/lambda/ProHandelFivetranConnector"

2. Test the Lambda function in the AWS Console:
   - On the Lambda function page, click "Test"
   - Create a new test event with the following JSON:
     ```json
     {
       "request": {
         "operation": "test",
         "secrets": {
           "api_key": "YOUR_API_KEY",
           "api_secret": "YOUR_API_SECRET",
           "api_url": "https://linde.prohandel.de/api/v2"
         }
       }
     }
     ```
   - Click "Test" to run the function and check the results

3. Verify IAM role permissions:
   - Make sure the trust relationship is correctly set up
   - Ensure the role has the necessary permissions for CloudWatch Logs and S3 (if used)

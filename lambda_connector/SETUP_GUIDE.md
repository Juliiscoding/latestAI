# ProHandel Fivetran AWS Lambda Connector Setup Guide

This guide will walk you through the process of setting up the ProHandel AWS Lambda connector for Fivetran integration.

## Prerequisites

1. AWS CLI installed and configured with your credentials
2. Python 3.9 or higher
3. pip package manager
4. Fivetran account with access to create connectors

## Step 1: Configure AWS CLI

If you haven't already configured AWS CLI, run:

```bash
aws configure
```

Enter your AWS Access Key ID, Secret Access Key, default region (eu-central-1), and output format (json).

## Step 2: Set Up IAM Role and Policy

Run the IAM setup script to create the necessary IAM role and policy:

```bash
cd /Users/juliusrechenbach/API\ ProHandelTest/lambda_connector
./setup-iam.sh
```

This script will:
- Create an IAM role named "ProHandelFivetranConnectorRole"
- Create an IAM policy named "ProHandelFivetranConnectorPolicy"
- Attach the policy to the role
- Display the Role ARN (you'll need this for Fivetran)

## Step 3: Deploy the Lambda Function

Run the deployment script to package and deploy the Lambda function:

```bash
cd /Users/juliusrechenbach/API\ ProHandelTest/lambda_connector
./deploy.sh
```

This script will:
- Create a deployment package with all dependencies
- Deploy the Lambda function to AWS
- Configure the function with appropriate settings

## Step 4: Configure Fivetran

1. Log in to your Fivetran account
2. Create a new AWS Lambda connector
3. Configure the connector with:
   - External ID: "look_frescoes"
   - Role ARN: The ARN displayed by the setup-iam.sh script
   - Lambda Function: The ARN of your Lambda function (format: arn:aws:lambda:eu-central-1:689864027744:function:ProHandelFivetranConnector)
   - Region: eu-central-1
   - Secrets:
     - api_key: Your ProHandel API key
     - api_secret: Your ProHandel API secret
     - api_url: The ProHandel API URL (https://linde.prohandel.de/api/v2)
   - Sync Method: "Sync directly" (or "Sync through S3 bucket" for larger datasets)

## Step 5: Test the Connection

1. In Fivetran, click "Save & Test"
2. Fivetran will test the connection to your Lambda function
3. If successful, you can proceed to set up the schema and start syncing data

## Troubleshooting

If you encounter issues:

1. Check CloudWatch Logs for Lambda function errors:
   ```bash
   aws logs describe-log-groups --log-group-name-prefix /aws/lambda/ProHandelFivetranConnector
   ```

2. Test the Lambda function locally:
   ```bash
   cd /Users/juliusrechenbach/API\ ProHandelTest/lambda_connector
   python test_lambda.py --operation test
   ```

3. Verify IAM role permissions:
   ```bash
   aws iam get-role --role-name ProHandelFivetranConnectorRole
   aws iam list-attached-role-policies --role-name ProHandelFivetranConnectorRole
   ```

## Additional Resources

- [Fivetran AWS Lambda Connector Documentation](https://fivetran.com/docs/connectors/functions/aws-lambda)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)

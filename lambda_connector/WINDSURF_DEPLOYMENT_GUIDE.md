# Windsurf Deployment Guide for ProHandel AWS Lambda Connector

This guide explains how to deploy the ProHandel AWS Lambda connector directly from the Windsurf terminal, without needing to use the AWS Console or Fivetran web interface.

## Prerequisites

1. AWS CLI (installed)
2. Python 3.9+ (installed)
3. Fivetran Python SDK (installed)
4. AWS credentials with administrator access
5. Fivetran API credentials

## Configuration

All configuration is stored in the `.env` file in the project root. Make sure the following variables are set:

```
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=eu-central-1
AWS_ACCOUNT_ID=689864027744

# Fivetran Configuration
FIVETRAN_API_KEY=your_fivetran_api_key
FIVETRAN_API_SECRET=your_fivetran_api_secret
FIVETRAN_EXTERNAL_ID=look_frescoes

# ProHandel Configuration
PROHANDEL_API_KEY=your_prohandel_api_key
PROHANDEL_API_SECRET=your_prohandel_api_secret
PROHANDEL_API_URL=https://linde.prohandel.de/api/v2
PROHANDEL_AUTH_URL=https://linde.prohandel.de/api/v2/auth
```

## Deployment

You can run the deployment script with various options:

### Full Deployment

To deploy everything (IAM role, Lambda function, and Fivetran connector):

```bash
cd /Users/juliusrechenbach/API\ ProHandelTest/lambda_connector
./deploy_all.py --aws-access-key $AWS_ACCESS_KEY_ID --aws-secret-key $AWS_SECRET_ACCESS_KEY
```

### Partial Deployment

You can skip certain steps if needed:

```bash
# Skip AWS credentials configuration (if already configured)
./deploy_all.py --skip-aws-config

# Skip IAM role creation (if already created)
./deploy_all.py --skip-iam

# Skip Lambda deployment (if already deployed)
./deploy_all.py --skip-lambda

# Skip Fivetran configuration (if already configured)
./deploy_all.py --skip-fivetran
```

### Update Lambda Function Only

To update just the Lambda function code:

```bash
./deploy_all.py --skip-aws-config --skip-iam --skip-fivetran
```

## Testing

After deployment, you can test the Lambda function locally:

```bash
cd /Users/juliusrechenbach/API\ ProHandelTest/lambda_connector
python test_lambda.py --operation test
```

Or test the entire pipeline:

```bash
python test_lambda.py --operation sync --state-days 30
```

## Troubleshooting

### AWS CLI Issues

If you encounter issues with the AWS CLI, you can verify your credentials:

```bash
/usr/local/bin/aws sts get-caller-identity
```

### Fivetran API Issues

If you encounter issues with the Fivetran API, you can test your credentials:

```python
import requests
auth = ("your_fivetran_api_key", "your_fivetran_api_secret")
response = requests.get("https://api.fivetran.com/v1/groups", auth=auth)
print(response.json())
```

### Lambda Function Issues

To check the Lambda function logs:

```bash
/usr/local/bin/aws logs describe-log-groups --log-group-name-prefix /aws/lambda/ProHandelFivetranConnector
```

To view the most recent log events:

```bash
/usr/local/bin/aws logs get-log-events --log-group-name /aws/lambda/ProHandelFivetranConnector --log-stream-name $(aws logs describe-log-streams --log-group-name /aws/lambda/ProHandelFivetranConnector --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text)
```

# Fix Lambda Permissions

The error message indicates that the IAM role `ProHandelFivetranConnectorRole` doesn't have permission to invoke the Lambda function. Here's how to fix it:

## Option 1: Add Permission Using AWS Console

1. Log in to the AWS Management Console
2. Navigate to the IAM service
3. Click on "Roles" in the left sidebar
4. Find and click on "ProHandelFivetranConnectorRole"
5. Click on the "Permissions" tab
6. Click "Add permissions" and select "Create inline policy"
7. Click on the "JSON" tab
8. Paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "lambda:InvokeFunction",
            "Resource": "arn:aws:lambda:eu-central-1:689864027744:function:prohandel-fivetran-connector"
        }
    ]
}
```

9. Click "Review policy"
10. Name the policy "LambdaInvokePermission"
11. Click "Create policy"

## Option 2: Add Permission Using AWS CLI

If you have AWS CLI configured, you can run the following command:

```bash
aws iam put-role-policy \
    --role-name ProHandelFivetranConnectorRole \
    --policy-name LambdaInvokePermission \
    --policy-document file://lambda_invoke_policy.json
```

## Option 3: Add Permission Using Lambda Console

You can also add permission directly from the Lambda function:

1. Navigate to the Lambda service in the AWS Management Console
2. Find and click on your "prohandel-fivetran-connector" function
3. Go to the "Configuration" tab
4. Click on "Permissions" in the left sidebar
5. Under "Resource-based policy statements", click "Add permissions"
6. Select "AWS account" for Principal
7. Enter the ARN of your IAM role: `arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole`
8. Select "lambda:InvokeFunction" for Action
9. Click "Save"

## Option 4: Fix Trust Relationship for Fivetran

The issue might also be related to the trust relationship. Make sure your role's trust relationship includes Fivetran's AWS account:

1. In the IAM console, go to the "ProHandelFivetranConnectorRole" role
2. Click on the "Trust relationships" tab
3. Click "Edit trust relationship"
4. Update the policy to include Fivetran's account:

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
          "sts:ExternalId": "armed_unleaded"
        }
      }
    }
  ]
}
```

5. Click "Update Trust Policy"

## Option 5: Update Lambda Function Code

If the Lambda function is not properly handling Fivetran requests, update it with our fixed version:

1. Navigate to the Lambda service in the AWS Management Console
2. Find and click on your "prohandel-fivetran-connector" function
3. In the "Code" tab, replace the code with the contents of `fixed_lambda_function.py`
4. Click "Deploy"

After making these changes, go back to Fivetran and click "Save & Test" again to retry the connection.

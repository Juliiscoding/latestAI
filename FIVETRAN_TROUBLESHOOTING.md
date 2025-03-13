# Fivetran Connector Troubleshooting Guide

This document outlines the issues we encountered when setting up the Fivetran connector for the ProHandel API and how we resolved them.

## Issue 1: Lambda Function Name Mismatch

**Error:**
```
Unable to access Lambda function
User: arn:aws:sts::689864027744:assumed-role/ProHandelFivetranConnectorRole/Fivetran-Session is not authorized to perform: lambda:InvokeFunction on resource: arn:aws:lambda:eu-central-1:689864027744:function:prohandel-connector
```

**Solution:**
- Updated the Lambda function ARN in the Fivetran configuration to use the correct function name: `prohandel-fivetran-connector`
- Updated the IAM policy to reference the correct Lambda function name

## Issue 2: IAM Permission Issues

**Error:**
```
Unable to access Lambda function
User: arn:aws:sts::689864027744:assumed-role/ProHandelFivetranConnectorRole/Fivetran-Session is not authorized to perform: lambda:InvokeFunction on resource: arn:aws:lambda:eu-central-1:689864027744:function:prohandel-fivetran-connector
```

**Solution:**
- Created an IAM policy that allows the `ProHandelFivetranConnectorRole` to invoke the Lambda function
- Added the policy to the IAM role using the AWS Management Console
- Updated the trust relationship to include Fivetran's AWS account (834469178297) with the correct external ID

## Issue 3: Lambda Function File System Access

**Error:**
```
Unable to access Lambda function
OSError : [Errno 30] Read-only file system: 'logs'
```

**Solution:**
- Modified the Lambda function to use the `/tmp` directory for logs, as it's the only writable location in AWS Lambda
- Created a helper function to redirect any paths starting with 'logs/' to '/tmp/logs/'

## Issue 4: Lambda Function Syntax Errors

**Error:**
```
Unable to access Lambda function
Runtime.UserCodeSyntaxError : Syntax error in module 'lambda_function': unexpected indent
```

**Solution:**
- Created a clean, simple Lambda function implementation from scratch
- Deployed the new implementation using a simple deployment script

## Issue 5: Lambda Function Event Structure Mismatch

**Error:**
```
Unable to access Lambda function
Unknown request type: 
```

**Solution:**
- Updated the Lambda function to correctly parse the Fivetran event structure
- Fixed the event parsing to extract operation and secrets directly from the event, not from a nested 'request' object
- Updated the response format to match what Fivetran expects ('success' instead of 'status')

## Diagnostic Tools

We've created several diagnostic tools to help troubleshoot issues:

1. **troubleshoot_lambda_connection.py**: Checks AWS credentials, IAM role, Lambda function, and tests invocation
2. **update_trust_policy.py**: Updates the IAM role's trust policy to include Fivetran's AWS account
3. **update_lambda_config.py**: Updates the Lambda function's timeout and memory settings
4. **test_lambda_fivetran.py**: Tests the Lambda function with proper Fivetran test and schema requests
5. **fixed_lambda_function.py**: A corrected Lambda function implementation that properly handles Fivetran requests

## Final Implementation

The final Lambda function implementation:
1. Creates a `/tmp/logs` directory for logging
2. Handles the Fivetran connector protocol (test, schema, sync)
3. Returns appropriate responses for each request type
4. Properly logs events and errors
5. Correctly parses Fivetran's event structure
6. Returns responses in the format Fivetran expects

## Next Steps

Now that the basic connection is working, you can enhance the Lambda function to:

1. Connect to the actual ProHandel API to fetch real data
2. Implement incremental loading based on timestamps
3. Add data validation and transformation
4. Expand the schema to include all relevant tables and fields
5. Implement error handling and retry mechanisms

## Maintenance

If you need to update the Lambda function in the future, you can use the `deploy_simple_lambda.py` script as a starting point.

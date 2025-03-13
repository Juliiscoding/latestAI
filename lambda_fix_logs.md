# Fix Lambda Function Logs Issue

We're now getting a different error:
```
OSError : [Errno 30] Read-only file system: 'logs'
```

This means your Lambda function is trying to write to a 'logs' directory in the root of the function, but Lambda's file system is read-only except for the `/tmp` directory.

## Option 1: Fix the Lambda Function Code

I've created a script that can automatically fix your Lambda function code to use the `/tmp` directory for logs:

```bash
pip install boto3
python fix_lambda_logs.py
```

This script will:
1. Download your Lambda function code
2. Find all references to the 'logs' directory
3. Replace them with '/tmp/logs'
4. Add code to create the '/tmp/logs' directory if it doesn't exist
5. Update your Lambda function with the fixed code

## Option 2: Manual Fix

If you prefer to fix the code manually:

1. Go to the AWS Lambda console
2. Open your `prohandel-fivetran-connector` function
3. Go to the "Code" tab
4. Find all references to the 'logs' directory
5. Replace them with '/tmp/logs'
6. Add the following code at the beginning of your handler function:
   ```python
   # Create logs directory in /tmp
   os.makedirs('/tmp/logs', exist_ok=True)
   ```
7. Click "Deploy" to update your function

## Option 3: Add a Layer with Writable Directories

You can also add a Lambda layer that provides a writable directory structure:

1. Create a new layer with a directory structure that includes a 'logs' directory
2. Configure your Lambda function to use this layer
3. Update your code to use the layer's path for logs

After fixing the logs issue, go back to Fivetran and click "Save & Test" again to retry the connection.

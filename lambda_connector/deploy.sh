#!/bin/bash
# Script to package and deploy the ProHandel Lambda function

# Set environment variables for deployment
FUNCTION_NAME="prohandel-fivetran-connector"
ROLE_ARN="arn:aws:iam::689864027744:role/ProHandelFivetranConnectorRole"
REGION="eu-central-1"
MEMORY_SIZE=256
TIMEOUT=180
AWS_CLI="python3 ./aws-cli.py"

# Create a temporary directory for the deployment package
mkdir -p build

# Copy the Lambda function code
cp lambda_function.py build/
cp -r ../etl build/
cp data_enhancer.py build/

# Install dependencies
pip install -r requirements.txt -t build/

# Create a zip file
cd build
zip -r ../deployment-package.zip .
cd ..

# Check if the Lambda function exists
echo "Checking if Lambda function exists..."
if $AWS_CLI lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>&1 | grep -q "Function not found"; then
    echo "Creating new Lambda function..."
    $AWS_CLI lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.9 \
        --role $ROLE_ARN \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://deployment-package.zip \
        --timeout $TIMEOUT \
        --memory-size $MEMORY_SIZE \
        --region $REGION \
        --environment Variables="{PROHANDEL_AUTH_URL=https://auth.prohandel.cloud/api/v4,PROHANDEL_API_URL=https://api.prohandel.de/api/v2}"
else
    echo "Updating existing Lambda function..."
    $AWS_CLI lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://deployment-package.zip \
        --region $REGION

    # Update environment variables
    $AWS_CLI lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --environment Variables="{PROHANDEL_AUTH_URL=https://auth.prohandel.cloud/api/v4,PROHANDEL_API_URL=https://api.prohandel.de/api/v2}" \
        --region $REGION
fi

# Clean up
rm -rf build
rm deployment-package.zip

echo "Deployment completed!"

#!/bin/bash
# Deployment script for ProHandel Lambda function

# Set variables
LAMBDA_NAME="prohandel-fivetran-connector"
REGION="eu-central-1"
ACCOUNT_ID="689864027744"  # From memory
ROLE_NAME="prohandel-lambda-role"
ZIP_FILE="lambda_package.zip"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting deployment of ProHandel Lambda function...${NC}"

# Create deployment package
echo -e "${YELLOW}Creating deployment package...${NC}"
cd lambda_connector
pip install -r requirements.txt -t ./package
cp -r *.py ./package/
cd package
zip -r ../${ZIP_FILE} .
cd ..
rm -rf package

# Check if Lambda function exists
echo -e "${YELLOW}Checking if Lambda function exists...${NC}"
if aws lambda get-function --function-name ${LAMBDA_NAME} --region ${REGION} 2>&1 | grep -q "Function not found"; then
    # Create Lambda function
    echo -e "${YELLOW}Creating new Lambda function...${NC}"
    aws lambda create-function \
        --function-name ${LAMBDA_NAME} \
        --runtime python3.9 \
        --handler lambda_function.lambda_handler \
        --role arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME} \
        --zip-file fileb://${ZIP_FILE} \
        --timeout 180 \
        --memory-size 256 \
        --region ${REGION} \
        --environment Variables="{PROHANDEL_API_URL=https://auth.prohandel.cloud/api/v4,PROHANDEL_USERNAME=$PROHANDEL_USERNAME,PROHANDEL_PASSWORD=$PROHANDEL_PASSWORD}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Lambda function created successfully!${NC}"
    else
        echo -e "${RED}Failed to create Lambda function!${NC}"
        exit 1
    fi
else
    # Update Lambda function
    echo -e "${YELLOW}Updating existing Lambda function...${NC}"
    aws lambda update-function-code \
        --function-name ${LAMBDA_NAME} \
        --zip-file fileb://${ZIP_FILE} \
        --region ${REGION}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Lambda function updated successfully!${NC}"
    else
        echo -e "${RED}Failed to update Lambda function!${NC}"
        exit 1
    fi
    
    # Update environment variables
    echo -e "${YELLOW}Updating environment variables...${NC}"
    aws lambda update-function-configuration \
        --function-name ${LAMBDA_NAME} \
        --environment Variables="{PROHANDEL_API_URL=https://auth.prohandel.cloud/api/v4,PROHANDEL_USERNAME=$PROHANDEL_USERNAME,PROHANDEL_PASSWORD=$PROHANDEL_PASSWORD}" \
        --region ${REGION}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Environment variables updated successfully!${NC}"
    else
        echo -e "${RED}Failed to update environment variables!${NC}"
        exit 1
    fi
fi

# Clean up
echo -e "${YELLOW}Cleaning up...${NC}"
rm ${ZIP_FILE}

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}Lambda function ARN: arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${LAMBDA_NAME}${NC}"
echo -e "${YELLOW}Use this ARN in your Fivetran AWS Lambda connector configuration.${NC}"

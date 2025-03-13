#!/bin/bash
# Script to set up IAM role for ProHandel Lambda function

# Set variables
ROLE_NAME="prohandel-lambda-role"
POLICY_NAME="prohandel-lambda-policy"
REGION="eu-central-1"
ACCOUNT_ID="689864027744"  # From memory

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up IAM role for ProHandel Lambda function...${NC}"

# Create trust policy document
echo -e "${YELLOW}Creating trust policy...${NC}"
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create IAM role
echo -e "${YELLOW}Creating IAM role...${NC}"
aws iam create-role \
    --role-name ${ROLE_NAME} \
    --assume-role-policy-document file://trust-policy.json

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Role may already exist, continuing...${NC}"
fi

# Create policy document
echo -e "${YELLOW}Creating policy document...${NC}"
cat > lambda-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:ProHandel*"
    }
  ]
}
EOF

# Create policy
echo -e "${YELLOW}Creating IAM policy...${NC}"
aws iam create-policy \
    --policy-name ${POLICY_NAME} \
    --policy-document file://lambda-policy.json

# Check if policy creation was successful
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Policy may already exist, retrieving ARN...${NC}"
    POLICY_ARN=$(aws iam list-policies --query "Policies[?PolicyName=='${POLICY_NAME}'].Arn" --output text)
else
    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"
fi

# Attach policy to role
echo -e "${YELLOW}Attaching policy to role...${NC}"
aws iam attach-role-policy \
    --role-name ${ROLE_NAME} \
    --policy-arn ${POLICY_ARN}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Successfully attached policy to role!${NC}"
else
    echo -e "${RED}Failed to attach policy to role!${NC}"
    exit 1
fi

# Attach AWS managed policy for Lambda basic execution
echo -e "${YELLOW}Attaching AWSLambdaBasicExecutionRole...${NC}"
aws iam attach-role-policy \
    --role-name ${ROLE_NAME} \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Successfully attached AWSLambdaBasicExecutionRole!${NC}"
else
    echo -e "${RED}Failed to attach AWSLambdaBasicExecutionRole!${NC}"
    exit 1
fi

# Clean up
echo -e "${YELLOW}Cleaning up...${NC}"
rm trust-policy.json lambda-policy.json

echo -e "${GREEN}IAM role setup completed successfully!${NC}"
echo -e "${YELLOW}Role ARN: arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}${NC}"

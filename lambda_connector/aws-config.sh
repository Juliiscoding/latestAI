#!/bin/bash

# This script will configure AWS CLI with your credentials

echo "Configuring AWS CLI..."
/usr/local/bin/aws configure set aws_access_key_id YOUR_AWS_ACCESS_KEY
/usr/local/bin/aws configure set aws_secret_access_key YOUR_AWS_SECRET_KEY
/usr/local/bin/aws configure set region eu-central-1
/usr/local/bin/aws configure set output json

echo "AWS CLI configuration complete!"

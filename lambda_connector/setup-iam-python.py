#!/usr/bin/env python3
import os
import json
import subprocess
import time

# Set variables
ROLE_NAME = "ProHandelFivetranConnectorRole"
POLICY_NAME = "ProHandelFivetranConnectorPolicy"
REGION = "eu-central-1"  # Change to your AWS region
AWS_ACCOUNT_ID = "689864027744"

# Read trust policy
with open('trust-policy.json', 'r') as f:
    trust_policy = f.read()

# Read lambda policy
with open('lambda-policy.json', 'r') as f:
    lambda_policy = f.read()

# Create the IAM role with trust policy
print("Creating IAM role...")
subprocess.run(["python3", "-m", "awscli", "iam", "create-role", 
                "--role-name", ROLE_NAME, 
                "--assume-role-policy-document", trust_policy])

# Create the IAM policy
print("Creating IAM policy...")
subprocess.run(["python3", "-m", "awscli", "iam", "create-policy", 
                "--policy-name", POLICY_NAME, 
                "--policy-document", lambda_policy])

# Attach the policy to the role
print("Attaching policy to role...")
subprocess.run(["python3", "-m", "awscli", "iam", "attach-role-policy", 
                "--role-name", ROLE_NAME, 
                "--policy-arn", f"arn:aws:iam::{AWS_ACCOUNT_ID}:policy/{POLICY_NAME}"])

# Wait for role to propagate
print("Waiting for role to propagate...")
time.sleep(10)

print("IAM setup completed!")
print(f"Role ARN: arn:aws:iam::{AWS_ACCOUNT_ID}:role/{ROLE_NAME}")

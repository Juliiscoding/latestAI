#!/usr/bin/env python3
"""
Debug script for environment variables.
"""
import os
from dotenv import load_dotenv

print("Before loading .env:")
print(f"PROHANDEL_AUTH_URL: {os.getenv('PROHANDEL_AUTH_URL')}")
print(f"PROHANDEL_API_URL: {os.getenv('PROHANDEL_API_URL')}")

# Load .env file
print("\nLoading .env file...")
load_dotenv()

print("\nAfter loading .env:")
print(f"PROHANDEL_AUTH_URL: {os.getenv('PROHANDEL_AUTH_URL')}")
print(f"PROHANDEL_API_URL: {os.getenv('PROHANDEL_API_URL')}")

# Try loading with override
print("\nLoading .env file with override...")
load_dotenv(override=True)

print("\nAfter loading .env with override:")
print(f"PROHANDEL_AUTH_URL: {os.getenv('PROHANDEL_AUTH_URL')}")
print(f"PROHANDEL_API_URL: {os.getenv('PROHANDEL_API_URL')}")

# Print the content of the .env file
print("\nContent of .env file:")
with open(".env", "r") as f:
    for line in f:
        if "PROHANDEL_AUTH_URL" in line or "PROHANDEL_API_URL" in line:
            print(line.strip())

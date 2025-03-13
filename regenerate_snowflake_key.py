#!/usr/bin/env python3
"""
Script to regenerate a properly formatted RSA key pair for Snowflake authentication.
This script follows Snowflake's documentation precisely to ensure compatibility.
"""

import os
import sys
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Output directory for the keys
KEY_DIR = "/Users/juliusrechenbach/.ssh/snowflake"
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "rsa_key.p8")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "rsa_key.pub")
PUBLIC_KEY_SQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "updated_register_key.sql")

def main():
    print(f"Regenerating Snowflake RSA key pair...")
    
    # Create directory if it doesn't exist
    if not os.path.exists(KEY_DIR):
        os.makedirs(KEY_DIR)
        print(f"Created directory: {KEY_DIR}")
    
    # Generate private key
    print("Generating 2048-bit RSA key pair...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Get public key in PEM format
    public_key = private_key.public_key()
    
    # Save private key in PKCS8 format (required by Snowflake)
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open(PRIVATE_KEY_PATH, 'wb') as f:
        f.write(private_key_bytes)
    print(f"Private key saved to: {PRIVATE_KEY_PATH}")
    
    # Save public key in PEM format for reference
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open(PUBLIC_KEY_PATH, 'wb') as f:
        f.write(public_key_pem)
    print(f"Public key saved to: {PUBLIC_KEY_PATH}")
    
    # Get public key in DER format and encode with base64 for Snowflake
    public_key_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_key_b64 = base64.b64encode(public_key_der).decode('utf-8')
    
    # Create SQL script to register the public key
    sql_script = f"""-- SQL script to register the updated public key with Snowflake
-- Run this script in the Snowflake web interface

-- Store the public key in a variable
SET PUBLIC_KEY = '{public_key_b64}';

-- Alter the user to add the public key
ALTER USER JULIUSRECHENBACH SET RSA_PUBLIC_KEY = $PUBLIC_KEY;

-- Verify the key was added correctly
DESCRIBE USER JULIUSRECHENBACH;

-- Optional: Set a comment to remember when the key was added
ALTER USER JULIUSRECHENBACH SET COMMENT = 'RSA key regenerated on 2025-03-11 for automated access';
"""
    
    with open(PUBLIC_KEY_SQL_PATH, 'w') as f:
        f.write(sql_script)
    print(f"SQL script to register public key saved to: {PUBLIC_KEY_SQL_PATH}")
    
    # Print verification information
    print("\n=== Key Generation Complete ===")
    print(f"Private key format: PKCS8 DER (Snowflake required format)")
    print(f"Private key path: {PRIVATE_KEY_PATH}")
    print(f"Public key path: {PUBLIC_KEY_PATH}")
    print(f"SQL script path: {PUBLIC_KEY_SQL_PATH}")
    print("\nNext steps:")
    print("1. Run the SQL script in Snowflake to register the new public key")
    print("2. Test the connection with the snowflake_key_auth_test.py script")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("Error generating key pair")
        sys.exit(1)
    else:
        print("\nKey pair generation successful!")
        sys.exit(0)

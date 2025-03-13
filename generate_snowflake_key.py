#!/usr/bin/env python3
"""
Script to generate a properly formatted RSA key pair for Snowflake authentication.
This script generates both the private key in PKCS8 DER format and the public key in the format
required by Snowflake.
"""

import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Directory to store the keys
KEY_DIR = "/Users/juliusrechenbach/.ssh/snowflake"

def generate_key_pair():
    """Generate a new RSA key pair suitable for Snowflake authentication"""
    # Create the directory if it doesn't exist
    os.makedirs(KEY_DIR, exist_ok=True)
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Save private key in PKCS8 format (required by Snowflake)
    private_key_path = os.path.join(KEY_DIR, "rsa_key.p8")
    with open(private_key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    print(f"Private key saved to: {private_key_path}")
    
    # Get public key in PEM format
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Save public key
    public_key_path = os.path.join(KEY_DIR, "rsa_key.pub")
    with open(public_key_path, "wb") as f:
        f.write(public_key_pem)
    print(f"Public key saved to: {public_key_path}")
    
    # Extract the public key in the format required by Snowflake
    # Snowflake requires the public key in a specific format for the ALTER USER command
    public_key_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Skip the first 24 bytes which contain the header
    snowflake_public_key = base64.b64encode(public_key_der).decode('utf-8')
    
    # Save the Snowflake-formatted public key to a file
    snowflake_key_path = os.path.join(KEY_DIR, "rsa_key.snowflake")
    with open(snowflake_key_path, "w") as f:
        f.write(snowflake_public_key)
    print(f"Snowflake-formatted public key saved to: {snowflake_key_path}")
    
    # Generate SQL command for registering the key in Snowflake
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "register_snowflake_key.sql")
    with open(sql_path, "w") as f:
        f.write("-- SQL script to register the public key with Snowflake\n")
        f.write("-- Run this script in the Snowflake web interface\n\n")
        f.write("-- Store the public key in a variable\n")
        f.write(f"SET PUBLIC_KEY = '{snowflake_public_key}';\n\n")
        f.write("-- Alter the user to add the public key\n")
        f.write("ALTER USER JULIUSRECHENBACH SET RSA_PUBLIC_KEY = $PUBLIC_KEY;\n\n")
        f.write("-- Verify the key was added correctly\n")
        f.write("DESCRIBE USER JULIUSRECHENBACH;\n\n")
        f.write("-- Optional: Set a comment to remember when the key was added\n")
        f.write("ALTER USER JULIUSRECHENBACH SET COMMENT = 'RSA key added on 2025-03-11 for automated access';\n")
    print(f"SQL script for registering the key saved to: {sql_path}")
    
    return private_key_path, public_key_path, snowflake_key_path

if __name__ == "__main__":
    private_key_path, public_key_path, snowflake_key_path = generate_key_pair()
    print("\nKey pair generation complete!")
    print("\nNext steps:")
    print("1. Log into the Snowflake web interface")
    print("2. Run the SQL commands in register_snowflake_key.sql to register your public key")
    print("3. Update your profiles.yml file with the path to the private key")
    print("4. Test the connection using the test_snowflake_connection.py script")

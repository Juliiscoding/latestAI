# Snowflake Key Pair Authentication Guide

## Overview
This guide explains how to use key pair authentication with Snowflake to bypass Duo Security prompts and enable automated access for the Mercurios.ai project.

## Prerequisites
- Access to Snowflake with ACCOUNTADMIN or SECURITYADMIN role
- OpenSSL installed on your machine

## Setup Steps

### 1. Key Pair Generation (Completed)
We've already generated the key pair:
- Private key: `/Users/juliusrechenbach/.ssh/snowflake/rsa_key.p8`
- Public key: `/Users/juliusrechenbach/.ssh/snowflake/rsa_key.pub`

### 2. Register Public Key with Snowflake
1. Log in to Snowflake web interface
2. Run the SQL in `updated_register_key.sql`:
   ```sql
   -- Store the public key in a variable
   SET PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAigSCRH1CBN/WCnGdTtMpi1Tqt1Td5SC43EiIy8OZGHZOEEAe/fyfDBhQtXB3qRhHj9X6SrWJxazODW6/N+rOg4iyxPM3E0c00eRfv8VzTrWetpC6gMEbfDA28daTEmjG8cLnIQrpD6pCX0A+VoP1FSBna7Xa5NKVIqej1ILkdNspIJddJ6fi6HFQXr1pUW00K1Q8dmaGWcYKDKcn87rBsB0Yx65B+bQ4bpzGugLShoVOxLRRP1C3cD8jEO5pd2fqoiX7WhMcudvvhE/KDnCsFrzPR911NR8ndKeVPQS3Wd3LG9JM3edjf8ax4cByegbxkf6EGB+WVXRzsqHegYhBMwIDAQAB';

   -- Alter the user to add the public key
   ALTER USER JULIUSRECHENBACH SET RSA_PUBLIC_KEY = $PUBLIC_KEY;
   ```

3. Verify the key was registered:
   ```sql
   DESCRIBE USER JULIUSRECHENBACH;
   ```

## Troubleshooting

If you're encountering "JWT token is invalid" errors, try these solutions:

### 1. Check Account Identifier Format
The account identifier might need to include the region. Try these formats:

```python
# Option 1: Original format
ACCOUNT = "VRXDFZX-ZZ95717"

# Option 2: With organization
ACCOUNT = "VRXDFZX-ZZ95717.snowflakecomputing.com"

# Option 3: With region
ACCOUNT = "eu-central-1.VRXDFZX-ZZ95717"
```

### 2. Verify Private Key Format
Snowflake requires the private key to be in PKCS8 DER format. You can check the format with:

```bash
openssl asn1parse -inform der -in /Users/juliusrechenbach/.ssh/snowflake/rsa_key.p8
```

If this command fails, the key may not be in the correct format. Regenerate it using:

```bash
python regenerate_snowflake_key.py
```

### 3. Test with Password Authentication
To verify other connection parameters, try connecting with password authentication:

```python
conn = snowflake.connector.connect(
    user="JULIUSRECHENBACH",
    password="your_password",
    account="VRXDFZX-ZZ95717",
    warehouse="MERCURIOS_DEV_WH",
    database="MERCURIOS_DATA",
    role="MERCURIOS_DEVELOPER"
)
```

### 4. Check for Typos in Account Name
Verify the exact account identifier in the Snowflake web interface URL:
- The URL format is: `https://<account-identifier>.snowflakecomputing.com`
- Extract the account identifier from this URL

### 5. Verify User Privileges
Ensure your user has the necessary privileges:

```sql
SHOW GRANTS TO USER JULIUSRECHENBACH;
```

### 6. Alternative Connection Method
Try using a connection string instead:

```python
conn = snowflake.connector.connect(
    connection_string="snowflake://JULIUSRECHENBACH@VRXDFZX-ZZ95717/?privateKey=path/to/rsa_key.p8&warehouse=MERCURIOS_DEV_WH&role=MERCURIOS_DEVELOPER"
)
```

## Next Steps After Authentication Works

1. Apply performance optimizations:
   ```bash
   python apply_snowflake_optimizations.py
   ```

2. Set up BI tool connections:
   ```bash
   python setup_bi_connections.py --tool tableau
   ```

3. Run dbt models:
   ```bash
   ./run_dbt_models.sh
   ```

-- SQL script to register the updated public key with Snowflake
-- Run this script in the Snowflake web interface

-- Store the public key in a variable
SET PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAigSCRH1CBN/WCnGdTtMpi1Tqt1Td5SC43EiIy8OZGHZOEEAe/fyfDBhQtXB3qRhHj9X6SrWJxazODW6/N+rOg4iyxPM3E0c00eRfv8VzTrWetpC6gMEbfDA28daTEmjG8cLnIQrpD6pCX0A+VoP1FSBna7Xa5NKVIqej1ILkdNspIJddJ6fi6HFQXr1pUW00K1Q8dmaGWcYKDKcn87rBsB0Yx65B+bQ4bpzGugLShoVOxLRRP1C3cD8jEO5pd2fqoiX7WhMcudvvhE/KDnCsFrzPR911NR8ndKeVPQS3Wd3LG9JM3edjf8ax4cByegbxkf6EGB+WVXRzsqHegYhBMwIDAQAB';

-- Alter the user to add the public key
ALTER USER JULIUSRECHENBACH SET RSA_PUBLIC_KEY = $PUBLIC_KEY;

-- Verify the key was added correctly
DESCRIBE USER JULIUSRECHENBACH;

-- Optional: Set a comment to remember when the key was added
ALTER USER JULIUSRECHENBACH SET COMMENT = 'RSA key regenerated on 2025-03-11 for automated access';

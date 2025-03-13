-- SQL script to register the public key with Snowflake
-- Run this script in the Snowflake web interface

-- Store the public key in a variable
SET PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtaW2VY3aSVhVL+0IlI8pOw2WMTxmUvnWUDEfLeMPqx6jiuK8BToJr1c/LYvHPK684M0HmTp1Hmo79bsQ2W0b22H6pVj0c5jmNeF7Vs7GXbvZlbxN9v1LtViKLTX6MvwpsO/CoHsAoprQJyoJCQSplxYMsk2yO1YEdxiTSD4QiZeKB6VlybivBmVAU2QMpi+Vk5KZfDhnFiWNyRqnBTBuo5lxV6YZselWeY8dAW4EJxTuqx7SXcUQLjDFIRv+T6Z6UQZjcEJ1y5kZ7qArQxMka5c1cUyZzexh7gbQ+gpyCjHX6OC0eyAHLFELvtTqkLbquxKXOFbgTo/YSo9XLFmYKQIDAQAB';

-- Alter the user to add the public key
ALTER USER JULIUSRECHENBACH SET RSA_PUBLIC_KEY = $PUBLIC_KEY;

-- Verify the key was added correctly
DESCRIBE USER JULIUSRECHENBACH;

-- Optional: Set a comment to remember when the key was added
ALTER USER JULIUSRECHENBACH SET COMMENT = 'RSA key added on 2025-03-11 for automated access';

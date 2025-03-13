-- Simple Fix for Snowflake Access Issues
-- This script provides a minimal approach to fix access issues

-- Step 1: Use ACCOUNTADMIN role for all operations
USE ROLE ACCOUNTADMIN;

-- Step 2: Grant the Fivetran service role to your user
-- This is the most critical step as the error shows your user doesn't have this role
GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER JULIUSRECHENBACH;

-- Step 3: Test access to Fivetran schemas
-- Switch to the Fivetran service role
USE ROLE MERCURIOS_FIVETRAN_SERVICE;

-- Show all schemas in the database
SHOW SCHEMAS IN DATABASE MERCURIOS_DATA;

-- Try to access Google Analytics 4 schema
USE SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4;
SHOW TABLES;

-- Try to access Klaviyo schema
USE SCHEMA MERCURIOS_DATA.KLAVIYO;
SHOW TABLES;

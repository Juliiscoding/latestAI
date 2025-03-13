-- Direct Access Fix for Snowflake
-- This script provides the most direct solution based on the schema information

-- Step 1: Use ACCOUNTADMIN role for all operations
USE ROLE ACCOUNTADMIN;

-- Step 2: Grant the Fivetran service role directly to your user
-- This is the most critical step as this role owns all the Fivetran schemas
GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER JULIUSRECHENBACH;

-- Step 3: Test access by switching to the Fivetran service role
USE ROLE MERCURIOS_FIVETRAN_SERVICE;

-- Step 4: Verify access to each schema
-- Google Analytics 4
USE SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4;
SHOW TABLES;

-- Klaviyo
USE SCHEMA MERCURIOS_DATA.KLAVIYO;
SHOW TABLES;

-- Klaviyo_Klaviyo
USE SCHEMA MERCURIOS_DATA.KLAVIYO_KLAVIYO;
SHOW TABLES;

-- Fivetran Metadata
USE SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA;
SHOW TABLES;

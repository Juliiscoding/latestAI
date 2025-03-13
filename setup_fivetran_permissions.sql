-- Setup Fivetran Service Account Permissions
-- Run this script with ACCOUNTADMIN privileges

-- 1. Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS MERCURIOS_DATA;

-- 2. Create warehouse if it doesn't exist
CREATE WAREHOUSE IF NOT EXISTS MERCURIOS_LOADING_WH
WITH WAREHOUSE_SIZE = 'XSMALL'
AUTO_SUSPEND = 300
AUTO_RESUME = TRUE;

-- 3. Create schemas if they don't exist
USE DATABASE MERCURIOS_DATA;
CREATE SCHEMA IF NOT EXISTS RAW;
CREATE SCHEMA IF NOT EXISTS STANDARD;
CREATE SCHEMA IF NOT EXISTS ANALYTICS;

-- 4. Create role if it doesn't exist
CREATE ROLE IF NOT EXISTS MERCURIOS_FIVETRAN_SERVICE;

-- 5. Grant warehouse privileges
GRANT USAGE ON WAREHOUSE MERCURIOS_LOADING_WH TO ROLE MERCURIOS_FIVETRAN_SERVICE;

-- 6. Grant database privileges
GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_FIVETRAN_SERVICE;

-- 7. Grant schema privileges
GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT CREATE TABLE, CREATE VIEW, CREATE STAGE, CREATE PIPE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT SELECT ON ALL VIEWS IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.STANDARD TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA MERCURIOS_DATA.STANDARD TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_FIVETRAN_SERVICE;

-- 8. Create future grants for new objects
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.STANDARD TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA MERCURIOS_DATA.STANDARD TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT SELECT, INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_FIVETRAN_SERVICE;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_FIVETRAN_SERVICE;

-- 9. Grant role to users
GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER FIVETRAN_USER;
GRANT ROLE MERCURIOS_FIVETRAN_SERVICE TO USER JULIUSRECHENBACH;  -- For testing purposes

-- 10. Set default role for FIVETRAN_USER
ALTER USER FIVETRAN_USER SET DEFAULT_ROLE = MERCURIOS_FIVETRAN_SERVICE;

-- 11. Create a procedure for setting tenant context (if needed)
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.ANALYTICS.SET_TENANT_CONTEXT(TENANT_ID VARCHAR)
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    // Store tenant ID in session variable
    var sql_command = "SET SESSION_CONTEXT('TENANT_ID' = '" + TENANT_ID + "')";
    snowflake.execute({sqlText: sql_command});
    return "Tenant context set to: " + TENANT_ID;
$$;

-- 12. Grant execute on procedure
GRANT USAGE ON PROCEDURE MERCURIOS_DATA.ANALYTICS.SET_TENANT_CONTEXT(VARCHAR) TO ROLE MERCURIOS_FIVETRAN_SERVICE;

-- Verify setup
SELECT 'Setup complete. Please verify permissions by connecting with the FIVETRAN_USER account.';

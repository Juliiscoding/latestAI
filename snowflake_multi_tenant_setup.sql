-- Snowflake Multi-Tenant Setup for Mercurios.ai
-- This script sets up the foundation for a scalable multi-tenant architecture in Snowflake

-- Step 1: Create roles for different access patterns
USE ROLE SECURITYADMIN;

-- Create role for dbt transformations
CREATE ROLE IF NOT EXISTS MERCURIOS_DBT_ROLE;
GRANT ROLE MERCURIOS_DBT_ROLE TO ROLE MERCURIOS_ADMIN;
GRANT ROLE MERCURIOS_DBT_ROLE TO USER JULIUSRECHENBACH;

-- Create role for API access
CREATE ROLE IF NOT EXISTS MERCURIOS_API_ROLE;
GRANT ROLE MERCURIOS_API_ROLE TO ROLE MERCURIOS_ADMIN;

-- Create role for read-only analytics
CREATE ROLE IF NOT EXISTS MERCURIOS_ANALYTICS_ROLE;
GRANT ROLE MERCURIOS_ANALYTICS_ROLE TO ROLE MERCURIOS_ADMIN;
GRANT ROLE MERCURIOS_ANALYTICS_ROLE TO ROLE MERCURIOS_ANALYST;

-- Step 2: Set up warehouse configuration
USE ROLE SYSADMIN;

-- Create separate warehouses for different workloads
CREATE WAREHOUSE IF NOT EXISTS MERCURIOS_TRANSFORM_WH
  WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for dbt transformations';

CREATE WAREHOUSE IF NOT EXISTS MERCURIOS_API_WH
  WAREHOUSE_SIZE = 'SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for API queries';

CREATE WAREHOUSE IF NOT EXISTS MERCURIOS_ANALYTICS_WH
  WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Warehouse for analytics queries';

-- Grant usage on warehouses to appropriate roles
GRANT USAGE ON WAREHOUSE MERCURIOS_TRANSFORM_WH TO ROLE MERCURIOS_DBT_ROLE;
GRANT USAGE ON WAREHOUSE MERCURIOS_API_WH TO ROLE MERCURIOS_API_ROLE;
GRANT USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH TO ROLE MERCURIOS_ANALYTICS_ROLE;

-- Step 3: Set up database structure for multi-tenant architecture
USE ROLE SYSADMIN;

-- Create schemas for transformed data
USE DATABASE MERCURIOS_DATA;

-- Schema for staging data (output of dbt staging models)
CREATE SCHEMA IF NOT EXISTS STAGING;

-- Schema for intermediate data (output of dbt intermediate models)
CREATE SCHEMA IF NOT EXISTS INTERMEDIATE;

-- Schema for analytics data (output of dbt marts models)
CREATE SCHEMA IF NOT EXISTS ANALYTICS;

-- Step 4: Grant permissions to roles
USE ROLE SECURITYADMIN;

-- Grant permissions to dbt role
GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_DBT_ROLE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_DBT_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_DBT_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_DBT_ROLE;

-- Grant permissions on Fivetran schemas
GRANT USAGE ON SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_DBT_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_DBT_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_DBT_ROLE;

GRANT USAGE ON SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_DBT_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_DBT_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_DBT_ROLE;

-- Grant permissions on output schemas
GRANT USAGE ON SCHEMA MERCURIOS_DATA.STAGING TO ROLE MERCURIOS_DBT_ROLE;
GRANT CREATE TABLE ON SCHEMA MERCURIOS_DATA.STAGING TO ROLE MERCURIOS_DBT_ROLE;
GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.STAGING TO ROLE MERCURIOS_DBT_ROLE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.INTERMEDIATE TO ROLE MERCURIOS_DBT_ROLE;
GRANT CREATE TABLE ON SCHEMA MERCURIOS_DATA.INTERMEDIATE TO ROLE MERCURIOS_DBT_ROLE;
GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.INTERMEDIATE TO ROLE MERCURIOS_DBT_ROLE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_DBT_ROLE;
GRANT CREATE TABLE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_DBT_ROLE;
GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_DBT_ROLE;

-- Grant permissions to API role
GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_API_ROLE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_API_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_API_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_API_ROLE;

-- Grant permissions to analytics role
GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_ANALYTICS_ROLE;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_ANALYTICS_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_ANALYTICS_ROLE;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.ANALYTICS TO ROLE MERCURIOS_ANALYTICS_ROLE;

-- Step 5: Create a secure function for tenant isolation
USE ROLE ACCOUNTADMIN;

-- Create a UDF to get the current tenant ID (for row-level security)
CREATE OR REPLACE FUNCTION MERCURIOS_DATA.PUBLIC.CURRENT_TENANT_ID()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
SELECT CURRENT_SESSION_PROPERTY('app.current_tenant_id')
$$;

-- Create a secure view example with row-level security
CREATE OR REPLACE SECURE VIEW MERCURIOS_DATA.ANALYTICS.TENANT_SALES AS
SELECT 
    s.*
FROM 
    MERCURIOS_DATA.RAW.SALES s
WHERE 
    s.tenant_id = MERCURIOS_DATA.PUBLIC.CURRENT_TENANT_ID();

-- Step 6: Create a stored procedure to set the tenant context
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.PUBLIC.SET_TENANT_CONTEXT(TENANT_ID VARCHAR)
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
EXECUTE AS CALLER
AS
$$
try {
    var sql = `ALTER SESSION SET app.current_tenant_id = '${TENANT_ID}'`;
    snowflake.execute({sqlText: sql});
    return "Tenant context set to: " + TENANT_ID;
} catch (err) {
    return "Error setting tenant context: " + err;
}
$$;

-- Example of how to use the tenant context
-- CALL MERCURIOS_DATA.PUBLIC.SET_TENANT_CONTEXT('tenant1');
-- SELECT * FROM MERCURIOS_DATA.ANALYTICS.TENANT_SALES;

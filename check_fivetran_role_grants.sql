-- Check Fivetran Role Grants
-- This script checks what roles the Fivetran service role has been granted to

-- Show all roles
SHOW ROLES;

-- Check grants of Fivetran service role
SHOW GRANTS OF ROLE MERCURIOS_FIVETRAN_SERVICE;

-- Check grants to Fivetran service role
SHOW GRANTS TO ROLE MERCURIOS_FIVETRAN_SERVICE;

-- List all schemas in the database
SHOW SCHEMAS IN DATABASE MERCURIOS_DATA;

-- Check grants on specific schemas
SHOW GRANTS ON SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4;
SHOW GRANTS ON SCHEMA MERCURIOS_DATA.KLAVIYO;
SHOW GRANTS ON SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA;

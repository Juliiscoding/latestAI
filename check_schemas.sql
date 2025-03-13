-- Check if schemas exist in the database
USE ROLE ACCOUNTADMIN;
USE DATABASE MERCURIOS_DATA;

-- Show all schemas in the database
SHOW SCHEMAS IN DATABASE MERCURIOS_DATA;

-- Check if the Fivetran service role exists
SHOW ROLES LIKE 'MERCURIOS_FIVETRAN_SERVICE';

-- Check what roles are granted to your user
SHOW GRANTS TO USER JULIUSRECHENBACH;

-- Check what privileges the Fivetran service role has
SHOW GRANTS TO ROLE MERCURIOS_FIVETRAN_SERVICE;

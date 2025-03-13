-- SQL script to configure Fivetran PostgreSQL connector network rule
-- Run this as ACCOUNTADMIN role in Snowflake

BEGIN;
    SET application_name = 'FIVETRAN_POSTGRESQL';
    SET network_rule = concat($application_name, '_APP_DATA.CONFIGURATION.', $application_name, '_CONSUMER_EXTERNAL_ACCESS_NETWORK_RULE');
    
    -- Replace the PostgreSQL database address and port with your actual values
    -- Example: '123.123.123.123:5432' for a standard PostgreSQL installation
    ALTER NETWORK RULE identifier($network_rule) SET VALUE_LIST=('0.0.0.0:443','0.0.0.0:80','your-postgres-host.example.com:5432');
COMMIT;

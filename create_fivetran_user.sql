-- Script to create or reset the FIVETRAN_USER account
-- Run this with ACCOUNTADMIN privileges

-- Check if FIVETRAN_USER exists
SHOW USERS LIKE 'FIVETRAN_USER';

-- Create FIVETRAN_USER if it doesn't exist
CREATE USER IF NOT EXISTS FIVETRAN_USER
  PASSWORD = 'YourStrongPassword123!'  -- Replace with a secure password
  DEFAULT_ROLE = MERCURIOS_FIVETRAN_SERVICE
  DEFAULT_WAREHOUSE = MERCURIOS_LOADING_WH
  COMMENT = 'Service account for Fivetran data integration';

-- Reset password if user already exists
-- Uncomment the line below if you need to reset the password
-- ALTER USER FIVETRAN_USER SET PASSWORD = 'YourStrongPassword123!';  -- Replace with a secure password

-- Verify FIVETRAN_USER exists
SHOW USERS LIKE 'FIVETRAN_USER';

-- Update your .env file with this new password
SELECT 'Remember to update your .env file with the new password for FIVETRAN_USER';

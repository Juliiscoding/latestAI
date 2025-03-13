-- Configure Snowflake authentication settings to reduce Duo MFA prompts
-- This script extends session timeouts and configures network policies

-- Use admin role to make these changes
USE ROLE ACCOUNTADMIN;

-- Set longer session timeout (8 hours instead of default)
ALTER ACCOUNT SET SESSION_TIMEOUT_MINS = 480;

-- Set client session keepalive to true (prevents timeout during idle periods)
ALTER ACCOUNT SET CLIENT_SESSION_KEEP_ALIVE = TRUE;

-- Create or modify network policy to allow longer session persistence
-- First check if a policy already exists
SHOW NETWORK POLICIES;

-- Create a new network policy with extended timeout if needed
-- (Comment this out if you already have a policy and modify the existing one instead)
CREATE OR REPLACE NETWORK POLICY MERCURIOS_NETWORK_POLICY
  ALLOWED_IP_LIST = ('0.0.0.0/0')  -- Allow all IPs, modify as needed for security
  BLOCKED_IP_LIST = ()
  COMMENT = 'Network policy with extended timeouts for Mercurios development';

-- Apply the network policy to your account
ALTER ACCOUNT SET NETWORK_POLICY = MERCURIOS_NETWORK_POLICY;

-- Configure MFA policy to reduce prompts
-- This sets MFA to be required only once per 8 hours (instead of per session)
ALTER ACCOUNT SET MULTI_FACTOR_AUTHENTICATION_POLICY = 'REQUIRED_ONCE_PER_DAY';

-- You can also set this for specific users if needed
-- ALTER USER JULIUSRECHENBACH SET MULTI_FACTOR_AUTHENTICATION_POLICY = 'REQUIRED_ONCE_PER_DAY';

-- Verify the changes
SHOW PARAMETERS LIKE 'SESSION_TIMEOUT%' IN ACCOUNT;
SHOW PARAMETERS LIKE 'CLIENT_SESSION%' IN ACCOUNT;
SHOW PARAMETERS LIKE 'MULTI_FACTOR%' IN ACCOUNT;

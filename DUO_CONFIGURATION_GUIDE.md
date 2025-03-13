# Duo Authentication Configuration Guide for Snowflake

## Problem
Frequent Duo authentication prompts during Snowflake operations are disrupting workflow efficiency, requiring multiple approvals within short time periods.

## Solutions

### Option 1: Modify Duo Settings (Recommended)
Contact your Duo administrator to adjust the following settings:

1. **Increase Remember Me Duration**:
   - In the Duo Admin Panel, go to `Applications` → `Protect an Application` → `Snowflake`
   - Increase the "Remember user for" setting from the default (typically 24 hours) to a longer period (e.g., 7 days)
   - This will reduce the frequency of authentication prompts

2. **Enable Remembered Devices**:
   - Enable the "Remember devices" option in the Duo application settings
   - This allows trusted devices to require less frequent authentication

3. **Adjust Session Lifetime**:
   - Modify the "New enrollment" and "Authentication" lifetime settings
   - Recommended: Set to at least 8 hours for development environments

### Option 2: Snowflake Configuration Changes
When you regain access to Snowflake, execute these commands as ACCOUNTADMIN:

```sql
-- Extend session timeout
ALTER ACCOUNT SET SESSION_TIMEOUT_MINS = 480;

-- Enable session keepalive
ALTER ACCOUNT SET CLIENT_SESSION_KEEP_ALIVE = TRUE;

-- Modify MFA policy (if your admin allows it)
ALTER ACCOUNT SET MULTI_FACTOR_AUTHENTICATION_POLICY = 'REQUIRED_ONCE_PER_DAY';
```

### Option 3: Use Snowflake Connection Parameters
Modify your dbt profiles.yml file to include these connection parameters:

```yaml
dev:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: vrxdfzx-zz95717
      user: JULIUSRECHENBACH
      password: "{{ env_var('DBT_PASSWORD') }}"
      role: MERCURIOS_DEVELOPER
      database: MERCURIOS_DATA
      warehouse: MERCURIOS_DEV_WH
      schema: staging
      threads: 4
      client_session_keep_alive: true  # Keeps session alive
      reuse_connections: true          # Reuses connections to reduce auth prompts
      authenticator: externalbrowser   # Optional: Use browser auth instead of Duo
```

### Option 4: Use Snowflake SnowSQL Config File
Create or modify ~/.snowsql/config with these settings:

```
[connections]
accountname = vrxdfzx-zz95717
username = JULIUSRECHENBACH
rolename = MERCURIOS_DEVELOPER
warehousename = MERCURIOS_DEV_WH
dbname = MERCURIOS_DATA
schemaname = staging

[parameters]
CLIENT_SESSION_KEEP_ALIVE = True
MULTI_FACTOR_AUTHENTICATION_POLICY = REQUIRED_ONCE_PER_DAY
```

## Immediate Workaround
While waiting for configuration changes, you can:

1. Use a single terminal session for all Snowflake operations
2. Run multiple commands in a single session
3. Use the Snowflake web interface for longer operations

## Contact Information
For Duo Security administration assistance, contact your organization's IT security team.

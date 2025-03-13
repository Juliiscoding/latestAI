# Snowflake Role Access Guide for Mercurios AI

## Current Access Situation

Based on our testing, we've identified the following access issues:

1. **ACCOUNTADMIN Role**:
   - Has access to `FIVETRAN_METADATA`, `PUBLIC`, and `RAW` schemas
   - Does NOT have access to `GOOGLE_ANALYTICS_4`, `KLAVIYO`, or `FIVETRAN_ARMED_UNLEADED_STAGING` schemas

2. **MERCURIOS_ADMIN Role**:
   - Has access to `RAW` schema only
   - Does NOT have access to any other schemas

3. **MERCURIOS_ANALYST Role**:
   - Does NOT have access to any schemas

4. **MERCURIOS_DEVELOPER Role**:
   - Has access to `RAW` schema only
   - Does NOT have access to any other schemas

## Resolving the Access Issues

### Option 1: Execute SQL Grants (Recommended)

The most comprehensive solution is to run the SQL grants in the `grant_snowflake_access.sql` file. This will:

1. Grant appropriate access to all roles
2. Set up future grants for new tables
3. Establish proper role hierarchy

**Steps to execute**:

1. Log in to Snowflake web interface as ACCOUNTADMIN
2. Open a worksheet
3. Copy and paste the contents of `grant_snowflake_access.sql`
4. Execute the SQL statements

### Option 2: Use the Snowflake Web Interface

If you prefer using the UI:

1. Log in to Snowflake web interface as ACCOUNTADMIN
2. Navigate to "Account" > "Access Management" > "Grants"
3. For each schema:
   - Select the schema
   - Click "Grant Privileges"
   - Select the role (MERCURIOS_ADMIN, MERCURIOS_ANALYST, etc.)
   - Grant "USAGE" privilege
   - Grant "SELECT" on all tables

### Option 3: Contact Fivetran Support

If you continue to have issues, contact Fivetran support to:

1. Verify the connector setup is correct
2. Ensure proper role permissions are granted
3. Check if there are any issues with the data sync

## Understanding Snowflake Role Hierarchy

Snowflake uses a hierarchical role model:

```
ACCOUNTADMIN
    |
    ├── SECURITYADMIN
    |       |
    |       └── USERADMIN
    |
    └── SYSADMIN
            |
            └── Custom Roles (MERCURIOS_ADMIN, etc.)
```

The ACCOUNTADMIN role is the most powerful and should be used sparingly. For day-to-day operations, use the MERCURIOS_ADMIN or MERCURIOS_ANALYST roles.

## Checking Access After Grants

After executing the grants, run the `test_snowflake_roles.py` script again to verify access:

```bash
python test_snowflake_roles.py
```

## Troubleshooting Common Issues

1. **"Object does not exist" errors**:
   - This usually means the role doesn't have USAGE privilege on the schema
   - Solution: Grant USAGE on the schema to the role

2. **"Insufficient privileges" errors**:
   - This means the role can see the object but doesn't have permission to use it
   - Solution: Grant appropriate privileges (SELECT, INSERT, etc.) on the object

3. **Missing schemas**:
   - If schemas like GOOGLE_ANALYTICS_4 aren't visible, they may not have been created yet
   - Solution: Wait for Fivetran to complete the initial sync (24-48 hours)

4. **Empty tables**:
   - If tables exist but have no data, the sync may still be in progress
   - Solution: Check Fivetran connector status and wait for completion

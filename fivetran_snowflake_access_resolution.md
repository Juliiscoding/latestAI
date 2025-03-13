# Resolving Fivetran-Snowflake Access Issues for Mercurios AI

## Summary of Current Access Issues

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

## Root Causes and Solutions

### 1. Missing Imported Privileges

**Issue**: The most likely cause is that the roles don't have the `IMPORTED PRIVILEGES` grant, which is required for accessing Fivetran-managed schemas.

**Solution**:
```sql
-- Run as ACCOUNTADMIN
GRANT IMPORTED PRIVILEGES ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_ADMIN;
GRANT IMPORTED PRIVILEGES ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_ANALYST;
GRANT IMPORTED PRIVILEGES ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_DEVELOPER;
```

### 2. Fivetran Connector Configuration

**Issue**: The Fivetran connector may not be properly configured to share data with your roles.

**Solution**:
1. Log in to Fivetran
2. Navigate to your connector settings
3. Under "Destination" > "Schema" ensure that:
   - The correct database (`MERCURIOS_DATA`) is selected
   - Schema names are correctly set (`GOOGLE_ANALYTICS_4`, `KLAVIYO`)
   - Share access with roles is enabled

### 3. Initial Sync Not Complete

**Issue**: If the Fivetran connector is newly set up, the initial sync may not be complete.

**Solution**:
1. Check the sync status in Fivetran
2. Wait for the initial sync to complete (can take 24-48 hours for large datasets)
3. Verify that tables are being created in the Snowflake schemas

## Step-by-Step Resolution Plan

### Step 1: Verify Schema Existence

First, verify that the schemas actually exist in the database:

```sql
-- Run as ACCOUNTADMIN
SHOW SCHEMAS IN DATABASE MERCURIOS_DATA;
```

### Step 2: Grant Imported Privileges

Grant the necessary imported privileges to your roles:

```sql
-- Run as ACCOUNTADMIN
GRANT IMPORTED PRIVILEGES ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_ADMIN;
GRANT IMPORTED PRIVILEGES ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_ANALYST;
GRANT IMPORTED PRIVILEGES ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_DEVELOPER;
```

### Step 3: Grant Direct Schema Access

Grant direct access to the schemas:

```sql
-- Run as ACCOUNTADMIN
GRANT USAGE ON SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_ADMIN;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_ADMIN;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.FIVETRAN_ARMED_UNLEADED_STAGING TO ROLE MERCURIOS_ADMIN;

-- For analysts
GRANT USAGE ON SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_ANALYST;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_ANALYST;
```

### Step 4: Grant Table Access

Grant access to all tables in the schemas:

```sql
-- Run as ACCOUNTADMIN
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_ADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_ADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.FIVETRAN_ARMED_UNLEADED_STAGING TO ROLE MERCURIOS_ADMIN;

-- For analysts
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_ANALYST;
```

### Step 5: Grant Future Access

Grant access to future tables that will be created:

```sql
-- Run as ACCOUNTADMIN
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_ADMIN;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_ADMIN;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.FIVETRAN_ARMED_UNLEADED_STAGING TO ROLE MERCURIOS_ADMIN;

-- For analysts
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.GOOGLE_ANALYTICS_4 TO ROLE MERCURIOS_ANALYST;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.KLAVIYO TO ROLE MERCURIOS_ANALYST;
```

## Contacting Fivetran Support

If the above steps don't resolve the issue, contact Fivetran support with the following information:

1. Your Fivetran account ID
2. Connector names (GA4, Klaviyo)
3. Snowflake account identifier (`VRXDFZX-ZZ95717`)
4. Error messages encountered
5. Roles you're trying to grant access to

## Verifying Resolution

After implementing the solutions, run the `test_snowflake_roles.py` script again to verify access:

```bash
python test_snowflake_roles.py
```

If access is still restricted, you may need to:

1. Check if the schemas are being created with a different naming convention
2. Verify that the Fivetran service account has the necessary permissions
3. Check if there are any policy-based access controls in place

## Understanding Fivetran-Snowflake Integration

Fivetran creates and manages schemas in your Snowflake account. The key components are:

1. **Connector**: The data source (GA4, Klaviyo)
2. **Destination**: Your Snowflake account
3. **Schema**: Where the data is stored (GOOGLE_ANALYTICS_4, KLAVIYO)
4. **Transformation**: Optional SQL transformations on the data

Access to Fivetran-managed schemas requires:

1. **IMPORTED PRIVILEGES**: Grants access to objects created by the Fivetran service account
2. **USAGE**: Permission to see and access the schema
3. **SELECT**: Permission to query tables in the schema

## Next Steps After Resolving Access

Once access is resolved:

1. Explore the GA4 and Klaviyo data structure
2. Create views or materialized views for simplified access
3. Set up regular reporting and dashboards
4. Integrate with your existing data pipeline

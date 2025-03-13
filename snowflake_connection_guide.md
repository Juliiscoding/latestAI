# Snowflake Connection Guide for Mercurios AI

## Connection Details

Based on our exploration, here are the confirmed Snowflake connection details:

- **Account Identifier**: `VRXDFZX-ZZ95717`
- **Username**: `JULIUSRECHENBACH`
- **Role**: `ACCOUNTADMIN`
- **Warehouse**: `COMPUTE_WH`
- **Database**: `MERCURIOS_DATA` (not `MERCURIOS` as initially thought)

## Available Data

We've confirmed the following data is available in your Snowflake instance:

1. **Fivetran Metadata**:
   - Contains information about your Fivetran connectors, logs, and transformations
   - Located in the `FIVETRAN_METADATA` schema

2. **RAW Data**:
   - Contains tables for `ARTICLES`, `CUSTOMERS`, and `ORDERS`
   - Located in the `RAW` schema
   - Currently these tables appear to be empty (0 rows)

3. **Google Analytics 4**:
   - Schema exists (`GOOGLE_ANALYTICS_4`)
   - We don't have direct access to this schema with the current role
   - Data is likely still being synced from BigQuery

4. **Klaviyo**:
   - Schema exists (`KLAVIYO`)
   - We don't have direct access to this schema with the current role

## Connection Methods

### 1. Python Connection

```python
import snowflake.connector

# Connect to Snowflake
conn = snowflake.connector.connect(
    user='JULIUSRECHENBACH',
    password='your_password',  # Replace with your actual password
    account='VRXDFZX-ZZ95717',
    role='ACCOUNTADMIN',
    warehouse='COMPUTE_WH',
    database='MERCURIOS_DATA'
)

# Create a cursor object
cur = conn.cursor()

# Execute a query
cur.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES LIMIT 10")
results = cur.fetchall()

# Close the connection
cur.close()
conn.close()
```

### 2. Snowflake CLI

If you have the Snowflake CLI installed, you can connect using:

```bash
snowsql -a VRXDFZX-ZZ95717 -u JULIUSRECHENBACH -r ACCOUNTADMIN -w COMPUTE_WH -d MERCURIOS_DATA
```

### 3. JDBC/ODBC Connection

For BI tools like Tableau, Power BI, or Looker, use these connection parameters:

- **JDBC URL**: `jdbc:snowflake://VRXDFZX-ZZ95717.snowflakecomputing.com/?warehouse=COMPUTE_WH&db=MERCURIOS_DATA`
- **ODBC DSN**: Configure with the same parameters as above

## Next Steps

1. **Wait for Data Sync**:
   - The GA4 data is still being synced from BigQuery to Snowflake
   - This typically takes 24-48 hours for the initial sync

2. **Request Additional Permissions**:
   - You currently don't have access to the Fivetran-managed schemas
   - Contact your Snowflake administrator to grant access to:
     - `GOOGLE_ANALYTICS_4` schema
     - `KLAVIYO` schema
     - `FIVETRAN_ARMED_UNLEADED_STAGING` schema

3. **Create Analysis Views**:
   - Once you have access, create views in the `ANALYTICS` schema that join data across sources
   - This will allow you to analyze customer behavior across channels

## Troubleshooting

If you continue to have connection issues:

1. **Verify Network Access**:
   - Ensure your network allows connections to Snowflake (port 443)
   - Check if a VPN is required

2. **Check Credentials**:
   - Verify your password is correct
   - Check if MFA is enabled for your account

3. **Role Permissions**:
   - Try using a different role if available
   - Request additional grants from your Snowflake administrator

# Mercurios.ai Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the Mercurios.ai Predictive Inventory Management system with Snowflake data quality monitoring. The implementation includes:

1. Setting up Snowflake monitoring infrastructure
2. Running dbt models for inventory optimization
3. Configuring data quality checks
4. Implementing multi-tenant data isolation

## Prerequisites

- Snowflake account with admin privileges
- dbt CLI installed
- Fivetran account configured with ProHandel connector
- Enriables set up for credentials
vironment va
## 1. Snowflake Setup

### 1.1 Fix Snowflake Permissions

Create a file named `fix_snowflake_permissions.sql` with the following content:

```sql
-- Run as ACCOUNTADMIN
USE ROLE ACCOUNTADMIN;

-- Grant necessary privileges to MERCURIOS_DEVELOPER role
GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE MERCURIOS_DEVELOPER;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_DEVELOPER;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.STAGING TO ROLE MERCURIOS_DEVELOPER;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.INTERMEDIATE TO ROLE MERCURIOS_DEVELOPER;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.MARTS TO ROLE MERCURIOS_DEVELOPER;

-- Grant read privileges on source data
GRANT SELECT ON ALL TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_DEVELOPER;
GRANT SELECT ON FUTURE TABLES IN SCHEMA MERCURIOS_DATA.RAW TO ROLE MERCURIOS_DEVELOPER;

-- Grant write privileges on target schemas
GRANT CREATE TABLE ON SCHEMA MERCURIOS_DATA.STAGING TO ROLE MERCURIOS_DEVELOPER;
GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.STAGING TO ROLE MERCURIOS_DEVELOPER;
GRANT CREATE TABLE ON SCHEMA MERCURIOS_DATA.INTERMEDIATE TO ROLE MERCURIOS_DEVELOPER;
GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.INTERMEDIATE TO ROLE MERCURIOS_DEVELOPER;
GRANT CREATE TABLE ON SCHEMA MERCURIOS_DATA.MARTS TO ROLE MERCURIOS_DEVELOPER;
GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.MARTS TO ROLE MERCURIOS_DEVELOPER;

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE MERCURIOS_DEV_WH TO ROLE MERCURIOS_DEVELOPER;

-- Create monitoring schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS MERCURIOS_DATA.MONITORING;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_DEVELOPER;
GRANT CREATE TABLE ON SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_DEVELOPER;
GRANT CREATE VIEW ON SCHEMA MERCURIOS_DATA.MONITORING TO ROLE MERCURIOS_DEVELOPER;
```

Execute this script using SnowSQL:

```bash
snowsql -a VRXDFZX-ZZ95717 -u JULIUSRECHENBACH -d MERCURIOS_DATA -r ACCOUNTADMIN -f fix_snowflake_permissions.sql
```

### 1.2 Set Up Monitoring Schema

Run the `setup_monitoring_schema.sql` script we created to set up the monitoring infrastructure:

```bash
snowsql -a VRXDFZX-ZZ95717 -u JULIUSRECHENBACH -d MERCURIOS_DATA -r MERCURIOS_ADMIN -f setup_monitoring_schema.sql
```

## 2. dbt Implementation

### 2.1 Configure Environment Variables

Create a `.env.dbt` file with the following content:

```
export DBT_PASSWORD="cajkik-4gunha-datweJ"
export DBT_USER="JULIUSRECHENBACH"
export DBT_ACCOUNT="VRXDFZX-ZZ95717"
export DBT_DATABASE="MERCURIOS_DATA"
export DBT_WAREHOUSE="MERCURIOS_DEV_WH"
export DBT_ROLE="MERCURIOS_DEVELOPER"
```

Source the environment variables:

```bash
source .env.dbt
```

### 2.2 Run dbt Models

Navigate to the dbt project directory and run the models:

```bash
cd dbt_mercurios
dbt run
```

This will execute all the dbt models we've created:
- Staging models for articles, inventory, and sales
- Intermediate models for inventory metrics
- Mart models for inventory status, stock levels, reorder recommendations, and demand forecasting
- Multi-tenant inventory dashboard

## 3. Data Quality Monitoring

### 3.1 Configure Data Quality Checks

Update the `snowflake_data_quality_config.json` file with the following content:

```json
{
  "connection": {
    "account": "VRXDFZX-ZZ95717",
    "user": "JULIUSRECHENBACH",
    "password": "${SNOWFLAKE_PASSWORD}",
    "warehouse": "MERCURIOS_ANALYTICS_WH",
    "database": "MERCURIOS_DATA",
    "schema": "RAW"
  },
  "tables": [
    {
      "name": "PROHANDEL_ARTICLES",
      "checks": [
        {"type": "record_count", "min_count": 1},
        {"type": "null_check", "columns": ["ARTICLE_ID", "ARTICLE_NUMBER", "DESCRIPTION"]},
        {"type": "duplicate_check", "columns": ["ARTICLE_ID"]},
        {"type": "value_range", "column": "PURCHASE_PRICE", "min_value": 0},
        {"type": "value_range", "column": "RETAIL_PRICE", "min_value": 0}
      ]
    },
    {
      "name": "PROHANDEL_INVENTORY",
      "checks": [
        {"type": "record_count", "min_count": 1},
        {"type": "null_check", "columns": ["INVENTORY_ID", "ARTICLE_ID", "WAREHOUSE_ID"]},
        {"type": "duplicate_check", "columns": ["INVENTORY_ID"]},
        {"type": "value_range", "column": "QUANTITY", "min_value": 0},
        {"type": "referential_integrity", "column": "ARTICLE_ID", "ref_table": "PROHANDEL_ARTICLES", "ref_column": "ARTICLE_ID"}
      ]
    },
    {
      "name": "PROHANDEL_SALES",
      "checks": [
        {"type": "record_count", "min_count": 1},
        {"type": "null_check", "columns": ["SALE_ID", "ARTICLE_ID", "SALE_DATE"]},
        {"type": "duplicate_check", "columns": ["SALE_ID"]},
        {"type": "value_range", "column": "QUANTITY", "min_value": 1},
        {"type": "value_range", "column": "REVENUE", "min_value": 0},
        {"type": "referential_integrity", "column": "ARTICLE_ID", "ref_table": "PROHANDEL_ARTICLES", "ref_column": "ARTICLE_ID"},
        {"type": "freshness_check", "date_column": "SALE_DATE", "max_days_old": 7}
      ]
    }
  ],
  "notification": {
    "email": {
      "enabled": true,
      "recipients": ["alerts@mercurios.ai"],
      "smtp_server": "smtp.mercurios.ai",
      "smtp_port": 587,
      "smtp_username": "${SMTP_USERNAME}",
      "smtp_password": "${SMTP_PASSWORD}",
      "from_address": "data-quality@mercurios.ai"
    },
    "slack": {
      "enabled": true,
      "webhook_url": "${SLACK_WEBHOOK_URL}",
      "channel": "#data-quality-alerts"
    }
  },
  "reporting": {
    "output_dir": "./reports",
    "formats": ["json", "html"],
    "save_to_database": true,
    "database_table": "MERCURIOS_DATA.MONITORING.DATA_QUALITY_ISSUES"
  }
}
```

### 3.2 Run Data Quality Monitoring

Execute the data quality monitoring script:

```bash
python snowflake_data_quality_monitor.py
```

## 4. Multi-Tenant Implementation

### 4.1 Row-Level Security Setup

Create a file named `setup_row_level_security.sql` with the following content:

```sql
-- Run as ACCOUNTADMIN
USE ROLE ACCOUNTADMIN;
USE DATABASE MERCURIOS_DATA;

-- Create secure view for multi-tenant access to inventory dashboard
CREATE OR REPLACE SECURE VIEW MARTS.TENANT_INVENTORY_DASHBOARD_SECURE AS
SELECT * FROM MARTS.TENANT_INVENTORY_DASHBOARD
WHERE TENANT_ID = CURRENT_SESSION_PROPERTY('app.tenant_id');

-- Create role for each tenant
CREATE ROLE IF NOT EXISTS TENANT_MERCURIOS;
GRANT USAGE ON DATABASE MERCURIOS_DATA TO ROLE TENANT_MERCURIOS;
GRANT USAGE ON SCHEMA MERCURIOS_DATA.MARTS TO ROLE TENANT_MERCURIOS;
GRANT SELECT ON VIEW MERCURIOS_DATA.MARTS.TENANT_INVENTORY_DASHBOARD_SECURE TO ROLE TENANT_MERCURIOS;
GRANT USAGE ON WAREHOUSE MERCURIOS_ANALYTICS_WH TO ROLE TENANT_MERCURIOS;

-- Create session policy for tenant isolation
CREATE OR REPLACE SESSION POLICY TENANT_ISOLATION
    SESSION_PARAMETERS = (
        APP.TENANT_ID = NULL
    );

-- Apply session policy to tenant role
ALTER ROLE TENANT_MERCURIOS SET SESSION POLICY TENANT_ISOLATION;

-- Create stored procedure to set tenant context
CREATE OR REPLACE PROCEDURE SET_TENANT_CONTEXT(TENANT_ID STRING)
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
    snowflake.execute({sqlText: `ALTER SESSION SET APP.TENANT_ID = '${TENANT_ID}'`});
    return "Tenant context set to: " + TENANT_ID;
$$;

-- Grant execute permission on the procedure
GRANT USAGE ON PROCEDURE SET_TENANT_CONTEXT(STRING) TO ROLE TENANT_MERCURIOS;
```

Execute this script using SnowSQL:

```bash
snowsql -a VRXDFZX-ZZ95717 -u JULIUSRECHENBACH -d MERCURIOS_DATA -r ACCOUNTADMIN -f setup_row_level_security.sql
```

## 5. Cost Optimization

### 5.1 Warehouse Configuration

Create a file named `optimize_warehouses.sql` with the following content:

```sql
-- Run as ACCOUNTADMIN
USE ROLE ACCOUNTADMIN;

-- Optimize ETL warehouse
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Optimize development warehouse
ALTER WAREHOUSE MERCURIOS_DEV_WH SET 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Optimize analytics warehouse with scaling
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET 
    WAREHOUSE_SIZE = 'SMALL'
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 3
    SCALING_POLICY = 'STANDARD'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Create resource monitor
CREATE OR REPLACE RESOURCE MONITOR MERCURIOS_MONITOR
WITH CREDIT_QUOTA = 100
FREQUENCY = MONTHLY
START_TIMESTAMP = IMMEDIATELY
TRIGGERS
    ON 75 PERCENT DO NOTIFY
    ON 90 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND;

-- Apply resource monitor to warehouses
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = MERCURIOS_MONITOR;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = MERCURIOS_MONITOR;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = MERCURIOS_MONITOR;
```

Execute this script using SnowSQL:

```bash
snowsql -a VRXDFZX-ZZ95717 -u JULIUSRECHENBACH -d MERCURIOS_DATA -r ACCOUNTADMIN -f optimize_warehouses.sql
```

## 6. Scheduled Jobs

### 6.1 Data Quality Monitoring Schedule

Create a cron job to run the data quality monitoring script daily:

```bash
# Add to crontab
0 1 * * * cd /path/to/project && python snowflake_data_quality_monitor.py
```

### 6.2 dbt Model Refresh Schedule

Create a cron job to refresh the dbt models daily:

```bash
# Add to crontab
0 2 * * * cd /path/to/project/dbt_mercurios && source ../.env.dbt && dbt run
```

## 7. Verification and Testing

### 7.1 Verify Data Quality Monitoring

Check that the data quality monitoring is working by examining the issues table:

```sql
SELECT * FROM MERCURIOS_DATA.MONITORING.DATA_QUALITY_ISSUES
ORDER BY TIMESTAMP DESC
LIMIT 10;
```

### 7.2 Verify dbt Models

Check that the dbt models have been created successfully:

```sql
-- Check inventory status
SELECT COUNT(*) FROM MERCURIOS_DATA.MARTS.INVENTORY_STATUS;

-- Check reorder recommendations
SELECT COUNT(*) FROM MERCURIOS_DATA.MARTS.REORDER_RECOMMENDATIONS;

-- Check demand forecast
SELECT COUNT(*) FROM MERCURIOS_DATA.MARTS.DEMAND_FORECAST;

-- Check multi-tenant dashboard
SELECT COUNT(*) FROM MERCURIOS_DATA.MARTS.TENANT_INVENTORY_DASHBOARD;
```

## 8. Troubleshooting

### 8.1 Snowflake Connection Issues

If you encounter connection issues with Snowflake:

1. Verify your credentials in the `.env` file
2. Check that your IP is whitelisted in Snowflake
3. Ensure that your Snowflake account is active

### 8.2 dbt Run Failures

If dbt runs fail:

1. Check the logs for specific error messages
2. Verify that the schemas referenced in your models exist
3. Ensure that your role has the necessary permissions

### 8.3 Data Quality Monitoring Issues

If data quality monitoring fails:

1. Check that the tables specified in the configuration exist
2. Verify that your role has SELECT privileges on those tables
3. Ensure that the notification settings are correctly configured

## 9. Next Steps

After successful implementation, consider these next steps:

1. **Advanced Analytics**: Implement more sophisticated forecasting models using Snowflake's machine learning capabilities
2. **Dashboard Integration**: Connect your BI tool (e.g., Tableau, Power BI) to the mart models
3. **Automated Actions**: Set up automated purchase order generation based on reorder recommendations
4. **Additional Data Sources**: Integrate additional data sources like Google Analytics for enhanced demand forecasting
5. **Performance Optimization**: Implement clustering keys and materialized views for frequently accessed data

## 10. Contact Support

For assistance with implementation, contact:
- Technical Support: support@mercurios.ai
- Snowflake Specialist: snowflake@mercurios.ai

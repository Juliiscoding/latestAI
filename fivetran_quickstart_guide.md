# Fivetran Quickstart Data Model Guide

## Overview

The Fivetran Quickstart Data Model for metadata provides pre-built transformations that help you monitor and analyze your Fivetran connectors without writing custom dbt code. This guide explains how to implement and use these models within the Mercurios.ai architecture.

## Benefits for Mercurios.ai

1. **Monitoring Dashboard Foundation**: These models provide the foundation for monitoring your data pipelines, which is critical for a multi-tenant SaaS platform.

2. **Integration with Architecture**: The models fit perfectly into the Data Transformation layer of your architecture, providing standardized views of connector health and performance.

3. **Accelerated Development**: By using these pre-built models, you can focus on developing your retail-specific transformations while having robust monitoring in place.

4. **Multi-Tenant Visibility**: The models help you track the health of connectors across all your tenants.

## Implementation Steps

### 1. Wait for Initial Sync to Complete

Before implementing the Quickstart Data Model, ensure that the initial sync of the metadata connector has completed. You can check this by:

```sql
-- Check if the schema exists
SHOW SCHEMAS LIKE 'FIVETRAN_METADATA' IN DATABASE MERCURIOS_DATA;

-- Check if tables have data
SELECT COUNT(*) FROM MERCURIOS_DATA.FIVETRAN_METADATA.CONNECTOR;
```

### 2. Add the Quickstart Data Model

Once the initial sync is complete:

1. Navigate to the Fivetran dashboard
2. Select the metadata connector
3. Go to the "Transformations" tab
4. Click "Add quickstart data model"
5. Review the model details and click "Add"

### 3. Monitor the Model Deployment

The model will be deployed and will start transforming your data. You can monitor its status in the Transformations tab.

### 4. Access the Transformed Data

Once deployed, you can access the transformed data in Snowflake:

```sql
-- List all views and tables created by the model
SHOW VIEWS IN SCHEMA MERCURIOS_DATA.FIVETRAN_LOG;

-- Example queries
SELECT * FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS;
SELECT * FROM MERCURIOS_DATA.FIVETRAN_LOG.TRANSFORMATION_STATUS;
SELECT * FROM MERCURIOS_DATA.FIVETRAN_LOG.SCHEMA_CHANGES;
```

## Key Tables and Views

The Quickstart Data Model creates the following key objects:

### Connector Monitoring

- `FIVETRAN_LOG.CONNECTOR_STATUS`: Current status of all connectors
- `FIVETRAN_LOG.DAILY_API_CALLS`: API usage by connector
- `FIVETRAN_LOG.SCHEMA_CHANGES`: History of schema changes

### Error Tracking

- `FIVETRAN_LOG.ERROR_REPORTING`: Detailed error logs
- `FIVETRAN_LOG.CONNECTOR_ISSUES`: Summary of connector issues

### Performance Metrics

- `FIVETRAN_LOG.SYNC_PERFORMANCE`: Sync duration and row counts
- `FIVETRAN_LOG.MONTHLY_ACTIVE_ROWS`: MAR usage by connector

## Integration with Mercurios.ai Architecture

### 1. Monitoring Dashboard

Create a monitoring dashboard using these models:

```sql
-- Example: Connector health query for dashboard
SELECT 
    connector_name,
    destination_name,
    connector_type,
    is_paused,
    status,
    last_successful_sync,
    DATEDIFF('hour', last_successful_sync, CURRENT_TIMESTAMP()) as hours_since_last_sync,
    sync_frequency,
    sync_status,
    error_count_7d
FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS
ORDER BY hours_since_last_sync DESC;
```

### 2. Alerting System

Set up alerts based on these models:

```sql
-- Example: Alert on connectors with errors
SELECT 
    connector_name,
    error_message,
    created_at,
    COUNT(*) as error_count
FROM MERCURIOS_DATA.FIVETRAN_LOG.ERROR_REPORTING
WHERE created_at >= DATEADD('day', -1, CURRENT_TIMESTAMP())
GROUP BY 1, 2, 3
HAVING COUNT(*) > 3;
```

### 3. Multi-Tenant Monitoring

For monitoring across tenants:

```sql
-- Example: Join with tenant metadata
SELECT 
    t.tenant_name,
    c.connector_name,
    c.status,
    c.last_successful_sync,
    c.sync_status
FROM MERCURIOS_DATA.FIVETRAN_LOG.CONNECTOR_STATUS c
JOIN MERCURIOS_DATA.PUBLIC.TENANTS t ON c.connector_name LIKE '%' || t.tenant_id || '%'
ORDER BY t.tenant_name, c.connector_name;
```

## Next Steps

1. **Create Monitoring Dashboard**: Build a dashboard in your BI tool using the queries above
2. **Set Up Alerts**: Configure alerts for failed syncs or unusual patterns
3. **Extend with Custom Models**: Build your own dbt models that reference these Quickstart models
4. **Document for Operations Team**: Create runbooks for common issues identified by these models

## Conclusion

The Fivetran Quickstart Data Model for metadata provides a solid foundation for monitoring your data pipelines. By implementing these models, you gain immediate visibility into your connectors' health and performance, which is critical for maintaining a reliable multi-tenant SaaS platform like Mercurios.ai.

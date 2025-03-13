# Fivetran Metadata Connector: First Sync Guide

## Overview
The Fivetran metadata connector provides information about your Fivetran account, connectors, and sync history. This guide will help you understand what to expect during the first sync and how to use the data.

## Starting the First Sync

1. Navigate to the fivetran_metadata connector in your Fivetran dashboard
2. Click the "Start Initial Sync" button
3. The sync should complete within a few minutes

## What Data Will Be Synced

The metadata connector will create and populate the following tables in your Snowflake database:

| Table | Description |
|-------|-------------|
| `FIVETRAN_METADATA.ACCOUNT` | Information about your Fivetran account |
| `FIVETRAN_METADATA.CONNECTOR` | Details about all connectors in your account |
| `FIVETRAN_METADATA.DESTINATION` | Information about your destinations |
| `FIVETRAN_METADATA.LOG` | Sync logs and error messages |
| `FIVETRAN_METADATA.SCHEMA_CHANGE` | History of schema changes |
| `FIVETRAN_METADATA.TRANSFORMATION` | Details about any transformations |
| `FIVETRAN_METADATA.TRIGGER_HISTORY` | History of sync triggers |
| `FIVETRAN_METADATA.USAGE` | Usage metrics for your account |

## Verifying the Sync in Snowflake

After the sync completes, you can verify the data in Snowflake with these queries:

```sql
-- Check if the schema was created
SHOW SCHEMAS LIKE 'FIVETRAN_METADATA' IN DATABASE MERCURIOS_DATA;

-- List all tables in the schema
SHOW TABLES IN SCHEMA MERCURIOS_DATA.FIVETRAN_METADATA;

-- Check connector data
SELECT * FROM MERCURIOS_DATA.FIVETRAN_METADATA.CONNECTOR;

-- Check account information
SELECT * FROM MERCURIOS_DATA.FIVETRAN_METADATA.ACCOUNT;
```

## Useful Queries for Monitoring

### Check Connector Status
```sql
SELECT 
    connector_name,
    connector_type,
    connector_id,
    destination_id,
    status,
    setup_state,
    sync_frequency,
    last_sync_start,
    last_sync_completion
FROM MERCURIOS_DATA.FIVETRAN_METADATA.CONNECTOR;
```

### Check Recent Sync Logs
```sql
SELECT 
    connector_name,
    message_data,
    event_type,
    created_at
FROM MERCURIOS_DATA.FIVETRAN_METADATA.LOG
ORDER BY created_at DESC
LIMIT 100;
```

### Monitor Usage
```sql
SELECT 
    connector_name,
    destination_name,
    measured_month,
    monthly_active_rows,
    credits_consumed
FROM MERCURIOS_DATA.FIVETRAN_METADATA.USAGE
ORDER BY measured_month DESC;
```

## Next Steps

1. **Set Up Sync Schedule**: Configure the sync frequency for the metadata connector (daily is recommended)
2. **Create Monitoring Dashboard**: Use the metadata to create dashboards for monitoring connector health
3. **Set Up Alerts**: Create alerts for failed syncs or unusual usage patterns
4. **Explore Schema Changes**: Track schema changes over time to understand how your data evolves

## Conclusion

The Fivetran metadata connector provides valuable insights into your Fivetran account and connectors. By regularly syncing this data to Snowflake, you can monitor the health of your data pipelines, track usage, and ensure everything is running smoothly.

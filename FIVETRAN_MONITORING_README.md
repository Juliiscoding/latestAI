# Fivetran Monitoring Tools

This document provides an overview of the monitoring tools we've created for the Fivetran-Snowflake integration in the Mercurios.ai architecture.

## Overview

Monitoring is a critical component of our data pipeline, especially in a multi-tenant architecture where we need to ensure that data is flowing correctly for all tenants. We've implemented a comprehensive monitoring system that includes:

1. **Fivetran Quickstart Data Model**: Pre-built transformations that provide analytics-ready views of connector health and performance
2. **Custom Monitoring Scripts**: Python scripts for monitoring, alerting, and analysis
3. **Integration with Multi-Tenant Architecture**: Tools designed to work with our tenant isolation strategy

## Fivetran Quickstart Data Model

The Fivetran Quickstart Data Model for metadata provides 19 pre-built analytics-ready views in the `FIVETRAN_LOG` schema. These views offer insights into connector health, performance, and issues without requiring custom code.

### Key Views

#### Connector Monitoring
- `CONNECTOR_STATUS`: Current status of all connectors
- `DAILY_API_CALLS`: API usage by connector
- `SCHEMA_CHANGES`: History of schema changes

#### Error Tracking
- `ERROR_REPORTING`: Detailed error logs
- `CONNECTOR_ISSUES`: Summary of connector issues

#### Performance Metrics
- `SYNC_PERFORMANCE`: Sync duration and row counts
- `MONTHLY_ACTIVE_ROWS`: MAR usage by connector

### Implementation

The Quickstart Data Model is implemented through the Fivetran UI:

1. Go to the Fivetran dashboard
2. Select the metadata connector
3. Go to the "Transformations" tab
4. Click "Add quickstart data model"
5. Select "fivetran_metadata" as the source
6. Click "Add & run packages"

## Custom Monitoring Scripts

We've developed several Python scripts to monitor and analyze our Fivetran connectors:

### Deployment Monitoring

#### `monitor_sync_until_complete.py`
Monitors the initial sync of the metadata connector until it completes.

```bash
python monitor_sync_until_complete.py
```

#### `monitor_quickstart_deployment.py`
Monitors the deployment of the Quickstart Data Model until it completes.

```bash
python monitor_quickstart_deployment.py
```

### Operational Monitoring

#### `fivetran_dashboard.py`
Generates a comprehensive dashboard of connector health and performance.

```bash
python fivetran_dashboard.py
```

The dashboard includes:
- Connector Status Overview
- Recent Sync Performance
- Recent Errors
- Recent Schema Changes
- Connector Health Alerts

#### `fivetran_alerts.py`
Checks for issues with connectors and can be configured to send alerts.

```bash
python fivetran_alerts.py
```

The alerts script checks for:
- Delayed syncs (syncs that are taking longer than expected)
- Connectors with frequent errors
- Connectors with failed status

In a production environment, this script would be configured to send alerts via email or Slack.

### Analysis Tools

#### `analyze_fivetran_quickstart.py`
Analyzes the Quickstart Data Model once deployed.

```bash
python analyze_fivetran_quickstart.py
```

#### `check_fivetran_metadata_sync.py`
Checks the status of the metadata sync.

```bash
python check_fivetran_metadata_sync.py
```

## Integration with Multi-Tenant Architecture

Our monitoring tools are designed to work with our multi-tenant architecture:

- **Centralized Monitoring**: Monitor connectors across all tenants from a central location
- **Tenant-Specific Alerts**: Identify issues that could impact specific tenants
- **Performance Tracking**: Track performance metrics for each tenant's data pipeline

### Example: Monitoring by Tenant

To monitor connectors by tenant, you can use a query like this:

```sql
-- Join with tenant metadata
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

## Setting Up Scheduled Monitoring

For production use, these scripts should be scheduled to run regularly:

### Example: Crontab Configuration

```
# Run dashboard every morning at 8:00 AM
0 8 * * * cd /path/to/project && python fivetran_dashboard.py > /path/to/logs/dashboard_$(date +\%Y\%m\%d).log 2>&1

# Run alerts every hour
0 * * * * cd /path/to/project && python fivetran_alerts.py > /path/to/logs/alerts_$(date +\%Y\%m\%d_\%H).log 2>&1
```

## Next Steps

1. **Create Monitoring Dashboard**: Build a dashboard in your BI tool using the Quickstart Data Model views
2. **Set Up Alerts**: Configure the `fivetran_alerts.py` script to send alerts via email or Slack
3. **Schedule Regular Monitoring**: Set up cron jobs to run the monitoring scripts regularly
4. **Extend with Custom Metrics**: Add custom metrics specific to your business needs

## Conclusion

These monitoring tools provide the foundation for a robust monitoring system that ensures our data pipelines are reliable and performant. By combining the Fivetran Quickstart Data Model with our custom scripts, we have comprehensive visibility into our data pipeline health and performance.

# Mercurios.ai Project Summary

## Project Overview
Mercurios.ai is a predictive inventory management tool that integrates data from ProHandel API into Snowflake for business intelligence and analytics.

## Current Setup

### Snowflake Environment
- **Account**: VRXDFZX-ZZ95717
- **Username**: JULIUSRECHENBACH
- **Warehouses**: 
  - MERCURIOS_LOADING_WH (ETL)
  - MERCURIOS_ANALYTICS_WH (Analytics)
  - MERCURIOS_DEV_WH (Development)
- **Database**: MERCURIOS_DATA
- **Schemas**: RAW, STANDARD, ANALYTICS
- **Roles**: 
  - MERCURIOS_ADMIN
  - MERCURIOS_DEVELOPER
  - MERCURIOS_ANALYST
  - MERCURIOS_FIVETRAN_SERVICE

### Fivetran Integration
- **Host**: vrxdfzx-zz95717.snowflakecomputing.com
- **Port**: 443
- **User**: FIVETRAN_USER
- **Database**: MERCURIOS_DATA
- **Schema**: RAW
- **Warehouse**: MERCURIOS_LOADING_WH
- **Role**: MERCURIOS_FIVETRAN_SERVICE

### ProHandel API Connector
- AWS Lambda function for integrating ProHandel API with Fivetran
- Handles data extraction, transformation, and loading
- Supports incremental loading based on timestamps
- Adds calculated fields and data enhancements

## Architecture Components
1. **Multi-Tenant Data Warehouse (Snowflake)**
   - Separate warehouses for ETL, analytics, and development
   - Role-based access control
   - Optimized schema design

2. **Enhanced Lambda Connector**
   - Tenant isolation with tenant_id
   - Data quality validation
   - Support for incremental loading

3. **ETL Pipeline**
   - ProHandelConnector for data extraction
   - DatabaseLoader for loading data into Snowflake
   - ETLOrchestrator for process coordination

## Fivetran Monitoring Tools

To ensure the reliability and performance of our Fivetran connectors, we've implemented several monitoring tools:

### 1. Fivetran Quickstart Data Model

We've deployed the Fivetran Quickstart Data Model for metadata, which provides 19 pre-built analytics-ready views in the `FIVETRAN_LOG` schema. These views offer insights into connector health, performance, and issues without requiring custom code.

Key views include:
- `CONNECTOR_STATUS`: Current status of all connectors
- `SYNC_PERFORMANCE`: Sync duration and row counts
- `ERROR_REPORTING`: Detailed error logs

### 2. Custom Monitoring Scripts

We've developed several Python scripts to monitor and analyze our Fivetran connectors:

#### Deployment Monitoring
- `monitor_sync_until_complete.py`: Monitors the initial sync of the metadata connector
- `monitor_quickstart_deployment.py`: Monitors the deployment of the Quickstart Data Model

#### Operational Monitoring
- `fivetran_dashboard.py`: Generates a comprehensive dashboard of connector health and performance
- `fivetran_alerts.py`: Checks for issues with connectors and can be configured to send alerts

#### Analysis Tools
- `analyze_fivetran_quickstart.py`: Analyzes the Quickstart Data Model once deployed
- `check_fivetran_metadata_sync.py`: Checks the status of the metadata sync

### 3. Integration with Multi-Tenant Architecture

Our monitoring tools are designed to work with our multi-tenant architecture:
- Monitor connectors across all tenants from a central location
- Identify issues that could impact specific tenants
- Track performance metrics for each tenant's data pipeline

### 4. Usage Examples

```bash
# Generate a monitoring dashboard
python fivetran_dashboard.py

# Check for alerts
python fivetran_alerts.py

# Analyze the Quickstart Data Model
python analyze_fivetran_quickstart.py
```

These tools provide the foundation for a robust monitoring system that ensures our data pipelines are reliable and performant.

## Key Files
- `snowflake_config.json`: Configuration for Snowflake connection
- `fivetran_config.json`: Configuration for Fivetran connection
- `setup_snowflake.py`: Script for setting up Snowflake environment
- `create_fivetran_user.py`: Script for creating Fivetran service user

## Next Steps
1. Complete Fivetran-Snowflake integration
2. Implement data transformation logic
3. Build analytics models
4. Set up monitoring and alerting

# Mercurios.ai System Architecture

## Overview

Mercurios.ai is a multi-tenant data analytics platform designed to process, analyze, and visualize point-of-sale (POS) data from various retail systems, with a primary focus on ProHandel integration. The architecture follows a modern cloud-native approach with Snowflake as the central data warehouse.

## System Components

### 1. Data Ingestion Layer

#### Fivetran Connectors
- **Purpose**: Extract data from source systems and load into Snowflake
- **Configuration**:
  - Host: vrxdfzx-zz95717.snowflakecomputing.com
  - Authentication: Password-based (with option to upgrade to KEY_PAIR)
  - Service Account: FIVETRAN_USER with MERCURIOS_FIVETRAN_SERVICE role
  - Target: MERCURIOS_DATA.RAW schema

#### Enhanced Lambda Connector
- **Purpose**: Custom connector for POS systems without native Fivetran support
- **Features**:
  - Tenant ID injection for multi-tenancy
  - Data quality validation
  - Error handling and logging
  - Incremental loading support

### 2. Data Storage Layer (Snowflake)

#### Warehouses
- **MERCURIOS_LOADING_WH**: Dedicated to ETL processes
- **MERCURIOS_ANALYTICS_WH**: Optimized for analytics queries
- **MERCURIOS_DEV_WH**: For development work
- **MERCURIOS_TASK_WH**: For scheduled tasks and maintenance

#### Database Structure
- **MERCURIOS_DATA**: Main database
  - **RAW Schema**: Raw data from source systems
  - **STANDARD Schema**: Standardized and cleansed data
  - **ANALYTICS Schema**: Optimized views for analytics
  - **ADMIN Schema**: Administrative functions and monitoring

#### Resource Monitors
- **MERCURIOS_ANALYTICS_MONITOR**: 10 credits monthly quota
- **MERCURIOS_DEV_MONITOR**: 5 credits monthly quota
- **MERCURIOS_LOADING_MONITOR**: 8 credits monthly quota
- **MERCURIOS_TASK_MONITOR**: 2 credits monthly quota

### 3. Data Processing Layer

#### Analytics Views
- **DAILY_SALES_SUMMARY**: Aggregated daily sales metrics
- **CUSTOMER_INSIGHTS**: Customer behavior and spending patterns
- **PRODUCT_PERFORMANCE**: Product sales and profitability metrics
- **INVENTORY_STATUS**: Current inventory levels and status
- **SHOP_PERFORMANCE**: Shop-level performance metrics
- **BUSINESS_DASHBOARD**: Key business metrics for executive dashboards

#### Scheduled Tasks
- Refresh tasks for materialized views
- Cost monitoring and reporting tasks

### 4. Tenant Management System

- **Tenant Registration**: Automated tenant provisioning
- **Credential Management**: Secure storage in AWS Secrets Manager
- **Configuration Management**: Tenant-specific settings in S3
- **Deployment**: Tenant-specific Lambda function deployment

### 5. Security Layer

#### Role-Based Access Control
- **MERCURIOS_ADMIN**: Full administrative access
- **MERCURIOS_DEVELOPER**: Development and testing access
- **MERCURIOS_ANALYST**: Read-only access to analytics views
- **MERCURIOS_FIVETRAN_SERVICE**: Limited access for data loading

#### Row-Level Security
- Tenant isolation through tenant_id filtering
- Data access controls based on user roles

## Data Flow

```
┌─────────────────┐     ┌──────────────┐     ┌────────────────────┐
│  Source Systems │────▶│   Fivetran   │────▶│ Snowflake RAW      │
│  (POS, ERP)     │     │   Connectors │     │ Schema             │
└─────────────────┘     └──────────────┘     └──────────┬─────────┘
                                                        │
┌─────────────────┐     ┌──────────────┐               │
│  Custom Sources │────▶│    Lambda    │───────────────┘
│  (APIs, Files)  │     │   Connector  │
└─────────────────┘     └──────────────┘
                                                        │
                                             ┌──────────▼─────────┐
                                             │ Snowflake STANDARD │
                                             │ Schema (Cleansed)  │
                                             └──────────┬─────────┘
                                                        │
                                             ┌──────────▼─────────┐
                                             │ Snowflake ANALYTICS│
                                             │ Schema (Views)     │
                                             └──────────┬─────────┘
                                                        │
                       ┌────────────────┐    ┌──────────▼─────────┐
                       │  Dashboards &  │◀───│ Materialized Views │
                       │  Reporting     │    │ & Tables           │
                       └────────────────┘    └────────────────────┘
```

## Cost Optimization Features

1. **Warehouse Auto-Suspension**: All warehouses auto-suspend after 60 seconds of inactivity
2. **Resource Monitors**: Prevent unexpected cost overruns with quota limits and alerts
3. **Cost-Efficient Analytics Views**: Optimized queries that minimize compute usage
4. **Monitoring Infrastructure**: Daily cost tracking and usage pattern analysis

## Scalability Considerations

1. **Multi-Tenant Design**: Efficient onboarding of new customers
2. **Separate Warehouses**: Isolation of workloads for optimal performance
3. **Modular Connector Framework**: Support for various POS systems
4. **Clustering Keys**: Optimized for large datasets and frequent query patterns

## Management Scripts

1. `suspend_all_warehouses.py`: Suspends all warehouses when not in use
2. `setup_resource_monitors_final.py`: Sets up resource monitors for cost control
3. `fix_permissions_individually.py`: Grants necessary permissions for analytics views
4. `setup_cost_monitoring.py`: Sets up cost monitoring views and alerts

## Future Enhancements

1. **Key-Pair Authentication**: Enhanced security for service accounts
2. **Multi-Cluster Warehouses**: For high-concurrency workloads
3. **Advanced Data Retention Policies**: Optimized storage management
4. **AI/ML Integration**: Predictive analytics and anomaly detection

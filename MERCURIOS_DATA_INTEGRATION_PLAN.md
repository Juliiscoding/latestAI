# Mercurios AI Data Integration Plan

## Overview

This document outlines the data integration strategy for the Mercurios AI Predictive Inventory Management project, focusing on how data flows from multiple sources into our analytics environment.

## Data Sources

### 1. ProHandel API (via AWS Lambda Connector)
- **Status**: ✅ Implemented and operational
- **Key Tables**:
  - `articles` - Product catalog information
  - `customers` - Customer master data
  - `orders` - Order transactions
  - `sales` - Sales transactions
  - `inventory` - Current stock levels
- **Update Frequency**: Incremental loading based on timestamps
- **Connector Type**: Custom AWS Lambda function

### 2. Google Analytics 4 (via BigQuery Export)
- **Status**: ⏳ Setup complete, waiting for data (24-48 hours)
- **Key Tables**:
  - `events_YYYYMMDD` - Daily event data
  - `user_properties` - User attribute data
- **Update Frequency**: Daily export
- **Connector Type**: GA4 Export to BigQuery → Fivetran to Snowflake

### 3. Shopify (via Fivetran)
- **Status**: ✅ Operational
- **Key Tables**:
  - `orders` - E-commerce orders
  - `customers` - Customer information
  - `products` - Product catalog
- **Update Frequency**: Near real-time via Fivetran

### 4. Klaviyo (via Fivetran)
- **Status**: ✅ Operational
- **Key Tables**:
  - `events` - Marketing events
  - `campaigns` - Email campaign data
  - `lists` - Customer segments
- **Update Frequency**: Near real-time via Fivetran

## Data Integration Strategy

### Phase 1: Data Collection (Current)
- Ensure all connectors are operational
- Verify data completeness and accuracy
- Set up monitoring for data pipeline health

### Phase 2: Data Modeling
- Create unified schemas that join data across sources
- Develop key metrics and KPIs
- Build core analytical views

### Phase 3: Predictive Analytics
- Develop inventory forecasting models
- Create customer segmentation
- Implement product affinity analysis

## Key Entity Relationships

### Product Data Integration
```
ProHandel.articles ←→ Shopify.products
                    ↓
GA4.events (item_view, add_to_cart, purchase)
```

### Customer Data Integration
```
ProHandel.customers ←→ Shopify.customers
                     ↓
Klaviyo.lists ←→ GA4.user_properties
```

### Sales Data Integration
```
ProHandel.sales ←→ Shopify.orders
                 ↓
GA4.events (purchase)
```

## Key Metrics for Predictive Inventory

1. **Product Performance Metrics**:
   - Sales velocity (units sold per day)
   - View-to-purchase conversion rate
   - Inventory turnover rate
   - Days of supply

2. **Customer Behavior Metrics**:
   - Repeat purchase rate
   - Average order value
   - Customer lifetime value
   - Product category affinity

3. **Marketing Impact Metrics**:
   - Campaign-attributed sales
   - Marketing channel effectiveness
   - Promotion response rate

## Next Steps

1. **Immediate (1-2 days)**:
   - Wait for GA4 data to appear in BigQuery
   - Verify Fivetran connector is syncing GA4 data to Snowflake
   - Document the GA4 schema once available

2. **Short-term (1 week)**:
   - Create initial data models joining ProHandel and GA4 data
   - Develop basic inventory performance dashboards
   - Set up data quality monitoring

3. **Medium-term (2-4 weeks)**:
   - Develop initial forecasting models
   - Create customer segmentation
   - Implement product affinity analysis

## Technical Implementation Notes

- Using "Columns" sync mode for all Fivetran connectors to enable direct SQL querying
- Implementing incremental loading where possible to minimize data transfer
- Standardizing entity IDs across systems for reliable joins
- Creating calculated fields for business metrics at the data model layer

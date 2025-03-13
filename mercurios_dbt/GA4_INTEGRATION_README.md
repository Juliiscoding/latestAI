# Google Analytics 4 Integration for Mercurios.ai

This document outlines the dbt models created for integrating Google Analytics 4 (GA4) data with ProHandel data to enhance the Mercurios.ai predictive inventory management system.

## Overview

The GA4 export connector provides rich, detailed data that can be integrated with ProHandel data to improve inventory management, customer segmentation, and sales forecasting. The integration models are structured in three layers:

1. **Staging Models** - Clean and transform raw GA4 data
2. **Intermediate Models** - Join GA4 data with ProHandel data
3. **Mart Models** - Provide business insights based on the combined data

## Models Created

### Staging Models

- **stg_ga4_product_performance** - Transforms GA4 ecommerce and page view data into product performance metrics
- **stg_ga4_user_acquisition** - Transforms GA4 user acquisition and demographic data into user behavior metrics

### Intermediate Models

- **int_product_performance_combined** - Joins ProHandel article/inventory/sales data with GA4 product performance data
- **int_customer_behavior_combined** - Joins ProHandel customer/order data with GA4 user acquisition data

### Mart Models

- **fct_product_insights** - Provides comprehensive product performance metrics and actionable insights
- **fct_customer_insights** - Provides comprehensive customer behavior metrics and segmentation
- **fct_inventory_forecast_enhanced** - Provides enhanced inventory forecasts using both offline and online signals

## Setup Instructions

### 1. Snowflake Access Requirements

To use these models, you need access to the following Snowflake objects:

- `GOOGLE_ANALYTICS_4` schema
- Tables within the GA4 schema, particularly:
  - `ECOMMERCE_PURCHASES_ITEM_ID_REPORT`
  - `ECOMMERCE_PURCHASES_ITEM_NAME_REPORT`
  - `PAGES_PATH_REPORT`
  - `USER_ACQUISITION_FIRST_USER_SOURCE_MEDIUM_REPORT`
  - `USER_ACQUISITION_FIRST_USER_CAMPAIGN_REPORT`
  - `DEMOGRAPHIC_CITY_REPORT`

### 2. Enabling the Models

The models are currently disabled due to access permission issues. Once access is granted, enable them by:

1. Update the configuration files to set `enabled: true`:
   - `models/staging/ga4_models.yml`
   - `models/intermediate/ga4_intermediate_models.yml`
   - `models/marts/ga4_mart_models.yml`

2. Run the models:
   ```bash
   dbt run --select stg_ga4_product_performance stg_ga4_user_acquisition int_product_performance_combined int_customer_behavior_combined fct_product_insights fct_customer_insights fct_inventory_forecast_enhanced
   ```

### 3. Adapting to Your GA4 Schema

The models assume certain column names and structures in the GA4 tables. You may need to adjust the models based on your specific GA4 export connector configuration:

1. Review the source definitions in `models/staging/src_google_analytics.yml`
2. Update column names in the staging models if they differ from your GA4 schema
3. Adjust the join conditions in the intermediate models if your product/user identifiers differ

## Integration Benefits

This integration enables:

1. **Enhanced Inventory Management**
   - Adjust inventory levels based on both offline sales and online interest
   - Identify products with high online views but low conversion for optimization
   - Forecast demand using both historical sales and current online trends

2. **Improved Customer Segmentation**
   - Combine offline purchase behavior with online acquisition channels
   - Create omnichannel customer segments for targeted marketing
   - Identify high-value customers across both online and offline channels

3. **Data-Driven Decision Making**
   - Understand which products perform better online vs. offline
   - Identify regional trends and preferences
   - Optimize marketing spend based on customer acquisition insights

## Multi-Tenant Considerations

These models are designed to work with Mercurios.ai's multi-tenant architecture:

- All models use the database specified in environment variables
- Row-level security can be implemented at the Snowflake level
- Models can be adapted to include tenant_id filtering

## Next Steps

1. **Request Snowflake Access**: Contact your Snowflake administrator to grant access to the GA4 schema and tables
2. **Enable and Test Models**: Once access is granted, enable the models and test with a small subset of data
3. **Customize for Business Needs**: Adjust thresholds, categories, and metrics to match your specific business requirements
4. **Create Dashboards**: Build dashboards in your BI tool of choice to visualize the insights from these models

# Cost-Efficient Dashboard Implementation Guide

## Overview

This guide outlines how to implement a cost-efficient dashboard solution that provides valuable business insights while minimizing Snowflake costs. By following this approach, you'll be able to extract maximum value from your data investment without incurring unnecessary expenses.

## Implementation Steps

### 1. Set Up Analytics Views

We've created the following analytics views to serve as the foundation for your dashboards:

- `DAILY_SALES_SUMMARY`: Aggregates sales data by day, tenant, and category
- `INVENTORY_STATUS`: Provides current inventory levels and reorder alerts
- `CUSTOMER_INSIGHTS`: Summarizes customer behavior and lifetime value
- `PRODUCT_PERFORMANCE`: Tracks product sales and category rankings
- `BUSINESS_DASHBOARD`: Consolidates key metrics for executive reporting

To implement these views, run the `implement_cost_efficient_views.sql` script. This will:
- Temporarily resume a warehouse
- Create all the necessary views
- Immediately suspend the warehouse to prevent unnecessary costs

### 2. Set Up Scheduled Refreshes

For optimal cost efficiency, we'll schedule dashboard refreshes during off-hours:

1. **Create a Materialized View for Daily Reports**

```sql
-- Run this once to create a materialized view of the dashboard
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH RESUME;

CREATE OR REPLACE MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV
AS SELECT * FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD;

ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SUSPEND;
```

2. **Schedule Daily Refresh**

```sql
-- Run this to create a scheduled task for daily refresh
ALTER WAREHOUSE MERCURIOS_DEV_WH RESUME;

-- Create a task to refresh the materialized view
CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_MV
  WAREHOUSE = MERCURIOS_ANALYTICS_WH
  SCHEDULE = 'USING CRON 0 3 * * * Europe/Berlin'
AS
  REFRESH MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV;

-- Initially suspend the task
ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_MV SUSPEND;

ALTER WAREHOUSE MERCURIOS_DEV_WH SUSPEND;
```

3. **Export Results to S3 (Optional)**

If you want to make dashboard data available outside of Snowflake:

```sql
-- Create an external stage for exports
CREATE OR REPLACE STAGE MERCURIOS_DATA.ADMIN.DASHBOARD_EXPORTS
  URL = 's3://your-bucket/dashboard-exports/'
  CREDENTIALS = (AWS_KEY_ID = 'your-key-id' AWS_SECRET_KEY = 'your-secret-key');

-- Create a task to export dashboard data
CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.EXPORT_DASHBOARD
  WAREHOUSE = MERCURIOS_ANALYTICS_WH
  SCHEDULE = 'USING CRON 0 4 * * * Europe/Berlin'
AS
  COPY INTO @MERCURIOS_DATA.ADMIN.DASHBOARD_EXPORTS/daily_dashboard_
  FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV
  FILE_FORMAT = (TYPE = 'CSV' COMPRESSION = 'GZIP')
  OVERWRITE = TRUE;

-- Initially suspend the task
ALTER TASK MERCURIOS_DATA.ADMIN.EXPORT_DASHBOARD SUSPEND;
```

### 3. Connect to Visualization Tools

For maximum cost efficiency, connect your visualization tool directly to the materialized views:

#### Option 1: Tableau

1. Connect Tableau to Snowflake
2. Create a data source that points to `MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV`
3. Build dashboards using this pre-aggregated data
4. Schedule Tableau to refresh after the materialized view is updated (e.g., 4:00 AM)

#### Option 2: Power BI

1. Connect Power BI to Snowflake
2. Create a dataset that imports from `MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV`
3. Build reports and dashboards using this dataset
4. Schedule Power BI to refresh after the materialized view is updated (e.g., 4:00 AM)

#### Option 3: Looker

1. Connect Looker to Snowflake
2. Create a model that uses `MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV`
3. Build dashboards and explores using this model
4. Schedule Looker to cache results after the materialized view is updated (e.g., 4:00 AM)

### 4. Implement Email Reports

For stakeholders who need regular updates without logging into a dashboard:

```sql
-- Create a stored procedure for email reports
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.ADMIN.SEND_DAILY_SUMMARY_EMAIL()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
  email_body STRING;
BEGIN
  -- Generate email body from dashboard data
  SELECT CONCAT(
    'Daily Business Summary for ', CURRENT_DATE(), '\n\n',
    'Total Sales (Last 7 Days): $', SUM(sales_7d), '\n',
    'Active Customers (Last 30 Days): ', SUM(active_customers_30d), '\n',
    'Products Needing Reorder: ', SUM(products_to_reorder), '\n',
    'Top Performing Products: ', SUM(top_performing_products)
  )
  INTO email_body
  FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV;
  
  -- Send email using Snowflake notification integration
  CALL SYSTEM$SEND_EMAIL(
    'your_notification_integration',
    'team@mercurios.ai',
    'Daily Business Summary',
    email_body
  );
  
  RETURN 'Email sent successfully';
END;
$$;

-- Create a task to send daily email reports (weekdays at 7 AM)
CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.SEND_DAILY_SUMMARY_EMAIL_TASK
  WAREHOUSE = MERCURIOS_ANALYTICS_WH
  SCHEDULE = 'USING CRON 0 7 * * 1-5 Europe/Berlin'
AS
  CALL MERCURIOS_DATA.ADMIN.SEND_DAILY_SUMMARY_EMAIL();

-- Initially suspend the task
ALTER TASK MERCURIOS_DATA.ADMIN.SEND_DAILY_SUMMARY_EMAIL_TASK SUSPEND;
```

## Activation Process

When you're ready to activate the dashboards:

1. Resume the warehouse:
   ```sql
   ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH RESUME;
   ```

2. Resume the tasks:
   ```sql
   ALTER TASK MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_MV RESUME;
   ALTER TASK MERCURIOS_DATA.ADMIN.EXPORT_DASHBOARD RESUME;
   ALTER TASK MERCURIOS_DATA.ADMIN.SEND_DAILY_SUMMARY_EMAIL_TASK RESUME;
   ```

3. Suspend the warehouse:
   ```sql
   ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SUSPEND;
   ```

## Cost Monitoring

To ensure your dashboard solution remains cost-efficient:

1. Create a dashboard cost monitoring view:
   ```sql
   CREATE OR REPLACE VIEW MERCURIOS_DATA.ADMIN.DASHBOARD_COST_MONITORING AS
   SELECT 
     DATE_TRUNC('DAY', START_TIME) AS DATE,
     COUNT(*) AS QUERY_COUNT,
     SUM(TOTAL_ELAPSED_TIME)/1000/60 AS RUNTIME_MINUTES,
     SUM(TOTAL_ELAPSED_TIME)/1000/60/60 * 
       CASE 
         WHEN WAREHOUSE_SIZE = 'XSMALL' THEN 1
         WHEN WAREHOUSE_SIZE = 'SMALL' THEN 2
         ELSE 4
       END AS ESTIMATED_CREDITS
   FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
   WHERE START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
   AND QUERY_TEXT ILIKE '%BUSINESS_DASHBOARD%'
   GROUP BY 1
   ORDER BY 1 DESC;
   ```

2. Review this monitoring view weekly to ensure costs remain under control.

## Expected Outcomes

By implementing this dashboard solution:

- **Cost Reduction**: 80-90% reduction in dashboard-related Snowflake costs
- **Data Freshness**: Daily updates providing timely business insights
- **User Experience**: Fast dashboard performance due to pre-aggregated data
- **Business Value**: Consistent access to key metrics for decision-making

This approach transforms your Snowflake investment from a cost center into a strategic asset that delivers consistent business value at a predictable, manageable cost.

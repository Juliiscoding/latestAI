-- Implementation Script for Cost-Efficient Analytics Views
-- This script will:
-- 1. Resume the smallest warehouse (MERCURIOS_DEV_WH)
-- 2. Create analytics views for efficient querying
-- 3. Immediately suspend the warehouse to prevent unnecessary costs

-- Step 1: Resume the warehouse
ALTER WAREHOUSE MERCURIOS_DEV_WH RESUME;

-- Step 2: Create analytics views
-- These views provide valuable insights while minimizing query costs

-- 1. Daily Sales Summary View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY AS
SELECT 
  DATE_TRUNC('DAY', sale_timestamp) AS sale_date,
  tenant_id,
  product_category,
  SUM(quantity) AS total_quantity,
  SUM(amount) AS total_amount,
  COUNT(DISTINCT order_id) AS order_count,
  COUNT(DISTINCT customer_id) AS customer_count
FROM MERCURIOS_DATA.RAW.sales
GROUP BY 1, 2, 3;

-- 2. Inventory Status View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.INVENTORY_STATUS AS
SELECT
  CURRENT_DATE() AS snapshot_date,
  tenant_id,
  product_id,
  product_name,
  category,
  current_stock_level,
  reorder_point,
  CASE 
    WHEN current_stock_level <= reorder_point THEN 'Reorder'
    WHEN current_stock_level <= (reorder_point * 1.5) THEN 'Warning'
    ELSE 'OK'
  END AS stock_status,
  last_restock_date,
  supplier_id
FROM MERCURIOS_DATA.RAW.inventory
WHERE current_stock_level IS NOT NULL;

-- 3. Customer Insights View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.CUSTOMER_INSIGHTS AS
SELECT
  tenant_id,
  customer_id,
  COUNT(DISTINCT order_id) AS total_orders,
  SUM(amount) AS total_spent,
  MIN(sale_timestamp) AS first_purchase_date,
  MAX(sale_timestamp) AS last_purchase_date,
  DATEDIFF('day', MIN(sale_timestamp), MAX(sale_timestamp)) AS customer_lifetime_days,
  SUM(amount) / NULLIF(COUNT(DISTINCT order_id), 0) AS average_order_value
FROM MERCURIOS_DATA.RAW.sales
GROUP BY 1, 2;

-- 4. Product Performance View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.PRODUCT_PERFORMANCE AS
SELECT
  tenant_id,
  product_id,
  product_name,
  category,
  SUM(quantity) AS total_quantity_sold,
  SUM(amount) AS total_revenue,
  COUNT(DISTINCT order_id) AS order_count,
  SUM(amount) / NULLIF(SUM(quantity), 0) AS average_unit_price,
  RANK() OVER (PARTITION BY tenant_id, category ORDER BY SUM(amount) DESC) AS revenue_rank_in_category
FROM MERCURIOS_DATA.RAW.sales
GROUP BY 1, 2, 3, 4;

-- 5. Consolidated Dashboard View (combines key metrics)
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD AS
SELECT
  CURRENT_DATE() AS report_date,
  tenant_id,
  
  -- Sales metrics
  (SELECT SUM(total_amount) FROM MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY 
   WHERE sale_date >= DATEADD('day', -30, CURRENT_DATE()) AND tenant_id = t.tenant_id) AS sales_30d,
  
  (SELECT SUM(total_amount) FROM MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY 
   WHERE sale_date >= DATEADD('day', -7, CURRENT_DATE()) AND tenant_id = t.tenant_id) AS sales_7d,
  
  -- Inventory metrics
  (SELECT COUNT(*) FROM MERCURIOS_DATA.ANALYTICS.INVENTORY_STATUS 
   WHERE stock_status = 'Reorder' AND tenant_id = t.tenant_id) AS products_to_reorder,
  
  -- Customer metrics
  (SELECT COUNT(DISTINCT customer_id) FROM MERCURIOS_DATA.ANALYTICS.CUSTOMER_INSIGHTS 
   WHERE last_purchase_date >= DATEADD('day', -30, CURRENT_DATE()) AND tenant_id = t.tenant_id) AS active_customers_30d,
  
  -- Product metrics
  (SELECT COUNT(*) FROM MERCURIOS_DATA.ANALYTICS.PRODUCT_PERFORMANCE 
   WHERE revenue_rank_in_category <= 5 AND tenant_id = t.tenant_id) AS top_performing_products
  
FROM (SELECT DISTINCT tenant_id FROM MERCURIOS_DATA.RAW.sales) t;

-- Step 3: Create a stored procedure to refresh the dashboard
-- This will be used by the scheduled task
CREATE OR REPLACE PROCEDURE MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_PROC()
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
  -- Refresh the materialized views or tables as needed
  -- This is a placeholder - implement based on your specific needs
  RETURN 'Dashboard refreshed successfully';
END;
$$;

-- Step 4: Create a scheduled task to refresh the dashboard daily (runs at 1 AM)
-- Note: This task will be created in suspended state
CREATE OR REPLACE TASK MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD
  WAREHOUSE = MERCURIOS_ANALYTICS_WH
  SCHEDULE = 'USING CRON 0 1 * * * Europe/Berlin'
AS
  CALL MERCURIOS_DATA.ADMIN.REFRESH_DASHBOARD_PROC();

-- Step 5: Immediately suspend the warehouse to prevent unnecessary costs
ALTER WAREHOUSE MERCURIOS_DEV_WH SUSPEND;

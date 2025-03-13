-- Cost-Efficient Analytics Views for Snowflake
-- This script creates optimized analytics views that provide valuable business insights
-- while minimizing query costs.

-- 1. Daily Sales Summary View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.DAILY_SALES_SUMMARY AS
SELECT
    DATE_TRUNC('DAY', o.ORDER_DATE) AS day,
    COUNT(DISTINCT o.ORDER_ID) AS order_count,
    COUNT(DISTINCT o.CUSTOMER_ID) AS customer_count,
    SUM(o.TOTAL_AMOUNT) AS total_sales
FROM MERCURIOS_DATA.RAW.ORDERS o
GROUP BY 1
ORDER BY 1 DESC;

-- 2. Customer Insights View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.CUSTOMER_INSIGHTS AS
SELECT
    c.CUSTOMER_ID,
    c.FIRST_NAME || ' ' || c.LAST_NAME AS full_name,
    c.EMAIL,
    c.PHONE,
    c.CITY,
    c.COUNTRY,
    COUNT(o.ORDER_ID) AS total_orders,
    SUM(o.TOTAL_AMOUNT) AS total_spend,
    AVG(o.TOTAL_AMOUNT) AS avg_order_value,
    MAX(o.ORDER_DATE) AS last_order_date,
    DATEDIFF('day', MAX(o.ORDER_DATE), CURRENT_DATE()) AS days_since_last_order
FROM MERCURIOS_DATA.RAW.CUSTOMERS c
LEFT JOIN MERCURIOS_DATA.RAW.ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
GROUP BY 1, 2, 3, 4, 5, 6;

-- 3. Product Performance View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.PRODUCT_PERFORMANCE AS
SELECT
    a.ARTICLE_ID,
    a.NAME,
    a.CATEGORY,
    a.PRICE,
    a.COST,
    SUM(oi.QUANTITY) AS total_quantity_sold,
    SUM(oi.QUANTITY * oi.PRICE) AS total_revenue,
    SUM(oi.QUANTITY * (oi.PRICE - a.COST)) AS total_profit,
    (SUM(oi.QUANTITY * (oi.PRICE - a.COST)) / NULLIF(SUM(oi.QUANTITY * oi.PRICE), 0)) * 100 AS profit_margin
FROM MERCURIOS_DATA.RAW.ARTICLES a
LEFT JOIN MERCURIOS_DATA.RAW.ORDER_ITEMS oi ON a.ARTICLE_ID = oi.ARTICLE_ID
GROUP BY 1, 2, 3, 4, 5;

-- 4. Inventory Status View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.INVENTORY_STATUS AS
SELECT
    a.ARTICLE_ID,
    a.NAME,
    a.CATEGORY,
    i.WAREHOUSE_ID,
    i.QUANTITY AS current_stock,
    i.LOCATION,
    i.LAST_COUNT_DATE,
    i.IS_AVAILABLE
FROM MERCURIOS_DATA.RAW.ARTICLES a
LEFT JOIN MERCURIOS_DATA.RAW.INVENTORY i ON a.ARTICLE_ID = i.ARTICLE_ID;

-- 5. Shop Performance View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.SHOP_PERFORMANCE AS
SELECT
    s.SHOP_ID,
    s.NAME AS shop_name,
    s.CITY,
    s.COUNTRY,
    COUNT(DISTINCT sa.SALE_ID) AS total_sales,
    SUM(sa.QUANTITY) AS total_items_sold,
    SUM(sa.PRICE * sa.QUANTITY) AS total_revenue,
    AVG(sa.PRICE * sa.QUANTITY) AS avg_sale_value
FROM MERCURIOS_DATA.RAW.SHOP s
LEFT JOIN MERCURIOS_DATA.RAW.SALE sa ON s.SHOP_ID = sa.SHOP_ID
GROUP BY 1, 2, 3, 4;

-- 6. Consolidated Business Dashboard View
CREATE OR REPLACE VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD AS
WITH today_sales AS (
    SELECT COALESCE(SUM(TOTAL_AMOUNT), 0) AS value
    FROM MERCURIOS_DATA.RAW.ORDERS
    WHERE DATE_TRUNC('DAY', ORDER_DATE) = CURRENT_DATE()
),
yesterday_sales AS (
    SELECT COALESCE(SUM(TOTAL_AMOUNT), 0) AS value
    FROM MERCURIOS_DATA.RAW.ORDERS
    WHERE DATE_TRUNC('DAY', ORDER_DATE) = DATEADD('day', -1, CURRENT_DATE())
),
month_sales AS (
    SELECT COALESCE(SUM(TOTAL_AMOUNT), 0) AS value
    FROM MERCURIOS_DATA.RAW.ORDERS
    WHERE DATE_TRUNC('month', ORDER_DATE) = DATE_TRUNC('month', CURRENT_DATE())
),
customer_count AS (
    SELECT COUNT(*) AS value
    FROM MERCURIOS_DATA.RAW.CUSTOMERS
),
low_stock AS (
    SELECT COUNT(*) AS value
    FROM MERCURIOS_DATA.RAW.INVENTORY
    WHERE QUANTITY < 10 AND IS_AVAILABLE = TRUE
)
SELECT 'Sales' AS metric_category, 'Today''s Sales' AS metric_name, value AS metric_value FROM today_sales
UNION ALL
SELECT 'Sales' AS metric_category, 'Yesterday''s Sales' AS metric_name, value AS metric_value FROM yesterday_sales
UNION ALL
SELECT 'Sales' AS metric_category, 'This Month''s Sales' AS metric_name, value AS metric_value FROM month_sales
UNION ALL
SELECT 'Customers' AS metric_category, 'Total Customers' AS metric_name, value AS metric_value FROM customer_count
UNION ALL
SELECT 'Inventory' AS metric_category, 'Low Stock Items' AS metric_name, value AS metric_value FROM low_stock;

-- 7. Create materialized view for dashboard
CREATE OR REPLACE MATERIALIZED VIEW MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD_MV
AS SELECT * FROM MERCURIOS_DATA.ANALYTICS.BUSINESS_DASHBOARD;

-- 8. Create a cost monitoring view
CREATE OR REPLACE VIEW MERCURIOS_DATA.ADMIN.WAREHOUSE_USAGE_MONITORING AS
SELECT 
    WAREHOUSE_NAME,
    DATE_TRUNC('DAY', START_TIME) AS DATE,
    COUNT(*) AS QUERY_COUNT,
    SUM(EXECUTION_TIME)/1000/60 AS RUNTIME_MINUTES
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE START_TIME >= DATEADD(DAY, -30, CURRENT_DATE())
GROUP BY 1, 2
ORDER BY 1, 2 DESC;

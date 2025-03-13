-- Fivetran Connector Analysis SQL Script
-- This script will:
-- 1. Resume the smallest warehouse (MERCURIOS_DEV_WH)
-- 2. Analyze Fivetran connector usage and value
-- 3. Immediately suspend the warehouse to prevent unnecessary costs

-- Step 1: Resume the warehouse
ALTER WAREHOUSE MERCURIOS_DEV_WH RESUME;

-- Step 2: Identify which tables come from which Fivetran connector
SELECT 
    table_name,
    CASE
        WHEN table_name ILIKE 'SHOPIFY%' THEN 'shopify'
        WHEN table_name ILIKE 'GA%' OR table_name ILIKE 'GOOGLE_ANALYTICS%' THEN 'google_analytics_4_export'
        WHEN table_name ILIKE 'KLAVIYO%' THEN 'klaviyo'
        WHEN table_name ILIKE 'AWS%' OR table_name ILIKE 'LAMBDA%' THEN 'aws_lambda'
        ELSE 'unknown'
    END as likely_source,
    'Table Source Mapping' as analysis_type
FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'RAW';

-- Step 3: Analyze table sizes
SELECT 
    table_schema,
    table_name,
    row_count,
    bytes/1024/1024 as size_mb,
    'Table Size Analysis' as analysis_type
FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
WHERE table_schema = 'RAW'
ORDER BY size_mb DESC;

-- Step 4: Analyze query history (last 7 days)
SELECT 
    query_text,
    execution_time/1000 as execution_time_sec,
    warehouse_name,
    'Query History' as analysis_type
FROM INFORMATION_SCHEMA.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
AND query_text ILIKE '%MERCURIOS_DATA.RAW%'
ORDER BY start_time DESC
LIMIT 100;

-- Step 5: Analyze which tables are queried most frequently
-- This is a simplified approximation since we can't easily parse the query text in SQL
SELECT 
    REGEXP_SUBSTR(query_text, 'MERCURIOS_DATA\\.RAW\\.([A-Za-z0-9_]+)', 1, 1, 'e') as table_name,
    COUNT(*) as query_count,
    'Table Usage Frequency' as analysis_type
FROM INFORMATION_SCHEMA.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
AND query_text ILIKE '%MERCURIOS_DATA.RAW%'
AND REGEXP_SUBSTR(query_text, 'MERCURIOS_DATA\\.RAW\\.([A-Za-z0-9_]+)', 1, 1, 'e') IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC;

-- Step 6: Get a count of tables by source (for summary)
WITH source_mapping AS (
    SELECT 
        table_name,
        CASE
            WHEN table_name ILIKE 'SHOPIFY%' THEN 'shopify'
            WHEN table_name ILIKE 'GA%' OR table_name ILIKE 'GOOGLE_ANALYTICS%' THEN 'google_analytics_4_export'
            WHEN table_name ILIKE 'KLAVIYO%' THEN 'klaviyo'
            WHEN table_name ILIKE 'AWS%' OR table_name ILIKE 'LAMBDA%' THEN 'aws_lambda'
            ELSE 'unknown'
        END as likely_source
    FROM MERCURIOS_DATA.INFORMATION_SCHEMA.TABLES
    WHERE table_schema = 'RAW'
)
SELECT 
    likely_source,
    COUNT(*) as table_count,
    'Source Summary' as analysis_type
FROM source_mapping
GROUP BY 1
ORDER BY 2 DESC;

-- Step 7: Immediately suspend the warehouse to prevent unnecessary costs
ALTER WAREHOUSE MERCURIOS_DEV_WH SUSPEND;

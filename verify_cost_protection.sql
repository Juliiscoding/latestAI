-- 1. Verify all warehouses are suspended
SHOW WAREHOUSES;

-- 2. Check for any scheduled tasks that might auto-start warehouses
SHOW TASKS;

-- 3. Check warehouse auto-resume settings (should all be FALSE)
SELECT "name", "auto_resume" 
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

-- 4. Check for any running queries that might be consuming credits
SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY(
  DATE_RANGE_START=>DATEADD('hour', -1, CURRENT_TIMESTAMP()),
  DATE_RANGE_END=>CURRENT_TIMESTAMP()))
WHERE EXECUTION_STATUS = 'RUNNING';

-- 5. Check storage usage (this still incurs costs but is minimal)
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE
ORDER BY USAGE_DATE DESC
LIMIT 1;

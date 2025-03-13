-- Emergency Snowflake Cost Reduction Commands
-- Run these commands one by one in the Snowflake console

-- 1. Suspend all warehouses immediately
ALTER WAREHOUSE MERCURIOS_LOADING_WH SUSPEND;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SUSPEND;
ALTER WAREHOUSE MERCURIOS_DEV_WH SUSPEND;
-- Check if these warehouses exist before trying to suspend them
SHOW WAREHOUSES LIKE 'COMPUTE_WH';
ALTER WAREHOUSE COMPUTE_WH SUSPEND;
SHOW WAREHOUSES LIKE 'FIVETRAN_WAREHOUSE';
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SUSPEND;

-- 2. Set aggressive auto-suspend timeouts (1 minute)
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET AUTO_SUSPEND = 60;
SHOW WAREHOUSES LIKE 'COMPUTE_WH';
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 60;
SHOW WAREHOUSES LIKE 'FIVETRAN_WAREHOUSE';
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET AUTO_SUSPEND = 60;

-- 3. Reduce warehouse sizes to minimum
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL';
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET WAREHOUSE_SIZE = 'XSMALL';
ALTER WAREHOUSE MERCURIOS_DEV_WH SET WAREHOUSE_SIZE = 'XSMALL';
SHOW WAREHOUSES LIKE 'COMPUTE_WH';
ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'XSMALL';
SHOW WAREHOUSES LIKE 'FIVETRAN_WAREHOUSE';
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET WAREHOUSE_SIZE = 'XSMALL';

-- 4. Disable multi-cluster warehouses
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1;
SHOW WAREHOUSES LIKE 'FIVETRAN_WAREHOUSE';
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1;

-- 5. Set scaling policy to standard (less aggressive)
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET SCALING_POLICY = 'STANDARD';
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET SCALING_POLICY = 'STANDARD';
ALTER WAREHOUSE MERCURIOS_DEV_WH SET SCALING_POLICY = 'STANDARD';
SHOW WAREHOUSES LIKE 'FIVETRAN_WAREHOUSE';
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET SCALING_POLICY = 'STANDARD';

-- 6. Check current warehouse settings to confirm changes
SHOW WAREHOUSES;

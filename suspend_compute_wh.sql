-- Suspend the COMPUTE_WH warehouse that is still running
ALTER WAREHOUSE COMPUTE_WH SUSPEND;

-- Verify all warehouses are suspended
SHOW WAREHOUSES;

-- Prevent auto-resume of COMPUTE_WH
ALTER WAREHOUSE COMPUTE_WH SET AUTO_RESUME = FALSE;

-- Set a very aggressive auto-suspend timeout (10 seconds)
ALTER WAREHOUSE COMPUTE_WH SET AUTO_SUSPEND = 10;

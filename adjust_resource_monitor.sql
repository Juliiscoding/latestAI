-- Check the current status of the resource monitor
SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER';

-- Temporarily adjust the resource monitor to allow implementation
ALTER RESOURCE MONITOR MERCURIOSSTOPPER SET CREDIT_QUOTA = 2.0;

-- Verify the change
SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER';

-- Check the current status of the resource monitor
SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER';

-- Temporarily adjust the resource monitor to allow implementation
-- Using proper format for credit quota (no decimal point)
ALTER RESOURCE MONITOR MERCURIOSSTOPPER SET CREDIT_QUOTA = 2;

-- Verify the change
SHOW RESOURCE MONITORS LIKE 'MERCURIOSSTOPPER';

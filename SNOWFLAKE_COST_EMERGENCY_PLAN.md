# Snowflake Cost Emergency Plan

## Current Situation

Based on the Snowflake cost management screenshots, we've identified a serious cost issue:

- **Daily spend of $48.94** (Mar 10-11) with only 11 credits used
- **Monthly spend of $192.28** (Feb 11-Mar 11) with 44.34 credits used
- **Compute price per credit is $3.90**, which is the standard Snowflake on-demand rate

## Primary Cost Drivers

1. **MERCURIOS_LOADING_WH**: 
   - Consuming 4.52 credits/day (21.05 credits/month)
   - This single warehouse is responsible for ~80% of your costs

2. **MERCURIOS_ANALYTICS_WH**:
   - Consuming 3.22 credits/day
   - Set to LARGE size (based on our analysis)

3. **FIVETRAN_WAREHOUSE**:
   - Appearing in the second screenshot (2.95 credits)
   - Likely running frequent ETL jobs

## Immediate Actions (Requires ACCOUNTADMIN)

Since your current role doesn't have sufficient privileges to modify warehouses, you need to:

1. **Log into Snowflake as ACCOUNTADMIN** and run these commands:

```sql
-- Suspend all warehouses immediately
ALTER WAREHOUSE MERCURIOS_LOADING_WH SUSPEND;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SUSPEND;
ALTER WAREHOUSE MERCURIOS_DEV_WH SUSPEND;
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SUSPEND IF EXISTS;

-- Set aggressive auto-suspend timeouts (1 minute)
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET AUTO_SUSPEND = 60;
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET AUTO_SUSPEND = 60 IF EXISTS;

-- Reduce warehouse sizes to minimum
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET WAREHOUSE_SIZE = 'XSMALL';
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET WAREHOUSE_SIZE = 'XSMALL';
ALTER WAREHOUSE MERCURIOS_DEV_WH SET WAREHOUSE_SIZE = 'XSMALL';
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET WAREHOUSE_SIZE = 'XSMALL' IF EXISTS;

-- Disable multi-cluster warehouses
ALTER WAREHOUSE MERCURIOS_LOADING_WH SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1;
ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1;
ALTER WAREHOUSE MERCURIOS_DEV_WH SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1;
ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET MAX_CLUSTER_COUNT = 1, MIN_CLUSTER_COUNT = 1 IF EXISTS;
```

2. **Check Fivetran Integration**:
   - Log into Fivetran and pause any active connectors
   - Reduce sync frequency for all connectors to daily or weekly
   - Check if there are any failing connectors causing repeated retries

## Root Causes Analysis

Based on the Snowflake cost insights panel, these issues are contributing to high costs:

1. **Large tables that are never queried** - Storing data that's not being used
2. **Tables where data is written but not read** - Wasting compute resources
3. **Rarely used materialized views** - These consume credits to maintain
4. **Short-lived permanent tables** - Creating and dropping tables frequently
5. **Rarely used search optimization paths** - Expensive feature that's not being utilized
6. **Rarely used tables with automatic clustering** - Auto-clustering consumes credits
7. **Inefficient usage of multi-cluster warehouses** - Paying for capacity you don't need

## Medium-Term Actions (Next 7 Days)

1. **Implement Resource Monitors** (requires ACCOUNTADMIN):
   ```sql
   -- Create a resource monitor with a 10 credit daily limit
   CREATE OR REPLACE RESOURCE MONITOR EMERGENCY_MONITOR
   WITH CREDIT_QUOTA = 10
   FREQUENCY = DAILY
   START_TIMESTAMP = CURRENT_TIMESTAMP
   TRIGGERS
   ON 80 PERCENT DO NOTIFY
   ON 90 PERCENT DO NOTIFY
   ON 100 PERCENT DO SUSPEND;
   
   -- Apply to all warehouses
   ALTER WAREHOUSE MERCURIOS_LOADING_WH SET RESOURCE_MONITOR = EMERGENCY_MONITOR;
   ALTER WAREHOUSE MERCURIOS_ANALYTICS_WH SET RESOURCE_MONITOR = EMERGENCY_MONITOR;
   ALTER WAREHOUSE MERCURIOS_DEV_WH SET RESOURCE_MONITOR = EMERGENCY_MONITOR;
   ALTER WAREHOUSE FIVETRAN_WAREHOUSE SET RESOURCE_MONITOR = EMERGENCY_MONITOR IF EXISTS;
   ```

2. **Review Expensive Queries**:
   - Analyze the "Most expensive queries" section from your screenshots
   - Focus on optimizing queries from FIVETRAN_USER that are consuming the most resources

3. **Optimize Data Pipeline**:
   - Review your dbt models for inefficient queries
   - Implement incremental models instead of full refreshes
   - Add appropriate filters to limit data scanned

## Long-Term Cost Optimization (Next 30 Days)

1. **Implement Data Retention Policies**:
   ```sql
   -- Set retention period for transient tables to 1 day
   ALTER DATABASE MERCURIOS_DATA SET DATA_RETENTION_TIME_IN_DAYS = 1;
   
   -- Reduce time travel for development schemas
   ALTER SCHEMA MERCURIOS_DATA.STAGING SET DATA_RETENTION_TIME_IN_DAYS = 1;
   ```

2. **Optimize Warehouse Usage**:
   - Schedule warehouses to scale based on workload patterns
   - Use separate warehouses for different workload types
   - Implement query tagging to track cost by feature/team

3. **Implement Cost Governance**:
   - Create cost monitoring dashboards
   - Set up email alerts for unusual spending
   - Implement chargeback mechanisms for different teams/features

## Monitoring Plan

1. **Daily Cost Check**:
   - Review the Snowflake cost management page daily
   - Track credit usage by warehouse
   - Identify any unexpected spikes

2. **Weekly Optimization Review**:
   - Review most expensive queries
   - Implement targeted optimizations
   - Update resource monitors as needed

3. **Monthly Cost Analysis**:
   - Compare month-over-month spending
   - Adjust budgets and resource limits
   - Review and update cost optimization strategy

## Conclusion

The current Snowflake costs are unsustainable at $48.94/day. By implementing the immediate actions, you should be able to reduce costs by 80-90% while still maintaining essential functionality. The medium and long-term actions will help establish proper cost governance to prevent future cost overruns.

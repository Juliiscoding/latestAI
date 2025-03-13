# Mercurios.ai Snowflake Cost Optimization Guide

## Overview
This guide outlines the comprehensive cost optimization measures implemented for Mercurios.ai's Snowflake environment. These optimizations are designed to significantly reduce credit consumption while maintaining full functionality and data insights.

## Implemented Optimizations

### 1. Warehouse Size Optimizations
- **MERCURIOS_LOADING_WH**: Reduced to XSMALL (from MEDIUM)
  - Added query acceleration to maintain performance
  - Potential savings: 60-75% on this warehouse
- **FIVETRAN_WAREHOUSE**: Reduced to XSMALL
- **MERCURIOS_DEV_WH**: Reduced to XSMALL

### 2. Auto-Suspend Settings
- All warehouses set to 60-second auto-suspend
- Eliminates idle warehouse costs
- Particularly impactful for intermittently used warehouses

### 3. Cluster Limits
- MERCURIOS_LOADING_WH: MIN=1, MAX=2
- FIVETRAN_WAREHOUSE: MIN=1, MAX=1
- Prevents unexpected scaling costs during peak periods

### 4. Resource Monitor
- Monthly credit quota: 80 credits
- Notification triggers: 70% (56 credits) and 90% (72 credits)
- Suspension trigger: 95% (76 credits)
- Applied to all warehouses

### 5. Query Performance Optimizations
- Enabled result caching for repetitive queries
- Set statement timeout limits to prevent runaway queries
- Added query acceleration for MERCURIOS_LOADING_WH

### 6. Monitoring Views
- **warehouse_cost_monitoring**: Tracks credit usage by warehouse
- **query_cost_by_type**: Identifies expensive query types
- **expensive_queries**: Lists the most credit-intensive queries
- **large_tables_for_partitioning**: Identifies tables that would benefit from partitioning
- **materialized_view_candidates**: Identifies frequently run queries that could be materialized
- **snowpipe_monitoring**: Tracks Snowpipe operations for Fivetran optimization

### 7. Advanced Optimization Tools
- Created stored procedure for scheduling ETL jobs during off-peak hours
- Created stored procedure for analyzing and optimizing expensive queries
- Enabled query tagging for better cost attribution

## Monthly Credit Budget

Based on current usage patterns and implemented optimizations:

- **Previous monthly run rate**: ~130 credits
- **New target monthly budget**: 80 credits
- **Expected savings**: 50+ credits per month

## Monitoring and Maintenance

### Weekly Tasks
1. Review the `warehouse_cost_monitoring` view
2. Check for any unexpected spikes in usage
3. Run the `optimize_expensive_queries` procedure

### Monthly Tasks
1. Compare actual usage against the 80-credit budget
2. Review the `materialized_view_candidates` view and implement new materialized views
3. Review the `large_tables_for_partitioning` view and implement partitioning for large tables

### Quarterly Tasks
1. Reassess warehouse sizes based on usage patterns
2. Review and adjust the resource monitor quota if needed
3. Evaluate Snowpipe implementation for Fivetran data loading

## Using the Advanced Optimization Script

The `advanced_snowflake_optimization.sh` script applies all these optimizations automatically:

```bash
# Make the script executable
chmod +x advanced_snowflake_optimization.sh

# Run the script
./advanced_snowflake_optimization.sh
```

## Useful Commands

### View Cost Monitoring Dashboard
```sql
SELECT * FROM MERCURIOS_DATA.PUBLIC.warehouse_cost_monitoring LIMIT 10;
```

### Identify Materialized View Candidates
```sql
SELECT * FROM MERCURIOS_DATA.PUBLIC.materialized_view_candidates LIMIT 10;
```

### Identify Large Tables for Partitioning
```sql
SELECT * FROM MERCURIOS_DATA.PUBLIC.large_tables_for_partitioning LIMIT 10;
```

### Get Recommendations for Optimizing Expensive Queries
```sql
CALL MERCURIOS_DATA.PUBLIC.optimize_expensive_queries();
```

### Check Warehouse Configurations
```sql
SELECT WAREHOUSE_NAME, WAREHOUSE_SIZE, AUTO_SUSPEND, RESOURCE_MONITOR 
FROM INFORMATION_SCHEMA.WAREHOUSES;
```

## Additional Recommendations

### For ETL Processes
- Schedule ETL jobs during off-peak hours (nights/weekends)
- Consider implementing Snowpipe for continuous micro-batch loading
- Evaluate if any transformations can be pushed to the source system

### For Analytics Queries
- Create materialized views for frequently run analytical queries
- Implement proper clustering keys on large tables
- Train users on writing efficient SQL queries

### For Development Work
- Use smaller warehouses for development and testing
- Implement separate development environments with stricter resource limits
- Consider using time travel judiciously to reduce storage costs

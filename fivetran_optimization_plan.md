# Fivetran Connector Optimization Plan

## Executive Summary

Based on our analysis of your Fivetran connectors, we've identified opportunities to optimize sync frequencies and reduce costs while preserving business value. This document outlines a practical implementation plan for each connector.

## Connector Value Analysis Results

| Connector | Value Score | Size (MB) | Query Count | Recommendation |
|-----------|-------------|-----------|-------------|----------------|
| Shopify | 1.70 | 1,080 | 1,839 | HIGH VALUE - Keep syncing regularly |
| Klaviyo | 0.77 | 396 | 307 | MEDIUM VALUE - Reduce sync frequency |
| Google Analytics | 0.65 | 464 | 304 | MEDIUM VALUE - Reduce sync frequency |
| AWS Lambda | 0.50 | 130 | 65 | MEDIUM VALUE - Reduce sync frequency |
| Unknown Sources | 0.08 | 36 | 3 | LOW VALUE - Consider pausing |

## Implementation Steps

### 1. Log into Fivetran

1. Navigate to [Fivetran Dashboard](https://fivetran.com/dashboard)
2. Log in with your credentials
3. Select the MERCURIOS destination

### 2. Optimize Shopify Connector (HIGH VALUE)

1. Navigate to the Shopify connector
2. Click "Configuration"
3. Under "Sync Frequency":
   - Change from "Continuous" to "Daily"
   - Set sync time to 1:00 AM (off-hours)
4. Under "Historical Sync":
   - Set to "Incremental" to reduce data volume
5. Save changes

### 3. Optimize Klaviyo Connector (MEDIUM VALUE)

1. Navigate to the Klaviyo connector
2. Click "Configuration"
3. Under "Sync Frequency":
   - Change from "Continuous" to "Daily"
   - Set sync time to 2:00 AM (off-hours)
4. Review schema and disable syncing for unused tables
5. Save changes

### 4. Optimize Google Analytics Connector (MEDIUM VALUE)

1. Navigate to the Google Analytics connector
2. Click "Configuration"
3. Under "Sync Frequency":
   - Change from "Continuous" to "Daily"
   - Set sync time to 3:00 AM (off-hours)
4. Under "Schema":
   - Disable syncing for unused report types
   - Focus on core metrics (sessions, users, conversions)
5. Save changes

### 5. Optimize AWS Lambda Connector (MEDIUM VALUE)

1. Navigate to the AWS Lambda connector
2. Click "Configuration"
3. Under "Sync Frequency":
   - Change from "Continuous" to "Daily"
   - Set sync time to 12:00 AM (midnight)
4. Save changes

### 6. Pause Low-Value Connectors

For any connectors identified as "unknown" or with very low value scores:
1. Navigate to the connector
2. Click "Configuration"
3. Click "Pause Sync"
4. Document which connectors were paused for future reference

## Verification Process

After implementing these changes, verify the optimization:

1. Monitor Snowflake credit usage for 7 days
2. Check that data is still being loaded successfully
3. Confirm that business reports and dashboards are still functioning correctly

## Expected Outcomes

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Fivetran Sync Frequency | Continuous | Daily/Weekly | 70-90% reduction |
| Data Freshness | Real-time | 24-hour delay | Acceptable for most use cases |
| Snowflake Compute Usage | Frequent | Scheduled | 50-70% reduction |
| Monthly Cost | $X | $Y | Estimated 60% reduction |

## Monitoring and Adjustment

1. Set up a monthly review of connector usage and value
2. Adjust sync frequencies based on changing business needs
3. Document any issues with data freshness that arise

By implementing this plan, you'll significantly reduce costs while maintaining the business value of your data pipelines.

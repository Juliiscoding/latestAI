# Fivetran Sync Monitoring Report

Generated: 2025-03-05 09:21:44

## Table Record Counts

| Table | Count | Min Required | Status |
|-------|-------|-------------|--------|
| article | 0 | 1 | ERROR: 'Engine' object has no attribute 'execute' |
| customer | 0 | 1 | ERROR: 'Engine' object has no attribute 'execute' |
| order | 0 | 1 | ERROR: 'Engine' object has no attribute 'execute' |
| sale | 0 | 1 | ERROR: 'Engine' object has no attribute 'execute' |
| inventory | 0 | 1 | ERROR: 'Engine' object has no attribute 'execute' |
| daily_sales_agg | 0 | 0 | ERROR: 'Engine' object has no attribute 'execute' |
| article_sales_agg | 0 | 0 | ERROR: 'Engine' object has no attribute 'execute' |
| warehouse_inventory_agg | 0 | 0 | ERROR: 'Engine' object has no attribute 'execute' |

## Data Freshness

| Table | Latest Timestamp | Age (hours) | Max Age | Status |
|-------|-----------------|-------------|---------|--------|
| article | None | N/A | N/A | ERROR: 'Engine' object has no attribute 'execute' |
| customer | None | N/A | N/A | ERROR: 'Engine' object has no attribute 'execute' |
| order | None | N/A | N/A | ERROR: 'Engine' object has no attribute 'execute' |
| sale | None | N/A | N/A | ERROR: 'Engine' object has no attribute 'execute' |
| inventory | None | N/A | N/A | ERROR: 'Engine' object has no attribute 'execute' |
| daily_sales_agg | None | N/A | N/A | ERROR: 'Engine' object has no attribute 'execute' |
| article_sales_agg | None | N/A | N/A | ERROR: 'Engine' object has no attribute 'execute' |
| warehouse_inventory_agg | None | N/A | N/A | ERROR: 'Engine' object has no attribute 'execute' |

## Lambda Function Errors

```
{
    "events": [],
    "searchedLogStreams": []
}

```

## Next Steps

1. Address any errors or warnings in the report
2. Run full data quality checks with `python data_quality_monitor.py`
3. Run dbt models to transform the data
4. Create dashboards based on the transformed data

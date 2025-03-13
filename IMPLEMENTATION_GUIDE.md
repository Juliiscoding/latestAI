# ProHandel Integration Implementation Guide

This guide provides step-by-step instructions for implementing the ProHandel integration using our hybrid approach.

## Architecture Overview

Our implementation follows a hybrid approach:

### Pre-Fivetran (Lambda)
- Basic aggregations and calculations that reduce data volume
- Critical transformations needed for data consistency
- Creation of unique identifiers for aggregated records

### Post-Fivetran (dbt)
- Business logic and complex calculations
- Joining data from multiple sources
- Creating final analytical models
- Implementing data quality tests

## Implementation Steps

### Step 1: Configure Fivetran Connector

Follow the checklist in `fivetran_setup_checklist.md` to:

1. Gather required information (Lambda ARN, API credentials)
2. Create and configure the AWS Lambda connector in Fivetran
3. Set up schema and destination
4. Start the initial sync

Detailed instructions are available in `/lambda_connector/FIVETRAN_CONFIGURATION_GUIDE.md`.

```bash
# Find your Lambda ARN if needed
aws lambda list-functions --region eu-central-1 | grep -A 2 "ProHandel"
```

### Step 2: Monitor Initial Sync

Use the `monitor_sync.py` script to monitor the initial sync process:

```bash
# Install required packages
pip install pandas sqlalchemy psycopg2-binary

# Run the monitoring script
python monitor_sync.py --config data_quality_config.json --output sync_monitor_report.md
```

This script will:
- Check record counts for all tables
- Verify data freshness
- Monitor Lambda function logs for errors
- Generate a monitoring report

### Step 3: Run Data Quality Checks

Once the initial sync is complete, run the data quality checks:

```bash
python data_quality_monitor.py --config data_quality_config.json --output data_quality_report.md
```

Review the data quality report and address any issues found.

### Step 4: Set Up dbt Project

Use the `run_dbt_models.sh` script to set up and run the dbt models:

```bash
./run_dbt_models.sh
```

This script will:
- Check database connection
- Install dbt dependencies
- Run all dbt models
- Run dbt tests
- Generate and serve documentation

### Step 5: Create Dashboards

Use the `dashboard_config.json` file as a reference to create dashboards in your BI tool:

1. Connect your BI tool to the database
2. Create the dashboards defined in the configuration
3. Set up scheduled refreshes

## Files and Resources

- `/lambda_connector/FIVETRAN_CONFIGURATION_GUIDE.md`: Detailed guide for Fivetran configuration
- `fivetran_setup_checklist.md`: Checklist for Fivetran setup
- `monitor_sync.py`: Script to monitor the sync process
- `data_quality_monitor.py`: Script to run data quality checks
- `data_quality_config.json`: Configuration for data quality checks
- `run_dbt_models.sh`: Script to run dbt models
- `dbt_prohandel/`: dbt project for data transformation
- `dashboard_config.json`: Configuration for dashboards

## Maintenance and Troubleshooting

### Regular Maintenance

1. Monitor sync status in Fivetran dashboard
2. Run data quality checks regularly
3. Update dbt models as needed
4. Review dashboards for insights

### Troubleshooting

- **Fivetran Sync Issues**: Check Fivetran logs and Lambda CloudWatch logs
- **Data Quality Issues**: Run data quality checks and review the report
- **dbt Model Failures**: Check dbt logs and fix any errors
- **Missing Data**: Verify ProHandel API is returning expected data

## Support

- For issues with the ProHandel API: Contact ProHandel support
- For issues with the Lambda function: Check AWS CloudWatch logs
- For issues with Fivetran: Contact Fivetran support at support@fivetran.com
- For issues with dbt models: Refer to dbt documentation at https://docs.getdbt.com/

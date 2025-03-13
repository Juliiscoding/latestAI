# Fivetran Setup Checklist

## Step 1: Gather Required Information

- [ ] AWS Lambda Function ARN: _________________________
  - If not available, run `aws lambda list-functions --region eu-central-1 | grep -A 2 "ProHandel"` to find it
  - Or check the AWS Lambda Console under Functions

- [ ] AWS Region: eu-central-1 (or your deployed region)

- [ ] ProHandel API Credentials:
  - Username: _________________________
  - Password: _________________________
  - Auth URL: https://auth.prohandel.cloud/api/v4
  - API URL: https://api.prohandel.de/api/v2

## Step 2: Fivetran Connector Setup

- [ ] Log in to Fivetran account: https://fivetran.com/dashboard
- [ ] Create new AWS Lambda connector
- [ ] Configure connector with name: "ProHandel Data"
- [ ] Enter AWS Lambda details:
  - Region: eu-central-1
  - Function ARN: (from Step 1)
  - Execution Timeout: 180 seconds
- [ ] Add secrets:
  - PROHANDEL_USERNAME: (from Step 1)
  - PROHANDEL_PASSWORD: (from Step 1)
  - PROHANDEL_AUTH_URL: https://auth.prohandel.cloud/api/v4
  - PROHANDEL_API_URL: https://api.prohandel.de/api/v2
- [ ] Test connection
- [ ] Configure schema (select all tables)
- [ ] Configure destination database
- [ ] Set sync schedule (recommended: hourly)
- [ ] Start initial sync

## Step 3: Monitor Initial Sync

- [ ] Check sync status in Fivetran dashboard
- [ ] Monitor AWS CloudWatch logs:
  ```
  aws logs filter-log-events --log-group-name /aws/lambda/prohandel-connector --start-time $(date -v-1H +%s)000
  ```
- [ ] Verify data is being loaded into destination database
- [ ] Check for any errors or warnings

## Step 4: Run Data Quality Checks

- [ ] Update database connection in data_quality_config.json
- [ ] Run data quality checks:
  ```
  python data_quality_monitor.py --config data_quality_config.json --output data_quality_report.md
  ```
- [ ] Review data quality report
- [ ] Address any issues found

## Step 5: Set Up dbt Project

- [ ] Update profiles.yml with correct database connection
- [ ] Install dbt dependencies:
  ```
  cd dbt_prohandel
  dbt deps
  ```
- [ ] Run dbt models:
  ```
  dbt run
  ```
- [ ] Run dbt tests:
  ```
  dbt test
  ```
- [ ] Verify transformed data in the database

## Step 6: Create Dashboards

- [ ] Connect BI tool to database
- [ ] Create inventory overview dashboard
- [ ] Create sales performance dashboard
- [ ] Create demand forecast dashboard
- [ ] Set up scheduled refreshes

## Notes and Issues

_Use this section to document any issues or notes during the setup process_

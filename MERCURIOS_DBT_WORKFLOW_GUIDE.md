# Mercurios.ai dbt Workflow Guide

## Overview
This guide provides a comprehensive workflow for developing and running dbt models for the Mercurios.ai Predictive Inventory Management system, with options for both local development and Snowflake deployment.

## Development Workflow

### Local Development (No Snowflake Authentication Required)
Use this workflow for developing and testing models without needing Snowflake access:

1. **Setup Local Environment**
   ```bash
   # Install required packages
   pip install dbt-duckdb
   
   # Run models locally
   ./run_dbt_local.sh
   ```

2. **Benefits of Local Development**
   - No authentication issues
   - Faster iteration cycles
   - Works offline
   - No Snowflake compute costs

3. **Limitations**
   - DuckDB syntax may differ slightly from Snowflake
   - Some Snowflake-specific functions need adaptation
   - Sample data must be created locally

### Snowflake Deployment
Use this workflow when you need to run models in Snowflake:

1. **Authentication Options**

   a. **Password Authentication**
   ```bash
   # Set password and run
   export DBT_PASSWORD="your-password"
   ./run_dbt_models.sh
   ```

   b. **Browser Authentication**
   ```bash
   # Uses browser-based authentication
   ./run_dbt_models.sh
   ```

2. **Troubleshooting Duo Authentication**
   - If locked out, contact Duo administrator
   - Consider using the Duo mobile app instead of push notifications
   - Try authenticating via the Snowflake web UI first, then run dbt

## Model Structure

### Staging Models (`/models/staging/`)
- Clean and standardize raw data
- Apply basic transformations
- Implement data quality checks

### Intermediate Models (`/models/intermediate/`)
- Join and aggregate staging models
- Calculate metrics and KPIs
- Prepare data for downstream analysis

### Mart Models (`/models/marts/`)
- Create business-specific views
- Generate forecasts and recommendations
- Provide actionable insights

## Best Practices

### Development Process
1. Develop and test models locally with DuckDB
2. Adapt any DuckDB-specific syntax for Snowflake
3. Run models in Snowflake when authentication is available
4. Document all models thoroughly

### Authentication Management
1. Use environment variables for credentials
2. Consider key pair authentication for automation
3. Minimize authentication frequency with session reuse
4. Use browser-based authentication when possible

### Performance Optimization
1. Use appropriate warehouse sizes
2. Implement incremental models for large datasets
3. Use clustering keys for frequently filtered columns
4. Leverage Snowflake materialized views for complex calculations

## Troubleshooting

### Common Issues

#### Authentication Problems
- **Duo Lock**: Contact administrator to unlock account
- **Connection Timeout**: Check network and VPN settings
- **Invalid Credentials**: Verify username and password

#### Model Failures
- **SQL Syntax**: Check for database-specific functions
- **Missing Relations**: Verify source tables exist
- **Permission Errors**: Check role permissions

### Debugging Tools
- `dbt debug`: Check configuration and connection
- `dbt compile`: Verify SQL syntax without running
- `dbt parse`: Validate project structure

## Continuous Integration

### GitHub Actions
Example workflow for CI/CD:
```yaml
name: dbt CI

on:
  push:
    branches: [ main, development ]
  pull_request:
    branches: [ main ]

jobs:
  dbt-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install dbt-snowflake
      - name: Run dbt tests
        run: dbt test
        env:
          DBT_PROFILES_DIR: ./
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
```

## Next Steps

1. **Develop Sample Data**
   - Create representative sample datasets
   - Test all models with sample data locally

2. **Implement Data Quality Tests**
   - Add schema tests for all models
   - Create custom data quality tests

3. **Create Visualization Layer**
   - Connect BI tools to dbt models
   - Create dashboards for inventory insights

4. **Automate Model Runs**
   - Set up scheduled runs
   - Implement alerting for failures

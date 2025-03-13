# Mercurios.ai dbt Model Guide

## Overview
This guide provides instructions for running and maintaining the dbt models for the Mercurios.ai Predictive Inventory Management system. The models transform raw ProHandel data into actionable insights for inventory management.

## Model Structure
The dbt models are organized in a modular structure:

1. **Staging Models** (`/models/staging/`)
   - Clean and standardize raw data
   - Apply basic transformations
   - Implement data quality checks

2. **Intermediate Models** (`/models/intermediate/`)
   - Join and aggregate staging models
   - Calculate metrics and KPIs
   - Prepare data for downstream analysis

3. **Mart Models** (`/models/marts/`)
   - Create business-specific views
   - Generate forecasts and recommendations
   - Provide actionable insights

## Running the Models

### Prerequisites
- Snowflake access with appropriate permissions
- dbt installed (`pip install dbt-snowflake`)
- Configured profiles.yml file

### Using the Automated Script
The `run_dbt_models.sh` script automates the process of running all models in the correct order:

```bash
# Set your password as an environment variable
export DBT_PASSWORD="your-password"

# Run the script
./run_dbt_models.sh
```

This script:
- Runs all models in a single authenticated session (minimizing Duo prompts)
- Executes models in the proper dependency order
- Runs tests to validate data quality
- Generates and serves documentation

### Manual Execution
If you prefer to run models manually:

```bash
# Navigate to the dbt project directory
cd dbt_mercurios

# Run specific model groups
dbt run --models staging
dbt run --models intermediate
dbt run --models marts

# Run specific models
dbt run --models marts.inventory.reorder_recommendations

# Run tests
dbt test

# Generate docs
dbt docs generate
dbt docs serve
```

## Troubleshooting

### Authentication Issues
If you encounter Duo Security authentication issues:

1. Refer to `DUO_CONFIGURATION_GUIDE.md` for solutions
2. Use a single terminal session for all operations
3. Ensure your profiles.yml has these settings:
   ```yaml
   client_session_keep_alive: True
   reuse_connections: True
   connect_retries: 3
   connect_timeout: 30
   retry_on_database_errors: True
   ```

### Model Failures
If specific models fail:

1. Check for schema changes in source data
2. Verify Snowflake permissions
3. Review error messages for specific issues
4. Run `dbt compile` to check for SQL errors before execution

## Model Descriptions

### Staging Models

#### stg_prohandel__articles
Transforms raw article data, adding:
- Profit margin calculations
- Price tier categorization
- ABC classification

#### stg_prohandel__inventory
Processes inventory data, adding:
- Stock level categorization
- Inventory value calculations
- Stockout risk assessment

#### stg_prohandel__sales
Transforms sales data, adding:
- Net price calculations
- Profit margin analysis
- Sales categorization

### Intermediate Models

#### int_inventory_with_metrics
Combines inventory and sales data to calculate:
- Historical sales metrics
- Inventory turnover rates
- Days of supply
- Seasonal patterns

### Mart Models

#### demand_forecast
Generates demand forecasts using:
- Historical sales data
- Seasonality factors
- Growth trends
- Moving averages

#### inventory_status
Provides current inventory status with:
- Stock level assessments
- Turnover metrics
- Value analysis
- Stockout risk evaluation

#### reorder_recommendations
Generates actionable reorder recommendations:
- Prioritized reorder lists
- Economic order quantities
- Reorder points
- Safety stock calculations

## Maintenance and Updates

### Adding New Models
1. Create SQL file in appropriate directory
2. Follow existing naming conventions
3. Add documentation using dbt docs
4. Update dependencies in schema.yml

### Modifying Existing Models
1. Test changes in development environment
2. Update documentation
3. Run and test dependent models
4. Update schema.yml if field changes are made

## Data Quality Checks
All models include data quality tests defined in schema.yml files:
- Not null constraints
- Uniqueness checks
- Referential integrity
- Custom business logic tests

## Documentation
Full documentation is available by running:
```bash
dbt docs generate
dbt docs serve
```

Then visit http://localhost:8080 in your browser.

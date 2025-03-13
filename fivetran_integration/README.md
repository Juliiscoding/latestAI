# Fivetran Integration for Mercurios.ai

This module integrates Fivetran with the Mercurios.ai data quality monitoring system, enabling comprehensive data quality checks on data loaded by Fivetran.

## Overview

The Fivetran integration consists of two main components:

1. **ProHandel Fivetran Connector**: A custom connector that extracts data from the ProHandel API and loads it into your data warehouse via Fivetran.

2. **Fivetran Quality Monitor**: A system that applies the Mercurios.ai data quality monitoring to data loaded by Fivetran.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Fivetran account
- ProHandel API credentials
- Access to your data warehouse (PostgreSQL, Snowflake, BigQuery, etc.)

### Installation

1. Set up the ProHandel Fivetran Connector:
   - Follow the instructions in `/fivetran_connector/README.md`

2. Configure the Fivetran Quality Monitor:
   - Edit `config.json` to include your database connection details and Fivetran API credentials
   - Set up your data quality monitoring configuration

### Configuration

The `config.json` file contains the following sections:

- **database**: Connection details for your data warehouse
- **fivetran**: API credentials and connector ID
- **data_quality**: Configuration for data quality monitoring
- **notification**: Settings for email and Slack notifications
- **scheduling**: Frequency and timing for automated runs

## Usage

### Running the Orchestrator

```bash
# Run the full pipeline (sync + quality checks)
python orchestrator.py

# Only run the sync
python orchestrator.py --sync-only

# Only run quality checks
python orchestrator.py --quality-only

# Force quality checks despite issues
python orchestrator.py --force-quality
```

### Scheduling

You can schedule the orchestrator to run automatically using cron or a similar scheduling system:

```bash
# Example cron entry to run daily at 1 AM
0 1 * * * cd /path/to/fivetran_integration && python orchestrator.py
```

## Data Quality Monitoring

The Fivetran Quality Monitor applies the following checks to your data:

- **Completeness**: Checks for missing values in required fields
- **Outlier Detection**: Identifies statistical outliers in numerical data
- **Consistency**: Validates data consistency and referential integrity
- **Format Validation**: Ensures data formats match expected patterns
- **Freshness**: Verifies that data is up-to-date

## Integration with Existing Systems

This integration works alongside your existing ETL pipeline and data quality monitoring system. It adds the ability to:

1. Use Fivetran's managed infrastructure for data extraction and loading
2. Apply your comprehensive data quality checks to Fivetran-loaded data
3. Generate alerts and reports for data quality issues
4. Automate the entire process

## Troubleshooting

- Check the `fivetran_orchestrator.log` file for detailed logs
- Verify your Fivetran API credentials and connector ID
- Ensure your database connection string is correct
- Check the data quality reports in the `fivetran_data_quality_reports` directory

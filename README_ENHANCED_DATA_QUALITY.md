# Enhanced Data Quality Monitoring System

## Overview

The Enhanced Data Quality Monitoring System extends the Mercurios.ai Predictive Inventory Management tool with advanced data quality validation capabilities. This system integrates seamlessly with the existing ETL pipeline to ensure data integrity, accuracy, and reliability throughout the data processing workflow.

## Key Features

### 1. Format Validation

The Format Validation monitor checks if data values conform to expected patterns and formats:

- **Email validation**: Ensures email addresses follow standard format
- **Phone number validation**: Verifies phone numbers match expected patterns
- **Custom pattern validation**: Supports custom regex patterns for specific data fields
- **Configurable violation thresholds**: Set acceptable violation rates for different data types

### 2. Freshness Monitoring

The Freshness Monitor ensures data is up-to-date and relevant:

- **Timestamp-based validation**: Checks if data is recent based on timestamp columns
- **Configurable age thresholds**: Define what constitutes "fresh" vs. "stale" data
- **Multiple freshness rules**: Apply different freshness requirements to different data types
- **Severity levels**: Assign appropriate severity to freshness violations

### 3. Optimized Sampling Strategies

For large datasets, the system implements intelligent sampling strategies:

- **Random sampling**: Basic random selection for general data quality assessment
- **Stratified sampling**: Ensures representation across important data categories
- **Outlier-biased sampling**: Prioritizes potential problem areas in the data
- **Configurable sample sizes**: Adjust sample size based on dataset characteristics

### 4. Integration with ETL Pipeline

The enhanced data quality monitoring is fully integrated with the ETL pipeline:

- **Pre-load validation**: Validate data before loading into the database
- **Quality-based decision making**: Optionally block loading of low-quality data
- **Detailed quality reporting**: Generate comprehensive reports of data quality issues
- **Visualization**: Create visual representations of data quality metrics

## Components

### Enhanced ETL Orchestrator

The `EnhancedETLOrchestrator` extends the standard `ETLOrchestrator` with data quality monitoring capabilities:

```python
# Initialize enhanced ETL orchestrator
orchestrator = EnhancedETLOrchestrator(
    db_session=db_session,
    incremental=True,
    data_quality_config=dq_config
)

# Run ETL with data quality monitoring
results = orchestrator.run_etl(entities=["article", "customer", "inventory"])

# Get quality summary
quality_summary = orchestrator.get_quality_summary()
```

### Data Quality Monitors

The system includes the following monitors:

1. **CompletenessMonitor**: Checks for missing values in data
2. **OutlierMonitor**: Detects outliers using statistical methods
3. **ConsistencyMonitor**: Checks for duplicates, uniqueness, and constraint violations
4. **FormatMonitor**: Validates data formats using regex patterns
5. **FreshnessMonitor**: Checks if data is up-to-date based on timestamp columns

### Data Sampler

The `DataSampler` class provides various sampling methods:

```python
# Sample data using different strategies
sampled_data, metadata = sampler.sample_data(
    data,
    strategy="outlier_biased",
    sample_size=2000,
    outlier_fraction=0.3
)
```

## Configuration

The data quality monitoring system is highly configurable:

```python
config = {
    "output_dir": "data_quality_reports",
    "sampling": {
        "enabled": True,
        "min_data_size_for_sampling": 5000,
        "default_sample_size": 2000,
        "strategy": "outlier_biased",
        "outlier_fraction": 0.3,
        "outlier_method": "zscore",
        "outlier_threshold": 3.0
    },
    "monitors": {
        "completeness": {
            "columns": ["article_id", "name", "price", "category"],
            "min_completeness_ratio": 0.98,
            "severity": "warning"
        },
        "outlier": {
            "columns": ["price", "stock_quantity"],
            "method": "zscore",
            "threshold": 3.0,
            "max_outlier_ratio": 0.05,
            "severity": "warning"
        },
        "consistency": {
            "unique_columns": ["article_id"],
            "max_violation_ratio": 0.05,
            "severity": "error"
        },
        "format": {
            "format_rules": [
                {
                    "name": "article_id_format",
                    "columns": ["article_id"],
                    "custom_pattern": r"^[A-Z0-9-]+$"
                },
                {
                    "name": "email_format",
                    "columns": ["email"],
                    "pattern_type": "email"
                }
            ],
            "max_violation_ratio": 0.03,
            "severity": "error"
        },
        "freshness": {
            "freshness_rules": [
                {
                    "name": "recent_update",
                    "column": "last_updated",
                    "max_age": 30,
                    "max_age_unit": "days",
                    "threshold": 0.1,
                    "severity": "warning"
                }
            ],
            "severity": "warning"
        }
    }
}
```

## Output and Reporting

The system generates comprehensive reports of data quality issues:

- **JSON reports**: Detailed reports of data quality issues in JSON format
- **Visualizations**: Charts and graphs showing data quality metrics
- **Alerts**: Categorized by severity (info, warning, error, critical)
- **Summary statistics**: Overall data quality metrics

## Integration with Mercurios.ai Dashboard

The enhanced data quality monitoring system integrates with the Mercurios.ai dashboard:

- **Quality metrics display**: View data quality metrics in the dashboard
- **Alert notifications**: Receive notifications of critical data quality issues
- **Trend analysis**: Track data quality over time
- **Drill-down capabilities**: Investigate specific data quality issues

## Usage Examples

### Basic Usage

```python
from etl.enhanced_orchestrator import EnhancedETLOrchestrator
from etl.utils.database import get_db_session

# Get database session
db_session = get_db_session()

# Initialize enhanced ETL orchestrator
orchestrator = EnhancedETLOrchestrator(
    db_session=db_session,
    incremental=True
)

# Run ETL with data quality monitoring
results = orchestrator.run_etl(entities=["article", "customer", "inventory"])

# Get quality summary
quality_summary = orchestrator.get_quality_summary()
```

### Custom Configuration

```python
# Custom data quality configuration
dq_config = {
    "output_dir": "custom_reports",
    "sampling": {
        "enabled": True,
        "strategy": "stratified",
        "stratify_columns": ["category"]
    },
    "monitors": {
        "format": {
            "format_rules": [
                {
                    "name": "custom_id_format",
                    "columns": ["id"],
                    "custom_pattern": r"^[A-Z]{2}\d{6}$"
                }
            ]
        },
        "freshness": {
            "freshness_rules": [
                {
                    "name": "daily_update",
                    "column": "timestamp",
                    "max_age": 1,
                    "max_age_unit": "days"
                }
            ]
        }
    }
}

# Initialize with custom configuration
orchestrator = EnhancedETLOrchestrator(
    db_session=db_session,
    data_quality_config=dq_config
)
```

## Conclusion

The Enhanced Data Quality Monitoring System provides a robust framework for ensuring data quality in the Mercurios.ai Predictive Inventory Management tool. By integrating format validation, freshness checks, and optimized sampling strategies, the system enhances the reliability and accuracy of the data used for predictive analytics and decision-making.

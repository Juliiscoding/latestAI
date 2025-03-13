# Data Quality Monitoring for Mercurios.ai Predictive Inventory Management

This document provides an overview of the data quality monitoring system implemented for the Mercurios.ai Predictive Inventory Management tool. The system ensures that data used for predictions and analytics meets quality standards, helping to maintain the accuracy and reliability of inventory forecasts.

## Overview

The data quality monitoring system consists of:

1. **Base Monitor Framework**: A flexible, extensible framework for creating data quality monitors
2. **Specific Monitors**: Implementations for common data quality checks
3. **Data Quality Manager**: Coordinates multiple monitors and aggregates results
4. **Integration Points**: With ETL pipeline and prediction engine

## Components

### Base Monitor

The `BaseDataQualityMonitor` class in `data_quality/base_monitor.py` provides the foundation for all data quality monitors. It defines:

- Common interface for all monitors
- Threshold checking logic
- Alert generation and management
- Result formatting

### Specific Monitors

#### Completeness Monitor

Located in `data_quality/monitors/completeness_monitor.py`, this monitor:
- Checks for missing values in specified columns
- Calculates completeness ratios
- Generates alerts when completeness falls below thresholds

```python
from data_quality.monitors.completeness_monitor import CompletenessMonitor

monitor = CompletenessMonitor(config={
    'threshold': 0.95,  # 95% completeness required
    'columns': ['product_id', 'quantity'],  # Columns to check
    'severity': 'critical'  # Alert severity level
})

results = monitor.run(data)
```

#### Outlier Monitor

Located in `data_quality/monitors/outlier_monitor.py`, this monitor:
- Detects outliers in numerical columns using statistical methods
- Supports multiple detection methods (z-score, IQR, percentile)
- Calculates outlier ratios and identifies specific outlier values

```python
from data_quality.monitors.outlier_monitor import OutlierMonitor

monitor = OutlierMonitor(config={
    'method': 'zscore',  # Detection method
    'threshold': 3.0,  # Z-score threshold
    'columns': ['quantity', 'unit_price'],  # Columns to check
    'max_outlier_ratio': 0.05,  # Maximum acceptable outlier ratio
    'severity': 'warning'  # Alert severity level
})

results = monitor.run(data)
```

#### Consistency Monitor

Located in `data_quality/monitors/consistency_monitor.py`, this monitor:
- Checks for duplicate records
- Verifies uniqueness constraints
- Validates business rules and constraints between columns

```python
from data_quality.monitors.consistency_monitor import ConsistencyMonitor

monitor = ConsistencyMonitor(config={
    'duplicate_columns': ['order_id', 'product_id', 'order_date'],  # Check for duplicates
    'unique_columns': ['order_id'],  # Columns that should be unique
    'constraints': [
        {
            'name': 'delivery_after_order',
            'type': 'comparison',
            'columns': ['delivery_date', 'order_date'],
            'operator': '>'  # delivery_date should be greater than order_date
        }
    ],
    'severity': 'error'  # Alert severity level
})

results = monitor.run(data)
```

### Data Quality Manager

The `DataQualityManager` class in `data_quality/manager.py` coordinates multiple monitors and provides a unified interface:

```python
from data_quality.manager import DataQualityManager

config = {
    'output_dir': 'data_quality_reports',
    'monitors': {
        'completeness': {
            'threshold': 0.95,
            'severity': 'critical'
        },
        'outlier': {
            'method': 'zscore',
            'threshold': 3.0,
            'max_outlier_ratio': 0.05,
            'severity': 'warning'
        },
        'consistency': {
            'duplicate_columns': ['order_id', 'product_id'],
            'unique_columns': ['order_id'],
            'constraints': [
                {
                    'name': 'delivery_after_order',
                    'type': 'comparison',
                    'columns': ['delivery_date', 'order_date'],
                    'operator': '>'
                }
            ],
            'severity': 'error'
        }
    }
}

manager = DataQualityManager(config=config)
results = manager.run_monitors(data)
alerts = manager.get_alerts()
filepath = manager.save_results('quality_report.json')
```

## Integration with Prediction Engine

The data quality monitoring system is integrated with the prediction engine to ensure that models are trained and used with high-quality data:

```python
from prediction.engine import PredictionEngine

# Initialize prediction engine with data quality monitoring
engine_config = {
    'model_dir': 'models',
    'data_quality': {
        'enabled': True,
        'save_reports': True,
        'monitors': {
            'completeness': {
                'threshold': 0.95,
                'severity': 'critical'
            },
            'outlier': {
                'method': 'zscore',
                'threshold': 3.0,
                'max_outlier_ratio': 0.05,
                'severity': 'warning'
            }
        }
    }
}

engine = PredictionEngine(engine_config)

# Train model (will check data quality first)
engine.train_model('demand_forecast', data)

# Force training despite quality issues
engine.train_model('demand_forecast', data, force_train=True)

# Generate predictions (will check data quality first)
predictions = engine.predict('demand_forecast', data, horizon=30)

# Force prediction despite quality issues
predictions = engine.predict('demand_forecast', data, horizon=30, force_predict=True)
```

## Integration with ETL Pipeline

The data quality monitoring system can be integrated with the ETL pipeline to ensure that data is validated before being loaded into the database:

```python
from data_quality.manager import DataQualityManager

# Initialize data quality manager
manager = DataQualityManager(config=data_quality_config)

# During extraction phase
extracted_data = connector.extract_data()
quality_results = manager.run_monitors(extracted_data)

# Check for critical issues
critical_alerts = [alert for alert in quality_results['all_alerts'] 
                  if alert['severity'] == 'critical']

if critical_alerts:
    # Handle critical issues (e.g., abort, notify, fix)
    logger.error(f"ETL aborted due to {len(critical_alerts)} critical data quality issues")
    # Send notification to data engineers
    notify_data_engineers(critical_alerts)
else:
    # Proceed with transformation and loading
    transformed_data = transformer.transform(extracted_data)
    loader.load(transformed_data)
```

## Demo Scripts

Several demo scripts are provided to showcase the data quality monitoring system:

1. **demo_data_quality.py**: Demonstrates basic usage of data quality monitors
2. **demo_prediction_with_quality.py**: Shows integration with the prediction engine
3. **demo_etl_with_quality.py**: Illustrates integration with the ETL pipeline

## Configuration Options

### Severity Levels

- **info**: Informational issues that don't affect data quality
- **warning**: Minor issues that might affect data quality
- **error**: Significant issues that affect data quality
- **critical**: Severe issues that should prevent processing

### Monitor-Specific Configuration

#### Completeness Monitor
- `threshold`: Minimum acceptable completeness ratio (0-1)
- `columns`: Specific columns to check (default: all)

#### Outlier Monitor
- `method`: Detection method ('zscore', 'iqr', 'percentile')
- `threshold`: Threshold for outlier detection
- `columns`: Numerical columns to check (default: all numerical)
- `max_outlier_ratio`: Maximum acceptable outlier ratio

#### Consistency Monitor
- `duplicate_columns`: Columns to check for duplicates
- `unique_columns`: Columns that should contain unique values
- `constraints`: Business rules to validate

## Best Practices

1. **Start with Critical Checks**: Focus on completeness and consistency checks that are critical for your application
2. **Tune Thresholds**: Adjust thresholds based on your data characteristics
3. **Layer Monitors**: Use multiple monitors to catch different types of issues
4. **Save Reports**: Enable report saving for audit and troubleshooting
5. **Handle Alerts Appropriately**: Define clear procedures for different severity levels

## Future Enhancements

Potential enhancements to the data quality monitoring system:

1. **Additional Monitors**: 
   - Format validation (regex patterns, data types)
   - Freshness/timeliness checks
   - Distribution drift detection

2. **Integration Improvements**:
   - Automated data cleansing based on quality issues
   - Quality metrics dashboard
   - Historical quality trend analysis

3. **Performance Optimizations**:
   - Parallel monitor execution
   - Sampling for large datasets
   - Incremental quality checks

# Mercurios.ai Data Quality Module

This module provides data quality monitoring capabilities for the Mercurios.ai Predictive Inventory Management tool. It allows for checking data completeness, detecting outliers, and ensuring data consistency before training prediction models or generating forecasts.

## Components

### Base Monitor

- **BaseDataQualityMonitor**: Abstract base class that defines the interface for all data quality monitors

### Specific Monitors

- **CompletenessMonitor**: Checks for missing values in the data
- **OutlierMonitor**: Detects outliers using various statistical methods (z-score, IQR, percentile)
- **ConsistencyMonitor**: Checks for duplicates, inconsistent values, and constraint violations

### Data Quality Manager

- **DataQualityManager**: Coordinates multiple monitors and aggregates their results

## Usage

See the `demo_data_quality.py` script for examples of how to use the data quality monitors.

### Basic Usage

```python
from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor

# Initialize a completeness monitor
completeness_config = {
    'threshold': 0.95,
    'columns': ['product_id', 'quantity', 'unit_price'],
    'severity': 'warning'
}
completeness_monitor = CompletenessMonitor(config=completeness_config)

# Run the monitor
results = completeness_monitor.run(data)

# Get alerts
alerts = completeness_monitor.get_alerts()
```

### Using the Data Quality Manager

```python
from data_quality.manager import DataQualityManager

# Initialize data quality manager
config = {
    'output_dir': 'data_quality_reports',
    'monitors': {
        'completeness': {
            'threshold': 0.95,
            'severity': 'warning'
        },
        'outlier': {
            'method': 'zscore',
            'threshold': 3.0,
            'max_outlier_ratio': 0.05,
            'severity': 'warning'
        },
        'consistency': {
            'duplicate_columns': ['product_id', 'order_date', 'quantity'],
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

# Run all monitors
results = manager.run_monitors(data)

# Get all alerts
alerts = manager.get_alerts()

# Save results to a file
filepath = manager.save_results()
```

### Integration with Prediction Engine

The data quality monitoring is integrated with the prediction engine to check data quality before training models or generating predictions:

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

## Dependencies

- pandas
- numpy
- scipy
- matplotlib (for visualization)

These dependencies are included in the main `prediction_requirements.txt` file.

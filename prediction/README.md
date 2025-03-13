# Mercurios.ai Prediction Module

This module contains the prediction models for the Mercurios.ai Predictive Inventory Management tool. It provides time-series forecasting, lead time prediction, reorder point calculation, and safety stock optimization capabilities.

## Components

### Time-Series Forecasting Models

- **ARIMA**: AutoRegressive Integrated Moving Average model for demand forecasting
- **Exponential Smoothing**: Holt-Winters Exponential Smoothing model for demand forecasting with trend and seasonality

### Lead Time Prediction

- **LeadTimePredictionModel**: Machine learning model to predict supplier delivery times based on historical data

### Inventory Optimization

- **ReorderPointCalculator**: Calculates optimal reorder points based on demand forecasts, lead time predictions, and desired service level
- **SafetyStockOptimizer**: Optimizes safety stock levels based on demand variability, lead time uncertainty, service level targets, and holding costs

### Prediction Engine

- **PredictionEngine**: Unified interface for all prediction models, providing methods for training, prediction, and generating inventory recommendations

## Usage

See the `demo_prediction.py` script for examples of how to use the prediction models.

### Basic Usage

```python
from prediction.models.time_series import ARIMAModel
from prediction.models.lead_time import LeadTimePredictionModel
from prediction.models.inventory_optimization import ReorderPointCalculator, SafetyStockOptimizer

# Initialize a time-series forecasting model
arima_config = {
    'p': 2,
    'd': 1,
    'q': 2,
    'seasonal': True,
    'P': 1,
    'D': 0,
    'Q': 1,
    's': 7,  # Weekly seasonality
    'auto': True  # Use auto-ARIMA
}
arima_model = ARIMAModel(arima_config)

# Train the model
arima_model.train(demand_data)

# Generate forecast
forecast = arima_model.predict(demand_data, horizon=30)
```

### Using the Prediction Engine

```python
from prediction.engine import PredictionEngine

# Initialize prediction engine
engine = PredictionEngine()

# Define model configurations
model_configs = {
    'demand_forecast': {
        'type': 'arima',
        'p': 2,
        'd': 1,
        'q': 2,
        'seasonal': True,
        'auto': True
    },
    'lead_time': {
        'type': 'lead_time',
        'model_type': 'rf'
    },
    'reorder_point': {
        'type': 'reorder_point',
        'service_level': 0.95
    },
    'safety_stock': {
        'type': 'safety_stock',
        'service_level': 0.95
    }
}

# Initialize models
engine.initialize_models(model_configs)

# Train models
engine.train_model('demand_forecast', demand_data)
engine.train_model('lead_time', lead_time_data)
engine.train_model('reorder_point', product_data)
engine.train_model('safety_stock', product_data)

# Generate inventory recommendations
recommendations = engine.generate_inventory_recommendations(product_ids)
```

## Dependencies

- numpy
- pandas
- matplotlib
- scikit-learn
- statsmodels
- pmdarima
- scipy
- sqlalchemy
- python-dotenv

Install dependencies with:

```bash
pip install -r prediction_requirements.txt
```

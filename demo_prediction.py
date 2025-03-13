#!/usr/bin/env python
"""
Demo script for the prediction models in the Mercurios.ai Predictive Inventory Management tool.

This script demonstrates how to use the time-series forecasting, lead time prediction,
reorder point calculation, and safety stock optimization models.
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prediction.models.time_series import ARIMAModel, ExponentialSmoothingModel
from prediction.models.lead_time import LeadTimePredictionModel
from prediction.models.inventory_optimization import ReorderPointCalculator, SafetyStockOptimizer
from prediction.utils.evaluation import plot_forecast_vs_actual, calculate_forecast_metrics
from prediction.engine import PredictionEngine


def generate_sample_data():
    """
    Generate sample data for demonstration purposes.
    
    Returns:
        tuple: (demand_data, lead_time_data, product_data)
    """
    # Generate dates for the past year
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    # Generate sample demand data with trend and seasonality
    np.random.seed(42)
    
    # Base demand with upward trend
    base_demand = np.linspace(50, 100, 365)
    
    # Add weekly seasonality
    weekly_pattern = 15 * np.sin(np.arange(365) * (2 * np.pi / 7))
    
    # Add monthly seasonality
    monthly_pattern = 30 * np.sin(np.arange(365) * (2 * np.pi / 30))
    
    # Add noise
    noise = np.random.normal(0, 10, 365)
    
    # Combine components
    demand = base_demand + weekly_pattern + monthly_pattern + noise
    
    # Ensure non-negative demand
    demand = np.maximum(demand, 0)
    
    # Create demand DataFrame
    demand_data = pd.DataFrame({
        'date': dates,
        'value': demand
    })
    
    # Generate sample lead time data
    product_ids = [1001, 1002, 1003, 1004, 1005]
    supplier_ids = [101, 102, 103]
    
    lead_time_rows = []
    
    for _ in range(500):
        product_id = np.random.choice(product_ids)
        supplier_id = np.random.choice(supplier_ids)
        order_date = start_date + timedelta(days=np.random.randint(0, 330))
        
        # Lead time depends on supplier and product
        base_lead_time = 5 if supplier_id == 101 else 8 if supplier_id == 102 else 12
        product_factor = 1.0 if product_id < 1003 else 1.2 if product_id < 1005 else 1.5
        
        # Add variability
        lead_time = int(np.random.normal(base_lead_time * product_factor, 2))
        lead_time = max(1, lead_time)  # Ensure positive lead time
        
        delivery_date = order_date + timedelta(days=lead_time)
        
        # Order quantity and value
        quantity = np.random.randint(10, 100)
        unit_price = np.random.uniform(10, 50)
        order_value = quantity * unit_price
        
        lead_time_rows.append({
            'supplier_id': supplier_id,
            'product_id': product_id,
            'order_date': order_date,
            'delivery_date': delivery_date,
            'quantity': quantity,
            'order_value': order_value,
            'lead_time_days': lead_time
        })
    
    lead_time_data = pd.DataFrame(lead_time_rows)
    
    # Generate product data for reorder point and safety stock calculation
    product_rows = []
    
    for product_id in product_ids:
        # Get demand for this product (using the same demand for all products in this demo)
        product_demand = demand.tolist()
        
        # Get lead times for this product
        product_lead_times = lead_time_data[lead_time_data['product_id'] == product_id]['lead_time_days'].tolist()
        if not product_lead_times:
            product_lead_times = [7, 8, 9, 10]  # Default if no lead times found
        
        # Calculate unit cost
        product_orders = lead_time_data[lead_time_data['product_id'] == product_id]
        if not product_orders.empty:
            total_quantity = product_orders['quantity'].sum()
            total_value = product_orders['order_value'].sum()
            unit_cost = total_value / total_quantity if total_quantity > 0 else 20
        else:
            unit_cost = 20  # Default unit cost
        
        product_rows.append({
            'product_id': product_id,
            'demand': product_demand,
            'lead_time': product_lead_times,
            'unit_cost': unit_cost
        })
    
    product_data = pd.DataFrame(product_rows)
    
    return demand_data, lead_time_data, product_data


def demo_time_series_forecasting():
    """
    Demonstrate time-series forecasting models.
    """
    logger.info("Demonstrating time-series forecasting models")
    
    # Generate sample data
    demand_data, _, _ = generate_sample_data()
    
    # Split data into training and test sets
    train_size = int(len(demand_data) * 0.8)
    train_data = demand_data.iloc[:train_size]
    test_data = demand_data.iloc[train_size:]
    
    # Initialize and train ARIMA model
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
    logger.info("Training ARIMA model")
    arima_model.train(train_data)
    
    # Generate forecast
    forecast_horizon = len(test_data)
    arima_forecast = arima_model.predict(train_data, forecast_horizon)
    
    # Plot forecast vs actual
    plt.figure(figsize=(12, 6))
    plt.plot(test_data['date'], test_data['value'], label='Actual')
    plt.plot(arima_forecast['date'], arima_forecast['value'], label='ARIMA Forecast')
    plt.title('ARIMA Forecast vs Actual')
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.legend()
    plt.grid(True)
    plt.savefig('arima_forecast.png')
    
    # Calculate metrics
    metrics = calculate_forecast_metrics(test_data['value'], arima_forecast['value'])
    logger.info(f"ARIMA forecast metrics: {metrics}")
    
    # Initialize and train Exponential Smoothing model
    exp_config = {
        'trend': 'add',
        'seasonal': 'add',
        'seasonal_periods': 7,  # Weekly seasonality
        'damped': True
    }
    
    exp_model = ExponentialSmoothingModel(exp_config)
    logger.info("Training Exponential Smoothing model")
    exp_model.train(train_data)
    
    # Generate forecast
    exp_forecast = exp_model.predict(train_data, forecast_horizon)
    
    # Plot forecast vs actual
    plt.figure(figsize=(12, 6))
    plt.plot(test_data['date'], test_data['value'], label='Actual')
    plt.plot(exp_forecast['date'], exp_forecast['value'], label='Exponential Smoothing Forecast')
    plt.title('Exponential Smoothing Forecast vs Actual')
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.legend()
    plt.grid(True)
    plt.savefig('exp_smoothing_forecast.png')
    
    # Calculate metrics
    metrics = calculate_forecast_metrics(test_data['value'], exp_forecast['value'])
    logger.info(f"Exponential Smoothing forecast metrics: {metrics}")
    
    # Compare both models
    plt.figure(figsize=(12, 6))
    plt.plot(test_data['date'], test_data['value'], label='Actual')
    plt.plot(arima_forecast['date'], arima_forecast['value'], label='ARIMA Forecast')
    plt.plot(exp_forecast['date'], exp_forecast['value'], label='Exponential Smoothing Forecast')
    plt.title('Forecast Comparison')
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.legend()
    plt.grid(True)
    plt.savefig('forecast_comparison.png')
    
    logger.info("Time-series forecasting demonstration completed")


def demo_lead_time_prediction():
    """
    Demonstrate lead time prediction model.
    """
    logger.info("Demonstrating lead time prediction model")
    
    # Generate sample data
    _, lead_time_data, _ = generate_sample_data()
    
    # Split data into training and test sets
    train_size = int(len(lead_time_data) * 0.8)
    train_data = lead_time_data.iloc[:train_size]
    test_data = lead_time_data.iloc[train_size:]
    
    # Initialize and train lead time prediction model
    lead_time_config = {
        'model_type': 'rf',  # Random Forest
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    }
    
    lead_time_model = LeadTimePredictionModel(lead_time_config)
    logger.info("Training lead time prediction model")
    lead_time_model.train(train_data)
    
    # Generate predictions
    predictions = lead_time_model.predict(test_data)
    
    # Evaluate predictions
    actual_lead_times = test_data['lead_time_days']
    predicted_lead_times = predictions['predicted_lead_time_days']
    
    # Calculate metrics
    mae = np.mean(np.abs(actual_lead_times - predicted_lead_times))
    rmse = np.sqrt(np.mean(np.square(actual_lead_times - predicted_lead_times)))
    
    logger.info(f"Lead time prediction metrics: MAE={mae:.2f}, RMSE={rmse:.2f}")
    
    # Plot actual vs predicted lead times
    plt.figure(figsize=(10, 6))
    plt.scatter(actual_lead_times, predicted_lead_times, alpha=0.5)
    plt.plot([min(actual_lead_times), max(actual_lead_times)], 
             [min(actual_lead_times), max(actual_lead_times)], 
             'r--')
    plt.title('Actual vs Predicted Lead Times')
    plt.xlabel('Actual Lead Time (days)')
    plt.ylabel('Predicted Lead Time (days)')
    plt.grid(True)
    plt.savefig('lead_time_prediction.png')
    
    # Plot lead time distribution by supplier
    plt.figure(figsize=(12, 6))
    for supplier_id in predictions['supplier_id'].unique():
        supplier_data = predictions[predictions['supplier_id'] == supplier_id]
        plt.hist(supplier_data['predicted_lead_time_days'], 
                 alpha=0.5, 
                 label=f'Supplier {supplier_id}')
    
    plt.title('Predicted Lead Time Distribution by Supplier')
    plt.xlabel('Lead Time (days)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    plt.savefig('lead_time_by_supplier.png')
    
    logger.info("Lead time prediction demonstration completed")


def demo_inventory_optimization():
    """
    Demonstrate reorder point calculation and safety stock optimization.
    """
    logger.info("Demonstrating inventory optimization models")
    
    # Generate sample data
    _, _, product_data = generate_sample_data()
    
    # Initialize reorder point calculator
    reorder_config = {
        'service_level': 0.95,
        'lead_time_factor': 1.1,
        'safety_factor': 1.2
    }
    
    reorder_calculator = ReorderPointCalculator(reorder_config)
    logger.info("Training reorder point calculator")
    reorder_calculator.train(product_data)
    
    # Calculate reorder points
    reorder_points = reorder_calculator.predict(product_data)
    
    logger.info("Reorder point calculation results:")
    logger.info(reorder_points[['product_id', 'avg_demand', 'avg_lead_time', 'safety_stock', 'reorder_point']])
    
    # Initialize safety stock optimizer
    safety_config = {
        'service_level': 0.95,
        'holding_cost_rate': 0.25,
        'stockout_cost_factor': 1.5,
        'review_period': 7
    }
    
    safety_optimizer = SafetyStockOptimizer(safety_config)
    logger.info("Training safety stock optimizer")
    safety_optimizer.train(product_data)
    
    # Optimize safety stock levels
    safety_stock = safety_optimizer.predict(product_data)
    
    logger.info("Safety stock optimization results:")
    logger.info(safety_stock[['product_id', 'service_level', 'service_level_safety_stock', 'cost_optimal_safety_stock', 'total_annual_cost']])
    
    # Plot safety stock levels for different service levels
    service_levels = [0.8, 0.85, 0.9, 0.95, 0.98, 0.99]
    safety_results = []
    
    for sl in service_levels:
        result = safety_optimizer.predict(product_data.iloc[:1], service_level=sl)
        safety_results.append({
            'service_level': sl,
            'safety_stock': result['service_level_safety_stock'].values[0],
            'annual_cost': result['total_annual_cost'].values[0]
        })
    
    safety_df = pd.DataFrame(safety_results)
    
    # Plot safety stock vs service level
    plt.figure(figsize=(10, 6))
    plt.plot(safety_df['service_level'], safety_df['safety_stock'], marker='o')
    plt.title('Safety Stock vs Service Level')
    plt.xlabel('Service Level')
    plt.ylabel('Safety Stock Units')
    plt.grid(True)
    plt.savefig('safety_stock_vs_service_level.png')
    
    # Plot total cost vs service level
    plt.figure(figsize=(10, 6))
    plt.plot(safety_df['service_level'], safety_df['annual_cost'], marker='o')
    plt.title('Annual Cost vs Service Level')
    plt.xlabel('Service Level')
    plt.ylabel('Annual Cost')
    plt.grid(True)
    plt.savefig('cost_vs_service_level.png')
    
    logger.info("Inventory optimization demonstration completed")


def demo_prediction_engine():
    """
    Demonstrate the prediction engine.
    """
    logger.info("Demonstrating prediction engine")
    
    # Generate sample data
    demand_data, lead_time_data, product_data = generate_sample_data()
    
    # Initialize prediction engine
    engine_config = {
        'model_dir': 'models',
        'use_database': False  # Don't use database for demo
    }
    
    engine = PredictionEngine(engine_config)
    
    # Define model configurations
    model_configs = {
        'demand_forecast': {
            'type': 'arima',
            'p': 2,
            'd': 1,
            'q': 2,
            'seasonal': True,
            'P': 1,
            'D': 0,
            'Q': 1,
            's': 7,
            'auto': True
        },
        'lead_time': {
            'type': 'lead_time',
            'model_type': 'rf',
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42
        },
        'reorder_point': {
            'type': 'reorder_point',
            'service_level': 0.95,
            'lead_time_factor': 1.1,
            'safety_factor': 1.2
        },
        'safety_stock': {
            'type': 'safety_stock',
            'service_level': 0.95,
            'holding_cost_rate': 0.25,
            'stockout_cost_factor': 1.5,
            'review_period': 7
        }
    }
    
    # Initialize models
    engine.initialize_models(model_configs)
    
    # Train models
    logger.info("Training demand forecast model")
    engine.train_model('demand_forecast', demand_data)
    
    logger.info("Training lead time prediction model")
    engine.train_model('lead_time', lead_time_data)
    
    logger.info("Training reorder point calculator")
    engine.train_model('reorder_point', product_data)
    
    logger.info("Training safety stock optimizer")
    engine.train_model('safety_stock', product_data)
    
    # Generate predictions
    forecast_horizon = 30
    logger.info(f"Generating demand forecast for {forecast_horizon} days")
    forecast = engine.predict('demand_forecast', demand_data, horizon=forecast_horizon)
    
    logger.info("Predicting lead times")
    lead_time_predictions = engine.predict('lead_time', lead_time_data)
    
    logger.info("Calculating reorder points")
    reorder_points = engine.predict('reorder_point', product_data)
    
    logger.info("Optimizing safety stock levels")
    safety_stock = engine.predict('safety_stock', product_data)
    
    # Close engine
    engine.close()
    
    logger.info("Prediction engine demonstration completed")


if __name__ == "__main__":
    logger.info("Starting prediction models demonstration")
    
    # Create output directory for plots
    os.makedirs('output', exist_ok=True)
    
    # Run demonstrations
    demo_time_series_forecasting()
    demo_lead_time_prediction()
    demo_inventory_optimization()
    demo_prediction_engine()
    
    logger.info("Demonstration completed successfully")

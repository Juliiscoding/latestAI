#!/usr/bin/env python
"""
Demo script for the prediction models with data quality monitoring in the Mercurios.ai Predictive Inventory Management tool.

This script demonstrates how to use the prediction engine with integrated data quality monitoring.
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

from prediction.engine import PredictionEngine
from data_quality.manager import DataQualityManager


def generate_sample_data(include_quality_issues=False):
    """
    Generate sample data for demonstration purposes.
    
    Args:
        include_quality_issues (bool): Whether to include data quality issues
        
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
    
    # Add data quality issues if requested
    if include_quality_issues:
        # Add missing values to demand data
        missing_mask = np.random.random(len(demand_data)) < 0.05  # 5% missing values
        demand_data.loc[missing_mask, 'value'] = np.nan
        
        # Add outliers to demand data
        outlier_mask = np.random.random(len(demand_data)) < 0.02  # 2% outliers
        demand_data.loc[outlier_mask, 'value'] = demand_data['value'].max() * np.random.uniform(3, 5, outlier_mask.sum())
        
        # Add missing values to lead time data
        for column in ['quantity', 'lead_time_days']:
            missing_mask = np.random.random(len(lead_time_data)) < 0.05  # 5% missing values
            lead_time_data.loc[missing_mask, column] = np.nan
        
        # Add outliers to lead time data
        outlier_mask = np.random.random(len(lead_time_data)) < 0.02  # 2% outliers
        lead_time_data.loc[outlier_mask, 'lead_time_days'] = np.random.randint(30, 60, outlier_mask.sum())
        
        # Add inconsistencies to lead time data
        inconsistent_mask = np.random.random(len(lead_time_data)) < 0.02  # 2% inconsistencies
        lead_time_data.loc[inconsistent_mask, 'delivery_date'] = lead_time_data.loc[inconsistent_mask, 'order_date'] - timedelta(days=1)
    
    return demand_data, lead_time_data, product_data


def demo_prediction_with_quality_monitoring():
    """
    Demonstrate prediction with data quality monitoring.
    """
    logger.info("Demonstrating prediction with data quality monitoring")
    
    # Generate sample data with quality issues
    demand_data, lead_time_data, product_data = generate_sample_data(include_quality_issues=True)
    
    # Create data quality configuration
    data_quality_config = {
        'enabled': True,
        'save_reports': True,
        'output_dir': 'data_quality_reports',
        'monitors': {
            'completeness': {
                'threshold': 0.95,
                'severity': 'critical'  # Make completeness issues critical
            },
            'outlier': {
                'method': 'zscore',
                'threshold': 3.0,
                'max_outlier_ratio': 0.05,
                'severity': 'warning'
            },
            'consistency': {
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
    
    # Initialize prediction engine with data quality monitoring
    engine_config = {
        'model_dir': 'models',
        'use_database': False,  # Don't use database for demo
        'data_quality': data_quality_config
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
        }
    }
    
    # Initialize models
    engine.initialize_models(model_configs)
    
    # Try to train models with data quality issues
    logger.info("\n=== Attempting to train models with data quality issues ===")
    
    try:
        logger.info("Training demand forecast model")
        engine.train_model('demand_forecast', demand_data)
    except Exception as e:
        logger.error(f"Error training demand forecast model: {str(e)}")
    
    try:
        logger.info("Training lead time prediction model")
        engine.train_model('lead_time', lead_time_data)
    except Exception as e:
        logger.error(f"Error training lead time prediction model: {str(e)}")
    
    # Force training despite quality issues
    logger.info("\n=== Forcing model training despite data quality issues ===")
    
    logger.info("Training demand forecast model with force_train=True")
    engine.train_model('demand_forecast', demand_data, force_train=True)
    
    logger.info("Training lead time prediction model with force_train=True")
    engine.train_model('lead_time', lead_time_data, force_train=True)
    
    # Try prediction with data quality issues
    logger.info("\n=== Attempting prediction with data quality issues ===")
    
    try:
        logger.info("Generating demand forecast")
        forecast = engine.predict('demand_forecast', demand_data, horizon=30)
        logger.info(f"Forecast shape: {forecast.shape if hasattr(forecast, 'shape') else 'N/A'}")
    except Exception as e:
        logger.error(f"Error generating demand forecast: {str(e)}")
    
    try:
        logger.info("Predicting lead times")
        lead_time_predictions = engine.predict('lead_time', lead_time_data)
        logger.info(f"Lead time predictions shape: {lead_time_predictions.shape if hasattr(lead_time_predictions, 'shape') else 'N/A'}")
    except Exception as e:
        logger.error(f"Error predicting lead times: {str(e)}")
    
    # Force prediction despite quality issues
    logger.info("\n=== Forcing prediction despite data quality issues ===")
    
    logger.info("Generating demand forecast with force_predict=True")
    forecast = engine.predict('demand_forecast', demand_data, horizon=30, force_predict=True)
    
    if not forecast.empty:
        logger.info(f"Forecast shape: {forecast.shape}")
        
        # Plot forecast
        plt.figure(figsize=(12, 6))
        plt.plot(forecast['date'], forecast['value'], label='Forecast')
        plt.title('Demand Forecast (with data quality issues)')
        plt.xlabel('Date')
        plt.ylabel('Demand')
        plt.legend()
        plt.grid(True)
        plt.savefig('forecast_with_quality_issues.png')
    
    logger.info("Predicting lead times with force_predict=True")
    lead_time_predictions = engine.predict('lead_time', lead_time_data, force_predict=True)
    
    if not lead_time_predictions.empty:
        logger.info(f"Lead time predictions shape: {lead_time_predictions.shape}")
        
        # Plot lead time predictions
        plt.figure(figsize=(10, 6))
        plt.hist(lead_time_predictions['predicted_lead_time_days'], bins=20)
        plt.title('Lead Time Predictions (with data quality issues)')
        plt.xlabel('Predicted Lead Time (days)')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.savefig('lead_time_predictions_with_quality_issues.png')
    
    # Now try with clean data
    logger.info("\n=== Using clean data ===")
    
    # Generate clean sample data
    clean_demand_data, clean_lead_time_data, clean_product_data = generate_sample_data(include_quality_issues=False)
    
    logger.info("Training demand forecast model with clean data")
    engine.train_model('demand_forecast', clean_demand_data)
    
    logger.info("Training lead time prediction model with clean data")
    engine.train_model('lead_time', clean_lead_time_data)
    
    logger.info("Generating demand forecast with clean data")
    clean_forecast = engine.predict('demand_forecast', clean_demand_data, horizon=30)
    
    if not clean_forecast.empty:
        logger.info(f"Clean forecast shape: {clean_forecast.shape}")
        
        # Plot forecast
        plt.figure(figsize=(12, 6))
        plt.plot(clean_forecast['date'], clean_forecast['value'], label='Forecast')
        plt.title('Demand Forecast (with clean data)')
        plt.xlabel('Date')
        plt.ylabel('Demand')
        plt.legend()
        plt.grid(True)
        plt.savefig('forecast_with_clean_data.png')
    
    logger.info("Predicting lead times with clean data")
    clean_lead_time_predictions = engine.predict('lead_time', clean_lead_time_data)
    
    if not clean_lead_time_predictions.empty:
        logger.info(f"Clean lead time predictions shape: {clean_lead_time_predictions.shape}")
        
        # Plot lead time predictions
        plt.figure(figsize=(10, 6))
        plt.hist(clean_lead_time_predictions['predicted_lead_time_days'], bins=20)
        plt.title('Lead Time Predictions (with clean data)')
        plt.xlabel('Predicted Lead Time (days)')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.savefig('lead_time_predictions_with_clean_data.png')
    
    # Close engine
    engine.close()
    
    logger.info("Demonstration completed successfully")


if __name__ == "__main__":
    logger.info("Starting prediction with data quality monitoring demonstration")
    
    # Create output directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('data_quality_reports', exist_ok=True)
    
    # Run demonstration
    demo_prediction_with_quality_monitoring()

"""
Evaluation utilities for prediction models.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Union, Tuple
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from etl.utils.logger import logger


def calculate_forecast_metrics(actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
    """
    Calculate forecast accuracy metrics.
    
    Args:
        actual (pd.Series): Actual values
        predicted (pd.Series): Predicted values
        
    Returns:
        Dict[str, float]: Dictionary of evaluation metrics
    """
    if len(actual) != len(predicted):
        logger.warning(f"Length mismatch: actual={len(actual)}, predicted={len(predicted)}")
        min_len = min(len(actual), len(predicted))
        actual = actual.iloc[:min_len]
        predicted = predicted.iloc[:min_len]
    
    # Calculate errors
    errors = actual - predicted
    abs_errors = np.abs(errors)
    
    # Handle division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        percentage_errors = abs_errors / actual
        percentage_errors = np.where(np.isfinite(percentage_errors), percentage_errors, 0)
    
    # Calculate metrics
    metrics = {
        "mae": mean_absolute_error(actual, predicted),
        "mse": mean_squared_error(actual, predicted),
        "rmse": np.sqrt(mean_squared_error(actual, predicted)),
        "mape": np.mean(percentage_errors) * 100,
        "r2": r2_score(actual, predicted)
    }
    
    return metrics


def plot_forecast_vs_actual(actual: pd.DataFrame, forecast: pd.DataFrame, 
                           date_col: str = 'date', value_col: str = 'value',
                           title: str = 'Forecast vs Actual', figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    Plot forecast values against actual values.
    
    Args:
        actual (pd.DataFrame): DataFrame with actual values
        forecast (pd.DataFrame): DataFrame with forecast values
        date_col (str): Name of the date column
        value_col (str): Name of the value column
        title (str): Plot title
        figsize (Tuple[int, int]): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot actual values
    ax.plot(actual[date_col], actual[value_col], label='Actual', marker='o')
    
    # Plot forecast values
    ax.plot(forecast[date_col], forecast[value_col], label='Forecast', marker='x')
    
    # Plot confidence intervals if available
    if 'lower_bound' in forecast.columns and 'upper_bound' in forecast.columns:
        ax.fill_between(forecast[date_col], 
                       forecast['lower_bound'], 
                       forecast['upper_bound'],
                       alpha=0.2, label='95% Confidence Interval')
    
    # Add labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    
    # Format date axis
    fig.autofmt_xdate()
    
    return fig


def plot_forecast_error_distribution(actual: pd.Series, predicted: pd.Series, 
                                    title: str = 'Forecast Error Distribution', 
                                    figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot the distribution of forecast errors.
    
    Args:
        actual (pd.Series): Actual values
        predicted (pd.Series): Predicted values
        title (str): Plot title
        figsize (Tuple[int, int]): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure
    """
    errors = actual - predicted
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot error histogram
    ax.hist(errors, bins=20, alpha=0.7, color='skyblue')
    
    # Add a vertical line at zero
    ax.axvline(x=0, color='red', linestyle='--', alpha=0.7)
    
    # Add labels and title
    ax.set_xlabel('Forecast Error')
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    # Add error statistics as text
    stats_text = (
        f"Mean Error: {np.mean(errors):.2f}\n"
        f"Std Dev: {np.std(errors):.2f}\n"
        f"Min Error: {np.min(errors):.2f}\n"
        f"Max Error: {np.max(errors):.2f}"
    )
    ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, 
           verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
    return fig


def plot_safety_stock_vs_service_level(optimizer, product_data: pd.DataFrame, 
                                      service_levels: List[float] = None,
                                      figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot safety stock levels against service levels.
    
    Args:
        optimizer: Safety stock optimizer model
        product_data (pd.DataFrame): Product data
        service_levels (List[float]): List of service levels to evaluate
        figsize (Tuple[int, int]): Figure size
        
    Returns:
        plt.Figure: Matplotlib figure
    """
    if service_levels is None:
        service_levels = [0.8, 0.85, 0.9, 0.95, 0.98, 0.99]
    
    results = []
    
    for sl in service_levels:
        result = optimizer.predict(product_data, service_level=sl)
        for _, row in result.iterrows():
            results.append({
                'product_id': row['product_id'],
                'service_level': sl,
                'safety_stock': row['service_level_safety_stock'],
                'annual_cost': row['total_annual_cost']
            })
    
    results_df = pd.DataFrame(results)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Group by product_id and plot safety stock vs service level
    for product_id, group in results_df.groupby('product_id'):
        ax1.plot(group['service_level'], group['safety_stock'], marker='o', label=f'Product {product_id}')
    
    ax1.set_xlabel('Service Level')
    ax1.set_ylabel('Safety Stock')
    ax1.set_title('Safety Stock vs Service Level')
    ax1.grid(True)
    
    # Group by product_id and plot total cost vs service level
    for product_id, group in results_df.groupby('product_id'):
        ax2.plot(group['service_level'], group['annual_cost'], marker='o', label=f'Product {product_id}')
    
    ax2.set_xlabel('Service Level')
    ax2.set_ylabel('Annual Cost')
    ax2.set_title('Annual Cost vs Service Level')
    ax2.grid(True)
    
    # Add legend if there are multiple products
    if len(results_df['product_id'].unique()) <= 5:
        ax1.legend()
        ax2.legend()
    
    fig.tight_layout()
    
    return fig

#!/usr/bin/env python
"""
Demo script for the data quality monitoring in the Mercurios.ai Predictive Inventory Management tool.

This script demonstrates how to use the data quality monitors to check data quality
before running prediction models.
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

from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor
from data_quality.manager import DataQualityManager


def generate_sample_data(include_quality_issues=False):
    """
    Generate sample data for demonstration purposes.
    
    Args:
        include_quality_issues (bool): Whether to include data quality issues
        
    Returns:
        pd.DataFrame: Sample data
    """
    # Generate dates for the past year
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    # Generate sample data
    np.random.seed(42)
    
    # Create product data
    product_ids = [1001, 1002, 1003, 1004, 1005]
    supplier_ids = [101, 102, 103]
    
    # Create rows
    rows = []
    
    for i in range(500):
        product_id = np.random.choice(product_ids)
        supplier_id = np.random.choice(supplier_ids)
        order_date = start_date + timedelta(days=np.random.randint(0, 330))
        
        # Base values
        quantity = np.random.randint(10, 100)
        unit_price = np.random.uniform(10, 50)
        order_value = quantity * unit_price
        
        # Lead time depends on supplier and product
        base_lead_time = 5 if supplier_id == 101 else 8 if supplier_id == 102 else 12
        product_factor = 1.0 if product_id < 1003 else 1.2 if product_id < 1005 else 1.5
        
        # Add variability
        lead_time = int(np.random.normal(base_lead_time * product_factor, 2))
        lead_time = max(1, lead_time)  # Ensure positive lead time
        
        delivery_date = order_date + timedelta(days=lead_time)
        
        row = {
            'order_id': i + 1000,
            'product_id': product_id,
            'supplier_id': supplier_id,
            'order_date': order_date,
            'delivery_date': delivery_date,
            'quantity': quantity,
            'unit_price': unit_price,
            'order_value': order_value,
            'lead_time_days': lead_time,
            'customer_id': np.random.randint(1, 100),
            'region': np.random.choice(['North', 'South', 'East', 'West']),
            'priority': np.random.choice(['Low', 'Medium', 'High']),
            'status': np.random.choice(['Pending', 'Shipped', 'Delivered', 'Cancelled']),
            'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer']),
            'shipping_cost': np.random.uniform(5, 20)
        }
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Add data quality issues if requested
    if include_quality_issues:
        # Add missing values
        for column in ['quantity', 'unit_price', 'shipping_cost', 'region', 'priority']:
            mask = np.random.random(len(df)) < 0.05  # 5% missing values
            df.loc[mask, column] = np.nan
        
        # Add outliers
        for column in ['quantity', 'unit_price', 'order_value', 'lead_time_days']:
            mask = np.random.random(len(df)) < 0.02  # 2% outliers
            if column == 'lead_time_days':
                df.loc[mask, column] = np.random.randint(30, 60)  # Very long lead times
            else:
                df.loc[mask, column] = df[column].max() * np.random.uniform(3, 5, mask.sum())
        
        # Add duplicates
        duplicate_count = int(len(df) * 0.03)  # 3% duplicates
        duplicate_indices = np.random.choice(df.index, duplicate_count, replace=False)
        for idx in duplicate_indices:
            duplicate_row = df.loc[idx].copy()
            duplicate_row['order_id'] = df['order_id'].max() + 1
            df = pd.concat([df, pd.DataFrame([duplicate_row])], ignore_index=True)
        
        # Add inconsistencies
        mask = np.random.random(len(df)) < 0.02  # 2% inconsistencies
        df.loc[mask, 'order_value'] = df.loc[mask, 'quantity'] * np.random.uniform(5, 100)
        
        # Add constraint violations
        mask = np.random.random(len(df)) < 0.02  # 2% violations
        df.loc[mask, 'delivery_date'] = df.loc[mask, 'order_date'] - timedelta(days=1)  # Delivery before order
    
    return df


def demo_completeness_monitor(data):
    """
    Demonstrate the completeness monitor.
    
    Args:
        data (pd.DataFrame): Data to monitor
    """
    logger.info("Demonstrating completeness monitor")
    
    # Initialize completeness monitor
    config = {
        'threshold': 0.95,
        'columns': ['product_id', 'supplier_id', 'quantity', 'unit_price', 'order_value', 'region'],
        'severity': 'warning'
    }
    
    monitor = CompletenessMonitor(config=config)
    
    # Run monitor
    results = monitor.run(data)
    
    # Print results
    logger.info(f"Completeness monitor results:")
    for column, metrics in results['column_completeness'].items():
        logger.info(f"  {column}: {metrics['completeness_ratio']:.2%} complete")
    
    logger.info(f"Overall completeness: {results['overall_completeness']:.2%}")
    
    # Print alerts
    alerts = monitor.get_alerts()
    if alerts:
        logger.warning(f"Found {len(alerts)} completeness issues:")
        for alert in alerts:
            logger.warning(f"  {alert['message']}")
    else:
        logger.info("No completeness issues found")


def demo_outlier_monitor(data):
    """
    Demonstrate the outlier monitor.
    
    Args:
        data (pd.DataFrame): Data to monitor
    """
    logger.info("Demonstrating outlier monitor")
    
    # Initialize outlier monitor
    config = {
        'method': 'zscore',
        'threshold': 3.0,
        'columns': ['quantity', 'unit_price', 'order_value', 'lead_time_days'],
        'max_outlier_ratio': 0.05,
        'severity': 'warning'
    }
    
    monitor = OutlierMonitor(config=config)
    
    # Run monitor
    results = monitor.run(data)
    
    # Print results
    logger.info(f"Outlier monitor results:")
    for column, metrics in results['column_outliers'].items():
        logger.info(f"  {column}: {metrics['outlier_ratio']:.2%} outliers ({metrics['outlier_count']} / {metrics['total_count']})")
    
    logger.info(f"Overall outlier ratio: {results['overall_outlier_ratio']:.2%}")
    
    # Print alerts
    alerts = monitor.get_alerts()
    if alerts:
        logger.warning(f"Found {len(alerts)} outlier issues:")
        for alert in alerts:
            logger.warning(f"  {alert['message']}")
    else:
        logger.info("No outlier issues found")
    
    # Plot outliers for one column
    if 'lead_time_days' in results['column_outliers']:
        column = 'lead_time_days'
        outlier_indices = results['column_outliers'][column]['outlier_indices']
        
        plt.figure(figsize=(10, 6))
        plt.hist(data[column], bins=30, alpha=0.5, label='All data')
        
        if outlier_indices:
            plt.hist(data.loc[outlier_indices, column], bins=10, alpha=0.7, color='red', label='Outliers')
        
        plt.title(f'Distribution of {column} with Outliers')
        plt.xlabel(column)
        plt.ylabel('Frequency')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'outliers_{column}.png')
        logger.info(f"Saved outlier plot to outliers_{column}.png")


def demo_consistency_monitor(data):
    """
    Demonstrate the consistency monitor.
    
    Args:
        data (pd.DataFrame): Data to monitor
    """
    logger.info("Demonstrating consistency monitor")
    
    # Initialize consistency monitor
    config = {
        'duplicate_columns': ['product_id', 'supplier_id', 'order_date', 'quantity'],
        'unique_columns': ['order_id'],
        'related_columns': {
            'product_id': ['supplier_id']
        },
        'constraints': [
            {
                'name': 'delivery_after_order',
                'type': 'comparison',
                'columns': ['delivery_date', 'order_date'],
                'operator': '>'
            },
            {
                'name': 'order_value_check',
                'type': 'comparison',
                'columns': ['order_value', 'quantity'],
                'operator': '>='
            }
        ],
        'max_duplicate_ratio': 0.01,
        'severity': 'warning'
    }
    
    monitor = ConsistencyMonitor(config=config)
    
    # Run monitor
    results = monitor.run(data)
    
    # Print results
    logger.info(f"Consistency monitor results:")
    
    # Print duplicate results
    if 'duplicate_records' in results['duplicates']:
        metrics = results['duplicates']['duplicate_records']
        logger.info(f"  Duplicate records: {metrics['duplicate_ratio']:.2%} ({metrics['duplicate_count']} / {metrics['total_count']})")
    
    for column in config['unique_columns']:
        if f"{column}_uniqueness" in results['duplicates']:
            metrics = results['duplicates'][f"{column}_uniqueness"]
            logger.info(f"  {column} uniqueness: {1 - metrics['duplicate_ratio']:.2%} unique")
    
    # Print constraint results
    for constraint in config['constraints']:
        constraint_name = constraint['name']
        if f"{constraint_name}_violations" in results['constraints']:
            metrics = results['constraints'][f"{constraint_name}_violations"]
            logger.info(f"  {constraint_name}: {metrics['violation_ratio']:.2%} violations ({metrics['violation_count']} / {metrics['total_count']})")
    
    # Print alerts
    alerts = monitor.get_alerts()
    if alerts:
        logger.warning(f"Found {len(alerts)} consistency issues:")
        for alert in alerts:
            logger.warning(f"  {alert['message']}")
    else:
        logger.info("No consistency issues found")


def demo_data_quality_manager(data):
    """
    Demonstrate the data quality manager.
    
    Args:
        data (pd.DataFrame): Data to monitor
    """
    logger.info("Demonstrating data quality manager")
    
    # Initialize data quality manager
    config = {
        'output_dir': 'data_quality_reports',
        'monitors': {
            'completeness': {
                'threshold': 0.95,
                'columns': ['product_id', 'supplier_id', 'quantity', 'unit_price', 'order_value', 'region'],
                'severity': 'warning'
            },
            'outlier': {
                'method': 'zscore',
                'threshold': 3.0,
                'columns': ['quantity', 'unit_price', 'order_value', 'lead_time_days'],
                'max_outlier_ratio': 0.05,
                'severity': 'warning'
            },
            'consistency': {
                'duplicate_columns': ['product_id', 'supplier_id', 'order_date', 'quantity'],
                'unique_columns': ['order_id'],
                'related_columns': {
                    'product_id': ['supplier_id']
                },
                'constraints': [
                    {
                        'name': 'delivery_after_order',
                        'type': 'comparison',
                        'columns': ['delivery_date', 'order_date'],
                        'operator': '>'
                    },
                    {
                        'name': 'order_value_check',
                        'type': 'comparison',
                        'columns': ['order_value', 'quantity'],
                        'operator': '>='
                    }
                ],
                'max_duplicate_ratio': 0.01,
                'severity': 'warning'
            }
        }
    }
    
    manager = DataQualityManager(config=config)
    
    # Run all monitors
    logger.info("Running all monitors")
    results = manager.run_monitors(data)
    
    # Print summary
    logger.info(f"Data quality summary:")
    logger.info(f"  Total alerts: {len(results['all_alerts'])}")
    
    # Count alerts by severity
    severity_counts = {}
    for alert in results['all_alerts']:
        severity = alert['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    for severity, count in severity_counts.items():
        logger.info(f"  {severity.capitalize()} alerts: {count}")
    
    # Save results
    filepath = manager.save_results()
    logger.info(f"Saved data quality report to {filepath}")


if __name__ == "__main__":
    logger.info("Starting data quality monitoring demonstration")
    
    # Create output directory for plots
    os.makedirs('output', exist_ok=True)
    
    # Generate sample data with quality issues
    logger.info("Generating sample data with quality issues")
    data_with_issues = generate_sample_data(include_quality_issues=True)
    
    # Generate sample data without quality issues
    logger.info("Generating sample data without quality issues")
    clean_data = generate_sample_data(include_quality_issues=False)
    
    # Run demonstrations on data with issues
    logger.info("\n=== Running monitors on data with quality issues ===")
    demo_completeness_monitor(data_with_issues)
    demo_outlier_monitor(data_with_issues)
    demo_consistency_monitor(data_with_issues)
    demo_data_quality_manager(data_with_issues)
    
    # Run demonstrations on clean data
    logger.info("\n=== Running monitors on clean data ===")
    demo_data_quality_manager(clean_data)
    
    logger.info("Demonstration completed successfully")

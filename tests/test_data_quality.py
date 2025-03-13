#!/usr/bin/env python
"""
Test script for validating data quality monitoring with real datasets.

This script loads real or realistic sample data and runs the data quality
monitoring system to validate its effectiveness.
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_quality.manager import DataQualityManager
from data_quality.monitors.completeness_monitor import CompletenessMonitor
from data_quality.monitors.outlier_monitor import OutlierMonitor
from data_quality.monitors.consistency_monitor import ConsistencyMonitor


def load_test_data():
    """
    Load test data from CSV files or generate realistic sample data.
    
    Returns:
        dict: Dictionary of DataFrames for different entity types
    """
    data_dir = Path("test_data")
    
    # Check if test data directory exists
    if data_dir.exists():
        logger.info(f"Loading test data from {data_dir}")
        
        # Load data from CSV files if they exist
        data = {}
        for file_path in data_dir.glob("*.csv"):
            entity_name = file_path.stem
            logger.info(f"Loading {entity_name} data from {file_path}")
            data[entity_name] = pd.read_csv(file_path)
        
        if data:
            return data
    
    # If no test data files exist, generate realistic sample data
    logger.info("Generating realistic sample data")
    
    # Create test data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)
    
    # Generate sample data similar to real ProHandel data
    np.random.seed(42)
    
    # Generate dates for the past year
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    # Generate article data
    article_count = 1000
    article_ids = list(range(1001, 1001 + article_count))
    categories = ["Electronics", "Clothing", "Food", "Home", "Garden", "Automotive", "Sports"]
    suppliers = list(range(101, 121))
    
    articles = pd.DataFrame({
        "article_id": article_ids,
        "article_name": [f"Article {i}" for i in article_ids],
        "category": np.random.choice(categories, size=article_count),
        "unit_price": np.random.uniform(5, 500, size=article_count),
        "supplier_id": np.random.choice(suppliers, size=article_count),
        "created_at": np.random.choice(dates[:180], size=article_count),
        "updated_at": np.random.choice(dates[180:], size=article_count)
    })
    
    # Add some missing values (5%)
    missing_mask = np.random.random(article_count) < 0.05
    articles.loc[missing_mask, "unit_price"] = np.nan
    
    # Generate sales data
    sales_count = 50000
    sales = pd.DataFrame({
        "sale_id": list(range(1, sales_count + 1)),
        "sale_date": np.random.choice(dates, size=sales_count),
        "article_id": np.random.choice(article_ids, size=sales_count),
        "customer_id": np.random.randint(1, 501, size=sales_count),
        "quantity": np.random.randint(1, 20, size=sales_count),
        "unit_price": np.random.uniform(5, 500, size=sales_count),
    })
    
    # Calculate total price
    sales["total_price"] = sales["quantity"] * sales["unit_price"]
    
    # Add some outliers (2%)
    outlier_mask = np.random.random(sales_count) < 0.02
    sales.loc[outlier_mask, "quantity"] = np.random.randint(50, 200, size=outlier_mask.sum())
    sales.loc[outlier_mask, "total_price"] = sales.loc[outlier_mask, "quantity"] * sales.loc[outlier_mask, "unit_price"]
    
    # Add some duplicates (1%)
    duplicate_count = int(sales_count * 0.01)
    duplicate_indices = np.random.choice(sales_count, duplicate_count, replace=False)
    duplicate_rows = sales.iloc[duplicate_indices].copy()
    duplicate_rows["sale_id"] = duplicate_rows["sale_id"] + sales_count  # Change IDs to avoid primary key conflicts
    sales = pd.concat([sales, duplicate_rows])
    
    # Generate inventory data
    inventory = pd.DataFrame({
        "article_id": article_ids,
        "current_stock": np.random.randint(0, 200, size=article_count),
        "min_stock": np.random.randint(5, 30, size=article_count),
        "max_stock": np.random.randint(50, 300, size=article_count),
        "last_restock_date": np.random.choice(dates[:-30], size=article_count),
        "updated_at": np.random.choice(dates[-30:], size=article_count)
    })
    
    # Add some inconsistencies (3%)
    inconsistent_mask = np.random.random(article_count) < 0.03
    inventory.loc[inconsistent_mask, "min_stock"] = inventory.loc[inconsistent_mask, "max_stock"] + 10
    
    # Save generated data to CSV files
    articles.to_csv(data_dir / "articles.csv", index=False)
    sales.to_csv(data_dir / "sales.csv", index=False)
    inventory.to_csv(data_dir / "inventory.csv", index=False)
    
    return {
        "articles": articles,
        "sales": sales,
        "inventory": inventory
    }


def visualize_data_quality_results(results, entity_name):
    """
    Visualize data quality results.
    
    Args:
        results (dict): Data quality results
        entity_name (str): Name of the entity
    """
    # Create output directory
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    
    # Extract metrics
    metrics = results.get("metrics", {})
    
    # Completeness visualization
    if "completeness" in metrics:
        completeness = metrics["completeness"].get("completeness_by_column", {})
        if completeness:
            plt.figure(figsize=(12, 6))
            columns = list(completeness.keys())
            values = list(completeness.values())
            
            # Sort by completeness value
            sorted_indices = np.argsort(values)
            sorted_columns = [columns[i] for i in sorted_indices]
            sorted_values = [values[i] for i in sorted_indices]
            
            plt.barh(sorted_columns, sorted_values)
            plt.xlabel("Completeness Ratio")
            plt.ylabel("Column")
            plt.title(f"Data Completeness by Column - {entity_name}")
            plt.xlim(0, 1)
            plt.tight_layout()
            plt.savefig(output_dir / f"{entity_name}_completeness.png")
    
    # Outlier visualization
    if "outlier" in metrics:
        outlier_ratio = metrics["outlier"].get("outlier_ratio_by_column", {})
        if outlier_ratio:
            plt.figure(figsize=(12, 6))
            columns = list(outlier_ratio.keys())
            values = list(outlier_ratio.values())
            
            # Sort by outlier ratio
            sorted_indices = np.argsort(values)[::-1]  # Descending order
            sorted_columns = [columns[i] for i in sorted_indices]
            sorted_values = [values[i] for i in sorted_indices]
            
            plt.barh(sorted_columns, sorted_values)
            plt.xlabel("Outlier Ratio")
            plt.ylabel("Column")
            plt.title(f"Outlier Ratio by Column - {entity_name}")
            plt.xlim(0, max(sorted_values) * 1.1 if sorted_values else 0.1)
            plt.tight_layout()
            plt.savefig(output_dir / f"{entity_name}_outliers.png")
    
    # Consistency visualization
    if "consistency" in metrics:
        duplicate_ratio = metrics["consistency"].get("duplicate_ratio", 0)
        constraint_violations = metrics["consistency"].get("constraint_violations", {})
        
        # Create a summary of consistency issues
        plt.figure(figsize=(10, 6))
        labels = ["Duplicates"]
        values = [duplicate_ratio]
        
        for constraint, violation in constraint_violations.items():
            labels.append(f"Constraint: {constraint}")
            values.append(violation.get("violation_ratio", 0))
        
        plt.barh(labels, values)
        plt.xlabel("Violation Ratio")
        plt.ylabel("Consistency Check")
        plt.title(f"Consistency Issues - {entity_name}")
        plt.xlim(0, max(values) * 1.1 if values else 0.1)
        plt.tight_layout()
        plt.savefig(output_dir / f"{entity_name}_consistency.png")
    
    # Alert summary
    alerts = results.get("all_alerts", [])
    severity_counts = {
        "critical": len([a for a in alerts if a["severity"] == "critical"]),
        "error": len([a for a in alerts if a["severity"] == "error"]),
        "warning": len([a for a in alerts if a["severity"] == "warning"]),
        "info": len([a for a in alerts if a["severity"] == "info"])
    }
    
    if sum(severity_counts.values()) > 0:
        plt.figure(figsize=(8, 6))
        plt.bar(severity_counts.keys(), severity_counts.values(), color=["darkred", "red", "orange", "blue"])
        plt.xlabel("Severity")
        plt.ylabel("Number of Alerts")
        plt.title(f"Data Quality Alerts by Severity - {entity_name}")
        plt.tight_layout()
        plt.savefig(output_dir / f"{entity_name}_alerts.png")


def test_data_quality_with_real_data():
    """
    Test data quality monitoring with real datasets.
    """
    logger.info("Testing data quality monitoring with real datasets")
    
    # Load test data
    test_data = load_test_data()
    
    # Create output directory for data quality reports
    os.makedirs("test_results", exist_ok=True)
    
    # Initialize data quality manager with comprehensive configuration
    data_quality_config = {
        "output_dir": "test_results",
        "monitors": {
            "completeness": {
                "threshold": 0.95,
                "severity": "critical"
            },
            "outlier": {
                "method": "zscore",
                "threshold": 3.0,
                "max_outlier_ratio": 0.05,
                "columns": None,  # Check all numerical columns
                "severity": "warning"
            },
            "consistency": {
                "duplicate_columns": None,  # Check all columns for duplicates
                "unique_columns": ["article_id", "sale_id"],
                "constraints": [
                    {
                        "name": "min_stock_less_than_max",
                        "type": "comparison",
                        "columns": ["min_stock", "max_stock"],
                        "operator": "<"
                    },
                    {
                        "name": "positive_quantity",
                        "type": "comparison",
                        "columns": ["quantity"],
                        "operator": ">",
                        "value": 0
                    },
                    {
                        "name": "positive_price",
                        "type": "comparison",
                        "columns": ["unit_price"],
                        "operator": ">",
                        "value": 0
                    }
                ],
                "severity": "error"
            }
        }
    }
    
    manager = DataQualityManager(config=data_quality_config)
    
    # Test data quality for each entity type
    for entity_name, entity_data in test_data.items():
        logger.info(f"Testing data quality for {entity_name}")
        
        # Run data quality checks
        results = manager.run_monitors(entity_data)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_quality_{entity_name}_{timestamp}.json"
        filepath = manager.save_results(filename)
        
        # Log alerts
        alerts = results.get("all_alerts", [])
        if alerts:
            logger.warning(f"Found {len(alerts)} data quality issues in {entity_name}")
            for alert in alerts:
                logger.warning(f"  {alert['severity'].upper()}: {alert['message']}")
        else:
            logger.info(f"No data quality issues found in {entity_name}")
        
        # Visualize results
        visualize_data_quality_results(results, entity_name)
    
    # Test performance with large datasets
    logger.info("Testing performance with large datasets")
    
    # Create a large dataset (1 million rows)
    large_data_size = 1000000
    logger.info(f"Creating large dataset with {large_data_size} rows")
    
    large_data = pd.DataFrame({
        "id": range(large_data_size),
        "value1": np.random.normal(100, 15, size=large_data_size),
        "value2": np.random.normal(50, 10, size=large_data_size),
        "category": np.random.choice(["A", "B", "C", "D"], size=large_data_size),
        "date": np.random.choice(pd.date_range(start="2024-01-01", end="2024-12-31"), size=large_data_size)
    })
    
    # Add some quality issues
    large_data.loc[np.random.choice(large_data_size, size=int(large_data_size * 0.01)), "value1"] = np.nan
    large_data.loc[np.random.choice(large_data_size, size=int(large_data_size * 0.005)), "value2"] = np.random.normal(200, 20, size=int(large_data_size * 0.005))
    
    # Test full dataset performance
    start_time = datetime.now()
    logger.info(f"Running data quality checks on full dataset ({large_data_size} rows)")
    results_full = manager.run_monitors(large_data)
    end_time = datetime.now()
    full_duration = (end_time - start_time).total_seconds()
    logger.info(f"Full dataset check completed in {full_duration:.2f} seconds")
    
    # Test sampling performance
    sample_size = 100000  # 10% sample
    start_time = datetime.now()
    logger.info(f"Running data quality checks on sampled dataset ({sample_size} rows)")
    sampled_data = large_data.sample(sample_size, random_state=42)
    results_sampled = manager.run_monitors(sampled_data)
    end_time = datetime.now()
    sample_duration = (end_time - start_time).total_seconds()
    logger.info(f"Sampled dataset check completed in {sample_duration:.2f} seconds")
    
    # Compare results
    logger.info("Comparing full and sampled results")
    
    # Compare alert counts
    full_alerts = len(results_full.get("all_alerts", []))
    sample_alerts = len(results_sampled.get("all_alerts", []))
    
    logger.info(f"Full dataset alerts: {full_alerts}")
    logger.info(f"Sampled dataset alerts: {sample_alerts}")
    logger.info(f"Performance improvement: {full_duration / sample_duration:.2f}x faster with sampling")
    logger.info(f"Accuracy: {sample_alerts / full_alerts:.2f} ratio of detected issues")
    
    # Create performance comparison visualization
    plt.figure(figsize=(10, 6))
    plt.bar(["Full Dataset", "Sampled Dataset"], [full_duration, sample_duration])
    plt.ylabel("Processing Time (seconds)")
    plt.title("Data Quality Check Performance Comparison")
    plt.tight_layout()
    plt.savefig("test_results/performance_comparison.png")
    
    # Create accuracy comparison visualization
    plt.figure(figsize=(10, 6))
    plt.bar(["Full Dataset", "Sampled Dataset"], [full_alerts, sample_alerts])
    plt.ylabel("Number of Alerts")
    plt.title("Data Quality Alert Comparison")
    plt.tight_layout()
    plt.savefig("test_results/accuracy_comparison.png")
    
    logger.info("Data quality testing completed")
    logger.info(f"Results and visualizations saved to test_results directory")


if __name__ == "__main__":
    logger.info("Starting data quality testing with real datasets")
    test_data_quality_with_real_data()
